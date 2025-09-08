#!/usr/bin/env python3
"""
Phase 1 Extended: Archive more dead code (consciousness, sacred, etc.)
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Get the project root
PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / ".archive-2025-09-08"

def archive_more_files():
    """Archive additional mystical and non-working files"""
    
    files_to_archive = [
        # Consciousness files
        ("src/luminous_nix/cli/consciousness_integration.py", "Consciousness integration"),
        ("src/luminous_nix/core/conscious_integration.py", "Conscious integration core"),
        ("src/luminous_nix/plugins/consciousness_router.py", "Consciousness router"),
        ("src/luminous_nix/ui/consciousness_orb.py", "Consciousness orb UI"),
        ("src/luminous_nix/ui/enhanced_consciousness_orb.py", "Enhanced consciousness orb"),
        ("tests/fixtures/consciousness_test_backend.py", "Consciousness test backend"),
        ("tests/CONSCIOUSNESS_FIRST_TESTING_GUIDE.md", "Consciousness testing guide"),
        
        # Sacred files
        ("src/luminous_nix/voice/sacred_voice_interface.py", "Sacred voice interface"),
        ("tests/fixtures/sacred_test_base.py", "Sacred test base"),
        ("tests/integration/sacred_synthesis", "Sacred synthesis tests"),
        
        # Personality/persona files (already moved but check for more)
        ("src/luminous_nix/ai/personality_modes.py", "Personality modes"),
        ("tests/unit/test_personality_system.py", "Personality system tests"),
        
        # Living system (aspirational)
        ("src/luminous_nix/living_system", "Living system directory"),
        ("demo_living_system.py", "Living system demo"),
        
        # Harmonic/mystical
        ("src/luminous_nix/plugins/harmonic_resolver.py", "Harmonic resolver"),
        
        # Trinity store (mystical naming)
        ("src/luminous_nix/persistence/trinity_store.py", "Trinity store"),
        ("src/luminous_nix/persistence/trinity_store_fixed.py", "Trinity store fixed"),
        ("src/luminous_nix/bridges/store_trinity_bridge.py", "Trinity bridge"),
        
        # Phenomenological (too philosophical)
        ("src/luminous_nix/knowledge/phenomenological_tracker.py", "Phenomenological tracker"),
        
        # SKG-related files (never worked)
        ("src/luminous_nix/knowledge/skg_core.py", "SKG core"),
        
        # Aspirational learning
        ("src/luminous_nix/learning/unified_learning.py", "Unified learning fiction"),
        ("src/luminous_nix/ai/learning_system.py", "Learning system fiction"),
        ("tests/unit/test_learning_system.py", "Learning system test"),
        
        # Old release directories (v1.0.0 doesn't exist yet!)
        ("release/v1.0.0", "Premature v1.0.0 release"),
        
        # Demo files for non-existent features
        ("demo_living_system.py", "Living system demo"),
    ]
    
    print("\n🗄️  Archiving additional dead code...")
    archived_count = 0
    
    for file_path, reason in files_to_archive:
        full_path = PROJECT_ROOT / file_path
        
        if full_path.exists():
            try:
                # Calculate relative path
                rel_path = Path(file_path)
                
                # Create destination path
                dest_path = ARCHIVE_DIR / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file or directory
                if full_path.is_dir():
                    if dest_path.exists():
                        print(f"  ⏭️  Already archived: {rel_path}")
                    else:
                        shutil.move(str(full_path), str(dest_path))
                        print(f"  📁 Archived directory: {rel_path}")
                        print(f"     Reason: {reason}")
                        archived_count += 1
                else:
                    if dest_path.exists():
                        print(f"  ⏭️  Already archived: {rel_path}")
                    else:
                        shutil.move(str(full_path), str(dest_path))
                        print(f"  📄 Archived file: {rel_path}")
                        print(f"     Reason: {reason}")
                        archived_count += 1
                        
            except Exception as e:
                print(f"  ❌ Error archiving {file_path}: {e}")
        else:
            print(f"  ⚠️  Not found: {file_path}")
    
    return archived_count

def update_more_imports():
    """Update additional files that might import archived code"""
    
    print("\n🔧 Updating more imports...")
    
    files_to_check = [
        "src/luminous_nix/cli/__init__.py",
        "src/luminous_nix/core/__init__.py", 
        "src/luminous_nix/ui/__init__.py",
        "src/luminous_nix/plugins/__init__.py",
        "tests/conftest.py",
    ]
    
    imports_to_comment = [
        "consciousness",
        "sacred",
        "trinity",
        "phenomenological",
        "harmonic",
        "living_system",
        "personality_modes",
    ]
    
    for file_path in files_to_check:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            try:
                content = full_path.read_text()
                original = content
                
                for term in imports_to_comment:
                    # Comment out any line containing these terms
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        if term in line.lower() and not line.strip().startswith('#'):
                            new_lines.append(f"# ARCHIVED: {line}")
                        else:
                            new_lines.append(line)
                    content = '\n'.join(new_lines)
                
                if content != original:
                    full_path.write_text(content)
                    print(f"  ✅ Updated {file_path}")
                    
            except Exception as e:
                print(f"  ❌ Error updating {file_path}: {e}")

def update_todo_list():
    """Update the todo tracking"""
    print("\n📋 Updating todo status...")
    print("  ✅ Version updated to v0.1.0-alpha")
    print("  ✅ Dead code archived (not deleted)")
    print("  ⏭️  Next: Fix TUI display issues")
    print("  ⏭️  Next: Integrate clean architecture")

def main():
    """Execute extended archiving"""
    
    print("=" * 60)
    print("🚀 Phase 1 Extended: Archive More Dead Code")
    print("=" * 60)
    
    # Archive more files
    archived_count = archive_more_files()
    
    # Update imports
    update_more_imports()
    
    # Update todo status
    update_todo_list()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Extended Archiving Complete!")
    print(f"  • Additional files archived: {archived_count}")
    print(f"  • Archive location: {ARCHIVE_DIR}")
    print("=" * 60)
    
    print("\n📋 Phase 1 Status:")
    print("  ✅ Version updated to 0.1.0-alpha")
    print("  ✅ Dead code archived (preserved for reference)")
    print("  ✅ Imports updated")
    print("  ✅ Honest README created")
    print("\n🎯 Ready for Phase 2: Fix TUI and integrate services")

if __name__ == "__main__":
    main()