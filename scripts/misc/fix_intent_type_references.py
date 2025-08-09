#!/usr/bin/env python3
"""
Fix IntentType references in unit tests to match actual enum values
"""

import re
from pathlib import Path

def fix_intent_type_references(file_path):
    """Fix IntentType references in a single test file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Map of old references to new ones
    replacements = [
        # Intent types
        (r'\bIntentType\.INSTALL\b', 'IntentType.INSTALL_PACKAGE'),
        (r'\bIntentType\.UPDATE\b', 'IntentType.UPDATE_SYSTEM'),
        (r'\bIntentType\.SEARCH\b', 'IntentType.SEARCH_PACKAGE'),
        (r'\bIntentType\.CONFIG\b', 'IntentType.CONFIGURE'),
        (r'\bIntentType\.INFO\b', 'IntentType.EXPLAIN'),
        
        # Attribute names
        (r'intent\.raw_input\b', 'intent.raw_text'),
        (r'getattr\(intent, "target"', 'getattr(intent, "entities", {}).get("package"'),
        (r'intent\.target\b', 'intent.entities.get("package")'),
        
        # Test value updates
        (r'"install"', '"install_package"'),
        (r'"update"', '"update_system"'),
        (r'"search"', '"search_package"'),
        (r'"config"', '"configure"'),
        (r'"info"', '"explain"'),
    ]
    
    # Apply replacements
    original = content
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    # Only write if changes were made
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix imports in all unit test files"""
    test_dir = Path('tests/unit')
    
    if not test_dir.exists():
        print(f"Test directory {test_dir} not found")
        return
    
    fixed_count = 0
    for test_file in test_dir.glob('test_*.py'):
        print(f"Checking {test_file.name}...")
        if fix_intent_type_references(test_file):
            print(f"  ✓ Fixed references in {test_file.name}")
            fixed_count += 1
    
    print(f"\nFixed references in {fixed_count} files")

if __name__ == '__main__':
    main()