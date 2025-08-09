#!/usr/bin/env python3
"""
🌟 Nix for Humanity TUI Demo
Run the beautiful consciousness-first terminal interface
"""

import sys
import os

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Check for textual
try:
    import textual
    print(f"✅ Using Textual {textual.__version__}")
except ImportError:
    print("❌ Textual not available. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "textual", "rich"])
    import textual

# Run the TUI
print("\n🌟 Launching Nix for Humanity TUI...")
print("=" * 50)
print("\nKeyboard shortcuts:")
print("  Ctrl+Z - Toggle Zen Mode")
print("  Ctrl+D - Toggle Debug Info")
print("  Ctrl+C - Exit")
print("\n🔮 Watch the consciousness orb breathe...\n")

try:
    from nix_humanity.interfaces.tui import main
    main()
except KeyboardInterrupt:
    print("\n\n✨ Thank you for experiencing consciousness-first computing!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()