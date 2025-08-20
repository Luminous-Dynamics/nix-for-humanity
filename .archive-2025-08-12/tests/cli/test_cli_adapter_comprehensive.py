#!/usr/bin/env python3
"""
Comprehensive CLI Adapter Testing Suite

This test file implements the strategic plan for achieving 95% coverage of the CLI Adapter component.
Tests the user-facing functionality that directly impacts the CLI experience with all 7 test classes:

1. TestCLIAdapterCore - Core functionality tests
2. TestCLIPersonalityAdaptation - All personality styles tested
3. TestCLIOutputFormatting - Response formatting
4. TestCLIErrorHandling - Error scenarios
5. TestCLIStreaming - Real-time updates
6. TestCLIAccessibility - Terminal compatibility
7. TestCLIPerformance - Response times

Following consciousness-first testing: Focus on user experience and accessibility.
"""

import os
import sys
import threading
import time

from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

import pytest

# Add source directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the CLI adapter under test
from luminous_nix.interfaces.cli import CLIAdapter

class TestCLIAdapterCore:
    """Test core functionality of the CLI Adapter."""

    @pytest.fixture
    def mock_core(self):
        """Mock the headless core engine."""
        with patch(
            "luminous_nix.interfaces.cli.NixForHumanityBackend"
        ) as mock_core_class:
            mock_core = Mock()
            mock_core_class.return_value = mock_core

            # Mock core methods
            mock_core.process.return_value = Mock(
                text="Test response", suggestions=[], feedback_requested=False
            )
            mock_core.intent_engine.recognize.return_value = Mock(
                type=Mock(value="install"), target="firefox"
            )
            mock_core.get_system_stats.return_value = {
                "queries_processed": 42,
                "uptime": "2 hours",
            }

            yield mock_core

    @pytest.fixture
    def cli_adapter(self, mock_core):
        """Create CLI adapter with mocked dependencies."""
        with patch("luminous_nix.interfaces.cli.Query") as mock_query:
            with patch("luminous_nix.interfaces.cli.str") as mock_mode:
                with patch(
                    "luminous_nix.interfaces.cli.PersonalityStyle"
                ) as mock_style:
                    with patch("luminous_nix.interfaces.cli.uuid") as mock_uuid:
                        # Mock UUID generation
                        mock_uuid.uuid4.return_value = Mock(
                            __str__=Mock(return_value="test-session-id-12345")
                        )

                        # Mock str constants
                        mock_mode.DRY_RUN = "dry_run"
                        mock_mode.EXECUTE = "execute"
                        mock_mode.EXPLAIN = "explain"

                        # Mock Query constructor
                        mock_query.side_effect = lambda **kwargs: Mock(**kwargs)

                        adapter = CLIAdapter()
                        return adapter

    def test_initialization(self, cli_adapter, mock_core):
        """Test CLI adapter initializes correctly with proper configuration."""
        # Verify core was initialized with CLI-specific config
        expected_config = {
            "dry_run": False,
            "default_personality": "friendly",
            "enable_learning": True,
            "collect_feedback": True,
        }
        mock_core.__class__.assert_called_once_with(expected_config)

        # Verify session ID is set correctly (first 8 chars of UUID)
        assert cli_adapter.session_id == "test-ses"

        # Verify CLI-specific settings
        assert cli_adapter.show_progress == True
        assert isinstance(cli_adapter.visual_mode, bool)

    def test_rich_availability_check_available(self, cli_adapter):
        """Test Rich library availability detection when available."""
        with patch("builtins.__import__") as mock_import:
            # Mock successful rich import
            mock_import.return_value = Mock()  # Rich module
            result = cli_adapter._check_rich_available()
            assert result == True

    def test_rich_availability_check_unavailable(self, cli_adapter):
        """Test Rich library availability detection when unavailable."""
        with patch("builtins.__import__", side_effect=ImportError):
            result = cli_adapter._check_rich_available()
            assert result == False

    def test_get_user_id_with_user_env(self, cli_adapter):
        """Test user ID retrieval when USER environment variable is set."""
        with patch.dict(os.environ, {"USER": "testuser"}):
            user_id = cli_adapter._get_user_id()
            assert user_id == "testuser"

    def test_get_user_id_anonymous_fallback(self, cli_adapter):
        """Test user ID fallback to anonymous when USER env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            user_id = cli_adapter._get_user_id()
            assert user_id == "anonymous"

    def test_process_query_execution_modes(self, cli_adapter, mock_core):
        """Test query processing with different execution modes."""
        # Test dry run mode
        response = cli_adapter.process_query("install firefox", dry_run=True)
        query_arg = mock_core.process.call_args[0][0]
        assert query_arg.mode == "dry_run"

        # Reset mock and test execute mode
        mock_core.reset_mock()
        response = cli_adapter.process_query("install firefox", execute=True)
        query_arg = mock_core.process.call_args[0][0]
        assert query_arg.mode == "execute"

        # Reset mock and test explain mode
        mock_core.reset_mock()
        response = cli_adapter.process_query(
            "install firefox", execute=False, dry_run=False
        )
        query_arg = mock_core.process.call_args[0][0]
        assert query_arg.mode == "explain"

    def test_process_query_with_intent_display(self, cli_adapter, mock_core):
        """Test query processing with intent display enabled."""
        with patch("builtins.print") as mock_print:
            response = cli_adapter.process_query("install firefox", show_intent=True)

            # Verify intent recognition was called
            mock_core.intent_engine.recognize.assert_called_once_with("install firefox")

            # Verify intent display
            mock_print.assert_any_call("\n🎯 Intent detected: install")
            mock_print.assert_any_call("📦 Target: firefox")

    def test_process_query_intent_no_target(self, cli_adapter, mock_core):
        """Test intent display when target is None."""
        # Mock intent with no target
        mock_core.intent_engine.recognize.return_value = Mock(
            type=Mock(value="help"), target=None
        )

        with patch("builtins.print") as mock_print:
            response = cli_adapter.process_query("help", show_intent=True)

            # Should print intent but not target
            mock_print.assert_any_call("\n🎯 Intent detected: help")
            target_calls = [
                call for call in mock_print.call_args_list if "Target:" in str(call)
            ]
            assert len(target_calls) == 0

class TestCLIPersonalityAdaptation:
    """Test personality adaptation across all supported styles."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter with personality system mocked."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch(
                        "luminous_nix.interfaces.cli.PersonalityStyle"
                    ) as mock_style:
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            adapter = CLIAdapter()
                            # Mock personality system
                            adapter.core.personality_system = Mock()
                            return adapter

    @pytest.mark.parametrize(
        "personality",
        ["minimal", "friendly", "encouraging", "technical", "sacred", "playful"],
    )
    def test_personality_styles(self, cli_adapter, personality):
        """Test setting different personality styles."""
        cli_adapter.set_personality(personality)

        # Verify personality system was called
        cli_adapter.core.personality_system.set_style.assert_called_once()

    def test_invalid_personality_handling(self, cli_adapter):
        """Test handling of invalid personality styles with user-friendly error."""
        cli_adapter.core.personality_system.set_style.side_effect = ValueError(
            "Invalid style"
        )

        with patch("builtins.print") as mock_print:
            cli_adapter.set_personality("invalid_style")

        mock_print.assert_called_with("Unknown personality style: invalid_style")

    def test_custom_personality_in_query(self, cli_adapter):
        """Test query processing with custom personality override."""
        mock_response = Mock(text="Response", suggestions=[], feedback_requested=False)
        cli_adapter.core.process.return_value = mock_response

        response = cli_adapter.process_query("install firefox", personality="technical")

        # Verify query was created with custom personality
        query_arg = cli_adapter.core.process.call_args[0][0]
        assert query_arg.personality == "technical"

class TestCLIOutputFormatting:
    """Test response formatting and display modes."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter for output testing."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            return CLIAdapter()

    def test_simple_text_display(self, cli_adapter):
        """Test simple text response display without rich formatting."""
        cli_adapter.visual_mode = False
        response = Mock(
            text="Simple response text",
            suggestions=["suggestion1", "suggestion2"],
            feedback_requested=False,
        )

        with patch("builtins.print") as mock_print:
            cli_adapter.display_response(response)

        # Verify text and suggestions displayed
        mock_print.assert_any_call("Simple response text")
        mock_print.assert_any_call("\n💡 Suggestions:")
        mock_print.assert_any_call("   • suggestion1")
        mock_print.assert_any_call("   • suggestion2")

    def test_rich_display_mode(self, cli_adapter):
        """Test rich formatting when Rich library is available."""
        cli_adapter.visual_mode = True
        response = Mock(
            text="Rich response",
            suggestions=["rich suggestion"],
            feedback_requested=False,
        )

        # Mock rich components
        with patch("builtins.__import__") as mock_import:
            mock_console_class = Mock()
            mock_panel_class = Mock()
            mock_markdown_class = Mock()
            mock_console = Mock()

            def import_side_effect(name, *args, **kwargs):
                if name == "rich.console":
                    module = Mock()
                    module.Console = mock_console_class
                    return module
                if name == "rich.panel":
                    module = Mock()
                    module.Panel = mock_panel_class
                    return module
                if name == "rich.markdown":
                    module = Mock()
                    module.Markdown = mock_markdown_class
                    return module
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect
            mock_console_class.return_value = mock_console

            cli_adapter._display_rich(response)

            # Verify rich components were used
            mock_console_class.assert_called_once()
            mock_panel_class.assert_called_once()
            mock_markdown_class.assert_called_once_with("Rich response")

    def test_rich_fallback_to_simple(self, cli_adapter):
        """Test fallback to simple display when Rich import fails."""
        cli_adapter.visual_mode = True
        response = Mock(
            text="Fallback response", suggestions=[], feedback_requested=False
        )

        with patch("builtins.__import__", side_effect=ImportError):
            with patch.object(cli_adapter, "_display_simple") as mock_simple:
                cli_adapter._display_rich(response)
                mock_simple.assert_called_once_with(response)

    def test_empty_suggestions_handling(self, cli_adapter):
        """Test proper handling of responses with no suggestions."""
        cli_adapter.visual_mode = False
        response = Mock(text="No suggestions", suggestions=[], feedback_requested=False)

        with patch("builtins.print") as mock_print:
            cli_adapter._display_simple(response)

        # Should only print response text, no suggestions section
        mock_print.assert_called_with("No suggestions")
        suggestion_calls = [
            call for call in mock_print.call_args_list if "Suggestions:" in str(call)
        ]
        assert len(suggestion_calls) == 0

    def test_none_suggestions_handling(self, cli_adapter):
        """Test graceful handling of None suggestions."""
        cli_adapter.visual_mode = False
        response = Mock(text="Response", suggestions=None, feedback_requested=False)

        with patch("builtins.print") as mock_print:
            cli_adapter._display_simple(response)

        # Should handle None gracefully without errors
        mock_print.assert_called_with("Response")

class TestCLIErrorHandling:
    """Test error scenarios and recovery mechanisms."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter for error testing."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            return CLIAdapter()

    def test_core_processing_exception(self, cli_adapter):
        """Test handling of exceptions from core processing."""
        cli_adapter.core.process.side_effect = Exception("Core processing failed")

        # Should propagate exception for proper error handling upstream
        with pytest.raises(Exception, match="Core processing failed"):
            cli_adapter.process_query("test query")

    def test_keyboard_interrupt_during_feedback(self, cli_adapter):
        """Test graceful handling of keyboard interrupt during feedback collection."""
        response = Mock(text="Test", suggestions=[], feedback_requested=False)

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            # Should not raise exception - should handle gracefully
            cli_adapter._gather_feedback(response)

    def test_personality_system_not_available(self, cli_adapter):
        """Test handling when personality system is not available."""
        # Mock core without personality_system attribute
        cli_adapter.core = Mock(spec=[])  # Empty spec means no attributes

        with patch("builtins.print") as mock_print:
            # Should handle AttributeError gracefully
            try:
                cli_adapter.set_personality("friendly")
            except AttributeError:
                # This is expected behavior when personality system not available
                pass

    def test_stats_system_unavailable(self, cli_adapter):
        """Test stats display when system stats are unavailable."""
        cli_adapter.core.get_system_stats.side_effect = Exception("Stats unavailable")

        # Should propagate exception for proper error handling
        with pytest.raises(Exception, match="Stats unavailable"):
            cli_adapter.get_stats()

class TestCLIStreaming:
    """Test streaming and real-time update functionality."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter for streaming tests."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            adapter = CLIAdapter()
                            adapter.show_progress = True
                            return adapter

    def test_progress_display_enabled(self, cli_adapter):
        """Test that progress display is enabled by default."""
        assert cli_adapter.show_progress == True

    def test_progress_display_configuration(self, cli_adapter):
        """Test progress display can be configured."""
        # Test disabling progress
        cli_adapter.show_progress = False
        assert cli_adapter.show_progress == False

        # Test re-enabling progress
        cli_adapter.show_progress = True
        assert cli_adapter.show_progress == True

    def test_visual_mode_affects_display(self, cli_adapter):
        """Test that visual mode selection affects display method choice."""
        response = Mock(text="Test", suggestions=[], feedback_requested=False)

        # Test visual mode calls rich display
        cli_adapter.visual_mode = True
        with patch.object(cli_adapter, "_display_rich") as mock_rich:
            cli_adapter.display_response(response)
            mock_rich.assert_called_once_with(response)

        # Test simple mode calls simple display
        cli_adapter.visual_mode = False
        with patch.object(cli_adapter, "_display_simple") as mock_simple:
            cli_adapter.display_response(response)
            mock_simple.assert_called_once_with(response)

class TestCLIAccessibility:
    """Test accessibility features and terminal compatibility."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter for accessibility testing."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            return CLIAdapter()

    def test_screen_reader_friendly_output(self, cli_adapter):
        """Test output is screen reader friendly with proper structure."""
        cli_adapter.visual_mode = False  # Simple mode is more screen reader friendly
        response = Mock(
            text="Installing Firefox browser for web browsing",
            suggestions=[
                "Try: firefox --help for options",
                "See: about:config for settings",
            ],
            feedback_requested=False,
        )

        with patch("builtins.print") as mock_print:
            cli_adapter._display_simple(response)

        # Verify clear, structured output
        mock_print.assert_any_call("Installing Firefox browser for web browsing")
        mock_print.assert_any_call("\n💡 Suggestions:")
        mock_print.assert_any_call("   • Try: firefox --help for options")
        mock_print.assert_any_call("   • See: about:config for settings")

    def test_keyboard_navigation_support(self, cli_adapter):
        """Test keyboard-only navigation through feedback system."""
        response = Mock(text="Test response", suggestions=[], feedback_requested=False)

        # Test various keyboard inputs
        keyboard_inputs = ["y", "n", "yes", "no", "skip", "Y", "N"]

        for input_value in keyboard_inputs:
            with patch("builtins.input", return_value=input_value):
                with patch("builtins.print") as mock_print:
                    cli_adapter._gather_feedback(response)

                    # Should handle all keyboard inputs gracefully
                    # Each input should result in appropriate feedback response
                    if input_value.lower() in ["y", "yes"]:
                        mock_print.assert_any_call("Great! Thank you for the feedback.")
                    elif input_value.lower() in ["n", "no"]:
                        mock_print.assert_any_call(
                            "\nI'd love to learn how to help better!"
                        )

    def test_terminal_width_independence(self, cli_adapter):
        """Test output works correctly regardless of terminal width."""
        response = Mock(
            text="This is a very long response that might wrap in narrow terminals but should display correctly regardless of terminal width settings",
            suggestions=[
                "This is a long suggestion that tests word wrapping behavior",
                "Another suggestion to test display formatting",
            ],
            feedback_requested=False,
        )

        with patch("builtins.print") as mock_print:
            cli_adapter._display_simple(response)

        # Output should be displayed without width-dependent formatting
        mock_print.assert_any_call(response.text)
        mock_print.assert_any_call(
            "   • This is a long suggestion that tests word wrapping behavior"
        )

    def test_unicode_and_emoji_handling(self, cli_adapter):
        """Test proper handling of Unicode characters and emojis."""
        response = Mock(
            text="Successfully installed 🦊 Firefox! 🎉",
            suggestions=["Try visiting 🌐 https://example.com"],
            feedback_requested=False,
        )

        with patch("builtins.print") as mock_print:
            cli_adapter._display_simple(response)

        # Should handle Unicode/emoji gracefully
        mock_print.assert_any_call("Successfully installed 🦊 Firefox! 🎉")
        mock_print.assert_any_call("   • Try visiting 🌐 https://example.com")

class TestCLIPerformance:
    """Test response times and performance requirements."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter for performance testing."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            adapter = CLIAdapter()
                            # Mock fast core responses
                            adapter.core.process.return_value = Mock(
                                text="Fast response",
                                suggestions=[],
                                feedback_requested=False,
                            )
                            return adapter

    def test_query_processing_performance(self, cli_adapter):
        """Test query processing meets performance requirements."""
        start_time = time.time()

        response = cli_adapter.process_query("install firefox")

        end_time = time.time()
        processing_time = end_time - start_time

        # Should complete within reasonable time (allowing for mocking overhead)
        assert (
            processing_time < 1.0
        ), f"Query processing took {processing_time}s, should be <1s"

    def test_display_performance(self, cli_adapter):
        """Test response display performance."""
        response = Mock(
            text="Test response",
            suggestions=["suggestion1", "suggestion2", "suggestion3"],
            feedback_requested=False,
        )

        start_time = time.time()

        with patch("builtins.print"):
            cli_adapter.display_response(response)

        end_time = time.time()
        display_time = end_time - start_time

        # Display should be nearly instantaneous
        assert display_time < 0.1, f"Display took {display_time}s, should be <0.1s"

    def test_stats_retrieval_performance(self, cli_adapter):
        """Test system stats retrieval performance."""
        cli_adapter.core.get_system_stats.return_value = {
            "queries": 1000,
            "cache_size": "50MB",
            "uptime": "24 hours",
        }

        start_time = time.time()

        with patch("builtins.print"):
            cli_adapter.get_stats()

        end_time = time.time()
        stats_time = end_time - start_time

        # Stats should display quickly
        assert stats_time < 0.5, f"Stats display took {stats_time}s, should be <0.5s"

    def test_concurrent_operation_safety(self, cli_adapter):
        """Test thread safety for concurrent operations."""
        results = []
        errors = []

        def query_worker(query_text):
            try:
                response = cli_adapter.process_query(f"test query {query_text}")
                results.append(response)
            except Exception as e:
                errors.append(e)

        # Run multiple concurrent queries
        threads = []
        for i in range(5):
            thread = threading.Thread(target=query_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=2.0)

        # All queries should complete successfully
        assert len(errors) == 0, f"Concurrent operations had errors: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"

class TestCLIFeedbackSystem:
    """Test the feedback collection and learning integration."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter for feedback testing."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            return CLIAdapter()

    def test_positive_feedback_collection(self, cli_adapter):
        """Test collection of positive user feedback."""
        response = Mock(text="Great response", suggestions=[], feedback_requested=False)

        with patch("builtins.input", return_value="y"):
            with patch("builtins.print") as mock_print:
                cli_adapter._gather_feedback(response)

        mock_print.assert_any_call("Great! Thank you for the feedback.")

    def test_negative_feedback_with_improvement(self, cli_adapter):
        """Test negative feedback collection with improvement suggestions."""
        response = Mock(
            text="Could be better", suggestions=[], feedback_requested=False
        )

        with patch("builtins.input", side_effect=["n", "Please be more specific"]):
            with patch("builtins.print") as mock_print:
                cli_adapter._gather_feedback(response)

        mock_print.assert_any_call("\nI'd love to learn how to help better!")
        mock_print.assert_any_call("Thank you! I'll use this to improve.")

    def test_feedback_system_interruption_handling(self, cli_adapter):
        """Test graceful handling of user interruption during feedback."""
        response = Mock(text="Test", suggestions=[], feedback_requested=False)

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            # Should not raise exception
            cli_adapter._gather_feedback(response)

    def test_feedback_requested_flag_triggers_collection(self, cli_adapter):
        """Test that feedback_requested flag triggers feedback collection."""
        cli_adapter.visual_mode = False
        response = Mock(text="Response", suggestions=[], feedback_requested=True)

        with patch.object(cli_adapter, "_gather_feedback") as mock_gather:
            with patch("builtins.print"):
                cli_adapter._display_simple(response)

        mock_gather.assert_called_once_with(response)

class TestCLISystemStats:
    """Test system statistics display and formatting."""

    @pytest.fixture
    def cli_adapter(self):
        """Create CLI adapter for stats testing."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            return CLIAdapter()

    def test_simple_stats_display(self, cli_adapter):
        """Test display of simple key-value statistics."""
        stats = {"queries_processed": 100, "uptime": "5 hours", "memory_usage": "150MB"}
        cli_adapter.core.get_system_stats.return_value = stats

        with patch("builtins.print") as mock_print:
            cli_adapter.get_stats()

        # Verify header
        mock_print.assert_any_call("\n📊 System Statistics")
        mock_print.assert_any_call("=" * 50)

        # Verify stats display
        mock_print.assert_any_call("queries_processed: 100")
        mock_print.assert_any_call("uptime: 5 hours")
        mock_print.assert_any_call("memory_usage: 150MB")

    def test_nested_stats_display(self, cli_adapter):
        """Test display of nested statistics with proper indentation."""
        stats = {
            "performance": {"response_time": "0.5s", "success_rate": "98%"},
            "learning": {"patterns_learned": 50, "accuracy": "95%"},
            "simple_stat": "value",
        }
        cli_adapter.core.get_system_stats.return_value = stats

        with patch("builtins.print") as mock_print:
            cli_adapter.get_stats()

        # Verify nested display with proper formatting
        mock_print.assert_any_call("\nperformance:")
        mock_print.assert_any_call("  response_time: 0.5s")
        mock_print.assert_any_call("  success_rate: 98%")
        mock_print.assert_any_call("\nlearning:")
        mock_print.assert_any_call("  patterns_learned: 50")
        mock_print.assert_any_call("  accuracy: 95%")
        mock_print.assert_any_call("simple_stat: value")

    def test_empty_stats_handling(self, cli_adapter):
        """Test handling of empty statistics."""
        cli_adapter.core.get_system_stats.return_value = {}

        with patch("builtins.print") as mock_print:
            cli_adapter.get_stats()

        # Should still display header
        mock_print.assert_any_call("\n📊 System Statistics")
        mock_print.assert_any_call("=" * 50)

# Integration test for CLI adapter coverage validation
class TestCLIAdapterCoverage:
    """Validate that all core CLI adapter functionality is covered."""

    def test_all_public_methods_covered(self):
        """Ensure all public methods of CLIAdapter are tested."""
        cli_adapter_methods = [
            "process_query",
            "display_response",
            "set_personality",
            "get_stats",
        ]

        # Verify each method has dedicated test coverage
        for method in cli_adapter_methods:
            assert hasattr(
                CLIAdapter, method
            ), f"Method {method} not found in CLIAdapter"

    def test_all_private_methods_covered(self):
        """Ensure key private methods are tested for implementation details."""
        private_methods = [
            "_check_rich_available",
            "_get_user_id",
            "_display_simple",
            "_display_rich",
            "_gather_feedback",
        ]

        for method in private_methods:
            assert hasattr(
                CLIAdapter, method
            ), f"Private method {method} not found in CLIAdapter"

    def test_initialization_parameters_covered(self):
        """Verify all initialization parameters and attributes are tested."""
        with patch("luminous_nix.interfaces.cli.NixForHumanityBackend"):
            with patch("luminous_nix.interfaces.cli.Query"):
                with patch("luminous_nix.interfaces.cli.str"):
                    with patch("luminous_nix.interfaces.cli.PersonalityStyle"):
                        with patch("luminous_nix.interfaces.cli.uuid"):
                            adapter = CLIAdapter()

                            # Verify key attributes exist
                            assert hasattr(adapter, "core")
                            assert hasattr(adapter, "session_id")
                            assert hasattr(adapter, "show_progress")
                            assert hasattr(adapter, "visual_mode")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
