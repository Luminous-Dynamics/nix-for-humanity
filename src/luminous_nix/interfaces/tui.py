#!/usr/bin/env python3
"""
🌟 Terminal UI with Textual - Beautiful Consciousness-First Interface

Launch the Nix for Humanity TUI with living consciousness orb,
adaptive complexity, and beautiful animations.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the TUI application"""
    try:
        # Try direct import first
        from luminous_nix.ui.main_app import NixForHumanityTUI
        
        # Create and run the app with beautiful consciousness orb
        app = NixForHumanityTUI()
        app.run()
        
    except ImportError as e:
        print(f"✨ Setting up the consciousness-first TUI...")
        print(f"Error: Could not import TUI components: {e}")
        print("\nPlease ensure you're in the Nix development environment:")
        print("  nix develop")
        print("\nOr install dependencies manually:")
        print("  pip install textual rich")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✨ Thank you for using Nix for Humanity!")
        print("🌊 We flow with gratitude.")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching TUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()