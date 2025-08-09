#!/usr/bin/env python3
"""Count all Python files with syntax errors"""

import os
import subprocess
from pathlib import Path

errors = []
for root, dirs, files in os.walk('.'):
    # Skip certain directories
    if any(skip in root for skip in ['.git', '__pycache__', 'venv', 'node_modules']):
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            result = subprocess.run(['python3', '-m', 'py_compile', filepath], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                errors.append(filepath)

print(f'Total Python files with syntax errors: {len(errors)}')
for error in errors[:10]:  # Show first 10
    print(f'  - {error}')
if len(errors) > 10:
    print(f'  ... and {len(errors) - 10} more')