#!/usr/bin/env python3
"""
Fix import issues in Nix for Humanity tests
🎂 Birthday Import Fixer!
"""

import os
import re
import sys
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix common import issues in a test file."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix 1: Update old import paths
    replacements = [
        # Old path -> New path
        (r'from core\.intent import', 'from nix_for_humanity.core.intent import'),
        (r'from core\.', 'from nix_for_humanity.core.'),
        (r'import core\.', 'import nix_for_humanity.core.'),
        
        # Fix AriaLivePriority import
        (r"from nix_for_humanity\.accessibility import AriaLivePriority",
         "from nix_for_humanity.accessibility.types import AriaLivePriority"),
        
        # Fix Plan import
        (r"from nix_for_humanity\.core\.interface import.*Plan",
         "from nix_for_humanity.core.interface import ExecutionPlan as Plan"),
    ]
    
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    # Fix 2: Add try/except for pytest imports
    if 'import pytest' in content and 'try:' not in content:
        content = content.replace(
            'import pytest',
            'try:\n    import pytest\nexcept ImportError:\n    pytest = None'
        )
    
    # Fix 3: Handle missing textual imports gracefully
    if 'from textual' in content:
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip().startswith('from textual'):
                new_lines.append('try:')
                new_lines.append(f'    {line}')
                new_lines.append('except ImportError:')
                new_lines.append('    pass  # Textual not installed')
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix imports in all test files."""
    print("🔧 Fixing imports in test files...")
    
    # Add src to Python path
    src_path = Path(__file__).parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    test_dir = Path(__file__).parent / 'tests'
    fixed_count = 0
    
    for test_file in test_dir.rglob('test_*.py'):
        if fix_imports_in_file(test_file):
            fixed_count += 1
            print(f"  ✅ Fixed: {test_file.relative_to(test_dir)}")
    
    print(f"\n🎉 Fixed {fixed_count} test files!")
    
    # Also fix the __init__.py files
    print("\n🔧 Fixing __init__.py files...")
    
    # Create missing __init__.py files
    for subdir in test_dir.rglob('*'):
        if subdir.is_dir() and not (subdir / '__init__.py').exists():
            (subdir / '__init__.py').write_text('')
            print(f"  ✅ Created: {subdir.relative_to(test_dir)}/__init__.py")

if __name__ == '__main__':
    main()