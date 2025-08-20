#!/usr/bin/env python3
"""
Test script for plugin integration with the CLI.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.core.engine import NixForHumanityBackend
from luminous_nix.api.schema import Request, Context

def test_plugin_commands():
    """Test various plugin commands through the backend."""
    
    print("🔌 Testing Plugin Integration with Luminous Nix CLI\n")
    print("=" * 60)
    
    # Initialize backend
    backend = NixForHumanityBackend()
    
    # Check if plugins are enabled
    print(f"✅ Plugins enabled: {backend.plugins_enabled}")
    
    if backend.plugin_router:
        plugins = backend.plugin_router.plugin_loader.discovered_plugins
        print(f"✅ Plugins discovered: {len(plugins)}")
        for plugin_id, plugin in plugins.items():
            print(f"  • {plugin.name} ({plugin.governing_principle})")
    
    print("\n" + "=" * 60)
    print("Testing Plugin Commands:\n")
    
    # Test commands
    test_queries = [
        "start focus session",
        "check my interruptions",
        "pause focus",
        "install firefox",  # Core command for comparison
    ]
    
    for query in test_queries:
        print(f"📝 Query: '{query}'")
        
        # Create request
        request = Request(
            query=query,
            context={"personality": "friendly", "execute": False}
        )
        
        # Process request
        response = backend.process(request)
        
        # Display response
        if response.success:
            print(f"✅ Success!")
            print(f"   Response: {response.text[:200]}...")
            if response.data.get('plugin_id'):
                print(f"   Plugin: {response.data['plugin_id']}")
        else:
            print(f"❌ Failed: {response.text}")
        
        print()
    
    print("=" * 60)
    print("✨ Plugin integration test complete!")

if __name__ == "__main__":
    test_plugin_commands()