#!/usr/bin/env python3
"""Quick performance test for native Python-Nix API."""

import time
import sys
import json
from pathlib import Path

print("🚀 Quick Performance Test - Native Python-Nix API\n")

# Add src to path
sys.path.insert(0, '/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src')

results = {}

# Test 1: Import and initialize native backend
print("1. Testing native backend import...")
start = time.perf_counter()
try:
    from nix_humanity.nix.native_backend import NativeNixBackend
    backend = NativeNixBackend()
    import_time = time.perf_counter() - start
    print(f"   ✅ Import successful: {import_time*1000:.2f}ms")
    results["import_native_backend"] = {"success": True, "time": import_time}
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    results["import_native_backend"] = {"success": False, "error": str(e)}
    sys.exit(1)

# Test 2: List generations (native)
print("\n2. Testing list generations (native)...")
start = time.perf_counter()
try:
    generations = backend._get_generations()
    native_time = time.perf_counter() - start
    print(f"   ✅ Native API: {native_time*1000:.2f}ms ({len(generations)} generations)")
    results["list_generations_native"] = {"success": True, "time": native_time, "count": len(generations)}
except Exception as e:
    print(f"   ❌ Native API failed: {e}")
    results["list_generations_native"] = {"success": False, "error": str(e)}

# Test 3: Get NixOS version (native)
print("\n3. Testing NixOS version check (native)...")
start = time.perf_counter()
try:
    version = backend._get_nixos_version()
    version_time = time.perf_counter() - start
    print(f"   ✅ Native API: {version_time*1000:.2f}ms (version: {version})")
    results["nixos_version_native"] = {"success": True, "time": version_time, "version": version}
except Exception as e:
    print(f"   ❌ Native API failed: {e}")
    results["nixos_version_native"] = {"success": False, "error": str(e)}

# Test 4: System info (native)
print("\n4. Testing system info (native)...")
start = time.perf_counter()
try:
    metrics = backend.get_metrics()
    metrics_time = time.perf_counter() - start
    print(f"   ✅ Native API: {metrics_time*1000:.2f}ms")
    results["system_info_native"] = {"success": True, "time": metrics_time}
except Exception as e:
    print(f"   ❌ Native API failed: {e}")
    results["system_info_native"] = {"success": False, "error": str(e)}

# Test 5: NLP processing speed
print("\n5. Testing NLP processing speed...")
try:
    from nix_humanity.ai.nlp import NLPEngine
    nlp = NLPEngine()
    
    test_phrases = [
        "install firefox",
        "search for text editors",
        "update my system"
    ]
    
    nlp_times = []
    for phrase in test_phrases:
        start = time.perf_counter()
        intent = nlp.process(phrase)
        nlp_time = time.perf_counter() - start
        nlp_times.append(nlp_time)
        print(f"   ✅ '{phrase}': {nlp_time*1000:.2f}ms")
    
    avg_nlp_time = sum(nlp_times) / len(nlp_times)
    results["nlp_processing"] = {"success": True, "avg_time": avg_nlp_time, "times": nlp_times}
except Exception as e:
    print(f"   ❌ NLP test failed: {e}")
    results["nlp_processing"] = {"success": False, "error": str(e)}

# Summary
print("\n📊 Performance Summary:")
print("="*50)

all_times = []
for test, data in results.items():
    if data.get("success") and "time" in data:
        all_times.append(data["time"])
        print(f"{test}: {data['time']*1000:.2f}ms")

if all_times:
    avg_time = sum(all_times) / len(all_times)
    print(f"\nAverage operation time: {avg_time*1000:.2f}ms")
    print(f"All operations < 100ms: {'YES' if all(t < 0.1 for t in all_times) else 'NO'}")

# Save results
Path('metrics').mkdir(exist_ok=True)
with open('metrics/quick_performance_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n✅ Results saved to metrics/quick_performance_test.json")

# Check if we validated the claims
if all_times and all(t < 0.1 for t in all_times):
    print("\n🎉 Performance claim validated: All native operations < 100ms!")