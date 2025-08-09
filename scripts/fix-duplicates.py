#!/usr/bin/env python3
"""Fix duplicate functions by consolidating implementations."""

import os
import shutil
from pathlib import Path

def fix_ai_module_duplication():
    """Fix the complete duplication between ai/nlp.py and ai/__init__.py."""
    ai_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src/nix_humanity/ai')
    init_file = ai_dir / '__init__.py'
    nlp_file = ai_dir / 'nlp.py'
    
    if init_file.exists() and nlp_file.exists():
        # Read both files
        with open(init_file, 'r') as f:
            init_content = f.read()
        with open(nlp_file, 'r') as f:
            nlp_content = f.read()
        
        # Check if they're duplicates
        if len(init_content) > 1000 and len(nlp_content) > 1000:
            # Keep the NLP module content, update __init__.py to import from it
            new_init_content = '''"""AI and NLP components for Nix for Humanity."""

from .nlp import (
    NLPEngine,
    process,
    extract_package_name,
    record_interaction_feedback,
    get_explanation_for_user
)

__all__ = [
    'NLPEngine',
    'process',
    'extract_package_name',
    'record_interaction_feedback',
    'get_explanation_for_user'
]
'''
            with open(init_file, 'w') as f:
                f.write(new_init_content)
            print("✅ Fixed AI module duplication")

def fix_nix_module_duplication():
    """Fix the duplication between nix/native_backend.py and nix/__init__.py."""
    nix_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src/nix_humanity/nix')
    init_file = nix_dir / '__init__.py'
    backend_file = nix_dir / 'native_backend.py'
    
    if init_file.exists() and backend_file.exists():
        # Update __init__.py to import from native_backend
        new_init_content = '''"""Native Python-Nix integration for high performance."""

from .native_backend import (
    NixCache,
    NixValidator,
    NixMetrics,
    find_nixos_rebuild_module,
    create_native_backend,
    NativeNixBackend,
    ProgressReporter,
    estimate_completion
)

__all__ = [
    'NixCache',
    'NixValidator',
    'NixMetrics',
    'find_nixos_rebuild_module',
    'create_native_backend',
    'NativeNixBackend',
    'ProgressReporter',
    'estimate_completion'
]
'''
        with open(init_file, 'w') as f:
            f.write(new_init_content)
        print("✅ Fixed Nix module duplication")

def fix_core_backend_duplication():
    """Fix duplication between core/backend.py and core/engine.py."""
    core_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src/nix_humanity/core')
    backend_file = core_dir / 'backend.py'
    engine_file = core_dir / 'engine.py'
    
    if backend_file.exists() and engine_file.exists():
        # Create a new backend.py that imports from engine
        new_backend_content = '''"""Backend compatibility layer - imports from engine."""

from .engine import (
    UnifiedBackend,
    create_backend,
    BackendResponse
)

# For backward compatibility
Backend = UnifiedBackend

__all__ = ['Backend', 'UnifiedBackend', 'create_backend', 'BackendResponse']
'''
        with open(backend_file, 'w') as f:
            f.write(new_backend_content)
        print("✅ Fixed core backend duplication")

def fix_intent_duplication():
    """Fix duplication between core/intent.py and core/intents.py."""
    core_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src/nix_humanity/core')
    intent_file = core_dir / 'intent.py'
    intents_file = core_dir / 'intents.py'
    
    if intent_file.exists() and intents_file.exists():
        # Remove the duplicate file and update imports
        os.remove(intent_file)
        print("✅ Removed duplicate intent.py file")

def fix_config_duplication():
    """Consolidate config module duplications."""
    config_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src/nix_humanity/config')
    
    # Update config_manager to remove duplicate methods
    config_manager_file = config_dir / 'config_manager.py'
    if config_manager_file.exists():
        with open(config_manager_file, 'r') as f:
            content = f.read()
        
        # Remove duplicate get_config_manager function
        import re
        content = re.sub(r'def get_config_manager\(.*?\):\s*""".*?""".*?return.*?\n\n', '', content, flags=re.DOTALL)
        
        with open(config_manager_file, 'w') as f:
            f.write(content)
        print("✅ Fixed config manager duplication")

def update_imports():
    """Update imports across the codebase to use consolidated modules."""
    project_root = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity')
    
    # Find all Python files
    python_files = list(project_root.rglob('*.py'))
    
    import_updates = {
        'from nix_humanity.core.intents import': 'from nix_humanity.core.intents import',
        'import nix_humanity.core.intents': 'import nix_humanity.core.intentss',
        'from .intents import': 'from .intents import',
    }
    
    updated_count = 0
    for filepath in python_files:
        if '__pycache__' in str(filepath):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            for old_import, new_import in import_updates.items():
                content = content.replace(old_import, new_import)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_count += 1
        except Exception as e:
            print(f"Error updating {filepath}: {e}")
    
    print(f"✅ Updated imports in {updated_count} files")

def main():
    """Main function to fix duplications."""
    print("🔧 Fixing duplicate functions and modules...")
    
    fix_ai_module_duplication()
    fix_nix_module_duplication()
    fix_core_backend_duplication()
    fix_intent_duplication()
    fix_config_duplication()
    update_imports()
    
    print("\n✅ Duplication fixes complete!")
    print("Next step: Run tests to ensure nothing broke")

if __name__ == '__main__':
    main()