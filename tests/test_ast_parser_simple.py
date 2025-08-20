#!/usr/bin/env python3
"""
Simple test for NixASTParser without full module loading
"""

import sys
from pathlib import Path

# Test if tree-sitter is available
try:
    import tree_sitter
    print("✅ tree-sitter library is installed")
    TREE_SITTER_AVAILABLE = True
except ImportError:
    print("❌ tree-sitter not installed!")
    print("   Run: pip install tree-sitter")
    TREE_SITTER_AVAILABLE = False

# Test if tree-sitter-nix is available
try:
    import tree_sitter_nix
    print("✅ tree-sitter-nix grammar is installed")
    TREE_SITTER_NIX_AVAILABLE = True
except ImportError:
    print("⚠️ tree-sitter-nix not installed")
    print("   Run: pip install tree-sitter-nix")
    TREE_SITTER_NIX_AVAILABLE = False

if TREE_SITTER_AVAILABLE:
    # Try to use tree-sitter directly
    from tree_sitter import Language, Parser
    
    parser = Parser()
    
    # Test parsing without grammar (will fail but shows tree-sitter works)
    test_code = "{ foo = 42; }"
    
    if TREE_SITTER_NIX_AVAILABLE:
        try:
            # Try to get the Nix language
            import tree_sitter_nix
            
            # This might need adjustment based on how tree_sitter_nix exports its language
            # Different packages export differently
            if hasattr(tree_sitter_nix, 'language'):
                nix_language = Language(tree_sitter_nix.language(), 'nix')
            elif hasattr(tree_sitter_nix, 'LANGUAGE'):
                nix_language = Language(tree_sitter_nix.LANGUAGE, 'nix')
            else:
                print("⚠️ tree-sitter-nix found but language export not recognized")
                nix_language = None
            
            if nix_language:
                parser.set_language(nix_language)
                tree = parser.parse(bytes(test_code, 'utf-8'))
                print(f"✅ Successfully parsed Nix code!")
                print(f"   Root node type: {tree.root_node.type}")
                print(f"   Children: {len(tree.root_node.children)}")
        except Exception as e:
            print(f"❌ Error using tree-sitter-nix: {e}")
    
    print("\n📊 Summary:")
    print(f"  tree-sitter: {'✅ Installed' if TREE_SITTER_AVAILABLE else '❌ Not installed'}")
    print(f"  tree-sitter-nix: {'✅ Installed' if TREE_SITTER_NIX_AVAILABLE else '❌ Not installed'}")
    
    if TREE_SITTER_AVAILABLE and not TREE_SITTER_NIX_AVAILABLE:
        print("\n🔧 Next Step:")
        print("  Install tree-sitter-nix grammar:")
        print("  pip install tree-sitter-nix")
        print("  OR")
        print("  Build grammar from source (more reliable)")
else:
    print("\n❌ Cannot proceed without tree-sitter")
    print("Install with: pip install tree-sitter tree-sitter-nix")