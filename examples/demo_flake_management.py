#!/usr/bin/env python3
"""
Demo: Flakes & Development Environment Management
Shows how natural language is translated into development environments
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nix_humanity.core.flake_manager import FlakeManager
from pathlib import Path
import tempfile

def demo_flake_creation():
    manager = FlakeManager()
    
    print("🎯 Nix for Humanity - Flake Management Demo\n")
    print("=" * 70)
    
    examples = [
        {
            "input": "python development environment with pytest and black",
            "description": "Python project with testing and formatting"
        },
        {
            "input": "rust web server with actix and diesel",
            "description": "Rust backend with web framework and ORM"
        },
        {
            "input": "node.js project with typescript and prettier",
            "description": "Modern JavaScript/TypeScript development"
        },
        {
            "input": "data science environment with jupyter pandas numpy",
            "description": "Data science and machine learning setup"
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['description']}")
        print(f"Input: \"{example['input']}\"")
        print("-" * 70)
        
        # Parse the natural language
        intent = manager.parse_intent(example['input'])
        
        print(f"\n🔍 Detected Components:")
        if intent['language']:
            print(f"   Language: {intent['language'].capitalize()}")
        if intent['packages']:
            print(f"   Packages: {', '.join(intent['packages'])}")
        if intent['features']:
            print(f"   Features: {', '.join(intent['features'])}")
        
        # Create a temporary directory for demo
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the flake
            success, message = manager.create_flake(intent, Path(tmpdir))
            
            if success:
                print(f"\n✅ {message}")
                
                # Read and display the generated flake
                flake_path = Path(tmpdir) / "flake.nix"
                if flake_path.exists():
                    with open(flake_path, 'r') as f:
                        content = f.read()
                    
                    print(f"\n📄 Generated flake.nix:")
                    print("```nix")
                    # Show first 25 lines or full content if shorter
                    lines = content.split('\n')
                    preview_lines = lines[:25] if len(lines) > 25 else lines
                    print('\n'.join(preview_lines))
                    if len(lines) > 25:
                        print(f"\n... ({len(lines) - 25} more lines)")
                    print("```")
            else:
                print(f"\n❌ {message}")
    
    print("\n" + "=" * 70)
    print("\n✨ Flake management demo complete!")
    print("\nTo use in the CLI:")
    print('  ask-nix "create flake for python web app"')
    print('  ask-nix flake create "rust project with testing"')
    print('  ask-nix flake convert  # Convert existing shell.nix')
    print('  ask-nix flake templates  # Show available templates')

def demo_project_detection():
    """Demo automatic project type detection"""
    print("\n\n🔍 Project Detection Demo")
    print("=" * 70)
    
    manager = FlakeManager()
    
    test_files = [
        ("requirements.txt", "Python"),
        ("package.json", "JavaScript/Node.js"),
        ("Cargo.toml", "Rust"),
        ("go.mod", "Go"),
        ("pom.xml", "Java"),
        ("CMakeLists.txt", "C++")
    ]
    
    print("\nAutomatic project detection based on files:")
    
    for filename, expected in test_files:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / filename
            test_file.touch()
            
            # Detect project type
            detected = manager.detect_project_type(Path(tmpdir))
            
            print(f"\n   {filename:20} → Detected: {detected or 'Unknown'}")
            if detected:
                print(f"   {'':20}   Expected: {expected} ✅")

if __name__ == "__main__":
    demo_flake_creation()
    demo_project_detection()