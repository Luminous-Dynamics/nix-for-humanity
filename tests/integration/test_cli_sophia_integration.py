"""
Integration Tests for CLI + Sophia

Verifies that Sophia intelligence is properly integrated into the CLI
and provides consciousness-aware assistance during command execution.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime


def test_cli_initializes_sophia():
    """Test that CLI initializes Sophia assistant"""
    with patch('luminous_nix.mycelix.get_sophia_cli_assistant') as mock_get:
        mock_sophia = Mock()
        mock_get.return_value = mock_sophia

        from luminous_nix.frontends.cli import UnifiedNixAssistant

        cli = UnifiedNixAssistant()

        # Verify Sophia was requested
        mock_get.assert_called_once()

        # Verify CLI has Sophia reference
        assert cli.sophia_assistant == mock_sophia


def test_cli_calls_sophia_on_successful_install():
    """Test that CLI calls Sophia when install succeeds"""
    from luminous_nix.frontends.cli import UnifiedNixAssistant

    cli = UnifiedNixAssistant()

    # Mock Sophia
    mock_sophia = Mock()
    mock_sophia.process_command = Mock(return_value=None)
    cli.sophia_assistant = mock_sophia

    # Mock command executor
    mock_cmd = Mock()
    mock_result = Mock()
    mock_result.success = Mock(return_value=True)
    mock_result.status = Mock()

    with patch.object(cli, 'command_executor') as mock_executor:
        mock_executor.create_command = Mock(return_value=mock_cmd)
        mock_executor.execute = Mock(return_value=mock_result)

        # Execute install
        cli._install_package_robust("firefox")

        # Verify Sophia was called
        mock_sophia.process_command.assert_called_once()

        # Verify call included success=True
        call_args = mock_sophia.process_command.call_args
        assert call_args.kwargs['success'] is True
        assert 'firefox' in call_args.kwargs['command']


def test_cli_calls_sophia_on_failed_install():
    """Test that CLI calls Sophia when install fails"""
    from luminous_nix.frontends.cli import UnifiedNixAssistant

    cli = UnifiedNixAssistant()

    # Mock Sophia
    mock_sophia = Mock()
    mock_sophia.process_command = Mock(return_value=None)
    cli.sophia_assistant = mock_sophia

    # Mock command executor with failure
    mock_cmd = Mock()
    mock_result = Mock()
    mock_result.success = Mock(return_value=False)
    mock_result.stderr = "Package not found"

    with patch.object(cli, 'command_executor') as mock_executor:
        with patch.object(cli, 'error_recovery', None):  # Disable error recovery
            mock_executor.create_command = Mock(return_value=mock_cmd)
            mock_executor.execute = Mock(return_value=mock_result)

            # Execute install (should fail)
            cli._install_package_robust("nonexistent-package")

            # Verify Sophia was called
            mock_sophia.process_command.assert_called_once()

            # Verify call included success=False and error
            call_args = mock_sophia.process_command.call_args
            assert call_args.kwargs['success'] is False
            assert call_args.kwargs['error'] == "Package not found"


def test_cli_displays_sophia_insights():
    """Test that CLI displays Sophia's insights when provided"""
    from luminous_nix.frontends.cli import UnifiedNixAssistant
    from luminous_nix.mycelix.sophia import SophiaResponse, EmotionalTone

    cli = UnifiedNixAssistant()

    # Create mock Sophia response
    response = SophiaResponse(
        message="You're doing great!",
        tone=EmotionalTone.ENCOURAGING,
        insights=["High success rate", "Good flow state"],
        suggestions=["Keep going", "Take a break soon"],
        should_take_action=False,
        action_type=None
    )

    # Mock Sophia to return insights
    mock_sophia = Mock()
    mock_sophia.process_command = Mock(return_value=response)
    mock_sophia.format_response_for_cli = Mock(return_value="Formatted insight")
    cli.sophia_assistant = mock_sophia

    # Mock command executor
    mock_cmd = Mock()
    mock_result = Mock()
    mock_result.success = Mock(return_value=True)

    with patch.object(cli, 'command_executor') as mock_executor:
        with patch('builtins.print') as mock_print:
            mock_executor.create_command = Mock(return_value=mock_cmd)
            mock_executor.execute = Mock(return_value=mock_result)

            # Execute install
            cli._install_package_robust("firefox")

            # Verify format_response_for_cli was called
            mock_sophia.format_response_for_cli.assert_called_once_with(response)

            # Verify formatted output was printed
            mock_print.assert_any_call("Formatted insight")


def test_cli_handles_sophia_unavailable_gracefully():
    """Test that CLI works fine when Sophia is not available"""
    from luminous_nix.frontends.cli import UnifiedNixAssistant

    cli = UnifiedNixAssistant()
    cli.sophia_assistant = None  # Sophia not available

    # Mock command executor
    mock_cmd = Mock()
    mock_result = Mock()
    mock_result.success = Mock(return_value=True)

    with patch.object(cli, 'command_executor') as mock_executor:
        mock_executor.create_command = Mock(return_value=mock_cmd)
        mock_executor.execute = Mock(return_value=mock_result)

        # Execute install - should work without Sophia
        cli._install_package_robust("firefox")

        # Should complete without errors (no exception raised)
        assert True


def test_sophia_tracks_command_duration():
    """Test that Sophia receives accurate command duration"""
    from luminous_nix.frontends.cli import UnifiedNixAssistant

    cli = UnifiedNixAssistant()

    # Mock Sophia
    mock_sophia = Mock()
    mock_sophia.process_command = Mock(return_value=None)
    cli.sophia_assistant = mock_sophia

    # Mock command executor
    mock_cmd = Mock()
    mock_result = Mock()
    mock_result.success = Mock(return_value=True)

    with patch.object(cli, 'command_executor') as mock_executor:
        mock_executor.create_command = Mock(return_value=mock_cmd)
        mock_executor.execute = Mock(return_value=mock_result)

        # Execute install
        cli._install_package_robust("firefox")

        # Verify Sophia was called with duration_ms
        call_args = mock_sophia.process_command.call_args
        assert 'duration_ms' in call_args.kwargs
        assert call_args.kwargs['duration_ms'] >= 0  # Should be non-negative
