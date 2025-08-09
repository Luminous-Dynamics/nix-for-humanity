#!/usr/bin/env python3
"""
from typing import Tuple
📏 Baseline Performance Measurement Script

Quick script to measure current performance baseline for Phase 2 optimization.
Provides immediate insights into current system performance.
"""

import time
import sys
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.nix_for_humanity.core.nlp_engine import NLPEngine
from src.nix_for_humanity.xai.xai_engine import XAIEngine
from src.nix_for_humanity.ai.advanced_learning_system import AdvancedLearningSystem


class BaselineMetrics:
    """Quick baseline performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "performance": {},
            "memory": {},
            "bottlenecks": []
        }
        
    def _get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": sys.version.split()[0]
        }
        
    def measure_operation(self, name: str, operation, iterations: int = 10) -> Tuple[float, float]:
        """Measure single operation performance"""
        times = []
        
        # Warm-up
        operation()
        
        # Measure
        for _ in range(iterations):
            start = time.perf_counter()
            operation()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
            
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        return avg_time, min_time, max_time
        
    def measure_nlp_baseline(self):
        """Measure NLP engine baseline performance"""
        print("🧠 Measuring NLP Engine baseline...")
        
        nlp = NLPEngine()
        
        test_cases = [
            ("Simple command", "install firefox"),
            ("Question", "why is my wifi not working?"),
            ("Complex query", "I need that photo editing software that's like photoshop but free"),
            ("System query", "show me all packages that start with python"),
        ]
        
        nlp_metrics = {}
        
        for name, query in test_cases:
            avg, min_time, max_time = self.measure_operation(
                name,
                lambda: nlp.parse(query)
            )
            
            nlp_metrics[name] = {
                "query": query,
                "avg_ms": round(avg, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2)
            }
            
            print(f"  {name}: {avg:.2f}ms (min: {min_time:.2f}ms, max: {max_time:.2f}ms)")
            
            # Flag potential bottlenecks
            if avg > 100:
                self.metrics["bottlenecks"].append({
                    "component": "NLP Engine",
                    "operation": name,
                    "avg_ms": avg,
                    "severity": "high" if avg > 200 else "medium"
                })
                
        self.metrics["performance"]["nlp"] = nlp_metrics
        
    def measure_xai_baseline(self):
        """Measure XAI engine baseline performance"""
        print("\n🤖 Measuring XAI Engine baseline...")
        
        xai = XAIEngine()
        
        test_cases = [
            ("Simple explanation", "install", {"package": "firefox"}, "Maya"),
            ("Complex explanation", "troubleshoot", {"issue": "network"}, "Grandma Rose"),
            ("Technical explanation", "explain", {"concept": "systemd"}, "Dr. Sarah"),
        ]
        
        xai_metrics = {}
        
        for name, intent_type, params, persona in test_cases:
            avg, min_time, max_time = self.measure_operation(
                name,
                lambda: xai.explain(intent_type, params, persona=persona)
            )
            
            xai_metrics[name] = {
                "intent": intent_type,
                "persona": persona,
                "avg_ms": round(avg, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2)
            }
            
            print(f"  {name}: {avg:.2f}ms (min: {min_time:.2f}ms, max: {max_time:.2f}ms)")
            
            # Flag potential bottlenecks
            if avg > 150:
                self.metrics["bottlenecks"].append({
                    "component": "XAI Engine",
                    "operation": name,
                    "avg_ms": avg,
                    "severity": "high" if avg > 300 else "medium"
                })
                
        self.metrics["performance"]["xai"] = xai_metrics
        
    def measure_memory_usage(self):
        """Measure memory usage of components"""
        print("\n💾 Measuring memory usage...")
        
        process = psutil.Process()
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # NLP Engine memory
        nlp = NLPEngine()
        nlp_memory = process.memory_info().rss / 1024 / 1024 - baseline_memory
        
        # XAI Engine memory
        xai = XAIEngine()
        xai_memory = process.memory_info().rss / 1024 / 1024 - baseline_memory - nlp_memory
        
        # Learning System memory
        learning = AdvancedLearningSystem()
        learning_memory = process.memory_info().rss / 1024 / 1024 - baseline_memory - nlp_memory - xai_memory
        
        self.metrics["memory"] = {
            "baseline_mb": round(baseline_memory, 2),
            "nlp_engine_mb": round(nlp_memory, 2),
            "xai_engine_mb": round(xai_memory, 2),
            "learning_system_mb": round(learning_memory, 2),
            "total_mb": round(process.memory_info().rss / 1024 / 1024, 2)
        }
        
        print(f"  Baseline: {baseline_memory:.2f}MB")
        print(f"  NLP Engine: {nlp_memory:.2f}MB")
        print(f"  XAI Engine: {xai_memory:.2f}MB")
        print(f"  Learning System: {learning_memory:.2f}MB")
        print(f"  Total: {self.metrics['memory']['total_mb']}MB")
        
    def measure_integration_flow(self):
        """Measure end-to-end integration performance"""
        print("\n🔗 Measuring integration flow...")
        
        nlp = NLPEngine()
        xai = XAIEngine()
        
        def full_flow(query: str, persona: str):
            # Parse input
            intent = nlp.parse(query)
            # Generate explanation
            explanation = xai.explain(
                intent.intent_type,
                intent.params,
                persona=persona
            )
            return explanation
            
        test_flows = [
            ("Simple flow", "install firefox", "Maya"),
            ("Complex flow", "help me fix my broken wifi connection", "Grandma Rose"),
        ]
        
        flow_metrics = {}
        
        for name, query, persona in test_flows:
            avg, min_time, max_time = self.measure_operation(
                name,
                lambda: full_flow(query, persona)
            )
            
            flow_metrics[name] = {
                "query": query,
                "persona": persona,
                "avg_ms": round(avg, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2)
            }
            
            print(f"  {name}: {avg:.2f}ms (min: {min_time:.2f}ms, max: {max_time:.2f}ms)")
            
            # Flag if over target
            if avg > 500:
                self.metrics["bottlenecks"].append({
                    "component": "Integration Flow",
                    "operation": name,
                    "avg_ms": avg,
                    "severity": "critical"
                })
                
        self.metrics["performance"]["integration"] = flow_metrics
        
    def analyze_bottlenecks(self):
        """Analyze and report bottlenecks"""
        print("\n🔍 Bottleneck Analysis:")
        
        if not self.metrics["bottlenecks"]:
            print("  ✅ No significant bottlenecks detected!")
        else:
            print(f"  ⚠️  Found {len(self.metrics['bottlenecks'])} bottlenecks:")
            
            # Sort by severity and time
            sorted_bottlenecks = sorted(
                self.metrics["bottlenecks"],
                key=lambda x: (
                    {"critical": 0, "high": 1, "medium": 2}[x["severity"]],
                    -x["avg_ms"]
                )
            )
            
            for bottleneck in sorted_bottlenecks:
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡"
                }[bottleneck["severity"]]
                
                print(f"    {severity_emoji} {bottleneck['component']} - {bottleneck['operation']}: {bottleneck['avg_ms']:.2f}ms")
                
    def generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        print("\n💡 Optimization Recommendations:")
        
        recommendations = []
        
        # Check NLP performance
        nlp_avg = sum(m["avg_ms"] for m in self.metrics["performance"]["nlp"].values()) / len(self.metrics["performance"]["nlp"])
        if nlp_avg > 50:
            recommendations.append({
                "component": "NLP Engine",
                "issue": f"Average response time {nlp_avg:.2f}ms > 50ms target",
                "suggestions": [
                    "Implement caching for common queries",
                    "Pre-compile regex patterns",
                    "Use lazy loading for intent patterns"
                ]
            })
            
        # Check XAI performance
        xai_avg = sum(m["avg_ms"] for m in self.metrics["performance"]["xai"].values()) / len(self.metrics["performance"]["xai"])
        if xai_avg > 100:
            recommendations.append({
                "component": "XAI Engine",
                "issue": f"Average explanation time {xai_avg:.2f}ms > 100ms target",
                "suggestions": [
                    "Cache persona-specific explanations",
                    "Pre-generate common explanations",
                    "Optimize template rendering"
                ]
            })
            
        # Check memory usage
        total_memory = self.metrics["memory"]["total_mb"]
        if total_memory > 150:
            recommendations.append({
                "component": "Memory Usage",
                "issue": f"Total memory {total_memory}MB > 150MB target",
                "suggestions": [
                    "Implement lazy loading for models",
                    "Use memory-mapped files for large data",
                    "Add garbage collection hints"
                ]
            })
            
        for rec in recommendations:
            print(f"\n  🎯 {rec['component']}:")
            print(f"     Issue: {rec['issue']}")
            print("     Suggestions:")
            for suggestion in rec['suggestions']:
                print(f"       - {suggestion}")
                
        self.metrics["recommendations"] = recommendations
        
    def save_baseline(self):
        """Save baseline metrics"""
        filename = "benchmarks/phase2/reports/baseline_metrics.json"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
        print(f"\n💾 Baseline metrics saved to: {filename}")
        
    def run(self):
        """Run complete baseline measurement"""
        print("📏 Nix for Humanity - Baseline Performance Measurement")
        print("=" * 60)
        
        # Run measurements
        self.measure_nlp_baseline()
        self.measure_xai_baseline()
        self.measure_memory_usage()
        self.measure_integration_flow()
        
        # Analysis
        self.analyze_bottlenecks()
        self.generate_optimization_recommendations()
        
        # Save results
        self.save_baseline()
        
        # Summary
        print("\n📊 Summary:")
        print(f"  Total bottlenecks: {len(self.metrics['bottlenecks'])}")
        print(f"  Total recommendations: {len(self.metrics.get('recommendations', []))}")
        print(f"  Memory usage: {self.metrics['memory']['total_mb']}MB")
        
        # Phase 2 targets
        print("\n🎯 Phase 2 Targets:")
        print("  - All operations < 500ms")
        print("  - NLP < 50ms average")
        print("  - XAI < 100ms average")
        print("  - Memory < 150MB total")
        

if __name__ == "__main__":
    baseline = BaselineMetrics()
    baseline.run()