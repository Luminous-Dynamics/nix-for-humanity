#!/usr/bin/env python3
"""
Direct TUI test - tries to run the TUI with whatever Python environment is available
"""

import sys
import subprocess
import os

print("🧪 Testing Nix for Humanity TUI directly...")
print("=" * 50)

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Check if we can import textual
try:
    import textual
    print(f"✅ Textual available: version {textual.__version__}")
except ImportError:
    print("❌ Textual not available")
    print("\nTrying to install in temporary virtual environment...")
    
    # Create temporary venv
    venv_path = "/tmp/nix-humanity-tui-env"
    subprocess.run([sys.executable, "-m", "venv", venv_path])
    
    # Activate and install
    pip_path = os.path.join(venv_path, "bin", "pip")
    python_path = os.path.join(venv_path, "bin", "python")
    
    print("📦 Installing textual and rich...")
    subprocess.run([pip_path, "install", "textual", "rich", "-q"])
    
    # Re-run this script with the venv Python
    print("\n🔄 Re-running with virtual environment...")
    os.execv(python_path, [python_path] + sys.argv)

# If we get here, textual is available
print("\n🎯 Testing TUI components...")

try:
    # Test imports
    from luminous_nix.ui.consciousness_orb import ConsciousnessOrb, AIState, EmotionalState
    from luminous_nix.ui.adaptive_interface import AdaptiveInterface
    from luminous_nix.ui.main_app import NixForHumanityTUI
    print("✅ All TUI components imported successfully!")
    
    # Test creating the app
    app = NixForHumanityTUI()
    print("✅ TUI app created successfully!")
    
    print("\n🚀 Ready to launch TUI!")
    print("\nPress Enter to start the TUI, or Ctrl+C to exit...")
    input()
    
    # Run the app
    app.run()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure you're in the project root directory")
except KeyboardInterrupt:
    print("\n\n✨ Test completed!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()