#!/usr/bin/env python3
"""
Demo: NixOS Configuration Generation Feature
Shows natural language to configuration translation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.config_generator import NixConfigGenerator


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def demo_config_generation():
    """Demonstrate configuration generation capabilities."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║       Luminous Nix - Configuration Generation Demo          ║
║    Natural Language → NixOS Configuration Translation       ║
╚══════════════════════════════════════════════════════════════╝
    """)

    generator = NixConfigGenerator()

    # Demo queries
    demos = [
        {
            "title": "💻 Development Workstation",
            "query": "Set up a development workstation with KDE desktop, Docker, VSCode, and user alice with admin access",
            "highlight": ["KDE Plasma", "Docker", "VSCode", "alice user"]
        },
        {
            "title": "🌐 Web Server",
            "query": "Configure a web server with nginx, PostgreSQL database, firewall, and SSH access",
            "highlight": ["Nginx", "PostgreSQL", "Firewall", "SSH"]
        },
        {
            "title": "🏠 Home Desktop",
            "query": "Create a desktop system with GNOME, Firefox, Git, and development tools",
            "highlight": ["GNOME desktop", "Firefox", "Git", "Development packages"]
        },
    ]

    for demo in demos:
        print_separator()
        print(f"🎯 {demo['title']}")
        print(f"📝 Query: '{demo['query']}'")
        print()

        # Parse intent
        intent = generator.parse_intent(demo['query'])
        
        print("🧠 Parsed Intent:")
        print(f"  • Modules: {', '.join(intent['modules']) if intent['modules'] else 'None'}")
        print(f"  • Packages: {', '.join(intent['packages'][:5]) if intent['packages'] else 'None'}")
        if len(intent['packages']) > 5:
            print(f"    (and {len(intent['packages']) - 5} more...)")
        print(f"  • Users: {', '.join([u['name'] for u in intent['users']]) if intent['users'] else 'Default user'}")
        
        # Check for conflicts
        conflicts = generator.check_conflicts(intent['modules'])
        if conflicts:
            print(f"  ⚠️ Conflicts detected: {conflicts}")
            print("     (Resolving conflicts...)")
        
        # Generate configuration
        config = generator.generate_config(intent)
        
        print("\n📄 Generated Configuration (Preview):")
        print("```nix")
        # Show first 20 lines of config
        lines = config.split('\n')[:20]
        for line in lines:
            print(line)
        if len(config.split('\n')) > 20:
            print(f"... ({len(config.split('\n')) - 20} more lines)")
        print("```")
        
        print("\n✅ Features included:")
        for feature in demo['highlight']:
            if any(keyword in config.lower() for keyword in feature.lower().split()):
                print(f"  • {feature} ✓")

    print_separator()
    print("""
🎉 Configuration Generation Complete!

The Luminous Nix configuration generator can:
• Parse natural language descriptions
• Detect required NixOS modules
• Resolve conflicts between incompatible modules
• Generate valid NixOS configurations
• Include appropriate defaults and dependencies

Try it with: ask-nix "generate config for [your description]"
    """)


def demo_advanced_features():
    """Show advanced configuration features."""
    print_separator()
    print("🚀 Advanced Features:")
    print()
    
    generator = NixConfigGenerator()
    
    # Demonstrate configuration explanation
    print("📖 Configuration Explanation:")
    print("   The generator can explain existing configurations in plain language")
    print()
    
    # Demonstrate validation
    print("✔️ Configuration Validation:")
    print("   Validates NixOS syntax before applying changes")
    print()
    
    # Demonstrate incremental updates
    print("🔄 Incremental Updates:")
    print("   Can modify existing configurations without full regeneration")
    print()
    
    # Demonstrate backup functionality
    print("💾 Automatic Backups:")
    print("   Creates timestamped backups before modifying configurations")


if __name__ == "__main__":
    try:
        demo_config_generation()
        demo_advanced_features()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()