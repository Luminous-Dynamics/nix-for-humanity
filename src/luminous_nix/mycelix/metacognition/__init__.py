"""
Metacognitive Intelligence Layer

This module implements genuine self-awareness and metacognition:
- Confidence calibration (real uncertainty quantification)
- Explanation generation (full reasoning transparency)
- Mistake detection and recovery
- User adaptation and learning
- Active learning from gaps

No mocks, no simulation - everything here is real and functional.
"""

from .confidence_calibrator import ConfidenceCalibrator, CalibrationResult
from .explanation_engine import ExplanationEngine, Explanation, ReasoningStep
from .mistake_detector import MistakeDetector, MistakeType, Recovery
from .user_modeler import UserModeler, UserProfile, Adaptation

__all__ = [
    # Confidence system
    "ConfidenceCalibrator",
    "CalibrationResult",

    # Explanation system
    "ExplanationEngine",
    "Explanation",
    "ReasoningStep",

    # Mistake detection
    "MistakeDetector",
    "MistakeType",
    "Recovery",

    # User modeling
    "UserModeler",
    "UserProfile",
    "Adaptation",
]
