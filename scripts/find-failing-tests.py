#!/usr/bin/env python3
"""Find which specific tests are failing in the natural language suite."""

import subprocess
import json
import re
from pathlib import Path

def find_failing_tests():
    """Analyze test results to find specific failures."""
    
    print("🔍 Analyzing Test Failures for Natural Language Processing\n")
    
    # First check the v1 integration test results we already have
    results_file = Path('config/v1_integration_test_results.json')
    if results_file.exists():
        with open(results_file) as f:
            results = json.load(f)
        
        print("📊 V1 Integration Test Results:")
        print(f"Natural Language: {results['features']['natural_language']['tests_passed']}")
        print(f"Smart Discovery: {results['features']['smart_discovery']['tests_passed']}")
        print(f"Error Handling: {results['features']['error_handling']['educational_errors']}")
        print(f"Flake Support: {results['features']['flake_support']['tests_passed']}")
    
    # Look for test files with natural language tests
    print("\n🔍 Searching for Natural Language Test Files...")
    
    test_files = [
        'tests/v1.0/test_v1_core_features.py',
        'tests/test_v1_basic.py',
        'tests/test_v1_final_integration.py',
        'tests/unit/test_nlp_comprehensive.py',
        'tests/unit/test_intent.py'
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n📄 Found: {test_file}")
            
            # Try to extract test names and patterns
            with open(test_file) as f:
                content = f.read()
            
            # Find test methods
            test_methods = re.findall(r'def (test_\w+)\(', content)
            if test_methods:
                print(f"   Tests found: {len(test_methods)}")
                for method in test_methods[:5]:  # Show first 5
                    print(f"   - {method}")
            
            # Look for specific test cases
            if 'test_natural_language' in content:
                print("   ✓ Contains natural language tests")
                
                # Extract test cases
                test_cases = re.findall(r'\("([^"]+)",\s*IntentType\.(\w+)', content)
                if test_cases:
                    print(f"\n   Test cases found ({len(test_cases)} total):")
                    for i, (query, intent_type) in enumerate(test_cases[:10]):
                        print(f"   {i+1}. '{query}' → {intent_type}")
    
    # Try to find actual test output
    print("\n🔍 Looking for test output logs...")
    
    log_patterns = [
        'tests/v1.0/test_results*.log',
        'tests/results/*.log',
        'logs/test*.log',
        '.pytest_cache/v/cache/lastfailed'
    ]
    
    for pattern in log_patterns:
        for log_file in Path('.').glob(pattern):
            print(f"\n📄 Found log: {log_file}")
            if log_file.name == 'lastfailed':
                with open(log_file) as f:
                    content = f.read()
                    if content and content != '{}':
                        print("   Failed tests recorded!")
                        # Parse the JSON
                        try:
                            failed = json.loads(content)
                            for test, value in failed.items():
                                if 'natural' in test.lower() or 'nlp' in test.lower():
                                    print(f"   ❌ {test}")
                        except Exception:
                            print(f"   Content: {content[:200]}")
    
    # Analyze patterns in natural language that might fail
    print("\n🔍 Analyzing Natural Language Patterns...")
    
    problem_patterns = {
        "Complex queries": [
            "help me install a web browser",
            "what packages do I have installed?",
            "show me all installed packages"
        ],
        "Ambiguous intents": [
            "I need firefox",  # Could be INSTALL or SEARCH
            "firefox please",  # Unclear intent
            "get me python"    # Could be INSTALL or INFO
        ],
        "Multi-word packages": [
            "install firefox esr",
            "remove python 3.11",
            "search nodejs 18"
        ],
        "Conversational style": [
            "could you please install firefox for me?",
            "I'd like to remove vim if possible",
            "would you mind searching for python?"
        ]
    }
    
    print("\nPotential problem areas:")
    for category, examples in problem_patterns.items():
        print(f"\n{category}:")
        for example in examples:
            print(f"  - '{example}'")
    
    # Create a test script to check these patterns
    print("\n💡 Creating test script to verify patterns...")
    
    test_script = '''#!/usr/bin/env python3
"""Test specific natural language patterns to find failures."""

import sys
sys.path.insert(0, 'src')

from nix_humanity.ai.nlp import NLPEngine

# Test patterns that might be failing
test_cases = [
    # Simple (should work)
    "install firefox",
    "remove vim",
    "search python",
    
    # Complex (might fail)
    "help me install a web browser",
    "show me all installed packages",
    "what's my current generation?",
    
    # Conversational (might fail)
    "please install firefox for me",
    "could you remove vim?",
    "I'd like to search for python packages"
]

nlp = NLPEngine()
passed = 0
failed = 0

for query in test_cases:
    try:
        result = nlp.process(query)
        if result and result.type:
            print(f"✅ '{query}' → {result.type}")
            passed += 1
        else:
            print(f"❌ '{query}' → No intent recognized")
            failed += 1
    except Exception as e:
        print(f"❌ '{query}' → ERROR: {e}")
        failed += 1

print(f"\\nResults: {passed} passed, {failed} failed")
print(f"Success rate: {passed}/{passed+failed} ({passed/(passed+failed)*100:.1f}%)")
'''
    
    with open('scripts/test-natural-language.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created scripts/test-natural-language.py")
    print("\nNext step: Run this script to identify specific failing patterns")

if __name__ == '__main__':
    find_failing_tests()