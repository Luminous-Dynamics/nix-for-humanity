"""
Credit Calculator (E/N/M Weighted)

Calculates credits earned based on Charter v2.0 epistemic classification.

Formula:
    credits = base_rate × E_multiplier × N_multiplier × M_multiplier × trust_modifier

Where:
    - E_multiplier: Based on empirical verifiability (E0-E4)
    - N_multiplier: Based on normative authority (N0-N3)
    - M_multiplier: Based on materiality/permanence (M0-M3)
    - trust_modifier: Based on MATL trust score (0.5×-1.0×)
"""

import logging
from typing import Optional

from luminous_nix.mycelix.trust import Interaction
from luminous_nix.mycelix.epistemic import EpistemicScore
from .types import CreditAmount, CreditWeights, CreditTransaction, TransactionType
from datetime import datetime

logger = logging.getLogger(__name__)


class CreditCalculator:
    """
    Calculate credits earned from interactions

    Uses E/N/M coordinates and MATL trust scores to determine credit allocation.
    """

    def __init__(self, weights: Optional[CreditWeights] = None):
        """
        Initialize calculator

        Args:
            weights: Custom credit weights (defaults to standard weights)
        """
        self.weights = weights or CreditWeights()

    def calculate_credits(
        self,
        epistemic_score: EpistemicScore,
        matl_score: float = 0.8  # Default trust score
    ) -> CreditAmount:
        """
        Calculate credits from epistemic score and trust

        Args:
            epistemic_score: E/N/M classification
            matl_score: MATL trust score (0.0-1.0)

        Returns:
            CreditAmount earned
        """
        # Get multipliers from E/N/M
        e_mult = self.weights.get_e_multiplier(epistemic_score.epistemic_e)
        n_mult = self.weights.get_n_multiplier(epistemic_score.epistemic_n)
        m_mult = self.weights.get_m_multiplier(epistemic_score.epistemic_m)

        # Get trust modifier
        trust_mod = self.weights.get_trust_modifier(matl_score)

        # Calculate total
        credits = self.weights.base_rate * e_mult * n_mult * m_mult * trust_mod

        logger.debug(
            f"Credit calculation: {self.weights.base_rate} × "
            f"{e_mult}(E) × {n_mult}(N) × {m_mult}(M) × {trust_mod}(trust) "
            f"= {credits:.2f}"
        )

        return CreditAmount(credits)

    def calculate_from_interaction(
        self,
        interaction: Interaction,
        matl_score: float = 0.8
    ) -> CreditAmount:
        """
        Calculate credits directly from interaction

        Args:
            interaction: Interaction with E/N/M fields populated
            matl_score: MATL trust score (0.0-1.0)

        Returns:
            CreditAmount earned

        Raises:
            ValueError: If interaction doesn't have E/N/M fields
        """
        if (interaction.epistemic_e is None or
            interaction.epistemic_n is None or
            interaction.epistemic_m is None):
            raise ValueError(
                "Interaction must have epistemic_e, epistemic_n, epistemic_m fields populated. "
                "Ensure InteractionLogger has classified the interaction first."
            )

        # Create EpistemicScore from interaction fields
        from luminous_nix.mycelix.epistemic import EpistemicScore as ES
        epistemic_score = ES(
            epistemic_e=interaction.epistemic_e,
            epistemic_n=interaction.epistemic_n,
            epistemic_m=interaction.epistemic_m
        )

        return self.calculate_credits(epistemic_score, matl_score)

    def create_transaction(
        self,
        interaction: Interaction,
        credits_earned: CreditAmount,
        matl_score: float
    ) -> CreditTransaction:
        """
        Create credit transaction from interaction

        Args:
            interaction: The interaction that earned credits
            credits_earned: Amount of credits earned
            matl_score: MATL trust score used

        Returns:
            CreditTransaction ready for logging
        """
        return CreditTransaction(
            timestamp=interaction.timestamp,
            user_did=interaction.user_did,
            tx_type=TransactionType.EARN,
            amount=credits_earned,
            interaction_id=None,  # Could add interaction ID if tracked
            description=f"{interaction.operation_type}: {interaction.query}",
            epistemic_e=interaction.epistemic_e,
            epistemic_n=interaction.epistemic_n,
            epistemic_m=interaction.epistemic_m,
            matl_score=matl_score
        )

    def get_breakdown(
        self,
        epistemic_score: EpistemicScore,
        matl_score: float = 0.8
    ) -> dict:
        """
        Get detailed breakdown of credit calculation

        Args:
            epistemic_score: E/N/M classification
            matl_score: MATL trust score

        Returns:
            Dictionary with calculation breakdown
        """
        e_mult = self.weights.get_e_multiplier(epistemic_score.epistemic_e)
        n_mult = self.weights.get_n_multiplier(epistemic_score.epistemic_n)
        m_mult = self.weights.get_m_multiplier(epistemic_score.epistemic_m)
        trust_mod = self.weights.get_trust_modifier(matl_score)

        total_credits = self.weights.base_rate * e_mult * n_mult * m_mult * trust_mod

        return {
            'base_rate': self.weights.base_rate,
            'e_multiplier': e_mult,
            'n_multiplier': n_mult,
            'm_multiplier': m_mult,
            'trust_modifier': trust_mod,
            'total_credits': total_credits,
            'coordinate': epistemic_score.get_coordinate(),
            'formula': (
                f"{self.weights.base_rate} × {e_mult} × {n_mult} × "
                f"{m_mult} × {trust_mod} = {total_credits:.2f}"
            )
        }


# Singleton instance
_calculator: Optional[CreditCalculator] = None


def get_calculator(weights: Optional[CreditWeights] = None) -> CreditCalculator:
    """
    Get singleton calculator instance

    Args:
        weights: Custom weights (only used on first call)

    Returns:
        CreditCalculator instance
    """
    global _calculator
    if _calculator is None:
        _calculator = CreditCalculator(weights)
    return _calculator
