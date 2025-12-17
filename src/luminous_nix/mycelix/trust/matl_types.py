"""
Data types for MATL Trust Scoring

MATL = Multi-Actor Trust Ledger
Components: PoGQ + TCDM + Entropy
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Interaction:
    """Single user interaction for MATL scoring"""
    timestamp: datetime
    operation_type: str  # "search", "install", etc.
    query: str
    success: bool
    duration_ms: float

    # Context
    user_did: str
    assurance_level: str

    # Results
    packages_found: int = 0
    packages_installed: int = 0
    errors: List[str] = field(default_factory=list)

    # Epistemic Classification (Charter v2.0) - Optional, populated by classifier
    epistemic_e: Optional[float] = None  # E-Axis: Empirical verifiability (0.0-1.0)
    epistemic_n: Optional[float] = None  # N-Axis: Normative authority (0.0-1.0)
    epistemic_m: Optional[int] = None    # M-Axis: Materiality/permanence (0-3)

    def to_dict(self) -> Dict:
        """Serialize for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Interaction':
        """Deserialize from storage"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class MATLScore:
    """Complete MATL trust score breakdown"""

    # Composite score (0.0-1.0)
    total_score: float

    # Components (0.0-1.0 each)
    pogq_score: float  # Proof of Genuine Query
    tcdm_score: float  # Temporal Consistency
    entropy_score: float  # Interaction diversity

    # Metadata
    interactions_count: int
    first_interaction: datetime
    last_interaction: datetime

    # Detailed breakdown
    components: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialize for storage"""
        return {
            'total_score': self.total_score,
            'pogq_score': self.pogq_score,
            'tcdm_score': self.tcdm_score,
            'entropy_score': self.entropy_score,
            'interactions_count': self.interactions_count,
            'first_interaction': self.first_interaction.isoformat(),
            'last_interaction': self.last_interaction.isoformat(),
            'components': self.components
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MATLScore':
        """Deserialize from storage"""
        data = data.copy()
        data['first_interaction'] = datetime.fromisoformat(data['first_interaction'])
        data['last_interaction'] = datetime.fromisoformat(data['last_interaction'])
        return cls(**data)
