#!/usr/bin/env python3
"""
Test script for Smart Query Routing

Tests both NixOS and general IT queries to verify routing works correctly.
"""

from src.luminous_nix.ai.routing.query_router import QueryRouter, Domain

def test_query_routing():
    """Test the query router with various queries"""

    router = QueryRouter()

    test_cases = [
        # NixOS queries (should route to Domain.NIXOS)
        ("how do I install firefox on nixos?", Domain.NIXOS),
        ("create a flake.nix for python", Domain.NIXOS),
        ("nixos-rebuild switch failing", Domain.NIXOS),
        ("configure nginx on nixos", Domain.NIXOS),

        # Programming queries (should route to Domain.PROGRAMMING)
        ("how do I write async javascript?", Domain.PROGRAMMING),
        ("debug this python error", Domain.PROGRAMMING),
        ("rust ownership rules", Domain.PROGRAMMING),

        # DevOps queries (should route to Domain.DEVOPS)
        ("setup docker container", Domain.DEVOPS),
        ("kubernetes deployment yaml", Domain.DEVOPS),
        ("ci/cd with gitlab", Domain.DEVOPS),

        # Networking queries (should route to Domain.NETWORKING)
        ("configure vpn", Domain.NETWORKING),
        ("firewall rules", Domain.NETWORKING),
        ("dns not resolving", Domain.NETWORKING),

        # Database queries (should route to Domain.DATABASE)
        ("postgresql optimization", Domain.DATABASE),
        ("mongodb schema design", Domain.DATABASE),

        # Security queries (should route to Domain.SECURITY)
        ("ssl certificate setup", Domain.SECURITY),

        # General queries (should route to Domain.GENERAL)
        ("help me", Domain.GENERAL),
        ("what should I do", Domain.GENERAL),
    ]

    print("🔀 Testing Smart Query Routing\n")
    print("=" * 70)

    results = {
        "total": len(test_cases),
        "correct": 0,
        "incorrect": 0,
        "by_domain": {}
    }

    for query, expected_domain in test_cases:
        route = router.route(query)

        # Check if routing is correct
        is_correct = route.domain == expected_domain
        results["correct" if is_correct else "incorrect"] += 1

        # Track by domain
        domain_name = expected_domain.value
        if domain_name not in results["by_domain"]:
            results["by_domain"][domain_name] = {"correct": 0, "total": 0}
        results["by_domain"][domain_name]["total"] += 1
        if is_correct:
            results["by_domain"][domain_name]["correct"] += 1

        # Display result
        status = "✅" if is_correct else "❌"
        emoji = router.get_domain_emoji(route.domain)
        display_name = router.get_domain_display_name(route.domain)

        print(f"{status} {emoji} {display_name}")
        print(f"   Query: {query}")
        print(f"   Expected: {expected_domain.value}")
        print(f"   Got: {route.domain.value}")
        print(f"   Confidence: {route.confidence:.2f}")
        if route.should_offer_nixos_context:
            print(f"   💡 Offers NixOS context!")
        if not is_correct:
            print(f"   ⚠️  INCORRECT ROUTING!")
        print()

    # Print summary
    print("=" * 70)
    print("\n📊 Test Summary\n")

    accuracy = (results["correct"] / results["total"]) * 100
    print(f"Overall Accuracy: {results['correct']}/{results['total']} ({accuracy:.1f}%)")
    print()

    print("Accuracy by Domain:")
    for domain, stats in sorted(results["by_domain"].items()):
        domain_accuracy = (stats["correct"] / stats["total"]) * 100
        print(f"  {domain}: {stats['correct']}/{stats['total']} ({domain_accuracy:.1f}%)")

    print()

    if accuracy == 100.0:
        print("🎉 ALL TESTS PASSED! Perfect routing accuracy!")
    elif accuracy >= 90.0:
        print("✅ Tests mostly passed. Good routing accuracy.")
    else:
        print("⚠️  Some tests failed. Routing needs improvement.")

    print("\n" + "=" * 70)

    return accuracy == 100.0


if __name__ == "__main__":
    success = test_query_routing()
    exit(0 if success else 1)
