#!/usr/bin/env python3
"""
Test script for Python backend integration in ask-nix
Verifies that the unified backend and Python API calls are working correctly
"""

import os
import subprocess
import sys
from pathlib import Path

def test_backend_import():
    """Test if we can import the unified backend directly"""
    print("\n🔬 Testing direct backend import...")
    try:
        # Add paths
        script_dir = Path(__file__).parent / "scripts"
        backend_dir = script_dir / "backend"
        sys.path.insert(0, str(script_dir))
        sys.path.insert(0, str(backend_dir))
        
        from nix_humanity.core.engine import UnifiedNixBackend, IntentType
        print("✅ Successfully imported UnifiedNixBackend")
        
        # Test basic functionality
        backend = UnifiedNixBackend()
        intent = backend.extract_intent("install firefox")
        print(f"✅ Intent extraction works: {intent.type.value}")
        return True
    except Exception as e:
        print(f"❌ Failed to import nix_humanity.core as backend: {e}")
        return False

def test_command(command: str, description: str, use_feature_flag: bool = True):
    """Test a single ask-nix command"""
    print(f"\n{'='*60}")
    print(f"📋 Testing: {description}")
    print(f"💬 Command: ask-nix '{command}'")
    print(f"🚩 Feature flag: {'ENABLED' if use_feature_flag else 'DISABLED'}")
    print(f"{'='*60}")
    
    # Set or unset the feature flag
    env = os.environ.copy()
    if use_feature_flag:
        env['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
    else:
        env.pop('NIX_HUMANITY_PYTHON_BACKEND', None)
    
    # Use full path to ask-nix
    ask_nix_path = Path(__file__).parent / "bin" / "ask-nix"
    
    result = subprocess.run(
        [str(ask_nix_path), "--dry-run", command],
        capture_output=True,
        text=True,
        env=env
    )
    
    print("\n📤 Output:")
    print(result.stdout)
    
    if result.stderr:
        print("\n⚠️  Stderr:")
        print(result.stderr)
    
    # Check if Python backend was used
    if "🐍 Using Python backend" in result.stdout:
        print("\n✅ Python backend was used!")
        return True
    else:
        print("\n⚠️  Python backend was NOT used (using traditional method)")
        return False

def main():
    print("🧪 Testing Unified Python Backend Integration for ask-nix")
    print("=" * 60)
    
    # Check if we're on NixOS
    is_nixos = Path("/etc/nixos").exists()
    print(f"💻 System: {'NixOS' if is_nixos else 'Non-NixOS'}")
    
    # Check if unified backend exists
    backend_path = Path(__file__).parent / "scripts" / "backend" / "unified_nix_backend.py"
    print(f"🐍 Unified backend exists: {backend_path.exists()}")
    
    
    # First test direct import
    backend_works = test_backend_import()
    
    if not backend_works:
        print("\n⚠️  Cannot proceed with ask-nix tests - backend import failed")
        return
    
    # Test cases
    print("\n\n🧪 Testing ask-nix with feature flag...")
    tests = [
        ("install firefox", "Package installation"),
        ("update my system", "System update"),
        ("search python", "Package search"),
        ("list generations", "List generations"),
        ("rollback", "System rollback"),
    ]
    
    # Test WITH feature flag
    print("\n📌 Test Set 1: With Python Backend Feature Flag")
    results_with_flag = []
    for command, description in tests:
        success = test_command(command, description, use_feature_flag=True)
        results_with_flag.append((description, success))
    
    # Test WITHOUT feature flag (to ensure fallback works)
    print("\n\n📌 Test Set 2: Without Python Backend Feature Flag (fallback test)")
    test_command("install firefox", "Package installation (fallback)", use_feature_flag=False)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary:")
    print("="*60)
    
    print("\n✅ Backend import test: PASSED" if backend_works else "\n❌ Backend import test: FAILED")
    
    python_backend_used = sum(1 for _, success in results_with_flag if success)
    print(f"\n🎯 Python backend usage (with flag): {python_backend_used}/{len(tests)} tests")
    
    for description, success in results_with_flag:
        status = "✅ Python backend used" if success else "⚠️  Fell back to traditional"
        print(f"  • {description}: {status}")
    
    if python_backend_used == 0:
        print("\n❌ Python backend is not being used at all!")
        print("Possible reasons:")
        print("- Feature flag not being detected")
        print("- Import errors in the unified backend")
        print("- Missing dependencies (check if all modules in scripts/ are available)")
        print("\nDebug with: export DEBUG=1 NIX_HUMANITY_PYTHON_BACKEND=true")
    elif python_backend_used < len(tests):
        print("\n⚠️  Python backend is partially working")
        print("Some commands fall back to traditional methods")
    else:
        print("\n✅ Python backend is fully operational!")
        print("\n🎉 Next steps:")
        print("1. Enable in production: export NIX_HUMANITY_PYTHON_BACKEND=true")
        print("2. Test with real commands (without --dry-run)")
        print("3. Monitor performance improvements")
        print("4. Make default after user testing (remove feature flag check)")

if __name__ == "__main__":
    main()