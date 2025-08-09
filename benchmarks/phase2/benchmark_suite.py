#!/usr/bin/env python3
"""
from typing import List, Dict
🚀 Performance Benchmarking Suite for Nix for Humanity

Comprehensive performance testing for Phase 2 optimization.
Measures response times, memory usage, and identifies bottlenecks.
"""

import time
import json
import psutil
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Callable
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, asdict

# Add project to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.nix_for_humanity.core.nlp_engine import NLPEngine
from src.nix_for_humanity.xai.xai_engine import XAIEngine
from src.nix_for_humanity.ai.advanced_learning_system import AdvancedLearningSystem
from src.nix_for_humanity.tui.persona_system import PersonaSystem
from src.nix_for_humanity.ai.context_manager import EnhancedContextManager


@dataclass
class BenchmarkResult:
    """Container for benchmark results"""
    name: str
    category: str
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    memory_mb: float
    iterations: int
    timestamp: str
    details: Dict[str, Any] = None


class PerformanceBenchmark:
    """Main benchmarking suite for Nix for Humanity"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.nlp_engine = None
        self.xai_engine = None
        self.learning_system = None
        self.persona_system = None
        self.context_manager = None
        
    def setup(self):
        """Initialize all components for benchmarking"""
        print("🔧 Setting up benchmark components...")
        self.nlp_engine = NLPEngine()
        self.xai_engine = XAIEngine()
        self.learning_system = AdvancedLearningSystem()
        self.persona_system = PersonaSystem()
        self.context_manager = EnhancedContextManager()
        print("✅ Components initialized")
        
    @contextmanager
    def measure_performance(self, name: str, category: str):
        """Context manager for measuring performance"""
        times = []
        memory_usage = []
        
        # Warm up
        yield lambda fn: fn()
        
        # Actual measurements
        iterations = 100
        for i in range(iterations):
            # Memory tracking
            tracemalloc.start()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Time tracking
            start_time = time.perf_counter()
            
            yield lambda fn: fn()
            
            # Record measurements
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)  # Convert to ms
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            memory_usage.append(peak / 1024 / 1024)  # Convert to MB
            
        # Calculate statistics
        result = BenchmarkResult(
            name=name,
            category=category,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            memory_mb=statistics.mean(memory_usage),
            iterations=iterations,
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(result)
        self._print_result(result)
        
    def _print_result(self, result: BenchmarkResult):
        """Pretty print benchmark result"""
        print(f"\n📊 {result.name}")
        print(f"   Category: {result.category}")
        print(f"   Avg Time: {result.avg_time_ms:.2f}ms")
        print(f"   Min/Max: {result.min_time_ms:.2f}ms / {result.max_time_ms:.2f}ms")
        print(f"   Std Dev: {result.std_dev_ms:.2f}ms")
        print(f"   Memory: {result.memory_mb:.2f}MB")
        
    def benchmark_nlp_engine(self):
        """Benchmark NLP engine performance"""
        print("\n🧠 Benchmarking NLP Engine...")
        
        test_inputs = [
            "install firefox",
            "update my system",
            "why is my wifi not working?",
            "show me all installed packages",
            "help me configure nginx",
            "I need that photo editing software, you know the free one",
            "can you explain what systemd does?",
            "remove all old kernel versions"
        ]
        
        for input_text in test_inputs:
            with self.measure_performance(
                f"NLP: {input_text[:30]}...", 
                "NLP Processing"
            ) as measure:
                measure(lambda: self.nlp_engine.parse(input_text))
                
    def benchmark_xai_engine(self):
        """Benchmark XAI engine performance"""
        print("\n🤖 Benchmarking XAI Engine...")
        
        test_intents = [
            ("install", {"package": "firefox"}),
            ("update", {"target": "system"}),
            ("troubleshoot", {"issue": "wifi"}),
            ("search", {"query": "editor"}),
            ("explain", {"concept": "systemd"})
        ]
        
        personas = ["Grandma Rose", "Maya", "Dr. Sarah", "Alex", "Luna"]
        
        for intent_type, params in test_intents:
            for persona in personas:
                with self.measure_performance(
                    f"XAI: {intent_type} for {persona}", 
                    "XAI Generation"
                ) as measure:
                    measure(lambda: self.xai_engine.explain(
                        intent_type, 
                        params, 
                        persona=persona
                    ))
                    
    def benchmark_learning_system(self):
        """Benchmark learning system performance"""
        print("\n📚 Benchmarking Learning System...")
        
        # Test preference learning
        with self.measure_performance(
            "Learning: Record preference",
            "Learning System"
        ) as measure:
            measure(lambda: self.learning_system.record_preference(
                "editor", "neovim", "Maya"
            ))
            
        # Test pattern extraction
        with self.measure_performance(
            "Learning: Extract patterns",
            "Learning System"
        ) as measure:
            measure(lambda: self.learning_system.extract_patterns("Maya"))
            
        # Test adaptation
        with self.measure_performance(
            "Learning: Adapt response",
            "Learning System"
        ) as measure:
            measure(lambda: self.learning_system.adapt_response(
                "Installing package...", "Maya"
            ))
            
    def benchmark_persona_adaptation(self):
        """Benchmark persona adaptation performance"""
        print("\n👥 Benchmarking Persona Adaptation...")
        
        personas = self.persona_system.get_all_personas()
        
        for persona_name in personas:
            with self.measure_performance(
                f"Persona: Switch to {persona_name}",
                "Persona System"
            ) as measure:
                measure(lambda: self.persona_system.set_active_persona(persona_name))
                
            with self.measure_performance(
                f"Persona: Adapt UI for {persona_name}",
                "Persona System"
            ) as measure:
                measure(lambda: self.persona_system.get_ui_config(persona_name))
                
    def benchmark_context_management(self):
        """Benchmark context management performance"""
        print("\n🧩 Benchmarking Context Management...")
        
        # Add context
        with self.measure_performance(
            "Context: Add interaction",
            "Context Management"
        ) as measure:
            measure(lambda: self.context_manager.add_context(
                "user asked about firefox",
                "Maya"
            ))
            
        # Retrieve context
        with self.measure_performance(
            "Context: Get relevant context",
            "Context Management"
        ) as measure:
            measure(lambda: self.context_manager.get_relevant_context(
                "install it", "Maya"
            ))
            
    def benchmark_integration(self):
        """Benchmark full integration flow"""
        print("\n🔗 Benchmarking Integration Flow...")
        
        test_flows = [
            ("install firefox", "Maya"),
            ("update system", "Grandma Rose"),
            ("fix wifi", "David"),
            ("search python editor", "Dr. Sarah"),
            ("explain nix generations", "Carlos")
        ]
        
        for input_text, persona in test_flows:
            with self.measure_performance(
                f"Integration: {input_text} ({persona})",
                "Full Pipeline"
            ) as measure:
                def full_flow():
                    # Parse input
                    intent = self.nlp_engine.parse(input_text)
                    # Generate explanation
                    explanation = self.xai_engine.explain(
                        intent.intent_type, 
                        intent.params,
                        persona=persona
                    )
                    # Update context
                    self.context_manager.add_context(input_text, persona)
                    # Adapt response
                    response = self.learning_system.adapt_response(
                        str(explanation), persona
                    )
                    return response
                    
                measure(full_flow)
                
    def identify_bottlenecks(self):
        """Analyze results and identify bottlenecks"""
        print("\n🔍 Analyzing Performance Bottlenecks...")
        
        # Group by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
            
        # Find slowest operations
        slowest = sorted(self.results, key=lambda r: r.avg_time_ms, reverse=True)[:10]
        
        print("\n⚠️  Top 10 Slowest Operations:")
        for i, result in enumerate(slowest, 1):
            print(f"{i}. {result.name}: {result.avg_time_ms:.2f}ms")
            
        # Category summaries
        print("\n📊 Performance by Category:")
        for category, results in categories.items():
            avg_times = [r.avg_time_ms for r in results]
            print(f"\n{category}:")
            print(f"  Average: {statistics.mean(avg_times):.2f}ms")
            print(f"  Min: {min(avg_times):.2f}ms")
            print(f"  Max: {max(avg_times):.2f}ms")
            
        # Memory analysis
        memory_heavy = sorted(self.results, key=lambda r: r.memory_mb, reverse=True)[:5]
        print("\n💾 Top 5 Memory-Heavy Operations:")
        for i, result in enumerate(memory_heavy, 1):
            print(f"{i}. {result.name}: {result.memory_mb:.2f}MB")
            
    def save_results(self):
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmarks/phase2/reports/baseline_{timestamp}.json"
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "results": [asdict(r) for r in self.results],
            "summary": {
                "total_benchmarks": len(self.results),
                "avg_response_time": statistics.mean([r.avg_time_ms for r in self.results]),
                "max_response_time": max([r.max_time_ms for r in self.results]),
                "avg_memory_usage": statistics.mean([r.memory_mb for r in self.results])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"\n💾 Results saved to: {filename}")
        
    def run_all_benchmarks(self):
        """Run complete benchmark suite"""
        print("🚀 Starting Nix for Humanity Performance Benchmark Suite")
        print("=" * 60)
        
        self.setup()
        
        # Run all benchmarks
        self.benchmark_nlp_engine()
        self.benchmark_xai_engine()
        self.benchmark_learning_system()
        self.benchmark_persona_adaptation()
        self.benchmark_context_management()
        self.benchmark_integration()
        
        # Analysis
        self.identify_bottlenecks()
        
        # Save results
        self.save_results()
        
        print("\n✅ Benchmarking complete!")
        print(f"   Total benchmarks: {len(self.results)}")
        print(f"   Average response: {statistics.mean([r.avg_time_ms for r in self.results]):.2f}ms")
        

if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()