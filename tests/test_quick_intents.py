#!/usr/bin/env python3
"""Quick test of intent recognition fixes."""

import sys
sys.path.insert(0, 'src')

from luminous_nix.core.intents import IntentRecognizer, IntentType

recognizer = IntentRecognizer()

# Test cases that were failing
test_cases = [
    ("get rid of python2", IntentType.REMOVE_PACKAGE),
    ("I don't want nodejs anymore", IntentType.REMOVE_PACKAGE),
    ("install firefox", IntentType.INSTALL_PACKAGE),
    ("remove vim", IntentType.REMOVE_PACKAGE),
    ("get me something", IntentType.INSTALL_PACKAGE),  # Should have low confidence
]

print("Testing intent recognition fixes:\n")
for query, expected_type in test_cases:
    intent = recognizer.recognize(query)
    status = "✅" if intent.type == expected_type else "❌"
    print(f"{status} '{query}'")
    print(f"   Type: {intent.type.value} (expected: {expected_type.value})")
    print(f"   Confidence: {intent.confidence:.2f}")
    if 'package' in intent.entities:
        print(f"   Package: {intent.entities['package']}")
    print()

print("\nKey fixes:")
print("1. Remove patterns now checked BEFORE install patterns")
print("2. 'get rid of' no longer matches install pattern")
print("3. Vague requests get lower confidence scores")