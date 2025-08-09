#!/usr/bin/env python3
"""Find and fix Python syntax errors in the codebase."""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple

def check_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check if a Python file has syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the project."""
    python_files = []
    
    # Directories to skip
    skip_dirs = {
        '__pycache__', '.git', 'venv', 'env', '.env',
        'node_modules', 'dist', 'build', '.pytest_cache',
        'archive', 'docs', 'experiments', 'training-data',
        'results', 'models', 'data', 'config', 'tui'
    }
    
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def main():
    """Main function to find and report syntax errors."""
    print("🔍 Searching for Python syntax errors...\n")
    
    # Start from the src directory
    root_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
    src_dir = root_dir / "src"
    scripts_dir = root_dir / "scripts"
    bin_dir = root_dir / "bin"
    tests_dir = root_dir / "tests"
    
    # Find all Python files
    all_files = []
    for directory in [src_dir, scripts_dir, bin_dir, tests_dir]:
        if directory.exists():
            all_files.extend(find_python_files(directory))
    
    print(f"Found {len(all_files)} Python files to check\n")
    
    # Check each file
    syntax_errors = []
    for file_path in all_files:
        is_valid, error_msg = check_syntax(file_path)
        if not is_valid:
            relative_path = file_path.relative_to(root_dir)
            syntax_errors.append((relative_path, error_msg))
    
    # Report results
    if syntax_errors:
        print(f"❌ Found {len(syntax_errors)} files with syntax errors:\n")
        for file_path, error in syntax_errors:
            print(f"  • {file_path}")
            print(f"    Error: {error}\n")
    else:
        print("✅ No syntax errors found!")
    
    # Check specific critical files
    print("\n📋 Checking critical files...")
    critical_files = [
        "src/nix_humanity/__init__.py",
        "src/nix_humanity/core/__init__.py",
        "src/nix_humanity/core/engine.py",
        "src/nix_humanity/core/intents.py",
        "src/nix_humanity/core/nlp.py",
        "src/nix_humanity/core/knowledge.py",
        "src/nix_humanity/ui/main_app.py",
        "bin/ask-nix",
        "bin/nix-tui",
    ]
    
    for file_rel in critical_files:
        file_path = root_dir / file_rel
        if file_path.exists():
            is_valid, error_msg = check_syntax(file_path)
            status = "✅" if is_valid else "❌"
            print(f"  {status} {file_rel}")
            if not is_valid:
                print(f"     Error: {error_msg}")
        else:
            print(f"  ⚠️  {file_rel} - FILE NOT FOUND")
    
    return len(syntax_errors)

if __name__ == "__main__":
    error_count = main()
    sys.exit(1 if error_count > 0 else 0)