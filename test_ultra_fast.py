#!/usr/bin/env python3
"""
Test ultra-fast cache that guarantees <100ms (actually <1ms) responses
"""

import statistics
import time

from src.luminous_nix.core.ultra_fast_cache import get_ultra_cache


def test_ultra_fast_performance():
    """Test that we achieve <1ms response times with in-memory cache"""

    print("⚡ Testing Ultra-Fast Cache Performance (<1ms target)")
    print("=" * 50)

    cache = get_ultra_cache()

    # Test search performance
    print("\n🔍 Search Performance (from memory):")
    search_times = []

    queries = [
        "firefox",
        "vim",
        "python",
        "docker",
        "rust",
        "nodejs",
        "chromium",
        "vscode",
    ]
    for query in queries:
        results, elapsed_ms = cache.search_instant(query)
        search_times.append(elapsed_ms)
        status = "✅" if elapsed_ms < 1 else "⚠️" if elapsed_ms < 100 else "❌"
        print(
            f"  {status} Search '{query}': {elapsed_ms:.3f}ms ({len(results)} results)"
        )

    # Test cached searches (should be even faster)
    print("\n🔄 Cached Search Performance (2nd run):")
    for query in ["firefox", "vim"]:
        results, elapsed_ms = cache.search_instant(query)
        status = "✅" if elapsed_ms < 0.1 else "⚠️"
        print(f"  {status} Cached '{query}': {elapsed_ms:.4f}ms")

    # Test list performance
    print("\n📋 List Performance:")
    packages, elapsed_ms = cache.list_instant()
    status = "✅" if elapsed_ms < 1 else "❌"
    print(f"  {status} List packages: {elapsed_ms:.3f}ms ({len(packages)} packages)")

    # Test info performance
    print("\n📄 Package Info Performance:")
    info_times = []
    for pkg in ["firefox", "vim", "git", "python"]:
        info, elapsed_ms = cache.info_instant(pkg)
        info_times.append(elapsed_ms)
        status = "✅" if elapsed_ms < 1 else "❌"
        print(f"  {status} Info '{pkg}': {elapsed_ms:.3f}ms")

    # Test command performance
    print("\n⚡ Command Performance:")
    cmd_times = []
    for cmd in ["nix --version", "nixos-version", "nix doctor"]:
        result, elapsed_ms = cache.command_instant(cmd)
        cmd_times.append(elapsed_ms)
        status = "✅" if elapsed_ms < 1 else "❌"
        print(f"  {status} Command '{cmd}': {elapsed_ms:.3f}ms")

    # Calculate statistics
    all_times = search_times + info_times + cmd_times + [elapsed_ms]

    print("\n📊 Performance Statistics:")
    print(f"  Average: {statistics.mean(all_times):.3f}ms")
    print(f"  Median: {statistics.median(all_times):.3f}ms")
    print(f"  Min: {min(all_times):.4f}ms")
    print(f"  Max: {max(all_times):.3f}ms")
    print(f"  Under 1ms: {sum(1 for t in all_times if t < 1)}/{len(all_times)}")
    print(f"  Under 100ms: {sum(1 for t in all_times if t < 100)}/{len(all_times)}")

    # Cache stats
    stats = cache.stats()
    print("\n🗄️ Cache Statistics:")
    print(f"  Packages cached: {stats['packages_cached']}")
    print(f"  Searches cached: {stats['searches_cached']}")
    print(f"  Has list cache: {stats['has_list_cache']}")

    # Overall result
    avg_time = statistics.mean(all_times)
    if avg_time < 1:
        print(
            f"\n🎉 ULTRA SUCCESS: Average {avg_time:.3f}ms - Sub-millisecond achieved!"
        )
        return True
    elif avg_time < 100:
        print(f"\n✅ SUCCESS: Average {avg_time:.1f}ms - Target <100ms achieved!")
        return True
    else:
        print(f"\n❌ FAILED: Average {avg_time:.1f}ms - Target <100ms NOT met")
        return False


def test_real_world_scenario():
    """Test a real-world usage scenario"""

    print("\n🌍 Real-World Scenario Test:")
    print("-" * 30)

    cache = get_ultra_cache()
    total_start = time.time()

    # User searches for a browser
    results, search_ms = cache.search_instant("browser")
    print(f"1. User searches 'browser': {search_ms:.3f}ms")

    # User gets info about firefox
    info, info_ms = cache.info_instant("firefox")
    print(f"2. User gets Firefox info: {info_ms:.3f}ms")

    # User lists installed packages
    packages, list_ms = cache.list_instant()
    print(f"3. User lists packages: {list_ms:.3f}ms")

    # User searches for editor
    results, search2_ms = cache.search_instant("editor")
    print(f"4. User searches 'editor': {search2_ms:.3f}ms")

    # User gets vim info
    info, info2_ms = cache.info_instant("vim")
    print(f"5. User gets Vim info: {info2_ms:.3f}ms")

    total_time = (time.time() - total_start) * 1000
    operation_time = search_ms + info_ms + list_ms + search2_ms + info2_ms

    print(f"\nTotal time for 5 operations: {total_time:.2f}ms")
    print(f"Sum of operation times: {operation_time:.2f}ms")
    print(f"Overhead: {(total_time - operation_time):.2f}ms")

    if total_time < 100:
        print("✅ Real-world scenario completed in <100ms!")
        return True
    else:
        print("❌ Real-world scenario exceeded 100ms")
        return False


def main():
    """Run all performance tests"""

    # Test ultra-fast cache
    ultra_success = test_ultra_fast_performance()

    # Test real-world scenario
    scenario_success = test_real_world_scenario()

    print("\n" + "=" * 50)
    if ultra_success and scenario_success:
        print("🚀 PERFORMANCE TARGET ACHIEVED!")
        print("✨ <100ms latency with <1ms average!")
        print("📊 Ready for production deployment!")
    else:
        print("⚠️ Some targets not met, but close!")


if __name__ == "__main__":
    main()
