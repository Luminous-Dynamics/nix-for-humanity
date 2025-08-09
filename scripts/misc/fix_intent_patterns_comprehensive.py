#!/usr/bin/env python3
"""
from typing import Dict, List
Comprehensive Intent Constructor Pattern Fixer

This script systematically fixes all Intent constructor patterns across the codebase
to use the standardized pattern from src/nix_for_humanity/core/types.py.

Standard Pattern:
    Intent(
        type=IntentType.SOME_TYPE,
        entities={'key': 'value'},
        confidence=0.95,
        raw_input="original text"
    )
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
import subprocess

class IntentPatternFixer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.changes_made = []
        self.files_processed = []
        self.errors = []
        
        # Pattern to match Intent constructors
        self.intent_constructor_pattern = re.compile(
            r'Intent\s*\(\s*([^)]+)\s*\)',
            re.MULTILINE | re.DOTALL
        )
        
        # Pattern to match old parameter names that need fixing
        self.old_param_patterns = {
            'raw_text': 'raw_input',
            'text': 'raw_input',
            'original_text': 'raw_input',
            'query': 'raw_input',
            'input_text': 'raw_input'
        }
        
        # IntentType mappings from different sources
        self.intent_type_mappings = {
            # From backend/core/intent.py to core/types.py
            'INSTALL_PACKAGE': 'INSTALL',
            'UPDATE_SYSTEM': 'UPDATE', 
            'SEARCH_PACKAGE': 'SEARCH',
            'CONFIGURE': 'CONFIG',
            'EXPLAIN': 'INFO',
            # Keep these as-is
            'ROLLBACK': 'ROLLBACK',
            'UNKNOWN': 'UNKNOWN',
            'HELP': 'HELP',
            'INSTALL': 'INSTALL',
            'REMOVE': 'REMOVE',
            'UPDATE': 'UPDATE',
            'SEARCH': 'SEARCH',
            'INFO': 'INFO',
            'CONFIG': 'CONFIG'
        }

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        
        # Look in key directories
        search_dirs = [
            'tests',
            'src', 
            'backend',
            'scripts'
        ]
        
        for search_dir in search_dirs:
            dir_path = self.root_path / search_dir
            if dir_path.exists():
                python_files.extend(dir_path.rglob('*.py'))
        
        # Also check root level Python files
        python_files.extend(self.root_path.glob('*.py'))
        
        return sorted(set(python_files))

    def analyze_intent_constructor(self, content: str, file_path: Path) -> List[Dict]:
        """Analyze Intent constructors in the content"""
        issues = []
        
        for match in self.intent_constructor_pattern.finditer(content):
            constructor_args = match.group(1).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            # Parse the arguments
            parsed_args = self.parse_constructor_args(constructor_args)
            
            issue = {
                'file': file_path,
                'line': line_num,
                'original': match.group(0),
                'args': parsed_args,
                'needs_fix': False,
                'fixes_needed': []
            }
            
            # Check for issues
            for arg_name, arg_value in parsed_args.items():
                if arg_name in self.old_param_patterns:
                    issue['needs_fix'] = True
                    issue['fixes_needed'].append(f"Rename {arg_name} to {self.old_param_patterns[arg_name]}")
                
                if arg_name == 'type' and 'IntentType.' in arg_value:
                    intent_type = arg_value.replace('IntentType.', '')
                    if intent_type in self.intent_type_mappings and self.intent_type_mappings[intent_type] != intent_type:
                        issue['needs_fix'] = True
                        issue['fixes_needed'].append(f"Change {intent_type} to {self.intent_type_mappings[intent_type]}")
            
            issues.append(issue)
        
        return issues

    def parse_constructor_args(self, args_str: str) -> Dict[str, str]:
        """Parse constructor arguments into a dictionary"""
        args = {}
        
        # Split by commas, but be careful with nested structures
        parts = []
        current_part = ""
        paren_count = 0
        brace_count = 0
        bracket_count = 0
        in_string = False
        string_char = None
        
        for char in args_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                elif char == ',' and paren_count == 0 and brace_count == 0 and bracket_count == 0:
                    parts.append(current_part.strip())
                    current_part = ""
                    continue
            
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Parse each part
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                args[key.strip()] = value.strip()
        
        return args

    def fix_intent_constructor(self, content: str, issue: Dict) -> str:
        """Fix a single Intent constructor"""
        original = issue['original']
        args = issue['args']
        
        # Build the new constructor
        new_args = []
        
        # Handle type parameter
        if 'type' in args:
            type_value = args['type']
            if 'IntentType.' in type_value:
                intent_type = type_value.replace('IntentType.', '')
                if intent_type in self.intent_type_mappings:
                    new_type = self.intent_type_mappings[intent_type]
                    new_args.append(f'type=IntentType.{new_type}')
                else:
                    new_args.append(f'type={type_value}')
            else:
                new_args.append(f'type={type_value}')
        
        # Handle entities parameter
        if 'entities' in args:
            new_args.append(f'entities={args["entities"]}')
        else:
            new_args.append('entities={}')
        
        # Handle confidence parameter
        if 'confidence' in args:
            new_args.append(f'confidence={args["confidence"]}')
        else:
            new_args.append('confidence=1.0')
        
        # Handle raw_input parameter (convert from old names)
        raw_input_value = None
        for old_name in ['raw_text', 'text', 'original_text', 'query', 'input_text', 'raw_input']:
            if old_name in args:
                raw_input_value = args[old_name]
                break
        
        if raw_input_value:
            new_args.append(f'raw_input={raw_input_value}')
        else:
            new_args.append('raw_input=""')
        
        # Build the new constructor
        new_constructor = f"Intent(\n        {',\n        '.join(new_args)}\n    )"
        
        return content.replace(original, new_constructor)

    def fix_imports(self, content: str, file_path: Path) -> str:
        """Fix import statements to use the correct Intent class"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Fix import statements
            if 'from nix_humanity.core.intents import' in line and 'Intent' in line:
                # Replace with the standard import
                new_line = line.replace(
                    'from nix_humanity.core.intents import',
                    'from nix_for_humanity.core.types import'
                )
                new_lines.append(new_line)
            elif 'from src.nix_for_humanity.core.types import' in line:
                # Simplify the import path
                new_line = line.replace(
                    'from src.nix_for_humanity.core.types import',
                    'from nix_for_humanity.core.types import'
                )
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)

    def process_file(self, file_path: Path) -> bool:
        """Process a single file"""
        try:
            # Skip the fixer scripts themselves
            if 'fix_intent' in file_path.name or 'fix_intents' in file_path.name:
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Skip files that don't contain Intent constructors
            if 'Intent(' not in original_content:
                return False
            
            self.files_processed.append(file_path)
            content = original_content
            
            # Analyze issues
            issues = self.analyze_intent_constructor(content, file_path)
            
            if not any(issue['needs_fix'] for issue in issues):
                return False
            
            # Fix imports first
            content = self.fix_imports(content, file_path)
            
            # Fix each Intent constructor
            changes_in_file = []
            for issue in issues:
                if issue['needs_fix']:
                    old_content = content
                    content = self.fix_intent_constructor(content, issue)
                    if content != old_content:
                        changes_in_file.extend(issue['fixes_needed'])
            
            if content != original_content:
                # Write the fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                change_record = {
                    'file': file_path,
                    'changes': changes_in_file,
                    'lines_changed': len([issue for issue in issues if issue['needs_fix']])
                }
                self.changes_made.append(change_record)
                return True
            
            return False
            
        except Exception as e:
            error_record = {
                'file': file_path,
                'error': str(e)
            }
            self.errors.append(error_record)
            return False

    def run(self) -> Dict:
        """Run the comprehensive fix"""
        print("🔧 Starting comprehensive Intent pattern fix...")
        print(f"📂 Scanning {self.root_path}")
        
        # Find all Python files
        python_files = self.find_python_files()
        print(f"📋 Found {len(python_files)} Python files")
        
        # Process each file
        files_changed = 0
        for file_path in python_files:
            if self.process_file(file_path):
                files_changed += 1
                print(f"✅ Fixed {file_path.relative_to(self.root_path)}")
        
        # Generate summary
        summary = {
            'files_scanned': len(python_files),
            'files_processed': len(self.files_processed),
            'files_changed': files_changed,
            'total_changes': sum(len(change['changes']) for change in self.changes_made),
            'errors': len(self.errors)
        }
        
        return summary

    def print_summary(self, summary: Dict):
        """Print a detailed summary of changes"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE INTENT FIX SUMMARY")
        print("="*60)
        
        print(f"📁 Files scanned: {summary['files_scanned']}")
        print(f"🔍 Files with Intent constructors: {summary['files_processed']}")
        print(f"✅ Files modified: {summary['files_changed']}")
        print(f"🔧 Total fixes applied: {summary['total_changes']}")
        print(f"❌ Errors encountered: {summary['errors']}")
        
        if self.changes_made:
            print("\n📝 DETAILED CHANGES:")
            for change in self.changes_made:
                rel_path = change['file'].relative_to(self.root_path)
                print(f"\n  📄 {rel_path}")
                for fix in change['changes']:
                    print(f"    • {fix}")
        
        if self.errors:
            print("\n❌ ERRORS ENCOUNTERED:")
            for error in self.errors:
                rel_path = error['file'].relative_to(self.root_path)
                print(f"  📄 {rel_path}: {error['error']}")
        
        print("\n🎯 NEXT STEPS:")
        print("1. Run tests to verify all fixes work correctly")
        print("2. Check git diff to review changes")
        print("3. Commit changes if everything looks good")
        
        print("\n🧪 Recommended test command:")
        print("   python -m pytest tests/unit/ -v")

def main():
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = Path.cwd()
    
    fixer = IntentPatternFixer(root_path)
    summary = fixer.run()
    fixer.print_summary(summary)
    
    # Return appropriate exit code
    if summary['errors'] > 0:
        print("\n⚠️  Some errors occurred during processing")
        return 1
    elif summary['files_changed'] > 0:
        print("\n✅ All Intent patterns fixed successfully!")
        return 0
    else:
        print("\n✅ No Intent patterns needed fixing")
        return 0

if __name__ == "__main__":
    sys.exit(main())