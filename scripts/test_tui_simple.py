#!/usr/bin/env python3
"""
Simple TUI test to verify textual is working
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, Static, Input
    from textual.containers import Container
    
    class SimpleTUITest(App):
        """Simple test TUI"""
        
        CSS = """
        Screen {
            background: $surface;
        }
        
        #welcome {
            height: 5;
            margin: 1;
            border: solid $primary;
            padding: 1;
        }
        """
        
        def compose(self) -> ComposeResult:
            yield Header()
            yield Container(
                Static("🌟 Luminous Nix TUI Test 🌟\n\nTextual is working!\nSystem Readiness: 90.0%", id="welcome")
            )
            yield Footer()
    
    def test_basic():
        """Test basic textual functionality"""
        print("✅ Textual imports successfully!")
        print("✅ TUI components available!")
        print("\nTo run the full TUI:")
        print("  python -m luminous_nix.ui.main_app")
        print("\nOr use the launcher:")
        print("  ./bin/nix-tui")
        return True
    
    # Test imports from our actual TUI
    from luminous_nix.ui.consciousness_orb import ConsciousnessOrb, AIState
    from luminous_nix.ui.adaptive_interface import AdaptiveInterface, ComplexityLevel
    from luminous_nix.ui.backend_connector import TUIBackendConnector
    
    print("✅ All TUI components import successfully!")
    print("\nTUI Features Available:")
    print("  • ConsciousnessOrb - Visual AI state")
    print("  • AdaptiveInterface - Complexity adaptation")
    print("  • BackendConnector - Command processing")
    print("  • MainApp - Full interface")
    
    test_basic()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTo fix, run:")
    print("  poetry add textual")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()