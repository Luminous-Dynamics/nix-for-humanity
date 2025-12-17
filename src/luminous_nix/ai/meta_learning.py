"""
Meta-Learning Intelligence - AI That Learns How You Learn

Revolutionary Layer 4: Not just teaching - discovering the OPTIMAL way to teach each user.

This module:
- Detects learning styles (Visual, Auditory, Kinesthetic, Reading/Writing)
- Measures learning effectiveness for each teaching mode
- Adapts teaching strategies dynamically
- Optimizes learning paths for individual users
- Discovers patterns in learning behavior

Philosophy: Every person learns differently. The best AI adapts to YOU.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import os
from pathlib import Path


class LearningStyle(Enum):
    """Primary learning modalities (VARK model)"""
    VISUAL = "visual"           # Learns through seeing (diagrams, charts, images)
    AUDITORY = "auditory"       # Learns through hearing (explanations, discussions)
    KINESTHETIC = "kinesthetic" # Learns through doing (hands-on, practice)
    READING = "reading"         # Learns through reading/writing (text, notes)


class TeachingEffectiveness(Enum):
    """How well a teaching approach worked"""
    EXCELLENT = "excellent"     # User understood immediately, high confidence
    GOOD = "good"              # User understood after clarification
    MODERATE = "moderate"      # User needed hints, partial understanding
    POOR = "poor"              # User struggled, needed multiple attempts


@dataclass
class LearningPreference:
    """User's learning preferences and patterns"""
    primary_style: LearningStyle
    secondary_style: Optional[LearningStyle]

    # Detailed preferences
    prefers_examples: bool = True        # Needs concrete examples?
    prefers_diagrams: bool = False       # Wants visual representations?
    prefers_practice: bool = True        # Learn by doing?
    prefers_theory: bool = False         # Wants deep explanations?

    # Pace preferences
    learning_pace: str = "moderate"      # fast, moderate, slow
    example_count_needed: int = 2        # How many examples typically needed

    # Optimal learning conditions
    best_time_of_day: Optional[str] = None  # morning, afternoon, evening
    attention_span_minutes: int = 30     # Typical focus duration

    # Confidence in these preferences (0.0-1.0)
    confidence: float = 0.0


@dataclass
class TeachingAttempt:
    """Record of a teaching interaction"""
    timestamp: float
    concept_id: str
    teaching_mode: str              # Analogy, Example, Question, etc.
    user_response: str
    effectiveness: TeachingEffectiveness
    time_to_understand: float       # Seconds
    hints_needed: int
    examples_shown: int
    user_confidence_after: float    # 0.0-1.0


@dataclass
class LearningPattern:
    """Discovered pattern in user's learning"""
    pattern_type: str              # "time_of_day", "concept_type", "teaching_mode"
    pattern_description: str       # What we discovered
    evidence: List[TeachingAttempt]
    confidence: float              # How sure we are (0.0-1.0)
    recommendation: str            # What to do based on this pattern


class MetaLearningEngine:
    """
    Learns how the user learns best and adapts teaching accordingly.

    This is revolutionary because:
    1. Personalizes teaching approach to individual learning style
    2. Discovers optimal teaching strategies through experimentation
    3. Continuously improves teaching effectiveness
    4. Adapts in real-time based on user responses
    """

    def __init__(self, user_id: str = "default"):
        """Initialize meta-learning engine for a user"""
        self.user_id = user_id
        self.storage_path = Path.home() / ".luminous-nix" / "meta_learning.json"

        # Learning history
        self.teaching_attempts: List[TeachingAttempt] = []

        # Current understanding of user
        self.learning_preferences = LearningPreference(
            primary_style=LearningStyle.KINESTHETIC,  # Default: learn by doing
            secondary_style=None
        )

        # Discovered patterns
        self.discovered_patterns: List[LearningPattern] = []

        # Load existing data if available
        self._load_data()

    def record_teaching_attempt(
        self,
        concept_id: str,
        teaching_mode: str,
        user_response: str,
        understood: bool,
        time_taken: float,
        hints_needed: int = 0,
        examples_shown: int = 0
    ) -> None:
        """
        Record a teaching interaction and learn from it.

        This is where the meta-learning magic happens!
        """
        # Determine effectiveness
        if understood and hints_needed == 0 and time_taken < 30:
            effectiveness = TeachingEffectiveness.EXCELLENT
            user_confidence = 0.9
        elif understood and hints_needed <= 1:
            effectiveness = TeachingEffectiveness.GOOD
            user_confidence = 0.7
        elif understood and hints_needed > 1:
            effectiveness = TeachingEffectiveness.MODERATE
            user_confidence = 0.5
        else:
            effectiveness = TeachingEffectiveness.POOR
            user_confidence = 0.3

        attempt = TeachingAttempt(
            timestamp=time.time(),
            concept_id=concept_id,
            teaching_mode=teaching_mode,
            user_response=user_response,
            effectiveness=effectiveness,
            time_to_understand=time_taken,
            hints_needed=hints_needed,
            examples_shown=examples_shown,
            user_confidence_after=user_confidence
        )

        self.teaching_attempts.append(attempt)

        # Analyze and adapt
        self._analyze_effectiveness()
        self._update_preferences()
        self._discover_patterns()
        self._save_data()

    def _analyze_effectiveness(self) -> None:
        """Analyze which teaching modes are most effective for this user"""
        if len(self.teaching_attempts) < 3:
            return  # Need more data

        # Group by teaching mode
        mode_effectiveness: Dict[str, List[TeachingEffectiveness]] = {}

        for attempt in self.teaching_attempts[-20:]:  # Last 20 attempts
            mode = attempt.teaching_mode
            if mode not in mode_effectiveness:
                mode_effectiveness[mode] = []
            mode_effectiveness[mode].append(attempt.effectiveness)

        # Calculate effectiveness scores
        effectiveness_scores = {
            TeachingEffectiveness.EXCELLENT: 1.0,
            TeachingEffectiveness.GOOD: 0.7,
            TeachingEffectiveness.MODERATE: 0.4,
            TeachingEffectiveness.POOR: 0.1
        }

        mode_scores = {}
        for mode, effectiveness_list in mode_effectiveness.items():
            score = sum(effectiveness_scores[e] for e in effectiveness_list) / len(effectiveness_list)
            mode_scores[mode] = score

        # Store for optimization
        self.mode_effectiveness_scores = mode_scores

    def _update_preferences(self) -> None:
        """Update learning preferences based on teaching history"""
        if len(self.teaching_attempts) < 5:
            return  # Need more data

        # Use all attempts if less than 10, otherwise last 10
        recent = self.teaching_attempts[-10:] if len(self.teaching_attempts) >= 10 else self.teaching_attempts

        # Detect if user needs more examples
        avg_examples = sum(a.examples_shown for a in recent) / len(recent)
        self.learning_preferences.example_count_needed = max(1, int(avg_examples + 0.5))

        # Detect if user learns better with practice
        practice_attempts = [a for a in recent if a.teaching_mode.lower() == "practice"]
        if practice_attempts:
            avg_practice_effectiveness = sum(
                1.0 if a.effectiveness in [TeachingEffectiveness.EXCELLENT, TeachingEffectiveness.GOOD]
                else 0.0
                for a in practice_attempts
            ) / len(practice_attempts)

            self.learning_preferences.prefers_practice = avg_practice_effectiveness > 0.6

        # Detect learning style from successful attempts
        successful = [a for a in recent if a.effectiveness in [
            TeachingEffectiveness.EXCELLENT,
            TeachingEffectiveness.GOOD
        ]]

        if successful:
            # Count modes in successful attempts
            mode_counts = {}
            for attempt in successful:
                mode = attempt.teaching_mode.lower()
                mode_counts[mode] = mode_counts.get(mode, 0) + 1

            # Infer learning style
            if mode_counts.get('example', 0) > len(successful) * 0.5:
                self.learning_preferences.primary_style = LearningStyle.VISUAL
            elif mode_counts.get('practice', 0) > len(successful) * 0.5:
                self.learning_preferences.primary_style = LearningStyle.KINESTHETIC
            elif mode_counts.get('explanation', 0) > len(successful) * 0.5:
                self.learning_preferences.primary_style = LearningStyle.READING

        # Update confidence in preferences
        if len(self.teaching_attempts) >= 5:
            self.learning_preferences.confidence = min(1.0, len(self.teaching_attempts) / 20)

    def _discover_patterns(self) -> None:
        """Discover patterns in learning behavior"""
        if len(self.teaching_attempts) < 4:
            return  # Need more data

        # Pattern: Time of day effectiveness
        self._discover_time_patterns()

        # Pattern: Concept type difficulty
        self._discover_concept_patterns()

        # Pattern: Teaching mode effectiveness
        self._discover_mode_patterns()

    def _discover_time_patterns(self) -> None:
        """Discover if user learns better at certain times"""
        time_buckets = {"morning": [], "afternoon": [], "evening": [], "night": []}

        for attempt in self.teaching_attempts[-30:]:  # Last 30 attempts
            hour = time.localtime(attempt.timestamp).tm_hour

            if 5 <= hour < 12:
                bucket = "morning"
            elif 12 <= hour < 17:
                bucket = "afternoon"
            elif 17 <= hour < 22:
                bucket = "evening"
            else:
                bucket = "night"

            effectiveness_score = {
                TeachingEffectiveness.EXCELLENT: 1.0,
                TeachingEffectiveness.GOOD: 0.7,
                TeachingEffectiveness.MODERATE: 0.4,
                TeachingEffectiveness.POOR: 0.1
            }[attempt.effectiveness]

            time_buckets[bucket].append(effectiveness_score)

        # Find best time
        avg_scores = {
            time: sum(scores) / len(scores)
            for time, scores in time_buckets.items()
            if scores
        }

        if avg_scores:
            best_time = max(avg_scores.items(), key=lambda x: x[1])
            if best_time[1] > 0.6 and len(time_buckets[best_time[0]]) >= 3:
                self.learning_preferences.best_time_of_day = best_time[0]

                # Create pattern
                pattern = LearningPattern(
                    pattern_type="time_of_day",
                    pattern_description=f"User learns best in the {best_time[0]} (effectiveness: {best_time[1]:.0%})",
                    evidence=[a for a in self.teaching_attempts if self._get_time_bucket(a.timestamp) == best_time[0]],
                    confidence=min(1.0, len(time_buckets[best_time[0]]) / 10),
                    recommendation=f"Schedule challenging concepts for {best_time[0]} learning sessions"
                )

                # Add or update pattern
                self._update_pattern(pattern)

    def _discover_concept_patterns(self) -> None:
        """Discover which concept types are easier/harder"""
        # Group by concept
        concept_effectiveness: Dict[str, List[float]] = {}

        for attempt in self.teaching_attempts[-20:]:
            concept = attempt.concept_id
            score = {
                TeachingEffectiveness.EXCELLENT: 1.0,
                TeachingEffectiveness.GOOD: 0.7,
                TeachingEffectiveness.MODERATE: 0.4,
                TeachingEffectiveness.POOR: 0.1
            }[attempt.effectiveness]

            if concept not in concept_effectiveness:
                concept_effectiveness[concept] = []
            concept_effectiveness[concept].append(score)

        # Identify difficult concepts (for extra support)
        for concept, scores in concept_effectiveness.items():
            if len(scores) >= 2:
                avg_score = sum(scores) / len(scores)

                if avg_score < 0.5:
                    pattern = LearningPattern(
                        pattern_type="concept_difficulty",
                        pattern_description=f"User finds {concept} challenging (effectiveness: {avg_score:.0%})",
                        evidence=[a for a in self.teaching_attempts if a.concept_id == concept],
                        confidence=min(1.0, len(scores) / 5),
                        recommendation=f"Use more examples and practice for {concept}. Consider breaking into smaller steps."
                    )
                    self._update_pattern(pattern)

    def _discover_mode_patterns(self) -> None:
        """Discover which teaching modes work best"""
        if not hasattr(self, 'mode_effectiveness_scores'):
            return

        # Find best mode
        if self.mode_effectiveness_scores:
            best_mode = max(self.mode_effectiveness_scores.items(), key=lambda x: x[1])

            if best_mode[1] > 0.6:
                pattern = LearningPattern(
                    pattern_type="teaching_mode",
                    pattern_description=f"User learns best with {best_mode[0]} (effectiveness: {best_mode[1]:.0%})",
                    evidence=[a for a in self.teaching_attempts if a.teaching_mode == best_mode[0]],
                    confidence=min(1.0, len([a for a in self.teaching_attempts if a.teaching_mode == best_mode[0]]) / 5),
                    recommendation=f"Prioritize {best_mode[0]} mode in teaching sequences"
                )
                self._update_pattern(pattern)

    def _update_pattern(self, new_pattern: LearningPattern) -> None:
        """Add or update a discovered pattern"""
        # Check if pattern of this type already exists
        for i, pattern in enumerate(self.discovered_patterns):
            if pattern.pattern_type == new_pattern.pattern_type:
                self.discovered_patterns[i] = new_pattern
                return

        # Add new pattern
        self.discovered_patterns.append(new_pattern)

    def _get_time_bucket(self, timestamp: float) -> str:
        """Get time bucket for a timestamp"""
        hour = time.localtime(timestamp).tm_hour

        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def get_optimal_teaching_strategy(self, concept_id: str) -> Dict[str, Any]:
        """
        Get optimal teaching strategy for this user and concept.

        This is the meta-learning in action!
        """
        strategy = {
            "primary_mode": "question",  # Default
            "example_count": 2,
            "use_diagrams": False,
            "pace": "moderate",
            "hints_ready": True,
            "personalization_notes": []
        }

        # Personalize based on learning preferences
        prefs = self.learning_preferences

        # Adapt primary mode
        if prefs.primary_style == LearningStyle.VISUAL:
            strategy["primary_mode"] = "example"
            strategy["use_diagrams"] = True
            strategy["personalization_notes"].append("Visual learner - using diagrams and examples")
        elif prefs.primary_style == LearningStyle.KINESTHETIC:
            strategy["primary_mode"] = "practice"
            strategy["personalization_notes"].append("Kinesthetic learner - emphasizing hands-on practice")
        elif prefs.primary_style == LearningStyle.READING:
            strategy["primary_mode"] = "explanation"
            strategy["personalization_notes"].append("Reading learner - providing detailed explanations")

        # Adapt example count
        strategy["example_count"] = prefs.example_count_needed

        # Adapt pace
        strategy["pace"] = prefs.learning_pace

        # Check for concept-specific patterns
        for pattern in self.discovered_patterns:
            if pattern.pattern_type == "concept_difficulty" and concept_id in pattern.pattern_description:
                strategy["example_count"] += 1
                strategy["hints_ready"] = True
                strategy["pace"] = "slow"
                strategy["personalization_notes"].append(f"Challenging concept - extra support ready")

        # Check for time-of-day optimization
        if prefs.best_time_of_day:
            current_hour = time.localtime().tm_hour
            current_bucket = self._get_time_bucket(time.time())

            if current_bucket != prefs.best_time_of_day:
                strategy["personalization_notes"].append(
                    f"FYI: You typically learn best in the {prefs.best_time_of_day}"
                )

        # Add confidence indicator
        strategy["personalization_confidence"] = prefs.confidence

        return strategy

    def get_learning_profile(self) -> Dict[str, Any]:
        """Get comprehensive learning profile for user"""
        return {
            "user_id": self.user_id,
            "primary_learning_style": self.learning_preferences.primary_style.value,
            "secondary_learning_style": self.learning_preferences.secondary_style.value if self.learning_preferences.secondary_style else None,
            "preferences": {
                "examples_needed": self.learning_preferences.example_count_needed,
                "prefers_practice": self.learning_preferences.prefers_practice,
                "prefers_diagrams": self.learning_preferences.prefers_diagrams,
                "learning_pace": self.learning_preferences.learning_pace,
                "best_time": self.learning_preferences.best_time_of_day
            },
            "teaching_history": {
                "total_attempts": len(self.teaching_attempts),
                "recent_effectiveness": self._get_recent_effectiveness(),
                "improvement_trend": self._get_improvement_trend()
            },
            "discovered_patterns": [
                {
                    "type": p.pattern_type,
                    "description": p.pattern_description,
                    "confidence": p.confidence,
                    "recommendation": p.recommendation
                }
                for p in self.discovered_patterns
            ],
            "confidence": self.learning_preferences.confidence
        }

    def _get_recent_effectiveness(self) -> float:
        """Calculate recent teaching effectiveness"""
        if not self.teaching_attempts:
            return 0.0

        recent = self.teaching_attempts[-5:]
        effectiveness_scores = {
            TeachingEffectiveness.EXCELLENT: 1.0,
            TeachingEffectiveness.GOOD: 0.7,
            TeachingEffectiveness.MODERATE: 0.4,
            TeachingEffectiveness.POOR: 0.1
        }

        return sum(effectiveness_scores[a.effectiveness] for a in recent) / len(recent)

    def _get_improvement_trend(self) -> str:
        """Determine if user is improving over time"""
        if len(self.teaching_attempts) < 6:
            return "insufficient_data"

        # Compare first half vs second half
        mid = len(self.teaching_attempts) // 2
        first_half = self.teaching_attempts[:mid]
        second_half = self.teaching_attempts[mid:]

        effectiveness_scores = {
            TeachingEffectiveness.EXCELLENT: 1.0,
            TeachingEffectiveness.GOOD: 0.7,
            TeachingEffectiveness.MODERATE: 0.4,
            TeachingEffectiveness.POOR: 0.1
        }

        first_avg = sum(effectiveness_scores[a.effectiveness] for a in first_half) / len(first_half)
        second_avg = sum(effectiveness_scores[a.effectiveness] for a in second_half) / len(second_half)

        if second_avg > first_avg + 0.1:
            return "improving"
        elif second_avg < first_avg - 0.1:
            return "declining"
        else:
            return "stable"

    def _save_data(self) -> None:
        """Save meta-learning data to disk"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "user_id": self.user_id,
            "learning_preferences": {
                "primary_style": self.learning_preferences.primary_style.value,
                "secondary_style": self.learning_preferences.secondary_style.value if self.learning_preferences.secondary_style else None,
                "prefers_examples": self.learning_preferences.prefers_examples,
                "prefers_diagrams": self.learning_preferences.prefers_diagrams,
                "prefers_practice": self.learning_preferences.prefers_practice,
                "prefers_theory": self.learning_preferences.prefers_theory,
                "learning_pace": self.learning_preferences.learning_pace,
                "example_count_needed": self.learning_preferences.example_count_needed,
                "best_time_of_day": self.learning_preferences.best_time_of_day,
                "confidence": self.learning_preferences.confidence
            },
            "teaching_attempts": [
                {
                    "timestamp": a.timestamp,
                    "concept_id": a.concept_id,
                    "teaching_mode": a.teaching_mode,
                    "effectiveness": a.effectiveness.value,
                    "time_to_understand": a.time_to_understand,
                    "hints_needed": a.hints_needed,
                    "examples_shown": a.examples_shown,
                    "user_confidence_after": a.user_confidence_after
                }
                for a in self.teaching_attempts[-100:]  # Keep last 100
            ],
            "discovered_patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "pattern_description": p.pattern_description,
                    "confidence": p.confidence,
                    "recommendation": p.recommendation
                }
                for p in self.discovered_patterns
            ]
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_data(self) -> None:
        """Load meta-learning data from disk"""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            # Load preferences
            prefs_data = data.get("learning_preferences", {})
            self.learning_preferences = LearningPreference(
                primary_style=LearningStyle(prefs_data.get("primary_style", "kinesthetic")),
                secondary_style=LearningStyle(prefs_data["secondary_style"]) if prefs_data.get("secondary_style") else None,
                prefers_examples=prefs_data.get("prefers_examples", True),
                prefers_diagrams=prefs_data.get("prefers_diagrams", False),
                prefers_practice=prefs_data.get("prefers_practice", True),
                prefers_theory=prefs_data.get("prefers_theory", False),
                learning_pace=prefs_data.get("learning_pace", "moderate"),
                example_count_needed=prefs_data.get("example_count_needed", 2),
                best_time_of_day=prefs_data.get("best_time_of_day"),
                confidence=prefs_data.get("confidence", 0.0)
            )

            # Load teaching attempts
            for attempt_data in data.get("teaching_attempts", []):
                attempt = TeachingAttempt(
                    timestamp=attempt_data["timestamp"],
                    concept_id=attempt_data["concept_id"],
                    teaching_mode=attempt_data["teaching_mode"],
                    user_response="",  # Not stored
                    effectiveness=TeachingEffectiveness(attempt_data["effectiveness"]),
                    time_to_understand=attempt_data["time_to_understand"],
                    hints_needed=attempt_data["hints_needed"],
                    examples_shown=attempt_data["examples_shown"],
                    user_confidence_after=attempt_data["user_confidence_after"]
                )
                self.teaching_attempts.append(attempt)

            # Load patterns
            for pattern_data in data.get("discovered_patterns", []):
                pattern = LearningPattern(
                    pattern_type=pattern_data["pattern_type"],
                    pattern_description=pattern_data["pattern_description"],
                    evidence=[],  # Not stored
                    confidence=pattern_data["confidence"],
                    recommendation=pattern_data["recommendation"]
                )
                self.discovered_patterns.append(pattern)

        except Exception as e:
            print(f"Warning: Could not load meta-learning data: {e}")


# Singleton instance
_meta_learning_engine: Optional[MetaLearningEngine] = None


def get_meta_learning_engine(user_id: str = "default") -> MetaLearningEngine:
    """Get singleton instance of meta-learning engine"""
    global _meta_learning_engine

    if _meta_learning_engine is None:
        _meta_learning_engine = MetaLearningEngine(user_id)

    return _meta_learning_engine
