#!/usr/bin/env python3
"""
from typing import List, Dict, Optional, Tuple
Intelligent Caching System for Nix for Humanity
Implements multi-level caching with consciousness-aware eviction policies
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple, Callable, List
from dataclasses import dataclass, field
from functools import wraps
import pickle
from collections import OrderedDict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels with different characteristics"""
    L1_MEMORY = "l1_memory"  # Ultra-fast, small (10MB)
    L2_MEMORY = "l2_memory"  # Fast, medium (100MB)
    L3_DISK = "l3_disk"      # Slower, large (1GB)


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    size_bytes: int
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)
    ttl_seconds: Optional[float] = None
    priority: float = 1.0  # For consciousness-aware caching
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.created_at > self.ttl_seconds
    
    def update_access(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_accessed = time.time()
    
    @property
    def score(self) -> float:
        """Calculate cache score for eviction"""
        # Consciousness-aware scoring: frequency + recency + priority
        recency_score = 1.0 / (time.time() - self.last_accessed + 1)
        frequency_score = self.access_count / 100.0
        return (recency_score + frequency_score) * self.priority


class LRUCache:
    """LRU cache with size limit"""
    
    def __init__(self, max_size_mb: float):
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.current_size_bytes = 0
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.current_size_bytes -= entry.size_bytes
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.update_access()
            
            return entry.value
    
    async def put(self, key: str, value: Any, ttl_seconds: Optional[float] = None, priority: float = 1.0):
        """Put value in cache"""
        async with self.lock:
            # Calculate size
            try:
                serialized = pickle.dumps(value)
                size_bytes = len(serialized)
            except Exception:
                # If can't pickle, estimate size
                size_bytes = len(str(value))
            
            # Remove old entry if exists
            if key in self.cache:
                old_entry = self.cache[key]
                self.current_size_bytes -= old_entry.size_bytes
                del self.cache[key]
            
            # Evict entries if needed
            while self.current_size_bytes + size_bytes > self.max_size_bytes and len(self.cache) > 0:
                # Remove least recently used
                oldest_key, oldest_entry = self.cache.popitem(last=False)
                self.current_size_bytes -= oldest_entry.size_bytes
                logger.debug(f"Evicted {oldest_key} from cache")
            
            # Add new entry
            if self.current_size_bytes + size_bytes <= self.max_size_bytes:
                entry = CacheEntry(
                    key=key,
                    value=value,
                    size_bytes=size_bytes,
                    ttl_seconds=ttl_seconds,
                    priority=priority
                )
                self.cache[key] = entry
                self.current_size_bytes += size_bytes
                
    async def clear(self):
        """Clear cache"""
        async with self.lock:
            self.cache.clear()
            self.current_size_bytes = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "entries": len(self.cache),
            "size_mb": self.current_size_bytes / 1024 / 1024,
            "capacity_mb": self.max_size_bytes / 1024 / 1024,
            "utilization": self.current_size_bytes / self.max_size_bytes * 100
        }


class IntelligentCache:
    """Multi-level intelligent caching system"""
    
    def __init__(self):
        # Initialize cache levels
        self.l1_cache = LRUCache(max_size_mb=10)    # Ultra-fast
        self.l2_cache = LRUCache(max_size_mb=100)   # Fast
        # L3 disk cache would be implemented with file storage
        
        self.stats = {
            "hits": 0,
            "misses": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0
        }
        
        # Pattern recognition for predictive caching
        self.access_patterns: List[str] = []
        self.pattern_predictions: Dict[str, List[str]] = {}
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create deterministic key from args and kwargs
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Tuple[Optional[Any], CacheLevel]:
        """Get from cache, checking all levels"""
        # Check L1
        value = await self.l1_cache.get(key)
        if value is not None:
            self.stats["hits"] += 1
            self.stats["l1_hits"] += 1
            self._record_access(key)
            return value, CacheLevel.L1_MEMORY
        
        # Check L2
        value = await self.l2_cache.get(key)
        if value is not None:
            self.stats["hits"] += 1
            self.stats["l2_hits"] += 1
            # Promote to L1
            await self.l1_cache.put(key, value)
            self._record_access(key)
            return value, CacheLevel.L2_MEMORY
        
        # L3 disk cache would be checked here
        
        self.stats["misses"] += 1
        return None, None
    
    async def put(self, key: str, value: Any, ttl_seconds: Optional[float] = None, priority: float = 1.0):
        """Put in cache with intelligent placement"""
        # Determine cache level based on value characteristics
        size_estimate = len(str(value))
        
        if size_estimate < 1024 * 10:  # <10KB goes to L1
            await self.l1_cache.put(key, value, ttl_seconds, priority)
        elif size_estimate < 1024 * 100:  # <100KB goes to L2
            await self.l2_cache.put(key, value, ttl_seconds, priority)
        else:
            # Large items would go to L3 disk cache
            pass
        
        # Predict future accesses
        self._predict_next_accesses(key)
    
    def _record_access(self, key: str):
        """Record access pattern for prediction"""
        self.access_patterns.append(key)
        if len(self.access_patterns) > 1000:
            self.access_patterns.pop(0)
        
        # Simple pattern detection: if A is often followed by B, predict B when A is accessed
        if len(self.access_patterns) >= 2:
            prev_key = self.access_patterns[-2]
            if prev_key not in self.pattern_predictions:
                self.pattern_predictions[prev_key] = []
            if key not in self.pattern_predictions[prev_key]:
                self.pattern_predictions[prev_key].append(key)
    
    def _predict_next_accesses(self, key: str) -> List[str]:
        """Predict what will be accessed next"""
        return self.pattern_predictions.get(key, [])
    
    async def prefetch(self, key: str, fetch_func: Callable):
        """Prefetch predicted items"""
        predictions = self._predict_next_accesses(key)
        for predicted_key in predictions[:3]:  # Prefetch top 3 predictions
            if await self.l1_cache.get(predicted_key) is None:
                # Asynchronously fetch and cache
                asyncio.create_task(self._prefetch_item(predicted_key, fetch_func))
    
    async def _prefetch_item(self, key: str, fetch_func: Callable):
        """Prefetch single item"""
        try:
            value = await fetch_func(key)
            await self.put(key, value, priority=0.8)  # Lower priority for prefetched items
        except Exception:
            pass  # Ignore prefetch errors
    
    def cache_decorator(self, ttl_seconds: Optional[float] = None, priority: float = 1.0):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.cache_key(func.__name__, *args, **kwargs)
                
                # Check cache
                cached_value, level = await self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {func.__name__} at {level.value}")
                    return cached_value
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.put(cache_key, result, ttl_seconds, priority)
                
                # Prefetch related items
                await self.prefetch(cache_key, func)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, use asyncio
                loop = asyncio.get_event_loop()
                cache_key = self.cache_key(func.__name__, *args, **kwargs)
                
                # Check cache
                cached_value, level = loop.run_until_complete(self.get(cache_key))
                if cached_value is not None:
                    logger.debug(f"Cache hit for {func.__name__} at {level.value}")
                    return cached_value
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                loop.run_until_complete(self.put(cache_key, result, ttl_seconds, priority))
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hit_rate": f"{hit_rate:.1%}",
            "total_hits": self.stats["hits"],
            "total_misses": self.stats["misses"],
            "l1_stats": self.l1_cache.stats(),
            "l2_stats": self.l2_cache.stats(),
            "l1_hit_rate": f"{self.stats['l1_hits'] / total_requests * 100:.1f}%" if total_requests > 0 else "0%",
            "l2_hit_rate": f"{self.stats['l2_hits'] / total_requests * 100:.1f}%" if total_requests > 0 else "0%",
            "patterns_learned": len(self.pattern_predictions),
            "recommendation": self._get_cache_recommendation()
        }
    
    def _get_cache_recommendation(self) -> str:
        """Generate cache optimization recommendation"""
        hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) if self.stats["hits"] + self.stats["misses"] > 0 else 0
        
        if hit_rate < 0.5:
            return "Consider increasing cache size or TTL"
        elif hit_rate < 0.8:
            return "Cache performing well, monitor access patterns"
        else:
            return "Excellent cache performance"
    
    async def clear_all(self):
        """Clear all cache levels"""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0
        }


# Consciousness-aware cache policies
class ConsciousCachePolicy:
    """Cache policies that respect user awareness and flow"""
    
    @staticmethod
    def calculate_priority(operation: str, user_context: Dict[str, Any]) -> float:
        """Calculate cache priority based on consciousness principles"""
        priority = 1.0
        
        # Frequently accessed by user = higher priority
        if user_context.get("access_frequency", 0) > 10:
            priority *= 1.5
        
        # Part of user's current workflow = higher priority
        if user_context.get("in_active_workflow", False):
            priority *= 2.0
        
        # Educational content = higher priority (supports learning)
        if "help" in operation or "explain" in operation:
            priority *= 1.8
        
        # Error recovery = highest priority (reduces frustration)
        if "error" in operation or "fix" in operation:
            priority *= 3.0
        
        return min(priority, 5.0)  # Cap at 5x
    
    @staticmethod
    def should_cache(operation: str, result: Any, execution_time_ms: float) -> bool:
        """Determine if result should be cached"""
        # Don't cache very fast operations (<10ms)
        if execution_time_ms < 10:
            return False
        
        # Don't cache large results (>10MB)
        if len(str(result)) > 10 * 1024 * 1024:
            return False
        
        # Don't cache sensitive operations
        if any(sensitive in operation for sensitive in ["password", "key", "secret"]):
            return False
        
        # Cache everything else
        return True


# Example usage
if __name__ == "__main__":
    cache = IntelligentCache()
    
    # Example cached function
    @cache.cache_decorator(ttl_seconds=300, priority=2.0)
    async def expensive_nlp_operation(text: str) -> str:
        """Simulated expensive NLP operation"""
        await asyncio.sleep(0.5)  # Simulate processing
        return f"Processed: {text}"
    
    async def main():
        # First call - cache miss
        start = time.time()
        result1 = await expensive_nlp_operation("Hello world")
        print(f"First call: {(time.time() - start) * 1000:.0f}ms")
        
        # Second call - cache hit
        start = time.time()
        result2 = await expensive_nlp_operation("Hello world")
        print(f"Second call: {(time.time() - start) * 1000:.0f}ms")
        
        # Different input - cache miss
        start = time.time()
        result3 = await expensive_nlp_operation("Different text")
        print(f"Third call: {(time.time() - start) * 1000:.0f}ms")
        
        # Show cache statistics
        stats = cache.get_stats()
        print("\nCache Statistics:")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
    
    asyncio.run(main())