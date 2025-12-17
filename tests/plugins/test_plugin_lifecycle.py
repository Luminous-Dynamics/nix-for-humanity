"""
Tests for plugin lifecycle management.

Tests lifecycle state transitions, events, and graceful shutdown.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from luminous_nix.plugins.lifecycle import (
    PluginLifecycleManager,
    LifecycleEvent
)
from luminous_nix.plugins.base import (
    Plugin,
    PluginStatus,
    PluginConfig,
    PluginContext,
    PluginMetadata
)
from luminous_nix.plugins.discovery import PluginManifest
from luminous_nix.plugins.interfaces import HookPlugin


class TestLifecycleEvent:
    """Test LifecycleEvent enum"""

    def test_lifecycle_events_exist(self):
        """Test all lifecycle events are defined"""
        assert LifecycleEvent.DISCOVERED.value == "discovered"
        assert LifecycleEvent.VALIDATED.value == "validated"
        assert LifecycleEvent.LOADED.value == "loaded"
        assert LifecycleEvent.INITIALIZED.value == "initialized"
        assert LifecycleEvent.ACTIVATED.value == "activated"
        assert LifecycleEvent.DEACTIVATED.value == "deactivated"
        assert LifecycleEvent.FAILED.value == "failed"
        assert LifecycleEvent.UNLOADED.value == "unloaded"


class TestPluginLifecycleManager:
    """Test PluginLifecycleManager"""

    @pytest.fixture
    def mock_plugin(self):
        """Create mock plugin"""
        class MockPlugin(HookPlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="mock-plugin",
                    version="1.0.0",
                    author="Test",
                    description="Mock plugin"
                )

            def pre_operation(self, state):
                pass

        return MockPlugin()

    @pytest.fixture
    def sample_manifest(self):
        """Create sample manifest"""
        return PluginManifest(
            name="test-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=Path("/test/path"),
            manifest_file=Path("/test/path/plugin.toml")
        )

    def test_lifecycle_initialization(self):
        """Test lifecycle manager initialization"""
        config = PluginConfig()
        manager = PluginLifecycleManager(config)

        assert manager.config == config
        assert len(manager._plugins) == 0
        assert len(manager._event_callbacks) == 0

    def test_register_event_callback(self):
        """Test registering event callbacks"""
        manager = PluginLifecycleManager(PluginConfig())

        callback = Mock()
        manager.register_event_callback(LifecycleEvent.LOADED, callback)

        assert LifecycleEvent.LOADED in manager._event_callbacks
        assert callback in manager._event_callbacks[LifecycleEvent.LOADED]

    def test_unregister_event_callback(self):
        """Test unregistering event callbacks"""
        manager = PluginLifecycleManager(PluginConfig())

        callback = Mock()
        manager.register_event_callback(LifecycleEvent.LOADED, callback)
        manager.unregister_event_callback(LifecycleEvent.LOADED, callback)

        assert callback not in manager._event_callbacks.get(LifecycleEvent.LOADED, [])

    def test_event_callback_triggered(self, mock_plugin, sample_manifest):
        """Test that event callbacks are triggered"""
        manager = PluginLifecycleManager(PluginConfig())

        callback = Mock()
        manager.register_event_callback(LifecycleEvent.LOADED, callback)

        # Mock the loader to return our mock plugin
        with patch.object(manager.loader, 'load_plugin', return_value=mock_plugin):
            manager.load_plugin(sample_manifest)

        # Callback should have been called
        callback.assert_called_once()

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_load_plugin_state_transitions(self, mock_loader_class, sample_manifest):
        """Test plugin goes through correct state transitions"""
        # Create mock plugin
        mock_plugin = Mock()
        mock_plugin.status = PluginStatus.INITIALIZED
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        # Mock loader returns our plugin - MUST set this BEFORE creating manager
        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        # Now create manager (will use mocked loader)
        manager = PluginLifecycleManager(PluginConfig())

        # Load plugin
        plugin = manager.load_plugin(sample_manifest)

        # Check plugin was activated
        mock_plugin.activate.assert_called_once()
        assert plugin.status == PluginStatus.ACTIVE

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_activate_plugin(self, mock_loader_class, sample_manifest):
        """Test activating a plugin"""
        mock_plugin = Mock()
        mock_plugin.status = PluginStatus.INITIALIZED
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Load plugin
        manager.load_plugin(sample_manifest)

        # Deactivate first
        manager.deactivate_plugin("test-plugin")

        # Then reactivate
        manager.activate_plugin("test-plugin")

        # Should have called activate twice (once during load, once explicitly)
        assert mock_plugin.activate.call_count == 2

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_deactivate_plugin(self, mock_loader_class, sample_manifest):
        """Test deactivating a plugin"""
        mock_plugin = Mock()
        mock_plugin.status = PluginStatus.ACTIVE
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Load plugin
        manager.load_plugin(sample_manifest)

        # Deactivate
        manager.deactivate_plugin("test-plugin")

        mock_plugin.deactivate.assert_called_once()

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_unload_plugin(self, mock_loader_class, sample_manifest):
        """Test unloading a plugin"""
        mock_plugin = Mock()
        mock_plugin.status = PluginStatus.ACTIVE
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Load plugin
        manager.load_plugin(sample_manifest)

        # Unload
        manager.unload_plugin("test-plugin")

        # Should deactivate and remove
        mock_plugin.deactivate.assert_called_once()
        assert "test-plugin" not in manager._plugins

    def test_unload_nonexistent_plugin(self):
        """Test unloading plugin that doesn't exist"""
        manager = PluginLifecycleManager(PluginConfig())

        # Should not raise
        manager.unload_plugin("nonexistent")

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_get_plugin(self, mock_loader_class, sample_manifest):
        """Test getting a loaded plugin"""
        mock_plugin = Mock()
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Load plugin
        manager.load_plugin(sample_manifest)

        # Get plugin
        plugin = manager.get_plugin("test-plugin")

        assert plugin == mock_plugin

    def test_get_nonexistent_plugin(self):
        """Test getting plugin that doesn't exist"""
        manager = PluginLifecycleManager(PluginConfig())

        plugin = manager.get_plugin("nonexistent")

        assert plugin is None

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_list_plugins(self, mock_loader_class, sample_manifest):
        """Test listing all loaded plugins"""
        manager = PluginLifecycleManager(PluginConfig())

        mock_plugin = Mock()
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        # Load plugin
        manager.load_plugin(sample_manifest)

        # List plugins
        plugins = manager.list_plugins()

        assert len(plugins) == 1
        assert "test-plugin" in plugins

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_shutdown_all_plugins(self, mock_loader_class):
        """Test shutting down all plugins"""
        # Create multiple mock plugins
        plugins = []
        for i in range(3):
            mock_plugin = Mock()
            mock_plugin.metadata = PluginMetadata(
                name=f"plugin-{i}",
                version="1.0.0",
                author="Test",
                description="Test"
            )
            plugins.append(mock_plugin)

        mock_loader_instance = Mock()
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Load all plugins
        for i, plugin in enumerate(plugins):
            mock_loader_instance.load_plugin.return_value = plugin
            manifest = PluginManifest(
                name=f"plugin-{i}",
                version="1.0.0",
                api_version="1.0",
                entry_point_module="main",
                entry_point_class="Plugin",
                plugin_dir=Path("/test"),
                manifest_file=Path("/test/plugin.toml")
            )
            manager.load_plugin(manifest)

        # Shutdown all
        manager.shutdown()

        # All plugins should be deactivated
        for plugin in plugins:
            plugin.deactivate.assert_called_once()

        # Manager should be empty
        assert len(manager._plugins) == 0

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_load_plugin_with_error(self, mock_loader_class, sample_manifest):
        """Test loading plugin that raises error"""
        from luminous_nix.plugins.errors import PluginLoadError

        # Mock loader raises error
        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.side_effect = PluginLoadError("Load failed")
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Should propagate error
        with pytest.raises(PluginLoadError):
            manager.load_plugin(sample_manifest)

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_activate_disabled_plugin(self, mock_loader_class, sample_manifest):
        """Test activating a disabled plugin"""
        mock_plugin = Mock()
        mock_plugin.status = PluginStatus.DISABLED
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Load plugin
        manager.load_plugin(sample_manifest)

        # Deactivate
        manager.deactivate_plugin("test-plugin")
        mock_plugin.status = PluginStatus.DISABLED

        # Reactivate
        manager.activate_plugin("test-plugin")

        # Should activate again
        assert mock_plugin.activate.call_count >= 2

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_multiple_event_callbacks(self, mock_loader_class, sample_manifest):
        """Test multiple callbacks for same event"""
        manager = PluginLifecycleManager(PluginConfig())

        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        manager.register_event_callback(LifecycleEvent.LOADED, callback1)
        manager.register_event_callback(LifecycleEvent.LOADED, callback2)
        manager.register_event_callback(LifecycleEvent.LOADED, callback3)

        mock_plugin = Mock()
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        # Load plugin
        manager.load_plugin(sample_manifest)

        # All callbacks should be called
        callback1.assert_called_once()
        callback2.assert_called_once()
        callback3.assert_called_once()

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_event_callback_error_handling(self, mock_loader_class, sample_manifest):
        """Test that callback errors don't break lifecycle"""
        manager = PluginLifecycleManager(PluginConfig())

        # Callback that raises error
        bad_callback = Mock(side_effect=Exception("Callback failed"))
        good_callback = Mock()

        manager.register_event_callback(LifecycleEvent.LOADED, bad_callback)
        manager.register_event_callback(LifecycleEvent.LOADED, good_callback)

        mock_plugin = Mock()
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        # Load plugin (should not raise even with bad callback)
        plugin = manager.load_plugin(sample_manifest)

        # Plugin should still be loaded
        assert plugin is not None

        # Good callback should still be called
        good_callback.assert_called_once()

    @patch('luminous_nix.plugins.lifecycle.PluginLoader')
    def test_plugin_cleanup_on_unload(self, mock_loader_class, sample_manifest):
        """Test cleanup is called on unload"""
        mock_plugin = Mock()
        mock_plugin.metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )

        mock_loader_instance = Mock()
        mock_loader_instance.load_plugin.return_value = mock_plugin
        mock_loader_class.return_value = mock_loader_instance

        manager = PluginLifecycleManager(PluginConfig())

        # Load plugin
        manager.load_plugin(sample_manifest)

        # Unload
        manager.unload_plugin("test-plugin")

        # Should call cleanup if available
        if hasattr(mock_plugin, 'cleanup'):
            mock_plugin.cleanup.assert_called_once()
