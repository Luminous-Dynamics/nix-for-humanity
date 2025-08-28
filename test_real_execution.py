#!/usr/bin/env python3
"""
Test if we can actually execute real NixOS commands
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.executor import SafeExecutor

def test_real_commands():
    """Test executing real NixOS commands"""
    
    print("🧪 Testing Real NixOS Command Execution")
    print("=" * 50)
    
    executor = SafeExecutor()
    executor.mindful_mode = False  # Skip pauses for testing
    
    # Test 1: List installed packages (safe, read-only)
    print("\n1. Testing: nix-env -q (list installed packages)")
    result = executor.execute("nix-env", ["-q"])
    
    if result.get("success"):
        output = result.get("output", "").strip()
        if output:
            print(f"✅ SUCCESS! Found {len(output.splitlines())} installed packages")
            print(f"   First few: {output.splitlines()[:3]}")
        else:
            print("⚠️  Command succeeded but no packages listed (might be empty profile)")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    
    # Test 2: Search for a package
    print("\n2. Testing: nix search nixpkgs firefox")
    result = executor.execute("nix", ["search", "nixpkgs", "firefox", "--json"])
    
    if result.get("success"):
        output = result.get("output", "").strip()
        if "firefox" in output.lower() or output.startswith("{"):
            print("✅ SUCCESS! Search returned results")
            print(f"   Output length: {len(output)} chars")
        else:
            print(f"⚠️  Unexpected output: {output[:100]}")
    else:
        error = result.get("error", "")
        if "experimental" in error.lower():
            print("⚠️  Need to enable experimental features for 'nix search'")
            print("   Try: nix --extra-experimental-features 'nix-command flakes' search")
        else:
            print(f"❌ FAILED: {error}")
    
    # Test 3: Check nix-env version (should always work)
    print("\n3. Testing: nix-env --version")
    result = executor.execute("nix-env", ["--version"])
    
    if result.get("success"):
        output = result.get("output", "").strip()
        print(f"✅ SUCCESS! nix-env version: {output}")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        print("   This is critical - nix-env should always be available on NixOS!")
    
    # Test 4: Try with experimental features
    print("\n4. Testing: nix with experimental features")
    result = executor.execute(
        "nix", 
        ["--extra-experimental-features", "nix-command flakes", "search", "nixpkgs", "vim", "--json"]
    )
    
    if result.get("success"):
        print("✅ SUCCESS! Experimental nix command works")
    else:
        print(f"⚠️  Experimental features might not be available: {result.get('error', '')[:100]}")
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print("If you see ✅ for test 3, basic execution IS working!")
    print("If all tests pass, we have real NixOS integration! 🎉")
    
if __name__ == "__main__":
    test_real_commands()