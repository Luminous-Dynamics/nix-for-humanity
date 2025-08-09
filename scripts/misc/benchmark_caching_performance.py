#!/usr/bin/env python3
"""
from typing import Dict
Benchmark script to demonstrate caching layer performance improvements

Shows the dramatic speedup achieved by intelligent caching.
"""

import time
import statistics
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from nix_humanity.core.backend import CachedBackend
from nix_humanity.core.backend import EnhancedBackend
from src.nix_for_humanity.core.types import Request, PersonalityStyle
from src.nix_for_humanity.ai.xai_engine import ExplanationLevel


console = Console()


class BenchmarkRunner:
    """Run performance benchmarks comparing cached vs uncached backends"""
    
    def __init__(self):
        # Initialize backends
        config = {
            'personality': PersonalityStyle.FRIENDLY,
            'cache_memory_mb': 50,
            'cache_warming': True
        }
        
        self.cached_backend = CachedBackend(config)
        self.uncached_backend = EnhancedBackend(config)
        
        # Test queries
        self.test_queries = [
            # Simple queries
            "install firefox",
            "update system",
            "list installed packages",
            "search python",
            
            # Complex queries
            "why is my wifi not working?",
            "how do I configure nginx on nixos?",
            "show me all packages related to development",
            
            # Error scenarios
            "install nonexistent-package",
            "build custom-derivation",
            
            # Variations of same intent
            "please install firefox",
            "can you install firefox for me",
            "I need firefox installed",
            
            # System queries
            "what is my disk usage",
            "show system information",
            "check for updates"
        ]
        
        self.personas = ['grandma_rose', 'maya_adhd', 'dr_sarah', 'default']
    
    def run_benchmarks(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        console.print(Panel.fit(
            "[bold cyan]Nix for Humanity - Caching Layer Performance Benchmark[/bold cyan]\n\n"
            "[yellow]Comparing cached vs uncached backend performance[/yellow]",
            border_style="cyan"
        ))
        
        results = {
            'cold_start': self._benchmark_cold_start(),
            'warm_cache': self._benchmark_warm_cache(),
            'xai_performance': self._benchmark_xai_explanations(),
            'cache_efficiency': self._measure_cache_efficiency(),
            'memory_usage': self._measure_memory_usage()
        }
        
        self._display_results(results)
        return results
    
    def _benchmark_cold_start(self) -> Dict[str, float]:
        """Benchmark cold start performance"""
        console.print("\n[cyan]1. Cold Start Performance[/cyan]")
        console.print("Testing first-time query processing...")
        
        times_cached = []
        times_uncached = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running cold start tests...", total=len(self.test_queries))
            
            for i, query in enumerate(self.test_queries):
                request = Request(
                    query=query,
                    context={'benchmark': True, 'run': i}
                )
                
                # Uncached
                start = time.time()
                self.uncached_backend.process(request)
                times_uncached.append(time.time() - start)
                
                # Cached (first run, so cache miss)
                start = time.time()
                self.cached_backend.process(request)
                times_cached.append(time.time() - start)
                
                progress.update(task, advance=1)
        
        return {
            'cached_avg': statistics.mean(times_cached),
            'uncached_avg': statistics.mean(times_uncached),
            'cached_p95': sorted(times_cached)[int(len(times_cached) * 0.95)],
            'uncached_p95': sorted(times_uncached)[int(len(times_uncached) * 0.95)]
        }
    
    def _benchmark_warm_cache(self) -> Dict[str, float]:
        """Benchmark warm cache performance"""
        console.print("\n[cyan]2. Warm Cache Performance[/cyan]")
        console.print("Testing repeated query processing...")
        
        # Warm the cache
        console.print("[dim]Warming cache...[/dim]")
        self.cached_backend.warm_cache(self.test_queries[:5])
        
        times_cached = []
        times_uncached = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running warm cache tests...", total=len(self.test_queries) * 3)
            
            # Run each query 3 times
            for _ in range(3):
                for query in self.test_queries:
                    request = Request(
                        query=query,
                        context={'benchmark': True}
                    )
                    
                    # Cached (should hit cache after first run)
                    start = time.time()
                    self.cached_backend.process(request)
                    times_cached.append(time.time() - start)
                    
                    # Uncached (always processes)
                    start = time.time()
                    self.uncached_backend.process(request)
                    times_uncached.append(time.time() - start)
                    
                    progress.update(task, advance=1)
        
        return {
            'cached_avg': statistics.mean(times_cached),
            'uncached_avg': statistics.mean(times_uncached),
            'speedup': statistics.mean(times_uncached) / statistics.mean(times_cached),
            'cache_hit_rate': self._get_cache_hit_rate()
        }
    
    def _benchmark_xai_explanations(self) -> Dict[str, float]:
        """Benchmark XAI explanation caching"""
        console.print("\n[cyan]3. XAI Explanation Performance[/cyan]")
        console.print("Testing explanation generation with caching...")
        
        # Test intent for XAI
        from src.nix_for_humanity.core.types import Intent, IntentType
        test_intents = [
            Intent(type=IntentType.INSTALL, raw_input="install firefox"),
            Intent(type=IntentType.UPDATE, raw_input="update system"),
            Intent(type=IntentType.SEARCH, raw_input="search python")
        ]
        
        times_cached = []
        times_uncached = []
        
        for intent in test_intents:
            # First run (cache miss)
            start = time.time()
            self.cached_backend.explain(intent)
            first_time = time.time() - start
            
            # Second run (cache hit)
            start = time.time()
            self.cached_backend.explain(intent)
            cached_time = time.time() - start
            
            # Uncached
            start = time.time()
            self.uncached_backend.explain(intent)
            uncached_time = time.time() - start
            
            times_cached.append(cached_time)
            times_uncached.append(uncached_time)
        
        return {
            'cached_avg': statistics.mean(times_cached),
            'uncached_avg': statistics.mean(times_uncached),
            'speedup': statistics.mean(times_uncached) / statistics.mean(times_cached)
        }
    
    def _measure_cache_efficiency(self) -> Dict[str, Any]:
        """Measure overall cache efficiency"""
        console.print("\n[cyan]4. Cache Efficiency Metrics[/cyan]")
        
        stats = self.cached_backend.get_cache_statistics()
        
        return {
            'hit_rate': stats['overall']['hit_rate'],
            'total_hits': stats['overall']['total_hits'],
            'total_misses': stats['overall']['total_misses'],
            'time_saved': stats['overall']['time_saved_seconds'],
            'avg_time_saved_per_hit': stats['overall']['avg_time_saved_ms']
        }
    
    def _measure_memory_usage(self) -> Dict[str, Any]:
        """Measure memory usage of cache"""
        console.print("\n[cyan]5. Memory Usage Analysis[/cyan]")
        
        cache_stats = self.cached_backend.cache_manager.get_statistics()
        
        return {
            'memory_used_mb': cache_stats.get('size_mb', 0),
            'entry_count': cache_stats.get('entry_count', 0),
            'evictions': cache_stats.get('evictions', 0)
        }
    
    def _get_cache_hit_rate(self) -> float:
        """Get current cache hit rate"""
        stats = self.cached_backend.get_cache_statistics()
        return float(stats['overall']['hit_rate'].rstrip('%')) / 100
    
    def _display_results(self, results: Dict[str, Any]) -> None:
        """Display benchmark results in a nice table"""
        console.print("\n[bold green]Benchmark Results[/bold green]")
        
        # Cold start results
        table = Table(title="Cold Start Performance")
        table.add_column("Metric", style="cyan")
        table.add_column("Cached Backend", style="green")
        table.add_column("Uncached Backend", style="yellow")
        table.add_column("Difference", style="magenta")
        
        cold = results['cold_start']
        table.add_row(
            "Average Response Time",
            f"{cold['cached_avg']*1000:.1f}ms",
            f"{cold['uncached_avg']*1000:.1f}ms",
            f"{(cold['uncached_avg']-cold['cached_avg'])*1000:.1f}ms slower"
        )
        table.add_row(
            "95th Percentile",
            f"{cold['cached_p95']*1000:.1f}ms",
            f"{cold['uncached_p95']*1000:.1f}ms",
            f"{(cold['uncached_p95']-cold['cached_p95'])*1000:.1f}ms slower"
        )
        console.print(table)
        
        # Warm cache results
        table = Table(title="Warm Cache Performance")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        warm = results['warm_cache']
        table.add_row("Cached Avg Response", f"{warm['cached_avg']*1000:.1f}ms")
        table.add_row("Uncached Avg Response", f"{warm['uncached_avg']*1000:.1f}ms")
        table.add_row("Speedup Factor", f"{warm['speedup']:.1f}x faster")
        table.add_row("Cache Hit Rate", f"{warm['cache_hit_rate']:.1%}")
        console.print(table)
        
        # XAI performance
        table = Table(title="XAI Explanation Caching")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        xai = results['xai_performance']
        table.add_row("Cached XAI Time", f"{xai['cached_avg']*1000:.1f}ms")
        table.add_row("Uncached XAI Time", f"{xai['uncached_avg']*1000:.1f}ms")
        table.add_row("XAI Speedup", f"{xai['speedup']:.1f}x faster")
        console.print(table)
        
        # Efficiency metrics
        table = Table(title="Cache Efficiency")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        eff = results['cache_efficiency']
        table.add_row("Overall Hit Rate", eff['hit_rate'])
        table.add_row("Total Cache Hits", str(eff['total_hits']))
        table.add_row("Total Time Saved", f"{eff['time_saved']:.1f}s")
        table.add_row("Avg Time Saved/Hit", f"{eff['avg_time_saved_per_hit']:.0f}ms")
        console.print(table)
        
        # Memory usage
        table = Table(title="Memory Usage")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        mem = results['memory_usage']
        table.add_row("Cache Memory Used", f"{mem['memory_used_mb']:.1f}MB")
        table.add_row("Cached Entries", str(mem['entry_count']))
        table.add_row("Evictions", str(mem['evictions']))
        console.print(table)
        
        # Summary
        console.print(Panel(
            f"[bold green]🚀 Performance Summary[/bold green]\n\n"
            f"• Warm cache speedup: [cyan]{warm['speedup']:.1f}x faster[/cyan]\n"
            f"• Cache hit rate: [cyan]{warm['cache_hit_rate']:.1%}[/cyan]\n"
            f"• Total time saved: [cyan]{eff['time_saved']:.1f} seconds[/cyan]\n"
            f"• Average response time: [cyan]{warm['cached_avg']*1000:.1f}ms[/cyan] (cached) vs "
            f"[yellow]{warm['uncached_avg']*1000:.1f}ms[/yellow] (uncached)\n\n"
            f"[dim]The caching layer provides dramatic performance improvements, especially for repeated queries![/dim]",
            border_style="green"
        ))


def main():
    """Run the benchmark"""
    runner = BenchmarkRunner()
    
    try:
        results = runner.run_benchmarks()
        
        # Save results
        import json
        with open('cache_benchmark_results.json', 'w') as f:
            # Convert to serializable format
            serializable_results = {}
            for key, value in results.items():
                if isinstance(value, dict):
                    serializable_results[key] = {
                        k: v if not isinstance(v, float) else round(v, 4)
                        for k, v in value.items()
                    }
                else:
                    serializable_results[key] = value
                    
            json.dump(serializable_results, f, indent=2)
            
        console.print("\n[green]Benchmark complete! Results saved to cache_benchmark_results.json[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Benchmark interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during benchmark: {e}[/red]")
        raise


if __name__ == "__main__":
    main()