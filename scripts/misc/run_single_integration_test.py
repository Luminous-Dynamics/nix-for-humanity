#!/usr/bin/env python3
"""
Run a single integration test to verify the system
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import what we need
from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.api.schema import Request, Context

def test_help_command():
    """Test that help command works"""
    print("Testing help command...")
    
    backend = NixForHumanityBackend()
    request = Request(
        query="help",
        context=Context(personality="friendly")
    )
    
    try:
        response = backend.process(request)
        
        # Check response
        assert response.success, f"Response failed: {response.error}"
        assert "install" in response.text.lower(), "Help should mention install"
        assert "update" in response.text.lower(), "Help should mention update" 
        assert "search" in response.text.lower(), "Help should mention search"
        
        print("✅ Help command test PASSED")
        print(f"Response text preview: {response.text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Help command test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_command():
    """Test that search command works"""
    print("\nTesting search command...")
    
    backend = NixForHumanityBackend()
    request = Request(
        query="search firefox",
        context=Context(personality="minimal", execute=False)
    )
    
    try:
        response = backend.process(request)
        
        # Check response
        assert response.success, f"Response failed: {response.error}"
        assert "firefox" in response.text.lower(), "Search should mention firefox"
        
        print("✅ Search command test PASSED")
        print(f"Response text preview: {response.text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Search command test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_install_dry_run():
    """Test install command in dry-run mode"""
    print("\nTesting install command (dry-run)...")
    
    backend = NixForHumanityBackend()
    request = Request(
        query="install hello",
        context=Context(
            personality="minimal",
            execute=False,
            dry_run=True
        )
    )
    
    try:
        response = backend.process(request)
        
        # Check response
        assert response.success, f"Response failed: {response.error}"
        assert "hello" in response.text.lower(), "Install should mention package name"
        
        print("✅ Install command test PASSED")
        print(f"Response text preview: {response.text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Install command test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running Nix for Humanity Integration Tests")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 3
    
    # Run tests
    if test_help_command():
        tests_passed += 1
        
    if test_search_command():
        tests_passed += 1
        
    if test_install_dry_run():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Summary: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print(f"❌ {tests_total - tests_passed} tests failed")
        sys.exit(1)