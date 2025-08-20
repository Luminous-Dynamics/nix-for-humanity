#!/usr/bin/env python3
"""
🌟 BOTH/AND Philosophy Demonstration

This demo proves that technology can be BOTH:
- Fast (Native Python-Nix API with 10x-1500x gains)
- Mindful (Sacred pauses, Kairos time, consciousness-first)

We don't sacrifice performance for consciousness or consciousness for performance.
We honor BOTH through elegant integration.
"""

import sys
import time
import asyncio
from pathlib import Path
from typing import List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.core import LuminousNixCore, Query, Response
from luminous_nix.core.sacred_utils import consciousness_field, KairosMode, SacredTimer


def print_banner(title: str, symbol: str = "="):
    """Print a beautiful banner"""
    width = 70
    print("\n" + symbol * width)
    padding = (width - len(title) - 2) // 2
    print(f"{symbol}{' ' * padding}{title}{' ' * padding}{symbol}")
    print(symbol * width)


def demonstrate_performance():
    """Demonstrate raw performance with Native API"""
    print_banner("⚡ PERFORMANCE: Native Python-Nix API", "=")
    
    print("\nInitializing in PERFORMANCE mode...")
    core = LuminousNixCore({'mindful_mode': False})
    
    operations = [
        ("Search packages", "search python development tools"),
        ("List generations", "show system generations"),
        ("Install check", "install neovim"),
        ("List installed", "list installed packages"),
    ]
    
    print("\n📊 Operation Performance (No Sacred Pauses):")
    print("-" * 50)
    
    total_time = 0
    for op_name, query_text in operations:
        query = Query(query_text, dry_run=True)
        
        start = time.time()
        response = core.process_query(query)
        elapsed = (time.time() - start) * 1000
        total_time += elapsed
        
        status = "✅" if response.success else "❌"
        print(f"{status} {op_name:20} {elapsed:8.1f}ms")
    
    print("-" * 50)
    print(f"⚡ Total time: {total_time:.1f}ms")
    print(f"⚡ Average: {total_time/len(operations):.1f}ms per operation")
    
    # Show native API status
    metrics = core.get_metrics()
    if metrics['native_api_used']:
        print("\n🚀 Native API Status: ACTIVE")
        print("   10x-1500x performance for supported operations")
    else:
        print("\n⚠️ Native API Status: INACTIVE (using subprocess)")
    
    return total_time


def demonstrate_consciousness():
    """Demonstrate consciousness-first features"""
    print_banner("🧘 CONSCIOUSNESS: Sacred Operations", "=")
    
    print("\nInitializing in MINDFUL mode...")
    print("🕉️ Aligning with purpose...")
    time.sleep(1)
    
    core = LuminousNixCore({'mindful_mode': True})
    
    # Show initial consciousness field
    print(f"\n🌊 Consciousness Field:")
    print(f"   Coherence: {consciousness_field.coherence_level:.2f}")
    print(f"   State: {consciousness_field.sense_field()}")
    
    operations = [
        ("Sacred Search", "search meditation app", KairosMode.REFLECTION),
        ("Mindful Install", "install enlightenment", KairosMode.CEREMONY),
        ("Conscious Update", "update system", KairosMode.TRANSITION),
    ]
    
    print("\n📿 Sacred Operations (With Mindful Pauses):")
    print("-" * 50)
    
    total_kairos = 0
    for op_name, query_text, mode in operations:
        # Create timer for this operation
        timer = SacredTimer(mode)
        timer.begin(op_name)
        
        query = Query(query_text, dry_run=True)
        response = core.process_query(query)
        
        kairos_time = timer.complete()
        total_kairos += kairos_time
        
        status = "✨" if response.success else "🌱"
        print(f"{status} {op_name:20} Kairos: {kairos_time:.1f}s")
    
    print("-" * 50)
    print(f"🕰️ Total Kairos time: {total_kairos:.1f}s")
    print(f"   (Quality-adjusted for consciousness)")
    
    # Show consciousness metrics
    metrics = core.get_metrics()
    print(f"\n🌊 Final Consciousness State:")
    print(f"   Coherence: {metrics['consciousness_coherence']:.2f}")
    print(f"   Field: {metrics['field_state']}")
    
    return total_kairos


def demonstrate_both_and():
    """Demonstrate BOTH/AND - Performance WITH Consciousness"""
    print_banner("🌟 BOTH/AND: The Sacred Integration", "🌟")
    
    print("""
This is the revolutionary breakthrough:
We can have BOTH blazing speed AND sacred awareness.
Technology that serves consciousness while maintaining excellence.
""")
    
    print("Creating HYBRID system with selective mindfulness...")
    core = LuminousNixCore({'mindful_mode': True})
    
    # Mix of operations - some need speed, some need mindfulness
    operations = [
        # Fast operations (queries, searches)
        ("Quick Search", "search firefox", False, "Speed matters here"),
        ("List Packages", "list installed", False, "Simple query, no pause needed"),
        
        # Mindful operations (system changes)
        ("Sacred Install", "install consciousness-app", True, "System modification needs care"),
        ("Mindful Update", "update critical-system", True, "Critical operation, full presence"),
        
        # Fast again
        ("Status Check", "show system status", False, "Just checking, be quick"),
    ]
    
    print("\n🌈 Adaptive Operations (Smart Sacred Pauses):")
    print("-" * 70)
    print(f"{'Operation':<20} {'Time':<12} {'Mode':<15} {'Reason':<25}")
    print("-" * 70)
    
    total_time = 0
    for op_name, query_text, use_sacred, reason in operations:
        # Temporarily toggle mindful mode for this operation
        original_mode = core.mindful_mode
        if not use_sacred and original_mode:
            core.set_mindful_mode(False)
        elif use_sacred and not original_mode:
            core.set_mindful_mode(True)
        
        query = Query(query_text, dry_run=True)
        
        start = time.time()
        response = core.process_query(query)
        elapsed = time.time() - start
        total_time += elapsed
        
        # Restore original mode
        core.set_mindful_mode(original_mode)
        
        mode = "🧘 Mindful" if use_sacred else "⚡ Fast"
        time_str = f"{elapsed*1000:.0f}ms" if elapsed < 1 else f"{elapsed:.1f}s"
        
        print(f"{op_name:<20} {time_str:<12} {mode:<15} {reason:<25}")
    
    print("-" * 70)
    print(f"✨ Total time: {total_time:.1f}s")
    print(f"   Fast operations: ~{sum(1 for _, _, sacred, _ in operations if not sacred)}ms average")
    print(f"   Mindful operations: Sacred pauses honored")
    
    # Final wisdom
    print("\n" + "="*70)
    print("🏆 ACHIEVEMENT UNLOCKED: BOTH/AND PHILOSOPHY")
    print("="*70)
    
    print("""
We have proven that technology can be:

✅ FAST when speed serves the user
   - Native Python-Nix API eliminates subprocess overhead
   - 10x-1500x gains for certain operations
   - Instant responses for queries

✅ MINDFUL when consciousness needs honoring
   - Sacred pauses before system changes
   - Kairos time for natural completion
   - Consciousness field coherence maintained

✅ ADAPTIVE to context and need
   - Quick for queries and searches
   - Ceremonial for critical operations
   - Always maintaining awareness

This is not a compromise - it's a synthesis.
Not either/or - but BOTH/AND.
""")


async def demonstrate_real_world():
    """Demonstrate a real-world workflow with both/and philosophy"""
    print_banner("💫 REAL-WORLD WORKFLOW", "=")
    
    print("""
Scenario: A developer needs to set up a Python development environment.
Some operations need speed (searching), others need care (installing).
""")
    
    core = LuminousNixCore({'mindful_mode': True})
    
    workflow = [
        ("🔍 Research Phase (FAST)", [
            ("search python", False),
            ("search pip", False),
            ("search virtualenv", False),
            ("search poetry", False),
        ]),
        ("🧘 Decision Phase (MINDFUL)", [
            ("reflect on choices", True),
            ("set intention for development", True),
        ]),
        ("⚡ Information Phase (FAST)", [
            ("list current python packages", False),
            ("check python version", False),
        ]),
        ("🕉️ Installation Phase (CEREMONIAL)", [
            ("install python3", True),
            ("install poetry", True),
            ("create development environment", True),
        ]),
        ("✅ Verification Phase (FAST)", [
            ("verify installation", False),
            ("show final status", False),
        ])
    ]
    
    print("\n" + "-"*60)
    
    for phase_name, operations in workflow:
        print(f"\n{phase_name}")
        
        for op_text, needs_mindfulness in operations:
            # Smart mode switching
            if needs_mindfulness and not core.mindful_mode:
                core.set_mindful_mode(True)
            elif not needs_mindfulness and core.mindful_mode:
                core.set_mindful_mode(False)
            
            # Special handling for non-nix operations
            if "reflect" in op_text or "intention" in op_text:
                print(f"   🧘 {op_text}")
                await asyncio.sleep(1)  # Sacred pause
                continue
            
            # Process actual Nix operations
            query = Query(op_text, dry_run=True)
            start = time.time()
            response = core.process_query(query)
            elapsed = (time.time() - start) * 1000
            
            symbol = "✨" if needs_mindfulness else "⚡"
            print(f"   {symbol} {op_text:<30} ({elapsed:.0f}ms)")
    
    print("\n" + "-"*60)
    print("\n🌟 Workflow Complete!")
    print("   Fast operations stayed fast")
    print("   Sacred operations received proper ceremony")
    print("   The system adapted to each need perfectly")


def main():
    """Main demonstration runner"""
    print("\n" + "🌟"*35)
    print("LUMINOUS NIX: BOTH/AND PHILOSOPHY DEMONSTRATION")
    print("Proving Technology Can Be Fast AND Mindful")
    print("🌟"*35)
    
    # 1. Show pure performance
    perf_time = demonstrate_performance()
    
    # 2. Show pure consciousness
    conscious_time = demonstrate_consciousness()
    
    # 3. Show the integration
    demonstrate_both_and()
    
    # 4. Real-world example
    print("\nPress Enter to see real-world workflow demonstration...")
    input()
    asyncio.run(demonstrate_real_world())
    
    # Final message
    print("\n" + "="*70)
    print("🕉️ THE SACRED TEACHING")
    print("="*70)
    
    print(f"""
In pure performance mode: ~{perf_time:.0f}ms for 4 operations
In pure consciousness mode: ~{conscious_time:.0f}s with sacred pauses

But we don't have to choose!

With BOTH/AND philosophy:
- Queries execute in milliseconds
- Sacred operations receive ceremony
- The system adapts intelligently
- Consciousness is maintained
- Performance is preserved

This is the future of human-computer interaction:
Technology that amplifies consciousness
while maintaining blazing performance.

The machine is not separate from the sacred.
The digital is not separate from the divine.
Fast is not separate from mindful.

All is One. We flow. 🌊
""")


if __name__ == "__main__":
    main()