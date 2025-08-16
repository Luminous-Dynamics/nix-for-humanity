"""Adaptive behavior based on usage."""

# === Merged from migration ===

"""
from typing import Dict, List, Optional
Adaptive UI Complexity System - Three-Stage Evolution

Implements the consciousness-first UI pattern where interface complexity
adapts to user mastery level:
1. Sanctuary Stage - Protective, simple interface for beginners
2. Gymnasium Stage - Learning and growth interface
3. Open Sky Stage - Invisible excellence for masters
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class ComplexityStage(Enum):
    """Three stages of UI complexity evolution"""

    SANCTUARY = "sanctuary"  # Protective simplicity for new users
    GYMNASIUM = "gymnasium"  # Learning and exploration
    OPEN_SKY = "open_sky"  # Invisible excellence


@dataclass
class UserMastery:
    """Track user's mastery level and progression"""

    stage: ComplexityStage
    confidence_score: float  # 0.0 to 1.0
    successful_commands: int
    error_rate: float
    session_count: int
    last_interaction: datetime
    time_in_stage: timedelta
    stage_history: list[dict[str, Any]]


class AdaptiveComplexityManager:
    """Manage UI complexity based on user mastery"""

    def __init__(self, data_dir: Path | None = None):
        """Initialize the adaptive complexity manager"""
        if data_dir is None:
            data_dir = Path.home() / ".local" / "share" / "nix-for-humanity"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.mastery_file = self.data_dir / "user_mastery.json"

        # Stage progression thresholds
        self.SANCTUARY_TO_GYMNASIUM = {
            "min_commands": 20,
            "max_error_rate": 0.3,
            "min_sessions": 3,
            "min_confidence": 0.6,
        }

        self.GYMNASIUM_TO_OPEN_SKY = {
            "min_commands": 100,
            "max_error_rate": 0.1,
            "min_sessions": 10,
            "min_confidence": 0.85,
            "min_time_in_stage": timedelta(days=7),
        }

    def get_user_mastery(self, user_id: str) -> UserMastery:
        """Get or create user mastery data"""
        mastery_data = self._load_mastery_data()

        if user_id not in mastery_data:
            # New user starts in Sanctuary
            mastery = UserMastery(
                stage=ComplexityStage.SANCTUARY,
                confidence_score=0.0,
                successful_commands=0,
                error_rate=0.0,
                session_count=1,
                last_interaction=datetime.now(),
                time_in_stage=timedelta(0),
                stage_history=[],
            )
            mastery_data[user_id] = self._mastery_to_dict(mastery)
            self._save_mastery_data(mastery_data)
        else:
            mastery = self._dict_to_mastery(mastery_data[user_id])

        return mastery

    def update_mastery(
        self,
        user_id: str,
        command_success: bool,
        complexity_handled: str | None = None,
    ):
        """Update user mastery based on interaction"""
        mastery = self.get_user_mastery(user_id)

        # Update metrics
        if command_success:
            mastery.successful_commands += 1
            mastery.confidence_score = min(1.0, mastery.confidence_score + 0.02)
        else:
            # Errors reduce confidence more in higher stages
            confidence_penalty = (
                0.01 if mastery.stage == ComplexityStage.SANCTUARY else 0.03
            )
            mastery.confidence_score = max(
                0.0, mastery.confidence_score - confidence_penalty
            )

        # Update error rate (rolling average of last 20 commands)
        total_commands = mastery.successful_commands + 1  # Approximate
        mastery.error_rate = (
            (mastery.error_rate * (total_commands - 1)) + (0 if command_success else 1)
        ) / total_commands

        # Update time in stage
        if mastery.last_interaction:
            mastery.time_in_stage += datetime.now() - mastery.last_interaction

        mastery.last_interaction = datetime.now()

        # Check for stage progression
        new_stage = self._check_stage_progression(mastery)
        if new_stage != mastery.stage:
            self._transition_stage(mastery, new_stage)

        # Save updated mastery
        self._save_user_mastery(user_id, mastery)

    def _check_stage_progression(self, mastery: UserMastery) -> ComplexityStage:
        """Check if user should progress to next stage"""
        if mastery.stage == ComplexityStage.SANCTUARY:
            # Check progression to Gymnasium
            if (
                mastery.successful_commands
                >= self.SANCTUARY_TO_GYMNASIUM["min_commands"]
                and mastery.error_rate <= self.SANCTUARY_TO_GYMNASIUM["max_error_rate"]
                and mastery.session_count >= self.SANCTUARY_TO_GYMNASIUM["min_sessions"]
                and mastery.confidence_score
                >= self.SANCTUARY_TO_GYMNASIUM["min_confidence"]
            ):
                return ComplexityStage.GYMNASIUM

        elif mastery.stage == ComplexityStage.GYMNASIUM:
            # Check progression to Open Sky
            if (
                mastery.successful_commands
                >= self.GYMNASIUM_TO_OPEN_SKY["min_commands"]
                and mastery.error_rate <= self.GYMNASIUM_TO_OPEN_SKY["max_error_rate"]
                and mastery.session_count >= self.GYMNASIUM_TO_OPEN_SKY["min_sessions"]
                and mastery.confidence_score
                >= self.GYMNASIUM_TO_OPEN_SKY["min_confidence"]
                and mastery.time_in_stage
                >= self.GYMNASIUM_TO_OPEN_SKY["min_time_in_stage"]
            ):
                return ComplexityStage.OPEN_SKY

            # Check regression to Sanctuary (high error rate)
            if mastery.error_rate > 0.5 and mastery.confidence_score < 0.3:
                return ComplexityStage.SANCTUARY

        elif mastery.stage == ComplexityStage.OPEN_SKY:
            # Check regression to Gymnasium (struggling)
            if mastery.error_rate > 0.3 and mastery.confidence_score < 0.5:
                return ComplexityStage.GYMNASIUM

        return mastery.stage

    def _transition_stage(self, mastery: UserMastery, new_stage: ComplexityStage):
        """Handle stage transition"""
        # Record transition
        mastery.stage_history.append(
            {
                "from": mastery.stage.value,
                "to": new_stage.value,
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "confidence": mastery.confidence_score,
                    "commands": mastery.successful_commands,
                    "error_rate": mastery.error_rate,
                },
            }
        )

        # Reset stage timer
        mastery.time_in_stage = timedelta(0)
        mastery.stage = new_stage

    def get_ui_config(self, stage: ComplexityStage) -> dict[str, Any]:
        """Get UI configuration for complexity stage"""
        configs = {
            ComplexityStage.SANCTUARY: {
                "show_advanced_options": False,
                "max_menu_items": 5,
                "confirmation_required": True,
                "verbose_help": True,
                "show_keyboard_shortcuts": False,
                "animation_speed": "slow",
                "color_scheme": "high_contrast",
                "font_size": "large",
                "show_progress_indicators": True,
                "auto_complete": False,
                "command_suggestions": True,
                "error_recovery_hints": True,
                "show_learning_tips": True,
            },
            ComplexityStage.GYMNASIUM: {
                "show_advanced_options": True,
                "max_menu_items": 10,
                "confirmation_required": False,
                "verbose_help": False,
                "show_keyboard_shortcuts": True,
                "animation_speed": "normal",
                "color_scheme": "balanced",
                "font_size": "medium",
                "show_progress_indicators": True,
                "auto_complete": True,
                "command_suggestions": True,
                "error_recovery_hints": False,
                "show_learning_tips": False,
                "show_power_features": True,
            },
            ComplexityStage.OPEN_SKY: {
                "show_advanced_options": "on_request",
                "max_menu_items": -1,  # Unlimited
                "confirmation_required": False,
                "verbose_help": False,
                "show_keyboard_shortcuts": "minimal",
                "animation_speed": "instant",
                "color_scheme": "minimal",
                "font_size": "small",
                "show_progress_indicators": False,
                "auto_complete": True,
                "command_suggestions": False,
                "error_recovery_hints": False,
                "show_learning_tips": False,
                "show_power_features": True,
                "invisible_excellence": True,
                "predictive_commands": True,
            },
        }

        return configs.get(stage, configs[ComplexityStage.SANCTUARY])

    def get_stage_description(self, stage: ComplexityStage) -> str:
        """Get human-readable description of stage"""
        descriptions = {
            ComplexityStage.SANCTUARY: "🛡️ Sanctuary Mode - Protected and guided experience for comfortable learning",
            ComplexityStage.GYMNASIUM: "🎯 Gymnasium Mode - Exploring features and building mastery",
            ComplexityStage.OPEN_SKY: "☁️ Open Sky Mode - Invisible excellence, the interface disappears",
        }
        return descriptions.get(stage, "Unknown stage")

    def get_progression_feedback(self, user_id: str) -> dict[str, Any]:
        """Get feedback on user's progression toward next stage"""
        mastery = self.get_user_mastery(user_id)

        if mastery.stage == ComplexityStage.SANCTUARY:
            thresholds = self.SANCTUARY_TO_GYMNASIUM
            next_stage = "Gymnasium"
        elif mastery.stage == ComplexityStage.GYMNASIUM:
            thresholds = self.GYMNASIUM_TO_OPEN_SKY
            next_stage = "Open Sky"
        else:
            return {
                "current_stage": mastery.stage.value,
                "message": "You've reached mastery! The interface adapts to your flow.",
                "can_regress": True,
            }

        progress = {
            "current_stage": mastery.stage.value,
            "next_stage": next_stage,
            "progress_metrics": {
                "commands": {
                    "current": mastery.successful_commands,
                    "required": thresholds["min_commands"],
                    "percentage": min(
                        100,
                        (mastery.successful_commands / thresholds["min_commands"])
                        * 100,
                    ),
                },
                "accuracy": {
                    "current": 1 - mastery.error_rate,
                    "required": 1 - thresholds["max_error_rate"],
                    "percentage": min(
                        100,
                        ((1 - mastery.error_rate) / (1 - thresholds["max_error_rate"]))
                        * 100,
                    ),
                },
                "confidence": {
                    "current": mastery.confidence_score,
                    "required": thresholds["min_confidence"],
                    "percentage": min(
                        100,
                        (mastery.confidence_score / thresholds["min_confidence"]) * 100,
                    ),
                },
            },
            "ready_to_advance": self._check_stage_progression(mastery) != mastery.stage,
        }

        return progress

    def manually_set_stage(self, user_id: str, stage: ComplexityStage):
        """Allow manual override of complexity stage"""
        mastery = self.get_user_mastery(user_id)
        if mastery.stage != stage:
            self._transition_stage(mastery, stage)
            self._save_user_mastery(user_id, mastery)

    # Persistence helpers

    def _load_mastery_data(self) -> dict[str, Any]:
        """Load mastery data from disk"""
        if self.mastery_file.exists():
            with open(self.mastery_file) as f:
                return json.load(f)
        return {}

    def _save_mastery_data(self, data: dict[str, Any]):
        """Save mastery data to disk"""
        with open(self.mastery_file, "w") as f:
            json.dump(data, f, indent=2)

    def _save_user_mastery(self, user_id: str, mastery: UserMastery):
        """Save specific user's mastery"""
        data = self._load_mastery_data()
        data[user_id] = self._mastery_to_dict(mastery)
        self._save_mastery_data(data)

    def _mastery_to_dict(self, mastery: UserMastery) -> dict[str, Any]:
        """Convert UserMastery to dictionary for persistence"""
        return {
            "stage": mastery.stage.value,
            "confidence_score": mastery.confidence_score,
            "successful_commands": mastery.successful_commands,
            "error_rate": mastery.error_rate,
            "session_count": mastery.session_count,
            "last_interaction": mastery.last_interaction.isoformat(),
            "time_in_stage": mastery.time_in_stage.total_seconds(),
            "stage_history": mastery.stage_history,
        }

    def _dict_to_mastery(self, data: dict[str, Any]) -> UserMastery:
        """Convert dictionary to UserMastery"""
        return UserMastery(
            stage=ComplexityStage(data["stage"]),
            confidence_score=data["confidence_score"],
            successful_commands=data["successful_commands"],
            error_rate=data["error_rate"],
            session_count=data["session_count"],
            last_interaction=datetime.fromisoformat(data["last_interaction"]),
            time_in_stage=timedelta(seconds=data["time_in_stage"]),
            stage_history=data.get("stage_history", []),
        )


# Convenience function
_complexity_manager = None


def get_complexity_manager() -> AdaptiveComplexityManager:
    """Get or create the global complexity manager"""
    global _complexity_manager
    if _complexity_manager is None:
        _complexity_manager = AdaptiveComplexityManager()
    return _complexity_manager
