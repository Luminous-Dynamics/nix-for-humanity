#!/usr/bin/env python3
"""
⚡ Performance Optimizations for AI-Driven Interface Generation
Async operations, caching strategies, and performance improvements
"""

import asyncio
import time
import json
import pickle
from typing import Dict, List, Any, Optional, Callable, TypeVar, Coroutine
from functools import wraps, lru_cache
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

from error_handler import safe_async_operation, get_logger


T = TypeVar('T')


@dataclass
class CacheEntry:
    """Represents a cache entry with TTL"""
    
    key: str
    value: Any
    timestamp: datetime
    ttl: timedelta
    hits: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() - self.timestamp > self.ttl
    
    def hit(self):
        """Record a cache hit"""
        self.hits += 1


class AsyncCache:
    """Async-aware cache with TTL and size limits"""
    
    def __init__(self, max_size: int = 1000, default_ttl: timedelta = timedelta(minutes=15)):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = asyncio.Lock()
        self.logger = get_logger(__name__)
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_expired():
                    # Remove expired entry
                    del self.cache[key]
                    self.misses += 1
                    return None
                
                # Record hit
                entry.hit()
                self.hits += 1
                
                # Move to end for LRU
                self.cache[key] = self.cache.pop(key)
                
                return entry.value
            
            self.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        """Set value in cache"""
        async with self.lock:
            # Check size limit
            if len(self.cache) >= self.max_size and key not in self.cache:
                # Evict least recently used
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.evictions += 1
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                ttl=ttl or self.default_ttl
            )
            
            self.cache[key] = entry
    
    async def clear_expired(self):
        """Remove expired entries"""
        async with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


def async_cached(ttl: timedelta = timedelta(minutes=5)):
    """Decorator for async function caching"""
    
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        cache = AsyncCache(default_ttl=ttl)
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Create cache key from function name and arguments
            key = f"{func.__name__}_{args}_{kwargs}"
            key_hash = hashlib.md5(key.encode()).hexdigest()
            
            # Check cache
            result = await cache.get(key_hash)
            if result is not None:
                return result
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(key_hash, result)
            
            return result
        
        # Attach cache for inspection
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


class BatchProcessor:
    """Process items in batches for efficiency"""
    
    def __init__(self, batch_size: int = 100, max_wait: float = 1.0):
        self.batch_size = batch_size
        self.max_wait = max_wait  # Maximum seconds to wait for batch to fill
        self.queue: List[Tuple[Any, asyncio.Future]] = []
        self.lock = asyncio.Lock()
        self.process_task = None
        self.logger = get_logger(__name__)
    
    async def add(self, item: Any) -> Any:
        """Add item for batch processing"""
        future = asyncio.get_event_loop().create_future()
        
        async with self.lock:
            self.queue.append((item, future))
            
            # Start processing if not already running
            if self.process_task is None or self.process_task.done():
                self.process_task = asyncio.create_task(self._process_batch())
        
        return await future
    
    async def _process_batch(self):
        """Process accumulated batch"""
        await asyncio.sleep(self.max_wait)  # Wait for batch to fill
        
        async with self.lock:
            if not self.queue:
                return
            
            # Take batch
            batch = self.queue[:self.batch_size]
            self.queue = self.queue[self.batch_size:]
            
        # Process batch
        items = [item for item, _ in batch]
        futures = [future for _, future in batch]
        
        try:
            # Process all items at once
            results = await self._batch_operation(items)
            
            # Distribute results
            for future, result in zip(futures, results):
                future.set_result(result)
        
        except Exception as e:
            # Set exception for all futures
            for future in futures:
                future.set_exception(e)
    
    async def _batch_operation(self, items: List[Any]) -> List[Any]:
        """Override this method for actual batch processing"""
        # Default implementation - process individually
        return items


class ConnectionPool:
    """Reusable connection pool for database operations"""
    
    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self.available = asyncio.Queue(maxsize=pool_size)
        self.lock = asyncio.Lock()
        self.logger = get_logger(__name__)
        
        # Initialize pool
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool"""
        import sqlite3
        
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self.connections.append(conn)
            self.available.put_nowait(conn)
    
    async def acquire(self):
        """Acquire a connection from the pool"""
        return await self.available.get()
    
    async def release(self, conn):
        """Release a connection back to the pool"""
        await self.available.put(conn)
    
    async def execute(self, query: str, params: tuple = ()) -> Any:
        """Execute a query using a pooled connection"""
        conn = await self.acquire()
        try:
            cursor = conn.cursor()
            result = cursor.execute(query, params)
            conn.commit()
            return result.fetchall()
        finally:
            await self.release(conn)
    
    def close_all(self):
        """Close all connections in the pool"""
        for conn in self.connections:
            conn.close()


class ParallelExecutor:
    """Execute tasks in parallel for better performance"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=self.max_workers)
        self.logger = get_logger(__name__)
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Run blocking function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_executor, func, *args, **kwargs)
    
    async def run_in_process(self, func: Callable, *args, **kwargs) -> Any:
        """Run CPU-intensive function in process pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_executor, func, *args, **kwargs)
    
    async def map_threaded(self, func: Callable, items: List[Any]) -> List[Any]:
        """Map function over items using thread pool"""
        tasks = [self.run_in_thread(func, item) for item in items]
        return await asyncio.gather(*tasks)
    
    async def map_process(self, func: Callable, items: List[Any]) -> List[Any]:
        """Map function over items using process pool"""
        tasks = [self.run_in_process(func, item) for item in items]
        return await asyncio.gather(*tasks)
    
    def shutdown(self):
        """Shutdown executors"""
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)


def memoize_async(maxsize: int = 128):
    """Async-aware memoization decorator"""
    
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        cache = {}
        cache_lock = asyncio.Lock()
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Create cache key
            key = (args, tuple(sorted(kwargs.items())))
            
            async with cache_lock:
                if key in cache:
                    return cache[key]
            
            # Call function
            result = await func(*args, **kwargs)
            
            async with cache_lock:
                # Implement LRU eviction
                if len(cache) >= maxsize:
                    # Remove oldest entry
                    oldest_key = next(iter(cache))
                    del cache[oldest_key]
                
                cache[key] = result
            
            return result
        
        wrapper.cache_info = lambda: {"size": len(cache), "maxsize": maxsize}
        wrapper.cache_clear = lambda: cache.clear()
        
        return wrapper
    
    return decorator


class LazyLoader:
    """Lazy loading for expensive resources"""
    
    def __init__(self, loader_func: Callable[[], Any]):
        self.loader_func = loader_func
        self._value = None
        self._loaded = False
        self._loading = False
        self._lock = threading.Lock()
    
    @property
    def value(self) -> Any:
        """Get the value, loading if necessary"""
        if not self._loaded:
            with self._lock:
                if not self._loaded and not self._loading:
                    self._loading = True
                    try:
                        self._value = self.loader_func()
                        self._loaded = True
                    finally:
                        self._loading = False
        
        return self._value
    
    def is_loaded(self) -> bool:
        """Check if value has been loaded"""
        return self._loaded
    
    def invalidate(self):
        """Invalidate the cached value"""
        with self._lock:
            self._loaded = False
            self._value = None


class PerformanceMonitor:
    """Monitor and optimize performance"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = asyncio.Lock()
        self.logger = get_logger(__name__)
    
    def measure(self, name: str):
        """Context manager for measuring execution time"""
        class Timer:
            def __init__(self, monitor, name):
                self.monitor = monitor
                self.name = name
                self.start_time = None
            
            def __enter__(self):
                self.start_time = time.perf_counter()
                return self
            
            def __exit__(self, *args):
                elapsed = time.perf_counter() - self.start_time
                asyncio.create_task(self.monitor.record_metric(self.name, elapsed))
        
        return Timer(self, name)
    
    async def record_metric(self, name: str, value: float):
        """Record a performance metric"""
        async with self.lock:
            if name not in self.metrics:
                self.metrics[name] = {
                    "count": 0,
                    "total": 0,
                    "min": float('inf'),
                    "max": 0,
                    "recent": []
                }
            
            metric = self.metrics[name]
            metric["count"] += 1
            metric["total"] += value
            metric["min"] = min(metric["min"], value)
            metric["max"] = max(metric["max"], value)
            
            # Keep recent values for percentiles
            metric["recent"].append(value)
            if len(metric["recent"]) > 100:
                metric["recent"] = metric["recent"][-100:]
    
    async def get_stats(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics"""
        async with self.lock:
            if name:
                if name not in self.metrics:
                    return {}
                
                metric = self.metrics[name]
                recent = sorted(metric["recent"])
                
                return {
                    "name": name,
                    "count": metric["count"],
                    "avg": metric["total"] / metric["count"] if metric["count"] > 0 else 0,
                    "min": metric["min"],
                    "max": metric["max"],
                    "p50": recent[len(recent)//2] if recent else 0,
                    "p95": recent[int(len(recent)*0.95)] if recent else 0,
                    "p99": recent[int(len(recent)*0.99)] if recent else 0
                }
            
            # Return all metrics
            return {
                name: await self.get_stats(name)
                for name in self.metrics
            }


async def demo_performance_optimizations():
    """Demonstrate performance optimizations"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        ⚡ PERFORMANCE OPTIMIZATIONS DEMO                            ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test async cache
    print("\n1️⃣ Async Cache Performance:")
    print("-" * 60)
    
    cache = AsyncCache(max_size=100)
    
    # Add some items
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")
    
    # Test hits and misses
    result = await cache.get("key1")  # Hit
    result = await cache.get("key1")  # Hit
    result = await cache.get("key4")  # Miss
    
    stats = cache.get_stats()
    print(f"   Cache stats:")
    print(f"     • Size: {stats['size']}/{stats['max_size']}")
    print(f"     • Hit rate: {stats['hit_rate']:.1%}")
    print(f"     • Total requests: {stats['total_requests']}")
    
    # Test cached async function
    print("\n2️⃣ Cached Async Function:")
    print("-" * 60)
    
    @async_cached(ttl=timedelta(seconds=5))
    async def expensive_operation(n: int) -> int:
        await asyncio.sleep(0.1)  # Simulate expensive operation
        return n * n
    
    # First call - slow
    start = time.time()
    result1 = await expensive_operation(10)
    time1 = time.time() - start
    
    # Second call - cached
    start = time.time()
    result2 = await expensive_operation(10)
    time2 = time.time() - start
    
    print(f"   First call: {time1:.3f}s (result: {result1})")
    print(f"   Cached call: {time2:.3f}s (result: {result2})")
    print(f"   Speedup: {time1/time2:.0f}x")
    
    # Test parallel execution
    print("\n3️⃣ Parallel Execution:")
    print("-" * 60)
    
    executor = ParallelExecutor(max_workers=4)
    
    def cpu_intensive(n):
        """Simulate CPU-intensive task"""
        total = 0
        for i in range(n * 1000000):
            total += i
        return total
    
    # Sequential execution
    start = time.time()
    sequential_results = []
    for i in range(4):
        sequential_results.append(cpu_intensive(1))
    sequential_time = time.time() - start
    
    # Parallel execution
    start = time.time()
    parallel_results = await executor.map_process(cpu_intensive, [1, 1, 1, 1])
    parallel_time = time.time() - start
    
    print(f"   Sequential: {sequential_time:.3f}s")
    print(f"   Parallel: {parallel_time:.3f}s")
    print(f"   Speedup: {sequential_time/parallel_time:.1f}x")
    
    executor.shutdown()
    
    # Test performance monitoring
    print("\n4️⃣ Performance Monitoring:")
    print("-" * 60)
    
    monitor = PerformanceMonitor()
    
    # Measure some operations
    for i in range(10):
        with monitor.measure("operation1"):
            await asyncio.sleep(0.01 + i * 0.001)
    
    for i in range(5):
        with monitor.measure("operation2"):
            await asyncio.sleep(0.02)
    
    # Get statistics
    stats = await monitor.get_stats()
    
    for name, metric in stats.items():
        if metric:
            print(f"   {name}:")
            print(f"     • Count: {metric['count']}")
            print(f"     • Average: {metric['avg']*1000:.1f}ms")
            print(f"     • Min/Max: {metric['min']*1000:.1f}ms / {metric['max']*1000:.1f}ms")
            print(f"     • P95: {metric['p95']*1000:.1f}ms")
    
    # Test lazy loading
    print("\n5️⃣ Lazy Loading:")
    print("-" * 60)
    
    load_count = 0
    
    def expensive_load():
        nonlocal load_count
        load_count += 1
        time.sleep(0.1)  # Simulate expensive load
        return {"data": "expensive data"}
    
    lazy_resource = LazyLoader(expensive_load)
    
    print(f"   Loaded? {lazy_resource.is_loaded()}")
    print(f"   Load count: {load_count}")
    
    # Access triggers load
    value1 = lazy_resource.value
    print(f"   After first access - Load count: {load_count}")
    
    # Subsequent accesses don't reload
    value2 = lazy_resource.value
    value3 = lazy_resource.value
    print(f"   After more accesses - Load count: {load_count}")
    
    print("""

═══════════════════════════════════════════════════════════════════════
✨ Performance Optimization Features:

1. Async Caching:
   • TTL-based expiration
   • LRU eviction
   • Hit rate tracking
   • Size limits

2. Batch Processing:
   • Accumulate items
   • Process in batches
   • Reduce overhead

3. Connection Pooling:
   • Reuse connections
   • Async-aware
   • Thread-safe

4. Parallel Execution:
   • Thread pools for I/O
   • Process pools for CPU
   • Async mapping

5. Performance Monitoring:
   • Execution time tracking
   • Percentile calculations
   • Real-time metrics

6. Lazy Loading:
   • Defer expensive operations
   • Load once, use many
   • Thread-safe

Benefits:
• 10-100x speedup possible
• Reduced memory usage
• Better resource utilization
• Scalable architecture

Next Steps:
• Add distributed caching
• Implement query optimization
• Add profiling tools
• Create performance dashboard
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    asyncio.run(demo_performance_optimizations())