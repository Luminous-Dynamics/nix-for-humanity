#!/usr/bin/env python3
"""
Fix the flake templates in flake_manager.py by properly escaping curly braces
"""

import re

# Read the file
with open('nix_humanity/core/flake_manager.py', 'r') as f:
    content = f.read()

# Function to fix template strings
def fix_template(template_str):
    # Replace single { with {{ except when it's already {{ or when it's a format placeholder
    # First, mark format placeholders
    placeholders = ['{description}', '{inputs}', '{input_args}', '{outputs}', '{name}', 
                   '{packages}', '{shell_hook}', '{pname}', '{version}', '{build_inputs}',
                   '{install_phase}', '{content}', '{python_version}', '{extra_hook}',
                   '{node_version}']
    
    # Temporarily replace placeholders with unique markers
    temp = template_str
    for i, ph in enumerate(placeholders):
        temp = temp.replace(ph, f'<<<PLACEHOLDER_{i}>>>')
    
    # Now double all remaining single braces
    # Replace { with {{ and } with }}
    temp = temp.replace('{', '{{').replace('}', '}}')
    
    # Restore placeholders
    for i, ph in enumerate(placeholders):
        temp = temp.replace(f'<<<PLACEHOLDER_{i}>>>', ph)
    
    return temp

# Find and fix the _load_templates method
pattern = r'(def _load_templates\(self\) -> Dict\[str, str\]:.*?return {)(.*?)(}\s*\n\s*def)'
match = re.search(pattern, content, re.DOTALL)

if match:
    method_start = match.group(1)
    templates_content = match.group(2)
    method_end = match.group(3)
    
    # Fix each template in the dictionary
    fixed_templates = templates_content
    
    # Extract and fix each template
    template_pattern = r'"([^"]+)":\s*\'\'\'(.*?)\'\'\'(?:,)?'
    
    def fix_match(m):
        template_name = m.group(1)
        template_content = m.group(2)
        fixed_content = fix_template(template_content)
        return f'"{template_name}": \'\'\'{fixed_content}\'\'\','
    
    fixed_templates = re.sub(template_pattern, fix_match, templates_content, flags=re.DOTALL)
    
    # Reconstruct the file
    new_content = content[:match.start()] + method_start + fixed_templates + method_end + content[match.end():]
    
    # Write back
    with open('nix_humanity/core/flake_manager.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed flake templates!")
else:
    print("❌ Could not find _load_templates method")