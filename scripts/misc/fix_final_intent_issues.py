#!/usr/bin/env python3
"""
Final Intent Issues Fixer

This script fixes the remaining issues in test files after the comprehensive fix:
1. Test assertions still using old property names (raw_text vs raw_input)
2. Test expectations still using old IntentType names
3. Import issues

This is a surgical fix for the remaining inconsistencies.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set

class FinalIntentFixer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.changes_made = []
        self.errors = []
        
        # Map old property names to new ones
        self.property_mappings = {
            'raw_text': 'raw_input',
            'intent.raw_text': 'intent.raw_input'
        }
        
        # Map old IntentType values to new ones
        self.intent_type_mappings = {
            'IntentType.INSTALL_PACKAGE': 'IntentType.INSTALL',
            'IntentType.UPDATE_SYSTEM': 'IntentType.UPDATE',
            'IntentType.SEARCH_PACKAGE': 'IntentType.SEARCH',
            'IntentType.CONFIGURE': 'IntentType.CONFIG',
            'IntentType.EXPLAIN': 'IntentType.INFO'
        }

    def fix_test_assertions(self, content: str) -> str:
        """Fix test assertions that use old property names"""
        
        # Fix property access in assertions
        for old_prop, new_prop in self.property_mappings.items():
            # Pattern to match property access in assertions
            pattern = re.compile(rf'\b{re.escape(old_prop)}\b')
            content = pattern.sub(new_prop, content)
        
        # Fix IntentType expectations in assertions
        for old_type, new_type in self.intent_type_mappings.items():
            content = content.replace(old_type, new_type)
        
        return content

    def fix_import_issues(self, content: str) -> str:
        """Fix import statement issues"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Fix imports that might be incorrect
            if 'from luminous_nix.core.intents import' in line and 'IntentRecognizer' in line:
                # This import should be from nix_for_humanity.core.types
                line = line.replace(
                    'from luminous_nix.core.intents import IntentRecognizer',
                    'from luminous_nix.core.intents import IntentRecognizer'
                )
                # But the Intent and IntentType should come from core.types
                if 'Intent,' in line and 'IntentType' in line:
                    # Split the import
                    new_lines.append('from luminous_nix.core.intents import IntentRecognizer')
                    new_lines.append('from nix_for_humanity.core.types import Intent, IntentType')
                    continue
                    
            new_lines.append(line)
        
        return '\n'.join(new_lines)

    def process_file(self, file_path: Path) -> bool:
        """Process a single file for final fixes"""
        try:
            # Only process test files
            if not file_path.name.startswith('test_'):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            
            # Apply fixes
            content = self.fix_import_issues(content)
            content = self.fix_test_assertions(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.changes_made.append({
                    'file': file_path,
                    'description': 'Fixed test assertions and imports'
                })
                return True
            
            return False
            
        except Exception as e:
            self.errors.append({
                'file': file_path,
                'error': str(e)
            })
            return False

    def run(self):
        """Run the final fixes"""
        print("🔧 Running final Intent fixes...")
        
        # Find test files
        test_files = list(self.root_path.rglob('test_*.py'))
        print(f"📋 Found {len(test_files)} test files")
        
        files_changed = 0
        for file_path in test_files:
            if self.process_file(file_path):
                files_changed += 1
                print(f"✅ Fixed {file_path.relative_to(self.root_path)}")
        
        print(f"\n📊 Final Fix Results:")
        print(f"   Files changed: {files_changed}")
        print(f"   Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"   {error['file']}: {error['error']}")

def main():
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = Path.cwd()
    
    fixer = FinalIntentFixer(root_path)
    fixer.run()

if __name__ == "__main__":
    main()