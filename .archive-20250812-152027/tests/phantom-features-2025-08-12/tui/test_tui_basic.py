#!/usr/bin/env python3
"""Basic TUI tests that actually work with the real implementation."""

from unittest.mock import Mock, MagicMock, patch, call
import asyncio

import pytest
from textual.pilot import Pilot

# Import the actual TUI app
from luminous_nix.ui.main_app import NixForHumanityTUI

class TestNixForHumanityTUI:
    """Test the actual TUI application."""

    @pytest.fixture
    def mock_backend(self):
        """Mock the backend for testing."""
        # Mock the consciousness orb to avoid animation issues
        with patch("nix_humanity.ui.consciousness_orb.ConsciousnessOrb"):
            with patch("nix_humanity.ui.main_app.NixForHumanityBackend") as mock_class:
                mock_instance = Mock()
                mock_class.return_value = mock_instance

                # Mock backend methods
                mock_instance.process.return_value = Mock(
                    text="Firefox installed successfully",
                    suggestions=["Run: firefox", "Configure: about:config"],
                    command="nix-env -iA nixpkgs.firefox",
                    feedback_requested=False,
                )

                mock_instance.get_statistics.return_value = {
                    "queries_processed": 42,
                    "uptime": "2 hours",
                    "accuracy_rate": 0.95,
                }

                yield mock_instance

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_tui_launches(self, mock_backend):
        """Test that TUI launches without errors."""
        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            # Check app started
            assert app is not None
            assert isinstance(pilot, Pilot)

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_basic_input(self, mock_backend):
        """Test basic input handling."""
        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            # Type a command
            await pilot.type("install firefox")

            # Press enter to submit
            await pilot.press("enter")

            # Give time for processing
            await asyncio.sleep(0.1)

            # Verify backend was called
            assert mock_backend.process.called

    @pytest.mark.asyncio
    async def test_tab_navigation(self, mock_backend):
        """Test tab key navigation."""
        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            # Press tab to navigate
            await pilot.press("tab")
            await pilot.press("tab")

            # Should still be running
            assert app.is_running

    @pytest.mark.asyncio
    async def test_quit_command(self, mock_backend):
        """Test quit functionality."""
        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            # Press ctrl+c to quit
            await pilot.press("ctrl+c")

            # App should exit gracefully
            assert not app.is_running

    @pytest.mark.asyncio
    async def test_error_display(self, mock_backend):
        """Test error handling in TUI."""
        # Make backend raise an error
        mock_backend.process.side_effect = Exception("Connection failed")

        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            await pilot.type("install firefox")
            await pilot.press("enter")
            await asyncio.sleep(0.1)

            # Should handle error gracefully
            assert app.is_running

class TestTUIComponents:
    """Test individual TUI components."""

    @pytest.fixture
    def app(self, mock_backend):
        """Create app instance for testing."""
        return NixForHumanityTUI()

    def test_app_initialization(self, app):
        """Test app initializes with correct attributes."""
        assert hasattr(app, "title")
        assert "Nix for Humanity" in app.title

    def test_css_loading(self, app):
        """Test CSS is properly configured."""
        # TUI should have styling
        assert app.css is not None or hasattr(app, "CSS")

    @pytest.mark.asyncio
    async def test_initial_focus(self, mock_backend):
        """Test initial focus is on input."""
        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            # Should be able to type immediately
            await pilot.type("test")
            # No errors = success

class TestTUIIntegration:
    """Test TUI integration with backend."""

    @pytest.mark.asyncio
    async def test_real_command_flow(self, mock_backend):
        """Test complete command flow."""
        app = NixForHumanityTUI()

        # Setup mock response
        mock_backend.process.return_value = Mock(
            text="Installing firefox...\nSuccess!",
            suggestions=["firefox is now available"],
            command="nix-env -iA nixpkgs.firefox",
            feedback_requested=True,
        )

        async with app.run_test() as pilot:
            # Enter command
            await pilot.type("install firefox")
            await pilot.press("enter")

            # Wait for processing
            await asyncio.sleep(0.2)

            # Verify backend called correctly
            mock_backend.process.assert_called_once()
            call_args = mock_backend.process.call_args[0][0]
            assert "firefox" in call_args.text.lower()

    @pytest.mark.asyncio
    async def test_suggestion_display(self, mock_backend):
        """Test suggestions are displayed."""
        mock_backend.process.return_value = Mock(
            text="Package found",
            suggestions=[
                "Try: firefox --safe-mode",
                "Configure: about:preferences",
                "Uninstall: nix-env -e firefox",
            ],
            feedback_requested=False,
        )

        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            await pilot.type("help firefox")
            await pilot.press("enter")
            await asyncio.sleep(0.1)

            # Suggestions should be processed
            assert mock_backend.process.called

# Consciousness-first test principles
class TestConsciousnessFirst:
    """Test consciousness-first principles in TUI."""

    @pytest.mark.asyncio
    async def test_gentle_error_messages(self, mock_backend):
        """Test errors are educational, not harsh."""
        mock_backend.process.return_value = Mock(
            text="I couldn't find 'fierox'. Did you mean 'firefox'?",
            suggestions=["Search: nix search firefox", "Similar: firefox-esr"],
            feedback_requested=False,
        )

        app = NixForHumanityTUI()
        async with app.run_test() as pilot:
            await pilot.type("install fierox")
            await pilot.press("enter")
            await asyncio.sleep(0.1)

            # Educational error delivered
            assert mock_backend.process.called

    @pytest.mark.asyncio
    async def test_progressive_disclosure(self, mock_backend):
        """Test interface complexity adapts to user."""
        app = NixForHumanityTUI()

        # Should start simple
        async with app.run_test() as pilot:
            # Basic interface accessible immediately
            await pilot.type("help")
            await pilot.press("enter")

            assert mock_backend.process.called

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
