#!/usr/bin/env python3
"""Test all imports to find what's actually broken."""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

print("🧪 Testing Imports\n")

# Track results
results = {
    'success': [],
    'failed': []
}

# Core imports to test
test_imports = [
    # Core
    ("luminous_nix", "Main package"),
    ("luminous_nix.core", "Core module"),
    ("luminous_nix.core.engine", "Engine module"),
    ("luminous_nix.core.backend", "Backend module"),
    ("luminous_nix.core.executor", "Executor module"),
    
    # AI/NLP
    ("luminous_nix.ai", "AI module"),
    ("luminous_nix.ai.nlp", "NLP module"),
    
    # From imports
    ("from luminous_nix.core import NixForHumanityBackend", "Backend class"),
    ("from luminous_nix.ai import NLPEngine", "NLP Engine"),
    ("from luminous_nix.ai.nlp import NLPPipeline", "NLP Pipeline"),
    ("from luminous_nix.ai.nlp import process", "process function"),
    
    # Security
    ("luminous_nix.security", "Security module"),
    ("luminous_nix.security.validator", "Validator module"),
    ("luminous_nix.security.input_validator", "Input validator"),
    
    # Nix
    ("luminous_nix.nix", "Nix module"),
    ("luminous_nix.nix.native_backend", "Native backend"),
]

for import_stmt, description in test_imports:
    try:
        if import_stmt.startswith("from"):
            exec(import_stmt)
            print(f"✅ {description}: {import_stmt}")
            results['success'].append(import_stmt)
        else:
            exec(f"import {import_stmt}")
            print(f"✅ {description}: import {import_stmt}")
            results['success'].append(import_stmt)
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ {description}: {error_type}: {error_msg}")
        results['failed'].append({
            'import': import_stmt,
            'description': description,
            'error': f"{error_type}: {error_msg}"
        })

print(f"\n📊 Summary: {len(results['success'])} succeeded, {len(results['failed'])} failed")

if results['failed']:
    print("\n❌ Failed Imports:")
    for failure in results['failed']:
        print(f"\n{failure['import']}")
        print(f"  Error: {failure['error']}")

# Now let's trace the actual import chain for the main issue
print("\n\n🔍 Tracing Import Chain for AI Module:")
print("=" * 60)

try:
    import luminous_nix.ai
    print("✅ Step 1: import luminous_nix.ai - SUCCESS")
    
    # Check what's in the module
    print(f"\nAvailable in luminous_nix.ai: {dir(luminous_nix.ai)}")
    
except Exception as e:
    print(f"❌ Step 1: import luminous_nix.ai - FAILED")
    traceback.print_exc()

# Check what's actually in the files
print("\n\n📄 Checking File Contents:")
print("=" * 60)

files_to_check = [
    "src/luminous_nix/ai/__init__.py",
    "src/luminous_nix/ai/nlp.py",
    "src/luminous_nix/core/__init__.py",
    "src/luminous_nix/core/backend.py",
    "src/luminous_nix/core/engine.py"
]

for file_path in files_to_check:
    if Path(file_path).exists():
        print(f"\n{file_path}:")
        with open(file_path) as f:
            lines = f.readlines()[:10]  # First 10 lines
            for i, line in enumerate(lines, 1):
                if line.strip() and not line.strip().startswith('#'):
                    print(f"  {i}: {line.rstrip()}")
    else:
        print(f"\n{file_path}: NOT FOUND")