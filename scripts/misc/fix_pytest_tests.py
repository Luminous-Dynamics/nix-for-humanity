#!/usr/bin/env python3
"""Convert pytest tests to unittest."""

import re
from pathlib import Path

def convert_pytest_to_unittest(filepath):
    """Convert a pytest test file to unittest."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # If it doesn't use pytest, skip
    if 'import pytest' not in content and 'from pytest' not in content:
        return False
    
    # Remove pytest imports
    content = re.sub(r'import pytest\n', '', content)
    content = re.sub(r'from pytest import .*\n', '', content)
    
    # Add unittest import if not present
    if 'import unittest' not in content:
        # Add after the module docstring and before other imports
        lines = content.split('\n')
        new_lines = []
        in_docstring = False
        import_added = False
        
        for i, line in enumerate(lines):
            if i < 3 and (line.startswith('"""') or line.startswith("'''")):
                in_docstring = not in_docstring
            
            new_lines.append(line)
            
            # Add import after docstring ends
            if not import_added and not in_docstring and i > 0 and line.strip() == '':
                new_lines.append('import unittest')
                import_added = True
        
        content = '\n'.join(new_lines)
    
    # Convert class definitions
    content = re.sub(r'class Test(\w+):', r'class Test\1(unittest.TestCase):', content)
    
    # Convert assertions
    content = re.sub(r'\bassert\s+(.+?)\s*==\s*(.+)', r'self.assertEqual(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s*!=\s*(.+)', r'self.assertNotEqual(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s*>\s*(.+)', r'self.assertGreater(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s*<\s*(.+)', r'self.assertLess(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s*>=\s*(.+)', r'self.assertGreaterEqual(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s*<=\s*(.+)', r'self.assertLessEqual(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s+in\s+(.+)', r'self.assertIn(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s+not in\s+(.+)', r'self.assertNotIn(\1, \2)', content)
    content = re.sub(r'\bassert\s+(.+?)\s+is\s+None', r'self.assertIsNone(\1)', content)
    content = re.sub(r'\bassert\s+(.+?)\s+is\s+not\s+None', r'self.assertIsNotNone(\1)', content)
    content = re.sub(r'\bassert\s+not\s+(.+)', r'self.assertFalse(\1)', content)
    content = re.sub(r'\bassert\s+(.+)', r'self.assertTrue(\1)', content)
    
    # Convert pytest.raises to assertRaises
    content = re.sub(r'with pytest\.raises\((\w+)\):', r'with self.assertRaises(\1):', content)
    
    # Add main block if not present
    if '__main__' not in content:
        content += '\n\nif __name__ == "__main__":\n    unittest.main()\n'
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Converted: {filepath}")
        return True
    
    return False

def main():
    """Convert all pytest tests to unittest."""
    test_dir = Path('tests')
    
    # Find all test files
    test_files = list(test_dir.rglob('test_*.py'))
    
    converted_count = 0
    for test_file in test_files:
        if convert_pytest_to_unittest(test_file):
            converted_count += 1
    
    print(f"\nConverted {converted_count} files from pytest to unittest")

if __name__ == '__main__':
    main()