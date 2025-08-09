#!/usr/bin/env python3
"""Remove or replace Query and ExecutionMode references in tests"""

import os
import re

# Find all test files
test_files = []
for root, dirs, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            test_files.append(os.path.join(root, file))

fixed_count = 0

for test_file in test_files:
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Remove Query and ExecutionMode imports
        content = re.sub(r',\s*Query\s*,\s*ExecutionMode', '', content)
        content = re.sub(r',\s*Query', '', content)
        content = re.sub(r',\s*ExecutionMode', '', content)
        content = re.sub(r'Query\s*,\s*ExecutionMode\s*,', '', content)
        content = re.sub(r'Query\s*,', '', content)
        content = re.sub(r'ExecutionMode\s*,', '', content)
        
        # Replace Query usage with dict
        content = re.sub(r'Query\((.*?)\)', r'{"query": \1}', content)
        
        # Replace ExecutionMode references
        content = re.sub(r'ExecutionMode\.DRY_RUN', '"dry_run"', content)
        content = re.sub(r'ExecutionMode\.NORMAL', '"normal"', content)
        content = re.sub(r'ExecutionMode\.\w+', '"normal"', content)
        
        if content != original_content:
            with open(test_file, 'w') as f:
                f.write(content)
            print(f"✅ Fixed: {test_file}")
            fixed_count += 1
            
    except Exception as e:
        print(f"❌ Error processing {test_file}: {e}")

print(f"\n✅ Fixed {fixed_count} files")