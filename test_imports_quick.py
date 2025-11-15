#!/usr/bin/env python3
"""Quick import test without external dependencies"""
import sys

sys.path.insert(0, "src")

print("Testing core module imports...")
print("=" * 60)

tests = [
    ("Core Executor", "luminous_nix.core.executor", "SafeExecutor"),
    ("Cache Service", "luminous_nix.services.cache", "CacheService"),
    ("Search Service", "luminous_nix.services.search", "SearchService"),
    ("Native API", "luminous_nix.core.native_nix_api", "NativeNixAPI"),
    ("JSON Optimizer", "luminous_nix.core.json_optimized_nix", "JSONOptimizedNix"),
]

passed = 0
failed = 0

for name, module, cls in tests:
    try:
        mod = __import__(module, fromlist=[cls])
        getattr(mod, cls)
        print(f"✅ {name:30} PASS")
        passed += 1
    except Exception as e:
        print(f"❌ {name:30} FAIL: {str(e)[:40]}")
        failed += 1

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print(f"Success rate: {passed}/{passed+failed} ({100*passed/(passed+failed):.0f}%)")
