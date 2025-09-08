#!/usr/bin/env python3
"""
Test that the TUI imports and initializes correctly after fixes.
"""

import sys
import os

def test_tui_imports():
    """Test that all TUI modules import correctly"""
    try:
        # Test main app import
        from luminous_nix.ui.main_app import LuminousNixTUI
        print("✅ main_app imports")
        
        # Test consciousness orb import
        from luminous_nix.ui.consciousness_orb import ConsciousnessOrb, AIState, EmotionalState
        print("✅ consciousness_orb imports")
        
        # Test configurable interface import
        from luminous_nix.ui.adaptive_interface import AdaptiveInterface, ComplexityLevel
        print("✅ adaptive_interface imports")
        
        # Test backend connector import
        from luminous_nix.ui.backend_connector import TUIBackendConnector
        print("✅ backend_connector imports")
        
        # Test visual orb bridge import
        from luminous_nix.ui.visual_orb_integration import VisualOrbBridge
        print("✅ visual_orb_integration imports")
        
        # Test consciousness detector stub
        from luminous_nix.consciousness.consciousness_detector import ConsciousnessBarometer
        print("✅ consciousness_detector imports")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_tui_creation():
    """Test that TUI can be created in headless mode"""
    try:
        from luminous_nix.ui.main_app import LuminousNixTUI
        
        # Create app in headless mode
        app = LuminousNixTUI(headless=True)
        print("✅ TUI created in headless mode")
        
        # Test basic attributes
        assert app.headless == True
        assert app.backend is not None
        print("✅ TUI attributes initialized")
        
        # Test consciousness barometer stub
        from luminous_nix.consciousness.consciousness_detector import ConsciousnessBarometer
        barometer = ConsciousnessBarometer()
        metrics = barometer.measure()
        assert 'coherence' in metrics
        assert 'flow_depth' in metrics
        print("✅ Consciousness detector stub works")
        
        return True
        
    except Exception as e:
        print(f"❌ Creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tui_components():
    """Test individual TUI components"""
    try:
        # Test ConsciousnessOrb
        from luminous_nix.ui.consciousness_orb import ConsciousnessOrb, AIState, EmotionalState
        orb = ConsciousnessOrb()
        orb.set_state(AIState.IDLE, EmotionalState.HAPPY)
        print("✅ ConsciousnessOrb works")
        
        # Test AdaptiveInterface
        from luminous_nix.ui.adaptive_interface import AdaptiveInterface, ComplexityLevel
        interface = AdaptiveInterface()
        interface.complexity_level = ComplexityLevel.FOCUSED
        print("✅ AdaptiveInterface works")
        
        # Test TUIBackendConnector
        from luminous_nix.ui.backend_connector import TUIBackendConnector
        backend = TUIBackendConnector(mindful_mode=False)
        state = backend.get_current_state()
        assert isinstance(state, dict)
        print("✅ TUIBackendConnector works")
        
        return True
        
    except Exception as e:
        print(f"❌ Component error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all TUI tests"""
    print("\n🧪 Testing TUI after fixes...")
    print("="*50)
    
    success = True
    
    # Test imports
    print("\n1. Testing imports:")
    if not test_tui_imports():
        success = False
    
    # Test creation
    print("\n2. Testing TUI creation:")
    if not test_tui_creation():
        success = False
    
    # Test components
    print("\n3. Testing TUI components:")
    if not test_tui_components():
        success = False
    
    # Summary
    print("\n" + "="*50)
    if success:
        print("✅ All TUI tests passed!")
        print("\nThe TUI is now working correctly:")
        print("- All imports succeed")
        print("- TUI can be created")
        print("- Components initialize properly")
        print("- Consciousness detector stub provides defaults")
        print("\nTo run the TUI:")
        print("  poetry run python -m luminous_nix.ui.main_app")
        print("  or: ./bin/nix-tui")
        return 0
    else:
        print("❌ Some TUI tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())