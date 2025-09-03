#!/usr/bin/env python3
"""Check what attributes Response objects have"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Enable real backend
os.environ["LUMINOUS_USE_REAL_BACKEND"] = "true"
os.environ["LUMINOUS_DRY_RUN"] = "true"

from luminous_nix.core.luminous_core import LuminousNixCore, Query

core = LuminousNixCore()

# Test each command
commands = ["help", "list", "search hello", "install cowsay", "remove hello", "info", "clean"]

for cmd in commands:
    print(f"\n=== Testing: {cmd} ===")
    query = Query(text=cmd, dry_run=True)
    response = core.process_query(query)
    
    if response:
        print(f"Response type: {type(response).__name__}")
        print(f"Response attributes: {dir(response)}")
        print(f"Has 'success': {hasattr(response, 'success')}")
        print(f"Has 'message': {hasattr(response, 'message')}")
        print(f"Has 'error': {hasattr(response, 'error')}")
        
        # Check actual values
        if hasattr(response, 'success'):
            print(f"  success = {response.success}")
        if hasattr(response, 'message'):
            print(f"  message = {response.message[:50]}..." if response.message else "  message = None")
        if hasattr(response, 'error'):
            print(f"  error = {response.error}")
    else:
        print("No response received")