#!/usr/bin/env python3
"""
Fix Import Issues Script
Fixes incorrect import paths for AriaLivePriority and Plan types
"""

import os
import re
from pathlib import Path

# Base directory for the project
BASE_DIR = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")

# Mapping of incorrect imports to correct imports
IMPORT_FIXES = {
    # AriaLivePriority fixes
    r'from nix_for_humanity\.tui\.components import.*AriaLivePriority': 
        'from nix_for_humanity.accessibility.screen_reader import AriaLivePriority',
    
    r'from nix_for_humanity\.types import.*AriaLivePriority':
        'from nix_for_humanity.accessibility.screen_reader import AriaLivePriority',
    
    # Plan fixes
    r'from nix_for_humanity\.types import.*Plan':
        'from nix_for_humanity.core.planning import Plan',
    
    # Mixed imports that need splitting
    r'from nix_for_humanity\.types import (.*)Plan(.*)':
        lambda match: _split_plan_import(match),
    
    r'from nix_for_humanity\.tui\.components import (.*)AriaLivePriority(.*)':
        lambda match: _split_aria_import(match),
}

def _split_plan_import(match):
    """Handle mixed imports containing Plan"""
    full_import = match.group(0)
    before = match.group(1).strip(', ')
    after = match.group(2).strip(', ')
    
    other_imports = []
    if before:
        other_imports.extend([i.strip() for i in before.split(',')])
    if after:
        other_imports.extend([i.strip() for i in after.split(',')])
    
    if other_imports:
        # Keep other imports from types, add Plan import separately
        return f"from nix_for_humanity.core.planning import Plan"
    else:
        return "from nix_for_humanity.core.planning import Plan"

def _split_aria_import(match):
    """Handle mixed imports containing AriaLivePriority"""
    full_import = match.group(0)
    before = match.group(1).strip(', ')
    after = match.group(2).strip(', ')
    
    other_imports = []
    if before:
        other_imports.extend([i.strip() for i in before.split(',')])
    if after:
        other_imports.extend([i.strip() for i in after.split(',')])
    
    if other_imports:
        # Keep other imports from tui.components, add AriaLivePriority import separately
        return f"from nix_for_humanity.accessibility.screen_reader import AriaLivePriority"
    else:
        return "from nix_for_humanity.accessibility.screen_reader import AriaLivePriority"

def fix_imports_in_file(filepath):
    """Fix imports in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    original_content = content
    changes_made = False
    
    for pattern, replacement in IMPORT_FIXES.items():
        if callable(replacement):
            # Handle complex replacements
            matches = list(re.finditer(pattern, content))
            for match in reversed(matches):  # Process in reverse to preserve positions
                new_text = replacement(match)
                content = content[:match.start()] + new_text + content[match.end():]
                changes_made = True
        else:
            # Simple string replacement
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made = True
    
    if changes_made:
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Fixed imports in: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return False
    
    return False

def find_files_with_import_issues():
    """Find all Python files with import issues"""
    files_to_fix = []
    
    # Search patterns to find files with issues
    search_patterns = [
        r"from nix_for_humanity\.tui\.components import.*AriaLivePriority",
        r"from nix_for_humanity\.types import.*AriaLivePriority",
        r"from nix_for_humanity\.types import.*Plan",
    ]
    
    # Find all Python files
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip hidden directories and virtual environments
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Check if file contains any problematic imports
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    for pattern in search_patterns:
                        if re.search(pattern, content):
                            files_to_fix.append(filepath)
                            break
                except Exception as e:
                    print(f"Error checking {filepath}: {e}")
    
    return files_to_fix

def main():
    """Main function to fix all import issues"""
    print("🔍 Searching for files with import issues...")
    
    files_to_fix = find_files_with_import_issues()
    
    if not files_to_fix:
        print("✨ No files with import issues found!")
        return
    
    print(f"\nFound {len(files_to_fix)} files with import issues:")
    for f in files_to_fix:
        print(f"  - {f}")
    
    print("\n🔧 Fixing imports...")
    fixed_count = 0
    
    for filepath in files_to_fix:
        if fix_imports_in_file(filepath):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count}/{len(files_to_fix)} files")
    
    # Verify fixes
    print("\n🔍 Verifying fixes...")
    remaining_issues = find_files_with_import_issues()
    
    if remaining_issues:
        print(f"⚠️  {len(remaining_issues)} files still have issues:")
        for f in remaining_issues:
            print(f"  - {f}")
    else:
        print("✨ All import issues have been fixed!")

if __name__ == "__main__":
    main()