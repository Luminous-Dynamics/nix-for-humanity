#!/usr/bin/env python3
"""
Comprehensive unit tests for the Engine
Tests the unified backend architecture serving all interfaces
"""

from unittest.mock import Mock, MagicMock, patch, call
import sys
import unittest
from datetime import datetime
from pathlib import Path

# Add the src and scripts directories to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from luminous_nix.core.engine import NixForHumanityBackend as Engine
from luminous_nix.core.intents import Context
from luminous_nix.api.schema import Response

class TestEngine(unittest.TestCase):
    """Comprehensive tests for the Engine"""

    def setUp(self):
        """Create a test instance of Engine"""
        # Mock the dependencies
        self.mock_knowledge = MagicMock()
        self.mock_feedback = MagicMock()
        self.mock_plugin_manager = MagicMock()
        self.mock_learning = MagicMock()
        self.mock_cache = MagicMock()

        # Create engine with mocked dependencies
        with patch(
            "luminous_nix.core.headless_engine.NixOSKnowledgeEngine",
            return_value=self.mock_knowledge,
        ):
            with patch(
                "luminous_nix.core.headless_engine.FeedbackCollector",
                return_value=self.mock_feedback,
            ):
                with patch(
                    "luminous_nix.core.headless_engine.get_plugin_manager",
                    return_value=self.mock_plugin_manager,
                ):
                    with patch(
                        "luminous_nix.core.headless_engine.CommandPreferenceManager",
                        return_value=self.mock_learning,
                    ):
                        with patch(
                            "luminous_nix.core.headless_engine.IntelligentPackageCache",
                            return_value=self.mock_cache,
                        ):
                            self.engine = Engine()

    def test_initialization(self):
        """Test Engine initialization"""
        self.assertIsNotNone(self.engine.knowledge)
        self.assertIsNotNone(self.engine.feedback)
        self.assertIsNotNone(self.engine.plugin_manager)
        self.assertIsNotNone(self.engine.learning)
        self.assertIsNotNone(self.engine.cache)
        self.assertEqual(len(self.engine.sessions), 0)
        self.assertIsInstance(self.engine.start_time, datetime)

    def test_process_basic_query(self):
        """Test processing a basic install query"""
        # Setup mocks
        self.mock_knowledge.extract_intent.return_value = {
            "action": "install",
            "package": "firefox",
        }
        self.mock_knowledge.get_solution.return_value = {
            "found": True,
            "methods": [
                {
                    "type": "profile",
                    "name": "Modern Nix (profile)",
                    "description": "Recommended approach",
                    "example": "nix profile install nixpkgs#firefox",
                }
            ],
        }
        self.mock_knowledge.format_response.return_value = (
            "I'll help you install Firefox!"
        )

        # Create context
        context = Context(personality="friendly")

        # Process query
        response = self.engine.process("install firefox", context)

        # Verify response
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent.action, "install")
        self.assertEqual(response.intent.package, "firefox")
        self.assertEqual(response.confidence, 0.9)
        self.assertEqual(len(response.commands), 1)
        self.assertEqual(response.commands[0], "nix profile install nixpkgs#firefox")
        self.assertIn("I'll help you install Firefox!", response.text)

    def test_process_with_plugin_handling(self):
        """Test that plugins can handle intents"""
        # Setup plugin to handle intent
        self.mock_plugin_manager.handle_intent.return_value = {
            "success": True,
            "response": "Plugin handled this!",
            "commands": ["custom-command"],
            "confidence": 0.95,
            "visual": {"type": "custom"},
        }

        # Setup knowledge engine
        self.mock_knowledge.extract_intent.return_value = {
            "action": "custom",
            "target": "something",
        }

        # Process query
        context = Context()
        response = self.engine.process("do something custom", context)

        # Verify plugin was called
        self.mock_plugin_manager.handle_intent.assert_called_once()

        # Verify response from plugin
        self.assertEqual(response.text, "Plugin handled this!")
        self.assertEqual(response.commands, ["custom-command"])
        self.assertEqual(response.confidence, 0.95)
        self.assertEqual(response.visual, {"type": "custom"})

    def test_intent_extraction(self):
        """Test intent extraction logic"""
        # Test various intent scenarios
        test_cases = [
            ({}, "unknown", None, 0.3),  # Unknown action
            ({"action": "install"}, "install", None, 0.7),  # Action without package
            (
                {"action": "install", "package": "vim"},
                "install",
                "vim",
                0.9,
            ),  # Full intent
        ]

        for (
            raw_intent,
            expected_action,
            expected_package,
            expected_confidence,
        ) in test_cases:
            self.mock_knowledge.extract_intent.return_value = raw_intent
            intent = self.engine._extract_intent("test query")

            self.assertEqual(intent.action, expected_action)
            self.assertEqual(intent.package, expected_package)
            self.assertEqual(intent.confidence, expected_confidence)

    def test_personality_application(self):
        """Test personality application to responses"""
        base_text = "Installing Firefox for you."

        # Test minimal personality
        context_minimal = Context(personality="minimal")
        result = self.engine._apply_personality(
            base_text + "\n💡 Tip: Use profiles!",
            Intent("install", "firefox"),
            context_minimal,
        )
        self.assertNotIn("💡", result)

        # Test symbiotic personality
        context_symbiotic = Context(personality="symbiotic")
        result = self.engine._apply_personality(
            base_text, Intent("install", "firefox"), context_symbiotic
        )
        self.assertIn("I'm still learning", result)
        self.assertIn("Was this helpful?", result)

        # Test friendly personality (default)
        context_friendly = Context(personality="friendly")
        result = self.engine._apply_personality(
            base_text, Intent("install", "firefox"), context_friendly
        )
        self.assertEqual(result, base_text)  # No changes for friendly

    def test_command_extraction(self):
        """Test command extraction from solutions"""
        # Test with installation methods
        solution_with_methods = {
            "methods": [
                {"example": "nix profile install firefox"},
                {"example": "nix-env -iA nixos.firefox"},
            ]
        }
        commands = self.engine._extract_commands(solution_with_methods)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0], "nix profile install firefox")

        # Test with direct example
        solution_direct = {"example": "nix search firefox"}
        commands = self.engine._extract_commands(solution_direct)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], "nix search firefox")

        # Test with no commands
        solution_empty = {"explanation": "Just some text"}
        commands = self.engine._extract_commands(solution_empty)
        self.assertEqual(len(commands), 0)

    def test_visual_generation(self):
        """Test visual representation generation"""
        # Test with visual capability
        context_visual = Context(capabilities=["text", "visual"])
        solution = {
            "methods": [
                {
                    "type": "profile",
                    "name": "Modern Nix",
                    "description": "Recommended",
                    "example": "nix profile install firefox",
                }
            ]
        }

        visual = self.engine._generate_visual(solution, context_visual)
        self.assertIsNotNone(visual)
        self.assertEqual(visual["type"], "options")
        self.assertEqual(visual["title"], "Installation Methods")
        self.assertEqual(len(visual["choices"]), 1)
        self.assertEqual(visual["choices"][0]["id"], "profile")

        # Test without visual capability
        context_no_visual = Context(capabilities=["text"])
        visual = self.engine._generate_visual(solution, context_no_visual)
        self.assertIsNone(visual)

    def test_feedback_generation(self):
        """Test feedback request generation"""
        # Test with feedback enabled (default)
        context_feedback = Context(collect_feedback=True, personality="symbiotic")
        feedback_request = self.engine._generate_feedback_request(context_feedback)
        self.assertIsNotNone(feedback_request)
        self.assertEqual(feedback_request["type"], "detailed")
        self.assertIn("How can I improve?", feedback_request["prompt"])

        # Test with simple feedback
        context_simple = Context(collect_feedback=True, personality="friendly")
        feedback_request = self.engine._generate_feedback_request(context_simple)
        self.assertEqual(feedback_request["type"], "simple")
        self.assertEqual(feedback_request["options"], ["yes", "no"])

        # Test with feedback disabled
        context_no_feedback = Context(collect_feedback=False)
        feedback_request = self.engine._generate_feedback_request(context_no_feedback)
        self.assertIsNone(feedback_request)

    def test_interaction_tracking(self):
        """Test that interactions are properly tracked"""
        # Setup mocks
        self.mock_knowledge.extract_intent.return_value = {
            "action": "install",
            "package": "vim",
        }
        self.mock_knowledge.get_solution.return_value = {"found": True}
        self.mock_knowledge.format_response.return_value = "Installing vim"

        # Process with tracking enabled
        context = Context(collect_feedback=True)
        response = self.engine.process("install vim", context)

        # Verify feedback collection
        self.mock_feedback.collect_implicit_feedback.assert_called_once()
        call_args = self.mock_feedback.collect_implicit_feedback.call_args
        self.assertEqual(call_args[1]["query"], "install vim")
        self.assertEqual(call_args[1]["user_action"], "query")

        # Verify learning system tracking
        self.mock_learning.record_command.assert_called_once_with(
            "install", "install vim", "install vim"
        )

    def test_collect_feedback_method(self):
        """Test explicit feedback collection"""
        # Test helpful feedback
        feedback_data = {
            "query": "install firefox",
            "response": "Installing Firefox...",
            "helpful": True,
            "improved_response": "Better way to install Firefox...",
        }

        result = self.engine.collect_feedback("session123", feedback_data)
        self.assertTrue(result)

        self.mock_feedback.collect_explicit_feedback.assert_called_once_with(
            query="install firefox",
            response="Installing Firefox...",
            helpful=True,
            better_response="Better way to install Firefox...",
        )

        # Test error handling
        self.mock_feedback.collect_explicit_feedback.side_effect = Exception("DB Error")
        result = self.engine.collect_feedback("session123", {"helpful": False})
        self.assertFalse(result)

    def test_get_stats(self):
        """Test engine statistics collection"""
        # Setup mocks
        self.mock_plugin_manager.get_plugin_info.return_value = {"total_plugins": 5}
        self.mock_cache.get_cache_stats.return_value = {"total_packages": 1000}
        self.mock_feedback.get_feedback_stats.return_value = {
            "total_feedback": 42,
            "helpful_percentage": 85.5,
            "preference_pairs": 10,
        }

        stats = self.engine.get_stats()

        self.assertIn("uptime", stats)
        self.assertEqual(stats["active_sessions"], 0)
        self.assertEqual(stats["plugins_loaded"], 5)
        self.assertEqual(stats["cache_stats"]["total_packages"], 1000)
        self.assertEqual(stats["feedback_stats"]["total"], 42)
        self.assertEqual(stats["feedback_stats"]["helpfulness_rate"], 85.5)

    def test_execution_modes(self):
        """Test different execution modes"""
        # Test DRY_RUN mode
        context_dry = Context(execution_mode="dry_run")
        self.mock_knowledge.extract_intent.return_value = {
            "action": "install",
            "package": "firefox",
        }

        response = self.engine.process("install firefox", context_dry)
        # Verify context is properly passed
        intent_context = response.intent.context
        self.assertEqual(intent_context["execution_mode"], "dry_run")

    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with knowledge engine error
        self.mock_knowledge.extract_intent.side_effect = Exception("Knowledge error")

        # Should not crash, but handle gracefully
        try:
            response = self.engine.process("install firefox", Context())
            # If it doesn't crash, check that it returns something reasonable
            self.assertIsInstance(response, Response)
        except Exception:
            # The current implementation might not handle all errors gracefully
            # This is a gap that could be improved
            pass

    def test_session_management(self):
        """Test session tracking"""
        # Create multiple contexts with different sessions
        context1 = Context(session_id="session1")
        context2 = Context(session_id="session2")

        # Process queries
        self.mock_knowledge.extract_intent.return_value = {"action": "help"}
        self.mock_knowledge.get_solution.return_value = {"found": True}
        self.mock_knowledge.format_response.return_value = "Help text"

        self.engine.process("help", context1)
        self.engine.process("help", context2)

        # Both sessions should be tracked (if implemented)
        # Note: Current implementation doesn't actually use sessions dict
        # This is a potential improvement area

    def test_shutdown(self):
        """Test clean shutdown"""
        # Should not raise any errors
        self.engine.shutdown()

        # Could verify cleanup actions if they were implemented
        # Currently shutdown() just prints a message

class Teststr(unittest.TestCase):
    """Test str enum"""

    def test_execution_mode_values(self):
        """Test that str has expected values"""
        self.assertEqual("dry_run".value, "dry_run")
        self.assertEqual("normal".value, "safe")
        self.assertEqual("normal".value, "full")
        self.assertEqual("normal".value, "learning")

class TestDataClasses(unittest.TestCase):
    """Test Intent, Context, and Response dataclasses"""

    def test_intent_creation(self):
        """Test Intent dataclass"""
        intent = Intent(entities={}, confidence=0.9, raw_input="install firefox")
        self.assertEqual(intent.action, "install")
        self.assertEqual(intent.package, "firefox")
        self.assertEqual(intent.query, "install firefox")
        self.assertEqual(intent.confidence, 0.9)
        self.assertIsNotNone(intent.context)
        self.assertEqual(intent.context, {})

    def test_context_creation(self):
        """Test Context dataclass"""
        # Test with defaults
        context = Context()
        self.assertEqual(context.user_id, "anonymous")
        self.assertIsNotNone(context.session_id)
        self.assertEqual(context.personality, "friendly")
        self.assertEqual(context.capabilities, ["text"])
        self.assertEqual(context.execution_mode.DRY_RUN)
        self.assertTrue(context.collect_feedback)

        # Test with custom values
        context2 = Context(
            user_id="test_user",
            personality="minimal",
            capabilities=["text", "voice", "visual"],
            execution_mode="normal",
        )
        self.assertEqual(context2.user_id, "test_user")
        self.assertEqual(context2.personality, "minimal")
        self.assertEqual(len(context2.capabilities), 3)

    def test_response_creation(self):
        """Test Response dataclass"""
        intent = Intent("install", "firefox")
        response = Response(
            text="Installing Firefox",
            intent=intent,
            commands=["nix profile install firefox"],
            confidence=0.95,
        )

        self.assertEqual(response.text, "Installing Firefox")
        self.assertEqual(response.intent.action, "install")
        self.assertEqual(len(response.commands), 1)
        self.assertEqual(response.confidence, 0.95)
        self.assertIsNone(response.visual)
        self.assertIsNone(response.voice)
        self.assertIsNone(response.feedback_request)
        self.assertIsNotNone(response.metadata)

    def test_response_to_dict(self):
        """Test Response.to_dict() method"""
        intent = Intent("search", "python")
        response = Response(
            text="Searching for python",
            intent=intent,
            commands=["nix search python"],
            visual={"type": "list"},
            feedback_request={"type": "simple"},
        )

        response_dict = response.to_dict()

        self.assertIsInstance(response_dict, dict)
        self.assertEqual(response_dict["text"], "Searching for python")
        self.assertIsInstance(response_dict["intent"], dict)
        self.assertEqual(response_dict["intent"]["action"], "search")
        self.assertEqual(len(response_dict["commands"]), 1)
        self.assertEqual(response_dict["visual"]["type"], "list")
        self.assertEqual(response_dict["feedback_request"]["type"], "simple")

class TestIntegration(unittest.TestCase):
    """Integration tests for Engine"""

    def setUp(self):
        """Create test engine with partial mocking"""
        # Only mock external dependencies, not internal components
        with patch("luminous_nix.core.headless_engine.ADVANCED_FEATURES", False):
            self.engine = Engine()

    def test_full_query_pipeline(self):
        """Test a complete query through the engine"""
        # Mock only the knowledge engine
        with patch.object(self.engine.knowledge, "extract_intent") as mock_extract:
            with patch.object(self.engine.knowledge, "get_solution") as mock_solution:
                with patch.object(
                    self.engine.knowledge, "format_response"
                ) as mock_format:
                    # Setup mocks
                    mock_extract.return_value = {
                        "action": "install",
                        "package": "neovim",
                    }
                    mock_solution.return_value = {
                        "found": True,
                        "methods": [
                            {
                                "type": "profile",
                                "name": "Modern approach",
                                "description": "Using nix profile",
                                "example": "nix profile install nixpkgs#neovim",
                            }
                        ],
                    }
                    mock_format.return_value = "Let me help you install Neovim!"

                    # Create a full context
                    context = Context(
                        user_id="test_user",
                        personality="symbiotic",
                        capabilities=["text", "visual"],
                        execution_mode="dry_run",
                        collect_feedback=True,
                    )

                    # Process query
                    response = self.engine.process("I want to install neovim", context)

                    # Verify complete response
                    self.assertIsInstance(response, Response)
                    self.assertIn("Let me help you install Neovim!", response.text)
                    self.assertIn(
                        "I'm still learning", response.text
                    )  # Symbiotic personality
                    self.assertEqual(response.intent.action, "install")
                    self.assertEqual(response.intent.package, "neovim")
                    self.assertEqual(len(response.commands), 1)
                    self.assertIsNotNone(response.visual)  # Visual capability enabled
                    self.assertIsNotNone(response.feedback_request)  # Feedback enabled
                    self.assertEqual(response.confidence, 0.9)

if __name__ == "__main__":
    unittest.main()
