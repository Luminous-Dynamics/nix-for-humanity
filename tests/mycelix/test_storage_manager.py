"""Tests for StorageManager (M0-M3 tiered retention)"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from luminous_nix.mycelix.trust import Interaction
from luminous_nix.mycelix.epistemic import StorageManager, MTier


class TestStorageManager:
    """Test M-tier based storage and retention policies"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def storage_manager(self, temp_storage):
        """Create StorageManager with temp storage"""
        return StorageManager(storage_path=temp_storage)

    def test_default_retention_periods(self, storage_manager):
        """Test default retention periods"""
        assert storage_manager.retention_days[MTier.M0] == 0
        assert storage_manager.retention_days[MTier.M1] == 30
        assert storage_manager.retention_days[MTier.M2] == 365
        assert storage_manager.retention_days[MTier.M3] is None

    def test_custom_retention_periods(self, temp_storage):
        """Test custom retention periods"""
        custom_retention = {
            MTier.M1: 60,  # 2 months instead of 1
            MTier.M2: 730  # 2 years instead of 1
        }

        manager = StorageManager(
            storage_path=temp_storage,
            retention_days=custom_retention
        )

        assert manager.retention_days[MTier.M1] == 60
        assert manager.retention_days[MTier.M2] == 730
        assert manager.retention_days[MTier.M3] is None  # Still default

    def test_should_store_m0_discarded(self, storage_manager):
        """Test that M0 interactions are not stored"""
        m0_interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="query",
            query="test",
            success=False,
            duration_ms=100.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            epistemic_e=0.0,
            epistemic_n=0.0,
            epistemic_m=0  # M0: Ephemeral
        )

        assert storage_manager.should_store(m0_interaction) is False

    def test_should_store_m1_m2_m3_kept(self, storage_manager):
        """Test that M1, M2, M3 interactions are stored"""
        for m_value in [1, 2, 3]:
            interaction = Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query="test",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_e=0.5,
                epistemic_n=0.0,
                epistemic_m=m_value
            )

            assert storage_manager.should_store(interaction) is True

    def test_should_prune_m0_always(self, storage_manager):
        """Test that M0 should always be pruned"""
        m0_interaction = Interaction(
            timestamp=datetime.now() - timedelta(days=1),
            operation_type="query",
            query="test",
            success=False,
            duration_ms=100.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            epistemic_m=0
        )

        assert storage_manager.should_prune(m0_interaction) is True

    def test_should_prune_m3_never(self, storage_manager):
        """Test that M3 should never be pruned"""
        # Even very old M3 interactions
        old_m3 = Interaction(
            timestamp=datetime.now() - timedelta(days=3650),  # 10 years old!
            operation_type="search",
            query="fundamental knowledge",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            epistemic_m=3
        )

        assert storage_manager.should_prune(old_m3) is False

    def test_should_prune_m1_after_30_days(self, storage_manager):
        """Test that M1 gets pruned after 30 days"""
        # 29 days old - keep
        m1_recent = Interaction(
            timestamp=datetime.now() - timedelta(days=29),
            operation_type="query",
            query="recent query",
            success=True,
            duration_ms=500.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            epistemic_m=1
        )

        assert storage_manager.should_prune(m1_recent) is False

        # 31 days old - prune
        m1_old = Interaction(
            timestamp=datetime.now() - timedelta(days=31),
            operation_type="query",
            query="old query",
            success=True,
            duration_ms=500.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            epistemic_m=1
        )

        assert storage_manager.should_prune(m1_old) is True

    def test_should_prune_m2_after_365_days(self, storage_manager):
        """Test that M2 gets pruned after 365 days"""
        # 364 days old - keep
        m2_recent = Interaction(
            timestamp=datetime.now() - timedelta(days=364),
            operation_type="install",
            query="package",
            success=True,
            duration_ms=5000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            epistemic_m=2
        )

        assert storage_manager.should_prune(m2_recent) is False

        # 366 days old - prune
        m2_old = Interaction(
            timestamp=datetime.now() - timedelta(days=366),
            operation_type="install",
            query="old package",
            success=True,
            duration_ms=5000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            epistemic_m=2
        )

        assert storage_manager.should_prune(m2_old) is True

    def test_get_storage_stats_empty(self, storage_manager):
        """Test storage stats on empty storage"""
        stats = storage_manager.get_storage_stats()

        assert stats["total"] == 0
        assert stats["by_tier"]["M0"] == 0
        assert stats["by_tier"]["M1"] == 0
        assert stats["by_tier"]["M2"] == 0
        assert stats["by_tier"]["M3"] == 0

    def test_prune_old_interactions_dry_run(self, storage_manager, temp_storage):
        """Test dry-run mode doesn't actually delete"""
        # Create log file with mix of old and new interactions
        log_file = temp_storage / "interactions_2024-01-01.jsonl"

        interactions = [
            # Old M1 (should prune)
            Interaction(
                timestamp=datetime.now() - timedelta(days=31),
                operation_type="query",
                query="old query",
                success=True,
                duration_ms=500.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=1
            ),
            # Recent M1 (keep)
            Interaction(
                timestamp=datetime.now() - timedelta(days=15),
                operation_type="query",
                query="recent query",
                success=True,
                duration_ms=500.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=1
            ),
            # M3 (always keep)
            Interaction(
                timestamp=datetime.now() - timedelta(days=1000),
                operation_type="search",
                query="foundational",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=3
            ),
        ]

        # Write interactions
        import json
        with open(log_file, 'w') as f:
            for interaction in interactions:
                f.write(json.dumps(interaction.to_dict()) + '\n')

        # Run dry run
        stats = storage_manager.prune_old_interactions(dry_run=True)

        assert stats["scanned"] == 3
        assert stats["pruned"] == 1  # Old M1
        assert stats["kept"] == 2    # Recent M1 + M3

        # File should still have all 3 interactions (dry run)
        with open(log_file, 'r') as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 3

    def test_prune_old_interactions_actual(self, storage_manager, temp_storage):
        """Test actual pruning deletes old interactions"""
        log_file = temp_storage / "interactions_2024-01-01.jsonl"

        interactions = [
            # Old M1 (should prune)
            Interaction(
                timestamp=datetime.now() - timedelta(days=31),
                operation_type="query",
                query="old query",
                success=True,
                duration_ms=500.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=1
            ),
            # Recent M3 (keep)
            Interaction(
                timestamp=datetime.now() - timedelta(days=15),
                operation_type="search",
                query="recent",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=3
            ),
        ]

        # Write interactions
        import json
        with open(log_file, 'w') as f:
            for interaction in interactions:
                f.write(json.dumps(interaction.to_dict()) + '\n')

        # Run actual pruning
        stats = storage_manager.prune_old_interactions(dry_run=False)

        assert stats["scanned"] == 2
        assert stats["pruned"] == 1
        assert stats["kept"] == 1

        # File should now have only 1 interaction
        with open(log_file, 'r') as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 1

            # Verify it's the M3 one
            data = json.loads(lines[0])
            assert data['epistemic_m'] == 3

    def test_archive_by_tier(self, storage_manager, temp_storage):
        """Test archiving specific M-tier"""
        log_file = temp_storage / "interactions_2024-01-01.jsonl"

        interactions = [
            Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query="search1",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=3  # M3
            ),
            Interaction(
                timestamp=datetime.now(),
                operation_type="install",
                query="package1",
                success=True,
                duration_ms=5000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=2  # M2
            ),
            Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query="search2",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=3  # M3
            ),
        ]

        # Write interactions
        import json
        with open(log_file, 'w') as f:
            for interaction in interactions:
                f.write(json.dumps(interaction.to_dict()) + '\n')

        # Archive M3 interactions
        archive_path = temp_storage / "archive"
        count = storage_manager.archive_by_tier(MTier.M3, archive_path)

        assert count == 2  # 2 M3 interactions

        # Verify archive file exists and contains M3
        archive_files = list(archive_path.glob("archived_M3_*.jsonl"))
        assert len(archive_files) == 1

        with open(archive_files[0], 'r') as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 2  # 2 M3 interactions

        # Verify original file now only has M2
        with open(log_file, 'r') as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 1  # Only M2 remains
            data = json.loads(lines[0])
            assert data['epistemic_m'] == 2


def test_storage_manager_integration():
    """Integration test: full storage lifecycle"""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        manager = StorageManager(storage_path=temp_dir)
        log_file = temp_dir / "interactions_2024-01-01.jsonl"

        # Create mix of interactions
        interactions = [
            # M0 - should not store
            Interaction(
                timestamp=datetime.now(),
                operation_type="query",
                query="ephemeral",
                success=False,
                duration_ms=100.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=0
            ),
            # M1 - old, should prune
            Interaction(
                timestamp=datetime.now() - timedelta(days=35),
                operation_type="query",
                query="temporal old",
                success=True,
                duration_ms=500.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=1
            ),
            # M2 - recent, keep
            Interaction(
                timestamp=datetime.now() - timedelta(days=100),
                operation_type="install",
                query="persistent",
                success=True,
                duration_ms=5000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=2
            ),
            # M3 - always keep
            Interaction(
                timestamp=datetime.now() - timedelta(days=1000),
                operation_type="search",
                query="foundational",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0",
                epistemic_m=3
            ),
        ]

        # Write only interactions that should be stored
        import json
        with open(log_file, 'w') as f:
            for interaction in interactions:
                if manager.should_store(interaction):
                    f.write(json.dumps(interaction.to_dict()) + '\n')

        # Verify M0 was not stored (only 3 interactions)
        with open(log_file, 'r') as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 3

        # Prune old interactions
        stats = manager.prune_old_interactions(dry_run=False)

        assert stats["pruned"] == 1  # Old M1
        assert stats["kept"] == 2    # M2 + M3

        # Verify final state
        with open(log_file, 'r') as f:
            lines = [line for line in f if line.strip()]
            assert len(lines) == 2

            # Both should be M2 and M3
            m_tiers = [json.loads(line)['epistemic_m'] for line in lines]
            assert 2 in m_tiers
            assert 3 in m_tiers

    finally:
        shutil.rmtree(temp_dir)
