"""
Epistemic Cube Classification (Charter v2.0)

Provides 3-dimensional classification of knowledge:
- E-Axis: Empirical Verifiability (E0-E4)
- N-Axis: Normative Authority (N0-N3)
- M-Axis: Materiality/Permanence (M0-M3)

Based on: Mycelix Epistemic Charter v2.0
"""

from .types import (
    ETier,
    NTier,
    MTier,
    EpistemicScore,
    EpistemicExplanation,
    CHARTER_EXAMPLES
)

from .classifier import (
    EpistemicClassifier,
    get_classifier
)

from .storage_manager import (
    StorageManager
)

__version__ = "1.0.0"
__all__ = [
    # Types
    'ETier',
    'NTier',
    'MTier',
    'EpistemicScore',
    'EpistemicExplanation',
    'CHARTER_EXAMPLES',
    # Classifier
    'EpistemicClassifier',
    'get_classifier',
    # Storage
    'StorageManager',
]
