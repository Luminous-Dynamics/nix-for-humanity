"""
Tests for plugin interfaces.

Tests OperationPlugin, HookPlugin, SecurityPlugin, and AIPlugin interfaces.
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from luminous_nix.plugins.interfaces import (
    OperationPlugin,
    HookPlugin,
    SecurityPlugin,
    AIPlugin
)
from luminous_nix.plugins.base import (
    PluginMetadata,
    PluginContext,
    PluginStatus
)

# Mock types for testing (these will be proper classes in the future)
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class OperationType(Enum):
    """Mock operation type for testing"""
    CUSTOM = "custom"
    INSTALL = "install"
    SEARCH = "search"

class OperationStatus(Enum):
    """Mock operation status for testing"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class OperationState:
    """Mock operation state for testing"""
    operation_id: str
    operation_type: OperationType
    user_query: Optional[str] = None
    status: OperationStatus = OperationStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TestOperationPlugin:
    """Test OperationPlugin interface"""

    class SimpleOperationPlugin(OperationPlugin):
        """Simple operation plugin for testing"""

        @property
        def metadata(self):
            return PluginMetadata(
                name="simple-op",
                version="1.0.0",
                author="Test",
                description="Simple operation plugin",
                operation_types=["CUSTOM_OP"]
            )

        def can_handle(self, operation_type: str) -> bool:
            return operation_type == "CUSTOM_OP"

        def execute(self, state: OperationState) -> OperationState:
            state.status = OperationStatus.COMPLETED
            state.result = {"executed": True}
            return state

    def test_operation_plugin_creation(self):
        """Test creating operation plugin"""
        plugin = self.SimpleOperationPlugin()

        assert plugin.type == "operation"
        assert plugin.metadata.name == "simple-op"
        assert "CUSTOM_OP" in plugin.metadata.operation_types

    def test_can_handle(self):
        """Test can_handle method"""
        plugin = self.SimpleOperationPlugin()

        assert plugin.can_handle("CUSTOM_OP") == True
        assert plugin.can_handle("OTHER_OP") == False

    def test_execute(self):
        """Test execute method"""
        plugin = self.SimpleOperationPlugin()

        state = OperationState(
            operation_id="test",
            operation_type=OperationType.CUSTOM,
            user_query="test query"
        )

        result = plugin.execute(state)

        assert result.status == OperationStatus.COMPLETED
        assert result.result["executed"] == True

    def test_validate_default(self):
        """Test default validate implementation"""
        plugin = self.SimpleOperationPlugin()

        state = OperationState(
            operation_id="test",
            operation_type=OperationType.CUSTOM,
            user_query="test"
        )

        # Default implementation returns True
        assert plugin.validate(state) == True

    def test_rollback_default(self):
        """Test default rollback implementation"""
        plugin = self.SimpleOperationPlugin()

        state = OperationState(
            operation_id="test",
            operation_type=OperationType.CUSTOM,
            user_query="test"
        )

        # Default implementation returns None
        assert plugin.rollback(state) is None

    def test_operation_with_validation(self):
        """Test operation plugin with validation"""

        class ValidatingPlugin(OperationPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="validating",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def can_handle(self, operation_type: str) -> bool:
                return True

            def validate(self, state: OperationState) -> bool:
                return state.user_query is not None

            def execute(self, state: OperationState) -> OperationState:
                return state

        plugin = ValidatingPlugin()

        # Valid state
        valid_state = OperationState(
            operation_id="test",
            operation_type=OperationType.CUSTOM,
            user_query="test"
        )
        assert plugin.validate(valid_state) == True

        # Invalid state
        invalid_state = OperationState(
            operation_id="test",
            operation_type=OperationType.CUSTOM,
            user_query=None
        )
        assert plugin.validate(invalid_state) == False

    def test_operation_with_rollback(self):
        """Test operation plugin with rollback"""

        class RollbackPlugin(OperationPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="rollback",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def can_handle(self, operation_type: str) -> bool:
                return True

            def execute(self, state: OperationState) -> OperationState:
                state.status = OperationStatus.FAILED
                return state

            def rollback(self, state: OperationState) -> OperationState:
                state.status = OperationStatus.ROLLED_BACK
                return state

        plugin = RollbackPlugin()

        state = OperationState(
            operation_id="test",
            operation_type=OperationType.CUSTOM,
            user_query="test"
        )

        # Execute and fail
        result = plugin.execute(state)
        assert result.status == OperationStatus.FAILED

        # Rollback
        rolled_back = plugin.rollback(result)
        assert rolled_back.status == OperationStatus.ROLLED_BACK


class TestHookPlugin:
    """Test HookPlugin interface"""

    class SimpleHookPlugin(HookPlugin):
        """Simple hook plugin for testing"""

        def __init__(self):
            super().__init__()
            self.calls = []

        @property
        def metadata(self):
            return PluginMetadata(
                name="simple-hook",
                version="1.0.0",
                author="Test",
                description="Simple hook plugin",
                hooks=["pre_operation", "post_operation"]
            )

        def pre_operation(self, state):
            self.calls.append("pre")

        def post_operation(self, state):
            self.calls.append("post")

    def test_hook_plugin_creation(self):
        """Test creating hook plugin"""
        plugin = self.SimpleHookPlugin()

        assert plugin.type == "hook"
        assert plugin.metadata.name == "simple-hook"
        assert "pre_operation" in plugin.metadata.hooks

    def test_pre_operation_hook(self):
        """Test pre_operation hook"""
        plugin = self.SimpleHookPlugin()

        state = Mock()
        plugin.pre_operation(state)

        assert "pre" in plugin.calls

    def test_post_operation_hook(self):
        """Test post_operation hook"""
        plugin = self.SimpleHookPlugin()

        state = Mock()
        plugin.post_operation(state)

        assert "post" in plugin.calls

    def test_on_error_hook(self):
        """Test on_error hook"""

        class ErrorHookPlugin(HookPlugin):
            def __init__(self):
                super().__init__()
                self.error_called = False

            @property
            def metadata(self):
                return PluginMetadata(
                    name="error-hook",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def on_error(self, state, error):
                self.error_called = True

        plugin = ErrorHookPlugin()

        state = Mock()
        error = Exception("Test error")

        plugin.on_error(state, error)

        assert plugin.error_called == True

    def test_on_state_change_hook(self):
        """Test on_state_change hook"""

        class StateChangeHookPlugin(HookPlugin):
            def __init__(self):
                super().__init__()
                self.changes = []

            @property
            def metadata(self):
                return PluginMetadata(
                    name="state-hook",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def on_state_change(self, old_state, new_state):
                self.changes.append((old_state, new_state))

        plugin = StateChangeHookPlugin()

        old = OperationStatus.PENDING
        new = OperationStatus.COMPLETED

        plugin.on_state_change(old, new)

        assert len(plugin.changes) == 1
        assert plugin.changes[0] == (old, new)

    def test_on_security_event_hook(self):
        """Test on_security_event hook"""

        class SecurityHookPlugin(HookPlugin):
            def __init__(self):
                super().__init__()
                self.events = []

            @property
            def metadata(self):
                return PluginMetadata(
                    name="security-hook",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def on_security_event(self, event_type, details):
                self.events.append((event_type, details))

        plugin = SecurityHookPlugin()

        plugin.on_security_event("permission_denied", {"permission": "filesystem:write"})

        assert len(plugin.events) == 1
        assert plugin.events[0][0] == "permission_denied"


class TestSecurityPlugin:
    """Test SecurityPlugin interface"""

    class SimpleSecurityPlugin(SecurityPlugin):
        """Simple security plugin for testing"""

        @property
        def metadata(self):
            return PluginMetadata(
                name="simple-security",
                version="1.0.0",
                author="Test",
                description="Simple security plugin"
            )

        def encrypt(self, data: bytes) -> bytes:
            return b"encrypted_" + data

        def decrypt(self, data: bytes) -> bytes:
            return data[10:]  # Remove "encrypted_" prefix

        def sign(self, data: bytes) -> bytes:
            return b"signature"

        def verify(self, data: bytes, signature: bytes) -> bool:
            return signature == b"signature"

    def test_security_plugin_creation(self):
        """Test creating security plugin"""
        plugin = self.SimpleSecurityPlugin()

        assert plugin.type == "security"
        assert plugin.metadata.name == "simple-security"

    def test_encrypt(self):
        """Test encrypt method"""
        plugin = self.SimpleSecurityPlugin()

        data = b"test data"
        encrypted = plugin.encrypt(data)

        assert encrypted == b"encrypted_test data"

    def test_decrypt(self):
        """Test decrypt method"""
        plugin = self.SimpleSecurityPlugin()

        encrypted = b"encrypted_test data"
        decrypted = plugin.decrypt(encrypted)

        assert decrypted == b"test data"

    def test_encrypt_decrypt_roundtrip(self):
        """Test encrypt/decrypt roundtrip"""
        plugin = self.SimpleSecurityPlugin()

        original = b"secret message"
        encrypted = plugin.encrypt(original)
        decrypted = plugin.decrypt(encrypted)

        assert decrypted == original

    def test_sign(self):
        """Test sign method"""
        plugin = self.SimpleSecurityPlugin()

        data = b"data to sign"
        signature = plugin.sign(data)

        assert signature == b"signature"

    def test_verify(self):
        """Test verify method"""
        plugin = self.SimpleSecurityPlugin()

        data = b"data to verify"
        signature = plugin.sign(data)

        assert plugin.verify(data, signature) == True
        assert plugin.verify(data, b"wrong") == False

    def test_validate_policy(self):
        """Test validate_policy method"""

        class PolicyPlugin(SecurityPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="policy",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def validate_policy(self, policy_name: str, context: dict) -> bool:
                return policy_name == "allowed_policy"

        plugin = PolicyPlugin()

        assert plugin.validate_policy("allowed_policy", {}) == True
        assert plugin.validate_policy("forbidden_policy", {}) == False


class TestAIPlugin:
    """Test AIPlugin interface"""

    class SimpleAIPlugin(AIPlugin):
        """Simple AI plugin for testing"""

        @property
        def metadata(self):
            return PluginMetadata(
                name="simple-ai",
                version="1.0.0",
                author="Test",
                description="Simple AI plugin"
            )

        def can_handle(self, query: str) -> bool:
            return "test" in query.lower()

        def process_query(self, query: str, context: dict) -> dict:
            return {
                "intent": "test",
                "confidence": 0.95,
                "response": f"Processed: {query}"
            }

    def test_ai_plugin_creation(self):
        """Test creating AI plugin"""
        plugin = self.SimpleAIPlugin()

        assert plugin.type == "ai"
        assert plugin.metadata.name == "simple-ai"

    def test_can_handle(self):
        """Test can_handle method"""
        plugin = self.SimpleAIPlugin()

        assert plugin.can_handle("test query") == True
        assert plugin.can_handle("other query") == False

    def test_process_query(self):
        """Test process_query method"""
        plugin = self.SimpleAIPlugin()

        result = plugin.process_query("test query", {})

        assert result["intent"] == "test"
        assert result["confidence"] == 0.95
        assert "Processed" in result["response"]

    def test_preprocess(self):
        """Test preprocess method"""

        class PreprocessPlugin(AIPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="preprocess",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def can_handle(self, query: str) -> bool:
                return True

            def preprocess(self, query: str) -> str:
                return query.lower().strip()

            def process_query(self, query: str, context: dict) -> dict:
                return {}

        plugin = PreprocessPlugin()

        preprocessed = plugin.preprocess("  TEST QUERY  ")

        assert preprocessed == "test query"

    def test_postprocess(self):
        """Test postprocess method"""

        class PostprocessPlugin(AIPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="postprocess",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def can_handle(self, query: str) -> bool:
                return True

            def process_query(self, query: str, context: dict) -> dict:
                return {"raw": "result"}

            def postprocess(self, result: dict) -> dict:
                result["formatted"] = result["raw"].upper()
                return result

        plugin = PostprocessPlugin()

        result = plugin.process_query("test", {})
        processed = plugin.postprocess(result)

        assert processed["formatted"] == "RESULT"

    def test_ai_full_pipeline(self):
        """Test full AI processing pipeline"""

        class FullPipelinePlugin(AIPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="full",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                )

            def can_handle(self, query: str) -> bool:
                return True

            def preprocess(self, query: str) -> str:
                return query.lower()

            def process_query(self, query: str, context: dict) -> dict:
                return {"query": query, "processed": True}

            def postprocess(self, result: dict) -> dict:
                result["finalized"] = True
                return result

        plugin = FullPipelinePlugin()

        # Full pipeline
        query = "TEST QUERY"
        preprocessed = plugin.preprocess(query)
        result = plugin.process_query(preprocessed, {})
        final = plugin.postprocess(result)

        assert final["query"] == "test query"
        assert final["processed"] == True
        assert final["finalized"] == True


class TestPluginInterfacePermissions:
    """Test permission handling across plugin interfaces"""

    def test_operation_plugin_requires_permission(self):
        """Test operation plugin checks permissions"""

        class PermissionPlugin(OperationPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="perm",
                    version="1.0.0",
                    author="Test",
                    description="Test",
                    requires_permissions=["operations:execute"]
                )

            def can_handle(self, operation_type: str) -> bool:
                return True

            def execute(self, state: OperationState) -> OperationState:
                self.require_permission("operations:execute")
                return state

        plugin = PermissionPlugin()

        # Without context
        state = OperationState(
            operation_id="test",
            operation_type=OperationType.CUSTOM,
            user_query="test"
        )

        # Should raise permission error
        from luminous_nix.plugins.errors import PluginPermissionError
        with pytest.raises(PluginPermissionError):
            plugin.execute(state)

        # With context and permission
        context = PluginContext(
            plugin_name="test",
            permissions={"operations:execute"}
        )
        plugin.context = context

        # Should work now
        result = plugin.execute(state)
        assert result is not None
