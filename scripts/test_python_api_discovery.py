#!/usr/bin/env python3
"""
Test Python API Discovery
=========================

Verify if we can find and import the nixos-rebuild Python module on NixOS 25.11.
"""

import os
import sys
import subprocess
from pathlib import Path
from glob import glob


def find_nixos_rebuild_module():
    """Try various methods to find the nixos-rebuild Python module"""
    
    print("🔍 Searching for nixos-rebuild Python module...")
    
    # Method 1: Check which nixos-rebuild
    try:
        result = subprocess.run(['which', 'nixos-rebuild'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            rebuild_path = Path(result.stdout.strip())
            print(f"✅ Found nixos-rebuild at: {rebuild_path}")
            
            # Resolve symlinks
            real_path = rebuild_path.resolve()
            print(f"📍 Resolved to: {real_path}")
            
            # Try to find Python modules in the same nix store path
            store_path = str(real_path.parent.parent)
            print(f"🏪 Nix store path: {store_path}")
            
            # Look for Python site-packages
            python_patterns = [
                f"{store_path}/lib/python*/site-packages",
                f"{store_path}/lib/python3.*/site-packages"
            ]
            
            for pattern in python_patterns:
                matches = glob(pattern)
                for match in matches:
                    print(f"🐍 Found Python path: {match}")
                    
                    # Check if nixos_rebuild module exists
                    module_path = Path(match) / "nixos_rebuild"
                    if module_path.exists():
                        print(f"✅ Found nixos_rebuild module at: {module_path}")
                        return str(match)
    except Exception as e:
        print(f"❌ Error with method 1: {e}")
    
    # Method 2: Search common locations
    print("\n🔍 Searching common locations...")
    search_patterns = [
        "/nix/store/*nixos-rebuild*/lib/python*/site-packages",
        "/run/current-system/sw/lib/python*/site-packages",
        "/nix/var/nix/profiles/system/sw/lib/python*/site-packages"
    ]
    
    for pattern in search_patterns:
        print(f"📂 Checking: {pattern}")
        matches = glob(pattern)
        for match in matches:
            module_path = Path(match) / "nixos_rebuild"
            if module_path.exists():
                print(f"✅ Found at: {match}")
                return match
    
    # Method 3: Check Python path
    print("\n🔍 Checking Python sys.path...")
    for path in sys.path:
        if "site-packages" in path:
            module_path = Path(path) / "nixos_rebuild"
            if module_path.exists():
                print(f"✅ Found in sys.path: {path}")
                return path
    
    return None


def test_import(module_path):
    """Test importing the module"""
    print(f"\n🧪 Testing import from: {module_path}")
    
    # Add to path
    sys.path.insert(0, module_path)
    
    try:
        # Try to import
        import nixos_rebuild
        print("✅ Successfully imported nixos_rebuild!")
        
        # Check what's available
        print("\n📦 Available modules:")
        for attr in dir(nixos_rebuild):
            if not attr.startswith('_'):
                print(f"  - {attr}")
        
        # Try to import submodules
        try:
            from nixos_rebuild import models, nix, services
            print("\n✅ Successfully imported submodules!")
            
            # Check Action enum
            if hasattr(models, 'Action'):
                print("\n🎯 Available actions:")
                for action in models.Action:
                    print(f"  - {action.name}: {action.value}")
                    
            return True
            
        except ImportError as e:
            print(f"⚠️  Could not import submodules: {e}")
            
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        
    return False


def check_nixos_version():
    """Check NixOS version"""
    print("🖥️  Checking NixOS version...")
    
    try:
        result = subprocess.run(['nixos-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📌 NixOS version: {result.stdout.strip()}")
    except Exception:
        print("⚠️  Could not determine NixOS version")


def main():
    print("🚀 NixOS Python API Discovery Test\n")
    
    # Check version
    check_nixos_version()
    print()
    
    # Find module
    module_path = find_nixos_rebuild_module()
    
    if module_path:
        print(f"\n✅ Found module path: {module_path}")
        
        # Test import
        if test_import(module_path):
            print("\n🎉 Python API is available and working!")
            
            # Generate code snippet
            print("\n📝 Code to use in your application:")
            print("```python")
            print(f"import sys")
            print(f"sys.path.insert(0, '{module_path}')")
            print(f"from nixos_rebuild import models, nix, services")
            print(f"from nixos_rebuild.models import Action")
            print("```")
        else:
            print("\n⚠️  Module found but import failed")
    else:
        print("\n❌ Could not find nixos-rebuild Python module")
        print("\nPossible reasons:")
        print("- Not running NixOS 25.11 or later")
        print("- nixos-rebuild-ng not in system path")
        print("- Python module not included in this version")


if __name__ == "__main__":
    main()