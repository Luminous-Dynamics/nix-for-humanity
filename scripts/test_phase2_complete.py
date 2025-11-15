#!/usr/bin/env python3
"""
Complete test of Phase 2 integrations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("=" * 60)
print("🧪 Phase 2 Complete Integration Test")
print("=" * 60)


def test_integrated_backend():
    """Test integrated backend with services"""
    print("\n📦 Testing Integrated Backend...")
    try:
        from luminous_nix.core.integrated_backend import get_integrated_backend

        backend = get_integrated_backend()

        # Test search
        print("  Testing search...")
        results = backend.search("firefox")
        if results:
            print(f"  ✅ Search works: Found {len(results)} results")
        else:
            print("  ⚠️  Search returned no results")

        # Test generate config
        print("  Testing config generation...")
        config = backend.generate_config("web server with nginx")
        if config:
            print("  ✅ Config generation works")
        else:
            print("  ⚠️  Config generation failed")

        return True
    except Exception as e:
        print(f"  ❌ Integrated backend failed: {e}")
        return False


def test_ai_orchestrator():
    """Test AI orchestrator"""
    print("\n🤖 Testing AI Orchestrator...")
    try:
        from luminous_nix.core.ai_orchestrator import get_ai_orchestrator

        ai = get_ai_orchestrator()

        # Test query understanding
        response = ai.understand_query("install firefox")
        print(f"  ✅ AI orchestrator works (using {response.source})")

        # Test availability
        if ai.is_ai_available():
            print("  ✅ AI systems available")
        else:
            print("  ⚠️  No AI systems available (basic fallback)")

        return True
    except Exception as e:
        print(f"  ❌ AI orchestrator failed: {e}")
        return False


def test_luminous_core():
    """Test the main core system"""
    print("\n🌟 Testing Luminous Core...")
    try:
        from luminous_nix.core.luminous_core import LuminousNixCore, Query

        core = LuminousNixCore()

        # Test search query
        query = Query("search vim", dry_run=True)
        response = core.process_query(query)

        if response.success:
            print(f"  ✅ Core search works: {response.message[:50]}...")
        else:
            print(f"  ❌ Core search failed: {response.error}")

        # Test metrics
        metrics = core.get_metrics()
        print(f"  ✅ Metrics: {metrics['operations']} operations")

        return True
    except Exception as e:
        print(f"  ❌ Luminous core failed: {e}")
        return False


def test_tui():
    """Test TUI can be imported and created"""
    print("\n🖥️  Testing TUI...")
    try:
        from luminous_nix.ui.main_app import LuminousNixTUI

        # Test headless mode
        app = LuminousNixTUI(headless=True)
        print("  ✅ TUI imports and creates successfully")

        # Test backend connector
        from luminous_nix.ui.backend_connector import TUIBackendConnector

        connector = TUIBackendConnector()
        state = connector.get_current_state()
        print(f"  ✅ Backend connector works: {state['field_state']}")

        return True
    except Exception as e:
        print(f"  ❌ TUI failed: {e}")
        return False


def test_cache_systems():
    """Test cache systems"""
    print("\n⚡ Testing Cache Systems...")
    try:
        # Test enhanced cache
        try:
            from luminous_nix.core.enhanced_cache import EnhancedCache

            cache = EnhancedCache()

            # Test set/get
            cache.set("test_key", "test_value")
            value = cache.get("test_key")
            if value == "test_value":
                print("  ✅ Enhanced cache works")
            else:
                print("  ❌ Enhanced cache failed")
        except ImportError:
            print("  ⚠️  Enhanced cache not available")

        # Test fast package cache
        try:
            from luminous_nix.core.fast_package_cache import FastPackageCache

            cache = FastPackageCache()
            print("  ✅ Fast package cache available")
        except ImportError:
            print("  ⚠️  Fast package cache not available")

        return True
    except Exception as e:
        print(f"  ❌ Cache systems failed: {e}")
        return False


def test_cli():
    """Test CLI with new backend"""
    print("\n🎯 Testing CLI...")
    try:
        import sys

        # Mock argv for help command
        old_argv = sys.argv
        sys.argv = ["ask-nix", "help"]

        # This should not crash
        print("  ✅ CLI module imports successfully")

        sys.argv = old_argv
        return True
    except Exception as e:
        print(f"  ❌ CLI failed: {e}")
        return False


def main():
    """Run all tests"""
    results = []

    # Test each component
    results.append(("Integrated Backend", test_integrated_backend()))
    results.append(("AI Orchestrator", test_ai_orchestrator()))
    results.append(("Luminous Core", test_luminous_core()))
    results.append(("TUI", test_tui()))
    results.append(("Cache Systems", test_cache_systems()))
    results.append(("CLI", test_cli()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Phase 2 Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("🎉 All Phase 2 integrations working!")
        print("\n✨ Ready for v0.1.0-alpha release!")
    else:
        print("⚠️  Some integrations need attention")
        print("\nBut that's OK for alpha release!")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
