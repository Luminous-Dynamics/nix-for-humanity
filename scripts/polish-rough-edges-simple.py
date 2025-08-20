#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List
Simplified Polish Rough Edges - Focus on key issues in Nix for Humanity
"""

import os
import sys
import re
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files in the project"""
    python_files = []
    exclude_dirs = {'__pycache__', '.git', 'venv', 'env', '.venv', 
                   'node_modules', 'dist', 'build', '.pytest_cache',
                   'docs', 'archive', 'deprecated'}
    
    for path in root.rglob('*.py'):
        # Skip if in excluded directory
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue
        python_files.append(path)
    
    return sorted(python_files)


def check_syntax_errors(files: List[Path]) -> List[Tuple[Path, str]]:
    """Check for Python syntax errors"""
    errors = []
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
        except SyntaxError as e:
            errors.append((file, f"Syntax error at line {e.lineno}: {e.msg}"))
        except Exception as e:
            errors.append((file, f"Error parsing: {str(e)}"))
    
    return errors


def find_todos_and_fixmes(files: List[Path]) -> List[Tuple[Path, int, str]]:
    """Find TODO, FIXME, HACK comments"""
    findings = []
    
    patterns = ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG']
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in patterns:
                        if pattern in line and '#' in line:
                            findings.append((file, line_num, line.strip()))
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
    
    return findings


def find_incomplete_implementations(files: List[Path]) -> List[Tuple[Path, int, str]]:
    """Find incomplete implementations"""
    findings = []
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for NotImplementedError
            for line_num, line in enumerate(content.splitlines(), 1):
                if 'NotImplementedError' in line:
                    findings.append((file, line_num, "NotImplementedError"))
                elif 'pass  # TODO' in line or 'pass # implement' in line:
                    findings.append((file, line_num, "Empty implementation"))
                elif '...' in line and 'def ' in content.splitlines()[max(0, line_num-2)]:
                    findings.append((file, line_num, "Ellipsis placeholder"))
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
    
    return findings


def check_missing_imports(files: List[Path]) -> List[Tuple[Path, str]]:
    """Check for potentially missing imports"""
    missing = []
    
    # Common imports that should be present
    expected_imports = {
        'backend.py': ['typing', 'pathlib'],
        'executor.py': ['subprocess', 'shlex'],
        'nlp.py': ['re', 'difflib'],
        'test_': ['pytest', 'unittest'],
    }
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for common missing imports based on usage
            if 'Path(' in content and 'from pathlib import' not in content:
                missing.append((file, "Missing: from pathlib import Path"))
            if 'Dict[' in content and 'from typing import' not in content:
                missing.append((file, "Missing: from typing import Dict"))
            if 'subprocess.' in content and 'import subprocess' not in content:
                missing.append((file, "Missing: import subprocess"))
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
    
    return missing


def check_error_handling(files: List[Path]) -> List[Tuple[Path, int, str]]:
    """Check for poor error handling"""
    issues = []
    
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                # Bare except
                if re.match(r'^\s*except\s*:', line):
                    issues.append((file, i+1, "Bare except clause"))
                    
                # Empty except block
                if 'except' in line and i+1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line == 'pass':
                        issues.append((file, i+1, "Empty except block"))
                        
                # Print in except without re-raise
                if 'except' in line and i+1 < len(lines):
                    next_line = lines[i+1]
                    if 'print(' in next_line and 'raise' not in lines[i+1:i+5]:
                        issues.append((file, i+1, "Exception printed but not re-raised"))
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
    
    return issues


def run_pytest_summary() -> Dict[str, int]:
    """Run pytest and get summary statistics"""
    stats = {}
    
    try:
        result = subprocess.run(
            ['pytest', '--tb=no', '-q', '--no-header'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        output = result.stdout + result.stderr
        
        # Parse summary line
        if 'failed' in output:
            match = re.search(r'(\d+) failed', output)
            if match:
                stats['failed'] = int(match.group(1))
                
        if 'passed' in output:
            match = re.search(r'(\d+) passed', output)
            if match:
                stats['passed'] = int(match.group(1))
                
        if 'skipped' in output:
            match = re.search(r'(\d+) skipped', output)
            if match:
                stats['skipped'] = int(match.group(1))
                
        if 'error' in output:
            match = re.search(r'(\d+) error', output)
            if match:
                stats['errors'] = int(match.group(1))
                
    except Exception as e:
        stats['error'] = str(e)
    
    return stats


def check_critical_files() -> List[Tuple[str, str]]:
    """Check critical files for known issues"""
    issues = []
    project_root = Path(__file__).parent.parent
    
    # Critical files to check
    critical_files = {
        'src/luminous_nix/core/backend.py': 'Core backend functionality',
        'src/luminous_nix/core/executor.py': 'Command execution',
        'src/luminous_nix/ai/nlp.py': 'Natural language processing',
        'src/luminous_nix/nix/native_backend.py': 'Native Nix integration',
        'bin/ask-nix': 'Main CLI entry point',
        'bin/nix-tui': 'TUI entry point',
    }
    
    for file_path, description in critical_files.items():
        full_path = project_root / file_path
        if not full_path.exists():
            issues.append((file_path, f"Missing critical file: {description}"))
        elif full_path.stat().st_size < 100:
            issues.append((file_path, f"Suspiciously small file: {description}"))
    
    return issues


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    print("🔍 Nix for Humanity - Rough Edges Analysis")
    print("=" * 80)
    
    # Find all Python files
    python_files = find_python_files(project_root)
    print(f"\n📁 Found {len(python_files)} Python files")
    
    # Check for syntax errors
    print("\n🚨 Checking for syntax errors...")
    syntax_errors = check_syntax_errors(python_files)
    if syntax_errors:
        print(f"❌ Found {len(syntax_errors)} files with syntax errors:")
        for file, error in syntax_errors[:5]:  # Show first 5
            print(f"   - {file.relative_to(project_root)}: {error}")
        if len(syntax_errors) > 5:
            print(f"   ... and {len(syntax_errors) - 5} more")
    else:
        print("✅ No syntax errors found")
    
    # Check critical files
    print("\n🔑 Checking critical files...")
    critical_issues = check_critical_files()
    if critical_issues:
        print(f"❌ Found {len(critical_issues)} critical file issues:")
        for file, issue in critical_issues:
            print(f"   - {file}: {issue}")
    else:
        print("✅ All critical files present")
    
    # Find TODOs and FIXMEs
    print("\n📝 Scanning for TODOs and FIXMEs...")
    todos = find_todos_and_fixmes(python_files)
    todo_counts = defaultdict(int)
    for _, _, line in todos:
        for tag in ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG']:
            if tag in line:
                todo_counts[tag] += 1
    
    if todo_counts:
        print("Found technical debt markers:")
        for tag, count in sorted(todo_counts.items()):
            print(f"   - {tag}: {count}")
    
    # Find incomplete implementations
    print("\n🚧 Scanning for incomplete implementations...")
    incomplete = find_incomplete_implementations(python_files)
    if incomplete:
        print(f"❌ Found {len(incomplete)} incomplete implementations:")
        for file, line, issue in incomplete[:5]:
            print(f"   - {file.relative_to(project_root)}:{line} - {issue}")
        if len(incomplete) > 5:
            print(f"   ... and {len(incomplete) - 5} more")
    else:
        print("✅ No obvious incomplete implementations")
    
    # Check error handling
    print("\n⚠️  Checking error handling...")
    error_issues = check_error_handling(python_files)
    if error_issues:
        print(f"Found {len(error_issues)} error handling issues:")
        issue_types = defaultdict(int)
        for _, _, issue_type in error_issues:
            issue_types[issue_type] += 1
        for issue_type, count in issue_types.items():
            print(f"   - {issue_type}: {count}")
    
    # Check missing imports
    print("\n📦 Checking for missing imports...")
    missing_imports = check_missing_imports(python_files)
    if missing_imports:
        print(f"Found {len(missing_imports)} potential missing imports")
    
    # Run pytest summary
    print("\n🧪 Running test summary...")
    test_stats = run_pytest_summary()
    if 'error' in test_stats:
        print(f"❌ Could not run tests: {test_stats['error']}")
    else:
        print("Test results:")
        for stat, count in test_stats.items():
            emoji = "✅" if stat == "passed" else "❌" if stat == "failed" else "⚠️"
            print(f"   {emoji} {stat}: {count}")
    
    # Priority recommendations
    print("\n🎯 Priority Recommendations:")
    print("=" * 80)
    
    priority = 1
    
    if syntax_errors:
        print(f"{priority}. Fix {len(syntax_errors)} syntax errors - These prevent code from running")
        priority += 1
        
    if critical_issues:
        print(f"{priority}. Address {len(critical_issues)} critical file issues")
        priority += 1
        
    if test_stats.get('failed', 0) > 0:
        print(f"{priority}. Fix {test_stats['failed']} failing tests")
        priority += 1
        
    if incomplete:
        print(f"{priority}. Complete {len(incomplete)} unimplemented features")
        priority += 1
        
    if error_issues:
        print(f"{priority}. Improve error handling in {len(set(f for f, _, _ in error_issues))} files")
        priority += 1
        
    if todo_counts.get('FIXME', 0) > 0:
        print(f"{priority}. Address {todo_counts['FIXME']} FIXME items")
        priority += 1
    
    print("\n✨ Focus on fixing syntax errors and failing tests first!")
    print("📋 Then work through incomplete implementations and error handling.")
    
    # Generate summary report
    report_path = project_root / "rough-edges-summary.txt"
    with open(report_path, 'w') as f:
        f.write("Nix for Humanity - Rough Edges Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Syntax Errors: {len(syntax_errors)}\n")
        f.write(f"Critical Issues: {len(critical_issues)}\n")
        f.write(f"Failing Tests: {test_stats.get('failed', 'Unknown')}\n")
        f.write(f"Incomplete Implementations: {len(incomplete)}\n")
        f.write(f"Error Handling Issues: {len(error_issues)}\n")
        f.write(f"TODOs: {todo_counts.get('TODO', 0)}\n")
        f.write(f"FIXMEs: {todo_counts.get('FIXME', 0)}\n")
        
    print(f"\n📄 Summary saved to: {report_path}")


if __name__ == "__main__":
    main()