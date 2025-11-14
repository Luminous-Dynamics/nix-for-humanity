"""
Fast Package Cache - Real performance through intelligent caching

Instead of indexing ALL packages (which takes forever), we:
1. Pre-cache the most common packages
2. Cache search results as we go
3. Build index incrementally

This gives us ACTUAL fast performance without the initial cost.
"""

import json
import logging
import pickle
import subprocess
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FastPackageCache:
    """
    Smart caching strategy for real performance improvements.

    Instead of trying to index 80,000+ packages upfront:
    1. Start with common packages (2-5 seconds)
    2. Cache searches as they happen
    3. Build knowledge over time
    """

    # Most commonly searched packages
    COMMON_PACKAGES = {
        # Browsers
        "firefox": {"description": "Web browser", "category": "browser"},
        "chromium": {"description": "Web browser", "category": "browser"},
        "brave": {"description": "Privacy-focused browser", "category": "browser"},
        "google-chrome": {
            "description": "Google Chrome browser",
            "category": "browser",
        },
        # Editors
        "vim": {"description": "Vi IMproved text editor", "category": "editor"},
        "neovim": {
            "description": "Vim-fork focused on extensibility",
            "category": "editor",
        },
        "emacs": {"description": "Extensible text editor", "category": "editor"},
        "vscode": {"description": "Visual Studio Code", "category": "editor"},
        "nano": {"description": "Simple text editor", "category": "editor"},
        # Development
        "git": {"description": "Version control system", "category": "development"},
        "docker": {"description": "Container platform", "category": "development"},
        "python3": {
            "description": "Python programming language",
            "category": "development",
        },
        "nodejs": {"description": "JavaScript runtime", "category": "development"},
        "rustc": {"description": "Rust compiler", "category": "development"},
        "gcc": {"description": "GNU Compiler Collection", "category": "development"},
        # Terminal
        "alacritty": {
            "description": "GPU-accelerated terminal",
            "category": "terminal",
        },
        "kitty": {"description": "Fast, feature-rich terminal", "category": "terminal"},
        "tmux": {"description": "Terminal multiplexer", "category": "terminal"},
        "zsh": {"description": "Z shell", "category": "shell"},
        "fish": {"description": "Friendly interactive shell", "category": "shell"},
        # System tools
        "htop": {"description": "Interactive process viewer", "category": "system"},
        "btop": {"description": "Resource monitor", "category": "system"},
        "neofetch": {"description": "System info tool", "category": "system"},
        "tree": {"description": "Directory listing", "category": "system"},
        "ripgrep": {"description": "Fast grep", "category": "system"},
        "fd": {"description": "Fast find", "category": "system"},
        # Media
        "vlc": {"description": "Media player", "category": "media"},
        "mpv": {"description": "Video player", "category": "media"},
        "spotify": {"description": "Music streaming", "category": "media"},
        "gimp": {"description": "Image editor", "category": "media"},
        "inkscape": {"description": "Vector graphics", "category": "media"},
    }

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the fast cache"""
        self.cache_dir = cache_dir or Path.home() / ".cache" / "luminous-nix"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_file = self.cache_dir / "fast_cache.pkl"
        self.stats_file = self.cache_dir / "cache_stats.json"

        # Load existing cache
        self.cache = self._load_cache()
        self.stats = self._load_stats()

    def _load_cache(self) -> dict:
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "rb") as f:
                    return pickle.load(f)
            except:
                pass

        # Initialize with common packages
        return {
            "packages": self.COMMON_PACKAGES.copy(),
            "searches": {},  # Cache search results
            "categories": self._build_categories(),
        }

    def _build_categories(self) -> dict[str, list[str]]:
        """Build category mappings"""
        categories = {}
        for name, info in self.COMMON_PACKAGES.items():
            cat = info.get("category", "other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)
        return categories

    def _save_cache(self):
        """Save cache to disk"""
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)

    def _load_stats(self) -> dict:
        """Load statistics"""
        if self.stats_file.exists():
            try:
                return json.loads(self.stats_file.read_text())
            except:
                pass
        return {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_searches": 0,
            "avg_cache_time_ms": 0,
            "avg_subprocess_time_ms": 0,
        }

    def _save_stats(self):
        """Save statistics"""
        self.stats_file.write_text(json.dumps(self.stats, indent=2))

    def search(self, query: str, limit: int = 30) -> tuple[list[dict], float, bool]:
        """
        Search for packages with caching.

        Returns: (results, elapsed_ms, from_cache)
        """
        start_time = time.time()
        self.stats["total_searches"] += 1

        # Check if we have this search cached
        cache_key = f"{query}:{limit}"
        if cache_key in self.cache.get("searches", {}):
            # Cache hit!
            self.stats["cache_hits"] += 1
            results = self.cache["searches"][cache_key]
            elapsed_ms = (time.time() - start_time) * 1000

            # Update average cache time
            avg = self.stats.get("avg_cache_time_ms", 0)
            self.stats["avg_cache_time_ms"] = (avg + elapsed_ms) / 2

            logger.debug(
                f"Cache hit for '{query}': {len(results)} results in {elapsed_ms:.1f}ms"
            )
            self._save_stats()

            return (results, elapsed_ms, True)

        # Not in cache, need to search
        self.stats["cache_misses"] += 1

        # First check our common packages
        results = []
        query_lower = query.lower()

        # Exact matches
        if query_lower in self.cache["packages"]:
            pkg = self.cache["packages"][query_lower]
            results.append(
                {
                    "name": query_lower,
                    "description": pkg.get("description", ""),
                    "source": "common",
                }
            )

        # Category matches
        if query_lower in self.cache.get("categories", {}):
            for pkg_name in self.cache["categories"][query_lower][:limit]:
                pkg = self.cache["packages"][pkg_name]
                results.append(
                    {
                        "name": pkg_name,
                        "description": pkg.get("description", ""),
                        "source": "category",
                    }
                )

        # Partial matches in common packages
        for name, info in self.cache["packages"].items():
            if (
                query_lower in name
                or query_lower in info.get("description", "").lower()
            ):
                if not any(r["name"] == name for r in results):
                    results.append(
                        {
                            "name": name,
                            "description": info.get("description", ""),
                            "source": "common",
                        }
                    )
                    if len(results) >= limit:
                        break

        # If we have enough results from cache, return them
        if len(results) >= 5:
            elapsed_ms = (time.time() - start_time) * 1000

            # Cache this search
            self.cache.setdefault("searches", {})[cache_key] = results
            self._save_cache()

            return (results, elapsed_ms, False)

        # Need to do actual search
        try:
            # Use subprocess as fallback
            result = subprocess.run(
                ["nix", "search", "nixpkgs", query, "--json"],
                capture_output=True,
                text=True,
                timeout=5,  # 5 second timeout
            )

            if result.returncode == 0 and result.stdout:
                packages = json.loads(result.stdout)

                # Add to results
                for full_name, info in list(packages.items())[:limit]:
                    name = full_name.split(".")[-1]

                    # Add to our package cache for future
                    self.cache["packages"][name] = {
                        "description": info.get("description", ""),
                        "version": info.get("version", ""),
                    }

                    results.append(
                        {
                            "name": name,
                            "description": info.get("description", ""),
                            "version": info.get("version", ""),
                            "source": "nix",
                        }
                    )

        except subprocess.TimeoutExpired:
            logger.warning(f"Search timed out for '{query}'")
        except Exception as e:
            logger.error(f"Search failed: {e}")

        elapsed_ms = (time.time() - start_time) * 1000

        # Update average subprocess time
        avg = self.stats.get("avg_subprocess_time_ms", 0)
        self.stats["avg_subprocess_time_ms"] = (avg + elapsed_ms) / 2

        # Cache this search result
        self.cache.setdefault("searches", {})[cache_key] = results
        self._save_cache()
        self._save_stats()

        return (results, elapsed_ms, False)

    def get_stats(self) -> dict:
        """Get cache statistics"""
        stats = self.stats.copy()
        stats["cached_packages"] = len(self.cache.get("packages", {}))
        stats["cached_searches"] = len(self.cache.get("searches", {}))
        stats["cache_size_kb"] = (
            self.cache_file.stat().st_size / 1024 if self.cache_file.exists() else 0
        )

        if stats["total_searches"] > 0:
            stats["hit_rate"] = stats["cache_hits"] / stats["total_searches"] * 100
        else:
            stats["hit_rate"] = 0

        return stats

    def warm_cache(self, common_queries: list[str] = None):
        """
        Warm the cache with common queries.
        Run this in background to improve performance.
        """
        queries = common_queries or [
            "browser",
            "editor",
            "terminal",
            "development",
            "python",
            "javascript",
            "rust",
            "git",
            "docker",
        ]

        for query in queries:
            logger.info(f"Warming cache for '{query}'...")
            self.search(query)

        logger.info(f"Cache warmed with {len(queries)} queries")


# Singleton instance
_fast_cache = None


def get_fast_cache() -> FastPackageCache:
    """Get or create the singleton cache"""
    global _fast_cache
    if _fast_cache is None:
        _fast_cache = FastPackageCache()
    return _fast_cache


def benchmark_fast_cache():
    """Benchmark the fast cache performance"""
    cache = get_fast_cache()

    print("\n🚀 Fast Cache Benchmark")
    print("=" * 50)

    queries = ["firefox", "vim", "editor", "development", "asdfghjkl"]

    for query in queries:
        print(f"\nQuery: '{query}'")

        # First search (might be slow)
        results1, time1, cached1 = cache.search(query)
        print(
            f"  First:  {time1:>6.1f}ms - {len(results1)} results (cached: {cached1})"
        )

        # Second search (should be cached)
        results2, time2, cached2 = cache.search(query)
        print(
            f"  Second: {time2:>6.1f}ms - {len(results2)} results (cached: {cached2})"
        )

        if time1 > 0:
            speedup = time1 / time2
            print(f"  Speedup: {speedup:.1f}x")

    # Show statistics
    stats = cache.get_stats()
    print("\n📊 Cache Statistics:")
    print(f"  Total searches: {stats['total_searches']}")
    print(f"  Cache hits:     {stats['cache_hits']}")
    print(f"  Cache misses:   {stats['cache_misses']}")
    print(f"  Hit rate:       {stats['hit_rate']:.1f}%")
    print(f"  Cached packages: {stats['cached_packages']}")
    print(f"  Cached searches: {stats['cached_searches']}")
    print(f"  Avg cache time:  {stats['avg_cache_time_ms']:.1f}ms")
    print(f"  Avg search time: {stats['avg_subprocess_time_ms']:.1f}ms")


if __name__ == "__main__":
    benchmark_fast_cache()
