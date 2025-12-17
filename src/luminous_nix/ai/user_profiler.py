"""
User Profiling System - Layer 5: User Experience Intelligence

Revolutionary capability: Understand WHO each user is, what they want,
and adapt the entire experience to their archetype and goals.

This system enables the AI to:
- Detect user archetypes (Learner, Pragmatist, Explorer, Creator)
- Assess technical level and goals
- Choose appropriate engagement modes
- Personalize every interaction

This is the foundation for making AI that serves EACH user uniquely.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class UserArchetype(Enum):
    """Four fundamental user types with different needs"""
    LEARNER = "learner"           # Wants deep understanding
    PRAGMATIST = "pragmatist"     # Wants working system, minimal fuss
    EXPLORER = "explorer"         # Wants to discover possibilities
    CREATOR = "creator"           # Wants to build custom solutions
    UNKNOWN = "unknown"           # Not yet determined


class TechnicalLevel(Enum):
    """User's technical proficiency"""
    BEGINNER = "beginner"         # New to NixOS/Linux
    INTERMEDIATE = "intermediate" # Familiar with Linux, learning Nix
    ADVANCED = "advanced"         # Experienced with Nix
    EXPERT = "expert"             # Deep Nix knowledge


class EngagementMode(Enum):
    """How the AI should interact with this user"""
    FULL_TEACHING = "full_teaching"           # Learner: Explain deeply
    JUST_DO_IT = "just_do_it"                 # Pragmatist: Execute, minimal talk
    SHOWCASE_POSSIBILITIES = "showcase"        # Explorer: Show options
    COLLABORATIVE_DEV = "collaborative"        # Creator: Co-create together
    ADAPTIVE = "adaptive"                      # Switch based on context


@dataclass
class UserGoal:
    """A goal the user wants to achieve"""
    description: str
    category: str  # "learning", "system_setup", "exploration", "development"
    priority: int  # 1-5, 5 is highest
    completed: bool = False


@dataclass
class UserProfile:
    """Complete profile of a user's characteristics and preferences"""
    user_id: str

    # Core characteristics
    archetype: UserArchetype
    technical_level: TechnicalLevel
    primary_goals: List[UserGoal] = field(default_factory=list)

    # Engagement preferences
    engagement_mode: EngagementMode = EngagementMode.ADAPTIVE
    wants_learning: bool = True  # Does user want educational content?
    prefers_automation: bool = False  # Automate without asking?

    # Learning preferences (from Layer 4 - Meta-Learning)
    learning_style: Optional[str] = None  # "visual", "kinesthetic", etc.

    # Discovery preferences
    interested_in_alternatives: bool = True  # Show FOSS alternatives?
    interested_in_customization: bool = False  # Want to build custom tools?

    # Session context
    onboarding_complete: bool = False
    sessions_count: int = 0
    last_updated: float = 0.0

    # Confidence in detection (0.0-1.0)
    archetype_confidence: float = 0.0
    technical_level_confidence: float = 0.0


@dataclass
class OnboardingQuestion:
    """A question to ask during onboarding"""
    id: str
    question: str
    options: List[str]
    detect_archetype: Optional[UserArchetype] = None
    detect_technical_level: Optional[TechnicalLevel] = None
    detect_goal_category: Optional[str] = None


class UserProfiler:
    """
    Understands users through questions and interactions.

    Philosophy: Don't assume - ask and observe. Every user is unique.
    """

    def __init__(self, storage_dir: str = "~/.luminous-nix"):
        """Initialize profiler with storage location"""
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_file = self.storage_dir / "user_profiles.json"

    def get_onboarding_questions(self) -> List[OnboardingQuestion]:
        """
        Generate onboarding questionnaire.

        These questions help us understand:
        - What does the user want to accomplish?
        - How technical are they?
        - What's their learning style?
        - Do they want automation or control?
        """
        return [
            OnboardingQuestion(
                id="goal",
                question="What brings you to NixOS? (Select your primary goal)",
                options=[
                    "I want to learn how NixOS works deeply",
                    "I just want a working system quickly",
                    "I want to explore what's possible with NixOS",
                    "I want to build custom tools and solutions"
                ],
                detect_archetype=None  # Will determine from choice
            ),
            OnboardingQuestion(
                id="experience",
                question="How would you describe your experience with Linux/NixOS?",
                options=[
                    "I'm new to Linux and NixOS",
                    "I know Linux but I'm new to NixOS",
                    "I've used NixOS and understand the basics",
                    "I'm very experienced with Nix"
                ],
                detect_technical_level=None  # Will determine from choice
            ),
            OnboardingQuestion(
                id="learning_preference",
                question="When learning something new, do you prefer to:",
                options=[
                    "Understand deeply before doing anything",
                    "Get something working first, understand later",
                    "See examples and experiment",
                    "Build it myself with guidance"
                ],
                detect_archetype=None
            ),
            OnboardingQuestion(
                id="automation_preference",
                question="How much do you want the AI to do automatically?",
                options=[
                    "Show me everything and let me decide",
                    "Handle routine tasks automatically",
                    "Ask before doing anything significant",
                    "I want full control over every step"
                ],
                detect_archetype=None
            ),
            OnboardingQuestion(
                id="discovery",
                question="Are you interested in discovering new tools you didn't know about?",
                options=[
                    "Yes! Show me alternatives and possibilities",
                    "Sometimes, if it's clearly better",
                    "No, I know what I want",
                    "Only if I ask"
                ],
                detect_archetype=None
            )
        ]

    def generate_initial_profile(self, responses: Dict[str, int]) -> UserProfile:
        """
        Generate initial user profile from onboarding responses.

        Args:
            responses: Dict mapping question_id to option index (0-3)

        Returns:
            UserProfile with detected characteristics
        """
        # Detect archetype from goal and learning preference
        archetype = self._determine_archetype(responses)

        # Assess technical level from experience question
        technical_level = self._assess_technical_level(responses)

        # Extract goals
        primary_goals = self._extract_goals(responses)

        # Determine engagement mode
        engagement_mode = self._choose_engagement_mode(archetype)

        # Determine preferences
        wants_learning = self._wants_learning(responses)
        prefers_automation = self._prefers_automation(responses)
        interested_in_alternatives = self._interested_in_discovery(responses)
        interested_in_customization = archetype == UserArchetype.CREATOR

        profile = UserProfile(
            user_id="default_user",  # Will support multi-user later
            archetype=archetype,
            technical_level=technical_level,
            primary_goals=primary_goals,
            engagement_mode=engagement_mode,
            wants_learning=wants_learning,
            prefers_automation=prefers_automation,
            interested_in_alternatives=interested_in_alternatives,
            interested_in_customization=interested_in_customization,
            onboarding_complete=True,
            sessions_count=1,
            archetype_confidence=0.7,  # Initial confidence from survey
            technical_level_confidence=0.8
        )

        # Save profile
        self._save_profile(profile)

        return profile

    def _determine_archetype(self, responses: Dict[str, int]) -> UserArchetype:
        """Determine user archetype from responses"""
        goal_response = responses.get("goal", 0)
        learning_response = responses.get("learning_preference", 0)

        # Goal question (index 0-3)
        if goal_response == 0:  # "Learn deeply"
            return UserArchetype.LEARNER
        elif goal_response == 1:  # "Working system quickly"
            return UserArchetype.PRAGMATIST
        elif goal_response == 2:  # "Explore possibilities"
            return UserArchetype.EXPLORER
        elif goal_response == 3:  # "Build custom tools"
            return UserArchetype.CREATOR

        # Fallback: use learning preference
        if learning_response == 0:  # "Understand deeply"
            return UserArchetype.LEARNER
        elif learning_response == 1:  # "Get working first"
            return UserArchetype.PRAGMATIST
        elif learning_response == 2:  # "See examples"
            return UserArchetype.EXPLORER
        elif learning_response == 3:  # "Build myself"
            return UserArchetype.CREATOR

        return UserArchetype.UNKNOWN

    def _assess_technical_level(self, responses: Dict[str, int]) -> TechnicalLevel:
        """Assess technical level from experience question"""
        experience = responses.get("experience", 0)

        levels = [
            TechnicalLevel.BEGINNER,      # New to Linux/NixOS
            TechnicalLevel.INTERMEDIATE,  # Know Linux, new to Nix
            TechnicalLevel.ADVANCED,      # Used NixOS, understand basics
            TechnicalLevel.EXPERT         # Very experienced
        ]

        return levels[experience] if experience < len(levels) else TechnicalLevel.BEGINNER

    def _extract_goals(self, responses: Dict[str, int]) -> List[UserGoal]:
        """Extract user goals from responses"""
        goals = []

        goal_response = responses.get("goal", 0)
        goal_texts = [
            "Learn NixOS deeply",
            "Set up working system",
            "Explore NixOS capabilities",
            "Build custom tools"
        ]

        if goal_response < len(goal_texts):
            goals.append(UserGoal(
                description=goal_texts[goal_response],
                category=["learning", "system_setup", "exploration", "development"][goal_response],
                priority=5  # Primary goal is highest priority
            ))

        return goals

    def _choose_engagement_mode(self, archetype: UserArchetype) -> EngagementMode:
        """Choose engagement mode based on archetype"""
        mode_map = {
            UserArchetype.LEARNER: EngagementMode.FULL_TEACHING,
            UserArchetype.PRAGMATIST: EngagementMode.JUST_DO_IT,
            UserArchetype.EXPLORER: EngagementMode.SHOWCASE_POSSIBILITIES,
            UserArchetype.CREATOR: EngagementMode.COLLABORATIVE_DEV,
            UserArchetype.UNKNOWN: EngagementMode.ADAPTIVE
        }
        return mode_map.get(archetype, EngagementMode.ADAPTIVE)

    def _wants_learning(self, responses: Dict[str, int]) -> bool:
        """Determine if user wants educational content"""
        goal = responses.get("goal", 0)
        learning = responses.get("learning_preference", 0)

        # Learners definitely want learning
        if goal == 0 or learning == 0:
            return True

        # Pragmatists may not want as much learning
        if goal == 1 or learning == 1:
            return False

        # Explorers and Creators want some learning
        return True

    def _prefers_automation(self, responses: Dict[str, int]) -> bool:
        """Determine if user wants automation"""
        automation = responses.get("automation_preference", 0)

        # Index 1 = "Handle routine tasks automatically"
        return automation == 1

    def _interested_in_discovery(self, responses: Dict[str, int]) -> bool:
        """Determine if user wants FOSS discovery"""
        discovery = responses.get("discovery", 0)

        # Indices 0 and 1 = interested in alternatives
        return discovery <= 1

    def load_profile(self, user_id: str = "default_user") -> Optional[UserProfile]:
        """Load user profile from disk"""
        if not self.profiles_file.exists():
            return None

        try:
            with open(self.profiles_file, 'r') as f:
                data = json.load(f)

            user_data = data.get(user_id)
            if not user_data:
                return None

            # Reconstruct profile
            profile = UserProfile(
                user_id=user_data["user_id"],
                archetype=UserArchetype(user_data["archetype"]),
                technical_level=TechnicalLevel(user_data["technical_level"]),
                primary_goals=[
                    UserGoal(**goal) for goal in user_data.get("primary_goals", [])
                ],
                engagement_mode=EngagementMode(user_data["engagement_mode"]),
                wants_learning=user_data.get("wants_learning", True),
                prefers_automation=user_data.get("prefers_automation", False),
                learning_style=user_data.get("learning_style"),
                interested_in_alternatives=user_data.get("interested_in_alternatives", True),
                interested_in_customization=user_data.get("interested_in_customization", False),
                onboarding_complete=user_data.get("onboarding_complete", False),
                sessions_count=user_data.get("sessions_count", 0),
                last_updated=user_data.get("last_updated", 0.0),
                archetype_confidence=user_data.get("archetype_confidence", 0.0),
                technical_level_confidence=user_data.get("technical_level_confidence", 0.0)
            )

            return profile

        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def _save_profile(self, profile: UserProfile) -> None:
        """Save user profile to disk"""
        # Load existing profiles
        if self.profiles_file.exists():
            with open(self.profiles_file, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        # Update with new profile
        data[profile.user_id] = {
            "user_id": profile.user_id,
            "archetype": profile.archetype.value,
            "technical_level": profile.technical_level.value,
            "primary_goals": [
                {
                    "description": goal.description,
                    "category": goal.category,
                    "priority": goal.priority,
                    "completed": goal.completed
                }
                for goal in profile.primary_goals
            ],
            "engagement_mode": profile.engagement_mode.value,
            "wants_learning": profile.wants_learning,
            "prefers_automation": profile.prefers_automation,
            "learning_style": profile.learning_style,
            "interested_in_alternatives": profile.interested_in_alternatives,
            "interested_in_customization": profile.interested_in_customization,
            "onboarding_complete": profile.onboarding_complete,
            "sessions_count": profile.sessions_count,
            "last_updated": profile.last_updated,
            "archetype_confidence": profile.archetype_confidence,
            "technical_level_confidence": profile.technical_level_confidence
        }

        # Save
        with open(self.profiles_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update_from_interaction(self, profile: UserProfile, interaction_data: Dict[str, Any]) -> UserProfile:
        """
        Update profile based on actual interactions.

        Over time, we learn more about the user from how they interact:
        - Which commands they use
        - How they respond to teaching
        - What they ask for help with
        - What they automate vs control manually

        This allows archetype confidence to grow with evidence.
        """
        profile.sessions_count += 1

        # Increase confidence with more interactions
        profile.archetype_confidence = min(
            1.0,
            profile.archetype_confidence + 0.02
        )
        profile.technical_level_confidence = min(
            1.0,
            profile.technical_level_confidence + 0.02
        )

        # Update based on interaction patterns
        # (This is simplified - real implementation would analyze patterns)

        self._save_profile(profile)
        return profile


def get_user_profiler() -> UserProfiler:
    """Get singleton instance of user profiler"""
    global _user_profiler

    if _user_profiler is None:
        _user_profiler = UserProfiler()

    return _user_profiler


# Singleton
_user_profiler: Optional[UserProfiler] = None
