#!/usr/bin/env python3
"""
Script to fix Intent constructor calls throughout the test suite.

This script converts old Intent constructor patterns to the new format:
- Old: Intent(IntentType.INSTALL, 'firefox', 0.95)
- New: Intent(type=IntentType.INSTALL, entities={'target': 'firefox'}, confidence=0.95, raw_input='install firefox')
"""

import re
import os
from pathlib import Path

def fix_intent_constructor(match):
    """Convert old Intent constructor to new format"""
    full_match = match.group(0)
    intent_type = match.group(1)
    target = match.group(2)
    confidence = match.group(3)
    metadata = match.group(4) if match.group(4) else None
    
    # Handle None target
    if target == 'None':
        entities = '{}'
        raw_input = f"'{intent_type.lower().replace('IntentType.', '')}'"
    else:
        # Remove quotes from target
        clean_target = target.strip("'\"")
        entities = f"{{'target': {target}, 'package': {target}}}"
        raw_input = f"'{intent_type.lower().replace('IntentType.', '')} {clean_target}'"
    
    # Build new constructor
    new_constructor = f"Intent(\n        type={intent_type},\n        entities={entities},\n        confidence={confidence}"
    
    if metadata:
        new_constructor += f",\n        raw_input={raw_input}"
    else:
        new_constructor += f",\n        raw_input={raw_input}"
    
    new_constructor += "\n    )"
    
    return new_constructor

def fix_file(file_path):
    """Fix Intent constructors in a single file"""
    print(f"Fixing {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Intent(IntentType.X, 'target', confidence)
    pattern1 = r'Intent\((IntentType\.\w+),\s*([^,]+),\s*([^,)]+)\)'
    content = re.sub(pattern1, fix_intent_constructor, content)
    
    # Pattern 2: Intent(IntentType.X, 'target', confidence, metadata)
    pattern2 = r'Intent\((IntentType\.\w+),\s*([^,]+),\s*([^,]+),\s*([^)]+)\)'
    content = re.sub(pattern2, fix_intent_constructor, content)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  Fixed Intent constructors in {file_path}")
        return True
    else:
        print(f"  No Intent constructors to fix in {file_path}")
        return False

def main():
    """Fix Intent constructors in all test files"""
    test_dir = Path("tests/unit")
    
    files_with_intent = [
        "test_engine_enhanced.py",
        "test_backend_comprehensive.py", 
        "test_executor_comprehensive.py",
        "test_headless_engine.py",
        "test_executor.py",
        "test_core_types.py",
        "test_intent.py",
        "test_cli_adapter_comprehensive.py"
    ]
    
    fixed_count = 0
    for filename in files_with_intent:
        file_path = test_dir / filename
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()