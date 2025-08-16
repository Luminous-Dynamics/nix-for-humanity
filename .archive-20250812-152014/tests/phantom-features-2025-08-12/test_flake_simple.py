#!/usr/bin/env python3
"""
Simple test for flake generation without validation
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from luminous_nix.core.flake_manager import FlakeManager

def test_flake_generation():
    """Test generating flakes from natural language"""
    print("🎯 Testing Flake Generation (No Validation)")
    print("=" * 60)

    manager = FlakeManager()

    # Test Python flake
    print("\n📝 Test: Python development environment")
    intent = manager.parse_intent(
        "create a python development environment with pytest and black"
    )
    print(f"   Language: {intent['language']}")
    print(f"   Features: {intent['features']}")

    with tempfile.TemporaryDirectory() as tmpdir:
        success, message = manager.create_flake(intent, Path(tmpdir))
        print(f"   Result: {'✅' if success else '❌'} {message}")

        if success:
            flake_path = Path(tmpdir) / "flake.nix"
            with open(flake_path) as f:
                content = f.read()
            print(f"\n📄 Generated flake.nix ({len(content)} bytes):")
            print("   First 10 lines:")
            for i, line in enumerate(content.split("\n")[:10], 1):
                print(f"   {i:2} | {line}")

    # Test Rust flake
    print("\n\n📝 Test: Rust web server")
    intent = manager.parse_intent("rust web server with actix")
    print(f"   Language: {intent['language']}")

    with tempfile.TemporaryDirectory() as tmpdir:
        success, message = manager.create_flake(intent, Path(tmpdir))
        print(f"   Result: {'✅' if success else '❌'} {message}")

        if success:
            flake_path = Path(tmpdir) / "flake.nix"
            if flake_path.exists():
                print("   ✅ Flake file created successfully!")

if __name__ == "__main__":
    print("🌟 Nix for Humanity - Simple Flake Test\n")
    test_flake_generation()
    print("\n✨ Test complete!")
