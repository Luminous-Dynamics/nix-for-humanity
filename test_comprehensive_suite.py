#!/usr/bin/env python3
"""
Comprehensive Test Suite for Luminous Nix Intelligence System
Tests all features, edge cases, performance, and stress scenarios
"""

import time
import json
import threading
import random
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from pathlib import Path

from src.luminous_nix.core.intelligent_system import (
    LuminousNixIntelligence,
    IntelligentCLI
)


class ComprehensiveTestSuite:
    """Comprehensive testing framework for the intelligent system"""
    
    def __init__(self):
        self.results = {}
        self.performance_metrics = []
        self.error_log = []
        
    def run_all_tests(self):
        """Run all test categories"""
        print("🚀 Luminous Nix Comprehensive Test Suite")
        print("=" * 70)
        print("Testing all features, edge cases, and performance scenarios\n")
        
        test_categories = [
            ("Functional Tests", self.test_functional),
            ("Edge Cases", self.test_edge_cases),
            ("Performance Tests", self.test_performance),
            ("Stress Tests", self.test_stress),
            ("Learning Tests", self.test_learning),
            ("Network Tests", self.test_network),
            ("Error Recovery", self.test_error_recovery),
            ("Real-World Scenarios", self.test_real_world)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n{'='*70}")
            print(f"📋 {category_name}")
            print("=" * 70)
            
            try:
                result = test_func()
                self.results[category_name] = result
            except Exception as e:
                print(f"❌ Category failed: {e}")
                self.results[category_name] = False
                self.error_log.append((category_name, str(e)))
        
        self.print_summary()
        return all(self.results.values())
    
    def test_functional(self) -> bool:
        """Test core functionality of each feature"""
        print("\n🔧 Testing Core Functionality\n")
        
        intelligence = LuminousNixIntelligence()
        tests_passed = []
        
        # Test 1: Semantic Understanding
        print("1. Semantic Understanding:")
        test_queries = [
            ("install web browser", ["firefox", "chromium"]),
            ("text editor for programming", ["vim", "neovim", "emacs"]),
            ("python development environment", ["python3", "python311"]),
            ("container management", ["docker", "podman"]),
            ("version control", ["git", "mercurial"])
        ]
        
        for query, expected_suggestions in test_queries:
            response = intelligence.intelligent_search(query, use_all_features=False)
            
            # Check if any expected package was suggested
            suggested = response.intent.suggested_packages or []
            match = any(pkg in suggested for pkg in expected_suggestions)
            
            status = "✅" if match else "❌"
            print(f"  {status} '{query}' → {suggested[:3]}")
            tests_passed.append(match)
        
        # Test 2: Usage Analytics
        print("\n2. Usage Analytics:")
        insights = intelligence.get_insights()
        
        has_session = insights['session']['total_queries'] > 0
        has_analytics = 'analytics' in insights
        has_recommendations = 'cache_optimization' in insights
        
        print(f"  {'✅' if has_session else '❌'} Session tracking: {insights['session']['total_queries']} queries")
        print(f"  {'✅' if has_analytics else '❌'} Analytics data collected")
        print(f"  {'✅' if has_recommendations else '❌'} Cache recommendations available")
        
        tests_passed.extend([has_session, has_analytics, has_recommendations])
        
        # Test 3: Predictive ML
        print("\n3. Predictive ML:")
        
        # Train with pattern
        for q in ["python", "pip", "pytest"]:
            intelligence.intelligent_search(q, use_all_features=False)
        
        # Test prediction
        response = intelligence.intelligent_search("python", use_all_features=True)
        has_predictions = len(response.predictions) > 0
        
        print(f"  {'✅' if has_predictions else '❌'} Predictions generated: {len(response.predictions)}")
        if has_predictions:
            print(f"     Next likely: {[p[0] for p in response.predictions[:3]]}")
        
        tests_passed.append(has_predictions)
        
        # Test 4: Network capability
        print("\n4. Collaborative Network:")
        stats = intelligence.collaborative.get_stats()
        
        network_ready = stats['status'] == 'operational'
        print(f"  {'✅' if network_ready else '❌'} Network status: {stats['status']}")
        print(f"     Port: {stats['port']}, Peers: {stats['peer_count']}")
        
        tests_passed.append(network_ready)
        
        # Test 5: Update monitoring
        print("\n5. Update Monitoring:")
        update_stats = intelligence.update_monitor.get_statistics()
        
        monitoring_active = update_stats['channels_monitored'] > 0
        print(f"  {'✅' if monitoring_active else '❌'} Channels monitored: {update_stats['channels_monitored']}")
        print(f"     Watched packages: {update_stats['watched_packages']}")
        
        tests_passed.append(monitoring_active)
        
        intelligence.shutdown()
        
        success_rate = sum(tests_passed) / len(tests_passed)
        print(f"\n📊 Functional Test Success Rate: {success_rate:.1%}")
        
        return success_rate > 0.8
    
    def test_edge_cases(self) -> bool:
        """Test edge cases and unusual inputs"""
        print("\n🔍 Testing Edge Cases\n")
        
        intelligence = LuminousNixIntelligence()
        tests_passed = []
        
        edge_cases = [
            # Empty/whitespace
            ("", "Empty query"),
            ("   ", "Whitespace only"),
            ("\n\t", "Special whitespace"),
            
            # Very long queries
            ("install " * 100 + "firefox", "Very long query"),
            
            # Special characters
            ("install @#$%^&*()", "Special characters"),
            ("firefox!!!???", "Punctuation"),
            ("install\x00null", "Null character"),
            
            # Mixed languages (if supported)
            ("install 火狐", "Chinese characters"),
            ("установить firefox", "Cyrillic"),
            ("🔥🦊", "Emojis"),
            
            # Typos and misspellings
            ("instal fierrfox", "Typos"),
            ("pythn developmnt", "Multiple typos"),
            
            # SQL injection attempts
            ("'; DROP TABLE users; --", "SQL injection"),
            ("1' OR '1'='1", "SQL injection variant"),
            
            # Command injection attempts
            ("firefox; rm -rf /", "Command injection"),
            ("$(whoami)", "Command substitution"),
            "`ls -la`", "Backticks"
        ]
        
        for query, description in edge_cases:
            try:
                response = intelligence.intelligent_search(query, use_all_features=False)
                # Success = didn't crash
                print(f"  ✅ {description}: Handled gracefully")
                tests_passed.append(True)
            except Exception as e:
                print(f"  ❌ {description}: {str(e)[:50]}")
                tests_passed.append(False)
        
        intelligence.shutdown()
        
        success_rate = sum(tests_passed) / len(tests_passed)
        print(f"\n📊 Edge Case Success Rate: {success_rate:.1%}")
        
        return success_rate > 0.7
    
    def test_performance(self) -> bool:
        """Test performance metrics"""
        print("\n⚡ Testing Performance\n")
        
        intelligence = LuminousNixIntelligence()
        
        # Warm up
        for _ in range(5):
            intelligence.intelligent_search("test", use_all_features=False)
        
        # Test different query types
        test_scenarios = [
            ("Simple search", "firefox", False),
            ("With all features", "python development", True),
            ("Complex query", "install web browser with developer tools and privacy features", True),
            ("Cached query", "firefox", False),  # Should hit cache
            ("Pattern query", "python pip pytest", True)
        ]
        
        for scenario_name, query, use_features in test_scenarios:
            times = []
            
            for _ in range(10):
                start = time.time()
                response = intelligence.intelligent_search(query, use_all_features=use_features)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
            
            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            min_time = min(times)
            max_time = max(times)
            
            print(f"{scenario_name}:")
            print(f"  Avg: {avg_time:.1f}ms ± {std_dev:.1f}ms")
            print(f"  Min: {min_time:.1f}ms, Max: {max_time:.1f}ms")
            
            self.performance_metrics.append({
                'scenario': scenario_name,
                'avg_ms': avg_time,
                'std_dev': std_dev,
                'min_ms': min_time,
                'max_ms': max_time
            })
        
        intelligence.shutdown()
        
        # Check if performance meets targets
        avg_performance = statistics.mean([m['avg_ms'] for m in self.performance_metrics])
        print(f"\n📊 Overall Average: {avg_performance:.1f}ms")
        
        return avg_performance < 200
    
    def test_stress(self) -> bool:
        """Stress test with concurrent users"""
        print("\n💪 Stress Testing\n")
        
        num_threads = 10
        queries_per_thread = 20
        
        def user_simulation(user_id: int) -> List[float]:
            """Simulate a user making queries"""
            intelligence = LuminousNixIntelligence()
            times = []
            
            queries = [
                "install firefox",
                "python development",
                "text editor",
                "docker containers",
                "web server"
            ]
            
            for i in range(queries_per_thread):
                query = random.choice(queries)
                start = time.time()
                
                try:
                    response = intelligence.intelligent_search(query)
                    elapsed = (time.time() - start) * 1000
                    times.append(elapsed)
                except Exception as e:
                    print(f"  User {user_id} error: {e}")
                    times.append(999999)  # Error marker
                
                time.sleep(random.uniform(0.1, 0.5))  # Simulate thinking time
            
            intelligence.shutdown()
            return times
        
        print(f"Simulating {num_threads} concurrent users...")
        print(f"Each user makes {queries_per_thread} queries\n")
        
        all_times = []
        errors = 0
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(user_simulation, i) for i in range(num_threads)]
            
            for i, future in enumerate(as_completed(futures)):
                user_times = future.result()
                all_times.extend(user_times)
                user_errors = sum(1 for t in user_times if t > 10000)
                errors += user_errors
                
                avg_time = statistics.mean([t for t in user_times if t < 10000])
                print(f"  User {i}: Avg {avg_time:.1f}ms, Errors: {user_errors}")
        
        # Calculate overall statistics
        valid_times = [t for t in all_times if t < 10000]
        
        if valid_times:
            print(f"\n📊 Stress Test Results:")
            print(f"  Total queries: {len(all_times)}")
            print(f"  Successful: {len(valid_times)}")
            print(f"  Errors: {errors}")
            print(f"  Average response: {statistics.mean(valid_times):.1f}ms")
            print(f"  95th percentile: {statistics.quantiles(valid_times, n=20)[18]:.1f}ms")
            
            success_rate = len(valid_times) / len(all_times)
            return success_rate > 0.95 and statistics.mean(valid_times) < 500
        
        return False
    
    def test_learning(self) -> bool:
        """Test learning and improvement over time"""
        print("\n🧠 Testing Learning Capabilities\n")
        
        intelligence = LuminousNixIntelligence()
        
        # Train with patterns
        patterns = [
            ["python", "pip", "pytest", "black"],
            ["nodejs", "npm", "yarn", "webpack"],
            ["rust", "cargo", "rustc", "clippy"]
        ]
        
        print("Training with patterns...")
        for pattern in patterns:
            for query in pattern:
                intelligence.intelligent_search(query)
        
        # Test predictions
        print("\nTesting learned predictions:")
        
        test_cases = [
            ("python", ["pip", "pytest", "black"]),
            ("nodejs", ["npm", "yarn", "webpack"]),
            ("rust", ["cargo", "rustc", "clippy"])
        ]
        
        correct_predictions = 0
        total_predictions = 0
        
        for base_query, expected in test_cases:
            response = intelligence.intelligent_search(base_query)
            predictions = [p[0] for p in response.predictions]
            
            matches = sum(1 for exp in expected if exp in predictions)
            print(f"  After '{base_query}': {matches}/{len(expected)} correct predictions")
            print(f"    Expected: {expected}")
            print(f"    Got: {predictions[:3]}")
            
            correct_predictions += matches
            total_predictions += len(expected)
        
        # Test cache optimization
        print("\nTesting cache optimization:")
        
        # Make some queries hot
        for _ in range(10):
            intelligence.intelligent_search("firefox")
        
        recommendations = intelligence.analytics.get_smart_cache_recommendations()
        
        has_hot_packages = len(recommendations['packages_to_cache']) > 0
        print(f"  {'✅' if has_hot_packages else '❌'} Hot packages identified: {len(recommendations['packages_to_cache'])}")
        
        if has_hot_packages:
            print(f"    Top packages: {recommendations['packages_to_cache'][:3]}")
        
        intelligence.shutdown()
        
        accuracy = correct_predictions / max(1, total_predictions)
        print(f"\n📊 Learning Accuracy: {accuracy:.1%}")
        
        return accuracy > 0.3  # At least 30% prediction accuracy
    
    def test_network(self) -> bool:
        """Test collaborative network features"""
        print("\n🌐 Testing Collaborative Network\n")
        
        # Create network of 3 nodes
        print("Creating 3-node network...")
        
        node1 = LuminousNixIntelligence()
        node2 = LuminousNixIntelligence()
        node3 = LuminousNixIntelligence()
        
        # Connect nodes
        node2.collaborative.join_network("localhost", node1.collaborative.node.port)
        node3.collaborative.join_network("localhost", node1.collaborative.node.port)
        
        time.sleep(2)  # Let network stabilize
        
        # Node 1 searches
        print("\nNode 1 searches for 'rust compiler'...")
        response1 = node1.intelligent_search("rust compiler")
        
        time.sleep(1)
        
        # Node 2 searches same query
        print("Node 2 searches for same query...")
        response2 = node2.intelligent_search("rust compiler")
        
        # Check if knowledge was shared
        shared = response2.source == "collaborative"
        print(f"  {'✅' if shared else '❌'} Knowledge shared: Source = {response2.source}")
        
        # Check network statistics
        stats1 = node1.collaborative.get_stats()
        stats2 = node2.collaborative.get_stats()
        stats3 = node3.collaborative.get_stats()
        
        print(f"\nNetwork Statistics:")
        print(f"  Node 1: {stats1['peer_count']} peers, {stats1['queries_shared']} shared")
        print(f"  Node 2: {stats2['peer_count']} peers, {stats2['queries_received']} received")
        print(f"  Node 3: {stats3['peer_count']} peers")
        
        # Cleanup
        node1.shutdown()
        node2.shutdown()
        node3.shutdown()
        
        return stats1['peer_count'] > 0 or stats1['queries_shared'] > 0
    
    def test_error_recovery(self) -> bool:
        """Test error recovery and resilience"""
        print("\n🛡️ Testing Error Recovery\n")
        
        intelligence = LuminousNixIntelligence()
        recovery_tests = []
        
        # Test 1: Database errors
        print("1. Database error recovery:")
        # Simulate by making many concurrent queries
        threads = []
        for i in range(20):
            t = threading.Thread(
                target=lambda: intelligence.intelligent_search(f"test{i}")
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # System should still work
        response = intelligence.intelligent_search("firefox")
        works_after_db_stress = len(response.results) > 0
        print(f"  {'✅' if works_after_db_stress else '❌'} System works after database stress")
        recovery_tests.append(works_after_db_stress)
        
        # Test 2: Invalid data handling
        print("\n2. Invalid data handling:")
        
        # Try to corrupt cache
        if hasattr(intelligence.base_cache, 'l1_cache'):
            intelligence.base_cache.l1_cache['test'] = None
            intelligence.base_cache.l1_cache['corrupt'] = {'invalid': 'data'}
        
        try:
            response = intelligence.intelligent_search("test")
            print(f"  ✅ Handles corrupted cache gracefully")
            recovery_tests.append(True)
        except:
            print(f"  ❌ Failed with corrupted cache")
            recovery_tests.append(False)
        
        # Test 3: Resource exhaustion
        print("\n3. Resource exhaustion:")
        
        # Make many queries rapidly
        for _ in range(100):
            intelligence.intelligent_search("test", use_all_features=False)
        
        # Check if system is still responsive
        start = time.time()
        response = intelligence.intelligent_search("firefox")
        elapsed = (time.time() - start) * 1000
        
        responsive = elapsed < 1000
        print(f"  {'✅' if responsive else '❌'} Still responsive after 100 queries ({elapsed:.1f}ms)")
        recovery_tests.append(responsive)
        
        intelligence.shutdown()
        
        success_rate = sum(recovery_tests) / len(recovery_tests)
        print(f"\n📊 Recovery Success Rate: {success_rate:.1%}")
        
        return success_rate > 0.6
    
    def test_real_world(self) -> bool:
        """Test real-world usage scenarios"""
        print("\n🌍 Testing Real-World Scenarios\n")
        
        cli = IntelligentCLI()
        scenarios_passed = []
        
        # Scenario 1: New user exploring
        print("Scenario 1: New User Exploring")
        new_user_queries = [
            "how to install a web browser",
            "what text editors are available",
            "python programming tools",
            "system monitoring tools",
            "file managers"
        ]
        
        for query in new_user_queries:
            result = cli.search(query)
            has_results = len(result['results']) > 0
            print(f"  {'✅' if has_results else '❌'} '{query[:30]}...' → {len(result['results'])} results")
            scenarios_passed.append(has_results)
        
        # Scenario 2: Developer workflow
        print("\nScenario 2: Developer Setting Up Environment")
        developer_flow = [
            "install git",
            "python development environment",
            "nodejs and npm",
            "docker for containers",
            "postgresql database",
            "redis cache",
            "nginx web server"
        ]
        
        for query in developer_flow:
            result = cli.search(query)
            has_results = len(result['results']) > 0
            
            # Check if learning is happening
            has_predictions = 'next_likely' in result
            
            status = "✅" if has_results else "❌"
            print(f"  {status} '{query[:30]}...'")
            
            if has_predictions:
                print(f"     → Suggests: {result['next_likely'][0]}")
            
            scenarios_passed.append(has_results)
        
        # Scenario 3: System administrator
        print("\nScenario 3: System Administrator Tasks")
        admin_queries = [
            "monitoring tools",
            "backup software",
            "security scanners",
            "log analyzers",
            "network tools"
        ]
        
        for query in admin_queries:
            result = cli.search(query)
            has_results = len(result['results']) > 0
            print(f"  {'✅' if has_results else '❌'} '{query}' → {len(result['results'])} results")
            scenarios_passed.append(has_results)
        
        # Get final insights
        print("\n" + cli.get_insights())
        
        cli.shutdown()
        
        success_rate = sum(scenarios_passed) / len(scenarios_passed)
        print(f"\n📊 Real-World Success Rate: {success_rate:.1%}")
        
        return success_rate > 0.8
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        # Overall results
        total_passed = sum(1 for v in self.results.values() if v)
        total_tests = len(self.results)
        overall_rate = total_passed / max(1, total_tests)
        
        print(f"\nOverall Success Rate: {overall_rate:.1%} ({total_passed}/{total_tests})")
        print("\nCategory Results:")
        
        for category, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {category}")
        
        # Performance summary
        if self.performance_metrics:
            print("\nPerformance Summary:")
            avg_perf = statistics.mean([m['avg_ms'] for m in self.performance_metrics])
            print(f"  Average Response: {avg_perf:.1f}ms")
            
            fastest = min(self.performance_metrics, key=lambda x: x['min_ms'])
            print(f"  Fastest: {fastest['scenario']} @ {fastest['min_ms']:.1f}ms")
            
            slowest = max(self.performance_metrics, key=lambda x: x['max_ms'])
            print(f"  Slowest: {slowest['scenario']} @ {slowest['max_ms']:.1f}ms")
        
        # Error summary
        if self.error_log:
            print("\nErrors Encountered:")
            for category, error in self.error_log[:5]:
                print(f"  {category}: {error[:60]}")
        
        # Final verdict
        print("\n" + "=" * 70)
        if overall_rate >= 0.8:
            print("🎉 SYSTEM READY FOR PRODUCTION!")
            print("All major features working with high reliability")
        elif overall_rate >= 0.6:
            print("⚠️ SYSTEM MOSTLY READY")
            print("Some issues need addressing before production")
        else:
            print("❌ SYSTEM NEEDS WORK")
            print("Significant issues found, not ready for production")
        
        print("=" * 70)


def main():
    """Run comprehensive test suite"""
    suite = ComprehensiveTestSuite()
    success = suite.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())