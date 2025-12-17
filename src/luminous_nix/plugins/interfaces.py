"""
Plugin interface definitions.

Defines interfaces for different plugin types:
- OperationPlugin: Custom operation types
- SecurityPlugin: Security extensions
- HookPlugin: System event hooks
- AIPlugin: AI/LLM extensions
"""

from abc import abstractmethod
from typing import Optional
from .base import Plugin, PluginMetadata

# Import core types (will be available when integrated)
try:
    from ..core.types import OperationState
except ImportError:
    # For development/testing without full core
    OperationState = None


class OperationPlugin(Plugin):
    """
    Plugin for adding custom operation types.

    Example use cases:
    - Docker operations
    - Cloud provider operations
    - Custom package managers
    - Development workflows
    """

    @property
    def type(self) -> str:
        return "operation"

    @abstractmethod
    def can_handle(self, operation_type: str) -> bool:
        """
        Check if this plugin can handle the given operation type.

        Args:
            operation_type: The operation type (e.g., "DOCKER_RUN")

        Returns:
            True if plugin can handle this operation type
        """
        pass

    @abstractmethod
    def execute(self, state: 'OperationState') -> 'OperationState':
        """
        Execute the operation.

        Args:
            state: Operation state with details of operation to execute

        Returns:
            Updated operation state with results

        Raises:
            PluginExecutionError: If execution fails
        """
        pass

    def validate(self, state: 'OperationState') -> bool:
        """
        Validate operation before execution.

        Override to add custom validation logic.

        Args:
            state: Operation state to validate

        Returns:
            True if operation is valid
        """
        return True

    def rollback(self, state: 'OperationState') -> Optional['OperationState']:
        """
        Rollback a failed operation.

        Override to implement rollback logic.

        Args:
            state: Operation state to rollback

        Returns:
            Updated operation state after rollback, or None if rollback not supported
        """
        return None


class SecurityPlugin(Plugin):
    """
    Plugin for extending security capabilities.

    Example use cases:
    - HSM integration
    - Alternative encryption algorithms
    - Custom signature schemes
    - Security policy enforcement
    """

    @property
    def type(self) -> str:
        return "security"

    def encrypt(self, data: bytes, **kwargs) -> bytes:
        """
        Encrypt data using custom method.

        Override to implement custom encryption.

        Args:
            data: Data to encrypt
            **kwargs: Additional encryption parameters

        Returns:
            Encrypted data
        """
        raise NotImplementedError("Plugin does not implement encryption")

    def decrypt(self, data: bytes, **kwargs) -> bytes:
        """
        Decrypt data using custom method.

        Override to implement custom decryption.

        Args:
            data: Data to decrypt
            **kwargs: Additional decryption parameters

        Returns:
            Decrypted data
        """
        raise NotImplementedError("Plugin does not implement decryption")

    def sign(self, data: bytes, **kwargs) -> bytes:
        """
        Sign data using custom method.

        Override to implement custom signing.

        Args:
            data: Data to sign
            **kwargs: Additional signing parameters

        Returns:
            Signature bytes
        """
        raise NotImplementedError("Plugin does not implement signing")

    def verify(self, data: bytes, signature: bytes, **kwargs) -> bool:
        """
        Verify signature using custom method.

        Override to implement custom verification.

        Args:
            data: Original data
            signature: Signature to verify
            **kwargs: Additional verification parameters

        Returns:
            True if signature is valid
        """
        raise NotImplementedError("Plugin does not implement verification")

    def validate_policy(self, operation: 'OperationState') -> bool:
        """
        Validate operation against security policy.

        Override to implement custom security policies.

        Args:
            operation: Operation to validate

        Returns:
            True if operation satisfies security policy
        """
        return True


class HookPlugin(Plugin):
    """
    Plugin for hooking into system events.

    Example use cases:
    - Event logging
    - Monitoring and alerting
    - Metrics collection
    - Audit trail
    """

    @property
    def type(self) -> str:
        return "hook"

    def pre_operation(self, state: 'OperationState') -> None:
        """
        Called before operation execution.

        Override to hook into pre-execution.

        Args:
            state: Operation state before execution
        """
        pass

    def post_operation(self, state: 'OperationState') -> None:
        """
        Called after operation execution.

        Override to hook into post-execution.

        Args:
            state: Operation state after execution
        """
        pass

    def on_error(self, state: 'OperationState', error: Exception) -> None:
        """
        Called when operation fails.

        Override to hook into error handling.

        Args:
            state: Operation state when error occurred
            error: The exception that occurred
        """
        pass

    def on_state_change(self, old_state: 'OperationState', new_state: 'OperationState') -> None:
        """
        Called when operation state changes.

        Override to hook into state transitions.

        Args:
            old_state: Previous operation state
            new_state: New operation state
        """
        pass

    def on_security_event(self, event_type: str, details: dict) -> None:
        """
        Called on security-related events.

        Override to hook into security events.

        Args:
            event_type: Type of security event
            details: Event details
        """
        pass


class AIPlugin(Plugin):
    """
    Plugin for extending AI capabilities.

    Example use cases:
    - Custom domain-specific models
    - Alternative LLM backends
    - Specialized intent recognition
    - Custom NLP preprocessing
    """

    @property
    def type(self) -> str:
        return "ai"

    @abstractmethod
    def process_query(self, query: str, **kwargs) -> dict:
        """
        Process user query with custom AI.

        Args:
            query: User's natural language query
            **kwargs: Additional processing parameters

        Returns:
            Dict with:
                - intent: Recognized intent
                - confidence: Confidence score (0.0-1.0)
                - entities: Extracted entities
                - metadata: Additional metadata
        """
        pass

    def can_handle(self, query: str) -> bool:
        """
        Check if plugin can handle query.

        Override to implement query routing logic.

        Args:
            query: User query

        Returns:
            True if plugin can process this query
        """
        return True

    def preprocess(self, query: str) -> str:
        """
        Preprocess query before main AI processing.

        Override to implement custom preprocessing.

        Args:
            query: Raw user query

        Returns:
            Preprocessed query
        """
        return query

    def postprocess(self, result: dict) -> dict:
        """
        Postprocess AI results.

        Override to implement custom postprocessing.

        Args:
            result: Raw AI result

        Returns:
            Postprocessed result
        """
        return result


# Export all interfaces
__all__ = [
    'OperationPlugin',
    'SecurityPlugin',
    'HookPlugin',
    'AIPlugin',
]
