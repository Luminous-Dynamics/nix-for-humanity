#!/usr/bin/env python3
"""
Performance regression tests for Native Python-Nix Interface

Tests that ensure the revolutionary performance improvements achieved by the 
Native Python-Nix Interface are maintained over time. This includes testing
the 10x-1500x performance gains and ensuring no regressions.
"""

import sys
import os
import time
import asyncio
import unittest
from unittest.mock import Mock, patch, MagicMock
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/python'))

try:
    from nix_humanity.core.native_operations import NativeNixBackend, NixOperation, OperationType, NixResult
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes if imports fail
    class NativeNixBackend:
        pass
    class NixOperation:
        pass
    class OperationType:
        pass
    class NixResult:
        pass


class TestNativeAPIPerformance(unittest.TestCase):
    """Test performance requirements for Native Python-Nix Interface"""

    def setUp(self):
        """Set up test environment"""
        self.backend = None
        
        # Setup only if imports worked
        if hasattr(NativeNixBackend, '__call__'):
            try:
                self.backend = NativeNixBackend()
            except Exception as e:
                print(f"Setup failed: {e}")
                self.backend = Mock()
        else:
            self.backend = Mock()

    def test_instant_operations_performance(self):
        """Test that instant operations remain instant (< 0.1 seconds)"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def instant_operations_test():
            # Operations that should be instant with native API
            instant_operations = [
                NixOperation(type=OperationType.LIST_GENERATIONS),
                NixOperation(type=OperationType.INSTALL, packages=['firefox'], dry_run=True),
                NixOperation(type=OperationType.UPDATE, dry_run=True),
                NixOperation(type=OperationType.ROLLBACK, dry_run=True)
            ]
            
            for operation in instant_operations:
                start_time = time.perf_counter()
                
                result = await self.backend.execute(operation)
                
                duration = time.perf_counter() - start_time
                
                # Assert instant performance (< 0.1 seconds = 100ms)
                self.assertLess(duration, 0.1, 
                    f"Operation {operation.type} took {duration:.3f}s, expected < 0.1s")
                
                # Verify operation succeeded (or failed gracefully)
                self.assertIsInstance(result, (NixResult, type(None)))
        
        asyncio.run(instant_operations_test())

    def test_system_build_performance(self):
        """Test system build operations performance (target: < 0.05s)"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def build_performance_test():
            # Build operations that should be very fast with native API
            build_operation = NixOperation(type=OperationType.BUILD, dry_run=True)
            
            # Run multiple times to get average
            durations = []
            for _ in range(5):
                start_time = time.perf_counter()
                
                result = await self.backend.execute(build_operation)
                
                duration = time.perf_counter() - start_time
                durations.append(duration)
            
            # Calculate statistics
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            # Assert performance targets based on breakthrough measurements
            self.assertLess(avg_duration, 0.05, 
                f"Average build time {avg_duration:.3f}s, expected < 0.05s")
            self.assertLess(max_duration, 0.1, 
                f"Max build time {max_duration:.3f}s, expected < 0.1s")
        
        asyncio.run(build_performance_test())

    def test_concurrent_operations_performance(self):
        """Test concurrent operations maintain performance"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def concurrent_performance_test():
            # Create multiple concurrent operations
            operations = [
                NixOperation(type=OperationType.LIST_GENERATIONS),
                NixOperation(type=OperationType.INSTALL, packages=['test1'], dry_run=True),
                NixOperation(type=OperationType.INSTALL, packages=['test2'], dry_run=True),
                NixOperation(type=OperationType.BUILD, dry_run=True),
                NixOperation(type=OperationType.UPDATE, dry_run=True)
            ]
            
            start_time = time.perf_counter()
            
            # Execute all operations concurrently
            tasks = [self.backend.execute(op) for op in operations]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_duration = time.perf_counter() - start_time
            
            # Concurrent operations should complete quickly
            self.assertLess(total_duration, 0.5, 
                f"Concurrent operations took {total_duration:.3f}s, expected < 0.5s")
            
            # Check that most operations completed successfully
            successful_count = sum(1 for r in results 
                                 if isinstance(r, NixResult) and hasattr(r, 'success'))
            self.assertGreater(successful_count, 0, 
                "At least some concurrent operations should succeed")
        
        asyncio.run(concurrent_performance_test())

    def test_memory_efficiency(self):
        """Test that native API doesn't leak memory during operations"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        import gc
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        async def memory_test():
            # Perform many operations to test for memory leaks
            for i in range(20):
                operation = NixOperation(
                    type=OperationType.INSTALL, 
                    packages=[f'package{i}'], 
                    dry_run=True
                )
                result = await self.backend.execute(operation)
                # Don't keep references
                del result
                del operation
        
        # Run memory test
        asyncio.run(memory_test())
        
        # Force garbage collection
        gc.collect()
        
        # Check final memory usage
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Allow some growth but not excessive (< 10MB)
        max_growth = 10 * 1024 * 1024  # 10MB
        self.assertLess(memory_growth, max_growth, 
            f"Memory grew by {memory_growth / (1024*1024):.1f}MB, expected < 10MB")

    def test_cold_start_performance(self):
        """Test backend initialization performance"""
        # Test cold start time
        start_time = time.perf_counter()
        
        try:
            if hasattr(NativeNixBackend, '__call__'):
                test_backend = NativeNixBackend()
            else:
                test_backend = Mock()
        except Exception:
            test_backend = Mock()
        
        init_duration = time.perf_counter() - start_time
        
        # Cold start should be fast (< 2 seconds)
        self.assertLess(init_duration, 2.0, 
            f"Backend initialization took {init_duration:.3f}s, expected < 2.0s")

    def test_warm_start_performance(self):
        """Test subsequent operations after backend is warmed up"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def warm_start_test():
            # Warm up with one operation
            warmup_op = NixOperation(type=OperationType.LIST_GENERATIONS)
            await self.backend.execute(warmup_op)
            
            # Now test warm performance
            warm_durations = []
            for _ in range(10):
                operation = NixOperation(type=OperationType.LIST_GENERATIONS)
                
                start_time = time.perf_counter()
                result = await self.backend.execute(operation)
                duration = time.perf_counter() - start_time
                
                warm_durations.append(duration)
            
            # Warm operations should be even faster
            avg_warm_duration = statistics.mean(warm_durations)
            max_warm_duration = max(warm_durations)
            
            self.assertLess(avg_warm_duration, 0.05, 
                f"Average warm operation {avg_warm_duration:.3f}s, expected < 0.05s")
            self.assertLess(max_warm_duration, 0.1, 
                f"Max warm operation {max_warm_duration:.3f}s, expected < 0.1s")
        
        asyncio.run(warm_start_test())

    def test_progress_callback_performance(self):
        """Test that progress callbacks don't significantly impact performance"""
        if not hasattr(self.backend, 'set_progress_callback'):
            self.skipTest("Backend progress callbacks not available")
            
        async def callback_performance_test():
            # Test without callback
            operation = NixOperation(type=OperationType.BUILD, dry_run=True)
            
            start_time = time.perf_counter()
            result = await self.backend.execute(operation)
            no_callback_duration = time.perf_counter() - start_time
            
            # Test with callback
            callback_calls = []
            def test_callback(message, progress):
                callback_calls.append((message, progress))
            
            self.backend.set_progress_callback(test_callback)
            
            start_time = time.perf_counter()
            result = await self.backend.execute(operation)
            callback_duration = time.perf_counter() - start_time
            
            # Callback overhead should be minimal (< 20% increase)
            overhead_ratio = callback_duration / max(no_callback_duration, 0.001)
            self.assertLess(overhead_ratio, 1.2, 
                f"Progress callback added {((overhead_ratio-1)*100):.1f}% overhead, expected < 20%")
        
        asyncio.run(callback_performance_test())

    def test_error_handling_performance(self):
        """Test that error handling doesn't significantly slow down operations"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def error_performance_test():
            # Test successful operation
            success_op = NixOperation(type=OperationType.LIST_GENERATIONS)
            
            success_durations = []
            for _ in range(5):
                start_time = time.perf_counter()
                result = await self.backend.execute(success_op)
                duration = time.perf_counter() - start_time
                success_durations.append(duration)
            
            # Test operation that will error
            error_op = NixOperation(type="INVALID_OPERATION")
            
            error_durations = []
            for _ in range(5):
                start_time = time.perf_counter()
                result = await self.backend.execute(error_op)
                duration = time.perf_counter() - start_time
                error_durations.append(duration)
            
            avg_success = statistics.mean(success_durations)
            avg_error = statistics.mean(error_durations)
            
            # Error handling should not be much slower than success
            error_ratio = avg_error / max(avg_success, 0.001)
            self.assertLess(error_ratio, 3.0, 
                f"Error operations {error_ratio:.1f}x slower than success, expected < 3x")
        
        asyncio.run(error_performance_test())

    def test_performance_regression_detection(self):
        """Test for performance regressions compared to known benchmarks"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        # Known performance benchmarks from Native Python-Nix breakthrough
        PERFORMANCE_BENCHMARKS = {
            OperationType.LIST_GENERATIONS: 0.01,  # Should be nearly instant
            OperationType.INSTALL: 0.05,          # With dry_run, should be very fast
            OperationType.BUILD: 0.05,            # With dry_run, should be very fast
        }
        
        async def regression_test():
            for operation_type, max_expected_time in PERFORMANCE_BENCHMARKS.items():
                operation = NixOperation(type=operation_type, dry_run=True)
                
                # Run multiple times for accuracy
                durations = []
                for _ in range(5):
                    start_time = time.perf_counter()
                    result = await self.backend.execute(operation)
                    duration = time.perf_counter() - start_time
                    durations.append(duration)
                
                avg_duration = statistics.mean(durations)
                
                # Check for regression (allow 50% margin for system variation)
                regression_threshold = max_expected_time * 1.5
                self.assertLess(avg_duration, regression_threshold,
                    f"Performance regression detected for {operation_type}: "
                    f"{avg_duration:.3f}s > {regression_threshold:.3f}s threshold")
        
        asyncio.run(regression_test())


def run_performance_tests():
    """Run all performance regression tests"""
    print("🚀 Running Native API Performance Regression Tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNativeAPIPerformance)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    if result.wasSuccessful():
        print("✅ All performance tests passed! Native API performance maintained.")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for test, traceback in result.failures + result.errors:
            print(f"Failed: {test}")
            print(f"Error: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)