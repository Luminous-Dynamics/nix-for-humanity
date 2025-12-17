"""
Core types for Predictive Intelligence System

Defines prediction types, confidence levels, and prediction structures.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


class PredictionType(Enum):
    """Types of predictions the system can make"""
    DEPENDENCY = "dependency"           # "You'll need package X"
    ERROR = "error"                     # "This will fail because Y"
    PATTERN = "pattern"                 # "You usually do Z next"
    CONFIGURATION = "configuration"     # "Consider setting A to B"
    NEXT_ACTION = "next_action"         # "Next likely action"
    MISSING_STEP = "missing_step"       # "You forgot to do X"


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = "very_high"      # >90% - Act automatically (if in autopilot mode)
    HIGH = "high"                # 75-90% - Strong suggestion
    MEDIUM = "medium"            # 50-75% - Gentle suggestion
    LOW = "low"                  # 25-50% - Mention as possibility
    VERY_LOW = "very_low"        # <25% - Don't show unless asked


@dataclass
class Prediction:
    """
    Base prediction structure

    All specific prediction types inherit from this.
    """
    prediction_type: PredictionType
    confidence: float                           # 0.0-1.0
    confidence_level: PredictionConfidence
    title: str                                  # Short description
    description: str                            # Detailed explanation
    evidence: List[str] = field(default_factory=list)  # Why we predict this
    suggested_action: Optional[str] = None      # What user should do
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Auto-set confidence level from confidence score"""
        if self.confidence >= 0.9:
            self.confidence_level = PredictionConfidence.VERY_HIGH
        elif self.confidence >= 0.75:
            self.confidence_level = PredictionConfidence.HIGH
        elif self.confidence >= 0.5:
            self.confidence_level = PredictionConfidence.MEDIUM
        elif self.confidence >= 0.25:
            self.confidence_level = PredictionConfidence.LOW
        else:
            self.confidence_level = PredictionConfidence.VERY_LOW

    def should_show(self, min_confidence: float = 0.5) -> bool:
        """Determine if prediction should be shown to user"""
        return self.confidence >= min_confidence

    def __str__(self) -> str:
        emoji = {
            PredictionConfidence.VERY_HIGH: "🎯",
            PredictionConfidence.HIGH: "✨",
            PredictionConfidence.MEDIUM: "💡",
            PredictionConfidence.LOW: "💭",
            PredictionConfidence.VERY_LOW: "🤔"
        }
        return f"{emoji[self.confidence_level]} {self.title} ({self.confidence:.0%} confident)"


@dataclass
class DependencyPrediction(Prediction):
    """
    Prediction about packages/dependencies you'll need

    Example: "You'll need docker-compose with docker"
    """
    package_name: str = ""              # Package name (required but needs default for dataclass)
    package_version: Optional[str] = None
    reason: str = ""                    # Why you need this
    related_packages: List[str] = field(default_factory=list)
    install_command: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        if not self.title:
            self.title = f"You'll likely need '{self.package_name}'"
        if not self.description:
            self.description = self.reason or f"Based on your current context, you'll need {self.package_name}"


@dataclass
class ErrorPrediction(Prediction):
    """
    Prediction about errors that will occur

    Example: "This build will fail because rust-analyzer is missing"
    """
    error_type: str = ""                # "missing_dependency", "config_error", etc.
    affected_operation: str = ""        # What will fail
    root_cause: str = ""                # Why it will fail
    prevention_steps: List[str] = field(default_factory=list)
    similar_past_errors: int = 0        # How many times we've seen this before

    def __post_init__(self):
        super().__post_init__()
        if not self.title:
            self.title = f"{self.affected_operation} will likely fail"
        if not self.description:
            self.description = f"Predicted failure: {self.root_cause}"


@dataclass
class PatternPrediction(Prediction):
    """
    Prediction based on learned workflow patterns

    Example: "You usually run tests after build"
    """
    pattern_name: str = ""              # "build_then_test", "commit_then_push", etc.
    pattern_frequency: float = 0.0      # How often user does this (0-1)
    last_step_observed: str = ""        # What user just did
    predicted_next_step: str = ""       # What they'll likely do next
    typical_delay_seconds: float = 0.0  # How long they usually wait

    def __post_init__(self):
        super().__post_init__()
        if not self.title:
            self.title = f"You usually '{self.predicted_next_step}' next"
        if not self.description:
            self.description = f"Based on your patterns, you typically {self.predicted_next_step} after {self.last_step_observed}"


@dataclass
class ConfigPrediction(Prediction):
    """
    Prediction about configuration changes

    Example: "Enable cachix for faster builds"
    """
    config_file: str = ""               # Which file to change
    config_key: str = ""                # What setting
    current_value: Any = None           # Current setting
    suggested_value: Any = None         # Recommended setting
    benefit: str = ""                   # Why change this
    risk_level: str = "low"             # "low", "medium", "high"

    def __post_init__(self):
        super().__post_init__()
        if not self.title:
            self.title = f"Consider setting {self.config_key} to {self.suggested_value}"
        if not self.description:
            self.description = f"Setting {self.config_key} to {self.suggested_value} will {self.benefit}"


@dataclass
class PredictionBatch:
    """
    Batch of predictions for current context

    Allows presenting multiple related predictions together.
    """
    predictions: List[Prediction] = field(default_factory=list)
    context_summary: str = ""
    generated_at: datetime = field(default_factory=datetime.now)

    def add(self, prediction: Prediction):
        """Add prediction to batch"""
        self.predictions.append(prediction)

    def filter_by_confidence(self, min_confidence: float = 0.5) -> List[Prediction]:
        """Get predictions above confidence threshold"""
        return [p for p in self.predictions if p.confidence >= min_confidence]

    def filter_by_type(self, prediction_type: PredictionType) -> List[Prediction]:
        """Get predictions of specific type"""
        return [p for p in self.predictions if p.prediction_type == prediction_type]

    def get_top_predictions(self, n: int = 5) -> List[Prediction]:
        """Get top N predictions by confidence"""
        sorted_predictions = sorted(self.predictions, key=lambda p: p.confidence, reverse=True)
        return sorted_predictions[:n]

    def __len__(self) -> int:
        return len(self.predictions)

    def __str__(self) -> str:
        high_confidence = len(self.filter_by_confidence(0.75))
        return f"PredictionBatch: {len(self.predictions)} predictions ({high_confidence} high confidence)"
