"""Tests for Entropy (Diversity) Calculator"""

import pytest
from datetime import datetime, timedelta

from luminous_nix.mycelix.trust import Interaction
from luminous_nix.mycelix.trust.entropy import EntropyCalculator


class TestEntropyCalculator:
    """Test Entropy Calculator"""

    @pytest.fixture
    def calculator(self):
        """Create Entropy calculator instance"""
        return EntropyCalculator()

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
        # Create 10 diverse queries on different topics
        queries = [
            "install vim editor",
            "search for web browser firefox",
            "how to configure git",
            "python development environment setup",
            "install postgresql database",
            "update system packages",
            "remove old kernels",
            "create flake for nodejs",
            "find markdown editors",
            "configure ssh keys"
        ]

        interactions = []
        for i, query in enumerate(queries):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search",
                query=query,
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
        # Create 10 nearly identical queries
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search",
                query="install vim",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Low diversity should yield low score (< 0.5)
        assert score < 0.5

    def test_operation_diversity(self, calculator):
        """Test that diverse operation types score well"""
        operations = ["search", "install", "update", "search", "config",
                     "flake", "search", "install", "remove", "search"]

        interactions = []
        for i, op_type in enumerate(operations):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type=op_type,
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        explanation = calculator.get_explanation(interactions)

        # Should have good operation diversity
        assert explanation['components']['operation_diversity']['score'] > 0.6

    def test_learning_progression_improving(self, calculator):
        """Test that improving behavior scores well"""
        interactions = []
        base_time = datetime.now()

        # Early interactions: simple, some failures
        for i in range(5):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(seconds=i * 60),
                operation_type="search",
                query=f"vim",  # Simple queries
                success=i >= 2,  # 60% success
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        # Later interactions: more complex, better success
        for i in range(5, 10):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(seconds=i * 60),
                operation_type="install" if i % 2 == 0 else "search",
                query=f"configure python development environment with poetry",  # Complex queries
                success=True,  # 100% success
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        explanation = calculator.get_explanation(interactions)

        # Should show learning progression
        assert explanation['components']['learning_progression']['score'] > 0.5

    def test_balanced_exploration_adoption(self, calculator):
        """Test that balanced exploration and adoption scores well"""
        interactions = []
        base_time = datetime.now()

        # Mix of search (exploration) and install (adoption)
        # 60% search, 40% install is ideal
        for i in range(10):
            op_type = "search" if i < 6 else "install"
            interactions.append(Interaction(
                timestamp=base_time + timedelta(seconds=i * 60),
                operation_type=op_type,
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                packages_found=5 if op_type == "search" else 0,
                packages_installed=1 if op_type == "install" else 0
            ))

        score = calculator.calculate(interactions)
        # Should score well for balanced behavior
        assert score > 0.5

    def test_exploration_without_adoption(self, calculator):
        """Test that excessive exploration without adoption scores lower"""
        # All search, no install (indecisive behavior)
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search",
                query=f"search query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                packages_found=5
            ))

        score = calculator.calculate(interactions)
        explanation = calculator.get_explanation(interactions)

        # Should have lower score for imbalanced behavior
        assert explanation['components']['operation_diversity']['score'] < 0.8

    def test_get_explanation(self, calculator):
        """Test that explanation provides component breakdown"""
        interactions = []
        for i in range(10):
            interactions.append(Interaction(
                timestamp=datetime.now() + timedelta(seconds=i * 60),
                operation_type="search" if i % 2 == 0 else "install",
                query=f"diverse query {i}",
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
        assert 'query_diversity' in components
        assert 'operation_diversity' in components
        assert 'learning_progression' in components

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
                timestamp=datetime.now() + timedelta(seconds=i * 60),
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
def test_entropy_realistic_scenario():
    """Test Entropy with realistic user learning journey"""
    calculator = EntropyCalculator()

    # Simulate a user's learning journey over 2 weeks
    interactions = []
    base_time = datetime.now()

    # Week 1: Beginner - exploring basics
    week1_queries = [
        ("search", "vim", True),
        ("search", "vim editor", True),
        ("install", "vim", True),
        ("search", "git", True),
        ("search", "how to use git", True),
        ("install", "git", True),
        ("search", "firefox", True),
        ("install", "firefox", True),
    ]

    for i, (op_type, query, success) in enumerate(week1_queries):
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

    # Week 2: Intermediate - more complex, diverse topics
    week2_queries = [
        ("search", "python development environment", True),
        ("search", "poetry python package manager", True),
        ("install", "python311", True),
        ("install", "poetry", True),
        ("config", "setup python environment", True),
        ("search", "postgresql database", True),
        ("install", "postgresql", True),
        ("flake", "create python dev flake", True),
    ]

    for i, (op_type, query, success) in enumerate(week2_queries):
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

    # Calculate score
    score = calculator.calculate(interactions)
    explanation = calculator.get_explanation(interactions)

    # Should show good diversity and learning
    assert score > 0.6  # Good score for learning user
    assert explanation['components']['query_diversity']['score'] > 0.6
    assert explanation['components']['operation_diversity']['score'] > 0.6
    assert explanation['components']['learning_progression']['score'] > 0.5

    print(f"✅ Entropy realistic scenario test passed!")
    print(f"   Score: {score:.3f}")
    print(f"   Query Diversity: {explanation['components']['query_diversity']['score']:.3f}")
    print(f"   Operation Diversity: {explanation['components']['operation_diversity']['score']:.3f}")
    print(f"   Learning Progression: {explanation['components']['learning_progression']['score']:.3f}")
    print(f"   Interpretation: {explanation['interpretation']}")
