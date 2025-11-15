#!/usr/bin/env python3
"""
Performance Profiler for Luminous Nix Intelligence System
Identifies bottlenecks and optimization opportunities
"""

import cProfile
import io
import json
import pstats
import statistics
import threading
import time
import tracemalloc
from collections.abc import Callable
from contextlib import contextmanager

from src.luminous_nix.core.intelligent_system import (
    LuminousNixIntelligence,
)


class PerformanceProfiler:
    """Comprehensive performance profiling system"""

    def __init__(self):
        self.timings = {}
        self.memory_usage = {}
        self.cpu_profiles = {}
        self.bottlenecks = []

    @contextmanager
    def profile_section(self, name: str):
        """Context manager for profiling code sections"""
        # Start timing
        start_time = time.perf_counter()

        # Start memory tracking
        tracemalloc.start()
        start_snapshot = tracemalloc.take_snapshot()

        try:
            yield
        finally:
            # End timing
            elapsed = (time.perf_counter() - start_time) * 1000

            # End memory tracking
            end_snapshot = tracemalloc.take_snapshot()
            top_stats = end_snapshot.compare_to(start_snapshot, "lineno")

            # Calculate memory usage
            total_memory = sum(stat.size_diff for stat in top_stats) / 1024 / 1024  # MB

            # Store results
            if name not in self.timings:
                self.timings[name] = []
            self.timings[name].append(elapsed)

            if name not in self.memory_usage:
                self.memory_usage[name] = []
            self.memory_usage[name].append(total_memory)

            tracemalloc.stop()

    def profile_function(self, func: Callable, *args, **kwargs):
        """Profile a specific function call"""
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # Store profile
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(10)

        func_name = func.__name__
        self.cpu_profiles[func_name] = s.getvalue()

        return result

    def analyze_bottlenecks(self):
        """Identify performance bottlenecks"""
        self.bottlenecks = []

        # Analyze timing bottlenecks
        for name, times in self.timings.items():
            avg_time = statistics.mean(times)
            max_time = max(times)

            if avg_time > 100:  # Over 100ms average
                self.bottlenecks.append(
                    {
                        "type": "timing",
                        "name": name,
                        "severity": "high" if avg_time > 500 else "medium",
                        "avg_ms": avg_time,
                        "max_ms": max_time,
                        "recommendation": self._get_timing_recommendation(
                            name, avg_time
                        ),
                    }
                )

        # Analyze memory bottlenecks
        for name, memory in self.memory_usage.items():
            avg_memory = statistics.mean(memory) if memory else 0
            max_memory = max(memory) if memory else 0

            if avg_memory > 10:  # Over 10MB
                self.bottlenecks.append(
                    {
                        "type": "memory",
                        "name": name,
                        "severity": "high" if avg_memory > 50 else "medium",
                        "avg_mb": avg_memory,
                        "max_mb": max_memory,
                        "recommendation": self._get_memory_recommendation(
                            name, avg_memory
                        ),
                    }
                )

        return self.bottlenecks

    def _get_timing_recommendation(self, name: str, avg_time: float) -> str:
        """Get optimization recommendation for timing issues"""
        recommendations = {
            "semantic_understanding": "Consider caching parsed intents",
            "database_write": "Batch writes or use async operations",
            "network_call": "Implement connection pooling",
            "ml_prediction": "Use simpler model or GPU acceleration",
            "cache_lookup": "Optimize data structure (use dict/set)",
            "file_io": "Use memory mapping or async I/O",
        }

        for key, rec in recommendations.items():
            if key in name.lower():
                return rec

        return "Profile deeper to identify specific cause"

    def _get_memory_recommendation(self, name: str, avg_memory: float) -> str:
        """Get optimization recommendation for memory issues"""
        if avg_memory > 100:
            return "Critical: Implement streaming or pagination"
        elif avg_memory > 50:
            return "High: Use generators instead of lists"
        elif avg_memory > 20:
            return "Medium: Consider object pooling"
        else:
            return "Low: Review data structures for efficiency"

    def generate_report(self) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append("🔬 PERFORMANCE PROFILE REPORT")
        report.append("=" * 70)

        # Timing Analysis
        report.append("\n⏱️ TIMING ANALYSIS")
        report.append("-" * 40)

        for name, times in sorted(
            self.timings.items(), key=lambda x: statistics.mean(x[1]), reverse=True
        ):
            avg = statistics.mean(times)
            std = statistics.stdev(times) if len(times) > 1 else 0
            report.append(f"{name:30} | Avg: {avg:7.2f}ms ± {std:5.2f}ms")

        # Memory Analysis
        report.append("\n💾 MEMORY ANALYSIS")
        report.append("-" * 40)

        for name, memory in sorted(
            self.memory_usage.items(),
            key=lambda x: statistics.mean(x[1]) if x[1] else 0,
            reverse=True,
        ):
            if memory:
                avg = statistics.mean(memory)
                max_mem = max(memory)
                report.append(f"{name:30} | Avg: {avg:7.2f}MB  Max: {max_mem:7.2f}MB")

        # Bottlenecks
        report.append("\n🚨 IDENTIFIED BOTTLENECKS")
        report.append("-" * 40)

        self.analyze_bottlenecks()
        if self.bottlenecks:
            for bottleneck in sorted(
                self.bottlenecks,
                key=lambda x: x.get("avg_ms", x.get("avg_mb", 0)),
                reverse=True,
            ):
                severity_icon = "🔴" if bottleneck["severity"] == "high" else "🟡"
                report.append(f"{severity_icon} {bottleneck['name']}")

                if bottleneck["type"] == "timing":
                    report.append(
                        f"   Time: {bottleneck['avg_ms']:.1f}ms avg, {bottleneck['max_ms']:.1f}ms max"
                    )
                else:
                    report.append(
                        f"   Memory: {bottleneck['avg_mb']:.1f}MB avg, {bottleneck['max_mb']:.1f}MB max"
                    )

                report.append(f"   Fix: {bottleneck['recommendation']}")
        else:
            report.append("✅ No significant bottlenecks detected!")

        # CPU Profiles
        if self.cpu_profiles:
            report.append("\n🖥️ CPU PROFILES")
            report.append("-" * 40)

            for func_name, profile in self.cpu_profiles.items():
                report.append(f"\n{func_name}:")
                # Show only top 5 lines of profile
                lines = profile.split("\n")[:8]
                for line in lines:
                    if line.strip():
                        report.append(f"  {line}")

        return "\n".join(report)


def profile_core_operations():
    """Profile core system operations"""
    print("🚀 Starting Performance Profiling")
    print("=" * 70)

    profiler = PerformanceProfiler()

    # Initialize system once
    print("\n📦 Initializing system...")
    with profiler.profile_section("system_initialization"):
        intelligence = LuminousNixIntelligence()

    # Test queries for profiling
    test_queries = [
        "firefox",
        "install web browser",
        "python development environment",
        "text editor for programming",
        "docker containers",
        "system monitoring tools",
    ]

    print("\n🔍 Profiling search operations...")

    # Profile individual components
    for query in test_queries:
        # 1. Semantic understanding
        with profiler.profile_section("semantic_understanding"):
            intent = intelligence.semantic.understand(query)

        # 2. Cache lookup
        with profiler.profile_section("cache_lookup"):
            cache_results, cache_time, source = intelligence.base_cache.search_hybrid(
                query
            )

        # 3. Analytics tracking
        with profiler.profile_section("analytics_tracking"):
            from src.luminous_nix.analytics.usage_analytics_improved import UsageEvent

            event = UsageEvent(
                timestamp=time.time(),
                event_type="search",
                query=query,
                result_count=len(cache_results) if cache_results else 0,
                response_time_ms=10.0,
                cache_hit=True,
                source=source,
            )
            intelligence.analytics.track_event(event)

        # 4. ML prediction
        with profiler.profile_section("ml_prediction"):
            predictions = intelligence.predictor.predict_next(query)

        # 5. Network check (if enabled)
        with profiler.profile_section("network_check"):
            # Check if method exists
            if hasattr(intelligence.collaborative, "search_network"):
                network_results = intelligence.collaborative.search_network(query)
            else:
                # Use the search method that exists
                network_results = (
                    intelligence.collaborative.search(query)
                    if hasattr(intelligence.collaborative, "search")
                    else []
                )

        # 6. Full integrated search
        with profiler.profile_section("integrated_search"):
            response = intelligence.intelligent_search(query, use_all_features=True)

    # Profile concurrent operations
    print("\n💪 Profiling concurrent operations...")

    def concurrent_search(thread_id: int):
        """Simulate concurrent searches"""
        for i in range(10):
            query = f"test_query_{thread_id}_{i}"
            intelligence.intelligent_search(query, use_all_features=False)

    with profiler.profile_section("concurrent_operations"):
        threads = []
        for i in range(5):
            t = threading.Thread(target=concurrent_search, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    # Profile memory-intensive operations
    print("\n💾 Profiling memory usage...")

    with profiler.profile_section("large_result_set"):
        # Simulate large result set
        large_query = "a" * 1000  # Very long query
        response = intelligence.intelligent_search(large_query)

    with profiler.profile_section("batch_analytics"):
        # Simulate batch analytics
        insights = intelligence.analytics.get_insights()
        recommendations = intelligence.analytics.get_smart_cache_recommendations(
            limit=100
        )

    # Clean shutdown
    intelligence.shutdown()

    # Generate and print report
    print("\n" + profiler.generate_report())

    # Save detailed results
    results = {
        "timings": {
            k: {"avg": statistics.mean(v), "max": max(v), "count": len(v)}
            for k, v in profiler.timings.items()
        },
        "memory": {
            k: {"avg": statistics.mean(v) if v else 0, "max": max(v) if v else 0}
            for k, v in profiler.memory_usage.items()
        },
        "bottlenecks": profiler.bottlenecks,
    }

    with open("performance_profile.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n📊 Detailed results saved to performance_profile.json")

    return profiler


def profile_specific_bottleneck(component: str):
    """Deep profile a specific component"""
    print(f"\n🔬 Deep Profiling: {component}")
    print("=" * 70)

    intelligence = LuminousNixIntelligence()
    profiler = PerformanceProfiler()

    if component == "semantic":
        # Profile semantic understanding in detail
        test_queries = [
            "vim",
            "neovim",
            "emacs",  # Simple
            "text editor for python",
            "IDE for web development",  # Complex
            "instal fierrfox",
            "pythn developmnt",  # Typos
        ]

        for query in test_queries:
            result = profiler.profile_function(intelligence.semantic.understand, query)
            print(f"  '{query}' → Category: {result.category}")

    elif component == "cache":
        # Profile cache operations
        for i in range(100):
            query = f"test_cache_{i % 10}"  # Create some repetition
            result = profiler.profile_function(
                intelligence.base_cache.search_hybrid, query
            )

    elif component == "analytics":
        # Profile analytics operations
        from src.luminous_nix.analytics.usage_analytics_improved import UsageEvent

        events = []
        for i in range(1000):
            events.append(
                UsageEvent(
                    timestamp=time.time(),
                    event_type="search",
                    query=f"query_{i}",
                    result_count=10,
                    response_time_ms=15.0,
                    cache_hit=(i % 3 == 0),
                    source="test",
                )
            )

        for event in events:
            profiler.profile_function(intelligence.analytics.track_event, event)

    intelligence.shutdown()

    # Show CPU profile for the component
    for func_name, profile in profiler.cpu_profiles.items():
        print(f"\n📊 CPU Profile for {func_name}:")
        print(profile)

    return profiler


def main():
    """Run comprehensive performance profiling"""
    print("🔬 Luminous Nix Performance Profiler")
    print("=" * 70)
    print("Identifying bottlenecks and optimization opportunities\n")

    # Run core profiling
    core_profiler = profile_core_operations()

    # If bottlenecks found, deep profile them
    if core_profiler.bottlenecks:
        print("\n🔍 Deep profiling identified bottlenecks...")

        for bottleneck in core_profiler.bottlenecks[:3]:  # Top 3
            if "semantic" in bottleneck["name"].lower():
                profile_specific_bottleneck("semantic")
            elif "cache" in bottleneck["name"].lower():
                profile_specific_bottleneck("cache")
            elif "analytics" in bottleneck["name"].lower():
                profile_specific_bottleneck("analytics")

    print("\n✅ Performance profiling complete!")
    print("\n💡 Key Insights:")

    # Calculate overall stats
    all_timings = []
    for times in core_profiler.timings.values():
        all_timings.extend(times)

    if all_timings:
        print(f"  • Average operation: {statistics.mean(all_timings):.2f}ms")
        print(
            f"  • 95th percentile: {statistics.quantiles(all_timings, n=20)[18]:.2f}ms"
        )
        print(f"  • Max operation: {max(all_timings):.2f}ms")

    if core_profiler.bottlenecks:
        print(f"  • Found {len(core_profiler.bottlenecks)} bottlenecks to optimize")
    else:
        print("  • No significant bottlenecks - system is well optimized!")

    return 0


if __name__ == "__main__":
    exit(main())
