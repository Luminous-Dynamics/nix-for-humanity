"""
Tests for plugin base classes and types.

Tests Plugin, PluginMetadata, PluginConfig, PluginContext, PluginStatus.
"""

import pytest
from pathlib import Path

from luminous_nix.plugins.base import (
    Plugin,
    PluginMetadata,
    PluginConfig,
    PluginContext,
    PluginStatus,
    PluginInfo,
    PluginHook
)


class TestPluginMetadata:
    """Test PluginMetadata dataclass"""

    def test_basic_metadata(self):
        """Test basic metadata creation"""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test Author",
            description="Test description"
        )

        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.description == "Test description"
        assert metadata.api_version == "1.0"  # default

    def test_metadata_with_optional_fields(self):
        """Test metadata with optional fields"""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test Author",
            description="Test description",
            email="test@example.com",
            homepage="https://example.com",
            license="MIT",
            operation_types=["CUSTOM_OP"],
            hooks=["pre_operation"],
            requires_permissions=["operations:execute"]
        )

        assert metadata.email == "test@example.com"
        assert metadata.homepage == "https://example.com"
        assert metadata.license == "MIT"
        assert "CUSTOM_OP" in metadata.operation_types
        assert "pre_operation" in metadata.hooks
        assert "operations:execute" in metadata.requires_permissions


class TestPluginConfig:
    """Test PluginConfig"""

    def test_default_config(self):
        """Test default configuration"""
        config = PluginConfig()

        assert len(config.plugin_paths) == 3
        assert config.allow_unsigned_plugins == True
        assert config.require_signatures == False
        assert config.lazy_loading == True
        assert config.enable_sandboxing == True

    def test_custom_config(self):
        """Test custom configuration"""
        config = PluginConfig(
            plugin_paths=[Path("/custom/path")],
            require_signatures=True,
            allow_unsigned_plugins=False,
            lazy_loading=False
        )

        assert len(config.plugin_paths) == 1
        assert config.plugin_paths[0] == Path("/custom/path")
        assert config.require_signatures == True
        assert config.allow_unsigned_plugins == False
        assert config.lazy_loading == False


class TestPluginContext:
    """Test PluginContext"""

    def test_basic_context(self):
        """Test basic context creation"""
        context = PluginContext(
            plugin_name="test-plugin",
            plugin_dir=Path("/test/path")
        )

        assert context.plugin_name == "test-plugin"
        assert context.plugin_dir == Path("/test/path")
        assert context.state_manager is None
        assert context.security is None

    def test_context_with_core_systems(self):
        """Test context with core systems"""
        mock_state_manager = object()
        mock_security = object()

        context = PluginContext(
            plugin_name="test-plugin",
            state_manager=mock_state_manager,
            security=mock_security
        )

        assert context.state_manager is mock_state_manager
        assert context.security is mock_security

    def test_has_permission(self):
        """Test permission checking"""
        context = PluginContext(
            plugin_name="test-plugin",
            permissions={"operations:execute", "filesystem:read"}
        )

        assert context.has_permission("operations:execute") == True
        assert context.has_permission("filesystem:read") == True
        assert context.has_permission("network:http") == False


class TestPluginStatus:
    """Test PluginStatus enum"""

    def test_status_values(self):
        """Test all status values exist"""
        assert PluginStatus.DISCOVERED.value == "discovered"
        assert PluginStatus.VALIDATED.value == "validated"
        assert PluginStatus.LOADED.value == "loaded"
        assert PluginStatus.INITIALIZED.value == "initialized"
        assert PluginStatus.ACTIVE.value == "active"
        assert PluginStatus.DISABLED.value == "disabled"
        assert PluginStatus.FAILED.value == "failed"
        assert PluginStatus.ERROR.value == "error"


class TestPluginBase:
    """Test Plugin base class"""

    class SimplePlugin(Plugin):
        """Simple plugin for testing"""

        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="simple-plugin",
                version="1.0.0",
                author="Test",
                description="Simple test plugin"
            )

    def test_plugin_initialization(self):
        """Test plugin initialization"""
        plugin = self.SimplePlugin()

        assert plugin.status == PluginStatus.INITIALIZED
        assert plugin.enabled == True
        assert plugin.context is None
        assert plugin.metadata.name == "simple-plugin"

    def test_plugin_status_changes(self):
        """Test plugin status changes"""
        plugin = self.SimplePlugin()

        plugin.status = PluginStatus.ACTIVE
        assert plugin.status == PluginStatus.ACTIVE

        plugin.status = PluginStatus.DISABLED
        assert plugin.status == PluginStatus.DISABLED

    def test_plugin_activation(self):
        """Test plugin activation"""
        plugin = self.SimplePlugin()

        plugin.activate()
        assert plugin.status == PluginStatus.ACTIVE

    def test_plugin_deactivation(self):
        """Test plugin deactivation"""
        plugin = self.SimplePlugin()

        plugin.activate()
        plugin.deactivate()
        assert plugin.status == PluginStatus.DISABLED

    def test_plugin_context(self):
        """Test setting plugin context"""
        plugin = self.SimplePlugin()
        context = PluginContext(plugin_name="test")

        plugin.context = context
        assert plugin.context == context

    def test_check_permission(self):
        """Test permission checking"""
        plugin = self.SimplePlugin()
        context = PluginContext(
            plugin_name="test",
            permissions={"operations:execute"}
        )
        plugin.context = context

        assert plugin.check_permission("operations:execute") == True
        assert plugin.check_permission("network:http") == False

    def test_require_permission_success(self):
        """Test require_permission with granted permission"""
        plugin = self.SimplePlugin()
        context = PluginContext(
            plugin_name="test",
            permissions={"operations:execute"}
        )
        plugin.context = context

        # Should not raise
        plugin.require_permission("operations:execute")

    def test_require_permission_failure(self):
        """Test require_permission without permission"""
        from luminous_nix.plugins.errors import PluginPermissionError

        plugin = self.SimplePlugin()
        context = PluginContext(
            plugin_name="test",
            permissions=set()
        )
        plugin.context = context

        with pytest.raises(PluginPermissionError):
            plugin.require_permission("operations:execute")

    def test_validate_context(self):
        """Test context validation"""
        plugin = self.SimplePlugin()

        # No context
        assert plugin.validate_context() == False

        # With context
        plugin.context = PluginContext(plugin_name="test")
        assert plugin.validate_context() == True

    def test_plugin_repr(self):
        """Test plugin string representation"""
        plugin = self.SimplePlugin()
        repr_str = repr(plugin)

        assert "SimplePlugin" in repr_str
        assert "simple-plugin" in repr_str
        assert "1.0.0" in repr_str


class TestPluginHook:
    """Test PluginHook class"""

    def test_hook_creation(self):
        """Test hook creation"""
        hook = PluginHook("test_hook")

        assert hook.name == "test_hook"
        assert len(hook.callbacks) == 0

    def test_hook_register(self):
        """Test registering callbacks"""
        hook = PluginHook("test_hook")
        callback = lambda: None

        hook.register(callback)
        assert len(hook.callbacks) == 1
        assert callback in hook.callbacks

    def test_hook_unregister(self):
        """Test unregistering callbacks"""
        hook = PluginHook("test_hook")
        callback = lambda: None

        hook.register(callback)
        hook.unregister(callback)
        assert len(hook.callbacks) == 0

    def test_hook_trigger(self):
        """Test triggering callbacks"""
        hook = PluginHook("test_hook")
        results = []

        def callback(value):
            results.append(value)

        hook.register(callback)
        hook.trigger(42)

        assert len(results) == 1
        assert results[0] == 42

    def test_hook_trigger_multiple_callbacks(self):
        """Test triggering multiple callbacks"""
        hook = PluginHook("test_hook")
        results = []

        def callback1(value):
            results.append(value * 2)

        def callback2(value):
            results.append(value * 3)

        hook.register(callback1)
        hook.register(callback2)
        hook.trigger(10)

        assert len(results) == 2
        assert 20 in results
        assert 30 in results

    def test_hook_trigger_with_error(self):
        """Test hook continues after callback error"""
        hook = PluginHook("test_hook")
        results = []

        def callback1():
            raise Exception("Test error")

        def callback2():
            results.append("success")

        hook.register(callback1)
        hook.register(callback2)
        hook.trigger()

        # Second callback should still execute despite first failing
        assert len(results) == 1
        assert results[0] == "success"


class TestPluginInfo:
    """Test PluginInfo dataclass"""

    def test_plugin_info(self):
        """Test plugin info creation"""
        info = PluginInfo(
            name="test-plugin",
            version="1.0.0",
            type="operation",
            status=PluginStatus.ACTIVE,
            description="Test plugin",
            author="Test Author",
            enabled=True
        )

        assert info.name == "test-plugin"
        assert info.version == "1.0.0"
        assert info.type == "operation"
        assert info.status == PluginStatus.ACTIVE
        assert info.description == "Test plugin"
        assert info.author == "Test Author"
        assert info.enabled == True
