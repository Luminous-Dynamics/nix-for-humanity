#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Performance Benchmarking System - Nix for Humanity

This script provides comprehensive performance benchmarking for all core operations,
helping us achieve and maintain our performance excellence goals.

Sacred Performance Targets:
- Maya (ADHD): <1 second for all operations
- Everyone: <2 seconds for complex operations  
- Native API: <0.1 seconds for most operations
"""

import os
import sys
import time
import json
import statistics
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3

@dataclass
class BenchmarkResult:
    """Single benchmark measurement."""
    operation: str
    duration_ms: float
    memory_mb: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results."""
    timestamp: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: List[BenchmarkResult]
    summary_stats: Dict[str, float]
    performance_grade: str

class PerformanceBenchmark:
    """Comprehensive performance benchmarking system."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.results_dir = self.project_root / ".performance_monitoring"
        self.db_path = self.results_dir / "performance_history.db"
        
        # Ensure directories exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Performance targets (milliseconds)
        self.TARGETS = {
            "maya_target": 1000,      # Maya (ADHD) - must be under 1s
            "general_target": 2000,   # Everyone else - under 2s
            "native_api_target": 100, # Native operations - under 0.1s
            "startup_target": 3000    # Cold startup - under 3s
        }
        
        # Test operations to benchmark
        self.OPERATIONS = {
            "startup": {
                "command": ["python", "-c", "import nix_humanity; print('Ready')"],
                "description": "Cold startup time",
                "target": "startup_target"
            },
            "intent_parsing": {
                "command": ["python", "-c", 
                    "from nix_humanity.nlp import NLPEngine; "
                    "nlp = NLPEngine(); "
                    "result = nlp.parse('install firefox'); "
                    "print(f'Intent: {result.intent}')"],
                "description": "Natural language parsing",
                "target": "general_target"
            },
            "package_search": {
                "command": ["python", "-c",
                    "from nix_humanity.executor import CommandExecutor; "
                    "exec = CommandExecutor(); "
                    "result = exec.search_packages('firefox'); "
                    "print(f'Found: {len(result)} packages')"],
                "description": "Package search operation",
                "target": "general_target"  
            },
            "native_api_generation_list": {
                "command": ["python", "-c",
                    "from nix_humanity.backend.native_api import NativeNixAPI; "
                    "api = NativeNixAPI(); "
                    "gens = api.list_generations(); "
                    "print(f'Generations: {len(gens)}')"],
                "description": "Native API generation listing",
                "target": "native_api_target"
            },
            "help_system": {
                "command": ["python", "-c",
                    "from nix_humanity.cli import CLIAdapter; "
                    "cli = CLIAdapter(); "
                    "help_text = cli.get_help('install'); "
                    "print('Help ready')"],
                "description": "Help system response",
                "target": "general_target"
            }
        }
    
    def _init_database(self):
        """Initialize SQLite database for performance tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    memory_mb REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    target_ms INTEGER NOT NULL,
                    performance_ratio REAL NOT NULL,
                    git_commit TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    regression_percent REAL NOT NULL,
                    current_ms REAL NOT NULL,
                    previous_ms REAL NOT NULL,
                    severity TEXT NOT NULL
                )
            """)
    
    def benchmark_operation(self, operation_name: str, warmup_runs: int = 2, 
                          measurement_runs: int = 5) -> BenchmarkResult:
        """Benchmark a single operation with multiple runs."""
        if operation_name not in self.OPERATIONS:
            return BenchmarkResult(
                operation=operation_name,
                duration_ms=0,
                memory_mb=0,
                success=False,
                error=f"Unknown operation: {operation_name}"
            )
        
        op_config = self.OPERATIONS[operation_name]
        command = op_config["command"]
        
        print(f"🔍 Benchmarking: {op_config['description']}")
        
        # Warmup runs
        for i in range(warmup_runs):
            try:
                subprocess.run(command, capture_output=True, cwd=self.project_root, timeout=10)
            except Exception:
                pass  # Ignore warmup failures
        
        # Measurement runs
        durations = []
        memory_usage = []
        errors = []
        
        for i in range(measurement_runs):
            try:
                # Measure memory before
                import psutil
                process = psutil.Process()
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
                
                # Time the operation
                start_time = time.perf_counter()
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True,
                    cwd=self.project_root,
                    timeout=15
                )
                end_time = time.perf_counter()
                
                # Measure memory after
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                
                duration_ms = (end_time - start_time) * 1000
                memory_delta = max(0, mem_after - mem_before)
                
                if result.returncode == 0:
                    durations.append(duration_ms)
                    memory_usage.append(memory_delta)
                else:
                    errors.append(result.stderr or "Command failed")
                    
            except subprocess.TimeoutExpired:
                errors.append("Operation timed out")
            except Exception as e:
                errors.append(str(e))
        
        # Calculate results
        if durations:
            avg_duration = statistics.mean(durations)
            avg_memory = statistics.mean(memory_usage) if memory_usage else 0
            success = True
            error = None
        else:
            avg_duration = float('inf')
            avg_memory = 0
            success = False
            error = "; ".join(errors) if errors else "All runs failed"
        
        return BenchmarkResult(
            operation=operation_name,
            duration_ms=avg_duration,
            memory_mb=avg_memory,
            success=success,
            error=error,
            metadata={
                "runs": len(durations),
                "target_ms": self.TARGETS[op_config["target"]],
                "description": op_config["description"],
                "raw_durations": durations
            }
        )
    
    def run_full_benchmark_suite(self) -> BenchmarkSuite:
        """Run complete benchmark suite for all operations."""
        print("🚀 Starting Performance Benchmark Suite")
        print("=" * 60)
        
        timestamp = datetime.now().isoformat()
        results = []
        
        for operation_name in self.OPERATIONS.keys():
            result = self.benchmark_operation(operation_name)
            results.append(result)
            
            # Show immediate feedback
            if result.success:
                target = result.metadata["target_ms"]
                status = "✅" if result.duration_ms <= target else "⚠️"
                print(f"{status} {operation_name}: {result.duration_ms:.1f}ms (target: {target}ms)")
            else:
                print(f"❌ {operation_name}: FAILED - {result.error}")
        
        # Calculate summary statistics
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        if successful_results:
            durations = [r.duration_ms for r in successful_results]
            summary_stats = {
                "mean_duration": statistics.mean(durations),
                "median_duration": statistics.median(durations),
                "max_duration": max(durations),
                "min_duration": min(durations),
                "std_deviation": statistics.stdev(durations) if len(durations) > 1 else 0
            }
        else:
            summary_stats = {
                "mean_duration": 0,
                "median_duration": 0,
                "max_duration": 0, 
                "min_duration": 0,
                "std_deviation": 0
            }
        
        # Calculate performance grade
        grade = self._calculate_performance_grade(results)
        
        suite = BenchmarkSuite(
            timestamp=timestamp,
            total_operations=len(results),
            successful_operations=len(successful_results),
            failed_operations=len(failed_results),
            results=results,
            summary_stats=summary_stats,
            performance_grade=grade
        )
        
        # Store results in database
        self._store_benchmark_results(suite)
        
        return suite
    
    def _calculate_performance_grade(self, results: List[BenchmarkResult]) -> str:
        """Calculate overall performance grade."""
        if not results:
            return "F"
        
        successful_results = [r for r in results if r.success]
        if not successful_results:
            return "F"
        
        # Check how many operations meet their targets
        targets_met = 0
        maya_compliant = 0
        
        for result in successful_results:
            target = result.metadata["target_ms"]
            if result.duration_ms <= target:
                targets_met += 1
            
            # Check Maya compliance (all operations under 1s)
            if result.duration_ms <= self.TARGETS["maya_target"]:
                maya_compliant += 1
        
        success_rate = targets_met / len(successful_results)
        maya_rate = maya_compliant / len(successful_results)
        
        # Grade based on performance
        if success_rate >= 0.95 and maya_rate >= 0.90:
            return "A+"
        elif success_rate >= 0.90 and maya_rate >= 0.80:
            return "A"
        elif success_rate >= 0.80:
            return "B"
        elif success_rate >= 0.70:
            return "C"
        elif success_rate >= 0.60:
            return "D"
        else:
            return "F"
    
    def _store_benchmark_results(self, suite: BenchmarkSuite):
        """Store benchmark results in database."""
        with sqlite3.connect(self.db_path) as conn:
            for result in suite.results:
                if result.success:
                    target = result.metadata["target_ms"]
                    performance_ratio = result.duration_ms / target
                    
                    conn.execute("""
                        INSERT INTO benchmark_history 
                        (timestamp, operation, duration_ms, memory_mb, success, 
                         target_ms, performance_ratio, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        suite.timestamp,
                        result.operation,
                        result.duration_ms,
                        result.memory_mb,
                        result.success,
                        target,
                        performance_ratio,
                        json.dumps(result.metadata)
                    ))
    
    def print_detailed_report(self, suite: BenchmarkSuite):
        """Print detailed performance report."""
        print(f"\n🎯 PERFORMANCE BENCHMARK REPORT")
        print("=" * 60)
        print(f"📅 Timestamp: {suite.timestamp}")
        print(f"📊 Overall Grade: {suite.performance_grade}")
        print(f"✅ Successful: {suite.successful_operations}/{suite.total_operations}")
        
        if suite.failed_operations > 0:
            print(f"❌ Failed: {suite.failed_operations}")
        
        print(f"\n📈 Summary Statistics")
        print("-" * 30)
        stats = suite.summary_stats
        print(f"Mean Duration: {stats['mean_duration']:.1f}ms")
        print(f"Median Duration: {stats['median_duration']:.1f}ms")
        print(f"Max Duration: {stats['max_duration']:.1f}ms")
        print(f"Min Duration: {stats['min_duration']:.1f}ms")
        
        print(f"\n🎭 Persona Compliance")
        print("-" * 30)
        maya_compliant = sum(1 for r in suite.results 
                           if r.success and r.duration_ms <= self.TARGETS["maya_target"])
        maya_rate = maya_compliant / suite.successful_operations if suite.successful_operations > 0 else 0
        print(f"Maya (ADHD) <1s: {maya_compliant}/{suite.successful_operations} ({maya_rate:.1%})")
        
        print(f"\n🔍 Detailed Results")
        print("-" * 30)
        for result in suite.results:
            if result.success:
                target = result.metadata["target_ms"]
                status = "✅" if result.duration_ms <= target else "⚠️"
                ratio = result.duration_ms / target
                print(f"{status} {result.operation:<25} {result.duration_ms:>7.1f}ms "
                      f"(target: {target}ms, ratio: {ratio:.2f}x)")
            else:
                print(f"❌ {result.operation:<25} FAILED: {result.error}")
        
        print(f"\n💡 Recommendations")
        print("-" * 30)
        self._print_recommendations(suite)
    
    def _print_recommendations(self, suite: BenchmarkSuite):
        """Print performance recommendations."""
        recommendations = []
        
        # Analyze results for recommendations
        slow_operations = [r for r in suite.results 
                          if r.success and r.duration_ms > r.metadata["target_ms"]]
        
        if slow_operations:
            recommendations.append("🐌 Slow operations detected - consider optimization")
            for op in slow_operations:
                target = op.metadata["target_ms"]
                ratio = op.duration_ms / target
                recommendations.append(f"   • {op.operation}: {ratio:.1f}x slower than target")
        
        # Maya compliance check
        maya_violations = [r for r in suite.results 
                          if r.success and r.duration_ms > self.TARGETS["maya_target"]]
        if maya_violations:
            recommendations.append("⚡ Maya (ADHD) speed violations - critical for accessibility")
            for op in maya_violations:
                recommendations.append(f"   • {op.operation}: {op.duration_ms:.1f}ms (needs <1000ms)")
        
        if suite.performance_grade in ["C", "D", "F"]:
            recommendations.append("🚨 Overall performance needs immediate attention")
            recommendations.append("   • Consider implementing caching layer")
            recommendations.append("   • Profile slow operations for bottlenecks")
            recommendations.append("   • Optimize critical path code")
        
        if not recommendations:
            recommendations.append("🎉 Excellent performance! All targets met")
            recommendations.append("   • Consider tightening targets for even better UX")
        
        for rec in recommendations:
            print(f"   {rec}")

def main():
    """Main entry point for performance benchmarking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Benchmarking for Nix for Humanity")
    parser.add_argument("--project-root", help="Project root directory", default=None)
    parser.add_argument("--operation", help="Benchmark specific operation only")
    parser.add_argument("--runs", type=int, default=5, help="Number of measurement runs")
    parser.add_argument("--save-report", action="store_true", help="Save JSON report")
    
    args = parser.parse_args()
    
    # Initialize benchmarker
    benchmark = PerformanceBenchmark(args.project_root)
    
    if args.operation:
        # Single operation benchmark
        result = benchmark.benchmark_operation(args.operation, measurement_runs=args.runs)
        print(f"\n🎯 Single Operation Benchmark: {args.operation}")
        print("=" * 50)
        
        if result.success:
            target = result.metadata["target_ms"]
            status = "✅ PASS" if result.duration_ms <= target else "⚠️ SLOW"
            print(f"{status} Duration: {result.duration_ms:.1f}ms (target: {target}ms)")
            print(f"Memory: {result.memory_mb:.1f}MB")
        else:
            print(f"❌ FAILED: {result.error}")
    else:
        # Full benchmark suite
        suite = benchmark.run_full_benchmark_suite()
        benchmark.print_detailed_report(suite)
        
        if args.save_report:
            report_file = benchmark.results_dir / f"benchmark_{suite.timestamp[:19].replace(':', '-')}.json"
            with open(report_file, 'w') as f:
                json.dump(asdict(suite), f, indent=2, default=str)
            print(f"\n📁 Report saved to: {report_file}")

if __name__ == "__main__":
    main()