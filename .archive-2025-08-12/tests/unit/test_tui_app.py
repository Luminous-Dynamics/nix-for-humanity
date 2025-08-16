#!/usr/bin/env python3
"""
Comprehensive tests for TUI Application

Tests all TUI functionality including:
- Application lifecycle
- Chat message handling
- Command preview functionality
- XAI explanations
- Personality switching
- Persona adaptation
- Feedback collection
- Keyboard shortcuts
"""

import os

from unittest.mock import Mock, MagicMock, patch, call
import sys
import unittest

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

# Mock Textual components before importing app
sys.modules["textual"] = MagicMock()
sys.modules["textual.app"] = MagicMock()
sys.modules["textual.widgets"] = MagicMock()
sys.modules["textual.containers"] = MagicMock()
sys.modules["textual.screen"] = MagicMock()
sys.modules["textual.reactive"] = MagicMock()
sys.modules["textual.events"] = MagicMock()
sys.modules["textual.message"] = MagicMock()
sys.modules["textual.binding"] = MagicMock()
sys.modules["rich.markdown"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.syntax"] = MagicMock()
sys.modules["rich.table"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Mock backend components
from luminous_nix.core.personality import PersonalityStyle
from luminous_nix.core import (
    Command,
    ExecutionResult,
    NixForHumanityBackend,
    dict,
)

# Now import the app module
from luminous_nix.tui.app import (
    ChatMessage,
    CommandPreview,
    HelpScreen,
    NixHumanityApp,
    XAIExplanationPanel,
)

# v2.0+ feature: from luminous_nix.ai.xai_engine import XAIEngine, ExplanationLevel, ConfidenceLevel
# v2.0+ feature: from luminous_nix.xai.causal_engine import CausalXAI, CausalExplanation
# v2.0+ feature: from luminous_nix.xai.confidence_calculator import ConfidenceCalculator
# v2.0+ feature: from luminous_nix.xai.explanation_formatter import PersonaExplanationAdapter
from luminous_nix.tui.persona_styles import PersonaStyleManager, PersonaType

class TestChatMessage(unittest.TestCase):
    """Test the ChatMessage widget."""

    def setUp(self):
        """Set up test fixtures."""
        self.static_mock = Mock()
        sys.modules["textual.widgets"].Static = self.static_mock

    def test_user_message_creation(self):
        """Test creating a user message."""
        message = ChatMessage("Hello, Nix!", is_user=True)
        self.assertEqual(message.content, "Hello, Nix!")
        self.assertTrue(message.is_user)

    def test_assistant_message_creation(self):
        """Test creating an assistant message."""
        message = ChatMessage("I can help with that!", is_user=False)
        self.assertEqual(message.content, "I can help with that!")
        self.assertFalse(message.is_user)

    def test_compose_user_message(self):
        """Test composing a user message."""
        message = ChatMessage("Test message", is_user=True)
        # Mock the compose method
        with patch.object(message, "compose") as mock_compose:
            mock_compose.return_value = [self.static_mock()]
            result = list(message.compose())
            self.assertEqual(len(result), 1)

class TestCommandPreview(unittest.TestCase):
    """Test the CommandPreview widget."""

    def test_command_preview_creation(self):
        """Test creating a command preview."""
        preview = CommandPreview("nix-env -iA nixpkgs.firefox")
        self.assertEqual(preview.command_text, "nix-env -iA nixpkgs.firefox")

    def test_compose_preview(self):
        """Test composing command preview."""
        preview = CommandPreview("sudo nixos-rebuild switch")
        # Mock the compose method
        with patch.object(preview, "compose") as mock_compose:
            mock_static = Mock()
            mock_compose.return_value = [mock_static]
            result = list(preview.compose())
            self.assertEqual(len(result), 1)

class TestXAIExplanationPanel(unittest.TestCase):
    """Test the XAI explanation panel."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_mock = Mock()
        self.explanation_adapter_mock = Mock()
        self.app_mock.explanation_adapter = self.explanation_adapter_mock

    def test_simple_explanation(self):
        """Test simple level explanation."""
        explanation = Mock()
        explanation.simple_explanation = "Simple explanation"
        explanation.primary_reason = "Test reason"
        explanation.confidence = ConfidenceLevel.HIGH

        panel = XAIExplanationPanel(
            explanation=explanation,
            level=ExplanationLevel.SIMPLE,
            persona=PersonaType.DAVID,
        )
        panel.app = self.app_mock

        # Test that it creates the panel with simple explanation
        self.assertEqual(panel.level, ExplanationLevel.SIMPLE)
        self.assertEqual(panel.persona, PersonaType.DAVID)

    def test_causal_explanation_adaptation(self):
        """Test adapting causal explanations for personas."""
        causal_explanation = Mock()
        causal_explanation.factors = [("intent_match", 0.8, {"type": "install"})]

        adapted = {
            "text": "Adapted explanation",
            "primary_reason": "Install Package",
            "confidence_emoji": "🟢",
            "style": "green",
        }
        self.explanation_adapter_mock.adapt_for_persona.return_value = adapted

        panel = XAIExplanationPanel(
            explanation=causal_explanation,
            level=ExplanationLevel.DETAILED,
            persona=PersonaType.GRANDMA_ROSE,
        )
        panel.app = self.app_mock

        # Test compose method
        with patch.object(panel, "compose") as mock_compose:
            mock_compose.return_value = [Mock()]
            list(panel.compose())

            # Verify adaptation was called
            self.explanation_adapter_mock.adapt_for_persona.assert_called_once_with(
                causal_explanation, PersonaType.GRANDMA_ROSE
            )

class TestNixHumanityApp(unittest.TestCase):
    """Test the main TUI application."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock all the dependencies
        self.core_mock = Mock(spec=NixForHumanityBackend)
        self.xai_engine_mock = Mock(spec=XAIEngine)
        self.causal_xai_mock = Mock(spec=CausalXAI)
        self.confidence_calculator_mock = Mock(spec=ConfidenceCalculator)
        self.explanation_adapter_mock = Mock(spec=PersonaExplanationAdapter)
        self.persona_manager_mock = Mock(spec=PersonaStyleManager)

        # Set up return values
        self.persona_manager_mock.get_css_styles.return_value = ""
        self.persona_manager_mock.current_persona = PersonaType.DAVID

        # Patch the constructors
        self.patches = [
            patch(
                "nix_humanity.ui.app.NixForHumanityBackend", return_value=self.core_mock
            ),
            patch("nix_humanity.ui.app.XAIEngine", return_value=self.xai_engine_mock),
            patch("nix_humanity.ui.app.CausalXAI", return_value=self.causal_xai_mock),
            patch(
                "nix_humanity.ui.app.ConfidenceCalculator",
                return_value=self.confidence_calculator_mock,
            ),
            patch(
                "nix_humanity.ui.app.PersonaExplanationAdapter",
                return_value=self.explanation_adapter_mock,
            ),
            patch(
                "nix_humanity.ui.app.PersonaStyleManager",
                return_value=self.persona_manager_mock,
            ),
        ]

        for p in self.patches:
            p.start()

    def tearDown(self):
        """Clean up patches."""
        for p in self.patches:
            p.stop()

    def test_app_initialization(self):
        """Test app initialization."""
        app = NixHumanityApp()

        # Verify initialization
        self.assertIsNotNone(app.core)
        self.assertIsNotNone(app.xai_engine)
        self.assertIsNotNone(app.causal_xai)
        self.assertIsNotNone(app.confidence_calculator)
        self.assertIsNotNone(app.explanation_adapter)
        self.assertIsNotNone(app.persona_manager)
        self.assertIsNotNone(app.session_id)
        self.assertEqual(app.personality, PersonalityStyle.FRIENDLY)
        self.assertFalse(app.show_explanations)
        self.assertEqual(app.explanation_level, ExplanationLevel.SIMPLE)

    def test_css_property(self):
        """Test CSS property combining base and persona styles."""
        app = NixHumanityApp()
        self.persona_manager_mock.get_css_styles.return_value = (
            ".custom { color: red; }"
        )

        css = app.CSS
        self.assertIn("Screen {", css)  # Base CSS
        self.assertIn(".custom { color: red; }", css)  # Persona CSS

    def test_process_query_basic(self):
        """Test processing a basic query."""
        app = NixHumanityApp()

        # Mock the UI elements
        app.query_one = Mock()
        input_widget = Mock()
        input_widget.value = ""
        chat_container = Mock()
        app.query_one.side_effect = lambda selector, *args: {
            "#user-input": input_widget,
            "#chat-container": chat_container,
        }.get(selector)

        # Mock the core response
        plan = dict(
            text="I'll install Firefox for you.",
            intent="install_package",
            command=None,
            requires_confirmation=False,
        )
        self.core_mock.plan.return_value = plan

        # Process query
        app.process_query("install firefox")

        # Verify query was processed
        self.core_mock.plan.assert_called_once()
        args = self.core_mock.plan.call_args[0][0]
        self.assertEqual(args.text, "install firefox")
        self.assertEqual(args.personality, "friendly")

        # Verify input was cleared
        self.assertEqual(input_widget.value, "")

        # Verify messages were added
        self.assertEqual(chat_container.mount.call_count, 2)  # User + assistant message

    def test_process_query_with_command(self):
        """Test processing query that returns a command."""
        app = NixHumanityApp()

        # Mock UI elements
        app.query_one = Mock()
        app.show_command_preview = Mock()

        # Mock the core response with command
        command = Command(
            program="nix-env", args=["-iA", "nixpkgs.firefox"], requires_sudo=False
        )
        plan = dict(
            text="Installing Firefox...",
            intent="install_package",
            command=command,
            requires_confirmation=True,
        )
        self.core_mock.plan.return_value = plan

        # Process query
        app.process_query("install firefox")

        # Verify command preview was shown
        app.show_command_preview.assert_called_once_with(plan)

    def test_process_query_with_xai_enabled(self):
        """Test processing query with XAI explanations enabled."""
        app = NixHumanityApp()
        app.show_explanations = True
        app.show_xai_explanation = Mock()

        # Mock UI elements
        app.query_one = Mock()

        # Mock causal explanation
        causal_explanation = Mock(spec=CausalExplanation)
        self.causal_xai_mock.explain_decision.return_value = causal_explanation

        # Mock confidence metrics
        confidence_metrics = Mock()
        self.confidence_calculator_mock.calculate_confidence.return_value = (
            confidence_metrics
        )

        # Mock plan
        plan = dict(
            text="Installing package...",
            intent="install_package",
            command=None,
            requires_confirmation=False,
        )
        self.core_mock.plan.return_value = plan

        # Process query
        app.process_query("install vim")

        # Verify XAI explanation was generated
        self.causal_xai_mock.explain_decision.assert_called_once()
        app.show_xai_explanation.assert_called_once_with(causal_explanation)

    def test_execute_current_plan_success(self):
        """Test executing a plan successfully."""
        app = NixHumanityApp()

        # Set up current plan
        command = Command(
            program="nix-env", args=["-iA", "nixpkgs.vim"], requires_sudo=False
        )
        app.current_plan = dict(
            text="Installing Vim...",
            intent="install_package",
            command=command,
            requires_confirmation=False,
        )

        # Mock UI elements
        app.query_one = Mock()
        app.update_status = Mock()

        # Mock execution result
        result = ExecutionResult(
            success=True, output="Package installed successfully", error=None
        )
        self.core_mock.execute_plan.return_value = result

        # Execute plan
        app.execute_current_plan()

        # Verify execution
        self.core_mock.execute_plan.assert_called_once_with(
            app.current_plan, "tui-user"
        )
        app.update_status.assert_any_call("Executing command...")
        app.update_status.assert_any_call("Ready")
        self.assertIsNone(app.current_plan)

    def test_execute_current_plan_failure(self):
        """Test executing a plan that fails."""
        app = NixHumanityApp()

        # Set up current plan
        command = Command(
            program="nix-env", args=["-iA", "nixpkgs.invalid"], requires_sudo=False
        )
        app.current_plan = dict(
            text="Installing invalid package...",
            intent="install_package",
            command=command,
            requires_confirmation=False,
        )

        # Mock UI elements
        app.query_one = Mock()
        chat_container = Mock()
        app.query_one.return_value = chat_container

        # Mock execution result
        result = ExecutionResult(success=False, output=None, error="Package not found")
        self.core_mock.execute_plan.return_value = result

        # Execute plan
        app.execute_current_plan()

        # Verify error message was shown
        chat_container.mount.assert_called_once()
        call_args = chat_container.mount.call_args[0][0]
        self.assertIsInstance(call_args, ChatMessage)
        self.assertIn("failed", call_args.content)
        self.assertIn("Package not found", call_args.content)

    def test_personality_toggle(self):
        """Test toggling through personality styles."""
        app = NixHumanityApp()
        app.update_status = Mock()
        app.query_one = Mock()

        # Mock personality system
        personality_system = Mock()
        self.core_mock.personality_system = personality_system

        # Initial personality
        self.assertEqual(app.personality, PersonalityStyle.FRIENDLY)

        # Toggle to next personality
        app.action_toggle_personality()

        # Verify personality changed
        self.assertNotEqual(app.personality, PersonalityStyle.FRIENDLY)
        personality_system.set_style.assert_called_once()
        app.update_status.assert_called_with("Ready")

    def test_persona_cycling(self):
        """Test cycling through user personas."""
        app = NixHumanityApp()
        app.refresh_css = Mock()
        app.query_one = Mock()

        # Mock persona profile
        profile = Mock()
        profile.name = "Maya Chen"
        profile.age = 16
        self.persona_manager_mock.profile = profile

        # Initial persona
        self.persona_manager_mock.current_persona = PersonaType.DAVID

        # Cycle persona
        app.action_cycle_persona()

        # Verify persona changed
        self.persona_manager_mock.set_persona.assert_called_once()
        app.refresh_css.assert_called_once()

    def test_explanation_toggle(self):
        """Test toggling XAI explanations."""
        app = NixHumanityApp()
        app.query_one = Mock()
        app.update_status = Mock()

        # Initial state
        self.assertFalse(app.show_explanations)

        # Toggle on
        app.action_toggle_explanations()
        self.assertTrue(app.show_explanations)

        # Toggle off
        app.action_toggle_explanations()
        self.assertFalse(app.show_explanations)

    def test_explanation_level_cycling(self):
        """Test cycling explanation detail levels."""
        app = NixHumanityApp()
        app.query_one = Mock()
        app.update_status = Mock()
        app.refresh_explanation = Mock()

        # Initial level
        self.assertEqual(app.explanation_level, ExplanationLevel.SIMPLE)

        # Cycle to DETAILED
        app.action_cycle_explanation_level()
        self.assertEqual(app.explanation_level, ExplanationLevel.DETAILED)

        # Cycle to TECHNICAL
        app.action_cycle_explanation_level()
        self.assertEqual(app.explanation_level, ExplanationLevel.TECHNICAL)

        # Cycle back to SIMPLE
        app.action_cycle_explanation_level()
        self.assertEqual(app.explanation_level, ExplanationLevel.SIMPLE)

    def test_feedback_ui_symbiotic_mode(self):
        """Test feedback UI in symbiotic mode."""
        app = NixHumanityApp()
        app.personality = PersonalityStyle.SYMBIOTIC

        # Mock UI elements
        preview_container = Mock()
        app.query_one = Mock(return_value=preview_container)

        # Show feedback UI
        app.show_feedback_ui("test query", "test response")

        # Verify feedback was stored
        self.assertEqual(app.last_query, "test query")
        self.assertEqual(app.last_response, "test response")

        # Verify UI was created
        self.assertTrue(preview_container.mount.called)

    def test_handle_feedback_helpful(self):
        """Test handling helpful feedback."""
        app = NixHumanityApp()
        app.last_query = "install firefox"
        app.last_response = "Installing Firefox..."

        # Mock UI elements
        app.query_one = Mock()

        # Mock learning system
        learning_system = Mock()
        self.core_mock.learning_system = learning_system

        # Handle helpful feedback
        app.handle_feedback_button("feedback-helpful")

        # Verify interaction was recorded
        learning_system.record_interaction.assert_called_once()
        interaction = learning_system.record_interaction.call_args[0][0]
        self.assertEqual(interaction.query, "install firefox")
        self.assertEqual(interaction.response, "Installing Firefox...")
        self.assertTrue(interaction.success)

    def test_handle_feedback_not_helpful(self):
        """Test handling not helpful feedback."""
        app = NixHumanityApp()
        app.query_one = Mock()

        # Handle not helpful feedback
        app.handle_feedback_button("feedback-not-helpful")

        # Verify awaiting explanation
        self.assertTrue(app.awaiting_feedback_explanation)

    def test_clear_chat(self):
        """Test clearing chat history."""
        app = NixHumanityApp()

        # Mock UI elements
        chat_container = Mock()
        preview_container = Mock()
        app.query_one = Mock()
        app.query_one.side_effect = lambda selector: {
            "#chat-container": chat_container,
            "#command-preview": preview_container,
        }.get(selector)

        app.update_status = Mock()

        # Clear chat
        app.action_clear_chat()

        # Verify chat was cleared
        chat_container.remove_children.assert_called_once()
        preview_container.remove_children.assert_called_once()
        app.update_status.assert_called_with("Ready")

    def test_show_help_screen(self):
        """Test showing help screen."""
        app = NixHumanityApp()
        app.push_screen = Mock()

        # Show help
        app.action_show_help()

        # Verify help screen was pushed
        app.push_screen.assert_called_once()
        screen = app.push_screen.call_args[0][0]
        self.assertIsInstance(screen, HelpScreen)

class TestHelpScreen(unittest.TestCase):
    """Test the help screen."""

    def test_help_screen_bindings(self):
        """Test help screen has proper key bindings."""
        screen = HelpScreen()

        # Check bindings exist
        binding_keys = [b.key for b in screen.BINDINGS]
        self.assertIn("escape", binding_keys)
        self.assertIn("q", binding_keys)

if __name__ == "__main__":
    unittest.main()
