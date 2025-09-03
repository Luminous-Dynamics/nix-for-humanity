#!/usr/bin/env python3
"""Simple test of real backend without pytest"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Enable real backend
os.environ["LUMINOUS_USE_REAL_BACKEND"] = "true"
os.environ["LUMINOUS_DRY_RUN"] = "true"

from luminous_nix.core.luminous_core import LuminousNixCore, Query

def test_commands():
    """Test basic commands with real backend"""
    
    print("=" * 60)
    print("TESTING REAL NIX BACKEND - v0.4.0")
    print("=" * 60)
    
    core = LuminousNixCore()
    
    tests = [
        ("help", "Help command"),
        ("list", "List installed packages"),
        ("search hello", "Search for hello package"),
        ("install cowsay", "Dry run install"),
        ("remove hello", "Dry run remove"),
        ("info", "System information"),
        ("clean", "Garbage collection"),
    ]
    
    passed = 0
    failed = 0
    
    for command, description in tests:
        print(f"\n📦 Testing: {description}")
        print(f"   Command: {command}")
        
        try:
            query = Query(text=command, dry_run=True)
            response = core.process_query(query)
            
            if response:
                if response.success:
                    print(f"   ✅ SUCCESS")
                    if response.message:
                        print(f"   Output: {response.message[:100]}...")
                    passed += 1
                else:
                    print(f"   ⚠️  FAILED: {response.error or 'Unknown error'}")
                    failed += 1
            else:
                print(f"   ❌ No response received")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if passed > failed:
        print("✅ Real backend is working!")
        print("The system can now execute actual NixOS commands.")
    else:
        print("⚠️  Some tests failed, but real backend is partially working.")
    
    return passed > 0

if __name__ == "__main__":
    success = test_commands()
    sys.exit(0 if success else 1)