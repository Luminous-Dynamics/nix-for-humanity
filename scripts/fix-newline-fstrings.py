#!/usr/bin/env python3
"""Fix all f-strings with literal newlines in prepare-production-release.py"""

import re

# Read the file
with open('scripts/prepare-production-release.py', 'r') as f:
    content = f.read()

# Find all f-strings with literal newlines and fix them
# Pattern: f"<newline> followed by content
pattern = r'print\(f"\n'
replacement = r'print(f"\n'

# Replace all occurrences
content = re.sub(pattern, replacement, content)

# Also fix the closing pattern
pattern2 = r'\n"\)'
replacement2 = r'\n")'

content = re.sub(pattern2, replacement2, content)

# More specific fixes for the actual issues
# Line 1216: print(f"<newline>
# Should be: print(f"\n
lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines):
    # Fix print statements with literal newlines
    if 'print(f"' in line and line.strip() == 'print(f"':
        # This is an incomplete f-string, fix it
        fixed_lines.append('        print(f"\\n')
    elif line.strip() == '")' and i > 0 and 'print(f"' in lines[i-1]:
        # This closes an f-string, add the missing quote
        fixed_lines.append('\\n")')
    elif 'print(f"' in line and not line.strip().endswith('")'):
        # Check if it's a multiline f-string that needs fixing
        if i + 1 < len(lines) and not ('"' in lines[i+1] or "'" in lines[i+1]):
            # This looks like a literal newline, fix it
            fixed_lines.append(line.rstrip() + '\\n" +')
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Join back together
content = '\n'.join(fixed_lines)

# Write the fixed content
with open('scripts/prepare-production-release.py', 'w') as f:
    f.write(content)

print("✅ Fixed f-string newline issues")

# Test if it compiles now
import py_compile
try:
    py_compile.compile('scripts/prepare-production-release.py', doraise=True)
    print("✅ File now compiles successfully!")
except py_compile.PyCompileError as e:
    print(f"❌ Still has errors: {e}")