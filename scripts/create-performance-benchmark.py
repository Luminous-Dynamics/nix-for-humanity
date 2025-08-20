#!/usr/bin/env python3
"""Create comprehensive performance benchmarks for Nix for Humanity."""

import time
import json
import subprocess
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class PerformanceBenchmark:
    """Benchmark native Python-Nix API vs subprocess operations."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "0.8.3",
            "environment": self._get_environment(),
            "benchmarks": {},
            "summary": {}
        }
    
    def _get_environment(self) -> Dict:
        """Get system environment information."""
        import platform
        return {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "nixos_version": self._get_nixos_version()
        }
    
    def _get_nixos_version(self) -> str:
        """Get NixOS version."""
        try:
            result = subprocess.run(
                ["nixos-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception:
            return "Unknown"
    
    def benchmark_operation(self, name: str, func, iterations: int = 10) -> Dict:
        """Benchmark a single operation."""
        times = []
        errors = 0
        
        # Warmup
        try:
            func()
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        # Actual benchmark
        for _ in range(iterations):
            try:
                start = time.perf_counter()
                func()
                end = time.perf_counter()
                times.append(end - start)
            except Exception as e:
                errors += 1
                print(f"Error in {name}: {e}")
        
        if times:
            return {
                "iterations": iterations,
                "errors": errors,
                "min_time": min(times),
                "max_time": max(times),
                "avg_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "stddev": statistics.stdev(times) if len(times) > 1 else 0,
                "times": times
            }
        else:
            return {"error": "All iterations failed", "errors": errors}
    
    def benchmark_native_api(self):
        """Benchmark native Python-Nix API operations."""
        print("🚀 Benchmarking Native Python-Nix API...")
        
        # Try to import native backend
        try:
            import sys
            sys.path.insert(0, '/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src')
            from luminous_nix.nix.native_backend import NativeNixBackend
            
            backend = NativeNixBackend()
            
            # Benchmark operations
            operations = {
                "list_generations": lambda: backend._get_generations(),
                "get_system_info": lambda: backend.get_metrics(),
                "check_nixos_version": lambda: backend._get_nixos_version(),
                "validate_simple": lambda: backend.validate_operation("search", {"query": "firefox"}),
            }
            
            results = {}
            for op_name, op_func in operations.items():
                print(f"  - Benchmarking {op_name}...")
                results[op_name] = self.benchmark_operation(op_name, op_func)
            
            self.results["benchmarks"]["native_api"] = results
            
        except ImportError as e:
            print(f"  ❌ Could not import native backend: {e}")
            self.results["benchmarks"]["native_api"] = {"error": str(e)}
    
    def benchmark_subprocess(self):
        """Benchmark subprocess-based operations."""
        print("🐌 Benchmarking Subprocess Operations...")
        
        operations = {
            "list_generations_subprocess": lambda: subprocess.run(
                ["nix-env", "--list-generations"],
                capture_output=True,
                timeout=10
            ),
            "nixos_version_subprocess": lambda: subprocess.run(
                ["nixos-version"],
                capture_output=True,
                timeout=5
            ),
            "nix_search_subprocess": lambda: subprocess.run(
                ["nix", "search", "nixpkgs", "firefox", "--json"],
                capture_output=True,
                timeout=30
            ),
        }
        
        results = {}
        for op_name, op_func in operations.items():
            print(f"  - Benchmarking {op_name}...")
            results[op_name] = self.benchmark_operation(op_name, op_func, iterations=5)
        
        self.results["benchmarks"]["subprocess"] = results
    
    def benchmark_nlp_operations(self):
        """Benchmark NLP processing speed."""
        print("🧠 Benchmarking NLP Operations...")
        
        try:
            import sys
            sys.path.insert(0, '/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src')
            from luminous_nix.ai.nlp import NLPEngine
            
            nlp = NLPEngine()
            
            test_phrases = [
                "install firefox",
                "search for text editors",
                "update my system",
                "show me all generations",
                "what packages do I have installed?",
                "create a python development environment with numpy and pandas",
            ]
            
            results = {}
            for phrase in test_phrases:
                op_name = f"nlp_{phrase.replace(' ', '_')[:20]}"
                results[op_name] = self.benchmark_operation(
                    op_name,
                    lambda p=phrase: nlp.process(p),
                    iterations=20
                )
            
            self.results["benchmarks"]["nlp"] = results
            
        except Exception as e:
            print(f"  ❌ NLP benchmark failed: {e}")
            self.results["benchmarks"]["nlp"] = {"error": str(e)}
    
    def calculate_speedups(self):
        """Calculate speedup factors between native and subprocess."""
        print("\n📊 Calculating Speedups...")
        
        speedups = {}
        
        # Compare native vs subprocess for similar operations
        comparisons = [
            ("native_api.list_generations", "subprocess.list_generations_subprocess"),
            ("native_api.check_nixos_version", "subprocess.nixos_version_subprocess"),
        ]
        
        for native_key, subprocess_key in comparisons:
            try:
                native_parts = native_key.split('.')
                subprocess_parts = subprocess_key.split('.')
                
                native_time = self.results["benchmarks"][native_parts[0]][native_parts[1]]["avg_time"]
                subprocess_time = self.results["benchmarks"][subprocess_parts[0]][subprocess_parts[1]]["avg_time"]
                
                speedup = subprocess_time / native_time
                speedups[f"{native_parts[1]}_speedup"] = {
                    "native_time": native_time,
                    "subprocess_time": subprocess_time,
                    "speedup_factor": speedup,
                    "speedup_formatted": f"{speedup:.1f}x"
                }
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        
        self.results["summary"]["speedups"] = speedups
    
    def generate_report(self):
        """Generate performance report."""
        print("\n📝 Generating Report...")
        
        # Calculate summary statistics
        all_native_times = []
        all_subprocess_times = []
        
        if "native_api" in self.results["benchmarks"]:
            for op, data in self.results["benchmarks"]["native_api"].items():
                if "avg_time" in data:
                    all_native_times.append(data["avg_time"])
        
        if "subprocess" in self.results["benchmarks"]:
            for op, data in self.results["benchmarks"]["subprocess"].items():
                if "avg_time" in data:
                    all_subprocess_times.append(data["avg_time"])
        
        if all_native_times and all_subprocess_times:
            self.results["summary"]["native_avg"] = statistics.mean(all_native_times)
            self.results["summary"]["subprocess_avg"] = statistics.mean(all_subprocess_times)
            self.results["summary"]["overall_speedup"] = (
                self.results["summary"]["subprocess_avg"] / 
                self.results["summary"]["native_avg"]
            )
        
        # Save JSON report
        with open('metrics/performance_benchmark.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate markdown report
        self._generate_markdown_report()
    
    def _generate_markdown_report(self):
        """Generate human-readable markdown report."""
        report = f"""# Performance Benchmark Report

Generated: {self.results['timestamp']}
Version: {self.results['version']}

## Executive Summary

"""
        
        # Add speedup summary
        if "speedups" in self.results["summary"]:
            report += "### 🚀 Performance Improvements\n\n"
            for op, data in self.results["summary"]["speedups"].items():
                report += f"- **{op.replace('_speedup', '')}**: {data['speedup_formatted']} faster\n"
                report += f"  - Native: {data['native_time']*1000:.2f}ms\n"
                report += f"  - Subprocess: {data['subprocess_time']*1000:.2f}ms\n\n"
        
        # Add detailed benchmarks
        report += "\n## Detailed Benchmarks\n\n"
        
        for category, benchmarks in self.results["benchmarks"].items():
            report += f"### {category.replace('_', ' ').title()}\n\n"
            
            if isinstance(benchmarks, dict) and "error" not in benchmarks:
                report += "| Operation | Avg Time | Min | Max | Median |\n"
                report += "|-----------|----------|-----|-----|--------|\n"
                
                for op, data in benchmarks.items():
                    if "avg_time" in data:
                        report += f"| {op} | {data['avg_time']*1000:.2f}ms | "
                        report += f"{data['min_time']*1000:.2f}ms | "
                        report += f"{data['max_time']*1000:.2f}ms | "
                        report += f"{data['median_time']*1000:.2f}ms |\n"
                
                report += "\n"
        
        # Add performance validation
        report += "\n## Performance Validation\n\n"
        
        validations = []
        
        # Check <0.1s claim for native operations
        native_under_100ms = True
        if "native_api" in self.results["benchmarks"]:
            for op, data in self.results["benchmarks"]["native_api"].items():
                if "avg_time" in data and data["avg_time"] > 0.1:
                    native_under_100ms = False
                    break
        
        validations.append(f"✅ Native operations <0.1s: {'YES' if native_under_100ms else 'NO'}")
        
        # Check 10x speedup claim
        if "overall_speedup" in self.results["summary"]:
            speedup = self.results["summary"]["overall_speedup"]
            validations.append(f"✅ 10x+ speedup achieved: {'YES' if speedup >= 10 else 'NO'} ({speedup:.1f}x)")
        
        report += "\n".join(validations)
        
        # Save report
        with open('docs/status/PERFORMANCE_VALIDATION_REPORT.md', 'w') as f:
            f.write(report)
        
        print(f"✅ Report saved to docs/status/PERFORMANCE_VALIDATION_REPORT.md")
    
    def run(self):
        """Run all benchmarks."""
        print("🏃 Starting Performance Benchmarks...\n")
        
        # Create metrics directory if needed
        Path('metrics').mkdir(exist_ok=True)
        
        # Run benchmarks
        self.benchmark_native_api()
        self.benchmark_subprocess()
        self.benchmark_nlp_operations()
        
        # Calculate speedups
        self.calculate_speedups()
        
        # Generate report
        self.generate_report()
        
        print("\n✅ Benchmarks complete!")
        
        # Print summary
        if "speedups" in self.results["summary"]:
            print("\n🎯 Key Results:")
            for op, data in self.results["summary"]["speedups"].items():
                print(f"  - {op.replace('_speedup', '')}: {data['speedup_formatted']} faster")

if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    benchmark.run()