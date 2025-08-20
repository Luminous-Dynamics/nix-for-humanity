#!/usr/bin/env python3
"""
from typing import Tuple, Dict
Automated Performance Regression Tests for Nix for Humanity
Ensures that performance improvements are maintained across updates
"""

import time
import pytest
import asyncio
import statistics
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import subprocess
import sys
import os

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from luminous_nix.core.native_operations import (
    EnhancedNativeNixBackend,
    NixOperation,
    OperationType,
    NATIVE_API_AVAILABLE
)


class PerformanceBenchmark:
    """Track performance metrics for regression testing"""
    
    def __init__(self):
        self.results = {}
        self.thresholds = self._load_thresholds()
        
    def _load_thresholds(self) -> Dict[str, float]:
        """Load performance thresholds from config or use defaults"""
        return {
            "list_generations": 0.1,      # Max 100ms
            "search_package": 0.5,         # Max 500ms  
            "dry_build": 1.0,             # Max 1s
            "check_package": 0.2,         # Max 200ms
            "rollback_plan": 0.1,         # Max 100ms
            "cache_hit": 0.01,            # Max 10ms
            "parse_generations": 0.05,    # Max 50ms
            "validate_input": 0.001,      # Max 1ms
        }
        
    def measure(self, operation_name: str, func, *args, **kwargs) -> Tuple[Any, float]:
        """Measure the execution time of a function"""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        
        if operation_name not in self.results:
            self.results[operation_name] = []
        self.results[operation_name].append(duration)
        
        return result, duration
        
    async def measure_async(self, operation_name: str, coro) -> Tuple[Any, float]:
        """Measure the execution time of an async function"""
        start = time.perf_counter()
        result = await coro
        duration = time.perf_counter() - start
        
        if operation_name not in self.results:
            self.results[operation_name] = []
        self.results[operation_name].append(duration)
        
        return result, duration
        
    def check_regression(self, operation_name: str) -> bool:
        """Check if an operation has regressed beyond threshold"""
        if operation_name not in self.results:
            return True
            
        times = self.results[operation_name]
        if not times:
            return True
            
        # Use 95th percentile to avoid outliers
        p95 = statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
        threshold = self.thresholds.get(operation_name, 1.0)
        
        return p95 <= threshold
        
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        
        for operation, times in self.results.items():
            if times:
                summary[operation] = {
                    "min": min(times),
                    "max": max(times),
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "p95": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
                    "threshold": self.thresholds.get(operation, 1.0),
                    "passed": self.check_regression(operation),
                    "samples": len(times)
                }
                
        return summary


# Global benchmark instance
benchmark = PerformanceBenchmark()


class TestPerformanceRegression:
    """Test suite for performance regression"""
    
    @pytest.fixture
    def backend(self):
        """Create enhanced backend instance"""
        return EnhancedNativeNixBackend()
        
    @pytest.fixture
    def basic_backend(self):
        """Create basic backend for comparison"""
        from luminous_nix.core.native_operations import NativeNixBackend
        return NativeNixBackend()
        
    def test_list_generations_performance(self, backend):
        """Test that listing generations stays fast"""
        operation = NixOperation(
            type=OperationType.LIST_GENERATIONS
        )
        
        # Warm up
        backend.execute_sync(operation)
        
        # Measure multiple times
        for _ in range(10):
            _, duration = benchmark.measure(
                "list_generations",
                backend.execute_sync,
                operation
            )
            
        assert benchmark.check_regression("list_generations"), \
            f"List generations regressed: {benchmark.results['list_generations']}"
            
    def test_search_package_performance(self, backend):
        """Test that package search stays fast"""
        operation = NixOperation(
            type=OperationType.SEARCH,
            packages=["firefox"]
        )
        
        # First search (no cache)
        _, duration1 = benchmark.measure(
            "search_package",
            backend.execute_sync,
            operation
        )
        
        # Second search (should hit cache)
        _, duration2 = benchmark.measure(
            "cache_hit",
            backend.execute_sync,
            operation
        )
        
        # Cache should be significantly faster
        assert duration2 < duration1 * 0.1, \
            f"Cache not working: {duration1}s vs {duration2}s"
            
        assert benchmark.check_regression("search_package"), \
            "Package search performance regressed"
            
    def test_dry_build_performance(self, backend):
        """Test that dry builds stay fast"""
        if not NATIVE_API_AVAILABLE:
            pytest.skip("Native API not available")
            
        operation = NixOperation(
            type=OperationType.BUILD,
            options={"dry_run": True}
        )
        
        # Measure
        _, duration = benchmark.measure(
            "dry_build",
            backend.execute_sync,
            operation
        )
        
        assert benchmark.check_regression("dry_build"), \
            f"Dry build performance regressed: {duration}s"
            
    def test_input_validation_performance(self, backend):
        """Test that input validation is fast"""
        from security.input_validator import InputValidator
        
        # Test various inputs
        test_inputs = [
            "install firefox",
            "update my system",
            "search for python packages",
            "rollback to previous generation",
            "install firefox && rm -rf /",  # Malicious
        ]
        
        for input_text in test_inputs:
            _, duration = benchmark.measure(
                "validate_input",
                InputValidator.validate_input,
                input_text,
                "nlp"
            )
            
        assert benchmark.check_regression("validate_input"), \
            "Input validation performance regressed"
            
    def test_generation_parsing_performance(self, backend):
        """Test that generation parsing stays fast"""
        # Create mock generation data
        mock_generations = [
            {
                "generation": i,
                "date": f"2024-01-{i:02d} 12:00:00",
                "current": i == 10
            }
            for i in range(1, 101)  # 100 generations
        ]
        
        # Measure parsing
        _, duration = benchmark.measure(
            "parse_generations",
            backend._parse_generations,
            "\n".join([f"{g['generation']} {g['date']}" for g in mock_generations])
        )
        
        assert benchmark.check_regression("parse_generations"), \
            "Generation parsing performance regressed"
            
    @pytest.mark.asyncio
    async def test_async_operation_performance(self, backend):
        """Test async operation performance"""
        operation = NixOperation(
            type=OperationType.LIST_GENERATIONS
        )
        
        # Measure async execution
        _, duration = await benchmark.measure_async(
            "async_list_generations",
            backend.execute(operation)
        )
        
        # Async should not add significant overhead
        assert duration < 0.2, f"Async overhead too high: {duration}s"
        
    def test_cache_effectiveness(self, backend):
        """Test that caching provides significant speedup"""
        # Operation that benefits from caching
        operation = NixOperation(
            type=OperationType.CHECK_PACKAGE,
            packages=["python3"]
        )
        
        # Clear cache first
        if hasattr(backend, 'cache'):
            backend.cache.clear()
            
        # First call (no cache)
        result1, duration1 = benchmark.measure(
            "check_package",
            backend.execute_sync,
            operation
        )
        
        # Second call (cached)
        result2, duration2 = benchmark.measure(
            "cache_hit",
            backend.execute_sync,
            operation
        )
        
        # Results should be identical
        assert result1.data == result2.data, "Cache returned different results"
        
        # Cache should be at least 10x faster
        speedup = duration1 / duration2 if duration2 > 0 else float('inf')
        assert speedup > 10, f"Cache speedup insufficient: {speedup}x"
        
    def test_enhanced_vs_basic_performance(self, backend, basic_backend):
        """Compare enhanced backend to basic backend"""
        operation = NixOperation(
            type=OperationType.LIST_GENERATIONS
        )
        
        # Measure basic backend
        basic_start = time.perf_counter()
        basic_result = basic_backend.execute_sync(operation)
        basic_duration = time.perf_counter() - basic_start
        
        # Measure enhanced backend
        enhanced_start = time.perf_counter()
        enhanced_result = backend.execute_sync(operation)
        enhanced_duration = time.perf_counter() - enhanced_start
        
        # Enhanced should be faster
        assert enhanced_duration <= basic_duration, \
            f"Enhanced backend slower: {enhanced_duration}s vs {basic_duration}s"
            
        # Record speedup
        speedup = basic_duration / enhanced_duration if enhanced_duration > 0 else float('inf')
        print(f"\n🚀 Enhanced backend speedup: {speedup:.1f}x")
        
    def test_memory_efficiency(self, backend):
        """Test that enhanced backend doesn't use excessive memory"""
        import psutil
        import gc
        
        # Get initial memory
        gc.collect()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        operation = NixOperation(type=OperationType.LIST_GENERATIONS)
        for _ in range(100):
            backend.execute_sync(operation)
            
        # Check memory growth
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Should not grow more than 50MB
        assert memory_growth < 50, \
            f"Excessive memory growth: {memory_growth:.1f}MB"


@pytest.fixture(scope="session", autouse=True)
def performance_report(request):
    """Generate performance report after all tests"""
    def generate_report():
        summary = benchmark.get_summary()
        
        # Create report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "native_api_available": NATIVE_API_AVAILABLE,
            "results": summary,
            "overall_pass": all(
                op_data.get("passed", False) 
                for op_data in summary.values()
            )
        }
        
        # Save report
        report_dir = Path(__file__).parent.parent / "performance_reports"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"regression_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Performance Regression Test Summary")
        print("=" * 60)
        
        for operation, data in summary.items():
            status = "✅" if data["passed"] else "❌"
            print(f"{status} {operation}:")
            print(f"   Mean: {data['mean']*1000:.2f}ms")
            print(f"   P95: {data['p95']*1000:.2f}ms (threshold: {data['threshold']*1000:.0f}ms)")
            
        print("=" * 60)
        print(f"Overall: {'✅ PASS' if report['overall_pass'] else '❌ FAIL'}")
        print(f"Report saved to: {report_file}")
        
    request.addfinalizer(generate_report)


if __name__ == "__main__":
    # Run with detailed output
    pytest.main([__file__, "-v", "--tb=short"])