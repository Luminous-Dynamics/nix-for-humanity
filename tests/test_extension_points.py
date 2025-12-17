"""
Test-Driven Development: Extension Points

Tests for extension point interfaces that enable plugins to extend
core functionality through well-defined interfaces.

Based on: Week 6 Extension Points
"""

import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


# === Test StepHandler Extension Point ===

def test_step_handler_interface():
    """Test that StepHandler defines correct interface"""
    from luminous_nix.core.extension_points import StepHandler
    from luminous_nix.core.execution_plan import ExecutionStep

    class CustomStepHandler(StepHandler):
        def can_handle(self, step_type: str) -> bool:
            return step_type == "custom"

        def execute(self, step: ExecutionStep, context: Dict[str, Any]) -> Any:
            return f"Executed {step.name}"

    handler = CustomStepHandler()
    assert handler.can_handle("custom")
    assert not handler.can_handle("other")


def test_step_handler_execution():
    """Test executing a custom step through handler"""
    from luminous_nix.core.extension_points import StepHandler
    from luminous_nix.core.execution_plan import ExecutionStep

    class CustomStepHandler(StepHandler):
        def can_handle(self, step_type: str) -> bool:
            return step_type == "custom"

        def execute(self, step: ExecutionStep, context: Dict[str, Any]) -> Any:
            return {"result": "success", "data": context.get("input", "")}

    handler = CustomStepHandler()

    # Create a step
    step = ExecutionStep(
        id="test_step",
        name="Test Custom Step",
        handler=lambda p: None,  # Handler will be overridden
        parameters={"type": "custom"},
        depends_on=set(),
        provides={'output'},
        requires=set()
    )

    # Execute through custom handler
    result = handler.execute(step, {"input": "test_data"})

    assert result["result"] == "success"
    assert result["data"] == "test_data"


def test_step_handler_registry():
    """Test registering and retrieving step handlers"""
    from luminous_nix.core.extension_points import StepHandlerRegistry, StepHandler

    class Handler1(StepHandler):
        def can_handle(self, step_type: str) -> bool:
            return step_type == "type1"

        def execute(self, step, context):
            return "handler1"

    class Handler2(StepHandler):
        def can_handle(self, step_type: str) -> bool:
            return step_type == "type2"

        def execute(self, step, context):
            return "handler2"

    registry = StepHandlerRegistry()

    handler1 = Handler1()
    handler2 = Handler2()

    registry.register(handler1)
    registry.register(handler2)

    # Get appropriate handler
    h1 = registry.get_handler("type1")
    h2 = registry.get_handler("type2")

    assert h1 is handler1
    assert h2 is handler2


def test_step_handler_not_found():
    """Test that missing handler returns None or raises"""
    from luminous_nix.core.extension_points import StepHandlerRegistry

    registry = StepHandlerRegistry()

    handler = registry.get_handler("nonexistent")
    assert handler is None


# === Test RecoveryStrategy Extension Point ===

def test_recovery_strategy_interface():
    """Test that RecoveryStrategy defines correct interface"""
    from luminous_nix.core.extension_points import RecoveryStrategy
    from luminous_nix.core.error_recovery import ClassifiedError

    class CustomRecoveryStrategy(RecoveryStrategy):
        def can_recover(self, error: ClassifiedError) -> bool:
            return "network" in str(error.message).lower()

        def recover(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
            # Attempt recovery
            return True

    strategy = CustomRecoveryStrategy()

    # Create a test error
    from luminous_nix.core.error_recovery import ErrorCategory, ErrorSeverity, RecoverabilityLevel

    error = ClassifiedError(
        message="Network connection failed",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
        operation_id="test_op",
        timestamp=datetime.now(),
        context={}
    )

    assert strategy.can_recover(error)


def test_recovery_strategy_execution():
    """Test executing recovery strategy"""
    from luminous_nix.core.extension_points import RecoveryStrategy
    from luminous_nix.core.error_recovery import ClassifiedError, ErrorCategory, ErrorSeverity, RecoverabilityLevel

    recovered = {"count": 0}

    class CustomRecoveryStrategy(RecoveryStrategy):
        def can_recover(self, error: ClassifiedError) -> bool:
            return error.category == ErrorCategory.NETWORK

        def recover(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
            recovered["count"] += 1
            return True

    strategy = CustomRecoveryStrategy()

    error = ClassifiedError(
        message="Connection timeout",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
        operation_id="test",
        timestamp=datetime.now(),
        context={}
    )

    result = strategy.recover(error, {"retry_count": 0})

    assert result is True
    assert recovered["count"] == 1


def test_recovery_strategy_registry():
    """Test registering and retrieving recovery strategies"""
    from luminous_nix.core.extension_points import RecoveryStrategyRegistry, RecoveryStrategy
    from luminous_nix.core.error_recovery import ClassifiedError

    class NetworkRecovery(RecoveryStrategy):
        def can_recover(self, error: ClassifiedError) -> bool:
            return "network" in error.message.lower()

        def recover(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
            return True

    registry = RecoveryStrategyRegistry()
    strategy = NetworkRecovery()

    registry.register("network", strategy)

    retrieved = registry.get_strategy("network")
    assert retrieved is strategy


# === Test PersistenceBackend Extension Point ===

def test_persistence_backend_interface():
    """Test that PersistenceBackend defines correct interface"""
    from luminous_nix.core.extension_points import PersistenceBackend
    from luminous_nix.core.state_manager import OperationState

    class CustomPersistenceBackend(PersistenceBackend):
        def __init__(self):
            self.storage = {}

        def save_state(self, operation_id: str, state: OperationState) -> bool:
            self.storage[operation_id] = state
            return True

        def load_state(self, operation_id: str) -> Optional[OperationState]:
            return self.storage.get(operation_id)

        def delete_state(self, operation_id: str) -> bool:
            if operation_id in self.storage:
                del self.storage[operation_id]
                return True
            return False

        def list_operations(self) -> list[str]:
            return list(self.storage.keys())

    backend = CustomPersistenceBackend()

    # Test methods exist
    assert hasattr(backend, 'save_state')
    assert hasattr(backend, 'load_state')
    assert hasattr(backend, 'delete_state')
    assert hasattr(backend, 'list_operations')


def test_persistence_backend_save_load():
    """Test saving and loading state through custom backend"""
    from luminous_nix.core.extension_points import PersistenceBackend
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    class MemoryBackend(PersistenceBackend):
        def __init__(self):
            self.storage = {}

        def save_state(self, operation_id: str, state: OperationState) -> bool:
            self.storage[operation_id] = state
            return True

        def load_state(self, operation_id: str) -> Optional[OperationState]:
            return self.storage.get(operation_id)

        def delete_state(self, operation_id: str) -> bool:
            if operation_id in self.storage:
                del self.storage[operation_id]
                return True
            return False

        def list_operations(self) -> list[str]:
            return list(self.storage.keys())

    backend = MemoryBackend()

    # Create state
    state = OperationState()
    state.operation_id = "test_op"
    state.user_query = "test operation"
    state.status = OperationStatus.PLANNING

    # Save
    assert backend.save_state("test_op", state)

    # Load
    loaded = backend.load_state("test_op")
    assert loaded is not None
    assert loaded.operation_id == "test_op"
    assert loaded.user_query == "test operation"

    # List
    ops = backend.list_operations()
    assert "test_op" in ops

    # Delete
    assert backend.delete_state("test_op")
    assert backend.load_state("test_op") is None


def test_persistence_backend_registry():
    """Test registering and using persistence backends"""
    from luminous_nix.core.extension_points import PersistenceBackendRegistry, PersistenceBackend

    class Backend1(PersistenceBackend):
        def save_state(self, operation_id: str, state) -> bool:
            return True

        def load_state(self, operation_id: str):
            return None

        def delete_state(self, operation_id: str) -> bool:
            return True

        def list_operations(self) -> list[str]:
            return []

    registry = PersistenceBackendRegistry()
    backend = Backend1()

    registry.register("memory", backend)

    retrieved = registry.get_backend("memory")
    assert retrieved is backend


# === Test ErrorClassifier Extension Point ===

def test_error_classifier_interface():
    """Test that ErrorClassifier defines correct interface"""
    from luminous_nix.core.extension_points import ErrorClassifier
    from luminous_nix.core.error_recovery import ClassifiedError

    class CustomErrorClassifier(ErrorClassifier):
        def classify(self, error_message: str, context: Dict[str, Any]) -> ClassifiedError:
            from luminous_nix.core.error_recovery import ErrorCategory, ErrorSeverity, RecoverabilityLevel

            return ClassifiedError(
                message=error_message,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
                operation_id=context.get("operation_id", "unknown"),
                timestamp=datetime.now(),
                context=context
            )

    classifier = CustomErrorClassifier()

    result = classifier.classify("Test error", {"operation_id": "test"})

    assert result.message == "Test error"
    assert result.operation_id == "test"


def test_error_classifier_custom_rules():
    """Test custom error classification rules"""
    from luminous_nix.core.extension_points import ErrorClassifier
    from luminous_nix.core.error_recovery import (
        ClassifiedError, ErrorCategory, ErrorSeverity, RecoverabilityLevel
    )

    class CustomErrorClassifier(ErrorClassifier):
        def classify(self, error_message: str, context: Dict[str, Any]) -> ClassifiedError:
            # Custom rule: "CRITICAL" in message = fatal
            if "CRITICAL" in error_message:
                severity = ErrorSeverity.FATAL
                recoverability = RecoverabilityLevel.NOT_RECOVERABLE
            else:
                severity = ErrorSeverity.MEDIUM
                recoverability = RecoverabilityLevel.RETRY_RECOVERABLE

            return ClassifiedError(
                message=error_message,
                category=ErrorCategory.UNKNOWN,
                severity=severity,
                recoverability=recoverability,
                operation_id=context.get("operation_id", "unknown"),
                timestamp=datetime.now(),
                context=context
            )

    classifier = CustomErrorClassifier()

    # Test non-critical error
    result1 = classifier.classify("Normal error", {})
    assert result1.severity == ErrorSeverity.MEDIUM
    assert result1.recoverability == RecoverabilityLevel.RETRY_RECOVERABLE

    # Test critical error
    result2 = classifier.classify("CRITICAL system failure", {})
    assert result2.severity == ErrorSeverity.FATAL
    assert result2.recoverability == RecoverabilityLevel.NOT_RECOVERABLE


def test_error_classifier_registry():
    """Test registering and retrieving error classifiers"""
    from luminous_nix.core.extension_points import ErrorClassifierRegistry, ErrorClassifier
    from luminous_nix.core.error_recovery import ClassifiedError, ErrorCategory, ErrorSeverity, RecoverabilityLevel

    class Classifier1(ErrorClassifier):
        def classify(self, error_message: str, context: Dict[str, Any]) -> ClassifiedError:
            return ClassifiedError(
                message=error_message,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
                operation_id="test",
                timestamp=datetime.now(),
                context=context
            )

    registry = ErrorClassifierRegistry()
    classifier = Classifier1()

    registry.register("custom", classifier)

    retrieved = registry.get_classifier("custom")
    assert retrieved is classifier


# === Test Extension Point Integration ===

def test_extension_points_with_plugins():
    """Test that plugins can provide extension point implementations"""
    from luminous_nix.core.plugin_registry import Plugin, PluginRegistry
    from luminous_nix.core.extension_points import StepHandler, StepHandlerRegistry

    class StepHandlerPlugin(Plugin):
        def __init__(self):
            super().__init__()
            self.handler = None

        @property
        def name(self) -> str:
            return "step-handler-plugin"

        @property
        def version(self) -> str:
            return "1.0.0"

        def on_enable(self) -> None:
            # Create and register custom step handler
            class CustomHandler(StepHandler):
                def can_handle(self, step_type: str) -> bool:
                    return step_type == "plugin_step"

                def execute(self, step, context):
                    return "plugin_handled"

            self.handler = CustomHandler()

    # Register plugin
    plugin_registry = PluginRegistry()
    plugin = StepHandlerPlugin()

    plugin_registry.register(plugin)
    plugin_registry.enable_plugin("step-handler-plugin")

    # Verify handler was created
    assert plugin.handler is not None
    assert plugin.handler.can_handle("plugin_step")


def test_multiple_extension_points_in_plugin():
    """Test plugin providing multiple extension points"""
    from luminous_nix.core.plugin_registry import Plugin, PluginRegistry
    from luminous_nix.core.extension_points import StepHandler, RecoveryStrategy

    class MultiExtensionPlugin(Plugin):
        def __init__(self):
            super().__init__()
            self.step_handler = None
            self.recovery_strategy = None

        @property
        def name(self) -> str:
            return "multi-extension"

        @property
        def version(self) -> str:
            return "1.0.0"

        def on_enable(self) -> None:
            # Provide step handler
            class Handler(StepHandler):
                def can_handle(self, step_type: str) -> bool:
                    return True

                def execute(self, step, context):
                    return "handled"

            # Provide recovery strategy
            class Strategy(RecoveryStrategy):
                def can_recover(self, error) -> bool:
                    return True

                def recover(self, error, context) -> bool:
                    return True

            self.step_handler = Handler()
            self.recovery_strategy = Strategy()

    # Enable plugin
    registry = PluginRegistry()
    plugin = MultiExtensionPlugin()

    registry.register(plugin)
    registry.enable_plugin("multi-extension")

    # Verify both extension points created
    assert plugin.step_handler is not None
    assert plugin.recovery_strategy is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
