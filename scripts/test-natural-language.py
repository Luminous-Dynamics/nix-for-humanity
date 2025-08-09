#!/usr/bin/env python3
"""Test specific natural language patterns to find failures."""

import sys
sys.path.insert(0, 'src')

from nix_humanity.ai.nlp import process

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

passed = 0
failed = 0

for query in test_cases:
    try:
        result = process(query)
        if result and hasattr(result, 'type') and result.type:
            print(f"✅ '{query}' → {result.type}")
            passed += 1
        else:
            print(f"❌ '{query}' → No intent recognized")
            failed += 1
    except Exception as e:
        print(f"❌ '{query}' → ERROR: {e}")
        failed += 1

print(f"\nResults: {passed} passed, {failed} failed")
print(f"Success rate: {passed}/{passed+failed} ({passed/(passed+failed)*100:.1f}%)")
