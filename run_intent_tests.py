#!/usr/bin/env python3
"""Run comprehensive intent recognition tests and generate improvement report.

This script:
1. Runs all intent recognition tests
2. Collects performance metrics
3. Identifies problem areas
4. Generates improvement suggestions
5. Creates a dashboard view
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.intents import IntentRecognizer, IntentType
from luminous_nix.core.intent_factory import IntentRecognizerProxy
from luminous_nix.core.config_enhanced_intent import IntentRecognitionConfig
from luminous_nix.core.intent_improvement import (
    IntentLearningDatabase,
    IntentAnalyzer,
    IntentImprovementDashboard,
    IntentFeedback
)


def run_coverage_test() -> Dict[str, any]:
    """Test coverage of all intent types."""
    print("🔍 Testing Intent Coverage...")
    
    recognizer = IntentRecognizer()
    all_intents = [t for t in IntentType if t != IntentType.UNKNOWN]
    
    # Test queries for each intent type
    test_queries = {
        IntentType.INSTALL_PACKAGE: ["install firefox", "add vim", "get docker"],
        IntentType.REMOVE_PACKAGE: ["remove firefox", "uninstall vim", "delete docker"],
        IntentType.SEARCH_PACKAGE: ["search editor", "find browser", "look for terminal"],
        IntentType.UPDATE_SYSTEM: ["update system", "upgrade nixos", "refresh system"],
        IntentType.ROLLBACK: ["rollback", "revert", "go back"],
        IntentType.GARBAGE_COLLECT: ["garbage collect", "clean up", "free space"],
        IntentType.LIST_INSTALLED: ["list installed", "what's installed", "show packages"],
        IntentType.DISK_USAGE: ["disk usage", "show disk space", "df"],
        IntentType.ANALYZE_DISK: ["analyze disk space", "what's using space"],
        IntentType.HELP: ["help", "help me", "what can you do"],
        # Add more as needed...
    }
    
    covered = set()
    failed = []
    
    for intent_type, queries in test_queries.items():
        for query in queries:
            result = recognizer.recognize(query)
            if result.type == intent_type:
                covered.add(intent_type)
                break
        else:
            failed.append((intent_type, queries))
    
    uncovered = set(all_intents) - covered
    
    return {
        'total_intents': len(all_intents),
        'covered': len(covered),
        'coverage_percent': (len(covered) / len(all_intents)) * 100,
        'uncovered': [t.value for t in uncovered],
        'failed_tests': [(t.value, q) for t, q in failed]
    }


def run_performance_test() -> Dict[str, any]:
    """Test performance characteristics."""
    print("⚡ Testing Performance...")
    
    recognizer = IntentRecognizer()
    
    # Common queries for benchmarking
    queries = [
        "install firefox",
        "search vim",
        "update system",
        "disk usage",
        "help",
        "analyze disk space",
        "list generations",
        "start nginx",
        "create user alice",
        "mount /dev/sdb1"
    ] * 10  # 100 queries total
    
    # Warm up
    for _ in range(10):
        recognizer.recognize("test")
    
    # Benchmark
    times = []
    for query in queries:
        start = time.perf_counter()
        recognizer.recognize(query)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
    
    # Statistics
    times.sort()
    
    return {
        'total_queries': len(queries),
        'avg_ms': sum(times) / len(times),
        'min_ms': min(times),
        'max_ms': max(times),
        'p50_ms': times[len(times) // 2],
        'p95_ms': times[int(len(times) * 0.95)],
        'p99_ms': times[int(len(times) * 0.99)]
    }


def run_ambiguity_test() -> Dict[str, any]:
    """Test handling of ambiguous queries."""
    print("🤔 Testing Ambiguous Queries...")
    
    recognizer = IntentRecognizer()
    db = IntentLearningDatabase()
    
    ambiguous_queries = [
        ("clean", "Could be garbage collect or clean something else"),
        ("update", "Could be system update or package update"),
        ("space", "Could be disk space or namespace"),
        ("fix", "Too vague to determine"),
        ("make it work", "No specific action"),
        ("install", "Missing package name"),
        ("help with", "Incomplete help request"),
        ("I need", "Incomplete statement"),
        ("show me", "Missing what to show"),
        ("check", "Missing what to check"),
    ]
    
    results = []
    for query, description in ambiguous_queries:
        intent = recognizer.recognize(query)
        
        results.append({
            'query': query,
            'description': description,
            'recognized_as': intent.type.value,
            'confidence': intent.confidence,
            'is_unknown': intent.type == IntentType.UNKNOWN
        })
        
        # Log for learning
        db.log_query(query, intent.type.value, intent.confidence, 0.5)
    
    # Calculate metrics
    unknown_count = sum(1 for r in results if r['is_unknown'])
    low_confidence = sum(1 for r in results if r['confidence'] < 0.5)
    
    return {
        'total_ambiguous': len(ambiguous_queries),
        'recognized_as_unknown': unknown_count,
        'low_confidence_count': low_confidence,
        'avg_confidence': sum(r['confidence'] for r in results) / len(results),
        'details': results
    }


def run_real_world_test() -> Dict[str, any]:
    """Test with real-world user queries."""
    print("🌍 Testing Real-World Queries...")
    
    recognizer = IntentRecognizer()
    
    # Real queries users might actually type
    real_queries = [
        ("how do I install firefox", IntentType.INSTALL_PACKAGE),
        ("my disk is full", IntentType.DISK_USAGE),
        ("wifi not working", IntentType.SHOW_NETWORK),
        ("undo last update", IntentType.ROLLBACK),
        ("firefox won't start", IntentType.UNKNOWN),
        ("make my system faster", IntentType.UNKNOWN),
        ("install text editor", IntentType.INSTALL_PACKAGE),
        ("show me network settings", IntentType.SHOW_NETWORK),
        ("how much ram do I have", IntentType.CHECK_STATUS),
        ("delete old stuff", IntentType.GARBAGE_COLLECT),
        ("python development environment", IntentType.CREATE_FLAKE),
        ("connect to wifi network", IntentType.CONNECT_WIFI),
        ("why is chrome using so much memory", IntentType.UNKNOWN),
        ("backup my system", IntentType.UNKNOWN),
        ("install everything I need for web development", IntentType.UNKNOWN),
    ]
    
    correct = 0
    results = []
    
    for query, expected in real_queries:
        intent = recognizer.recognize(query)
        is_correct = intent.type == expected
        if is_correct:
            correct += 1
            
        results.append({
            'query': query,
            'expected': expected.value,
            'recognized': intent.type.value,
            'correct': is_correct,
            'confidence': intent.confidence
        })
    
    return {
        'total_queries': len(real_queries),
        'correct': correct,
        'accuracy': (correct / len(real_queries)) * 100,
        'failures': [r for r in results if not r['correct']]
    }


def collect_improvement_data(recognizer: IntentRecognizer) -> List[Dict]:
    """Collect data for improvement suggestions."""
    print("📊 Collecting Improvement Data...")
    
    db = IntentLearningDatabase()
    
    # Simulate some corrections
    corrections = [
        ("wipe disk", IntentType.UNKNOWN, IntentType.GARBAGE_COLLECT),
        ("install stuff", IntentType.UNKNOWN, IntentType.INSTALL_PACKAGE),
        ("fix network", IntentType.UNKNOWN, IntentType.SHOW_NETWORK),
        ("make faster", IntentType.UNKNOWN, IntentType.GARBAGE_COLLECT),
    ]
    
    for query, recognized, correct in corrections:
        intent = recognizer.recognize(query)
        
        feedback = IntentFeedback(
            query=query,
            recognized_intent=intent.type.value,
            correct_intent=correct.value,
            confidence=intent.confidence,
            timestamp=time.time(),
            user_satisfaction=2 if intent.type == IntentType.UNKNOWN else 4
        )
        db.add_feedback(feedback)
    
    # Get suggestions
    analyzer = IntentAnalyzer(db)
    suggestions = analyzer.suggest_improvements()
    
    return suggestions


def generate_report(results: Dict[str, any]):
    """Generate a comprehensive report."""
    print("\n" + "="*70)
    print(" 📋 INTENT RECOGNITION TEST REPORT")
    print("="*70)
    
    # Coverage Report
    coverage = results['coverage']
    print(f"\n🎯 Coverage: {coverage['coverage_percent']:.1f}%")
    print(f"   Covered: {coverage['covered']}/{coverage['total_intents']} intent types")
    if coverage['uncovered']:
        print(f"   Missing: {', '.join(coverage['uncovered'][:5])}")
    
    # Performance Report
    perf = results['performance']
    print(f"\n⚡ Performance:")
    print(f"   Average: {perf['avg_ms']:.2f}ms")
    print(f"   P95: {perf['p95_ms']:.2f}ms")
    print(f"   P99: {perf['p99_ms']:.2f}ms")
    
    # Ambiguity Handling
    ambig = results['ambiguity']
    print(f"\n🤔 Ambiguous Query Handling:")
    print(f"   Recognized as UNKNOWN: {ambig['recognized_as_unknown']}/{ambig['total_ambiguous']}")
    print(f"   Average Confidence: {ambig['avg_confidence']:.2%}")
    
    # Real-World Accuracy
    real = results['real_world']
    print(f"\n🌍 Real-World Accuracy: {real['accuracy']:.1f}%")
    print(f"   Correct: {real['correct']}/{real['total_queries']}")
    if real['failures']:
        print("   Failed on:")
        for f in real['failures'][:3]:
            print(f"     '{f['query']}' -> {f['recognized']} (expected {f['expected']})")
    
    # Improvement Suggestions
    if results['suggestions']:
        print("\n💡 Improvement Suggestions:")
        for i, suggestion in enumerate(results['suggestions'][:3], 1):
            print(f"   {i}. {suggestion}")
    
    print("\n" + "="*70)
    
    # Overall Grade
    score = (
        coverage['coverage_percent'] * 0.3 +
        min(100, (1000 / max(1, perf['avg_ms'])) * 10) * 0.2 +  # Speed score
        (100 - ambig['recognized_as_unknown'] / ambig['total_ambiguous'] * 100) * 0.2 +
        real['accuracy'] * 0.3
    )
    
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D"
    
    print(f"\n🏆 Overall Grade: {grade} ({score:.1f}/100)")
    
    if score < 80:
        print("\n⚠️  Recommendation: Enable LLM assistance for better accuracy")
    
    print("="*70)


def main():
    """Run all tests and generate report."""
    print("🚀 Starting Comprehensive Intent Recognition Tests")
    print("-" * 70)
    
    # Run all test suites
    results = {
        'coverage': run_coverage_test(),
        'performance': run_performance_test(),
        'ambiguity': run_ambiguity_test(),
        'real_world': run_real_world_test(),
    }
    
    # Collect improvement suggestions
    recognizer = IntentRecognizer()
    results['suggestions'] = collect_improvement_data(recognizer)
    
    # Generate report
    generate_report(results)
    
    # Show dashboard
    dashboard = IntentImprovementDashboard()
    dashboard.print_dashboard()
    
    # Save results for tracking
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"intent_test_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    results = main()
    
    # Exit with non-zero if accuracy is too low
    if results['real_world']['accuracy'] < 70:
        sys.exit(1)