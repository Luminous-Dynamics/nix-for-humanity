#!/usr/bin/env python3
"""
CLI Integration for Package Intelligence System.

Connects the smart package discovery to the ask-nix CLI interface.
"""

import asyncio
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from luminous_nix.discovery.package_intelligence import (
    PackageIntelligence, 
    PackageInfo,
    SearchIntent
)
from luminous_nix.nix.global_cache import GlobalCacheManager, cached

logger = logging.getLogger(__name__)


class PackageDiscoveryCLI:
    """
    CLI interface for intelligent package discovery.
    """
    
    def __init__(self):
        self.intelligence = PackageIntelligence()
        self.cache = GlobalCacheManager()
        self.last_search_results = []
        
    @cached('search')
    async def search(self, query: str) -> Dict[str, Any]:
        """
        Smart search with natural language understanding.
        
        Returns structured results for CLI display.
        """
        # Parse intent
        intent = self.intelligence.parse_intent(query)
        
        # Perform search
        results = await self.intelligence.search_packages(query)
        self.last_search_results = results
        
        # Structure response
        response = {
            "query": query,
            "intent": {
                "action": intent.action,
                "category": intent.category,
                "confidence": intent.confidence
            },
            "results": [],
            "suggestions": [],
            "tips": []
        }
        
        # Format results
        for pkg in results[:10]:  # Limit to top 10
            result = {
                "name": pkg.name,
                "version": pkg.version,
                "description": pkg.description[:100] + "..." if len(pkg.description) > 100 else pkg.description,
                "categories": pkg.categories,
                "tags": pkg.tags,
                "popularity": pkg.popularity,
                "install_command": f"nix-env -iA nixpkgs.{pkg.name}",
                "config_snippet": f"environment.systemPackages = with pkgs; [ {pkg.name} ];",
            }
            
            # Add alternatives if available
            if pkg.alternatives:
                result["alternatives"] = pkg.alternatives[:3]
            
            # Add recommendations
            if pkg.commonly_with:
                result["install_with"] = pkg.commonly_with[:3]
            
            response["results"].append(result)
        
        # Add contextual suggestions
        response["suggestions"] = self._generate_suggestions(intent, results)
        
        # Add helpful tips
        response["tips"] = self._generate_tips(intent, query)
        
        return response
    
    def _generate_suggestions(self, intent: SearchIntent, results: List[PackageInfo]) -> List[str]:
        """Generate contextual suggestions based on search."""
        suggestions = []
        
        if intent.action == "alternative":
            suggestions.append("Try 'compare firefox chromium' to see differences")
        
        if intent.category:
            suggestions.append(f"See all {intent.category}s with 'list {intent.category}s'")
            suggestions.append(f"Compare popular {intent.category}s with 'best {intent.category}s'")
        
        if not results:
            suggestions.append("Try a broader search term")
            suggestions.append("Check spelling or use 'similar to X' format")
        
        if len(results) > 10:
            suggestions.append("Narrow your search with more specific terms")
            suggestions.append("Use categories like 'editor', 'browser', 'terminal'")
        
        return suggestions[:3]
    
    def _generate_tips(self, intent: SearchIntent, query: str) -> List[str]:
        """Generate helpful tips for users."""
        tips = []
        
        # General tips
        tips.append("💡 Use natural language like 'I need a text editor'")
        
        # Intent-specific tips
        if intent.action == "alternative":
            tips.append("🔄 Found alternatives! These are similar packages")
        elif intent.category:
            tips.append(f"📦 Showing popular {intent.category}s sorted by relevance")
        
        # Search tips
        if "like" in query.lower() or "similar" in query.lower():
            tips.append("🎯 Finding packages similar to your request")
        
        return tips[:2]
    
    async def get_recommendations(self, installed: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get personalized package recommendations.
        """
        if not installed:
            # Try to detect installed packages
            installed = await self._detect_installed_packages()
        
        recommendations = self.intelligence.get_recommendations(installed)
        
        return {
            "based_on": installed,
            "recommendations": [
                {
                    "name": pkg.name,
                    "reason": pkg.description,
                    "install_command": f"nix-env -iA nixpkgs.{pkg.name}",
                }
                for pkg in recommendations
            ],
            "tips": [
                "💡 These packages work well with what you have installed",
                "🔧 Install multiple at once: nix-env -iA nixpkgs.{pkg1,pkg2,pkg3}"
            ]
        }
    
    async def _detect_installed_packages(self) -> List[str]:
        """Detect currently installed packages."""
        # This would normally query the actual system
        # For now, return empty list
        return []
    
    async def explore_category(self, category: str) -> Dict[str, Any]:
        """
        Explore packages in a specific category.
        """
        results = self.intelligence.search_by_category(category)
        
        return {
            "category": category,
            "description": f"Popular {category} packages",
            "packages": [
                {
                    "name": pkg.name,
                    "description": pkg.description[:80] + "...",
                    "popularity": "⭐" * int(pkg.popularity * 5),
                    "tags": pkg.tags[:3]
                }
                for pkg in results
            ],
            "subcategories": self._get_subcategories(category),
            "tips": [
                f"💡 Install the most popular: nix-env -iA nixpkgs.{results[0].name if results else 'package'}",
                f"📊 Compare options with 'compare {' '.join(r.name for r in results[:3])}'"
            ]
        }
    
    def _get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a category."""
        subcategories = {
            "development": ["languages", "tools", "ides", "version-control"],
            "media": ["players", "editors", "converters", "streaming"],
            "graphics": ["editors", "viewers", "3d", "vector"],
            "system": ["monitoring", "file-managers", "terminals", "shells"],
        }
        return subcategories.get(category, [])
    
    def format_for_display(self, response: Dict[str, Any]) -> str:
        """
        Format response for beautiful CLI display.
        """
        output = []
        
        # Header
        output.append("\n" + "="*60)
        output.append(f"🔍 Search: {response['query']}")
        output.append("="*60)
        
        # Intent understanding
        intent = response['intent']
        if intent['category']:
            output.append(f"📂 Category: {intent['category']}")
        output.append(f"🎯 Intent: {intent['action']}")
        output.append("")
        
        # Results
        if response['results']:
            output.append(f"📦 Found {len(response['results'])} packages:")
            output.append("-" * 40)
            
            for i, pkg in enumerate(response['results'], 1):
                output.append(f"\n{i}. {pkg['name']} (v{pkg['version']})")
                output.append(f"   {pkg['description']}")
                
                if pkg.get('alternatives'):
                    output.append(f"   🔄 Alternatives: {', '.join(pkg['alternatives'])}")
                
                if pkg.get('install_with'):
                    output.append(f"   📦 Install with: {', '.join(pkg['install_with'])}")
                
                output.append(f"   💻 Install: {pkg['install_command']}")
        else:
            output.append("❌ No packages found")
        
        # Suggestions
        if response['suggestions']:
            output.append("\n💡 Suggestions:")
            for suggestion in response['suggestions']:
                output.append(f"  • {suggestion}")
        
        # Tips
        if response['tips']:
            output.append("\n📝 Tips:")
            for tip in response['tips']:
                output.append(f"  {tip}")
        
        output.append("")
        return "\n".join(output)


class PackageDiscoveryCommand:
    """
    Command handler for package discovery in ask-nix CLI.
    """
    
    def __init__(self):
        self.discovery = PackageDiscoveryCLI()
    
    async def handle_command(self, args: List[str]) -> str:
        """
        Handle package discovery commands.
        
        Commands:
        - search <query>: Smart search
        - find <query>: Alias for search
        - alternative <package>: Find alternatives
        - recommend: Get recommendations
        - explore <category>: Browse category
        """
        if not args:
            return self.show_help()
        
        command = args[0].lower()
        
        if command in ["search", "find"]:
            query = " ".join(args[1:])
            if not query:
                return "Please provide a search query"
            
            response = await self.discovery.search(query)
            return self.discovery.format_for_display(response)
        
        elif command == "alternative":
            if len(args) < 2:
                return "Please specify a package to find alternatives for"
            
            package = args[1]
            query = f"alternative to {package}"
            response = await self.discovery.search(query)
            return self.discovery.format_for_display(response)
        
        elif command == "recommend":
            response = await self.discovery.get_recommendations()
            return self.format_recommendations(response)
        
        elif command == "explore":
            if len(args) < 2:
                return "Please specify a category to explore"
            
            category = args[1]
            response = await self.discovery.explore_category(category)
            return self.format_category(response)
        
        else:
            # Treat entire input as search query
            query = " ".join(args)
            response = await self.discovery.search(query)
            return self.discovery.format_for_display(response)
    
    def format_recommendations(self, response: Dict[str, Any]) -> str:
        """Format recommendations for display."""
        output = [
            "\n" + "="*60,
            "🎯 Personalized Recommendations",
            "="*60,
            ""
        ]
        
        if response['based_on']:
            output.append(f"Based on: {', '.join(response['based_on'])}")
            output.append("")
        
        for rec in response['recommendations']:
            output.append(f"📦 {rec['name']}")
            output.append(f"   {rec['reason']}")
            output.append(f"   💻 {rec['install_command']}")
            output.append("")
        
        for tip in response['tips']:
            output.append(tip)
        
        return "\n".join(output)
    
    def format_category(self, response: Dict[str, Any]) -> str:
        """Format category exploration for display."""
        output = [
            "\n" + "="*60,
            f"📂 Category: {response['category']}",
            "="*60,
            f"{response['description']}",
            ""
        ]
        
        for pkg in response['packages']:
            output.append(f"📦 {pkg['name']} {pkg['popularity']}")
            output.append(f"   {pkg['description']}")
            if pkg['tags']:
                output.append(f"   🏷️  {', '.join(pkg['tags'])}")
            output.append("")
        
        if response['subcategories']:
            output.append("📁 Subcategories:")
            for sub in response['subcategories']:
                output.append(f"  • {sub}")
            output.append("")
        
        for tip in response['tips']:
            output.append(tip)
        
        return "\n".join(output)
    
    def show_help(self) -> str:
        """Show help for package discovery."""
        return """
╔══════════════════════════════════════════════════════════════╗
║              📦 Package Discovery Commands                   ║
╚══════════════════════════════════════════════════════════════╝

Natural Language Search:
  search <query>         Smart package search
  find <query>          Alias for search
  
  Examples:
    search I need a text editor
    search music player
    find browser

Finding Alternatives:
  alternative <package>  Find alternative packages
  
  Examples:
    alternative firefox
    alternative docker

Recommendations:
  recommend             Get personalized recommendations
  
Categories:
  explore <category>    Browse packages by category
  
  Examples:
    explore editors
    explore development
    explore media

Tips:
  💡 Use natural language: "I need something like Photoshop"
  🔄 Find alternatives: "alternative to firefox"
  📂 Browse categories: "explore graphics"
  🎯 Get recommendations based on what you have installed
"""


# Integration with main CLI
async def integrate_with_cli():
    """
    Example of integrating with the main ask-nix CLI.
    """
    discovery = PackageDiscoveryCommand()
    
    # Example commands
    examples = [
        ["search", "I", "need", "a", "text", "editor"],
        ["alternative", "firefox"],
        ["explore", "development"],
        ["recommend"],
    ]
    
    print("🚀 Package Discovery CLI Integration Demo")
    print("="*60)
    
    for args in examples:
        print(f"\n📝 Command: {' '.join(args)}")
        result = await discovery.handle_command(args)
        print(result)


if __name__ == "__main__":
    asyncio.run(integrate_with_cli())