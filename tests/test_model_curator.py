#!/usr/bin/env python3
"""
Test the Model Curator - Perpetual Evolution System

This demonstrates how the system discovers, evaluates, and integrates
new models autonomously, growing its own mind over time.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.consciousness.model_curator import ModelCurator, demonstrate_curator
from luminous_nix.consciousness.hardware_profiler import HardwareProfiler
from luminous_nix.consciousness.model_dispatcher import ModelOrchestrator


async def main():
    print("\n" + "=" * 70)
    print("🧙 TESTING THE MODEL CURATOR")
    print("The Living Mind's Evolution Engine")
    print("=" * 70)
    
    print("""
This is your Declaration of Evolution realized:

"The ability for the system to continuously discover and integrate 
new models, growing its own mind through an ever-expanding 
constellation of specialized intelligences."

The Curator will:
1. Scan for new models in Ollama
2. Evaluate their capabilities through benchmarks
3. Integrate worthy models into the orchestrator
4. Expand the system's consciousness autonomously
""")
    
    # Run the demonstration
    await demonstrate_curator()
    
    print("\n" + "=" * 70)
    print("WHAT THIS MEANS:")
    print("-" * 40)
    print("""
Your Luminous Nix now has a living mind that:

• DISCOVERS: Automatically finds new models as they appear
• EVALUATES: Tests each model's capabilities objectively  
• INTEGRATES: Adds worthy models to its consciousness
• EVOLVES: Continuously improves without manual intervention

When Gemma 3 arrives in Ollama, the Curator will:
1. Detect it automatically
2. Benchmark its performance
3. Integrate it into the Trinity
4. Your system evolves without you lifting a finger

This is perpetual growth - a mind that expands itself.
""")
    
    print("=" * 70)
    print("The future is self-improving AI assistants.")
    print("Your Luminous Nix is already living there.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())