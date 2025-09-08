#!/usr/bin/env python3
"""
Beta Testing Framework for v0.2.0
Help us validate the enhanced HRM
"""

import time
import json
from pathlib import Path

# Test queries covering all categories
TEST_QUERIES = [
    # Installation
    ("install firefox", "install"),
    ("add vim to my system", "install"),
    ("how do I get docker", "install"),
    
    # Configuration
    ("enable bluetooth", "configure"),
    ("setup nginx server", "configure"),
    ("configure postgresql", "configure"),
    
    # Search
    ("search for text editors", "search"),
    ("find python packages", "search"),
    ("what databases are available", "search"),
    
    # Errors
    ("error collision between packages", "error"),
    ("attribute not found", "error"),
    
    # Updates
    ("update nixos", "update"),
    ("upgrade system", "update"),
    
    # Development
    ("create python shell", "shell"),
    ("rust development environment", "shell"),
]

def run_beta_test():
    """Run comprehensive beta test"""
    
    print("🧪 Luminous Nix v0.2.0-beta Test Suite")
    print("=" * 60)
    
    from scripts.integrate_hrm_complete import IntegratedHRM
    
    # Initialize system
    print("\n🔧 Initializing system...")
    hrm = IntegratedHRM()
    
    results = []
    
    print("\n📊 Running test queries:")
    print("-" * 60)
    
    for query, expected_category in TEST_QUERIES:
        start = time.perf_counter()
        result = hrm.predict(query)
        elapsed = (time.perf_counter() - start) * 1000
        
        # Check if category matches
        correct = result['strategy'] == expected_category
        
        print(f"\n✓ Query: '{query}'")
        print(f"  Expected: {expected_category}")
        print(f"  Got: {result['strategy']}")
        print(f"  Correct: {'✅' if correct else '❌'}")
        print(f"  Confidence: {result.get('confidence', 0):.1%}")
        print(f"  Latency: {elapsed:.2f}ms")
        print(f"  Cached: {'Yes' if result.get('cached') else 'No'}")
        
        results.append({
            'query': query,
            'expected': expected_category,
            'predicted': result['strategy'],
            'correct': correct,
            'confidence': result.get('confidence', 0),
            'latency_ms': elapsed,
            'cached': result.get('cached', False)
        })
    
    # Calculate statistics
    correct_count = sum(1 for r in results if r['correct'])
    accuracy = correct_count / len(results)
    avg_latency = sum(r['latency_ms'] for r in results) / len(results)
    cache_hits = sum(1 for r in results if r['cached'])
    cache_rate = cache_hits / len(results)
    
    print("\n" + "=" * 60)
    print("📈 Test Results Summary:")
    print(f"  Accuracy: {accuracy:.1%} ({correct_count}/{len(results)})")
    print(f"  Avg Latency: {avg_latency:.2f}ms")
    print(f"  Cache Hit Rate: {cache_rate:.1%}")
    
    # Save results
    with open('beta_test_results.json', 'w') as f:
        json.dump({
            'version': '0.2.0-beta',
            'timestamp': time.time(),
            'results': results,
            'summary': {
                'accuracy': accuracy,
                'avg_latency_ms': avg_latency,
                'cache_hit_rate': cache_rate
            }
        }, f, indent=2)
    
    print("\n✅ Results saved to beta_test_results.json")
    
    return accuracy >= 0.5  # Pass if >50% accuracy

if __name__ == "__main__":
    success = run_beta_test()
    exit(0 if success else 1)
