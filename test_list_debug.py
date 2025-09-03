#!/usr/bin/env python3
"""Debug why 'list' command is failing"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.intents import IntentRecognizer, IntentType

# Create recognizer
recognizer = IntentRecognizer()

# Test "list" command
test_commands = ["list", "list installed", "list packages", "show packages"]

for cmd in test_commands:
    intent = recognizer.recognize(cmd)
    if intent:
        print(f"'{cmd}' -> IntentType.{intent.type.name} (confidence: {intent.confidence})")
        if hasattr(intent, 'entities'):
            print(f"  Entities: {intent.entities}")
    else:
        print(f"'{cmd}' -> No intent recognized")