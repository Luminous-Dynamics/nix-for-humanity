"""
🌟 UX-TUI Integration Module

Bridges the UserExperienceSystem with the TUI's AdaptiveUISystem.
This creates a unified adaptive experience across CLI and TUI interfaces.
"""

from dataclasses import dataclass
from typing import Any, Optional
import logging

from ..core.user_experience import UserExperienceSystem, get_user_experience, ProactiveInsight
from ..core.personality_system import PersonalityStyle
from .adaptive_complexity import (
    AdaptiveUISystem,
    UIComplexityLevel,
    AdaptiveUIConfig,
    UIElement,
    NIXOS_UI_ELEMENTS,
)
from .consciousness_orb import EmotionalState

logger = logging.getLogger(__name__)


@dataclass
class TUIUserContext:
    """
    Adapter that converts UserExperienceSystem profile to AdaptiveUISystem's expected format.

    This bridges the behavioral learning system with the UI complexity system.
    """
    technical_proficiency: float = 0.5
    confidence_level: float = 0.5
    patience_level: float = 0.5
    preferred_verbosity: float = 0.5
    learning_speed: float = 0.5
    exploration_tendency: float = 0.5
    frustration_level: float = 0.0
    current_mood: EmotionalState = EmotionalState.NEUTRAL
    session_count: int = 1

    # For compatibility with DynamicPersona interface
    @property
    def mode(self) -> str:
        """Compatibility property"""
        return "standard"


class UXTUIBridge:
    """
    Bridges UserExperienceSystem with TUI's AdaptiveUISystem.

    This integration:
    - Converts behavioral learning profiles to UI complexity settings
    - Maps personality styles to visual presentations
    - Provides proactive suggestions appropriate for TUI display
    - Maintains consistency between CLI and TUI experiences
    """

    def __init__(self, user_id: Optional[str] = None):
        """
        Initialize the bridge.

        Args:
            user_id: Optional user identifier for personalization
        """
        # Get or create the user experience system
        self.ux = get_user_experience() if user_id is None else UserExperienceSystem(user_id)

        # Create the UI system
        self.ui_system = AdaptiveUISystem()

        # Track state
        self._last_complexity_level = UIComplexityLevel.STANDARD
        self._suggestions_shown_in_tui = 0

    def get_user_context(self) -> TUIUserContext:
        """
        Convert UserExperienceSystem profile to TUIUserContext.

        Returns:
            TUIUserContext with current user state
        """
        profile = self.ux.behavior.profile

        # Map adaptive behavior profile to TUI context
        return TUIUserContext(
            technical_proficiency=profile.technical_level,
            confidence_level=min(1.0, profile.risk_tolerance + 0.2),  # Confidence slightly above risk tolerance
            patience_level=1.0 - profile.speed_preference,  # Inverse of speed preference
            preferred_verbosity=0.7 if profile.technical_level < 0.5 else 0.3,
            learning_speed=0.5,  # Default, could be tracked
            exploration_tendency=profile.risk_tolerance,
            frustration_level=min(1.0, self.ux.errors_this_session * 0.2),  # Increases with errors
            current_mood=self._determine_mood(),
            session_count=max(1, self.ux.commands_this_session),
        )

    def _determine_mood(self) -> EmotionalState:
        """Determine current emotional state from session metrics."""
        # High error rate suggests frustration
        if self.ux.errors_this_session > 3:
            return EmotionalState.FRUSTRATED

        # Fast interaction suggests rushed
        if self.ux.behavior.profile.speed_preference > 0.8:
            return EmotionalState.RUSHED

        # Low technical level with help requests suggests learning
        if self.ux.behavior.profile.technical_level < 0.4:
            return EmotionalState.LEARNING

        # Good success rate suggests happy
        if self.ux.commands_this_session > 5 and self.ux.errors_this_session == 0:
            return EmotionalState.HAPPY

        return EmotionalState.NEUTRAL

    def get_complexity_level(self) -> UIComplexityLevel:
        """
        Get appropriate UI complexity level based on user profile.

        Returns:
            UIComplexityLevel for current user state
        """
        context = self.get_user_context()

        # Create a compatible object for the UI system
        level = self.ui_system.determine_complexity_level(context)
        self._last_complexity_level = level

        return level

    def get_ui_config(self) -> AdaptiveUIConfig:
        """
        Get full UI configuration adapted to user.

        Returns:
            AdaptiveUIConfig with all settings
        """
        context = self.get_user_context()
        return self.ui_system.adapt_ui(context)

    def get_visible_elements(self) -> list[UIElement]:
        """
        Get UI elements appropriate for current complexity level.

        Returns:
            List of visible UIElement objects
        """
        level = self.get_complexity_level()
        return self.ui_system.get_visible_elements(NIXOS_UI_ELEMENTS, level)

    def format_response(self, response: str, response_type: str = "info") -> str:
        """
        Format a response using both personality and complexity settings.

        Args:
            response: The base response text
            response_type: Type of response (success, error, info, etc.)

        Returns:
            Formatted response string
        """
        # Apply personality formatting
        styled = self.ux.format_response(response, response_type)

        # Apply complexity-based simplification
        level = self._last_complexity_level
        styled = self.ui_system.format_for_complexity(styled, level)

        return styled

    def get_tui_suggestions(self, max_suggestions: int = 2) -> list[dict[str, Any]]:
        """
        Get proactive suggestions formatted for TUI display.

        Args:
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries with display info
        """
        insights = self.ux.get_proactive_suggestions()

        tui_suggestions = []
        for insight in insights[:max_suggestions]:
            tui_suggestions.append({
                "message": insight.message,
                "category": insight.category,
                "action": insight.action_suggestion,
                "icon": self._get_category_icon(insight.category),
                "priority": insight.confidence,
            })

        self._suggestions_shown_in_tui += len(tui_suggestions)
        return tui_suggestions

    def _get_category_icon(self, category: str) -> str:
        """Get icon for suggestion category."""
        icons = {
            "learning": "📚",
            "optimization": "⚡",
            "help": "🆘",
            "maintenance": "🔧",
            "info": "ℹ️",
            "warning": "⚠️",
        }
        return icons.get(category, "💡")

    def record_tui_interaction(
        self,
        command: str,
        execution_time: float,
        success: bool,
        context: Optional[dict] = None
    ) -> None:
        """
        Record a TUI interaction for learning.

        Args:
            command: The command or action taken
            execution_time: Time taken in seconds
            success: Whether it succeeded
            context: Optional additional context
        """
        # Add TUI-specific context
        full_context = context or {}
        full_context["interface"] = "tui"
        full_context["complexity_level"] = self._last_complexity_level.value

        self.ux.record_command(command, execution_time, success, full_context)

    def get_personality_style(self) -> str:
        """Get current personality style name."""
        return self.ux.personality.get_current_style().value

    def set_personality_style(self, style: str) -> str:
        """
        Set personality style and return confirmation.

        Args:
            style: Personality style name

        Returns:
            Confirmation message in new style
        """
        return self.ux.set_mode(style)

    def get_welcome_message(self) -> str:
        """Get a personalized welcome message for TUI."""
        greeting = self.ux.get_greeting()

        # Enhance based on complexity
        level = self.get_complexity_level()

        if level == UIComplexityLevel.MINIMAL:
            return f"{greeting}\n\nType what you need. I'll help."
        elif level == UIComplexityLevel.SIMPLE:
            return f"{greeting}\n\nJust describe what you want to do!"
        elif level == UIComplexityLevel.EXPERT:
            return f"{greeting}\n\nReady for your commands."
        else:
            return f"{greeting}\n\nAsk me anything about NixOS!"

    def get_status_summary(self) -> dict[str, Any]:
        """
        Get a summary of current UX/UI state for TUI status display.

        Returns:
            Dictionary with status information
        """
        profile = self.ux.behavior.profile

        return {
            "personality": self.get_personality_style(),
            "complexity": self._last_complexity_level.value,
            "technical_level": f"{profile.technical_level:.0%}",
            "session_commands": self.ux.commands_this_session,
            "session_errors": self.ux.errors_this_session,
            "adaptation_status": self.ux.behavior.get_status(),
            "mood": self._determine_mood().value if hasattr(self._determine_mood(), 'value') else str(self._determine_mood()),
        }

    def should_show_confirmation(self, command: str) -> bool:
        """
        Determine if a command should require confirmation.

        Args:
            command: The command about to be executed

        Returns:
            True if confirmation should be shown
        """
        # Get config-based decision
        config = self.get_ui_config()

        # Dangerous commands always need confirmation in simpler modes
        dangerous_keywords = ["delete", "remove", "clean", "garbage", "switch", "rebuild"]
        is_dangerous = any(kw in command.lower() for kw in dangerous_keywords)

        if is_dangerous:
            return config.confirm_dangerous

        # Check behavioral system's recommendation
        return self.ux.should_request_confirmation(command)

    def should_show_preview(self, command: str) -> bool:
        """
        Determine if a command preview should be shown.

        Args:
            command: The command about to be executed

        Returns:
            True if preview should be shown
        """
        return self.ux.should_show_preview(command)


# Singleton instance for easy access
_ux_tui_bridge: Optional[UXTUIBridge] = None


def get_ux_tui_bridge() -> UXTUIBridge:
    """Get or create the global UX-TUI bridge instance."""
    global _ux_tui_bridge
    if _ux_tui_bridge is None:
        _ux_tui_bridge = UXTUIBridge()
    return _ux_tui_bridge


# Convenience functions for TUI integration
def get_adaptive_config() -> AdaptiveUIConfig:
    """Get current adaptive UI config."""
    return get_ux_tui_bridge().get_ui_config()


def get_complexity_level() -> UIComplexityLevel:
    """Get current complexity level."""
    return get_ux_tui_bridge().get_complexity_level()


def format_for_user(text: str, response_type: str = "info") -> str:
    """Format text according to user's personality and complexity."""
    return get_ux_tui_bridge().format_response(text, response_type)


def record_interaction(command: str, time: float, success: bool) -> None:
    """Record an interaction for adaptive learning."""
    get_ux_tui_bridge().record_tui_interaction(command, time, success)
