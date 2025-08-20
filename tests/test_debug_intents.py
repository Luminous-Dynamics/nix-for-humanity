#!/usr/bin/env python3
"""Debug intent recognition."""

import sys
sys.path.insert(0, 'src')

from luminous_nix.core.intents import IntentRecognizer, IntentType

recognizer = IntentRecognizer()

# Test the specific failing cases
test_cases = [
    "disk usage",
    "analyze disk space", 
    "find large files",
    "get rid of python2",
    "I don't want nodejs anymore",
]

print("Debugging intent recognition:\n")
for query in test_cases:
    intent = recognizer.recognize(query)
    print(f"Query: '{query}'")
    print(f"  Recognized as: {intent.type.value}")
    print(f"  Confidence: {intent.confidence:.2f}")
    print(f"  Entities: {intent.entities}")
    print()