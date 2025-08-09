#!/usr/bin/env python3
"""Fix the import structure by creating missing functions and reorganizing."""

from pathlib import Path
import re

from typing import Union, Dict, Optional
def fix_imports():
    """Fix the import structure."""
    
    print("🔧 Fixing Import Structure\n")
    
    # Step 1: Fix AI module - add missing functions
    print("1. Fixing AI module exports...")
    
    nlp_file = Path('src/nix_humanity/ai/nlp.py')
    
    # Read current content
    with open(nlp_file) as f:
        content = f.read()
    
    # Add the missing functions at the end of the file
    missing_functions = '''

# === Export functions for backward compatibility ===

def process(text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Intent]:
    """Process natural language text and return intent.
    
    This is a convenience function that creates an NLPPipeline instance
    and processes the text.
    """
    pipeline = NLPPipeline()
    return pipeline.process_text(text, context)


def extract_package_name(text: str) -> Optional[str]:
    """Extract package name from user input.
    
    Args:
        text: User input text
        
    Returns:
        Extracted package name or None
    """
    # Simple extraction logic
    import re
    
    # Remove common words
    text = text.lower()
    for word in ['install', 'remove', 'search', 'please', 'can', 'you', 'i', 'want', 'to', 'for', 'the']:
        text = text.replace(word, '')
    
    # Look for package-like words
    words = text.strip().split()
    if words:
        # Return the first non-empty word that looks like a package
        for word in words:
            if word and re.match(r'^[a-z][a-z0-9-]*$', word):
                return word
    
    return None


def record_interaction_feedback(intent: Any, success: bool, feedback: Optional[str] = None) -> None:
    """Record user feedback for learning.
    
    Args:
        intent: The processed intent
        success: Whether the operation was successful
        feedback: Optional user feedback
    """
    # TODO: Implement feedback recording for learning system
    pass


def get_explanation_for_user(intent: Any) -> str:
    """Get human-readable explanation of what will happen.
    
    Args:
        intent: The processed intent
        
    Returns:
        Human-readable explanation
    """
    if not intent:
        return "I couldn't understand your request."
    
    explanations = {
        'INSTALL': f"I'll install the {intent.entities.get('package', 'requested package')} for you.",
        'REMOVE': f"I'll remove {intent.entities.get('package', 'the package')} from your system.",
        'SEARCH': f"I'll search for packages matching '{intent.entities.get('query', 'your query')}'.",
        'UPDATE': "I'll update your NixOS system to the latest configuration.",
        'ROLLBACK': "I'll rollback to the previous system generation.",
        'LIST': f"I'll list {intent.entities.get('target', 'the requested items')} for you.",
        'STATUS': f"I'll check the status of {intent.entities.get('target', 'your system')}."
    }
    
    return explanations.get(str(intent.type), f"I'll execute the {intent.type} operation.")
'''
    
    # Check if functions already exist
    if 'def process(' not in content:
        # Add missing imports at the top
        import_section = """
from typing import Dict, Any, List, Optional
from ..core.intents import Intent
"""
        # Insert after existing imports
        import_pos = content.find('import re')
        if import_pos > 0:
            end_of_line = content.find('\n', import_pos)
            content = content[:end_of_line+1] + import_section + content[end_of_line+1:]
        
        # Add functions at the end
        content += missing_functions
        
        # Write back
        with open(nlp_file, 'w') as f:
            f.write(content)
        
        print("   ✅ Added missing functions to nlp.py")
    
    # Step 2: Fix Nix module - remove NixCache import
    print("\n2. Fixing Nix module exports...")
    
    nix_init = Path('src/nix_humanity/nix/__init__.py')
    if nix_init.exists():
        with open(nix_init) as f:
            content = f.read()
        
        # Remove NixCache from imports
        content = re.sub(r',?\s*NixCache', '', content)
        content = re.sub(r'NixCache,?\s*', '', content)
        
        # Also remove from __all__ if present
        content = re.sub(r"'NixCache',?\s*", '', content)
        content = re.sub(r",?\s*'NixCache'", '', content)
        
        with open(nix_init, 'w') as f:
            f.write(content)
        
        print("   ✅ Removed NixCache from nix/__init__.py")
    
    # Step 3: Create a types module for shared types
    print("\n3. Creating shared types module...")
    
    types_file = Path('src/nix_humanity/types.py')
    if not types_file.exists():
        types_content = '''"""Shared types for Nix for Humanity.

This module contains types that are used across multiple modules
to avoid circular dependencies.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum


@dataclass
class BackendResponse:
    """Response from backend operations."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


@dataclass
class CommandResult:
    """Result of executing a command."""
    success: bool
    output: str
    error: Optional[str] = None
    return_code: int = 0


# Type aliases
ConfigDict = Dict[str, Any]
MetricsDict = Dict[str, Union[str, int, float]]
'''
        
        with open(types_file, 'w') as f:
            f.write(types_content)
        
        print("   ✅ Created src/nix_humanity/types.py")
    
    # Step 4: Update imports to use the types module
    print("\n4. Updating imports to use types module...")
    
    files_to_update = [
        'src/nix_humanity/core/engine.py',
        'src/nix_humanity/core/backend.py',
        'src/nix_humanity/core/executor.py'
    ]
    
    for file_path in files_to_update:
        if Path(file_path).exists():
            with open(file_path) as f:
                content = f.read()
            
            # Add types import if BackendResponse is used
            if 'BackendResponse' in content and 'from ..types import' not in content:
                # Add import after other imports
                import_line = 'from ..types import BackendResponse, CommandResult\n'
                
                # Find a good place to insert
                if 'from typing import' in content:
                    pos = content.find('\n', content.find('from typing import'))
                    content = content[:pos+1] + import_line + content[pos+1:]
                else:
                    # Add at the beginning after docstring
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line and not line.startswith(('"""', '#', 'import', 'from')):
                            lines.insert(i, import_line)
                            break
                    content = '\n'.join(lines)
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"   ✅ Updated {Path(file_path).name}")
    
    print("\n✅ Import structure fixes complete!")
    print("\nNext steps:")
    print("1. Test imports: python3 -c 'import nix_humanity.ai'")
    print("2. Run the natural language tests")

if __name__ == '__main__':
    fix_imports()