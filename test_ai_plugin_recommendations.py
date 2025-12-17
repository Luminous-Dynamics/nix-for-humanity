#!/usr/bin/env python3
"""
Test script for AI plugin recommendations.

Tests that the AI orchestrator can recommend plugins based on queries.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from luminous_nix.core.ai_orchestrator import get_ai_orchestrator

def test_plugin_recommendations():
    """Test plugin recommendation functionality."""
    print("🧪 Testing AI Plugin Recommendations\n")
    print("=" * 70)

    # Get AI orchestrator (singleton)
    orchestrator = get_ai_orchestrator()

    print("\n✅ AI Orchestrator initialized")
    print(f"   Plugin manager available: {orchestrator.plugin_manager is not None}")

    if orchestrator.plugin_manager:
        manifests = list(orchestrator.plugin_manager._manifests.values())
        print(f"   Discovered plugins: {len(manifests)}")
        for manifest in manifests:
            print(f"     • {manifest.name} v{manifest.version}")

    print("\n" + "=" * 70)
    print("\n🔍 Testing Plugin Recommendations\n")

    # Test queries
    test_queries = [
        "I need to manage docker containers",
        "How do I run a docker-compose project?",
        "Install git and configure my dotfiles",
        "Show me how to use systemd services",
        "I want to search for packages",  # Should not recommend plugins
    ]

    for query in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        print("-" * 70)

        response = orchestrator.recommend_plugins(query)

        if response.success:
            recommendations = response.result.get('recommendations', [])
            print(f"✅ Found {len(recommendations)} recommendation(s):")
            for rec in recommendations:
                print(f"\n   🔌 {rec['name']} v{rec['version']}")
                if rec.get('description'):
                    print(f"      Description: {rec['description']}")
                if rec.get('keywords'):
                    print(f"      Matched keywords: {', '.join(rec['keywords'])}")
                print(f"      Command: {rec['command']}")
        else:
            print(f"⚪ No recommendations: {response.result}")

    print("\n" + "=" * 70)
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_plugin_recommendations()
