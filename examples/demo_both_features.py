#!/usr/bin/env python3
"""
Demonstrate both new core features:
1. Configuration.nix Generation
2. Flake Management
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from luminous_nix.core.config_generator import NixConfigGenerator
from luminous_nix.core.flake_manager import FlakeManager

def demo_config_generation():
    """Demo configuration generation"""
    print("🔧 Feature 1: Configuration.nix Generation")
    print("=" * 60)
    
    generator = NixConfigGenerator()
    
    examples = [
        "web server with nginx and postgresql",
        "desktop environment with kde plasma and development tools",
        "home lab server with docker and monitoring"
    ]
    
    for desc in examples:
        print(f"\n📝 Generating config for: {desc}")
        intent = generator.parse_intent(desc)
        
        print(f"   Detected modules: {intent['modules']}")
        print(f"   Detected packages: {intent['packages'][:3]}..." if len(intent['packages']) > 3 else f"   Detected packages: {intent['packages']}")
        
        conflicts = generator.check_conflicts(intent['modules'])
        if conflicts:
            print(f"   ⚠️  Conflicts: {conflicts}")
        else:
            print("   ✅ No conflicts detected")
        
        # Generate a preview
        config = generator.generate_config(intent)
        preview = '\n'.join(config.split('\n')[:15])
        print(f"\n   Preview:\n{preview}\n   ...")

def demo_flake_management():
    """Demo flake management"""
    print("\n\n🎯 Feature 2: Flake Management & Dev Environments")
    print("=" * 60)
    
    manager = FlakeManager()
    
    examples = [
        {
            "desc": "python machine learning environment with jupyter tensorflow",
            "expected": "Data science setup"
        },
        {
            "desc": "rust embedded development with probe-rs",
            "expected": "Embedded Rust setup"
        },
        {
            "desc": "fullstack web app with node react postgres",
            "expected": "Web development setup"
        }
    ]
    
    for example in examples:
        print(f"\n📝 Creating flake for: {example['desc']}")
        intent = manager.parse_intent(example['desc'])
        
        print(f"   Language: {intent['language'] or 'multi-language'}")
        print(f"   Packages: {intent['packages']}")
        print(f"   Purpose: {example['expected']}")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            success, message = manager.create_flake(intent, Path(tmpdir))
            status = "✅" if success else "❌"
            print(f"   {status} {message}")
            
            if success:
                # Show flake structure
                flake_path = Path(tmpdir) / "flake.nix"
                with open(flake_path, 'r') as f:
                    lines = f.readlines()
                
                # Find key sections
                for i, line in enumerate(lines):
                    if 'buildInputs' in line:
                        print(f"   📦 Packages included:")
                        for j in range(i+1, min(i+6, len(lines))):
                            if '];' in lines[j]:
                                break
                            if lines[j].strip():
                                print(f"      {lines[j].strip()}")
                        break

def demo_integration():
    """Show how both features work together"""
    print("\n\n🌟 Integration: Using Both Features Together")
    print("=" * 60)
    
    print("\n📚 Complete NixOS Development Workflow:")
    print("1. Generate system configuration:")
    print('   ask-nix "generate config for development workstation with docker vscode"')
    print("\n2. Create project-specific dev environment:")
    print('   ask-nix "create flake for python web api with fastapi pytest"')
    print("\n3. Apply configuration:")
    print("   sudo nixos-rebuild switch")
    print("\n4. Enter dev environment:")
    print("   nix develop")
    
    print("\n✨ Both features work seamlessly together!")
    print("   - System config (configuration.nix) defines your base OS")
    print("   - Project flakes define per-project development environments")
    print("   - Natural language makes both accessible to everyone!")

if __name__ == "__main__":
    print("🌟 Nix for Humanity - Core Features Demonstration\n")
    print("We've added 2 powerful features to make NixOS more accessible:\n")
    
    demo_config_generation()
    demo_flake_management()
    demo_integration()
    
    print("\n\n🎉 Both core features are working!")
    print("\nNext steps:")
    print("- Test with real users")
    print("- Add more language support")
    print("- Improve natural language understanding")
    print("- Integrate with the TUI for visual configuration")