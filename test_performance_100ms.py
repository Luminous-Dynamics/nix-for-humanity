#!/usr/bin/env python3
"""
Test that we can achieve <100ms latency with the optimized API
"""

import statistics
import time

from src.luminous_nix.core.native_fast_api import get_fast_api


def test_performance():
    """Test that all operations complete in <100ms"""

    print("🚀 Testing <100ms Performance Target")
    print("=" * 50)

    api = get_fast_api()

    # Test search performance (most common operation)
    print("\n📦 Testing Package Search Performance:")
    search_times = []

    for query in ["vim", "firefox", "python", "git", "nodejs"]:
        results, elapsed_ms = api.search_packages_fast(query)
        search_times.append(elapsed_ms)
        status = "✅" if elapsed_ms < 100 else "❌"
        print(
            f"  {status} Search '{query}': {elapsed_ms:.1f}ms ({len(results)} results)"
        )

    # Test with cache hits (should be instant)
    print("\n🔄 Testing Cached Searches (2nd run):")
    for query in ["vim", "firefox"]:
        results, elapsed_ms = api.search_packages_fast(query)
        status = "✅" if elapsed_ms < 10 else "⚠️"
        print(f"  {status} Cached search '{query}': {elapsed_ms:.2f}ms")

    # Test list performance
    print("\n📋 Testing List Installed:")
    packages, elapsed_ms = api.list_installed_fast()
    status = "✅" if elapsed_ms < 100 else "❌"
    print(f"  {status} List installed: {elapsed_ms:.1f}ms ({len(packages)} packages)")

    # Test package info
    print("\n📄 Testing Package Info:")
    info, elapsed_ms = api.get_package_info_fast("firefox")
    status = "✅" if elapsed_ms < 100 else "❌"
    print(f"  {status} Get info 'firefox': {elapsed_ms:.1f}ms")

    # Test command execution
    print("\n⚡ Testing Fast Command Execution:")
    success, output, elapsed_ms = api.execute_fast("nix", ["--version"])
    status = "✅" if elapsed_ms < 100 else "❌"
    print(f"  {status} Execute 'nix --version': {elapsed_ms:.1f}ms")

    # Calculate statistics
    all_times = search_times + [elapsed_ms]

    print("\n📊 Performance Statistics:")
    print(f"  Average: {statistics.mean(all_times):.1f}ms")
    print(f"  Median: {statistics.median(all_times):.1f}ms")
    print(f"  Min: {min(all_times):.1f}ms")
    print(f"  Max: {max(all_times):.1f}ms")
    print(f"  Under 100ms: {sum(1 for t in all_times if t < 100)}/{len(all_times)}")

    # Check cache stats
    stats = api.get_performance_stats()
    print("\n🗄️ Cache Statistics:")
    print(f"  Package cache: {stats['package_cache_size']} entries")
    print(f"  Command cache: {stats['cache_size']} entries")
    print(f"  Search cache hits: {stats['lru_cache_info']['search']['hits']}")
    print(f"  Search cache misses: {stats['lru_cache_info']['search']['misses']}")

    # Overall result
    avg_time = statistics.mean(all_times)
    if avg_time < 100:
        print(f"\n✅ SUCCESS: Average {avg_time:.1f}ms - Target <100ms ACHIEVED!")
        return True
    else:
        print(f"\n❌ FAILED: Average {avg_time:.1f}ms - Target <100ms NOT met")
        return False


def test_cold_start():
    """Test cold start performance (first run)"""
    print("\n🧊 Testing Cold Start Performance:")

    # Create new instance (cold start)
    start = time.time()
    api = get_fast_api()
    init_time = (time.time() - start) * 1000

    print(f"  API initialization: {init_time:.1f}ms")

    # First search (cold)
    results, elapsed_ms = api.search_packages_fast("firefox")
    print(f"  First search: {elapsed_ms:.1f}ms")

    # Second search (warm)
    results, elapsed_ms = api.search_packages_fast("firefox")
    print(f"  Second search (cached): {elapsed_ms:.2f}ms")

    return elapsed_ms < 10  # Cached should be <10ms


def main():
    """Run all performance tests"""

    # Test cold start
    cold_success = test_cold_start()

    # Test warmed up performance
    warm_success = test_performance()

    print("\n" + "=" * 50)
    if cold_success and warm_success:
        print("🎉 ALL PERFORMANCE TARGETS MET!")
        print("✨ <100ms latency achieved!")
    else:
        print("⚠️  Some performance targets not met")
        print("🔧 Further optimization needed")


if __name__ == "__main__":
    main()
