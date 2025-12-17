"""
Test-Driven Development: Plugin System Foundation

Tests for the plugin infrastructure that enables extensibility
through a clean plugin architecture.

Based on: Week 5 Plugin System Foundation

Note: This tests the clean PluginRegistry foundation (plugin_registry.py),
not the feature-rich PluginManager (plugin_system.py).
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional


# === Test Plugin Registration ===

def test_plugin_registry_creation():
    """Test creating a plugin registry"""
    from luminous_nix.core.plugin_registry import PluginRegistry

    registry = PluginRegistry()
    assert registry is not None
    assert len(registry.list_plugins()) == 0


def test_register_plugin():
    """Test registering a plugin"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin

    class TestPlugin(Plugin):
        @property
        def name(self) -> str:
            return "test-plugin"

        @property
        def version(self) -> str:
            return "1.0.0"

    registry = PluginRegistry()
    plugin = TestPlugin()

    registry.register(plugin)

    assert len(registry.list_plugins()) == 1
    assert "test-plugin" in registry.list_plugins()


def test_register_duplicate_plugin_fails():
    """Test that registering duplicate plugin names fails"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin, PluginError

    class TestPlugin(Plugin):
        @property
        def name(self) -> str:
            return "duplicate"

        @property
        def version(self) -> str:
            return "1.0.0"

    registry = PluginRegistry()
    plugin1 = TestPlugin()
    plugin2 = TestPlugin()

    registry.register(plugin1)

    with pytest.raises(PluginError, match="already registered"):
        registry.register(plugin2)


def test_unregister_plugin():
    """Test unregistering a plugin"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin

    class TestPlugin(Plugin):
        @property
        def name(self) -> str:
            return "test-plugin"

        @property
        def version(self) -> str:
            return "1.0.0"

    registry = PluginRegistry()
    plugin = TestPlugin()

    registry.register(plugin)
    assert len(registry.list_plugins()) == 1

    registry.unregister("test-plugin")
    assert len(registry.list_plugins()) == 0


def test_get_plugin():
    """Test retrieving a registered plugin"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin

    class TestPlugin(Plugin):
        @property
        def name(self) -> str:
            return "test-plugin"

        @property
        def version(self) -> str:
            return "1.0.0"

    registry = PluginRegistry()
    plugin = TestPlugin()
    registry.register(plugin)

    retrieved = registry.get_plugin("test-plugin")
    assert retrieved is not None
    assert retrieved.name == "test-plugin"
    assert retrieved.version == "1.0.0"


# === Test Plugin Lifecycle ===

def test_plugin_lifecycle_methods():
    """Test that plugin lifecycle methods are called correctly"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin

    lifecycle_events = []

    class TestPlugin(Plugin):
        @property
        def name(self) -> str:
            return "lifecycle-test"

        @property
        def version(self) -> str:
            return "1.0.0"

        def on_load(self) -> None:
            lifecycle_events.append("on_load")

        def on_enable(self) -> None:
            lifecycle_events.append("on_enable")

        def on_disable(self) -> None:
            lifecycle_events.append("on_disable")

        def on_unload(self) -> None:
            lifecycle_events.append("on_unload")

    registry = PluginRegistry()
    plugin = TestPlugin()

    # Register should call on_load
    registry.register(plugin)
    assert "on_load" in lifecycle_events

    # Enable
    registry.enable_plugin("lifecycle-test")
    assert "on_enable" in lifecycle_events

    # Disable
    registry.disable_plugin("lifecycle-test")
    assert "on_disable" in lifecycle_events

    # Unregister should call on_unload
    registry.unregister("lifecycle-test")
    assert "on_unload" in lifecycle_events

    # Verify order
    assert lifecycle_events == ["on_load", "on_enable", "on_disable", "on_unload"]


def test_plugin_enabled_state():
    """Test plugin enabled/disabled state tracking"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin

    class TestPlugin(Plugin):
        @property
        def name(self) -> str:
            return "state-test"

        @property
        def version(self) -> str:
            return "1.0.0"

    registry = PluginRegistry()
    plugin = TestPlugin()

    registry.register(plugin)
    assert not registry.is_enabled("state-test")  # Disabled by default

    registry.enable_plugin("state-test")
    assert registry.is_enabled("state-test")

    registry.disable_plugin("state-test")
    assert not registry.is_enabled("state-test")


# === Test Plugin Discovery ===

def test_discover_plugins_from_directory():
    """Test automatic plugin discovery from directory"""
    from luminous_nix.core.plugin_registry import PluginRegistry

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        plugins_dir = tmpdir / "plugins"
        plugins_dir.mkdir()

        # Create a simple plugin file
        plugin_file = plugins_dir / "test_plugin.py"
        plugin_file.write_text("""
from luminous_nix.core.plugin_registry import Plugin

class SimplePlugin(Plugin):
    @property
    def name(self) -> str:
        return "discovered-plugin"

    @property
    def version(self) -> str:
        return "1.0.0"
""")

        registry = PluginRegistry()
        discovered = registry.discover_plugins(plugins_dir)

        assert len(discovered) >= 1
        assert "discovered-plugin" in [p.name for p in discovered]


def test_discover_skips_invalid_plugins():
    """Test that discovery skips files that aren't valid plugins"""
    from luminous_nix.core.plugin_registry import PluginRegistry

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        plugins_dir = tmpdir / "plugins"
        plugins_dir.mkdir()

        # Create invalid plugin files
        (plugins_dir / "not_a_plugin.txt").write_text("Just text")
        (plugins_dir / "bad_plugin.py").write_text("print('Not a plugin class')")

        registry = PluginRegistry()
        discovered = registry.discover_plugins(plugins_dir)

        # Should discover 0 valid plugins
        assert len(discovered) == 0


# === Test Plugin Dependencies ===

def test_plugin_with_dependencies():
    """Test plugin dependency declaration"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin

    class DependentPlugin(Plugin):
        @property
        def name(self) -> str:
            return "dependent"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def dependencies(self) -> list[str]:
            return ["base-plugin"]

    plugin = DependentPlugin()
    assert "base-plugin" in plugin.dependencies


def test_enable_plugin_checks_dependencies():
    """Test that enabling plugin checks dependencies are satisfied"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin, PluginError

    class BasePlugin(Plugin):
        @property
        def name(self) -> str:
            return "base"

        @property
        def version(self) -> str:
            return "1.0.0"

    class DependentPlugin(Plugin):
        @property
        def name(self) -> str:
            return "dependent"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def dependencies(self) -> list[str]:
            return ["base"]

    registry = PluginRegistry()
    dependent = DependentPlugin()

    # Try to enable without dependency
    registry.register(dependent)

    with pytest.raises(PluginError, match="dependencies not satisfied"):
        registry.enable_plugin("dependent")

    # Now register and enable dependency
    base = BasePlugin()
    registry.register(base)
    registry.enable_plugin("base")

    # Should work now
    registry.enable_plugin("dependent")
    assert registry.is_enabled("dependent")


def test_disable_plugin_checks_dependents():
    """Test that disabling plugin checks if other plugins depend on it"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin, PluginError

    class BasePlugin(Plugin):
        @property
        def name(self) -> str:
            return "base"

        @property
        def version(self) -> str:
            return "1.0.0"

    class DependentPlugin(Plugin):
        @property
        def name(self) -> str:
            return "dependent"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def dependencies(self) -> list[str]:
            return ["base"]

    registry = PluginRegistry()
    base = BasePlugin()
    dependent = DependentPlugin()

    registry.register(base)
    registry.register(dependent)

    registry.enable_plugin("base")
    registry.enable_plugin("dependent")

    # Try to disable base while dependent is enabled
    with pytest.raises(PluginError, match="still has enabled dependents"):
        registry.disable_plugin("base")

    # Disable dependent first
    registry.disable_plugin("dependent")

    # Now should work
    registry.disable_plugin("base")
    assert not registry.is_enabled("base")


# === Test Plugin Versioning ===

def test_plugin_version_validation():
    """Test that plugin versions are validated"""
    from luminous_nix.core.plugin_registry import Plugin, validate_version

    # Valid versions
    assert validate_version("1.0.0")
    assert validate_version("0.1.0")
    assert validate_version("10.20.30")

    # Invalid versions
    assert not validate_version("1.0")
    assert not validate_version("v1.0.0")
    assert not validate_version("1.0.0-beta")
    assert not validate_version("not-a-version")


def test_plugin_version_comparison():
    """Test version comparison for compatibility checking"""
    from luminous_nix.core.plugin_registry import compare_versions

    # Equal
    assert compare_versions("1.0.0", "1.0.0") == 0

    # Less than
    assert compare_versions("1.0.0", "2.0.0") < 0
    assert compare_versions("1.0.0", "1.1.0") < 0
    assert compare_versions("1.0.0", "1.0.1") < 0

    # Greater than
    assert compare_versions("2.0.0", "1.0.0") > 0
    assert compare_versions("1.1.0", "1.0.0") > 0
    assert compare_versions("1.0.1", "1.0.0") > 0


def test_plugin_version_compatibility():
    """Test checking version compatibility with dependency requirements"""
    from luminous_nix.core.plugin_registry import is_version_compatible

    # Format: "name>=1.0.0"
    assert is_version_compatible("1.0.0", ">=1.0.0")
    assert is_version_compatible("1.5.0", ">=1.0.0")
    assert is_version_compatible("2.0.0", ">=1.0.0")
    assert not is_version_compatible("0.9.0", ">=1.0.0")

    # Format: "name==1.0.0"
    assert is_version_compatible("1.0.0", "==1.0.0")
    assert not is_version_compatible("1.0.1", "==1.0.0")


# === Test Plugin Metadata ===

def test_plugin_metadata():
    """Test plugin metadata (author, description, etc)"""
    from luminous_nix.core.plugin_registry import Plugin

    class DocumentedPlugin(Plugin):
        @property
        def name(self) -> str:
            return "documented"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def author(self) -> str:
            return "Test Author"

        @property
        def description(self) -> str:
            return "A test plugin with metadata"

        @property
        def homepage(self) -> Optional[str]:
            return "https://example.com/plugin"

    plugin = DocumentedPlugin()

    assert plugin.author == "Test Author"
    assert plugin.description == "A test plugin with metadata"
    assert plugin.homepage == "https://example.com/plugin"


def test_plugin_list_with_metadata():
    """Test listing plugins with their metadata"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin

    class Plugin1(Plugin):
        @property
        def name(self) -> str:
            return "plugin1"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def description(self) -> str:
            return "First plugin"

    class Plugin2(Plugin):
        @property
        def name(self) -> str:
            return "plugin2"

        @property
        def version(self) -> str:
            return "2.0.0"

        @property
        def description(self) -> str:
            return "Second plugin"

    registry = PluginRegistry()
    registry.register(Plugin1())
    registry.register(Plugin2())

    plugins_info = registry.list_plugins_with_metadata()

    assert len(plugins_info) == 2
    assert plugins_info["plugin1"]["version"] == "1.0.0"
    assert plugins_info["plugin1"]["description"] == "First plugin"
    assert plugins_info["plugin2"]["version"] == "2.0.0"
    assert plugins_info["plugin2"]["description"] == "Second plugin"


# === Test Error Handling ===

def test_enable_nonexistent_plugin_fails():
    """Test that enabling non-existent plugin fails gracefully"""
    from luminous_nix.core.plugin_registry import PluginRegistry, PluginError

    registry = PluginRegistry()

    with pytest.raises(PluginError, match="not found"):
        registry.enable_plugin("nonexistent")


def test_disable_nonexistent_plugin_fails():
    """Test that disabling non-existent plugin fails gracefully"""
    from luminous_nix.core.plugin_registry import PluginRegistry, PluginError

    registry = PluginRegistry()

    with pytest.raises(PluginError, match="not found"):
        registry.disable_plugin("nonexistent")


def test_plugin_lifecycle_exception_handling():
    """Test that exceptions in plugin lifecycle methods are handled"""
    from luminous_nix.core.plugin_registry import PluginRegistry, Plugin, PluginError

    class BrokenPlugin(Plugin):
        @property
        def name(self) -> str:
            return "broken"

        @property
        def version(self) -> str:
            return "1.0.0"

        def on_enable(self) -> None:
            raise RuntimeError("Plugin initialization failed")

    registry = PluginRegistry()
    plugin = BrokenPlugin()
    registry.register(plugin)

    with pytest.raises(PluginError, match="Failed to enable plugin"):
        registry.enable_plugin("broken")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
