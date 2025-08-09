#!/usr/bin/env python3
"""Fix circular import issues in the codebase."""

import re
from pathlib import Path

def fix_circular_imports():
    """Fix the circular import issues."""
    
    print("🔧 Fixing Circular Import Issues\n")
    
    # First, let's understand the import structure
    print("1. Analyzing import dependencies...")
    
    # The main issue is UnifiedBackend import
    backend_file = Path('src/nix_humanity/core/backend.py')
    engine_file = Path('src/nix_humanity/core/engine.py')
    
    # Read backend.py
    with open(backend_file) as f:
        backend_content = f.read()
    
    print(f"📄 {backend_file}:")
    imports = re.findall(r'from \.engine import \((.*?)\)', backend_content, re.DOTALL)
    if imports:
        imported_items = [item.strip() for item in imports[0].split(',')]
        print(f"   Imports from engine: {imported_items}")
        
        # UnifiedBackend is being imported but might not exist
        if 'UnifiedBackend' in imported_items:
            print("   ❌ Trying to import UnifiedBackend (might not exist)")
    
    # Check what's actually in engine.py
    with open(engine_file) as f:
        engine_content = f.read()
    
    print(f"\n📄 {engine_file}:")
    classes = re.findall(r'^class (\w+)', engine_content, re.MULTILINE)
    functions = re.findall(r'^def (\w+)', engine_content, re.MULTILINE)
    print(f"   Classes defined: {classes}")
    print(f"   Functions defined: {functions}")
    
    # Fix 1: Remove UnifiedBackend from import if it doesn't exist
    if 'UnifiedBackend' in imported_items and 'UnifiedBackend' not in classes:
        print("\n🔧 Fix 1: Removing UnifiedBackend from import")
        
        # Remove UnifiedBackend from the import
        new_backend_content = re.sub(
            r'from \.engine import \([^)]+\)',
            lambda m: m.group(0).replace('UnifiedBackend,', '').replace(', UnifiedBackend', '').replace('UnifiedBackend', ''),
            backend_content
        )
        
        # Also check if it's used anywhere
        if 'UnifiedBackend' in new_backend_content and 'from .engine import' in new_backend_content:
            print("   ⚠️  UnifiedBackend is still referenced in the code")
            # Replace usage with NixForHumanityBackend
            new_backend_content = new_backend_content.replace('UnifiedBackend', 'NixForHumanityBackend')
        
        with open(backend_file, 'w') as f:
            f.write(new_backend_content)
        
        print("   ✅ Fixed backend.py imports")
    
    # Fix 2: Check core/__init__.py for circular imports
    core_init = Path('src/nix_humanity/core/__init__.py')
    with open(core_init) as f:
        core_init_content = f.read()
    
    print(f"\n📄 {core_init}:")
    
    # Look for potential circular imports
    if 'from .backend import' in core_init_content and 'from .engine import' in core_init_content:
        print("   ⚠️  Both backend and engine imported in __init__.py")
        print("   This can cause circular imports if they import each other")
        
        # Reorder imports to avoid circularity
        new_init_content = '''"""Core functionality for Nix for Humanity."""

# Import order matters to avoid circular imports
from .intent import Intent, IntentType
from .knowledge_base import KnowledgeBase
from .executor import SafeExecutor

# Import engine before backend since backend depends on engine
from .engine import NixForHumanityBackend, create_backend
# Don't import from backend if it just re-exports from engine

# Legacy exports for compatibility
NixForHumanityEngine = NixForHumanityBackend

__all__ = [
    'Intent',
    'IntentType', 
    'KnowledgeBase',
    'SafeExecutor',
    'NixForHumanityBackend',
    'NixForHumanityEngine',
    'create_backend'
]
'''
        
        with open(core_init, 'w') as f:
            f.write(new_init_content)
        
        print("   ✅ Fixed core/__init__.py import order")
    
    # Fix 3: Check if backend.py is just a thin wrapper
    print("\n🔍 Checking if backend.py is redundant...")
    
    # Count actual code in backend.py (not imports/comments)
    code_lines = [line for line in backend_content.split('\n') 
                  if line.strip() and not line.strip().startswith(('#', 'from', 'import', '"""'))]
    
    print(f"   Code lines in backend.py: {len(code_lines)}")
    if len(code_lines) < 5:
        print("   💡 backend.py appears to be just a re-export file")
    
    # Fix 4: Update any files that import UnifiedBackend
    print("\n🔍 Checking for other UnifiedBackend references...")
    
    for py_file in Path('src').rglob('*.py'):
        try:
            with open(py_file) as f:
                content = f.read()
            
            if 'UnifiedBackend' in content:
                print(f"   Found in: {py_file}")
                
                # Replace with NixForHumanityBackend
                new_content = content.replace('UnifiedBackend', 'NixForHumanityBackend')
                
                with open(py_file, 'w') as f:
                    f.write(new_content)
                
                print(f"   ✅ Fixed {py_file}")
        except Exception as e:
            print(f"   ❌ Error processing {py_file}: {e}")
    
    print("\n✅ Circular import fixes complete!")
    print("\nNext steps:")
    print("1. Test imports: python3 -c 'import nix_humanity'")
    print("2. Run natural language tests")

if __name__ == '__main__':
    fix_circular_imports()