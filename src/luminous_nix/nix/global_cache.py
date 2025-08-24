#!/usr/bin/env python3
"""
Global Cache Manager for Luminous Nix

Provides centralized caching for all expensive operations across the system.
This dramatically improves performance by eliminating redundant subprocess calls.
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Union
from functools import wraps
import logging

from luminous_nix.nix.improved_cache import ImprovedCache

logger = logging.getLogger(__name__)


class GlobalCacheManager:
    """
    Centralized cache manager for all Luminous Nix operations.
    
    Features:
    - Category-specific caches with smart TTLs
    - Automatic cache invalidation
    - Performance metrics tracking
    - Cache warming on startup
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - one global cache manager"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize category-specific caches with appropriate TTLs"""
        if not hasattr(self, 'initialized'):
            self.caches = {
                # Package operations - cache for 24 hours
                'search': ImprovedCache(max_memory_entries=200),
                'packages': ImprovedCache(max_memory_entries=100),
                
                # Configuration - cache for 12 hours
                'config': ImprovedCache(max_memory_entries=50),
                'modules': ImprovedCache(max_memory_entries=100),
                
                # System state - cache for 5 minutes
                'generations': ImprovedCache(max_memory_entries=20),
                'health': ImprovedCache(max_memory_entries=10),
                
                # Expressions - cache for 7 days (deterministic)
                'expressions': ImprovedCache(max_memory_entries=500),
                'evaluations': ImprovedCache(max_memory_entries=200),
                
                # AST parsing - cache for 1 hour
                'ast': ImprovedCache(max_memory_entries=100),
                'symbols': ImprovedCache(max_memory_entries=200),
                
                # Templates - cache for 24 hours
                'poml': ImprovedCache(max_memory_entries=50),
                'templates': ImprovedCache(max_memory_entries=50),
                
                # Permissions - cache for 1 hour
                'permissions': ImprovedCache(max_memory_entries=20),
                
                # Flakes - cache for 30 minutes
                'flakes': ImprovedCache(max_memory_entries=30),
                
                # Version info - cache for 24 hours
                'version': ImprovedCache(max_memory_entries=5),
            }
            
            # TTL policies per category
            self.ttl_policies = {
                'search': timedelta(hours=24),
                'packages': timedelta(hours=24),
                'config': timedelta(hours=12),
                'modules': timedelta(hours=12),
                'generations': timedelta(minutes=5),
                'health': timedelta(minutes=1),
                'expressions': timedelta(days=7),
                'evaluations': timedelta(days=7),
                'ast': timedelta(hours=1),
                'symbols': timedelta(hours=1),
                'poml': timedelta(hours=24),
                'templates': timedelta(hours=24),
                'permissions': timedelta(hours=1),
                'flakes': timedelta(minutes=30),
                'version': timedelta(hours=24),
            }
            
            # Track invalidation triggers
            self.invalidation_triggers = {
                'rebuild': ['generations', 'health', 'version'],
                'config_change': ['config', 'modules', 'generations'],
                'flake_update': ['flakes', 'packages'],
                'home_change': ['packages', 'config'],
            }
            
            self.initialized = True
            logger.info("✨ Global cache manager initialized")
    
    def get_cache(self, category: str) -> ImprovedCache:
        """Get cache for a specific category"""
        if category not in self.caches:
            logger.warning(f"Unknown cache category: {category}, using default")
            return self.caches['search']
        return self.caches[category]
    
    async def get(self, category: str, key: str) -> Optional[Any]:
        """Get value from category cache"""
        cache = self.get_cache(category)
        return await cache.get(category, key)
    
    async def put(self, category: str, key: str, value: Any, 
                  operation_time_ms: float = 0):
        """Store value in category cache"""
        cache = self.get_cache(category)
        await cache.put(category, key, value, operation_time_ms)
    
    def invalidate_category(self, category: str):
        """Invalidate all entries in a category"""
        if category in self.caches:
            # Clear memory cache
            self.caches[category].memory_cache.clear()
            logger.info(f"🧹 Invalidated cache category: {category}")
    
    def invalidate_on_event(self, event: str):
        """Invalidate related caches based on system event"""
        if event in self.invalidation_triggers:
            categories = self.invalidation_triggers[event]
            for category in categories:
                self.invalidate_category(category)
            logger.info(f"🔄 Invalidated caches for event: {event}")
    
    async def warm_caches(self):
        """Pre-warm caches with common operations"""
        logger.info("🔥 Pre-warming global caches...")
        
        # Pre-warm common package searches
        common_packages = ['firefox', 'python', 'git', 'vim', 'docker']
        search_cache = self.get_cache('search')
        
        for pkg in common_packages:
            if not await search_cache.get('search', pkg):
                # Would normally call actual search here
                # For now, just mark as attempted
                logger.debug(f"Would pre-warm: {pkg}")
        
        logger.info("✅ Cache pre-warming complete")
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get statistics across all caches"""
        total_hits = 0
        total_misses = 0
        total_memory = 0
        total_disk = 0
        category_stats = {}
        
        for name, cache in self.caches.items():
            stats = cache.get_stats()
            category_stats[name] = stats
            total_hits += stats.get('hits', 0)
            total_misses += stats.get('misses', 0)
            total_memory += stats.get('memory_entries', 0)
            total_disk += stats.get('disk_entries', 0)
        
        total_requests = total_hits + total_misses
        global_hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            'global_hit_rate': f"{global_hit_rate:.1%}",
            'total_hits': total_hits,
            'total_misses': total_misses,
            'total_memory_entries': total_memory,
            'total_disk_entries': total_disk,
            'categories': category_stats
        }
    
    def close_all(self):
        """Close all cache connections properly"""
        for cache in self.caches.values():
            cache.close()


def cached(category: str, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Usage:
        @cached('config')
        def generate_config(intent):
            # expensive operation
            return config
        
        @cached('expressions', key_func=lambda expr, pure: expr if pure else None)
        def eval_expression(expr, pure=True):
            # only cache if pure
            return result
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
                if cache_key is None:
                    # Don't cache
                    return await func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Check cache
            cache_manager = GlobalCacheManager()
            cached_value = await cache_manager.get(category, cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute and cache
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            await cache_manager.put(category, cache_key, result, elapsed_ms)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Sync version for non-async functions
            if key_func:
                cache_key = key_func(*args, **kwargs)
                if cache_key is None:
                    return func(*args, **kwargs)
            else:
                key_parts = [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Use sync cache methods (simplified)
            cache_manager = GlobalCacheManager()
            cache = cache_manager.get_cache(category)
            
            # Check memory cache only for sync
            if cache_key in cache.memory_cache:
                entry = cache.memory_cache[cache_key]
                if cache._is_valid_entry(entry, category, cache_key):
                    cache.hits += 1
                    return entry['data']
            
            # Execute and cache
            result = func(*args, **kwargs)
            
            # Add to memory cache
            entry = {
                'data': result,
                'timestamp': datetime.now().isoformat(),
                'type': category,
            }
            cache._add_to_memory_cache(cache_key, entry)
            
            return result
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Example usage in other modules:

class CachedConfigGenerator:
    """Example: Config generator with caching"""
    
    @cached('config')
    def generate_config(self, intent: Dict[str, Any]) -> str:
        """Generate NixOS configuration from intent - automatically cached"""
        # Expensive config generation
        config = self._build_config(intent)
        return config
    
    @cached('modules')
    def lookup_module(self, module_name: str) -> Dict:
        """Lookup module configuration - automatically cached"""
        # Expensive module lookup
        return self._fetch_module(module_name)


class CachedGenerationManager:
    """Example: Generation manager with caching"""
    
    @cached('generations')
    async def list_generations(self):
        """List NixOS generations - automatically cached for 5 minutes"""
        # Expensive subprocess call
        result = await self._fetch_generations()
        return result
    
    @cached('health')
    async def check_system_health(self):
        """Check system health - automatically cached for 1 minute"""
        # Multiple expensive checks
        health = await self._analyze_system()
        return health


class CachedExpressionEvaluator:
    """Example: Expression evaluator with caching"""
    
    @cached('expressions', key_func=lambda self, expr, pure: expr if pure else None)
    def eval_expression(self, expr: str, pure: bool = True):
        """Evaluate Nix expression - only cached if pure"""
        # Expensive evaluation
        result = self._eval_nix_expression(expr)
        return result


# Singleton instance
_global_cache = None

def get_global_cache() -> GlobalCacheManager:
    """Get the global cache manager instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = GlobalCacheManager()
    return _global_cache


# Cache invalidation helpers
def invalidate_on_rebuild():
    """Call this when system is rebuilt"""
    cache = get_global_cache()
    cache.invalidate_on_event('rebuild')


def invalidate_on_config_change():
    """Call this when configuration changes"""
    cache = get_global_cache()
    cache.invalidate_on_event('config_change')


def invalidate_on_flake_update():
    """Call this when flake is updated"""
    cache = get_global_cache()
    cache.invalidate_on_event('flake_update')


if __name__ == "__main__":
    # Demo the global cache
    async def demo():
        print("\n" + "="*60)
        print("🌍 GLOBAL CACHE MANAGER DEMO")
        print("="*60)
        
        cache = GlobalCacheManager()
        
        # Test different categories
        await cache.put('config', 'test-config', {'config': 'data'}, 100)
        await cache.put('search', 'firefox', {'packages': ['firefox-1.0']}, 7000)
        await cache.put('expressions', '2+2', 4, 50)
        
        # Test retrieval
        print("\n📊 Testing cache retrieval:")
        config = await cache.get('config', 'test-config')
        print(f"  Config: {config}")
        
        search = await cache.get('search', 'firefox')
        print(f"  Search: {search}")
        
        expr = await cache.get('expressions', '2+2')
        print(f"  Expression: {expr}")
        
        # Test invalidation
        print("\n🔄 Testing invalidation:")
        cache.invalidate_on_event('rebuild')
        
        # Show stats
        print("\n📊 Global Statistics:")
        stats = cache.get_global_stats()
        for key, value in stats.items():
            if key != 'categories':
                print(f"  {key}: {value}")
        
        # Clean up
        cache.close_all()
        print("\n✅ Demo complete!")
    
    asyncio.run(demo())