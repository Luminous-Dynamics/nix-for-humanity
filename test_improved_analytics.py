#!/usr/bin/env python3
"""
Test the improved analytics implementation to verify it solves database locking
"""

import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.luminous_nix.analytics.usage_analytics_improved import (
    ImprovedUsageAnalytics,
    SmartCacheOptimizerImproved,
    UsageEvent,
)


def test_concurrent_writes():
    """Test heavy concurrent writes without locking"""
    print("🔬 Testing Improved Analytics - Concurrent Writes")
    print("=" * 60)

    analytics = ImprovedUsageAnalytics()

    # Track timing and errors
    write_times = []
    errors = []

    def write_events(thread_id: int):
        """Simulate a thread writing many events"""
        local_times = []

        for i in range(50):
            event = UsageEvent(
                timestamp=time.time(),
                event_type="search",
                query=f"test_query_{thread_id}_{i}",
                result_count=10,
                response_time_ms=15.5,
                cache_hit=(i % 3 == 0),
                source="test",
                session_id=f"session_{thread_id}",
            )

            start = time.time()
            try:
                analytics.track_event(event)
                elapsed = (time.time() - start) * 1000
                local_times.append(elapsed)
            except Exception as e:
                errors.append(str(e))

            # Rapid fire writes
            time.sleep(0.001)

        return local_times

    print("Starting 20 concurrent threads, each writing 50 events...")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(write_events, i) for i in range(20)]

        for i, future in enumerate(as_completed(futures)):
            thread_times = future.result()
            write_times.extend(thread_times)
            avg_time = statistics.mean(thread_times) if thread_times else 0
            print(f"  Thread {i}: Avg write time: {avg_time:.2f}ms")

    print("\n📊 Results:")
    print(f"  Total writes: {len(write_times)}")
    print(f"  Errors: {len(errors)}")
    print(f"  Average write time: {statistics.mean(write_times):.2f}ms")
    print(f"  Max write time: {max(write_times):.2f}ms")

    # Check queue stats
    queue_stats = analytics.write_queue.get_stats()
    print("\n📈 Queue Statistics:")
    print(f"  Writes completed: {queue_stats['writes_completed']}")
    print(f"  Writes failed: {queue_stats['writes_failed']}")
    print(f"  Queue high water mark: {queue_stats['queue_high_water_mark']}")
    print(f"  Current queue size: {queue_stats['queue_size']}")

    # Wait for queue to flush
    time.sleep(1)

    analytics.close_session()

    # Success if no errors and fast writes
    success = len(errors) == 0 and statistics.mean(write_times) < 10
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: No locking issues detected")

    return success


def test_read_while_writing():
    """Test reading while heavy writes are happening"""
    print("\n🔄 Testing Read/Write Concurrency")
    print("=" * 60)

    analytics = ImprovedUsageAnalytics()

    # Mock cache for optimizer
    class MockCache:
        def __init__(self):
            self.l1_cache = {}

    cache = MockCache()
    optimizer = SmartCacheOptimizerImproved(analytics, cache)

    print("Starting optimizer and heavy writes...")

    read_times = []
    write_times = []
    errors = []

    def heavy_writer():
        """Continuously write events"""
        for i in range(200):
            event = UsageEvent(
                timestamp=time.time(),
                event_type="search",
                query=f"heavy_write_{i}",
                result_count=5,
                response_time_ms=10.0,
                cache_hit=False,
                source="writer",
            )

            start = time.time()
            try:
                analytics.track_event(event)
                write_times.append((time.time() - start) * 1000)
            except Exception as e:
                errors.append(f"Write error: {e}")

            time.sleep(0.005)

    def frequent_reader():
        """Continuously read analytics"""
        for i in range(50):
            start = time.time()
            try:
                # These reads should not block
                recommendations = analytics.get_smart_cache_recommendations()
                session_data = analytics.get_session_analytics()
                insights = analytics.get_insights()

                elapsed = (time.time() - start) * 1000
                read_times.append(elapsed)

                if i % 10 == 0:
                    print(
                        f"  Read {i}: {elapsed:.1f}ms (found {len(recommendations['packages_to_cache'])} recommendations)"
                    )

            except Exception as e:
                errors.append(f"Read error: {e}")

            time.sleep(0.02)

    # Start both in parallel
    writer_thread = threading.Thread(target=heavy_writer)
    reader_thread = threading.Thread(target=frequent_reader)

    writer_thread.start()
    reader_thread.start()

    writer_thread.join()
    reader_thread.join()

    print("\n📊 Results:")
    print(f"  Writes: {len(write_times)} (avg: {statistics.mean(write_times):.2f}ms)")
    print(f"  Reads: {len(read_times)} (avg: {statistics.mean(read_times):.2f}ms)")
    print(f"  Errors: {len(errors)}")

    if errors:
        print("\nFirst 5 errors:")
        for error in errors[:5]:
            print(f"  - {error}")

    optimizer.shutdown()
    analytics.close_session()

    # Success if reads are fast and no errors
    success = len(errors) == 0 and statistics.mean(read_times) < 100
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Reads don't block on writes")

    return success


def test_optimizer_doesnt_lock():
    """Test that background optimizer doesn't cause locks"""
    print("\n⚙️ Testing Background Optimizer")
    print("=" * 60)

    analytics = ImprovedUsageAnalytics()

    # Populate some data first
    for i in range(100):
        event = UsageEvent(
            timestamp=time.time(),
            event_type="search",
            query="firefox" if i % 10 == 0 else f"query_{i}",
            result_count=5,
            response_time_ms=20.0,
            cache_hit=(i % 5 == 0),
            source="test",
        )
        analytics.track_event(event)

    # Create optimizer
    class MockCache:
        def __init__(self):
            self.l1_cache = {}

    cache = MockCache()
    optimizer = SmartCacheOptimizerImproved(analytics, cache)

    # Force an optimization
    optimizer.optimization_interval = 0.1  # Fast for testing

    print("Optimizer running, tracking events...")

    # Track events while optimizer runs
    times = []
    errors = []

    for i in range(100):
        event = UsageEvent(
            timestamp=time.time(),
            event_type="search",
            query=f"concurrent_{i}",
            result_count=3,
            response_time_ms=15.0,
            cache_hit=False,
            source="test",
        )

        start = time.time()
        try:
            analytics.track_event(event)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        except Exception as e:
            errors.append(str(e))

        time.sleep(0.01)

    # Check optimizer status
    status = optimizer.get_status()
    print("\nOptimizer Status:")
    print(f"  Running: {status['running']}")
    print(
        f"  Time since last optimization: {status['time_since_last']:.1f}s"
        if status["time_since_last"]
        else "  No optimization yet"
    )

    print("\n📊 Event Tracking Results:")
    print(f"  Events tracked: {len(times)}")
    print(f"  Average time: {statistics.mean(times):.2f}ms")
    print(f"  Max time: {max(times):.2f}ms")
    print(f"  Errors: {len(errors)}")

    optimizer.shutdown()
    analytics.close_session()

    success = len(errors) == 0 and statistics.mean(times) < 10
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Optimizer doesn't cause locks")

    return success


def main():
    """Run all improved analytics tests"""
    print("🚀 Testing Improved Analytics Implementation")
    print("=" * 70)
    print("Verifying that database locking issues are solved\n")

    tests = [
        ("Concurrent Writes", test_concurrent_writes),
        ("Read/Write Concurrency", test_read_while_writing),
        ("Background Optimizer", test_optimizer_doesnt_lock),
    ]

    results = {}

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")

    all_passed = all(results.values())

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Database locking issues are SOLVED!")
        print("\nKey improvements:")
        print("  • Write queue prevents lock contention")
        print("  • Separate read connections for queries")
        print("  • Non-blocking event tracking")
        print("  • Background optimizer doesn't interfere")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Further investigation needed")

    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
