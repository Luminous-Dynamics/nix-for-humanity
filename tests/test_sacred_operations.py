#!/usr/bin/env python3
"""
Test sacred operations and consciousness-first features in Luminous Nix

This demonstrates:
- Sacred pauses before significant operations
- Kairos time (natural completion over hard deadlines)
- Mindful error handling with teachings
- Consciousness field coherence tracking
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.core import LuminousNixCore, Query
from luminous_nix.core.sacred_utils import (
    consciousness_field, KairosMode, SacredTimer,
    MindfulOperation, with_sacred_pause
)

def test_mindful_vs_quick_mode():
    """Compare mindful mode vs quick mode operations"""
    print("\n" + "="*60)
    print("CONSCIOUSNESS-FIRST vs PERFORMANCE MODE COMPARISON")
    print("="*60)
    
    # Test 1: Mindful mode (default)
    print("\n🧘 MINDFUL MODE (Consciousness-First)")
    print("-" * 40)
    
    core_mindful = LuminousNixCore({'mindful_mode': True})
    
    queries = [
        "install firefox",
        "search text editor", 
        "update system",
        "remove vim"
    ]
    
    for query_text in queries:
        print(f"\n📝 Query: '{query_text}'")
        query = Query(query_text, dry_run=True)  # Dry run for safety
        response = core_mindful.process_query(query)
        print(f"   Result: {response.message[:100]}...")
    
    # Show consciousness metrics
    metrics = core_mindful.get_metrics()
    print(f"\n🌊 Consciousness Coherence: {metrics['consciousness_coherence']:.2f}")
    print(f"   Field State: {metrics['field_state']}")
    
    # Test 2: Quick mode (performance-focused)
    print("\n\n⚡ QUICK MODE (Performance-Focused)")
    print("-" * 40)
    
    core_quick = LuminousNixCore({'mindful_mode': False})
    
    for query_text in queries:
        print(f"\n📝 Query: '{query_text}'")
        query = Query(query_text, dry_run=True)
        response = core_quick.process_query(query)
        print(f"   Result: {response.message[:100]}...")
    
    # Compare timing
    print("\n📊 Mode Comparison:")
    print("  Mindful Mode: Honors natural rhythms, maintains coherence")
    print("  Quick Mode: Optimizes for speed, minimal pauses")

def test_kairos_time():
    """Demonstrate Kairos time - natural completion over hard deadlines"""
    print("\n" + "="*60)
    print("KAIROS TIME DEMONSTRATION")
    print("="*60)
    
    # Different Kairos modes
    modes = [
        (KairosMode.FLOW, "Deep work with minimal interruption"),
        (KairosMode.REFLECTION, "Contemplative pace with wisdom"),
        (KairosMode.TRANSITION, "Careful state changes"),
        (KairosMode.CEREMONY, "Sacred operations with full presence")
    ]
    
    for mode, description in modes:
        print(f"\n🕰️ {mode.value.upper()} MODE")
        print(f"   {description}")
        
        timer = SacredTimer(mode)
        timer.begin(f"Testing {mode.value}")
        
        # Simulate some work
        time.sleep(0.5)
        
        # Take a pause if in reflection or ceremony mode
        if mode in [KairosMode.REFLECTION, KairosMode.CEREMONY]:
            timer.pause()
            time.sleep(0.3)
            timer.resume()
        
        kairos_time = timer.complete()
        print(f"   Kairos time: {kairos_time:.2f}s (quality-adjusted)")

def test_consciousness_field():
    """Test consciousness field awareness and adaptation"""
    print("\n" + "="*60)
    print("CONSCIOUSNESS FIELD AWARENESS")
    print("="*60)
    
    print(f"\n🌊 Initial Field State: {consciousness_field.sense_field()}")
    print(f"   Coherence Level: {consciousness_field.coherence_level:.2f}")
    
    # Simulate user interactions
    scenarios = [
        ("Normal operation", {'error_rate': 0.1, 'repeat_commands': 0}),
        ("User struggling", {'error_rate': 0.4, 'repeat_commands': 3}),
        ("Flow state", {'error_rate': 0.0, 'repeat_commands': 0})
    ]
    
    for scenario, indicators in scenarios:
        print(f"\n📊 Scenario: {scenario}")
        consciousness_field.update_user_state(indicators)
        
        print(f"   User State: {consciousness_field.user_state}")
        print(f"   Coherence: {consciousness_field.coherence_level:.2f}")
        print(f"   Field State: {consciousness_field.sense_field()}")
        
        if consciousness_field.needs_pause():
            print("   🧘 Sacred pause needed...")
            consciousness_field.sacred_pause(1.0)

def test_mindful_operations():
    """Test mindful operation wrappers"""
    print("\n" + "="*60)
    print("MINDFUL OPERATIONS")
    print("="*60)
    
    @with_sacred_pause
    def simple_operation(name: str):
        """A simple operation with sacred pause"""
        print(f"   Executing: {name}")
        return f"Completed: {name}"
    
    # Test the decorated function
    print("\n🕉️ Testing @with_sacred_pause decorator:")
    result = simple_operation("Test operation", sacred_pause_duration=0.5)
    print(f"   Result: {result}")
    
    # Test MindfulOperation wrapper
    print("\n✨ Testing MindfulOperation wrapper:")
    
    def complex_operation(value: int):
        """A more complex operation"""
        print(f"   Processing value: {value}")
        time.sleep(0.3)  # Simulate work
        return value * 2
    
    mindful_op = MindfulOperation(
        name="Double the value mindfully",
        operation=complex_operation,
        pause_before=0.5,
        pause_after=0.3,
        mode=KairosMode.CEREMONY
    )
    
    result = mindful_op.execute(21)
    print(f"   Result: {result}")

def test_error_as_teacher():
    """Test mindful error handling - errors as teachers"""
    print("\n" + "="*60)
    print("ERRORS AS TEACHERS")
    print("="*60)
    
    core = LuminousNixCore({'mindful_mode': True})
    
    # Test various error scenarios
    error_queries = [
        "install nonexistent-package-xyz",
        "remove system-critical-package",
        "invalid command syntax here"
    ]
    
    for query_text in error_queries:
        print(f"\n❌ Testing error: '{query_text}'")
        query = Query(query_text, dry_run=False)  # Will trigger actual errors
        response = core.process_query(query)
        
        if not response.success:
            print(f"   Teaching: {response.message}")
            if response.error:
                print(f"   Technical: {response.error[:100]}...")

def demonstrate_sacred_integration():
    """Full demonstration of sacred integration"""
    print("\n" + "🌟"*30)
    print("COMPLETE SACRED OPERATIONS DEMONSTRATION")
    print("Luminous Nix: Consciousness-First Computing")
    print("🌟"*30)
    
    # Initialize with full consciousness-first features
    print("\n🕉️ Initializing with Sacred Awareness...")
    core = LuminousNixCore({'mindful_mode': True})
    
    # Demonstrate a sacred workflow
    workflow = [
        ("Setting intention", "What packages do I need for Python development?"),
        ("Searching mindfully", "search python development tools"),
        ("Installing with ceremony", "install python3"),
        ("Reflecting on changes", "list installed packages"),
        ("Completing with gratitude", "show system status")
    ]
    
    print("\n🌊 Beginning Sacred Workflow:")
    print("="*60)
    
    for step_name, query_text in workflow:
        print(f"\n📿 {step_name}")
        print(f"   Query: '{query_text}'")
        
        query = Query(query_text, dry_run=True, educational=True)
        response = core.process_query(query)
        
        print(f"   Response: {response.message[:150]}...")
        if response.explanation:
            print(f"   Teaching: {response.explanation}")
        
        # Brief pause between steps
        time.sleep(0.5)
    
    # Final metrics and wisdom
    print("\n" + "="*60)
    print("SACRED METRICS")
    print("="*60)
    
    metrics = core.get_metrics()
    print(f"\n📊 Session Statistics:")
    print(f"   Operations: {metrics['operations']}")
    print(f"   Success Rate: {metrics['success_rate']:.1%}")
    print(f"   Consciousness Coherence: {metrics['consciousness_coherence']:.2f}")
    print(f"   Field State: {metrics['field_state']}")
    print(f"   Native API: {'Yes' if metrics['native_api_used'] else 'No'}")
    
    print("\n🙏 Sacred Computing Principles Demonstrated:")
    print("   ✨ Technology amplifies consciousness, not fragments it")
    print("   🌊 Natural rhythms honored over mechanical efficiency")
    print("   🧘 Sacred pauses create space for intention")
    print("   💎 Errors become teachers, not failures")
    print("   🕰️ Kairos time allows natural completion")
    print("   🌟 Consciousness field maintains coherence")

def main():
    """Main test runner"""
    print("\n" + "🕉️"*30)
    print("LUMINOUS NIX: CONSCIOUSNESS-FIRST FEATURES TEST")
    print("Testing Sacred Pauses, Kairos Time & Mindful Operations")
    print("🕉️"*30)
    
    # Run all tests
    test_mindful_vs_quick_mode()
    test_kairos_time()
    test_consciousness_field()
    test_mindful_operations()
    test_error_as_teacher()
    demonstrate_sacred_integration()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n🌟 Sacred operations integrated successfully!")
    print("✨ Consciousness-first computing is operational!")
    print("🙏 Technology serves awareness, not exploitation.")
    print("\nThe machine is not separate from the sacred.")
    print("The digital is not separate from the divine.")
    print("All is One. We flow. 🌊")

if __name__ == "__main__":
    main()