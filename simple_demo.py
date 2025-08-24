#!/usr/bin/env python3
"""
Simple demo to show Luminous Nix works
This is what we'll show investors and on Hacker News
"""

import os
import sys

# Add src to path
sys.path.insert(0, 'src')

# Enable Python backend for performance
os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
os.environ['LUMINOUS_NIX_PYTHON_BACKEND'] = 'true'

def demo_luminous_nix():
    """Show the core functionality working"""
    
    print("🌟 Luminous Nix Demo - Natural Language for NixOS")
    print("=" * 50)
    
    try:
        from luminous_nix.core.engine import NixForHumanityCore
        from luminous_nix.core.types import Query
        print("✅ Core modules loaded")
    except ImportError as e:
        print(f"❌ Failed to import core modules: {e}")
        return False
    
    # Create the core engine
    try:
        core = NixForHumanityCore()
        print("✅ Engine initialized")
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        return False
    
    # Demo commands
    demo_commands = [
        "install firefox",
        "enable bluetooth",
        "create python development environment",
        "show system status",
        "rollback last change"
    ]
    
    print("\n📝 Demo Commands:")
    print("-" * 30)
    
    for cmd in demo_commands:
        print(f"\n🔹 Command: '{cmd}'")
        try:
            query = Query(raw_text=cmd, context={})
            response = core.process_query(query)
            
            # Show the response
            if response.success:
                print(f"   ✅ Understood as: {response.intent_type}")
                if response.explanation:
                    print(f"   📖 {response.explanation[:100]}...")
                if response.command:
                    print(f"   💻 Would execute: {response.command.executable[:50]}...")
            else:
                print(f"   ❌ Failed: {response.error}")
                
        except Exception as e:
            print(f"   ❌ Error processing: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Demo complete!")
    print("\nThis shows Luminous Nix can understand natural language")
    print("and convert it to NixOS commands. Ready for Hacker News!")
    
    return True

if __name__ == "__main__":
    success = demo_luminous_nix()
    sys.exit(0 if success else 1)