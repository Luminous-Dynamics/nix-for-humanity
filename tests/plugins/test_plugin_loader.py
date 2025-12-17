"""
Tests for plugin loader.

Tests dynamic module loading, class instantiation, and context injection.
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from luminous_nix.plugins.loader import PluginLoader
from luminous_nix.plugins.discovery import PluginManifest
from luminous_nix.plugins.base import (
    Plugin,
    PluginMetadata,
    PluginContext,
    PluginConfig,
    PluginStatus
)
from luminous_nix.plugins.interfaces import HookPlugin
from luminous_nix.plugins.errors import PluginLoadError


class TestPluginLoader:
    """Test PluginLoader class"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def simple_plugin_code(self):
        """Simple plugin Python code"""
        return '''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class SimplePlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="simple-plugin",
            version="1.0.0",
            author="Test",
            description="Simple test plugin"
        )

    def pre_operation(self, state):
        pass

    def post_operation(self, state):
        pass
'''

    @pytest.fixture
    def create_plugin_module(self, temp_plugin_dir, simple_plugin_code):
        """Helper to create a plugin module"""
        def _create(plugin_name="test-plugin", code=None):
            plugin_dir = temp_plugin_dir / plugin_name
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # Create main.py
            main_file = plugin_dir / "main.py"
            main_file.write_text(code or simple_plugin_code)

            return plugin_dir
        return _create

    @pytest.fixture
    def sample_manifest(self, temp_plugin_dir):
        """Create sample manifest"""
        plugin_dir = temp_plugin_dir / "test-plugin"
        plugin_dir.mkdir()

        return PluginManifest(
            name="test-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="SimplePlugin",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"
        )

    def test_loader_initialization(self):
        """Test loader initialization"""
        config = PluginConfig()
        loader = PluginLoader(config)

        assert loader.config == config
        assert len(loader._module_cache) == 0

    def test_load_simple_plugin(self, create_plugin_module, sample_manifest):
        """Test loading a simple plugin"""
        create_plugin_module("test-plugin")

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(sample_manifest)

        assert plugin is not None
        assert isinstance(plugin, Plugin)
        assert plugin.metadata.name == "simple-plugin"
        assert plugin.status == PluginStatus.INITIALIZED

    def test_load_plugin_with_context(self, create_plugin_module, sample_manifest):
        """Test loading plugin with context"""
        create_plugin_module("test-plugin")

        context = PluginContext(plugin_name="test-plugin")

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(sample_manifest, context)

        assert plugin.context == context

    def test_module_caching(self, create_plugin_module, sample_manifest):
        """Test that modules are cached"""
        create_plugin_module("test-plugin")

        loader = PluginLoader(PluginConfig())

        # First load
        plugin1 = loader.load_plugin(sample_manifest)

        # Check cache has module
        assert len(loader._module_cache) == 1

        # Second load (should use cache)
        plugin2 = loader.load_plugin(sample_manifest)

        # Different instances but same module
        assert plugin1 is not plugin2
        assert plugin1.__class__.__module__ == plugin2.__class__.__module__

    def test_load_nonexistent_module(self, temp_plugin_dir):
        """Test loading plugin with nonexistent module"""
        manifest = PluginManifest(
            name="missing",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="nonexistent",
            entry_point_class="Plugin",
            plugin_dir=temp_plugin_dir / "missing",
            manifest_file=temp_plugin_dir / "missing" / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())

        with pytest.raises(PluginLoadError) as exc:
            loader.load_plugin(manifest)

        assert ("Failed to load module" in str(exc.value) or "Module file not found" in str(exc.value))

    def test_load_missing_class(self, create_plugin_module, temp_plugin_dir):
        """Test loading plugin with missing class"""
        # Create plugin with different class name
        code = '''
class WrongClassName:
    pass
'''
        create_plugin_module("wrong-class", code)

        manifest = PluginManifest(
            name="wrong-class",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="ExpectedClassName",
            plugin_dir=temp_plugin_dir / "wrong-class",
            manifest_file=temp_plugin_dir / "wrong-class" / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())

        with pytest.raises(PluginLoadError) as exc:
            loader.load_plugin(manifest)

        assert "does not have class" in str(exc.value)

    def test_load_invalid_plugin_class(self, create_plugin_module, temp_plugin_dir):
        """Test loading class that doesn't inherit from Plugin"""
        code = '''
class NotAPlugin:
    """This doesn't inherit from Plugin"""
    pass
'''
        create_plugin_module("not-plugin", code)

        manifest = PluginManifest(
            name="not-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="NotAPlugin",
            plugin_dir=temp_plugin_dir / "not-plugin",
            manifest_file=temp_plugin_dir / "not-plugin" / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())

        with pytest.raises(PluginLoadError) as exc:
            loader.load_plugin(manifest)

        assert "is not a Plugin subclass" in str(exc.value)

    def test_load_plugin_with_syntax_error(self, create_plugin_module, temp_plugin_dir):
        """Test loading plugin with Python syntax error"""
        code = '''
This is not valid Python syntax!!!
class BadPlugin:
    pass
'''
        create_plugin_module("syntax-error", code)

        manifest = PluginManifest(
            name="syntax-error",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="BadPlugin",
            plugin_dir=temp_plugin_dir / "syntax-error",
            manifest_file=temp_plugin_dir / "syntax-error" / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())

        with pytest.raises(PluginLoadError):
            loader.load_plugin(manifest)

    def test_load_plugin_with_import_error(self, create_plugin_module, temp_plugin_dir):
        """Test loading plugin with import errors"""
        code = '''
import nonexistent_module

from luminous_nix.plugins import HookPlugin, PluginMetadata

class ImportErrorPlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
'''
        create_plugin_module("import-error", code)

        manifest = PluginManifest(
            name="import-error",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="ImportErrorPlugin",
            plugin_dir=temp_plugin_dir / "import-error",
            manifest_file=temp_plugin_dir / "import-error" / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())

        with pytest.raises(PluginLoadError):
            loader.load_plugin(manifest)

    def test_unload_plugin(self, create_plugin_module, sample_manifest):
        """Test unloading a plugin"""
        create_plugin_module("test-plugin")

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(sample_manifest)

        # Unload
        loader.unload_plugin("test-plugin")

        # Check cache cleared
        assert "test-plugin" not in loader._module_cache

    def test_unload_nonexistent_plugin(self):
        """Test unloading plugin that wasn't loaded"""
        loader = PluginLoader(PluginConfig())

        # Should not raise
        loader.unload_plugin("nonexistent")

    def test_clear_cache(self, create_plugin_module, sample_manifest):
        """Test clearing all cached modules"""
        create_plugin_module("test-plugin")

        loader = PluginLoader(PluginConfig())
        loader.load_plugin(sample_manifest)

        assert len(loader._module_cache) == 1

        # Clear cache
        loader.clear_cache()

        assert len(loader._module_cache) == 0

    def test_sys_path_manipulation(self, create_plugin_module, sample_manifest):
        """Test that sys.path is temporarily modified"""
        create_plugin_module("test-plugin")

        original_path = sys.path.copy()

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(sample_manifest)

        # sys.path should be restored after load
        assert sys.path == original_path

    def test_load_multiple_plugins(self, create_plugin_module, temp_plugin_dir):
        """Test loading multiple different plugins"""
        # Create two plugins
        create_plugin_module("plugin1")
        create_plugin_module("plugin2")

        manifest1 = PluginManifest(
            name="plugin1",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="SimplePlugin",
            plugin_dir=temp_plugin_dir / "plugin1",
            manifest_file=temp_plugin_dir / "plugin1" / "plugin.toml"
        )

        manifest2 = PluginManifest(
            name="plugin2",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="SimplePlugin",
            plugin_dir=temp_plugin_dir / "plugin2",
            manifest_file=temp_plugin_dir / "plugin2" / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())

        plugin1 = loader.load_plugin(manifest1)
        plugin2 = loader.load_plugin(manifest2)

        assert plugin1 is not None
        assert plugin2 is not None
        assert len(loader._module_cache) == 2

    def test_plugin_with_dependencies(self, create_plugin_module, temp_plugin_dir):
        """Test loading plugin with internal dependencies"""
        plugin_dir = temp_plugin_dir / "deps-plugin"
        plugin_dir.mkdir()

        # Create helper module
        (plugin_dir / "helper.py").write_text('''
def helper_function():
    return "helper"
''')

        # Create main plugin that imports helper
        (plugin_dir / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata
from helper import helper_function

class DepsPlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="deps-plugin",
            version="1.0.0",
            author="Test",
            description="Plugin with dependencies"
        )

    def pre_operation(self, state):
        result = helper_function()
        assert result == "helper"
''')

        manifest = PluginManifest(
            name="deps-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="DepsPlugin",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(manifest)

        # Should load successfully
        assert plugin is not None
        assert isinstance(plugin, Plugin)

    def test_plugin_instantiation_error(self, create_plugin_module, temp_plugin_dir):
        """Test plugin that raises error during instantiation"""
        code = '''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class ErrorPlugin(HookPlugin):
    def __init__(self):
        super().__init__()
        raise RuntimeError("Instantiation failed")

    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
'''
        create_plugin_module("error-plugin", code)

        manifest = PluginManifest(
            name="error-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="ErrorPlugin",
            plugin_dir=temp_plugin_dir / "error-plugin",
            manifest_file=temp_plugin_dir / "error-plugin" / "plugin.toml"
        )

        loader = PluginLoader(PluginConfig())

        with pytest.raises(PluginLoadError) as exc:
            loader.load_plugin(manifest)

        # Error should contain the instantiation error message
        assert ("Instantiation failed" in str(exc.value) or "Failed to load plugin" in str(exc.value))

    def test_reload_plugin(self, create_plugin_module, sample_manifest):
        """Test reloading a plugin"""
        create_plugin_module("test-plugin")

        loader = PluginLoader(PluginConfig())

        # First load
        plugin1 = loader.load_plugin(sample_manifest)

        # Unload
        loader.unload_plugin("test-plugin")

        # Reload
        plugin2 = loader.load_plugin(sample_manifest)

        # Should get new instance
        assert plugin1 is not plugin2


class TestPluginLoaderContextInjection:
    """Test context injection during plugin loading"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def create_plugin(self, temp_plugin_dir):
        """Helper to create a test plugin"""
        def _create():
            plugin_dir = temp_plugin_dir / "test-plugin"
            plugin_dir.mkdir()

            code = '''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class TestPlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test"
        )
'''
            (plugin_dir / "main.py").write_text(code)

            return PluginManifest(
                name="test-plugin",
                version="1.0.0",
                api_version="1.0",
                entry_point_module="main",
                entry_point_class="TestPlugin",
                plugin_dir=plugin_dir,
                manifest_file=plugin_dir / "plugin.toml"
            )
        return _create

    def test_inject_basic_context(self, create_plugin):
        """Test injecting basic context"""
        manifest = create_plugin()

        context = PluginContext(plugin_name="test-plugin")

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(manifest, context)

        assert plugin.context == context
        assert plugin.context.plugin_name == "test-plugin"

    def test_inject_context_with_permissions(self, create_plugin):
        """Test injecting context with permissions"""
        manifest = create_plugin()

        context = PluginContext(
            plugin_name="test-plugin",
            permissions={"operations:execute", "filesystem:read"}
        )

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(manifest, context)

        assert plugin.check_permission("operations:execute")
        assert plugin.check_permission("filesystem:read")
        assert not plugin.check_permission("network:http")

    def test_inject_context_with_core_systems(self, create_plugin):
        """Test injecting context with core system references"""
        manifest = create_plugin()

        mock_state_manager = Mock()
        mock_security = Mock()

        context = PluginContext(
            plugin_name="test-plugin",
            state_manager=mock_state_manager,
            security=mock_security
        )

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(manifest, context)

        assert plugin.context.state_manager == mock_state_manager
        assert plugin.context.security == mock_security

    def test_load_without_context(self, create_plugin):
        """Test loading plugin without context"""
        manifest = create_plugin()

        loader = PluginLoader(PluginConfig())
        plugin = loader.load_plugin(manifest)

        assert plugin.context is None
