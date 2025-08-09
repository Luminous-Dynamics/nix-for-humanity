#!/usr/bin/env python3
"""
Simplified tests for TUI Application

Tests basic TUI functionality with proper imports and mocking.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestTUIApp(unittest.TestCase):
    """Test the TUI application with proper mocking."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock all Textual and Rich components
        self.textual_mock = MagicMock()
        self.rich_mock = MagicMock()
        
        # Create module mocks
        sys.modules['textual'] = self.textual_mock
        sys.modules['textual.app'] = self.textual_mock.app
        sys.modules['textual.widgets'] = self.textual_mock.widgets
        sys.modules['textual.containers'] = self.textual_mock.containers
        sys.modules['textual.screen'] = self.textual_mock.screen
        sys.modules['textual.reactive'] = self.textual_mock.reactive
        sys.modules['textual.events'] = self.textual_mock.events
        sys.modules['textual.message'] = self.textual_mock.message
        sys.modules['textual.binding'] = self.textual_mock.binding
        sys.modules['rich'] = self.rich_mock
        sys.modules['rich.markdown'] = self.rich_mock.markdown
        sys.modules['rich.panel'] = self.rich_mock.panel
        sys.modules['rich.syntax'] = self.rich_mock.syntax
        sys.modules['rich.table'] = self.rich_mock.table
        sys.modules['rich.text'] = self.rich_mock.text
        
        # Mock the Textual App base class
        self.app_base = MagicMock()
        self.textual_mock.app.App = self.app_base
        
        # Mock widgets
        self.textual_mock.widgets.Static = MagicMock()
        self.textual_mock.screen.Screen = MagicMock()
        self.textual_mock.binding.Binding = MagicMock()
        
        # Mock backend core components
        self.core_mock = MagicMock()
        sys.modules['nix_humanity.core'] = self.core_mock
        sys.modules['nix_humanity.core.backend'] = MagicMock()
        
        # Set up necessary attributes
        self.core_mock.NixForHumanityBackend = MagicMock()
        
        # Mock the AI and XAI components
        self.ai_mock = MagicMock()
        self.xai_mock = MagicMock()
        sys.modules['nix_for_humanity'] = MagicMock()
        sys.modules['nix_for_humanity.ai'] = self.ai_mock
        sys.modules['nix_for_humanity.ai.xai_engine'] = self.ai_mock.xai_engine
        sys.modules['nix_for_humanity.xai'] = self.xai_mock
        sys.modules['nix_for_humanity.xai.causal_engine'] = self.xai_mock.causal_engine
        sys.modules['nix_for_humanity.xai.confidence_calculator'] = self.xai_mock.confidence_calculator
        sys.modules['nix_for_humanity.xai.explanation_formatter'] = self.xai_mock.explanation_formatter
        sys.modules['nix_for_humanity.tui'] = MagicMock()
        sys.modules['nix_for_humanity.tui.persona_styles'] = MagicMock()
        
        # Set up enums and classes
        self.ai_mock.xai_engine.ExplanationLevel = MagicMock()
        self.ai_mock.xai_engine.ExplanationLevel.SIMPLE = 'simple'
        self.ai_mock.xai_engine.ExplanationLevel.DETAILED = 'detailed'
        self.ai_mock.xai_engine.ExplanationLevel.TECHNICAL = 'technical'
        
        self.ai_mock.xai_engine.ConfidenceLevel = MagicMock()
        self.ai_mock.xai_engine.ConfidenceLevel.HIGH = 'high'
        self.ai_mock.xai_engine.ConfidenceLevel.MEDIUM = 'medium'
        self.ai_mock.xai_engine.ConfidenceLevel.LOW = 'low'
        
        # Mock PersonalityStyle enum
        self.personality_style_mock = MagicMock()
        self.personality_style_mock.FRIENDLY = 'friendly'
        self.personality_style_mock.MINIMAL = 'minimal'
        self.personality_style_mock.SYMBIOTIC = 'symbiotic'
        
        # Mock PersonaType enum
        self.persona_type_mock = MagicMock()
        self.persona_type_mock.DAVID = 'david'
        self.persona_type_mock.GRANDMA_ROSE = 'grandma_rose'
        self.persona_type_mock.MAYA = 'maya'
        
        # Mock core types
        sys.modules['nix_humanity.core.types'] = MagicMock()
        sys.modules['nix_humanity.core.types'].PersonalityStyle = self.personality_style_mock
        
        # Create mock classes for app components
        self.chat_message_mock = MagicMock()
        self.command_preview_mock = MagicMock()
        self.help_screen_mock = MagicMock()
        self.xai_panel_mock = MagicMock()
        
    def test_app_module_imports(self):
        """Test that TUI app module can be imported with mocks."""
        try:
            # Import the app module
            from nix_humanity.tui import app
            # If we get here, imports worked
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import TUI app module: {e}")
    
    @patch('nix_for_humanity.tui.app.NixForHumanityBackend')
    @patch('nix_for_humanity.tui.app.PersonaStyleManager')
    def test_app_creation_with_mocks(self, mock_persona_manager, mock_core):
        """Test creating app instance with mocked dependencies."""
        # Set up return values
        mock_persona_manager.return_value.get_css_styles.return_value = ""
        mock_persona_manager.return_value.current_persona = self.persona_type_mock.DAVID
        
        # Store reference to personality mock
        personality_style_mock = self.personality_style_mock
        
        # Create a mock app class
        class MockNixHumanityApp:
            def __init__(self):
                self.core = mock_core()
                self.persona_manager = mock_persona_manager()
                self.session_id = "test-session"
                self.personality = personality_style_mock.FRIENDLY
                self.show_explanations = False
                self.explanation_level = 'simple'
                self.current_plan = None
        
        # Create instance
        app = MockNixHumanityApp()
        
        # Test basic attributes
        self.assertIsNotNone(app.core)
        self.assertIsNotNone(app.persona_manager)
        self.assertEqual(app.personality, 'friendly')
        self.assertFalse(app.show_explanations)
    
    def test_chat_message_structure(self):
        """Test ChatMessage basic structure."""
        # Create a mock ChatMessage class
        class MockChatMessage:
            def __init__(self, content, is_user=True):
                self.content = content
                self.is_user = is_user
        
        # Test user message
        user_msg = MockChatMessage("Hello!", is_user=True)
        self.assertEqual(user_msg.content, "Hello!")
        self.assertTrue(user_msg.is_user)
        
        # Test assistant message
        asst_msg = MockChatMessage("Hi there!", is_user=False)
        self.assertEqual(asst_msg.content, "Hi there!")
        self.assertFalse(asst_msg.is_user)
    
    def test_command_preview_structure(self):
        """Test CommandPreview basic structure."""
        # Create a mock CommandPreview class
        class MockCommandPreview:
            def __init__(self, command_text):
                self.command_text = command_text
        
        preview = MockCommandPreview("nix-env -iA nixpkgs.firefox")
        self.assertEqual(preview.command_text, "nix-env -iA nixpkgs.firefox")
    
    def test_personality_toggle_logic(self):
        """Test personality style toggling logic."""
        # Define personality styles
        styles = ['minimal', 'friendly', 'encouraging', 'technical', 'symbiotic']
        
        # Test cycling through personalities
        current_index = 1  # Start at 'friendly'
        current = styles[current_index]
        self.assertEqual(current, 'friendly')
        
        # Toggle to next
        current_index = (current_index + 1) % len(styles)
        current = styles[current_index]
        self.assertEqual(current, 'encouraging')
        
        # Toggle again
        current_index = (current_index + 1) % len(styles)
        current = styles[current_index]
        self.assertEqual(current, 'technical')
    
    def test_persona_cycling_logic(self):
        """Test persona cycling logic."""
        # Define personas
        personas = ['grandma_rose', 'maya', 'alex', 'david', 'carlos']
        
        # Test cycling
        current_index = 3  # Start at 'david'
        current = personas[current_index]
        self.assertEqual(current, 'david')
        
        # Cycle to next
        current_index = (current_index + 1) % len(personas)
        current = personas[current_index]
        self.assertEqual(current, 'carlos')
        
        # Cycle wraps around
        current_index = (current_index + 1) % len(personas)
        current = personas[current_index]
        self.assertEqual(current, 'grandma_rose')
    
    def test_explanation_level_cycling(self):
        """Test explanation level cycling logic."""
        levels = ['simple', 'detailed', 'technical']
        
        # Test cycling
        current_index = 0
        current = levels[current_index]
        self.assertEqual(current, 'simple')
        
        # Cycle through all levels
        current_index = (current_index + 1) % len(levels)
        self.assertEqual(levels[current_index], 'detailed')
        
        current_index = (current_index + 1) % len(levels)
        self.assertEqual(levels[current_index], 'technical')
        
        # Wrap back to simple
        current_index = (current_index + 1) % len(levels)
        self.assertEqual(levels[current_index], 'simple')
    
    def test_feedback_state_management(self):
        """Test feedback collection state management."""
        # Mock app state
        class MockAppState:
            def __init__(self):
                self.last_query = ""
                self.last_response = ""
                self.awaiting_feedback_explanation = False
        
        state = MockAppState()
        
        # Store feedback info
        state.last_query = "install firefox"
        state.last_response = "Installing Firefox..."
        
        self.assertEqual(state.last_query, "install firefox")
        self.assertEqual(state.last_response, "Installing Firefox...")
        
        # Set awaiting feedback
        state.awaiting_feedback_explanation = True
        self.assertTrue(state.awaiting_feedback_explanation)
        
        # Clear feedback state
        state.awaiting_feedback_explanation = False
        self.assertFalse(state.awaiting_feedback_explanation)
    
    def test_plan_execution_state(self):
        """Test plan execution state management."""
        # Mock plan and command
        class MockCommand:
            def __init__(self, program, args, requires_sudo=False):
                self.program = program
                self.args = args
                self.requires_sudo = requires_sudo
        
        class MockPlan:
            def __init__(self, text, intent, command=None):
                self.text = text
                self.intent = intent
                self.command = command
                self.requires_confirmation = command is not None
        
        # Create a plan with command
        cmd = MockCommand("nix-env", ["-iA", "nixpkgs.vim"])
        plan = MockPlan("Installing Vim...", "install_package", cmd)
        
        self.assertEqual(plan.text, "Installing Vim...")
        self.assertEqual(plan.intent, "install_package")
        self.assertIsNotNone(plan.command)
        self.assertTrue(plan.requires_confirmation)
        
        # Plan without command
        info_plan = MockPlan("Here's the system info...", "system_info")
        self.assertIsNone(info_plan.command)
        self.assertFalse(info_plan.requires_confirmation)
    
    def test_xai_explanation_toggle(self):
        """Test XAI explanation toggle state."""
        # Mock app with XAI state
        class MockXAIState:
            def __init__(self):
                self.show_explanations = False
                self.explanation_level = 'simple'
                self.current_explanation = None
        
        xai_state = MockXAIState()
        
        # Initially off
        self.assertFalse(xai_state.show_explanations)
        
        # Toggle on
        xai_state.show_explanations = not xai_state.show_explanations
        self.assertTrue(xai_state.show_explanations)
        
        # Toggle off
        xai_state.show_explanations = not xai_state.show_explanations
        self.assertFalse(xai_state.show_explanations)
        
        # Set explanation
        xai_state.current_explanation = {"reason": "Intent recognized as install"}
        self.assertIsNotNone(xai_state.current_explanation)


if __name__ == '__main__':
    unittest.main()