"""
Epistemic Classifier (Rule-Based)

Implements Charter v2.0 classification logic using deterministic rules.
"""

from typing import Optional
from luminous_nix.mycelix.trust import Interaction
from luminous_nix.mycelix.epistemic.types import (
    EpistemicScore,
    EpistemicExplanation,
    ETier,
    NTier,
    MTier
)


class EpistemicClassifier:
    """
    Rule-based E/N/M classifier (Charter v2.0)

    Classifies interactions along three axes:
    - E-Axis: Empirical verifiability
    - N-Axis: Normative authority
    - M-Axis: Materiality/permanence
    """

    def __init__(self):
        self.version = "1.0.0"

    def classify(
        self,
        interaction: Interaction,
        user_did: Optional[str] = None
    ) -> EpistemicScore:
        """
        Classify interaction into E/N/M cube

        Args:
            interaction: The interaction to classify
            user_did: Optional user DID for context

        Returns:
            EpistemicScore with E/N/M classification
        """
        # Classify each axis independently
        e_score, e_method = self._classify_empirical(interaction)
        n_score, n_scope = self._classify_normative(interaction)
        m_tier = self._classify_materiality(interaction)

        # Generate explanation
        explanation = self._generate_explanation(
            interaction, e_score, n_score, m_tier
        )

        return EpistemicScore(
            epistemic_e=e_score,
            epistemic_n=n_score,
            epistemic_m=m_tier,
            classifier_version=self.version,
            explanation=explanation,
            verifiability_method=e_method,
            normative_scope=n_scope
        )

    def _classify_empirical(self, interaction: Interaction) -> tuple[float, str]:
        """
        Classify E-Axis: How do we verify this?

        Returns: (score, method)

        Priority order:
        1. Failed operations → E0 (regardless of other factors)
        2. Public data → E4 (highest verifiability)
        3. System-verified → E2 (audit trail)
        4. DID-signed → E3 (cryptographic)
        5. User query → E1 (testimonial)
        """
        # E0: Failed operations are unverifiable
        if not interaction.success:
            return (0.0, "none")

        # E4: Publicly Reproducible (1.0)
        # - NixOS package queries (verifiable via nixpkgs)
        if interaction.operation_type == "search" and interaction.packages_found > 0:
            return (1.0, "public")  # E4: Can verify package exists in nixpkgs

        # E2: Privately Verifiable (0.5)
        # - System-verified operations (internal audit)
        # - Installs and configs are verified by the system
        if interaction.operation_type in ["install", "config"]:
            return (0.5, "audit")  # E2: System verified operation

        # E1: Testimonial (0.25)
        # - User queries without verification
        if interaction.operation_type in ["query"]:
            return (0.25, "testimonial")  # E1: User's word

        # E3: Cryptographically Proven (0.75)
        # - DID-signed operations that don't fit above categories
        if interaction.user_did and interaction.user_did.startswith("did:mycelix:"):
            return (0.75, "signature")  # E3: Signed by user DID

        # E0: Null/Unverifiable (0.0)
        # - Default for unknown operation types
        return (0.0, "none")  # E0: Cannot verify

    def _classify_normative(self, interaction: Interaction) -> tuple[float, str]:
        """
        Classify N-Axis: Who agrees this is binding?

        Returns: (score, scope)
        """
        # N3: Axiomatic (1.0)
        # - Core NixOS facts, constitutional knowledge
        if interaction.operation_type == "search" and "nix" in interaction.query.lower():
            # NixOS knowledge is "axiomatic" for this system
            return (1.0, "axiomatic")

        # N2: Network (0.67)
        # - System-wide policies (future: MIP-like changes)
        # Currently not applicable to personal NixOS operations
        # Reserved for future use

        # N1: Communal (0.33)
        # - Shared preferences, DAO-like decisions
        # Currently not applicable to single-user system
        # Reserved for future use

        # N0: Personal (0.0)
        # - All current operations are personal
        return (0.0, "personal")  # N0: User's personal action

    def _classify_materiality(self, interaction: Interaction) -> int:
        """
        Classify M-Axis: How long does this matter?

        Returns: M-tier (0-3)

        Priority order:
        1. Failed operations → M0 (ephemeral, discard immediately)
        2. Search with results → M3 (foundational knowledge)
        3. Install/config → M2 (persistent for audit)
        4. Query → M1 (temporal, session-based)
        """
        # M0: Ephemeral (0)
        # - Transient signals, errors
        # CHECK FIRST: Failed operations are ephemeral regardless of type
        if not interaction.success:
            # Failed operations are ephemeral
            return 0  # M0: Discard

        # M3: Foundational (3)
        # - Core system knowledge, permanent facts
        if interaction.operation_type == "search" and interaction.packages_found > 0:
            # Package existence is foundational knowledge
            return 3  # M3: Permanent

        # M2: Persistent (2)
        # - User's operation history (for trust scoring)
        if interaction.operation_type in ["install", "config"]:
            # Installation history matters for auditing
            return 2  # M2: Keep for audit trail

        # M1: Temporal (1)
        # - Current session context
        if interaction.operation_type == "query":
            # Simple queries only matter during session
            return 1  # M1: Session-based

        # Default to M1 (temporal)
        return 1

    def _generate_explanation(
        self,
        interaction: Interaction,
        e_score: float,
        n_score: float,
        m_tier: int
    ) -> str:
        """Generate human-readable explanation"""
        # Convert scores to tiers
        e_tier = self._score_to_e_tier(e_score)
        n_tier = self._score_to_n_tier(n_score)
        m_tier_enum = MTier(m_tier)

        explanation = (
            f"{e_tier.name}: "
            f"{self._explain_e_tier(e_tier, interaction)} | "
            f"{n_tier.name}: "
            f"{self._explain_n_tier(n_tier)} | "
            f"{m_tier_enum.name}: "
            f"{self._explain_m_tier(m_tier_enum, interaction)}"
        )

        return explanation

    def _score_to_e_tier(self, score: float) -> ETier:
        """Convert E-score to tier"""
        if score < 0.125:
            return ETier.E0
        elif score < 0.375:
            return ETier.E1
        elif score < 0.625:
            return ETier.E2
        elif score < 0.875:
            return ETier.E3
        else:
            return ETier.E4

    def _score_to_n_tier(self, score: float) -> NTier:
        """Convert N-score to tier"""
        if score < 0.17:
            return NTier.N0
        elif score < 0.5:
            return NTier.N1
        elif score < 0.84:
            return NTier.N2
        else:
            return NTier.N3

    def _explain_e_tier(self, tier: ETier, interaction: Interaction) -> str:
        """Explain E-tier classification"""
        if tier == ETier.E4:
            return "Publicly verifiable (nixpkgs data)"
        elif tier == ETier.E3:
            return "Cryptographically signed (DID)"
        elif tier == ETier.E2:
            return "System-verified operation"
        elif tier == ETier.E1:
            return "User testimonial"
        else:
            return "Unverifiable"

    def _explain_n_tier(self, tier: NTier) -> str:
        """Explain N-tier classification"""
        if tier == NTier.N3:
            return "Axiomatic (system knowledge)"
        elif tier == NTier.N2:
            return "Network consensus"
        elif tier == NTier.N1:
            return "Communal agreement"
        else:
            return "Personal action"

    def _explain_m_tier(self, tier: MTier, interaction: Interaction) -> str:
        """Explain M-tier classification"""
        if tier == MTier.M3:
            return "Foundational (permanent)"
        elif tier == MTier.M2:
            return "Persistent (audit trail)"
        elif tier == MTier.M1:
            return "Temporal (session)"
        else:
            return "Ephemeral (discard)"

    def get_detailed_explanation(
        self,
        interaction: Interaction
    ) -> EpistemicExplanation:
        """
        Get detailed explanation with Charter v2.0 examples

        Args:
            interaction: The classified interaction

        Returns:
            EpistemicExplanation with detailed rationale
        """
        score = self.classify(interaction)

        e_rationale = (
            f"Classified as {score.get_e_tier().name} "
            f"({score.epistemic_e:.2f}) because: "
            f"{self._explain_e_tier(score.get_e_tier(), interaction)}"
        )

        n_rationale = (
            f"Classified as {score.get_n_tier().name} "
            f"({score.epistemic_n:.2f}) because: "
            f"{self._explain_n_tier(score.get_n_tier())}"
        )

        m_rationale = (
            f"Classified as {score.get_m_tier().name} "
            f"({score.epistemic_m}) because: "
            f"{self._explain_m_tier(score.get_m_tier(), interaction)}"
        )

        # Find similar Charter examples
        examples = self._find_similar_examples(score)

        return EpistemicExplanation(
            e_axis_rationale=e_rationale,
            n_axis_rationale=n_rationale,
            m_axis_rationale=m_rationale,
            example_claims=examples
        )

    def _find_similar_examples(self, score: EpistemicScore) -> list[str]:
        """Find similar Charter v2.0 examples"""
        from luminous_nix.mycelix.epistemic.types import CHARTER_EXAMPLES

        similar = []
        for name, example in CHARTER_EXAMPLES.items():
            # Check if coordinates are similar (within 1 tier)
            e_diff = abs(score.epistemic_e - example.epistemic_e)
            n_diff = abs(score.epistemic_n - example.epistemic_n)
            m_diff = abs(score.epistemic_m - example.epistemic_m)

            if e_diff < 0.3 and n_diff < 0.3 and m_diff <= 1:
                similar.append(
                    f"{name}: {example.get_coordinate()} - {example.explanation}"
                )

        return similar[:3]  # Return top 3 matches


# Singleton instance
_classifier: Optional[EpistemicClassifier] = None


def get_classifier() -> EpistemicClassifier:
    """Get singleton classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = EpistemicClassifier()
    return _classifier
