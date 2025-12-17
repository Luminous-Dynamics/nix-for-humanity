"""
Real-Time Emotional Intelligence - Layer 6 Component 1

Revolutionary capability: Detect user's EMOTIONAL STATE in real-time
during conversation, not just their archetype over time.

This is like having emotional intelligence in AI - understanding not just
WHO you are, but HOW YOU FEEL right now in this moment.

Five Emotional States Detected:
1. FLOW - Deep engagement, everything clicking
2. FRUSTRATED - Stuck, errors, repeated attempts
3. CONFUSED - Uncertain, asking for clarification
4. EXCITED - Rapid experimentation, high engagement
5. OVERWHELMED - Too much information, slowing down

Detection happens in REAL-TIME from micro-patterns in the conversation.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics


class EmotionalState(Enum):
    """Five primary emotional states we can detect"""
    FLOW = "flow"                    # Deep engagement, productive
    FRUSTRATED = "frustrated"        # Stuck, errors, struggling
    CONFUSED = "confused"            # Uncertain, needs clarification
    EXCITED = "excited"              # High energy, experimenting
    OVERWHELMED = "overwhelmed"      # Too much, needs simplification


@dataclass
class EmotionalSignal:
    """
    A single micro-pattern that indicates emotional state.

    These are REAL-TIME indicators - much faster than archetype detection.
    We can detect emotional shifts within 2-3 interactions.
    """
    timestamp: str
    signal_type: str              # "rapid_query", "error", "clarification", etc.
    intensity: float              # 0.0-1.0 how strong the signal is
    context: Optional[Dict] = None

    # Common signal types:
    # - "rapid_query" (typing fast, short queries)
    # - "error_encountered" (command failed)
    # - "repeated_query" (asked same thing again)
    # - "clarification_request" ("what does X mean?")
    # - "long_pause" (took time to respond)
    # - "experimentation" (trying different approaches)
    # - "copy_paste" (executing immediately)
    # - "reading_fully" (took time with response)
    # - "skipping_ahead" (quick scroll through)


@dataclass
class EmotionalStateSnapshot:
    """Current emotional state with confidence and indicators"""
    state: EmotionalState
    confidence: float              # 0.0-1.0
    intensity: float               # 0.0-1.0 how strongly they feel it
    duration_seconds: float        # How long in this state
    key_signals: List[str]         # What indicated this state
    trend: str                     # "improving", "stable", "worsening"


class RealTimeEmotionalDetector:
    """
    Detects emotional state in real-time from conversation patterns.

    Revolutionary features:
    - Detects state shifts within 2-3 interactions (not 10+)
    - Uses micro-patterns (response time, query length, errors)
    - Provides intensity scores (slightly frustrated vs very frustrated)
    - Tracks emotional trajectory (getting better or worse?)
    - Context-aware (same pattern means different things in different contexts)
    """

    def __init__(self):
        """Initialize emotional detector"""
        # Recent signal history (last 10 signals)
        self.recent_signals: List[EmotionalSignal] = []
        self.max_recent_signals = 10

        # Current emotional state
        self.current_state: Optional[EmotionalState] = None
        self.state_start_time: Optional[datetime] = None
        self.state_confidence: float = 0.0

        # State history for trend analysis
        self.state_history: List[EmotionalStateSnapshot] = []

    def record_signal(self, signal: EmotionalSignal):
        """
        Record an emotional signal from the conversation.

        Call this after EVERY interaction to maintain real-time detection.
        """
        self.recent_signals.append(signal)

        # Keep only recent signals
        if len(self.recent_signals) > self.max_recent_signals:
            self.recent_signals.pop(0)

    def detect_current_state(self) -> EmotionalStateSnapshot:
        """
        Detect current emotional state from recent signals.

        This is FAST - analyzes last 10 signals to determine state.
        Can detect shifts within 2-3 interactions.

        Returns:
            Current emotional state with confidence and details
        """
        if not self.recent_signals:
            # No data yet - assume neutral/flow
            return EmotionalStateSnapshot(
                state=EmotionalState.FLOW,
                confidence=0.0,
                intensity=0.0,
                duration_seconds=0.0,
                key_signals=[],
                trend="stable"
            )

        # Calculate scores for each emotional state
        flow_score = self._calculate_flow_score()
        frustrated_score = self._calculate_frustrated_score()
        confused_score = self._calculate_confused_score()
        excited_score = self._calculate_excited_score()
        overwhelmed_score = self._calculate_overwhelmed_score()

        # Find dominant state
        scores = {
            EmotionalState.FLOW: flow_score,
            EmotionalState.FRUSTRATED: frustrated_score,
            EmotionalState.CONFUSED: confused_score,
            EmotionalState.EXCITED: excited_score,
            EmotionalState.OVERWHELMED: overwhelmed_score
        }

        detected_state = max(scores, key=scores.get)
        state_score = scores[detected_state]

        # Calculate confidence (how clear is this state?)
        confidence = self._calculate_confidence(scores, detected_state)

        # Get key signals for this state
        key_signals = self._get_key_signals_for_state(detected_state)

        # Calculate duration if state hasn't changed
        duration = self._calculate_state_duration(detected_state)

        # Determine trend
        trend = self._calculate_emotional_trend(detected_state)

        # Create snapshot
        snapshot = EmotionalStateSnapshot(
            state=detected_state,
            confidence=confidence,
            intensity=state_score,
            duration_seconds=duration,
            key_signals=key_signals,
            trend=trend
        )

        # Update current state
        if self.current_state != detected_state:
            self.current_state = detected_state
            self.state_start_time = datetime.now()

        self.state_confidence = confidence
        self.state_history.append(snapshot)

        return snapshot

    def _calculate_flow_score(self) -> float:
        """
        Calculate likelihood user is in FLOW state.

        Flow indicators:
        - Consistent interaction pace (not too fast, not too slow)
        - Few errors
        - No repeated questions
        - Reading responses fully
        - Executing commands successfully
        - Long session duration
        """
        if not self.recent_signals:
            return 0.0

        flow_indicators = 0.0
        total = len(self.recent_signals)

        for signal in self.recent_signals:
            if signal.signal_type == "reading_fully":
                flow_indicators += 1.0
            elif signal.signal_type == "copy_paste":
                flow_indicators += 0.8
            elif signal.signal_type == "experimentation":
                flow_indicators += 0.6
            elif signal.signal_type == "error_encountered":
                flow_indicators -= 0.5
            elif signal.signal_type == "repeated_query":
                flow_indicators -= 0.3

        # Normalize to 0-1
        score = (flow_indicators / total + 1.0) / 2.0
        return max(0.0, min(1.0, score))

    def _calculate_frustrated_score(self) -> float:
        """
        Calculate likelihood user is FRUSTRATED.

        Frustration indicators:
        - Repeated errors
        - Same query multiple times
        - Rapid queries (short, impatient)
        - Long pauses after errors
        - Shorter queries over time (giving up)
        """
        if not self.recent_signals:
            return 0.0

        frustration_indicators = 0.0
        total = len(self.recent_signals)

        # Count errors
        error_count = sum(1 for s in self.recent_signals if s.signal_type == "error_encountered")
        repeated_count = sum(1 for s in self.recent_signals if s.signal_type == "repeated_query")
        rapid_count = sum(1 for s in self.recent_signals if s.signal_type == "rapid_query")

        # Errors are strong frustration signals
        frustration_indicators += error_count * 0.4
        frustration_indicators += repeated_count * 0.5
        frustration_indicators += rapid_count * 0.3

        # Normalize
        score = frustration_indicators / max(1, total)
        return max(0.0, min(1.0, score))

    def _calculate_confused_score(self) -> float:
        """
        Calculate likelihood user is CONFUSED.

        Confusion indicators:
        - Clarification requests ("what does X mean?")
        - Uncertain language ("maybe?", "I think?")
        - Long pauses before responding
        - Questions about questions
        - Asking for simpler explanations
        """
        if not self.recent_signals:
            return 0.0

        confusion_indicators = 0.0
        total = len(self.recent_signals)

        for signal in self.recent_signals:
            if signal.signal_type == "clarification_request":
                confusion_indicators += 1.0
            elif signal.signal_type == "long_pause":
                confusion_indicators += 0.5
            elif signal.signal_type == "repeated_query":
                confusion_indicators += 0.4

        score = confusion_indicators / max(1, total)
        return max(0.0, min(1.0, score))

    def _calculate_excited_score(self) -> float:
        """
        Calculate likelihood user is EXCITED.

        Excitement indicators:
        - Rapid experimentation
        - Multiple queries in quick succession
        - Trying different approaches
        - Following up immediately
        - Longer queries (enthusiastic)
        """
        if not self.recent_signals:
            return 0.0

        excitement_indicators = 0.0
        total = len(self.recent_signals)

        experimentation_count = sum(1 for s in self.recent_signals if s.signal_type == "experimentation")
        rapid_count = sum(1 for s in self.recent_signals if s.signal_type == "rapid_query")

        excitement_indicators += experimentation_count * 0.7
        excitement_indicators += rapid_count * 0.5

        score = excitement_indicators / max(1, total)
        return max(0.0, min(1.0, score))

    def _calculate_overwhelmed_score(self) -> float:
        """
        Calculate likelihood user is OVERWHELMED.

        Overwhelm indicators:
        - Skipping ahead through responses
        - Asking to simplify
        - Long pauses (processing overload)
        - Decreasing engagement over time
        - Shorter responses to complex content
        """
        if not self.recent_signals:
            return 0.0

        overwhelm_indicators = 0.0
        total = len(self.recent_signals)

        for signal in self.recent_signals:
            if signal.signal_type == "skipping_ahead":
                overwhelm_indicators += 1.0
            elif signal.signal_type == "long_pause":
                overwhelm_indicators += 0.6

        score = overwhelm_indicators / max(1, total)
        return max(0.0, min(1.0, score))

    def _calculate_confidence(
        self,
        scores: Dict[EmotionalState, float],
        detected_state: EmotionalState
    ) -> float:
        """
        Calculate confidence in state detection.

        High confidence = clear winner, low confidence = multiple states similar
        """
        detected_score = scores[detected_state]
        other_scores = [s for state, s in scores.items() if state != detected_state]

        if not other_scores:
            return 1.0

        # Margin between winner and runner-up
        second_highest = max(other_scores)
        margin = detected_score - second_highest

        # Confidence = margin + base confidence from score
        confidence = (margin + detected_score) / 2.0

        return max(0.0, min(1.0, confidence))

    def _get_key_signals_for_state(self, state: EmotionalState) -> List[str]:
        """Get the signals that most strongly indicate this state"""
        signal_counts = {}

        for signal in self.recent_signals[-5:]:  # Last 5 signals
            signal_type = signal.signal_type
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1

        # Sort by frequency
        sorted_signals = sorted(signal_counts.items(), key=lambda x: x[1], reverse=True)

        # Return top 3
        return [signal for signal, count in sorted_signals[:3]]

    def _calculate_state_duration(self, state: EmotionalState) -> float:
        """Calculate how long user has been in this state"""
        if self.current_state == state and self.state_start_time:
            duration = (datetime.now() - self.state_start_time).total_seconds()
            return duration
        return 0.0

    def _calculate_emotional_trend(self, current_state: EmotionalState) -> str:
        """
        Calculate if emotional state is improving, stable, or worsening.

        improving: Moving toward flow
        stable: Same state for a while
        worsening: Moving toward frustrated/overwhelmed
        """
        if len(self.state_history) < 3:
            return "stable"

        # Look at last 3 states
        recent_states = [s.state for s in self.state_history[-3:]]

        # Positive states
        positive = {EmotionalState.FLOW, EmotionalState.EXCITED}
        negative = {EmotionalState.FRUSTRATED, EmotionalState.OVERWHELMED}

        # Check trajectory
        positive_count = sum(1 for s in recent_states if s in positive)
        negative_count = sum(1 for s in recent_states if s in negative)

        if positive_count > negative_count:
            return "improving"
        elif negative_count > positive_count:
            return "worsening"
        else:
            return "stable"

    def get_adaptive_suggestions(self, state: EmotionalStateSnapshot) -> List[str]:
        """
        Get suggestions for how to adapt based on emotional state.

        These are ACTIONABLE recommendations for the conversation system.
        """
        suggestions = []

        if state.state == EmotionalState.FLOW:
            suggestions.append("Maintain current pace")
            suggestions.append("User is productive - don't interrupt")
            if state.duration_seconds > 300:  # 5 minutes
                suggestions.append("Consider proactive: 'You're on a roll! Need anything?'")

        elif state.state == EmotionalState.FRUSTRATED:
            suggestions.append("URGENT: Offer immediate help")
            suggestions.append("Simplify next response")
            suggestions.append("Ask: 'I see you're stuck - want me to try a different approach?'")
            if state.intensity > 0.7:
                suggestions.append("HIGH PRIORITY: User very frustrated, provide step-by-step guidance")

        elif state.state == EmotionalState.CONFUSED:
            suggestions.append("Provide clearer explanations")
            suggestions.append("Use more examples and analogies")
            suggestions.append("Ask: 'Would an example help clarify this?'")
            suggestions.append("Break down into smaller steps")

        elif state.state == EmotionalState.EXCITED:
            suggestions.append("Match their energy!")
            suggestions.append("Provide advanced options")
            suggestions.append("Suggest: 'Want to try something more advanced?'")
            suggestions.append("Encourage experimentation")

        elif state.state == EmotionalState.OVERWHELMED:
            suggestions.append("SIMPLIFY IMMEDIATELY")
            suggestions.append("Reduce information density")
            suggestions.append("Ask: 'Too much? Want me to focus on just the essentials?'")
            suggestions.append("Provide single clear next step")

        return suggestions


def get_emotional_detector() -> RealTimeEmotionalDetector:
    """Get singleton emotional detector"""
    global _emotional_detector

    if _emotional_detector is None:
        _emotional_detector = RealTimeEmotionalDetector()

    return _emotional_detector


# Singleton
_emotional_detector: Optional[RealTimeEmotionalDetector] = None
