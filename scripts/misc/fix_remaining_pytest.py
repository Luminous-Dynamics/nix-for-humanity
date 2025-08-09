#!/usr/bin/env python3
"""Fix remaining pytest issues in tests."""

import re
from pathlib import Path

def fix_pytest_issues(filepath):
    """Fix remaining pytest decorators and fixtures."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Remove pytest.fixture decorators
    content = re.sub(r'@pytest\.fixture\s*\n', '', content)
    
    # Remove pytest.mark decorators
    content = re.sub(r'@pytest\.mark\.\w+\s*\n', '', content)
    
    # Convert fixture methods to setUp
    content = re.sub(r'def (\w+)\(self\):\s*\n\s*""".*fixture.*"""', 
                     r'def setUp(self):\n        """Set up test fixtures"""', content)
    
    # Fix pytest.main calls
    content = re.sub(r'pytest\.main\(\[.*?\]\)', 'unittest.main()', content)
    
    # Fix AsyncMock import
    if 'AsyncMock' in content and 'from unittest.mock import' in content:
        # Add AsyncMock if not imported
        content = re.sub(r'from unittest.mock import (.+)(?<!AsyncMock)', 
                         r'from unittest.mock import \1, AsyncMock', content)
    
    # Add missing asyncio import
    if 'asyncio' in content and 'import asyncio' not in content:
        content = re.sub(r'import unittest', 'import unittest\nimport asyncio', content)
    
    # Fix backend.core.executor patches
    content = re.sub(r"@patch\('backend\.core\.executor\.", "@patch('", content)
    
    # Add missing unittest import
    if 'unittest.TestCase' in content and 'import unittest' not in content:
        content = 'import unittest\n' + content
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    
    return False

def main():
    """Fix all remaining pytest issues."""
    test_files = [
        'tests/unit/test_executor_comprehensive.py',
        'tests/unit/test_backend_comprehensive.py',
        'tests/unit/test_cli_adapter.py',
        'tests/unit/test_native_nix_backend.py',
        'tests/unit/test_xai_causal_engine.py',
    ]
    
    fixed_count = 0
    for test_file in test_files:
        filepath = Path(test_file)
        if filepath.exists():
            if fix_pytest_issues(filepath):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()