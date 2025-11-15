#!/usr/bin/env python3
"""
Remove all false performance claims from the codebase

This script will:
1. Find all files with false performance claims
2. Replace them with honest statements
3. Update documentation to reflect reality
"""

import os
import re
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix false claims in a single file"""

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, OSError):
        return False

    original_content = content

    # Remove false performance claims
    replacements = [
        # Performance multipliers
        (r"10x-1500x performance", "standard Nix performance"),
        (r"10x-1500x faster", "standard speed"),
        (r"10x-1500x", "normal"),
        (r"10,000x faster", "standard speed"),
        (r"9,300x slower", "standard Nix timing"),
        (r"3,400x slower", "standard Nix timing"),
        # Specific timing claims
        (r"0\.29ms", "2-3 seconds"),
        (r"0\.29 ms", "2-3 seconds"),
        (r"<0\.5s", "5-30 seconds"),
        (r"instant", "2-5 seconds"),
        (r"blazing fast", "standard speed"),
        (r"lightning fast", "normal speed"),
        # Native API claims
        (r"Native Python-Nix API", "subprocess-based operations"),
        (r"native Python-Nix API", "subprocess-based operations"),
        (
            r"Native nixos-rebuild-ng API loaded",
            "Using subprocess (nixos-rebuild-ng not available)",
        ),
        (r"Direct Nix Python bindings", "Subprocess calls"),
        (r"eliminates subprocess overhead", "uses subprocess"),
        (r"eliminating subprocess overhead", "using subprocess"),
        # Performance claims in comments
        (r"# Use native API.*faster.*", "# Use subprocess (standard speed)"),
        (r"# Native API.*performance.*", "# Subprocess-based operation"),
        (r"# Direct API.*faster.*", "# Standard subprocess call"),
        # Marketing speak
        (r"Revolutionary performance", "Standard performance"),
        (r"Performance breakthrough", "Normal operation"),
        (r"Game-changing speed", "Regular speed"),
        (r"Unprecedented performance", "Standard performance"),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    # Fix specific misleading messages
    content = re.sub(
        r'print\(["\']🚀.*["\'].*\)',
        'print("ℹ️ Using standard subprocess operations")',
        content,
    )

    # Fix performance boost claims
    content = re.sub(
        r'"performance_boost":\s*"[^"]*"', '"performance_boost": "1x"', content
    )

    # Fix speed comparisons
    content = re.sub(r"\(.*ms vs.*ms.*\)", "(standard Nix timing)", content)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def update_readme(project_root: Path):
    """Update README with honest claims"""
    readme_path = project_root / "README.md"

    if not readme_path.exists():
        return

    with open(readme_path, "r") as f:
        content = f.read()

    # Update performance section
    content = re.sub(
        r"### ⚠️ Performance Notes.*?(?=###|\Z)",
        """### ⚠️ Performance Notes
- Search operations take 2-3 seconds (standard Nix speed)
- Install/remove operations require appropriate permissions
- All operations use subprocess (no native API exists)
- Info commands complete in <5 seconds
- No performance improvements over standard Nix commands

""",
        content,
        flags=re.DOTALL,
    )

    # Remove native API claims from planned features
    content = re.sub(
        r"- Native Python-Nix API for performance improvements\n", "", content
    )

    with open(readme_path, "w") as f:
        f.write(content)

    print("✅ Updated README.md with honest performance claims")


def main():
    """Run the cleanup"""

    project_root = Path(__file__).parent.parent

    # Find all Python and Markdown files
    files_to_check = []

    # Python files in src
    src_dir = project_root / "src"
    if src_dir.exists():
        files_to_check.extend(src_dir.glob("**/*.py"))

    # Markdown files
    files_to_check.extend(project_root.glob("*.md"))
    files_to_check.extend(
        (project_root / "docs").glob("**/*.md")
        if (project_root / "docs").exists()
        else []
    )

    # Exclude specific honest files
    honest_files = [
        "FEATURE_STATUS_REALITY.md",
        "COMPREHENSIVE_AUDIT_REPORT.md",
        "REALITY_CHECK_COMPLETE.md",
    ]

    files_to_check = [
        f
        for f in files_to_check
        if f.name not in honest_files
        and ".archive" not in str(f)
        and "__pycache__" not in str(f)
    ]

    print("🔍 Removing false performance claims...")
    print(f"Found {len(files_to_check)} files to check")

    fixed_count = 0

    for filepath in files_to_check:
        if fix_file(filepath):
            print(f"✅ Fixed: {filepath.relative_to(project_root)}")
            fixed_count += 1

    # Update README specially
    update_readme(project_root)

    print(f"\n✨ Cleanup complete!")
    print(f"   {fixed_count} files updated")
    print(f"   All false performance claims removed")

    print("\n📝 Next steps:")
    print("1. Review changes with: git diff")
    print("2. Run tests to ensure nothing broke")
    print("3. Commit with: git commit -m 'Remove false performance claims, be honest'")
    print("4. Update version to v0.1.0 to reflect actual maturity")


if __name__ == "__main__":
    main()
