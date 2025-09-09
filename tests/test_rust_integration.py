#!/usr/bin/env python3
"""Test Rust module integration with PyO3."""

import sys
import time
import json
from pathlib import Path

# Add Rust module to path when built
rust_module_path = Path(__file__).parent.parent / "rust/target/release"
sys.path.insert(0, str(rust_module_path))

def test_rust_import():
    """Test that we can import the Rust module."""
    try:
        import luminous_nix_core
        print("✅ Rust module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Rust module: {e}")
        print("  Run: cd rust && cargo build --release")
        return False

def test_fast_searcher():
    """Test the FastSearcher class."""
    try:
        from luminous_nix_core import FastSearcher
        
        searcher = FastSearcher()
        print("✅ FastSearcher created")
        
        # Load test packages
        test_packages = json.dumps({
            "firefox": {
                "pname": "firefox",
                "version": "123.0",
                "description": "Mozilla Firefox web browser"
            },
            "firefox-esr": {
                "pname": "firefox-esr",
                "version": "115.0",
                "description": "Firefox Extended Support Release"
            },
            "chromium": {
                "pname": "chromium",
                "version": "122.0",
                "description": "Open source web browser"
            }
        })
        
        count = searcher.load_packages(test_packages)
        print(f"✅ Loaded {count} packages")
        
        # Test search
        start = time.time()
        results = searcher.search("firefox", 10)
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ Search completed in {elapsed:.2f}ms")
        print(f"   Found {len(results)} results")
        
        # Test fuzzy search
        results = searcher.search("firfox", 10)  # Typo
        if results:
            print(f"✅ Fuzzy search handled typo: found {results[0]['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastSearcher test failed: {e}")
        return False

def test_smart_cache():
    """Test the SmartCache class."""
    try:
        from luminous_nix_core import SmartCache
        
        cache = SmartCache(1024 * 1024, 100)  # 1MB max, 100 byte compression threshold
        print("✅ SmartCache created")
        
        # Test set/get
        test_data = b"Hello, Luminous Nix!"
        cache.set("test_key", test_data)
        
        retrieved = cache.get("test_key")
        if retrieved == test_data:
            print("✅ Cache set/get working")
        else:
            print("❌ Cache data mismatch")
            return False
        
        # Test compression for large data
        large_data = b"x" * 1000
        cache.set("large_key", large_data)
        
        stats = cache.stats()
        print(f"✅ Cache stats: {stats['compressed']} compressed entries")
        
        return True
        
    except Exception as e:
        print(f"❌ SmartCache test failed: {e}")
        return False

def test_json_optimizer():
    """Test the JsonOptimizer class."""
    try:
        from luminous_nix_core import JsonOptimizer
        
        optimizer = JsonOptimizer()
        print("✅ JsonOptimizer created")
        
        # Test JSON parsing
        test_json = '{"name": "firefox", "version": "123.0"}'
        optimizer.parse(test_json)
        
        # Test field extraction
        result = optimizer.get_field(["name"])
        if result == '"firefox"':
            print("✅ JSON field extraction working")
        else:
            print(f"❌ Expected 'firefox', got {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ JsonOptimizer test failed: {e}")
        return False

def test_pattern_matcher():
    """Test the PatternMatcher class."""
    try:
        from luminous_nix_core import PatternMatcher
        
        matcher = PatternMatcher()
        print("✅ PatternMatcher created")
        
        # Add patterns
        matcher.add_pattern(r"install (.+)", "install")
        matcher.add_pattern(r"search for (.+)", "search")
        
        # Test matching
        intent = matcher.match_intent("install firefox")
        if intent == "install":
            print("✅ Pattern matching working")
        else:
            print(f"❌ Expected 'install', got {intent}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ PatternMatcher test failed: {e}")
        return False

def test_fuzzy_search_function():
    """Test the standalone fuzzy_search function."""
    try:
        from luminous_nix_core import fuzzy_search
        
        candidates = ["firefox", "firefox-esr", "chromium", "chrome"]
        
        # Test exact match
        results = fuzzy_search("firefox", candidates, 3)
        if results and results[0][0] == "firefox":
            print("✅ Fuzzy search function working")
        else:
            print(f"❌ Unexpected fuzzy search results: {results}")
            return False
        
        # Test typo
        results = fuzzy_search("firfox", candidates, 3)
        if results and "firefox" in [r[0] for r in results]:
            print("✅ Fuzzy search handles typos")
        
        return True
        
    except Exception as e:
        print(f"❌ Fuzzy search function test failed: {e}")
        return False

def test_performance():
    """Benchmark Rust vs Python performance."""
    try:
        from luminous_nix_core import fuzzy_search
        import random
        import string
        
        # Generate test data
        candidates = []
        for _ in range(1000):
            name = ''.join(random.choices(string.ascii_lowercase, k=10))
            candidates.append(f"package-{name}")
        
        # Benchmark Rust fuzzy search
        start = time.time()
        for _ in range(100):
            fuzzy_search("package-test", candidates, 10)
        rust_time = time.time() - start
        
        print(f"✅ Rust: 100 searches in {rust_time*1000:.2f}ms")
        print(f"   Average: {rust_time*10:.3f}ms per search")
        
        # Compare with simple Python
        def python_search(query, candidates, limit):
            results = []
            for c in candidates:
                if query in c:
                    results.append(c)
                    if len(results) >= limit:
                        break
            return results
        
        start = time.time()
        for _ in range(100):
            python_search("package-test", candidates, 10)
        python_time = time.time() - start
        
        print(f"✅ Python: 100 searches in {python_time*1000:.2f}ms")
        print(f"   Speedup: {python_time/rust_time:.1f}x faster with Rust")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("\n🧪 Testing Rust Module Integration\n")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_rust_import),
        ("FastSearcher", test_fast_searcher),
        ("SmartCache", test_smart_cache),
        ("JsonOptimizer", test_json_optimizer),
        ("PatternMatcher", test_pattern_matcher),
        ("Fuzzy Search", test_fuzzy_search_function),
        ("Performance", test_performance),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n📝 {name}:")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Rust integration working perfectly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())