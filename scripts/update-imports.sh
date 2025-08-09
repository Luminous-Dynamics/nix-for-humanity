#!/usr/bin/env bash
# Update Python imports after reorganization
# This script fixes import statements after moving files to src/

set -euo pipefail

echo "🔄 Updating Python imports after reorganization..."

# Check if we have the right tools
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

# Create a Python script to update imports
cat > /tmp/update_imports.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import os
import re
from pathlib import Path

def update_imports_in_file(filepath):
    """Update imports in a single Python file."""
    updates_made = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Common import patterns to update
    replacements = [
        # Update backend imports to nix_humanity
        (r'from backend\.core\.(\w+)', r'from nix_humanity.core.\1'),
        (r'from backend\.python\.(\w+)', r'from nix_humanity.core.\1'),
        (r'import backend\.core\.(\w+)', r'import nix_humanity.core.\1'),
        
        # Update relative imports that might break
        (r'from nix_humanity\.', r'from nix_humanity.'),
        (r'import nix_humanity\.', r'import nix_humanity.'),
        
        # Fix test imports
        (r'from tests\.', r'from tests.'),
        
        # Handle the move to src structure
        (r'from nix_for_humanity\.', r'from nix_humanity.'),
        (r'import nix_for_humanity\.', r'import nix_humanity.'),
    ]
    
    for pattern, replacement in replacements:
        new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        if count > 0:
            content = new_content
            updates_made.append(f"{pattern} -> {replacement} ({count} replacements)")
    
    # Handle sys.path manipulations
    if 'sys.path' in content:
        # Update common path manipulations
        content = re.sub(
            r"sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(__file__\), ['\"]\.\.['\"]\)\)",
            "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))",
            content
        )
        
        # Update absolute path additions
        content = re.sub(
            r"sys\.path\.append\(['\"].*?/nix_humanity['\"]\)",
            "sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))",
            content
        )
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return updates_made
    
    return []

def update_test_imports(test_file):
    """Special handling for test files."""
    with open(test_file, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Add src to path if not already there
    if 'sys.path' not in content and 'import nix_humanity' in content:
        import_line = next((i for i, line in enumerate(content.split('\n')) 
                           if line.strip() and not line.startswith('#')), 0)
        
        lines = content.split('\n')
        path_setup = [
            "import sys",
            "import os",
            "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))",
            ""
        ]
        
        lines = lines[:import_line] + path_setup + lines[import_line:]
        content = '\n'.join(lines)
    
    if content != original_content:
        with open(test_file, 'w') as f:
            f.write(content)
        return True
    
    return False

def main():
    # Update all Python files in src/
    src_files = list(Path('src').rglob('*.py')) if Path('src').exists() else []
    
    print(f"Found {len(src_files)} Python files in src/")
    
    for file in src_files:
        updates = update_imports_in_file(file)
        if updates:
            print(f"✓ Updated {file}")
            for update in updates:
                print(f"  - {update}")
    
    # Update test files
    test_files = list(Path('tests').rglob('*.py')) if Path('tests').exists() else []
    
    print(f"\nFound {len(test_files)} test files")
    
    for file in test_files:
        if update_test_imports(file):
            print(f"✓ Updated test imports in {file}")
        updates = update_imports_in_file(file)
        if updates:
            for update in updates:
                print(f"  - {update}")
    
    # Update bin scripts
    bin_files = list(Path('bin').glob('*')) if Path('bin').exists() else []
    
    for file in bin_files:
        if file.suffix == '' and file.is_file():
            try:
                with open(file, 'r') as f:
                    if f.read(2) == '#!':
                        updates = update_imports_in_file(file)
                        if updates:
                            print(f"✓ Updated {file}")
                            for update in updates:
                                print(f"  - {update}")
            except:
                pass

if __name__ == '__main__':
    main()
PYTHON_SCRIPT

# Run the import updater
python3 /tmp/update_imports.py

# Clean up
rm -f /tmp/update_imports.py

echo ""
echo "🔍 Checking for broken imports..."

# Simple check for obviously broken imports
python3 -c "
import os
import ast
from pathlib import Path

def check_imports(filepath):
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if 'backend' in alias.name:
                        print(f'⚠️  {filepath}: Still importing from backend: {alias.name}')
            elif isinstance(node, ast.ImportFrom):
                if node.module and 'backend' in node.module:
                    print(f'⚠️  {filepath}: Still importing from backend: {node.module}')
    except:
        pass

# Check all Python files
for file in Path('.').rglob('*.py'):
    if 'archive' not in str(file) and 'venv' not in str(file):
        check_imports(file)
"

echo ""
echo "✅ Import update complete!"
echo ""
echo "Next steps:"
echo "1. Run tests to verify imports work: pytest tests/"
echo "2. Check for any remaining import errors"
echo "3. Update any hardcoded paths in configuration files"