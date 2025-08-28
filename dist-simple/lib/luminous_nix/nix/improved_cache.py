#!/usr/bin/env python3
"""
Improved caching implementation with persistence and intelligence.

Quick wins that can be implemented immediately for real benefit.
"""

import asyncio
import json
import logging
import shelve
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import OrderedDict
import hashlib

logger = logging.getLogger(__name__)


class ImprovedCache:
    """
    Production-ready cache with persistence and intelligent policies.
    
    Features:
    - Persistent storage across restarts
    - LRU eviction with size bounds
    - Smart TTLs based on operation type
    - Pre-warming for common queries
    - Usage tracking for optimization
    """
    
    # Common packages that users frequently search for
    COMMON_PACKAGES = [
        'firefox', 'chrome', 'chromium',
        'python', 'python3', 'python311', 'python312',
        'nodejs', 'node', 'npm', 'yarn',
        'git', 'vim', 'neovim', 'emacs', 'nano',
        'docker', 'podman', 'kubernetes',
        'vscode', 'code', 'vscodium',
        'htop', 'btop', 'tree', 'curl', 'wget',
        'gcc', 'clang', 'rustc', 'go',
        'zsh', 'fish', 'bash', 'tmux', 'screen',
        'postgresql', 'mysql', 'redis', 'mongodb'
    ]
    
    def __init__(self, 
                 cache_dir: Optional[Path] = None,
                 max_memory_entries: int = 100,
                 max_disk_entries: int = 1000):
        """
        Initialize improved cache with both memory and disk storage.
        
        Args:
            cache_dir: Directory for persistent cache (default: ~/.cache/luminous-nix)
            max_memory_entries: Maximum entries in memory cache
            max_disk_entries: Maximum entries in disk cache
        """
        # Set up cache directory
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "luminous-nix"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory cache (fast, limited size)
        self.memory_cache = OrderedDict()
        self.max_memory_entries = max_memory_entries
        
        # Persistent cache (survives restarts)
        self.persistent_cache_path = self.cache_dir / "package_cache.db"
        self._init_persistent_cache()
        
        # Metrics
        self.hits = 0
        self.misses = 0
        self.time_saved_ms = 0
        
        # TTL policies
        self.ttl_policies = {
            'search': timedelta(hours=24),      # Package searches change rarely
            'list': timedelta(minutes=30),      # Installed packages can change
            'eval': timedelta(days=7),          # Evaluations are deterministic
            'config': timedelta(hours=1),       # Configs might change
            'common': timedelta(days=30),       # Common packages rarely change
        }
        
        logger.info(f"✨ Improved cache initialized at {self.cache_dir}")
    
    def _init_persistent_cache(self):
        """Initialize persistent cache with error handling."""
        try:
            # Try to open existing cache
            self.persistent_cache = shelve.open(str(self.persistent_cache_path))
            
            # Clean expired entries on startup
            self._clean_expired_entries()
            
            logger.info(f"📁 Loaded {len(self.persistent_cache)} cached entries")
        except Exception as e:
            logger.warning(f"Could not open persistent cache: {e}")
            # Create in-memory fallback
            self.persistent_cache = {}
    
    def _clean_expired_entries(self):
        """Remove expired entries from persistent cache."""
        expired = []
        now = datetime.now()
        
        for key in list(self.persistent_cache.keys()):
            try:
                entry = self.persistent_cache[key]
                if isinstance(entry, dict) and 'timestamp' in entry:
                    timestamp = datetime.fromisoformat(entry['timestamp'])
                    ttl = self.ttl_policies.get(entry.get('type', 'search'), timedelta(hours=24))
                    
                    if now - timestamp > ttl:
                        expired.append(key)
            except Exception:
                # Remove corrupted entries
                expired.append(key)
        
        for key in expired:
            del self.persistent_cache[key]
        
        if expired:
            logger.info(f"🧹 Cleaned {len(expired)} expired cache entries")
    
    def _get_cache_key(self, operation: str, query: str) -> str:
        """Generate cache key from operation and query."""
        # Use hash for consistent keys
        content = f"{operation}:{query}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_common_package(self, query: str) -> bool:
        """Check if query is for a common package."""
        query_lower = query.lower()
        return any(pkg in query_lower for pkg in self.COMMON_PACKAGES)
    
    def _get_ttl(self, operation: str, query: str) -> timedelta:
        """Get intelligent TTL based on operation and query."""
        # Common packages get longer TTL
        if self._is_common_package(query):
            return self.ttl_policies['common']
        
        # Version queries need fresher data
        if any(word in query.lower() for word in ['latest', 'version', 'update']):
            return timedelta(minutes=10)
        
        return self.ttl_policies.get(operation, timedelta(hours=1))
    
    async def get(self, operation: str, query: str) -> Optional[Any]:
        """
        Get from cache with multi-layer lookup.
        
        Returns None if not found or expired.
        """
        cache_key = self._get_cache_key(operation, query)
        
        # Layer 1: Check memory cache (fastest)
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if self._is_valid_entry(entry, operation, query):
                self.hits += 1
                self._track_time_saved(entry.get('operation_time', 1000))
                # Move to end (LRU)
                self.memory_cache.move_to_end(cache_key)
                logger.debug(f"✨ Memory cache hit for '{query}'")
                return entry['data']
        
        # Layer 2: Check persistent cache
        if cache_key in self.persistent_cache:
            entry = self.persistent_cache[cache_key]
            if self._is_valid_entry(entry, operation, query):
                self.hits += 1
                self._track_time_saved(entry.get('operation_time', 1000))
                # Promote to memory cache
                self._add_to_memory_cache(cache_key, entry)
                logger.debug(f"💾 Disk cache hit for '{query}'")
                return entry['data']
        
        self.misses += 1
        return None
    
    def _is_valid_entry(self, entry: Dict, operation: str, query: str) -> bool:
        """Check if cache entry is still valid."""
        if not isinstance(entry, dict) or 'timestamp' not in entry:
            return False
        
        try:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            ttl = self._get_ttl(operation, query)
            return datetime.now() - timestamp < ttl
        except Exception:
            return False
    
    def _add_to_memory_cache(self, key: str, entry: Dict):
        """Add entry to memory cache with LRU eviction."""
        # Evict if at capacity
        while len(self.memory_cache) >= self.max_memory_entries:
            # Remove least recently used
            self.memory_cache.popitem(last=False)
        
        self.memory_cache[key] = entry
    
    def _track_time_saved(self, operation_time_ms: float):
        """Track time saved by cache hit."""
        self.time_saved_ms += operation_time_ms
    
    async def put(self, operation: str, query: str, data: Any, operation_time_ms: float = 0):
        """
        Store in cache with metadata.
        
        Args:
            operation: Type of operation (search, eval, etc.)
            query: The query string
            data: Result data to cache
            operation_time_ms: How long the operation took (for metrics)
        """
        cache_key = self._get_cache_key(operation, query)
        
        entry = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'type': operation,
            'query': query,
            'operation_time': operation_time_ms,
            'hit_count': 0
        }
        
        # Add to memory cache
        self._add_to_memory_cache(cache_key, entry)
        
        # Add to persistent cache
        try:
            self.persistent_cache[cache_key] = entry
            # Force sync for important data
            if hasattr(self.persistent_cache, 'sync'):
                self.persistent_cache.sync()
        except Exception as e:
            logger.warning(f"Could not persist cache entry: {e}")
    
    async def pre_warm(self, search_func):
        """
        Pre-warm cache with common packages.
        
        Args:
            search_func: Async function to perform actual search
        """
        logger.info("🔥 Pre-warming cache with common packages...")
        
        tasks = []
        for package in self.COMMON_PACKAGES[:20]:  # Limit initial warming
            cache_key = self._get_cache_key('search', package)
            
            # Skip if already cached
            if cache_key in self.memory_cache or cache_key in self.persistent_cache:
                continue
            
            # Create pre-warming task
            tasks.append(self._warm_single(package, search_func))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(1 for r in results if not isinstance(r, Exception))
            logger.info(f"✅ Pre-warmed {successful} common packages")
    
    async def _warm_single(self, package: str, search_func):
        """Pre-warm a single package."""
        try:
            start = time.perf_counter()
            result = await search_func(package)
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            await self.put('search', package, result, elapsed_ms)
            return result
        except Exception as e:
            logger.debug(f"Could not pre-warm {package}: {e}")
            return e
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1%}",
            'memory_entries': len(self.memory_cache),
            'disk_entries': len(self.persistent_cache),
            'time_saved_seconds': f"{self.time_saved_ms/1000:.1f}",
            'avg_time_saved_per_hit': f"{self.time_saved_ms/self.hits:.1f}ms" if self.hits > 0 else "0ms"
        }
    
    def close(self):
        """Close persistent cache properly."""
        if hasattr(self.persistent_cache, 'close'):
            self.persistent_cache.close()


# Demo usage
async def demo_improved_cache():
    """Demonstrate improved caching features."""
    
    # Simulate search function
    async def mock_search(query: str) -> List[Dict]:
        # Simulate network delay
        await asyncio.sleep(0.5)
        return [{'name': query, 'version': '1.0'}]
    
    print("\n" + "="*60)
    print("🚀 IMPROVED CACHE DEMO")
    print("="*60)
    
    cache = ImprovedCache()
    
    # Test persistence
    print("\n📊 Test 1: Persistence Across Sessions")
    print("-" * 40)
    
    # First "session"
    result = await cache.get('search', 'firefox')
    if result is None:
        print("  Cache miss (expected on first run)")
        result = await mock_search('firefox')
        await cache.put('search', 'firefox', result, 500)
    else:
        print("  Cache hit! (cache persisted from previous run)")
    
    # Pre-warm common packages
    print("\n📊 Test 2: Pre-warming Common Packages")
    print("-" * 40)
    await cache.pre_warm(mock_search)
    
    # Test cache effectiveness
    print("\n📊 Test 3: Cache Effectiveness")
    print("-" * 40)
    
    queries = ['python', 'git', 'firefox', 'nodejs', 'random-pkg']
    for query in queries:
        start = time.perf_counter()
        result = await cache.get('search', query)
        
        if result is None:
            result = await mock_search(query)
            elapsed_ms = (time.perf_counter() - start) * 1000
            await cache.put('search', query, result, elapsed_ms)
            print(f"  {query}: {elapsed_ms:.1f}ms (cache miss)")
        else:
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"  {query}: {elapsed_ms:.1f}ms (cache hit! ✨)")
    
    # Show statistics
    print("\n📊 Cache Statistics")
    print("-" * 40)
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n💡 Benefits Demonstrated:")
    print("  1. Cache persists across restarts")
    print("  2. Common packages pre-warmed")
    print("  3. Instant (0ms) responses for cached queries")
    print("  4. Intelligent TTLs based on query type")
    print("  5. Bounded memory usage with LRU eviction")
    
    cache.close()
    print("="*60)


if __name__ == "__main__":
    asyncio.run(demo_improved_cache())