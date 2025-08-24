#!/usr/bin/env python3
"""
Benchmark current subprocess performance to establish baseline
before native bindings are available.
"""

import asyncio
import time
import subprocess
import json
from statistics import mean, stdev

async def benchmark_subprocess_async(cmd: list, iterations: int = 10):
    """Benchmark async subprocess performance."""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms
    
    return {
        "mean": mean(times),
        "stdev": stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "samples": len(times)
    }

def benchmark_subprocess_sync(cmd: list, iterations: int = 10):
    """Benchmark sync subprocess performance."""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms
    
    return {
        "mean": mean(times),
        "stdev": stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "samples": len(times)
    }

async def main():
    """Run comprehensive performance benchmarks."""
    
    print("=" * 60)
    print("📊 CURRENT SUBPROCESS PERFORMANCE BASELINE")
    print("=" * 60)
    print()
    
    # Test commands
    commands = [
        (["echo", "test"], "Simple echo"),
        (["nix", "--version"], "Nix version check"),
        (["nix", "search", "nixpkgs", "nonexistentpackage123"], "Package search (no results)"),
        (["nix", "eval", "--expr", "1 + 1"], "Simple evaluation"),
    ]
    
    results = {}
    
    for cmd, description in commands:
        print(f"🧪 Testing: {description}")
        print(f"   Command: {' '.join(cmd)}")
        
        # Skip if command doesn't exist
        try:
            subprocess.run(cmd[0:1], capture_output=True, timeout=0.1)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"   ⚠️  Command not available, skipping")
            continue
        
        # Async benchmark
        print("   Async subprocess...")
        async_result = await benchmark_subprocess_async(cmd, 5)
        
        # Sync benchmark
        print("   Sync subprocess...")
        sync_result = benchmark_subprocess_sync(cmd, 5)
        
        results[description] = {
            "command": " ".join(cmd),
            "async": async_result,
            "sync": sync_result
        }
        
        print(f"   ✅ Async: {async_result['mean']:.2f}ms (±{async_result['stdev']:.2f}ms)")
        print(f"   ✅ Sync:  {sync_result['mean']:.2f}ms (±{sync_result['stdev']:.2f}ms)")
        print()
    
    # Summary
    print("=" * 60)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 60)
    print()
    
    print("Current Implementation (Subprocess):")
    for desc, data in results.items():
        print(f"  {desc}:")
        print(f"    Async: {data['async']['mean']:.2f}ms")
        print(f"    Sync:  {data['sync']['mean']:.2f}ms")
    
    print()
    print("Expected with Native Bindings (Theoretical):")
    print("  Simple operations: <0.1ms (100x improvement)")
    print("  Complex queries: <1ms (10-50x improvement)")
    print("  No subprocess overhead!")
    
    print()
    print("=" * 60)
    print("💡 INSIGHTS")
    print("=" * 60)
    print()
    
    # Calculate average overhead
    if "Simple echo" in results:
        echo_time = results["Simple echo"]["async"]["mean"]
        print(f"🎯 Subprocess overhead: ~{echo_time:.2f}ms per call")
        print(f"   This is eliminated with native bindings!")
        
    print()
    print("📝 Native Binding Benefits:")
    print("  1. Zero subprocess spawn time")
    print("  2. Direct memory access")
    print("  3. No serialization overhead")
    print("  4. Better error handling")
    print("  5. Real progress callbacks")
    
    # Save results
    with open("benchmark_baseline.json", "w") as f:
        json.dump(results, f, indent=2)
    print()
    print("📊 Results saved to benchmark_baseline.json")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())