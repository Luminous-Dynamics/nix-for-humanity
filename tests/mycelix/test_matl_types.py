"""Tests for MATL data types"""

import pytest
from datetime import datetime

from luminous_nix.mycelix.trust.matl_types import Interaction, MATLScore


class TestInteraction:
    """Test Interaction dataclass"""

    def test_create_interaction(self):
        """Test creating an Interaction"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="install firefox",
            success=True,
            duration_ms=1500.0,
            user_did="did:mycelix:luminous_nix:test123",
            assurance_level="E0",
            packages_found=5
        )

        assert interaction.operation_type == "search"
        assert interaction.success is True
        assert interaction.packages_found == 5

    def test_interaction_serialization(self):
        """Test Interaction to_dict() and from_dict()"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="firefox",
            success=True,
            duration_ms=2000.0,
            user_did="did:mycelix:luminous_nix:abc123",
            assurance_level="E0"
        )

        # Serialize
        data = interaction.to_dict()
        assert data['operation_type'] == "install"
        assert data['query'] == "firefox"
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], str)  # Should be ISO format string

        # Deserialize
        interaction2 = Interaction.from_dict(data)
        assert interaction2.operation_type == interaction.operation_type
        assert interaction2.query == interaction.query
        assert interaction2.timestamp == interaction.timestamp


class TestMATLScore:
    """Test MATLScore dataclass"""

    def test_create_matl_score(self):
        """Test creating a MATLScore"""
        score = MATLScore(
            total_score=0.85,
            pogq_score=0.9,
            tcdm_score=0.8,
            entropy_score=0.85,
            interactions_count=100,
            first_interaction=datetime.now(),
            last_interaction=datetime.now()
        )

        assert score.total_score == 0.85
        assert score.pogq_score == 0.9
        assert score.interactions_count == 100

    def test_matl_score_serialization(self):
        """Test MATLScore to_dict() and from_dict()"""
        score = MATLScore(
            total_score=0.75,
            pogq_score=0.8,
            tcdm_score=0.7,
            entropy_score=0.75,
            interactions_count=50,
            first_interaction=datetime.now(),
            last_interaction=datetime.now(),
            components={'custom': 0.6}
        )

        # Serialize
        data = score.to_dict()
        assert data['total_score'] == 0.75
        assert data['interactions_count'] == 50
        assert 'first_interaction' in data

        # Deserialize
        score2 = MATLScore.from_dict(data)
        assert score2.total_score == score.total_score
        assert score2.interactions_count == score.interactions_count
