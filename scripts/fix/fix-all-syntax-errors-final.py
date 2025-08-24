#!/usr/bin/env python3
"""Final comprehensive syntax error fixer"""

import subprocess
from pathlib import Path

def get_syntax_error(file_path):
    """Get specific syntax error for a file"""
    result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        return result.stderr
    return None

def fix_file(file_path):
    """Fix syntax errors in a specific file"""
    error = get_syntax_error(file_path)
    if not error:
        return True
    
    print(f"\n🔧 Fixing {file_path}")
    print(f"   Error: {error.strip()}")
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Extract line number from error
        import re
        line_match = re.search(r'line (\d+)', error)
        if line_match:
            line_num = int(line_match.group(1))
            
            # Apply fixes based on error type
            if 'unexpected indent' in error:
                # Fix indentation
                if line_num <= len(lines):
                    # Check if line is over-indented
                    current_line = lines[line_num - 1]
                    if current_line.startswith('    '):
                        lines[line_num - 1] = current_line[4:]
                        print(f"   ✅ Fixed indentation on line {line_num}")
            
            elif 'invalid syntax' in error:
                if line_num <= len(lines):
                    current_line = lines[line_num - 1].rstrip()
                    
                    # Check for common issues
                    if current_line and not current_line.endswith(':') and ('def ' in current_line or 'class ' in current_line):
                        lines[line_num - 1] = current_line + ':\n'
                        print(f"   ✅ Added missing colon on line {line_num}")
                    elif current_line.count('(') > current_line.count(')'):
                        lines[line_num - 1] = current_line + ')\n'
                        print(f"   ✅ Added missing closing parenthesis on line {line_num}")
                    elif current_line.count('[') > current_line.count(']'):
                        lines[line_num - 1] = current_line + ']\n'
                        print(f"   ✅ Added missing closing bracket on line {line_num}")
                    elif current_line.count('{') > current_line.count('}'):
                        lines[line_num - 1] = current_line + '}\n'
                        print(f"   ✅ Added missing closing brace on line {line_num}")
                    elif current_line.endswith('\\'):
                        # Line continuation issue
                        lines[line_num - 1] = current_line.rstrip('\\').rstrip() + '\n'
                        print(f"   ✅ Removed line continuation on line {line_num}")
                    else:
                        # Check for missing quotes
                        quote_count = current_line.count('"')
                        if quote_count % 2 == 1:
                            lines[line_num - 1] = current_line + '"\n'
                            print(f"   ✅ Added missing quote on line {line_num}")
            
            elif 'forgot a comma' in error:
                if line_num <= len(lines):
                    current_line = lines[line_num - 1].rstrip()
                    if not current_line.endswith(',') and not current_line.endswith(':'):
                        lines[line_num - 1] = current_line + ',\n'
                        print(f"   ✅ Added missing comma on line {line_num}")
        
        # Write back
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        # Check if fixed
        if get_syntax_error(file_path) is None:
            print("   ✅ File fixed!")
            return True
        else:
            print("   ⚠️  Still has errors, needs manual fix")
            return False
    
    except Exception as e:
        print(f"   ❌ Error fixing file: {e}")
        return False

def main():
    """Fix all syntax errors"""
    print("🔧 Final syntax error fixing pass...")
    
    # Files with known syntax errors
    problem_files = [
        "scripts/perform-consolidation.py",
        "tests/test_full_integration.py",
        "tests/test_research_components_simple.py",
        "tests/test_component_integration.py",
        "tests/integration/test_error_intelligence_integration.py",
        "tests/unit/test_executor_comprehensive.py",
        "tests/unit/test_native_nix_backend.py",
    ]
    
    fixed = 0
    still_broken = []
    
    for file in problem_files:
        if Path(file).exists():
            if fix_file(file):
                fixed += 1
            else:
                still_broken.append(file)
    
    print(f"\n📊 Summary: Fixed {fixed}/{len(problem_files)} files")
    
    if still_broken:
        print(f"\n⚠️  {len(still_broken)} files still need manual fixes:")
        for file in still_broken:
            print(f"   - {file}")
        
        # Try to get more details
        print("\n📋 Detailed errors for remaining files:")
        for file in still_broken:
            error = get_syntax_error(file)
            if error:
                print(f"\n{file}:")
                print(error)
    else:
        print("\n🎉 All syntax errors fixed!")

if __name__ == "__main__":
    main()