#!/usr/bin/env python3
"""Fix f-string issues with semicolons in prepare-production-release.py"""

# Read the file
with open('scripts/prepare-production-release.py', 'r') as f:
    lines = f.readlines()

# Find the problematic section and convert it
# The issue is in the Installation section with Nix code
in_nix_block = False
fixed_lines = []

for i, line in enumerate(lines):
    # Check if we're entering a Nix code block inside the f-string
    if i > 140 and i < 200 and '```nix' in line:
        in_nix_block = True
    elif in_nix_block and '```' in line and 'nix' not in line:
        in_nix_block = False
    
    # If we're in a Nix block, escape semicolons or use different approach
    if in_nix_block and ';' in line:
        # Instead of escaping, we'll fix the f-string by not using f-string for static content
        fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Actually, let's take a different approach - change the f-string to regular string + format
# Find the release_notes f-string and convert it
new_lines = []
for i, line in enumerate(lines):
    if 'release_notes = f"""' in line:
        # Change from f-string to regular string with .format()
        new_lines.append('        release_notes = """# Nix for Humanity v{version} Release Notes\n')
    elif i > 50 and '"""' in line and 'installation_instructions' not in line:
        # Close the string and add format
        new_lines.append(line.replace('"""', '""".format(version=self.version, release_date=self.release_date)'))
    else:
        # Replace {self.version} with {version} and {self.release_date} with {release_date}
        if i > 50 and i < 250:
            line = line.replace('{self.version}', '{version}')
            line = line.replace('{self.release_date}', '{release_date}')
        new_lines.append(line)

# Write the fixed content
with open('scripts/prepare-production-release.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed f-string issues!")