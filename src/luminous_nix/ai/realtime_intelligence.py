"""
Real-Time Intelligence Integration - Layer 6

Integrates all three revolutionary real-time systems:
1. Emotional Intelligence - Detect emotional state
2. Dynamic Response Adaptation - Adapt responses while being consumed
3. Predictive Assistance - Help before being asked

This creates an AI that feels like it's "reading your mind" - understanding
you in THIS MOMENT and adapting everything in real-time.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .emotional_intelligence import (
    RealTimeEmotionalDetector, EmotionalSignal, EmotionalState,
    EmotionalStateSnapshot, get_emotional_detector
)
from .dynamic_response_adapter import (
    DynamicResponseAdapter, ConsumptionSignal, ConsumptionPattern,
    AdaptiveResponse, ResponseSection, get_response_adapter
)
from .predictive_assistance import (
    PredictiveAssistant, PredictedNeed, MicroIntervention,
    InterventionTiming, get_predictive_assistant
)


@dataclass
class RealTimeContext:
    """
    Complete real-time context about the interaction.

    This combines emotional state, consumption patterns, and predictions.
    """
    # Emotional state
    emotional_state: EmotionalStateSnapshot

    # Response consumption
    consumption_pattern: Optional[ConsumptionPattern]
    active_response: Optional[AdaptiveResponse]

    # Predictions
    predicted_needs: List[PredictedNeed]
    ready_interventions: List[MicroIntervention]

    # Meta
    timestamp: str
    session_duration_seconds: float


class RealTimeIntelligence:
    """
    Unified real-time intelligence system.

    This integrates:
    - Emotional detection (HOW you feel)
    - Response adaptation (HOW you consume)
    - Predictive assistance (WHAT you need)

    Revolutionary features:
    - Understands you IN THIS MOMENT
    - Adapts DURING interaction, not after
    - Predicts needs BEFORE you ask
    - Non-intrusive, natural assistance
    - Learns from every interaction
    """

    def __init__(self):
        """Initialize real-time intelligence"""
        self.emotional_detector = get_emotional_detector()
        self.response_adapter = get_response_adapter()
        self.predictive_assistant = get_predictive_assistant()

        # Session tracking
        self.session_start = datetime.now()
        self.interaction_count = 0

    def record_interaction(
        self,
        query: str,
        response: str,
        response_time_ms: float = 0.0,
        reading_time_ms: float = 0.0,
        user_action: Optional[str] = None,
        error_occurred: bool = False
    ):
        """
        Record a complete interaction.

        This updates all three real-time systems.

        Args:
            query: User's query
            response: System's response
            response_time_ms: Time user took to respond
            reading_time_ms: Time spent reading response
            user_action: What user did (executed, skipped, etc.)
            error_occurred: Did an error happen?
        """
        timestamp = datetime.now().isoformat()
        self.interaction_count += 1

        # === Update Emotional State ===
        self._record_emotional_signals(
            query, response_time_ms, reading_time_ms,
            user_action, error_occurred, timestamp
        )

        # === Update Response Consumption ===
        self._record_consumption_signals(
            reading_time_ms, user_action, timestamp
        )

    def get_realtime_context(self) -> RealTimeContext:
        """
        Get complete real-time context about current state.

        This is the GOLD - all intelligence in one place.

        Returns:
            Complete real-time context
        """
        # Get emotional state
        emotional_state = self.emotional_detector.detect_current_state()

        # Get consumption pattern
        consumption_pattern = None
        if self.response_adapter.consumption_signals:
            consumption_pattern = self.response_adapter._detect_consumption_pattern()

        # Get active response
        active_response = self.response_adapter.current_response

        # Predict needs
        prediction_context = self._build_prediction_context(emotional_state)
        predicted_needs = self.predictive_assistant.predict_needs(prediction_context)

        # Get ready interventions
        ready_interventions = self.predictive_assistant.get_ready_interventions()

        # Calculate session duration
        session_duration = (datetime.now() - self.session_start).total_seconds()

        return RealTimeContext(
            emotional_state=emotional_state,
            consumption_pattern=consumption_pattern,
            active_response=active_response,
            predicted_needs=predicted_needs,
            ready_interventions=ready_interventions,
            timestamp=datetime.now().isoformat(),
            session_duration_seconds=session_duration
        )

    def create_adaptive_response(
        self,
        content: Dict[ResponseSection, str]
    ) -> AdaptiveResponse:
        """
        Create a response that adapts in real-time.

        This uses current emotional state and consumption patterns.

        Args:
            content: Response sections

        Returns:
            Adaptive response ready for real-time adjustment
        """
        # Get current context
        context = self.get_realtime_context()

        # Determine initial consumption pattern from emotional state
        initial_pattern = self._predict_initial_consumption(context.emotional_state)

        # Create adaptive response
        response = self.response_adapter.create_adaptive_response(
            content,
            initial_consumption_pattern=initial_pattern
        )

        return response

    def get_proactive_help(self) -> Optional[MicroIntervention]:
        """
        Get proactive help intervention if needed.

        This is the "mind reading" - offering help at perfect moment.

        Returns:
            Intervention if needed, None otherwise
        """
        interventions = self.predictive_assistant.get_ready_interventions()

        if not interventions:
            return None

        # Return highest priority intervention
        return interventions[0]

    def should_adapt_mid_response(self) -> bool:
        """
        Should we adapt the response mid-stream?

        Checks if user's consumption pattern suggests adaptation.

        Returns:
            True if response should be adapted now
        """
        if not self.response_adapter.consumption_signals:
            return False

        # Check for strong consumption pattern
        pattern = self.response_adapter._detect_consumption_pattern()

        # Adapt if skimming or jumping to code
        if pattern in [ConsumptionPattern.SKIMMING, ConsumptionPattern.JUMPING_TO_CODE]:
            return True

        # Check for confusion signals
        clarification = self.response_adapter.should_interrupt_with_clarification()
        if clarification:
            return True

        return False

    def get_adaptive_suggestions(self) -> List[str]:
        """
        Get suggestions for how to adapt based on ALL real-time intelligence.

        Combines emotional state, consumption, and predictions.

        Returns:
            List of actionable suggestions
        """
        context = self.get_realtime_context()
        suggestions = []

        # Add emotional state suggestions
        emotional_suggestions = self.emotional_detector.get_adaptive_suggestions(
            context.emotional_state
        )
        suggestions.extend(emotional_suggestions)

        # Add consumption-based suggestions
        if context.consumption_pattern == ConsumptionPattern.SKIMMING:
            suggestions.append("User skimming - collapse detailed sections")
        elif context.consumption_pattern == ConsumptionPattern.JUMPING_TO_CODE:
            suggestions.append("User wants code - prioritize code blocks")

        # Add predicted need suggestions
        for need in context.predicted_needs:
            if need.timing == InterventionTiming.IMMEDIATE:
                suggestions.append(f"URGENT: {need.suggestion}")

        return suggestions

    def get_intelligence_dashboard(self) -> Dict:
        """
        Get complete intelligence dashboard.

        Shows everything the real-time intelligence knows.

        Returns:
            Complete dashboard data
        """
        context = self.get_realtime_context()

        return {
            "emotional_state": {
                "state": context.emotional_state.state.value,
                "confidence": context.emotional_state.confidence,
                "intensity": context.emotional_state.intensity,
                "duration": context.emotional_state.duration_seconds,
                "trend": context.emotional_state.trend,
                "key_signals": context.emotional_state.key_signals
            },
            "consumption": {
                "pattern": context.consumption_pattern.value if context.consumption_pattern else None,
                "signals_count": len(self.response_adapter.consumption_signals)
            },
            "predictions": {
                "predicted_needs": [
                    {
                        "type": need.prediction_type.value,
                        "confidence": need.confidence,
                        "timing": need.timing.value,
                        "suggestion": need.suggestion
                    }
                    for need in context.predicted_needs
                ],
                "ready_interventions": [
                    {
                        "message": intervention.message,
                        "actions": intervention.actions,
                        "priority": intervention.priority
                    }
                    for intervention in context.ready_interventions
                ]
            },
            "session": {
                "duration_seconds": context.session_duration_seconds,
                "interactions": self.interaction_count
            },
            "adaptive_suggestions": self.get_adaptive_suggestions()
        }

    def _record_emotional_signals(
        self,
        query: str,
        response_time_ms: float,
        reading_time_ms: float,
        user_action: Optional[str],
        error_occurred: bool,
        timestamp: str
    ):
        """Record emotional signals from interaction"""
        signals = []

        # Detect rapid queries (frustration or excitement)
        if len(query) < 20 and response_time_ms < 2000:
            signals.append(EmotionalSignal(
                timestamp=timestamp,
                signal_type="rapid_query",
                intensity=0.7
            ))

        # Error signals
        if error_occurred:
            signals.append(EmotionalSignal(
                timestamp=timestamp,
                signal_type="error_encountered",
                intensity=0.8
            ))

        # Reading signals
        if reading_time_ms > 5000:  # Read fully
            signals.append(EmotionalSignal(
                timestamp=timestamp,
                signal_type="reading_fully",
                intensity=0.6
            ))
        elif reading_time_ms < 1000:  # Skipped
            signals.append(EmotionalSignal(
                timestamp=timestamp,
                signal_type="skipping_ahead",
                intensity=0.5
            ))

        # Action signals
        if user_action == "executed":
            signals.append(EmotionalSignal(
                timestamp=timestamp,
                signal_type="copy_paste",
                intensity=0.7
            ))
        elif user_action == "asked_clarification":
            signals.append(EmotionalSignal(
                timestamp=timestamp,
                signal_type="clarification_request",
                intensity=0.8
            ))
        elif user_action == "experimentation":
            signals.append(EmotionalSignal(
                timestamp=timestamp,
                signal_type="experimentation",
                intensity=0.6
            ))

        # Record all signals
        for signal in signals:
            self.emotional_detector.record_signal(signal)

    def _record_consumption_signals(
        self,
        reading_time_ms: float,
        user_action: Optional[str],
        timestamp: str
    ):
        """Record consumption signals from interaction"""
        signals = []

        # Reading behavior
        if reading_time_ms > 5000:
            signals.append(ConsumptionSignal(
                timestamp=timestamp,
                signal_type="reading_fully",
                time_spent_ms=reading_time_ms
            ))
        elif reading_time_ms < 1000:
            signals.append(ConsumptionSignal(
                timestamp=timestamp,
                signal_type="scrolled_fast",
                time_spent_ms=reading_time_ms
            ))

        # Action signals
        if user_action == "executed":
            signals.append(ConsumptionSignal(
                timestamp=timestamp,
                signal_type="copied_code",
                section=ResponseSection.CODE
            ))

        # Record signals
        for signal in signals:
            self.response_adapter.record_consumption_signal(signal)

    def _build_prediction_context(
        self,
        emotional_state: EmotionalStateSnapshot
    ) -> Dict:
        """Build context for predictive assistant"""
        return {
            "emotional_state": emotional_state.state.value,
            "session_duration_seconds": (datetime.now() - self.session_start).total_seconds(),
            "interaction_count": self.interaction_count,
            "error_count": sum(
                1 for signal in self.emotional_detector.recent_signals
                if signal.signal_type == "error_encountered"
            ),
            "confusion_signals": sum(
                1 for signal in self.emotional_detector.recent_signals
                if signal.signal_type == "clarification_request"
            ),
            "complexity_level": 0.5,  # Would be calculated from actual task
            "user_technical_level": 0.5,  # From user profile
            "exploration_rate": 0.0,  # Would be calculated
            "repeated_attempts": 0,  # Would be tracked
            "consecutive_successes": 0,  # Would be tracked
            "error_rate_increasing": False,  # Would be calculated
            "recent_commands": [],  # Would be tracked
            "asked_about_alternatives": False  # Would be detected from queries
        }

    def _predict_initial_consumption(
        self,
        emotional_state: EmotionalStateSnapshot
    ) -> Optional[ConsumptionPattern]:
        """Predict how user will consume response based on emotional state"""
        state = emotional_state.state

        if state == EmotionalState.FRUSTRATED:
            return ConsumptionPattern.SKIMMING  # Just want solution
        elif state == EmotionalState.EXCITED:
            return ConsumptionPattern.JUMPING_TO_CODE  # Want to try it
        elif state == EmotionalState.FLOW:
            return ConsumptionPattern.READING_FULLY  # Engaged
        elif state == EmotionalState.OVERWHELMED:
            return ConsumptionPattern.SKIMMING  # Too much
        elif state == EmotionalState.CONFUSED:
            return ConsumptionPattern.PAUSED  # Processing

        return None


def get_realtime_intelligence() -> RealTimeIntelligence:
    """Get singleton real-time intelligence"""
    global _realtime_intelligence

    if _realtime_intelligence is None:
        _realtime_intelligence = RealTimeIntelligence()

    return _realtime_intelligence


# Singleton
_realtime_intelligence: Optional[RealTimeIntelligence] = None
