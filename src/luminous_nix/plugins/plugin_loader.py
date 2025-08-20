"""
Plugin Loader - The Invitation to Join Our Ecosystem

This module discovers and loads plugins that have valid manifests,
serving as the bridge between intention and incarnation.
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import yaml
import json

try:
    from .manifest_validator import ManifestValidator, ValidationResult
except ImportError:
    from manifest_validator import ManifestValidator, ValidationResult


@dataclass
class DiscoveredPlugin:
    """A plugin that has been discovered and validated"""
    id: str
    name: str
    version: str
    path: Path
    manifest_path: Path
    manifest_data: Dict
    validation_result: ValidationResult
    
    @property
    def is_valid(self) -> bool:
        return self.validation_result.valid
    
    @property
    def governing_principle(self) -> str:
        return self.manifest_data.get('consciousness', {}).get('governing_principle', 'unknown')
    
    @property
    def sacred_promise(self) -> str:
        return self.manifest_data.get('consciousness', {}).get('sacred_promise', '')


class PluginLoader:
    """
    The Bridge between plugin potential and plugin reality.
    
    This loader discovers plugins, validates their manifests,
    and prepares them for activation within our ecosystem.
    """
    
    def __init__(self, plugins_dir: Optional[Path] = None):
        """
        Initialize the plugin loader.
        
        Args:
            plugins_dir: Directory containing plugins. Defaults to 'plugins' in project root.
        """
        if plugins_dir is None:
            # Default to plugins directory in project root
            plugins_dir = Path(__file__).parent.parent.parent.parent / "plugins"
        
        self.plugins_dir = plugins_dir
        self.validator = ManifestValidator()
        self.discovered_plugins: Dict[str, DiscoveredPlugin] = {}
        
    def discover_plugins(self) -> List[DiscoveredPlugin]:
        """
        Discover all plugins in the plugins directory.
        
        This is the most "embarrassingly simple" version - it just finds
        directories with valid manifest.yaml files and reports them.
        """
        discovered = []
        
        if not self.plugins_dir.exists():
            print(f"⚠️  Plugins directory not found: {self.plugins_dir}")
            return discovered
        
        # Look for all directories that might be plugins
        for item in self.plugins_dir.iterdir():
            if not item.is_dir():
                continue
            
            # Skip hidden directories and common non-plugin dirs
            if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules']:
                continue
            
            # Look for manifest file
            manifest_path = None
            for possible_manifest in ['manifest.yaml', 'manifest.yml', 'manifest.json']:
                candidate = item / possible_manifest
                if candidate.exists():
                    manifest_path = candidate
                    break
            
            if not manifest_path:
                continue
            
            # Validate the manifest
            validation_result = self.validator.validate_manifest(manifest_path)
            
            if validation_result.manifest_data:
                plugin_info = validation_result.manifest_data.get('plugin', {})
                plugin = DiscoveredPlugin(
                    id=plugin_info.get('id', 'unknown'),
                    name=plugin_info.get('name', 'Unknown Plugin'),
                    version=plugin_info.get('version', '0.0.0'),
                    path=item,
                    manifest_path=manifest_path,
                    manifest_data=validation_result.manifest_data,
                    validation_result=validation_result
                )
                discovered.append(plugin)
                self.discovered_plugins[plugin.id] = plugin
        
        return discovered
    
    def print_discovery_report(self):
        """
        Print a beautiful report of all discovered plugins.
        """
        plugins = self.discover_plugins()
        
        if not plugins:
            print("🔍 No plugins found in", self.plugins_dir)
            return
        
        print(f"🎉 Discovered {len(plugins)} plugin(s) in {self.plugins_dir}")
        print("=" * 60)
        
        # Group by validity
        valid_plugins = [p for p in plugins if p.is_valid]
        invalid_plugins = [p for p in plugins if not p.is_valid]
        
        if valid_plugins:
            print(f"\n✅ Valid Plugins ({len(valid_plugins)}):")
            for plugin in valid_plugins:
                print(f"\n  📦 {plugin.name} (v{plugin.version})")
                print(f"     ID: {plugin.id}")
                print(f"     Path: {plugin.path}")
                print(f"     Principle: {plugin.governing_principle}")
                print(f"     Promise: {plugin.sacred_promise[:80]}...")
                
                if plugin.validation_result.has_warnings:
                    print(f"     ⚠️  {len(plugin.validation_result.warnings)} warnings")
        
        if invalid_plugins:
            print(f"\n❌ Invalid Plugins ({len(invalid_plugins)}):")
            for plugin in invalid_plugins:
                print(f"\n  📦 {plugin.name} (v{plugin.version})")
                print(f"     Path: {plugin.path}")
                print(f"     Errors:")
                for error in plugin.validation_result.errors[:3]:  # Show first 3 errors
                    print(f"       • {error}")
                if len(plugin.validation_result.errors) > 3:
                    print(f"       ... and {len(plugin.validation_result.errors) - 3} more")
    
    def get_plugins_by_principle(self, principle: str) -> List[DiscoveredPlugin]:
        """
        Get all valid plugins that serve a specific consciousness principle.
        """
        return [
            p for p in self.discovered_plugins.values()
            if p.is_valid and p.governing_principle == principle
        ]
    
    def load_plugin(self, plugin_id: str) -> Optional[Any]:
        """
        Load a specific plugin module.
        
        NOTE: This is a placeholder for the actual loading logic
        which will be implemented when we build the sandbox.
        """
        plugin = self.discovered_plugins.get(plugin_id)
        if not plugin:
            print(f"❌ Plugin not found: {plugin_id}")
            return None
        
        if not plugin.is_valid:
            print(f"❌ Cannot load invalid plugin: {plugin_id}")
            return None
        
        # For now, just return the plugin info
        # In the future, this will actually import and instantiate the plugin
        print(f"📦 Plugin {plugin_id} ready for loading (sandbox not yet implemented)")
        return plugin
    
    def list_capabilities(self) -> Dict[str, List[str]]:
        """
        List all capabilities (intents) provided by valid plugins.
        """
        capabilities = {}
        
        for plugin in self.discovered_plugins.values():
            if not plugin.is_valid:
                continue
            
            intents = plugin.manifest_data.get('capabilities', {}).get('intents', [])
            for intent in intents:
                pattern = intent.get('pattern', '')
                if pattern:
                    if plugin.id not in capabilities:
                        capabilities[plugin.id] = []
                    capabilities[plugin.id].append(pattern)
        
        return capabilities
    
    def print_capabilities_map(self):
        """
        Print a map of what natural language patterns are handled by which plugins.
        """
        capabilities = self.list_capabilities()
        
        if not capabilities:
            print("📭 No capabilities registered yet")
            return
        
        print("🗺️  Plugin Capabilities Map")
        print("=" * 60)
        
        for plugin_id, patterns in capabilities.items():
            plugin = self.discovered_plugins[plugin_id]
            print(f"\n📦 {plugin.name} ({plugin_id})")
            print(f"   Principle: {plugin.governing_principle}")
            print("   Handles:")
            for pattern in patterns:
                print(f"     • \"{pattern}\"")


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    # Allow custom plugin directory
    if len(sys.argv) > 1:
        plugins_dir = Path(sys.argv[1])
    else:
        plugins_dir = None
    
    loader = PluginLoader(plugins_dir)
    
    print("🔌 Luminous Nix Plugin Discovery System")
    print("=" * 60)
    
    # Discover and report
    loader.print_discovery_report()
    
    # Show capabilities
    print("\n")
    loader.print_capabilities_map()
    
    # Show principle grouping
    print("\n🕊️ Plugins by Consciousness Principle:")
    print("=" * 60)
    
    principles = [
        "amplify_awareness", "protect_attention", "enable_sovereignty",
        "serve_wellbeing", "foster_learning", "build_community",
        "preserve_privacy", "reduce_complexity"
    ]
    
    for principle in principles:
        plugins = loader.get_plugins_by_principle(principle)
        if plugins:
            print(f"\n{principle}:")
            for plugin in plugins:
                print(f"  • {plugin.name} ({plugin.id})")