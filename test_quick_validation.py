#!/usr/bin/env python3
"""
Quick validation test to ensure basic functionality works
"""

from src.luminous_nix.core.intelligent_system import (
    IntelligentCLI,
    LuminousNixIntelligence,
)


def test_basic_operations():
    """Test basic operations without stress"""
    print("🧪 Quick Validation Test")
    print("=" * 60)

    # Test 1: Basic search
    print("\n1. Basic Search Test:")
    intelligence = LuminousNixIntelligence()

    test_queries = ["firefox", "python", "vim", "docker", "git"]
    all_passed = True

    for query in test_queries:
        try:
            response = intelligence.intelligent_search(query, use_all_features=False)

            # Check response structure
            has_results = response.results is not None and isinstance(
                response.results, list
            )
            has_intent = response.intent is not None
            has_time = response.response_time_ms > 0

            passed = has_results and has_intent and has_time

            status = "✅" if passed else "❌"
            print(
                f"  {status} '{query}': {len(response.results)} results in {response.response_time_ms:.1f}ms"
            )

            if not passed:
                all_passed = False
                if not has_results:
                    print("     ERROR: No results or wrong type")
                if not has_intent:
                    print("     ERROR: No intent")
                if not has_time:
                    print("     ERROR: Invalid time")

        except Exception as e:
            print(f"  ❌ '{query}': ERROR - {e}")
            all_passed = False

    intelligence.shutdown()

    # Test 2: CLI wrapper
    print("\n2. CLI Wrapper Test:")
    cli = IntelligentCLI()

    try:
        result = cli.search("install web browser")

        has_query = "query" in result
        has_results = "results" in result and isinstance(result["results"], list)
        has_time = "response_time" in result

        cli_passed = has_query and has_results and has_time

        if cli_passed:
            print(f"  ✅ CLI search works: {len(result['results'])} results")
        else:
            print("  ❌ CLI search failed")
            if not has_query:
                print("     ERROR: No query in result")
            if not has_results:
                print("     ERROR: No results in result")
            if not has_time:
                print("     ERROR: No response_time in result")

    except Exception as e:
        print(f"  ❌ CLI error: {e}")
        cli_passed = False

    cli.shutdown()

    # Test 3: Cache corruption handling
    print("\n3. Cache Corruption Test:")
    intelligence = LuminousNixIntelligence()

    # Intentionally corrupt cache
    intelligence.base_cache.l1_cache["test"] = None
    intelligence.base_cache.l1_cache["corrupt"] = "not a dict"
    intelligence.base_cache.l1_cache["invalid"] = {"missing": "fields"}

    try:
        # Should handle corrupted entries gracefully
        response = intelligence.intelligent_search("test", use_all_features=False)
        print("  ✅ Handles corrupted cache gracefully")
        corruption_handled = True
    except Exception as e:
        print(f"  ❌ Failed with corrupted cache: {e}")
        corruption_handled = False

    intelligence.shutdown()

    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)

    print(f"  Basic Search: {'✅ PASS' if all_passed else '❌ FAIL'}")
    print(f"  CLI Wrapper: {'✅ PASS' if cli_passed else '❌ FAIL'}")
    print(f"  Error Handling: {'✅ PASS' if corruption_handled else '❌ FAIL'}")

    overall = all_passed and cli_passed and corruption_handled

    print("\n" + "=" * 60)
    if overall:
        print("✅ VALIDATION PASSED - System is functional")
    else:
        print("❌ VALIDATION FAILED - Issues need fixing")
    print("=" * 60)

    return overall


if __name__ == "__main__":
    success = test_basic_operations()
    exit(0 if success else 1)
