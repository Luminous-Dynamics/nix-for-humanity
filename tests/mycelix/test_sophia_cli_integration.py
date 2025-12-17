"""
Tests for Sophia CLI Integration

Verifies that Sophia can provide consciousness-aware assistance through the CLI.
"""

import pytest
from datetime import datetime

from luminous_nix.mycelix.sophia_cli_integration import (
    SophiaCLIAssistant,
    get_sophia_cli_assistant,
    enable_sophia_for_cli
)
from luminous_nix.mycelix.context import Context, IntentType, SessionState


def test_sophia_cli_assistant_initialization():
    """Test that Sophia CLI assistant initializes"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    assert assistant.user_id == "test_user"
    assert assistant.sophia is not None
    assert assistant.context is not None
    assert assistant.command_count == 0
    assert assistant.error_count == 0


def test_singleton_pattern():
    """Test that get_sophia_cli_assistant returns singleton"""
    assistant1 = get_sophia_cli_assistant()
    assistant2 = get_sophia_cli_assistant()

    assert assistant1 is assistant2


def test_enable_sophia_for_cli():
    """Test enabling Sophia for CLI"""
    result = enable_sophia_for_cli()

    assert result is True


def test_process_successful_command():
    """Test processing a successful command"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    response = assistant.process_command(
        command="nix-env -q",
        success=True,
        duration_ms=500
    )

    # Should track the command
    assert assistant.command_count == 1
    assert assistant.error_count == 0
    assert len(assistant.context.recent_commands) == 1

    # May or may not return insights for success
    # (depends on whether Sophia has actionable guidance)


def test_process_failed_command():
    """Test processing a failed command"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    response = assistant.process_command(
        command="nix-env -iA nonexistent",
        success=False,
        error="Package not found",
        duration_ms=1000
    )

    # Should track the error
    assert assistant.command_count == 1
    assert assistant.error_count == 1
    assert len(assistant.context.recent_commands) == 1

    # Should provide insights on error
    assert response is not None
    assert isinstance(response.message, str)


def test_process_multiple_commands():
    """Test processing multiple commands builds context"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # Success
    assistant.process_command("nix-env -q", success=True, duration_ms=100)

    # Success
    assistant.process_command("nix-shell", success=True, duration_ms=200)

    # Failure
    assistant.process_command("invalid", success=False, error="Bad command", duration_ms=50)

    assert assistant.command_count == 3
    assert assistant.error_count == 1
    assert len(assistant.context.recent_commands) == 3

    # Calculate success rate - should be 2/3
    successes = sum(1 for cmd in assistant.context.recent_commands if cmd.success)
    success_rate = successes / len(assistant.context.recent_commands)
    assert 0.6 < success_rate < 0.7


def test_get_proactive_insights():
    """Test getting proactive insights"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # Simulate some activity
    for i in range(5):
        assistant.process_command(f"command_{i}", success=True, duration_ms=100)

    # Get proactive insights
    response = assistant.get_proactive_insights()

    # May or may not have insights (depends on state)
    # Just verify it returns proper type
    assert response is None or hasattr(response, 'message')


def test_assess_current_state():
    """Test assessing current consciousness state"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # Execute some commands
    assistant.process_command("test", success=True, duration_ms=100)
    assistant.process_command("build", success=True, duration_ms=500)

    # Assess state
    state = assistant.assess_current_state()

    # Verify state structure
    assert "consciousness_level" in state
    assert "should_take_break" in state
    assert "emotional_state" in state
    assert "success_rate" in state
    assert "session_minutes" in state
    assert "insights" in state
    assert "priority_actions" in state
    assert "confidence" in state

    # Verify values are reasonable
    assert isinstance(state["consciousness_level"], str)
    assert isinstance(state["should_take_break"], bool)
    assert isinstance(state["success_rate"], float)
    assert 0.0 <= state["success_rate"] <= 1.0
    assert 0.0 <= state["confidence"] <= 1.0


def test_format_response_for_cli():
    """Test formatting Sophia's response for CLI display"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # Create a mock response
    from luminous_nix.mycelix.sophia import SophiaResponse, EmotionalTone

    response = SophiaResponse(
        message="You're doing great!",
        tone=EmotionalTone.ENCOURAGING,
        insights=["You have a high success rate", "You're in flow state"],
        suggestions=["Keep going", "Take a break in 15 minutes"],
        should_take_action=False,
        action_type=None
    )

    formatted = assistant.format_response_for_cli(response)

    # Verify formatting
    assert "Sophia:" in formatted
    assert "You're doing great!" in formatted
    assert "Insights:" in formatted
    assert "Suggestions:" in formatted


def test_biometric_estimation():
    """Test biometric state estimation from command patterns"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # All successful commands - should be calm
    for i in range(10):
        assistant.process_command(f"cmd_{i}", success=True, duration_ms=100)

    biometric = assistant._estimate_biometric_state()
    assert biometric is not None
    assert biometric.heart_rate >= 70  # Base HR
    assert biometric.hrv > 60.0  # Good HRV when calm

    # Add errors - should increase stress
    for i in range(10):
        assistant.process_command(f"err_{i}", success=False, error="Error", duration_ms=100)

    biometric_stressed = assistant._estimate_biometric_state()
    assert biometric_stressed.heart_rate > biometric.heart_rate
    assert biometric_stressed.hrv < biometric.hrv


def test_session_duration_tracking():
    """Test session duration tracking"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # Should start at 0
    duration = assistant._get_session_minutes()
    assert duration >= 0.0
    assert duration < 0.1  # Less than 6 seconds


def test_command_activity_tracking():
    """Test that command activity is properly tracked"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # Add command
    assistant.process_command("test", success=True, duration_ms=100)

    # Verify tracked
    assert len(assistant.context.recent_commands) == 1
    cmd = assistant.context.recent_commands[0]
    assert cmd.command == "test"
    assert cmd.success is True
    assert cmd.duration_ms == 100


def test_error_context_preservation():
    """Test that error context is preserved for causal analysis"""
    assistant = SophiaCLIAssistant(user_id="test_user")

    # Add failed command with error
    assistant.process_command(
        command="nix-build",
        success=False,
        error="Missing dependency: pkgs.python3",
        duration_ms=5000
    )

    # Verify failure is tracked
    cmd = assistant.context.recent_commands[0]
    assert cmd.success is False
    assert cmd.exit_code != 0  # Error indicated by non-zero exit code
    assert cmd.command == "nix-build"
