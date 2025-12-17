"""
User Context Manager - Tracks user skill level, preferences, and history
Enables adaptive AI responses that match user expertise
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class SkillLevel(Enum):
    """User skill levels for adaptive responses"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class UserContext:
    """User profile and preferences"""
    skill_level: SkillLevel
    prefers_flakes: bool
    command_history: List[str]
    successful_actions: int
    failed_actions: int
    preferences: Dict[str, Any]

    def to_context_string(self) -> str:
        """Convert to natural language for AI"""
        success_rate = self._calculate_success_rate()
        context = f"""
User Profile:
- Skill Level: {self.skill_level.value}
- Prefers: {'Flakes' if self.prefers_flakes else 'Traditional Nix'}
- Success Rate: {success_rate:.1%}
- Commands Used: {len(self.command_history)}
"""
        return context

    def _calculate_success_rate(self) -> float:
        total = self.successful_actions + self.failed_actions
        if total == 0:
            return 0.0
        return self.successful_actions / total


class UserContextManager:
    """Manages user profile and context with automatic skill detection"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "luminous-nix"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profile_path = self.config_dir / "user_profile.json"
        self.context = self._load_or_create_profile()

    def _load_or_create_profile(self) -> UserContext:
        """Load existing profile or create new one"""
        if self.profile_path.exists():
            try:
                with open(self.profile_path) as f:
                    data = json.load(f)

                    # Smart defaults for preferences if not set
                    preferences = data.get('preferences', {})
                    skill_level = SkillLevel(data.get('skill_level', 'beginner'))

                    # Set dual_answer_mode based on skill level if not explicitly set
                    if 'dual_answer_mode' not in preferences:
                        # Beginners: OFF (just show NixOS way, less confusing)
                        # Advanced: ON (show comparison, educational)
                        preferences['dual_answer_mode'] = skill_level in [
                            SkillLevel.INTERMEDIATE,
                            SkillLevel.ADVANCED,
                            SkillLevel.EXPERT
                        ]

                    return UserContext(
                        skill_level=skill_level,
                        prefers_flakes=data.get('prefers_flakes', True),
                        command_history=data.get('command_history', []),
                        successful_actions=data.get('successful_actions', 0),
                        failed_actions=data.get('failed_actions', 0),
                        preferences=preferences
                    )
            except Exception as e:
                print(f"Warning: Could not load profile: {e}")

        # Create new profile with smart defaults
        return UserContext(
            skill_level=SkillLevel.BEGINNER,
            prefers_flakes=True,  # Recommend flakes by default!
            command_history=[],
            successful_actions=0,
            failed_actions=0,
            preferences={
                'dual_answer_mode': False  # OFF for beginners by default
            }
        )

    def save(self):
        """Persist profile to disk"""
        data = {
            'skill_level': self.context.skill_level.value,
            'prefers_flakes': self.context.prefers_flakes,
            'command_history': self.context.command_history[-100:],  # Keep last 100
            'successful_actions': self.context.successful_actions,
            'failed_actions': self.context.failed_actions,
            'preferences': self.context.preferences
        }
        with open(self.profile_path, 'w') as f:
            json.dump(data, f, indent=2)

    def record_command(self, command: str):
        """Record a command in history"""
        self.context.command_history.append(command)
        self.save()

    def record_success(self):
        """Record a successful action"""
        self.context.successful_actions += 1
        self._update_skill_level()
        self.save()

    def record_failure(self):
        """Record a failed action"""
        self.context.failed_actions += 1
        self.save()

    def _update_skill_level(self):
        """Automatically detect skill level based on usage patterns"""
        total = self.context.successful_actions + self.context.failed_actions

        if total < 10:
            # Still learning the basics
            self.context.skill_level = SkillLevel.BEGINNER
        elif total < 50:
            success_rate = self.context.successful_actions / total
            if success_rate > 0.8:
                self.context.skill_level = SkillLevel.INTERMEDIATE
            else:
                self.context.skill_level = SkillLevel.BEGINNER
        elif total < 200:
            success_rate = self.context.successful_actions / total
            if success_rate > 0.85:
                self.context.skill_level = SkillLevel.ADVANCED
            elif success_rate > 0.75:
                self.context.skill_level = SkillLevel.INTERMEDIATE
            else:
                self.context.skill_level = SkillLevel.BEGINNER
        else:
            success_rate = self.context.successful_actions / total
            if success_rate > 0.9:
                self.context.skill_level = SkillLevel.EXPERT
            elif success_rate > 0.85:
                self.context.skill_level = SkillLevel.ADVANCED
            elif success_rate > 0.75:
                self.context.skill_level = SkillLevel.INTERMEDIATE
            else:
                self.context.skill_level = SkillLevel.BEGINNER

    def get_context(self) -> UserContext:
        """Get current user context"""
        return self.context

    def set_skill_level(self, level: SkillLevel):
        """Manually set skill level"""
        self.context.skill_level = level
        self.save()

    def set_flake_preference(self, prefers: bool):
        """Set flake preference"""
        self.context.prefers_flakes = prefers
        self.save()
