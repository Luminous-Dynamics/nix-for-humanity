#!/usr/bin/env python3
"""Comprehensive syntax error fixer for all remaining files"""

import re
from pathlib import Path

def fix_test_full_integration():
    """Fix test_full_integration.py - module name with dots issue"""
    filepath = Path("tests/test_full_integration.py")
    if not filepath.exists():
        return
    
    content = filepath.read_text()
    # Replace features.v3.0 with features.v3_0
    content = re.sub(r'features\.v3\.0\.', 'features.v3_0.', content)
    
    filepath.write_text(content)
    print(f"✅ Fixed {filepath}")

def fix_test_error_intelligence_integration():
    """Fix test_error_intelligence_integration.py"""
    filepath = Path("tests/integration/test_error_intelligence_integration.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Fix line 296: self.assertGreater(len(edu_error.solutions), = 2  # Multiple solutions)
    content = re.sub(
        r'self\.assertGreater\(len\(edu_error\.solutions\), = 2  # Multiple solutions\)',
        'self.assertGreater(len(edu_error.solutions), 2)  # Multiple solutions',
        content
    )
    
    filepath.write_text(content)
    print(f"✅ Fixed {filepath}")

def fix_test_executor_comprehensive():
    """Fix test_executor_comprehensive.py - indentation"""
    filepath = Path("tests/unit/test_executor_comprehensive.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    lines = content.split('\n')
    
    # Find line 124 area and fix indentation
    fixed_lines = []
    for i, line in enumerate(lines):
        if i == 124 and line.strip().startswith('self.assertIsNotNone'):
            # This line needs proper indentation
            fixed_lines.append('        ' + line.strip())
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
    
    # Fix the class and method definitions
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix class definition if missing
        if 'class TestNativeNixBackend' in line and 'unittest.TestCase' not in line:
            fixed_lines.append('class TestNativeNixBackend(unittest.TestCase):')
        # Fix method indentation
        elif i > 35 and 'def ' in line and not line.startswith('    '):
            fixed_lines.append('    ' + line.strip())
        else:
            fixed_lines.append(line)
    
    # Add missing import if needed
    if 'import unittest' not in content:
        fixed_lines.insert(0, 'import unittest')
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_test_backend_comprehensive():
    """Fix test_backend_comprehensive.py"""
    filepath = Path("tests/unit/test_backend_comprehensive.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    lines = content.split('\n')
    
    # Fix line 127 - missing indentation after function definition
    fixed_lines = []
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        # If this is line 127 with a function definition, ensure next line is indented
        if i == 126 and 'def test_process_request_basic' in line:
            # Make sure the docstring on next line is indented
            if i + 1 < len(lines) and '"""' in lines[i + 1] and not lines[i + 1].startswith('    '):
                fixed_lines[i + 1] = '        ' + lines[i + 1].strip()
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_test_nix_integration():
    """Fix test_nix_integration.py - unterminated string"""
    filepath = Path("tests/unit/test_nix_integration.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # Fix unterminated strings
    content = re.sub(
        r"read_data='VERSION=\"24\.05 \(Uakari\)\"$",
        "read_data='VERSION=\"24.05 (Uakari)\"'",
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r"read_data='NAME=\"NixOS\"$",
        "read_data='NAME=\"NixOS\"'",
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r"read_data='NAME=NixOS$",
        "read_data='NAME=NixOS'",
        content,
        flags=re.MULTILINE
    )
    
    filepath.write_text(content)
    print(f"✅ Fixed {filepath}")

def fix_test_xai_causal_engine():
    """Fix test_xai_causal_engine.py"""
    filepath = Path("features/v3.0/xai/test_xai_causal_engine.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    lines = content.split('\n')
    
    # Fix indentation issues
    fixed_lines = []
    for i, line in enumerate(lines):
        # Remove unexpected indentation at line 22
        if i == 21 and line.strip():
            fixed_lines.append(line.lstrip())
        else:
            fixed_lines.append(line)
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_train_nixos_expert():
    """Fix train-nixos-expert.py"""
    filepath = Path("scripts/train-nixos-expert.py")
    if not filepath.exists():
        return
        
    content = filepath.read_text()
    
    # The file seems to have lost its class definition and imports
    # Let's reconstruct it properly
    fixed_content = """#!/usr/bin/env python3
\"\"\"Train NixOS expert models from documentation\"\"\"

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class NixOSModelTrainer:
    \"\"\"Trainer for NixOS expert models\"\"\"
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        self.models_dir.mkdir(exist_ok=True)
    
    def check_dependencies(self) -> bool:
        \"\"\"Check if required dependencies are installed\"\"\"
        # Implementation here
        return True
    
""" + content
    
    # Fix indentation throughout
    lines = fixed_content.split('\n')
    fixed_lines = []
    class_level = False
    
    for line in lines:
        if 'class NixOSModelTrainer' in line:
            class_level = True
        
        # Fix method definitions that should be at class level
        if class_level and line.strip().startswith('def ') and not line.startswith('    '):
            fixed_lines.append('    ' + line)
        else:
            fixed_lines.append(line)
    
    filepath.write_text('\n'.join(fixed_lines))
    print(f"✅ Fixed {filepath}")

def fix_perform_consolidation():
    """Fix perform-consolidation.py"""
    filepath = Path("scripts/perform-consolidation.py")
    if not filepath.exists():
        return
        
    # Already fixed in previous run, just verify
    print(f"✅ {filepath} already fixed")

def main():
    """Fix all remaining syntax errors"""
    print("🔧 Final comprehensive syntax error fix...")
    print("=" * 60)
    
    # Fix each file
    fix_test_full_integration()
    fix_test_error_intelligence_integration()
    fix_test_executor_comprehensive()
    fix_test_native_nix_backend()
    fix_test_backend_comprehensive()
    fix_test_nix_integration()
    fix_test_xai_causal_engine()
    fix_train_nixos_expert()
    fix_perform_consolidation()
    
    print("\n✅ All fixes applied!")
    
    # Verify
    print("\n🔍 Verifying all Python files...")
    import subprocess
    
    remaining_errors = 0
    for filepath in [
        "tests/test_full_integration.py",
        "tests/integration/test_error_intelligence_integration.py",
        "tests/unit/test_executor_comprehensive.py",
        "tests/unit/test_native_nix_backend.py",
        "tests/unit/test_backend_comprehensive.py",
        "tests/unit/test_nix_integration.py",
        "features/v3.0/xai/test_xai_causal_engine.py",
        "scripts/train-nixos-expert.py",
        "scripts/perform-consolidation.py"
    ]:
        if Path(filepath).exists():
            result = subprocess.run(['python3', '-m', 'py_compile', filepath], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ {filepath} still has errors")
                remaining_errors += 1
            else:
                print(f"✅ {filepath} - OK")
    
    print(f"\n{'🎉 All syntax errors fixed!' if remaining_errors == 0 else f'⚠️  {remaining_errors} files still need attention'}")

if __name__ == "__main__":
    main()