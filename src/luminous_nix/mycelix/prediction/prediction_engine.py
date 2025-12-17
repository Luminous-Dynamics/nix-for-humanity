"""
Prediction Engine - Orchestrates all predictors

Main interface for the Predictive Intelligence System.

Usage:
    engine = get_prediction_engine()
    predictions = engine.predict_all()

    # Filter high-confidence predictions
    important = predictions.filter_by_confidence(0.75)

    # Get top 3 predictions
    top_3 = predictions.get_top_predictions(3)
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..context import get_context_engine, Context
from .types import (
    Prediction,
    PredictionType,
    PredictionBatch,
    DependencyPrediction,
    ErrorPrediction,
    PatternPrediction,
    ConfigPrediction,
)
from .dependency_predictor import get_dependency_predictor
from .error_forecaster import get_error_forecaster
from .pattern_completer import get_pattern_completer
from .config_predictor import get_config_predictor

logger = logging.getLogger(__name__)


class PredictionEngine:
    """
    Orchestrates all prediction systems

    Combines predictions from:
    - DependencyPredictor
    - ErrorForecaster
    - PatternCompleter
    - ConfigurationPredictor

    Provides unified interface for getting predictions.
    """

    def __init__(self):
        """Initialize the prediction engine"""
        self.context_engine = get_context_engine()

        # Initialize all predictors
        self.dependency_predictor = get_dependency_predictor()
        self.error_forecaster = get_error_forecaster()
        self.pattern_completer = get_pattern_completer()
        self.config_predictor = get_config_predictor()

        # Stats
        self.total_predictions_made = 0
        self.predictions_by_type: Dict[PredictionType, int] = {}
        self.prediction_accuracy: Dict[str, float] = {}

        logger.info("🔮 Prediction Engine initialized")

    def predict_all(
        self,
        context: Optional[Context] = None,
        min_confidence: float = 0.5,
    ) -> PredictionBatch:
        """
        Get all predictions from all predictors

        Args:
            context: Optional context (uses current if None)
            min_confidence: Minimum confidence threshold

        Returns:
            PredictionBatch with all predictions
        """
        if context is None:
            context = self.context_engine.get_current_context()

        # Collect predictions from all sources
        all_predictions = PredictionBatch(
            context_summary=f"Predictions for {context.primary_project} project"
        )

        # Get predictions from each predictor
        try:
            dep_predictions = self.dependency_predictor.predict(context)
            all_predictions.predictions.extend(dep_predictions.predictions)
        except Exception as e:
            logger.error(f"Dependency prediction failed: {e}")

        try:
            error_predictions = self.error_forecaster.predict(context)
            all_predictions.predictions.extend(error_predictions.predictions)
        except Exception as e:
            logger.error(f"Error forecasting failed: {e}")

        try:
            pattern_predictions = self.pattern_completer.predict(context)
            all_predictions.predictions.extend(pattern_predictions.predictions)
        except Exception as e:
            logger.error(f"Pattern completion failed: {e}")

        try:
            config_predictions = self.config_predictor.predict(context)
            all_predictions.predictions.extend(config_predictions.predictions)
        except Exception as e:
            logger.error(f"Config prediction failed: {e}")

        # Filter by confidence
        filtered = all_predictions.filter_by_confidence(min_confidence)
        final_batch = PredictionBatch(
            predictions=filtered,
            context_summary=all_predictions.context_summary
        )

        # Update stats
        self.total_predictions_made += len(final_batch.predictions)
        for pred in final_batch.predictions:
            self.predictions_by_type[pred.prediction_type] = \
                self.predictions_by_type.get(pred.prediction_type, 0) + 1

        return final_batch

    def predict_dependencies(
        self,
        context: Optional[Context] = None
    ) -> PredictionBatch:
        """Get only dependency predictions"""
        predictions = self.predict_all(context)
        return PredictionBatch(
            predictions=predictions.filter_by_type(PredictionType.DEPENDENCY),
            context_summary="Dependency predictions"
        )

    def predict_errors(
        self,
        context: Optional[Context] = None
    ) -> PredictionBatch:
        """Get only error predictions"""
        predictions = self.predict_all(context)
        return PredictionBatch(
            predictions=predictions.filter_by_type(PredictionType.ERROR),
            context_summary="Error predictions"
        )

    def predict_patterns(
        self,
        context: Optional[Context] = None
    ) -> PredictionBatch:
        """Get only pattern predictions"""
        predictions = self.predict_all(context)
        return PredictionBatch(
            predictions=predictions.filter_by_type(PredictionType.PATTERN),
            context_summary="Pattern predictions"
        )

    def predict_configs(
        self,
        context: Optional[Context] = None
    ) -> PredictionBatch:
        """Get only configuration predictions"""
        predictions = self.predict_all(context)
        return PredictionBatch(
            predictions=predictions.filter_by_type(PredictionType.CONFIGURATION),
            context_summary="Configuration predictions"
        )

    def get_top_predictions(
        self,
        n: int = 5,
        context: Optional[Context] = None
    ) -> List[Prediction]:
        """
        Get top N predictions across all types

        Args:
            n: Number of predictions to return
            context: Optional context

        Returns:
            List of top predictions sorted by confidence
        """
        predictions = self.predict_all(context)
        return predictions.get_top_predictions(n)

    def predict_next_action(
        self,
        context: Optional[Context] = None
    ) -> Optional[Prediction]:
        """
        Get single best prediction for next action

        Returns the highest-confidence prediction or None.
        """
        top = self.get_top_predictions(n=1, context=context)
        return top[0] if top else None

    def explain_prediction(self, prediction: Prediction) -> str:
        """
        Generate human-readable explanation for a prediction

        Args:
            prediction: The prediction to explain

        Returns:
            Formatted explanation string
        """
        explanation = f"### {prediction.title}\n\n"
        explanation += f"**Type**: {prediction.prediction_type.value}\n"
        explanation += f"**Confidence**: {prediction.confidence:.0%}\n\n"
        explanation += f"{prediction.description}\n\n"

        if prediction.evidence:
            explanation += "**Evidence**:\n"
            for evidence in prediction.evidence:
                explanation += f"- {evidence}\n"

        if prediction.suggested_action:
            explanation += f"\n**Suggested Action**:\n{prediction.suggested_action}\n"

        # Type-specific details
        if isinstance(prediction, DependencyPrediction):
            explanation += f"\n**Package**: {prediction.package_name}\n"
            if prediction.install_command:
                explanation += f"**Install**: `{prediction.install_command}`\n"

        elif isinstance(prediction, ErrorPrediction):
            explanation += f"\n**Error Type**: {prediction.error_type}\n"
            if prediction.prevention_steps:
                explanation += "**Prevention**:\n"
                for step in prediction.prevention_steps:
                    explanation += f"- {step}\n"

        elif isinstance(prediction, PatternPrediction):
            explanation += f"\n**Pattern**: {prediction.pattern_name}\n"
            explanation += f"**Frequency**: {prediction.pattern_frequency:.0%}\n"

        elif isinstance(prediction, ConfigPrediction):
            explanation += f"\n**Config File**: {prediction.config_file}\n"
            explanation += f"**Setting**: {prediction.config_key}\n"
            explanation += f"**Risk Level**: {prediction.risk_level}\n"

        return explanation

    def get_statistics(self) -> Dict:
        """Get prediction engine statistics"""
        return {
            "total_predictions": self.total_predictions_made,
            "predictions_by_type": dict(self.predictions_by_type),
            "predictors_active": 4,
            "dependency_predictor_stats": self.dependency_predictor.__dict__,
            "pattern_stats": self.pattern_completer.get_pattern_statistics(),
        }

    def format_predictions_for_display(
        self,
        predictions: PredictionBatch,
        max_display: int = 10
    ) -> str:
        """
        Format predictions for terminal display

        Args:
            predictions: Batch of predictions
            max_display: Maximum predictions to show

        Returns:
            Formatted string for display
        """
        if len(predictions) == 0:
            return "No predictions available.\n"

        output = f"\n🔮 Predictions ({len(predictions)} total)\n"
        output += "=" * 70 + "\n\n"

        top = predictions.get_top_predictions(max_display)

        for i, pred in enumerate(top, 1):
            output += f"{i}. {pred}\n"
            output += f"   {pred.description}\n"

            if pred.suggested_action:
                output += f"   💡 {pred.suggested_action}\n"

            output += "\n"

        if len(predictions) > max_display:
            remaining = len(predictions) - max_display
            output += f"... and {remaining} more predictions\n"

        return output


# Global instance
_prediction_engine: Optional[PredictionEngine] = None


def get_prediction_engine() -> PredictionEngine:
    """Get or create global prediction engine"""
    global _prediction_engine

    if _prediction_engine is None:
        _prediction_engine = PredictionEngine()
        logger.info("🔮 Global prediction engine created")

    return _prediction_engine


# Example usage
if __name__ == "__main__":
    # Create engine
    engine = get_prediction_engine()

    # Get all predictions
    print("Getting all predictions...\n")
    predictions = engine.predict_all(min_confidence=0.5)

    # Display
    print(engine.format_predictions_for_display(predictions))

    # Get top 3
    print("\nTop 3 Predictions:")
    print("=" * 70)
    for pred in engine.get_top_predictions(3):
        print(f"\n{pred}")
        print(engine.explain_prediction(pred))

    # Stats
    print("\nEngine Statistics:")
    print("=" * 70)
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
