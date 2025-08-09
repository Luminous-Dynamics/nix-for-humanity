#!/usr/bin/env python3
"""Fix remaining backend imports after reorganization."""

import os
import re
import sys
from pathlib import Path

# Define import mappings
IMPORT_MAPPINGS = {
    # Backend core imports
    r'from backend\.core\.(\w+) import': r'from nix_humanity.core.\1 import',
    r'from backend\.core import': r'from nix_humanity.core import',
    r'from backend\.api\.(\w+) import': r'from nix_humanity.api.\1 import',
    r'from backend\.api import': r'from nix_humanity.api import',
    r'from nix_humanity.core import': r'from nix_humanity.core import',
    
    # Python native backend
    r'from nix_humanity.core.native_operations import': r'from nix_humanity.core.native_operations import',
    r'from nix_humanity.core.native_operations import': r'from nix_humanity.core.native_operations import',
    r'from nix_humanity.core.native_operations import': r'from nix_humanity.core.native_operations import',
    
    # Unified backend
    r'from nix_humanity.core.engine import': r'from nix_humanity.core.engine import',
    r'from nix_humanity.core.engine import': r'from nix_humanity.core.engine import',
    
    # Test fixtures
    r'from tests\.fixtures\.consciousness_test_backend import': r'from tests.fixtures.sacred_test_base import',
    r'from src\.nix_for_humanity\.backend\.core_engine import': r'from nix_humanity.core.engine import',
    
    # Knowledge graph and other components
    r'from backend\.knowledge_graph\.(\w+) import': r'from features.v3.0.intelligence.knowledge_graph.\1 import',
    r'from backend\.trust_modeling\.(\w+) import': r'from features.v3.0.intelligence.trust_modeling.\1 import',
    r'from backend\.perception\.(\w+) import': r'from features.v3.0.intelligence.perception.\1 import',
    r'from backend\.mocks import': r'from features.v3.0.intelligence.mocks import',
    r'from backend\.config\.(\w+) import': r'from nix_humanity.config.\1 import',
    
    # Specific backend modules
    r'from nix_humanity\.core\.backend import': r'from nix_humanity.core.engine import',
    r'import nix_humanity.core as backend': r'import nix_humanity.core as backend',
    r'from core\.backend import': r'from nix_humanity.core.engine import',
    r'from nix_humanity\.nix\.native_backend import': r'from nix_humanity.core.native_operations import',
    r'from backend\.voice import': r'from nix_humanity.voice import',
    
    # Cached backend
    r'from src\.nix_for_humanity\.backend\.cached_backend import': r'from nix_humanity.core.engine import',
    r'from src\.nix_for_humanity\.backend\.enhanced_backend import': r'from nix_humanity.core.engine import',
}

def fix_imports_in_file(filepath):
    """Fix imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    original_content = content
    changed = False
    
    # Apply all import mappings
    for pattern, replacement in IMPORT_MAPPINGS.items():
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changed = True
            content = new_content
    
    # Write back if changed
    if changed:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed imports in: {filepath}")
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    
    return False

def main():
    """Main function to fix all backend imports."""
    project_root = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity')
    
    # Find all Python files
    python_files = []
    for pattern in ['*.py']:
        python_files.extend(project_root.rglob(pattern))
    
    # Exclude some directories
    exclude_dirs = {'__pycache__', '.git', 'venv', 'env', '.tox', 'build', 'dist'}
    python_files = [f for f in python_files if not any(ex in str(f) for ex in exclude_dirs)]
    
    print(f"Found {len(python_files)} Python files to check...")
    
    fixed_count = 0
    for filepath in python_files:
        if fix_imports_in_file(filepath):
            fixed_count += 1
    
    print(f"\n✅ Fixed imports in {fixed_count} files")
    
    # Special case fixes
    print("\n🔧 Applying special case fixes...")
    
    # Fix consciousness_test_backend.py
    test_backend_file = project_root / 'tests/fixtures/consciousness_test_backend.py'
    if test_backend_file.exists():
        with open(test_backend_file, 'w') as f:
            f.write("""\"\"\"Sacred test backend for consciousness-first testing.\"\"\"

# Re-export from sacred test base
from .sacred_test_base import *
""")
        print(f"✅ Fixed {test_backend_file}")

if __name__ == '__main__':
    main()