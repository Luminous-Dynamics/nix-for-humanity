#!/usr/bin/env python3
"""Add type hints to functions missing them."""

import ast
import os
from pathlib import Path
from typing import List, Tuple, Set

from typing import List, Tuple, Dict
class TypeHintAdder(ast.NodeTransformer):
    """AST transformer to add type hints to functions."""
    
    def __init__(self):
        self.modified = False
        self.common_types = {
            'filename': 'str',
            'filepath': 'str', 
            'path': 'str',
            'content': 'str',
            'text': 'str',
            'message': 'str',
            'name': 'str',
            'value': 'str',
            'query': 'str',
            'command': 'str',
            'package': 'str',
            'config': 'Dict[str, Any]',
            'data': 'Dict[str, Any]',
            'result': 'Dict[str, Any]',
            'response': 'Dict[str, Any]',
            'options': 'Dict[str, Any]',
            'params': 'Dict[str, Any]',
            'kwargs': 'Dict[str, Any]',
            'args': 'Tuple[Any, ...]',
            'items': 'List[Any]',
            'files': 'List[str]',
            'patterns': 'List[str]',
            'count': 'int',
            'index': 'int',
            'size': 'int',
            'timeout': 'int',
            'port': 'int',
            'enabled': 'bool',
            'success': 'bool',
            'verbose': 'bool',
            'debug': 'bool',
            'force': 'bool',
        }
    
    def visit_FunctionDef(self, node):
        """Add type hints to function definitions."""
        # Skip if already has return type
        if node.returns:
            return self.generic_visit(node)
        
        # Skip special methods
        if node.name.startswith('__') and node.name.endswith('__'):
            return self.generic_visit(node)
        
        # Add parameter type hints
        for arg in node.args.args:
            if not arg.annotation and arg.arg != 'self':
                # Try to infer type from parameter name
                type_hint = self.infer_type(arg.arg)
                if type_hint:
                    arg.annotation = ast.Name(id=type_hint, ctx=ast.Load())
                    self.modified = True
        
        # Add return type hint
        return_type = self.infer_return_type(node)
        if return_type:
            node.returns = ast.Name(id=return_type, ctx=ast.Load())
            self.modified = True
        
        return self.generic_visit(node)
    
    def infer_type(self, param_name: str) -> str:
        """Infer type from parameter name."""
        param_lower = param_name.lower()
        
        # Check common types
        for pattern, type_hint in self.common_types.items():
            if pattern in param_lower:
                return type_hint
        
        # Check for boolean patterns
        if param_lower.startswith(('is_', 'has_', 'should_', 'can_', 'will_')):
            return 'bool'
        
        # Check for list patterns
        if param_lower.endswith('s') and param_lower not in ['success', 'args']:
            return 'List[Any]'
        
        return ''
    
    def infer_return_type(self, node) -> str:
        """Infer return type from function body."""
        # Look for return statements
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                if child.value is None:
                    return 'None'
                elif isinstance(child.value, ast.Constant):
                    if isinstance(child.value.value, bool):
                        return 'bool'
                    elif isinstance(child.value.value, int):
                        return 'int'
                    elif isinstance(child.value.value, str):
                        return 'str'
                elif isinstance(child.value, ast.Dict):
                    return 'Dict[str, Any]'
                elif isinstance(child.value, ast.List):
                    return 'List[Any]'
                elif isinstance(child.value, ast.Tuple):
                    return 'Tuple[Any, ...]'
        
        # Check function name patterns
        name_lower = node.name.lower()
        if name_lower.startswith(('is_', 'has_', 'should_', 'can_', 'check_')):
            return 'bool'
        elif name_lower.startswith('get_') or name_lower.startswith('find_'):
            return 'Any'
        elif name_lower.startswith('create_') or name_lower.startswith('build_'):
            return 'Any'
        
        # Default to None for functions without explicit return
        return 'None'

def add_imports(content: str) -> str:
    """Add necessary imports for type hints."""
    lines = content.split('\n')
    
    # Find where to insert imports
    insert_pos = 0
    has_typing_import = False
    
    for i, line in enumerate(lines):
        if line.startswith('"""') and i > 0:
            # After module docstring
            for j in range(i + 1, len(lines)):
                if not lines[j].strip() or lines[j].startswith('"""'):
                    continue
                insert_pos = j
                break
            break
        elif line.startswith(('import ', 'from ')):
            insert_pos = i + 1
            if 'from typing import' in line:
                has_typing_import = True
    
    # Add typing imports if needed
    if not has_typing_import:
        imports = "from typing import Dict, List, Tuple, Any, Optional, Union"
        lines.insert(insert_pos, imports)
        lines.insert(insert_pos + 1, "")
    
    return '\n'.join(lines)

def process_file(filepath: Path) -> bool:
    """Process a single Python file to add type hints."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Transform the AST
        transformer = TypeHintAdder()
        new_tree = transformer.visit(tree)
        
        if transformer.modified:
            # Add imports
            content = add_imports(content)
            
            # Re-parse with imports
            tree = ast.parse(content)
            transformer = TypeHintAdder()
            new_tree = transformer.visit(tree)
            
            # Convert back to source code
            # Note: This is simplified - in practice you'd need to preserve formatting
            # For now, we'll just mark files that need type hints
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def analyze_type_coverage(project_root: Path) -> Tuple[int, int]:
    """Analyze current type hint coverage."""
    total_functions = 0
    typed_functions = 0
    
    for filepath in project_root.rglob('*.py'):
        if '__pycache__' in str(filepath) or 'venv' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    # Check if has return type or any parameter types
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        typed_functions += 1
                        
        except Exception:
            continue
    
    return typed_functions, total_functions

def main():
    """Main function to add type hints."""
    project_root = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src')
    
    print("📊 Analyzing current type hint coverage...")
    typed, total = analyze_type_coverage(project_root)
    current_coverage = (typed / total * 100) if total > 0 else 0
    print(f"Current coverage: {typed}/{total} functions ({current_coverage:.1f}%)")
    
    # For now, let's add type hints to some key modules
    key_modules = [
        'nix_humanity/core/executor.py',
        'nix_humanity/core/knowledge.py',
        'nix_humanity/core/personality.py',
        'nix_humanity/ai/nlp.py',
        'nix_humanity/learning/patterns.py',
        'nix_humanity/security/validator.py',
    ]
    
    files_to_update = []
    for module in key_modules:
        filepath = project_root / module
        if filepath.exists() and process_file(filepath):
            files_to_update.append(filepath)
    
    # Create a simple script to add basic type hints
    print(f"\n📝 Creating type hint update script...")
    
    script_content = '''#!/usr/bin/env python3
"""Add basic type hints to improve coverage."""

import re
from pathlib import Path

def add_basic_type_hints(filepath: Path) -> None:
    """Add basic type hints to a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add typing import if not present
    if 'from typing import' not in content:
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if line.startswith(('import ', 'from ')) or (i > 0 and not line.strip()):
                lines.insert(i, 'from typing import Dict, List, Optional, Any, Tuple')
                content = '\\n'.join(lines)
                break
    
    # Simple regex replacements for common patterns
    replacements = [
        (r'def (\\w+)\\(self\\):', r'def \\1(self) -> None:'),
        (r'def (\\w+)\\(self, (\\w+)\\):', r'def \\1(self, \\2: Any) -> Any:'),
        (r'def get_(\\w+)\\(self\\):', r'def get_\\1(self) -> Any:'),
        (r'def set_(\\w+)\\(self, value\\):', r'def set_\\1(self, value: Any) -> None:'),
        (r'def is_(\\w+)\\(self\\):', r'def is_\\1(self) -> bool:'),
        (r'def has_(\\w+)\\(self\\):', r'def has_\\1(self) -> bool:'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w') as f:
        f.write(content)

# Add type hints to key files
key_files = [
    'src/nix_humanity/core/executor.py',
    'src/nix_humanity/core/knowledge.py',
    'src/nix_humanity/core/personality.py',
    'src/nix_humanity/learning/patterns.py',
]

for file_path in key_files:
    filepath = Path(file_path)
    if filepath.exists():
        add_basic_type_hints(filepath)
        print(f"✅ Added type hints to {file_path}")
'''
    
    with open('scripts/add-basic-type-hints.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Created add-basic-type-hints.py")
    print("Run: python3 scripts/add-basic-type-hints.py")
    
    # Estimate improvement
    files_with_hints = len(files_to_update)
    estimated_new_typed = typed + (files_with_hints * 10)  # Assume 10 functions per file
    estimated_coverage = (estimated_new_typed / total * 100) if total > 0 else 0
    print(f"\nEstimated coverage after updates: {estimated_coverage:.1f}%")

if __name__ == '__main__':
    main()