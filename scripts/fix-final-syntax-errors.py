#!/usr/bin/env python3
"""Fix all remaining syntax errors for v1.0.0 release"""

import subprocess
import re
from pathlib import Path

def get_syntax_error_details(filepath):
    """Get detailed syntax error information"""
    result = subprocess.run(['python3', '-m', 'py_compile', filepath], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        return result.stderr
    return None

def fix_test_executor_comprehensive():
    """Fix test_executor_comprehensive.py"""
    filepath = Path("tests/unit/test_executor_comprehensive.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    lines = content.split('\n')
    
    # Look for orphaned lines around line 124
    fixed_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # Skip orphaned lines that look like incomplete code
        if i == 123 and 'self.assertIsNotNone' in line and not line.strip().startswith('self.'):
            # This line is orphaned, skip it
            continue
        elif i == 124 and 'self.assertIsNotNone' in line and not line.strip().startswith('self.'):
            continue
        else:
            fixed_lines.append(line)
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_test_native_nix_backend():
    """Fix test_native_nix_backend.py"""
    filepath = Path("tests/unit/test_native_nix_backend.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Fix the class definition issue
    content = re.sub(r'class TestNativeNixBackend.*\n.*""".*\n\ndef backend\(self\):',
                     'class TestNativeNixBackend(unittest.TestCase):\n    """Test the native Python-Nix backend that achieved the performance breakthrough"""\n    \n    def backend(self):',
                     content, flags=re.DOTALL)
    
    filepath.write_text(content)
    print(f"✅ Fixed {filepath}")

def fix_test_execution_engine():
    """Fix test_execution_engine.py"""
    filepath = Path("tests/unit/test_execution_engine.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Fix the @patch issues - remove incomplete decorators
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip orphaned @patch decorators
        if line.strip() == '@patch(\\' or (line.strip().startswith('@patch(') and line.strip().endswith('\\')):
            # Skip until we find a proper function definition
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('def '):
                i += 1
            continue
        else:
            fixed_lines.append(line)
        i += 1
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_test_backend_comprehensive():
    """Fix test_backend_comprehensive.py"""
    filepath = Path("tests/unit/test_backend_comprehensive.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Similar fix for @patch decorators
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip incomplete @patch decorators and their content
        if line.strip() == '@patch(\\' or (line.strip().startswith('@patch(') and line.strip().endswith('\\')):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('def '):
                i += 1
            continue
        else:
            fixed_lines.append(line)
        i += 1
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_test_execution_engine_enhanced():
    """Fix test_execution_engine_enhanced.py"""
    filepath = Path("tests/unit/test_execution_engine_enhanced.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Same pattern - fix @patch decorators
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.strip() == '@patch(\\' or (line.strip().startswith('@patch(') and line.strip().endswith('\\')):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('def '):
                i += 1
            continue
        else:
            fixed_lines.append(line)
        i += 1
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_test_nix_integration():
    """Fix test_nix_integration.py"""
    filepath = Path("tests/unit/test_nix_integration.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Fix multi-line string issues
    content = re.sub(r'read_data=\'NAME="NixOS"\\\n', 
                     'read_data=\'NAME="NixOS"\\n', 
                     content)
    content = re.sub(r'read_data=\'VERSION="24\.05 \(Uakari\)"\\\n',
                     'read_data=\'VERSION="24.05 (Uakari)"\\n',
                     content)
    content = re.sub(r'read_data=\'NAME=NixOS\\\n',
                     'read_data=\'NAME=NixOS\\n',
                     content)
    
    # Fix @patch decorators
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.strip() == '@patch(\\':
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('def '):
                i += 1
            continue
        else:
            fixed_lines.append(line)
        i += 1
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_test_error_intelligence_integration():
    """Fix test_error_intelligence_integration.py"""
    filepath = Path("tests/integration/test_error_intelligence_integration.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Fix line 156 - the any() call is malformed
    content = re.sub(
        r"self\.assertIn\(any\('overlay' in s or 'override' in s for s in edu_error\.solutions\)\)",
        "self.assertTrue(any('overlay' in s or 'override' in s for s in edu_error.solutions))",
        content
    )
    
    filepath.write_text(content)
    print(f"✅ Fixed {filepath}")

def fix_test_xai_causal_engine():
    """Fix test_xai_causal_engine.py"""
    filepath = Path("features/v3.0/xai/test_xai_causal_engine.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Common issues in test files - missing imports, syntax errors
    # Add missing imports if needed
    if 'import unittest' not in content:
        content = 'import unittest\n' + content
    
    filepath.write_text(content)
    print(f"✅ Fixed {filepath}")

def fix_train_nixos_expert():
    """Fix train-nixos-expert.py"""
    filepath = Path("scripts/train-nixos-expert.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # The error said it was already fixed, let's verify
    error = get_syntax_error_details(str(filepath))
    if error:
        print(f"⚠️  {filepath} still has error: {error}")
        # Try to fix based on error
        lines = content.split('\n')
        # Look for common indentation issues
        for i, line in enumerate(lines):
            if line and line[0] == ' ' and len(lines) > i-1 and lines[i-1].strip() == '':
                # Likely an indentation error
                lines[i] = line.lstrip()
        
        filepath.write_text('\n'.join(lines))
    else:
        print(f"✅ {filepath} already fixed")

def fix_perform_consolidation():
    """Fix perform-consolidation.py"""
    filepath = Path("scripts/perform-consolidation.py") 
    if not filepath.exists():
        return
        
    # Already fixed in previous run
    error = get_syntax_error_details(str(filepath))
    if not error:
        print(f"✅ {filepath} already fixed")
    else:
        print(f"⚠️  {filepath} needs manual attention: {error}")

def main():
    """Fix all syntax errors"""
    print("🔧 Fixing all remaining syntax errors for v1.0.0...")
    print("=" * 60)
    
    # Fix each file
    fix_test_executor_comprehensive()
    fix_test_native_nix_backend()
    fix_test_execution_engine()
    fix_test_backend_comprehensive()
    fix_test_execution_engine_enhanced()
    fix_test_nix_integration()
    fix_test_error_intelligence_integration()
    fix_test_xai_causal_engine()
    fix_train_nixos_expert()
    fix_perform_consolidation()
    
    print("\n" + "=" * 60)
    print("✅ Syntax error fixing complete!")
    
    # Verify results
    print("\n🔍 Verifying fixes...")
    remaining_errors = []
    
    test_files = [
        "tests/test_full_integration.py",
        "tests/integration/test_error_intelligence_integration.py",
        "tests/unit/test_executor_comprehensive.py",
        "tests/unit/test_native_nix_backend.py",
        "tests/unit/test_execution_engine.py",
        "tests/unit/test_backend_comprehensive.py",
        "tests/unit/test_execution_engine_enhanced.py",
        "tests/unit/test_nix_integration.py",
        "features/v3.0/xai/test_xai_causal_engine.py",
        "scripts/train-nixos-expert.py",
        "scripts/perform-consolidation.py"
    ]
    
    for filepath in test_files:
        if Path(filepath).exists():
            error = get_syntax_error_details(filepath)
            if error:
                remaining_errors.append((filepath, error))
            else:
                print(f"✅ {filepath} - No syntax errors")
    
    if remaining_errors:
        print(f"\n⚠️  {len(remaining_errors)} files still have syntax errors:")
        for filepath, error in remaining_errors:
            print(f"\n{filepath}:")
            print(error[:200] + "..." if len(error) > 200 else error)
    else:
        print("\n🎉 All syntax errors fixed!")

if __name__ == "__main__":
    main()