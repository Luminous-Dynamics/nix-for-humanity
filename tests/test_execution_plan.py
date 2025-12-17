"""
Tests for ExecutionPlan - Multi-step operations with DAG dependencies

Test-Driven Development: These tests are written FIRST, then we implement
until all tests pass.

Based on design from: DEEP_DIVE_EXECUTION_PLAN.md
"""

import pytest
from datetime import datetime
from typing import Dict, Any, Set


# === Test Data Structures ===

def test_step_status_enum():
    """Test StepStatus enum exists with correct values"""
    from luminous_nix.core.execution_plan import StepStatus

    assert hasattr(StepStatus, 'PENDING')
    assert hasattr(StepStatus, 'READY')
    assert hasattr(StepStatus, 'RUNNING')
    assert hasattr(StepStatus, 'SUCCESS')
    assert hasattr(StepStatus, 'FAILED')
    assert hasattr(StepStatus, 'SKIPPED')
    assert hasattr(StepStatus, 'ROLLED_BACK')
    assert hasattr(StepStatus, 'ROLLBACK_FAILED')


def test_execution_step_creation():
    """Test creating an ExecutionStep"""
    from luminous_nix.core.execution_plan import ExecutionStep, StepStatus

    def mock_handler(params: Dict[str, Any]) -> Any:
        return "success"

    step = ExecutionStep(
        id="step1",
        name="Test Step",
        handler=mock_handler,
        parameters={'param1': 'value1'},
        depends_on={'step0'},
        provides={'resource1'},
        requires={'resource0'}
    )

    assert step.id == "step1"
    assert step.name == "Test Step"
    assert step.handler == mock_handler
    assert step.parameters == {'param1': 'value1'}
    assert step.depends_on == {'step0'}
    assert step.provides == {'resource1'}
    assert step.requires == {'resource0'}
    assert step.status == StepStatus.PENDING
    assert step.parallelizable is True  # Default
    assert step.idempotent is False  # Default


def test_execution_step_with_rollback():
    """Test ExecutionStep with rollback handler"""
    from luminous_nix.core.execution_plan import ExecutionStep

    def mock_handler(params):
        return "executed"

    def mock_rollback(params):
        return "rolled back"

    step = ExecutionStep(
        id="step1",
        name="Test",
        handler=mock_handler,
        parameters={},
        depends_on=set(),
        provides=set(),
        requires=set(),
        rollback_handler=mock_rollback,
        can_rollback=True
    )

    assert step.rollback_handler == mock_rollback
    assert step.can_rollback is True


# === Test ExecutionPlan ===

def test_execution_plan_creation():
    """Test creating an ExecutionPlan"""
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    step1 = ExecutionStep(
        id="step1",
        name="Step 1",
        handler=lambda p: "done",
        parameters={},
        depends_on=set(),
        provides={'r1'},
        requires=set()
    )

    step2 = ExecutionStep(
        id="step2",
        name="Step 2",
        handler=lambda p: "done",
        parameters={},
        depends_on={'step1'},
        provides={'r2'},
        requires={'r1'}
    )

    plan = ExecutionPlan(steps=[step1, step2])

    assert len(plan.steps) == 2
    assert plan.steps[0].id == "step1"
    assert plan.steps[1].id == "step2"


def test_simple_linear_plan():
    """
    Test simple linear plan: A → B → C

    Expected execution order: [[A], [B], [C]]
    (Each step in its own batch)
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A",
        name="Step A",
        handler=lambda p: "done",
        parameters={},
        depends_on=set(),
        provides={'rA'},
        requires=set()
    )

    stepB = ExecutionStep(
        id="B",
        name="Step B",
        handler=lambda p: "done",
        parameters={},
        depends_on={'A'},
        provides={'rB'},
        requires={'rA'}
    )

    stepC = ExecutionStep(
        id="C",
        name="Step C",
        handler=lambda p: "done",
        parameters={},
        depends_on={'B'},
        provides={'rC'},
        requires={'rB'}
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC])

    # Should compute execution order during initialization
    assert plan.execution_order is not None
    assert len(plan.execution_order) == 3

    # Check order: A, then B, then C
    assert plan.execution_order[0] == ['A']
    assert plan.execution_order[1] == ['B']
    assert plan.execution_order[2] == ['C']


def test_parallel_execution_plan():
    """
    Test parallel execution: A → (B, C) → D

    B and C have no dependencies on each other, so can run in parallel.

    Expected execution order: [[A], [B, C], [D]]
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A",
        name="Step A",
        handler=lambda p: "done",
        parameters={},
        depends_on=set(),
        provides={'rA'},
        requires=set()
    )

    stepB = ExecutionStep(
        id="B",
        name="Step B",
        handler=lambda p: "done",
        parameters={},
        depends_on={'A'},
        provides={'rB'},
        requires={'rA'}
    )

    stepC = ExecutionStep(
        id="C",
        name="Step C",
        handler=lambda p: "done",
        parameters={},
        depends_on={'A'},
        provides={'rC'},
        requires={'rA'}
    )

    stepD = ExecutionStep(
        id="D",
        name="Step D",
        handler=lambda p: "done",
        parameters={},
        depends_on={'B', 'C'},
        provides={'rD'},
        requires={'rB', 'rC'}
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC, stepD])

    assert len(plan.execution_order) == 3
    assert plan.execution_order[0] == ['A']

    # B and C should be in same batch (parallel)
    batch2 = set(plan.execution_order[1])
    assert batch2 == {'B', 'C'}

    assert plan.execution_order[2] == ['D']


def test_cycle_detection():
    """
    Test that cycles in dependencies are detected and raise error.

    A → B → C → A (cycle!)
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A",
        name="Step A",
        handler=lambda p: "done",
        parameters={},
        depends_on={'C'},  # Depends on C (creates cycle)
        provides={'rA'},
        requires={'rC'}
    )

    stepB = ExecutionStep(
        id="B",
        name="Step B",
        handler=lambda p: "done",
        parameters={},
        depends_on={'A'},
        provides={'rB'},
        requires={'rA'}
    )

    stepC = ExecutionStep(
        id="C",
        name="Step C",
        handler=lambda p: "done",
        parameters={},
        depends_on={'B'},
        provides={'rC'},
        requires={'rB'}
    )

    # Should raise ValueError for cycle
    with pytest.raises(ValueError, match="[Cc]ycle"):
        plan = ExecutionPlan(steps=[stepA, stepB, stepC])


def test_missing_dependency_detection():
    """Test that missing dependencies are detected"""
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A",
        name="Step A",
        handler=lambda p: "done",
        parameters={},
        depends_on={'nonexistent'},  # Depends on step that doesn't exist
        provides={'rA'},
        requires=set()
    )

    # Should raise ValueError for missing dependency
    with pytest.raises(ValueError, match="dependency.*not found"):
        plan = ExecutionPlan(steps=[stepA])


def test_resource_validation():
    """
    Test that resource requirements are validated.

    Step requires 'resource1' but no previous step provides it.
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A",
        name="Step A",
        handler=lambda p: "done",
        parameters={},
        depends_on=set(),
        provides={'rA'},
        requires=set()
    )

    stepB = ExecutionStep(
        id="B",
        name="Step B",
        handler=lambda p: "done",
        parameters={},
        depends_on={'A'},
        provides={'rB'},
        requires={'rA', 'missing_resource'}  # Requires resource that's not provided
    )

    # Should raise ValueError for missing resource
    with pytest.raises(ValueError, match="resource.*(not provided|no step provides)"):
        plan = ExecutionPlan(steps=[stepA, stepB])


def test_duration_estimation_linear():
    """
    Test duration estimation for linear plan.

    A (10s) → B (20s) → C (15s)
    Expected total: 10 + 20 + 15 = 45s
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A",
        name="Step A",
        handler=lambda p: "done",
        parameters={},
        depends_on=set(),
        provides={'rA'},
        requires=set(),
        estimated_duration_s=10.0
    )

    stepB = ExecutionStep(
        id="B",
        name="Step B",
        handler=lambda p: "done",
        parameters={},
        depends_on={'A'},
        provides={'rB'},
        requires={'rA'},
        estimated_duration_s=20.0
    )

    stepC = ExecutionStep(
        id="C",
        name="Step C",
        handler=lambda p: "done",
        parameters={},
        depends_on={'B'},
        provides={'rC'},
        requires={'rB'},
        estimated_duration_s=15.0
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC])

    # Linear plan: sum of all durations
    assert plan.estimated_duration_s == 45.0


def test_duration_estimation_parallel():
    """
    Test duration estimation for parallel plan.

    A (10s) → (B (20s), C (15s)) → D (5s)

    Expected: 10 + max(20, 15) + 5 = 35s
    (B and C run in parallel, so we take the max)
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A", name="Step A", handler=lambda p: "done",
        parameters={}, depends_on=set(), provides={'rA'}, requires=set(),
        estimated_duration_s=10.0
    )

    stepB = ExecutionStep(
        id="B", name="Step B", handler=lambda p: "done",
        parameters={}, depends_on={'A'}, provides={'rB'}, requires={'rA'},
        estimated_duration_s=20.0
    )

    stepC = ExecutionStep(
        id="C", name="Step C", handler=lambda p: "done",
        parameters={}, depends_on={'A'}, provides={'rC'}, requires={'rA'},
        estimated_duration_s=15.0
    )

    stepD = ExecutionStep(
        id="D", name="Step D", handler=lambda p: "done",
        parameters={}, depends_on={'B', 'C'}, provides={'rD'}, requires={'rB', 'rC'},
        estimated_duration_s=5.0
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC, stepD])

    # Parallel plan: longest path through DAG
    assert plan.estimated_duration_s == 35.0


def test_get_next_batch():
    """
    Test getting next batch of ready-to-execute steps.

    A → (B, C) → D

    Initially: [A]
    After A: [B, C]
    After B and C: [D]
    After D: None
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep, StepStatus

    stepA = ExecutionStep(
        id="A", name="Step A", handler=lambda p: "done",
        parameters={}, depends_on=set(), provides={'rA'}, requires=set()
    )

    stepB = ExecutionStep(
        id="B", name="Step B", handler=lambda p: "done",
        parameters={}, depends_on={'A'}, provides={'rB'}, requires={'rA'}
    )

    stepC = ExecutionStep(
        id="C", name="Step C", handler=lambda p: "done",
        parameters={}, depends_on={'A'}, provides={'rC'}, requires={'rA'}
    )

    stepD = ExecutionStep(
        id="D", name="Step D", handler=lambda p: "done",
        parameters={}, depends_on={'B', 'C'}, provides={'rD'}, requires={'rB', 'rC'}
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC, stepD])

    # Get first batch
    batch1 = plan.get_next_batch()
    assert len(batch1) == 1
    assert batch1[0].id == 'A'

    # Mark A as complete
    stepA.status = StepStatus.SUCCESS

    # Get second batch
    batch2 = plan.get_next_batch()
    assert len(batch2) == 2
    batch2_ids = {s.id for s in batch2}
    assert batch2_ids == {'B', 'C'}

    # Mark B and C as complete
    stepB.status = StepStatus.SUCCESS
    stepC.status = StepStatus.SUCCESS

    # Get third batch
    batch3 = plan.get_next_batch()
    assert len(batch3) == 1
    assert batch3[0].id == 'D'

    # Mark D as complete
    stepD.status = StepStatus.SUCCESS

    # No more batches
    batch4 = plan.get_next_batch()
    assert batch4 is None or len(batch4) == 0


def test_rollback_order():
    """
    Test getting rollback order (reverse of execution).

    Execution: A → B → C
    Rollback: C → B → A
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep, StepStatus

    def mock_handler(p):
        return "done"

    def mock_rollback(p):
        return "undone"

    stepA = ExecutionStep(
        id="A", name="Step A", handler=mock_handler, rollback_handler=mock_rollback,
        parameters={}, depends_on=set(), provides={'rA'}, requires=set()
    )

    stepB = ExecutionStep(
        id="B", name="Step B", handler=mock_handler, rollback_handler=mock_rollback,
        parameters={}, depends_on={'A'}, provides={'rB'}, requires={'rA'}
    )

    stepC = ExecutionStep(
        id="C", name="Step C", handler=mock_handler, rollback_handler=mock_rollback,
        parameters={}, depends_on={'B'}, provides={'rC'}, requires={'rB'}
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC])

    # Mark steps as executed (so they can be rolled back)
    stepA.status = StepStatus.SUCCESS
    stepB.status = StepStatus.SUCCESS
    stepC.status = StepStatus.SUCCESS

    rollback_order = plan.get_rollback_order()

    # Should be reverse order
    assert len(rollback_order) == 3
    assert rollback_order[0].id == 'C'
    assert rollback_order[1].id == 'B'
    assert rollback_order[2].id == 'A'


def test_complex_plan_python_dev_environment():
    """
    Test complex real-world plan: Setup Python Dev Environment

    Steps:
    1. check_python_installed
    2. install_python (depends on 1 if needed)
    3. install_poetry (parallel with 4)
    4. install_git (parallel with 3)
    5. create_shell_nix (depends on 2, 3, 4)
    6. test_shell (parallel with 7, depends on 5)
    7. create_direnv (parallel with 6, depends on 5)

    Expected batches:
    [check_python], [install_python], [install_poetry, install_git],
    [create_shell_nix], [test_shell, create_direnv]
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    steps = []

    # Step 1: Check Python
    steps.append(ExecutionStep(
        id="check_python",
        name="Check Python Installed",
        handler=lambda p: True,
        parameters={},
        depends_on=set(),
        provides={'python_check'},
        requires=set(),
        estimated_duration_s=2.0
    ))

    # Step 2: Install Python
    steps.append(ExecutionStep(
        id="install_python",
        name="Install Python",
        handler=lambda p: "installed",
        parameters={'version': '3.11'},
        depends_on={'check_python'},
        provides={'python'},
        requires={'python_check'},
        estimated_duration_s=30.0
    ))

    # Step 3: Install Poetry (parallel with git)
    steps.append(ExecutionStep(
        id="install_poetry",
        name="Install Poetry",
        handler=lambda p: "installed",
        parameters={},
        depends_on={'install_python'},
        provides={'poetry'},
        requires={'python'},
        estimated_duration_s=15.0
    ))

    # Step 4: Install Git (parallel with poetry)
    steps.append(ExecutionStep(
        id="install_git",
        name="Install Git",
        handler=lambda p: "installed",
        parameters={},
        depends_on={'install_python'},
        provides={'git'},
        requires={'python'},
        estimated_duration_s=10.0
    ))

    # Step 5: Create shell.nix
    steps.append(ExecutionStep(
        id="create_shell_nix",
        name="Create shell.nix",
        handler=lambda p: "created",
        parameters={},
        depends_on={'install_python', 'install_poetry', 'install_git'},
        provides={'shell_nix'},
        requires={'python', 'poetry', 'git'},
        estimated_duration_s=5.0
    ))

    # Step 6: Test shell (parallel with direnv)
    steps.append(ExecutionStep(
        id="test_shell",
        name="Test Nix Shell",
        handler=lambda p: "tested",
        parameters={},
        depends_on={'create_shell_nix'},
        provides={'shell_tested'},
        requires={'shell_nix'},
        estimated_duration_s=10.0
    ))

    # Step 7: Create .envrc (parallel with test)
    steps.append(ExecutionStep(
        id="create_envrc",
        name="Create .envrc",
        handler=lambda p: "created",
        parameters={},
        depends_on={'create_shell_nix'},
        provides={'direnv'},
        requires={'shell_nix'},
        estimated_duration_s=1.5
    ))

    plan = ExecutionPlan(steps=steps)

    # Check execution order has 5 batches
    assert len(plan.execution_order) == 5

    # Check first batch
    assert plan.execution_order[0] == ['check_python']

    # Check second batch
    assert plan.execution_order[1] == ['install_python']

    # Check third batch (poetry and git in parallel)
    batch3 = set(plan.execution_order[2])
    assert batch3 == {'install_poetry', 'install_git'}

    # Check fourth batch
    assert plan.execution_order[3] == ['create_shell_nix']

    # Check fifth batch (test and direnv in parallel)
    batch5 = set(plan.execution_order[4])
    assert batch5 == {'test_shell', 'create_envrc'}

    # Check duration estimation
    # Path: check(2) → install_python(30) → install_poetry(15) → create_shell(5) → test_shell(10) = 62s
    # OR: check(2) → install_python(30) → install_git(10) → create_shell(5) → test_shell(10) = 57s
    # Longest path is 62s + max(10, 1.5) for last batch = 72s
    expected_duration = 2 + 30 + max(15, 10) + 5 + max(10, 1.5)
    assert plan.estimated_duration_s == expected_duration  # Should be 62s


# === Test Edge Cases ===

def test_empty_plan():
    """Test creating plan with no steps"""
    from luminous_nix.core.execution_plan import ExecutionPlan

    plan = ExecutionPlan(steps=[])

    assert len(plan.steps) == 0
    assert plan.execution_order == []
    assert plan.estimated_duration_s == 0.0


def test_single_step_plan():
    """Test plan with single step"""
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    step = ExecutionStep(
        id="only",
        name="Only Step",
        handler=lambda p: "done",
        parameters={},
        depends_on=set(),
        provides=set(),
        requires=set(),
        estimated_duration_s=10.0
    )

    plan = ExecutionPlan(steps=[step])

    assert len(plan.execution_order) == 1
    assert plan.execution_order[0] == ['only']
    assert plan.estimated_duration_s == 10.0


def test_diamond_dependency():
    """
    Test diamond dependency pattern:

        A
       / \\
      B   C
       \\ /
        D

    A → (B, C) → D
    """
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    stepA = ExecutionStep(
        id="A", name="A", handler=lambda p: "done",
        parameters={}, depends_on=set(), provides={'rA'}, requires=set()
    )

    stepB = ExecutionStep(
        id="B", name="B", handler=lambda p: "done",
        parameters={}, depends_on={'A'}, provides={'rB'}, requires={'rA'}
    )

    stepC = ExecutionStep(
        id="C", name="C", handler=lambda p: "done",
        parameters={}, depends_on={'A'}, provides={'rC'}, requires={'rA'}
    )

    stepD = ExecutionStep(
        id="D", name="D", handler=lambda p: "done",
        parameters={}, depends_on={'B', 'C'}, provides={'rD'}, requires={'rB', 'rC'}
    )

    plan = ExecutionPlan(steps=[stepA, stepB, stepC, stepD])

    # Should have 3 batches
    assert len(plan.execution_order) == 3
    assert plan.execution_order[0] == ['A']
    assert set(plan.execution_order[1]) == {'B', 'C'}
    assert plan.execution_order[2] == ['D']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
