#!/usr/bin/env python3
"""
Migration script: Replace persona system with user preferences

This script will:
1. Find all files using the persona system
2. Update imports to use user_preferences instead
3. Replace PersonalityManager with UserPreferences
4. Update documentation to remove false claims
"""

import os
import re
from pathlib import Path


def migrate_file(filepath: Path) -> bool:
    """Migrate a single file from personas to preferences"""

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, OSError):
        # Skip binary files or files with encoding issues
        return False

    original_content = content

    # Update imports
    content = re.sub(
        r"from luminous_nix\.core\.personality import.*",
        "from luminous_nix.core.user_preferences import get_preferences",
        content,
    )

    content = re.sub(
        r"from \.personality import.*",
        "from .user_preferences import get_preferences",
        content,
    )

    content = re.sub(
        r"import luminous_nix\.core\.personality.*",
        "import luminous_nix.core.user_preferences",
        content,
    )

    # Replace PersonalityManager with UserPreferences
    content = re.sub(r"PersonalityManager\(\)", "get_preferences()", content)

    content = re.sub(r"personality_manager", "preferences", content)

    content = re.sub(
        r"PersonalityStyle\.\w+", '"friendly"', content  # Default to friendly style
    )

    # Replace adaptive claims with honest ones
    content = re.sub(
        r"10-persona adaptive system",
        "configurable user preferences",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r"learns your patterns",
        "remembers your preferences",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r"AI-powered persona detection",
        "simple preference settings",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r"adaptive interface", "configurable interface", content, flags=re.IGNORECASE
    )

    content = re.sub(
        r"personality adaptation",
        "preference configuration",
        content,
        flags=re.IGNORECASE,
    )

    # Update method calls
    content = re.sub(r"\.get_response\(", ".get_response_style()[", content)

    content = re.sub(
        r"\.adapt_response\(",
        "# adapt_response removed - using simple templates\n# ",
        content,
    )

    content = re.sub(
        r"\.learn_from_interaction\(",
        "# learn_from_interaction removed - no learning\n# ",
        content,
    )

    if content != original_content:
        with open(filepath, "w") as f:
            f.write(content)
        return True

    return False


def main():
    """Run the migration"""

    project_root = Path(__file__).parent.parent

    # Only process our source files, not dependencies
    src_dir = project_root / "src"
    bin_dir = project_root / "bin"
    tests_dir = project_root / "tests"

    python_files = []
    if src_dir.exists():
        python_files.extend(src_dir.glob("**/*.py"))
    if tests_dir.exists():
        python_files.extend(tests_dir.glob("**/*.py"))

    # Also check bin scripts
    for bin_file in bin_dir.glob("*"):
        if bin_file.is_file() and not bin_file.suffix:
            python_files.append(bin_file)

    # Exclude archive and cache
    python_files = [
        f
        for f in python_files
        if ".archive" not in str(f)
        and "__pycache__" not in str(f)
        and ".venv" not in str(f)
        and "venv" not in str(f)
    ]

    print("🔄 Migrating from persona system to user preferences...")
    print(f"Found {len(python_files)} Python files to check")

    migrated_count = 0

    for filepath in python_files:
        if migrate_file(filepath):
            print(f"✅ Migrated: {filepath.relative_to(project_root)}")
            migrated_count += 1

    print(f"\n✨ Migration complete!")
    print(f"   {migrated_count} files updated")

    # Move personality.py to archive
    personality_file = project_root / "src/luminous_nix/core/personality.py"
    if personality_file.exists():
        archive_dir = project_root / "docs/design/personas"
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_path = archive_dir / "personality_system_design.py"
        personality_file.rename(archive_path)
        print(f"📦 Archived personality.py to docs/design/personas/")

    print("\n📝 Next steps:")
    print("1. Review the changes with git diff")
    print("2. Run tests to ensure everything works")
    print("3. Update documentation to reflect reality")
    print("4. Commit with message: 'Remove persona system, add honest preferences'")


if __name__ == "__main__":
    main()
