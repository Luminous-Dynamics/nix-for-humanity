"""
Tests for Mycelix Identity System (Layer 7 Phase 1)

Tests:
- DID creation
- DID loading
- DID format validation
- Storage and retrieval
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from luminous_nix.mycelix.identity import DIDManager, LuminousNixDID


class TestDIDManager:
    """Test DID Manager functionality."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def did_manager(self, temp_storage):
        """Create DID manager with temporary storage."""
        return DIDManager(storage_path=temp_storage / "identity")

    def test_create_did_with_passphrase(self, did_manager):
        """Test creating a new DID with custom passphrase."""
        passphrase = "my_secure_passphrase_123"

        # Create DID
        did = did_manager.create_did(passphrase)

        # Verify DID format
        assert did.did.startswith("did:mycelix:luminous_nix:")
        assert len(did.did.split(":")[-1]) == 16  # Hash is 16 chars

        # Verify attributes
        assert did.public_key is not None
        assert did.private_key_encrypted is not None
        assert did.assurance_level == "E0"
        assert did.recovery_guardians == []
        assert did.recovery_threshold == 0

        # Verify created_at timestamp
        from datetime import datetime
        created_time = datetime.fromisoformat(did.created_at)
        assert created_time is not None

    def test_create_did_without_passphrase(self, did_manager):
        """Test creating DID without passphrase (dev mode)."""
        # Should generate random passphrase
        did = did_manager.create_did(passphrase=None)

        assert did.did.startswith("did:mycelix:luminous_nix:")
        assert did.assurance_level == "E0"

    def test_load_existing_did(self, did_manager):
        """Test loading an existing DID."""
        passphrase = "test_passphrase"

        # Create DID
        original_did = did_manager.create_did(passphrase)

        # Load DID
        loaded_did = did_manager.load_did(passphrase)

        # Verify loaded DID matches original
        assert loaded_did.did == original_did.did
        assert loaded_did.public_key == original_did.public_key
        assert loaded_did.created_at == original_did.created_at
        assert loaded_did.assurance_level == original_did.assurance_level

    def test_load_nonexistent_did(self, did_manager):
        """Test loading DID when none exists."""
        with pytest.raises(FileNotFoundError):
            did_manager.load_did("any_passphrase")

    def test_load_did_wrong_passphrase(self, did_manager):
        """Test loading DID with wrong passphrase."""
        # Create DID with correct passphrase
        did_manager.create_did("correct_passphrase")

        # Try to load with wrong passphrase
        with pytest.raises(ValueError, match="Invalid passphrase"):
            did_manager.load_did("wrong_passphrase")

    def test_create_or_load_creates_new(self, did_manager):
        """Test create_or_load creates new DID when none exists."""
        passphrase = "test_passphrase"

        did = did_manager.create_or_load(passphrase)

        assert did.did.startswith("did:mycelix:luminous_nix:")
        assert did.assurance_level == "E0"

    def test_create_or_load_loads_existing(self, did_manager):
        """Test create_or_load loads existing DID."""
        passphrase = "test_passphrase"

        # Create first time
        did1 = did_manager.create_or_load(passphrase)

        # Create or load second time (should load)
        did2 = did_manager.create_or_load(passphrase)

        # Should be the same DID
        assert did1.did == did2.did
        assert did1.created_at == did2.created_at

    def test_did_storage_file_permissions(self, did_manager):
        """Test that DID file has proper permissions (600)."""
        passphrase = "test_passphrase"

        did_manager.create_did(passphrase)

        # Check file permissions
        did_file = did_manager.did_file
        assert did_file.exists()

        # Permissions should be 0o600 (readable/writable only by owner)
        import stat
        file_stat = did_file.stat()
        permissions = stat.filemode(file_stat.st_mode)
        assert permissions == "-rw-------"

    def test_get_current_did_exists(self, did_manager):
        """Test getting current DID when it exists."""
        # Create DID
        did_manager.create_did("passphrase")

        # Get current DID
        current = did_manager.get_current_did()

        assert current is not None
        assert current.did.startswith("did:mycelix:luminous_nix:")

    def test_get_current_did_not_exists(self, did_manager):
        """Test getting current DID when none exists."""
        current = did_manager.get_current_did()
        assert current is None


class TestLuminousNixDID:
    """Test LuminousNixDID dataclass."""

    def test_did_dataclass_creation(self):
        """Test creating LuminousNixDID instance."""
        from datetime import datetime

        did = LuminousNixDID(
            did="did:mycelix:luminous_nix:abc123",
            public_key="pubkey123",
            private_key_encrypted="encrypted_privkey",
            created_at=datetime.now().isoformat(),
            assurance_level="E0",
            recovery_guardians=[],
            recovery_threshold=0
        )

        assert did.did == "did:mycelix:luminous_nix:abc123"
        assert did.assurance_level == "E0"

    def test_did_format_validation(self):
        """Test DID format follows specification."""
        from datetime import datetime

        did = LuminousNixDID(
            did="did:mycelix:luminous_nix:0123456789abcdef",
            public_key="pubkey",
            private_key_encrypted="encrypted",
            created_at=datetime.now().isoformat(),
            assurance_level="E0",
            recovery_guardians=[],
            recovery_threshold=0
        )

        # Split DID into parts
        parts = did.did.split(":")
        assert len(parts) == 4
        assert parts[0] == "did"
        assert parts[1] == "mycelix"
        assert parts[2] == "luminous_nix"
        assert len(parts[3]) == 16  # Hash should be 16 chars


# Integration test
def test_end_to_end_did_workflow():
    """Test complete DID workflow from creation to loading."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "identity"

        # Create manager
        manager = DIDManager(storage_path=storage_path)

        # Create DID
        passphrase = "my_secret_passphrase"
        did = manager.create_did(passphrase)

        # Verify DID was saved
        assert manager.did_file.exists()

        # Create new manager instance (simulate restart)
        manager2 = DIDManager(storage_path=storage_path)

        # Load DID
        loaded_did = manager2.load_did(passphrase)

        # Verify loaded DID matches original
        assert loaded_did.did == did.did
        assert loaded_did.public_key == did.public_key

        print(f"✅ End-to-end test passed! DID: {did.did}")
