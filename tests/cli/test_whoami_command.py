"""Tests for whoami command"""

import pytest
from pathlib import Path
import tempfile
import shutil
from io import StringIO

from luminous_nix.cli.commands.whoami import cmd_whoami
from luminous_nix.mycelix.identity import DIDManager
from luminous_nix.core.user_profile import UserProfileManager


class TestWhoamiCommand:
    """Test whoami command"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_whoami_with_did(self, temp_storage, capsys):
        """Test whoami shows DID information"""
        # Create DID
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        did_mgr.create_did(passphrase="test123")

        # Create profile
        profile_mgr = UserProfileManager(storage_path=temp_storage)
        profile_mgr.load_or_create(passphrase="test123")

        # Run whoami
        cmd_whoami(storage_path=str(temp_storage))

        # Check output
        captured = capsys.readouterr()
        assert "did:mycelix:luminous_nix:" in captured.out
        assert "Assurance Level" in captured.out
        assert "Total Operations" in captured.out

    def test_whoami_without_did(self, temp_storage, capsys):
        """Test whoami when no DID exists"""
        # Run whoami without creating DID
        cmd_whoami(storage_path=str(temp_storage))

        # Check output
        captured = capsys.readouterr()
        assert "No identity found" in captured.out
        assert "ask-nix did setup" in captured.out

    def test_whoami_with_stats(self, temp_storage, capsys):
        """Test whoami displays usage statistics"""
        # Create DID and profile
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        did_mgr.create_did(passphrase="test123")

        profile_mgr = UserProfileManager(storage_path=temp_storage)
        profile_mgr.load_or_create(passphrase="test123")

        # Add some stats
        profile_mgr.update_operation_stats(success=True)
        profile_mgr.update_operation_stats(success=True)
        profile_mgr.update_operation_stats(success=False)

        # Run whoami
        cmd_whoami(storage_path=str(temp_storage))

        # Check output
        captured = capsys.readouterr()
        assert "Total Operations" in captured.out
        assert "Success Rate" in captured.out
        assert "2/3" in captured.out  # 2 successful out of 3 total
