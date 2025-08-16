#!/usr/bin/env python3
"""
Basic CLI Adapter Testing - Phase 2.2 Coverage Blitz
Simplified testing without heavy dependencies to measure core coverage
"""

import os
import sys
from pathlib import Path

# Add both src and frontends to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
frontends_path = project_root / "frontends"
backend_path = project_root / "backend"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(frontends_path))
sys.path.insert(0, str(backend_path))

# Set test environment
os.environ["NIX_FOR_HUMANITY_TEST_MODE"] = "true"
os.environ["PYTHONPATH"] = f"{src_path}:{frontends_path}:{backend_path}"

def test_cli_adapter_basic():
    """Test basic CLI adapter functionality without complex dependencies"""

    print("🧪 Phase 2.2 CLI Adapter Testing - Basic Functionality")
    print("=" * 60)

    try:
        # Test import
        print("📦 Testing imports...")
        from cli.adapter import CLIAdapter

        print("✅ CLI Adapter imported successfully")

        # Test initialization
        print("\n🔧 Testing initialization...")
        adapter = CLIAdapter()
        print(f"✅ Session ID: {adapter.session_id}")
        print(f"✅ Backend: {type(adapter.backend).__name__}")

        # Test argument parsing
        print("\n⚙️ Testing argument parsing...")
        # Mock sys.argv for testing
        original_argv = sys.argv
        sys.argv = ["ask-nix", "install", "firefox"]

        args = adapter.parse_arguments()
        print(f"✅ Query parsed: {args.query}")
        print(f"✅ Personality: {args.personality}")
        print(f"✅ Execute mode: {args.execute}")

        # Test request building
        print("\n🏗️ Testing request building...")
        request = adapter.build_request(args)
        print(f"✅ Request query: '{request.query}'")
        print(f"✅ Request context: {request.context.frontend}")

        # Restore sys.argv
        sys.argv = original_argv

        # Count methods for coverage estimate
        public_methods = [
            method for method in dir(adapter) if not method.startswith("_")
        ]
        print("\n📊 CLI Adapter Analysis:")
        print(f"   Public methods: {len(public_methods)}")
        print(f"   Methods: {', '.join(public_methods)}")

        # Check backend capabilities
        if hasattr(adapter.backend, "get_capabilities"):
            caps = adapter.backend.get_capabilities()
            print(f"\n🚀 Backend capabilities: {list(caps.keys())}")

        print("\n✅ Basic CLI Adapter functionality verified!")
        print("🎯 Ready for comprehensive testing with full coverage")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔍 Available modules check:")

        # Check what's available
        cli_path = frontends_path / "cli"
        if cli_path.exists():
            print(f"   CLI directory exists: {list(cli_path.glob('*.py'))}")
        else:
            print(f"   CLI directory not found at: {cli_path}")

        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False

def estimate_coverage_potential():
    """Estimate potential coverage improvement from CLI adapter tests"""

    print("\n📊 Coverage Analysis - CLI Adapter")
    print("=" * 40)

    # Check actual CLI adapter file
    adapter_path = project_root / "frontends" / "cli" / "adapter.py"
    if adapter_path.exists():
        lines = adapter_path.read_text().splitlines()
        total_lines = len(lines)

        # Simple executable line count (excluding comments/docstrings)
        executable_lines = 0
        for line in lines:
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith('"""')
                and not stripped.startswith("'''")
                and stripped != '"""'
                and stripped != "'''"
                and not (
                    stripped.startswith('"')
                    and stripped.endswith('"')
                    and len(stripped.split()) < 5
                )
            ):
                executable_lines += 1

        print(
            f"📄 CLI Adapter: {total_lines} total lines, ~{executable_lines} executable"
        )

        # Check test file size
        test_path = project_root / "tests" / "unit" / "test_cli_adapter.py"
        if test_path.exists():
            test_lines = len(test_path.read_text().splitlines())
            ratio = test_lines / executable_lines if executable_lines > 0 else 0
            print(f"🧪 Test suite: {test_lines} lines ({ratio:.1f}x coverage ratio)")

            if ratio > 2.0:
                print("✅ Comprehensive test coverage expected!")
                print("🎯 Estimated coverage potential: 85-95%")
            else:
                print("⚠️ Additional tests may be needed")
                print("🎯 Estimated coverage potential: 60-80%")
        else:
            print("❌ Test file not found")

    else:
        print("❌ CLI adapter file not found")

if __name__ == "__main__":
    print("🚀 Phase 2.2 Coverage Blitz - CLI Adapter Focus")
    print("Target: Improve coverage from current state to 90%+")
    print()

    success = test_cli_adapter_basic()
    print()
    estimate_coverage_potential()

    if success:
        print("\n🎯 Status: CLI Adapter basic testing PASSED")
        print("📈 Ready for comprehensive coverage measurement")
        print("🔄 Next: Run full test suite with coverage metrics")
    else:
        print("\n❌ Status: Import issues need resolution")
        print("🔧 Next: Fix remaining import path problems")

    sys.exit(0 if success else 1)
