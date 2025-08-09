#!/usr/bin/env python3
"""
Properly fix the flake templates - only double braces that aren't format placeholders
"""

# Read the file
with open('nix_humanity/core/flake_manager.py', 'r') as f:
    content = f.read()

# Replace quadruple braces with double braces
content = content.replace('{{{{', '{{')
content = content.replace('}}}}', '}}')

# Write back
with open('nix_humanity/core/flake_manager.py', 'w') as f:
    f.write(content)

print("✅ Fixed quadruple braces back to double braces!")