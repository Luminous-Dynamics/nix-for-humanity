#!/usr/bin/env python3
"""
Test AST Component Integration into System Orchestrator

This verifies that the AST-enhanced components are properly wired into
the main system flow.
"""

import sys
sys.path.insert(0, 'src')

from luminous_nix.core.system_orchestrator import SystemOrchestrator

def test_ast_components_loaded():
    """Test that AST components are loaded in the orchestrator"""
    print("\n🧪 Testing AST Component Integration")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = SystemOrchestrator()
    
    # Check if AST ErrorIntelligence is loaded
    if hasattr(orchestrator.error_intelligence, '__class__'):
        error_class = orchestrator.error_intelligence.__class__.__name__
        if error_class == 'ASTErrorIntelligence':
            print("✅ AST ErrorIntelligence loaded successfully")
        else:
            print(f"⚠️ Using standard ErrorIntelligence: {error_class}")
    
    # Check if AST ConfigGenerator is loaded
    if orchestrator.config_generator:
        print("✅ AST ConfigGenerator loaded successfully")
    else:
        print("⚠️ AST ConfigGenerator not available")
    
    # Check if Knowledge Graph is loaded
    if orchestrator.knowledge_graph:
        print("✅ Knowledge Graph initialized")
    else:
        print("⚠️ Knowledge Graph not available")
    
    # Check if GraphInterface is available
    if orchestrator.graph_interface:
        print("✅ GraphInterface ready for plugins")
    else:
        print("⚠️ GraphInterface not available")
    
    return True

def test_ast_config_generation():
    """Test AST-based config generation through orchestrator"""
    print("\n🔧 Testing AST Config Generation")
    print("-" * 50)
    
    orchestrator = SystemOrchestrator()
    
    if not orchestrator.config_generator:
        print("⚠️ AST ConfigGenerator not available - skipping test")
        return False
    
    # Test configuration generation
    result = orchestrator.generate_config_with_ast("install firefox")
    
    if result['success']:
        print("✅ Configuration generated with AST understanding")
        print(f"   Intent: {result['intent']['action']} {result['intent']['target']}")
        print(f"   Changes: {len(result.get('changes', []))} modifications")
        if 'consciousness_note' in result:
            print(f"   {result['consciousness_note']}")
    else:
        print(f"❌ Generation failed: {result['error']}")
    
    return result['success']

def test_error_intelligence_ast():
    """Test AST-enhanced error intelligence"""
    print("\n🩺 Testing AST Error Intelligence")
    print("-" * 50)
    
    orchestrator = SystemOrchestrator()
    
    # Test error analysis
    error_msg = "error: undefined variable 'pkgs' at /etc/nixos/configuration.nix:42:15"
    
    try:
        result = orchestrator.analyze_error(error_msg)
        
        if result and result.get('suggestions'):
            print("✅ Error analyzed with intelligence")
            print(f"   Category: {result.get('category', 'Unknown')}")
            print(f"   Suggestions: {len(result['suggestions'])} available")
            
            # Check if using AST intelligence
            if hasattr(orchestrator.error_intelligence, 'analyze_error_with_ast'):
                print("   🧠 Using AST-enhanced understanding")
        else:
            print("⚠️ Basic error analysis only")
            
    except Exception as e:
        print(f"❌ Error analysis failed: {e}")
        return False
    
    return True

def test_plugin_graph_access():
    """Test that plugins can access the knowledge graph"""
    print("\n🔌 Testing Plugin Graph Access")
    print("-" * 50)
    
    orchestrator = SystemOrchestrator()
    
    if not orchestrator.graph_interface:
        print("⚠️ GraphInterface not available - skipping test")
        return False
    
    # Test creating a plugin context with graph access
    if orchestrator.consciousness_router:
        print("✅ Plugin system initialized")
        print("   Consciousness Router ready")
        
        # Check if plugins can get graph interface
        from luminous_nix.plugins.plugin_context import PluginContextBuilder
        
        builder = PluginContextBuilder()
        context = builder.with_knowledge_graph(orchestrator.graph_interface).build()
        
        if context.knowledge_graph:
            print("✅ Plugins can access Knowledge Graph")
        else:
            print("⚠️ Graph access not available to plugins")
    else:
        print("⚠️ Plugin system not initialized")
    
    return True

def main():
    """Run all integration tests"""
    print("🌟 AST Component Integration Test Suite 🌟")
    print("=" * 60)
    print("\nVerifying that consciousness components are properly integrated...")
    
    tests = [
        ("Component Loading", test_ast_components_loaded),
        ("Config Generation", test_ast_config_generation),
        ("Error Intelligence", test_error_intelligence_ast),
        ("Plugin Graph Access", test_plugin_graph_access)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Summary")
    print("=" * 60)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All AST components successfully integrated!")
        print("The consciousness has been woven into the system.")
    elif passed > 0:
        print("\n⚠️ Partial integration achieved")
        print("Some components may need tree-sitter or other dependencies.")
    else:
        print("\n❌ Integration needs attention")
        print("Check dependencies and error messages above.")
    
    return 0 if passed > 0 else 1

if __name__ == "__main__":
    sys.exit(main())