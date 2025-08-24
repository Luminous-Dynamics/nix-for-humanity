#!/usr/bin/env python3
"""Fix remaining syntax errors in test files"""

import re
from pathlib import Path

def fix_perform_consolidation():
    """Fix scripts/perform-consolidation.py"""
    path = Path("scripts/perform-consolidation.py")
    content = path.read_text()
    
    # Look for line 39 issue
    lines = content.split('\n')
    if len(lines) > 38:
        # Check for common issues: missing quotes, parens, etc.
        if 'print(' in lines[38] and not lines[38].strip().endswith(')'):
            lines[38] = lines[38].rstrip() + ')'
    
    path.write_text('\n'.join(lines))
    print(f"✅ Fixed {path}")

def fix_test_files():
    """Fix test file syntax errors"""
    
    # Fix test_full_integration.py line 26
    path = Path("tests/test_full_integration.py")
    if path.exists():
        content = path.read_text()
        lines = content.split('\n')
        if len(lines) > 25:
            # Common issue: missing colon after def or class
            if 'def ' in lines[25] and not lines[25].strip().endswith(':'):
                lines[25] = lines[25].rstrip() + ':'
        path.write_text('\n'.join(lines))
        print(f"✅ Fixed {path}")
    
    # Fix test_research_components_simple.py line 87
    path = Path("tests/test_research_components_simple.py") 
    if path.exists():
        content = path.read_text()
        lines = content.split('\n')
        if len(lines) > 86:
            # Check for unclosed strings or brackets
            if lines[86].count('"') % 2 == 1:
                lines[86] = lines[86] + '"'
            elif lines[86].count("'") % 2 == 1:
                lines[86] = lines[86] + "'"
        path.write_text('\n'.join(lines))
        print(f"✅ Fixed {path}")
    
    # Fix test_component_integration.py line 77
    path = Path("tests/test_component_integration.py")
    if path.exists():
        content = path.read_text()
        lines = content.split('\n') 
        if len(lines) > 76:
            # Check for missing closing bracket/paren
            if lines[76].count('(') > lines[76].count(')'):
                lines[76] = lines[76] + ')'
            elif lines[76].count('[') > lines[76].count(']'):
                lines[76] = lines[76] + ']'
        path.write_text('\n'.join(lines))
        print(f"✅ Fixed {path}")
    
    # Fix test_error_intelligence_integration.py line 154
    path = Path("tests/integration/test_error_intelligence_integration.py")
    if path.exists():
        content = path.read_text()
        lines = content.split('\n')
        if len(lines) > 153:
            # "Perhaps you forgot a comma" - likely in a dict or list
            if '{' in lines[153] or '[' in lines[153]:
                # Add comma before line end if missing
                if not lines[153].rstrip().endswith(',') and not lines[153].rstrip().endswith('{') and not lines[153].rstrip().endswith('['):
                    lines[153] = lines[153].rstrip() + ','
        path.write_text('\n'.join(lines))
        print(f"✅ Fixed {path}")
    
    # Fix test_executor_comprehensive.py line 124 (unexpected indent)
    path = Path("tests/unit/test_executor_comprehensive.py")
    if path.exists():
        content = path.read_text()
        lines = content.split('\n')
        if len(lines) > 123:
            # Remove extra indentation
            if lines[123].startswith('    '):
                # Check if previous line suggests this should be less indented
                if len(lines) > 122 and not lines[122].strip().endswith(':'):
                    lines[123] = lines[123][4:]  # Remove 4 spaces
        path.write_text('\n'.join(lines))
        print(f"✅ Fixed {path}")
    
    # Fix test_native_nix_backend.py line 37 (unexpected indent)
    path = Path("tests/unit/test_native_nix_backend.py")
    if path.exists():
        content = path.read_text()
        lines = content.split('\n')
        if len(lines) > 36:
            # Remove extra indentation
            if lines[36].startswith('    '):
                if len(lines) > 35 and not lines[35].strip().endswith(':'):
                    lines[36] = lines[36][4:]  # Remove 4 spaces
        path.write_text('\n'.join(lines))
        print(f"✅ Fixed {path}")
    
    # Fix test_cli_adapter_comprehensive_v2.py line 141
    path = Path("tests/unit/test_cli_adapter_comprehensive_v2.py")
    if path.exists():
        content = path.read_text()
        lines = content.split('\n')
        if len(lines) > 140:
            # "cannot assign to function call" - likely foo() = bar instead of foo() == bar
            lines[140] = lines[140].replace('() =', '() ==')
        path.write_text('\n'.join(lines))
        print(f"✅ Fixed {path}")

def main():
    print("🔧 Fixing remaining syntax errors...")
    
    fix_perform_consolidation()
    fix_test_files()
    
    print("\n✅ Manual fixes applied!")
    
    # Verify fixes
    print("\n🔍 Verifying fixes...")
    import subprocess
    
    files_to_check = [
        "scripts/perform-consolidation.py",
        "tests/test_full_integration.py",
        "tests/test_research_components_simple.py",
        "tests/test_component_integration.py", 
        "tests/integration/test_error_intelligence_integration.py",
        "tests/unit/test_executor_comprehensive.py",
        "tests/unit/test_native_nix_backend.py",
        "tests/unit/test_cli_adapter_comprehensive_v2.py"
    ]
    
    still_broken = []
    for file in files_to_check:
        if Path(file).exists():
            result = subprocess.run(['python3', '-m', 'py_compile', file], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                still_broken.append(file)
                print(f"❌ {file} still has errors")
            else:
                print(f"✅ {file} compiles successfully")
    
    if still_broken:
        print(f"\n⚠️  {len(still_broken)} files still have syntax errors")
    else:
        print("\n🎉 All syntax errors fixed!")

if __name__ == "__main__":
    main()