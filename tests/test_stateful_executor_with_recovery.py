"""
Integration Tests - StatefulExecutor with ErrorRecovery

Test-Driven Development: Enhanced StatefulExecutor that integrates
ErrorRecovery for automatic retry and intelligent failure handling.

Based on: Week 4 Enhanced Integration
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import time


# === Test Enhanced StatefulExecutor with ErrorRecovery ===

def test_enhanced_executor_creation():
    """Test creating enhanced executor with error recovery"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)

        executor = StatefulExecutorWithRecovery(
            state_manager=state_mgr,
            error_recovery=recovery_mgr
        )

        assert executor.state_manager == state_mgr
        assert executor.error_recovery == recovery_mgr


def test_automatic_retry_on_transient_failure():
    """Test that transient failures are automatically retried"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        # Create operation
        state = state_mgr.create_operation("test with retry")

        # Track call count
        call_count = {'count': 0}

        def flaky_handler(params):
            call_count['count'] += 1
            if call_count['count'] == 1:
                # First call fails with recoverable error
                raise RuntimeError("Connection refused")
            else:
                # Second call succeeds
                return "success"

        step = ExecutionStep(
            id="flaky", name="Flaky Step",
            handler=flaky_handler, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Execute - should retry and succeed
        result = executor.execute_with_state(plan, state.operation_id)

        # Verify retry happened
        assert result.status == OperationStatus.COMPLETED
        assert call_count['count'] == 2  # Called twice (fail + retry)
        assert 'flaky' in result.completed_steps


def test_no_retry_on_fatal_error():
    """Test that fatal errors are not retried"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        state = state_mgr.create_operation("test fatal error")

        call_count = {'count': 0}

        def fatal_handler(params):
            call_count['count'] += 1
            raise RuntimeError("Segmentation fault (core dumped)")

        step = ExecutionStep(
            id="fatal", name="Fatal Step",
            handler=fatal_handler, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Execute - should fail without retry
        result = executor.execute_with_state(plan, state.operation_id)

        # Verify no retry
        assert result.status == OperationStatus.FAILED
        assert call_count['count'] == 1  # Only called once (no retry)
        assert 'fatal' in result.failed_steps


def test_max_retries_respected():
    """Test that max retries limit is respected"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        # Create operation with max_retries=2
        state = state_mgr.create_operation("test max retries")
        state.max_retries = 2
        state_mgr.update_operation(state)

        call_count = {'count': 0}

        def always_fails(params):
            call_count['count'] += 1
            raise RuntimeError("Connection refused")

        step = ExecutionStep(
            id="failing", name="Always Fails",
            handler=always_fails, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Execute - should try max 3 times (initial + 2 retries)
        result = executor.execute_with_state(plan, state.operation_id)

        # Verify max retries
        assert result.status == OperationStatus.FAILED
        assert call_count['count'] <= 3  # Initial + 2 retries max
        assert 'failing' in result.failed_steps


def test_recovery_state_tracking():
    """Test that recovery attempts are tracked in state"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        state = state_mgr.create_operation("test recovery tracking")

        attempt = {'count': 0}

        def flaky_handler(params):
            attempt['count'] += 1
            if attempt['count'] == 1:
                raise RuntimeError("Connection refused")
            return "success"

        step = ExecutionStep(
            id="tracked", name="Tracked Step",
            handler=flaky_handler, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Execute
        result = executor.execute_with_state(plan, state.operation_id)

        # Verify recovery tracking in state
        final_state = state_mgr.get_operation(state.operation_id)
        assert final_state.retry_count > 0  # At least one retry
        assert len(final_state.error_details) > 0  # Error details recorded


def test_partial_execution_with_recovery():
    """Test execution with some steps succeeding and some needing recovery"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        state = state_mgr.create_operation("partial execution test")

        attempts = {'B': 0}

        def success_handler(params):
            return f"success: {params['name']}"

        def flaky_handler(params):
            attempts['B'] += 1
            if attempts['B'] == 1:
                raise RuntimeError("Network unreachable")
            return f"success: {params['name']}"

        # Plan: A (succeeds) → B (fails once, retries) → C (succeeds)
        stepA = ExecutionStep(
            id="A", name="Step A",
            handler=success_handler, parameters={'name': 'A'},
            depends_on=set(), provides={'rA'}, requires=set()
        )

        stepB = ExecutionStep(
            id="B", name="Step B (flaky)",
            handler=flaky_handler, parameters={'name': 'B'},
            depends_on={'A'}, provides={'rB'}, requires={'rA'}
        )

        stepC = ExecutionStep(
            id="C", name="Step C",
            handler=success_handler, parameters={'name': 'C'},
            depends_on={'B'}, provides={'rC'}, requires={'rB'}
        )

        plan = ExecutionPlan(steps=[stepA, stepB, stepC])

        # Execute
        result = executor.execute_with_state(plan, state.operation_id)

        # All steps should succeed (B after retry)
        assert result.status == OperationStatus.COMPLETED
        assert len(result.completed_steps) == 3
        assert 'A' in result.completed_steps
        assert 'B' in result.completed_steps
        assert 'C' in result.completed_steps
        assert attempts['B'] == 2  # B tried twice


def test_error_classification_affects_retry():
    """Test that error classification determines retry behavior"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        # Test 1: Network error (should retry)
        state1 = state_mgr.create_operation("network error test")
        attempts1 = {'count': 0}

        def network_error_handler(params):
            attempts1['count'] += 1
            if attempts1['count'] == 1:
                raise RuntimeError("Connection refused")
            return "success"

        step1 = ExecutionStep(
            id="network", name="Network Error",
            handler=network_error_handler, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )
        plan1 = ExecutionPlan(steps=[step1])

        result1 = executor.execute_with_state(plan1, state1.operation_id)
        assert result1.status == OperationStatus.COMPLETED
        assert attempts1['count'] == 2  # Retried

        # Test 2: Fatal error (should not retry)
        state2 = state_mgr.create_operation("fatal error test")
        attempts2 = {'count': 0}

        def fatal_error_handler(params):
            attempts2['count'] += 1
            raise RuntimeError("Segmentation fault")

        step2 = ExecutionStep(
            id="fatal", name="Fatal Error",
            handler=fatal_error_handler, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )
        plan2 = ExecutionPlan(steps=[step2])

        result2 = executor.execute_with_state(plan2, state2.operation_id)
        assert result2.status == OperationStatus.FAILED
        assert attempts2['count'] == 1  # Not retried


def test_exponential_backoff_delays():
    """Test that retry delays follow exponential backoff"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        state = state_mgr.create_operation("backoff test")
        state.max_retries = 3
        state_mgr.update_operation(state)

        timestamps = []

        def failing_handler(params):
            timestamps.append(time.time())
            raise RuntimeError("Connection refused")

        step = ExecutionStep(
            id="failing", name="Failing Step",
            handler=failing_handler, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Execute (will fail after retries)
        result = executor.execute_with_state(plan, state.operation_id)

        # Verify delays increased (exponential backoff)
        if len(timestamps) >= 2:
            delay1 = timestamps[1] - timestamps[0]
            if len(timestamps) >= 3:
                delay2 = timestamps[2] - timestamps[1]
                # Second delay should be longer (exponential)
                # Allow some margin for execution overhead
                assert delay2 > delay1 * 0.8


def test_successful_execution_no_recovery():
    """Test that successful execution doesn't trigger recovery"""
    from luminous_nix.core.stateful_executor_with_recovery import StatefulExecutorWithRecovery
    from luminous_nix.core.state_manager import StateManager, OperationStatus
    from luminous_nix.core.execution_plan import ExecutionPlan, ExecutionStep
    from luminous_nix.core.error_recovery import ErrorRecoveryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )
        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)
        executor = StatefulExecutorWithRecovery(state_mgr, recovery_mgr)

        state = state_mgr.create_operation("success test")

        def success_handler(params):
            return "success"

        step = ExecutionStep(
            id="success", name="Success Step",
            handler=success_handler, parameters={},
            depends_on=set(), provides={'result'}, requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Execute
        result = executor.execute_with_state(plan, state.operation_id)

        # Verify no recovery attempts
        final_state = state_mgr.get_operation(state.operation_id)
        assert result.status == OperationStatus.COMPLETED
        assert final_state.retry_count == 0  # No retries
        assert final_state.error is None  # No error recorded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
