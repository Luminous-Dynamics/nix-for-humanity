#!/usr/bin/env python3
"""
Demo: Configuration.nix Generation Feature
Shows how natural language is translated into NixOS configurations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nix_humanity.core.config_generator import NixConfigGenerator

def demo_config_generation():
    generator = NixConfigGenerator()
    
    print("🔧 Nix for Humanity - Configuration Generation Demo\n")
    print("=" * 70)
    
    examples = [
        {
            "input": "web server with nginx and postgresql",
            "description": "Professional web server setup"
        },
        {
            "input": "desktop with KDE plasma and firefox",
            "description": "KDE desktop environment"
        },
        {
            "input": "development machine with docker vscode git",
            "description": "Developer workstation"
        },
        {
            "input": "minimal server with ssh firewall hostname myserver",
            "description": "Secure minimal server"
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['description']}")
        print(f"Input: \"{example['input']}\"")
        print("-" * 70)
        
        # Parse the natural language
        intent = generator.parse_intent(example['input'])
        
        print(f"\n🔍 Detected Components:")
        if intent['modules']:
            print(f"   Modules: {', '.join(intent['modules'])}")
        if intent['packages']:
            print(f"   Packages: {', '.join(intent['packages'])}")
        if intent['users']:
            print(f"   Users: {', '.join([u['name'] for u in intent['users']])}")
        if intent['settings']:
            print(f"   Settings: {intent['settings']}")
        
        # Check for conflicts
        conflicts = generator.check_conflicts(intent['modules'])
        if conflicts:
            print(f"\n⚠️  Conflicts detected:")
            for m1, m2 in conflicts:
                print(f"   - {m1} conflicts with {m2}")
            continue
        
        # Generate the configuration
        config = generator.generate_config(intent)
        
        print(f"\n📄 Generated Configuration:")
        print("```nix")
        # Show first 30 lines or full config if shorter
        lines = config.split('\n')
        preview_lines = lines[:30] if len(lines) > 30 else lines
        print('\n'.join(preview_lines))
        if len(lines) > 30:
            print(f"\n... ({len(lines) - 30} more lines)")
        print("```")
        
    print("\n" + "=" * 70)
    print("\n✨ Configuration generation demo complete!")
    print("\nTo use in the CLI:")
    print('  ask-nix "generate config for web server with nginx"')
    print('  ask-nix config generate "desktop with kde"')
    print('  ask-nix config wizard  # Interactive configuration builder')

if __name__ == "__main__":
    demo_config_generation()