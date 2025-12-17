"""
Predictive Intelligence System for Conscious Co-Pilot

Phase 2 of the Conscious Co-Pilot vision: The AI that predicts your needs
before you even ask.

Components:
- DependencyPredictor: Predicts what packages/tools you'll need
- ErrorForecaster: Predicts what will fail and why
- PatternCompleter: Learns and predicts your workflow patterns
- ConfigurationPredictor: Suggests configuration changes
- PredictionEngine: Orchestrates all predictors

Week 11-12 Implementation: Phase 2 of Conscious Co-Pilot Vision
"""

from .types import (
    Prediction,
    PredictionType,
    PredictionConfidence,
    DependencyPrediction,
    ErrorPrediction,
    PatternPrediction,
    ConfigPrediction,
    PredictionBatch,
)
from .dependency_predictor import DependencyPredictor, get_dependency_predictor
from .error_forecaster import ErrorForecaster, get_error_forecaster
from .pattern_completer import PatternCompleter, get_pattern_completer
from .config_predictor import ConfigurationPredictor, get_config_predictor
from .prediction_engine import PredictionEngine, get_prediction_engine

__all__ = [
    # Core types
    "Prediction",
    "PredictionType",
    "PredictionConfidence",
    "DependencyPrediction",
    "ErrorPrediction",
    "PatternPrediction",
    "ConfigPrediction",
    "PredictionBatch",

    # Predictors
    "DependencyPredictor",
    "ErrorForecaster",
    "PatternCompleter",
    "ConfigurationPredictor",

    # Predictor singletons
    "get_dependency_predictor",
    "get_error_forecaster",
    "get_pattern_completer",
    "get_config_predictor",

    # Engine
    "PredictionEngine",
    "get_prediction_engine",
]
