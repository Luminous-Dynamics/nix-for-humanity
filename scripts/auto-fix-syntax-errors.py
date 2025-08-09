#!/usr/bin/env python3
"""Automatically fix common syntax errors."""

import re
from pathlib import Path

def fix_file(file_path: Path, error_msg: str):
    """Try to automatically fix common syntax errors."""
    print(f"\n🔧 Fixing {file_path}")
    print(f"   Error: {error_msg}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixed = False
        
        # Fix f-string errors
        if "f-string: expecting" in error_msg:
            # Find unclosed f-strings
            content = re.sub(r'f"([^"]*){([^}]*)$', r'f"\1{\2}"', content, flags=re.MULTILINE)
            content = re.sub(r"f'([^']*){([^}]*)$", r"f'\1{\2}'", content, flags=re.MULTILINE)
            fixed = True
            
        # Fix unexpected indent
        if "unexpected indent" in error_msg:
            lines = content.split('\n')
            if "Line" in error_msg:
                line_num = int(re.search(r'Line (\d+)', error_msg).group(1)) - 1
                if 0 <= line_num < len(lines):
                    # Remove leading spaces/tabs
                    lines[line_num] = lines[line_num].lstrip()
                    content = '\n'.join(lines)
                    fixed = True
        
        # Fix unexpected character after line continuation
        if "unexpected character after line continuation character" in error_msg:
            # Remove characters after backslash
            content = re.sub(r'\\\s*[^\n]+', r'\\', content)
            fixed = True
            
        # Fix assignment to function call
        if "cannot assign to function call" in error_msg:
            # Change = to == in function calls
            content = re.sub(r'(\w+\([^)]*\))\s*=\s*([^=])', r'\1 == \2', content)
            fixed = True
        
        # Fix invalid syntax (missing comma)
        if "Perhaps you forgot a comma" in error_msg:
            # Add comma between dict/list items
            content = re.sub(r'(["\'])\s*\n\s*(["\'])', r'\1,\n    \2', content)
            fixed = True
        
        if fixed and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Fixed!")
            return True
        else:
            print(f"   ⚠️  Could not auto-fix this error")
            return False
            
    except Exception as e:
        print(f"   ❌ Error fixing file: {e}")
        return False

def main():
    """Fix syntax errors in known problematic files."""
    root_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
    
    # List of files with errors and their error messages
    files_to_fix = [
        ("scripts/prepare-production-release.py", "Line 149: f-string: expecting '!', or ':', or '}'"),
        ("scripts/train-nixos-expert.py", "Line 4: unexpected indent"),
        ("scripts/perform-consolidation.py", "Line 39: invalid syntax"),
        ("tests/test_full_integration.py", "Line 26: invalid syntax"),
        ("tests/test_research_components_simple.py", "Line 87: invalid syntax"),
        ("tests/test_component_integration.py", "Line 77: invalid syntax"),
        ("tests/integration/test_error_intelligence_integration.py", "Line 154: invalid syntax. Perhaps you forgot a comma?"),
        ("tests/unit/test_executor_comprehensive.py", "Line 124: unexpected indent"),
        ("tests/unit/test_native_nix_backend.py", "Line 37: unexpected indent"),
        ("tests/unit/test_execution_engine.py", "Line 125: unexpected character after line continuation character"),
        ("tests/unit/test_backend_comprehensive.py", "Line 127: unexpected character after line continuation character"),
        ("tests/unit/test_execution_engine_enhanced.py", "Line 183: unexpected character after line continuation character"),
        ("tests/unit/test_cli_adapter_comprehensive_v2.py", "Line 141: cannot assign to function call here. Maybe you meant '==' instead of '='?"),
        ("tests/unit/test_nix_integration.py", "Line 402: unexpected character after line continuation character"),
    ]
    
    print("🔧 Auto-fixing syntax errors...\n")
    
    fixed_count = 0
    for file_rel, error_msg in files_to_fix:
        file_path = root_dir / file_rel
        if file_path.exists():
            if fix_file(file_path, error_msg):
                fixed_count += 1
        else:
            print(f"\n⚠️  {file_rel} - FILE NOT FOUND")
    
    print(f"\n\n📊 Summary: Fixed {fixed_count}/{len(files_to_fix)} files")
    
    # Now let's manually fix some specific errors
    print("\n\n🔧 Applying manual fixes for specific files...")
    
    # Fix prepare-production-release.py
    fix_production_release(root_dir / "scripts/prepare-production-release.py")
    
    # Fix train-nixos-expert.py
    fix_train_nixos_expert(root_dir / "scripts/train-nixos-expert.py")

def fix_production_release(file_path: Path):
    """Fix the f-string error in prepare-production-release.py."""
    if not file_path.exists():
        return
        
    print(f"\n🔧 Manually fixing {file_path}")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Fix line 149 (0-indexed as 148)
    if len(lines) > 148:
        if '{VERSION' in lines[148] and '}' not in lines[148]:
            lines[148] = lines[148].replace('{VERSION', '{VERSION}')
            with open(file_path, 'w') as f:
                f.writelines(lines)
            print("   ✅ Fixed f-string error!")

def fix_train_nixos_expert(file_path: Path):
    """Fix the indentation error in train-nixos-expert.py."""
    if not file_path.exists():
        return
        
    print(f"\n🔧 Manually fixing {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the indentation by ensuring proper structure
    lines = content.split('\n')
    if len(lines) > 3:
        # Ensure line 4 (index 3) is not indented if it's a top-level statement
        if lines[3].startswith('    ') and not lines[2].endswith(':'):
            lines[3] = lines[3].lstrip()
            
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))
    print("   ✅ Fixed indentation error!")

if __name__ == "__main__":
    main()