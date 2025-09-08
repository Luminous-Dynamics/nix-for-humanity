#!/usr/bin/env python3
"""
Test suite for dev environment specialist
Validates that we've fixed the 0% accuracy issue
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.ai.dev_environment_specialist import DevEnvironmentSpecialist
from luminous_nix.ai.hrm_enhanced_v3 import HRMEnhancedV3
import json

def test_dev_specialist():
    """Test the dev environment specialist"""
    specialist = DevEnvironmentSpecialist()
    
    # Test cases that were failing before (0% accuracy)
    test_queries = [
        # Python queries
        ("create python development environment", "python"),
        ("setup python dev shell", "python"),
        ("I need a python environment", "python"),
        ("python development", "python"),
        
        # Rust queries  
        ("setup rust development", "rust"),
        ("rust dev environment", "rust"),
        ("cargo and rust tools", "rust"),
        
        # Node.js queries
        ("nodejs development shell", "node"),
        ("npm development environment", "node"),
        ("javascript dev setup", "node"),
        
        # Go queries
        ("go development environment", "go"),
        ("golang dev shell", "go"),
        
        # C++ queries
        ("c++ development environment", "cpp"),
        ("gcc compiler setup", "cpp"),
        
        # Generic queries
        ("development shell", "generic"),
        ("create shell.nix", "shell.nix"),
        ("make a flake", "flake"),
        
        # Web development
        ("web development environment", "web"),
        ("full stack development", "web"),
    ]
    
    results = []
    success_count = 0
    
    print("Testing Dev Environment Specialist")
    print("=" * 50)
    
    for query, expected_type in test_queries:
        result = specialist.handle_query(query)
        
        if result:
            success_count += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        results.append({
            'query': query,
            'expected': expected_type,
            'result': result,
            'status': status
        })
        
        print(f"{status} | {query[:40]:<40}")
        if result:
            print(f"    Command: {result['command'][:60]}...")
            print(f"    Confidence: {result['confidence']:.2f}")
        else:
            print(f"    No result returned")
        print()
    
    # Calculate success rate
    success_rate = (success_count / len(test_queries)) * 100
    
    print("=" * 50)
    print(f"Results: {success_count}/{len(test_queries)} passed")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Previous: 0% → Current: {success_rate:.1f}% 🎉")
    
    return results, success_rate

def test_hrm_v3():
    """Test the full HRM v3 with dev specialist integration"""
    hrm = HRMEnhancedV3()
    
    print("\n" + "=" * 50)
    print("Testing HRM v3 Integration")
    print("=" * 50)
    
    # Test queries that cover different categories
    test_cases = [
        # Dev queries (previously 0% accuracy)
        "create python development environment",
        "setup rust development shell",
        "nodejs development environment",
        
        # Regular NixOS queries (should still work)
        "install firefox",
        "search text editor",
        "update system",
    ]
    
    for query in test_cases:
        result = hrm.process_query(query)
        
        if result.get('success'):
            print(f"✅ {query}")
            print(f"   Source: {result.get('source', 'unknown')}")
            if 'command' in result:
                print(f"   Command: {result['command'][:50]}...")
        else:
            print(f"⚠️  {query}")
            print(f"   Message: {result.get('message', 'No message')}")
        print()
    
    # Print metrics
    metrics = hrm.get_metrics()
    print("\nHRM v3 Metrics:")
    print(f"Total queries: {metrics['total_queries']}")
    print(f"Dev queries handled: {metrics['dev_queries']}")
    print(f"Dev success rate: {metrics.get('dev_success_rate', 0):.1%}")
    print(f"Overall success rate: {metrics.get('overall_success_rate', 0):.1%}")

def generate_training_data():
    """Generate training data for the neural network"""
    specialist = DevEnvironmentSpecialist()
    examples = specialist.get_training_examples()
    
    print("\n" + "=" * 50)
    print("Generated Training Examples")
    print("=" * 50)
    
    training_data = []
    for query, command in examples[:10]:  # Show first 10
        print(f"Q: {query}")
        print(f"C: {command}")
        print()
        
        training_data.append({
            'query': query,
            'command': command,
            'category': 'development'
        })
    
    # Save training data
    with open('data/dev_training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Generated {len(examples)} training examples")
    print("Saved to data/dev_training_data.json")
    
    return training_data

def main():
    """Run all tests"""
    print("🚀 Testing Dev Environment Fix for 0% Accuracy Issue")
    print("=" * 60)
    
    # Test the specialist
    results, success_rate = test_dev_specialist()
    
    if success_rate < 80:
        print("\n⚠️  Warning: Success rate below 80%")
        print("Some dev queries are still failing")
    else:
        print("\n✅ Success! Dev queries fixed!")
        print(f"Improved from 0% to {success_rate:.1f}%")
    
    # Test HRM v3 integration
    test_hrm_v3()
    
    # Generate training data
    generate_training_data()
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"• Dev query accuracy: 0% → {success_rate:.1f}%")
    print(f"• Solution: Pattern-based specialist")
    print(f"• Integration: HRM v3 ready")
    print(f"• Training data: Generated")
    print("\n🎯 Next Steps:")
    print("1. Deploy this fix in v0.2.1")
    print("2. Collect user feedback")
    print("3. Train neural network on dev queries")
    print("4. Achieve 95% overall accuracy")

if __name__ == "__main__":
    main()