#!/usr/bin/env python3
"""
🌟 Nix for Humanity TUI Showcase
Interactive demonstration of the consciousness-first terminal interface
"""

import sys
import os
import time
from datetime import datetime

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("🌟 Nix for Humanity TUI Feature Showcase")
print("=" * 50)
print("\nThis demo will show you the key features of our consciousness-first interface:\n")

features = [
    ("🔮 Living Consciousness Orb", "A breathing, animated presence that responds to AI states"),
    ("🎨 Adaptive Complexity", "Interface that adjusts to your cognitive flow state"),
    ("⌨️ Natural Language Input", "Just type what you want in plain language"),
    ("🌊 Flow State Protection", "Respects your attention with gentle interactions"),
    ("✨ Beautiful Animations", "60fps smooth transitions and particle effects")
]

for i, (feature, description) in enumerate(features, 1):
    print(f"{i}. {feature}")
    print(f"   {description}")
    time.sleep(0.5)

print("\n" + "=" * 50)
print("\n🎮 Interactive Commands to Try:\n")

commands = [
    "install firefox       - Natural language package installation",
    "help                 - See what the system can do",
    "search editor        - Find packages by description",
    "Ctrl+Z              - Toggle Zen Mode (minimal UI)",
    "Ctrl+D              - Toggle Debug Info",
    "Ctrl+C              - Exit gracefully"
]

for cmd in commands:
    print(f"  • {cmd}")
    time.sleep(0.3)

print("\n" + "=" * 50)
print("\n🚀 Press Enter to launch the TUI showcase...")

try:
    input()
    
    # Create a simple mock if real backend isn't available
    print("\n🔮 Launching consciousness-first interface...\n")
    
    # Try to import and run
    try:
        from nix_humanity.ui.main_app import NixForHumanityTUI
        from nix_humanity.core.engine import NixForHumanityBackend
        
        # Create mock backend if needed
        class MockBackend:
            def __init__(self):
                self.state = "ready"
                
            async def process_query(self, query):
                # Simple mock responses
                if "install" in query.lower():
                    return {
                        "success": True,
                        "message": f"Installing {query.split()[-1]}...",
                        "command": f"nix-env -iA nixpkgs.{query.split()[-1]}"
                    }
                elif "help" in query.lower():
                    return {
                        "success": True,
                        "message": "I can help you install packages, search for software, and manage your NixOS system!"
                    }
                else:
                    return {
                        "success": True,
                        "message": f"Processing: {query}"
                    }
        
        # Try real backend first, fall back to mock
        try:
            backend = NixForHumanityBackend()
            print("✅ Using real backend")
        except Exception:
            backend = MockBackend()
            print("📝 Using mock backend for demo")
        
        # Create and run app
        app = NixForHumanityTUI(engine=backend)
        app.run()
        
    except ImportError as e:
        print(f"❌ Error importing TUI components: {e}")
        print("\nMake sure you have textual installed:")
        print("  pip install textual rich")
        
except KeyboardInterrupt:
    print("\n\n✨ Thank you for exploring consciousness-first computing!")
    print("🌊 We flow with gratitude.")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("📚 Learn more about the architecture:")
print("  • SYMBIOTIC_PARTNER_ARCHITECTURE.md")
print("  • EMBODIMENT_ROADMAP.md")
print("  • docs/PHILOSOPHY.md")
print("\n🌟 The future of human-AI partnership begins here! 🌟")