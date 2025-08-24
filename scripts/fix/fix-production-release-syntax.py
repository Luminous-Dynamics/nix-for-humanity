#!/usr/bin/env python3
"""Fix the syntax error in prepare-production-release.py"""

import re

# Read the file
with open('scripts/prepare-production-release.py', 'r') as f:
    content = f.read()

# Find the problematic f-string
# The error is at line 149, which is inside a multiline f-string starting around line 55
# Look for unclosed braces in the f-string

# Split into lines
lines = content.split('\n')

# Find where the f-string starts and ends
in_fstring = False
fstring_start = -1
fstring_end = -1

for i, line in enumerate(lines):
    if 'release_notes = f"""' in line:
        in_fstring = True
        fstring_start = i
    elif in_fstring and '"""' in line and i > fstring_start:
        fstring_end = i
        break

print(f"F-string starts at line {fstring_start + 1} and ends at line {fstring_end + 1}")

# Check for unclosed braces in the f-string content
if fstring_start >= 0 and fstring_end >= 0:
    fstring_content = '\n'.join(lines[fstring_start:fstring_end+1])
    
    # Count braces
    open_braces = fstring_content.count('{')
    close_braces = fstring_content.count('}')
    
    print(f"Open braces: {open_braces}, Close braces: {close_braces}")
    
    # Look for the specific problem
    # The issue is likely {VERSION or similar without closing brace
    
    # Find unclosed placeholders
    import re
    unclosed = re.findall(r'{[A-Z_]+(?!})', fstring_content)
    print(f"Potential unclosed placeholders: {unclosed}")
    
    # Fix by finding {VERSION and adding missing }
    for i in range(fstring_start, fstring_end + 1):
        if '{VERSION' in lines[i] and '{VERSION}' not in lines[i]:
            print(f"Found unclosed {{VERSION at line {i+1}")
            lines[i] = lines[i].replace('{VERSION', '{VERSION}')
            
    # Write back
    with open('scripts/prepare-production-release.py', 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Fixed!")
else:
    print("Could not find f-string boundaries")