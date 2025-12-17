"""
MATL (Multi-Actor Trust Ledger) Engine

Complete trust scoring system that combines:
- PoGQ (Proof of Genuine Query) - Query authenticity
- TCDM (Temporal Consistency) - Timing patterns
- Entropy (Diversity) - Exploration and learning

Produces comprehensive trust scores for users based on interaction history.
"""

from typing import List, Optional
from datetime import datetime
import logging

from .matl_types import Interaction, MATLScore
from .pogq import PoGQCalculator
from .tcdm import TCDMCalculator
from .entropy import EntropyCalculator

logger = logging.getLogger(__name__)


class MATLEngine:
    """
    Complete MATL Trust Scoring Engine.

    Combines PoGQ, TCDM, and Entropy into a unified trust score.
    """

    def __init__(
        self,
        pogq_weight: float = 0.4,
        tcdm_weight: float = 0.3,
        entropy_weight: float = 0.3
    ):
        """
        Initialize MATL Engine with component calculators.

        Args:
            pogq_weight: Weight for PoGQ component (default: 0.4)
            tcdm_weight: Weight for TCDM component (default: 0.3)
            entropy_weight: Weight for Entropy component (default: 0.3)
        """
        # Validate weights sum to 1.0
        total_weight = pogq_weight + tcdm_weight + entropy_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Component weights must sum to 1.0, got {total_weight}")

        self.pogq_weight = pogq_weight
        self.tcdm_weight = tcdm_weight
        self.entropy_weight = entropy_weight

        # Initialize component calculators
        self.pogq_calc = PoGQCalculator()
        self.tcdm_calc = TCDMCalculator()
        self.entropy_calc = EntropyCalculator()

        # Minimum interactions for reliable scoring
        self.min_interactions = 5

    def calculate_trust_score(
        self,
        interactions: List[Interaction],
        user_did: Optional[str] = None
    ) -> MATLScore:
        """
        Calculate complete MATL trust score.

        Args:
            interactions: List of user interactions
            user_did: User's DID (optional, for filtering)

        Returns:
            MATLScore: Complete trust score with component breakdown
        """
        if not interactions:
            return self._create_empty_score(user_did)

        # Filter by user DID if specified
        if user_did:
            interactions = [i for i in interactions if i.user_did == user_did]
            if not interactions:
                return self._create_empty_score(user_did)

        # Calculate component scores
        pogq_score = self.pogq_calc.calculate(interactions)
        tcdm_score = self.tcdm_calc.calculate(interactions)
        entropy_score = self.entropy_calc.calculate(interactions)

        # Calculate weighted total
        total_score = (
            self.pogq_weight * pogq_score +
            self.tcdm_weight * tcdm_score +
            self.entropy_weight * entropy_score
        )

        # Clamp to [0, 1]
        total_score = max(0.0, min(1.0, total_score))

        # Get first and last interaction times
        first_interaction = interactions[0].timestamp
        last_interaction = interactions[-1].timestamp

        # Create MATL score
        matl_score = MATLScore(
            total_score=total_score,
            pogq_score=pogq_score,
            tcdm_score=tcdm_score,
            entropy_score=entropy_score,
            interactions_count=len(interactions),
            first_interaction=first_interaction,
            last_interaction=last_interaction,
            components={
                'pogq': pogq_score,
                'tcdm': tcdm_score,
                'entropy': entropy_score
            }
        )

        return matl_score

    def get_detailed_explanation(
        self,
        interactions: List[Interaction]
    ) -> dict:
        """
        Get detailed explanation of trust score with component breakdowns.

        Args:
            interactions: List of user interactions

        Returns:
            dict: Comprehensive explanation with all components
        """
        if not interactions:
            return {
                'total_score': 0.0,
                'message': 'No interactions yet',
                'components': {},
                'recommendations': []
            }

        # Get component explanations
        pogq_explanation = self.pogq_calc.get_explanation(interactions)
        tcdm_explanation = self.tcdm_calc.get_explanation(interactions)
        entropy_explanation = self.entropy_calc.get_explanation(interactions)

        # Calculate total score
        total_score = (
            self.pogq_weight * pogq_explanation['score'] +
            self.tcdm_weight * tcdm_explanation['score'] +
            self.entropy_weight * entropy_explanation['score']
        )

        # Generate recommendations based on component scores
        recommendations = self._generate_recommendations(
            pogq_explanation['score'],
            tcdm_explanation['score'],
            entropy_explanation['score']
        )

        return {
            'total_score': total_score,
            'interpretation': self._interpret_total_score(total_score),
            'components': {
                'pogq': {
                    'score': pogq_explanation['score'],
                    'weight': self.pogq_weight,
                    'interpretation': pogq_explanation['interpretation'],
                    'details': pogq_explanation['components']
                },
                'tcdm': {
                    'score': tcdm_explanation['score'],
                    'weight': self.tcdm_weight,
                    'interpretation': tcdm_explanation['interpretation'],
                    'details': tcdm_explanation['components']
                },
                'entropy': {
                    'score': entropy_explanation['score'],
                    'weight': self.entropy_weight,
                    'interpretation': entropy_explanation['interpretation'],
                    'details': entropy_explanation['components']
                }
            },
            'interactions_analyzed': len(interactions),
            'recommendations': recommendations
        }

    def _create_empty_score(self, user_did: Optional[str] = None) -> MATLScore:
        """Create an empty MATL score for users with no interactions."""
        now = datetime.now()
        return MATLScore(
            total_score=0.0,
            pogq_score=0.0,
            tcdm_score=0.0,
            entropy_score=0.0,
            interactions_count=0,
            first_interaction=now,
            last_interaction=now,
            components={}
        )

    def _interpret_total_score(self, score: float) -> str:
        """Interpret overall trust score."""
        if score >= 0.9:
            return "Exceptional - Highly trustworthy, genuine user"
        elif score >= 0.8:
            return "Excellent - Very trustworthy behavior"
        elif score >= 0.7:
            return "Very Good - Strong trust signals"
        elif score >= 0.6:
            return "Good - Reliable user behavior"
        elif score >= 0.5:
            return "Fair - Average trust level"
        elif score >= 0.4:
            return "Below Average - Some concerns"
        else:
            return "Low - Suspicious patterns detected"

    def _generate_recommendations(
        self,
        pogq_score: float,
        tcdm_score: float,
        entropy_score: float
    ) -> List[str]:
        """Generate recommendations for improving trust score."""
        recommendations = []

        # PoGQ recommendations
        if pogq_score < 0.6:
            recommendations.append(
                "Query Diversity: Try asking more varied questions to demonstrate genuine learning"
            )
        if pogq_score < 0.5:
            recommendations.append(
                "Query Quality: Avoid repetitive or bot-like query patterns"
            )

        # TCDM recommendations
        if tcdm_score < 0.6:
            recommendations.append(
                "Timing Patterns: Natural breaks between sessions improve trust"
            )
        if tcdm_score < 0.5:
            recommendations.append(
                "Activity Rhythm: Consider using the system during typical waking hours"
            )

        # Entropy recommendations
        if entropy_score < 0.6:
            recommendations.append(
                "Exploration: Try exploring different package categories and topics"
            )
        if entropy_score < 0.5:
            recommendations.append(
                "Learning: Balance exploration (search) with adoption (install/use)"
            )

        # Overall recommendations
        if not recommendations:
            recommendations.append(
                "Excellent trust profile! Continue your natural usage patterns."
            )

        return recommendations

    def calculate_assurance_level(self, matl_score: MATLScore) -> str:
        """
        Calculate recommended assurance level based on MATL score.

        Assurance Levels:
        - E0 (Basic): New users, low trust (< 0.5)
        - E1 (Established): Regular users, moderate trust (0.5-0.7)
        - E2 (Verified): Trusted users, high trust (0.7-0.85)
        - E3 (Enhanced): Highly trusted, very high trust (0.85-0.95)
        - E4 (Distributed): Exceptional trust (>= 0.95)

        Args:
            matl_score: MATL trust score

        Returns:
            str: Recommended assurance level (E0-E4)
        """
        score = matl_score.total_score

        if score >= 0.95:
            return "E4"
        elif score >= 0.85:
            return "E3"
        elif score >= 0.7:
            return "E2"
        elif score >= 0.5:
            return "E1"
        else:
            return "E0"

    def get_component_weights(self) -> dict:
        """Get current component weights."""
        return {
            'pogq': self.pogq_weight,
            'tcdm': self.tcdm_weight,
            'entropy': self.entropy_weight
        }

    def set_component_weights(
        self,
        pogq_weight: Optional[float] = None,
        tcdm_weight: Optional[float] = None,
        entropy_weight: Optional[float] = None
    ):
        """
        Update component weights.

        Args:
            pogq_weight: New PoGQ weight (optional)
            tcdm_weight: New TCDM weight (optional)
            entropy_weight: New Entropy weight (optional)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        # Use current weights as defaults
        new_pogq = pogq_weight if pogq_weight is not None else self.pogq_weight
        new_tcdm = tcdm_weight if tcdm_weight is not None else self.tcdm_weight
        new_entropy = entropy_weight if entropy_weight is not None else self.entropy_weight

        # Validate weights sum to 1.0
        total = new_pogq + new_tcdm + new_entropy
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Component weights must sum to 1.0, got {total}")

        self.pogq_weight = new_pogq
        self.tcdm_weight = new_tcdm
        self.entropy_weight = new_entropy

        logger.info(f"Updated MATL weights: PoGQ={new_pogq}, TCDM={new_tcdm}, Entropy={new_entropy}")
