"""
Search Service - Clean, focused package search

Single responsibility: Find NixOS packages based on queries.
No caching logic, no display logic, just search.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import subprocess
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Package:
    """Clean package representation"""

    name: str
    description: str
    version: Optional[str] = None
    source: str = "nixpkgs"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "source": self.source,
        }


@dataclass
class SearchResult:
    """Clean search result"""

    packages: List[Package]
    query: str
    elapsed_ms: float
    source: str = "direct"  # direct, cache, semantic

    @property
    def count(self) -> int:
        return len(self.packages)


class SearchService:
    """
    Clean search service with single responsibility.

    This service ONLY searches for packages. It doesn't:
    - Handle caching (that's CacheService's job)
    - Format output (that's the UI's job)
    - Execute commands (that's NixExecutor's job)
    """

    def __init__(self, timeout: int = 5):
        """
        Initialize search service.

        Args:
            timeout: Search timeout in seconds
        """
        self.timeout = timeout

    def search(self, query: str, limit: int = 30) -> SearchResult:
        """
        Search for packages matching query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            SearchResult with found packages
        """
        import time

        start = time.time()

        packages = self._search_nix(query, limit)

        elapsed_ms = (time.time() - start) * 1000

        return SearchResult(
            packages=packages, query=query, elapsed_ms=elapsed_ms, source="direct"
        )

    def _search_nix(self, query: str, limit: int) -> List[Package]:
        """
        Search using nix search command.

        Private method that does the actual subprocess call.
        """
        try:
            result = subprocess.run(
                ["nix", "search", "nixpkgs", query, "--json"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                logger.warning(f"Search failed: {result.stderr}")
                return []

            if not result.stdout:
                return []

            # Parse JSON output
            data = json.loads(result.stdout)
            packages = []

            for full_name, info in list(data.items())[:limit]:
                # Extract package name from full path
                name = full_name.split(".")[-1]

                packages.append(
                    Package(
                        name=name,
                        description=info.get("description", ""),
                        version=info.get("version", ""),
                        source="nixpkgs",
                    )
                )

            return packages

        except subprocess.TimeoutExpired:
            logger.warning(f"Search timed out after {self.timeout}s")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse search results: {e}")
            return []
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def search_by_category(self, category: str) -> SearchResult:
        """
        Search for packages in a category.

        Categories like "editor", "browser", "database" etc.
        """
        # Map categories to search terms
        category_map = {
            "editor": "editor",
            "browser": "browser web",
            "database": "database sql",
            "terminal": "terminal emulator",
            "development": "development programming",
            "media": "video audio media",
            "graphics": "graphics image photo",
        }

        search_term = category_map.get(category.lower(), category)
        return self.search(search_term)

    def batch_search(self, queries: List[str]) -> Dict[str, SearchResult]:
        """
        Search for multiple queries efficiently.

        Useful for warming cache or bulk operations.
        """
        results = {}
        for query in queries:
            results[query] = self.search(query)
        return results
