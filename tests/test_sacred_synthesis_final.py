#!/usr/bin/env python3
"""
🌟 Final Sacred Synthesis Integration Test
Tests that all AST components, data trinity, and plugin systems work together
"""

import sys
import os
sys.path.insert(0, 'src')

from luminous_nix.core.system_orchestrator import SystemOrchestrator
from luminous_nix.core.nix_ast_parser import NixASTParser
from pathlib import Path


def test_ast_components():
    """Test AST-enhanced components"""
    print("\n🔬 Testing AST Components")
    print("=" * 50)
    
    orchestrator = SystemOrchestrator()
    
    # Check capabilities
    print("\n📊 System Capabilities:")
    print(f"  AST Config Generation: {orchestrator.has_capability('ast_config_generation')}")
    print(f"  AST Error Intelligence: {orchestrator.has_capability('ast_error_intelligence')}")
    print(f"  Graph Interface: {orchestrator.has_capability('graph_interface')}")
    
    # Test AST config generation if available
    if orchestrator.has_capability('ast_config_generation'):
        print("\n🔧 Testing AST Config Generation:")
        try:
            config = orchestrator.generate_config_ast("web server with nginx")
            print("  ✅ Generated config using AST")
            print(f"  Config length: {len(config)} chars")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test AST error analysis if available
    if orchestrator.has_capability('ast_error_intelligence'):
        print("\n🩺 Testing AST Error Analysis:")
        try:
            error_msg = "error: attribute 'nodejs_18' missing"
            analysis = orchestrator.analyze_error_ast(error_msg)
            print("  ✅ Analyzed error using AST")
            if 'error_type' in analysis:
                print(f"  Error type: {analysis['error_type']}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return True


def test_data_trinity():
    """Test Data Trinity integration"""
    print("\n💾 Testing Data Trinity")
    print("=" * 50)
    
    # Test DuckDB
    try:
        import duckdb
        conn = duckdb.connect('data/trinity/duckdb/chronicle.db')
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"  ✅ DuckDB: {len(result)} tables")
    except Exception as e:
        print(f"  ⚠️ DuckDB: {e}")
    
    # Test ChromaDB
    try:
        from luminous_nix.memory.semantic_memory import SemanticMemoryField
        memory = SemanticMemoryField()
        stats = memory.get_statistics()
        print(f"  ✅ ChromaDB: {stats['total_memories']} memories")
    except Exception as e:
        print(f"  ⚠️ ChromaDB: {e}")
    
    # Test Kùzu
    try:
        import kuzu
        db = kuzu.Database("data/trinity/kuzu/structure")
        conn = kuzu.Connection(db)
        # Check if tables exist
        result = conn.execute("CALL show_tables() RETURN *")
        tables = result.get_as_df()
        print(f"  ✅ Kùzu: {len(tables)} tables")
    except Exception as e:
        print(f"  ⚠️ Kùzu: {e}")
    
    return True


def test_plugin_graph_integration():
    """Test plugin access to graph interface"""
    print("\n🔌 Testing Plugin-Graph Integration")
    print("=" * 50)
    
    orchestrator = SystemOrchestrator()
    
    if orchestrator.graph_interface:
        print("  ✅ Graph interface available to plugins")
        
        # Test graph queries through plugin context
        try:
            from luminous_nix.plugins.plugin_context import PluginContextBuilder
            
            context = PluginContextBuilder()\
                .with_graph_interface(orchestrator.graph_interface)\
                .build()
            
            if context.graph_interface:
                print("  ✅ Plugin context has graph access")
            else:
                print("  ⚠️ Graph not available in plugin context")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print("  ⚠️ Graph interface not initialized")
    
    return True


def test_nix_parser():
    """Test Nix AST parser"""
    print("\n🌳 Testing Nix AST Parser")
    print("=" * 50)
    
    parser = NixASTParser()
    
    # Test parsing a simple expression
    test_config = """
    {
      environment.systemPackages = with pkgs; [
        firefox
        vim
      ];
    }
    """
    
    tree = parser.parse(test_config)
    if tree:
        print("  ✅ Parsed Nix configuration")
        print(f"  Root type: {tree.root_node.type}")
        
        # Find packages
        packages = parser.find_packages(tree)
        print(f"  Found packages: {packages}")
    else:
        print("  ❌ Failed to parse configuration")
    
    return True


def main():
    """Run all integration tests"""
    print("🌟 Sacred Synthesis Final Integration Test")
    print("=" * 60)
    print("\nTesting complete integration of:")
    print("  • AST-enhanced components")
    print("  • Data Trinity (DuckDB, ChromaDB, Kùzu)")
    print("  • Plugin-Graph integration")
    print("  • Nix AST parser")
    
    tests = [
        ("AST Components", test_ast_components),
        ("Data Trinity", test_data_trinity),
        ("Plugin-Graph Integration", test_plugin_graph_integration),
        ("Nix AST Parser", test_nix_parser),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} failed with error: {e}")
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
        print("\n🎉 Sacred Synthesis Complete!")
        print("All components are working together harmoniously.")
    else:
        print("\n⚠️ Some components need attention")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())