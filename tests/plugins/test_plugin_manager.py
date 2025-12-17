"""
Tests for main PluginManager.

Tests discovery, loading, unloading, and core system integration.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from luminous_nix.plugins.manager import PluginManager
from luminous_nix.plugins.base import (
    Plugin,
    PluginConfig,
    PluginStatus,
    PluginMetadata,
    PluginInfo
)
from luminous_nix.plugins.interfaces import HookPlugin, OperationPlugin
from luminous_nix.plugins.errors import (
    PluginError,
    PluginNotFoundError,
    PluginValidationError
)


class TestPluginManager:
    """Test PluginManager main functionality"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_plugin_code(self):
        """Sample plugin code"""
        return '''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class TestPlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )

    def pre_operation(self, state):
        pass
'''

    @pytest.fixture
    def create_test_plugin(self, temp_plugin_dir, sample_plugin_code):
        """Helper to create test plugin"""
        def _create(name="test-plugin"):
            plugin_dir = temp_plugin_dir / name
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # Create manifest
            (plugin_dir / "plugin.toml").write_text(f'''
[plugin]
name = "{name}"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "TestPlugin"
''')

            # Create main.py
            (plugin_dir / "main.py").write_text(sample_plugin_code)

            return plugin_dir
        return _create

    def test_manager_initialization(self):
        """Test manager initialization"""
        manager = PluginManager()

        assert manager.discovery is not None
        assert manager.validator is not None
        assert manager.lifecycle is not None
        assert len(manager._plugins) == 0

    def test_manager_with_custom_config(self, temp_plugin_dir):
        """Test manager with custom configuration"""
        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        assert manager.config == config
        assert temp_plugin_dir in manager.config.plugin_paths

    def test_discover_plugins(self, create_test_plugin, temp_plugin_dir):
        """Test discovering plugins"""
        create_test_plugin("plugin1")
        create_test_plugin("plugin2")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        manifests = manager.discover_plugins()

        assert len(manifests) >= 2

    def test_load_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test loading a plugin"""
        create_test_plugin("test-plugin")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        plugin = manager.load_plugin("test-plugin")

        assert plugin is not None
        assert isinstance(plugin, Plugin)
        assert plugin.status == PluginStatus.ACTIVE

    def test_load_nonexistent_plugin(self, temp_plugin_dir):
        """Test loading plugin that doesn't exist"""
        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        with pytest.raises(PluginNotFoundError):
            manager.load_plugin("nonexistent")

    def test_unload_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test unloading a plugin"""
        create_test_plugin("test-plugin")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugin
        manager.load_plugin("test-plugin")

        # Unload
        manager.unload_plugin("test-plugin")

        # Should not be in registry
        assert "test-plugin" not in manager._plugins

    def test_get_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test getting a loaded plugin"""
        create_test_plugin("test-plugin")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugin
        original_plugin = manager.load_plugin("test-plugin")

        # Get it
        plugin = manager.get_plugin("test-plugin")

        assert plugin == original_plugin

    def test_get_nonexistent_plugin(self):
        """Test getting plugin that doesn't exist"""
        manager = PluginManager()

        plugin = manager.get_plugin("nonexistent")

        assert plugin is None

    def test_list_plugins(self, create_test_plugin, temp_plugin_dir):
        """Test listing all loaded plugins"""
        create_test_plugin("plugin1")
        create_test_plugin("plugin2")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugins
        manager.load_plugin("plugin1")
        manager.load_plugin("plugin2")

        # List
        plugins = manager.list_plugins()

        assert len(plugins) >= 2
        assert any(p.name == "test-plugin" for p in plugins)

    def test_activate_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test activating a disabled plugin"""
        create_test_plugin("test-plugin")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load and deactivate
        manager.load_plugin("test-plugin")
        manager.deactivate_plugin("test-plugin")

        # Reactivate
        manager.activate_plugin("test-plugin")

        plugin = manager.get_plugin("test-plugin")
        assert plugin.status == PluginStatus.ACTIVE

    def test_deactivate_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test deactivating a plugin"""
        create_test_plugin("test-plugin")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugin
        manager.load_plugin("test-plugin")

        # Deactivate
        manager.deactivate_plugin("test-plugin")

        plugin = manager.get_plugin("test-plugin")
        assert plugin.status == PluginStatus.DISABLED

    def test_reload_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test reloading a plugin"""
        create_test_plugin("test-plugin")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugin
        plugin1 = manager.load_plugin("test-plugin")

        # Reload
        plugin2 = manager.reload_plugin("test-plugin")

        # Should be different instance
        assert plugin1 is not plugin2
        assert plugin2.status == PluginStatus.ACTIVE

    def test_shutdown(self, create_test_plugin, temp_plugin_dir):
        """Test shutting down all plugins"""
        create_test_plugin("plugin1")
        create_test_plugin("plugin2")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugins
        manager.load_plugin("plugin1")
        manager.load_plugin("plugin2")

        # Shutdown
        manager.shutdown()

        # All plugins should be unloaded
        assert len(manager._plugins) == 0


class TestPluginManagerByType:
    """Test plugin management by type"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def create_typed_plugin(self, plugin_dir, name, plugin_type):
        """Helper to create plugins of different types"""
        pdir = plugin_dir / name
        pdir.mkdir(parents=True, exist_ok=True)

        if plugin_type == "hook":
            code = '''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class TypedPlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
'''
        elif plugin_type == "operation":
            code = '''
from luminous_nix.plugins import OperationPlugin, PluginMetadata

class TypedPlugin(OperationPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")

    def can_handle(self, operation_type: str) -> bool:
        return False

    def execute(self, state):
        return state
'''
        else:
            code = "class TypedPlugin: pass"

        (pdir / "main.py").write_text(code)
        (pdir / "plugin.toml").write_text(f'''
[plugin]
name = "{name}"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "TypedPlugin"
''')

        return pdir

    def test_get_plugins_by_type(self, temp_plugin_dir):
        """Test getting plugins by type"""
        self.create_typed_plugin(temp_plugin_dir, "hook1", "hook")
        self.create_typed_plugin(temp_plugin_dir, "hook2", "hook")
        self.create_typed_plugin(temp_plugin_dir, "op1", "operation")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load all
        manager.load_plugin("hook1")
        manager.load_plugin("hook2")
        manager.load_plugin("op1")

        # Get hooks
        hooks = manager.get_plugins_by_type("hook")
        assert len(hooks) == 2

        # Get operations
        ops = manager.get_plugins_by_type("operation")
        assert len(ops) == 1

    def test_get_operation_plugins(self, temp_plugin_dir):
        """Test getting all operation plugins"""
        self.create_typed_plugin(temp_plugin_dir, "op1", "operation")
        self.create_typed_plugin(temp_plugin_dir, "hook1", "hook")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        manager.load_plugin("op1")
        manager.load_plugin("hook1")

        ops = manager.get_operation_plugins()
        assert len(ops) >= 1
        assert all(isinstance(p, OperationPlugin) for p in ops)

    def test_get_hook_plugins(self, temp_plugin_dir):
        """Test getting all hook plugins"""
        self.create_typed_plugin(temp_plugin_dir, "hook1", "hook")
        self.create_typed_plugin(temp_plugin_dir, "op1", "operation")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        manager.load_plugin("hook1")
        manager.load_plugin("op1")

        hooks = manager.get_hook_plugins()
        assert len(hooks) >= 1
        assert all(isinstance(p, HookPlugin) for p in hooks)


class TestPluginManagerIntegration:
    """Test integration with core systems"""

    def test_integrate_with_core(self):
        """Test integrating plugins with core systems"""
        manager = PluginManager()

        mock_state_manager = Mock()
        mock_security = Mock()
        mock_ai = Mock()
        mock_executor = Mock()

        # Integrate
        manager.integrate_with_core(
            state_manager=mock_state_manager,
            security=mock_security,
            ai=mock_ai,
            executor=mock_executor
        )

        # Core systems should be stored
        assert manager._state_manager == mock_state_manager
        assert manager._security == mock_security
        assert manager._ai == mock_ai
        assert manager._executor == mock_executor

    def test_plugins_receive_core_context(self, tmp_path):
        """Test plugins receive core system context"""
        # Create test plugin
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()

        (plugin_dir / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class TestPlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
''')

        (plugin_dir / "plugin.toml").write_text('''
[plugin]
name = "test-plugin"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "TestPlugin"
''')

        config = PluginConfig(plugin_paths=[tmp_path])
        manager = PluginManager(config)

        # Integrate with mocks
        mock_state_manager = Mock()
        manager.integrate_with_core(state_manager=mock_state_manager)

        # Load plugin
        plugin = manager.load_plugin("test-plugin")

        # Plugin should have context with core systems
        assert plugin.context is not None
        assert plugin.context.state_manager == mock_state_manager


class TestPluginManagerErrorHandling:
    """Test error handling in PluginManager"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_load_invalid_plugin(self, temp_plugin_dir):
        """Test loading plugin with validation errors"""
        # Create invalid plugin (missing required fields)
        plugin_dir = temp_plugin_dir / "invalid"
        plugin_dir.mkdir()

        (plugin_dir / "plugin.toml").write_text('''
[plugin]
name = ""
# Missing version and other required fields
''')

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Should raise appropriate error
        with pytest.raises((PluginValidationError, PluginNotFoundError)):
            manager.load_plugin("invalid")

    def test_double_load_same_plugin(self, temp_plugin_dir):
        """Test loading same plugin twice"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()

        (plugin_dir / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class Test(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
''')

        (plugin_dir / "plugin.toml").write_text('''
[plugin]
name = "test"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "Test"
''')

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # First load
        plugin1 = manager.load_plugin("test")

        # Second load should either:
        # 1. Return existing plugin
        # 2. Reload and return new instance
        # 3. Raise error
        # Any is acceptable behavior
        try:
            plugin2 = manager.load_plugin("test")
            # If it doesn't raise, should return a plugin
            assert plugin2 is not None
        except PluginError:
            # If it raises, that's also acceptable
            pass

    def test_unload_nonexistent_plugin(self):
        """Test unloading plugin that doesn't exist"""
        manager = PluginManager()

        # Should not raise
        manager.unload_plugin("nonexistent")

    def test_activate_nonexistent_plugin(self):
        """Test activating plugin that doesn't exist"""
        manager = PluginManager()

        # Should handle gracefully
        with pytest.raises((PluginError, KeyError)):
            manager.activate_plugin("nonexistent")

    def test_plugin_load_error_cleanup(self, temp_plugin_dir):
        """Test cleanup when plugin load fails"""
        plugin_dir = temp_plugin_dir / "error"
        plugin_dir.mkdir()

        # Plugin with syntax error
        (plugin_dir / "main.py").write_text("This is not valid Python!!!")

        (plugin_dir / "plugin.toml").write_text('''
[plugin]
name = "error"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "Test"
''')

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load should fail
        with pytest.raises(PluginError):
            manager.load_plugin("error")

        # Plugin should not be in registry
        assert "error" not in manager._plugins
