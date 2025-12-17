# 🔬 Deep Dive: ExecutionPlan + DAG Architecture

**Created**: December 2, 2025
**Purpose**: Detailed design of execution planning system - the foundation for multi-step operations
**Approach**: Test-Driven Design - write tests first, then implement

---

## Executive Summary

**Problem**: Need to execute complex multi-step operations reliably across all contexts
**Solution**: ExecutionPlan with directed acyclic graph (DAG) for dependencies
**Key Features**: Parallel execution, partial rollback, state persistence, resumability

---

## 1. Core Data Structures

### 1.1 ExecutionStep

The atomic unit of work.

```python
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional, Set
from enum import Enum
from datetime import datetime
import uuid


class StepStatus(Enum):
    """All possible states of an execution step"""
    PENDING = "pending"           # Not yet started
    READY = "ready"               # Dependencies satisfied, ready to run
    RUNNING = "running"           # Currently executing
    SUCCESS = "success"           # Completed successfully
    FAILED = "failed"             # Execution failed
    SKIPPED = "skipped"          # Skipped (e.g., already satisfied)
    ROLLED_BACK = "rolled_back"  # Successfully undone
    ROLLBACK_FAILED = "rollback_failed"  # Rollback failed (requires manual intervention)


class StepType(Enum):
    """Categories of steps for different handling"""
    QUERY = "query"              # Read-only, safe, fast (e.g., check if installed)
    MODIFY = "modify"            # Changes system state (e.g., install package)
    GENERATE = "generate"        # Creates files/config (e.g., write configuration.nix)
    VERIFY = "verify"            # Validates result (e.g., test if service running)
    CLEANUP = "cleanup"          # Removes temporary artifacts


@dataclass
class ExecutionStep:
    """
    A single atomic operation in an execution plan.

    Design principles:
    - Immutable once created (except status/result)
    - Self-contained (has all info needed to execute)
    - Idempotent when possible (can run multiple times safely)
    - Reversible when needed (can rollback)
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = field(default="")
    description: str = field(default="")
    step_type: StepType = StepType.MODIFY

    # Execution
    handler: Callable[[Dict[str, Any]], Any] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Dependencies - the DAG structure
    depends_on: Set[str] = field(default_factory=set)  # IDs of steps that must complete first
    provides: Set[str] = field(default_factory=set)    # Resources this step provides
    requires: Set[str] = field(default_factory=set)    # Resources this step needs

    # Optimization flags
    parallelizable: bool = True   # Can run in parallel with non-dependent steps
    idempotent: bool = False      # Safe to run multiple times
    cacheable: bool = False       # Result can be cached

    # Rollback
    rollback_handler: Optional[Callable[[Dict[str, Any]], Any]] = None
    can_rollback: bool = True     # Can this step be undone?
    rollback_priority: int = 0    # Higher priority rolled back first

    # Execution constraints
    estimated_duration: float = 30.0  # Seconds
    timeout: float = 300.0            # Maximum execution time
    max_retries: int = 3
    retry_delay: float = 1.0          # Seconds between retries

    # State (mutable during execution)
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[Exception] = None
    attempts: int = 0

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def can_execute(self, completed_steps: Set[str]) -> bool:
        """Check if all dependencies are satisfied"""
        return self.depends_on.issubset(completed_steps)

    def duration(self) -> float:
        """Calculate actual execution duration"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0

    def is_terminal(self) -> bool:
        """Check if step is in terminal state (no more work to do)"""
        return self.status in [
            StepStatus.SUCCESS,
            StepStatus.FAILED,
            StepStatus.SKIPPED,
            StepStatus.ROLLED_BACK,
            StepStatus.ROLLBACK_FAILED
        ]

    def should_retry(self) -> bool:
        """Check if step should be retried after failure"""
        return (
            self.status == StepStatus.FAILED and
            self.attempts < self.max_retries and
            self.error is not None
        )
```

### 1.2 ExecutionPlan

The complete execution plan with dependency graph.

```python
from collections import defaultdict, deque
from typing import List, Set, Dict, Tuple, Optional
import json


class PlanStatus(Enum):
    """Overall plan execution status"""
    CREATED = "created"
    VALIDATING = "validating"
    READY = "ready"
    EXECUTING = "executing"
    PAUSED = "paused"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ExecutionPlan:
    """
    Complete execution plan with DAG of steps.

    Design principles:
    - Validates on creation (no cycles, all deps exist)
    - Determines execution order via topological sort
    - Supports parallel execution where possible
    - Tracks state throughout execution
    - Can pause/resume/rollback
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""

    # Steps
    steps: List[ExecutionStep] = field(default_factory=list)

    # DAG representation (computed from steps)
    _adjacency_list: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    _reverse_adjacency: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    _step_map: Dict[str, ExecutionStep] = field(default_factory=dict)

    # Execution state
    status: PlanStatus = PlanStatus.CREATED
    execution_order: List[List[str]] = field(default_factory=list)  # Batches that can run in parallel

    # Progress tracking
    completed_steps: Set[str] = field(default_factory=set)
    failed_steps: Set[str] = field(default_factory=set)
    current_batch: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate and prepare plan after creation"""
        self._build_dag()
        self._validate()
        if not self.execution_order:
            self.execution_order = self._compute_execution_order()
        self.status = PlanStatus.READY

    def _build_dag(self):
        """Build adjacency list representation from steps"""
        self._step_map = {step.id: step for step in self.steps}

        for step in self.steps:
            # Forward edges (dependencies)
            for dep_id in step.depends_on:
                self._adjacency_list[dep_id].add(step.id)

            # Reverse edges (for rollback)
            for dep_id in step.depends_on:
                self._reverse_adjacency[step.id].add(dep_id)

    def _validate(self):
        """
        Validate plan structure.

        Checks:
        1. No cycles in dependency graph
        2. All dependencies reference valid steps
        3. Resource requirements can be satisfied
        """
        # Check all dependencies exist
        for step in self.steps:
            for dep_id in step.depends_on:
                if dep_id not in self._step_map:
                    raise ValueError(
                        f"Step {step.id} depends on non-existent step {dep_id}"
                    )

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in self._adjacency_list.get(node_id, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for step_id in self._step_map:
            if step_id not in visited:
                if has_cycle(step_id):
                    raise ValueError(
                        f"Cycle detected in execution plan at step {step_id}"
                    )

        # Check resource satisfaction
        self._validate_resources()

    def _validate_resources(self):
        """Ensure all required resources will be provided"""
        provided_resources = set()

        # Topological order ensures we check in execution order
        for batch in self._compute_execution_order():
            batch_provides = set()
            batch_requires = set()

            for step_id in batch:
                step = self._step_map[step_id]
                batch_requires.update(step.requires)
                batch_provides.update(step.provides)

            # Check if batch requirements can be satisfied
            unsatisfied = batch_requires - provided_resources
            if unsatisfied:
                # Check if batch provides what it needs (internal satisfaction)
                unsatisfied = unsatisfied - batch_provides
                if unsatisfied:
                    raise ValueError(
                        f"Resources {unsatisfied} required but never provided"
                    )

            provided_resources.update(batch_provides)

    def _compute_execution_order(self) -> List[List[str]]:
        """
        Compute execution order using topological sort.

        Returns batches of step IDs that can run in parallel.
        Each batch contains steps with no dependencies on each other.

        Algorithm: Kahn's algorithm for topological sort, modified for batching
        """
        # Count in-degrees (number of dependencies)
        in_degree = {step.id: len(step.depends_on) for step in self.steps}

        # Find all steps with no dependencies (in-degree 0)
        ready_queue = deque([
            step_id for step_id, degree in in_degree.items() if degree == 0
        ])

        batches = []

        while ready_queue:
            # Current batch: all ready steps
            batch = []
            batch_size = len(ready_queue)

            for _ in range(batch_size):
                step_id = ready_queue.popleft()
                step = self._step_map[step_id]

                # Check if step can run in parallel with others in batch
                can_parallel = step.parallelizable
                if can_parallel:
                    # Check if any step in current batch conflicts
                    for other_id in batch:
                        other = self._step_map[other_id]
                        if self._steps_conflict(step, other):
                            can_parallel = False
                            break

                if can_parallel:
                    batch.append(step_id)
                else:
                    # Defer to next batch
                    ready_queue.append(step_id)

            if batch:
                batches.append(batch)

                # Reduce in-degree for dependent steps
                for step_id in batch:
                    for dependent_id in self._adjacency_list[step_id]:
                        in_degree[dependent_id] -= 1
                        if in_degree[dependent_id] == 0:
                            ready_queue.append(dependent_id)

        # Check if all steps were scheduled
        total_scheduled = sum(len(batch) for batch in batches)
        if total_scheduled != len(self.steps):
            raise ValueError(
                f"Failed to schedule all steps. "
                f"Scheduled {total_scheduled}, expected {len(self.steps)}. "
                f"Possible cycle in dependencies."
            )

        return batches

    def _steps_conflict(self, step1: ExecutionStep, step2: ExecutionStep) -> bool:
        """
        Check if two steps conflict and cannot run in parallel.

        Conflicts occur when:
        1. One requires what the other provides
        2. Both modify the same resource
        3. One is not parallelizable
        """
        # If either is not parallelizable, they conflict
        if not step1.parallelizable or not step2.parallelizable:
            return True

        # If one provides what the other requires, they conflict
        if step1.provides & step2.requires:
            return True
        if step2.provides & step1.requires:
            return True

        # If both modify the same resource, they conflict
        if step1.step_type == StepType.MODIFY and step2.step_type == StepType.MODIFY:
            if step1.provides & step2.provides:
                return True

        return False

    def get_next_batch(self) -> Optional[List[ExecutionStep]]:
        """Get next batch of steps ready to execute"""
        if self.current_batch >= len(self.execution_order):
            return None

        batch_ids = self.execution_order[self.current_batch]
        batch_steps = [self._step_map[step_id] for step_id in batch_ids]

        # Filter to only steps that are actually ready
        ready_steps = [
            step for step in batch_steps
            if step.status == StepStatus.READY or step.status == StepStatus.PENDING
        ]

        return ready_steps if ready_steps else None

    def mark_step_complete(self, step_id: str, success: bool, result: Any = None, error: Exception = None):
        """Mark a step as complete and update plan state"""
        step = self._step_map[step_id]

        if success:
            step.status = StepStatus.SUCCESS
            step.result = result
            self.completed_steps.add(step_id)
        else:
            step.status = StepStatus.FAILED
            step.error = error
            self.failed_steps.add(step_id)

        step.completed_at = datetime.now()

        # Check if we can advance to next batch
        batch_ids = self.execution_order[self.current_batch]
        if all(self._step_map[sid].is_terminal() for sid in batch_ids):
            self.current_batch += 1

    def get_rollback_order(self) -> List[ExecutionStep]:
        """
        Compute order for rolling back completed steps.

        Returns steps in reverse topological order (undoing in reverse).
        Only includes steps that:
        1. Were successfully completed
        2. Can be rolled back

        Sorted by rollback_priority (high to low), then reverse execution order.
        """
        rollback_candidates = [
            step for step in self.steps
            if step.status == StepStatus.SUCCESS and step.can_rollback
        ]

        # Sort by priority (high first), then reverse completion time
        rollback_candidates.sort(
            key=lambda s: (-s.rollback_priority, -(s.completed_at or datetime.min).timestamp())
        )

        return rollback_candidates

    def estimate_duration(self) -> float:
        """
        Estimate total execution time.

        For parallel execution, duration is the longest path in the DAG.
        """
        # Compute longest path using dynamic programming
        memo = {}

        def longest_path(step_id: str) -> float:
            if step_id in memo:
                return memo[step_id]

            step = self._step_map[step_id]

            if not step.depends_on:
                # Leaf node
                result = step.estimated_duration
            else:
                # Max of all dependency paths + this step's duration
                max_dep_path = max(
                    longest_path(dep_id) for dep_id in step.depends_on
                )
                result = max_dep_path + step.estimated_duration

            memo[step_id] = result
            return result

        # Find maximum path among all terminal nodes (nodes with no dependents)
        terminal_nodes = [
            step.id for step in self.steps
            if not self._adjacency_list[step.id]
        ]

        if not terminal_nodes:
            # All steps have dependents? Take max of all
            terminal_nodes = list(self._step_map.keys())

        return max(longest_path(node_id) for node_id in terminal_nodes)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize plan to dictionary (for persistence)"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'steps': [
                {
                    'id': step.id,
                    'name': step.name,
                    'status': step.status.value,
                    'depends_on': list(step.depends_on),
                    'result': str(step.result) if step.result else None,
                    'error': str(step.error) if step.error else None,
                    'attempts': step.attempts,
                    'started_at': step.started_at.isoformat() if step.started_at else None,
                    'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                }
                for step in self.steps
            ],
            'execution_order': self.execution_order,
            'current_batch': self.current_batch,
            'completed_steps': list(self.completed_steps),
            'failed_steps': list(self.failed_steps),
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

    def to_json(self) -> str:
        """Serialize plan to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
```

---

## 2. Example: "Setup Python Dev Environment"

Let's design a concrete multi-step operation:

```python
def create_python_dev_plan() -> ExecutionPlan:
    """
    Create execution plan for setting up Python development environment.

    Steps:
    1. Check if python is already installed
    2. Install python3
    3. Install poetry
    4. Install git
    5. Create shell.nix
    6. Test shell
    7. Create .envrc for direnv (optional)
    """

    steps = []

    # Step 1: Check if python installed (QUERY - fast, parallelizable)
    check_python = ExecutionStep(
        id="check_python",
        name="Check Python Installation",
        description="Check if python3 is already available",
        step_type=StepType.QUERY,
        handler=lambda params: subprocess.run(
            ["which", "python3"],
            capture_output=True
        ).returncode == 0,
        parameters={},
        parallelizable=True,
        idempotent=True,
        cacheable=True,
        can_rollback=False,  # Query operations don't need rollback
        estimated_duration=0.5,
    )
    steps.append(check_python)

    # Step 2: Install python3 (MODIFY - changes system)
    install_python = ExecutionStep(
        id="install_python",
        name="Install Python 3",
        description="Install python3 and development tools",
        step_type=StepType.MODIFY,
        handler=lambda params: install_package("python3"),
        parameters={'package': 'python3'},
        depends_on={'check_python'},  # Only run if check completes
        provides={'python3'},
        parallelizable=False,  # Package installs are sequential
        idempotent=True,  # nix-env is idempotent
        can_rollback=True,
        rollback_handler=lambda params: remove_package("python3"),
        rollback_priority=10,
        estimated_duration=30.0,
        max_retries=3,
    )
    steps.append(install_python)

    # Step 3: Install poetry (parallel with git)
    install_poetry = ExecutionStep(
        id="install_poetry",
        name="Install Poetry",
        description="Install poetry for dependency management",
        step_type=StepType.MODIFY,
        handler=lambda params: install_package("poetry"),
        parameters={'package': 'poetry'},
        depends_on={'install_python'},  # Needs python first
        provides={'poetry'},
        requires={'python3'},
        parallelizable=True,  # Can run parallel with git
        idempotent=True,
        can_rollback=True,
        rollback_handler=lambda params: remove_package("poetry"),
        estimated_duration=20.0,
    )
    steps.append(install_poetry)

    # Step 4: Install git (parallel with poetry)
    install_git = ExecutionStep(
        id="install_git",
        name="Install Git",
        description="Install git for version control",
        step_type=StepType.MODIFY,
        handler=lambda params: install_package("git"),
        parameters={'package': 'git'},
        depends_on={'install_python'},  # Can start after python
        provides={'git'},
        parallelizable=True,  # Can run parallel with poetry
        idempotent=True,
        can_rollback=True,
        rollback_handler=lambda params: remove_package("git"),
        estimated_duration=15.0,
    )
    steps.append(install_git)

    # Step 5: Create shell.nix (GENERATE - creates config)
    create_shell_nix = ExecutionStep(
        id="create_shell_nix",
        name="Create shell.nix",
        description="Generate shell.nix for reproducible environment",
        step_type=StepType.GENERATE,
        handler=lambda params: create_file(
            "shell.nix",
            SHELL_NIX_TEMPLATE.format(**params)
        ),
        parameters={
            'python_version': '311',
            'packages': ['poetry', 'pytest', 'black', 'mypy']
        },
        depends_on={'install_poetry', 'install_git'},  # Needs both
        provides={'shell_nix'},
        requires={'poetry', 'git'},
        parallelizable=False,  # File generation is fast, no need to parallelize
        idempotent=True,
        can_rollback=True,
        rollback_handler=lambda params: remove_file("shell.nix"),
        estimated_duration=2.0,
    )
    steps.append(create_shell_nix)

    # Step 6: Test shell (VERIFY - checks result)
    test_shell = ExecutionStep(
        id="test_shell",
        name="Test Development Shell",
        description="Verify shell.nix works correctly",
        step_type=StepType.VERIFY,
        handler=lambda params: test_nix_shell(),
        parameters={},
        depends_on={'create_shell_nix'},
        requires={'shell_nix'},
        parallelizable=False,
        idempotent=True,
        can_rollback=False,  # Verification doesn't need rollback
        estimated_duration=5.0,
    )
    steps.append(test_shell)

    # Step 7: Create .envrc (optional, for direnv users)
    create_envrc = ExecutionStep(
        id="create_envrc",
        name="Create .envrc",
        description="Setup direnv for automatic environment activation",
        step_type=StepType.GENERATE,
        handler=lambda params: create_file(".envrc", "use nix\n"),
        parameters={},
        depends_on={'create_shell_nix'},
        provides={'envrc'},
        requires={'shell_nix'},
        parallelizable=True,  # Independent of test_shell
        idempotent=True,
        can_rollback=True,
        rollback_handler=lambda params: remove_file(".envrc"),
        estimated_duration=1.0,
    )
    steps.append(create_envrc)

    # Create plan
    plan = ExecutionPlan(
        name="Python Development Environment Setup",
        description="Sets up complete Python dev environment with poetry, git, and nix-shell",
        steps=steps
    )

    return plan


# Example usage
if __name__ == "__main__":
    plan = create_python_dev_plan()

    print(f"Plan: {plan.name}")
    print(f"Total steps: {len(plan.steps)}")
    print(f"Estimated duration: {plan.estimate_duration():.1f}s")
    print(f"\nExecution order (batches that can run in parallel):")

    for i, batch in enumerate(plan.execution_order):
        print(f"\nBatch {i+1}:")
        for step_id in batch:
            step = plan._step_map[step_id]
            print(f"  - {step.name} ({step.estimated_duration}s)")
```

Expected output:
```
Plan: Python Development Environment Setup
Total steps: 7
Estimated duration: 73.5s

Execution order (batches that can run in parallel):

Batch 1:
  - Check Python Installation (0.5s)

Batch 2:
  - Install Python 3 (30.0s)

Batch 3:
  - Install Poetry (20.0s)
  - Install Git (15.0s)

Batch 4:
  - Create shell.nix (2.0s)

Batch 5:
  - Test Development Shell (5.0s)
  - Create .envrc (1.0s)
```

---

## 3. Test Cases (TDD Approach)

Write tests BEFORE implementing:

```python
import pytest
from execution_plan import ExecutionPlan, ExecutionStep, StepStatus, StepType


class TestExecutionStep:
    """Test individual step behavior"""

    def test_step_creation(self):
        """Test creating a step with minimal parameters"""
        step = ExecutionStep(
            name="Test Step",
            handler=lambda p: "result"
        )

        assert step.name == "Test Step"
        assert step.status == StepStatus.PENDING
        assert len(step.id) > 0  # UUID generated
        assert step.can_rollback == True  # Default

    def test_step_dependencies_satisfied(self):
        """Test checking if dependencies are satisfied"""
        step = ExecutionStep(
            name="Dependent Step",
            depends_on={'step1', 'step2'}
        )

        assert not step.can_execute(set())
        assert not step.can_execute({'step1'})
        assert step.can_execute({'step1', 'step2'})
        assert step.can_execute({'step1', 'step2', 'step3'})  # Extra is OK

    def test_step_duration_calculation(self):
        """Test calculating step execution duration"""
        from datetime import datetime, timedelta

        step = ExecutionStep(name="Timed Step")
        assert step.duration() == 0.0  # Not yet started

        step.started_at = datetime.now()
        assert step.duration() == 0.0  # Not yet completed

        step.completed_at = step.started_at + timedelta(seconds=5.5)
        assert abs(step.duration() - 5.5) < 0.1  # Within 100ms

    def test_step_retry_logic(self):
        """Test retry decision logic"""
        step = ExecutionStep(
            name="Retry Step",
            max_retries=3
        )

        # Initially no retry needed
        assert not step.should_retry()

        # After failure, should retry
        step.status = StepStatus.FAILED
        step.error = Exception("Network error")
        step.attempts = 1
        assert step.should_retry()

        # After max retries, should not retry
        step.attempts = 3
        assert not step.should_retry()


class TestExecutionPlan:
    """Test plan creation and validation"""

    def test_empty_plan(self):
        """Test creating empty plan"""
        plan = ExecutionPlan(name="Empty Plan")
        assert plan.status == PlanStatus.READY
        assert len(plan.steps) == 0
        assert len(plan.execution_order) == 0

    def test_simple_linear_plan(self):
        """Test plan with linear dependencies (A -> B -> C)"""
        steps = [
            ExecutionStep(id="a", name="Step A"),
            ExecutionStep(id="b", name="Step B", depends_on={'a'}),
            ExecutionStep(id="c", name="Step C", depends_on={'b'}),
        ]

        plan = ExecutionPlan(name="Linear Plan", steps=steps)

        assert plan.status == PlanStatus.READY
        assert len(plan.execution_order) == 3
        assert plan.execution_order == [['a'], ['b'], ['c']]

    def test_parallel_execution_plan(self):
        """Test plan with parallelizable steps"""
        steps = [
            ExecutionStep(id="a", name="Step A"),
            ExecutionStep(id="b", name="Step B", depends_on={'a'}),
            ExecutionStep(id="c", name="Step C", depends_on={'a'}),
            ExecutionStep(id="d", name="Step D", depends_on={'b', 'c'}),
        ]

        plan = ExecutionPlan(name="Parallel Plan", steps=steps)

        assert len(plan.execution_order) == 3
        assert plan.execution_order[0] == ['a']
        assert set(plan.execution_order[1]) == {'b', 'c'}  # Parallel
        assert plan.execution_order[2] == ['d']

    def test_cycle_detection(self):
        """Test that cycles in dependencies are detected"""
        steps = [
            ExecutionStep(id="a", name="Step A", depends_on={'b'}),
            ExecutionStep(id="b", name="Step B", depends_on={'a'}),
        ]

        with pytest.raises(ValueError, match="Cycle detected"):
            ExecutionPlan(name="Cyclic Plan", steps=steps)

    def test_missing_dependency_detection(self):
        """Test that missing dependencies are detected"""
        steps = [
            ExecutionStep(id="a", name="Step A", depends_on={'nonexistent'}),
        ]

        with pytest.raises(ValueError, match="non-existent"):
            ExecutionPlan(name="Invalid Plan", steps=steps)

    def test_resource_validation(self):
        """Test that required resources must be provided"""
        steps = [
            ExecutionStep(
                id="a",
                name="Step A",
                requires={'python3'},  # Requires python3
                provides=set()         # But doesn't provide it
            ),
        ]

        with pytest.raises(ValueError, match="never provided"):
            ExecutionPlan(name="Unsatisfied Plan", steps=steps)

    def test_resource_satisfaction(self):
        """Test that resources can be satisfied by earlier steps"""
        steps = [
            ExecutionStep(
                id="provider",
                name="Provide Python",
                provides={'python3'}
            ),
            ExecutionStep(
                id="consumer",
                name="Use Python",
                requires={'python3'},
                depends_on={'provider'}
            ),
        ]

        plan = ExecutionPlan(name="Satisfied Plan", steps=steps)
        assert plan.status == PlanStatus.READY

    def test_duration_estimation_linear(self):
        """Test duration estimation for linear plan"""
        steps = [
            ExecutionStep(id="a", name="A", estimated_duration=10.0),
            ExecutionStep(id="b", name="B", estimated_duration=20.0, depends_on={'a'}),
            ExecutionStep(id="c", name="C", estimated_duration=15.0, depends_on={'b'}),
        ]

        plan = ExecutionPlan(steps=steps)
        assert plan.estimate_duration() == 45.0  # 10 + 20 + 15

    def test_duration_estimation_parallel(self):
        """Test duration estimation for parallel plan"""
        steps = [
            ExecutionStep(id="a", name="A", estimated_duration=10.0),
            ExecutionStep(id="b", name="B", estimated_duration=20.0, depends_on={'a'}),
            ExecutionStep(id="c", name="C", estimated_duration=15.0, depends_on={'a'}),
            ExecutionStep(id="d", name="D", estimated_duration=5.0, depends_on={'b', 'c'}),
        ]

        plan = ExecutionPlan(steps=steps)
        # Longest path: a(10) -> b(20) -> d(5) = 35
        assert plan.estimate_duration() == 35.0

    def test_get_next_batch(self):
        """Test getting next batch of steps to execute"""
        steps = [
            ExecutionStep(id="a", name="A"),
            ExecutionStep(id="b", name="B", depends_on={'a'}),
            ExecutionStep(id="c", name="C", depends_on={'a'}),
        ]

        plan = ExecutionPlan(steps=steps)

        # First batch
        batch = plan.get_next_batch()
        assert len(batch) == 1
        assert batch[0].id == 'a'

        # Mark complete and get next
        plan.mark_step_complete('a', success=True)
        batch = plan.get_next_batch()
        assert len(batch) == 2
        assert {s.id for s in batch} == {'b', 'c'}

    def test_rollback_order(self):
        """Test computing rollback order"""
        steps = [
            ExecutionStep(id="a", name="A", rollback_priority=1),
            ExecutionStep(id="b", name="B", rollback_priority=2, depends_on={'a'}),
            ExecutionStep(id="c", name="C", rollback_priority=3, depends_on={'b'}),
        ]

        plan = ExecutionPlan(steps=steps)

        # Mark all as completed
        for step in plan.steps:
            step.status = StepStatus.SUCCESS

        # Get rollback order (should be reverse: c, b, a)
        rollback = plan.get_rollback_order()
        assert [s.id for s in rollback] == ['c', 'b', 'a']

    def test_plan_serialization(self):
        """Test serializing plan to dict/JSON"""
        steps = [
            ExecutionStep(id="a", name="Step A"),
            ExecutionStep(id="b", name="Step B", depends_on={'a'}),
        ]

        plan = ExecutionPlan(name="Test Plan", steps=steps)

        # Serialize to dict
        plan_dict = plan.to_dict()
        assert plan_dict['name'] == "Test Plan"
        assert len(plan_dict['steps']) == 2

        # Serialize to JSON
        plan_json = plan.to_json()
        assert "Test Plan" in plan_json
        assert isinstance(plan_json, str)
```

---

## 4. Edge Cases to Handle

### 4.1 Diamond Dependencies

```python
def test_diamond_dependencies():
    """
    Test plan with diamond dependency pattern:

        A
       / \
      B   C
       \ /
        D

    D depends on both B and C, which both depend on A.
    """
    steps = [
        ExecutionStep(id="a", name="A"),
        ExecutionStep(id="b", name="B", depends_on={'a'}),
        ExecutionStep(id="c", name="C", depends_on={'a'}),
        ExecutionStep(id="d", name="D", depends_on={'b', 'c'}),
    ]

    plan = ExecutionPlan(steps=steps)

    # A runs first
    assert 'a' in plan.execution_order[0]

    # B and C run in parallel
    assert set(plan.execution_order[1]) == {'b', 'c'}

    # D runs last
    assert 'd' in plan.execution_order[2]
```

### 4.2 Partial Rollback

```python
def test_partial_rollback():
    """
    Test rolling back when some steps can't be undone.

    Scenario: Steps A, B, C completed. C fails to rollback.
    Expected: B and A still rolled back, C marked as rollback_failed.
    """
    # Implementation should handle this gracefully
    pass
```

### 4.3 Timeout Handling

```python
def test_step_timeout():
    """Test that steps respect timeout settings"""
    import time

    def slow_handler(params):
        time.sleep(10)
        return "done"

    step = ExecutionStep(
        name="Slow Step",
        handler=slow_handler,
        timeout=1.0  # 1 second timeout
    )

    # Executor should raise timeout error
    pass
```

---

## 5. Implementation Checklist

### Phase 1: Core Data Structures ✅
- [x] Define `StepStatus` enum
- [x] Define `StepType` enum
- [x] Implement `ExecutionStep` dataclass
- [x] Implement `ExecutionPlan` dataclass
- [x] Write comprehensive tests

### Phase 2: DAG Operations 🔄 Next
- [ ] Implement topological sort
- [ ] Implement cycle detection
- [ ] Implement parallel batch computation
- [ ] Test with complex graphs

### Phase 3: Resource Management 🔄 Next
- [ ] Implement resource validation
- [ ] Implement conflict detection
- [ ] Test resource satisfaction

### Phase 4: Integration 📋 Later
- [ ] Wire into strategy router
- [ ] Connect to execution engine
- [ ] Add persistence layer

---

## 6. Next Steps

1. **Review this design** with fresh eyes
2. **Run the tests** (they should all pass with implementation)
3. **Move to State Management deep dive** (next document)
4. **Implement ExecutionPlan** (after all 3 deep dives complete)

---

**Status**: Design complete, ready for review
**Next**: Deep dive on State Management
**Then**: Deep dive on Error Recovery
**Finally**: Implement all three together
