#!/usr/bin/env python3
"""Fix the prepare-production-release.py script properly."""

import re

# Read the file
with open('scripts/prepare-production-release.py', 'r') as f:
    content = f.read()

# Fix the mangled docstrings
content = re.sub(r'""".format\(.*?\)([^"]+)""".format\(.*?\)', r'"""\1"""', content)

# Fix f-strings in the generate_release_checklist method
content = re.sub(r'f""".format\(.*?\)# Nix for Humanity', r'f"""# Nix for Humanity', content)

# Write back
with open('scripts/prepare-production-release.py', 'w') as f:
    f.write(content)

print("✅ Fixed docstrings and f-strings")

# Now let's check specific problematic sections
import ast
try:
    ast.parse(content)
    print("✅ File now parses correctly!")
except SyntaxError as e:
    print(f"❌ Still has syntax error at line {e.lineno}: {e.msg}")
    # If still errors, let's look at the specific issue
    lines = content.split('\n')
    if e.lineno <= len(lines):
        print(f"Problem line: {lines[e.lineno-1]}")
        
        # The issue is likely in multi-line strings with Nix syntax
        # Let's find all f-strings and check them
        for i, line in enumerate(lines):
            if 'f"""' in line or "f'''" in line:
                print(f"F-string starts at line {i+1}")