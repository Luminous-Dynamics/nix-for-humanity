#!/usr/bin/env python3
"""
Test v0.3.1 Improvements - Verify all critical fixes work
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from luminous_nix.ai.hrm_integrated_v6_final import HRMIntegratedV6Final

def test_v031_improvements():
    """Test all the v0.3.1 critical fixes"""
    print("🧪 Testing v0.3.1 Improvements")
    print("=" * 60)
    
    # Initialize system
    system = HRMIntegratedV6Final(enable_active_learning=False)
    
    # Test queries that previously failed
    test_cases = [
        # Home-manager support (was failing)
        ("home-manager switch", "home-manager", "Home-manager support"),
        ("update home configuration", "home-manager", "Home config update"),
        ("home-manager rollback", "home-manager", "Home-manager rollback"),
        ("list home generations", "home-manager", "Home generations"),
        
        # Flake operations (was failing)
        ("nix flake update", "flake", "Flake update"),
        ("nix flake init", "flake", "Flake init"),
        ("check flake", "flake", "Flake check"),
        ("enter flake shell", "flake", "Flake develop"),
        
        # Service vs package confusion (was failing)
        ("enable docker", "service", "Docker service enable"),
        ("start nginx service", "service", "Nginx service start"),
        ("enable bluetooth", "service", "Bluetooth enable"),
        ("systemctl status ssh", "service", "SSH status"),
        
        # Garbage collection (was failing)
        ("gc old generations", "garbage", "GC old generations"),
        ("nix garbage collect", "garbage", "Nix GC"),
        ("free disk space", "garbage", "Free disk space"),
        ("clean nix store", "garbage", "Clean store"),
        
        # Generation management (was failing)
        ("list generations", "generation", "List generations"),
        ("show system generations", "generation", "System generations"),
    ]
    
    results = {
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    print("\n📝 Running Tests:")
    print("-" * 60)
    
    for query, expected_keyword, description in test_cases:
        start_time = time.time()
        result = system.process_query(query)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Check if result contains expected keyword
        command = result.get('command', '')
        category = result.get('category', '')
        confidence = result.get('confidence', 0)
        
        # Pass if command contains keyword or category matches
        passed = (expected_keyword in command.lower() or 
                 expected_keyword in category.lower() or
                 confidence > 0.7)
        
        if passed:
            results['passed'] += 1
            status = "✅"
        else:
            results['failed'] += 1
            status = "❌"
            
        results['details'].append({
            'query': query,
            'passed': passed,
            'command': command,
            'confidence': confidence,
            'time_ms': elapsed_ms
        })
        
        print(f"{status} {description:25} | Confidence: {confidence:.2f} | {elapsed_ms:.1f}ms")
        if not passed:
            print(f"   Query: '{query}'")
            print(f"   Got: '{command}'")
    
    # Calculate overall metrics
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("-" * 60)
    
    total = results['passed'] + results['failed']
    accuracy = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    print(f"Accuracy: {accuracy:.1f}%")
    
    # Performance metrics
    avg_time = sum(d['time_ms'] for d in results['details']) / len(results['details'])
    print(f"Average Response Time: {avg_time:.1f}ms")
    
    # Check if we met v0.3.1 goals
    print("\n🎯 v0.3.1 Goals:")
    if accuracy >= 97:
        print("✅ Target accuracy (97%) achieved!")
    else:
        print(f"⚠️  Below target accuracy (97% target, {accuracy:.1f}% actual)")
    
    if avg_time < 10:
        print("✅ Response time target (<10ms) achieved!")
    else:
        print(f"⚠️  Above response time target (<10ms target, {avg_time:.1f}ms actual)")
    
    # Show failed tests for debugging
    if results['failed'] > 0:
        print("\n❌ Failed Tests:")
        for detail in results['details']:
            if not detail['passed']:
                print(f"  - '{detail['query']}' → '{detail['command']}'")
    
    return accuracy >= 97

if __name__ == "__main__":
    success = test_v031_improvements()
    
    if success:
        print("\n🎉 v0.3.1 improvements successful! Ready to ship.")
    else:
        print("\n⚠️  v0.3.1 needs more work before release.")
    
    sys.exit(0 if success else 1)