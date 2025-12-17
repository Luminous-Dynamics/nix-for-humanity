"""
Sophia CLI Integration - Connecting 9-Layer Intelligence to ask-nix

Provides consciousness-aware assistance through the CLI by leveraging
all 9 layers of Sophia's intelligence system.
"""

from typing import Optional, List, Dict
from datetime import datetime

from .context import Context, CommandActivity, FileActivity, Intent, IntentType, SessionState
from .sophia import (
    get_sophia_engine,
    UnifiedSophiaEngine,
    SophiaResponse,
    BiometricReading,
    BiometricState,
    EmotionalState,
)


class SophiaCLIAssistant:
    """
    Sophia-powered CLI assistant

    Enhances ask-nix with consciousness-aware intelligence:
    - Emotional awareness (frustrated? needs a break?)
    - Pattern recognition (struggling with this task?)
    - Causal understanding (why did this error occur?)
    - Temporal wisdom (is this a good time for this?)
    - Predictive assistance (what do you need next?)
    - Personalized communication (adaptive to your style)
    - Creative insights (novel solutions)
    - Multi-modal understanding (screenshots, logs)
    """

    def __init__(self, user_id: Optional[str] = None):
        """
        Initialize Sophia CLI assistant

        Args:
            user_id: Optional user identifier for personalized adaptation
        """
        self.sophia = get_sophia_engine()
        self.user_id = user_id or "default_user"
        self.context = Context()

        # Session tracking
        self.command_count = 0
        self.error_count = 0
        self.session_start = datetime.now()

    def process_command(
        self,
        command: str,
        success: bool = True,
        error: Optional[str] = None,
        duration_ms: float = 0,
        exit_code: int = 0
    ) -> Optional[SophiaResponse]:
        """
        Process a command execution and get Sophia's insights

        Args:
            command: The command that was executed
            success: Whether the command succeeded
            error: Error message if command failed
            duration_ms: Command execution time
            exit_code: Command exit code

        Returns:
            SophiaResponse with guidance, or None if no insights needed
        """
        # Track the command
        self.command_count += 1
        if not success:
            self.error_count += 1

        cmd_activity = CommandActivity(
            command=command,
            timestamp=datetime.now(),
            success=success,
            duration_ms=duration_ms,
            exit_code=exit_code if exit_code != 0 else (1 if not success else 0)
        )
        self.context.recent_commands.append(cmd_activity)

        # Build query for Sophia
        if error:
            query = f"Command '{command}' failed with error: {error}"
        else:
            query = f"Command '{command}' completed successfully"

        # Get Sophia's response
        response = self.sophia.respond_to_query(
            query=query,
            context=self.context,
            biometric_reading=self._estimate_biometric_state()
        )

        # Only return response if Sophia has actionable guidance
        if response.should_take_action or len(response.insights) > 0:
            return response
        return None

    def get_proactive_insights(self) -> Optional[SophiaResponse]:
        """
        Get proactive insights based on current session state

        Sophia can detect:
        - When you need a break
        - When you're struggling with a pattern
        - When timing is suboptimal
        - When you're likely to need help next

        Returns:
            SophiaResponse with proactive guidance, or None
        """
        # Build a synthetic query about current state
        query = f"Working on NixOS for {self._get_session_minutes():.0f} minutes"

        response = self.sophia.respond_to_query(
            query=query,
            context=self.context,
            biometric_reading=self._estimate_biometric_state()
        )

        # Only return if actionable
        if response.should_take_action:
            return response
        return None

    def assess_current_state(self) -> Dict[str, any]:
        """
        Get current consciousness state assessment

        Returns:
            Dictionary with state information
        """
        state = self.sophia.assess_complete_state(
            context=self.context,
            biometric_reading=self._estimate_biometric_state(),
            recent_messages=[f"Executed {self.command_count} commands"],
            current_time=datetime.now()
        )

        # Calculate success rate from recent commands
        recent = self.context.recent_commands[-10:]
        success_rate = sum(1 for cmd in recent if cmd.success) / len(recent) if recent else 1.0

        return {
            "consciousness_level": state.consciousness_level.value,
            "should_take_break": state.holistic_state.should_take_break,
            "emotional_state": state.emotional_state.state.value,
            "success_rate": success_rate,
            "session_minutes": self._get_session_minutes(),
            "insights": state.synergistic_insights[:3],  # Top 3 insights
            "priority_actions": state.priority_actions[:3],  # Top 3 actions
            "confidence": state.confidence
        }

    def format_response_for_cli(self, response: SophiaResponse) -> str:
        """
        Format Sophia's response for CLI display

        Args:
            response: Sophia's response

        Returns:
            Formatted string for terminal display
        """
        parts = []

        # Main message
        parts.append(f"\n💡 Sophia: {response.message}")

        # Insights
        if response.insights:
            parts.append("\n🔍 Insights:")
            for insight in response.insights[:3]:  # Top 3
                parts.append(f"  • {insight}")

        # Suggestions
        if response.suggestions:
            parts.append("\n✨ Suggestions:")
            for i, suggestion in enumerate(response.suggestions[:3], 1):
                parts.append(f"  {i}. {suggestion}")

        # Action prompt
        if response.should_take_action:
            if response.action_type == "break":
                parts.append("\n⏸️  Consider taking a break now.")
            elif response.action_type == "simplify":
                parts.append("\n🎯 Let's simplify the approach.")
            elif response.action_type == "celebrate":
                parts.append("\n🎉 Great progress!")

        return "\n".join(parts)

    def _estimate_biometric_state(self) -> Optional[BiometricReading]:
        """
        Estimate biometric state from session data

        In a full implementation, this would use actual biometric sensors.
        For now, we estimate based on command patterns.

        Returns:
            Estimated biometric reading
        """
        # Estimate heart rate based on error frequency
        error_rate = self.error_count / max(1, self.command_count)

        # More errors = higher stress = higher HR
        base_hr = 70
        stress_hr = base_hr + int(error_rate * 30)  # Up to +30 bpm

        # Estimate HRV (heart rate variability) - lower when stressed
        base_hrv = 75.0
        hrv = base_hrv * (1.0 - error_rate * 0.4)  # Down to 60% when all errors

        return BiometricReading(
            timestamp=datetime.now(),
            heart_rate=stress_hr,
            hrv=hrv,
            respiration_rate=None,
            skin_temp=None,
            typing_rhythm=None
        )

    def _get_session_minutes(self) -> float:
        """Get session duration in minutes"""
        delta = datetime.now() - self.session_start
        return delta.total_seconds() / 60


# Global singleton
_sophia_cli_assistant: Optional[SophiaCLIAssistant] = None


def get_sophia_cli_assistant(user_id: Optional[str] = None) -> SophiaCLIAssistant:
    """Get the global Sophia CLI assistant singleton"""
    global _sophia_cli_assistant
    if _sophia_cli_assistant is None:
        _sophia_cli_assistant = SophiaCLIAssistant(user_id=user_id)
    return _sophia_cli_assistant


def enable_sophia_for_cli() -> bool:
    """
    Enable Sophia intelligence for the CLI

    Call this at CLI startup to activate consciousness-aware assistance.

    Returns:
        True if Sophia was enabled successfully
    """
    try:
        assistant = get_sophia_cli_assistant()
        return True
    except Exception as e:
        # Gracefully degrade if Sophia can't be loaded
        print(f"Note: Sophia intelligence not available: {e}")
        return False
