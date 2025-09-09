#!/usr/bin/env python3
"""
Investigate database locking issues
Find out exactly why and when the database gets locked
"""

import sqlite3
import threading
import time
from pathlib import Path
import os


def test_basic_wal_mode():
    """Test if WAL mode is actually being enabled"""
    print("🔍 Testing WAL Mode Configuration")
    print("=" * 60)
    
    db_path = Path("/tmp/test_wal.db")
    if db_path.exists():
        db_path.unlink()
    
    # Create connection with WAL mode
    conn = sqlite3.connect(str(db_path))
    
    # Check journal mode BEFORE setting
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode")
    mode_before = cursor.fetchone()[0]
    print(f"Journal mode before: {mode_before}")
    
    # Set WAL mode
    cursor.execute("PRAGMA journal_mode=WAL")
    mode_set = cursor.fetchone()[0]
    print(f"Journal mode after setting: {mode_set}")
    
    # Verify it persisted
    cursor.execute("PRAGMA journal_mode")
    mode_after = cursor.fetchone()[0]
    print(f"Journal mode verification: {mode_after}")
    
    # Check if WAL files were created
    wal_file = Path(f"{db_path}-wal")
    shm_file = Path(f"{db_path}-shm")
    
    print(f"\nWAL file exists: {wal_file.exists()}")
    print(f"SHM file exists: {shm_file.exists()}")
    
    conn.close()
    
    # Test with new connection
    print("\nTesting persistence with new connection:")
    conn2 = sqlite3.connect(str(db_path))
    cursor2 = conn2.cursor()
    cursor2.execute("PRAGMA journal_mode")
    mode_new_conn = cursor2.fetchone()[0]
    print(f"Journal mode in new connection: {mode_new_conn}")
    conn2.close()
    
    return mode_after == "wal"


def test_concurrent_connections():
    """Test concurrent connections with different configurations"""
    print("\n🔄 Testing Concurrent Connections")
    print("=" * 60)
    
    db_path = Path("/tmp/test_concurrent.db")
    if db_path.exists():
        db_path.unlink()
    
    # Create initial connection and setup
    conn1 = sqlite3.connect(str(db_path), check_same_thread=False)
    conn1.execute("PRAGMA journal_mode=WAL")
    conn1.execute("PRAGMA synchronous=NORMAL")
    conn1.execute("PRAGMA busy_timeout=100")
    
    # Create table
    conn1.execute("""
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY,
            value TEXT
        )
    """)
    conn1.commit()
    
    errors = []
    success_count = 0
    
    def writer_thread(thread_id):
        """Thread that writes to database"""
        nonlocal errors, success_count
        
        try:
            # Each thread gets its own connection
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=100")
            
            for i in range(10):
                try:
                    conn.execute("INSERT INTO test (value) VALUES (?)", 
                                (f"thread_{thread_id}_value_{i}",))
                    conn.commit()
                    success_count += 1
                except sqlite3.OperationalError as e:
                    errors.append(f"Thread {thread_id}: {e}")
                time.sleep(0.01)
            
            conn.close()
        except Exception as e:
            errors.append(f"Thread {thread_id} failed: {e}")
    
    # Start multiple writer threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=writer_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    print(f"Successful writes: {success_count}/50")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nFirst 5 errors:")
        for error in errors[:5]:
            print(f"  - {error}")
    
    conn1.close()
    return len(errors) == 0


def test_check_same_thread():
    """Test the impact of check_same_thread parameter"""
    print("\n🧵 Testing check_same_thread Parameter")
    print("=" * 60)
    
    db_path = Path("/tmp/test_thread.db")
    if db_path.exists():
        db_path.unlink()
    
    # Test 1: check_same_thread=False (what we're using)
    print("Test 1: check_same_thread=False")
    conn1 = sqlite3.connect(str(db_path), check_same_thread=False)
    conn1.execute("CREATE TABLE IF NOT EXISTS test1 (id INTEGER)")
    
    def other_thread_false():
        try:
            conn1.execute("INSERT INTO test1 (id) VALUES (1)")
            conn1.commit()
            return "Success"
        except Exception as e:
            return f"Error: {e}"
    
    t1 = threading.Thread(target=lambda: print(f"  Result: {other_thread_false()}"))
    t1.start()
    t1.join()
    conn1.close()
    
    # Test 2: check_same_thread=True (SQLite default)
    print("\nTest 2: check_same_thread=True")
    conn2 = sqlite3.connect(str(db_path), check_same_thread=True)
    
    def other_thread_true():
        try:
            conn2.execute("INSERT INTO test1 (id) VALUES (2)")
            conn2.commit()
            return "Success"
        except Exception as e:
            return f"Error: {e}"
    
    t2 = threading.Thread(target=lambda: print(f"  Result: {other_thread_true()}"))
    t2.start()
    t2.join()
    conn2.close()


def test_our_actual_setup():
    """Test our actual UsageAnalytics setup"""
    print("\n🔬 Testing Our Actual Setup")
    print("=" * 60)
    
    from src.luminous_nix.analytics.usage_analytics import UsageAnalytics, UsageEvent
    
    # Create instance
    analytics = UsageAnalytics()
    
    # Check what journal mode we actually got
    cursor = analytics.conn.cursor()
    cursor.execute("PRAGMA journal_mode")
    journal_mode = cursor.fetchone()[0]
    print(f"Actual journal mode: {journal_mode}")
    
    cursor.execute("PRAGMA synchronous")
    sync_mode = cursor.fetchone()[0]
    print(f"Synchronous mode: {sync_mode}")
    
    cursor.execute("PRAGMA busy_timeout")
    timeout = cursor.fetchone()[0]
    print(f"Busy timeout: {timeout}ms")
    
    # Test concurrent writes
    print("\nTesting concurrent event tracking:")
    
    errors = []
    success = 0
    
    def track_events(thread_id):
        nonlocal errors, success
        
        for i in range(20):
            event = UsageEvent(
                timestamp=time.time(),
                event_type="test",
                query=f"test_query_{thread_id}_{i}",
                result_count=1,
                response_time_ms=10.0,
                cache_hit=False,
                source="test",
                session_id=f"test_{thread_id}"
            )
            
            try:
                analytics.track_event(event)
                success += 1
            except Exception as e:
                errors.append(str(e))
            
            time.sleep(0.001)  # Very fast writes
    
    # Create multiple threads writing simultaneously
    threads = []
    for i in range(10):
        t = threading.Thread(target=track_events, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    print(f"Successful events: {success}/200")
    print(f"Errors: {len(errors)}")
    
    if errors:
        # Count unique error types
        unique_errors = {}
        for error in errors:
            if "locked" in error:
                key = "Database locked"
            else:
                key = error[:50]
            unique_errors[key] = unique_errors.get(key, 0) + 1
        
        print("\nError breakdown:")
        for error_type, count in unique_errors.items():
            print(f"  - {error_type}: {count} times")
    
    analytics.close_session()
    
    return len(errors) == 0


def test_background_optimizer():
    """Test if the background optimizer is causing locks"""
    print("\n⚙️ Testing Background Optimizer Impact")
    print("=" * 60)
    
    from src.luminous_nix.analytics.usage_analytics import UsageAnalytics, UsageEvent, SmartCacheOptimizer
    
    # Create analytics with optimizer
    analytics = UsageAnalytics()
    
    # Create a mock cache
    class MockCache:
        def __init__(self):
            self.l1_cache = {}
            
    cache = MockCache()
    optimizer = SmartCacheOptimizer(analytics, cache)
    
    print("Background optimizer started...")
    
    # Track events while optimizer might be running
    errors = []
    for i in range(50):
        event = UsageEvent(
            timestamp=time.time(),
            event_type="test",
            query=f"optimizer_test_{i}",
            result_count=1,
            response_time_ms=10.0,
            cache_hit=False,
            source="test"
        )
        
        try:
            analytics.track_event(event)
        except Exception as e:
            if "locked" in str(e):
                errors.append(e)
        
        time.sleep(0.01)
    
    print(f"Events tracked: {50 - len(errors)}/50")
    print(f"Lock errors: {len(errors)}")
    
    # Check if optimizer is accessing the database
    print("\nForcing optimizer to get recommendations...")
    
    try:
        recommendations = analytics.get_smart_cache_recommendations()
        print(f"Got recommendations successfully")
        print(f"  - Packages to cache: {len(recommendations['packages_to_cache'])}")
        print(f"  - Common patterns: {len(recommendations['common_patterns'])}")
    except Exception as e:
        print(f"Error getting recommendations: {e}")
    
    optimizer.shutdown()
    analytics.close_session()
    
    return len(errors) == 0


def main():
    """Run all database locking tests"""
    print("🔍 Database Locking Investigation")
    print("=" * 70)
    print("Finding the root cause of database locking issues\n")
    
    tests = [
        ("WAL Mode Configuration", test_basic_wal_mode),
        ("Concurrent Connections", test_concurrent_connections),
        ("Thread Safety Settings", test_check_same_thread),
        ("Our Actual Setup", test_our_actual_setup),
        ("Background Optimizer", test_background_optimizer)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            print(f"\n{'='*70}")
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 INVESTIGATION SUMMARY")
    print("=" * 70)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ ISSUE FOUND"
        print(f"  {status}: {name}")
    
    print("\n🔎 Root Cause Analysis:")
    
    if not results.get("WAL Mode Configuration", False):
        print("  • WAL mode is not being properly enabled")
    
    if not results.get("Concurrent Connections", False):
        print("  • Concurrent writes are failing even with WAL mode")
    
    if not results.get("Our Actual Setup", False):
        print("  • Our UsageAnalytics class has concurrency issues")
        print("    - Multiple threads are competing for database writes")
        print("    - The 100ms timeout is too short for heavy concurrency")
        print("    - We need a write queue or connection pool")
    
    if not results.get("Background Optimizer", False):
        print("  • Background optimizer is competing for database access")
        print("    - It's running get_smart_cache_recommendations() frequently")
        print("    - This holds locks while querying")
    
    print("\n💡 Recommended Solutions:")
    print("  1. Use a write queue to serialize database writes")
    print("  2. Use separate read-only connections for queries")
    print("  3. Increase busy_timeout to 1000ms (1 second)")
    print("  4. Use connection pooling for better concurrency")
    print("  5. Move analytics to a separate thread with queue")


if __name__ == "__main__":
    main()