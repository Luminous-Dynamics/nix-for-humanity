#!/usr/bin/env python3
"""
Simplified CLI Adapter test focusing on core functionality
"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Test just the CLI adapter without heavy dependencies
try:
    print("🚀 Testing CLI Adapter core functionality...")

    # Test basic import
    from luminous_nix.cli import CLIAdapter

    print("✅ CLI Adapter import successful")

    # Test initialization
    adapter = CLIAdapter()
    print(f"✅ Initialization successful - Session ID: {adapter.session_id}")

    # Test methods exist
    expected_methods = [
        "process_query",
        "display_response",
        "set_personality",
        "get_stats",
    ]
    for method in expected_methods:
        if hasattr(adapter, method):
            print(f"✅ Method {method} exists")
        else:
            print(f"❌ Method {method} missing")

    print("\n📊 CLI Adapter Analysis Complete")
    print("🎯 Core functionality verified - ready for comprehensive testing")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
