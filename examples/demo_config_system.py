#!/usr/bin/env python3
"""
Demo script for the comprehensive configuration system in Nix for Humanity
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from luminous_nix.utils.config import (
    ConfigManager, get_config, get_config_manager,
    ConfigSchema, Personality, ResponseFormat
)

def main():
    """Demonstrate the configuration system"""
    
    print("🎯 Nix for Humanity Configuration System Demo\n")
    
    # Get the configuration manager
    manager = get_config_manager()
    
    # Show current configuration
    print("📋 Current Configuration:")
    print(f"  • Personality: {manager.config.ui.default_personality.value}")
    print(f"  • Fast mode: {manager.config.performance.fast_mode}")
    print(f"  • Learning enabled: {manager.config.learning.enabled}")
    print(f"  • Voice enabled: {manager.config.voice.enabled}")
    print(f"  • Profile: {manager.config.profile_name or 'default'}")
    
    # Demonstrate getting values
    print("\n🔍 Getting Configuration Values:")
    print(f"  • ui.use_colors = {manager.get('ui.use_colors')}")
    print(f"  • performance.timeout = {manager.get('performance.timeout')}")
    print(f"  • privacy.local_only = {manager.get('privacy.local_only')}")
    
    # Demonstrate setting values
    print("\n✏️  Setting Configuration Values:")
    old_timeout = manager.get('performance.timeout')
    manager.set('performance.timeout', 45)
    print(f"  • Changed timeout from {old_timeout} to {manager.get('performance.timeout')}")
    
    # Show available profiles
    print("\n👥 Available Profiles:")
    profiles = manager.list_profiles()
    for profile in profiles[:5]:  # Show first 5
        print(f"  • {profile}")
    if len(profiles) > 5:
        print(f"  • ... and {len(profiles) - 5} more")
    
    # Apply a profile
    print("\n🎭 Applying Profile 'maya' (fast, minimal):")
    manager.apply_profile('maya')
    print(f"  • Personality: {manager.config.ui.default_personality.value}")
    print(f"  • Fast mode: {manager.config.performance.fast_mode}")
    print(f"  • Response format: {manager.config.ui.response_format.value}")
    
    # Show aliases
    print("\n🔤 Command Aliases:")
    aliases = manager.get_aliases()
    for alias, command in list(aliases.items())[:3]:
        print(f"  • {alias} → {command}")
    
    # Show shortcuts
    print("\n⚡ Command Shortcuts:")
    shortcuts = manager.get_shortcuts()
    for name, commands in list(shortcuts.items())[:2]:
        print(f"  • {name}:")
        for cmd in commands:
            print(f"    → {cmd}")
    
    # Validate configuration
    print("\n✅ Validating Configuration:")
    errors = manager.validate()
    if errors:
        print("  ❌ Validation errors:")
        for error in errors:
            print(f"    • {error}")
    else:
        print("  ✅ Configuration is valid!")
    
    # Export configuration
    print("\n📤 Exporting Configuration:")
    yaml_export = manager.export('yaml')
    if yaml_export:
        lines = yaml_export.split('\n')[:10]  # Show first 10 lines
        for line in lines:
            print(f"  {line}")
        print("  ...")
    
    # Environment variable overrides
    print("\n🌍 Environment Variable Support:")
    print("  Set these to override configuration:")
    print("  • NIX_HUMANITY_PERSONALITY=minimal")
    print("  • NIX_HUMANITY_FAST_MODE=true")
    print("  • NIX_HUMANITY_VOICE_ENABLED=true")
    print("  • NIX_HUMANITY_DEBUG=true")
    
    # Configuration locations
    print("\n📁 Configuration File Locations:")
    print("  • User: ~/.config/nix-for-humanity/config.yaml")
    print("  • System: /etc/nix-for-humanity/config.yaml")
    print("  • Project: ./.nix-humanity/config.yaml")
    print("  • Example: config.example.yaml")
    
    print("\n✨ Configuration system is ready for use!")
    print("Run 'ask-nix-new settings --help' to manage your settings interactively.")


if __name__ == "__main__":
    main()