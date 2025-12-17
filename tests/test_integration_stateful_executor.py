"""
Integration Tests - StatefulExecutor (ExecutionPlan + StateManager)

Test-Driven Development: These tests are written FIRST to define how
ExecutionPlan and StateManager integrate together.

Based on design from: DEEP_DIVE_STATE_MANAGEMENT.md Part 8
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import time


# === Test StatefulExecutor Integration ===

def test_stateful_executor_creation():
    """Test creating StatefulExecutor"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)

        assert executor.state_manager == manager


def test_execute_simple_plan_with_state():
    """Test executing a simple 3-step plan with state tracking"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)

        # Create operation
        state = manager.create_operation("install firefox")

        # Create simple plan: A → B → C
        def mock_handler(params):
            return f"Result: {params.get('name', 'unknown')}"

        stepA = ExecutionStep(
            id="A", name="Step A",
            handler=mock_handler,
            parameters={'name': 'A'},
            depends_on=set(),
            provides={'rA'},
            requires=set(),
            estimated_duration_s=0.1
        )

        stepB = ExecutionStep(
            id="B", name="Step B",
            handler=mock_handler,
            parameters={'name': 'B'},
            depends_on={'A'},
            provides={'rB'},
            requires={'rA'},
            estimated_duration_s=0.1
        )

        stepC = ExecutionStep(
            id="C", name="Step C",
            handler=mock_handler,
            parameters={'name': 'C'},
            depends_on={'B'},
            provides={'rC'},
            requires={'rB'},
            estimated_duration_s=0.1
        )

        plan = ExecutionPlan(steps=[stepA, stepB, stepC])

        # Execute with state tracking
        result_state = executor.execute_with_state(plan, state.operation_id)

        # Verify state
        assert result_state.status == OperationStatus.COMPLETED
        assert len(result_state.completed_steps) == 3
        assert 'A' in result_state.completed_steps
        assert 'B' in result_state.completed_steps
        assert 'C' in result_state.completed_steps
        assert len(result_state.failed_steps) == 0
        assert result_state.completed_at is not None


def test_execute_parallel_plan_with_state():
    """Test executing plan with parallel steps: A → (B, C) → D"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)
        state = manager.create_operation("parallel test")

        # Track execution order
        execution_log = []

        def logged_handler(params):
            execution_log.append(params['name'])
            time.sleep(0.05)  # Simulate work
            return f"Result: {params['name']}"

        # A → (B, C) → D
        stepA = ExecutionStep(
            id="A", name="Step A",
            handler=logged_handler,
            parameters={'name': 'A'},
            depends_on=set(),
            provides={'rA'},
            requires=set()
        )

        stepB = ExecutionStep(
            id="B", name="Step B",
            handler=logged_handler,
            parameters={'name': 'B'},
            depends_on={'A'},
            provides={'rB'},
            requires={'rA'}
        )

        stepC = ExecutionStep(
            id="C", name="Step C",
            handler=logged_handler,
            parameters={'name': 'C'},
            depends_on={'A'},
            provides={'rC'},
            requires={'rA'}
        )

        stepD = ExecutionStep(
            id="D", name="Step D",
            handler=logged_handler,
            parameters={'name': 'D'},
            depends_on={'B', 'C'},
            provides={'rD'},
            requires={'rB', 'rC'}
        )

        plan = ExecutionPlan(steps=[stepA, stepB, stepC, stepD])

        # Execute
        result_state = executor.execute_with_state(plan, state.operation_id)

        # Verify state
        assert result_state.status == OperationStatus.COMPLETED
        assert len(result_state.completed_steps) == 4

        # Verify execution order (B and C can be in any order, but A before them, D after)
        assert execution_log[0] == 'A'  # A first
        assert execution_log[-1] == 'D'  # D last
        assert 'B' in execution_log[1:3]  # B and C in middle
        assert 'C' in execution_log[1:3]


def test_state_tracking_during_execution():
    """Test that state is updated during execution"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)
        state = manager.create_operation("test")

        # Create plan with steps that verify state
        state_snapshots = []

        def capture_state_handler(params):
            # Get current state from manager
            current = manager.get_operation(state.operation_id)
            state_snapshots.append({
                'step': params['name'],
                'status': current.status,
                'completed': len(current.completed_steps),
                'current_step': current.current_step_id
            })
            time.sleep(0.05)
            return "ok"

        steps = []
        for i in range(3):
            steps.append(ExecutionStep(
                id=f"step{i}",
                name=f"Step {i}",
                handler=capture_state_handler,
                parameters={'name': f"step{i}"},
                depends_on={f"step{i-1}"} if i > 0 else set(),
                provides={f"r{i}"},
                requires={f"r{i-1}"} if i > 0 else set()
            ))

        plan = ExecutionPlan(steps=steps)

        # Execute
        result_state = executor.execute_with_state(plan, state.operation_id)

        # Verify state was tracked
        assert len(state_snapshots) == 3

        # Each step should see status as EXECUTING
        for snapshot in state_snapshots:
            assert snapshot['status'] == OperationStatus.EXECUTING


def test_checkpoint_creation_after_batches():
    """Test that checkpoints are created after each batch"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)
        state = manager.create_operation("checkpoint test")

        def simple_handler(params):
            return "ok"

        # Create plan: A → (B, C) → D
        # Should create checkpoints after batches [A], [B,C], [D]
        stepA = ExecutionStep(
            id="A", name="A",
            handler=simple_handler, parameters={},
            depends_on=set(), provides={'rA'}, requires=set()
        )

        stepB = ExecutionStep(
            id="B", name="B",
            handler=simple_handler, parameters={},
            depends_on={'A'}, provides={'rB'}, requires={'rA'}
        )

        stepC = ExecutionStep(
            id="C", name="C",
            handler=simple_handler, parameters={},
            depends_on={'A'}, provides={'rC'}, requires={'rA'}
        )

        stepD = ExecutionStep(
            id="D", name="D",
            handler=simple_handler, parameters={},
            depends_on={'B', 'C'}, provides={'rD'}, requires={'rB', 'rC'}
        )

        plan = ExecutionPlan(steps=[stepA, stepB, stepC, stepD])

        # Execute
        result_state = executor.execute_with_state(plan, state.operation_id)

        # Verify checkpoint was created
        assert len(result_state.checkpoint_data) > 0
        assert 'completed_steps' in result_state.checkpoint_data


def test_execution_failure_handling():
    """Test that failures are handled gracefully"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)
        state = manager.create_operation("failure test")

        def success_handler(params):
            return "ok"

        def failing_handler(params):
            raise RuntimeError("Simulated failure")

        # Create plan: A → B (fails) → C (should not run)
        stepA = ExecutionStep(
            id="A", name="Step A",
            handler=success_handler, parameters={},
            depends_on=set(), provides={'rA'}, requires=set()
        )

        stepB = ExecutionStep(
            id="B", name="Step B (fails)",
            handler=failing_handler, parameters={},
            depends_on={'A'}, provides={'rB'}, requires={'rA'}
        )

        stepC = ExecutionStep(
            id="C", name="Step C",
            handler=success_handler, parameters={},
            depends_on={'B'}, provides={'rC'}, requires={'rB'}
        )

        plan = ExecutionPlan(steps=[stepA, stepB, stepC])

        # Execute (should fail)
        result_state = executor.execute_with_state(plan, state.operation_id)

        # Verify failure handling
        assert result_state.status == OperationStatus.FAILED
        assert 'A' in result_state.completed_steps  # A succeeded
        assert 'B' in result_state.failed_steps     # B failed
        assert 'C' not in result_state.completed_steps  # C never ran
        assert result_state.error is not None
        assert "Simulated failure" in result_state.error


def test_retrieve_state_after_execution():
    """Test that state can be retrieved after execution completes"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)
        state = manager.create_operation("retrieval test")
        op_id = state.operation_id

        def simple_handler(params):
            return "ok"

        stepA = ExecutionStep(
            id="A", name="Step A",
            handler=simple_handler, parameters={},
            depends_on=set(), provides={'rA'}, requires=set()
        )

        plan = ExecutionPlan(steps=[stepA])

        # Execute
        executor.execute_with_state(plan, op_id)

        # Retrieve state from database
        retrieved = manager.get_operation(op_id)

        assert retrieved is not None
        assert retrieved.operation_id == op_id
        assert retrieved.status == OperationStatus.COMPLETED
        assert 'A' in retrieved.completed_steps


def test_stateful_execution_with_complex_plan():
    """Test complex 7-step plan with state tracking"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)
        state = manager.create_operation("setup python dev environment")

        # Use the Python dev environment example from ExecutionPlan tests
        def mock_handler(params):
            return {"status": "success", "action": params.get('action', 'unknown')}

        steps = [
            ExecutionStep(
                id="check_python", name="Check Python",
                handler=mock_handler, parameters={'action': 'check'},
                depends_on=set(), provides={'python_checked'}, requires=set()
            ),
            ExecutionStep(
                id="install_python", name="Install Python",
                handler=mock_handler, parameters={'action': 'install_python'},
                depends_on={'check_python'}, provides={'python'}, requires={'python_checked'}
            ),
            ExecutionStep(
                id="install_poetry", name="Install Poetry",
                handler=mock_handler, parameters={'action': 'install_poetry'},
                depends_on={'install_python'}, provides={'poetry'}, requires={'python'}
            ),
            ExecutionStep(
                id="install_git", name="Install Git",
                handler=mock_handler, parameters={'action': 'install_git'},
                depends_on={'install_python'}, provides={'git'}, requires={'python'}
            ),
            ExecutionStep(
                id="create_shell_nix", name="Create shell.nix",
                handler=mock_handler, parameters={'action': 'create_shell'},
                depends_on={'install_poetry', 'install_git'},
                provides={'shell_nix'}, requires={'poetry', 'git'}
            ),
            ExecutionStep(
                id="test_shell", name="Test shell",
                handler=mock_handler, parameters={'action': 'test'},
                depends_on={'create_shell_nix'}, provides={'tested'}, requires={'shell_nix'}
            ),
            ExecutionStep(
                id="create_envrc", name="Create .envrc",
                handler=mock_handler, parameters={'action': 'create_envrc'},
                depends_on={'create_shell_nix'}, provides={'envrc'}, requires={'shell_nix'}
            )
        ]

        plan = ExecutionPlan(steps=steps)

        # Execute
        result_state = executor.execute_with_state(plan, state.operation_id)

        # Verify all steps completed
        assert result_state.status == OperationStatus.COMPLETED
        assert len(result_state.completed_steps) == 7
        assert len(result_state.failed_steps) == 0


def test_execution_plan_attached_to_state():
    """Test that ExecutionPlan is properly attached to OperationState"""
    from luminous_nix.core.stateful_executor import StatefulExecutor
    from luminous_nix.core.state_manager import StateManager
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)
        state = manager.create_operation("test")

        def simple_handler(params):
            return "ok"

        step = ExecutionStep(
            id="A", name="Step A",
            handler=simple_handler, parameters={},
            depends_on=set(), provides={'rA'}, requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Before execution - no plan
        pre_state = manager.get_operation(state.operation_id)
        assert pre_state.execution_plan is None

        # Execute
        executor.execute_with_state(plan, state.operation_id)

        # After execution - plan attached
        post_state = manager.get_operation(state.operation_id)
        assert post_state.execution_plan is not None
        assert len(post_state.execution_plan.steps) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
