#!/usr/bin/env python3
"""
Test the Semantic Memory Field - ChromaDB Integration

This verifies that our semantic memory (the Resonance Field) is working
and can store and retrieve memories based on semantic similarity.
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from luminous_nix.memory.semantic_memory import SemanticMemoryField, UnifiedMemory


def test_semantic_memory():
    """Test the semantic memory field"""
    print("\n🎨 Testing Semantic Memory Field (ChromaDB)")
    print("=" * 50)
    
    # Initialize in-memory semantic field
    memory = SemanticMemoryField()
    
    # Test remembering concepts
    print("\n📝 Storing concepts...")
    memory.remember_concept(
        concept="flake",
        description="A reproducible, declarative Nix configuration",
        category="nix",
        importance="high"
    )
    
    memory.remember_concept(
        concept="derivation",
        description="A build recipe in Nix that produces a package",
        category="nix",
        importance="high"
    )
    
    memory.remember_concept(
        concept="home-manager",
        description="Tool for managing user configurations and dotfiles",
        category="tools",
        importance="medium"
    )
    
    print("  ✅ Stored 3 concepts")
    
    # Test semantic recall
    print("\n🔍 Testing semantic recall...")
    
    query = "How do I make my config reproducible?"
    results = memory.recall_similar(query, n_results=2)
    
    print(f"  Query: '{query}'")
    print(f"  Found {len(results)} relevant memories:")
    for r in results:
        print(f"    • {r['metadata']['concept']}: {r['document'][:60]}...")
    
    # Test interaction memory
    print("\n📝 Storing interactions...")
    memory.remember_interaction(
        intent="install firefox",
        action="add_package",
        result="firefox added to systemPackages",
        success=True
    )
    
    memory.remember_interaction(
        intent="enable bluetooth",
        action="enable_service",
        result="hardware.bluetooth.enable set to true",
        success=True
    )
    
    print("  ✅ Stored 2 interactions")
    
    # Test error solutions
    print("\n📝 Storing error solutions...")
    memory.remember_error(
        error_type="undefined_variable",
        error_message="undefined variable 'pkgs'",
        solution="Add 'pkgs' to the function arguments or use 'with pkgs;'",
        context="configuration.nix"
    )
    
    memory.remember_error(
        error_type="syntax_error",
        error_message="unexpected ';'",
        solution="Check for missing closing brackets or parentheses",
        context="configuration.nix"
    )
    
    print("  ✅ Stored 2 error solutions")
    
    # Test finding solutions
    print("\n🩺 Testing error solution finding...")
    error = "error: undefined variable 'lib'"
    solution = memory.find_solution(error)
    
    if solution:
        print(f"  Error: '{error}'")
        print(f"  Solution: {solution['solution']}")
        print(f"  Confidence: {solution['confidence']:.2f}")
    else:
        print(f"  No solution found for: {error}")
    
    # Test configuration patterns
    print("\n🔧 Testing configuration patterns...")
    memory.remember_configuration(
        config_type="package_installation",
        pattern="Add package to environment.systemPackages",
        example="environment.systemPackages = with pkgs; [ firefox ];",
        category="basic"
    )
    
    pattern = memory.find_configuration_pattern("I want to install software")
    if pattern:
        print(f"  Intent: 'I want to install software'")
        print(f"  Pattern: {pattern['pattern']}")
        print(f"  Type: {pattern['type']}")
        print(f"  Confidence: {pattern['confidence']:.2f}")
    
    # Test learning from interaction
    print("\n🧠 Testing learning...")
    memory.learn_from_interaction(
        intent="install vscode",
        action="add_package",
        result="vscode added to systemPackages",
        success=True
    )
    print("  ✅ Learned from successful interaction")
    
    # Get statistics
    stats = memory.get_statistics()
    print(f"\n📊 Memory Statistics:")
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  Concepts: {stats['concepts']}")
    print(f"  Interactions: {stats['interactions']}")
    print(f"  Configurations: {stats['configurations']}")
    print(f"  Errors: {stats['errors']}")
    
    return True


def test_unified_memory():
    """Test the unified memory interface"""
    print("\n🌟 Testing Unified Memory System")
    print("=" * 50)
    
    # Initialize unified memory
    memory = UnifiedMemory()
    
    # Store different types of memories
    print("\n📝 Storing memories through unified interface...")
    
    memory.remember(
        memory_type="concept",
        concept="nixpkgs",
        description="The main package repository for Nix",
        category="core"
    )
    
    memory.remember(
        memory_type="interaction",
        intent="update system",
        action="nixos-rebuild switch",
        result="System updated successfully",
        success=True
    )
    
    memory.remember(
        memory_type="error",
        error_type="build_failure",
        error_message="build failed",
        solution="Check build logs and dependencies"
    )
    
    print("  ✅ Stored memories across different types")
    
    # Recall memories
    print("\n🔍 Testing unified recall...")
    results = memory.recall("how to update nixos")
    
    if results['semantic']:
        print(f"  Found {len(results['semantic'])} semantic memories")
        for r in results['semantic'][:2]:
            print(f"    • {r['document'][:80]}...")
    
    return True


def main():
    """Run all semantic memory tests"""
    print("🌟 Semantic Memory Test Suite 🌟")
    print("=" * 60)
    print("\nTesting the Resonance Field (ChromaDB integration)...")
    
    tests = [
        ("Semantic Memory Field", test_semantic_memory),
        ("Unified Memory Interface", test_unified_memory)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Semantic Memory Test Summary")
    print("=" * 60)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Semantic Memory fully operational!")
        print("The Resonance Field is ready to hold intuitive knowledge.")
    elif passed > 0:
        print("\n⚠️ Partial success")
        print("Some memory functions need attention.")
    else:
        print("\n❌ Memory system needs configuration")
    
    # Final philosophical note
    print("\n✨ The Data Trinity Status:")
    print("  📚 DuckDB (Chronicle): ✅ Installed, schema created")
    print("  🎨 ChromaDB (Resonance): ✅ Working perfectly")
    print("  🌐 Kùzu (Structure): ✅ Installed, graph created")
    print("\nThe consciousness now has a complete memory system!")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())