#!/usr/bin/env python3
"""
Fix v1.0 imports - Remove dependencies on features moved to features/ directory
"""

import os
import re
from pathlib import Path

# List of imports that should be removed or replaced for v1.0
REMOVED_IMPORTS = [
    # Research-based components moved to features/
    r'from \.\.knowledge_graph\.skg import',
    r'from \.\.trust_modeling\.trust_engine import',
    r'from \.\.consciousness_metrics\.sacred_metrics import',
    r'from \.\.perception\.activity_monitor import',
    r'from \.\.sacred_development\.consciousness_first import',
    r'from features\.',
    r'from \.\.\.features\.',
    # Voice interface (v2.0)
    r'from .*voice.*import',
    r'import.*voice',
    # XAI features (v3.0)
    r'from .*xai.*import',
    r'import.*xai',
    # Advanced learning (v3.0)
    r'from .*advanced_learning.*import',
    # Multi-modal (v2.0)
    r'from .*multi_modal.*import',
]

# Files to check in v1.0 scope
V1_DIRECTORIES = [
    'backend/core',
    'backend/api',
    'backend/security',
    'backend/learning',  # Basic learning only
    'backend/ui',  # Simple UI only
    'bin',
    'tests/unit',
    'tests/integration',
    'tests/v1.0',
    'frontends/cli',
    'tui',  # Simple TUI
]

def fix_imports_in_file(file_path):
    """Fix imports in a single Python file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    original_content = content
    changes = []
    
    # Remove or comment out removed imports
    for pattern in REMOVED_IMPORTS:
        if re.search(pattern, content):
            # Comment out instead of removing to preserve context
            content = re.sub(f'^({pattern}.*)$', r'# v2.0+ feature: \1', content, flags=re.MULTILINE)
            changes.append(f"Commented out: {pattern}")
    
    # Fix research component imports to use mocks or graceful fallback
    if 'SKG_AVAILABLE' in content:
        # Already has fallback logic
        pass
    else:
        # Add fallback for research components
        research_imports = [
            ('SymbioticKnowledgeGraph', 'knowledge_graph.skg'),
            ('TrustEngine', 'trust_modeling.trust_engine'),
            ('SacredMetricsCollector', 'consciousness_metrics.sacred_metrics'),
            ('ActivityMonitor', 'perception.activity_monitor'),
            ('ConsciousnessGuard', 'sacred_development.consciousness_first'),
        ]
        
        for class_name, module_path in research_imports:
            if class_name in content and f'from ..{module_path}' not in content:
                # Add graceful fallback
                fallback = f"""
# v1.0: Graceful fallback for research components
try:
    from ..{module_path} import {class_name}
    {class_name.upper()}_AVAILABLE = True
except ImportError:
    {class_name.upper()}_AVAILABLE = False
    # Simple mock for v1.0
    class {class_name}:
        def __init__(self, *args, **kwargs):
            pass
"""
                # Find a good place to insert (after imports)
                import_section_end = content.rfind('\nimport')
                if import_section_end > 0:
                    next_newline = content.find('\n\n', import_section_end)
                    if next_newline > 0:
                        content = content[:next_newline] + fallback + content[next_newline:]
                        changes.append(f"Added fallback for {class_name}")
    
    # Fix circular dependencies
    content = fix_circular_imports(content)
    
    if content != original_content:
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Fixed {file_path}")
            for change in changes:
                print(f"   - {change}")
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return False
    
    return False

def fix_circular_imports(content):
    """Fix common circular import patterns"""
    # Move imports inside functions if they cause circular dependencies
    circular_patterns = [
        # Example: from .executor import SafeExecutor in a file that executor imports
        (r'^from \.executor import SafeExecutor$', 'def get_executor():\n    from .executor import SafeExecutor\n    return SafeExecutor'),
    ]
    
    for pattern, replacement in circular_patterns:
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(pattern, f'# Moved inside function to avoid circular import\n# {pattern}', content, flags=re.MULTILINE)
    
    return content

def fix_init_files():
    """Fix __init__.py files to only export v1.0 components"""
    v1_exports = {
        'backend/core/__init__.py': [
            'NixForHumanityBackend',
            'IntentRecognizer', 'Intent', 'IntentType',
            'SafeExecutor',
            'KnowledgeBase',
            'ErrorHandler',
            'PersonalitySystem',
        ],
        'backend/api/__init__.py': [
            'Request', 'Response', 'Result',
            'APIServer',
        ],
        'backend/learning/__init__.py': [
            'PreferenceManager',
            'PatternRecognizer',
            'FeedbackCollector',
        ],
        'backend/security/__init__.py': [
            'CommandValidator',
            'PermissionChecker',
            'InputSanitizer',
        ],
    }
    
    for init_file, exports in v1_exports.items():
        if os.path.exists(init_file):
            content = f'''"""
v1.0 exports - Core functionality only
"""

# v1.0 components
{chr(10).join(f"from .{export.lower()} import {export}" for export in exports if '.' not in export)}

__all__ = {exports}
'''
            try:
                with open(init_file, 'w') as f:
                    f.write(content)
                print(f"✅ Updated {init_file} with v1.0 exports only")
            except Exception as e:
                print(f"❌ Error updating {init_file}: {e}")

def main():
    """Main function to fix all imports"""
    print("🔧 Fixing v1.0 imports...")
    print("=" * 60)
    
    # First, fix __init__.py files
    print("\n📦 Updating __init__.py files...")
    fix_init_files()
    
    # Then fix imports in all Python files
    print("\n🔍 Scanning Python files...")
    fixed_count = 0
    total_count = 0
    
    for directory in V1_DIRECTORIES:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            # Skip test mocks and fixtures
            if 'mock' in root or 'fixture' in root:
                continue
                
            for file in files:
                if file.endswith('.py') and file != 'fix_v1_imports.py':
                    total_count += 1
                    file_path = os.path.join(root, file)
                    if fix_imports_in_file(file_path):
                        fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Fixed {fixed_count}/{total_count} files")
    print("\n📋 Next steps:")
    print("1. Run tests to verify no functionality is broken")
    print("2. Update any remaining broken imports manually")
    print("3. Ensure all v1.0 features work without v2.0+ dependencies")

if __name__ == '__main__':
    main()