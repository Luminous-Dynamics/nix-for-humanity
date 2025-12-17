#!/usr/bin/env python3
"""
Test script for plugin auto-loading.

Tests that plugins in the autoload list are automatically loaded.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from luminous_nix.plugins.manager import PluginManager

def test_autoload():
    """Test that autoload plugins are loaded automatically."""
    print("🧪 Testing Plugin Auto-Load\n")
    print("=" * 70)

    # Create plugin manager with auto_load=True
    print("\n📦 Creating PluginManager with auto_load=True...")
    manager = PluginManager(auto_load=True)

    # Check loaded plugins
    loaded_plugins = list(manager._plugins.keys())
    print(f"\n✅ Loaded {len(loaded_plugins)} plugin(s):\n")

    for plugin_name in loaded_plugins:
        plugin = manager._plugins[plugin_name]
        version = plugin.metadata.version if hasattr(plugin, 'metadata') else "unknown"
        print(f"  🔌 {plugin_name}")
        print(f"     Type: {plugin.type}")
        print(f"     Version: {version}")
        print(f"     Status: {plugin.status}")

    # Verify specific plugins
    print("\n" + "=" * 70)
    print("\n🔍 Verifying Expected Plugins:\n")

    expected_plugins = ["hello-world", "docker-operations"]
    for plugin_name in expected_plugins:
        if plugin_name in loaded_plugins:
            print(f"  ✅ {plugin_name} - Auto-loaded successfully!")
        else:
            print(f"  ❌ {plugin_name} - NOT loaded (expected in autoload)")

    print("\n" + "=" * 70)

    if set(expected_plugins) == set(loaded_plugins):
        print("\n✅ All tests passed! Auto-loading works perfectly!")
    else:
        print(f"\n⚠️  Loaded: {loaded_plugins}")
        print(f"⚠️  Expected: {expected_plugins}")

if __name__ == "__main__":
    test_autoload()
