#!/usr/bin/env python3
"""Organize remaining root files into proper directories."""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Define categories and their patterns
FILE_CATEGORIES = {
    'docs/status': [
        '*_SUMMARY.md', '*_REPORT.md', '*_STATUS.md', 'STATUS.md',
        'ACHIEVEMENTS_*.md', 'ASSESSMENT_*.md', 'CURRENT_STATE.md',
        'WEEK*_*.md', 'PROJECT_ASSESSMENT_*.md'
    ],
    'docs/planning': [
        '*_PLAN.md', '*_ROADMAP.md', '*_STRATEGY.md', '*_CHECKLIST.md',
        'ACTION_PLAN_*.md', 'IMPROVEMENT_*.md', 'PHASE_*_*.md'
    ],
    'docs/architecture': [
        'ARCHITECTURE*.md', '*_ARCHITECTURE.md', '*_DIAGRAM*.md',
        'UNIFIED_*.md', 'SYMBIOTIC_*.md', '*_GUIDE.md'
    ],
    'docs/technical': [
        '*_ANALYSIS.md', '*_REVIEW.md', '*_INTEGRATION.md',
        'CODE_*.md', 'IMPLEMENTATION_*.md', '*_OPTIMIZATION.md'
    ],
    'scripts/analysis': [
        'analyze_*.py', 'benchmark_*.py', 'diagnose_*.py',
        'test_*.py', 'validate_*.py'
    ],
    'scripts/fixes': [
        'fix_*.py', 'update_*.py', 'remove_*.py', 'polish_*.py'
    ],
    'scripts/demos': [
        'demo*.py', 'showcase*.py', 'simple_*.py', 'capture*.py'
    ],
    'scripts/utilities': [
        'create_*.py', 'initialize_*.py', 'phase*.py', 'run_*.py'
    ],
    'config': [
        '*.yaml', '*.yml', '*.conf', '*.json', 'Dockerfile*',
        'Makefile', 'Procfile', 'supervisord.conf', 'nginx.conf'
    ],
    'archive/databases': [
        '*.db', '*.lock'
    ],
    'archive/logs': [
        '*.log', '*.xml', 'coverage.xml'
    ],
    'archive/backups': [
        '*.tar.gz', '*.backup'
    ],
    'docs/reference': [
        'README*.md', 'CONTRIBUTING*.md', 'CHANGELOG.md',
        'VERSION', 'LICENSE*', '*_REFERENCE.md'
    ]
}

# Files to keep in root
KEEP_IN_ROOT = {
    'README.md',
    'pyproject.toml',
    'poetry.lock',
    'flake.nix',
    'flake.lock',
    'shell.nix',
    'setup.py',
    'MANIFEST.in',
    '.gitignore',
    '.envrc',
    'VERSION'
}

# Directories to ignore
IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.tox',
    'build', 'dist', '.pytest_cache', 'htmlcov'
}

def categorize_file(filename):
    """Determine which category a file belongs to."""
    # Check if file should be kept in root
    if filename in KEEP_IN_ROOT:
        return None
    
    # Check each category
    for category, patterns in FILE_CATEGORIES.items():
        for pattern in patterns:
            if pattern.startswith('*') and pattern.endswith('*'):
                # Contains pattern
                if pattern[1:-1] in filename:
                    return category
            elif pattern.startswith('*'):
                # Ends with pattern
                if filename.endswith(pattern[1:]):
                    return category
            elif pattern.endswith('*'):
                # Starts with pattern
                if filename.startswith(pattern[:-1]):
                    return category
            else:
                # Exact match
                if filename == pattern:
                    return category
    
    # Default categories based on extension
    if filename.endswith('.md'):
        return 'docs/misc'
    elif filename.endswith('.py'):
        return 'scripts/misc'
    elif filename.endswith(('.yaml', '.yml', '.json', '.conf')):
        return 'config'
    elif filename.endswith(('.db', '.lock')):
        return 'archive/databases'
    elif filename.endswith(('.log', '.xml')):
        return 'archive/logs'
    
    return 'archive/misc'

def main():
    """Main function to organize files."""
    root_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity')
    os.chdir(root_dir)
    
    # Create all necessary directories
    directories = set()
    for category in FILE_CATEGORIES.keys():
        directories.add(category)
    directories.update(['docs/misc', 'scripts/misc', 'archive/misc'])
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Get all files in root
    files_to_move = []
    for item in os.listdir('.'):
        if os.path.isfile(item) and not item.startswith('.'):
            if item not in KEEP_IN_ROOT:
                category = categorize_file(item)
                if category:
                    files_to_move.append((item, category))
    
    # Move files
    moved_count = 0
    for filename, category in sorted(files_to_move):
        source = Path(filename)
        dest_dir = Path(category)
        dest = dest_dir / filename
        
        try:
            # Handle existing files
            if dest.exists():
                # Add timestamp to avoid overwriting
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    new_name = f"{filename}_{timestamp}"
                dest = dest_dir / new_name
            
            shutil.move(str(source), str(dest))
            print(f"✓ Moved {filename} → {category}/")
            moved_count += 1
            
        except Exception as e:
            print(f"✗ Error moving {filename}: {e}")
    
    # Count remaining files
    remaining_files = []
    for item in os.listdir('.'):
        if os.path.isfile(item) and not item.startswith('.'):
            remaining_files.append(item)
    
    print(f"\n📊 Summary:")
    print(f"- Files moved: {moved_count}")
    print(f"- Files remaining in root: {len(remaining_files)}")
    print(f"- Target: <15 files in root")
    
    if remaining_files:
        print(f"\n📁 Files kept in root:")
        for f in sorted(remaining_files):
            print(f"  - {f}")
    
    # Create an organization report
    report = f"""# Root File Organization Report

## Summary
- Files moved: {moved_count}
- Files remaining: {len(remaining_files)}
- Target: <15 files

## Files Kept in Root
"""
    for f in sorted(remaining_files):
        report += f"- {f}\n"
    
    report += f"\n## Files Moved by Category\n"
    for category in sorted(set(cat for _, cat in files_to_move)):
        files_in_cat = [f for f, c in files_to_move if c == category]
        if files_in_cat:
            report += f"\n### {category}/ ({len(files_in_cat)} files)\n"
            for f in sorted(files_in_cat)[:10]:  # Show first 10
                report += f"- {f}\n"
            if len(files_in_cat) > 10:
                report += f"- ... and {len(files_in_cat) - 10} more\n"
    
    with open('ROOT_ORGANIZATION_REPORT.md', 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to ROOT_ORGANIZATION_REPORT.md")

if __name__ == '__main__':
    main()