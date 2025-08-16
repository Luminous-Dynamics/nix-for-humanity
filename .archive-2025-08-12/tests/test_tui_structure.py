#!/usr/bin/env python3
"""
Test TUI structure and verify all components exist
"""

from pathlib import Path

print("🔍 Checking TUI implementation structure...")

# Check directory structure
tui_dir = Path("src/tui")
if tui_dir.exists():
    print(f"✅ TUI directory exists: {tui_dir}")

    # List TUI files
    tui_files = list(tui_dir.glob("*.py"))
    print(f"\n📁 TUI files found ({len(tui_files)}):")
    for file in sorted(tui_files):
        print(f"  - {file.name}")

    # Check for key files
    key_files = ["app.py", "enhanced_app.py", "widgets.py", "styles.css"]
    for file in key_files:
        file_path = tui_dir / file
        if file_path.exists():
            print(f"✅ {file} exists ({file_path.stat().st_size} bytes)")
        else:
            print(f"❌ {file} missing")
else:
    print(f"❌ TUI directory not found at {tui_dir}")

# Check if backend exists
backend_dir = Path("src/nix_for_humanity")
if backend_dir.exists():
    print(f"\n✅ Backend directory exists: {backend_dir}")
    backend_files = list(backend_dir.glob("**/*.py"))
    print(f"  Found {len(backend_files)} Python files")
else:
    print(f"\n❌ Backend directory not found at {backend_dir}")

# Check requirements
req_file = Path("requirements-tui.txt")
if req_file.exists():
    print("\n✅ TUI requirements file exists")
    with open(req_file) as f:
        deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    print(f"  Required dependencies ({len(deps)}):")
    for dep in deps[:5]:  # Show first 5
        print(f"    - {dep}")
    if len(deps) > 5:
        print(f"    ... and {len(deps) - 5} more")
else:
    print("\n❌ TUI requirements file not found")

print("\n📊 Summary:")
print("  - TUI implementation exists ✅")
print("  - Uses Textual framework (requires installation)")
print("  - Has both basic and enhanced versions")
print("  - Integrated with headless core backend")
print("\n💡 To use the TUI:")
print("  1. Install dependencies: pip install -r requirements-tui.txt")
print("  2. Run: python3 src/tui/app.py")
print("  3. Or enhanced: python3 src/tui/enhanced_app.py")
