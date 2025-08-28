#!/usr/bin/env python3
"""
🌍 Real-World Scenario Testing
Tests the AI interface generation with realistic use cases
"""

import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from learning_persistence import ContinuousImprovementEngine, LearningDatabase
from nl_interface_builder import NLInterfaceBuilder, UserContext


class RealWorldTestSuite:
    """Tests real-world scenarios across different user personas"""

    def __init__(self):
        self.builder = NLInterfaceBuilder()
        self.db = LearningDatabase(":memory:")  # In-memory for testing
        self.learning = ContinuousImprovementEngine(self.db)
        self.results = defaultdict(list)

    def run_persona_tests(self) -> dict:
        """Run tests for all personas"""

        print("\n" + "=" * 60)
        print("🌍 REAL-WORLD SCENARIO TESTING")
        print("=" * 60)

        personas = {
            "developer": self.test_developer_persona(),
            "data_scientist": self.test_data_scientist_persona(),
            "sysadmin": self.test_sysadmin_persona(),
            "writer": self.test_writer_persona(),
            "beginner": self.test_beginner_persona(),
            "power_user": self.test_power_user_persona(),
        }

        # Analyze results
        self.analyze_results()

        return personas

    def test_developer_persona(self) -> list[dict]:
        """Test developer-focused scenarios"""

        print("\n👨‍💻 DEVELOPER PERSONA")
        print("-" * 40)

        context = UserContext(
            user_id="dev_user",
            expertise_level="expert",
            device_type="desktop",
            preferences={"theme": "dark", "density": "dense"},
        )

        scenarios = [
            "Create a code editor with syntax highlighting, line numbers, and a dark theme",
            "Build a git interface showing staged files, diff view, and commit message input",
            "Show me a terminal emulator with tabs and command history",
            "Design a REST API testing tool with request builder and response viewer",
            "Create a database query interface with schema browser and result table",
            "Make a debugging dashboard with breakpoints, variables, and call stack",
        ]

        return self._test_scenarios(scenarios, context, "developer")

    def test_data_scientist_persona(self) -> list[dict]:
        """Test data science scenarios"""

        print("\n📊 DATA SCIENTIST PERSONA")
        print("-" * 40)

        context = UserContext(
            user_id="data_user",
            expertise_level="expert",
            device_type="desktop",
            preferences={"visualization": "rich", "interactivity": "high"},
        )

        scenarios = [
            "Create a data visualization dashboard with multiple interactive charts",
            "Build a machine learning training monitor showing loss curves and metrics",
            "Design a dataset explorer with filters, sorting, and statistical summaries",
            "Show me a correlation matrix heatmap with zoom and pan",
            "Create a feature engineering workspace with transformations and preview",
            "Make an A/B test results viewer with statistical significance",
        ]

        return self._test_scenarios(scenarios, context, "data_scientist")

    def test_sysadmin_persona(self) -> list[dict]:
        """Test system administrator scenarios"""

        print("\n🔧 SYSADMIN PERSONA")
        print("-" * 40)

        context = UserContext(
            user_id="admin_user",
            expertise_level="expert",
            device_type="desktop",
            preferences={"updates": "real-time", "density": "high"},
        )

        scenarios = [
            "Create a server monitoring dashboard with CPU, memory, and disk usage",
            "Build a log viewer with search, filtering, and severity highlighting",
            "Show system alerts in a real-time feed with acknowledgment",
            "Design a network traffic monitor with bandwidth graphs",
            "Create a service health dashboard with uptime and response times",
            "Make a backup status interface with schedule and history",
        ]

        return self._test_scenarios(scenarios, context, "sysadmin")

    def test_writer_persona(self) -> list[dict]:
        """Test creative writer scenarios"""

        print("\n✍️ WRITER PERSONA")
        print("-" * 40)

        context = UserContext(
            user_id="writer_user",
            expertise_level="intermediate",
            device_type="desktop",
            preferences={"style": "minimal", "distractions": "none"},
        )

        scenarios = [
            "Create a distraction-free writing environment with word count",
            "Build a markdown editor with live preview",
            "Show me a zen mode for focused writing",
            "Design a story outline tool with chapters and scenes",
            "Create a character development tracker",
            "Make a writing goals dashboard with daily targets",
        ]

        return self._test_scenarios(scenarios, context, "writer")

    def test_beginner_persona(self) -> list[dict]:
        """Test beginner-friendly scenarios"""

        print("\n👶 BEGINNER PERSONA")
        print("-" * 40)

        context = UserContext(
            user_id="beginner_user",
            expertise_level="beginner",
            device_type="desktop",
            preferences={"guidance": "high", "simplicity": "maximum"},
        )

        scenarios = [
            "Show me my files",
            "I want to write a document",
            "Help me organize my photos",
            "Create something to track my tasks",
            "Make a simple calculator",
            "Show me the weather",
        ]

        return self._test_scenarios(scenarios, context, "beginner")

    def test_power_user_persona(self) -> list[dict]:
        """Test power user complex scenarios"""

        print("\n🚀 POWER USER PERSONA")
        print("-" * 40)

        context = UserContext(
            user_id="power_user",
            expertise_level="expert",
            device_type="desktop",
            preferences={"customization": "maximum", "features": "all"},
        )

        scenarios = [
            "Create a multi-panel IDE with file tree, editor, terminal, and output in a customizable layout with draggable panels",
            "Build a financial dashboard with real-time stock charts, portfolio analysis, news feed, and trading interface",
            "Design a project management system with kanban board, gantt chart, resource allocation, and time tracking",
            "Show me a system monitoring suite with process manager, network analyzer, disk usage, and performance profiler",
            "Create a data pipeline builder with visual flow editor, transformation nodes, and execution monitoring",
            "Make a multi-modal AI playground with text, image, and code generation in tabbed interface",
        ]

        return self._test_scenarios(scenarios, context, "power_user")

    def _test_scenarios(
        self, scenarios: list[str], context: UserContext, persona: str
    ) -> list[dict]:
        """Test a set of scenarios"""

        results = []

        for scenario in scenarios:
            print(f"\n📝 Testing: {scenario[:50]}...")

            try:
                start_time = time.time()

                # Generate interface
                interface = self.builder.build_interface(scenario, context)
                generation_time = (time.time() - start_time) * 1000

                # Analyze result
                success = len(interface.components) > 0
                complexity = self._calculate_complexity(interface)
                accuracy = self._estimate_accuracy(scenario, interface)

                result = {
                    "persona": persona,
                    "scenario": scenario,
                    "success": success,
                    "generation_time": generation_time,
                    "components": len(interface.components),
                    "complexity": complexity,
                    "accuracy": accuracy,
                    "layout": interface.layout.get("type"),
                    "theme": interface.theme.get("mode"),
                }

                # Display result
                print(f"   ✅ Success: {success}")
                print(f"   ⏱️ Time: {generation_time:.2f}ms")
                print(f"   📦 Components: {len(interface.components)}")
                print(f"   🎯 Accuracy: {accuracy:.0%}")

                results.append(result)
                self.results[persona].append(result)

            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append(
                    {
                        "persona": persona,
                        "scenario": scenario,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    def _calculate_complexity(self, interface) -> str:
        """Calculate interface complexity"""

        component_count = len(interface.components)

        if component_count <= 1:
            return "simple"
        if component_count <= 3:
            return "moderate"
        return "complex"

    def _estimate_accuracy(self, request: str, interface) -> float:
        """Estimate how well the interface matches the request"""

        request_lower = request.lower()
        score = 0.5  # Base score

        # Check for key terms in request
        if "dark" in request_lower and interface.theme.get("mode") == "dark":
            score += 0.1
        if "simple" in request_lower and len(interface.components) <= 2:
            score += 0.1
        if "dashboard" in request_lower and interface.layout.get("type") == "grid":
            score += 0.1
        if "editor" in request_lower and any(
            c.dna.purpose == "editor" for c in interface.components
        ):
            score += 0.1
        if "real-time" in request_lower and any(
            "realtime" in str(c.dna.behaviors) for c in interface.components
        ):
            score += 0.1

        return min(score, 1.0)

    def analyze_results(self):
        """Analyze test results across all personas"""

        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)

        for persona, results in self.results.items():
            if not results:
                continue

            success_rate = sum(1 for r in results if r.get("success", False)) / len(
                results
            )
            avg_time = sum(r.get("generation_time", 0) for r in results) / len(results)
            avg_components = sum(r.get("components", 0) for r in results) / len(results)
            avg_accuracy = sum(r.get("accuracy", 0) for r in results) / len(results)

            print(f"\n{persona.upper()} PERSONA:")
            print(f"  Success Rate: {success_rate:.0%}")
            print(f"  Avg Generation Time: {avg_time:.2f}ms")
            print(f"  Avg Components: {avg_components:.1f}")
            print(f"  Avg Accuracy: {avg_accuracy:.0%}")

    def test_edge_cases(self):
        """Test edge cases and error handling"""

        print("\n" + "=" * 60)
        print("🔥 EDGE CASE TESTING")
        print("=" * 60)

        edge_cases = [
            # Ambiguous
            ("Make something cool", "ambiguous"),
            ("I need a thing", "vague"),
            ("Create interface", "underspecified"),
            # Contradictory
            ("Create a dark light theme", "contradictory"),
            ("Make it big and small", "contradictory"),
            ("Simple complex dashboard", "contradictory"),
            # Very complex
            (
                "Create a dashboard with forms, charts, tables, real-time updates, filters, search, export, import, and make it responsive with dark mode and accessibility",
                "complex",
            ),
            # Typos
            ("Craete a dashbord for montering", "typos"),
            ("Bild a frm with inpot feelds", "typos"),
            # Empty/Invalid
            ("", "empty"),
            ("123 456 789", "nonsense"),
            ("!@#$%^&*()", "special_chars"),
        ]

        for test_input, case_type in edge_cases:
            print(f"\n🧪 Testing {case_type}: '{test_input[:30]}...'")

            try:
                context = UserContext(user_id="test", expertise_level="intermediate")
                interface = self.builder.build_interface(test_input, context)
                print("   ✅ Handled gracefully")
                print(f"   Generated: {len(interface.components)} components")
            except Exception as e:
                print(f"   ⚠️ Exception: {e}")

    def test_performance_scaling(self):
        """Test performance with increasing complexity"""

        print("\n" + "=" * 60)
        print("⚡ PERFORMANCE SCALING TEST")
        print("=" * 60)

        context = UserContext(user_id="perf_test", expertise_level="intermediate")

        complexity_levels = [
            ("Simple", "Create a button"),
            ("Moderate", "Create a form with three fields"),
            ("Complex", "Create a dashboard with charts and tables"),
            (
                "Very Complex",
                "Create a multi-panel IDE with file browser, editor, terminal, debugger, and output",
            ),
        ]

        for level, request in complexity_levels:
            print(f"\n{level}: {request[:40]}...")

            times = []
            for _ in range(3):  # Run 3 times for average
                start = time.time()
                interface = self.builder.build_interface(request, context)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)

            avg_time = sum(times) / len(times)
            print(f"   Avg time: {avg_time:.2f}ms")
            print(f"   Components: {len(interface.components)}")


def main():
    """Run all real-world tests"""

    suite = RealWorldTestSuite()

    # Run persona tests
    suite.run_persona_tests()

    # Run edge case tests
    suite.test_edge_cases()

    # Run performance tests
    suite.test_performance_scaling()

    print("\n" + "=" * 60)
    print("✅ REAL-WORLD TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
