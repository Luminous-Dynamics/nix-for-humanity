"""
Tests for plugin discovery system.

Tests PluginDiscovery, PluginManifest parsing, multi-path discovery, and caching.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from luminous_nix.plugins.discovery import (
    PluginDiscovery,
    PluginManifest
)
from luminous_nix.plugins.base import PluginConfig
from luminous_nix.plugins.errors import PluginValidationError


class TestPluginManifest:
    """Test PluginManifest dataclass"""

    def test_manifest_creation(self):
        """Test basic manifest creation"""
        manifest = PluginManifest(
            name="test-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=Path("/test/path"),
            manifest_file=Path("/test/path/plugin.toml")
        )

        assert manifest.name == "test-plugin"
        assert manifest.version == "1.0.0"
        assert manifest.api_version == "1.0"
        assert manifest.entry_point_module == "main"
        assert manifest.entry_point_class == "TestPlugin"

    def test_manifest_with_metadata(self):
        """Test manifest with full metadata"""
        manifest = PluginManifest(
            name="test-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=Path("/test/path"),
            manifest_file=Path("/test/path/plugin.toml"),
            author="Test Author",
            description="Test description",
            homepage="https://example.com",
            license="MIT"
        )

        assert manifest.author == "Test Author"
        assert manifest.description == "Test description"
        assert manifest.homepage == "https://example.com"
        assert manifest.license == "MIT"


class TestPluginDiscovery:
    """Test PluginDiscovery system"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_manifest_content(self):
        """Sample TOML manifest content"""
        return """
[plugin]
name = "test-plugin"
version = "1.0.0"
api_version = "1.0"
author = "Test Author"
description = "Test plugin"

[plugin.entry_points]
module = "main"
class = "TestPlugin"

[plugin.provides]
hooks = ["pre_operation", "post_operation"]

[plugin.requires]
permissions = ["operations:execute"]
"""

    @pytest.fixture
    def create_test_plugin(self, temp_plugin_dir, sample_manifest_content):
        """Helper to create a test plugin"""
        def _create(plugin_name="test-plugin"):
            plugin_dir = temp_plugin_dir / plugin_name
            plugin_dir.mkdir(parents=True, exist_ok=True)

            manifest_file = plugin_dir / "plugin.toml"
            manifest_file.write_text(sample_manifest_content)

            # Create main.py
            main_file = plugin_dir / "main.py"
            main_file.write_text("class TestPlugin: pass")

            return plugin_dir
        return _create

    def test_discovery_initialization(self):
        """Test discovery initialization"""
        config = PluginConfig()
        discovery = PluginDiscovery(config)

        assert discovery.config == config
        assert len(discovery.config.plugin_paths) == 3

    def test_discover_single_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test discovering a single plugin"""
        create_test_plugin("hello-world")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        manifests = discovery.discover_all()

        assert len(manifests) == 1
        assert manifests[0].name == "test-plugin"
        assert manifests[0].version == "1.0.0"

    def test_discover_multiple_plugins(self, create_test_plugin, temp_plugin_dir):
        """Test discovering multiple plugins"""
        create_test_plugin("plugin-one")
        create_test_plugin("plugin-two")
        create_test_plugin("plugin-three")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        manifests = discovery.discover_all()

        assert len(manifests) == 3

    def test_discover_from_multiple_paths(self, temp_plugin_dir, sample_manifest_content):
        """Test discovering from multiple plugin paths"""
        # Create two separate plugin directories
        path1 = temp_plugin_dir / "path1"
        path2 = temp_plugin_dir / "path2"
        path1.mkdir()
        path2.mkdir()

        # Create plugin in each path
        for path, name in [(path1, "plugin1"), (path2, "plugin2")]:
            plugin_dir = path / name
            plugin_dir.mkdir()
            (plugin_dir / "plugin.toml").write_text(sample_manifest_content)
            (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        config = PluginConfig(plugin_paths=[path1, path2])
        discovery = PluginDiscovery(config)

        manifests = discovery.discover_all()
        assert len(manifests) == 2

    def test_find_specific_plugin(self, create_test_plugin, temp_plugin_dir):
        """Test finding a specific plugin by name"""
        create_test_plugin("hello-world")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        manifest = discovery.find_plugin("test-plugin")

        assert manifest is not None
        assert manifest.name == "test-plugin"

    def test_find_nonexistent_plugin(self, temp_plugin_dir):
        """Test finding a plugin that doesn't exist"""
        from luminous_nix.plugins.errors import PluginNotFoundError

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        with pytest.raises(PluginNotFoundError):
            discovery.find_plugin("nonexistent-plugin")

    def test_skip_invalid_manifest(self, temp_plugin_dir):
        """Test that invalid manifests are skipped"""
        # Create plugin with invalid manifest
        plugin_dir = temp_plugin_dir / "bad-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.toml").write_text("invalid toml {{{")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        # Should not raise, just skip invalid
        manifests = discovery.discover_all()
        assert len(manifests) == 0

    def test_skip_missing_required_fields(self, temp_plugin_dir):
        """Test that manifests missing required fields are skipped"""
        # Create plugin missing required fields
        plugin_dir = temp_plugin_dir / "incomplete-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.toml").write_text("""
[plugin]
name = "incomplete"
# Missing version, api_version, entry_points
""")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        manifests = discovery.discover_all()
        # Should skip incomplete manifest
        assert len(manifests) == 0

    def test_manifest_caching(self, create_test_plugin, temp_plugin_dir):
        """Test that discovery results are cached"""
        create_test_plugin("cached-plugin")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        # First discovery
        manifests1 = discovery.discover_all()

        # Second discovery (should use cache)
        manifests2 = discovery.discover_all()

        assert len(manifests1) == len(manifests2)
        assert manifests1[0].name == manifests2[0].name

    def test_clear_cache(self, create_test_plugin, temp_plugin_dir):
        """Test clearing discovery cache"""
        create_test_plugin("plugin1")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        # Discover and cache
        manifests1 = discovery.discover_all()
        assert len(manifests1) == 1

        # Add another plugin
        create_test_plugin("plugin2")

        # Should still have cached result
        manifests2 = discovery.discover_all()
        assert len(manifests2) == 1

        # Clear cache
        discovery.clear_cache()

        # Should discover both now
        manifests3 = discovery.discover_all()
        assert len(manifests3) == 2

    def test_parse_plugin_provides(self, temp_plugin_dir):
        """Test parsing plugin provides section"""
        plugin_dir = temp_plugin_dir / "provides-test"
        plugin_dir.mkdir()

        manifest_content = """
[plugin]
name = "provides-test"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "TestPlugin"

[plugin.provides]
operation_types = ["CUSTOM_OP", "SPECIAL_OP"]
hooks = ["pre_operation", "post_operation"]
"""
        (plugin_dir / "plugin.toml").write_text(manifest_content)
        (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        manifest = discovery.find_plugin("provides-test")

        assert "CUSTOM_OP" in manifest.operation_types
        assert "SPECIAL_OP" in manifest.operation_types
        assert "pre_operation" in manifest.hooks
        assert "post_operation" in manifest.hooks

    def test_parse_plugin_requires(self, temp_plugin_dir):
        """Test parsing plugin requires section"""
        plugin_dir = temp_plugin_dir / "requires-test"
        plugin_dir.mkdir()

        manifest_content = """
[plugin]
name = "requires-test"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "TestPlugin"

[plugin.requires]
permissions = ["operations:execute", "filesystem:read"]
dependencies = ["dep1>=1.0", "dep2>=2.0"]
nix_version = ">=2.4"
"""
        (plugin_dir / "plugin.toml").write_text(manifest_content)
        (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        manifest = discovery.find_plugin("requires-test")

        assert "operations:execute" in manifest.requires_permissions
        assert "filesystem:read" in manifest.requires_permissions
        assert "dep1>=1.0" in manifest.dependencies
        assert manifest.requires_nix_version == ">=2.4"

    def test_ignore_hidden_directories(self, temp_plugin_dir):
        """Test that hidden directories are ignored"""
        # Create hidden plugin directory
        hidden_dir = temp_plugin_dir / ".hidden-plugin"
        hidden_dir.mkdir()
        (hidden_dir / "plugin.toml").write_text("""
[plugin]
name = "hidden"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "Test"
""")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        manifests = discovery.discover_all()
        # Should not discover hidden directories
        assert len(manifests) == 0

    def test_priority_order(self, temp_plugin_dir):
        """Test that plugins are discovered in priority order"""
        # Create same plugin in multiple locations
        system = temp_plugin_dir / "system"
        user = temp_plugin_dir / "user"
        project = temp_plugin_dir / "project"

        for path in [system, user, project]:
            path.mkdir()
            plugin_dir = path / "same-plugin"
            plugin_dir.mkdir()
            (plugin_dir / "plugin.toml").write_text(f"""
[plugin]
name = "same-plugin"
version = "1.0.0"
api_version = "1.0"
description = "From {path.name}"

[plugin.entry_points]
module = "main"
class = "Test"
""")

        # Priority: system < user < project
        config = PluginConfig(plugin_paths=[system, user, project])
        discovery = PluginDiscovery(config)

        # Find plugin (should get highest priority)
        manifest = discovery.find_plugin("same-plugin")

        # Project has highest priority (last in list)
        assert "project" in manifest.description


class TestPluginDiscoveryEdgeCases:
    """Test edge cases in plugin discovery"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_empty_plugin_directory(self):
        """Test discovering from empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PluginConfig(plugin_paths=[Path(temp_dir)])
            discovery = PluginDiscovery(config)

            manifests = discovery.discover_all()
            assert len(manifests) == 0

    def test_nonexistent_plugin_path(self):
        """Test with nonexistent plugin path"""
        config = PluginConfig(plugin_paths=[Path("/nonexistent/path")])
        discovery = PluginDiscovery(config)

        # Should not crash, just return empty
        manifests = discovery.discover_all()
        assert len(manifests) == 0

    def test_plugin_without_main_py(self, temp_plugin_dir):
        """Test plugin directory without main.py"""
        plugin_dir = temp_plugin_dir / "no-main"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.toml").write_text("""
[plugin]
name = "no-main"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "Test"
""")
        # No main.py created

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        # Discovery should still find it (validation happens later)
        manifests = discovery.discover_all()
        assert len(manifests) == 1

    def test_malformed_toml(self, temp_plugin_dir):
        """Test handling of malformed TOML"""
        plugin_dir = temp_plugin_dir / "bad-toml"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.toml").write_text("not valid toml [[[")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        discovery = PluginDiscovery(config)

        # Should skip malformed manifests
        manifests = discovery.discover_all()
        assert len(manifests) == 0
