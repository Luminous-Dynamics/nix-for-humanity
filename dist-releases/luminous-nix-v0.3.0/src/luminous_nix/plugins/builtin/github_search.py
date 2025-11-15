"""
GitHub Search Plugin - Search for packages on GitHub

This plugin adds the ability to search GitHub for Nix packages
and flakes, extending the built-in search capabilities.
"""

from typing import List, Dict, Any
import subprocess
import json
import logging

from ..base import SearchPlugin, PluginInfo

logger = logging.getLogger(__name__)


class GitHubSearchPlugin(SearchPlugin):
    """
    Plugin that searches GitHub for Nix packages and flakes.

    Adds commands:
    - github:search <query> - Search GitHub for Nix packages
    - github:trending - Show trending Nix projects
    """

    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        return PluginInfo(
            name="github_search",
            version="1.0.0",
            description="Search GitHub for Nix packages and flakes",
            author="Luminous Nix Team",
            capabilities=["search", "commands"],
        )

    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize plugin"""
        self.context = context
        self.cache = context.get("cache_service")
        return True

    def _register_commands(self):
        """Register plugin commands"""
        self.register_command(
            "search", self._search_github, "Search GitHub for Nix packages"
        )
        self.register_command(
            "trending", self._trending_nix, "Show trending Nix projects"
        )

    def search(self, query: str) -> List[Dict]:
        """
        Search GitHub for Nix-related repositories.

        Args:
            query: Search query

        Returns:
            List of results
        """
        # Check cache first
        if self.cache:
            cache_key = f"github:{query}"
            cached, from_cache = self.cache.get(cache_key)
            if from_cache and cached:
                return cached

        results = []

        try:
            # Use GitHub CLI if available
            result = subprocess.run(
                [
                    "gh",
                    "search",
                    "repos",
                    f"{query} language:nix",
                    "--json",
                    "name,description,url,stargazersCount",
                    "--limit",
                    "10",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout:
                repos = json.loads(result.stdout)

                for repo in repos:
                    results.append(
                        {
                            "name": repo.get("name", ""),
                            "description": f"⭐ {repo.get('stargazersCount', 0)} - {repo.get('description', '')}",
                            "source": "github",
                            "url": repo.get("url", ""),
                        }
                    )

                # Cache results
                if self.cache and results:
                    self.cache.set(cache_key, results)

        except FileNotFoundError:
            # gh CLI not installed
            logger.debug("GitHub CLI not available")
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")

        return results

    def _search_github(self, query: str) -> str:
        """
        Command handler for GitHub search.

        Args:
            query: Search query

        Returns:
            Formatted results
        """
        results = self.search(query)

        if not results:
            return "No GitHub results found. Install 'gh' CLI for GitHub search."

        output = f"GitHub results for '{query}':\n\n"
        for result in results:
            output += f"📦 {result['name']}\n"
            output += f"   {result['description']}\n"
            if result.get("url"):
                output += f"   🔗 {result['url']}\n"
            output += "\n"

        return output

    def _trending_nix(self) -> str:
        """
        Show trending Nix projects on GitHub.

        Returns:
            Formatted trending projects
        """
        # Search for popular Nix projects
        results = self.search("stars:>100")

        if not results:
            return "Could not fetch trending projects."

        output = "🔥 Trending Nix Projects on GitHub:\n\n"
        for i, result in enumerate(results[:5], 1):
            output += f"{i}. {result['name']}\n"
            output += f"   {result['description']}\n\n"

        return output

    def get_commands(self) -> Dict[str, callable]:
        """Get plugin commands"""
        if not self.commands:
            self._register_commands()
        return self.commands

    def shutdown(self):
        """Cleanup"""
        pass
