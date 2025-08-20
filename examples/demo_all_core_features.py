#!/usr/bin/env python3
"""
Demonstrate all 3 implemented core features:
1. Configuration.nix Generation
2. Flake Management
3. Generation Management & System Recovery
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from luminous_nix.core.config_generator import NixConfigGenerator
from luminous_nix.core.flake_manager import FlakeManager
from luminous_nix.core.generation_manager import GenerationManager, list_system_generations, check_system_recovery_status

def demo_config_generation():
    """Demo configuration generation"""
    print("🔧 Feature 1: Configuration.nix Generation")
    print("=" * 60)
    
    generator = NixConfigGenerator()
    
    description = "development workstation with docker, vscode, and python"
    print(f"\n📝 Generating config for: {description}")
    
    intent = generator.parse_intent(description)
    print(f"   Detected modules: {intent['modules']}")
    print(f"   Detected packages: {intent['packages']}")
    
    # Generate config
    config = generator.generate_config(intent)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.nix', delete=False) as f:
        f.write(config)
        temp_path = f.name
    
    print(f"   ✅ Configuration saved to: {temp_path}")
    print(f"\n   Preview (first 15 lines):")
    print("   " + "-" * 50)
    for i, line in enumerate(config.split('\n')[:15]):
        print(f"   {line}")
    print("   ...")

def demo_flake_management():
    """Demo flake management"""
    print("\n\n🎯 Feature 2: Flake Management & Dev Environments")
    print("=" * 60)
    
    manager = FlakeManager()
    
    description = "python web api with fastapi pytest redis"
    print(f"\n📝 Creating flake for: {description}")
    
    intent = manager.parse_intent(description)
    print(f"   Language: {intent['language']}")
    print(f"   Packages: {intent['packages']}")
    print(f"   Features: {intent['features']}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        success, message = manager.create_flake(intent, Path(tmpdir))
        if success:
            print(f"   ✅ {message}")
            
            # Show commands
            print(f"\n   Commands to use this flake:")
            print(f"   cd {tmpdir}")
            print(f"   nix develop        # Enter dev shell")
            print(f"   nix flake check    # Validate flake")
        else:
            print(f"   ❌ {message}")

def demo_generation_management():
    """Demo generation management"""
    print("\n\n🔄 Feature 3: Generation Management & System Recovery")
    print("=" * 60)
    
    # List generations
    print("\n📋 System Generations:")
    print(list_system_generations(5))
    
    # Check health
    print("\n🏥 System Health Check:")
    print(check_system_recovery_status())
    
    # Show available commands
    print("\n🛠️ Available Generation Commands:")
    commands = [
        "ask-nix generation list                     # List all generations",
        "ask-nix generation rollback                 # Rollback to previous",
        "ask-nix generation rollback 42              # Rollback to specific",
        "ask-nix generation diff 42 43               # Compare generations",
        "ask-nix generation clean --keep 5           # Delete old generations",
        "ask-nix generation health                   # Check system health",
        "ask-nix generation snapshot 'Before update' # Create recovery point",
    ]
    
    for cmd in commands:
        print(f"   {cmd}")

def demo_natural_language_examples():
    """Show natural language examples for all features"""
    print("\n\n💬 Natural Language Examples")
    print("=" * 60)
    
    examples = {
        "Configuration Generation": [
            '"generate config for gaming desktop with steam and discord"',
            '"create configuration for web server with nginx and postgresql"',
            '"make me a home lab server config with docker and monitoring"',
        ],
        "Flake Management": [
            '"create flake for rust embedded development"',
            '"make python machine learning environment with jupyter"',
            '"convert my shell.nix to a flake"',
        ],
        "Generation Management": [
            '"rollback to previous generation"',
            '"show me the last 10 generations"',
            '"check system health"',
            '"create snapshot before major update"',
            '"clean old generations keep 5"',
        ]
    }
    
    for category, commands in examples.items():
        print(f"\n{category}:")
        for cmd in commands:
            print(f"   ask-nix {cmd}")

def main():
    print("🌟 Nix for Humanity - Core Features Demonstration")
    print("Making NixOS accessible through natural conversation\n")
    
    # Demo all features
    demo_config_generation()
    demo_flake_management()
    demo_generation_management()
    demo_natural_language_examples()
    
    print("\n\n🎉 All 3 Core Features Demonstrated!")
    print("\nThese features work together to provide:")
    print("• Easy system configuration through natural language")
    print("• Modern development environments with flakes")
    print("• Safe system management with recovery options")
    print("\n✨ Making NixOS accessible to everyone!")

if __name__ == "__main__":
    main()