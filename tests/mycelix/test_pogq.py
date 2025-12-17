"""Tests for PoGQ (Proof of Genuine Query) Calculator"""

import pytest
from datetime import datetime, timedelta

from luminous_nix.mycelix.trust import Interaction
from luminous_nix.mycelix.trust.pogq import PoGQCalculator


class TestPoGQCalculator:
    """Test PoGQ Calculator"""

    @pytest.fixture
    def calculator(self):
        """Create PoGQ calculator instance"""
        return PoGQCalculator()

    def test_empty_interactions(self, calculator):
        """Test with no interactions"""
        score = calculator.calculate([])
        assert score == 0.0

    def test_insufficient_interactions(self, calculator):
        """Test with fewer than minimum interactions"""
        interactions = [
            Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query="test",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            )
        ]

        # Should return neutral score (0.5) for insufficient data
        score = calculator.calculate(interactions)
        assert score == 0.5

    def test_diverse_queries_score_high(self, calculator):
        """Test that diverse queries get high scores"""
        # Create 10 unique queries
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query=f"unique query {i} with different words",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # High diversity should yield high score (> 0.7)
        assert score > 0.7

    def test_repetitive_queries_score_low(self, calculator):
        """Test that repetitive queries get low scores"""
        # Create 10 identical queries (bot-like behavior)
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query="same query",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Low diversity should yield lower score (< 0.5)
        assert score < 0.5

    def test_appropriate_length_queries(self, calculator):
        """Test that appropriate query lengths score well"""
        interactions = []
        for i in range(10):
            # Queries with reasonable length (10-30 chars)
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query=f"query number {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Should have reasonable coherence component
        assert score > 0.5

    def test_inappropriate_length_queries(self, calculator):
        """Test that very short or very long queries score lower"""
        interactions = []
        for i in range(5):
            # Very short queries (<2 chars)
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query="a",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        for i in range(5, 10):
            # Very long queries (>100 chars)
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query="x" * 150,
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Should score lower due to inappropriate lengths
        assert score < 0.7

    def test_learning_progression(self, calculator):
        """Test that improving success rate and complexity increases score"""
        interactions = []

        # Early interactions: simple, some failures
        for i in range(5):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query=f"simple {i}",
                success=i % 2 == 0,  # 60% success
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        # Later interactions: more complex, better success
        for i in range(5, 10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query=f"more complex query with additional terms {i}",
                success=True,  # 100% success
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Learning progression should contribute positively
        assert score > 0.6

    def test_get_explanation(self, calculator):
        """Test that explanation provides component breakdown"""
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        explanation = calculator.get_explanation(interactions)

        # Check structure
        assert 'score' in explanation
        assert 'components' in explanation
        assert 'interpretation' in explanation
        assert 'interactions_analyzed' in explanation

        # Check components
        components = explanation['components']
        assert 'diversity' in components
        assert 'coherence' in components
        assert 'progression' in components

        # Each component should have score, weight, description
        for component in components.values():
            assert 'score' in component
            assert 'weight' in component
            assert 'description' in component

        # Verify weights sum to 1.0
        total_weight = sum(c['weight'] for c in components.values())
        assert abs(total_weight - 1.0) < 0.01

        # Verify interactions count
        assert explanation['interactions_analyzed'] == 10

    def test_score_clamping(self, calculator):
        """Test that scores are always clamped to [0, 1]"""
        # Even with extreme inputs, score should be in valid range
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i),
                operation_type="search",
                query=f"test {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        assert 0.0 <= score <= 1.0


# Integration test
def test_pogq_realistic_scenario():
    """Test PoGQ with realistic user interaction patterns"""
    calculator = PoGQCalculator()

    # Simulate a genuine user learning NixOS over time
    interactions = []
    base_time = datetime.now()

    # Week 1: Learning basics, some failures
    queries_week1 = [
        "install vim",
        "how to install vim",
        "vim",
        "install text editor",
        "what is nix",
    ]
    for i, query in enumerate(queries_week1):
        interactions.append(Interaction(
            timestamp=base_time + timedelta(days=i),
            operation_type="search",
            query=query,
            success=i > 1,  # First 2 fail, rest succeed
            duration_ms=1500.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        ))

    # Week 2: More diverse, better success
    queries_week2 = [
        "install firefox",
        "configure git",
        "setup python development environment",
        "install postgresql",
        "how to use nix-shell",
    ]
    for i, query in enumerate(queries_week2):
        interactions.append(Interaction(
            timestamp=base_time + timedelta(days=7+i),
            operation_type="search",
            query=query,
            success=True,  # All succeed
            duration_ms=1200.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        ))

    # Calculate score
    score = calculator.calculate(interactions)
    explanation = calculator.get_explanation(interactions)

    # Should show good genuine behavior
    assert score > 0.6  # Good score for genuine learning user
    assert explanation['components']['diversity']['score'] > 0.7
    assert explanation['components']['progression']['score'] > 0.5

    print(f"✅ PoGQ realistic scenario test passed!")
    print(f"   Score: {score:.3f}")
    print(f"   Diversity: {explanation['components']['diversity']['score']:.3f}")
    print(f"   Coherence: {explanation['components']['coherence']['score']:.3f}")
    print(f"   Progression: {explanation['components']['progression']['score']:.3f}")
    print(f"   Interpretation: {explanation['interpretation']}")
