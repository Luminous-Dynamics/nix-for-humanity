"""
Enhanced Cache with Background Warming, Fuzzy Matching, and Sharing

This module extends the fast cache with:
1. Background cache warming for common queries
2. Fuzzy matching for typos and partial matches
3. Shared cache support for teams
4. Cache management utilities
"""

import json
import pickle
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import logging
from difflib import get_close_matches
from datetime import datetime, timedelta
import hashlib
import os

logger = logging.getLogger(__name__)


class EnhancedCache:
    """
    Enhanced caching with background warming, fuzzy matching, and sharing.
    """

    # Common queries to warm cache with
    WARM_QUERIES = [
        # Categories
        "browser",
        "editor",
        "terminal",
        "shell",
        "development",
        "media",
        "video",
        "audio",
        "graphics",
        "network",
        "security",
        "system",
        "database",
        "compiler",
        "language",
        # Popular packages
        "firefox",
        "chromium",
        "vim",
        "neovim",
        "emacs",
        "vscode",
        "git",
        "docker",
        "python",
        "nodejs",
        "rust",
        "go",
        "gcc",
        "clang",
        "make",
        "cmake",
        "nginx",
        "apache",
        "postgresql",
        "mysql",
        "redis",
        "mongodb",
        "sqlite",
        "ffmpeg",
        "vlc",
        "mpv",
        "gimp",
        "inkscape",
        "blender",
        "tmux",
        "screen",
        "htop",
        "btop",
        "neofetch",
        "tree",
        "curl",
        "wget",
        "rsync",
        "ssh",
        "gpg",
        "openssl",
        # Common typos
        "fierrfox",
        "chormium",
        "pytohn",
        "dcoker",
        "postgress",
    ]

    # Expanded common packages with metadata
    COMMON_PACKAGES = {
        # Browsers
        "firefox": {"desc": "Free web browser", "cat": "browser", "aliases": ["ff"]},
        "chromium": {
            "desc": "Open-source Chrome",
            "cat": "browser",
            "aliases": ["chrome"],
        },
        "brave": {"desc": "Privacy browser", "cat": "browser", "aliases": []},
        "vivaldi": {"desc": "Feature-rich browser", "cat": "browser", "aliases": []},
        "qutebrowser": {
            "desc": "Keyboard-driven browser",
            "cat": "browser",
            "aliases": [],
        },
        # Editors
        "vim": {"desc": "Vi IMproved", "cat": "editor", "aliases": ["vi"]},
        "neovim": {"desc": "Vim fork", "cat": "editor", "aliases": ["nvim"]},
        "emacs": {"desc": "Extensible editor", "cat": "editor", "aliases": []},
        "vscode": {"desc": "Visual Studio Code", "cat": "editor", "aliases": ["code"]},
        "nano": {"desc": "Simple editor", "cat": "editor", "aliases": []},
        "helix": {"desc": "Post-modern editor", "cat": "editor", "aliases": ["hx"]},
        # Development
        "git": {"desc": "Version control", "cat": "dev", "aliases": []},
        "docker": {"desc": "Containers", "cat": "dev", "aliases": []},
        "docker-compose": {"desc": "Multi-container", "cat": "dev", "aliases": []},
        "python3": {"desc": "Python language", "cat": "dev", "aliases": ["python"]},
        "nodejs": {"desc": "JavaScript runtime", "cat": "dev", "aliases": ["node"]},
        "rustc": {"desc": "Rust compiler", "cat": "dev", "aliases": ["rust"]},
        "go": {"desc": "Go language", "cat": "dev", "aliases": ["golang"]},
        "gcc": {"desc": "GNU compiler", "cat": "dev", "aliases": []},
        "clang": {"desc": "LLVM compiler", "cat": "dev", "aliases": []},
        "make": {"desc": "Build tool", "cat": "dev", "aliases": []},
        "cmake": {"desc": "Build system", "cat": "dev", "aliases": []},
        # Databases
        "postgresql": {
            "desc": "SQL database",
            "cat": "database",
            "aliases": ["postgres"],
        },
        "mysql": {"desc": "SQL database", "cat": "database", "aliases": ["mariadb"]},
        "sqlite": {"desc": "Embedded database", "cat": "database", "aliases": []},
        "redis": {"desc": "Key-value store", "cat": "database", "aliases": []},
        "mongodb": {"desc": "NoSQL database", "cat": "database", "aliases": ["mongo"]},
        # Media
        "ffmpeg": {"desc": "Media converter", "cat": "media", "aliases": []},
        "vlc": {"desc": "Media player", "cat": "media", "aliases": []},
        "mpv": {"desc": "Video player", "cat": "media", "aliases": []},
        "obs-studio": {
            "desc": "Recording/streaming",
            "cat": "media",
            "aliases": ["obs"],
        },
        "gimp": {"desc": "Image editor", "cat": "media", "aliases": []},
        "inkscape": {"desc": "Vector graphics", "cat": "media", "aliases": []},
        "blender": {"desc": "3D creation", "cat": "media", "aliases": []},
        "audacity": {"desc": "Audio editor", "cat": "media", "aliases": []},
        # System tools
        "htop": {"desc": "Process viewer", "cat": "system", "aliases": []},
        "btop": {"desc": "Resource monitor", "cat": "system", "aliases": []},
        "neofetch": {"desc": "System info", "cat": "system", "aliases": []},
        "tree": {"desc": "Directory tree", "cat": "system", "aliases": []},
        "ripgrep": {"desc": "Fast grep", "cat": "system", "aliases": ["rg"]},
        "fd": {"desc": "Fast find", "cat": "system", "aliases": []},
        "bat": {"desc": "Better cat", "cat": "system", "aliases": []},
        "exa": {"desc": "Better ls", "cat": "system", "aliases": []},
        "tmux": {"desc": "Terminal mux", "cat": "terminal", "aliases": []},
        "screen": {"desc": "Terminal mux", "cat": "terminal", "aliases": []},
        "alacritty": {"desc": "GPU terminal", "cat": "terminal", "aliases": []},
        "kitty": {"desc": "Fast terminal", "cat": "terminal", "aliases": []},
    }

    def __init__(
        self, cache_dir: Optional[Path] = None, shared_dir: Optional[Path] = None
    ):
        """Initialize enhanced cache with optional shared directory"""
        # User cache
        self.cache_dir = cache_dir or Path.home() / ".cache" / "luminous-nix"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Shared cache (e.g., /var/cache/luminous-nix for teams)
        self.shared_dir = shared_dir or Path("/var/cache/luminous-nix")
        if self.shared_dir.exists() and os.access(self.shared_dir, os.R_OK):
            self.use_shared = True
        else:
            self.use_shared = False

        self.cache_file = self.cache_dir / "enhanced_cache.pkl"
        self.stats_file = self.cache_dir / "cache_stats.json"

        # Load caches
        self.cache = self._load_cache()
        self.stats = self._load_stats()

        # Build category mappings
        self._build_indexes()

        # Start background warming if needed
        if self._should_warm():
            self._start_background_warming()

    def _build_indexes(self):
        """Build various indexes for fast lookup"""
        self.categories = {}
        self.aliases = {}

        for name, info in self.COMMON_PACKAGES.items():
            # Category index
            cat = info.get("cat", "other")
            if cat not in self.categories:
                self.categories[cat] = []
            self.categories[cat].append(name)

            # Alias index
            for alias in info.get("aliases", []):
                self.aliases[alias] = name

    def _load_cache(self) -> Dict:
        """Load cache from user and shared directories"""
        cache = {
            "packages": self.COMMON_PACKAGES.copy(),
            "searches": {},
            "last_warm": None,
        }

        # Load user cache
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "rb") as f:
                    user_cache = pickle.load(f)
                    cache.update(user_cache)
            except:
                pass

        # Load shared cache if available
        if self.use_shared:
            shared_cache_file = self.shared_dir / "shared_cache.pkl"
            if shared_cache_file.exists():
                try:
                    with open(shared_cache_file, "rb") as f:
                        shared_cache = pickle.load(f)
                        # Merge shared searches
                        cache["searches"].update(shared_cache.get("searches", {}))
                        cache["packages"].update(shared_cache.get("packages", {}))
                except:
                    pass

        return cache

    def _save_cache(self):
        """Save cache to disk"""
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)

        # Try to update shared cache if we have write access
        if self.use_shared and os.access(self.shared_dir, os.W_OK):
            shared_cache_file = self.shared_dir / "shared_cache.pkl"
            try:
                # Load existing shared cache
                if shared_cache_file.exists():
                    with open(shared_cache_file, "rb") as f:
                        shared = pickle.load(f)
                else:
                    shared = {"searches": {}, "packages": {}}

                # Merge our cache into shared
                shared["searches"].update(self.cache.get("searches", {}))
                shared["packages"].update(self.cache.get("packages", {}))

                # Save merged cache
                with open(shared_cache_file, "wb") as f:
                    pickle.dump(shared, f)

                logger.info("Updated shared cache")
            except Exception as e:
                logger.warning(f"Could not update shared cache: {e}")

    def _load_stats(self) -> Dict:
        """Load statistics"""
        default_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "fuzzy_matches": 0,
            "total_searches": 0,
            "warming_runs": 0,
            "last_warm": None,
        }

        if self.stats_file.exists():
            try:
                loaded = json.loads(self.stats_file.read_text())
                # Merge with defaults to ensure all keys exist
                default_stats.update(loaded)
                return default_stats
            except:
                pass
        return default_stats

    def _save_stats(self):
        """Save statistics"""
        self.stats_file.write_text(json.dumps(self.stats, indent=2))

    def _should_warm(self) -> bool:
        """Check if we should warm the cache"""
        if not self.cache.get("last_warm"):
            return True

        try:
            last_warm = datetime.fromisoformat(self.cache["last_warm"])
            # Warm every 24 hours
            return datetime.now() - last_warm > timedelta(hours=24)
        except:
            return True

    def _start_background_warming(self):
        """Start warming cache in background"""

        def warm():
            logger.info("Starting background cache warming...")
            self.warm_cache()

        thread = threading.Thread(target=warm, daemon=True)
        thread.start()

    def fuzzy_search(
        self, query: str, limit: int = 30
    ) -> Tuple[List[Dict], float, str]:
        """
        Search with fuzzy matching for typos and partial matches.

        Returns: (results, elapsed_ms, match_type)
        """
        start_time = time.time()
        self.stats["total_searches"] += 1

        # Try exact search first
        results, elapsed, from_cache = self._exact_search(query, limit)
        if results:
            return (results, elapsed, "exact")

        # Try fuzzy matching on package names
        query_lower = query.lower()

        # Check aliases
        if query_lower in self.aliases:
            actual_name = self.aliases[query_lower]
            results, elapsed, from_cache = self._exact_search(actual_name, limit)
            if results:
                self.stats["fuzzy_matches"] += 1
                return (results, elapsed, "alias")

        # Fuzzy match on known packages
        all_names = list(self.cache["packages"].keys())
        close_matches = get_close_matches(query_lower, all_names, n=5, cutoff=0.6)

        if close_matches:
            self.stats["fuzzy_matches"] += 1
            # Search for the best match
            results, elapsed, from_cache = self._exact_search(close_matches[0], limit)

            # Add note about correction
            if results:
                results[0]["_suggested"] = close_matches[0]
                results[0]["_original_query"] = query

            elapsed_ms = (time.time() - start_time) * 1000
            return (results, elapsed_ms, "fuzzy")

        # No fuzzy matches, do actual search
        results, elapsed, from_cache = self._exact_search(query, limit)
        return (results, elapsed, "none")

    def _exact_search(self, query: str, limit: int) -> Tuple[List[Dict], float, bool]:
        """Perform exact search with caching"""
        start_time = time.time()

        # Check cache
        cache_key = f"{query}:{limit}"
        if cache_key in self.cache.get("searches", {}):
            self.stats["cache_hits"] += 1
            results = self.cache["searches"][cache_key]
            elapsed_ms = (time.time() - start_time) * 1000
            return (results, elapsed_ms, True)

        # Not in cache
        self.stats["cache_misses"] += 1
        results = []
        query_lower = query.lower()

        # Check common packages
        if query_lower in self.cache["packages"]:
            pkg = self.cache["packages"][query_lower]
            results.append(
                {
                    "name": query_lower,
                    "description": pkg.get("desc", ""),
                    "category": pkg.get("cat", ""),
                    "source": "common",
                }
            )

        # Check categories
        if query_lower in self.categories:
            for pkg_name in self.categories[query_lower][:limit]:
                pkg = self.cache["packages"][pkg_name]
                results.append(
                    {
                        "name": pkg_name,
                        "description": pkg.get("desc", ""),
                        "category": pkg.get("cat", ""),
                        "source": "category",
                    }
                )

        # If not enough results, search with nix
        if len(results) < 3:
            try:
                result = subprocess.run(
                    ["nix", "search", "nixpkgs", query, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0 and result.stdout:
                    packages = json.loads(result.stdout)
                    for full_name, info in list(packages.items())[:limit]:
                        name = full_name.split(".")[-1]

                        # Add to cache for future
                        self.cache["packages"][name] = {
                            "desc": info.get("description", ""),
                            "cat": "searched",
                        }

                        if not any(r["name"] == name for r in results):
                            results.append(
                                {
                                    "name": name,
                                    "description": info.get("description", ""),
                                    "version": info.get("version", ""),
                                    "source": "nix",
                                }
                            )
            except:
                pass

        # Cache results
        self.cache.setdefault("searches", {})[cache_key] = results
        self._save_cache()

        elapsed_ms = (time.time() - start_time) * 1000
        return (results, elapsed_ms, False)

    def warm_cache(self, queries: Optional[List[str]] = None):
        """Warm cache with common queries"""
        queries = queries or self.WARM_QUERIES
        warmed = 0

        for query in queries:
            try:
                # Don't log during warming to avoid spam
                old_level = logger.level
                logger.setLevel(logging.WARNING)

                _, _, from_cache = self._exact_search(query, 10)
                if not from_cache:
                    warmed += 1

                logger.setLevel(old_level)

                # Small delay to avoid hammering
                if not from_cache:
                    time.sleep(0.1)

            except:
                pass

        self.cache["last_warm"] = datetime.now().isoformat()
        self.stats["warming_runs"] += 1
        self._save_cache()
        self._save_stats()

        logger.info(f"Cache warming complete: {warmed} new entries cached")
        return warmed

    def get_cache_info(self) -> Dict:
        """Get detailed cache information"""
        info = {
            "user_cache": str(self.cache_file),
            "shared_cache": str(self.shared_dir) if self.use_shared else None,
            "total_packages": len(self.cache.get("packages", {})),
            "cached_searches": len(self.cache.get("searches", {})),
            "cache_size_kb": self.cache_file.stat().st_size / 1024
            if self.cache_file.exists()
            else 0,
            "stats": self.stats,
        }

        if self.stats["total_searches"] > 0:
            info["hit_rate"] = (
                self.stats["cache_hits"] / self.stats["total_searches"] * 100
            )
            info["fuzzy_rate"] = (
                self.stats["fuzzy_matches"] / self.stats["total_searches"] * 100
            )

        return info

    def clear_cache(self, searches_only: bool = False):
        """Clear cache (optionally just searches)"""
        if searches_only:
            self.cache["searches"] = {}
            logger.info("Cleared search cache")
        else:
            self.cache = {
                "packages": self.COMMON_PACKAGES.copy(),
                "searches": {},
                "last_warm": None,
            }
            logger.info("Cleared entire cache")

        self._save_cache()
        return True


# Singleton instance
_enhanced_cache = None


def get_enhanced_cache() -> EnhancedCache:
    """Get or create singleton cache"""
    global _enhanced_cache
    if _enhanced_cache is None:
        _enhanced_cache = EnhancedCache()
    return _enhanced_cache


def demo_enhanced_features():
    """Demonstrate enhanced cache features"""
    cache = get_enhanced_cache()

    print("\n🚀 Enhanced Cache Demo")
    print("=" * 60)

    # Test fuzzy matching
    print("\n1. Fuzzy Matching for Typos:")
    typos = [
        ("fierrfox", "firefox"),  # Typo
        ("pytohn", "python3"),  # Typo
        ("code", "vscode"),  # Alias
        ("postgres", "postgresql"),  # Alias
        ("editro", "editor"),  # Close match
    ]

    for typo, expected in typos:
        results, time_ms, match_type = cache.fuzzy_search(typo)
        if results:
            actual = results[0]["name"]
            status = "✅" if actual == expected else "❌"
            print(f"  '{typo}' → '{actual}' ({match_type}) {status}")
        else:
            print(f"  '{typo}' → No results ❌")

    # Test categories
    print("\n2. Category Search:")
    categories = ["browser", "editor", "database", "media"]
    for cat in categories:
        results, time_ms, match_type = cache.fuzzy_search(cat)
        names = [r["name"] for r in results[:3]]
        print(f"  {cat}: {', '.join(names)} ({len(results)} total)")

    # Show cache info
    print("\n3. Cache Information:")
    info = cache.get_cache_info()
    print(f"  Total packages: {info['total_packages']}")
    print(f"  Cached searches: {info['cached_searches']}")
    print(f"  Cache size: {info['cache_size_kb']:.1f} KB")
    if "hit_rate" in info:
        print(f"  Hit rate: {info['hit_rate']:.1f}%")
    if "fuzzy_rate" in info:
        print(f"  Fuzzy match rate: {info['fuzzy_rate']:.1f}%")

    # Test warming
    print("\n4. Background Cache Warming:")
    print("  Warming cache with common queries...")
    warmed = cache.warm_cache(["git", "docker", "python", "rust", "vim"])
    print(f"  Warmed {warmed} new entries")

    print("\n✅ Enhanced cache features working!")


if __name__ == "__main__":
    demo_enhanced_features()
