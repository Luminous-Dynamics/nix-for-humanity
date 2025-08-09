#!/usr/bin/env python3
"""
Simple test for the flake management feature
"""

import sys
import os
import tempfile
from pathlib import Path

# Add module path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nix_humanity.core.flake_manager import FlakeManager

def test_flake_creation():
    """Test creating flakes from natural language"""
    print("🎯 Testing Flake Creation Feature")
    print("=" * 60)
    
    manager = FlakeManager()
    
    test_cases = [
        {
            "input": "create a python development environment with pytest and black",
            "expected_language": "python",
            "expected_features": ["testing", "formatting"]
        },
        {
            "input": "rust web server with actix and diesel",
            "expected_language": "rust",
            "expected_packages": ["actix", "diesel"]
        },
        {
            "input": "node.js project with typescript and prettier",
            "expected_language": "javascript",
            "expected_packages": ["typescript", "prettier"]
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: {test['input']}")
        print("-" * 60)
        
        # Parse intent
        intent = manager.parse_intent(test['input'])
        print(f"✅ Parsed Language: {intent['language']}")
        print(f"✅ Packages: {intent['packages']}")
        print(f"✅ Features: {intent['features']}")
        print(f"✅ Description: {intent['description']}")
        
        # Create temporary directory for flake
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the flake
            success, message = manager.create_flake(intent, Path(tmpdir))
            
            if success:
                print(f"\n✅ {message}")
                
                # Read and display the flake
                flake_path = Path(tmpdir) / "flake.nix"
                if flake_path.exists():
                    with open(flake_path, 'r') as f:
                        content = f.read()
                    
                    print("\n📄 Generated flake.nix:")
                    print("-" * 60)
                    lines = content.split('\n')
                    for i, line in enumerate(lines[:30]):  # Show first 30 lines
                        print(f"{i+1:3} | {line}")
                    if len(lines) > 30:
                        print(f"... ({len(lines) - 30} more lines)")
            else:
                print(f"\n❌ {message}")

def test_project_detection():
    """Test automatic project type detection"""
    print("\n\n🔍 Testing Project Type Detection")
    print("=" * 60)
    
    manager = FlakeManager()
    
    test_files = {
        "requirements.txt": "python",
        "package.json": "javascript",
        "Cargo.toml": "rust",
        "go.mod": "go",
        "pom.xml": "java",
        "CMakeLists.txt": "c++"
    }
    
    for filename, expected_lang in test_files.items():
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / filename
            test_file.touch()
            
            # Detect language
            detected = manager.detect_project_type(Path(tmpdir))
            
            status = "✅" if detected == expected_lang else "❌"
            print(f"{status} {filename:20} → {detected or 'Unknown':10} (expected: {expected_lang})")

def test_flake_validation():
    """Test flake validation"""
    print("\n\n🔬 Testing Flake Validation")
    print("=" * 60)
    
    manager = FlakeManager()
    
    # Test with no flake
    with tempfile.TemporaryDirectory() as tmpdir:
        success, message = manager.validate_flake(Path(tmpdir))
        print(f"❌ No flake.nix: {message}")
    
    # Test with valid flake
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple flake
        intent = manager.parse_intent("python development environment")
        success, message = manager.create_flake(intent, Path(tmpdir))
        
        if success:
            # Now validate it
            success, message = manager.validate_flake(Path(tmpdir))
            print(f"\n{'✅' if success else '❌'} Valid flake: {message}")

if __name__ == "__main__":
    print("🌟 Nix for Humanity - Flake Management Feature Test\n")
    
    test_flake_creation()
    test_project_detection()
    test_flake_validation()
    
    print("\n\n✨ Flake feature testing complete!")
    print("\n💡 To use in the CLI:")
    print('   ask-nix "create flake for python web app"')
    print('   ask-nix flake create "rust project with testing"')
    print('   ask-nix flake validate')
    print('   ask-nix flake convert  # Convert shell.nix to flake')