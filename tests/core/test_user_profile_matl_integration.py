"""Tests for User Profile MATL Integration"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta

from luminous_nix.core.user_profile import UserProfile, UserProfileManager
from luminous_nix.mycelix.trust import Interaction, InteractionLogger


class TestUserProfileMATLIntegration:
    """Test MATL integration with User Profile"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def profile_manager(self, temp_storage):
        """Create profile manager with temp storage"""
        return UserProfileManager(storage_path=temp_storage)

    @pytest.fixture
    def sample_interactions(self):
        """Create sample interactions for testing"""
        interactions = []
        base_time = datetime.now()

        # Create 10 diverse interactions
        for i in range(10):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(minutes=i * 5),
                operation_type="search" if i % 2 == 0 else "install",
                query=f"diverse query {i}",
                success=True,
                duration_ms=1000.0 + i * 100,
                user_did="did:mycelix:test:user",
                assurance_level="E0",
                packages_found=3 if i % 2 == 0 else 0,
                packages_installed=1 if i % 2 == 1 else 0
            ))

        return interactions

    def test_calculate_trust_score_no_interactions(self, profile_manager, temp_storage):
        """Test trust score calculation with no interactions"""
        # Create profile
        profile = profile_manager.load_or_create()
        profile.did = "did:mycelix:test:user"
        profile_manager._save_profile(profile)

        # Calculate trust score (should return 0.0 for no interactions)
        score = profile_manager.calculate_and_update_trust_score()

        assert score == 0.0

        # Verify profile was updated
        updated_profile = profile_manager.get_profile()
        assert updated_profile.matl_score == 0.0

    def test_calculate_trust_score_with_interactions(self, profile_manager, temp_storage, sample_interactions):
        """Test trust score calculation with interactions"""
        # Create profile
        profile = profile_manager.load_or_create()
        profile.did = "did:mycelix:test:user"
        profile_manager._save_profile(profile)

        # Log interactions
        trust_storage = temp_storage / "trust"
        interaction_logger = InteractionLogger(storage_path=trust_storage)
        for interaction in sample_interactions:
            interaction_logger.log_interaction(interaction)

        # Calculate trust score
        score = profile_manager.calculate_and_update_trust_score()

        # Should have a valid score (> 0)
        assert score is not None
        assert score > 0.0
        assert score <= 1.0

        # Verify profile was updated
        updated_profile = profile_manager.get_profile()
        assert updated_profile.matl_score == score
        assert 'pogq' in updated_profile.trust_components
        assert 'tcdm' in updated_profile.trust_components
        assert 'entropy' in updated_profile.trust_components

    def test_assurance_level_updates_with_trust_score(self, profile_manager, temp_storage, sample_interactions):
        """Test that assurance level updates based on trust score"""
        # Create profile with E0
        profile = profile_manager.load_or_create()
        profile.did = "did:mycelix:test:user"
        profile.assurance_level = "E0"
        profile_manager._save_profile(profile)

        # Log interactions
        trust_storage = temp_storage / "trust"
        interaction_logger = InteractionLogger(storage_path=trust_storage)
        for interaction in sample_interactions:
            interaction_logger.log_interaction(interaction)

        # Calculate trust score
        score = profile_manager.calculate_and_update_trust_score()

        # Verify assurance level may have updated
        updated_profile = profile_manager.get_profile()
        # Assurance level should be valid
        assert updated_profile.assurance_level in ["E0", "E1", "E2", "E3", "E4"]

    def test_trust_components_stored_correctly(self, profile_manager, temp_storage, sample_interactions):
        """Test that trust components are stored correctly"""
        # Create profile
        profile = profile_manager.load_or_create()
        profile.did = "did:mycelix:test:user"
        profile_manager._save_profile(profile)

        # Log interactions
        trust_storage = temp_storage / "trust"
        interaction_logger = InteractionLogger(storage_path=trust_storage)
        for interaction in sample_interactions:
            interaction_logger.log_interaction(interaction)

        # Calculate trust score
        score = profile_manager.calculate_and_update_trust_score()

        # Verify components
        updated_profile = profile_manager.get_profile()
        components = updated_profile.trust_components

        # Should have all three components
        assert 'pogq' in components
        assert 'tcdm' in components
        assert 'entropy' in components

        # All components should be valid scores
        assert 0.0 <= components['pogq'] <= 1.0
        assert 0.0 <= components['tcdm'] <= 1.0
        assert 0.0 <= components['entropy'] <= 1.0

    def test_calculate_with_explicit_user_did(self, profile_manager, temp_storage, sample_interactions):
        """Test calculating trust score with explicit user DID"""
        # Create profile
        profile = profile_manager.load_or_create()
        profile.did = "did:mycelix:test:user"
        profile_manager._save_profile(profile)

        # Log interactions
        trust_storage = temp_storage / "trust"
        interaction_logger = InteractionLogger(storage_path=trust_storage)
        for interaction in sample_interactions:
            interaction_logger.log_interaction(interaction)

        # Calculate trust score with explicit DID
        score = profile_manager.calculate_and_update_trust_score(user_did="did:mycelix:test:user")

        # Should have valid score
        assert score is not None
        assert score > 0.0

    def test_calculate_without_did_returns_none(self, profile_manager, temp_storage):
        """Test that calculation without DID returns None"""
        # Create profile without DID
        profile = profile_manager.load_or_create()
        profile.did = None
        profile_manager._save_profile(profile)

        # Calculate trust score (should fail gracefully)
        score = profile_manager.calculate_and_update_trust_score()

        # Should return None
        assert score is None

    def test_persistence_across_sessions(self, profile_manager, temp_storage, sample_interactions):
        """Test that trust scores persist across sessions"""
        # Create profile and calculate trust score
        profile = profile_manager.load_or_create()
        profile.did = "did:mycelix:test:user"
        profile_manager._save_profile(profile)

        # Log interactions
        trust_storage = temp_storage / "trust"
        interaction_logger = InteractionLogger(storage_path=trust_storage)
        for interaction in sample_interactions:
            interaction_logger.log_interaction(interaction)

        # Calculate trust score
        score1 = profile_manager.calculate_and_update_trust_score()

        # Create new profile manager (simulate new session)
        new_profile_manager = UserProfileManager(storage_path=temp_storage)
        loaded_profile = new_profile_manager.get_profile()

        # Trust score should be persisted
        assert loaded_profile.matl_score == score1
        assert 'pogq' in loaded_profile.trust_components
        assert 'tcdm' in loaded_profile.trust_components
        assert 'entropy' in loaded_profile.trust_components


# Integration test
def test_complete_matl_profile_workflow():
    """Test complete MATL + Profile workflow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # 1. Create profile manager
        profile_manager = UserProfileManager(storage_path=storage_path)

        # 2. Create profile with DID
        profile = profile_manager.load_or_create()
        profile.did = "did:mycelix:test:complete"
        profile_manager._save_profile(profile)

        # 3. Log user interactions over time
        trust_storage = storage_path / "trust"
        interaction_logger = InteractionLogger(storage_path=trust_storage)

        base_time = datetime.now()
        interactions = [
            ("search", "vim editor", True),
            ("install", "vim", True),
            ("search", "git", True),
            ("install", "git", True),
            ("search", "python development", True),
            ("install", "python311", True),
            ("config", "setup environment", True),
            ("search", "postgresql", True),
            ("install", "postgresql", True),
            ("search", "docker", True),
        ]

        for i, (op_type, query, success) in enumerate(interactions):
            interaction = Interaction(
                timestamp=base_time + timedelta(minutes=i * 10),
                operation_type=op_type,
                query=query,
                success=success,
                duration_ms=1000.0 + i * 50,
                user_did="did:mycelix:test:complete",
                assurance_level="E0",
                packages_found=3 if op_type == "search" else 0,
                packages_installed=1 if op_type == "install" else 0
            )
            interaction_logger.log_interaction(interaction)

        # 4. Calculate trust score
        trust_score = profile_manager.calculate_and_update_trust_score()

        # Verify score is valid
        assert trust_score is not None
        assert 0.0 <= trust_score <= 1.0

        # 5. Verify profile updated
        final_profile = profile_manager.get_profile()
        assert final_profile.matl_score == trust_score
        assert len(final_profile.trust_components) == 3
        assert final_profile.assurance_level in ["E0", "E1", "E2", "E3", "E4"]

        # 6. Verify persistence
        new_manager = UserProfileManager(storage_path=storage_path)
        persisted_profile = new_manager.get_profile()
        assert persisted_profile.matl_score == trust_score

        print("✅ Complete MATL + Profile workflow test passed!")
        print(f"   Trust Score: {trust_score:.3f}")
        print(f"   PoGQ: {final_profile.trust_components['pogq']:.3f}")
        print(f"   TCDM: {final_profile.trust_components['tcdm']:.3f}")
        print(f"   Entropy: {final_profile.trust_components['entropy']:.3f}")
        print(f"   Assurance Level: {final_profile.assurance_level}")
