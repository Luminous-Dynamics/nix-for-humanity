#!/usr/bin/env python3
"""
Phase 1: Remove TypeScript/JavaScript files - Python-only consolidation.
This script removes all TS/JS files while preserving the archive directory.
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
    '__pycache__',
    'luminous_nix',  # Our new Python package
    'backend',  # Keep backend Python code for now
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

# Directories to remove entirely
REMOVE_DIRS = [
    'src',  # TypeScript source
    'src-tauri',  # Tauri app
    'packages',  # TypeScript packages
    'implementations/nodejs-mvp',
    'implementations/web-based',
    'implementations/server',
    'implementations/core',
    'implementations/security',
    'implementations/monitoring',
    'implementations/nlp',
    'implementations/implementations',
    'frontend',
    'frontends/web',
    'examples',  # Has TS files
]

def should_exclude_dir(path: Path) -> bool:
    """Check if directory should be excluded from processing."""
    parts = path.parts
    for exclude in EXCLUDE_DIRS:
        if exclude in parts:
            return True
    return False

def remove_typescript_javascript():
    """Remove all TypeScript/JavaScript files and directories."""
    root_dir = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity')
    removed_files = []
    removed_dirs = []
    
    # Remove specific directories first
    print("🗑️  Removing TypeScript/JavaScript directories...")
    for dir_name in REMOVE_DIRS:
        dir_path = root_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                removed_dirs.append(str(dir_path))
                print(f"  ✅ Removed directory: {dir_name}")
            except Exception as e:
                print(f"  ❌ Error removing {dir_name}: {e}")
    
    # Remove individual TS/JS files
    print("\n🗑️  Removing TypeScript/JavaScript files...")
    for ext in TS_JS_EXTENSIONS:
        for file_path in root_dir.rglob(f'*{ext}'):
            if not should_exclude_dir(file_path) and file_path.exists():
                try:
                    file_path.unlink()
                    removed_files.append(str(file_path))
                    print(f"  ✅ Removed: {file_path.name}")
                except Exception as e:
                    print(f"  ❌ Error removing {file_path}: {e}")
    
    # Remove config files
    print("\n🗑️  Removing build configuration files...")
    for config in CONFIG_FILES:
        for file_path in root_dir.rglob(config):
            if not should_exclude_dir(file_path) and file_path.exists():
                try:
                    file_path.unlink()
                    removed_files.append(str(file_path))
                    print(f"  ✅ Removed: {config}")
                except Exception as e:
                    print(f"  ❌ Error removing {file_path}: {e}")
    
    # Clean up empty directories
    print("\n🧹 Cleaning up empty directories...")
    empty_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        dir_path = Path(dirpath)
        if not should_exclude_dir(dir_path) and dir_path.exists():
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    empty_dirs.append(str(dir_path))
                    print(f"  ✅ Removed empty: {dir_path.name}")
            except Exception:
                pass  # Directory not empty or other error
    
    # Create summary report
    summary_path = root_dir / 'PHASE1_TYPESCRIPT_REMOVAL_COMPLETE.md'
    with open(summary_path, 'w') as f:
        f.write(f"# Phase 1: TypeScript/JavaScript Removal Complete\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Removed {len(removed_files)} TypeScript/JavaScript files\n")
        f.write(f"- Removed {len(removed_dirs)} directories\n")
        f.write(f"- Cleaned up {len(empty_dirs)} empty directories\n\n")
        f.write(f"## Next Steps\n\n")
        f.write(f"1. Migrate Python code from `backend/` to `luminous_nix/`\n")
        f.write(f"2. Update all imports to use the new package structure\n")
        f.write(f"3. Remove the old `backend/` directory\n")
        f.write(f"4. Update `pyproject.toml` with all dependencies\n")
        f.write(f"5. Run tests to ensure everything works\n")
    
    print(f"\n✅ Summary written to: {summary_path}")
    return len(removed_files), len(removed_dirs), len(empty_dirs)

def main():
    """Main execution."""
    print("🧹 Phase 1: TypeScript/JavaScript Removal")
    print("=" * 60)
    print("⚠️  This will remove all TypeScript/JavaScript code")
    print("✅ Python code in backend/ will be preserved")
    print("✅ Archive directory will be preserved")
    print("=" * 60)
    
    files_removed, dirs_removed, empty_cleaned = remove_typescript_javascript()
    
    print("\n" + "=" * 60)
    print("🎉 Phase 1 Complete!")
    print(f"   - {files_removed} files removed")
    print(f"   - {dirs_removed} directories removed")
    print(f"   - {empty_cleaned} empty directories cleaned")
    print("\n📋 See PHASE1_TYPESCRIPT_REMOVAL_COMPLETE.md for details")

if __name__ == '__main__':
    main()