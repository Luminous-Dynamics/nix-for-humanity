#!/usr/bin/env python3
"""
Demonstrate Home Manager Integration feature

This shows how natural language can configure personal dotfiles and themes.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nix_humanity.core.home_manager import HomeManager

def demo_home_manager():
    """Demo the Home Manager integration"""
    print("🏠 Feature 5: Home Manager Integration")
    print("=" * 60)
    print("\nManaging personal configurations with natural language.\n")
    
    manager = HomeManager()
    
    # Example 1: Natural language setup
    print("1. Natural Language Setup:")
    print("-" * 40)
    
    test_cases = [
        "set up my dotfiles for vim and tmux with dracula theme",
        "configure zsh with dark theme",
        "manage my git configuration",
        "setup a rust development environment with vim"
    ]
    
    for description in test_cases:
        print(f"\n💬 User: \"{description}\"")
        config = manager.init_home_config(description)
        
        print(f"\n✨ Generated Configuration:")
        print(f"   Dotfiles: {', '.join(d.name for d in config.dotfiles) if config.dotfiles else 'none'}")
        print(f"   Theme: {config.themes[0].name if config.themes else 'default'}")
        print(f"   Shell: {config.shell_config.get('shell', 'bash')}")
    
    # Example 2: Theme management
    print("\n\n2. Theme Management:")
    print("-" * 40)
    
    themes = ["dracula", "nord", "solarized-dark", "gruvbox"]
    
    for theme in themes:
        result = manager.apply_theme(theme, ["terminal"])
        print(f"\n🎨 {theme.title()} Theme:")
        print(f"   Type: {manager.themes[theme]['type']}")
        print(f"   Background: {manager.themes[theme]['colors']['background']}")
        print(f"   Foreground: {manager.themes[theme]['colors']['foreground']}")
    
    # Example 3: Generated home.nix
    print("\n\n3. Generated home.nix Configuration:")
    print("-" * 40)
    
    config = manager.init_home_config("vim and tmux with fish shell")
    home_nix = manager.generate_home_nix(config)
    
    print("\n📄 home.nix (first 30 lines):")
    lines = home_nix.split("\n")[:30]
    for line in lines:
        print(f"   {line}")
    print("   ...")
    
    # Example 4: Current status
    print("\n\n4. Current Status:")
    print("-" * 40)
    
    managed = manager.list_managed_configs()
    print(f"\n📊 Managed Configurations:")
    print(f"   Dotfiles found: {len(managed['dotfiles'])}")
    print(f"   Available themes: {', '.join(managed['themes'])}")
    print(f"   Backup locations: {len(managed['backups'])}")

def demo_natural_language_examples():
    """Show natural language examples"""
    print("\n\n💬 Natural Language Examples")
    print("=" * 60)
    
    examples = [
        ("Basic Setup", [
            "setup my home configuration",
            "configure my dotfiles",
            "manage my personal settings"
        ]),
        ("Specific Tools", [
            "setup vim with plugins",
            "configure tmux for development",
            "manage my git settings",
            "setup neovim with lua config"
        ]),
        ("Themes", [
            "apply dracula theme",
            "use nord color scheme",
            "set dark theme for terminal",
            "change to gruvbox theme"
        ]),
        ("Shell Configuration", [
            "configure zsh with oh-my-zsh",
            "setup fish shell",
            "manage bash aliases",
            "configure my shell prompt"
        ]),
        ("Development Environments", [
            "setup python development with vim",
            "configure rust environment",
            "manage nodejs dotfiles",
            "setup full stack development"
        ])
    ]
    
    for category, commands in examples:
        print(f"\n{category}:")
        for cmd in commands:
            print(f'  ask-nix "{cmd}"')

def main():
    print("🌟 Nix for Humanity - Home Manager Integration")
    print("Personal configuration management through conversation\n")
    
    demo_home_manager()
    demo_natural_language_examples()
    
    print("\n\n🎉 Home Manager Integration Complete!")
    print("\nBenefits:")
    print("✅ Natural language configuration")
    print("✅ Automatic dotfile management")
    print("✅ Theme consistency across apps")
    print("✅ Easy configuration sharing")
    print("✅ Backup before changes")
    print("\n✨ Your personal environment, declaratively managed!")

if __name__ == "__main__":
    main()