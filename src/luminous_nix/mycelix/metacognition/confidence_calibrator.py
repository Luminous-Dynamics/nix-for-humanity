"""
Confidence Calibrator - Real Uncertainty Quantification

This is NOT a mock confidence score. This is genuine uncertainty estimation based on:
1. Response variance across agents (disagreement = uncertainty)
2. Historical accuracy on similar queries
3. Knowledge coverage (do we have relevant knowledge?)
4. Context quality (is the query clear and complete?)

The goal: Be HONEST about what we know vs don't know.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import math


@dataclass
class CalibrationResult:
    """Result of confidence calibration"""
    calibrated_confidence: float  # 0.0 to 1.0
    original_confidence: float  # What the agent(s) reported
    uncertainty_sources: Dict[str, float]  # What contributes to uncertainty
    should_defer: bool  # Should we admit "I don't know"?
    explanation: str  # Human-readable explanation
    suggestions: List[str] = field(default_factory=list)  # What to do about low confidence


class ConfidenceCalibrator:
    """
    Calibrates confidence scores based on multiple real factors

    Philosophy:
    - It's better to say "I don't know" than to be confidently wrong
    - Uncertainty is information, not a failure
    - Calibration improves with experience
    """

    def __init__(self):
        """Initialize confidence calibrator"""
        # Track historical accuracy by query type
        self.accuracy_history: Dict[str, List[Tuple[float, bool]]] = defaultdict(list)

        # Track knowledge coverage by domain
        self.knowledge_coverage: Dict[str, int] = defaultdict(int)

        # Calibration parameters (learned from experience)
        self.calibration_curve = {
            # Maps reported confidence to actual accuracy
            # Initially assumes perfect calibration
            0.5: 0.5,
            0.6: 0.6,
            0.7: 0.7,
            0.8: 0.8,
            0.9: 0.9,
            1.0: 1.0,
        }

        # Thresholds
        self.defer_threshold = 0.5  # Below this, say "I don't know"
        self.caution_threshold = 0.7  # Below this, add warnings

    def calibrate(
        self,
        agent_responses: List[Dict[str, Any]],
        query: str,
        query_type: Optional[str] = None,
        has_relevant_knowledge: bool = True,
        context_quality: float = 1.0,
    ) -> CalibrationResult:
        """
        Calibrate confidence based on real factors

        Args:
            agent_responses: Responses from agents (with their confidences)
            query: The user query
            query_type: Category of query (for historical accuracy)
            has_relevant_knowledge: Do we have knowledge about this?
            context_quality: How clear/complete is the context? (0-1)

        Returns:
            CalibrationResult with honest uncertainty estimate
        """
        # Extract agent confidences
        confidences = [r.get("confidence", 0.5) for r in agent_responses]

        if not confidences:
            # No agents responded - maximum uncertainty
            return CalibrationResult(
                calibrated_confidence=0.0,
                original_confidence=0.0,
                uncertainty_sources={"no_responses": 1.0},
                should_defer=True,
                explanation="No agents provided a response",
                suggestions=["Try rephrasing the query", "Check if the system is configured correctly"]
            )

        # Calculate base confidence (mean of agent confidences)
        mean_confidence = sum(confidences) / len(confidences)

        # Calculate uncertainty sources
        uncertainty_sources = {}

        # 1. Agent Disagreement
        if len(confidences) > 1:
            variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(confidences)
            std_dev = math.sqrt(variance)
            disagreement = std_dev / 0.5  # Normalize (max std_dev ~0.5)
            uncertainty_sources["agent_disagreement"] = disagreement
        else:
            disagreement = 0.0

        # 2. Historical Accuracy
        historical_accuracy = self._get_historical_accuracy(query_type)
        if historical_accuracy < 1.0:
            uncertainty_sources["historical_accuracy"] = 1.0 - historical_accuracy

        # 3. Knowledge Coverage
        if not has_relevant_knowledge:
            uncertainty_sources["missing_knowledge"] = 0.5

        # 4. Context Quality
        if context_quality < 1.0:
            uncertainty_sources["unclear_context"] = 1.0 - context_quality

        # Calculate calibrated confidence
        calibrated = mean_confidence

        # Adjust for disagreement (high disagreement = lower confidence)
        if disagreement > 0:
            calibrated *= (1 - disagreement * 0.3)  # Up to 30% reduction

        # Adjust for historical accuracy
        if historical_accuracy < 1.0:
            calibrated *= historical_accuracy

        # Adjust for knowledge coverage
        if not has_relevant_knowledge:
            calibrated *= 0.5  # Significant penalty

        # Adjust for context quality
        calibrated *= context_quality

        # Apply calibration curve (learned from experience)
        calibrated = self._apply_calibration_curve(calibrated)

        # Determine if we should defer
        should_defer = calibrated < self.defer_threshold

        # Generate explanation
        explanation = self._generate_explanation(
            calibrated, mean_confidence, uncertainty_sources, len(confidences)
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(
            calibrated, uncertainty_sources
        )

        return CalibrationResult(
            calibrated_confidence=calibrated,
            original_confidence=mean_confidence,
            uncertainty_sources=uncertainty_sources,
            should_defer=should_defer,
            explanation=explanation,
            suggestions=suggestions
        )

    def _get_historical_accuracy(self, query_type: Optional[str]) -> float:
        """Get historical accuracy for this query type"""
        if not query_type or query_type not in self.accuracy_history:
            return 0.8  # Default assumption

        history = self.accuracy_history[query_type]
        if not history:
            return 0.8

        # Calculate accuracy: weighted by confidence
        weighted_sum = sum(conf * (1.0 if correct else 0.0) for conf, correct in history)
        total_weight = sum(conf for conf, _ in history)

        if total_weight == 0:
            return 0.8

        return weighted_sum / total_weight

    def _apply_calibration_curve(self, confidence: float) -> float:
        """Apply learned calibration curve"""
        # Find closest points in calibration curve
        points = sorted(self.calibration_curve.items())

        for i, (x, y) in enumerate(points):
            if confidence <= x:
                if i == 0:
                    return y
                # Linear interpolation
                x0, y0 = points[i-1]
                x1, y1 = x, y
                t = (confidence - x0) / (x1 - x0)
                return y0 + t * (y1 - y0)

        return points[-1][1]

    def _generate_explanation(
        self,
        calibrated: float,
        original: float,
        sources: Dict[str, float],
        num_agents: int
    ) -> str:
        """Generate human-readable explanation of confidence"""
        if calibrated >= 0.9:
            base = "High confidence"
        elif calibrated >= 0.7:
            base = "Moderate confidence"
        elif calibrated >= 0.5:
            base = "Low confidence"
        else:
            base = "Very low confidence - uncertain about this"

        # Add context
        parts = [base]

        if abs(calibrated - original) > 0.1:
            if calibrated < original:
                parts.append(f"(adjusted down from {original:.0%})")
            else:
                parts.append(f"(adjusted up from {original:.0%})")

        # Explain main uncertainty sources
        if sources:
            top_source = max(sources.items(), key=lambda x: x[1])
            source_name = top_source[0].replace("_", " ")
            if top_source[1] > 0.2:
                parts.append(f"due to {source_name}")

        if num_agents > 1:
            parts.append(f"based on {num_agents} agents")

        return " ".join(parts) + "."

    def _generate_suggestions(
        self,
        confidence: float,
        sources: Dict[str, float]
    ) -> List[str]:
        """Generate suggestions for low confidence scenarios"""
        suggestions = []

        if confidence < self.defer_threshold:
            suggestions.append("Consider rephrasing the query for clarity")

        if "agent_disagreement" in sources and sources["agent_disagreement"] > 0.3:
            suggestions.append("Agents disagree - consider asking for multiple perspectives")

        if "missing_knowledge" in sources:
            suggestions.append("This may be outside my current knowledge - I can learn about it")

        if "unclear_context" in sources:
            suggestions.append("Provide more context or details")

        if confidence < self.caution_threshold:
            suggestions.append("Verify critical information before acting")

        return suggestions

    def record_outcome(
        self,
        query_type: str,
        reported_confidence: float,
        was_correct: bool
    ):
        """
        Record outcome for calibration learning

        Args:
            query_type: Category of query
            reported_confidence: What confidence we gave
            was_correct: Was our answer actually correct?
        """
        self.accuracy_history[query_type].append((reported_confidence, was_correct))

        # Limit history size
        if len(self.accuracy_history[query_type]) > 100:
            self.accuracy_history[query_type] = self.accuracy_history[query_type][-100:]

        # Update calibration curve (simple approach - could be more sophisticated)
        self._update_calibration_curve()

    def _update_calibration_curve(self):
        """Update calibration curve based on historical data"""
        # Group by confidence bins
        bins = defaultdict(list)

        for history in self.accuracy_history.values():
            for conf, correct in history:
                bin_key = round(conf * 10) / 10  # Round to nearest 0.1
                bins[bin_key].append(1.0 if correct else 0.0)

        # Update curve
        for bin_key, outcomes in bins.items():
            if len(outcomes) >= 5:  # Need enough data
                actual_accuracy = sum(outcomes) / len(outcomes)
                self.calibration_curve[bin_key] = actual_accuracy

    def get_calibration_stats(self) -> Dict[str, Any]:
        """Get calibration statistics"""
        total_records = sum(len(h) for h in self.accuracy_history.values())

        if total_records == 0:
            return {
                "total_records": 0,
                "overall_accuracy": 0.0,
                "calibration_error": 0.0,
                "query_types": 0
            }

        # Calculate overall accuracy
        all_outcomes = []
        for history in self.accuracy_history.values():
            all_outcomes.extend(history)

        overall_accuracy = sum(1.0 if c else 0.0 for _, c in all_outcomes) / len(all_outcomes)

        # Calculate calibration error (how far off are we?)
        calibration_error = 0.0
        for conf, correct in all_outcomes:
            predicted = conf
            actual = 1.0 if correct else 0.0
            calibration_error += abs(predicted - actual)
        calibration_error /= len(all_outcomes)

        return {
            "total_records": total_records,
            "overall_accuracy": overall_accuracy,
            "calibration_error": calibration_error,
            "query_types": len(self.accuracy_history),
            "calibration_curve": dict(self.calibration_curve)
        }
