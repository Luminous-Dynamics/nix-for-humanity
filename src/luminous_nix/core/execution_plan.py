"""
ExecutionPlan - Multi-step operations with DAG dependencies

This module implements the execution plan system that enables complex,
multi-step NixOS operations with dependency tracking, parallel execution,
and rollback support.

Based on design: DEEP_DIVE_EXECUTION_PLAN.md
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Lifecycle status of an execution step"""
    PENDING = "pending"                  # Not yet started
    READY = "ready"                      # Dependencies met, ready to run
    RUNNING = "running"                  # Currently executing
    SUCCESS = "success"                  # Completed successfully
    FAILED = "failed"                    # Failed with error
    SKIPPED = "skipped"                  # Skipped (dependency failed)
    ROLLED_BACK = "rolled_back"          # Successfully rolled back
    ROLLBACK_FAILED = "rollback_failed"  # Rollback itself failed

    def is_terminal(self) -> bool:
        """Check if this is a final state"""
        return self in {
            StepStatus.SUCCESS,
            StepStatus.FAILED,
            StepStatus.SKIPPED,
            StepStatus.ROLLED_BACK,
            StepStatus.ROLLBACK_FAILED
        }

    def is_complete(self) -> bool:
        """Check if step has completed (successfully or not)"""
        return self.is_terminal()


@dataclass
class ExecutionStep:
    """
    A single step in an execution plan.

    Represents one operation (e.g., "install python", "create config file")
    with its dependencies, resources, and handlers.
    """
    # Identity
    id: str
    name: str

    # Execution
    handler: Callable[[Dict[str, Any]], Any]
    parameters: Dict[str, Any]

    # DAG structure
    depends_on: Set[str]  # Step IDs that must complete first
    provides: Set[str]    # Resources this step provides
    requires: Set[str]    # Resources this step needs

    # Optimization hints
    parallelizable: bool = True     # Can run in parallel with other steps?
    idempotent: bool = False        # Safe to run multiple times?
    estimated_duration_s: float = 10.0  # Estimated time in seconds

    # Rollback support
    rollback_handler: Optional[Callable[[Dict[str, Any]], Any]] = None
    can_rollback: bool = True       # Can this step be rolled back?
    rollback_priority: int = 0      # Higher priority rolled back first

    # State
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        """Validate step after creation"""
        if not self.id:
            raise ValueError("Step ID cannot be empty")
        if not self.name:
            raise ValueError("Step name cannot be empty")
        if not self.handler:
            raise ValueError("Step handler cannot be None")


@dataclass
class ExecutionPlan:
    """
    Complete execution plan for a multi-step operation.

    Manages dependencies, determines execution order, estimates duration,
    and supports parallel execution and rollback.

    Uses Kahn's algorithm for topological sort to compute execution order.
    """
    steps: List[ExecutionStep]

    # Computed during initialization
    _adjacency_list: Dict[str, Set[str]] = field(default_factory=dict, init=False)
    _reverse_adjacency: Dict[str, Set[str]] = field(default_factory=dict, init=False)
    _step_map: Dict[str, ExecutionStep] = field(default_factory=dict, init=False)

    execution_order: List[List[str]] = field(default_factory=list, init=False)
    estimated_duration_s: float = 0.0

    def __post_init__(self):
        """Initialize plan and compute execution order"""
        # Build step map
        self._step_map = {step.id: step for step in self.steps}

        # Validate and build adjacency lists
        self._build_adjacency_lists()

        # Validate no cycles
        self._validate_no_cycles()

        # Validate dependencies exist
        self._validate_dependencies()

        # Validate resources can be satisfied
        self._validate_resources()

        # Compute execution order (batches for parallel execution)
        self.execution_order = self._compute_execution_order()

        # Estimate total duration
        self.estimated_duration_s = self._estimate_duration()

    def _build_adjacency_lists(self):
        """Build forward and reverse adjacency lists for DAG"""
        # Initialize adjacency lists
        for step in self.steps:
            self._adjacency_list[step.id] = set()
            self._reverse_adjacency[step.id] = set()

        # Build adjacency lists from dependencies
        for step in self.steps:
            for dep_id in step.depends_on:
                # Forward: dep_id → step.id (dep_id must come before step.id)
                if dep_id in self._adjacency_list:
                    self._adjacency_list[dep_id].add(step.id)

                # Reverse: step.id ← dep_id
                self._reverse_adjacency[step.id].add(dep_id)

    def _validate_no_cycles(self):
        """
        Detect cycles in the dependency graph using DFS.

        Raises ValueError if a cycle is detected.
        """
        # Colors: WHITE (unvisited), GRAY (visiting), BLACK (visited)
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {step.id: WHITE for step in self.steps}

        def dfs(node_id: str) -> bool:
            """DFS to detect cycles. Returns True if cycle found."""
            colors[node_id] = GRAY

            for neighbor_id in self._adjacency_list[node_id]:
                if colors[neighbor_id] == GRAY:
                    # Back edge - cycle detected!
                    return True
                if colors[neighbor_id] == WHITE:
                    if dfs(neighbor_id):
                        return True

            colors[node_id] = BLACK
            return False

        # Check all nodes
        for step in self.steps:
            if colors[step.id] == WHITE:
                if dfs(step.id):
                    raise ValueError(
                        f"Cycle detected in execution plan dependencies. "
                        f"Cannot have circular dependencies between steps."
                    )

    def _validate_dependencies(self):
        """Validate all dependencies reference existing steps"""
        for step in self.steps:
            for dep_id in step.depends_on:
                if dep_id not in self._step_map:
                    raise ValueError(
                        f"Step '{step.id}' depends on '{dep_id}' but that "
                        f"dependency was not found in the plan."
                    )

    def _validate_resources(self):
        """
        Validate all required resources are provided by some step.

        Each step's 'requires' must be satisfied by 'provides' from
        dependencies or be available initially.
        """
        # Collect all provided resources
        all_provided = set()
        for step in self.steps:
            all_provided.update(step.provides)

        # Check each step's requirements
        for step in self.steps:
            for resource in step.requires:
                if resource not in all_provided:
                    raise ValueError(
                        f"Step '{step.id}' requires resource '{resource}' "
                        f"but no step provides it."
                    )

    def _compute_execution_order(self) -> List[List[str]]:
        """
        Compute execution order using Kahn's algorithm.

        Returns list of batches, where each batch contains step IDs
        that can be executed in parallel.

        Algorithm:
        1. Start with steps that have no dependencies
        2. Add them to current batch
        3. Remove them from graph
        4. Find newly-ready steps (all dependencies complete)
        5. Repeat until no steps remain
        """
        if not self.steps:
            return []

        # Copy reverse adjacency for modification
        in_degree = {
            step_id: len(deps)
            for step_id, deps in self._reverse_adjacency.items()
        }

        # Queue of steps ready to execute (no pending dependencies)
        ready_queue = [step.id for step in self.steps if in_degree[step.id] == 0]

        batches = []

        while ready_queue:
            # Current batch: all steps currently ready
            current_batch = list(ready_queue)
            batches.append(current_batch)

            # Process current batch
            ready_queue = []

            for step_id in current_batch:
                # For each step that depends on this one
                for dependent_id in self._adjacency_list[step_id]:
                    # Decrease in-degree
                    in_degree[dependent_id] -= 1

                    # If all dependencies satisfied, add to ready queue
                    if in_degree[dependent_id] == 0:
                        ready_queue.append(dependent_id)

        # Sanity check: all steps should be in batches
        total_steps = sum(len(batch) for batch in batches)
        if total_steps != len(self.steps):
            # This shouldn't happen if cycle detection worked
            raise ValueError(
                f"Internal error: Not all steps were scheduled. "
                f"Expected {len(self.steps)}, got {total_steps}"
            )

        return batches

    def _estimate_duration(self) -> float:
        """
        Estimate total execution duration.

        For parallel execution, duration is the longest path through
        the DAG, not the sum of all steps.

        Algorithm: Find longest path using dynamic programming.
        """
        if not self.steps:
            return 0.0

        # Compute longest path to each step
        longest_path = {step.id: 0.0 for step in self.steps}

        # Process steps in topological order (use execution_order)
        for batch in self.execution_order:
            for step_id in batch:
                step = self._step_map[step_id]

                # Longest path to this step = max path to any dependency + this step's duration
                max_dep_path = 0.0
                for dep_id in step.depends_on:
                    dep_path = longest_path[dep_id]
                    max_dep_path = max(max_dep_path, dep_path)

                longest_path[step_id] = max_dep_path + step.estimated_duration_s

        # Total duration = max of all paths
        return max(longest_path.values()) if longest_path else 0.0

    def get_next_batch(self) -> Optional[List[ExecutionStep]]:
        """
        Get next batch of steps ready to execute.

        Returns:
            List of steps whose dependencies are all complete and
            status is PENDING. Returns None if no steps are ready.
        """
        ready_steps = []

        for step in self.steps:
            # Skip if not pending
            if step.status != StepStatus.PENDING:
                continue

            # Check if all dependencies are complete
            all_deps_complete = True
            for dep_id in step.depends_on:
                dep_step = self._step_map[dep_id]
                if dep_step.status != StepStatus.SUCCESS:
                    all_deps_complete = False
                    break

            if all_deps_complete:
                # Mark as ready and add to batch
                step.status = StepStatus.READY
                ready_steps.append(step)

        return ready_steps if ready_steps else None

    def get_rollback_order(self) -> List[ExecutionStep]:
        """
        Get steps in rollback order (reverse of execution).

        Only includes steps that:
        - Can be rolled back (can_rollback=True)
        - Have a rollback handler
        - Have been executed (status is not PENDING)

        Steps are ordered by:
        1. Reverse execution order (dependencies first)
        2. Rollback priority (higher priority first)
        """
        # Get all executed steps that can be rolled back
        rollback_steps = [
            step for step in self.steps
            if step.can_rollback
            and step.rollback_handler is not None
            and step.status not in {StepStatus.PENDING, StepStatus.READY}
        ]

        # Reverse execution order
        # Build execution order list (flat)
        exec_order_flat = []
        for batch in self.execution_order:
            for step_id in batch:
                exec_order_flat.append(step_id)

        # Create reverse map (step_id -> execution index)
        exec_index = {step_id: i for i, step_id in enumerate(exec_order_flat)}

        # Sort by execution order (reversed) and rollback priority
        rollback_steps.sort(
            key=lambda s: (-exec_index.get(s.id, 0), -s.rollback_priority)
        )

        return rollback_steps

    def get_step(self, step_id: str) -> Optional[ExecutionStep]:
        """Get step by ID"""
        return self._step_map.get(step_id)

    def all_complete(self) -> bool:
        """Check if all steps are complete"""
        return all(step.status.is_complete() for step in self.steps)

    def has_failures(self) -> bool:
        """Check if any steps have failed"""
        return any(step.status == StepStatus.FAILED for step in self.steps)

    def get_progress(self) -> float:
        """
        Get progress as a percentage (0.0 to 1.0)

        Based on number of completed steps vs total steps.
        """
        if not self.steps:
            return 1.0

        complete_count = sum(1 for step in self.steps if step.status.is_complete())
        return complete_count / len(self.steps)

    def summary(self) -> Dict[str, Any]:
        """Get summary of plan"""
        status_counts = {}
        for step in self.steps:
            status = step.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            'total_steps': len(self.steps),
            'total_batches': len(self.execution_order),
            'estimated_duration_s': self.estimated_duration_s,
            'progress': self.get_progress(),
            'all_complete': self.all_complete(),
            'has_failures': self.has_failures(),
            'status_counts': status_counts
        }

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"ExecutionPlan(steps={len(self.steps)}, "
            f"batches={len(self.execution_order)}, "
            f"duration={self.estimated_duration_s:.1f}s)"
        )


# === Utility Functions ===

def create_simple_plan(
    operations: List[Dict[str, Any]],
    sequential: bool = False
) -> ExecutionPlan:
    """
    Create a simple execution plan from a list of operations.

    Args:
        operations: List of dicts with 'id', 'name', 'handler', 'parameters'
        sequential: If True, operations run sequentially. If False, in parallel.

    Returns:
        ExecutionPlan
    """
    steps = []
    prev_id = None

    for i, op in enumerate(operations):
        depends_on = {prev_id} if sequential and prev_id else set()

        step = ExecutionStep(
            id=op.get('id', f'step{i}'),
            name=op.get('name', f'Step {i}'),
            handler=op['handler'],
            parameters=op.get('parameters', {}),
            depends_on=depends_on,
            provides={op.get('id', f'step{i}')},
            requires={prev_id} if prev_id else set(),
            estimated_duration_s=op.get('duration', 10.0)
        )

        steps.append(step)
        prev_id = step.id

    return ExecutionPlan(steps=steps)


if __name__ == "__main__":
    # Example: Create and display a simple plan
    def mock_handler(params):
        print(f"Executing with params: {params}")
        return "success"

    # Create a simple 3-step plan: A → (B, C) → D
    stepA = ExecutionStep(
        id="A",
        name="Step A",
        handler=mock_handler,
        parameters={'step': 'A'},
        depends_on=set(),
        provides={'rA'},
        requires=set(),
        estimated_duration_s=10.0
    )

    stepB = ExecutionStep(
        id="B",
        name="Step B",
        handler=mock_handler,
        parameters={'step': 'B'},
        depends_on={'A'},
        provides={'rB'},
        requires={'rA'},
        estimated_duration_s=20.0
    )

    stepC = ExecutionStep(
        id="C",
        name="Step C",
        handler=mock_handler,
        parameters={'step': 'C'},
        depends_on={'A'},
        provides={'rC'},
        requires={'rA'},
        estimated_duration_s=15.0
    )

    stepD = ExecutionStep(
        id="D",
        name="Step D",
        handler=mock_handler,
        parameters={'step': 'D'},
        depends_on={'B', 'C'},
        provides={'rD'},
        requires={'rB', 'rC'},
        estimated_duration_s=5.0
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC, stepD])

    print(f"Plan: {plan}")
    print(f"Execution order: {plan.execution_order}")
    print(f"Estimated duration: {plan.estimated_duration_s}s")
    print(f"Summary: {plan.summary()}")
