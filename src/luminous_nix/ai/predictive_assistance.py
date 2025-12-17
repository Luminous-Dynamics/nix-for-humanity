"""
Predictive Micro-Assistance - Layer 6 Component 3

Revolutionary capability: Help users BEFORE they ask for it.

Traditional AI: Waits for explicit questions
Revolutionary AI: Predicts needs and offers proactive help

Key innovations:
1. Context Prediction: Understand what user needs from context
2. Timing Intelligence: Know WHEN to offer help (not too early, not too late)
3. Micro-Interventions: Small, helpful nudges at perfect moments
4. Non-Intrusive: Suggestions feel natural, not pushy
5. Learning from Acceptance: Learn which predictions are helpful

This makes the AI feel like it's "reading your mind" - but it's reading patterns.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class PredictionType(Enum):
    """Types of predictions we can make"""
    NEEDS_SIMPLIFICATION = "needs_simplification"      # Too complex, simplify
    READY_FOR_ADVANCED = "ready_for_advanced"          # Can handle more
    STUCK_ON_ERROR = "stuck_on_error"                  # Stuck, needs help
    WANTS_ALTERNATIVES = "wants_alternatives"          # Exploring options
    READY_TO_MOVE_ON = "ready_to_move_on"             # Finished, what's next?
    NEEDS_BREAK = "needs_break"                        # Been working too long
    REPETITIVE_TASK = "repetitive_task"                # Could be automated
    MISSING_PREREQUISITE = "missing_prerequisite"      # Missing knowledge


class InterventionTiming(Enum):
    """When to intervene"""
    IMMEDIATE = "immediate"          # Right now (stuck, frustrated)
    SOON = "soon"                   # In 30-60 seconds
    WHEN_READY = "when_ready"       # When they finish current task
    NEXT_SESSION = "next_session"   # Remember for later
    NEVER = "never"                 # Don't intervene on this


@dataclass
class PredictedNeed:
    """A predicted user need"""
    prediction_type: PredictionType
    confidence: float              # 0.0-1.0 how sure we are
    timing: InterventionTiming     # When to intervene
    suggestion: str                # What to suggest
    context: Dict                  # Why we think this
    expires_at: Optional[str] = None  # When prediction becomes stale


@dataclass
class MicroIntervention:
    """A small, helpful intervention"""
    message: str                   # What to say
    actions: List[str]             # Possible actions user can take
    dismissible: bool = True       # Can user dismiss it?
    priority: int = 0              # 0=low, 1=medium, 2=high


class PredictiveAssistant:
    """
    Predicts user needs and offers proactive micro-assistance.

    Revolutionary features:
    - Predicts needs from behavioral patterns
    - Times interventions perfectly (not annoying)
    - Learns from user responses (accepted vs dismissed)
    - Non-intrusive suggestions
    - Context-aware predictions
    """

    def __init__(self):
        """Initialize predictive assistant"""
        self.active_predictions: List[PredictedNeed] = []
        self.prediction_history: List[PredictedNeed] = []
        self.intervention_history: List[Tuple[MicroIntervention, bool]] = []  # (intervention, accepted?)

        # Learning: track which predictions are helpful
        self.prediction_accuracy: Dict[PredictionType, float] = {}
        self.optimal_timing: Dict[PredictionType, float] = {}  # Seconds to wait

    def predict_needs(
        self,
        context: Dict
    ) -> List[PredictedNeed]:
        """
        Predict what user needs based on current context.

        Context should include:
        - current_task: What they're doing
        - emotional_state: How they're feeling
        - interaction_history: Recent interactions
        - time_on_task: How long they've been working
        - error_count: Recent errors
        - complexity_level: What they're attempting

        Returns:
            List of predicted needs with timing and suggestions
        """
        predictions = []

        # Check for simplification need
        if self._should_simplify(context):
            predictions.append(self._create_simplification_prediction(context))

        # Check for stuck state
        if self._is_stuck(context):
            predictions.append(self._create_stuck_prediction(context))

        # Check for advanced readiness
        if self._ready_for_advanced(context):
            predictions.append(self._create_advanced_prediction(context))

        # Check for alternative exploration
        if self._wants_alternatives(context):
            predictions.append(self._create_alternatives_prediction(context))

        # Check for repetitive work
        if self._has_repetitive_pattern(context):
            predictions.append(self._create_automation_prediction(context))

        # Check for break need
        if self._needs_break(context):
            predictions.append(self._create_break_prediction(context))

        # Check for missing prerequisite
        if self._missing_prerequisite(context):
            predictions.append(self._create_prerequisite_prediction(context))

        # Store predictions
        self.active_predictions = predictions
        self.prediction_history.extend(predictions)

        return predictions

    def _should_simplify(self, context: Dict) -> bool:
        """Should we suggest simplifying?"""
        emotional_state = context.get("emotional_state")
        complexity = context.get("complexity_level", 0)
        errors = context.get("error_count", 0)

        # Overwhelmed and dealing with complexity
        if emotional_state == "overwhelmed" and complexity > 0.7:
            return True

        # Multiple errors with complex task
        if errors >= 3 and complexity > 0.6:
            return True

        return False

    def _create_simplification_prediction(self, context: Dict) -> PredictedNeed:
        """Create prediction for simplification need"""
        return PredictedNeed(
            prediction_type=PredictionType.NEEDS_SIMPLIFICATION,
            confidence=0.8,
            timing=InterventionTiming.IMMEDIATE,
            suggestion="I notice this is getting complex. Want me to break it down into simpler steps?",
            context=context
        )

    def _is_stuck(self, context: Dict) -> bool:
        """Is user stuck?"""
        time_on_task = context.get("time_on_task_seconds", 0)
        errors = context.get("error_count", 0)
        emotional_state = context.get("emotional_state")
        repeated_attempts = context.get("repeated_attempts", 0)

        # Been working on same thing too long with errors
        if time_on_task > 180 and errors >= 2:  # 3 minutes with errors
            return True

        # Frustrated state
        if emotional_state == "frustrated":
            return True

        # Multiple repeated attempts
        if repeated_attempts >= 3:
            return True

        return False

    def _create_stuck_prediction(self, context: Dict) -> PredictedNeed:
        """Create prediction for stuck state"""
        return PredictedNeed(
            prediction_type=PredictionType.STUCK_ON_ERROR,
            confidence=0.9,
            timing=InterventionTiming.IMMEDIATE,
            suggestion="I see you're stuck. Want me to try a different approach or provide a working example?",
            context=context,
            expires_at=(datetime.now() + timedelta(seconds=30)).isoformat()
        )

    def _ready_for_advanced(self, context: Dict) -> bool:
        """Is user ready for advanced features?"""
        emotional_state = context.get("emotional_state")
        success_streak = context.get("consecutive_successes", 0)
        complexity = context.get("complexity_level", 0)

        # In flow with good success rate
        if emotional_state == "flow" and success_streak >= 3:
            return True

        # Excited and experimenting
        if emotional_state == "excited" and complexity < 0.5:
            return True

        return False

    def _create_advanced_prediction(self, context: Dict) -> PredictedNeed:
        """Create prediction for advanced readiness"""
        return PredictedNeed(
            prediction_type=PredictionType.READY_FOR_ADVANCED,
            confidence=0.7,
            timing=InterventionTiming.WHEN_READY,
            suggestion="You're doing great! Want to try something more advanced?",
            context=context
        )

    def _wants_alternatives(self, context: Dict) -> bool:
        """Does user want to explore alternatives?"""
        emotional_state = context.get("emotional_state")
        exploration_rate = context.get("exploration_rate", 0)
        asking_about_alternatives = context.get("asked_about_alternatives", False)

        if emotional_state == "excited" and exploration_rate > 0.5:
            return True

        if asking_about_alternatives:
            return True

        return False

    def _create_alternatives_prediction(self, context: Dict) -> PredictedNeed:
        """Create prediction for alternatives interest"""
        return PredictedNeed(
            prediction_type=PredictionType.WANTS_ALTERNATIVES,
            confidence=0.6,
            timing=InterventionTiming.SOON,
            suggestion="There are a few other ways to do this. Want to see the alternatives?",
            context=context
        )

    def _has_repetitive_pattern(self, context: Dict) -> bool:
        """Is user doing repetitive work?"""
        recent_commands = context.get("recent_commands", [])

        if len(recent_commands) < 3:
            return False

        # Check for repeated similar commands
        # Simple heuristic: same command with variations
        command_patterns = set()
        for cmd in recent_commands:
            # Extract command name (before first space)
            base_cmd = cmd.split()[0] if cmd else ""
            command_patterns.add(base_cmd)

        # If using same command repeatedly, might want automation
        if len(command_patterns) == 1 and len(recent_commands) >= 3:
            return True

        return False

    def _create_automation_prediction(self, context: Dict) -> PredictedNeed:
        """Create prediction for automation opportunity"""
        return PredictedNeed(
            prediction_type=PredictionType.REPETITIVE_TASK,
            confidence=0.75,
            timing=InterventionTiming.WHEN_READY,
            suggestion="I notice you're doing this repeatedly. Want me to show you how to automate it?",
            context=context
        )

    def _needs_break(self, context: Dict) -> bool:
        """Does user need a break?"""
        session_duration = context.get("session_duration_seconds", 0)
        emotional_state = context.get("emotional_state")
        errors_increasing = context.get("error_rate_increasing", False)

        # Long session with declining performance
        if session_duration > 3600 and errors_increasing:  # 1 hour
            return True

        # Overwhelmed state for extended time
        if emotional_state == "overwhelmed" and session_duration > 1800:  # 30 min
            return True

        return False

    def _create_break_prediction(self, context: Dict) -> PredictedNeed:
        """Create prediction for break need"""
        return PredictedNeed(
            prediction_type=PredictionType.NEEDS_BREAK,
            confidence=0.65,
            timing=InterventionTiming.WHEN_READY,
            suggestion="You've been at this for a while. Taking a short break often helps!",
            context=context
        )

    def _missing_prerequisite(self, context: Dict) -> bool:
        """Is user missing prerequisite knowledge?"""
        complexity = context.get("complexity_level", 0)
        user_level = context.get("user_technical_level", 0)
        confusion_signals = context.get("confusion_signals", 0)

        # Attempting advanced task at beginner level
        if complexity > 0.7 and user_level < 0.3:
            return True

        # Multiple confusion signals
        if confusion_signals >= 3:
            return True

        return False

    def _create_prerequisite_prediction(self, context: Dict) -> PredictedNeed:
        """Create prediction for missing prerequisite"""
        return PredictedNeed(
            prediction_type=PredictionType.MISSING_PREREQUISITE,
            confidence=0.7,
            timing=InterventionTiming.SOON,
            suggestion="This builds on some concepts we haven't covered. Want a quick primer first?",
            context=context
        )

    def get_ready_interventions(self) -> List[MicroIntervention]:
        """
        Get interventions that are ready to show now.

        Filters predictions by timing and creates micro-interventions.
        """
        now = datetime.now()
        interventions = []

        for prediction in self.active_predictions:
            # Check if expired
            if prediction.expires_at:
                expire_time = datetime.fromisoformat(prediction.expires_at)
                if now > expire_time:
                    continue

            # Check timing
            if prediction.timing == InterventionTiming.IMMEDIATE:
                intervention = self._create_intervention(prediction)
                interventions.append(intervention)

            elif prediction.timing == InterventionTiming.SOON:
                # Show soon-timing predictions with lower priority
                intervention = self._create_intervention(prediction)
                intervention.priority = 0  # Low priority
                interventions.append(intervention)

        # Sort by priority
        interventions.sort(key=lambda i: i.priority, reverse=True)

        return interventions

    def _create_intervention(self, prediction: PredictedNeed) -> MicroIntervention:
        """Create micro-intervention from prediction"""
        # Determine priority
        priority = 0
        if prediction.timing == InterventionTiming.IMMEDIATE:
            priority = 2  # High
        elif prediction.prediction_type in [PredictionType.STUCK_ON_ERROR, PredictionType.NEEDS_SIMPLIFICATION]:
            priority = 2  # High
        elif prediction.prediction_type in [PredictionType.NEEDS_BREAK]:
            priority = 0  # Low

        # Generate possible actions
        actions = self._generate_actions(prediction)

        return MicroIntervention(
            message=prediction.suggestion,
            actions=actions,
            dismissible=True,
            priority=priority
        )

    def _generate_actions(self, prediction: PredictedNeed) -> List[str]:
        """Generate actionable options for user"""
        actions = []

        if prediction.prediction_type == PredictionType.STUCK_ON_ERROR:
            actions = [
                "Show me a working example",
                "Try a different approach",
                "Break it down step-by-step"
            ]
        elif prediction.prediction_type == PredictionType.NEEDS_SIMPLIFICATION:
            actions = [
                "Simplify this for me",
                "Show just the essentials",
                "I can handle it"
            ]
        elif prediction.prediction_type == PredictionType.READY_FOR_ADVANCED:
            actions = [
                "Show me advanced features",
                "Teach me more",
                "Not now"
            ]
        elif prediction.prediction_type == PredictionType.WANTS_ALTERNATIVES:
            actions = [
                "Yes, show alternatives",
                "Not now"
            ]
        elif prediction.prediction_type == PredictionType.REPETITIVE_TASK:
            actions = [
                "Show me how to automate",
                "Create a script for this",
                "I prefer doing it manually"
            ]
        elif prediction.prediction_type == PredictionType.MISSING_PREREQUISITE:
            actions = [
                "Yes, teach me the basics first",
                "Show me a primer",
                "I'll figure it out"
            ]

        return actions

    def record_intervention_response(
        self,
        intervention: MicroIntervention,
        accepted: bool,
        action_taken: Optional[str] = None
    ):
        """
        Record how user responded to intervention.

        This helps us learn which predictions are helpful.
        """
        self.intervention_history.append((intervention, accepted))

        # Update accuracy metrics
        # (In production, this would use more sophisticated learning)

    def get_intervention_effectiveness(self) -> Dict[str, float]:
        """Get effectiveness metrics for interventions"""
        if not self.intervention_history:
            return {}

        total = len(self.intervention_history)
        accepted = sum(1 for _, acc in self.intervention_history if acc)

        return {
            "total_interventions": total,
            "acceptance_rate": accepted / total if total > 0 else 0.0,
            "effectiveness": accepted / total if total > 0 else 0.0
        }


def get_predictive_assistant() -> PredictiveAssistant:
    """Get singleton predictive assistant"""
    global _predictive_assistant

    if _predictive_assistant is None:
        _predictive_assistant = PredictiveAssistant()

    return _predictive_assistant


# Singleton
_predictive_assistant: Optional[PredictiveAssistant] = None
