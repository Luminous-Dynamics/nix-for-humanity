#!/usr/bin/env python3
"""
Simple script to fix the most common Intent constructor patterns
"""

import re
from pathlib import Path

def process_file(filepath):
    """Process a single file to fix Intent constructors"""
    print(f"Processing {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix 3-parameter constructors: Intent(IntentType.X, 'target', confidence)
    pattern1 = r"Intent\(IntentType\.(\w+),\s*'([^']+)',\s*([0-9.]+)\)"
    def replace1(match):
        intent_type, target, confidence = match.groups()
        return f"""Intent(
            type=IntentType.{intent_type},
            entities={{'target': '{target}', 'package': '{target}'}},
            confidence={confidence},
            raw_input='{intent_type.lower()} {target}'
        )"""
    content = re.sub(pattern1, replace1, content)
    
    # Fix 3-parameter with None: Intent(IntentType.X, None, confidence)
    pattern2 = r"Intent\(IntentType\.(\w+),\s*None,\s*([0-9.]+)\)"
    def replace2(match):
        intent_type, confidence = match.groups()
        return f"""Intent(
            type=IntentType.{intent_type},
            entities={{}},
            confidence={confidence},
            raw_input='{intent_type.lower()}'
        )"""
    content = re.sub(pattern2, replace2, content)
    
    # Fix 4-parameter constructors: Intent(IntentType.X, 'target', confidence, metadata)
    pattern3 = r"Intent\(IntentType\.(\w+),\s*'([^']+)',\s*([0-9.]+),\s*\{[^}]+\}\)"
    def replace3(match):
        intent_type, target, confidence = match.groups()
        return f"""Intent(
            type=IntentType.{intent_type},
            entities={{'target': '{target}', 'package': '{target}'}},
            confidence={confidence},
            raw_input='{intent_type.lower()} {target}'
        )"""
    content = re.sub(pattern3, replace3, content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  Fixed Intent constructors")
        return True
    else:
        print(f"  No changes needed")
        return False

def main():
    files_to_fix = [
        "tests/unit/test_engine_enhanced.py",
        "tests/unit/test_backend_comprehensive.py",
        "tests/unit/test_executor_comprehensive.py",
        "tests/unit/test_headless_engine.py",
        "tests/unit/test_executor.py"
    ]
    
    fixed_count = 0
    for filepath in files_to_fix:
        path = Path(filepath)
        if path.exists():
            if process_file(path):
                fixed_count += 1
        else:
            print(f"File not found: {filepath}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()