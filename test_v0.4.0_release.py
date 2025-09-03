#!/usr/bin/env python3
"""Test script for v0.4.0 release artifacts"""

import sys
import subprocess
import tempfile
import os

def test_wheel():
    """Test the Python wheel"""
    print("🧪 Testing v0.4.0 wheel...")
    
    # Test import
    try:
        from luminous_nix import __version__
        from luminous_nix.cli import main
        from luminous_nix.core import LuminousNixCore
        from luminous_nix.core.config_generator import NixConfigGenerator
        from luminous_nix.core.flake_manager import FlakeManager
        
        print(f"✅ Import successful - Version: {__version__}")
        
        # Test core functionality
        core = LuminousNixCore()
        print("✅ Core initialized")
        
        # Test config generator
        generator = NixConfigGenerator()
        intent = generator.parse_intent("web server with nginx")
        print(f"✅ Config generator working - Parsed: {intent.get('modules', [])[:2]}")
        
        # Test flake manager  
        manager = FlakeManager()
        flake_intent = manager.parse_intent("python web app")
        print(f"✅ Flake manager working - Language: {flake_intent.get('language')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cli():
    """Test the CLI"""
    print("\n🧪 Testing CLI...")
    
    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, "-m", "luminous_nix.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "Luminous Nix" in result.stdout:
            print("✅ CLI help command works")
            return True
        else:
            print(f"❌ CLI failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI error: {e}")
        return False

def main():
    print("=" * 60)
    print("📦 Luminous Nix v0.4.0 Release Test")
    print("=" * 60)
    
    results = []
    
    # Test wheel
    results.append(test_wheel())
    
    # Test CLI
    results.append(test_cli())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 All tests passed! v0.4.0 is ready for release!")
    else:
        print("⚠️ Some tests failed. Please review.")
    print("=" * 60)

if __name__ == "__main__":
    main()