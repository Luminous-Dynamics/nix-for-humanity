#!/usr/bin/env python3
"""
Real Performance Benchmark - The Truth About Speed

This script measures ACTUAL performance improvements, not fantasy numbers.
Run this to see the real difference between:
1. Current subprocess approach (slow)
2. New indexed approach (fast)
3. Smart discovery (medium)
"""

import time
import subprocess
import json
import sys
from pathlib import Path
from statistics import mean, median

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.package_index import get_package_index, PackageIndex
from luminous_nix.core.smart_package_discovery import get_smart_discovery


def benchmark_subprocess(query: str, iterations: int = 3) -> dict:
    """Benchmark the current subprocess approach"""
    times = []
    
    for i in range(iterations):
        start = time.time()
        try:
            result = subprocess.run(
                ["nix", "search", "nixpkgs", query, "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            if result.returncode == 0 and result.stdout:
                packages = json.loads(result.stdout)
                count = len(packages)
            else:
                count = 0
                
        except subprocess.TimeoutExpired:
            times.append(10000)  # 10 second timeout
            count = 0
        except Exception as e:
            print(f"Subprocess error: {e}")
            times.append(10000)
            count = 0
    
    return {
        "method": "subprocess",
        "query": query,
        "avg_ms": mean(times),
        "median_ms": median(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "result_count": count,
        "times": times
    }


def benchmark_index(query: str, iterations: int = 3, index: PackageIndex = None) -> dict:
    """Benchmark the new indexed approach"""
    if not index:
        index = get_package_index()
    
    # Ensure index is built
    if index.needs_update():
        print("Building index first (one-time cost)...")
        success, count, build_time = index.build_index()
        print(f"  Built index with {count} packages in {build_time:.1f}s")
    
    times = []
    count = 0
    
    for i in range(iterations):
        results, elapsed_ms = index.search(query)
        times.append(elapsed_ms)
        count = len(results)
    
    return {
        "method": "index",
        "query": query,
        "avg_ms": mean(times),
        "median_ms": median(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "result_count": count,
        "times": times
    }


def benchmark_smart_discovery(query: str, iterations: int = 3) -> dict:
    """Benchmark smart discovery (in-memory)"""
    discovery = get_smart_discovery()
    times = []
    
    for i in range(iterations):
        start = time.time()
        matches = discovery.find_packages(query)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    return {
        "method": "smart_discovery",
        "query": query,
        "avg_ms": mean(times),
        "median_ms": median(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "result_count": len(matches),
        "times": times
    }


def print_results(results: list):
    """Print benchmark results in a nice table"""
    print("\n" + "="*70)
    print("🔬 REAL PERFORMANCE BENCHMARK RESULTS")
    print("="*70)
    
    # Group by query
    queries = {}
    for r in results:
        query = r["query"]
        if query not in queries:
            queries[query] = []
        queries[query].append(r)
    
    for query, methods in queries.items():
        print(f"\n📦 Query: '{query}'")
        print("-"*50)
        
        # Sort by median time
        methods.sort(key=lambda x: x["median_ms"])
        
        # Find baseline (slowest)
        baseline = max(methods, key=lambda x: x["median_ms"])
        
        for m in methods:
            speedup = baseline["median_ms"] / m["median_ms"] if m["median_ms"] > 0 else 999
            
            print(f"\n  {m['method'].upper()}:")
            print(f"    Median:  {m['median_ms']:>8.1f}ms")
            print(f"    Average: {m['avg_ms']:>8.1f}ms")
            print(f"    Min:     {m['min_ms']:>8.1f}ms")
            print(f"    Max:     {m['max_ms']:>8.1f}ms")
            print(f"    Results: {m['result_count']:>8} packages")
            
            if m != baseline:
                print(f"    Speedup: {speedup:>8.1f}x faster! ✨")


def main():
    """Run the complete benchmark suite"""
    
    print("🚀 Starting REAL Performance Benchmarks")
    print("This will measure actual performance, not fantasy numbers.\n")
    
    # Test queries
    queries = [
        "firefox",
        "vim", 
        "python",
        "text editor",  # Multi-word query
        "development",  # Broad query
    ]
    
    # Initialize index once
    print("📚 Initializing package index...")
    index = get_package_index()
    
    results = []
    
    for query in queries:
        print(f"\n⏱️  Benchmarking: '{query}'")
        
        # Benchmark each method
        print("  1. Testing subprocess (current method)...")
        subprocess_result = benchmark_subprocess(query, iterations=1)  # Only 1 iteration because it's slow
        results.append(subprocess_result)
        
        print("  2. Testing index (new method)...")
        index_result = benchmark_index(query, iterations=5, index=index)
        results.append(index_result)
        
        print("  3. Testing smart discovery...")
        smart_result = benchmark_smart_discovery(query, iterations=5)
        results.append(smart_result)
    
    # Print results
    print_results(results)
    
    # Calculate overall improvement
    print("\n" + "="*70)
    print("📊 OVERALL PERFORMANCE SUMMARY")
    print("="*70)
    
    subprocess_times = [r["median_ms"] for r in results if r["method"] == "subprocess"]
    index_times = [r["median_ms"] for r in results if r["method"] == "index"]
    
    if subprocess_times and index_times:
        avg_subprocess = mean(subprocess_times)
        avg_index = mean(index_times)
        overall_speedup = avg_subprocess / avg_index if avg_index > 0 else 999
        
        print(f"\nAverage subprocess time: {avg_subprocess:.1f}ms")
        print(f"Average index time:      {avg_index:.1f}ms")
        print(f"\n🎯 REAL SPEEDUP: {overall_speedup:.1f}x faster")
        print(f"   (Not 10,000x, but still significant!)")
        
        # Time saved per search
        time_saved = avg_subprocess - avg_index
        print(f"\n⏱️  Time saved per search: {time_saved:.1f}ms")
        print(f"   Over 100 searches:    {time_saved * 100 / 1000:.1f} seconds saved")
        print(f"   Over 1000 searches:   {time_saved * 1000 / 1000:.1f} seconds saved")
    
    print("\n✅ Benchmark complete!")
    print("\nNOTE: These are REAL measurements, not aspirational claims.")
    print("The index provides genuine performance improvements after initial build.")


if __name__ == "__main__":
    main()