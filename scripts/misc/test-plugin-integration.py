#!/usr/bin/env python3
"""
Test script to verify plugin integration with ask-nix command
"""

import subprocess
import sys
import os

def test_help_shows_plugins():
    """Test that --help shows plugin information"""
    print("🧪 Testing: ask-nix --help should show plugin information")
    
    result = subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), 'bin', 'ask-nix'),
        '--help'
    ], capture_output=True, text=True)
    
    output = result.stdout + result.stderr
    
    # Check for plugin system mention
    if "Plugin System:" in output or "Plugin Options:" in output:
        print("✅ Plugin information found in help text")
        if "Total plugins loaded:" in output:
            print("✅ Plugin count displayed")
        return True
    else:
        print("❌ No plugin information in help text")
        print("Output:", output[:500])
        return False

def test_plugin_personality():
    """Test that plugin personalities work"""
    print("\n🧪 Testing: Plugin-based personality transformation")
    
    # Test minimal personality
    result = subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), 'bin', 'ask-nix'),
        '--minimal',
        'what is nix?'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Minimal personality command executed")
        return True
    else:
        print("❌ Minimal personality command failed")
        print("Error:", result.stderr[:200])
        return False

def test_plugin_feature():
    """Test that plugin features can handle intents"""
    print("\n🧪 Testing: Plugin feature handling")
    
    # This will test if plugins can intercept and handle intents
    result = subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), 'bin', 'ask-nix'),
        '--show-intent',
        'install firefox'
    ], capture_output=True, text=True)
    
    output = result.stdout + result.stderr
    
    if "Intent detected:" in output:
        print("✅ Intent detection working")
        if "install_package" in output:
            print("✅ Correct intent identified")
        return True
    else:
        print("❌ Intent detection not working")
        return False

def main():
    """Run all tests"""
    print("🔌 Plugin Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_help_shows_plugins,
        test_plugin_personality,
        test_plugin_feature
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Plugin integration is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())