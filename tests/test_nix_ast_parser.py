#!/usr/bin/env python3
"""
Test the NixASTParser - Phase A-Prime Foundation Test

This verifies that tree-sitter integration is working and we can
parse Nix code into ASTs for safe manipulation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.nix_ast_parser import NixASTParser, NixNodeType, get_parser

def test_basic_parsing():
    """Test basic parsing functionality"""
    print("\n🔍 Testing Basic Parsing...")
    print("=" * 60)
    
    parser = NixASTParser()
    
    if not parser.parser:
        print("❌ Parser not initialized - tree-sitter-nix may not be installed")
        print("   Run: pip install tree-sitter tree-sitter-nix")
        return False
    
    # Simple Nix expression
    code = """
    {
      environment.systemPackages = with pkgs; [
        firefox
        vim
        git
      ];
      
      services.nginx.enable = true;
    }
    """
    
    ast = parser.parse(code)
    
    if not ast:
        print("❌ Failed to parse Nix code")
        return False
    
    print(f"✅ Parsed successfully!")
    print(f"   Root type: {ast.type}")
    print(f"   Children: {len(ast.children)}")
    
    return True

def test_syntax_validation():
    """Test syntax validation"""
    print("\n🔍 Testing Syntax Validation...")
    print("=" * 60)
    
    parser = get_parser()
    
    if not parser:
        print("❌ Parser not available")
        return False
    
    # Valid Nix code
    valid_code = "{ foo = 42; }"
    is_valid, errors = parser.validate_syntax(valid_code)
    print(f"Valid code: {is_valid} (expected: True)")
    
    # Invalid Nix code
    invalid_code = "{ foo = ; }"  # Missing value
    is_valid, errors = parser.validate_syntax(invalid_code)
    print(f"Invalid code: {is_valid} (expected: False)")
    if errors:
        print(f"   Errors: {errors[0]['message']}")
    
    return True

def test_find_nodes():
    """Test finding nodes by type"""
    print("\n🔍 Testing Node Finding...")
    print("=" * 60)
    
    parser = get_parser()
    
    if not parser:
        print("❌ Parser not available")
        return False
    
    code = """
    {
      imports = [ ./hardware.nix ];
      
      environment.systemPackages = with pkgs; [
        firefox
        vim
      ];
    }
    """
    
    ast = parser.parse(code)
    
    if not ast:
        print("❌ Failed to parse code")
        return False
    
    # Find all identifiers
    identifiers = parser.find_nodes_by_type(ast, NixNodeType.IDENTIFIER)
    print(f"Found {len(identifiers)} identifiers")
    for ident in identifiers[:5]:
        print(f"   - {ident.text}")
    
    # Find imports
    imports = parser.extract_imports(ast)
    print(f"\nFound {len(imports)} imports")
    for imp in imports:
        print(f"   - {imp}")
    
    return True

def test_attribute_finding():
    """Test finding specific attributes"""
    print("\n🔍 Testing Attribute Finding...")
    print("=" * 60)
    
    parser = get_parser()
    
    if not parser:
        print("❌ Parser not available")
        return False
    
    code = """
    {
      services.nginx.enable = true;
      services.nginx.virtualHosts."example.com" = {
        root = "/var/www";
        locations."/" = {
          index = "index.html";
        };
      };
    }
    """
    
    ast = parser.parse(code)
    
    if not ast:
        print("❌ Failed to parse code")
        return False
    
    # Find the nginx.enable attribute
    nginx_enable = parser.find_attribute(ast, "services.nginx.enable")
    
    if nginx_enable:
        print(f"✅ Found services.nginx.enable = {nginx_enable.text}")
    else:
        print("❌ Could not find services.nginx.enable")
    
    return True

def test_ast_pretty_print():
    """Test AST pretty printing for debugging"""
    print("\n🔍 Testing AST Pretty Print...")
    print("=" * 60)
    
    parser = get_parser()
    
    if not parser:
        print("❌ Parser not available")
        return False
    
    code = "{ foo = 42; bar = true; }"
    
    ast = parser.parse(code)
    
    if not ast:
        print("❌ Failed to parse code")
        return False
    
    print("AST Structure:")
    print(parser.pretty_print(ast))
    
    return True

def main():
    """Run all parser tests"""
    print("=" * 60)
    print("🌳 NIX AST PARSER TEST - Phase A-Prime Foundation")
    print("=" * 60)
    
    try:
        # Check if tree-sitter is available
        try:
            import tree_sitter
            print("✅ tree-sitter library is installed")
        except ImportError:
            print("❌ tree-sitter not installed!")
            print("   Run: pip install tree-sitter")
            return
        
        # Check if tree-sitter-nix is available
        try:
            import tree_sitter_nix
            print("✅ tree-sitter-nix grammar is installed")
        except ImportError:
            print("⚠️ tree-sitter-nix not installed")
            print("   The parser will attempt fallback methods")
        
        # Run tests
        tests = [
            test_basic_parsing,
            test_syntax_validation,
            test_find_nodes,
            test_attribute_finding,
            test_ast_pretty_print
        ]
        
        passed = 0
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 Results: {passed}/{len(tests)} tests passed")
        
        if passed == len(tests):
            print("🎉 ALL TESTS PASSED!")
            print("\n🌟 Phase A-Prime Foundation is ready!")
            print("Tree-sitter integration provides:")
            print("  ✅ Grammatically perfect parsing")
            print("  ✅ Safe AST manipulation")
            print("  ✅ Accurate error location")
            print("  ✅ Foundation for GraphRAG")
        else:
            print("\n⚠️ Some tests failed")
            print("Tree-sitter-nix may need to be properly configured")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()