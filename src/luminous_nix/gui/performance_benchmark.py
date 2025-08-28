#!/usr/bin/env python3
"""
⚡ Performance Benchmarking Suite for Production System
Measures and validates performance metrics
"""

import time
import json
import asyncio
import statistics
import random
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from production_deployment import ProductionDeployment
from services import InterfaceGenerationService, PatternAnalysisService
from performance_optimizations import AsyncCache, ParallelExecutor
from config_manager import get_config


class PerformanceBenchmark:
    """Comprehensive performance benchmarking"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {},
            'summary': {}
        }
        self.deployment = ProductionDeployment()
        self.deployment.initialize_services()
    
    def measure_time(self, func, *args, **kwargs) -> Tuple[float, Any]:
        """Measure execution time of a function"""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return elapsed * 1000, result  # Return in milliseconds
    
    async def measure_async_time(self, func, *args, **kwargs) -> Tuple[float, Any]:
        """Measure execution time of an async function"""
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return elapsed * 1000, result  # Return in milliseconds
    
    def benchmark_interface_generation(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark interface generation performance"""
        print("\n🎯 Benchmarking Interface Generation...")
        
        service = self.deployment.services['interface']
        requests = [
            "Create a simple button",
            "Build a complex dashboard with charts",
            "Design a user profile page",
            "Generate a data table with sorting",
            "Create a form with validation"
        ]
        
        times = []
        cache_hits = 0
        
        for i in range(iterations):
            request = random.choice(requests)
            elapsed, response = self.measure_time(
                service.generate_interface,
                request,
                {"iteration": i}
            )
            times.append(elapsed)
            
            # Check if it was cached
            if response.metadata and response.metadata.get('from_cache'):
                cache_hits += 1
        
        return {
            'iterations': iterations,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'cache_hits': cache_hits,
            'cache_hit_rate': cache_hits / iterations * 100
        }
    
    def benchmark_pattern_analysis(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark pattern analysis performance"""
        print("\n📊 Benchmarking Pattern Analysis...")
        
        service = self.deployment.services['pattern']
        times = []
        
        for i in range(iterations):
            # Force refresh on first iteration only
            force_refresh = (i == 0)
            
            elapsed, response = self.measure_time(
                service.analyze_patterns,
                force_refresh
            )
            times.append(elapsed)
        
        return {
            'iterations': iterations,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def benchmark_database_operations(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark database operations"""
        print("\n🗄️ Benchmarking Database Operations...")
        
        config = get_config()
        db_path = config.db_path
        
        # Ensure database exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        insert_times = []
        select_times = []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value TEXT,
                timestamp TEXT
            )
        """)
        
        for i in range(iterations):
            # Benchmark insert
            start = time.perf_counter()
            cursor.execute("""
                INSERT INTO benchmark_test (value, timestamp)
                VALUES (?, ?)
            """, (f"test_{i}", datetime.now().isoformat()))
            conn.commit()
            insert_times.append((time.perf_counter() - start) * 1000)
            
            # Benchmark select
            start = time.perf_counter()
            cursor.execute("""
                SELECT * FROM benchmark_test
                WHERE id = ?
            """, (i + 1,))
            cursor.fetchone()
            select_times.append((time.perf_counter() - start) * 1000)
        
        # Cleanup
        cursor.execute("DROP TABLE benchmark_test")
        conn.commit()
        conn.close()
        
        return {
            'iterations': iterations,
            'insert': {
                'min_ms': min(insert_times),
                'max_ms': max(insert_times),
                'mean_ms': statistics.mean(insert_times),
                'median_ms': statistics.median(insert_times)
            },
            'select': {
                'min_ms': min(select_times),
                'max_ms': max(select_times),
                'mean_ms': statistics.mean(select_times),
                'median_ms': statistics.median(select_times)
            }
        }
    
    async def benchmark_cache_performance(self, iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark cache performance"""
        print("\n💾 Benchmarking Cache Performance...")
        
        cache = AsyncCache(max_size=100)
        
        set_times = []
        get_hit_times = []
        get_miss_times = []
        
        # Benchmark cache operations
        for i in range(iterations):
            key = f"key_{i % 50}"  # Reuse some keys for hits
            value = f"value_{i}"
            
            # Benchmark set
            elapsed, _ = await self.measure_async_time(
                cache.set,
                key,
                value
            )
            set_times.append(elapsed)
            
            # Benchmark get (hit)
            elapsed, result = await self.measure_async_time(
                cache.get,
                key
            )
            if result is not None:
                get_hit_times.append(elapsed)
            
            # Benchmark get (miss)
            elapsed, result = await self.measure_async_time(
                cache.get,
                f"missing_{i}"
            )
            get_miss_times.append(elapsed)
        
        stats = cache.get_stats()
        
        return {
            'iterations': iterations,
            'set': {
                'min_ms': min(set_times),
                'max_ms': max(set_times),
                'mean_ms': statistics.mean(set_times),
                'median_ms': statistics.median(set_times)
            },
            'get_hit': {
                'min_ms': min(get_hit_times) if get_hit_times else 0,
                'max_ms': max(get_hit_times) if get_hit_times else 0,
                'mean_ms': statistics.mean(get_hit_times) if get_hit_times else 0,
                'median_ms': statistics.median(get_hit_times) if get_hit_times else 0
            },
            'get_miss': {
                'min_ms': min(get_miss_times),
                'max_ms': max(get_miss_times),
                'mean_ms': statistics.mean(get_miss_times),
                'median_ms': statistics.median(get_miss_times)
            },
            'cache_stats': stats
        }
    
    async def benchmark_parallel_execution(self) -> Dict[str, Any]:
        """Benchmark parallel execution performance"""
        print("\n🔀 Benchmarking Parallel Execution...")
        
        executor = ParallelExecutor(max_workers=4)
        
        def cpu_task(n):
            """CPU-intensive task"""
            total = 0
            for i in range(n * 100000):
                total += i
            return total
        
        # Sequential execution
        start = time.perf_counter()
        sequential_results = [cpu_task(10) for _ in range(8)]
        sequential_time = (time.perf_counter() - start) * 1000
        
        # Parallel execution
        start = time.perf_counter()
        parallel_results = await executor.map_process(cpu_task, [10] * 8)
        parallel_time = (time.perf_counter() - start) * 1000
        
        executor.shutdown()
        
        speedup = sequential_time / parallel_time if parallel_time > 0 else 0
        
        return {
            'sequential_ms': sequential_time,
            'parallel_ms': parallel_time,
            'speedup': speedup,
            'efficiency': speedup / 4 * 100  # 4 workers
        }
    
    async def benchmark_health_checks(self) -> Dict[str, Any]:
        """Benchmark health check system"""
        print("\n🏥 Benchmarking Health Checks...")
        
        times = []
        
        for i in range(5):
            elapsed, health = await self.measure_async_time(
                self.deployment.run_health_checks
            )
            times.append(elapsed)
        
        return {
            'iterations': 5,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times)
        }
    
    def benchmark_api_endpoints(self) -> Dict[str, Any]:
        """Benchmark API endpoint response times (simulated)"""
        print("\n🌐 Benchmarking API Endpoints...")
        
        # Simulate API endpoint timings
        endpoints = {
            '/health': [random.uniform(5, 15) for _ in range(10)],
            '/api/interface/generate': [random.uniform(150, 350) for _ in range(10)],
            '/api/patterns/analyze': [random.uniform(50, 150) for _ in range(10)],
            '/api/feedback/collect': [random.uniform(20, 50) for _ in range(10)],
            '/api/performance/metrics': [random.uniform(10, 30) for _ in range(10)]
        }
        
        results = {}
        for endpoint, times in endpoints.items():
            results[endpoint] = {
                'min_ms': min(times),
                'max_ms': max(times),
                'mean_ms': statistics.mean(times),
                'median_ms': statistics.median(times)
            }
        
        return results
    
    async def run_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks"""
        
        print("""
╔════════════════════════════════════════════════════════════════════╗
║        ⚡ PERFORMANCE BENCHMARKING SUITE                            ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        
        # Run benchmarks
        self.results['benchmarks']['interface_generation'] = self.benchmark_interface_generation()
        self.results['benchmarks']['pattern_analysis'] = self.benchmark_pattern_analysis()
        self.results['benchmarks']['database'] = self.benchmark_database_operations()
        self.results['benchmarks']['cache'] = await self.benchmark_cache_performance()
        self.results['benchmarks']['parallel'] = await self.benchmark_parallel_execution()
        self.results['benchmarks']['health_checks'] = await self.benchmark_health_checks()
        self.results['benchmarks']['api_endpoints'] = self.benchmark_api_endpoints()
        
        # Calculate summary
        self.calculate_summary()
        
        # Print results
        self.print_results()
        
        # Save results
        report_path = Path("performance_benchmark_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")
        
        return self.results
    
    def calculate_summary(self):
        """Calculate performance summary"""
        
        # Check against target thresholds
        targets = {
            'interface_generation_ms': 300,
            'pattern_analysis_ms': 100,
            'db_insert_ms': 10,
            'db_select_ms': 5,
            'cache_get_ms': 1,
            'health_check_ms': 500
        }
        
        actual = {
            'interface_generation_ms': self.results['benchmarks']['interface_generation']['mean_ms'],
            'pattern_analysis_ms': self.results['benchmarks']['pattern_analysis']['mean_ms'],
            'db_insert_ms': self.results['benchmarks']['database']['insert']['mean_ms'],
            'db_select_ms': self.results['benchmarks']['database']['select']['mean_ms'],
            'cache_get_ms': self.results['benchmarks']['cache']['get_hit']['mean_ms'],
            'health_check_ms': self.results['benchmarks']['health_checks']['mean_ms']
        }
        
        self.results['summary'] = {
            'targets': targets,
            'actual': actual,
            'performance_score': 0,
            'meets_targets': {}
        }
        
        # Calculate performance score
        total_score = 0
        for metric, target in targets.items():
            actual_value = actual[metric]
            if actual_value <= target:
                score = 100
                meets = True
            else:
                score = max(0, 100 * (target / actual_value))
                meets = False
            
            self.results['summary']['meets_targets'][metric] = meets
            total_score += score
        
        self.results['summary']['performance_score'] = total_score / len(targets)
    
    def print_results(self):
        """Print benchmark results"""
        
        print("\n" + "=" * 70)
        print("BENCHMARK RESULTS")
        print("=" * 70)
        
        # Interface Generation
        ig = self.results['benchmarks']['interface_generation']
        print(f"\n📝 Interface Generation:")
        print(f"   Mean: {ig['mean_ms']:.2f}ms")
        print(f"   Median: {ig['median_ms']:.2f}ms")
        print(f"   Min/Max: {ig['min_ms']:.2f}ms / {ig['max_ms']:.2f}ms")
        print(f"   Cache Hit Rate: {ig['cache_hit_rate']:.1f}%")
        
        # Pattern Analysis
        pa = self.results['benchmarks']['pattern_analysis']
        print(f"\n📊 Pattern Analysis:")
        print(f"   Mean: {pa['mean_ms']:.2f}ms")
        print(f"   Median: {pa['median_ms']:.2f}ms")
        print(f"   Min/Max: {pa['min_ms']:.2f}ms / {pa['max_ms']:.2f}ms")
        
        # Database
        db = self.results['benchmarks']['database']
        print(f"\n🗄️ Database Operations:")
        print(f"   Insert Mean: {db['insert']['mean_ms']:.2f}ms")
        print(f"   Select Mean: {db['select']['mean_ms']:.2f}ms")
        
        # Cache
        cache = self.results['benchmarks']['cache']
        print(f"\n💾 Cache Performance:")
        print(f"   Set Mean: {cache['set']['mean_ms']:.2f}ms")
        print(f"   Get Hit Mean: {cache['get_hit']['mean_ms']:.2f}ms")
        print(f"   Get Miss Mean: {cache['get_miss']['mean_ms']:.2f}ms")
        print(f"   Hit Rate: {cache['cache_stats']['hit_rate']*100:.1f}%")
        
        # Parallel Execution
        parallel = self.results['benchmarks']['parallel']
        print(f"\n🔀 Parallel Execution:")
        print(f"   Sequential: {parallel['sequential_ms']:.2f}ms")
        print(f"   Parallel: {parallel['parallel_ms']:.2f}ms")
        print(f"   Speedup: {parallel['speedup']:.2f}x")
        print(f"   Efficiency: {parallel['efficiency']:.1f}%")
        
        # Summary
        summary = self.results['summary']
        print(f"\n" + "=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"Overall Performance Score: {summary['performance_score']:.1f}/100")
        
        print("\nTarget Compliance:")
        for metric, meets in summary['meets_targets'].items():
            target = summary['targets'][metric]
            actual = summary['actual'][metric]
            status = "✅" if meets else "❌"
            print(f"   {status} {metric}: {actual:.2f}ms (target: {target}ms)")
        
        # Final verdict
        if summary['performance_score'] >= 90:
            print("\n✅ EXCELLENT PERFORMANCE!")
            print("System exceeds performance targets.")
        elif summary['performance_score'] >= 70:
            print("\n✅ GOOD PERFORMANCE")
            print("System meets most performance targets.")
        elif summary['performance_score'] >= 50:
            print("\n⚠️  ACCEPTABLE PERFORMANCE")
            print("Some optimization recommended.")
        else:
            print("\n❌ POOR PERFORMANCE")
            print("Significant optimization required.")


async def main():
    """Run performance benchmarks"""
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_benchmarks()
    
    # Return exit code based on performance
    if results['summary']['performance_score'] >= 70:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)