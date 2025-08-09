#!/usr/bin/env python3
"""
Remove all TypeScript and JavaScript files from the project.
This is Phase 1 of the Python-only architecture consolidation.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Directories to exclude from removal
EXCLUDE_DIRS = {
    'archive',
    'node_modules',
    '.next',
    'dist',
    'build',
    '.git',
    '__pycache__'
}

# File extensions to remove
TS_JS_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}

# Related config files to remove
CONFIG_FILES = {
    'package.json',
    'package-lock.json',
    'yarn.lock',
    'tsconfig.json',
    'tsconfig.base.json',
    'tsconfig.node.json',
    'jest.config.js',
    'vite.config.js',
    'vite.config.ts',
    'postcss.config.js',
    'tailwind.config.js',
    'webpack.config.js',
    '.eslintrc.js',
    '.prettierrc.js'
}

def should_exclude_dir(path: Path) -> bool:
    """Check if directory should be excluded from processing."""
    parts = path.parts
    for exclude in EXCLUDE_DIRS:
        if exclude in parts:
            return True
    return False

def find_files_to_remove(root_dir: Path):
    """Find all TypeScript/JavaScript files and related configs."""
    files_to_remove = []
    
    # Find TS/JS files
    for ext in TS_JS_EXTENSIONS:
        for file_path in root_dir.rglob(f'*{ext}'):
            if not should_exclude_dir(file_path):
                files_to_remove.append(file_path)
    
    # Find config files
    for config in CONFIG_FILES:
        for file_path in root_dir.rglob(config):
            if not should_exclude_dir(file_path):
                files_to_remove.append(file_path)
    
    return sorted(set(files_to_remove))

def find_directories_to_remove(root_dir: Path):
    """Find directories that will be empty after file removal."""
    dirs_to_check = []
    
    # Common TS/JS directories
    ts_js_dirs = [
        'src',  # If it contains only TS/JS
        'packages',
        'implementations/nodejs-mvp',
        'implementations/web-based',
        'implementations/server',
        'implementations/core',
        'implementations/security',
        'implementations/monitoring',
        'frontend',
        'frontends/web',
        'src-tauri'
    ]
    
    for dir_name in ts_js_dirs:
        for dir_path in root_dir.rglob(dir_name):
            if dir_path.is_dir() and not should_exclude_dir(dir_path):
                dirs_to_check.append(dir_path)
    
    return sorted(set(dirs_to_check), reverse=True)  # Deepest first

def create_backup(files_to_remove, backup_dir: Path):
    """Create a backup of files before removal."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_file = backup_dir / 'REMOVED_FILES_MANIFEST.txt'
    with open(manifest_file, 'w') as f:
        f.write(f"TypeScript/JavaScript Removal Backup\n")
        f.write(f"Created: {datetime.now().isoformat()}\n")
        f.write(f"Total files: {len(files_to_remove)}\n\n")
        
        for file_path in files_to_remove:
            f.write(f"{file_path}\n")
    
    print(f"✅ Created removal manifest: {manifest_file}")

def remove_files(files_to_remove, dry_run=True):
    """Remove the identified files."""
    if dry_run:
        print("\n🔍 DRY RUN - No files will be removed")
    else:
        print("\n🗑️  REMOVING FILES")
    
    removed_count = 0
    for file_path in files_to_remove:
        if file_path.exists():
            if dry_run:
                print(f"Would remove: {file_path}")
            else:
                try:
                    file_path.unlink()
                    print(f"Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing {file_path}: {e}")
    
    return removed_count

def remove_empty_directories(dirs_to_check, dry_run=True):
    """Remove directories that are now empty."""
    removed_dirs = []
    
    for dir_path in dirs_to_check:
        if dir_path.exists() and dir_path.is_dir():
            # Check if directory is empty or contains only empty subdirs
            try:
                if not any(dir_path.iterdir()):
                    if dry_run:
                        print(f"Would remove empty dir: {dir_path}")
                    else:
                        shutil.rmtree(dir_path)
                        print(f"Removed empty dir: {dir_path}")
                        removed_dirs.append(dir_path)
            except Exception as e:
                print(f"❌ Error checking/removing {dir_path}: {e}")
    
    return removed_dirs

def main():
    """Main execution function."""
    root_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity')
    backup_dir = root_dir / 'archive' / f'ts-js-removal-{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    print("🧹 TypeScript/JavaScript Removal Tool")
    print("=" * 50)
    
    # Find files to remove
    print("\n📋 Scanning for TypeScript/JavaScript files...")
    files_to_remove = find_files_to_remove(root_dir)
    print(f"Found {len(files_to_remove)} files to remove")
    
    # Find directories that might become empty
    dirs_to_check = find_directories_to_remove(root_dir)
    print(f"Found {len(dirs_to_check)} directories to check")
    
    # Create backup manifest
    create_backup(files_to_remove, backup_dir)
    
    # Show summary
    print("\n📊 Summary:")
    print(f"  - TypeScript/JavaScript files: {len([f for f in files_to_remove if f.suffix in TS_JS_EXTENSIONS])}")
    print(f"  - Config files: {len([f for f in files_to_remove if f.name in CONFIG_FILES])}")
    print(f"  - Total files to remove: {len(files_to_remove)}")
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will permanently remove all TypeScript/JavaScript files!")
    print("A manifest has been created, but files will not be backed up.")
    
    response = input("\nProceed with removal? (yes/no): ").strip().lower()
    
    if response == 'yes':
        # Remove files
        removed_count = remove_files(files_to_remove, dry_run=False)
        print(f"\n✅ Removed {removed_count} files")
        
        # Remove empty directories
        removed_dirs = remove_empty_directories(dirs_to_check, dry_run=False)
        print(f"✅ Removed {len(removed_dirs)} empty directories")
        
        print("\n🎉 TypeScript/JavaScript removal complete!")
        print(f"📁 Manifest saved to: {backup_dir / 'REMOVED_FILES_MANIFEST.txt'}")
    else:
        print("\n❌ Removal cancelled")
        
        # Offer dry run
        if input("\nWould you like to see what would be removed? (yes/no): ").strip().lower() == 'yes':
            print("\n" + "=" * 50)
            remove_files(files_to_remove[:20], dry_run=True)  # Show first 20
            if len(files_to_remove) > 20:
                print(f"\n... and {len(files_to_remove) - 20} more files")

if __name__ == '__main__':
    main()