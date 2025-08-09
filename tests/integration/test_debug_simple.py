#!/usr/bin/env python3
"""
Debug test to identify the timeout issue
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

print("Starting debug test...")

try:
    print("Importing Query and ExecutionMode...")
    from nix_humanity.core.interface import Query
    print("✓ Imports successful")
    
    print("\nCreating Query object...")
    query = {"query": text="install vim", mode="dry_run"}
    print(f"✓ Query created: {query}")
    
    print("\nImporting Engine...")
    from nix_humanity.core.engine import NixForHumanityBackend as Engine
    print("✓ Engine imported")
    
    print("\nCreating Engine instance...")
    config = {
        'dry_run': True,
        'default_personality': 'friendly'
    }
    engine = Engine(config)
    print("✓ Engine created")
    
    print("\nProcessing query...")
    response = engine.process(query)
    print(f"✓ Response: {response}")
    print(f"Response text: {response.text}")
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\nDebug test complete.")