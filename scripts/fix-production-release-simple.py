#!/usr/bin/env python3
"""Simple fix for prepare-production-release.py syntax errors"""

# Read the file
with open('scripts/prepare-production-release.py', 'r') as f:
    lines = f.readlines()

# Fix specific known issues
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix line 1216: print(f"
    if i == 1215 and line.strip() == 'print(f"':
        # This is a multiline f-string with literal newline
        # Combine with next line
        fixed_lines.append('        print(f"\\n{"="*60}")\n')
        i += 2  # Skip the next line which has {'='*60}")
        continue
    
    # Fix line 1221: print(f"{'='*60}
    elif i == 1220 and 'print(f"{\'=\'*60}' in line and not line.strip().endswith('")'):
        fixed_lines.append('        print(f"{"="*60}\\n")\n')
        i += 2  # Skip the ")
        continue
        
    # Fix line 1226: print(f"
    elif i == 1225 and line.strip() == 'print(f"':
        fixed_lines.append('    print(f"\\n{"="*60}")\n')
        i += 2  # Skip next line
        continue
        
    # Fix line 1229: print(f"{'='*60}
    elif i == 1228 and 'print(f"{\'=\'*60}' in line and not line.strip().endswith('")'):
        fixed_lines.append('    print(f"{"="*60}\\n")\n')
        i += 2  # Skip the ")
        continue
    
    # Fix literal newlines in other f-strings
    elif 'print(f"\\n' in line and '\\n' not in line:
        # This has a literal newline, not \n
        fixed_lines.append(line.replace('print(f"', 'print(f"\\n'))
    else:
        fixed_lines.append(line)
    
    i += 1

# Write back
with open('scripts/prepare-production-release.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Applied simple fixes")

# Test compilation
import subprocess
result = subprocess.run(['python3', '-m', 'py_compile', 'scripts/prepare-production-release.py'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ File now compiles successfully!")
else:
    print(f"❌ Still has errors:\n{result.stderr}")