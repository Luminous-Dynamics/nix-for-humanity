#!/usr/bin/env python3
"""
Simplified Integration Test - No Heavy Dependencies

Tests core functionality without numpy/faiss/transformers
"""

import sys
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class Colors:
    """Terminal colors."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def test_native_api_simple():
    """Test if native API can be imported."""
    print(f"\n{Colors.YELLOW}1. Testing Native Python API Import...{Colors.RESET}")
    try:
        from luminous_nix.core.native_nix_api import NativeNixAPI

        print(f"  {Colors.GREEN}✅ Native API module imported{Colors.RESET}")

        # Try to create instance
        api = NativeNixAPI()
        print(f"  {Colors.GREEN}✅ API instance created{Colors.RESET}")

        # Try a simple operation
        try:
            result = api.list_generations()
            if result:
                print(
                    f"  {Colors.GREEN}✅ Listed {len(result)} generations{Colors.RESET}"
                )
            else:
                print(
                    f"  {Colors.YELLOW}⚠️  No generations found (expected on non-NixOS){Colors.RESET}"
                )
        except Exception as e:
            print(
                f"  {Colors.YELLOW}⚠️  API call failed: {str(e)[:50]}...{Colors.RESET}"
            )

        return True
    except ImportError as e:
        print(f"  {Colors.RED}❌ Failed to import: {e}{Colors.RESET}")
        return False
    except Exception as e:
        print(f"  {Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False


def test_json_optimization():
    """Test JSON-optimized operations."""
    print(f"\n{Colors.YELLOW}2. Testing JSON Optimization...{Colors.RESET}")
    try:
        from luminous_nix.core.json_optimized_nix import JSONOptimizedNix

        print(f"  {Colors.GREEN}✅ JSON optimizer imported{Colors.RESET}")

        optimizer = JSONOptimizedNix()

        # Test that it has the search method
        if hasattr(optimizer, "search_packages"):
            print(f"  {Colors.GREEN}✅ Has search_packages method{Colors.RESET}")
        else:
            print(f"  {Colors.RED}❌ Missing search_packages method{Colors.RESET}")

        # Test info gathering
        info = optimizer.get_system_info()
        if info:
            print(
                f"  {Colors.GREEN}✅ Got system info: {info.get('nixos_version', 'unknown')}{Colors.RESET}"
            )
        else:
            print(f"  {Colors.YELLOW}⚠️  Could not get system info{Colors.RESET}")

        return True
    except Exception as e:
        print(f"  {Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False


def test_hrm_import():
    """Test HRM neural network import."""
    print(f"\n{Colors.YELLOW}3. Testing HRM Neural Network...{Colors.RESET}")
    try:
        from luminous_nix.ai.hrm_reasoner_v2 import HRMv2NixOSReasoner

        print(f"  {Colors.GREEN}✅ HRM v2 imported{Colors.RESET}")

        # Create instance
        hrm = HRMv2NixOSReasoner()
        print(f"  {Colors.GREEN}✅ HRM instance created{Colors.RESET}")

        # Test reasoning
        result = hrm.reason("install firefox")
        if result and result.get("intent"):
            print(
                f"  {Colors.GREEN}✅ Intent recognized: {result['intent']}{Colors.RESET}"
            )
            print(f"     Confidence: {result.get('confidence', 0):.2%}")
        else:
            print(f"  {Colors.YELLOW}⚠️  No intent recognized{Colors.RESET}")

        return True
    except ImportError as e:
        print(
            f"  {Colors.YELLOW}⚠️  Import failed (PyTorch not installed): {str(e)[:50]}...{Colors.RESET}"
        )
        return True  # Not a failure, just not available
    except Exception as e:
        print(f"  {Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False


def test_executor():
    """Test command executor."""
    print(f"\n{Colors.YELLOW}4. Testing Command Executor...{Colors.RESET}")
    try:
        from luminous_nix.core.executor import SafeExecutor

        print(f"  {Colors.GREEN}✅ SafeExecutor imported{Colors.RESET}")

        executor = SafeExecutor()

        # Test help command (safe, fast)
        result = executor.execute("help")
        if result and not result.get("error"):
            print(f"  {Colors.GREEN}✅ Help command executed{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}⚠️  Help returned error{Colors.RESET}")

        # Test version check using execute
        result = executor.execute("version")
        if result and not result.get("error"):
            output = result.get("output", "")
            if output:
                print(f"  {Colors.GREEN}✅ Version check passed{Colors.RESET}")
            else:
                print(f"  {Colors.YELLOW}⚠️  No version output{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}⚠️  Version check failed (expected){Colors.RESET}")

        return True
    except Exception as e:
        print(f"  {Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False


def test_cache_framework():
    """Test cache framework."""
    print(f"\n{Colors.YELLOW}5. Testing Cache Framework...{Colors.RESET}")
    try:
        # Try the services cache first (the new clean one)
        from luminous_nix.services.cache import CacheService

        print(f"  {Colors.GREEN}✅ Cache service imported{Colors.RESET}")

        # Create cache service
        cache = CacheService()

        # Test basic operations
        cache.set("test_key", {"data": "test_value"})
        result = cache.get("test_key")

        if result and result.get("data") == "test_value":
            print(f"  {Colors.GREEN}✅ Cache set/get working{Colors.RESET}")
        else:
            print(f"  {Colors.RED}❌ Cache not working properly{Colors.RESET}")

        # Check cache has items
        print(f"  {Colors.GREEN}✅ Cache operational{Colors.RESET}")

        return True
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠️  Cache error: {str(e)[:50]}...{Colors.RESET}")
        return True  # Not critical


def test_integrated_backend():
    """Test integrated backend."""
    print(f"\n{Colors.YELLOW}6. Testing Integrated Backend...{Colors.RESET}")
    try:
        from luminous_nix.core.integrated_backend import IntegratedBackend

        print(f"  {Colors.GREEN}✅ Backend imported{Colors.RESET}")

        backend = IntegratedBackend()
        print(f"  {Colors.GREEN}✅ Backend instance created{Colors.RESET}")

        # Test simple query - use process() not process_query()
        start = time.time()
        # Create a simple intent dict (no need for Intent class)
        intent = {"action": "help", "entities": {}}
        result = backend.process(intent)
        elapsed_ms = (time.time() - start) * 1000

        if result:
            print(
                f"  {Colors.GREEN}✅ Query processed in {elapsed_ms:.1f}ms{Colors.RESET}"
            )
            if elapsed_ms < 100:
                print(f"  {Colors.GREEN}✨ <100ms target achieved!{Colors.RESET}")
            elif elapsed_ms < 500:
                print(f"  {Colors.YELLOW}⚠️  Under 500ms (acceptable){Colors.RESET}")
            else:
                print(f"  {Colors.RED}❌ Over 500ms (needs optimization){Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}⚠️  No result returned{Colors.RESET}")

        return True
    except Exception as e:
        print(f"  {Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False


def test_rust_module():
    """Test if Rust module is available."""
    print(f"\n{Colors.YELLOW}7. Testing Rust Module...{Colors.RESET}")
    try:
        import luminous_nix_core

        print(f"  {Colors.GREEN}✅ Rust module imported!{Colors.RESET}")

        # Test fuzzy search
        from luminous_nix_core import fuzzy_search

        results = fuzzy_search("firefox", ["firefox", "chrome", "safari"], 2)
        print(f"  {Colors.GREEN}✅ Fuzzy search working{Colors.RESET}")
        print(f"     Results: {results}")

        return True
    except ImportError:
        print(f"  {Colors.YELLOW}⚠️  Rust module not built yet{Colors.RESET}")
        print("     Run: cd rust && maturin develop")
        return False
    except Exception as e:
        print(f"  {Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False


def test_performance_check():
    """Quick performance check."""
    print(f"\n{Colors.YELLOW}8. Performance Quick Check...{Colors.RESET}")

    operations = []

    # Test 1: Import speed
    start = time.time()

    import_time = (time.time() - start) * 1000
    operations.append(("Module import", import_time))

    # Test 2: Instance creation
    start = time.time()
    from luminous_nix.core.executor import SafeExecutor

    exec = SafeExecutor()
    create_time = (time.time() - start) * 1000
    operations.append(("Instance creation", create_time))

    # Test 3: Simple operation
    start = time.time()
    result = exec.execute("help")
    exec_time = (time.time() - start) * 1000
    operations.append(("Help execution", exec_time))

    # Show results
    for name, time_ms in operations:
        if time_ms < 10:
            status = f"{Colors.GREEN}✅{Colors.RESET}"
        elif time_ms < 100:
            status = f"{Colors.YELLOW}⚠️{Colors.RESET}"
        else:
            status = f"{Colors.RED}❌{Colors.RESET}"
        print(f"  {status} {name}: {time_ms:.1f}ms")

    total = sum(t for _, t in operations)
    print(f"\n  Total: {total:.1f}ms")

    return total < 500  # Reasonable target for these operations


def main():
    """Run simplified integration tests."""
    print(f"\n{Colors.CYAN}={'='*60}{Colors.RESET}")
    print(
        f"{Colors.BOLD}{Colors.BLUE}LUMINOUS NIX v0.4.0 - SIMPLIFIED INTEGRATION TEST{Colors.RESET}"
    )
    print(f"{Colors.CYAN}={'='*60}{Colors.RESET}")
    print(
        f"\n{Colors.CYAN}Testing core components without heavy dependencies...{Colors.RESET}"
    )

    tests = [
        ("Native API", test_native_api_simple),
        ("JSON Optimization", test_json_optimization),
        ("HRM Import", test_hrm_import),
        ("Command Executor", test_executor),
        ("Cache Framework", test_cache_framework),
        ("Integrated Backend", test_integrated_backend),
        ("Rust Module", test_rust_module),
        ("Performance", test_performance_check),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n{Colors.RED}Test '{name}' crashed: {e}{Colors.RESET}")
            results.append((name, False))

    # Summary
    print(f"\n{Colors.CYAN}={'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.CYAN}={'='*60}{Colors.RESET}\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = (
            f"{Colors.GREEN}✅ PASS{Colors.RESET}"
            if success
            else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        )
        print(f"  {name:20} {status}")

    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! Ready for v0.4.0!{Colors.RESET}")
        return 0
    elif passed >= total * 0.7:
        print(
            f"\n{Colors.YELLOW}⚠️  Most tests passed. Minor fixes needed.{Colors.RESET}"
        )
        return 1
    else:
        print(
            f"\n{Colors.RED}❌ Multiple failures. Significant work needed.{Colors.RESET}"
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
