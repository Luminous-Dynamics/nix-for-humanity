#!/usr/bin/env python3
"""
Fix remaining luminous_nix imports that the bash script missed.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    original = content
    
    # Replace various import patterns
    content = re.sub(r'from luminous_nix', 'from luminous_nix', content)
    content = re.sub(r'import luminous_nix', 'import luminous_nix', content)
    content = re.sub(r'luminous_nix\.', 'luminous_nix.', content)
    content = re.sub(r'"luminous_nix"', '"luminous_nix"', content)
    content = re.sub(r"'luminous_nix'", "'luminous_nix'", content)
    
    # Fix package references in strings
    content = re.sub(r'luminous_nix', 'luminous_nix', content)
    
    if content != original:
        try:
            # Create backup
            backup_path = str(filepath) + '.bak.rename'
            if not os.path.exists(backup_path):
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original)
            
            # Write fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    return False

def main():
    """Fix all Python files in the project."""
    project_root = Path('/srv/luminous-dynamics/11-meta-consciousness/luminous-nix')
    
    # Directories to skip
    skip_dirs = {'.archive', '__pycache__', '.git', 'archive', 'archives', 
                 'luminous-nix-archives-2025-08-17', '.pytest_cache'}
    
    fixed_count = 0
    total_count = 0
    
    print("🔧 Fixing remaining luminous_nix imports...")
    
    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py') and not file.endswith('.bak.rename'):
                filepath = Path(root) / file
                total_count += 1
                
                if fix_imports_in_file(filepath):
                    fixed_count += 1
                    print(f"  Fixed: {filepath.relative_to(project_root)}")
    
    print(f"\n✅ Fixed {fixed_count} out of {total_count} Python files")
    
    # Also update pyproject.toml scripts section
    pyproject_path = project_root / 'pyproject.toml'
    if pyproject_path.exists():
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        original = content
        content = re.sub(r'nix_for_humanity', 'luminous_nix', content)
        content = re.sub(r'luminous_nix', 'luminous_nix', content)
        
        if content != original:
            with open(pyproject_path, 'w') as f:
                f.write(content)
            print("✅ Updated pyproject.toml")

if __name__ == '__main__':
    main()