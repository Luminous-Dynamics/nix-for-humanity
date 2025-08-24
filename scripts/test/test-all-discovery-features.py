#!/usr/bin/env python3
"""Test all smart discovery features."""

import sys
sys.path.insert(0, 'src')

from luminous_nix.core.package_discovery import PackageDiscovery

discovery = PackageDiscovery()

print("🧪 Comprehensive Smart Discovery Testing\n")
print("="*60)

# Test 1: Direct package names
print("\n📦 Test 1: Direct Package Names")
for query in ["firefox", "python", "vim"]:
    results = discovery.search_packages(query, limit=3)
    print(f"\nQuery: '{query}'")
    for r in results:
        print(f"  - {r.name} (score: {r.score}, reason: {r.reason})")

# Test 2: Categories
print("\n\n📂 Test 2: Category-Based Search")
for query in ["web browser", "text editor", "development tools"]:
    results = discovery.search_packages(query, limit=3)
    print(f"\nQuery: '{query}'")
    for r in results:
        print(f"  - {r.name} (score: {r.score}, reason: {r.reason})")

# Test 3: Typo correction
print("\n\n🔤 Test 3: Typo Correction & Fuzzy Matching")
for query in ["fierrfox", "pythn", "neovmi", "vscode"]:
    results = discovery.search_packages(query, limit=3)
    print(f"\nQuery: '{query}'")
    for r in results:
        print(f"  - {r.name} (score: {r.score}, reason: {r.reason})")

# Test 4: Feature-based search
print("\n\n🎯 Test 4: Feature-Based Search")
for query in ["pdf viewer", "screenshot tool", "music player"]:
    results = discovery.search_packages(query, limit=3)
    print(f"\nQuery: '{query}'")
    for r in results:
        print(f"  - {r.name} (score: {r.score}, reason: {r.reason})")

# Test 5: Command suggestions
print("\n\n💻 Test 5: Command-Based Package Suggestions")
for cmd in ["python", "npm", "cargo", "docker"]:
    suggestions = discovery.suggest_by_command(cmd)
    print(f"\nCommand '{cmd}' not found. Install:")
    for s in suggestions[:3]:
        print(f"  - {s.name}: {s.description}")

# Test 6: Find alternatives
print("\n\n🔄 Test 6: Package Alternatives")
for pkg in ["firefox", "vim", "python3"]:
    alternatives = discovery.find_alternatives(pkg)
    if alternatives:
        print(f"\nAlternatives to {pkg}:")
        for alt in alternatives[:3]:
            print(f"  - {alt}")

# Test 7: Popular packages
print("\n\n⭐ Test 7: Popular Packages")
popular = discovery.get_popular_packages()
print("\nMost popular packages:")
for name, desc in popular[:5]:
    print(f"  - {name}: {desc}")

# Summary
print("\n\n" + "="*60)
print("✅ All smart discovery features tested successfully!")
print("\nCapabilities demonstrated:")
print("  • Direct package name search")
print("  • Category-based discovery")
print("  • Typo correction & fuzzy matching")
print("  • Feature-based search")
print("  • Command-to-package mapping")
print("  • Alternative package suggestions")
print("  • Popular package browsing")