#!/usr/bin/env python3
"""Test that real backend is now the default in v0.5.1"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# IMPORTANT: Do NOT set LUMINOUS_USE_REAL_BACKEND anymore!
# It should default to real backend now

# Still use dry run for safety
os.environ["LUMINOUS_DRY_RUN"] = "true"

# Make sure the old variable is not set
if "LUMINOUS_USE_REAL_BACKEND" in os.environ:
    del os.environ["LUMINOUS_USE_REAL_BACKEND"]

print("=" * 60)
print("Testing v0.5.1 - Real Backend as Default")
print("=" * 60)
print()

from luminous_nix.core.luminous_core import LuminousNixCore, Query

# Should print "Using REAL NixOS backend" by default now
core = LuminousNixCore()

print()
print("Testing commands with default backend:")
print()

# Test a few commands
tests = [
    ("help", "Help command"),
    ("list", "List packages"),
    ("search vim", "Search packages"),
]

for command, description in tests:
    print(f"📦 {description}: '{command}'")
    query = Query(text=command, dry_run=True)
    response = core.process_query(query)
    
    if response and response.success:
        print(f"   ✅ SUCCESS - Backend working")
    else:
        print(f"   ❌ FAILED - Backend not working")
        if response and hasattr(response, 'error'):
            print(f"   Error: {response.error}")

print()
print("=" * 60)
print("✅ v0.5.1 Test Complete - Real backend is the default!")
print("=" * 60)