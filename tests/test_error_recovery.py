"""
Tests for ErrorRecovery Framework

Test-Driven Development: Core error recovery functionality.
This is a focused, production-ready implementation covering essential features.

Based on design from: DEEP_DIVE_ERROR_RECOVERY.md
"""

import pytest
import tempfile
from pathlib import Path
import time


# === Test Error Classification ===

def test_error_category_enum():
    """Test ErrorCategory enum exists with core values"""
    from luminous_nix.core.error_recovery import ErrorCategory

    assert hasattr(ErrorCategory, 'NETWORK')
    assert hasattr(ErrorCategory, 'RESOURCE')
    assert hasattr(ErrorCategory, 'DEPENDENCY')
    assert hasattr(ErrorCategory, 'AUTHENTICATION')
    assert hasattr(ErrorCategory, 'CONFIGURATION')
    assert hasattr(ErrorCategory, 'TIMEOUT')
    assert hasattr(ErrorCategory, 'UNKNOWN')


def test_error_severity_enum():
    """Test ErrorSeverity enum"""
    from luminous_nix.core.error_recovery import ErrorSeverity

    assert hasattr(ErrorSeverity, 'FATAL')
    assert hasattr(ErrorSeverity, 'CRITICAL')
    assert hasattr(ErrorSeverity, 'HIGH')
    assert hasattr(ErrorSeverity, 'MEDIUM')
    assert hasattr(ErrorSeverity, 'LOW')


def test_recoverability_level_enum():
    """Test RecoverabilityLevel enum"""
    from luminous_nix.core.error_recovery import RecoverabilityLevel

    assert hasattr(RecoverabilityLevel, 'AUTO_RECOVERABLE')
    assert hasattr(RecoverabilityLevel, 'RETRY_RECOVERABLE')
    assert hasattr(RecoverabilityLevel, 'FALLBACK_RECOVERABLE')
    assert hasattr(RecoverabilityLevel, 'USER_RECOVERABLE')
    assert hasattr(RecoverabilityLevel, 'NOT_RECOVERABLE')


def test_classified_error_creation():
    """Test creating ClassifiedError"""
    from luminous_nix.core.error_recovery import (
        ClassifiedError,
        ErrorCategory,
        ErrorSeverity,
        RecoverabilityLevel
    )

    error = ClassifiedError(
        message="Connection refused",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
        operation_id="test_op"
    )

    assert error.message == "Connection refused"
    assert error.category == ErrorCategory.NETWORK
    assert error.severity == ErrorSeverity.HIGH
    assert error.can_retry is True


def test_error_classifier_network_error():
    """Test classifying network errors"""
    from luminous_nix.core.error_recovery import ErrorClassifier, ErrorCategory

    classifier = ErrorClassifier()

    # Test various network error messages
    error1 = classifier.classify("Connection refused")
    assert error1.category == ErrorCategory.NETWORK

    error2 = classifier.classify("Network unreachable")
    assert error2.category == ErrorCategory.NETWORK

    error3 = classifier.classify("Temporary failure in name resolution")
    assert error3.category == ErrorCategory.NETWORK


def test_error_classifier_resource_error():
    """Test classifying resource errors"""
    from luminous_nix.core.error_recovery import ErrorClassifier, ErrorCategory

    classifier = ErrorClassifier()

    error1 = classifier.classify("No space left on device")
    assert error1.category == ErrorCategory.RESOURCE

    error2 = classifier.classify("Disk quota exceeded")
    assert error2.category == ErrorCategory.RESOURCE


def test_error_classifier_dependency_error():
    """Test classifying dependency errors"""
    from luminous_nix.core.error_recovery import ErrorClassifier, ErrorCategory

    classifier = ErrorClassifier()

    error1 = classifier.classify("hash mismatch in fixed-output derivation")
    assert error1.category == ErrorCategory.DEPENDENCY

    error2 = classifier.classify("Package collision detected")
    assert error2.category == ErrorCategory.DEPENDENCY


# === Test Recovery Decision Making ===

def test_recovery_action_creation():
    """Test creating RecoveryAction"""
    from luminous_nix.core.error_recovery import RecoveryAction

    def mock_handler(error, context):
        return True

    action = RecoveryAction(
        name="test_action",
        description="Test recovery action",
        handler=mock_handler,
        estimated_time_s=5.0
    )

    assert action.name == "test_action"
    assert action.description == "Test recovery action"
    assert action.estimated_time_s == 5.0


def test_recovery_decision_tree_network_error():
    """Test recovery decisions for network errors"""
    from luminous_nix.core.error_recovery import (
        RecoveryDecisionTree,
        ClassifiedError,
        ErrorCategory,
        ErrorSeverity,
        RecoverabilityLevel
    )

    tree = RecoveryDecisionTree()

    error = ClassifiedError(
        message="Connection refused",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
        operation_id="test"
    )

    actions = tree.decide_recovery(error)

    assert len(actions) > 0
    # Should suggest retry-related actions
    action_names = [a.name for a in actions]
    assert 'wait_and_retry' in action_names


def test_recovery_decision_tree_resource_error():
    """Test recovery decisions for resource errors"""
    from luminous_nix.core.error_recovery import (
        RecoveryDecisionTree,
        ClassifiedError,
        ErrorCategory,
        ErrorSeverity,
        RecoverabilityLevel
    )

    tree = RecoveryDecisionTree()

    error = ClassifiedError(
        message="No space left on device",
        category=ErrorCategory.RESOURCE,
        severity=ErrorSeverity.CRITICAL,
        recoverability=RecoverabilityLevel.AUTO_RECOVERABLE,
        operation_id="test"
    )

    actions = tree.decide_recovery(error)

    assert len(actions) > 0
    action_names = [a.name for a in actions]
    # Should suggest cleanup actions
    assert any('cleanup' in name or 'garbage' in name for name in action_names)


# === Test Retry Strategy ===

def test_retry_strategy_exponential_backoff():
    """Test retry with exponential backoff"""
    from luminous_nix.core.error_recovery import RetryStrategy

    strategy = RetryStrategy(
        max_retries=3,
        base_delay_s=1.0,
        max_delay_s=10.0,
        exponential_base=2.0
    )

    # Test delay calculations
    assert strategy.get_delay(attempt=0) == 1.0  # 1 * 2^0
    assert strategy.get_delay(attempt=1) == 2.0  # 1 * 2^1
    assert strategy.get_delay(attempt=2) == 4.0  # 1 * 2^2
    assert strategy.get_delay(attempt=3) <= 10.0  # Capped at max_delay


def test_retry_strategy_should_retry():
    """Test retry decision logic"""
    from luminous_nix.core.error_recovery import RetryStrategy

    strategy = RetryStrategy(max_retries=3)

    assert strategy.should_retry(attempt=0) is True
    assert strategy.should_retry(attempt=1) is True
    assert strategy.should_retry(attempt=2) is True
    assert strategy.should_retry(attempt=3) is False  # Max retries reached


# === Test ErrorRecoveryManager Integration ===

def test_error_recovery_manager_creation():
    """Test creating ErrorRecoveryManager"""
    from luminous_nix.core.error_recovery import ErrorRecoveryManager
    from luminous_nix.core.state_manager import StateManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=manager)

        assert recovery_mgr.state_manager == manager
        assert recovery_mgr.classifier is not None
        assert recovery_mgr.decision_tree is not None


def test_error_recovery_classify_and_decide():
    """Test classify error and decide recovery"""
    from luminous_nix.core.error_recovery import (
        ErrorRecoveryManager,
        ErrorCategory
    )
    from luminous_nix.core.state_manager import StateManager

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)

        # Classify
        error = recovery_mgr.classifier.classify("Connection refused")
        assert error.category == ErrorCategory.NETWORK

        # Decide recovery
        actions = recovery_mgr.decision_tree.decide_recovery(error)
        assert len(actions) > 0


def test_error_recovery_full_flow_recoverable():
    """Test full recovery flow for recoverable error"""
    from luminous_nix.core.error_recovery import ErrorRecoveryManager
    from luminous_nix.core.state_manager import StateManager, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)

        # Create operation
        state = state_mgr.create_operation("test operation")
        state.status = OperationStatus.EXECUTING
        state_mgr.update_operation(state)

        # Simulate recoverable error (network)
        outcome = recovery_mgr.handle_error(
            operation_id=state.operation_id,
            error_message="Connection refused - temporary network issue",
            command="nix-build"
        )

        # Should attempt recovery
        assert outcome is not None
        assert outcome.error.category.value == "network"


def test_error_recovery_non_recoverable():
    """Test handling of non-recoverable errors"""
    from luminous_nix.core.error_recovery import (
        ErrorRecoveryManager,
        ErrorSeverity
    )
    from luminous_nix.core.state_manager import StateManager, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)

        # Create operation
        state = state_mgr.create_operation("test operation")
        state.status = OperationStatus.EXECUTING
        state_mgr.update_operation(state)

        # Simulate fatal error
        outcome = recovery_mgr.handle_error(
            operation_id=state.operation_id,
            error_message="Segmentation fault (core dumped)",
            command="nix-build"
        )

        # Should not recover
        assert outcome.recovered is False


def test_error_recovery_max_retries():
    """Test that max retries limit is respected"""
    from luminous_nix.core.error_recovery import ErrorRecoveryManager
    from luminous_nix.core.state_manager import StateManager, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)

        # Create operation with retry count at max
        state = state_mgr.create_operation("test operation")
        state.status = OperationStatus.EXECUTING
        state.retry_count = 3  # At max retries
        state.max_retries = 3
        state_mgr.update_operation(state)

        # Try to recover
        outcome = recovery_mgr.handle_error(
            operation_id=state.operation_id,
            error_message="Connection refused",
            command="nix-build"
        )

        # Should not attempt recovery (max retries reached)
        assert outcome.recovered is False


def test_error_recovery_state_update():
    """Test that state is updated with error details"""
    from luminous_nix.core.error_recovery import ErrorRecoveryManager
    from luminous_nix.core.state_manager import StateManager, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)

        # Create operation
        state = state_mgr.create_operation("test operation")
        state.status = OperationStatus.EXECUTING
        state_mgr.update_operation(state)

        # Handle error
        recovery_mgr.handle_error(
            operation_id=state.operation_id,
            error_message="Test error message",
            stderr="Error output",
            exit_code=1,
            command="test-command"
        )

        # Verify state was updated
        updated_state = state_mgr.get_operation(state.operation_id)
        assert updated_state.error is not None
        assert "Test error message" in updated_state.error
        assert len(updated_state.error_details) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
