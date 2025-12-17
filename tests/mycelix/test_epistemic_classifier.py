"""Tests for Epistemic Classifier (Charter v2.0)"""

import pytest
from datetime import datetime, timedelta

from luminous_nix.mycelix.epistemic import (
    EpistemicClassifier,
    EpistemicScore,
    ETier,
    NTier,
    MTier,
    CHARTER_EXAMPLES,
    get_classifier
)
from luminous_nix.mycelix.trust import Interaction


class TestEpistemicTypes:
    """Test Epistemic types and conversions"""

    def test_epistemic_score_creation(self):
        """Test creating EpistemicScore"""
        score = EpistemicScore(
            epistemic_e=0.75,
            epistemic_n=0.33,
            epistemic_m=2
        )

        assert score.epistemic_e == 0.75
        assert score.epistemic_n == 0.33
        assert score.epistemic_m == 2
        assert isinstance(score.classified_at, datetime)

    def test_e_tier_conversion(self):
        """Test E-score to ETier conversion"""
        # E0
        score_e0 = EpistemicScore(0.0, 0.0, 0)
        assert score_e0.get_e_tier() == ETier.E0

        # E1
        score_e1 = EpistemicScore(0.25, 0.0, 0)
        assert score_e1.get_e_tier() == ETier.E1

        # E2
        score_e2 = EpistemicScore(0.5, 0.0, 0)
        assert score_e2.get_e_tier() == ETier.E2

        # E3
        score_e3 = EpistemicScore(0.75, 0.0, 0)
        assert score_e3.get_e_tier() == ETier.E3

        # E4
        score_e4 = EpistemicScore(1.0, 0.0, 0)
        assert score_e4.get_e_tier() == ETier.E4

    def test_n_tier_conversion(self):
        """Test N-score to NTier conversion"""
        # N0
        score_n0 = EpistemicScore(0.0, 0.0, 0)
        assert score_n0.get_n_tier() == NTier.N0

        # N1
        score_n1 = EpistemicScore(0.0, 0.33, 0)
        assert score_n1.get_n_tier() == NTier.N1

        # N2
        score_n2 = EpistemicScore(0.0, 0.67, 0)
        assert score_n2.get_n_tier() == NTier.N2

        # N3
        score_n3 = EpistemicScore(0.0, 1.0, 0)
        assert score_n3.get_n_tier() == NTier.N3

    def test_m_tier_conversion(self):
        """Test M-tier as enum"""
        score_m0 = EpistemicScore(0.0, 0.0, 0)
        assert score_m0.get_m_tier() == MTier.M0

        score_m3 = EpistemicScore(0.0, 0.0, 3)
        assert score_m3.get_m_tier() == MTier.M3

    def test_coordinate_string(self):
        """Test (E, N, M) coordinate string"""
        score = EpistemicScore(0.75, 0.33, 3)
        coord = score.get_coordinate()

        assert "E3" in coord
        assert "N1" in coord
        assert "M3" in coord

    def test_serialization(self):
        """Test to_dict/from_dict"""
        score = EpistemicScore(0.5, 0.67, 2, explanation="Test score")

        # Serialize
        data = score.to_dict()
        assert data['epistemic_e'] == 0.5
        assert data['epistemic_n'] == 0.67
        assert data['epistemic_m'] == 2

        # Deserialize
        restored = EpistemicScore.from_dict(data)
        assert restored.epistemic_e == 0.5
        assert restored.epistemic_n == 0.67
        assert restored.epistemic_m == 2


class TestEpistemicClassifier:
    """Test Epistemic Classifier"""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance"""
        return EpistemicClassifier()

    def test_classifier_creation(self, classifier):
        """Test creating classifier"""
        assert classifier is not None
        assert classifier.version == "1.0.0"

    def test_singleton_classifier(self):
        """Test singleton pattern"""
        c1 = get_classifier()
        c2 = get_classifier()
        assert c1 is c2

    def test_classify_search_operation(self, classifier):
        """Test classifying search operation"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox browser",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_found=5
        )

        score = classifier.classify(interaction)

        # Should be E4 (publicly verifiable in nixpkgs)
        assert score.epistemic_e == 1.0
        assert score.get_e_tier() == ETier.E4

        # Should be N0 (personal action)
        assert score.epistemic_n == 0.0
        assert score.get_n_tier() == NTier.N0

        # Should be M3 (foundational knowledge)
        assert score.epistemic_m == 3
        assert score.get_m_tier() == MTier.M3

    def test_classify_install_operation(self, classifier):
        """Test classifying install operation"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="vim",
            success=True,
            duration_ms=5000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_installed=1
        )

        score = classifier.classify(interaction)

        # Should be E2 (system-verified)
        assert score.epistemic_e == 0.5
        assert score.get_e_tier() == ETier.E2

        # Should be N0 (personal)
        assert score.epistemic_n == 0.0

        # Should be M2 (persistent, audit trail)
        assert score.epistemic_m == 2
        assert score.get_m_tier() == MTier.M2

    def test_classify_failed_operation(self, classifier):
        """Test classifying failed operation"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="nonexistent-package",
            success=False,
            duration_ms=1000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        )

        score = classifier.classify(interaction)

        # Should be E0 (unverifiable)
        assert score.epistemic_e == 0.0
        assert score.get_e_tier() == ETier.E0

        # Should be M0 (ephemeral)
        assert score.epistemic_m == 0
        assert score.get_m_tier() == MTier.M0

    def test_classify_query_operation(self, classifier):
        """Test classifying simple query"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="query",
            query="how to install packages",
            success=True,
            duration_ms=500.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        )

        score = classifier.classify(interaction)

        # Should be E1 (testimonial)
        assert score.epistemic_e == 0.25
        assert score.get_e_tier() == ETier.E1

        # Should be M1 (temporal, session-based)
        assert score.epistemic_m == 1
        assert score.get_m_tier() == MTier.M1

    def test_explanation_generation(self, classifier):
        """Test explanation generation"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="git",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_found=3
        )

        score = classifier.classify(interaction)

        assert score.explanation is not None
        assert len(score.explanation) > 0
        assert "E4" in score.explanation or "Publicly" in score.explanation
        assert "M3" in score.explanation or "Foundational" in score.explanation

    def test_detailed_explanation(self, classifier):
        """Test detailed explanation"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="python311",
            success=True,
            duration_ms=10000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_installed=1
        )

        explanation = classifier.get_detailed_explanation(interaction)

        assert explanation.e_axis_rationale is not None
        assert explanation.n_axis_rationale is not None
        assert explanation.m_axis_rationale is not None
        assert "E2" in explanation.e_axis_rationale
        assert "M2" in explanation.m_axis_rationale


class TestCharterExamples:
    """Test against Charter v2.0 examples"""

    def test_charter_examples_exist(self):
        """Test that Charter examples are defined"""
        assert len(CHARTER_EXAMPLES) > 0
        assert "like" in CHARTER_EXAMPLES
        assert "math_proof" in CHARTER_EXAMPLES

    def test_like_example(self):
        """Test 'like' example (E0, N0, M0)"""
        like_score = CHARTER_EXAMPLES["like"]

        assert like_score.get_e_tier() == ETier.E0
        assert like_score.get_n_tier() == NTier.N0
        assert like_score.get_m_tier() == MTier.M0

    def test_math_proof_example(self):
        """Test math proof example (E4, N3, M3)"""
        math_score = CHARTER_EXAMPLES["math_proof"]

        assert math_score.get_e_tier() == ETier.E4
        assert math_score.get_n_tier() == NTier.N3
        assert math_score.get_m_tier() == MTier.M3

    def test_constitution_example(self):
        """Test constitution example (E0, N3, M3)"""
        # Constitution is unverifiable belief but axiomatic
        const_score = CHARTER_EXAMPLES["constitution"]

        assert const_score.get_e_tier() == ETier.E0  # Belief
        assert const_score.get_n_tier() == NTier.N3  # Axiomatic
        assert const_score.get_m_tier() == MTier.M3  # Foundational

    def test_agora_sale_example(self):
        """Test Agora sale example (E2, N1, M2)"""
        sale_score = CHARTER_EXAMPLES["agora_sale"]

        assert sale_score.get_e_tier() == ETier.E2  # Audit-verified
        assert sale_score.get_n_tier() == NTier.N1  # Communal
        assert sale_score.get_m_tier() == MTier.M2  # Persistent


# Integration test
def test_complete_classification_workflow():
    """Test complete classification workflow"""
    classifier = get_classifier()

    # Create diverse interactions
    interactions = [
        # E4, N0, M3: Package search
        Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="python packages",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            packages_found=10
        ),
        # E2, N0, M2: Install
        Interaction(
            timestamp=datetime.now() + timedelta(seconds=10),
            operation_type="install",
            query="python311",
            success=True,
            duration_ms=5000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            packages_installed=1
        ),
        # E0, N0, M0: Failed operation
        Interaction(
            timestamp=datetime.now() + timedelta(seconds=20),
            operation_type="install",
            query="bad-package",
            success=False,
            duration_ms=500.0,
            user_did="did:mycelix:test",
            assurance_level="E0"
        ),
    ]

    # Classify all
    scores = [classifier.classify(i) for i in interactions]

    assert len(scores) == 3

    # Verify classifications
    assert scores[0].get_e_tier() == ETier.E4  # Publicly verifiable
    assert scores[1].get_e_tier() == ETier.E2  # System-verified
    assert scores[2].get_e_tier() == ETier.E0  # Unverifiable

    assert scores[0].get_m_tier() == MTier.M3  # Foundational
    assert scores[1].get_m_tier() == MTier.M2  # Persistent
    assert scores[2].get_m_tier() == MTier.M0  # Ephemeral

    print("✅ Complete classification workflow test passed!")
    print(f"   Search: {scores[0].get_coordinate()}")
    print(f"   Install: {scores[1].get_coordinate()}")
    print(f"   Failed: {scores[2].get_coordinate()}")
