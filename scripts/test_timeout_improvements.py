#!/usr/bin/env python3
"""
Test the improved timeout handling for Sacred Council
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from luminous_nix.consciousness.model_dispatcher import ModelOrchestrator, TaskType
from luminous_nix.consciousness.hardware_profiler import HardwareProfiler


def test_timeout_improvements():
    """Test that timeout improvements work correctly"""
    print("\n" + "=" * 70)
    print("🧪 TESTING TIMEOUT IMPROVEMENTS")
    print("=" * 70)
    print()
    
    # Initialize orchestrator
    profiler = HardwareProfiler()
    orchestrator = ModelOrchestrator(profiler.get_profile())
    
    print("Testing execute_with_model with different timeout scenarios...")
    print()
    
    # Test 1: Quick response model (should work)
    print("1️⃣ Testing with fast model (gemma:2b):")
    start = time.time()
    response = orchestrator.execute_with_model(
        model_tag='gemma:2b',
        prompt='Say "hello" in one word',
        timeout=10  # Short timeout for fast model
    )
    elapsed = time.time() - start
    
    if response:
        print(f"   ✅ Success in {elapsed:.1f}s")
        print(f"   Response: {response[:50]}...")
    else:
        print(f"   ❌ Failed after {elapsed:.1f}s")
    
    print()
    
    # Test 2: Test retry mechanism with potentially slow model
    print("2️⃣ Testing retry mechanism (with timeout simulation):")
    
    # Use a model that might need loading
    test_model = orchestrator.select_model_for_task(TaskType.ETHICAL_REASONING)
    if test_model:
        print(f"   Using: {test_model}")
        
        start = time.time()
        response = orchestrator.execute_with_model(
            model_tag=test_model,
            prompt='What is 2+2? Answer in one number only.',
            timeout=15,  # Short initial timeout to test retry
            retry_on_timeout=True
        )
        elapsed = time.time() - start
        
        if response:
            print(f"   ✅ Success in {elapsed:.1f}s (may have retried)")
            print(f"   Response: {response[:50]}...")
        else:
            print(f"   ⚠️ Could not get response in {elapsed:.1f}s")
    else:
        print("   ⚠️ No ethical reasoning model configured")
    
    print()
    
    # Test 3: Test first-run detection
    print("3️⃣ Testing first-run detection:")
    
    # Clear active models to simulate fresh start
    orchestrator.active_models.clear()
    
    # This should detect it's a first run and use extended timeout
    start = time.time()
    response = orchestrator.execute_with_model(
        model_tag='gemma:2b',
        prompt='What is the capital of France? One word answer.',
        # No timeout specified - should auto-detect first run
    )
    elapsed = time.time() - start
    
    if response:
        print(f"   ✅ First-run handled in {elapsed:.1f}s")
        print(f"   Response: {response[:50]}...")
    else:
        print(f"   ❌ Failed after {elapsed:.1f}s")
    
    # Second run should be faster
    print("\n   Testing second run (should use shorter timeout):")
    start = time.time()
    response = orchestrator.execute_with_model(
        model_tag='gemma:2b',
        prompt='What is 1+1? Number only.',
    )
    elapsed = time.time() - start
    
    if response:
        print(f"   ✅ Second run completed in {elapsed:.1f}s")
        print(f"   Response: {response[:50]}...")
    else:
        print(f"   ❌ Failed after {elapsed:.1f}s")
    
    print()
    print("=" * 70)
    print("✨ Timeout improvement testing complete!")
    print()
    print("Key improvements:")
    print("  • First-run detection with extended timeouts")
    print("  • Automatic retry on timeout with progressive delays")
    print("  • Model loading state tracking")
    print("  • Configurable timeout and retry behavior")
    print("=" * 70)


if __name__ == "__main__":
    test_timeout_improvements()