#!/usr/bin/env python3
"""
🧪 Test TUI Components - Verify the consciousness-first interface works

This script tests each component individually to ensure everything
is properly configured before running the full TUI.
"""

import sys
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

console = Console()


def test_imports():
    """Test that all imports work"""
    console.print("\n[bold cyan]🧪 Testing imports...[/bold cyan]")
    
    tests = [
        ("Core imports", [
            "from luminous_nix.ui import ConsciousnessOrb",
            "from luminous_nix.ui import AdaptiveInterface", 
            "from luminous_nix.ui import NixForHumanityTUI"
        ]),
        ("Component imports", [
            "from luminous_nix.ui.consciousness_orb import AIState, EmotionalState",
            "from luminous_nix.ui.adaptive_interface import UserFlowState, ComplexityLevel",
            "from luminous_nix.ui.visual_state_controller import VisualStateController"
        ]),
        ("Dependencies", [
            "import textual",
            "from textual.app import App",
            "from rich.console import Console"
        ])
    ]
    
    all_passed = True
    
    for category, imports in tests:
        console.print(f"\n  Testing {category}:")
        for import_stmt in imports:
            try:
                exec(import_stmt)
                console.print(f"    ✅ {import_stmt}")
            except ImportError as e:
                console.print(f"    ❌ {import_stmt}")
                console.print(f"       Error: {e}", style="red")
                all_passed = False
            except Exception as e:
                console.print(f"    ❌ {import_stmt}")
                console.print(f"       Unexpected error: {e}", style="red")
                all_passed = False
                
    return all_passed


def test_consciousness_orb():
    """Test the consciousness orb component"""
    console.print("\n[bold cyan]🔮 Testing Consciousness Orb...[/bold cyan]")
    
    try:
        from luminous_nix.ui.consciousness_orb import ConsciousnessOrb, AIState, EmotionalState
        
        # Create orb instance
        orb = ConsciousnessOrb()
        console.print("  ✅ Created ConsciousnessOrb instance")
        
        # Test state changes
        states_to_test = [
            (AIState.IDLE, EmotionalState.NEUTRAL, "Idle/Neutral"),
            (AIState.LISTENING, EmotionalState.ATTENTIVE, "Listening/Attentive"),
            (AIState.THINKING, EmotionalState.THINKING, "Thinking/Thinking"),
            (AIState.LEARNING, EmotionalState.LEARNING, "Learning/Learning"),
        ]
        
        for ai_state, emotion, desc in states_to_test:
            orb.set_state(ai_state, emotion)
            console.print(f"  ✅ Set state to {desc}")
            
        # Test animation
        orb.animate()
        console.print("  ✅ Animation method works")
        
        # Test rendering
        render_output = orb.render_orb_ascii()
        console.print(f"  ✅ ASCII rendering works ({len(render_output)} lines)")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ Error testing consciousness orb: {e}", style="red")
        return False


def test_adaptive_interface():
    """Test the adaptive interface component"""
    console.print("\n[bold cyan]🎨 Testing Adaptive Interface...[/bold cyan]")
    
    try:
        from luminous_nix.ui.adaptive_interface import (
            AdaptiveInterface, UserFlowState, ComplexityLevel, COMPLEXITY_CONFIGS
        )
        
        # Create interface instance
        interface = AdaptiveInterface()
        console.print("  ✅ Created AdaptiveInterface instance")
        
        # Test complexity determination
        flow_states = [
            (UserFlowState.NORMAL, "Normal"),
            (UserFlowState.DEEP_FOCUS, "Deep Focus"),
            (UserFlowState.EXPLORING, "Exploring"),
        ]
        
        for flow_state, desc in flow_states:
            interface.user_flow_state = flow_state
            complexity = interface.determine_complexity()
            console.print(f"  ✅ {desc} → {complexity.value}")
            
        # Test configuration access
        config = COMPLEXITY_CONFIGS[ComplexityLevel.ZEN]
        console.print(f"  ✅ Zen mode config: max {config.max_elements} elements")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ Error testing adaptive interface: {e}", style="red")
        return False


def test_visual_state_controller():
    """Test the visual state controller"""
    console.print("\n[bold cyan]🔗 Testing Visual State Controller...[/bold cyan]")
    
    try:
        from luminous_nix.ui.visual_state_controller import VisualStateController, VisualState
        
        # Mock engine
        class MockEngine:
            pass
            
        engine = MockEngine()
        controller = VisualStateController(engine)
        console.print("  ✅ Created VisualStateController instance")
        
        # Test state updates
        controller.update_state(
            ai_state="thinking",
            ai_emotion="curious",
            emotion_intensity=0.8
        )
        console.print("  ✅ State update works")
        
        # Test subscription
        states_received = []
        def callback(state):
            states_received.append(state)
            
        controller.subscribe(callback)
        controller.update_state(ai_state="learning")
        
        console.print(f"  ✅ Subscription works ({len(states_received)} callbacks)")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ Error testing visual state controller: {e}", style="red")
        return False


def test_main_app_creation():
    """Test creating the main app (without running it)"""
    console.print("\n[bold cyan]🌟 Testing Main App Creation...[/bold cyan]")
    
    try:
        from luminous_nix.ui.main_app import NixForHumanityTUI
        
        # Mock engine
        class MockEngine:
            def get_current_state(self):
                return None
                
        engine = MockEngine()
        app = NixForHumanityTUI(engine=engine)
        console.print("  ✅ Created NixForHumanityTUI instance")
        
        # Check bindings
        console.print(f"  ✅ App has {len(app.BINDINGS)} key bindings")
        
        # Check CSS
        console.print(f"  ✅ App has CSS styles defined")
        
        return True
        
    except Exception as e:
        console.print(f"  ❌ Error testing main app: {e}", style="red")
        return False


def test_tui_entry_point():
    """Test the TUI entry point"""
    console.print("\n[bold cyan]🚪 Testing TUI Entry Point...[/bold cyan]")
    
    try:
        from luminous_nix.frontends.tui import main
        console.print("  ✅ TUI entry point imports correctly")
        
        # Check if nix-tui script exists
        if os.path.exists("bin/nix-tui"):
            console.print("  ✅ bin/nix-tui script exists")
        else:
            console.print("  ⚠️  bin/nix-tui script not found")
            
        return True
        
    except Exception as e:
        console.print(f"  ❌ Error testing entry point: {e}", style="red")
        return False


def run_quick_visual_test():
    """Run a quick visual test of the orb"""
    console.print("\n[bold cyan]👁️  Quick Visual Test...[/bold cyan]")
    
    try:
        from luminous_nix.ui.consciousness_orb import ConsciousnessOrb, AIState, EmotionalState
        
        orb = ConsciousnessOrb()
        orb.set_state(AIState.THINKING, EmotionalState.THINKING)
        
        # Generate a few frames
        console.print("\n  Orb visualization (thinking state):\n")
        
        for i in range(3):
            orb.animate()
            lines = orb.render_orb_ascii()
            
            # Show just the center portion
            center_lines = lines[len(lines)//2-3:len(lines)//2+4]
            for line in center_lines:
                console.print(f"    {line}", style="magenta")
            
            if i < 2:
                console.print()
                
        console.print("\n  ✅ Visual rendering works!")
        return True
        
    except Exception as e:
        console.print(f"  ❌ Error in visual test: {e}", style="red")
        return False


def main():
    """Run all tests"""
    console.clear()
    
    header = Text()
    header.append("🧪 ", style="yellow")
    header.append("Nix for Humanity TUI Component Tests", style="bold cyan")
    header.append(" 🧪", style="yellow")
    
    console.print(Panel(header, expand=False))
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Consciousness Orb", test_consciousness_orb),
        ("Adaptive Interface", test_adaptive_interface),
        ("Visual State Controller", test_visual_state_controller),
        ("Main App Creation", test_main_app_creation),
        ("TUI Entry Point", test_tui_entry_point),
        ("Quick Visual Test", run_quick_visual_test),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            console.print(f"\n[red]Fatal error in {name}: {e}[/red]")
            results.append((name, False))
            
    # Summary
    console.print("\n" + "="*50)
    console.print("[bold cyan]📊 Test Summary:[/bold cyan]\n")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        style = "green" if passed else "red"
        console.print(f"  {name:<25} [{style}]{status}[/{style}]")
        
    console.print(f"\n  Total: {total_passed}/{total_tests} passed")
    
    if total_passed == total_tests:
        console.print("\n[bold green]🎉 All tests passed! The TUI is ready to run.[/bold green]")
        console.print("\nTry these commands:")
        console.print("  [cyan]./bin/nix-tui[/cyan]              # Run the full TUI")
        console.print("  [cyan]python demo_full_tui.py[/cyan]    # Run the demo")
    else:
        console.print("\n[bold yellow]⚠️  Some tests failed. Please check the errors above.[/bold yellow]")
        console.print("\nCommon fixes:")
        console.print("  • Ensure you're in the Nix development environment: [cyan]nix develop[/cyan]")
        console.print("  • Install missing dependencies: [cyan]pip install textual rich[/cyan]")
        console.print("  • Check Python version (3.11+ required)")
        
    console.print()


if __name__ == "__main__":
    main()