"""
🌟 Unified User Experience System

Combines adaptive behavior learning, personality formatting, and proactive assistance
to create a delightful, personalized experience for every user.

Path 2 (Delight Users) + Path 3 (System Intelligence)
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any

from .adaptive_behavior import (
    AdaptiveBehaviorSystem,
    AdaptiveProfile,
    ObservationType,
)
from .personality_system import (
    PersonalityManager,
    PersonalityStyle,
    get_personality_manager,
)

logger = logging.getLogger(__name__)


@dataclass
class ProactiveInsight:
    """A proactive suggestion or insight for the user"""
    message: str
    confidence: float  # 0.0 to 1.0
    category: str  # maintenance, optimization, learning, warning
    action_suggestion: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class UserExperienceSystem:
    """
    Unified system for adaptive, personalized user experience.

    Combines:
    - AdaptiveBehaviorSystem: Learns from user behavior
    - PersonalityManager: Formats responses in user's preferred style
    - ProactiveAssistant: Anticipates needs and offers helpful suggestions

    Philosophy:
    - The interface should feel like a helpful companion, not a tool
    - Learn continuously, but never feel invasive
    - Proactive help should be gentle, not nagging
    - Every user is unique - adapt to them specifically
    """

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or "default"

        # Core systems
        self.behavior = AdaptiveBehaviorSystem(user_id=self.user_id)
        self.personality = PersonalityManager()

        # Session tracking
        self.session_start = datetime.now()
        self.commands_this_session = 0
        self.errors_this_session = 0

        # Proactive assistance state
        self.last_proactive_suggestion = None
        self.suggestions_shown = 0
        self.proactive_cooldown = timedelta(minutes=5)  # Don't spam suggestions

        # Load user preferences
        self._load_preferences()

    def _load_preferences(self):
        """Load saved user preferences"""
        prefs_path = Path.home() / ".luminous-nix" / "user_prefs.json"
        if prefs_path.exists():
            try:
                with open(prefs_path) as f:
                    prefs = json.load(f)
                    if "personality_style" in prefs:
                        self.personality.set_style(prefs["personality_style"])
                    if "proactive_enabled" in prefs:
                        self.proactive_enabled = prefs["proactive_enabled"]
            except Exception as e:
                logger.debug(f"Could not load preferences: {e}")

    def _save_preferences(self):
        """Save user preferences"""
        prefs_path = Path.home() / ".luminous-nix" / "user_prefs.json"
        prefs_path.parent.mkdir(parents=True, exist_ok=True)

        prefs = {
            "personality_style": self.personality.get_current_style().value,
            "proactive_enabled": getattr(self, 'proactive_enabled', True),
            "last_updated": datetime.now().isoformat(),
        }

        with open(prefs_path, "w") as f:
            json.dump(prefs, f, indent=2)

    # ==========================================================================
    # Path 2: Delight Users - Personalized Responses
    # ==========================================================================

    def format_response(
        self,
        response: str,
        response_type: str = "success",
        context: Optional[dict] = None
    ) -> str:
        """
        Format a response according to user's preferred personality style.

        Args:
            response: The base response content
            response_type: Type (success, error, confirmation, etc.)
            context: Additional context for formatting

        Returns:
            Personalized response string
        """
        # Get explanation level from adaptive behavior
        explanation_level = self.behavior.get_explanation_level()

        # Simplify technical terms for non-technical users
        if explanation_level == "simple":
            response = self._simplify_response(response)

        # Let personality manager add flavor
        styled_response = self.personality.adapt_response(response, response_type)

        return styled_response

    def _simplify_response(self, response: str) -> str:
        """Simplify technical jargon for non-technical users"""
        replacements = {
            "nixpkgs#": "package ",
            "flake": "configuration",
            "derivation": "package",
            "attribute": "option",
            "nix-env": "package manager",
            "nixos-rebuild": "system update",
            "configuration.nix": "settings file",
            "hash": "identifier",
            "closure": "dependencies",
        }

        for technical, simple in replacements.items():
            response = response.replace(technical, simple)

        return response

    def get_greeting(self) -> str:
        """Get a personalized greeting based on time and user history"""
        hour = datetime.now().hour

        # Time-aware base greeting
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        # Personalize based on history
        if self.commands_this_session == 0:
            # First interaction this session
            if self.behavior.profile.technical_level > 0.7:
                return f"{time_greeting}. Ready when you are."
            else:
                return self.personality.get_response("greeting")

        # Returning during session
        return "Welcome back! How can I help?"

    def get_farewell(self) -> str:
        """Get a personalized farewell"""
        session_duration = datetime.now() - self.session_start

        if self.errors_this_session > 3:
            return self.personality.get_response("error", {"error": "rough session"}).replace(
                "rough session", "that was a challenging session. Don't worry, we'll do better next time!"
            )

        if self.commands_this_session > 10:
            return "Great productive session! See you next time."

        return self.personality.get_response("completion")

    # ==========================================================================
    # Behavior Tracking
    # ==========================================================================

    def record_command(
        self,
        command: str,
        execution_time: float,
        success: bool,
        context: Optional[dict] = None
    ):
        """Record a command execution for learning"""
        self.commands_this_session += 1

        if success:
            self.behavior.observe(
                ObservationType.COMMAND_EXECUTED,
                details={
                    "time_to_execute": execution_time,
                    "command": command,
                },
                context=context
            )
        else:
            self.errors_this_session += 1
            self.behavior.observe(
                ObservationType.ERROR_ENCOUNTERED,
                details={"command": command},
                context=context
            )

        # Update personality based on interaction speed
        if execution_time < 3:
            self.personality.learn_from_interaction(
                command, success, interaction_speed="fast"
            )
        elif execution_time > 10:
            self.personality.learn_from_interaction(
                command, success, interaction_speed="slow"
            )

    def record_preview_read(self, read_time: float):
        """Record that user read a preview"""
        self.behavior.observe(
            ObservationType.PREVIEW_READ,
            details={"read_time": read_time}
        )

    def record_help_request(self, topic: Optional[str] = None):
        """Record a help request"""
        self.behavior.observe(
            ObservationType.HELP_REQUESTED,
            details={"topic": topic} if topic else {}
        )

    def record_error_recovery(self, error: str, recovery_action: str):
        """Record successful error recovery"""
        self.behavior.observe(
            ObservationType.ERROR_RECOVERED,
            details={
                "error": error,
                "recovery": recovery_action,
            }
        )

    # ==========================================================================
    # Path 3: Proactive Assistance
    # ==========================================================================

    def get_proactive_suggestions(self) -> list[ProactiveInsight]:
        """
        Generate proactive suggestions based on user behavior and system state.

        Returns helpful suggestions without being annoying.
        """
        suggestions = []

        # Check if we should even offer suggestions
        if not self._should_offer_suggestion():
            return suggestions

        # 1. Learning suggestions for newer users
        if self.behavior.profile.technical_level < 0.4:
            if self.commands_this_session > 5:
                suggestions.append(ProactiveInsight(
                    message="You're getting the hang of this! Want to learn about more advanced features?",
                    confidence=0.7,
                    category="learning",
                    action_suggestion="ask-nix help advanced"
                ))

        # 2. Efficiency suggestions for experienced users
        if self.behavior.profile.technical_level > 0.6:
            if self.behavior.profile.speed_preference < 0.5:
                suggestions.append(ProactiveInsight(
                    message="Pro tip: You can use aliases for common commands. Try 'ask-nix config aliases'",
                    confidence=0.6,
                    category="optimization",
                ))

        # 3. Error recovery suggestions
        if self.errors_this_session > 2:
            suggestions.append(ProactiveInsight(
                message="Having trouble? I can help troubleshoot common issues.",
                confidence=0.8,
                category="help",
                action_suggestion="ask-nix troubleshoot"
            ))

        # 4. System maintenance reminders (gentle)
        if self.commands_this_session > 20 and self.suggestions_shown < 2:
            suggestions.append(ProactiveInsight(
                message="Great session! Remember, you can run 'nix-collect-garbage' periodically to free up space.",
                confidence=0.5,
                category="maintenance",
            ))

        # 5. Adaptive behavior status
        behavior_status = self.behavior.get_status()
        if "Learning your preferences" in behavior_status:
            suggestions.append(ProactiveInsight(
                message="I'm learning how you work to personalize your experience. The more you use me, the better I'll get!",
                confidence=0.9,
                category="info",
            ))

        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        return suggestions[:2]  # Max 2 suggestions at a time

    def _should_offer_suggestion(self) -> bool:
        """Check if it's appropriate to offer a proactive suggestion"""
        # Respect cooldown
        if self.last_proactive_suggestion:
            time_since_last = datetime.now() - self.last_proactive_suggestion
            if time_since_last < self.proactive_cooldown:
                return False

        # Don't interrupt fast workers
        if self.behavior.profile.speed_preference > 0.8:
            return False

        # Be more proactive with beginners
        if self.behavior.profile.technical_level < 0.3:
            return True

        # Offer suggestions periodically
        return self.suggestions_shown < 3  # Max 3 per session

    def acknowledge_suggestion(self, accepted: bool):
        """Record whether user accepted a proactive suggestion"""
        self.last_proactive_suggestion = datetime.now()
        self.suggestions_shown += 1

        if not accepted:
            # User dismissed - increase cooldown
            self.proactive_cooldown = timedelta(minutes=10)

    # ==========================================================================
    # Interface Adaptation
    # ==========================================================================

    def get_interface_settings(self) -> dict[str, Any]:
        """
        Get current interface settings based on adaptive profile.

        Returns dict for UI components to use.
        """
        base_settings = self.behavior.get_interface_mode()

        # Enhance with personality
        base_settings["personality_style"] = self.personality.get_current_style().value
        base_settings["session_commands"] = self.commands_this_session
        base_settings["session_errors"] = self.errors_this_session

        return base_settings

    def should_show_preview(self, command: str) -> bool:
        """Determine if preview should be shown for a command"""
        return self.behavior.should_show_preview(command)

    def should_request_confirmation(self, command: str) -> bool:
        """Determine if confirmation is needed"""
        return self.behavior.should_request_confirmation(command)

    # ==========================================================================
    # Personality Modes (Quick Switch)
    # ==========================================================================

    def set_mode(self, mode: str) -> str:
        """
        Quick mode switch for users who want a specific experience.

        Args:
            mode: One of: minimal, friendly, encouraging, playful, sacred,
                  professional, teacher, companion, hacker, zen

        Returns:
            Confirmation message in the new style
        """
        valid_modes = [s.value for s in PersonalityStyle]

        if mode not in valid_modes:
            return f"Unknown mode '{mode}'. Available: {', '.join(valid_modes)}"

        self.personality.set_style(mode)
        self._save_preferences()

        return self.personality.get_response("greeting")

    def get_available_modes(self) -> list[dict[str, str]]:
        """Get list of available personality modes"""
        return [
            {"name": "minimal", "description": "Just the facts, technical precision"},
            {"name": "friendly", "description": "Warm and helpful, balanced approach"},
            {"name": "encouraging", "description": "Supportive growth, educational focus"},
            {"name": "playful", "description": "Light humor, engaging interaction"},
            {"name": "sacred", "description": "Mindful computing, consciousness-first"},
            {"name": "professional", "description": "Business-like, formal efficiency"},
            {"name": "teacher", "description": "Educational, patient explanations"},
            {"name": "companion", "description": "Empathetic, emotional support"},
            {"name": "hacker", "description": "Technical slang, power user focused"},
            {"name": "zen", "description": "Calm, meditative, minimalist wisdom"},
        ]

    # ==========================================================================
    # Status & Diagnostics
    # ==========================================================================

    def get_status(self) -> dict[str, Any]:
        """Get complete user experience status"""
        return {
            "user_id": self.user_id,
            "session_duration": str(datetime.now() - self.session_start),
            "commands_this_session": self.commands_this_session,
            "errors_this_session": self.errors_this_session,
            "adaptation_status": self.behavior.get_status(),
            "personality_style": self.personality.get_style_description(),
            "interface_mode": self.get_interface_settings(),
            "profile": {
                "technical_level": f"{self.behavior.profile.technical_level:.0%}",
                "risk_tolerance": f"{self.behavior.profile.risk_tolerance:.0%}",
                "speed_preference": f"{self.behavior.profile.speed_preference:.0%}",
            },
        }


# Singleton instance
_ux_system: Optional[UserExperienceSystem] = None


def get_user_experience() -> UserExperienceSystem:
    """Get or create the global user experience system"""
    global _ux_system
    if _ux_system is None:
        _ux_system = UserExperienceSystem()
    return _ux_system


# Example usage
if __name__ == "__main__":
    ux = UserExperienceSystem(user_id="demo")

    print("🌟 Luminous Nix User Experience System")
    print("=" * 50)

    print(f"\nGreeting: {ux.get_greeting()}")

    # Simulate some interactions
    ux.record_command("search firefox", 1.5, True)
    ux.record_command("install vim", 2.0, True)
    ux.record_help_request("how to update")
    ux.record_command("update system", 15.0, True)

    print(f"\nStatus: {ux.get_status()}")

    # Test mode switching
    print("\n--- Testing Modes ---")
    for mode in ["hacker", "zen", "playful", "minimal"]:
        response = ux.set_mode(mode)
        print(f"{mode}: {response}")

    # Test proactive suggestions
    print("\n--- Proactive Suggestions ---")
    suggestions = ux.get_proactive_suggestions()
    for s in suggestions:
        print(f"[{s.category}] {s.message}")

    print(f"\nFarewell: {ux.get_farewell()}")
