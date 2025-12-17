"""
Behavioral Feature Extraction - Revolutionary User Understanding

Instead of ASKING users who they are, we OBSERVE what they do.

Revolutionary capability: Detect user archetype from pure behavior -
no surveys, no self-report. Just watching how they naturally interact.

This is groundbreaking: First AI that understands users through behavior alone.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path
import numpy as np


class InteractionType(Enum):
    """Types of interactions we track"""
    COMMAND = "command"           # User executed a command
    QUERY = "query"               # User asked a question
    ERROR = "error"               # User encountered error
    TEACHING = "teaching"         # User in teaching session
    EXPLORATION = "exploration"   # User exploring alternatives
    CUSTOMIZATION = "customization"  # User customizing system


class ResponseBehavior(Enum):
    """How user responds to AI output"""
    READ_FULLY = "read_fully"         # Read entire response
    SKIMMED = "skimmed"               # Quickly scanned
    ACTED_IMMEDIATELY = "acted_immediately"  # Executed without reading
    ASKED_CLARIFICATION = "asked_clarification"  # Wanted more explanation
    IGNORED = "ignored"               # Didn't engage


class ErrorResponseStyle(Enum):
    """How user handles errors"""
    ASK_FOR_HELP = "ask_for_help"     # Immediately asks AI
    EXPLORE_SELF = "explore_self"     # Tries to figure out themselves
    DEMAND_FIX = "demand_fix"         # Just wants it fixed
    GIVE_UP = "give_up"               # Abandons task


@dataclass
class BehavioralSignal:
    """Single behavioral observation"""
    timestamp: float
    interaction_type: InteractionType

    # Command characteristics
    command_complexity: Optional[float] = None  # 0.0=simple, 1.0=complex
    command_category: Optional[str] = None      # install, configure, query, etc.

    # Response characteristics
    response_length: int = 0                    # Characters in AI response
    reading_time: float = 0.0                   # Seconds spent reading
    response_behavior: Optional[ResponseBehavior] = None

    # Question characteristics
    question_type: Optional[str] = None         # "why", "how", "what", "when"
    question_depth: Optional[float] = None      # 0.0=shallow, 1.0=deep

    # Error handling
    error_encountered: bool = False
    error_response_style: Optional[ErrorResponseStyle] = None

    # Learning engagement
    teaching_participated: bool = False
    teaching_depth_requested: Optional[str] = None  # "skip", "basic", "deep"

    # Exploration behavior
    explored_alternatives: bool = False
    documentation_accessed: bool = False

    # Outcome
    task_completed: bool = False
    needed_help: bool = False


@dataclass
class BehavioralFeatures:
    """
    Aggregated behavioral features for archetype classification.

    These are the signals the neural network uses to detect WHO you are.
    """

    # Command pattern features (5)
    avg_command_complexity: float = 0.5      # Simple (0) vs Complex (1)
    command_variety_score: float = 0.5       # Narrow (0) vs Wide exploration (1)
    install_vs_config_ratio: float = 0.5     # Just install (0) vs Configure (1)
    automation_preference: float = 0.5       # Manual (0) vs Automate (1)
    customization_frequency: float = 0.0     # Never (0) vs Always (1)

    # Response reading features (4)
    avg_reading_time_ratio: float = 0.5      # Skip (0) vs Read fully (1)
    skipping_frequency: float = 0.5          # Never skip (0) vs Always skip (1)
    immediate_action_rate: float = 0.5       # Think first (0) vs Act immediately (1)
    clarification_request_rate: float = 0.0  # Never ask (0) vs Always ask (1)

    # Question pattern features (4)
    why_how_question_ratio: float = 0.0      # What/when (0) vs Why/how (1)
    question_depth_avg: float = 0.5          # Surface (0) vs Deep (1)
    explanation_seeking_rate: float = 0.0    # Don't want (0) vs Always want (1)
    analogy_preference: float = 0.5          # Direct (0) vs Analogies (1)

    # Error handling features (3)
    ask_for_help_rate: float = 0.5           # Figure out (0) vs Ask immediately (1)
    self_exploration_rate: float = 0.5       # Never (0) vs Always (1)
    error_frustration_level: float = 0.0     # Patient (0) vs Frustrated (1)

    # Learning engagement features (4)
    teaching_participation_rate: float = 0.0  # Skip (0) vs Participate (1)
    teaching_depth_preference: float = 0.5    # Surface (0) vs Deep (1)
    example_request_frequency: float = 0.0    # Never (0) vs Always (1)
    practice_engagement_rate: float = 0.0     # Skip (0) vs Do practice (1)

    # Exploration features (4)
    alternative_exploration_rate: float = 0.0  # Stick to known (0) vs Explore (1)
    documentation_reading_rate: float = 0.0    # Never (0) vs Always (1)
    experimentation_frequency: float = 0.0     # Cautious (0) vs Experimental (1)
    curiosity_score: float = 0.0               # Low (0) vs High (1)

    # Meta features (4)
    interaction_count: int = 0                 # Total interactions
    sessions_count: int = 0                    # Total sessions
    avg_session_length: float = 0.0            # Minutes per session
    time_of_day_preference: str = "any"        # morning, afternoon, evening, night

    # Confidence metadata
    feature_confidence: float = 0.0            # 0.0-1.0, based on interaction count
    last_updated: float = 0.0


class BehavioralFeatureExtractor:
    """
    Extracts behavioral features from interaction history.

    Revolutionary: We don't ask users who they are - we OBSERVE and LEARN.
    """

    def __init__(self, storage_dir: str = "~/.luminous-nix"):
        """Initialize feature extractor"""
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.signals_file = self.storage_dir / "behavioral_signals.json"

        # Behavioral signal history
        self.signals: List[BehavioralSignal] = []
        self._load_signals()

    def record_signal(self, signal: BehavioralSignal) -> None:
        """
        Record a behavioral signal.

        Every interaction leaves a trace. Over time, these traces
        reveal who the user is.
        """
        self.signals.append(signal)
        self._save_signals()

    def extract_features(self, user_id: str = "default_user") -> BehavioralFeatures:
        """
        Extract aggregated behavioral features from signal history.

        This is where raw observations become meaningful patterns.
        The neural network uses these features to detect archetype.
        """
        if not self.signals:
            # No data yet - return neutral features
            return BehavioralFeatures()

        features = BehavioralFeatures()

        # Calculate all feature dimensions
        features.avg_command_complexity = self._calc_command_complexity()
        features.command_variety_score = self._calc_command_variety()
        features.install_vs_config_ratio = self._calc_install_config_ratio()
        features.automation_preference = self._calc_automation_preference()
        features.customization_frequency = self._calc_customization_frequency()

        features.avg_reading_time_ratio = self._calc_reading_time_ratio()
        features.skipping_frequency = self._calc_skipping_frequency()
        features.immediate_action_rate = self._calc_immediate_action_rate()
        features.clarification_request_rate = self._calc_clarification_rate()

        features.why_how_question_ratio = self._calc_why_how_ratio()
        features.question_depth_avg = self._calc_question_depth()
        features.explanation_seeking_rate = self._calc_explanation_seeking()
        features.analogy_preference = self._calc_analogy_preference()

        features.ask_for_help_rate = self._calc_ask_for_help_rate()
        features.self_exploration_rate = self._calc_self_exploration_rate()
        features.error_frustration_level = self._calc_frustration_level()

        features.teaching_participation_rate = self._calc_teaching_participation()
        features.teaching_depth_preference = self._calc_teaching_depth_pref()
        features.example_request_frequency = self._calc_example_requests()
        features.practice_engagement_rate = self._calc_practice_engagement()

        features.alternative_exploration_rate = self._calc_alternative_exploration()
        features.documentation_reading_rate = self._calc_documentation_reading()
        features.experimentation_frequency = self._calc_experimentation()
        features.curiosity_score = self._calc_curiosity_score()

        features.interaction_count = len(self.signals)
        features.sessions_count = self._calc_sessions_count()
        features.avg_session_length = self._calc_avg_session_length()
        features.time_of_day_preference = self._calc_time_preference()

        # Confidence increases with more interactions
        features.feature_confidence = min(1.0, len(self.signals) / 50.0)
        features.last_updated = time.time()

        return features

    def to_numpy_array(self, features: BehavioralFeatures) -> np.ndarray:
        """
        Convert features to numpy array for neural network input.

        Neural networks need numbers, not dataclasses.
        """
        return np.array([
            # Command patterns (5)
            features.avg_command_complexity,
            features.command_variety_score,
            features.install_vs_config_ratio,
            features.automation_preference,
            features.customization_frequency,

            # Response reading (4)
            features.avg_reading_time_ratio,
            features.skipping_frequency,
            features.immediate_action_rate,
            features.clarification_request_rate,

            # Question patterns (4)
            features.why_how_question_ratio,
            features.question_depth_avg,
            features.explanation_seeking_rate,
            features.analogy_preference,

            # Error handling (3)
            features.ask_for_help_rate,
            features.self_exploration_rate,
            features.error_frustration_level,

            # Learning engagement (4)
            features.teaching_participation_rate,
            features.teaching_depth_preference,
            features.example_request_frequency,
            features.practice_engagement_rate,

            # Exploration (4)
            features.alternative_exploration_rate,
            features.documentation_reading_rate,
            features.experimentation_frequency,
            features.curiosity_score,

            # Meta (normalize to 0-1)
            min(1.0, features.interaction_count / 100.0),
            min(1.0, features.sessions_count / 20.0),
            min(1.0, features.avg_session_length / 60.0),  # Normalize to 1 hour
        ], dtype=np.float32)

    # Feature calculation methods (simplified for now - will enhance)

    def _calc_command_complexity(self) -> float:
        """Calculate average command complexity"""
        complexities = [s.command_complexity for s in self.signals
                       if s.command_complexity is not None]
        return np.mean(complexities) if complexities else 0.5

    def _calc_command_variety(self) -> float:
        """Calculate command variety score"""
        categories = set(s.command_category for s in self.signals
                        if s.command_category)
        return min(1.0, len(categories) / 10.0)  # Normalize to 10 categories

    def _calc_install_config_ratio(self) -> float:
        """Ratio of install vs configure commands"""
        installs = sum(1 for s in self.signals
                      if s.command_category == "install")
        configs = sum(1 for s in self.signals
                     if s.command_category == "configure")
        total = installs + configs
        return configs / total if total > 0 else 0.5

    def _calc_automation_preference(self) -> float:
        """How much user prefers automation"""
        # Users who act immediately without reading prefer automation
        immediate = sum(1 for s in self.signals
                       if s.response_behavior == ResponseBehavior.ACTED_IMMEDIATELY)
        return immediate / len(self.signals) if self.signals else 0.5

    def _calc_customization_frequency(self) -> float:
        """How often user customizes"""
        customizations = sum(1 for s in self.signals
                           if s.interaction_type == InteractionType.CUSTOMIZATION)
        return customizations / len(self.signals) if self.signals else 0.0

    def _calc_reading_time_ratio(self) -> float:
        """How thoroughly user reads responses"""
        if not self.signals:
            return 0.5

        # Expected reading time: ~200 words/min = 3.3 chars/sec
        reading_ratios = []
        for s in self.signals:
            if s.response_length > 0 and s.reading_time > 0:
                expected_time = s.response_length / 3.3
                actual_ratio = min(1.0, s.reading_time / expected_time)
                reading_ratios.append(actual_ratio)

        return np.mean(reading_ratios) if reading_ratios else 0.5

    def _calc_skipping_frequency(self) -> float:
        """How often user skips reading"""
        skipped = sum(1 for s in self.signals
                     if s.response_behavior == ResponseBehavior.SKIMMED)
        return skipped / len(self.signals) if self.signals else 0.5

    def _calc_immediate_action_rate(self) -> float:
        """How often user acts without thinking"""
        immediate = sum(1 for s in self.signals
                       if s.response_behavior == ResponseBehavior.ACTED_IMMEDIATELY)
        return immediate / len(self.signals) if self.signals else 0.5

    def _calc_clarification_rate(self) -> float:
        """How often user asks for clarification"""
        clarifications = sum(1 for s in self.signals
                           if s.response_behavior == ResponseBehavior.ASKED_CLARIFICATION)
        return clarifications / len(self.signals) if self.signals else 0.0

    def _calc_why_how_ratio(self) -> float:
        """Ratio of why/how questions vs what/when"""
        why_how = sum(1 for s in self.signals
                     if s.question_type in ["why", "how", "explain"])
        what_when = sum(1 for s in self.signals
                       if s.question_type in ["what", "when", "which"])
        total = why_how + what_when
        return why_how / total if total > 0 else 0.0

    def _calc_question_depth(self) -> float:
        """Average depth of questions asked"""
        depths = [s.question_depth for s in self.signals
                 if s.question_depth is not None]
        return np.mean(depths) if depths else 0.5

    def _calc_explanation_seeking(self) -> float:
        """How often user seeks explanations"""
        seeking = sum(1 for s in self.signals
                     if s.question_type in ["why", "how", "explain"])
        return seeking / len(self.signals) if self.signals else 0.0

    def _calc_analogy_preference(self) -> float:
        """Preference for analogies (from meta-learning)"""
        # This would integrate with Layer 4 meta-learning
        # For now, placeholder
        return 0.5

    def _calc_ask_for_help_rate(self) -> float:
        """How often user asks for help on errors"""
        errors = [s for s in self.signals if s.error_encountered]
        if not errors:
            return 0.5

        asked_help = sum(1 for s in errors
                        if s.error_response_style == ErrorResponseStyle.ASK_FOR_HELP)
        return asked_help / len(errors)

    def _calc_self_exploration_rate(self) -> float:
        """How often user explores solutions themselves"""
        errors = [s for s in self.signals if s.error_encountered]
        if not errors:
            return 0.5

        explored = sum(1 for s in errors
                      if s.error_response_style == ErrorResponseStyle.EXPLORE_SELF)
        return explored / len(errors)

    def _calc_frustration_level(self) -> float:
        """Estimate frustration from error patterns"""
        errors = [s for s in self.signals if s.error_encountered]
        if not errors:
            return 0.0

        # Quick succession of errors = frustration
        frustration_signals = 0
        for i in range(1, len(errors)):
            time_diff = errors[i].timestamp - errors[i-1].timestamp
            if time_diff < 300:  # Less than 5 minutes
                frustration_signals += 1

        return min(1.0, frustration_signals / max(1, len(errors)))

    def _calc_teaching_participation(self) -> float:
        """How often user participates in teaching"""
        teaching = sum(1 for s in self.signals if s.teaching_participated)
        return teaching / len(self.signals) if self.signals else 0.0

    def _calc_teaching_depth_pref(self) -> float:
        """Preference for teaching depth"""
        teaching = [s for s in self.signals if s.teaching_depth_requested]
        if not teaching:
            return 0.5

        depth_map = {"skip": 0.0, "basic": 0.5, "deep": 1.0}
        depths = [depth_map.get(s.teaching_depth_requested, 0.5) for s in teaching]
        return np.mean(depths)

    def _calc_example_requests(self) -> float:
        """How often user requests examples"""
        # Would track from interaction history
        return 0.0

    def _calc_practice_engagement(self) -> float:
        """How often user does practice exercises"""
        # Would track practice completion
        return 0.0

    def _calc_alternative_exploration(self) -> float:
        """How often user explores alternatives"""
        explorations = sum(1 for s in self.signals if s.explored_alternatives)
        return explorations / len(self.signals) if self.signals else 0.0

    def _calc_documentation_reading(self) -> float:
        """How often user reads documentation"""
        doc_reads = sum(1 for s in self.signals if s.documentation_accessed)
        return doc_reads / len(self.signals) if self.signals else 0.0

    def _calc_experimentation(self) -> float:
        """How often user experiments"""
        experiments = sum(1 for s in self.signals
                         if s.interaction_type == InteractionType.EXPLORATION)
        return experiments / len(self.signals) if self.signals else 0.0

    def _calc_curiosity_score(self) -> float:
        """Overall curiosity score"""
        # Combination of exploration, documentation, alternatives
        exploration = self._calc_alternative_exploration()
        documentation = self._calc_documentation_reading()
        experimentation = self._calc_experimentation()
        return (exploration + documentation + experimentation) / 3.0

    def _calc_sessions_count(self) -> int:
        """Count distinct sessions"""
        # Sessions separated by >30 minutes
        if not self.signals:
            return 0

        sessions = 1
        for i in range(1, len(self.signals)):
            time_diff = self.signals[i].timestamp - self.signals[i-1].timestamp
            if time_diff > 1800:  # 30 minutes
                sessions += 1

        return sessions

    def _calc_avg_session_length(self) -> float:
        """Average session length in minutes"""
        if not self.signals:
            return 0.0

        total_time = self.signals[-1].timestamp - self.signals[0].timestamp
        sessions = self._calc_sessions_count()
        return (total_time / 60.0) / sessions if sessions > 0 else 0.0

    def _calc_time_preference(self) -> str:
        """Determine preferred time of day"""
        if not self.signals:
            return "any"

        # Count interactions by time of day
        from datetime import datetime

        morning = afternoon = evening = night = 0
        for signal in self.signals:
            hour = datetime.fromtimestamp(signal.timestamp).hour
            if 6 <= hour < 12:
                morning += 1
            elif 12 <= hour < 18:
                afternoon += 1
            elif 18 <= hour < 22:
                evening += 1
            else:
                night += 1

        times = {"morning": morning, "afternoon": afternoon,
                "evening": evening, "night": night}
        return max(times, key=times.get) if sum(times.values()) > 0 else "any"

    def _save_signals(self) -> None:
        """Save signals to disk"""
        data = []
        for signal in self.signals:
            signal_dict = {
                "timestamp": signal.timestamp,
                "interaction_type": signal.interaction_type.value,
                "command_complexity": signal.command_complexity,
                "command_category": signal.command_category,
                "response_length": signal.response_length,
                "reading_time": signal.reading_time,
                "response_behavior": signal.response_behavior.value if signal.response_behavior else None,
                "question_type": signal.question_type,
                "question_depth": signal.question_depth,
                "error_encountered": signal.error_encountered,
                "error_response_style": signal.error_response_style.value if signal.error_response_style else None,
                "teaching_participated": signal.teaching_participated,
                "teaching_depth_requested": signal.teaching_depth_requested,
                "explored_alternatives": signal.explored_alternatives,
                "documentation_accessed": signal.documentation_accessed,
                "task_completed": signal.task_completed,
                "needed_help": signal.needed_help
            }
            data.append(signal_dict)

        with open(self.signals_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_signals(self) -> None:
        """Load signals from disk"""
        if not self.signals_file.exists():
            return

        try:
            with open(self.signals_file, 'r') as f:
                data = json.load(f)

            for signal_dict in data:
                signal = BehavioralSignal(
                    timestamp=signal_dict["timestamp"],
                    interaction_type=InteractionType(signal_dict["interaction_type"]),
                    command_complexity=signal_dict.get("command_complexity"),
                    command_category=signal_dict.get("command_category"),
                    response_length=signal_dict.get("response_length", 0),
                    reading_time=signal_dict.get("reading_time", 0.0),
                    response_behavior=ResponseBehavior(signal_dict["response_behavior"]) if signal_dict.get("response_behavior") else None,
                    question_type=signal_dict.get("question_type"),
                    question_depth=signal_dict.get("question_depth"),
                    error_encountered=signal_dict.get("error_encountered", False),
                    error_response_style=ErrorResponseStyle(signal_dict["error_response_style"]) if signal_dict.get("error_response_style") else None,
                    teaching_participated=signal_dict.get("teaching_participated", False),
                    teaching_depth_requested=signal_dict.get("teaching_depth_requested"),
                    explored_alternatives=signal_dict.get("explored_alternatives", False),
                    documentation_accessed=signal_dict.get("documentation_accessed", False),
                    task_completed=signal_dict.get("task_completed", False),
                    needed_help=signal_dict.get("needed_help", False)
                )
                self.signals.append(signal)
        except Exception as e:
            print(f"Error loading behavioral signals: {e}")


def get_behavioral_extractor() -> BehavioralFeatureExtractor:
    """Get singleton instance of behavioral feature extractor"""
    global _behavioral_extractor

    if _behavioral_extractor is None:
        _behavioral_extractor = BehavioralFeatureExtractor()

    return _behavioral_extractor


# Singleton
_behavioral_extractor: Optional[BehavioralFeatureExtractor] = None
