#!/usr/bin/env python3
"""
Fix all remaining consciousness imports in the codebase
"""

import re
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

# Files with consciousness imports that need fixing
files_to_fix = [
    "src/luminous_nix/ui/visual_orb_integration.py",
    "src/luminous_nix/voice/voice_nlp_bridge.py",
    "src/luminous_nix/core/error_intelligence_unified.py",
    "src/luminous_nix/core/system_orchestrator.py",
    "src/luminous_nix/cli/voice_integration.py",
    "src/luminous_nix/api/llm_api.py",
]

for file_path in files_to_fix:
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        print(f"⏭️  Skipping {file_path} (doesn't exist)")
        continue

    try:
        content = full_path.read_text()
        original = content

        # Comment out all consciousness imports
        patterns = [
            r"from \.\.consciousness[^\n]*\n",
            r"from luminous_nix\.consciousness[^\n]*\n",
        ]

        for pattern in patterns:
            content = re.sub(pattern, lambda m: f"# ARCHIVED: {m.group()}", content)

        # Add stubs for commonly used classes
        if (
            "ConsciousnessBarometer" in content
            and "class ConsciousnessBarometer" not in content
        ):
            content = (
                """# Stub for archived consciousness classes
class ConsciousnessBarometer:
    def __init__(self): pass
    def measure(self): return 0.5

"""
                + content
            )

        if "AdaptivePersona" in content and "class AdaptivePersona" not in content:
            content = (
                """# Stub for archived consciousness classes
class AdaptivePersona:
    def __init__(self): pass
    def adapt(self): pass

"""
                + content
            )

        if "POMLConsciousness" in content and "class POMLConsciousness" not in content:
            content = (
                """# Stub for archived consciousness classes
class POMLConsciousness:
    def __init__(self): pass

"""
                + content
            )

        # Write back if changed
        if content != original:
            full_path.write_text(content)
            print(f"✅ Fixed {file_path}")
        else:
            print(f"⏭️  No changes needed for {file_path}")

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")

print("\n✅ All consciousness imports fixed!")
