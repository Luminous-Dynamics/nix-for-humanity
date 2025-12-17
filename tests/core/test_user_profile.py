"""
Tests for User Profile Management (Week 2)

Tests:
- Profile creation
- DID integration
- Statistics tracking
- Persistence
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from luminous_nix.core.user_profile import UserProfile, UserProfileManager
from luminous_nix.mycelix.identity import DIDManager


class TestUserProfile:
    """Test UserProfile dataclass"""

    def test_create_user_profile(self):
        """Test creating a new user profile"""
        profile = UserProfile(
            did="did:mycelix:luminous_nix:test123",
            assurance_level="E0"
        )

        assert profile.did == "did:mycelix:luminous_nix:test123"
        assert profile.assurance_level == "E0"
        assert profile.total_operations == 0
        assert profile.matl_score == 0.0

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        profile = UserProfile()

        # No operations
        assert profile.get_success_rate() == 0.0

        # Some operations
        profile.total_operations = 10
        profile.successful_operations = 8
        assert profile.get_success_rate() == 0.8

    def test_profile_serialization(self):
        """Test profile to_dict() and from_dict()"""
        profile = UserProfile(
            did="did:mycelix:luminous_nix:test123",
            total_operations=5,
            successful_operations=4
        )

        # Serialize
        data = profile.to_dict()
        assert data['did'] == "did:mycelix:luminous_nix:test123"
        assert data['total_operations'] == 5

        # Deserialize
        profile2 = UserProfile.from_dict(data)
        assert profile2.did == profile.did
        assert profile2.total_operations == profile.total_operations


class TestUserProfileManager:
    """Test UserProfileManager"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_create_new_profile(self, temp_storage):
        """Test creating a new user profile"""
        manager = UserProfileManager(storage_path=temp_storage)
        profile = manager.load_or_create(passphrase="test123")

        assert profile is not None
        assert profile.did is not None
        assert profile.did.startswith("did:mycelix:luminous_nix:")
        assert profile.assurance_level == "E0"

    def test_load_existing_profile(self, temp_storage):
        """Test loading an existing profile"""
        manager = UserProfileManager(storage_path=temp_storage)

        # Create profile
        profile1 = manager.load_or_create(passphrase="test123")
        original_did = profile1.did

        # Load profile (should be same)
        profile2 = manager.load_or_create(passphrase="test123")
        assert profile2.did == original_did

    def test_update_operation_stats(self, temp_storage):
        """Test updating operation statistics"""
        manager = UserProfileManager(storage_path=temp_storage)
        manager.load_or_create(passphrase="test123")

        # Update stats
        manager.update_operation_stats(success=True)
        manager.update_operation_stats(success=True)
        manager.update_operation_stats(success=False)

        # Verify
        profile = manager.get_profile()
        assert profile.total_operations == 3
        assert profile.successful_operations == 2
        assert profile.get_success_rate() == 2/3

    def test_update_trust_score(self, temp_storage):
        """Test updating MATL trust score"""
        manager = UserProfileManager(storage_path=temp_storage)
        manager.load_or_create(passphrase="test123")

        # Update trust score
        components = {
            'pogq': 0.8,
            'tcdm': 0.7,
            'entropy': 0.9
        }
        manager.update_trust_score(matl_score=0.8, components=components)

        # Verify
        profile = manager.get_profile()
        assert profile.matl_score == 0.8
        assert profile.trust_components == components

    def test_profile_persistence(self, temp_storage):
        """Test that profile persists across manager instances"""
        # Create profile
        manager1 = UserProfileManager(storage_path=temp_storage)
        profile1 = manager1.load_or_create(passphrase="test123")
        manager1.update_operation_stats(success=True)

        # Create new manager (simulate restart)
        manager2 = UserProfileManager(storage_path=temp_storage)
        profile2 = manager2.get_profile()

        # Verify persistence
        assert profile2 is not None
        assert profile2.did == profile1.did
        assert profile2.total_operations == 1

    def test_get_profile_when_none_exists(self, temp_storage):
        """Test get_profile returns None when no profile exists"""
        manager = UserProfileManager(storage_path=temp_storage)
        profile = manager.get_profile()
        assert profile is None


# Integration test
def test_complete_profile_flow():
    """Test complete profile workflow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # Step 1: Create profile
        manager = UserProfileManager(storage_path=storage_path)
        profile = manager.load_or_create(passphrase="test123")
        print(f"✅ Created profile with DID: {profile.did}")

        # Step 2: Update stats
        manager.update_operation_stats(success=True)
        manager.update_operation_stats(success=True)
        manager.update_operation_stats(success=False)
        print(f"✅ Updated stats: {profile.total_operations} operations")

        # Step 3: Update trust
        manager.update_trust_score(0.75, {'pogq': 0.8, 'tcdm': 0.7})
        print(f"✅ Updated trust score: {profile.matl_score}")

        # Step 4: Load profile (simulate restart)
        manager2 = UserProfileManager(storage_path=storage_path)
        profile2 = manager2.get_profile()

        # Verify
        assert profile2.did == profile.did
        assert profile2.total_operations == 3
        assert profile2.successful_operations == 2
        assert profile2.matl_score == 0.75

        print(f"✅ Profile persisted across restart!")
        print(f"   DID: {profile2.did}")
        print(f"   Operations: {profile2.total_operations}")
        print(f"   Success Rate: {profile2.get_success_rate():.2%}")
        print(f"   Trust Score: {profile2.matl_score}")
