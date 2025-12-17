"""
Extension Points - Interfaces for Plugin Extensibility

Defines extension point interfaces that plugins can implement to extend
core functionality in well-defined ways.

Based on: Week 6 Extension Points
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


# === StepHandler Extension Point ===

class StepHandler(ABC):
    """
    Extension point for custom execution step handlers.

    Plugins can implement this to provide custom step types
    that can be executed by the ExecutionPlan.
    """

    @abstractmethod
    def can_handle(self, step_type: str) -> bool:
        """
        Check if this handler can handle the given step type.

        Args:
            step_type: Type of step to check

        Returns:
            True if this handler can handle the step type
        """
        pass

    @abstractmethod
    def execute(self, step: 'ExecutionStep', context: Dict[str, Any]) -> Any:
        """
        Execute the step.

        Args:
            step: ExecutionStep to execute
            context: Execution context with available resources

        Returns:
            Result of step execution
        """
        pass


class StepHandlerRegistry:
    """
    Registry for step handlers.

    Manages registration and retrieval of step handlers based on step type.
    """

    def __init__(self):
        """Initialize empty step handler registry"""
        self._handlers: List[StepHandler] = []

    def register(self, handler: StepHandler) -> None:
        """
        Register a step handler.

        Args:
            handler: StepHandler instance to register
        """
        self._handlers.append(handler)
        logger.info(f"Registered step handler: {handler.__class__.__name__}")

    def unregister(self, handler: StepHandler) -> None:
        """
        Unregister a step handler.

        Args:
            handler: StepHandler instance to unregister
        """
        if handler in self._handlers:
            self._handlers.remove(handler)
            logger.info(f"Unregistered step handler: {handler.__class__.__name__}")

    def get_handler(self, step_type: str) -> Optional[StepHandler]:
        """
        Get handler for step type.

        Args:
            step_type: Type of step

        Returns:
            StepHandler that can handle the type, or None if not found
        """
        for handler in self._handlers:
            if handler.can_handle(step_type):
                return handler
        return None

    def list_handlers(self) -> List[StepHandler]:
        """
        List all registered handlers.

        Returns:
            List of registered step handlers
        """
        return list(self._handlers)


# === RecoveryStrategy Extension Point ===

class RecoveryStrategy(ABC):
    """
    Extension point for custom error recovery strategies.

    Plugins can implement this to provide custom recovery logic
    for specific types of errors.
    """

    @abstractmethod
    def can_recover(self, error: 'ClassifiedError') -> bool:
        """
        Check if this strategy can recover from the error.

        Args:
            error: Classified error to check

        Returns:
            True if this strategy can attempt recovery
        """
        pass

    @abstractmethod
    def recover(self, error: 'ClassifiedError', context: Dict[str, Any]) -> bool:
        """
        Attempt to recover from the error.

        Args:
            error: Classified error to recover from
            context: Recovery context with operation state

        Returns:
            True if recovery successful, False otherwise
        """
        pass


class RecoveryStrategyRegistry:
    """
    Registry for recovery strategies.

    Manages registration and retrieval of recovery strategies.
    """

    def __init__(self):
        """Initialize empty recovery strategy registry"""
        self._strategies: Dict[str, RecoveryStrategy] = {}

    def register(self, name: str, strategy: RecoveryStrategy) -> None:
        """
        Register a recovery strategy.

        Args:
            name: Name for the strategy
            strategy: RecoveryStrategy instance
        """
        self._strategies[name] = strategy
        logger.info(f"Registered recovery strategy: {name}")

    def unregister(self, name: str) -> None:
        """
        Unregister a recovery strategy.

        Args:
            name: Name of strategy to unregister
        """
        if name in self._strategies:
            del self._strategies[name]
            logger.info(f"Unregistered recovery strategy: {name}")

    def get_strategy(self, name: str) -> Optional[RecoveryStrategy]:
        """
        Get recovery strategy by name.

        Args:
            name: Name of strategy

        Returns:
            RecoveryStrategy instance or None if not found
        """
        return self._strategies.get(name)

    def get_applicable_strategies(self, error: 'ClassifiedError') -> List[RecoveryStrategy]:
        """
        Get all strategies that can recover from error.

        Args:
            error: Classified error

        Returns:
            List of applicable recovery strategies
        """
        applicable = []
        for strategy in self._strategies.values():
            if strategy.can_recover(error):
                applicable.append(strategy)
        return applicable

    def list_strategies(self) -> Dict[str, RecoveryStrategy]:
        """
        List all registered strategies.

        Returns:
            Dictionary mapping names to strategies
        """
        return dict(self._strategies)


# === PersistenceBackend Extension Point ===

class PersistenceBackend(ABC):
    """
    Extension point for custom state persistence backends.

    Plugins can implement this to provide alternative storage
    mechanisms for operation state (e.g., Redis, PostgreSQL, S3).
    """

    @abstractmethod
    def save_state(self, operation_id: str, state: 'OperationState') -> bool:
        """
        Save operation state.

        Args:
            operation_id: ID of operation
            state: OperationState to save

        Returns:
            True if saved successfully
        """
        pass

    @abstractmethod
    def load_state(self, operation_id: str) -> Optional['OperationState']:
        """
        Load operation state.

        Args:
            operation_id: ID of operation

        Returns:
            OperationState if found, None otherwise
        """
        pass

    @abstractmethod
    def delete_state(self, operation_id: str) -> bool:
        """
        Delete operation state.

        Args:
            operation_id: ID of operation

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    def list_operations(self) -> List[str]:
        """
        List all operation IDs.

        Returns:
            List of operation IDs
        """
        pass


class PersistenceBackendRegistry:
    """
    Registry for persistence backends.

    Manages registration and retrieval of persistence backends.
    """

    def __init__(self):
        """Initialize empty persistence backend registry"""
        self._backends: Dict[str, PersistenceBackend] = {}

    def register(self, name: str, backend: PersistenceBackend) -> None:
        """
        Register a persistence backend.

        Args:
            name: Name for the backend
            backend: PersistenceBackend instance
        """
        self._backends[name] = backend
        logger.info(f"Registered persistence backend: {name}")

    def unregister(self, name: str) -> None:
        """
        Unregister a persistence backend.

        Args:
            name: Name of backend to unregister
        """
        if name in self._backends:
            del self._backends[name]
            logger.info(f"Unregistered persistence backend: {name}")

    def get_backend(self, name: str) -> Optional[PersistenceBackend]:
        """
        Get persistence backend by name.

        Args:
            name: Name of backend

        Returns:
            PersistenceBackend instance or None if not found
        """
        return self._backends.get(name)

    def list_backends(self) -> Dict[str, PersistenceBackend]:
        """
        List all registered backends.

        Returns:
            Dictionary mapping names to backends
        """
        return dict(self._backends)


# === ErrorClassifier Extension Point ===

class ErrorClassifier(ABC):
    """
    Extension point for custom error classification.

    Plugins can implement this to provide domain-specific
    error classification logic.
    """

    @abstractmethod
    def classify(
        self,
        error_message: str,
        context: Dict[str, Any]
    ) -> 'ClassifiedError':
        """
        Classify an error.

        Args:
            error_message: Error message to classify
            context: Error context with additional information

        Returns:
            ClassifiedError with category, severity, recoverability
        """
        pass


class ErrorClassifierRegistry:
    """
    Registry for error classifiers.

    Manages registration and retrieval of error classifiers.
    """

    def __init__(self):
        """Initialize empty error classifier registry"""
        self._classifiers: Dict[str, ErrorClassifier] = {}

    def register(self, name: str, classifier: ErrorClassifier) -> None:
        """
        Register an error classifier.

        Args:
            name: Name for the classifier
            classifier: ErrorClassifier instance
        """
        self._classifiers[name] = classifier
        logger.info(f"Registered error classifier: {name}")

    def unregister(self, name: str) -> None:
        """
        Unregister an error classifier.

        Args:
            name: Name of classifier to unregister
        """
        if name in self._classifiers:
            del self._classifiers[name]
            logger.info(f"Unregistered error classifier: {name}")

    def get_classifier(self, name: str) -> Optional[ErrorClassifier]:
        """
        Get error classifier by name.

        Args:
            name: Name of classifier

        Returns:
            ErrorClassifier instance or None if not found
        """
        return self._classifiers.get(name)

    def list_classifiers(self) -> Dict[str, ErrorClassifier]:
        """
        List all registered classifiers.

        Returns:
            Dictionary mapping names to classifiers
        """
        return dict(self._classifiers)


# === Example Implementations ===

if __name__ == "__main__":
    # Example: Custom Step Handler
    class PrintStepHandler(StepHandler):
        """Example step handler that prints messages"""

        def can_handle(self, step_type: str) -> bool:
            return step_type == "print"

        def execute(self, step, context):
            message = step.parameters.get('message', 'Hello!')
            print(f"[PrintStepHandler] {message}")
            return {"printed": message}

    # Example: Custom Recovery Strategy
    class RetryNetworkStrategy(RecoveryStrategy):
        """Example recovery strategy for network errors"""

        def can_recover(self, error) -> bool:
            return "network" in error.message.lower()

        def recover(self, error, context) -> bool:
            print(f"[RetryNetworkStrategy] Attempting recovery for: {error.message}")
            # Simulate recovery attempt
            return True

    # Example: In-Memory Persistence Backend
    class MemoryBackend(PersistenceBackend):
        """Example persistence backend using in-memory storage"""

        def __init__(self):
            self.storage = {}

        def save_state(self, operation_id: str, state) -> bool:
            self.storage[operation_id] = state
            return True

        def load_state(self, operation_id: str):
            return self.storage.get(operation_id)

        def delete_state(self, operation_id: str) -> bool:
            if operation_id in self.storage:
                del self.storage[operation_id]
                return True
            return False

        def list_operations(self) -> List[str]:
            return list(self.storage.keys())

    # Example: Custom Error Classifier
    class SimpleErrorClassifier(ErrorClassifier):
        """Example error classifier with simple rules"""

        def classify(self, error_message: str, context: Dict[str, Any]):
            from luminous_nix.core.error_recovery import (
                ClassifiedError, ErrorCategory, ErrorSeverity, RecoverabilityLevel
            )
            from datetime import datetime

            # Simple classification logic
            if "network" in error_message.lower():
                category = ErrorCategory.NETWORK
                severity = ErrorSeverity.HIGH
                recoverability = RecoverabilityLevel.RETRY_RECOVERABLE
            else:
                category = ErrorCategory.UNKNOWN
                severity = ErrorSeverity.MEDIUM
                recoverability = RecoverabilityLevel.RETRY_RECOVERABLE

            return ClassifiedError(
                message=error_message,
                category=category,
                severity=severity,
                recoverability=recoverability,
                operation_id=context.get('operation_id', 'unknown'),
                timestamp=datetime.now(),
                context=context
            )

    print("Extension Points Examples:")
    print("✓ StepHandler - Custom step execution")
    print("✓ RecoveryStrategy - Custom error recovery")
    print("✓ PersistenceBackend - Custom state storage")
    print("✓ ErrorClassifier - Custom error classification")
