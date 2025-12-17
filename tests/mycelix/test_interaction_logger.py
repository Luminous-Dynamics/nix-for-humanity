"""Tests for Interaction Logger"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta

from luminous_nix.mycelix.trust import Interaction, InteractionLogger


class TestInteractionLogger:
    """Test InteractionLogger"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_log_interaction(self, temp_storage):
        """Test logging a single interaction"""
        logger = InteractionLogger(storage_path=temp_storage)

        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1500.0,
            user_did="did:mycelix:luminous_nix:test123",
            assurance_level="E0",
            packages_found=5
        )

        logger.log_interaction(interaction)

        # Verify log file was created
        log_files = list(temp_storage.glob("interactions_*.jsonl"))
        assert len(log_files) == 1

    def test_get_interactions(self, temp_storage):
        """Test retrieving logged interactions"""
        logger = InteractionLogger(storage_path=temp_storage)

        # Log some interactions
        for i in range(3):
            interaction = Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query=f"package{i}",
                success=True,
                duration_ms=1000.0 + i * 100,
                user_did="did:mycelix:luminous_nix:test123",
                assurance_level="E0"
            )
            logger.log_interaction(interaction)

        # Retrieve interactions
        interactions = logger.get_interactions()
        assert len(interactions) == 3
        assert interactions[0].query == "package0"

    def test_filter_by_user_did(self, temp_storage):
        """Test filtering interactions by user DID"""
        logger = InteractionLogger(storage_path=temp_storage)

        # Log interactions for different users
        for i, did in enumerate(["did:mycelix:luminous_nix:user1", "did:mycelix:luminous_nix:user2"]):
            interaction = Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query=f"package{i}",
                success=True,
                duration_ms=1000.0,
                user_did=did,
                assurance_level="E0"
            )
            logger.log_interaction(interaction)

        # Filter by user1
        user1_interactions = logger.get_interactions(user_did="did:mycelix:luminous_nix:user1")
        assert len(user1_interactions) == 1
        assert user1_interactions[0].user_did == "did:mycelix:luminous_nix:user1"

    def test_filter_by_time(self, temp_storage):
        """Test filtering interactions by time"""
        logger = InteractionLogger(storage_path=temp_storage)

        # Log interactions at different times
        past = datetime.now() - timedelta(hours=2)
        recent = datetime.now()

        logger.log_interaction(Interaction(
            timestamp=past,
            operation_type="search",
            query="old",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:luminous_nix:test",
            assurance_level="E0"
        ))

        logger.log_interaction(Interaction(
            timestamp=recent,
            operation_type="search",
            query="new",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:luminous_nix:test",
            assurance_level="E0"
        ))

        # Filter by time (only recent)
        since = datetime.now() - timedelta(hours=1)
        recent_interactions = logger.get_interactions(since=since)
        assert len(recent_interactions) == 1
        assert recent_interactions[0].query == "new"

    def test_get_interaction_count(self, temp_storage):
        """Test getting interaction count"""
        logger = InteractionLogger(storage_path=temp_storage)

        # Initially should be 0
        assert logger.get_interaction_count() == 0

        # Log some interactions
        for i in range(5):
            logger.log_interaction(Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query=f"package{i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:luminous_nix:test",
                assurance_level="E0"
            ))

        # Should now be 5
        assert logger.get_interaction_count() == 5


# Integration test
def test_complete_interaction_logging():
    """Test complete interaction logging workflow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)
        logger = InteractionLogger(storage_path=storage_path)

        # Simulate user workflow
        user_did = "did:mycelix:luminous_nix:testuser"

        # 1. Search for package
        logger.log_interaction(Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1500.0,
            user_did=user_did,
            assurance_level="E0",
            packages_found=5
        ))

        # 2. Install package
        logger.log_interaction(Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="firefox",
            success=True,
            duration_ms=3000.0,
            user_did=user_did,
            assurance_level="E0",
            packages_installed=1
        ))

        # Verify interactions were logged
        interactions = logger.get_interactions(user_did=user_did)
        assert len(interactions) == 2
        assert interactions[0].operation_type == "search"
        assert interactions[1].operation_type == "install"

        # Verify count
        assert logger.get_interaction_count(user_did=user_did) == 2

        print("✅ Complete interaction logging test passed!")
