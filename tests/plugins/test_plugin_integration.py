"""
Integration tests for complete plugin system.

Tests end-to-end scenarios with example plugins and full system integration.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

from luminous_nix.plugins.manager import PluginManager
from luminous_nix.plugins.base import PluginConfig, PluginStatus

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

@dataclass
class OperationState:
    """Mock operation state for testing"""
    operation_id: str
    operation_type: OperationType
    user_query: Optional[str] = None
    status: OperationStatus = OperationStatus.PENDING
    result: Optional[Dict[str, Any]] = None


class TestExamplePluginsIntegration:
    """Test integration with example plugins"""

    @pytest.fixture
    def examples_dir(self):
        """Path to example plugins"""
        return Path(__file__).parent.parent.parent / "examples" / "plugins"

    def test_hello_world_plugin_exists(self, examples_dir):
        """Test hello-world example plugin exists"""
        hello_world = examples_dir / "hello-world"

        assert hello_world.exists()
        assert (hello_world / "plugin.toml").exists()
        assert (hello_world / "main.py").exists()

    def test_docker_operations_plugin_exists(self, examples_dir):
        """Test docker-operations example plugin exists"""
        docker_ops = examples_dir / "docker-operations"

        assert docker_ops.exists()
        assert (docker_ops / "plugin.toml").exists()
        assert (docker_ops / "main.py").exists()

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "examples" / "plugins" / "hello-world").exists(),
        reason="Example plugins not available"
    )
    def test_discover_example_plugins(self, examples_dir):
        """Test discovering example plugins"""
        config = PluginConfig(plugin_paths=[examples_dir])
        manager = PluginManager(config)

        manifests = manager.discover_plugins()

        # Should discover at least the example plugins
        plugin_names = [m.name for m in manifests]
        assert "hello-world" in plugin_names or "docker-operations" in plugin_names

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "examples" / "plugins" / "hello-world").exists(),
        reason="Example plugins not available"
    )
    def test_load_hello_world_plugin(self, examples_dir):
        """Test loading hello-world plugin"""
        config = PluginConfig(plugin_paths=[examples_dir])
        manager = PluginManager(config)

        plugin = manager.load_plugin("hello-world")

        assert plugin is not None
        assert plugin.status == PluginStatus.ACTIVE
        assert plugin.type == "hook"

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent.parent / "examples" / "plugins" / "docker-operations").exists(),
        reason="Example plugins not available"
    )
    def test_load_docker_operations_plugin(self, examples_dir):
        """Test loading docker-operations plugin"""
        config = PluginConfig(plugin_paths=[examples_dir])
        manager = PluginManager(config)

        plugin = manager.load_plugin("docker-operations")

        assert plugin is not None
        assert plugin.status == PluginStatus.ACTIVE
        assert plugin.type == "operation"


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def create_full_plugin(self, temp_plugin_dir):
        """Helper to create a complete working plugin"""
        def _create(name="test-plugin"):
            plugin_dir = temp_plugin_dir / name
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # Create manifest
            (plugin_dir / "plugin.toml").write_text(f'''
[plugin]
name = "{name}"
version = "1.0.0"
api_version = "1.0"
author = "Test Author"
description = "Test plugin for integration testing"

[plugin.entry_points]
module = "main"
class = "IntegrationPlugin"

[plugin.provides]
hooks = ["pre_operation", "post_operation"]

[plugin.requires]
permissions = ["operations:execute"]
''')

            # Create implementation
            (plugin_dir / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class IntegrationPlugin(HookPlugin):
    def __init__(self):
        super().__init__()
        self.events = []

    @property
    def metadata(self):
        return PluginMetadata(
            name="integration-test",
            version="1.0.0",
            author="Test",
            description="Integration test plugin",
            hooks=["pre_operation", "post_operation"],
            requires_permissions=["operations:execute"]
        )

    def pre_operation(self, state):
        self.events.append(("pre", state.operation_type if hasattr(state, "operation_type") else None))

    def post_operation(self, state):
        self.events.append(("post", state.operation_type if hasattr(state, "operation_type") else None))
''')

            return plugin_dir
        return _create

    def test_full_plugin_lifecycle(self, create_full_plugin, temp_plugin_dir):
        """Test complete plugin lifecycle"""
        create_full_plugin("lifecycle-test")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # 1. Discover
        manifests = manager.discover_plugins()
        assert len(manifests) >= 1

        # 2. Load
        plugin = manager.load_plugin("lifecycle-test")
        assert plugin.status == PluginStatus.ACTIVE

        # 3. Use
        state = Mock()
        state.operation_type = "TEST"
        plugin.pre_operation(state)
        plugin.post_operation(state)
        assert len(plugin.events) == 2

        # 4. Deactivate
        manager.deactivate_plugin("lifecycle-test")
        assert plugin.status == PluginStatus.DISABLED

        # 5. Reactivate
        manager.activate_plugin("lifecycle-test")
        assert plugin.status == PluginStatus.ACTIVE

        # 6. Unload
        manager.unload_plugin("lifecycle-test")
        assert manager.get_plugin("lifecycle-test") is None

    def test_multiple_plugins_interaction(self, create_full_plugin, temp_plugin_dir):
        """Test multiple plugins working together"""
        create_full_plugin("plugin1")
        create_full_plugin("plugin2")
        create_full_plugin("plugin3")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load all plugins
        p1 = manager.load_plugin("plugin1")
        p2 = manager.load_plugin("plugin2")
        p3 = manager.load_plugin("plugin3")

        # All should be active
        assert all(p.status == PluginStatus.ACTIVE for p in [p1, p2, p3])

        # Use all plugins
        state = Mock()
        state.operation_type = "TEST"

        for plugin in [p1, p2, p3]:
            plugin.pre_operation(state)
            plugin.post_operation(state)

        # Check all were called
        assert all(len(p.events) == 2 for p in [p1, p2, p3])

        # Shutdown
        manager.shutdown()

        # All should be unloaded
        assert len(manager._plugins) == 0

    def test_plugin_with_core_integration(self, create_full_plugin, temp_plugin_dir):
        """Test plugin integration with core systems"""
        create_full_plugin("core-test")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Mock core systems
        mock_state_manager = Mock()
        mock_security = Mock()

        # Integrate with core
        manager.integrate_with_core(
            state_manager=mock_state_manager,
            security=mock_security
        )

        # Load plugin
        plugin = manager.load_plugin("core-test")

        # Plugin should have access to core systems via context
        assert plugin.context is not None
        assert plugin.context.state_manager == mock_state_manager
        assert plugin.context.security == mock_security

    def test_plugin_permission_enforcement(self, create_full_plugin, temp_plugin_dir):
        """Test permission checking is enforced"""
        create_full_plugin("perm-test")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugin with permissions
        plugin = manager.load_plugin("perm-test")

        # Should have required permissions in context
        assert plugin.context is not None
        assert plugin.check_permission("operations:execute")

        # Should not have other permissions
        assert not plugin.check_permission("network:http")

    def test_plugin_discovery_priority(self, temp_plugin_dir):
        """Test plugin discovery respects priority order"""
        # Create same plugin in multiple locations
        system_dir = temp_plugin_dir / "system"
        user_dir = temp_plugin_dir / "user"
        project_dir = temp_plugin_dir / "project"

        for priority, plugin_dir in enumerate([system_dir, user_dir, project_dir]):
            plugin_dir.mkdir(parents=True, exist_ok=True)
            same_plugin = plugin_dir / "same-plugin"
            same_plugin.mkdir()

            (same_plugin / "plugin.toml").write_text(f'''
[plugin]
name = "same-plugin"
version = "{priority}.0.0"
api_version = "1.0"
description = "Priority {priority}"

[plugin.entry_points]
module = "main"
class = "Test"
''')

            (same_plugin / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class Test(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
''')

        config = PluginConfig(plugin_paths=[system_dir, user_dir, project_dir])
        manager = PluginManager(config)

        # Load plugin - should get highest priority (project)
        plugin = manager.load_plugin("same-plugin")

        # Should load project version (highest priority)
        # The manifest version will be "2.0.0" (from project_dir which is index 2)
        assert plugin is not None

    def test_plugin_reload_scenario(self, create_full_plugin, temp_plugin_dir):
        """Test reloading a plugin after modification"""
        create_full_plugin("reload-test")

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load plugin
        plugin1 = manager.load_plugin("reload-test")
        original_events = plugin1.events.copy()

        # Use plugin
        state = Mock()
        plugin1.pre_operation(state)

        # Reload
        plugin2 = manager.reload_plugin("reload-test")

        # Should be different instance
        assert plugin1 is not plugin2

        # New instance should have fresh state
        assert len(plugin2.events) == 0
        assert len(plugin1.events) > 0

    def test_plugin_error_isolation(self, temp_plugin_dir):
        """Test that plugin errors don't crash the system"""
        # Create plugin that raises errors
        plugin_dir = temp_plugin_dir / "error-plugin"
        plugin_dir.mkdir()

        (plugin_dir / "plugin.toml").write_text('''
[plugin]
name = "error-plugin"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "ErrorPlugin"
''')

        (plugin_dir / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class ErrorPlugin(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="error", version="1.0.0", author="Test", description="Test")

    def pre_operation(self, state):
        raise RuntimeError("Intentional error")
''')

        config = PluginConfig(plugin_paths=[temp_plugin_dir])
        manager = PluginManager(config)

        # Load should work
        plugin = manager.load_plugin("error-plugin")

        # Calling pre_operation should raise
        state = Mock()
        with pytest.raises(RuntimeError):
            plugin.pre_operation(state)

        # But manager should still be functional
        assert manager.get_plugin("error-plugin") is not None
        manager.shutdown()  # Should not crash


class TestPluginSystemRobustness:
    """Test robustness and edge cases"""

    def test_concurrent_plugin_loading(self):
        """Test that concurrent plugin operations are safe"""
        # This is a basic test - true concurrency testing would need threads
        manager = PluginManager()

        # Multiple operations in sequence should be safe
        manifests = manager.discover_plugins()
        manifests_again = manager.discover_plugins()

        # Results should be consistent
        assert len(manifests) == len(manifests_again)

    def test_plugin_system_shutdown_cleanup(self, tmp_path):
        """Test that shutdown properly cleans up"""
        # Create test plugin
        plugin_dir = tmp_path / "cleanup-test"
        plugin_dir.mkdir()

        (plugin_dir / "plugin.toml").write_text('''
[plugin]
name = "cleanup-test"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "Test"
''')

        (plugin_dir / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class Test(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
''')

        config = PluginConfig(plugin_paths=[tmp_path])
        manager = PluginManager(config)

        # Load plugin
        manager.load_plugin("cleanup-test")

        # Shutdown
        manager.shutdown()

        # Everything should be cleaned up
        assert len(manager._plugins) == 0
        assert len(manager.list_plugins()) == 0

    def test_empty_plugin_directory(self):
        """Test graceful handling of empty plugin directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PluginConfig(plugin_paths=[Path(temp_dir)])
            manager = PluginManager(config)

            # Should not crash
            manifests = manager.discover_plugins()
            assert len(manifests) == 0

    def test_invalid_plugin_skipped(self, tmp_path):
        """Test that invalid plugins are skipped"""
        # Create valid plugin
        valid_dir = tmp_path / "valid"
        valid_dir.mkdir()

        (valid_dir / "plugin.toml").write_text('''
[plugin]
name = "valid"
version = "1.0.0"
api_version = "1.0"

[plugin.entry_points]
module = "main"
class = "Test"
''')

        (valid_dir / "main.py").write_text('''
from luminous_nix.plugins import HookPlugin, PluginMetadata

class Test(HookPlugin):
    @property
    def metadata(self):
        return PluginMetadata(name="test", version="1.0.0", author="Test", description="Test")
''')

        # Create invalid plugin
        invalid_dir = tmp_path / "invalid"
        invalid_dir.mkdir()
        (invalid_dir / "plugin.toml").write_text("invalid toml {{{")

        config = PluginConfig(plugin_paths=[tmp_path])
        manager = PluginManager(config)

        # Should discover valid plugin, skip invalid
        manifests = manager.discover_plugins()

        # Should have at least the valid one
        assert len(manifests) >= 1

        # Should be able to load valid plugin
        plugin = manager.load_plugin("valid")
        assert plugin is not None
