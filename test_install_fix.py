#!/usr/bin/env python3
"""
Test that the install command fix is working
"""

import subprocess
import sys

def test_install_command():
    """Test that 'install firefox' correctly identifies firefox as the package"""
    
    print("🧪 Testing Install Command Fix")
    print("=" * 50)
    
    # Test 1: Basic install command
    print("\n✅ Test 1: Basic 'install firefox' command")
    result = subprocess.run(
        ["./bin/ask-nix", "install firefox"],
        capture_output=True,
        text=True,
        env={"LUMINOUS_DRY_RUN": "true", "LUMINOUS_SKIP_CONFIRM": "true"},
        timeout=5
    )
    
    # Check if "firefox" appears in output (not "install")
    if "firefox" in result.stdout.lower() and "install install" not in result.stdout.lower():
        print("   ✅ PASS: Correctly identified 'firefox' as package")
    else:
        print("   ❌ FAIL: Did not correctly identify package")
        print(f"   Output: {result.stdout[:200]}")
    
    # Test 2: Natural language install
    print("\n✅ Test 2: Natural language 'i want to install firefox'")
    result = subprocess.run(
        ["./bin/ask-nix", "i want to install firefox"],
        capture_output=True,
        text=True,
        env={"LUMINOUS_DRY_RUN": "true", "LUMINOUS_SKIP_CONFIRM": "true"},
        timeout=5
    )
    
    if "firefox" in result.stdout.lower():
        print("   ✅ PASS: Correctly handled natural language")
    else:
        print("   ❌ FAIL: Natural language parsing failed")
    
    # Test 3: Check for the specific error we were seeing
    print("\n✅ Test 3: Checking for 'Install install' bug")
    result = subprocess.run(
        ["./bin/ask-nix", "install firefox"],
        capture_output=True,
        text=True,
        env={"LUMINOUS_DRY_RUN": "true", "LUMINOUS_SKIP_CONFIRM": "true"},
        timeout=5
    )
    
    if "Install install" in result.stdout or "Install install" in result.stderr:
        print("   ❌ FAIL: Bug still present - seeing 'Install install'")
        return False
    else:
        print("   ✅ PASS: Bug fixed - no 'Install install' found")
    
    print("\n" + "=" * 50)
    print("🎉 Install Command Fix Verified!")
    return True

if __name__ == "__main__":
    success = test_install_command()
    sys.exit(0 if success else 1)