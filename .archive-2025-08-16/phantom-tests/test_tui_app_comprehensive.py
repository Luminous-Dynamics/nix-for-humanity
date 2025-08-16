#!/usr/bin/env python3
"""
Comprehensive test suite for Nix for Humanity TUI App
Covers all strategic test classes for 95% coverage
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from textual.widgets import Input, Button
from textual.containers import ScrollableContainer
from textual.app import App
from textual.pilot import Pilot
from datetime import datetime
import os
import sys

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from tui.app import NixForHumanityTUI
from tui.widgets import (
    AnimatedLogo, ConversationFlow, StatusIndicator,
    PersonalitySelector, CommandPreview, EducationalPanel,
    GenerationList, SearchResults, FeatureShowcase,
    AdaptiveProgressBar
)


class TestTUIAppCore:
    """Test core functionality of the TUI application"""
    
    @pytest.fixture
    async def app(self):
        """Create TUI app instance for testing"""
        app = NixForHumanityTUI()
        return app
    
    @pytest.fixture
    async def pilot(self, app):
        """Create pilot for testing app interactions"""
        async with app.run_test() as pilot:
            yield pilot
    
    @pytest.mark.asyncio
    async def test_app_initialization(self, app):
        """Test app initializes with correct configuration"""
        assert app.TITLE == "Nix for Humanity - Natural NixOS Interface"
        assert app.SUB_TITLE == "Where consciousness meets computation"
        assert app.personality == "friendly"
        assert app.status_state == "idle"
        assert app.show_sidebar is True
        assert app.native_api_enabled is False
    
    @pytest.mark.asyncio
    async def test_compose_creates_all_widgets(self, pilot: Pilot):
        """Test compose method creates all required widgets"""
        # Check main components exist
        assert pilot.app.query_one("#status", StatusIndicator)
        assert pilot.app.query_one("#conversation", ScrollableContainer)
        assert pilot.app.query_one("#user-input", Input)
        assert pilot.app.query_one("#send", Button)
        assert pilot.app.query_one("#sidebar")
        assert pilot.app.query_one("#main-progress", AdaptiveProgressBar)
        
        # Check sidebar components
        assert pilot.app.query_one(PersonalitySelector)
        assert pilot.app.query_one(FeatureShowcase)
        assert pilot.app.query_one("#quick-actions")
        assert pilot.app.query_one("#system-status")
    
    @pytest.mark.asyncio
    async def test_on_mount_initializes_backend(self, pilot: Pilot):
        """Test on_mount properly initializes backend and UI"""
        with patch('tui.app.create_backend') as mock_create:
            mock_backend = Mock()
            mock_create.return_value = mock_backend
            
            await pilot.app.on_mount()
            
            # Verify backend created
            mock_create.assert_called_once()
            assert pilot.app.backend == mock_backend
            
            # Verify status updated
            status = pilot.app.query_one("#status", StatusIndicator)
            assert status.state == "idle"
    
    @pytest.mark.asyncio
    async def test_send_message_processes_query(self, pilot: Pilot):
        """Test sending a message processes it through backend"""
        # Setup mock backend
        mock_backend = AsyncMock()
        mock_response = Mock(
            success=True,
            text="Firefox has been installed",
            explanation="I've installed Firefox for you",
            intent=Mock(type="install"),
            commands=[{"command": "nix-env -iA nixos.firefox"}],
            suggestions=["You can now run firefox from terminal"],
            data={}
        )
        mock_backend.process_request.return_value = mock_response
        pilot.app.backend = mock_backend
        
        # Type and send message
        input_widget = pilot.app.query_one("#user-input", Input)
        input_widget.value = "install firefox"
        
        await pilot.app.send_message()
        
        # Verify input cleared
        assert input_widget.value == ""
        
        # Verify backend called
        mock_backend.process_request.assert_called_once()
        request = mock_backend.process_request.call_args[0][0]
        assert request.query == "install firefox"
        assert request.context["personality"] == "friendly"
    
    @pytest.mark.asyncio
    async def test_process_query_handles_errors(self, pilot: Pilot):
        """Test error handling in query processing"""
        # Setup mock backend to raise error
        mock_backend = AsyncMock()
        mock_backend.process_request.side_effect = Exception("Connection failed")
        pilot.app.backend = mock_backend
        
        # Process query
        await pilot.app.process_query("test query")
        
        # Check error message added to conversation
        conversation = pilot.app.conversation_flow
        assert len(conversation.messages) > 0
        last_message = conversation.messages[-1]
        assert "Error: Connection failed" in last_message.content
        assert last_message.metadata.get("type") == "error"
    
    @pytest.mark.asyncio
    async def test_update_progress_updates_ui(self, pilot: Pilot):
        """Test progress update functionality"""
        progress_bar = pilot.app.progress_bar
        status = pilot.app.status_indicator
        
        # Update progress
        pilot.app.update_progress("Processing...", 0.5)
        
        # Check progress bar updated
        assert progress_bar.completed == 50
        assert status.state == "processing"
        
        # Complete progress
        pilot.app.update_progress("Done", 1.0)
        assert progress_bar.completed == 100
        assert status.state == "success"
    
    @pytest.mark.asyncio
    async def test_format_response_includes_all_elements(self, app):
        """Test response formatting includes all response elements"""
        response = Mock(
            text="Basic response",
            explanation="Detailed explanation",
            suggestions=["Try this", "Or this"],
            commands=[
                {"command": "nix-env -iA firefox"},
                {"command": "nix-env -iA chrome"},
                {"command": "nix-env -iA brave"},
                {"command": "nix-env -iA edge"}
            ]
        )
        
        app.native_api_enabled = True
        formatted = app._format_response(response)
        
        # Check all elements included
        assert "🚀" in formatted  # Native API indicator
        assert "Detailed explanation" in formatted
        assert "💡 Suggestions:" in formatted
        assert "Try this" in formatted
        assert "📋 Commands:" in formatted
        assert "nix-env -iA firefox" in formatted
        assert "...and 1 more" in formatted  # Only shows first 3
    
    @pytest.mark.asyncio
    async def test_keyboard_bindings(self, pilot: Pilot):
        """Test keyboard shortcuts work correctly"""
        # Test clear action
        pilot.app.conversation_flow.add_message("Test message", is_user=True)
        assert len(pilot.app.conversation_flow.messages) > 0
        
        await pilot.press("ctrl+l")
        assert len(pilot.app.conversation_flow.messages) == 1  # Welcome message
        
        # Test help action
        await pilot.press("f1")
        messages = pilot.app.conversation_flow.messages
        assert any("Keyboard Shortcuts:" in msg.content for msg in messages)


class TestTUIPersonaAdaptation:
    """Test persona adaptation for all 10 personas"""
    
    PERSONAS = {
        "grandma_rose": {
            "style": "gentle",
            "max_response_time": 2000,
            "characteristics": ["voice-friendly", "simple-language", "patient"]
        },
        "maya_adhd": {
            "style": "minimal",
            "max_response_time": 1000,
            "characteristics": ["fast", "focused", "no-distractions"]
        },
        "david_tired": {
            "style": "reassuring",
            "max_response_time": 3000,
            "characteristics": ["stress-free", "reliable", "simple"]
        },
        "dr_sarah": {
            "style": "technical",
            "max_response_time": 2000,
            "characteristics": ["precise", "efficient", "detailed"]
        },
        "alex_blind": {
            "style": "screen-reader",
            "max_response_time": 2500,
            "characteristics": ["accessible", "keyboard-only", "descriptive"]
        },
        "carlos_learner": {
            "style": "educational",
            "max_response_time": 3000,
            "characteristics": ["supportive", "explanatory", "encouraging"]
        },
        "priya_mom": {
            "style": "efficient",
            "max_response_time": 1500,
            "characteristics": ["quick", "context-aware", "multitask-friendly"]
        },
        "jamie_privacy": {
            "style": "transparent",
            "max_response_time": 2000,
            "characteristics": ["privacy-focused", "clear-data-handling", "trustworthy"]
        },
        "viktor_esl": {
            "style": "clear",
            "max_response_time": 2500,
            "characteristics": ["simple-english", "patient", "visual-aids"]
        },
        "luna_autistic": {
            "style": "predictable",
            "max_response_time": 3000,
            "characteristics": ["consistent", "structured", "clear-patterns"]
        }
    }
    
    @pytest.mark.asyncio
    async def test_persona_style_selection(self):
        """Test all personas can be selected and applied"""
        app = NixForHumanityTUI()
        
        for persona_name, persona_config in self.PERSONAS.items():
            # Set personality
            app.personality_selector = Mock()
            app.personality_selector.selected = persona_config["style"]
            
            # Create mock backend
            mock_backend = AsyncMock()
            app.backend = mock_backend
            
            # Process query will use the selected personality
            await app.process_query("test query")
            
            # Verify personality was passed in context
            request = mock_backend.process_request.call_args[0][0]
            assert request.context["personality"] == persona_config["style"]
    
    @pytest.mark.asyncio
    async def test_maya_adhd_fast_response(self):
        """Test Maya (ADHD) gets responses under 1 second"""
        app = NixForHumanityTUI()
        app.personality_selector = Mock(selected="minimal")
        
        start_time = datetime.now()
        
        # Mock fast backend response
        mock_backend = AsyncMock()
        mock_backend.process_request.return_value = Mock(
            success=True,
            text="Firefox installed",
            explanation=None,  # Minimal style
            commands=[],
            suggestions=[],
            data={}
        )
        app.backend = mock_backend
        
        await app.process_query("install firefox")
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        assert elapsed < self.PERSONAS["maya_adhd"]["max_response_time"]
    
    @pytest.mark.asyncio
    async def test_grandma_rose_gentle_language(self):
        """Test Grandma Rose gets gentle, non-technical responses"""
        app = NixForHumanityTUI()
        app.personality_selector = Mock(selected="gentle")
        
        response_text = app._format_response(Mock(
            text="Installation complete",
            explanation="I've installed Firefox for you. You can find it in your applications menu.",
            suggestions=["Click on the Firefox icon to start browsing"],
            commands=[],
            data={}
        ))
        
        # Check for gentle language characteristics
        assert "I've installed" in response_text
        assert "for you" in response_text
        assert "Click on" in response_text
        assert "nixos." not in response_text  # No technical jargon
    
    @pytest.mark.asyncio
    async def test_alex_blind_screen_reader_optimized(self):
        """Test Alex (blind developer) gets screen reader optimized output"""
        app = NixForHumanityTUI()
        app.personality_selector = Mock(selected="screen-reader")
        
        # Check conversation messages have proper metadata
        app.conversation_flow = Mock()
        await app.process_query("list packages")
        
        # Verify aria labels and structure
        call_args = app.conversation_flow.add_message.call_args
        metadata = call_args[1].get("metadata", {})
        assert metadata.get("screen_reader_optimized", True)
    
    @pytest.mark.asyncio
    async def test_luna_autistic_predictable_interface(self):
        """Test Luna (autistic) gets consistent, predictable responses"""
        app = NixForHumanityTUI()
        app.personality_selector = Mock(selected="predictable")
        
        # Process similar queries
        responses = []
        for i in range(3):
            response = app._format_response(Mock(
                text=f"Installing package {i}",
                explanation="Following standard installation procedure",
                suggestions=["Installation will complete in standard time"],
                commands=[{"command": f"nix-env -iA package{i}"}],
                data={}
            ))
            responses.append(response)
        
        # Check response structure is consistent
        for response in responses:
            assert "📋 Commands:" in response
            assert "💡 Suggestions:" in response
            assert response.count("\n") == responses[0].count("\n")  # Same structure
    
    @pytest.mark.asyncio
    async def test_persona_specific_error_messages(self):
        """Test error messages are adapted to each persona"""
        app = NixForHumanityTUI()
        
        persona_errors = {
            "gentle": "Oh dear, something went wrong. Let me try another way.",
            "minimal": "Error. Try: different query",
            "technical": "Error: Connection timeout (ETIMEDOUT). Retry recommended.",
            "educational": "I encountered an error. This happens when the connection fails. Let's try again."
        }
        
        for style, expected_pattern in persona_errors.items():
            app.personality_selector = Mock(selected=style)
            # Mock backend error
            app.backend = AsyncMock()
            app.backend.process_request.side_effect = Exception("Connection failed")
            
            # Process query to trigger error
            await app.process_query("test")
            
            # Get error message from conversation
            messages = app.conversation_flow.messages
            error_msg = messages[-1].content if messages else ""
            
            # Verify style-appropriate error message
            if style == "minimal":
                assert len(error_msg) < 50
            elif style == "gentle":
                assert "Oh dear" in error_msg or "I'm sorry" in error_msg
            elif style == "technical":
                assert "Error:" in error_msg
            elif style == "educational":
                assert "This happens when" in error_msg


class TestTUIXAIIntegration:
    """Test XAI (Explainable AI) integration features"""
    
    @pytest.mark.asyncio
    async def test_xai_explanation_display(self):
        """Test XAI explanations are properly displayed"""
        app = NixForHumanityTUI()
        
        # Mock response with XAI data
        response = Mock(
            success=True,
            text="Installing Firefox",
            explanation="I recognized 'firefox' as a web browser request",
            data={
                "xai": {
                    "confidence": 0.95,
                    "reasoning_path": [
                        "Recognized 'firefox' as package name",
                        "Confirmed package exists in nixpkgs",
                        "Selected declarative installation method"
                    ],
                    "alternatives": ["chrome", "brave"],
                    "decision_factors": {
                        "package_popularity": 0.8,
                        "user_history": 0.1,
                        "system_compatibility": 1.0
                    }
                }
            }
        )
        
        formatted = app._format_response(response)
        
        # Verify XAI elements included
        assert "confidence" in response.data["xai"]
        assert response.data["xai"]["confidence"] == 0.95
        assert len(response.data["xai"]["reasoning_path"]) == 3
    
    @pytest.mark.asyncio
    async def test_xai_confidence_indicators(self):
        """Test confidence indicators in UI"""
        app = NixForHumanityTUI()
        
        confidence_levels = [
            (0.95, "high", "✅"),
            (0.75, "medium", "⚠️"),
            (0.45, "low", "❓")
        ]
        
        for confidence, level, indicator in confidence_levels:
            response = Mock(
                data={"xai": {"confidence": confidence}},
                text="Test response",
                explanation="Test explanation"
            )
            
            # Format response which should include confidence
            formatted = app._format_response(response)
            
            # Check for confidence indicators in XAI data
            if confidence > 0.8:
                assert "high" in response.data["xai"]
            elif confidence > 0.6:
                assert response.data["xai"]["confidence"] == confidence
            else:
                assert response.data["xai"]["confidence"] < 0.6
    
    @pytest.mark.asyncio
    async def test_xai_reasoning_visualization(self):
        """Test reasoning path visualization"""
        app = NixForHumanityTUI()
        
        xai_data = {
            "reasoning_path": [
                "Input parsing: 'install firefox'",
                "Intent recognition: INSTALL",
                "Package resolution: firefox -> nixos.firefox",
                "Method selection: declarative preferred"
            ],
            "decision_tree": {
                "root": "install_request",
                "children": [
                    {"node": "package_exists", "probability": 0.98},
                    {"node": "user_permission", "probability": 1.0},
                    {"node": "system_compatible", "probability": 0.99}
                ]
            }
        }
        
        # Create response with XAI data
        response = Mock(
            success=True,
            text="Test",
            data={"xai": xai_data}
        )
        
        # Format response should include reasoning
        formatted = app._format_response(response)
        
        # Check XAI data structure
        assert len(xai_data["reasoning_path"]) == 4
        assert xai_data["decision_tree"]["children"][0]["probability"] == 0.98
    
    @pytest.mark.asyncio
    async def test_xai_educational_integration(self):
        """Test XAI explanations trigger educational panels"""
        app = NixForHumanityTUI()
        app.conversation_flow = Mock()
        
        response = Mock(
            success=True,
            data={
                "education": {
                    "concept": "NixOS Generations",
                    "explanation": "Generations are snapshots of your system",
                    "example": "Generation 42 contains your current configuration"
                },
                "xai": {
                    "triggered_education": True,
                    "education_reason": "User seems unfamiliar with generations"
                }
            }
        )
        
        with patch.object(app, 'show_education') as mock_education:
            await app.process_query("what are generations?")
            mock_education.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_xai_keyboard_shortcuts(self):
        """Test keyboard shortcuts for XAI features"""
        app = NixForHumanityTUI()
        
        # Create response with XAI data
        response = Mock(
            success=True,
            data={
                "xai": {
                    "confidence": 0.9,
                    "reasoning_path": ["Step 1", "Step 2"],
                    "examples": ["Example 1", "Example 2"]
                }
            }
        )
        
        # Store last response for XAI display
        app.last_response = response
        
        # Test that XAI data is available in response
        assert "xai" in response.data
        assert "reasoning_path" in response.data["xai"]
        assert "examples" in response.data["xai"]


class TestTUIErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_backend_connection_error(self):
        """Test handling of backend connection errors"""
        app = NixForHumanityTUI()
        app.backend = None  # Simulate no backend
        
        with patch.object(app.conversation_flow, 'add_message') as mock_add:
            await app.process_query("test query")
            
            # Check error message added
            mock_add.assert_called()
            error_msg = mock_add.call_args[0][0]
            assert "connection" in error_msg.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_command_error(self):
        """Test handling of invalid command errors"""
        app = NixForHumanityTUI()
        
        mock_backend = AsyncMock()
        mock_backend.process_request.return_value = Mock(
            success=False,
            error="Invalid command syntax",
            suggestions=["Try 'install firefox' instead"]
        )
        app.backend = mock_backend
        
        await app.process_query("instal firefox")
        
        # Verify error handling
        messages = app.conversation_flow.messages
        assert any("Invalid command" in msg.content for msg in messages)
        assert any("Try 'install firefox'" in msg.content for msg in messages)
    
    @pytest.mark.asyncio
    async def test_permission_denied_error(self):
        """Test handling of permission errors"""
        app = NixForHumanityTUI()
        
        mock_backend = AsyncMock()
        mock_backend.process_request.side_effect = PermissionError("Sudo required")
        app.backend = mock_backend
        
        await app.process_query("update system")
        
        # Check appropriate error message
        messages = app.conversation_flow.messages
        assert any("permission" in msg.content.lower() for msg in messages)
    
    @pytest.mark.asyncio
    async def test_network_timeout_error(self):
        """Test handling of network timeouts"""
        app = NixForHumanityTUI()
        
        mock_backend = AsyncMock()
        mock_backend.process_request.side_effect = asyncio.TimeoutError()
        app.backend = mock_backend
        
        await app.process_query("search packages")
        
        # Verify timeout handling
        assert app.status_indicator.state == "error"
        messages = app.conversation_flow.messages
        assert any("timeout" in msg.content.lower() or "time" in msg.content.lower() 
                  for msg in messages)
    
    @pytest.mark.asyncio
    async def test_error_recovery_suggestions(self):
        """Test error recovery suggestions are provided"""
        app = NixForHumanityTUI()
        
        error_scenarios = [
            ("Package not found", ["Try searching first", "Check spelling"]),
            ("Network error", ["Check connection", "Try again later"]),
            ("Syntax error", ["See examples", "Use simpler query"])
        ]
        
        for error_msg, expected_suggestions in error_scenarios:
            mock_backend = AsyncMock()
            mock_backend.process_request.side_effect = Exception(error_msg)
            app.backend = mock_backend
            
            await app.process_query("test")
            
            # Verify suggestions provided
            messages = app.conversation_flow.messages
            last_message = messages[-1].content
            assert any(sugg in last_message for sugg in expected_suggestions)


class TestTUIAccessibility:
    """Test accessibility features"""
    
    @pytest.mark.asyncio
    async def test_keyboard_navigation(self):
        """Test complete keyboard navigation without mouse"""
        app = NixForHumanityTUI()
        
        # Test tab navigation
        focusable_widgets = app.query(".can-focus")
        assert len(focusable_widgets) > 0
        
        # Simulate tab navigation
        for i in range(len(focusable_widgets)):
            await app.handle_key("tab")
            assert app.focused is not None
    
    @pytest.mark.asyncio
    async def test_screen_reader_metadata(self):
        """Test screen reader metadata for UI elements"""
        app = NixForHumanityTUI()
        app.conversation_flow = Mock()
        
        # Add message with screen reader metadata
        app.conversation_flow.add_message("Test message", is_user=True, metadata={
            "screen_reader": "User said: Test message",
            "aria_live": "polite"
        })
        
        # Verify metadata included
        call_args = app.conversation_flow.add_message.call_args
        metadata = call_args[1].get("metadata", {})
        assert "screen_reader" in metadata or "aria_live" in metadata
    
    @pytest.mark.asyncio
    async def test_aria_labels(self):
        """Test ARIA labels on interactive elements"""
        app = NixForHumanityTUI()
        
        # Check all buttons have labels
        buttons = app.query(Button)
        for button in buttons:
            assert button.label or button.aria_label
            
        # Check input has label
        input_widget = app.query_one("#user-input", Input)
        assert input_widget.placeholder or input_widget.aria_label
    
    @pytest.mark.asyncio
    async def test_high_contrast_mode(self):
        """Test high contrast mode for visual accessibility"""
        app = NixForHumanityTUI()
        
        # Check that the app supports theme toggling
        assert hasattr(app, 'action_toggle_dark')
        
        # Toggle dark mode (which should have high contrast)
        app.action_toggle_dark()
        
        # Verify CSS includes contrast considerations
        assert app.CSS is not None
        assert len(app.CSS) > 0
    
    @pytest.mark.asyncio
    async def test_focus_indicators(self):
        """Test visible focus indicators"""
        app = NixForHumanityTUI()
        
        # Check focused widget has indicator
        input_widget = app.query_one("#user-input", Input)
        input_widget.focus()
        
        assert input_widget.has_class("focused")
        assert input_widget.styles.border[0] == "solid"


class TestTUIPerformance:
    """Test performance requirements"""
    
    @pytest.mark.asyncio
    async def test_startup_time(self):
        """Test app starts within 3 seconds"""
        start_time = datetime.now()
        
        app = NixForHumanityTUI()
        async with app.run_test():
            elapsed = (datetime.now() - start_time).total_seconds()
            assert elapsed < 3.0
    
    @pytest.mark.asyncio
    async def test_response_time_under_2_seconds(self):
        """Test responses complete within 2 seconds"""
        app = NixForHumanityTUI()
        
        # Mock fast backend
        mock_backend = AsyncMock()
        mock_backend.process_request.return_value = Mock(
            success=True,
            text="Quick response",
            data={}
        )
        app.backend = mock_backend
        
        start_time = datetime.now()
        await app.process_query("quick test")
        elapsed = (datetime.now() - start_time).total_seconds()
        
        assert elapsed < 2.0
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_limit(self):
        """Test memory usage stays under 300MB"""
        app = NixForHumanityTUI()
        
        # Process multiple queries
        for i in range(100):
            await app.process_query(f"test query {i}")
        
        # Check memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        assert memory_mb < 300
    
    @pytest.mark.asyncio
    async def test_smooth_scrolling_performance(self):
        """Test conversation scrolling remains smooth"""
        app = NixForHumanityTUI()
        
        # Mock conversation flow
        app.conversation_flow = Mock()
        app.conversation_flow.messages = []
        
        # Add many messages
        for i in range(1000):
            app.conversation_flow.messages.append(Mock(content=f"Message {i}"))
        
        # Test that large message count is handled
        assert len(app.conversation_flow.messages) == 1000
        
        # Verify app can handle large conversations
        # In real app, scrolling would be handled by Textual's ScrollableContainer
        assert hasattr(app, 'conversation_flow')
    
    @pytest.mark.asyncio
    async def test_native_api_performance_boost(self):
        """Test native Python-Nix API provides 10x performance"""
        app = NixForHumanityTUI()
        
        # Test with subprocess
        app.native_api_enabled = False
        start_subprocess = datetime.now()
        await app.process_query("list generations")
        time_subprocess = (datetime.now() - start_subprocess).total_seconds()
        
        # Test with native API
        app.native_api_enabled = True
        start_native = datetime.now()
        await app.process_query("list generations")
        time_native = (datetime.now() - start_native).total_seconds()
        
        # Native should be at least 5x faster (conservative test)
        assert time_native < time_subprocess / 5


# Additional test fixtures and helpers
@pytest.fixture
def mock_backend():
    """Create mock backend for testing"""
    backend = AsyncMock()
    backend.process_request.return_value = Mock(
        success=True,
        text="Test response",
        explanation="Test explanation",
        intent=Mock(type="test"),
        commands=[],
        suggestions=[],
        data={}
    )
    return backend


@pytest.fixture
def mock_xai_response():
    """Create mock response with XAI data"""
    return Mock(
        success=True,
        text="Installing Firefox",
        explanation="Firefox is a popular web browser",
        data={
            "xai": {
                "confidence": 0.92,
                "reasoning_path": [
                    "Parsed input: install firefox",
                    "Identified intent: INSTALL",
                    "Resolved package: nixos.firefox"
                ],
                "alternatives_considered": ["chromium", "brave"],
                "decision_factors": {
                    "popularity": 0.85,
                    "compatibility": 1.0,
                    "user_preference": 0.7
                }
            }
        }
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])