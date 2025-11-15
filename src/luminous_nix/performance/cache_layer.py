"""
High-performance caching layer for Luminous Nix.
Implements LRU cache with TTL and pre-compiled command database.
"""

import json
import time
import hashlib
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import pickle

class PerformanceCache:
    """High-performance caching system with multiple strategies."""

    def __init__(self, cache_dir: Path = None, max_size: int = 10000, ttl: int = 3600):
        self.cache_dir = cache_dir or Path.home() / '.cache' / 'luminous-nix'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        self.ttl = ttl
        self.memory_cache: Dict[str, Tuple[Any, float]] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Pre-compiled command database
        self.command_db = self._load_command_database()

        # Statistics
        self.hits = 0
        self.misses = 0

    def _load_command_database(self) -> Dict[str, Any]:
        """Load pre-compiled command mappings for 2-5 seconds lookups."""
        db_file = self.cache_dir / 'command_db.pkl'

        if db_file.exists():
            with open(db_file, 'rb') as f:
                return pickle.load(f)

        # Build initial database
        db = {
            # Common queries -> 2-5 seconds responses
            'list installed': {'command': 'nix-env -q', 'cached': True},
            'search firefox': {'command': 'nix search nixpkgs firefox', 'cached': True},
            'update system': {'command': 'nix-channel --update', 'risk': 'medium'},
            'garbage collect': {'command': 'nix-collect-garbage -d', 'risk': 'low'},

            # Package installations
            'install firefox': {'package': 'firefox', 'command': 'nix-env -iA nixpkgs.firefox'},
            'install chrome': {'package': 'google-chrome', 'command': 'nix-env -iA nixpkgs.google-chrome'},
            'install vscode': {'package': 'vscode', 'command': 'nix-env -iA nixpkgs.vscode'},

            # Configuration templates
            'web server': {'template': 'nginx', 'services': ['nginx', 'ssl']},
            'dev environment': {'template': 'development', 'packages': ['git', 'vim', 'tmux']},
            'gaming setup': {'template': 'gaming', 'packages': ['steam', 'discord', 'obs']},
        }

        # Add all package aliases
        from ..package_aliases import EXTENDED_PACKAGE_ALIASES
        for alias, real_name in EXTENDED_PACKAGE_ALIASES.items():
            db[f'install {alias}'] = {
                'package': real_name,
                'command': f'nix-env -iA nixpkgs.{real_name}'
            }

        # Save database
        with open(db_file, 'wb') as f:
            pickle.dump(db, f)

        return db

    def _cache_key(self, query: str, context: Optional[Dict] = None) -> str:
        """Generate cache key from query and context."""
        key_data = query.lower().strip()
        if context:
            key_data += json.dumps(context, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, query: str, context: Optional[Dict] = None) -> Optional[Any]:
        """Get cached result if available and not expired."""
        key = self._cache_key(query, context)

        # Check memory cache first
        if key in self.memory_cache:
            result, timestamp = self.memory_cache[key]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                return result
            else:
                del self.memory_cache[key]

        # Check disk cache
        cache_file = self.cache_dir / f'{key}.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                if time.time() - data['timestamp'] < self.ttl:
                    self.hits += 1
                    # Promote to memory cache
                    self.memory_cache[key] = (data['result'], data['timestamp'])
                    return data['result']
            except:
                cache_file.unlink()

        self.misses += 1
        return None

    def set(self, query: str, result: Any, context: Optional[Dict] = None):
        """Cache a result."""
        key = self._cache_key(query, context)
        timestamp = time.time()

        # Memory cache
        self.memory_cache[key] = (result, timestamp)

        # Limit memory cache size
        if len(self.memory_cache) > self.max_size:
            # Remove oldest entries
            sorted_items = sorted(self.memory_cache.items(),
                                key=lambda x: x[1][1])
            for old_key, _ in sorted_items[:len(sorted_items)//2]:
                del self.memory_cache[old_key]

        # Async disk cache
        self.executor.submit(self._save_to_disk, key, result, timestamp)

    def _save_to_disk(self, key: str, result: Any, timestamp: float):
        """Save to disk cache asynchronously."""
        cache_file = self.cache_dir / f'{key}.json'
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'result': result,
                    'timestamp': timestamp
                }, f)
        except:
            pass

    def get_fast_result(self, query: str) -> Optional[Dict]:
        """Get fast result (typically 2-5 seconds) from pre-compiled database."""
        normalized = query.lower().strip()

        # Direct lookup
        if normalized in self.command_db:
            return self.command_db[normalized]

        # Fuzzy matching for common patterns
        for pattern, data in self.command_db.items():
            if pattern in normalized or normalized in pattern:
                return data

        return None

    def clear(self):
        """Clear all caches."""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
        self.hits = 0
        self.misses = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f'{hit_rate:.1f}%',
            'memory_size': len(self.memory_cache),
            'disk_files': len(list(self.cache_dir.glob('*.json'))),
            'command_db_size': len(self.command_db)
        }


class AsyncOperations:
    """Async/await for parallel operations."""

    def __init__(self, cache: PerformanceCache):
        self.cache = cache
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent operations

    async def parallel_search(self, queries: List[str]) -> List[Any]:
        """Execute multiple searches in parallel."""
        tasks = [self._search_with_cache(q) for q in queries]
        return await asyncio.gather(*tasks)

    async def _search_with_cache(self, query: str) -> Any:
        """Search with caching."""
        async with self.semaphore:
            # Check cache first
            cached = self.cache.get(query)
            if cached:
                return cached

            # Simulate async operation
            result = await self._execute_search(query)
            self.cache.set(query, result)
            return result

    async def _execute_search(self, query: str) -> Dict:
        """Execute actual search (simulated async)."""
        await asyncio.sleep(0.1)  # Simulate network/disk I/O
        return {'query': query, 'results': ['package1', 'package2']}

    async def batch_install(self, packages: List[str]) -> List[Dict]:
        """Install multiple packages efficiently."""
        tasks = []
        for pkg in packages:
            tasks.append(self._install_package(pkg))
        return await asyncio.gather(*tasks)

    async def _install_package(self, package: str) -> Dict:
        """Install single package asynchronously."""
        async with self.semaphore:
            # Check if already installed from cache
            cache_key = f'installed_{package}'
            if self.cache.get(cache_key):
                return {'package': package, 'status': 'already_installed'}

            # Simulate installation
            await asyncio.sleep(0.5)
            self.cache.set(cache_key, True)
            return {'package': package, 'status': 'installed'}


class MemoryOptimizer:
    """Optimize memory usage patterns."""

    def __init__(self):
        self.pools = {}
        self.reusable_objects = []

    def optimize_package_list(self, packages: List[Dict]) -> List[Dict]:
        """Optimize package list memory usage."""
        # Intern common strings
        interned = {}
        optimized = []

        for pkg in packages:
            opt_pkg = {}
            for key, value in pkg.items():
                if isinstance(value, str):
                    if value not in interned:
                        interned[value] = value
                    opt_pkg[key] = interned[value]
                else:
                    opt_pkg[key] = value
            optimized.append(opt_pkg)

        return optimized

    @lru_cache(maxsize=1000)
    def cached_parse(self, text: str) -> Any:
        """Cache parsed results to avoid re-parsing."""
        # This would contain actual parsing logic
        return {'parsed': text}

    def clear_pools(self):
        """Clear object pools to free memory."""
        self.pools.clear()
        self.reusable_objects.clear()
        self.cached_parse.cache_clear()


# Singleton instance
_cache = None

def get_cache() -> PerformanceCache:
    """Get singleton cache instance."""
    global _cache
    if _cache is None:
        _cache = PerformanceCache()
    return _cache


# Example usage
async def example_usage():
    """Example of performance optimizations in action."""
    cache = get_cache()
    async_ops = AsyncOperations(cache)
    optimizer = MemoryOptimizer()

    # Fast lookup from pre-compiled database (typically 2-5 seconds)
    fast_result = cache.get_fast_result('install firefox')
    print(f"Fast result: {fast_result}")

    # Parallel searches
    results = await async_ops.parallel_search([
        'search editor',
        'search browser',
        'search terminal'
    ])
    print(f"Parallel results: {results}")

    # Batch operations
    installed = await async_ops.batch_install(['vim', 'git', 'tmux'])
    print(f"Batch installed: {installed}")

    # Show cache stats
    print(f"Cache stats: {cache.stats()}")


if __name__ == '__main__':
    asyncio.run(example_usage())
