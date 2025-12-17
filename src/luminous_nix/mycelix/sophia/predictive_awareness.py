"""
Predictive Awareness Engine - Revolutionary Proactive Intelligence

The paradigm shift: Most AI is REACTIVE (you ask → it responds).
Sophia is PROACTIVE (she anticipates → offers help before you ask).

This engine predicts:
- What you'll want to do next
- Problems before they happen
- Optimal paths forward
- When to intervene proactively

Revolutionary because it creates genuine "she knows me" partnership.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from enum import Enum

from ..context import Context


class PredictionType(Enum):
    """Types of predictions we can make"""
    NEXT_ACTION = "next_action"              # What will they do next?
    POTENTIAL_PROBLEM = "potential_problem"  # What could go wrong?
    OPTIMAL_PATH = "optimal_path"            # Best way forward
    INTERVENTION_NEEDED = "intervention_needed"  # Should we help now?
    LEARNING_OPPORTUNITY = "learning_opportunity"  # Chance to teach


class InterventionTiming(Enum):
    """When should we intervene?"""
    IMMEDIATE = "immediate"        # Right now, before they struggle
    SOON = "soon"                 # In the next few actions
    WHEN_ASKED = "when_asked"     # Wait for explicit request
    NEVER = "never"               # Don't interrupt, just observe


class PredictionConfidence(Enum):
    """How confident are we in this prediction?"""
    VERY_HIGH = "very_high"    # 90%+ - Act on this
    HIGH = "high"              # 75-90% - Strongly suggest
    MODERATE = "moderate"      # 50-75% - Offer as option
    LOW = "low"                # 25-50% - Mention if relevant
    VERY_LOW = "very_low"      # <25% - Just observe


@dataclass
class Prediction:
    """A single prediction about what will happen or what's needed"""
    prediction_type: PredictionType
    description: str
    reasoning: str  # WHY we predict this
    confidence: float  # 0.0-1.0
    confidence_level: PredictionConfidence

    # What should we do about it?
    suggested_action: Optional[str]
    intervention_timing: InterventionTiming

    # Evidence supporting this prediction
    evidence: List[str]

    # Consequences if we don't act
    potential_impact: str

    # When this prediction was made
    timestamp: datetime


@dataclass
class ProactiveIntervention:
    """A proactive suggestion to help before being asked"""
    trigger: str  # What made us think to intervene?
    message: str  # What to tell the user
    action_offer: str  # What we can do to help

    # Why intervene NOW?
    timing_rationale: str
    urgency: InterventionTiming

    # What happens if they accept?
    expected_benefit: str

    # Confidence in our suggestion
    confidence: float


@dataclass
class WorkflowPattern:
    """A learned pattern in how this user works"""
    pattern_name: str
    description: str

    # The sequence we've observed
    typical_steps: List[str]
    current_step_index: int  # Where are we in this pattern?

    # How often this pattern occurs
    frequency: float  # 0.0-1.0
    last_seen: datetime

    # Success rate when following this pattern
    success_rate: float

    # What usually comes next?
    predicted_next_steps: List[Tuple[str, float]]  # (action, probability)


@dataclass
class PredictiveAnalysis:
    """Complete predictive analysis of current situation"""
    timestamp: datetime

    # Predictions we're making
    predictions: List[Prediction]

    # Should we intervene proactively?
    proactive_interventions: List[ProactiveIntervention]

    # Recognized workflow patterns
    active_workflows: List[WorkflowPattern]

    # What we predict will happen next (top 3)
    most_likely_next_actions: List[Tuple[str, float]]  # (action, probability)

    # Problems we're anticipating
    anticipated_problems: List[Prediction]

    # Overall predictive confidence
    overall_confidence: float


class PredictiveAwarenessEngine:
    """
    Revolutionary Predictive Awareness Engine

    The shift: From reactive AI to proactive partnership.

    Sophia learns YOUR patterns and anticipates YOUR needs:
    - Predicts next actions before you take them
    - Warns about problems before they happen
    - Suggests optimal paths based on your history
    - Intervenes proactively when it helps

    This creates genuine "she knows me" feeling.
    """

    def __init__(self):
        # Historical workflow patterns we've learned
        self.learned_workflows: Dict[str, WorkflowPattern] = {}

        # Predictions we've made (for learning)
        self.prediction_history: List[Prediction] = []

        # Success rate of our predictions
        self.prediction_accuracy: Dict[PredictionType, float] = {
            pt: 0.5 for pt in PredictionType
        }

        # Common action sequences (2-grams, 3-grams)
        self.action_sequences: Dict[Tuple[str, ...], List[str]] = {}

        # User's typical response to interventions
        self.intervention_acceptance_rate: float = 0.5

    def analyze_and_predict(
        self,
        context: Optional[Context] = None,
        recent_actions: Optional[List[str]] = None,
        current_time: Optional[datetime] = None
    ) -> PredictiveAnalysis:
        """
        Analyze current situation and make predictions

        The core of proactive intelligence - we look at where you are
        and predict where you're going, what you'll need, and when to help.

        Args:
            context: Current session context
            recent_actions: Recent actions taken
            current_time: Current time

        Returns:
            PredictiveAnalysis with all predictions and interventions
        """
        now = current_time or datetime.now()
        recent_actions = recent_actions or []

        # Recognize active workflow patterns
        active_workflows = self._recognize_active_workflows(recent_actions)

        # Predict next actions
        next_actions = self._predict_next_actions(
            context, recent_actions, active_workflows
        )

        # Anticipate potential problems
        anticipated_problems = self._anticipate_problems(
            context, recent_actions, next_actions
        )

        # Generate all predictions
        predictions = self._generate_predictions(
            context, recent_actions, active_workflows, next_actions
        )

        # Determine if we should intervene proactively
        interventions = self._determine_proactive_interventions(
            predictions, anticipated_problems, context
        )

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(predictions)

        analysis = PredictiveAnalysis(
            timestamp=now,
            predictions=predictions,
            proactive_interventions=interventions,
            active_workflows=active_workflows,
            most_likely_next_actions=next_actions,
            anticipated_problems=anticipated_problems,
            overall_confidence=overall_confidence
        )

        return analysis

    def _recognize_active_workflows(
        self,
        recent_actions: List[str]
    ) -> List[WorkflowPattern]:
        """Recognize which workflow patterns are currently active"""
        active = []

        # Check if recent actions match any learned workflows
        for workflow_name, workflow in self.learned_workflows.items():
            # See if recent actions match this workflow's typical steps
            match_score = self._calculate_workflow_match(
                recent_actions, workflow.typical_steps
            )

            if match_score > 0.6:  # 60% match threshold
                # Update current step index
                workflow.current_step_index = len(recent_actions) - 1
                active.append(workflow)

        return active

    def _calculate_workflow_match(
        self,
        recent_actions: List[str],
        workflow_steps: List[str]
    ) -> float:
        """Calculate how well recent actions match a workflow"""
        if not recent_actions or not workflow_steps:
            return 0.0

        # Simple substring matching for now
        matches = 0
        for action in recent_actions[-5:]:  # Last 5 actions
            for step in workflow_steps:
                if action.lower() in step.lower() or step.lower() in action.lower():
                    matches += 1
                    break

        return matches / min(len(recent_actions), 5)

    def _predict_next_actions(
        self,
        context: Optional[Context],
        recent_actions: List[str],
        active_workflows: List[WorkflowPattern]
    ) -> List[Tuple[str, float]]:
        """Predict the most likely next actions"""
        predictions = []

        # From active workflows
        for workflow in active_workflows:
            if workflow.predicted_next_steps:
                predictions.extend(workflow.predicted_next_steps[:2])

        # From action sequences (if we've learned patterns)
        if len(recent_actions) >= 2:
            last_two = tuple(recent_actions[-2:])
            if last_two in self.action_sequences:
                next_actions = self.action_sequences[last_two]
                for action in next_actions[:2]:
                    predictions.append((action, 0.6))

        # Default common next actions if we have no patterns yet
        if not predictions:
            predictions = [
                ("Continue current task", 0.5),
                ("Take a break", 0.3),
                ("Switch to another task", 0.2)
            ]

        # Sort by probability and return top 3
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:3]

    def _anticipate_problems(
        self,
        context: Optional[Context],
        recent_actions: List[str],
        next_actions: List[Tuple[str, float]]
    ) -> List[Prediction]:
        """Anticipate problems that might occur"""
        problems = []

        # Check for signs of potential issues

        # Problem: Repeating same failed action
        if len(recent_actions) >= 3:
            if recent_actions[-1] == recent_actions[-2] == recent_actions[-3]:
                problems.append(Prediction(
                    prediction_type=PredictionType.POTENTIAL_PROBLEM,
                    description="Repeated action pattern detected",
                    reasoning="We're repeating the same action - might be stuck",
                    confidence=0.75,
                    confidence_level=PredictionConfidence.HIGH,
                    suggested_action="Try a different approach",
                    intervention_timing=InterventionTiming.SOON,
                    evidence=[f"Action '{recent_actions[-1]}' repeated 3 times"],
                    potential_impact="Wasted time on ineffective approach",
                    timestamp=datetime.now()
                ))

        # Problem: Long session without break (if we had time data)
        # Problem: Complex action without testing (if we had context)

        return problems

    def _generate_predictions(
        self,
        context: Optional[Context],
        recent_actions: List[str],
        active_workflows: List[WorkflowPattern],
        next_actions: List[Tuple[str, float]]
    ) -> List[Prediction]:
        """Generate all types of predictions"""
        predictions = []

        # Next action predictions
        for action, probability in next_actions:
            confidence_level = self._probability_to_confidence(probability)

            predictions.append(Prediction(
                prediction_type=PredictionType.NEXT_ACTION,
                description=f"Likely next action: {action}",
                reasoning=f"Based on workflow patterns and recent history",
                confidence=probability,
                confidence_level=confidence_level,
                suggested_action=None,
                intervention_timing=InterventionTiming.WHEN_ASKED,
                evidence=[f"Pattern frequency: {probability:.0%}"],
                potential_impact="Helps us prepare optimal assistance",
                timestamp=datetime.now()
            ))

        # Learning opportunity predictions
        if len(recent_actions) > 5:
            predictions.append(Prediction(
                prediction_type=PredictionType.LEARNING_OPPORTUNITY,
                description="Good time to explain patterns we've noticed",
                reasoning="We've built enough context to share insights",
                confidence=0.7,
                confidence_level=PredictionConfidence.HIGH,
                suggested_action="Offer pattern reflection",
                intervention_timing=InterventionTiming.SOON,
                evidence=["Sufficient session context built"],
                potential_impact="Increased awareness of our working patterns",
                timestamp=datetime.now()
            ))

        return predictions

    def _determine_proactive_interventions(
        self,
        predictions: List[Prediction],
        anticipated_problems: List[Prediction],
        context: Optional[Context]
    ) -> List[ProactiveIntervention]:
        """Determine when and how to intervene proactively"""
        interventions = []

        # Intervene for high-confidence problems
        for problem in anticipated_problems:
            if problem.confidence > 0.7:
                interventions.append(ProactiveIntervention(
                    trigger=problem.description,
                    message=f"I noticed: {problem.reasoning}",
                    action_offer=problem.suggested_action or "Let me help",
                    timing_rationale="High confidence this will help",
                    urgency=problem.intervention_timing,
                    expected_benefit=f"Avoid: {problem.potential_impact}",
                    confidence=problem.confidence
                ))

        # Offer help for predicted next actions (if very confident)
        high_confidence_predictions = [
            p for p in predictions
            if p.prediction_type == PredictionType.NEXT_ACTION
            and p.confidence > 0.8
        ]

        for pred in high_confidence_predictions:
            interventions.append(ProactiveIntervention(
                trigger=pred.description,
                message=f"I predict you'll want to: {pred.description}",
                action_offer="Want me to prepare or check anything first?",
                timing_rationale="Very high confidence prediction",
                urgency=InterventionTiming.SOON,
                expected_benefit="Smooth path forward",
                confidence=pred.confidence
            ))

        return interventions

    def _calculate_overall_confidence(
        self,
        predictions: List[Prediction]
    ) -> float:
        """Calculate overall confidence in our predictions"""
        if not predictions:
            return 0.5

        # Average confidence weighted by prediction type importance
        weights = {
            PredictionType.NEXT_ACTION: 1.0,
            PredictionType.POTENTIAL_PROBLEM: 1.2,
            PredictionType.OPTIMAL_PATH: 1.0,
            PredictionType.INTERVENTION_NEEDED: 1.5,
            PredictionType.LEARNING_OPPORTUNITY: 0.8
        }

        total_weighted = 0.0
        total_weight = 0.0

        for pred in predictions:
            weight = weights.get(pred.prediction_type, 1.0)
            total_weighted += pred.confidence * weight
            total_weight += weight

        return total_weighted / total_weight if total_weight > 0 else 0.5

    def _probability_to_confidence(self, probability: float) -> PredictionConfidence:
        """Convert probability to confidence level"""
        if probability >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif probability >= 0.75:
            return PredictionConfidence.HIGH
        elif probability >= 0.5:
            return PredictionConfidence.MODERATE
        elif probability >= 0.25:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

    def learn_from_outcome(
        self,
        prediction: Prediction,
        actual_outcome: str,
        was_correct: bool
    ):
        """Learn from whether our prediction was correct"""
        # Update prediction accuracy for this type
        current_accuracy = self.prediction_accuracy[prediction.prediction_type]

        # Moving average with learning rate 0.1
        new_accuracy = current_accuracy * 0.9 + (1.0 if was_correct else 0.0) * 0.1
        self.prediction_accuracy[prediction.prediction_type] = new_accuracy

    def learn_workflow_pattern(
        self,
        pattern_name: str,
        steps: List[str],
        success: bool
    ):
        """Learn a new workflow pattern from observation"""
        if pattern_name in self.learned_workflows:
            # Update existing pattern
            workflow = self.learned_workflows[pattern_name]
            workflow.frequency = workflow.frequency * 0.9 + 0.1
            workflow.last_seen = datetime.now()

            # Update success rate
            old_success = workflow.success_rate
            workflow.success_rate = old_success * 0.9 + (1.0 if success else 0.0) * 0.1
        else:
            # Create new pattern
            self.learned_workflows[pattern_name] = WorkflowPattern(
                pattern_name=pattern_name,
                description=f"Workflow: {pattern_name}",
                typical_steps=steps,
                current_step_index=0,
                frequency=0.1,
                last_seen=datetime.now(),
                success_rate=1.0 if success else 0.0,
                predicted_next_steps=[]
            )

    def get_prediction_summary(self, analysis: PredictiveAnalysis) -> str:
        """Generate human-readable summary of predictions"""
        parts = ["🔮 Predictive Analysis:\n"]

        # Most likely next actions
        if analysis.most_likely_next_actions:
            parts.append("\n📍 Predicted Next Actions:")
            for action, prob in analysis.most_likely_next_actions:
                parts.append(f"  • {action} ({prob:.0%} confidence)")

        # Anticipated problems
        if analysis.anticipated_problems:
            parts.append("\n⚠️  Potential Issues:")
            for problem in analysis.anticipated_problems:
                parts.append(f"  • {problem.description}")

        # Proactive interventions
        if analysis.proactive_interventions:
            parts.append("\n💡 Proactive Suggestions:")
            for intervention in analysis.proactive_interventions:
                if intervention.urgency in [InterventionTiming.IMMEDIATE, InterventionTiming.SOON]:
                    parts.append(f"  • {intervention.message}")
                    parts.append(f"    {intervention.action_offer}")

        # Overall confidence
        parts.append(f"\n📊 Prediction Confidence: {analysis.overall_confidence:.0%}")

        return "\n".join(parts)


# Global singleton
_predictive_awareness_engine: Optional[PredictiveAwarenessEngine] = None


def get_predictive_awareness_engine() -> PredictiveAwarenessEngine:
    """Get the global predictive awareness engine singleton"""
    global _predictive_awareness_engine
    if _predictive_awareness_engine is None:
        _predictive_awareness_engine = PredictiveAwarenessEngine()
    return _predictive_awareness_engine
