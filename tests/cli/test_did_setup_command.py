"""Tests for did setup command"""

import pytest
from pathlib import Path
import tempfile
import shutil

from luminous_nix.cli.commands.did_setup import cmd_did_setup
from luminous_nix.mycelix.identity import DIDManager


class TestDIDSetupCommand:
    """Test did setup command"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_did_setup_creates_new_did(self, temp_storage, capsys):
        """Test did setup creates a new DID"""
        # Run setup with auto-passphrase and force
        cmd_did_setup(
            storage_path=str(temp_storage),
            auto_passphrase="test123",
            force=True
        )

        # Check output
        captured = capsys.readouterr()
        assert "Identity Created Successfully" in captured.out
        assert "did:mycelix:luminous_nix:" in captured.out

        # Verify DID was actually created
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        current_did = did_mgr.get_current_did()
        assert current_did is not None
        assert current_did.did.startswith("did:mycelix:luminous_nix:")

    def test_did_setup_creates_profile(self, temp_storage):
        """Test did setup also creates user profile"""
        # Run setup with force
        cmd_did_setup(
            storage_path=str(temp_storage),
            auto_passphrase="test123",
            force=True
        )

        # Verify profile was created
        from luminous_nix.core.user_profile import UserProfileManager
        profile_mgr = UserProfileManager(storage_path=temp_storage)
        profile = profile_mgr.get_profile()

        assert profile is not None
        assert profile.did is not None
        assert profile.did.startswith("did:mycelix:luminous_nix:")


# Integration test
def test_setup_then_whoami():
    """Test did setup followed by whoami"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # Setup DID with force
        cmd_did_setup(
            storage_path=str(storage_path),
            auto_passphrase="test123",
            force=True
        )

        # Verify with whoami
        from luminous_nix.cli.commands.whoami import cmd_whoami
        import sys
        from io import StringIO

        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        cmd_whoami(storage_path=str(storage_path))

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Verify whoami shows the DID
        assert "did:mycelix:luminous_nix:" in output
        assert "Assurance Level" in output

        print("✅ Integration test passed: setup → whoami")
