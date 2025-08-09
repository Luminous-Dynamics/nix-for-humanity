#!/usr/bin/env python3
"""Fix indentation in test_executor_comprehensive.py"""

# Read the file
with open("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/tests/unit/test_executor_comprehensive.py", "r") as f:
    lines = f.readlines()

# Fix indentation for test methods that start with spaces
fixed_lines = []
for i, line in enumerate(lines):
    # Fix lines that start with 8 spaces and contain "def test_"
    if line.startswith("        def test_"):
        fixed_lines.append(line[4:])  # Remove 4 spaces
    # Fix lines that start with 8 spaces and contain type=IntentType
    elif i > 0 and "type=IntentType" in line and line.startswith("        "):
        fixed_lines.append("            " + line.strip() + "\n")
    # Fix lines that start with 8 spaces and contain entities=
    elif i > 0 and "entities=" in line and line.startswith("        "):
        fixed_lines.append("            " + line.strip() + "\n")
    # Fix lines that start with 8 spaces and contain confidence=
    elif i > 0 and "confidence=" in line and line.startswith("        "):
        fixed_lines.append("            " + line.strip() + "\n")
    # Fix lines that start with 8 spaces and contain raw_input=
    elif i > 0 and "raw_input=" in line and line.startswith("        "):
        fixed_lines.append("            " + line.strip() + "\n")
    # Fix closing parenthesis
    elif i > 0 and line.strip() == ")" and len(line) - len(line.lstrip()) == 4:
        fixed_lines.append("        )\n")
    else:
        fixed_lines.append(line)

# Write the fixed content back
with open("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/tests/unit/test_executor_comprehensive.py", "w") as f:
    f.writelines(fixed_lines)

print("Fixed indentation in test_executor_comprehensive.py")