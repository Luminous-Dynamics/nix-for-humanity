#!/usr/bin/env python3
"""
from typing import List, Dict
Comprehensive Performance Benchmark Suite for Nix for Humanity
Core Excellence Phase - Performance Mastery Component

Benchmarks all operations to establish baselines and identify optimization targets.
Measures real-world performance across all personas and use cases.
"""

import asyncio
import time
import json
import sqlite3
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import psutil
import sys
import os

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.nix_for_humanity.core.engine import NIXForHumanityEngine
    from src.nix_for_humanity.adapters.cli_adapter import CLIAdapter
    ENGINE_AVAILABLE = True
except ImportError:
    ENGINE_AVAILABLE = False
    print("⚠️ Engine import failed - will use CLI benchmarking only")

class PerformanceBenchmark:
    """Comprehensive performance benchmarking system."""
    
    def __init__(self):
        self.project_root = project_root
        self.results_dir = self.project_root / ".performance_metrics"
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize results database
        self.db_path = self.results_dir / "performance_history.db"
        self.init_database()
        
        # Performance targets (Core Excellence goals)
        self.targets = {
            "startup_time": 3.0,          # seconds - cold start
            "warm_startup": 1.0,          # seconds - warm start
            "simple_command": 2.0,        # seconds - install firefox
            "complex_command": 3.0,       # seconds - search + install
            "feedback_response": 0.1,     # seconds - show something to user
            "memory_idle": 150,           # MB - idle memory usage
            "memory_active": 300,         # MB - active memory usage
            "memory_peak": 500,           # MB - peak memory usage
            "maya_response": 1.0,         # seconds - ADHD persona requirement
            "grandma_response": 2.0,      # seconds - elderly persona requirement
        }
        
        # Benchmark scenarios
        self.scenarios = [
            {
                "name": "startup_cold",
                "description": "Cold startup time from script launch",
                "command": "./bin/ask-nix --version",
                "timeout": 10,
                "target": "startup_time"
            },
            {
                "name": "startup_warm", 
                "description": "Warm startup (second invocation)",
                "command": "./bin/ask-nix --version",
                "timeout": 5,
                "target": "warm_startup"
            },
            {
                "name": "simple_install",
                "description": "Simple package installation",
                "command": "./bin/ask-nix 'install firefox' --dry-run",
                "timeout": 5,
                "target": "simple_command"
            },
            {
                "name": "search_command",
                "description": "Package search operation", 
                "command": "./bin/ask-nix 'search for browsers' --dry-run",
                "timeout": 8,
                "target": "complex_command"
            },
            {
                "name": "help_command",
                "description": "Help system response",
                "command": "./bin/ask-nix 'help'",
                "timeout": 3,
                "target": "feedback_response"
            },
            {
                "name": "typo_correction",
                "description": "Typo correction and learning",
                "command": "./bin/ask-nix 'instal fierfix' --dry-run",
                "timeout": 5,
                "target": "simple_command"
            },
            {
                "name": "maya_scenario",
                "description": "ADHD persona - speed critical",
                "command": "./bin/ask-nix 'firefox now' --personality minimal --dry-run",
                "timeout": 2,
                "target": "maya_response" 
            },
            {
                "name": "grandma_scenario", 
                "description": "Elderly persona - patient but responsive",
                "command": "./bin/ask-nix 'I need that Firefox browser thing' --personality friendly --dry-run",
                "timeout": 5,
                "target": "grandma_response"
            }
        ]

    def init_database(self):
        """Initialize performance metrics database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    scenario TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    memory_mb REAL,
                    cpu_percent REAL,
                    target_met BOOLEAN,
                    target_ms REAL,
                    system_info TEXT,
                    git_commit TEXT,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_count INTEGER,
                    memory_total_gb REAL,
                    python_version TEXT,
                    nixos_version TEXT,
                    git_commit TEXT
                )
            """)

    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            git_commit = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.project_root,
                text=True
            ).strip()
        except Exception:
            git_commit = "unknown"
            
        try:
            nixos_version = subprocess.check_output(
                ["nixos-version"], text=True
            ).strip()
        except Exception:
            nixos_version = "unknown"
            
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": sys.version.split()[0],
            "nixos_version": nixos_version,
            "git_commit": git_commit,
            "timestamp": datetime.now().isoformat()
        }

    async def benchmark_command(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark a single command scenario."""
        print(f"🔍 Benchmarking: {scenario['name']} - {scenario['description']}")
        
        # Pre-execution metrics
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Execute command and measure
        start_time = time.perf_counter()
        
        try:
            result = subprocess.run(
                scenario["command"].split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=scenario["timeout"],
                env={**os.environ, "NIX_HUMANITY_PYTHON_BACKEND": "true"}
            )
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Post-execution metrics
            memory_after = process.memory_info().rss / (1024 * 1024)  # MB
            memory_used = max(memory_after - memory_before, 0)
            
            # Determine if target was met
            target_key = scenario.get("target", "simple_command")
            target_s = self.targets.get(target_key, 2.0)
            target_ms = target_s * 1000
            target_met = duration_ms <= target_ms
            
            success = result.returncode == 0
            
            benchmark_result = {
                "scenario": scenario["name"],
                "description": scenario["description"],
                "duration_ms": duration_ms,
                "memory_mb": memory_used,
                "target_ms": target_ms,
                "target_met": target_met,
                "success": success,
                "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
                "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0,
                "command": scenario["command"]
            }
            
            # Performance assessment
            if target_met:
                status = "✅ TARGET MET"
            elif duration_ms <= target_ms * 1.5:  # Within 50% of target
                status = "⚠️ CLOSE TO TARGET"
            else:
                status = "❌ NEEDS OPTIMIZATION"
                
            print(f"   Duration: {duration_ms:.1f}ms (target: {target_ms:.0f}ms) {status}")
            print(f"   Memory: {memory_used:.1f}MB | Success: {success}")
            
            return benchmark_result
            
        except subprocess.TimeoutExpired:
            duration_ms = scenario["timeout"] * 1000
            target_ms = self.targets.get(scenario.get("target", "simple_command"), 2.0) * 1000
            
            print(f"   ❌ TIMEOUT after {scenario['timeout']}s (target: {target_ms:.0f}ms)")
            
            return {
                "scenario": scenario["name"],
                "description": scenario["description"],
                "duration_ms": duration_ms,
                "memory_mb": 0,
                "target_ms": target_ms,
                "target_met": False,
                "success": False,
                "timeout": True,
                "command": scenario["command"]
            }
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                "scenario": scenario["name"],
                "description": scenario["description"], 
                "duration_ms": 0,
                "memory_mb": 0,
                "target_ms": 0,
                "target_met": False,
                "success": False,
                "error": str(e),
                "command": scenario["command"]
            }

    async def run_memory_stress_test(self) -> Dict[str, Any]:
        """Test memory usage under load."""
        print("🧠 Running memory stress test...")
        
        process = psutil.Process()
        memory_baseline = process.memory_info().rss / (1024 * 1024)
        
        # Simulate multiple concurrent operations
        tasks = []
        for i in range(5):
            task = asyncio.create_task(
                self.benchmark_command({
                    "name": f"concurrent_{i}",
                    "description": f"Concurrent operation {i}",
                    "command": "./bin/ask-nix 'help' --dry-run",
                    "timeout": 10,
                    "target": "simple_command"
                })
            )
            tasks.append(task)
        
        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.perf_counter()
        
        memory_peak = process.memory_info().rss / (1024 * 1024)
        memory_used = memory_peak - memory_baseline
        
        concurrent_duration = (end_time - start_time) * 1000
        
        memory_target_met = memory_used <= self.targets["memory_active"]
        
        print(f"   Concurrent Duration: {concurrent_duration:.1f}ms")
        print(f"   Memory Used: {memory_used:.1f}MB (target: {self.targets['memory_active']}MB)")
        print(f"   Memory Target: {'✅ MET' if memory_target_met else '❌ EXCEEDED'}")
        
        return {
            "scenario": "memory_stress",
            "description": "Memory usage under concurrent load",
            "duration_ms": concurrent_duration,
            "memory_mb": memory_used,
            "target_ms": 5000,  # 5 seconds for concurrent ops
            "target_met": concurrent_duration <= 5000 and memory_target_met,
            "success": len([r for r in results if not isinstance(r, Exception)]) >= 3,
            "concurrent_operations": 5
        }

    def save_results(self, results: List[Dict[str, Any]], system_info: Dict[str, Any]):
        """Save benchmark results to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Save system info
            conn.execute("""
                INSERT INTO system_metrics 
                (cpu_count, memory_total_gb, python_version, nixos_version, git_commit)
                VALUES (?, ?, ?, ?, ?)
            """, (
                system_info["cpu_count"],
                system_info["memory_total_gb"], 
                system_info["python_version"],
                system_info["nixos_version"],
                system_info["git_commit"]
            ))
            
            # Save benchmark results
            for result in results:
                conn.execute("""
                    INSERT INTO benchmarks
                    (scenario, duration_ms, memory_mb, target_met, target_ms, system_info, git_commit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    result["scenario"],
                    result["duration_ms"],
                    result.get("memory_mb", 0),
                    result["target_met"],
                    result.get("target_ms", 0),
                    json.dumps(system_info),
                    system_info["git_commit"]
                ))

    def generate_report(self, results: List[Dict[str, Any]], system_info: Dict[str, Any]) -> str:
        """Generate comprehensive performance report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate summary statistics
        successful_results = [r for r in results if r.get("success", False)]
        targets_met = [r for r in results if r.get("target_met", False)]
        
        avg_duration = statistics.mean([r["duration_ms"] for r in successful_results]) if successful_results else 0
        max_duration = max([r["duration_ms"] for r in results]) if results else 0
        
        total_memory = sum([r.get("memory_mb", 0) for r in results])
        avg_memory = total_memory / len(results) if results else 0
        
        # Performance grade
        target_success_rate = len(targets_met) / len(results) if results else 0
        if target_success_rate >= 0.9:
            grade = "A+ EXCELLENT"
        elif target_success_rate >= 0.8:
            grade = "A- GOOD" 
        elif target_success_rate >= 0.7:
            grade = "B+ ACCEPTABLE"
        elif target_success_rate >= 0.6:
            grade = "B- NEEDS WORK"
        else:
            grade = "C OPTIMIZATION REQUIRED"
            
        report = f"""
# Performance Benchmark Report - Core Excellence Phase
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 Executive Summary

**Overall Performance Grade**: {grade}
**Target Success Rate**: {target_success_rate:.1%} ({len(targets_met)}/{len(results)})
**Average Response Time**: {avg_duration:.1f}ms
**Maximum Response Time**: {max_duration:.1f}ms  
**Average Memory Usage**: {avg_memory:.1f}MB

## 🖥️ System Information

- **CPU Cores**: {system_info['cpu_count']}
- **Total Memory**: {system_info['memory_total_gb']:.1f}GB
- **Python Version**: {system_info['python_version']}
- **NixOS Version**: {system_info['nixos_version']}
- **Git Commit**: {system_info['git_commit']}

## 🎯 Performance Targets vs Results

"""
        
        # Add detailed results
        for result in results:
            target_status = "✅ MET" if result.get("target_met", False) else "❌ MISSED"
            success_status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
            
            report += f"""
### {result['scenario'].replace('_', ' ').title()}
- **Description**: {result.get('description', 'No description')}
- **Duration**: {result['duration_ms']:.1f}ms (target: {result.get('target_ms', 0):.0f}ms) {target_status}
- **Memory**: {result.get('memory_mb', 0):.1f}MB
- **Status**: {success_status}
- **Command**: `{result.get('command', 'N/A')}`
"""

        # Add optimization recommendations
        report += """
## 🚀 Optimization Recommendations

"""
        
        failed_targets = [r for r in results if not r.get("target_met", False)]
        if failed_targets:
            report += "### Priority Optimizations:\n"
            for result in failed_targets:
                over_target = result["duration_ms"] - result.get("target_ms", 0)
                report += f"- **{result['scenario']}**: {over_target:.0f}ms over target - investigate {result.get('command', '')}\n"
        else:
            report += "### 🎉 All Performance Targets Met!\nSystem is performing within specifications.\n"
            
        # Add persona-specific analysis
        report += """
## 👥 Persona Performance Analysis

"""
        
        maya_result = next((r for r in results if r["scenario"] == "maya_scenario"), None)
        if maya_result:
            maya_status = "✅ EXCELLENT" if maya_result["target_met"] else "⚠️ NEEDS ATTENTION"
            report += f"- **Maya (ADHD)**: {maya_result['duration_ms']:.0f}ms response - {maya_status}\n"
            
        grandma_result = next((r for r in results if r["scenario"] == "grandma_scenario"), None)  
        if grandma_result:
            grandma_status = "✅ GOOD" if grandma_result["target_met"] else "⚠️ TOO SLOW"
            report += f"- **Grandma Rose**: {grandma_result['duration_ms']:.0f}ms response - {grandma_status}\n"

        # Add next steps
        report += f"""
## 📋 Next Steps for Core Excellence

### Immediate Actions:
1. **Critical Path Optimization**: Focus on scenarios exceeding targets by >50%
2. **Memory Management**: Review memory usage patterns for optimization opportunities  
3. **Caching Implementation**: Add intelligent caching for repeated operations
4. **Performance Monitoring**: Set up continuous performance regression testing

### Performance Targets Achieved: {len(targets_met)}/{len(results)}
"""

        # Save report to file
        report_path = self.results_dir / f"performance_report_{timestamp}.md"
        with open(report_path, 'w') as f:
            f.write(report)
            
        return report

    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run complete performance benchmark suite."""
        print("🚀 Starting Comprehensive Performance Benchmark")
        print("=" * 60)
        
        system_info = self.get_system_info()
        print(f"📊 System: {system_info['cpu_count']} cores, {system_info['memory_total_gb']:.1f}GB RAM")
        print(f"🐍 Python: {system_info['python_version']} | 💻 NixOS: {system_info['nixos_version']}")
        print(f"📝 Commit: {system_info['git_commit']}")
        print()
        
        results = []
        
        # Run all scenario benchmarks
        for i, scenario in enumerate(self.scenarios, 1):
            print(f"[{i}/{len(self.scenarios)}]", end=" ")
            result = await self.benchmark_command(scenario)
            results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(0.5)
            
        print()
        
        # Run memory stress test
        memory_result = await self.run_memory_stress_test()
        results.append(memory_result)
        
        print()
        
        # Save results and generate report
        self.save_results(results, system_info)
        report = self.generate_report(results, system_info)
        
        # Summary
        targets_met = len([r for r in results if r.get("target_met", False)])
        total_scenarios = len(results)
        success_rate = targets_met / total_scenarios
        
        print("📊 BENCHMARK COMPLETE")
        print("=" * 60)
        print(f"✅ Targets Met: {targets_met}/{total_scenarios} ({success_rate:.1%})")
        print(f"📄 Report saved to: {self.results_dir}/performance_report_*.md")
        print(f"🗄️ Data saved to: {self.db_path}")
        
        if success_rate >= 0.8:
            print("🎉 CORE EXCELLENCE: Performance targets largely achieved!")
        elif success_rate >= 0.6:
            print("⚠️ OPTIMIZATION NEEDED: Several targets require attention")
        else:
            print("🚨 CRITICAL: Major performance optimizations required")
            
        return {
            "total_scenarios": total_scenarios,
            "targets_met": targets_met,
            "success_rate": success_rate,
            "results": results,
            "system_info": system_info,
            "report_generated": True
        }

async def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()
    
    try:
        results = await benchmark.run_comprehensive_benchmark()
        
        # Exit with appropriate code
        if results["success_rate"] >= 0.8:
            sys.exit(0)  # Success
        elif results["success_rate"] >= 0.6:
            sys.exit(1)  # Warning - some optimization needed
        else:
            sys.exit(2)  # Critical - major optimization required
            
    except KeyboardInterrupt:
        print("\n🛑 Benchmark interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())