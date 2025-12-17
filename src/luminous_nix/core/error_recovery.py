"""
ErrorRecovery Framework - Intelligent error recovery for Luminous Nix

This module provides intelligent error classification, recovery decision making,
and retry strategies for robust operation execution.

Based on design: DEEP_DIVE_ERROR_RECOVERY.md
Test-Driven Development: Implementation matches tests/test_error_recovery.py
"""

from typing import List, Dict, Any, Callable, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import logging

from .state_manager import StateManager, OperationState, OperationStatus

logger = logging.getLogger(__name__)


# === Error Classification ===

class ErrorCategory(Enum):
    """Categories of errors"""
    NETWORK = "network"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    FATAL = "fatal"           # Cannot recover
    CRITICAL = "critical"     # Serious but might recover
    HIGH = "high"             # Significant issue
    MEDIUM = "medium"         # Moderate issue
    LOW = "low"               # Minor issue


class RecoverabilityLevel(Enum):
    """How recoverable an error is"""
    AUTO_RECOVERABLE = "auto_recoverable"           # Can auto-recover
    RETRY_RECOVERABLE = "retry_recoverable"         # Can retry
    FALLBACK_RECOVERABLE = "fallback_recoverable"   # Has fallback
    USER_RECOVERABLE = "user_recoverable"           # Needs user input
    NOT_RECOVERABLE = "not_recoverable"             # Cannot recover


@dataclass
class ClassifiedError:
    """An error that has been classified"""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    recoverability: RecoverabilityLevel
    operation_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    original_exception: Optional[Exception] = None
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def can_retry(self) -> bool:
        """Check if error can be retried"""
        return self.recoverability in (
            RecoverabilityLevel.AUTO_RECOVERABLE,
            RecoverabilityLevel.RETRY_RECOVERABLE
        )

    @property
    def needs_user_input(self) -> bool:
        """Check if error needs user input"""
        return self.recoverability == RecoverabilityLevel.USER_RECOVERABLE


class ErrorClassifier:
    """Classifies errors based on patterns and context"""

    def __init__(self):
        """Initialize error classifier with pattern database"""
        # Network error patterns
        self.network_patterns = [
            r"connection refused",
            r"network unreachable",
            r"temporary failure in name resolution",
            r"could not resolve host",
            r"timeout",
            r"connection timed out",
        ]

        # Resource error patterns
        self.resource_patterns = [
            r"no space left on device",
            r"disk quota exceeded",
            r"out of memory",
            r"cannot allocate memory",
            r"too many open files",
        ]

        # Dependency error patterns
        self.dependency_patterns = [
            r"hash mismatch",
            r"package collision",
            r"dependency.*not found",
            r"missing.*dependency",
            r"unmet.*dependencies",
        ]

        # Fatal error patterns
        self.fatal_patterns = [
            r"segmentation fault",
            r"core dumped",
            r"permission denied",
            r"access denied",
        ]

    def classify(
        self,
        error_message: str,
        operation_id: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> ClassifiedError:
        """
        Classify an error message.

        Args:
            error_message: Error message to classify
            operation_id: ID of operation that failed
            context: Additional context

        Returns:
            ClassifiedError with category, severity, and recoverability
        """
        error_lower = error_message.lower()
        context = context or {}

        # Check for fatal errors first
        if self._matches_patterns(error_lower, self.fatal_patterns):
            return ClassifiedError(
                message=error_message,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.FATAL,
                recoverability=RecoverabilityLevel.NOT_RECOVERABLE,
                operation_id=operation_id,
                context=context
            )

        # Check network errors
        if self._matches_patterns(error_lower, self.network_patterns):
            return ClassifiedError(
                message=error_message,
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
                operation_id=operation_id,
                context=context
            )

        # Check resource errors
        if self._matches_patterns(error_lower, self.resource_patterns):
            return ClassifiedError(
                message=error_message,
                category=ErrorCategory.RESOURCE,
                severity=ErrorSeverity.CRITICAL,
                recoverability=RecoverabilityLevel.AUTO_RECOVERABLE,
                operation_id=operation_id,
                context=context
            )

        # Check dependency errors
        if self._matches_patterns(error_lower, self.dependency_patterns):
            return ClassifiedError(
                message=error_message,
                category=ErrorCategory.DEPENDENCY,
                severity=ErrorSeverity.HIGH,
                recoverability=RecoverabilityLevel.FALLBACK_RECOVERABLE,
                operation_id=operation_id,
                context=context
            )

        # Unknown error - conservative approach
        return ClassifiedError(
            message=error_message,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            recoverability=RecoverabilityLevel.USER_RECOVERABLE,
            operation_id=operation_id,
            context=context
        )

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any pattern"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


# === Recovery Decision Making ===

@dataclass
class RecoveryAction:
    """A recovery action that can be taken"""
    name: str
    description: str
    handler: Callable[[ClassifiedError, Dict[str, Any]], bool]
    estimated_time_s: float = 5.0
    requires_user_input: bool = False


class RecoveryDecisionTree:
    """Decides recovery strategy based on error classification"""

    def __init__(self):
        """Initialize decision tree with recovery actions"""
        self.recovery_actions: Dict[ErrorCategory, List[RecoveryAction]] = {
            ErrorCategory.NETWORK: [
                RecoveryAction(
                    name="wait_and_retry",
                    description="Wait briefly and retry operation",
                    handler=self._wait_and_retry_handler,
                    estimated_time_s=5.0
                ),
                RecoveryAction(
                    name="check_connectivity",
                    description="Verify network connectivity",
                    handler=self._check_connectivity_handler,
                    estimated_time_s=2.0
                ),
            ],
            ErrorCategory.RESOURCE: [
                RecoveryAction(
                    name="cleanup_temp_files",
                    description="Clean up temporary files",
                    handler=self._cleanup_temp_handler,
                    estimated_time_s=10.0
                ),
                RecoveryAction(
                    name="run_garbage_collection",
                    description="Run Nix garbage collection",
                    handler=self._garbage_collection_handler,
                    estimated_time_s=30.0
                ),
            ],
            ErrorCategory.DEPENDENCY: [
                RecoveryAction(
                    name="update_channels",
                    description="Update package channels",
                    handler=self._update_channels_handler,
                    estimated_time_s=60.0
                ),
                RecoveryAction(
                    name="rebuild_with_fallback",
                    description="Try alternative package sources",
                    handler=self._fallback_sources_handler,
                    estimated_time_s=120.0
                ),
            ],
        }

    def decide_recovery(
        self,
        error: ClassifiedError,
        context: Optional[Dict[str, Any]] = None
    ) -> List[RecoveryAction]:
        """
        Decide recovery actions for an error.

        Args:
            error: Classified error
            context: Additional context

        Returns:
            List of recovery actions (ordered by priority)
        """
        context = context or {}

        # If not recoverable, return empty list
        if error.recoverability == RecoverabilityLevel.NOT_RECOVERABLE:
            return []

        # Get recovery actions for this error category
        actions = self.recovery_actions.get(error.category, [])

        # Filter based on severity
        if error.severity == ErrorSeverity.FATAL:
            return []
        elif error.severity == ErrorSeverity.CRITICAL:
            # Only auto-recovery actions for critical
            actions = [a for a in actions if not a.requires_user_input]

        return actions

    # Recovery action handlers (placeholders for now)

    def _wait_and_retry_handler(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
        """Wait and retry handler"""
        return True

    def _check_connectivity_handler(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
        """Check connectivity handler"""
        return True

    def _cleanup_temp_handler(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
        """Cleanup temporary files handler"""
        return True

    def _garbage_collection_handler(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
        """Garbage collection handler"""
        return True

    def _update_channels_handler(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
        """Update channels handler"""
        return True

    def _fallback_sources_handler(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
        """Fallback sources handler"""
        return True


# === Retry Strategy ===

@dataclass
class RetryStrategy:
    """Strategy for retrying failed operations"""
    max_retries: int = 3
    base_delay_s: float = 1.0
    max_delay_s: float = 60.0
    exponential_base: float = 2.0

    def should_retry(self, attempt: int) -> bool:
        """
        Check if operation should be retried.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False if max retries reached
        """
        return attempt < self.max_retries

    def get_delay(self, attempt: int) -> float:
        """
        Get delay before next retry.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds (with exponential backoff)
        """
        delay = self.base_delay_s * (self.exponential_base ** attempt)
        return min(delay, self.max_delay_s)


# === ErrorRecoveryManager Integration ===

@dataclass
class ErrorRecoveryOutcome:
    """Outcome of error recovery attempt"""
    error: ClassifiedError
    recovered: bool
    actions_taken: List[str] = field(default_factory=list)
    recovery_time_s: float = 0.0
    final_state: Optional[OperationStatus] = None


class ErrorRecoveryManager:
    """
    Main integration point for error recovery.

    Combines error classification, recovery decision making,
    and retry strategies with StateManager integration.
    """

    def __init__(self, state_manager: StateManager):
        """
        Initialize error recovery manager.

        Args:
            state_manager: StateManager instance for state persistence
        """
        self.state_manager = state_manager
        self.classifier = ErrorClassifier()
        self.decision_tree = RecoveryDecisionTree()
        self.default_retry_strategy = RetryStrategy()

    def handle_error(
        self,
        operation_id: str,
        error_message: str,
        command: Optional[str] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        exit_code: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorRecoveryOutcome:
        """
        Handle an error that occurred during operation execution.

        Args:
            operation_id: ID of operation that failed
            error_message: Error message
            command: Command that failed
            stdout: Standard output
            stderr: Standard error
            exit_code: Exit code
            context: Additional context

        Returns:
            ErrorRecoveryOutcome with recovery details
        """
        start_time = datetime.now()
        context = context or {}

        # Get operation state
        state = self.state_manager.get_operation(operation_id)
        if not state:
            logger.error(f"Operation {operation_id} not found")
            return ErrorRecoveryOutcome(
                error=ClassifiedError(
                    message=error_message,
                    category=ErrorCategory.UNKNOWN,
                    severity=ErrorSeverity.MEDIUM,
                    recoverability=RecoverabilityLevel.NOT_RECOVERABLE,
                    operation_id=operation_id
                ),
                recovered=False
            )

        # Classify error
        error = self.classifier.classify(
            error_message=error_message,
            operation_id=operation_id,
            context=context
        )

        # Update state with error details
        state.error = error_message
        state.error_details = {
            'message': error_message,
            'category': error.category.value,
            'severity': error.severity.value,
            'recoverability': error.recoverability.value,
            'command': command,
            'stdout': stdout,
            'stderr': stderr,
            'exit_code': exit_code,
            'timestamp': error.timestamp.isoformat()
        }

        # Check if we can attempt recovery
        if not error.can_retry:
            state.status = OperationStatus.FAILED
            self.state_manager.update_operation(state)

            recovery_time = (datetime.now() - start_time).total_seconds()
            return ErrorRecoveryOutcome(
                error=error,
                recovered=False,
                recovery_time_s=recovery_time,
                final_state=OperationStatus.FAILED
            )

        # Check retry count
        if state.retry_count >= state.max_retries:
            logger.info(f"Max retries ({state.max_retries}) reached for operation {operation_id}")
            state.status = OperationStatus.FAILED
            self.state_manager.update_operation(state)

            recovery_time = (datetime.now() - start_time).total_seconds()
            return ErrorRecoveryOutcome(
                error=error,
                recovered=False,
                recovery_time_s=recovery_time,
                final_state=OperationStatus.FAILED
            )

        # Decide recovery actions
        actions = self.decision_tree.decide_recovery(error, context)
        actions_taken = [action.name for action in actions]

        # Update state
        self.state_manager.update_operation(state)

        recovery_time = (datetime.now() - start_time).total_seconds()

        return ErrorRecoveryOutcome(
            error=error,
            recovered=len(actions) > 0,  # Recovered if we have actions
            actions_taken=actions_taken,
            recovery_time_s=recovery_time,
            final_state=state.status
        )


if __name__ == "__main__":
    # Example usage
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Initialize
        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=manager)

        # Create operation
        state = manager.create_operation("test operation")
        state.status = OperationStatus.EXECUTING
        manager.update_operation(state)

        # Simulate error
        outcome = recovery_mgr.handle_error(
            operation_id=state.operation_id,
            error_message="Connection refused - temporary network issue",
            command="nix-build",
            exit_code=1
        )

        print(f"Error category: {outcome.error.category.value}")
        print(f"Severity: {outcome.error.severity.value}")
        print(f"Recovered: {outcome.recovered}")
        print(f"Actions: {outcome.actions_taken}")
