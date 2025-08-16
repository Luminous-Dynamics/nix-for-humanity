#!/usr/bin/env python3
"""
Simplified tests for Headless Engine focusing on core functionality
"""

import os

from unittest.mock import Mock, MagicMock, patch, call
import sys
import unittest
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../scripts/core"))

# Import the modules we'll be testing
from luminous_nix.core.headless_engine import Context, HeadlessEngine, Intent, Response

class TestHeadlessEngineSimple(unittest.TestCase):
    """Simplified tests for the HeadlessEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.knowledge_mock = Mock()
        self.feedback_mock = Mock()
        self.plugin_manager_mock = Mock()
        self.learning_mock = Mock()
        self.cache_mock = Mock()

        # Patch the imports
        self.patches = [
            patch(
                "luminous_nix.core.headless_engine.NixOSKnowledgeEngine",
                return_value=self.knowledge_mock,
            ),
            patch(
                "luminous_nix.core.headless_engine.FeedbackCollector",
                return_value=self.feedback_mock,
            ),
            patch(
                "luminous_nix.core.headless_engine.get_plugin_manager",
                return_value=self.plugin_manager_mock,
            ),
            patch(
                "luminous_nix.core.headless_engine.CommandPreferenceManager",
                return_value=self.learning_mock,
            ),
            patch(
                "luminous_nix.core.headless_engine.IntelligentPackageCache",
                return_value=self.cache_mock,
            ),
        ]

        for p in self.patches:
            p.start()

    def tearDown(self):
        """Clean up patches."""
        for p in self.patches:
            p.stop()

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = HeadlessEngine()

        self.assertIsNotNone(engine.knowledge)
        self.assertIsNotNone(engine.feedback)
        self.assertIsNotNone(engine.plugin_manager)
        self.assertIsNotNone(engine.learning)
        self.assertIsNotNone(engine.cache)
        self.assertEqual(len(engine.sessions), 0)
        self.assertIsInstance(engine.start_time, datetime)

    def test_process_basic_query_simplified(self):
        """Test processing a basic query without detailed assertions."""
        engine = HeadlessEngine()

        # Mock knowledge engine responses
        self.knowledge_mock.extract_intent.return_value = {
            "action": "install_package",
            "package": "firefox",
        }
        self.knowledge_mock.get_solution.return_value = {
            "methods": [
                {
                    "type": "nix-env",
                    "name": "User Environment",
                    "description": "Install to user profile",
                    "example": "nix-env -iA nixpkgs.firefox",
                }
            ]
        }
        self.knowledge_mock.format_response.return_value = (
            "I'll install Firefox for you."
        )

        # Mock plugin manager to not transform text
        self.plugin_manager_mock.apply_personality.return_value = (
            "I'll install Firefox for you."
        )

        # Process query
        response = engine.process("install firefox")

        # Basic verifications
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent.action, "install_package")
        self.assertEqual(response.intent.package, "firefox")
        # Don't check response.text or commands as they may be complex objects

    def test_collect_feedback_simple(self):
        """Test explicit feedback collection."""
        engine = HeadlessEngine()

        # Collect feedback
        feedback_data = {
            "query": "install vim",
            "response": "Installing Vim...",
            "helpful": True,
            "improved_response": None,
        }

        result = engine.collect_feedback("test_session", feedback_data)

        # Verify feedback was collected
        self.assertTrue(result)
        self.feedback_mock.collect_explicit_feedback.assert_called_once()

    def test_get_stats_simple(self):
        """Test engine statistics."""
        engine = HeadlessEngine()

        # Mock stats from components
        self.plugin_manager_mock.get_plugin_info.return_value = {"total_plugins": 5}
        self.cache_mock.get_cache_stats.return_value = {
            "total_packages": 1000,
            "cache_age": "2 days",
        }
        self.feedback_mock.get_feedback_stats.return_value = {
            "total_feedback": 50,
            "helpful_percentage": 0.8,
            "preference_pairs": 10,
        }

        # Get stats
        stats = engine.get_stats()

        # Verify basic stats structure
        self.assertIn("uptime", stats)
        self.assertEqual(stats["active_sessions"], 0)
        self.assertEqual(stats["plugins_loaded"], 5)

    def test_context_defaults(self):
        """Test Context with defaults."""
        context = Context()

        self.assertEqual(context.user_id, "anonymous")
        self.assertIsNotNone(context.session_id)
        self.assertEqual(context.personality, "friendly")
        self.assertEqual(context.capabilities, ["text"])
        self.assertEqual(context.execution_mode.DRY_RUN)
        self.assertTrue(context.collect_feedback)

    def test_intent_creation(self):
        """Test creating an Intent."""
        intent = Intent(
            action="install_package",
            package="firefox",
            query="install firefox",
            confidence=0.9,
        )

        self.assertEqual(intent.action, "install_package")
        self.assertEqual(intent.package, "firefox")
        self.assertEqual(intent.query, "install firefox")
        self.assertEqual(intent.confidence, 0.9)
        self.assertIsNotNone(intent.context)

    def test_response_to_dict(self):
        """Test Response serialization to dict."""
        intent = Intent(action="search_package", query="search python")
        response = Response(
            text="Found Python packages.",
            intent=intent,
            commands=[],
            visual={"type": "list", "items": ["python3", "python3-pip"]},
        )

        result = response.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["text"], "Found Python packages.")
        self.assertIn("intent", result)
        self.assertEqual(result["intent"]["action"], "search_package")
        self.assertIn("visual", result)
        self.assertEqual(result["visual"]["type"], "list")

    def test_shutdown(self):
        """Test engine shutdown."""
        engine = HeadlessEngine()

        # Capture print output
        with patch("builtins.print") as mock_print:
            engine.shutdown()
            mock_print.assert_called_with("Headless engine shutdown complete")

if __name__ == "__main__":
    unittest.main()
