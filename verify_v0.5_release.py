#!/usr/bin/env python3
"""
Quick verification script for v0.5.0 release
Tests core functionality of all Phase 2 features
"""

import subprocess
import json
import sys

def run_test(command, description):
    """Run a single test command"""
    try:
        result = subprocess.run(
            f"poetry run ask-nix {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        success = result.returncode == 0
        print(f"{'✅' if success else '❌'} {description}")
        if not success and result.stderr:
            print(f"   Error: {result.stderr[:100]}")
        return success
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} (timeout)")
        return False
    except Exception as e:
        print(f"❌ {description} (exception: {e})")
        return False

def main():
    """Run all verification tests"""
    print("🚀 Verifying Luminous Nix v0.5.0 Release")
    print("=" * 50)
    
    tests = [
        # Version check
        ("--version", "Version check"),
        
        # Flake Migration commands
        ("flake --help", "Flake help"),
        ("flake analyze --json", "Flake analyze"),
        ("flake validate . --json", "Flake validate"),
        ("flake improve .", "Flake improve suggestions"),
        
        # Dev Environment commands
        ("devenv --help", "DevEnv help"),
        ("devenv analyze .", "DevEnv analyze current dir"),
        ("devenv list-stacks", "DevEnv list stacks"),
        ("devenv create python-django --dry-run", "DevEnv create python-django"),
        
        # Performance commands
        ("performance --help", "Performance help"),
        ("performance profile --json", "Performance profile"),
        ("performance boot --json", "Performance boot optimization"),
        ("performance rebuild", "Performance rebuild optimization"),
        ("performance resources", "Performance resource analysis"),
    ]
    
    passed = 0
    failed = 0
    
    print("\n📋 Running Tests:")
    print("-" * 50)
    
    for command, description in tests:
        if run_test(command, description):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✅ All tests passed! Ready for v0.5.0 release!")
        return 0
    elif passed >= len(tests) * 0.8:
        print("⚠️ Most tests passed. Review failures before release.")
        return 1
    else:
        print("❌ Too many failures. Fix issues before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main())