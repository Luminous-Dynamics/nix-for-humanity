#!/usr/bin/env python3
"""
Example usage of the Luminous Nix Intelligent API
Shows how to leverage all intelligent features through a clean interface
"""

import asyncio

from src.luminous_nix.api.intelligent_api import (
    create_api,
    quick_search_sync,
)


def example_basic_search():
    """Example: Basic package search"""
    print("\n📦 Example 1: Basic Search")
    print("=" * 50)

    api = create_api()

    # Search for a web browser
    response = api.search("install web browser", limit=5)

    if response.success:
        print(f"✅ {response.message}")
        print(f"⏱️ Response time: {response.metadata['response_time_ms']:.1f}ms")
        print(f"🎯 Intent: {response.metadata['intent']}")
        print(f"💡 Suggested: {response.metadata['suggested_packages']}")

        print("\nResults:")
        for i, result in enumerate(response.data, 1):
            print(f"  {i}. {result['name']} ({result['version']})")
            print(f"     {result['description'][:60]}...")
    else:
        print(f"❌ {response.message}")

    api.shutdown()


def example_smart_suggestions():
    """Example: Get smart suggestions for partial queries"""
    print("\n💡 Example 2: Smart Suggestions")
    print("=" * 50)

    api = create_api()

    # Get suggestions for partial query
    response = api.suggest("pyth")

    if response.success:
        print(f"✅ {response.message}")
        print("\nSuggestions:")
        for suggestion in response.data:
            icon = "🧠" if suggestion["type"] == "semantic" else "🔮"
            confidence = suggestion["confidence"]
            print(f"  {icon} {suggestion['text']} (confidence: {confidence:.1%})")

    api.shutdown()


def example_learning():
    """Example: Teach the system from user feedback"""
    print("\n🎓 Example 3: Learning from Feedback")
    print("=" * 50)

    api = create_api()

    # User searched for "IDE" and selected "vscode"
    response = api.learn(
        query="best IDE for web development", selected="vscode", satisfied=True
    )

    if response.success:
        print(f"✅ {response.message}")
        print("System will now prefer 'vscode' for similar queries")

    api.shutdown()


def example_install_commands():
    """Example: Get install commands"""
    print("\n🛠️ Example 4: Install Commands")
    print("=" * 50)

    api = create_api()

    # Get temporary install command
    response = api.get_install_command("firefox", permanent=False)
    if response.success:
        print("Temporary install:")
        print(f"  {response.data['command']}")

    # Get permanent install command
    response = api.get_install_command("firefox", permanent=True)
    if response.success:
        print("\nPermanent install:")
        for step in response.data["steps"]:
            print(f"  {step}")

    api.shutdown()


def example_analytics():
    """Example: Get system insights"""
    print("\n📊 Example 5: Analytics & Insights")
    print("=" * 50)

    api = create_api()

    # Make some searches first
    api.search("firefox")
    api.search("python")
    api.search("vim")

    # Get insights
    response = api.get_insights()

    if response.success:
        insights = response.data
        print("Session stats:")
        print(f"  • Queries: {insights['session']['total_queries']}")
        print(f"  • Avg response: {insights['session']['average_response_ms']:.1f}ms")
        print(f"  • Cache hit rate: {insights['session']['cache_hit_rate']:.1%}")

        print("\nPerformance:")
        print(f"  • Queue size: {insights['performance']['queue_size']}")
        print(f"  • Writes completed: {insights['performance']['writes_completed']}")

    # Get popular packages
    response = api.get_popular_packages(5)
    if response.success and response.data:
        print("\nPopular packages:")
        for pkg in response.data:
            print(f"  • {pkg['name']} (used {pkg['frequency']} times)")

    api.shutdown()


def example_batch_operations():
    """Example: Batch search for multiple queries"""
    print("\n🚀 Example 6: Batch Operations")
    print("=" * 50)

    api = create_api()

    queries = [
        "text editor",
        "web browser",
        "python development",
        "docker containers",
        "git version control",
    ]

    response = api.batch_search(queries)

    if response.success:
        print(f"✅ {response.message}")
        print(f"⏱️ Total time: {response.metadata['total_time_ms']:.1f}ms")
        print(f"   Avg per query: {response.metadata['avg_time_ms']:.1f}ms")

        print("\nResults summary:")
        for query, result in response.data.items():
            count = len(result["results"])
            time_ms = result["response_time_ms"]
            print(f"  • '{query}': {count} results in {time_ms:.1f}ms")

    api.shutdown()


async def example_async_operations():
    """Example: Async operations for better performance"""
    print("\n⚡ Example 7: Async Operations")
    print("=" * 50)

    api = create_api()

    # Async search
    response = await api.search_async("install rust compiler")

    if response.success:
        print(f"✅ Async search completed: {len(response.data)} results")

    # Async batch search
    queries = ["vim", "emacs", "neovim", "vscode", "sublime"]
    response = await api.batch_search_async(queries)

    if response.success:
        print(f"✅ Async batch completed: {response.message}")
        for query in queries:
            count = len(response.data[query]["results"])
            print(f"  • '{query}': {count} results")

    api.shutdown()


def example_health_check():
    """Example: Check system health"""
    print("\n🏥 Example 8: Health Check")
    print("=" * 50)

    api = create_api()

    response = api.health_check()

    if response.success:
        print(f"System status: {response.message}")
        print("\nComponent health:")
        for component, status in response.data.items():
            icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
            print(f"  {icon} {component}: {status}")

    api.shutdown()


def example_quick_helpers():
    """Example: Using quick helper functions"""
    print("\n🎯 Example 9: Quick Helpers")
    print("=" * 50)

    # Quick synchronous search
    results = quick_search_sync("firefox")
    print(f"Quick search found {len(results)} results:")
    for result in results[:3]:
        print(f"  • {result['name']}")


def main():
    """Run all examples"""
    print("🌟 Luminous Nix Intelligent API Examples")
    print("=" * 70)
    print("Demonstrating all intelligent features through clean API\n")

    # Run synchronous examples
    example_basic_search()
    example_smart_suggestions()
    example_learning()
    example_install_commands()
    example_analytics()
    example_batch_operations()
    example_health_check()
    example_quick_helpers()

    # Run async examples
    print("\n" + "=" * 70)
    print("Running async examples...")
    asyncio.run(example_async_operations())

    print("\n" + "=" * 70)
    print("✅ All examples completed successfully!")
    print("\n💡 Key Takeaways:")
    print("  • Simple API masks complex intelligence")
    print("  • All 5 features working together seamlessly")
    print("  • <10ms response times for most operations")
    print("  • System learns and improves with use")
    print("  • Async support for high-performance applications")


if __name__ == "__main__":
    main()
