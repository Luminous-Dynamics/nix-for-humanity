"""
Epistemic Cube Types (Charter v2.0)

Based on Mycelix Epistemic Charter v2.0:
- E-Axis: Empirical Verifiability (E0-E4)
- N-Axis: Normative Authority (N0-N3)
- M-Axis: Materiality/Permanence (M0-M3)
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class ETier(Enum):
    """E-Axis: Empirical Verifiability"""
    E0 = 0  # Null/Unverifiable (belief, opinion)
    E1 = 1  # Testimonial (personal attestation)
    E2 = 2  # Privately Verifiable (audit guild)
    E3 = 3  # Cryptographically Proven (ZKP)
    E4 = 4  # Publicly Reproducible (open data/code)


class NTier(Enum):
    """N-Axis: Normative Authority"""
    N0 = 0  # Personal (a-normative, self only)
    N1 = 1  # Communal (local DAO consensus)
    N2 = 2  # Network (global consensus, MIP)
    N3 = 3  # Axiomatic (constitutional, mathematical)


class MTier(Enum):
    """M-Axis: Materiality/Permanence"""
    M0 = 0  # Ephemeral (transient, discard)
    M1 = 1  # Temporal (valid until state change)
    M2 = 2  # Persistent (archive, audit trail)
    M3 = 3  # Foundational (permanent, never prune)


@dataclass
class EpistemicScore:
    """
    E/N/M classification result (Charter v2.0)

    Represents a point in the 3-dimensional Epistemic Cube.
    """

    # E-Axis: Empirical verifiability (0.0-1.0, maps to E0-E4)
    epistemic_e: float  # 0.0=E0, 0.25=E1, 0.5=E2, 0.75=E3, 1.0=E4

    # N-Axis: Normative authority (0.0-1.0, maps to N0-N3)
    epistemic_n: float  # 0.0=N0, 0.33=N1, 0.67=N2, 1.0=N3

    # M-Axis: Materiality/permanence (0-3)
    epistemic_m: int  # M0, M1, M2, or M3

    # Metadata
    classified_at: datetime = field(default_factory=datetime.now)
    classifier_version: str = "1.0.0"
    explanation: str = ""  # Human-readable rationale

    # Charter v2.0 fields (for advanced use)
    verifiability_method: str = "none"  # none, signature, zkproof, audit, public
    normative_scope: str = "personal"  # personal, communal, network, axiomatic

    def get_e_tier(self) -> ETier:
        """Convert E-score to discrete tier"""
        if self.epistemic_e < 0.125:
            return ETier.E0
        elif self.epistemic_e < 0.375:
            return ETier.E1
        elif self.epistemic_e < 0.625:
            return ETier.E2
        elif self.epistemic_e < 0.875:
            return ETier.E3
        else:
            return ETier.E4

    def get_n_tier(self) -> NTier:
        """Convert N-score to discrete tier"""
        if self.epistemic_n < 0.17:
            return NTier.N0
        elif self.epistemic_n < 0.5:
            return NTier.N1
        elif self.epistemic_n < 0.84:
            return NTier.N2
        else:
            return NTier.N3

    def get_m_tier(self) -> MTier:
        """Get M-tier as enum"""
        return MTier(self.epistemic_m)

    def get_coordinate(self) -> str:
        """Get (E, N, M) coordinate string"""
        e_tier = self.get_e_tier()
        n_tier = self.get_n_tier()
        m_tier = self.get_m_tier()
        return f"({e_tier.name}, {n_tier.name}, {m_tier.name})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        data = asdict(self)
        data['classified_at'] = self.classified_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EpistemicScore':
        """Deserialize from dictionary"""
        if isinstance(data['classified_at'], str):
            data['classified_at'] = datetime.fromisoformat(data['classified_at'])
        return cls(**data)


@dataclass
class EpistemicExplanation:
    """
    Detailed explanation of classification

    Provides human-readable rationale for each axis.
    """

    e_axis_rationale: str
    n_axis_rationale: str
    m_axis_rationale: str

    # Charter v2.0 examples for context
    example_claims: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Format as readable markdown"""
        md = "## Epistemic Classification Explanation\n\n"
        md += f"**E-Axis (Empirical)**: {self.e_axis_rationale}\n\n"
        md += f"**N-Axis (Normative)**: {self.n_axis_rationale}\n\n"
        md += f"**M-Axis (Materiality)**: {self.m_axis_rationale}\n\n"

        if self.example_claims:
            md += "**Similar Claims**:\n"
            for example in self.example_claims:
                md += f"- {example}\n"

        return md


# Charter v2.0 Example Classifications (for testing/reference)
CHARTER_EXAMPLES = {
    "like": EpistemicScore(0.0, 0.0, 0, explanation="Unverifiable, personal, ephemeral"),
    "mail_message": EpistemicScore(0.25, 0.0, 1, explanation="Testimonial, personal, temporal"),
    "agora_listing": EpistemicScore(0.25, 0.33, 1, explanation="Testimonial, communal, temporal"),
    "agora_sale": EpistemicScore(0.5, 0.33, 2, explanation="Audit-verified, communal, persistent"),
    "song_copyright": EpistemicScore(0.75, 0.33, 3, explanation="Cryptographic proof, communal, foundational"),
    "math_proof": EpistemicScore(1.0, 1.0, 3, explanation="Publicly reproducible, axiomatic, foundational"),
    "constitution": EpistemicScore(0.0, 1.0, 3, explanation="Belief, axiomatic, foundational"),
}
