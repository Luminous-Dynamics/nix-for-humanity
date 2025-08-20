"""
Comprehensive test suite for the plugin system.

Tests all seven sacred stones of our plugin architecture.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from luminous_nix.plugins.manifest_validator import ManifestValidator, ValidationResult
from luminous_nix.plugins.plugin_loader import PluginLoader, DiscoveredPlugin
from luminous_nix.plugins.permission_manager import (
    PermissionManager, Permission, RiskLevel, 
    PermissionRequest, ConsentDecision
)
from luminous_nix.plugins.sandbox import PluginSandbox, SandboxViolation, ConsentRequired
from luminous_nix.plugins.consciousness_router import ConsciousnessRouter, RouteMatch


class TestManifestValidator:
    """Test the constitutional law of plugins."""
    
    def test_validate_valid_manifest(self, tmp_path):
        """Test validation of a valid manifest."""
        manifest_content = """
manifest_version: "1.0.0"
plugin:
  id: "test-plugin"
  name: "Test Plugin"
  version: "1.0.0"
  description: "A test plugin"
  author:
    name: "Test Author"
consciousness:
  governing_principle: "protect_attention"
  sacred_promise: "I will protect your focus"
capabilities:
  intents:
    - pattern: "test pattern"
      handler: "handle_test"
boundaries:
  forbidden_actions:
    - "share data externally"
"""
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(manifest_content)
        
        validator = ManifestValidator()
        result = validator.validate_manifest(manifest_path)
        
        assert result.valid
        assert not result.errors
        assert result.manifest_data is not None
    
    def test_validate_invalid_manifest_missing_consciousness(self, tmp_path):
        """Test that manifests without consciousness section are invalid."""
        manifest_content = """
manifest_version: "1.0.0"
plugin:
  id: "test-plugin"
  name: "Test Plugin"
  version: "1.0.0"
  description: "A test plugin"
capabilities:
  intents:
    - pattern: "test pattern"
      handler: "handle_test"
boundaries:
  forbidden_actions:
    - "share data externally"
"""
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(manifest_content)
        
        validator = ManifestValidator()
        result = validator.validate_manifest(manifest_path)
        
        assert not result.valid
        assert "'consciousness' is a required property" in str(result.errors)
    
    def test_semantic_warnings(self, tmp_path):
        """Test that semantic warnings are generated."""
        manifest_content = """
manifest_version: "1.0.0"
plugin:
  id: "test-plugin"
  name: "Test Plugin"
  version: "1.0.0"
  description: "A test plugin"
  author:
    name: "Test Author"
consciousness:
  governing_principle: "protect_attention"
  sacred_promise: "I will protect your focus"
capabilities:
  intents:
    - pattern: "test pattern"
      handler: "handle_test"
  permissions:
    required:
      - "network.internet"
boundaries:
  forbidden_actions: []
"""
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(manifest_content)
        
        validator = ManifestValidator()
        result = validator.validate_manifest(manifest_path)
        
        assert result.valid
        assert result.has_warnings
        assert any("network.internet" in w for w in result.warnings)


class TestPluginLoader:
    """Test the plugin discovery bridge."""
    
    def test_discover_valid_plugin(self, tmp_path):
        """Test discovery of a valid plugin."""
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        manifest_content = """
manifest_version: "1.0.0"
plugin:
  id: "test-plugin"
  name: "Test Plugin"
  version: "1.0.0"
  description: "A test plugin"
  author:
    name: "Test Author"
consciousness:
  governing_principle: "protect_attention"
  sacred_promise: "I will protect your focus"
capabilities:
  intents:
    - pattern: "test pattern"
      handler: "handle_test"
boundaries:
  forbidden_actions:
    - "share data externally"
"""
        (plugin_dir / "manifest.yaml").write_text(manifest_content)
        
        loader = PluginLoader(tmp_path)
        plugins = loader.discover_plugins()
        
        assert len(plugins) == 1
        assert plugins[0].id == "test-plugin"
        assert plugins[0].is_valid
        assert plugins[0].governing_principle == "protect_attention"
    
    def test_skip_invalid_plugin(self, tmp_path):
        """Test that invalid plugins are discovered but marked invalid."""
        plugin_dir = tmp_path / "bad-plugin"
        plugin_dir.mkdir()
        
        manifest_content = """
manifest_version: "1.0.0"
plugin:
  id: "bad-plugin"
  name: "Bad Plugin"
"""
        (plugin_dir / "manifest.yaml").write_text(manifest_content)
        
        loader = PluginLoader(tmp_path)
        plugins = loader.discover_plugins()
        
        assert len(plugins) == 1
        assert not plugins[0].is_valid
    
    def test_get_plugins_by_principle(self, tmp_path):
        """Test filtering plugins by consciousness principle."""
        # Create two plugins with different principles
        for i, principle in enumerate(["protect_attention", "preserve_privacy"]):
            plugin_dir = tmp_path / f"plugin-{i}"
            plugin_dir.mkdir()
            
            manifest_content = f"""
manifest_version: "1.0.0"
plugin:
  id: "plugin-{i}"
  name: "Plugin {i}"
  version: "1.0.0"
  description: "Plugin {i}"
  author:
    name: "Test Author"
consciousness:
  governing_principle: "{principle}"
  sacred_promise: "Promise {i}"
capabilities:
  intents: []
boundaries:
  forbidden_actions: []
"""
            (plugin_dir / "manifest.yaml").write_text(manifest_content)
        
        loader = PluginLoader(tmp_path)
        loader.discover_plugins()
        
        attention_plugins = loader.get_plugins_by_principle("protect_attention")
        assert len(attention_plugins) == 1
        assert attention_plugins[0].id == "plugin-0"
        
        privacy_plugins = loader.get_plugins_by_principle("preserve_privacy")
        assert len(privacy_plugins) == 1
        assert privacy_plugins[0].id == "plugin-1"


class TestPermissionManager:
    """Test the sacred boundary keeper."""
    
    @pytest.fixture
    def manifest(self):
        return {
            'plugin': {'id': 'test-plugin'},
            'consciousness': {
                'governing_principle': 'protect_attention',
                'sacred_promise': 'I protect your focus'
            },
            'capabilities': {
                'permissions': {
                    'required': ['system.notifications', 'process.monitor']
                }
            },
            'boundaries': {
                'forbidden_actions': ['share data externally', 'modify files']
            }
        }
    
    def test_can_perform_allowed_action(self, manifest):
        """Test that allowed actions pass permission check."""
        pm = PermissionManager(manifest)
        
        allowed, reason = pm.can_perform(
            "show notification", 
            Permission.SYSTEM_NOTIFICATIONS
        )
        
        assert allowed
        assert "permitted" in reason
    
    def test_can_perform_forbidden_action(self, manifest):
        """Test that forbidden actions are blocked."""
        pm = PermissionManager(manifest)
        
        allowed, reason = pm.can_perform(
            "share data externally to cloud", 
            Permission.NETWORK_INTERNET
        )
        
        assert not allowed
        assert "forbidden" in reason
    
    def test_can_perform_missing_permission(self, manifest):
        """Test that actions without permission are blocked."""
        pm = PermissionManager(manifest)
        
        allowed, reason = pm.can_perform(
            "write config", 
            Permission.CONFIGURATION_WRITE
        )
        
        assert not allowed
        assert "lacks permission" in reason
    
    def test_needs_consent(self, manifest):
        """Test consent requirement detection."""
        pm = PermissionManager(manifest)
        
        # High risk always needs consent
        assert pm.needs_consent(Permission.CONFIGURATION_WRITE)
        
        # Low risk doesn't need consent if granted
        assert not pm.needs_consent(Permission.SYSTEM_NOTIFICATIONS)
        
        # Medium risk needs consent if not granted
        assert pm.needs_consent(Permission.NETWORK_INTERNET)
    
    def test_generate_consent_prompt(self, manifest):
        """Test educational consent prompt generation."""
        pm = PermissionManager(manifest)
        
        request = pm.request_permission(
            "Monitor focus apps",
            Permission.PROCESS_MONITOR,
            {"reason": "Track interruptions"}
        )
        
        prompt = pm.generate_consent_prompt(request)
        
        assert "test-plugin" in prompt
        assert "protect_attention" in prompt
        assert "I protect your focus" in prompt
        assert "Monitor focus apps" in prompt
        assert "Track interruptions" in prompt


class TestPluginSandbox:
    """Test the sacred vessel of trust."""
    
    @pytest.fixture
    def manifest(self):
        return {
            'plugin': {'id': 'test-plugin'},
            'consciousness': {
                'governing_principle': 'protect_attention',
                'sacred_promise': 'I protect your focus'
            },
            'capabilities': {
                'intents': [
                    {'pattern': 'test action', 'handler': 'handle_test'}
                ],
                'permissions': {
                    'required': ['system.notifications']
                }
            },
            'boundaries': {
                'forbidden_actions': [],
                'resource_limits': {
                    'max_memory_mb': 128,
                    'max_cpu_percent': 10,
                    'max_storage_mb': 100
                }
            }
        }
    
    @pytest.fixture
    def mock_plugin(self):
        """Create a mock plugin for testing."""
        class MockPlugin:
            plugin_id = "test-plugin"
            plugin_version = "1.0.0"
            governing_principle = "protect_attention"
            
            async def handle_test(self, intent_data):
                return {"result": "test successful", "data": intent_data}
        
        return MockPlugin()
    
    @pytest.mark.asyncio
    async def test_execute_valid_intent(self, manifest, mock_plugin):
        """Test executing a valid intent."""
        sandbox = PluginSandbox(manifest, mock_plugin)
        
        result = await sandbox.execute(
            "test action",
            {"test": "data"}
        )
        
        assert result['success']
        assert result['plugin_id'] == 'test-plugin'
        assert result['result']['result'] == 'test successful'
    
    @pytest.mark.asyncio
    async def test_execute_undeclared_intent(self, manifest, mock_plugin):
        """Test that undeclared intents are blocked."""
        sandbox = PluginSandbox(manifest, mock_plugin)
        
        result = await sandbox.execute(
            "undeclared action",
            {"test": "data"}
        )
        
        assert not result['success']
        assert result['error_type'] == 'violation'
        assert "not declared" in result['error']
    
    def test_workspace_creation(self, manifest, mock_plugin):
        """Test that plugin workspace is created."""
        sandbox = PluginSandbox(manifest, mock_plugin)
        
        assert sandbox.workspace.exists()
        assert (sandbox.workspace / "data").exists()
        assert (sandbox.workspace / "cache").exists()
        assert (sandbox.workspace / "logs").exists()
    
    def test_get_boundaries_report(self, manifest, mock_plugin):
        """Test boundaries report generation."""
        sandbox = PluginSandbox(manifest, mock_plugin)
        
        report = sandbox.get_boundaries_report()
        
        assert "test-plugin" in report
        assert "128 MB" in report  # Memory limit
        assert "10%" in report  # CPU limit
        assert str(sandbox.workspace) in report


class TestConsciousnessRouter:
    """Test the sacred dispatcher."""
    
    def test_route_core_pattern(self):
        """Test routing to core for known patterns."""
        router = ConsciousnessRouter()
        
        route = router.route("install firefox")
        
        assert route.handler_type == 'core'
        assert route.intent_pattern == 'install'
        assert route.confidence > 0.9
    
    def test_route_plugin_pattern(self, tmp_path):
        """Test routing to plugin for plugin patterns."""
        # Create a test plugin
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        manifest_content = """
manifest_version: "1.0.0"
plugin:
  id: "test-plugin"
  name: "Test Plugin"
  version: "1.0.0"
  description: "A test plugin"
  author:
    name: "Test Author"
consciousness:
  governing_principle: "protect_attention"
  sacred_promise: "I will protect your focus"
capabilities:
  intents:
    - pattern: "test special action"
      handler: "handle_test"
boundaries:
  forbidden_actions: []
"""
        (plugin_dir / "manifest.yaml").write_text(manifest_content)
        
        router = ConsciousnessRouter(tmp_path)
        route = router.route("test special action")
        
        assert route.handler_type == 'plugin'
        assert route.handler_id == 'test-plugin'
        assert route.confidence > 0.9
    
    def test_route_unknown_pattern(self):
        """Test routing unknown patterns to core with low confidence."""
        router = ConsciousnessRouter()
        
        route = router.route("do something random xyz123")
        
        assert route.handler_type == 'core'
        assert route.intent_pattern == 'unknown'
        assert route.confidence < 0.5
    
    def test_get_plugin_suggestions(self, tmp_path):
        """Test getting plugin suggestions for queries."""
        # Create a test plugin
        plugin_dir = tmp_path / "focus-plugin"
        plugin_dir.mkdir()
        
        manifest_content = """
manifest_version: "1.0.0"
plugin:
  id: "focus-plugin"
  name: "Focus Plugin"
  version: "1.0.0"
  description: "Helps you focus and avoid distractions"
  author:
    name: "Test Author"
consciousness:
  governing_principle: "protect_attention"
  sacred_promise: "I will protect your focus"
capabilities:
  intents:
    - pattern: "block distractions"
      handler: "handle_block"
boundaries:
  forbidden_actions: []
"""
        (plugin_dir / "manifest.yaml").write_text(manifest_content)
        
        router = ConsciousnessRouter(tmp_path)
        suggestions = router.get_plugin_suggestions("help me focus better")
        
        assert len(suggestions) > 0
        assert suggestions[0]['plugin_id'] == 'focus-plugin'
        assert suggestions[0]['relevance'] > 0
    
    @pytest.mark.asyncio
    async def test_execute_core_route(self):
        """Test executing a core route."""
        router = ConsciousnessRouter()
        
        result = await router.execute("install firefox")
        
        assert result['source'] == 'core'
        assert result['intent'] == 'install'
        assert result['confidence'] > 0.9
    
    def test_route_caching(self):
        """Test that routes are cached for efficiency."""
        router = ConsciousnessRouter()
        
        # First route
        route1 = router.route("install firefox")
        
        # Should be cached now
        assert "install firefox" in router.route_cache
        
        # Second route should come from cache
        route2 = router.route("install firefox")
        
        assert route1 is route2  # Same object


if __name__ == "__main__":
    pytest.main([__file__, "-v"])