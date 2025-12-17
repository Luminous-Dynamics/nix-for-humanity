"""Tests for MATL (Multi-Actor Trust Ledger) Engine"""

import pytest
from datetime import datetime, timedelta

from luminous_nix.mycelix.trust import Interaction, MATLScore
from luminous_nix.mycelix.trust.matl_engine import MATLEngine


class TestMATLEngine:
    """Test MATL Engine"""

    @pytest.fixture
    def engine(self):
        """Create MATL engine instance with default weights"""
        return MATLEngine()

    @pytest.fixture
    def custom_engine(self):
        """Create MATL engine with custom weights"""
        return MATLEngine(pogq_weight=0.5, tcdm_weight=0.3, entropy_weight=0.2)

    def test_engine_initialization(self, engine):
        """Test that engine initializes with correct default weights"""
        weights = engine.get_component_weights()
        assert weights['pogq'] == 0.4
        assert weights['tcdm'] == 0.3
        assert weights['entropy'] == 0.3

    def test_custom_weights_initialization(self, custom_engine):
        """Test that engine accepts custom weights"""
        weights = custom_engine.get_component_weights()
        assert weights['pogq'] == 0.5
        assert weights['tcdm'] == 0.3
        assert weights['entropy'] == 0.2

    def test_invalid_weights_raise_error(self):
        """Test that invalid weights (not summing to 1.0) raise error"""
        with pytest.raises(ValueError):
            MATLEngine(pogq_weight=0.5, tcdm_weight=0.3, entropy_weight=0.1)

    def test_empty_interactions(self, engine):
        """Test with no interactions"""
        score = engine.calculate_trust_score([])
        assert isinstance(score, MATLScore)
        assert score.total_score == 0.0
        assert score.interactions_count == 0

    def test_calculate_trust_score_structure(self, engine):
        """Test that trust score has correct structure"""
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search",
                query=f"diverse query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test:user",
                assurance_level="E0"
            ))

        score = engine.calculate_trust_score(interactions)

        # Check structure
        assert isinstance(score, MATLScore)
        assert hasattr(score, 'total_score')
        assert hasattr(score, 'pogq_score')
        assert hasattr(score, 'tcdm_score')
        assert hasattr(score, 'entropy_score')
        assert hasattr(score, 'interactions_count')
        assert hasattr(score, 'first_interaction')
        assert hasattr(score, 'last_interaction')
        assert hasattr(score, 'components')

        # Check values are in valid range
        assert 0.0 <= score.total_score <= 1.0
        assert 0.0 <= score.pogq_score <= 1.0
        assert 0.0 <= score.tcdm_score <= 1.0
        assert 0.0 <= score.entropy_score <= 1.0

        # Check interaction count
        assert score.interactions_count == 10

    def test_weighted_combination(self, engine):
        """Test that total score is correctly weighted combination"""
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = engine.calculate_trust_score(interactions)

        # Calculate expected total manually
        expected_total = (
            0.4 * score.pogq_score +
            0.3 * score.tcdm_score +
            0.3 * score.entropy_score
        )

        # Should match (within floating point precision)
        assert abs(score.total_score - expected_total) < 0.01

    def test_filter_by_user_did(self, engine):
        """Test filtering interactions by user DID"""
        interactions = []

        # User 1 interactions
        for i in range(5):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search",
                query=f"user1_query{i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:user1",
                assurance_level="E0"
            ))

        # User 2 interactions
        for i in range(5):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=(i + 5) * 60),
                operation_type="search",
                query=f"user2_query{i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:user2",
                assurance_level="E0"
            ))

        # Calculate score for user1 only
        user1_score = engine.calculate_trust_score(interactions, user_did="did:mycelix:user1")
        assert user1_score.interactions_count == 5

    def test_get_detailed_explanation(self, engine):
        """Test detailed explanation structure"""
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search" if i % 2 == 0 else "install",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        explanation = engine.get_detailed_explanation(interactions)

        # Check top-level structure
        assert 'total_score' in explanation
        assert 'interpretation' in explanation
        assert 'components' in explanation
        assert 'interactions_analyzed' in explanation
        assert 'recommendations' in explanation

        # Check components structure
        components = explanation['components']
        assert 'pogq' in components
        assert 'tcdm' in components
        assert 'entropy' in components

        # Each component should have score, weight, interpretation, details
        for component_name in ['pogq', 'tcdm', 'entropy']:
            component = components[component_name]
            assert 'score' in component
            assert 'weight' in component
            assert 'interpretation' in component
            assert 'details' in component

        # Check recommendations
        assert isinstance(explanation['recommendations'], list)
        assert len(explanation['recommendations']) > 0

    def test_calculate_assurance_level(self, engine):
        """Test assurance level calculation based on trust score"""
        # Create mock scores with different total scores
        test_cases = [
            (0.3, "E0"),   # Low trust
            (0.6, "E1"),   # Moderate trust
            (0.75, "E2"),  # High trust
            (0.9, "E3"),   # Very high trust
            (0.96, "E4"),  # Exceptional trust
        ]

        now = datetime.now()
        for total_score, expected_level in test_cases:
            mock_score = MATLScore(
                total_score=total_score,
                pogq_score=total_score,
                tcdm_score=total_score,
                entropy_score=total_score,
                interactions_count=10,
                first_interaction=now,
                last_interaction=now,
                components={}
            )

            calculated_level = engine.calculate_assurance_level(mock_score)
            assert calculated_level == expected_level

    def test_set_component_weights(self, engine):
        """Test updating component weights"""
        # Update weights
        engine.set_component_weights(pogq_weight=0.5, tcdm_weight=0.25, entropy_weight=0.25)

        weights = engine.get_component_weights()
        assert weights['pogq'] == 0.5
        assert weights['tcdm'] == 0.25
        assert weights['entropy'] == 0.25

    def test_set_invalid_weights_raises_error(self, engine):
        """Test that invalid weight updates raise error"""
        with pytest.raises(ValueError):
            engine.set_component_weights(pogq_weight=0.5, tcdm_weight=0.3, entropy_weight=0.1)

    def test_set_partial_weights(self, engine):
        """Test that partial weight updates must still sum to 1.0"""
        # Attempting to update just one weight without adjusting others should fail
        # because the weights must sum to 1.0
        with pytest.raises(ValueError):
            # This would create: 0.5 (new pogq) + 0.3 (old tcdm) + 0.3 (old entropy) = 1.1
            engine.set_component_weights(pogq_weight=0.5)

        # Valid partial update: adjust multiple weights to maintain sum
        engine.set_component_weights(pogq_weight=0.5, tcdm_weight=0.25, entropy_weight=0.25)
        weights = engine.get_component_weights()
        assert weights['pogq'] == 0.5
        assert weights['tcdm'] == 0.25
        assert weights['entropy'] == 0.25
        assert abs(sum(weights.values()) - 1.0) < 0.01


# Integration tests
def test_matl_complete_workflow():
    """Test complete MATL workflow with realistic data"""
    engine = MATLEngine()

    # Simulate a user's journey over time
    interactions = []
    base_time = datetime.now()

    # Week 1: Learning basics
    week1_data = [
        ("search", "vim editor", True),
        ("search", "vim", True),
        ("install", "vim", True),
        ("search", "git version control", True),
        ("install", "git", True),
    ]

    for i, (op_type, query, success) in enumerate(week1_data):
        interactions.append(Interaction(
            timestamp=base_time + timedelta(days=i),
            operation_type=op_type,
            query=query,
            success=success,
            duration_ms=1500.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_found=3 if op_type == "search" else 0,
            packages_installed=1 if op_type == "install" else 0
        ))

    # Week 2: Expanding knowledge
    week2_data = [
        ("search", "python development", True),
        ("install", "python311", True),
        ("search", "postgresql database", True),
        ("install", "postgresql", True),
        ("config", "setup python env", True),
    ]

    for i, (op_type, query, success) in enumerate(week2_data):
        interactions.append(Interaction(
            timestamp=base_time + timedelta(days=7 + i),
            operation_type=op_type,
            query=query,
            success=success,
            duration_ms=1200.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_found=4 if op_type == "search" else 0,
            packages_installed=1 if op_type == "install" else 0
        ))

    # Calculate trust score
    matl_score = engine.calculate_trust_score(interactions)
    explanation = engine.get_detailed_explanation(interactions)

    # Should show good trust for genuine learning user
    assert matl_score.total_score > 0.5
    assert matl_score.interactions_count == 10

    # Get recommended assurance level
    recommended_level = engine.calculate_assurance_level(matl_score)
    assert recommended_level in ["E0", "E1", "E2", "E3", "E4"]

    print(f"✅ MATL complete workflow test passed!")
    print(f"   Total Score: {matl_score.total_score:.3f}")
    print(f"   PoGQ: {matl_score.pogq_score:.3f}")
    print(f"   TCDM: {matl_score.tcdm_score:.3f}")
    print(f"   Entropy: {matl_score.entropy_score:.3f}")
    print(f"   Recommended Level: {recommended_level}")
    print(f"   Interpretation: {explanation['interpretation']}")


def test_matl_serialization():
    """Test that MATL scores can be serialized"""
    engine = MATLEngine()

    interactions = []
    for i in range(10):
        interactions.append(Interaction(
            timestamp=datetime.now() + timedelta(seconds=i * 60),
            operation_type="search",
            query=f"query {i}",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test",
            assurance_level="E0"
        ))

    score = engine.calculate_trust_score(interactions)

    # Test serialization (to dict)
    score_dict = score.to_dict()
    assert isinstance(score_dict, dict)
    assert 'total_score' in score_dict
    assert 'pogq_score' in score_dict
    assert 'tcdm_score' in score_dict
    assert 'entropy_score' in score_dict

    # Test deserialization (from dict)
    restored_score = MATLScore.from_dict(score_dict)
    assert restored_score.total_score == score.total_score
    assert restored_score.pogq_score == score.pogq_score
    assert restored_score.tcdm_score == score.tcdm_score
    assert restored_score.entropy_score == score.entropy_score

    print("✅ MATL serialization test passed!")
