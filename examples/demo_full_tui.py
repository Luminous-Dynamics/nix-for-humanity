#!/usr/bin/env python3
"""
🌟 Full TUI Demo - Experience the Complete Consciousness-First Interface

This demo showcases the full Nix for Humanity TUI with:
- Living consciousness orb
- Adaptive interface complexity
- Natural conversation flow
- Beautiful animations
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the full TUI demo"""
    print("\n" + "="*60)
    print("🌟 Nix for Humanity - Full TUI Demo")
    print("="*60)
    print("\nThis demo showcases our consciousness-first terminal interface:")
    print("• 🔮 Living consciousness orb that breathes with AI state")
    print("• 🎨 Adaptive complexity based on your flow state")
    print("• 💬 Natural conversation with your AI partner")
    print("• ✨ Beautiful animations at 60fps")
    print("\nSpecial commands to try:")
    print("• 'help' - See what I can do")
    print("• 'install firefox' - Natural package management")
    print("• 'flow' - Enter flow state (Easter egg!)")
    print("• Ctrl+Z - Toggle Zen mode")
    print("• Ctrl+C - Exit gracefully")
    print("\n" + "="*60)
    
    input("\nPress Enter to launch the TUI...")
    
    try:
        # Import and run the TUI
        from nix_humanity.ui.main_app import NixForHumanityTUI
        
        # Create a mock engine for demo
        class MockEngine:
            """Simple mock engine for demo"""
            def get_current_state(self):
                return None
                
        engine = MockEngine()
        app = NixForHumanityTUI(engine=engine)
        app.run()
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nPlease ensure you have Textual installed:")
        print("  pip install textual rich")
        print("\nOr use the Nix development environment:")
        print("  nix develop")
        return 1
        
    except KeyboardInterrupt:
        print("\n\n✨ Thank you for experiencing consciousness-first computing!")
        print("🌊 We flow with gratitude.\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())