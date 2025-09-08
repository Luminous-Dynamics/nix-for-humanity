#!/usr/bin/env python3
"""
Phase 1: Update version to v0.1.0-alpha and archive dead code
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Get the project root
PROJECT_ROOT = Path(__file__).parent.parent

def update_version_in_files():
    """Update version to 0.1.0-alpha in all relevant files"""
    
    version_updates = [
        # (file_path, old_pattern, new_value)
        ("pyproject.toml", r'version = "[^"]*"', 'version = "0.1.0-alpha"'),
        ("src/luminous_nix/__init__.py", r'__version__ = "[^"]*"', '__version__ = "0.1.0-alpha"'),
        ("README.md", r'v\d+\.\d+\.\d+[-\w]*', 'v0.1.0-alpha'),
        ("docs/README.md", r'v\d+\.\d+\.\d+[-\w]*', 'v0.1.0-alpha'),
        # Update any help text
        ("src/luminous_nix/core/backend_real.py", r'Luminous Nix v[\d.]+', 'Luminous Nix v0.1.0-alpha'),
        ("src/luminous_nix/core/luminous_core.py", r'Luminous Nix v[\d.]+', 'Luminous Nix v0.1.0-alpha'),
        # Update status in help
        ("src/luminous_nix/core/backend_real.py", r'STATUS: v[\d.]+-alpha', 'STATUS: v0.1.0-alpha'),
    ]
    
    print("📝 Updating version to 0.1.0-alpha...")
    
    for file_path, pattern, replacement in version_updates:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            try:
                content = full_path.read_text()
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    full_path.write_text(new_content)
                    print(f"  ✅ Updated {file_path}")
                else:
                    print(f"  ⏭️  No changes needed in {file_path}")
            except Exception as e:
                print(f"  ❌ Error updating {file_path}: {e}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

def create_archive_directory() -> Path:
    """Create archive directory with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    archive_dir = PROJECT_ROOT / f".archive-{timestamp}"
    archive_dir.mkdir(exist_ok=True)
    
    # Create archive log
    log_file = archive_dir / "ARCHIVE_LOG.md"
    log_content = f"""# Archive Log - {timestamp}

## Reason for Archive
Moving to v0.1.0-alpha with honest capabilities. Archiving aspirational and non-working code.

## Archive Categories

### 1. Mystical/Consciousness Code
- All consciousness detection
- Sacred utilities
- Quantum features
- Mystical timers and pauses

### 2. Non-Working Features
- Fake native API (always falls back to subprocess)
- SKG integration (never tested)
- Complex persona system
- Theory of mind
- Blockchain integration

### 3. Aspirational Features
- Voice interface (architecture only)
- Learning system (complete fiction)
- Advanced AI features

## Archive Strategy
- Keep for 6 months for reference
- May contain salvageable patterns
- Delete after October 2025 if not needed

---
*Archived on {timestamp} as part of v0.1.0-alpha honest release*
"""
    log_file.write_text(log_content)
    print(f"📦 Created archive directory: {archive_dir}")
    return archive_dir

def get_files_to_archive() -> List[Tuple[Path, str]]:
    """Get list of files/directories to archive with reasons"""
    
    files_to_archive = []
    
    # Consciousness and mystical code
    consciousness_files = [
        ("src/luminous_nix/consciousness", "Mystical consciousness detection"),
        ("src/luminous_nix/core/sacred_utils.py", "Sacred utilities"),
        ("src/luminous_nix/core/sacred_messages.py", "Mystical messages"),
        ("src/luminous_nix/core/sacred_pause.py", "Arbitrary delays"),
        ("src/luminous_nix/quantum", "Quantum nonsense"),
    ]
    
    # Non-working features
    non_working = [
        ("src/luminous_nix/knowledge/skg_integration.py", "SKG never tested"),
        ("src/luminous_nix/ai/theory_of_mind.py", "Theory of mind fiction"),
        ("src/luminous_nix/blockchain", "Blockchain integration"),
        ("src/luminous_nix/personas/personality_manager.py", "Complex persona system"),
    ]
    
    # Aspirational features (keep structure but archive implementation)
    aspirational = [
        ("src/luminous_nix/voice/voice_processor.py", "Voice implementation mock"),
        ("src/luminous_nix/learning/consciousness_evolution.py", "Learning fiction"),
        ("src/luminous_nix/ai/quantum_reasoning.py", "Quantum AI nonsense"),
    ]
    
    # Check which files actually exist
    for file_path, reason in consciousness_files + non_working + aspirational:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            files_to_archive.append((full_path, reason))
    
    return files_to_archive

def archive_files(archive_dir: Path, files_to_archive: List[Tuple[Path, str]]):
    """Archive files to the archive directory"""
    
    print("\n🗄️  Archiving dead code...")
    
    archived_count = 0
    for file_path, reason in files_to_archive:
        try:
            # Calculate relative path from project root
            rel_path = file_path.relative_to(PROJECT_ROOT)
            
            # Create destination path in archive
            dest_path = archive_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file or directory
            if file_path.is_dir():
                shutil.move(str(file_path), str(dest_path))
                print(f"  📁 Archived directory: {rel_path}")
                print(f"     Reason: {reason}")
            else:
                shutil.move(str(file_path), str(dest_path))
                print(f"  📄 Archived file: {rel_path}")
                print(f"     Reason: {reason}")
            
            archived_count += 1
            
        except Exception as e:
            print(f"  ❌ Error archiving {file_path}: {e}")
    
    print(f"\n✅ Archived {archived_count} items")
    return archived_count

def update_imports_after_archive():
    """Update imports to remove references to archived code"""
    
    print("\n🔧 Updating imports after archiving...")
    
    # Files that might have imports to archived code
    files_to_check = [
        "src/luminous_nix/core/luminous_core.py",
        "src/luminous_nix/core/__init__.py",
        "src/luminous_nix/__init__.py",
        "src/luminous_nix/cli.py",
    ]
    
    # Patterns to remove or comment out
    archived_imports = [
        r'from \.\.consciousness[.\w]* import .*',
        r'from \.sacred_utils import .*',
        r'from \.\.quantum[.\w]* import .*',
        r'from \.\.knowledge\.skg_integration import .*',
        r'from \.\.ai\.theory_of_mind import .*',
        r'from \.\.blockchain[.\w]* import .*',
        r'import consciousness.*',
        r'import sacred_.*',
        r'import quantum.*',
    ]
    
    for file_path in files_to_check:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            try:
                content = full_path.read_text()
                original_content = content
                
                # Comment out archived imports
                for pattern in archived_imports:
                    content = re.sub(
                        pattern,
                        lambda m: f"# ARCHIVED: {m.group(0)}",
                        content,
                        flags=re.MULTILINE
                    )
                
                if content != original_content:
                    full_path.write_text(content)
                    print(f"  ✅ Updated imports in {file_path}")
                    
            except Exception as e:
                print(f"  ❌ Error updating {file_path}: {e}")

def create_honest_readme():
    """Create an honest README for v0.1.0-alpha"""
    
    readme_content = """# Luminous Nix v0.1.0-alpha

*Natural language interface for NixOS - Early Alpha Release*

## ⚠️ Alpha Software Notice

This is **v0.1.0-alpha** - early development software with limited functionality.

## What Actually Works

✅ **Basic Natural Language CLI**
```bash
ask-nix "search firefox"     # 2-3 seconds
ask-nix "install vim"        # 5-30 seconds
ask-nix "list installed"     # 1-2 seconds
```

✅ **Smart Package Discovery**
- Typo correction: `fierrfox` → `firefox`
- Semantic search: "text editor" → vim, emacs, nano
- Category matching: "browser" → firefox, chromium

✅ **Basic Operations**
- Search packages
- Install packages (requires privileges)
- Remove packages (requires privileges)
- List installed packages
- Show help

## What Doesn't Work Yet

❌ **TUI** - Has import errors  
❌ **Voice Interface** - Architecture only  
❌ **Learning System** - Not implemented  
❌ **Native API** - Falls back to subprocess  
❌ **Config Generation** - Templates exist but generation broken  

## Installation

```bash
# Clone repository
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix

# Install with Poetry
poetry install

# Run
poetry run ask-nix "search firefox"
```

## Performance

**Honest metrics** (standard NixOS performance):
- Search: 2-3 seconds
- Install: 5-30 seconds  
- List: 1-2 seconds
- No "10,000x improvements" - that was false

## Development Status

- **Version**: 0.1.0-alpha
- **Stability**: Experimental
- **Testing**: Basic tests pass
- **Documentation**: Being updated for accuracy

## Contributing

We need help making this real! Areas for contribution:
- Fix TUI display issues
- Implement real voice interface
- Improve error messages
- Add more package mappings
- Write tests for existing features

## License

MIT

---

*This is alpha software. Expect bugs. Help us make it better.*
"""
    
    readme_path = PROJECT_ROOT / "README_ALPHA.md"
    readme_path.write_text(readme_content)
    print(f"\n📄 Created honest README_ALPHA.md")

def main():
    """Execute Phase 1 updates"""
    
    print("=" * 60)
    print("🚀 Phase 1: Update to v0.1.0-alpha and Archive Dead Code")
    print("=" * 60)
    
    # Step 1: Update version
    update_version_in_files()
    
    # Step 2: Create archive directory
    archive_dir = create_archive_directory()
    
    # Step 3: Get files to archive
    files_to_archive = get_files_to_archive()
    
    # Step 4: Archive files (not delete!)
    if files_to_archive:
        archived_count = archive_files(archive_dir, files_to_archive)
    else:
        print("⚠️  No files found to archive")
        archived_count = 0
    
    # Step 5: Update imports
    update_imports_after_archive()
    
    # Step 6: Create honest README
    create_honest_readme()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Phase 1 Complete!")
    print(f"  • Version updated to 0.1.0-alpha")
    print(f"  • Archived {archived_count} dead code items")
    print(f"  • Archive location: {archive_dir}")
    print(f"  • Created honest README_ALPHA.md")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("  1. Review archived files in", archive_dir)
    print("  2. Test that imports still work")
    print("  3. Fix TUI display issues")
    print("  4. Integrate clean service architecture")
    print("  5. Prepare for v0.1.0-alpha release")

if __name__ == "__main__":
    main()