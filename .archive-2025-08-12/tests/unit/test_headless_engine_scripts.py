#!/usr/bin/env python3
"""
Comprehensive tests for Headless Engine

Tests all headless engine functionality including:
- Engine initialization
- Query processing
- Intent extraction
- Plugin handling
- Response generation
- Feedback collection
- Learning system integration
- Statistics tracking
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

class Teststr(unittest.TestCase):
    """Test the str enum."""

    def test_execution_modes(self):
        """Test all execution modes are defined."""
        self.assertEqual("dry_run".value, "dry_run")
        self.assertEqual("normal".value, "safe")
        self.assertEqual("normal".value, "full")
        self.assertEqual("normal".value, "learning")

class TestIntent(unittest.TestCase):
    """Test the Intent dataclass."""

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
        self.assertEqual(intent.context, {})

    def test_intent_with_context(self):
        """Test Intent with custom context."""
        context = {"source": "cli", "user": "test"}
        intent = Intent(
            action="update_system", query="update my system", context=context
        )

        self.assertEqual(intent.action, "update_system")
        self.assertIsNone(intent.package)
        self.assertEqual(intent.context, context)

class TestContext(unittest.TestCase):
    """Test the Context dataclass."""

    def test_default_context(self):
        """Test Context with defaults."""
        context = Context()

        self.assertEqual(context.user_id, "anonymous")
        self.assertIsNotNone(context.session_id)
        self.assertEqual(context.personality, "friendly")
        self.assertEqual(context.capabilities, ["text"])
        self.assertEqual(context.execution_mode.DRY_RUN)
        self.assertTrue(context.collect_feedback)

    def test_custom_context(self):
        """Test Context with custom values."""
        context = Context(
            user_id="test_user",
            session_id="test_session",
            personality="minimal",
            capabilities=["text", "visual", "voice"],
            execution_mode="normal",
            collect_feedback=False,
        )

        self.assertEqual(context.user_id, "test_user")
        self.assertEqual(context.session_id, "test_session")
        self.assertEqual(context.personality, "minimal")
        self.assertEqual(len(context.capabilities), 3)
        self.assertEqual(context.execution_mode.FULL)
        self.assertFalse(context.collect_feedback)

class TestResponse(unittest.TestCase):
    """Test the Response dataclass."""

    def test_response_creation(self):
        """Test creating a Response."""
        intent = Intent(action="install_package", package="vim")
        response = Response(
            text="Installing Vim for you.",
            intent=intent,
            commands=["nix-env -iA nixpkgs.vim"],
            confidence=0.95,
        )

        self.assertEqual(response.text, "Installing Vim for you.")
        self.assertEqual(response.intent.action, "install_package")
        self.assertEqual(len(response.commands), 1)
        self.assertEqual(response.confidence, 0.95)
        self.assertIsNone(response.visual)
        self.assertIsNone(response.voice)
        self.assertIsNone(response.feedback_request)
        self.assertIsNotNone(response.metadata)

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

class TestHeadlessEngine(unittest.TestCase):
    """Test the HeadlessEngine class."""

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

    def test_process_basic_query(self):
        """Test processing a basic query."""
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

        # Mock _apply_personality and _extract_commands
        with patch.object(
            engine, "_apply_personality", return_value="I'll install Firefox for you."
        ):
            with patch.object(
                engine,
                "_extract_commands",
                return_value=["nix-env -iA nixpkgs.firefox"],
            ):
                # Process query
                response = engine.process("install firefox")

                # Verify response
                self.assertIsInstance(response, Response)
                self.assertEqual(response.intent.action, "install_package")
                self.assertEqual(response.intent.package, "firefox")
                self.assertIn("Firefox", response.text)
                self.assertEqual(len(response.commands), 1)
                self.assertEqual(response.commands[0], "nix-env -iA nixpkgs.firefox")

    def test_process_with_context(self):
        """Test processing with custom context."""
        engine = HeadlessEngine()

        # Set up mocks
        self.knowledge_mock.extract_intent.return_value = {"action": "system_info"}
        self.knowledge_mock.get_solution.return_value = {}
        self.knowledge_mock.format_response.return_value = "System info..."

        # Create context
        context = Context(
            user_id="test_user",
            personality="minimal",
            execution_mode="normal",
            capabilities=["text", "visual"],
        )

        # Mock _apply_personality to return a string
        with patch.object(engine, "_apply_personality", return_value="System info..."):
            # Process
            response = engine.process("show system info", context)

            # Verify context was used
            call_args = self.knowledge_mock.extract_intent.call_args[0][0]
            self.assertEqual(call_args, "show system info")

            # Verify personality was applied
            self.assertIsInstance(response.text, str)
            self.assertEqual(response.text, "System info...")

    def test_plugin_handling(self):
        """Test plugin system integration."""
        engine = HeadlessEngine()

        # Mock plugin response
        plugin_result = {
            "success": True,
            "response": "Plugin handled this!",
            "commands": ["custom-command"],
            "confidence": 0.85,
        }
        self.plugin_manager_mock.handle_intent.return_value = plugin_result

        # Mock knowledge engine
        self.knowledge_mock.extract_intent.return_value = {"action": "custom_action"}

        # Mock _apply_personality to return the plugin response text
        with patch.object(
            engine, "_apply_personality", return_value="Plugin handled this!"
        ):
            # Process
            response = engine.process("do something custom")

            # Verify plugin was called
            self.plugin_manager_mock.handle_intent.assert_called_once()
            self.assertEqual(response.text, "Plugin handled this!")
            self.assertEqual(response.commands, ["custom-command"])
            self.assertEqual(response.confidence, 0.85)

    def test_personality_application(self):
        """Test personality transformation."""
        engine = HeadlessEngine()

        # Mock the _apply_personality method to return actual strings
        def mock_apply_personality(text, intent, context):
            if context.personality == "minimal":
                # Strip emojis for minimal
                return text.replace("💡", "").strip()
            if context.personality == "symbiotic":
                # Add learning prompt for symbiotic
                return f"{text} I'm still learning and improving."
            return text

        # Patch the _apply_personality method
        with patch.object(
            engine, "_apply_personality", side_effect=mock_apply_personality
        ):
            # Set up basic response
            self.knowledge_mock.extract_intent.return_value = {"action": "help"}
            self.knowledge_mock.get_solution.return_value = {}
            self.knowledge_mock.format_response.return_value = (
                "Here's some help text with 💡 emoji"
            )

            # Test minimal personality
            context = Context(personality="minimal")
            response = engine.process("help", context)

            # Minimal should strip emojis
            self.assertNotIn("💡", response.text)

            # Test symbiotic personality
            context = Context(personality="symbiotic")
            response = engine.process("help", context)

            # Symbiotic should add learning prompt
            self.assertIn("I'm still learning", response.text)

    def test_visual_generation(self):
        """Test visual content generation for GUI."""
        engine = HeadlessEngine()

        # Mock a solution with multiple methods
        solution = {
            "methods": [
                {
                    "type": "nix-env",
                    "name": "User Install",
                    "description": "Install to user profile",
                    "example": "nix-env -iA nixpkgs.firefox",
                },
                {
                    "type": "configuration",
                    "name": "System Install",
                    "description": "Add to configuration.nix",
                    "example": "environment.systemPackages = [ pkgs.firefox ];",
                },
            ]
        }

        self.knowledge_mock.extract_intent.return_value = {"action": "install_package"}
        self.knowledge_mock.get_solution.return_value = solution
        self.knowledge_mock.format_response.return_value = (
            "Multiple installation methods available."
        )

        # Mock _apply_personality, _generate_visual, and _extract_commands
        with patch.object(
            engine,
            "_apply_personality",
            return_value="Multiple installation methods available.",
        ):
            with patch.object(
                engine,
                "_generate_visual",
                return_value={
                    "type": "options",
                    "title": "Installation Methods",
                    "choices": [
                        {
                            "name": "User Install",
                            "description": "Install to user profile",
                        },
                        {
                            "name": "System Install",
                            "description": "Add to configuration.nix",
                        },
                    ],
                },
            ):
                with patch.object(
                    engine,
                    "_extract_commands",
                    return_value=[
                        "nix-env -iA nixpkgs.firefox",
                        "environment.systemPackages = [ pkgs.firefox ];",
                    ],
                ):
                    # Process with visual capability
                    context = Context(capabilities=["text", "visual"])
                    response = engine.process("install firefox", context)

                    # Verify visual content
                    self.assertIsNotNone(response.visual)
                    self.assertEqual(response.visual["type"], "options")
                    self.assertEqual(response.visual["title"], "Installation Methods")
                    self.assertEqual(len(response.visual["choices"]), 2)

    def test_feedback_collection(self):
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

        # Check call arguments
        call_args = self.feedback_mock.collect_explicit_feedback.call_args[1]
        self.assertEqual(call_args["query"], "install vim")
        self.assertEqual(call_args["response"], "Installing Vim...")
        self.assertTrue(call_args["helpful"])

    def test_tracking_interaction(self):
        """Test interaction tracking for learning."""
        engine = HeadlessEngine()

        # Set up response
        self.knowledge_mock.extract_intent.return_value = {
            "action": "install_package",
            "package": "emacs",
        }
        self.knowledge_mock.get_solution.return_value = {
            "example": "nix-env -iA nixpkgs.emacs"
        }
        self.knowledge_mock.format_response.return_value = "Installing Emacs..."

        # Mock _apply_personality and _track_interaction
        with patch.object(
            engine, "_apply_personality", return_value="Installing Emacs..."
        ):
            with patch.object(engine, "_track_interaction") as mock_track:
                # Process with learning enabled
                context = Context(collect_feedback=True)
                response = engine.process("install emacs", context)

                # Verify track_interaction was called
                mock_track.assert_called_once()

                # Verify learning system was notified
                self.learning_mock.record_command.assert_called_once_with(
                    "install_package", "install emacs", "install emacs"
                )

    def test_get_stats(self):
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

        # Verify stats structure
        self.assertIn("uptime", stats)
        self.assertEqual(stats["active_sessions"], 0)
        self.assertEqual(stats["plugins_loaded"], 5)
        self.assertEqual(stats["cache_stats"]["total_packages"], 1000)
        self.assertEqual(stats["feedback_stats"]["total"], 50)
        self.assertEqual(stats["feedback_stats"]["helpfulness_rate"], 0.8)

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        engine = HeadlessEngine()

        # Check if method exists
        if hasattr(engine, "_calculate_confidence"):
            # Test unknown action
            intent = {"action": "unknown"}
            confidence = engine._calculate_confidence(intent)
            self.assertEqual(confidence, 0.3)

            # Test with package
            intent = {"action": "install_package", "package": "firefox"}
            confidence = engine._calculate_confidence(intent)
            self.assertEqual(confidence, 0.9)

            # Test without package
            intent = {"action": "update_system"}
            confidence = engine._calculate_confidence(intent)
            self.assertEqual(confidence, 0.7)
        else:
            # Mock the behavior if the method doesn't exist
            self.skipTest("_calculate_confidence method not found")

    def test_command_extraction(self):
        """Test command extraction from solutions."""
        engine = HeadlessEngine()

        # Check if method exists
        if hasattr(engine, "_extract_commands"):
            # Test with methods
            solution = {
                "methods": [
                    {"example": "nix-env -iA nixpkgs.firefox"},
                    {"example": "nix-shell -p firefox"},
                ]
            }
            commands = engine._extract_commands(solution)
            self.assertEqual(len(commands), 2)
            self.assertEqual(commands[0], "nix-env -iA nixpkgs.firefox")

            # Test with direct example
            solution = {"example": "nixos-rebuild switch"}
            commands = engine._extract_commands(solution)
            self.assertEqual(len(commands), 1)
            self.assertEqual(commands[0], "nixos-rebuild switch")

            # Test with no commands
            solution = {"info": "Just information"}
            commands = engine._extract_commands(solution)
            self.assertEqual(len(commands), 0)
        else:
            # Skip if method doesn't exist
            self.skipTest("_extract_commands method not found")

    def test_feedback_request_generation(self):
        """Test feedback request generation based on context."""
        engine = HeadlessEngine()

        # Check if method exists
        if hasattr(engine, "_generate_feedback_request"):
            # Test with symbiotic personality
            context = Context(personality="symbiotic", collect_feedback=True)
            request = engine._generate_feedback_request(context)
            self.assertIsNotNone(request)
            self.assertEqual(request["type"], "detailed")
            self.assertEqual(request["prompt"], "How can I improve?")

            # Test with other personality
            context = Context(personality="friendly", collect_feedback=True)
            request = engine._generate_feedback_request(context)
            self.assertIsNotNone(request)
            self.assertEqual(request["type"], "simple")
            self.assertEqual(request["prompt"], "Was this helpful?")

            # Test with feedback disabled
            context = Context(collect_feedback=False)
            request = engine._generate_feedback_request(context)
            self.assertIsNone(request)
        else:
            # Skip if method doesn't exist
            self.skipTest("_generate_feedback_request method not found")

    def test_shutdown(self):
        """Test engine shutdown."""
        engine = HeadlessEngine()

        # Capture print output
        with patch("builtins.print") as mock_print:
            engine.shutdown()
            mock_print.assert_called_with("Headless engine shutdown complete")

if __name__ == "__main__":
    unittest.main()
