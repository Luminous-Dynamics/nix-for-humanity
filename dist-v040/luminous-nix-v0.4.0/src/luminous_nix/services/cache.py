"""
Cache Service - Clean, focused caching

Single responsibility: Cache and retrieve data efficiently.
No search logic, no display logic, just caching.
"""

from typing import Any, Dict, Optional, Tuple
from pathlib import Path
import pickle
import json
import time
import hashlib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Clean cache service with single responsibility.

    This service ONLY handles caching. It doesn't:
    - Search for packages (that's SearchService's job)
    - Execute commands (that's NixExecutor's job)
    - Format output (that's the UI's job)
    """

    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: int = 24):
        """
        Initialize cache service.

        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = cache_dir or Path.home() / ".cache" / "luminous-nix"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ttl = timedelta(hours=ttl_hours)
        self.cache_file = self.cache_dir / "cache.pkl"
        self.stats_file = self.cache_dir / "stats.json"

        self.cache = self._load_cache()
        self.stats = self._load_stats()

    def get(self, key: str) -> Tuple[Optional[Any], bool]:
        """
        Get item from cache.

        Args:
            key: Cache key

        Returns:
            Tuple of (value, from_cache)
            Value is None if not in cache or expired
        """
        if key not in self.cache:
            self.stats["misses"] += 1
            self._save_stats()
            return None, False

        entry = self.cache[key]

        # Check if expired
        if self._is_expired(entry):
            del self.cache[key]
            self.stats["misses"] += 1
            self._save_stats()
            return None, False

        self.stats["hits"] += 1
        self._save_stats()
        return entry["value"], True

    def set(self, key: str, value: Any) -> None:
        """
        Set item in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "hits": 0,
        }
        self._save_cache()

    def invalidate(self, key: str) -> bool:
        """
        Remove item from cache.

        Args:
            key: Cache key

        Returns:
            True if item was in cache
        """
        if key in self.cache:
            del self.cache[key]
            self._save_cache()
            return True
        return False

    def clear(self) -> int:
        """
        Clear entire cache.

        Returns:
            Number of items cleared
        """
        count = len(self.cache)
        self.cache = {}
        self._save_cache()
        self.stats["clears"] += 1
        self._save_stats()
        return count

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = self.stats.get("hits", 0) + self.stats.get("misses", 0)
        hit_rate = 0
        if total > 0:
            hit_rate = (self.stats.get("hits", 0) / total) * 100

        return {
            "total_items": len(self.cache),
            "hits": self.stats.get("hits", 0),
            "misses": self.stats.get("misses", 0),
            "hit_rate": hit_rate,
            "clears": self.stats.get("clears", 0),
            "cache_size_kb": self._get_cache_size(),
        }

    def warm(self, items: Dict[str, Any]) -> int:
        """
        Warm cache with multiple items.

        Args:
            items: Dictionary of key-value pairs

        Returns:
            Number of items added
        """
        count = 0
        for key, value in items.items():
            if key not in self.cache:
                self.set(key, value)
                count += 1
        return count

    def _is_expired(self, entry: Dict) -> bool:
        """Check if cache entry is expired"""
        try:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            return datetime.now() - timestamp > self.ttl
        except:
            return True

    def _load_cache(self) -> Dict:
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "rb") as f:
                    return pickle.load(f)
            except:
                logger.warning("Failed to load cache, starting fresh")
        return {}

    def _save_cache(self) -> None:
        """Save cache to disk"""
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _load_stats(self) -> Dict:
        """Load statistics from disk"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"hits": 0, "misses": 0, "clears": 0}

    def _save_stats(self) -> None:
        """Save statistics to disk"""
        try:
            with open(self.stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass

    def _get_cache_size(self) -> float:
        """Get cache file size in KB"""
        if self.cache_file.exists():
            return self.cache_file.stat().st_size / 1024
        return 0

    @staticmethod
    def make_key(*args) -> str:
        """
        Create cache key from arguments.

        Args:
            *args: Arguments to hash

        Returns:
            Cache key string
        """
        key_str = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()
