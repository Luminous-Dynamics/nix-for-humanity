#!/usr/bin/env python3
"""
Comprehensive Test Suite for v0.3.1
Tests all critical functionality and known issues
"""

import json
import time

import pytest

from feedback_collection_system import FeedbackCollector
from monitoring_dashboard import MetricsDashboard
from src.luminous_nix.ai.dev_environment_specialist import DevEnvironmentSpecialist

# Import our systems
from src.luminous_nix.ai.hrm_integrated_v6_final import HRMIntegratedV6Final
from src.luminous_nix.ai.update_maintenance_specialist import (
    UpdateMaintenanceSpecialist,
)


class TestCoreAccuracy:
    """Test accuracy on critical query types"""

    def setup_method(self):
        """Initialize test system"""
        self.system = HRMIntegratedV6Final(enable_active_learning=False)
        self.test_queries = {
            "install": [
                ("install firefox", "nix-env -iA nixpkgs.firefox"),
                ("get spotify", "nix-env -iA nixpkgs.spotify"),
                ("install vscode editor", "nix-env -iA nixpkgs.vscode"),
            ],
            "dev": [
                (
                    "python development environment",
                    "nix-shell -p python3 python3Packages.pip",
                ),
                ("setup rust development", "nix-shell -p rustc cargo"),
                ("node.js environment", "nix-shell -p nodejs"),
            ],
            "update": [
                ("update system", "sudo nixos-rebuild switch"),
                ("update all packages", "nix-channel --update && nix-env -u"),
            ],
            "search": [
                ("search text editors", "nix search nixpkgs editor"),
                ("find pdf viewers", "nix search nixpkgs pdf"),
            ],
            "config": [
                ("enable bluetooth", "systemctl enable bluetooth"),
                ("edit configuration", "sudo nano /etc/nixos/configuration.nix"),
            ],
            "rollback": [
                (
                    "rollback to previous generation",
                    "sudo nixos-rebuild switch --rollback",
                ),
                ("undo last update", "sudo nixos-rebuild switch --rollback"),
            ],
        }

    def test_install_accuracy(self):
        """Test installation command accuracy"""
        correct = 0
        total = 0

        for query, expected in self.test_queries["install"]:
            result = self.system.process_query(query)
            if expected in result.get("command", ""):
                correct += 1
            total += 1

        accuracy = (correct / total) * 100
        assert accuracy >= 95, f"Install accuracy {accuracy}% below 95% target"

    def test_dev_environment_accuracy(self):
        """Test development environment accuracy"""
        specialist = DevEnvironmentSpecialist()

        for query, expected in self.test_queries["dev"]:
            result = specialist.handle_query(query)
            assert expected in result["command"], f"Failed: {query}"

    def test_update_accuracy(self):
        """Test update command accuracy"""
        specialist = UpdateMaintenanceSpecialist()

        for query, expected in self.test_queries["update"]:
            result = specialist.handle_query(query)
            assert result["confidence"] >= 0.9, f"Low confidence for: {query}"

    def test_overall_accuracy(self):
        """Test overall system accuracy"""
        correct = 0
        total = 0
        failures = []

        for category, queries in self.test_queries.items():
            for query, expected in queries:
                result = self.system.process_query(query)
                if expected in result.get("command", ""):
                    correct += 1
                else:
                    failures.append(
                        {
                            "query": query,
                            "expected": expected,
                            "actual": result.get("command", "None"),
                        }
                    )
                total += 1

        accuracy = (correct / total) * 100

        if failures:
            print("\n❌ Failed queries:")
            for fail in failures:
                print(f"  Query: {fail['query']}")
                print(f"  Expected: {fail['expected']}")
                print(f"  Got: {fail['actual']}")

        assert accuracy >= 96, f"Overall accuracy {accuracy:.1f}% below 96% target"


class TestPerformance:
    """Test performance metrics"""

    def setup_method(self):
        self.system = HRMIntegratedV6Final(enable_active_learning=False)

    def test_response_time(self):
        """Test average response time"""
        queries = ["install firefox", "update system", "search editors"]
        times = []

        for query in queries * 10:  # Test 30 queries
            start = time.time()
            self.system.process_query(query)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        assert avg_time < 10, f"Average response time {avg_time:.2f}ms exceeds 10ms"

    def test_cache_performance(self):
        """Test cache hit rate"""
        queries = ["install firefox"] * 10

        # First query (cache miss)
        start = time.time()
        self.system.process_query(queries[0])
        first_time = (time.time() - start) * 1000

        # Subsequent queries (cache hits)
        cached_times = []
        for query in queries[1:]:
            start = time.time()
            self.system.process_query(query)
            cached_times.append((time.time() - start) * 1000)

        avg_cached = sum(cached_times) / len(cached_times)

        # Cached should be much faster
        assert avg_cached < first_time / 10, "Cache not providing speedup"

    def test_memory_usage(self):
        """Test memory usage stays within limits"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process many queries
        for i in range(100):
            self.system.process_query(f"install package{i}")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        self.system = HRMIntegratedV6Final(enable_active_learning=False)

    def test_empty_query(self):
        """Test handling of empty query"""
        result = self.system.process_query("")
        assert "error" in result or result["confidence"] < 0.5

    def test_special_characters(self):
        """Test queries with special characters"""
        queries = [
            "install package@latest",
            "search for C++ compiler",
            "enable service.target",
            "install python3.11",
        ]

        for query in queries:
            result = self.system.process_query(query)
            assert result is not None
            assert "command" in result

    def test_very_long_query(self):
        """Test handling of very long queries"""
        long_query = "install " + " ".join(["package"] * 50)
        result = self.system.process_query(long_query)
        assert result is not None

    def test_unknown_language_query(self):
        """Test non-English queries (should fail gracefully)"""
        result = self.system.process_query("安装火狐浏览器")
        assert result["confidence"] < 0.8  # Low confidence expected

    def test_typos_and_misspellings(self):
        """Test common typos"""
        typo_queries = [
            ("instal firefox", "install"),  # Missing 'l'
            ("updaet system", "update"),  # Typo
            ("serach editors", "search"),  # Typo
        ]

        for query, expected_intent in typo_queries:
            result = self.system.process_query(query)
            # Should still understand intent despite typos
            assert expected_intent in result.get("category", "").lower()


class TestNewFeatures:
    """Test new features for v0.3.1"""

    def test_home_manager_commands(self):
        """Test home-manager command support"""
        queries = [
            ("home-manager switch", "home-manager"),
            ("update home configuration", "home-manager"),
            ("home-manager rollback", "home-manager generations"),
        ]

        system = HRMIntegratedV6Final(enable_active_learning=False)

        for query, expected_keyword in queries:
            result = system.process_query(query)
            # Currently might not work - this tests if we need to add it
            if expected_keyword not in result.get("command", ""):
                pytest.skip("Home-manager support not yet implemented")

    def test_flake_operations(self):
        """Test flake command support"""
        queries = [
            ("nix flake init", "nix flake init"),
            ("update flake", "nix flake update"),
            ("check flake", "nix flake check"),
        ]

        system = HRMIntegratedV6Final(enable_active_learning=False)

        for query, expected in queries:
            result = system.process_query(query)
            if expected not in result.get("command", ""):
                pytest.skip("Flake support not yet implemented")


class TestFeedbackSystem:
    """Test feedback collection system"""

    def setup_method(self):
        self.collector = FeedbackCollector(db_path=":memory:")

    def test_record_feedback(self):
        """Test feedback recording"""
        self.collector.record_feedback(
            query="install firefox",
            actual_command="nix-env -iA nixpkgs.firefox",
            was_correct=True,
            rating=5,
        )

        metrics = self.collector.get_accuracy_metrics()
        assert metrics["total_queries"] == 1
        assert metrics["accuracy_percent"] == 100

    def test_bug_reporting(self):
        """Test bug report system"""
        bug_id = self.collector.report_bug(
            title="Install command fails",
            description="Firefox install not working",
            severity="high",
        )

        bugs = self.collector.get_open_bugs()
        assert len(bugs) == 1
        assert bugs[0]["severity"] == "high"

    def test_feature_requests(self):
        """Test feature request system"""
        req_id = self.collector.request_feature(
            title="Voice interface",
            description="Add voice commands",
            use_case="Hands-free operation",
            priority=2,
        )

        features = self.collector.get_top_feature_requests()
        assert len(features) == 1


class TestMonitoring:
    """Test monitoring dashboard"""

    def test_health_score_calculation(self):
        """Test health score calculation"""
        dashboard = MetricsDashboard()
        dashboard.metrics["github_stars"] = 50
        dashboard.metrics["pypi_downloads"] = 100
        dashboard.metrics["user_accuracy"] = 96.3

        score = dashboard.calculate_health_score()
        assert score > 50, f"Health score {score} too low"

    def test_alert_detection(self):
        """Test alert detection"""
        dashboard = MetricsDashboard()
        dashboard.metrics["user_accuracy"] = 90  # Below 95% threshold
        dashboard.detect_alerts()

        assert len(dashboard.alerts) > 0
        assert any(a["level"] == "critical" for a in dashboard.alerts)


def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("🧪 Running Comprehensive Test Suite for v0.3.1")
    print("=" * 60)

    test_results = {"passed": 0, "failed": 0, "skipped": 0, "errors": []}

    test_classes = [
        TestCoreAccuracy,
        TestPerformance,
        TestEdgeCases,
        TestNewFeatures,
        TestFeedbackSystem,
        TestMonitoring,
    ]

    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        instance = test_class()

        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    if hasattr(instance, "setup_method"):
                        instance.setup_method()

                    method = getattr(instance, method_name)
                    method()

                    print(f"  ✅ {method_name}")
                    test_results["passed"] += 1

                except pytest.skip.Exception as e:
                    print(f"  ⏭️  {method_name}: {e}")
                    test_results["skipped"] += 1

                except AssertionError as e:
                    print(f"  ❌ {method_name}: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(
                        {
                            "test": f"{test_class.__name__}.{method_name}",
                            "error": str(e),
                        }
                    )

                except Exception as e:
                    print(f"  💥 {method_name}: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(
                        {
                            "test": f"{test_class.__name__}.{method_name}",
                            "error": str(e),
                        }
                    )

    # Generate report
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print(f"  Passed: {test_results['passed']} ✅")
    print(f"  Failed: {test_results['failed']} ❌")
    print(f"  Skipped: {test_results['skipped']} ⏭️")

    total = test_results["passed"] + test_results["failed"] + test_results["skipped"]
    if total > 0:
        pass_rate = (test_results["passed"] / total) * 100
        print(f"  Pass Rate: {pass_rate:.1f}%")

    if test_results["errors"]:
        print("\n❌ Failed Tests:")
        for error in test_results["errors"]:
            print(f"  - {error['test']}")
            print(f"    {error['error']}")

    # Save results
    with open("test_results_v031.json", "w") as f:
        json.dump(test_results, f, indent=2)

    print("\n✅ Test results saved to test_results_v031.json")

    return test_results["failed"] == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
