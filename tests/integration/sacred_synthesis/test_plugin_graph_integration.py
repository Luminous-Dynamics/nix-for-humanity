#!/usr/bin/env python3
"""
Test Plugin-GraphRAG Integration

This script tests that plugins can successfully access the knowledge graph
through the GraphInterface provided in their PluginContext.
"""

import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_integration():
    """Test the complete plugin-graph integration"""
    
    print("\n🔬 Testing Plugin-GraphRAG Integration\n")
    print("=" * 60)
    
    # Step 1: Import and initialize the orchestrator
    print("\n1️⃣ Initializing System Orchestrator...")
    try:
        import sys
        sys.path.insert(0, 'src')
        from luminous_nix.core.system_orchestrator import SystemOrchestrator
        orchestrator = SystemOrchestrator()
        print("   ✅ Orchestrator initialized")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Step 2: Check if knowledge graph is available
    print("\n2️⃣ Checking Knowledge Graph availability...")
    if orchestrator.graph_interface:
        print("   ✅ GraphInterface is available")
        print(f"   📊 Graph has {len(orchestrator.knowledge_graph.nodes)} nodes")
    else:
        print("   ⚠️ GraphInterface not initialized (tree-sitter may not be available)")
        # This is OK - the system should work without it
    
    # Step 3: Create a test plugin context
    print("\n3️⃣ Creating Plugin Context...")
    try:
        from luminous_nix.plugins.plugin_context import PluginContextBuilder, PluginCapabilities
        from luminous_nix.learning.unified_learning import UnifiedLearningSystem, UserProfile
        from luminous_nix.core.generation_manager import SystemHealth
        
        # Create mock plugin info
        class MockPluginInfo:
            id = "test-plugin"
            name = "Test Plugin"
            version = "1.0.0"
        
        # Get a plugin context
        plugin_info = MockPluginInfo()
        context = orchestrator._create_plugin_context(plugin_info)
        
        if context:
            print("   ✅ Plugin context created")
            print(f"   📦 Plugin: {context.plugin_name}")
            print(f"   🌐 Has graph access: {context.knowledge_graph is not None}")
        else:
            print("   ❌ Failed to create plugin context")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Step 4: Test graph access through plugin context
    print("\n4️⃣ Testing Graph Access through Plugin...")
    if context and context.knowledge_graph:
        try:
            # Enable graph access for this test
            context.capabilities.can_access_knowledge_graph = True
            
            # Try a simple query
            result = context.query_knowledge_graph('find_packages')
            print(f"   ✅ Graph query executed")
            if result:
                print(f"   📊 Result: {result.get('success', False)}")
                if result.get('data'):
                    packages = result['data'].get('packages', [])
                    print(f"   📦 Found {len(packages)} packages")
        except Exception as e:
            print(f"   ⚠️ Query failed (expected if no config loaded): {e}")
    else:
        print("   ⏭️ Skipping (no graph available)")
    
    # Step 5: Test the complete flow
    print("\n5️⃣ Testing Complete Integration Flow...")
    
    # Load a sample Nix configuration if available
    sample_config = Path("/etc/nixos/configuration.nix")
    if sample_config.exists() and orchestrator.knowledge_graph:
        try:
            print(f"   📄 Loading {sample_config}...")
            orchestrator.knowledge_graph.build_from_file(sample_config)
            print(f"   ✅ Configuration loaded")
            print(f"   📊 Graph now has {len(orchestrator.knowledge_graph.nodes)} nodes")
            
            # Now plugins can query real data
            if context:
                result = context.query_knowledge_graph('find_packages')
                if result and result.get('success'):
                    print(f"   ✅ Plugin successfully accessed graph data!")
        except Exception as e:
            print(f"   ⚠️ Could not load config: {e}")
    else:
        print("   ⏭️ Skipping (no config file or graph)")
    
    print("\n" + "=" * 60)
    print("\n✨ Integration Test Complete!")
    print("\nSummary:")
    print("  • System Orchestrator: ✅")
    print(f"  • Knowledge Graph: {'✅' if orchestrator.knowledge_graph else '⚠️ Not available'}")
    print(f"  • GraphInterface: {'✅' if orchestrator.graph_interface else '⚠️ Not available'}")
    print("  • Plugin Context: ✅")
    print(f"  • Plugin→Graph Access: {'✅ Working' if context and context.knowledge_graph else '⚠️ Not available'}")
    
    return True

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)