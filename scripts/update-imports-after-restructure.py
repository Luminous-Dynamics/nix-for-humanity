#!/usr/bin/env python3
"""Update imports after professional restructuring."""

import os
import re
from pathlib import Path

# Map old imports to new imports
IMPORT_MAPPINGS = {
    # Core mappings
    'from luminous_nix.core.intent': 'from luminous_nix.core.intent',
    'from luminous_nix.core.executor': 'from luminous_nix.core.executor',
    'from luminous_nix.core.knowledge': 'from luminous_nix.core.knowledge',
    'from luminous_nix.core.types': 'from luminous_nix.core.types',
    
    # Backend mappings
    'from luminous_nix.backends.nix_native': 'from luminous_nix.backends.nix_native',
    'from luminous_nix.backends.subprocess': 'from luminous_nix.backends.subprocess',
    
    # Frontend mappings
    'from luminous_nix.frontends.cli': 'from luminous_nix.frontends.cli',
    'from luminous_nix.frontends.tui': 'from luminous_nix.frontends.tui',
    'from luminous_nix.frontends.api': 'from luminous_nix.frontends.api',
    'from luminous_nix.frontends.cli': 'from luminous_nix.frontends.cli',
    
    # Extension mappings
    'from luminous_nix.extensions.voice': 'from luminous_nix.extensions.voice',
    'from luminous_nix.extensions.learning': 'from luminous_nix.extensions.learning',
    'from luminous_nix.extensions.ai': 'from luminous_nix.extensions.ai',
    
    # Utils mappings
    'from luminous_nix.utils.config': 'from luminous_nix.utils.config',
    'from luminous_nix.utils.logging': 'from luminous_nix.utils.logging',
    'from luminous_nix.utils.config import': 'from luminous_nix.utils.config import',
    
    # Remove consciousness imports (archived)
    '# ARCHIVED: consciousness module': '# ARCHIVED: consciousness module',
    '# ARCHIVED: consciousness module': '# ARCHIVED: consciousness module',
}

def update_imports_in_file(filepath: Path) -> bool:
    """Update imports in a single Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Apply import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                print(f"  Updated: {old_import} -> {new_import}")
        
        # Handle relative imports that might break
        if 'from .' in content and '/consciousness/' not in str(filepath):
            # Fix relative imports based on new structure
            pass
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"  Error processing {filepath}: {e}")
        return False

def main():
    """Update all Python files with new import structure."""
    print("🔄 Updating imports after restructuring...")
    print("="*50)
    
    project_root = Path('/srv/luminous-dynamics/11-meta-consciousness/luminous-nix')
    
    # Find all Python files
    python_files = list(project_root.glob('**/*.py'))
    
    # Exclude archived files
    python_files = [
        f for f in python_files 
        if '.archive' not in str(f) and '__pycache__' not in str(f)
    ]
    
    print(f"Found {len(python_files)} Python files to check")
    print()
    
    updated_count = 0
    
    for filepath in python_files:
        relative_path = filepath.relative_to(project_root)
        print(f"Checking: {relative_path}")
        
        if update_imports_in_file(filepath):
            updated_count += 1
            print(f"  ✓ Updated")
        else:
            print(f"  - No changes needed")
    
    print()
    print("="*50)
    print(f"✅ Updated {updated_count} files")
    
    # Check for broken imports
    print()
    print("🔍 Checking for potentially broken imports...")
    
    broken_patterns = [
        r'from\s+luminous_nix\.consciousness',
        r'from\s+luminous_nix\.llm',
        r'from\s+luminous_nix\.sandbox',
        r'from\s+luminous_nix\.gui',
    ]
    
    for filepath in python_files:
        with open(filepath, 'r') as f:
            content = f.read()
        
        for pattern in broken_patterns:
            if re.search(pattern, content):
                relative_path = filepath.relative_to(project_root)
                print(f"  ⚠️  {relative_path} has archived imports")
    
    print()
    print("🎯 Next steps:")
    print("  1. Run: pytest tests/unit")
    print("  2. Fix any remaining import errors")
    print("  3. Update bin/ask-nix entry point")
    print("  4. Test basic functionality")

if __name__ == '__main__':
    main()
