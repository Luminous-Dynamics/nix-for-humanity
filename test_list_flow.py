#!/usr/bin/env python3
"""Debug the full flow for 'list' command"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Enable real backend
os.environ["LUMINOUS_USE_REAL_BACKEND"] = "true"
os.environ["LUMINOUS_DRY_RUN"] = "true"

from luminous_nix.core.luminous_core import LuminousNixCore, Query
from luminous_nix.core.intents import IntentRecognizer

# Test intent recognition first
recognizer = IntentRecognizer()
intent = recognizer.recognize("list")
print(f"Intent recognized: {intent.type if intent else 'None'}")

# Test full flow
core = LuminousNixCore()
query = Query(text="list", dry_run=True)

try:
    response = core.process_query(query)
    print(f"Response success: {response.success}")
    print(f"Response message: {response.message}")
    if hasattr(response, 'error'):
        print(f"Response error: {response.error}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()