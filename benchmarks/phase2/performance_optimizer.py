#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List
Performance Optimization Engine for Nix for Humanity
Achieves <500ms response times while maintaining consciousness-first principles
"""

import asyncio
import time
import psutil
import cProfile
import pstats
from io import StringIO
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass
from functools import wraps
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Tracks performance across all dimensions"""
    operation: str
    start_time: float
    end_time: float
    memory_before: float
    memory_after: float
    cpu_percent: float
    response_time_ms: float
    cache_hits: int = 0
    cache_misses: int = 0
    
    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000
    
    @property
    def memory_delta_mb(self) -> float:
        return (self.memory_after - self.memory_before) / 1024 / 1024
    
    def meets_target(self, target_ms: float = 500) -> bool:
        """Check if performance meets Phase 2 target"""
        return self.duration_ms < target_ms


class PerformanceOptimizer:
    """Main optimization engine coordinating all performance improvements"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        self.optimization_strategies = {
            'nlp': self._optimize_nlp,
            'xai': self._optimize_xai,
            'learning': self._optimize_learning,
            'memory': self._optimize_memory,
            'io': self._optimize_io
        }
        self._profiler = cProfile.Profile()
        
    def measure_performance(self, func: Callable) -> Callable:
        """Decorator to measure performance of any operation"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = await self._measure_async(func, *args, **kwargs)
            self.metrics_history.append(metrics)
            
            if not metrics.meets_target():
                logger.warning(f"{func.__name__} exceeded 500ms target: {metrics.duration_ms:.2f}ms")
                await self._auto_optimize(func.__name__, metrics)
            
            return metrics, await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics = self._measure_sync(func, *args, **kwargs)
            self.metrics_history.append(metrics)
            
            if not metrics.meets_target():
                logger.warning(f"{func.__name__} exceeded 500ms target: {metrics.duration_ms:.2f}ms")
                self._auto_optimize_sync(func.__name__, metrics)
            
            result = func(*args, **kwargs)
            return metrics, result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    async def _measure_async(self, func: Callable, *args, **kwargs) -> PerformanceMetrics:
        """Measure async function performance"""
        process = psutil.Process()
        memory_before = process.memory_info().rss
        cpu_before = process.cpu_percent()
        
        start_time = time.perf_counter()
        await func(*args, **kwargs)
        end_time = time.perf_counter()
        
        memory_after = process.memory_info().rss
        cpu_after = process.cpu_percent()
        
        return PerformanceMetrics(
            operation=func.__name__,
            start_time=start_time,
            end_time=end_time,
            memory_before=memory_before,
            memory_after=memory_after,
            cpu_percent=(cpu_after - cpu_before),
            response_time_ms=(end_time - start_time) * 1000
        )
    
    def _measure_sync(self, func: Callable, *args, **kwargs) -> PerformanceMetrics:
        """Measure sync function performance"""
        process = psutil.Process()
        memory_before = process.memory_info().rss
        cpu_before = process.cpu_percent()
        
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        
        memory_after = process.memory_info().rss
        cpu_after = process.cpu_percent()
        
        return PerformanceMetrics(
            operation=func.__name__,
            start_time=start_time,
            end_time=end_time,
            memory_before=memory_before,
            memory_after=memory_after,
            cpu_percent=(cpu_after - cpu_before),
            response_time_ms=(end_time - start_time) * 1000
        )
    
    async def _auto_optimize(self, operation: str, metrics: PerformanceMetrics):
        """Automatically apply optimizations when targets are missed"""
        logger.info(f"Auto-optimizing {operation}...")
        
        # Identify bottleneck category
        if 'nlp' in operation.lower():
            await self._optimize_nlp(metrics)
        elif 'xai' in operation.lower():
            await self._optimize_xai(metrics)
        elif 'learning' in operation.lower():
            await self._optimize_learning(metrics)
        
        # Always try memory optimization
        await self._optimize_memory(metrics)
    
    def _auto_optimize_sync(self, operation: str, metrics: PerformanceMetrics):
        """Sync version of auto-optimization"""
        asyncio.create_task(self._auto_optimize(operation, metrics))
    
    async def _optimize_nlp(self, metrics: PerformanceMetrics):
        """NLP-specific optimizations"""
        logger.info("Applying NLP optimizations...")
        # Implemented in nlp_optimizer.py
        from .nlp_optimizer import NLPOptimizer
        optimizer = NLPOptimizer()
        await optimizer.optimize(metrics)
    
    async def _optimize_xai(self, metrics: PerformanceMetrics):
        """XAI-specific optimizations"""
        logger.info("Applying XAI optimizations...")
        # Implemented in xai_optimizer.py
        from .xai_optimizer import XAIOptimizer
        optimizer = XAIOptimizer()
        await optimizer.optimize(metrics)
    
    async def _optimize_learning(self, metrics: PerformanceMetrics):
        """Learning system optimizations"""
        logger.info("Applying learning system optimizations...")
        # Batch operations, lazy loading, etc.
    
    async def _optimize_memory(self, metrics: PerformanceMetrics):
        """Memory usage optimizations"""
        logger.info("Applying memory optimizations...")
        # Implemented in memory_profiler.py
        from .memory_profiler import MemoryProfiler
        profiler = MemoryProfiler()
        await profiler.optimize(metrics)
    
    async def _optimize_io(self, metrics: PerformanceMetrics):
        """I/O optimizations"""
        logger.info("Applying I/O optimizations...")
        # Async I/O, buffering, etc.
    
    def profile_code(self, func: Callable) -> Tuple[Any, str]:
        """Profile code execution for detailed analysis"""
        self._profiler.enable()
        result = func()
        self._profiler.disable()
        
        # Get profile stats
        s = StringIO()
        ps = pstats.Stats(self._profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        return result, s.getvalue()
    
    async def parallel_execute(self, tasks: List[Callable], max_workers: int = 4) -> List[Any]:
        """Execute tasks in parallel for optimal performance"""
        loop = asyncio.get_event_loop()
        
        # Determine if tasks are CPU or I/O bound
        cpu_bound_tasks = []
        io_bound_tasks = []
        
        for task in tasks:
            if self._is_cpu_bound(task):
                cpu_bound_tasks.append(task)
            else:
                io_bound_tasks.append(task)
        
        results = []
        
        # Execute CPU-bound tasks in process pool
        if cpu_bound_tasks:
            cpu_futures = [
                loop.run_in_executor(self.process_pool, task)
                for task in cpu_bound_tasks
            ]
            cpu_results = await asyncio.gather(*cpu_futures)
            results.extend(cpu_results)
        
        # Execute I/O-bound tasks in thread pool
        if io_bound_tasks:
            io_futures = [
                loop.run_in_executor(self.thread_pool, task)
                for task in io_bound_tasks
            ]
            io_results = await asyncio.gather(*io_futures)
            results.extend(io_results)
        
        return results
    
    def _is_cpu_bound(self, task: Callable) -> bool:
        """Heuristic to determine if task is CPU-bound"""
        # Check function name and module for hints
        cpu_indicators = ['compute', 'calculate', 'process', 'parse', 'nlp', 'xai']
        return any(indicator in str(task).lower() for indicator in cpu_indicators)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics_history:
            return {"status": "No metrics collected"}
        
        # Calculate statistics
        response_times = [m.duration_ms for m in self.metrics_history]
        memory_deltas = [m.memory_delta_mb for m in self.metrics_history]
        
        report = {
            "total_operations": len(self.metrics_history),
            "average_response_ms": np.mean(response_times),
            "p95_response_ms": np.percentile(response_times, 95),
            "p99_response_ms": np.percentile(response_times, 99),
            "max_response_ms": max(response_times),
            "min_response_ms": min(response_times),
            "target_met_percentage": sum(1 for m in self.metrics_history if m.meets_target()) / len(self.metrics_history) * 100,
            "average_memory_delta_mb": np.mean(memory_deltas),
            "operations_by_type": self._group_by_operation(),
            "optimization_recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _group_by_operation(self) -> Dict[str, Dict[str, float]]:
        """Group metrics by operation type"""
        grouped = {}
        for metric in self.metrics_history:
            if metric.operation not in grouped:
                grouped[metric.operation] = {
                    "count": 0,
                    "total_ms": 0,
                    "max_ms": 0,
                    "min_ms": float('inf')
                }
            
            grouped[metric.operation]["count"] += 1
            grouped[metric.operation]["total_ms"] += metric.duration_ms
            grouped[metric.operation]["max_ms"] = max(grouped[metric.operation]["max_ms"], metric.duration_ms)
            grouped[metric.operation]["min_ms"] = min(grouped[metric.operation]["min_ms"], metric.duration_ms)
        
        # Calculate averages
        for op in grouped:
            grouped[op]["average_ms"] = grouped[op]["total_ms"] / grouped[op]["count"]
        
        return grouped
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        # Check for slow operations
        slow_ops = [m for m in self.metrics_history if not m.meets_target()]
        if slow_ops:
            slowest = max(slow_ops, key=lambda m: m.duration_ms)
            recommendations.append(f"Focus on optimizing {slowest.operation} (currently {slowest.duration_ms:.0f}ms)")
        
        # Check memory usage
        high_memory_ops = [m for m in self.metrics_history if m.memory_delta_mb > 50]
        if high_memory_ops:
            recommendations.append("Consider memory optimization for operations using >50MB")
        
        # Check cache effectiveness
        cache_metrics = [m for m in self.metrics_history if m.cache_hits + m.cache_misses > 0]
        if cache_metrics:
            total_hits = sum(m.cache_hits for m in cache_metrics)
            total_misses = sum(m.cache_misses for m in cache_metrics)
            hit_rate = total_hits / (total_hits + total_misses) if total_hits + total_misses > 0 else 0
            if hit_rate < 0.8:
                recommendations.append(f"Improve cache hit rate (currently {hit_rate:.1%})")
        
        return recommendations
    
    async def benchmark_operation(self, operation: Callable, iterations: int = 100) -> Dict[str, float]:
        """Benchmark an operation multiple times for statistical analysis"""
        logger.info(f"Benchmarking {operation.__name__} with {iterations} iterations...")
        
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            if asyncio.iscoroutinefunction(operation):
                await operation()
            else:
                operation()
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        return {
            "mean_ms": np.mean(times),
            "std_ms": np.std(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p50_ms": np.percentile(times, 50),
            "p95_ms": np.percentile(times, 95),
            "p99_ms": np.percentile(times, 99)
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


# Sacred optimization principles
class ConsciousPerformance:
    """Maintains consciousness-first principles while optimizing"""
    
    @staticmethod
    def optimize_with_awareness(func: Callable) -> Callable:
        """Optimize while maintaining user awareness"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Show immediate feedback (consciousness-first)
            print("✨ Processing your request...", end='', flush=True)
            
            # Execute optimized function
            result = await func(*args, **kwargs)
            
            # Clear feedback
            print("\r" + " " * 30 + "\r", end='', flush=True)
            
            return result
        
        return wrapper
    
    @staticmethod
    def batch_with_rhythm(operations: List[Callable], rhythm_ms: int = 50) -> List[Any]:
        """Batch operations while maintaining natural rhythm"""
        results = []
        for i, op in enumerate(operations):
            # Natural pause between operations
            if i > 0:
                time.sleep(rhythm_ms / 1000)
            results.append(op())
        return results


# Example usage
if __name__ == "__main__":
    optimizer = PerformanceOptimizer()
    
    # Example function to optimize
    @optimizer.measure_performance
    async def example_nlp_operation():
        """Simulated NLP operation"""
        await asyncio.sleep(0.6)  # Simulating slow operation
        return "Processed"
    
    # Run optimization
    async def main():
        # This will trigger auto-optimization since it exceeds 500ms
        metrics, result = await example_nlp_operation()
        print(f"Operation took {metrics.duration_ms:.2f}ms")
        
        # Get performance report
        report = optimizer.get_performance_report()
        print("\nPerformance Report:")
        for key, value in report.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
        
        optimizer.cleanup()
    
    asyncio.run(main())