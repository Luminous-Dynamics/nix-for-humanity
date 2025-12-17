"""
Test-Driven Development: PQC Integration

Tests for integrating PQC encryption throughout the system.

Based on: Week 9-10 PQC Integration
Depends on: Week 8 PQC Foundation
"""

import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


# === Test State Manager Integration ===

def test_state_manager_uses_pqc_by_default():
    """Test that StateManager uses PQC encryption by default"""
    from luminous_nix.core.state_manager import StateManager, OperationState, OperationStatus

    # Create state manager with encryption enabled
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)
        manager = StateManager(storage_dir=storage_dir, encryption_enabled=True)

        # Create and save state
        state = OperationState()
        state.operation_id = "test_encrypted"
        state.user_query = "install firefox"
        state.status = OperationStatus.PLANNING

        # Save state
        success = manager.save_state(state)
        assert success

        # Verify file is encrypted (shouldn't contain plaintext)
        state_files = list(storage_dir.glob("*.encrypted"))
        assert len(state_files) == 1

        encrypted_content = state_files[0].read_bytes()
        assert b"install firefox" not in encrypted_content
        assert b"test_encrypted" not in encrypted_content

        # Verify we can load it back
        loaded_state = manager.load_state("test_encrypted")
        assert loaded_state is not None
        assert loaded_state.operation_id == "test_encrypted"
        assert loaded_state.user_query == "install firefox"


def test_state_manager_encryption_can_be_disabled():
    """Test that encryption can be disabled for backward compatibility"""
    from luminous_nix.core.state_manager import StateManager, OperationState, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)
        manager = StateManager(storage_dir=storage_dir, encryption_enabled=False)

        # Create and save state
        state = OperationState()
        state.operation_id = "test_plain"
        state.user_query = "search vim"
        state.status = OperationStatus.COMPLETED

        # Save state
        success = manager.save_state(state)
        assert success

        # Verify file is NOT encrypted (should contain plaintext)
        state_files = list(storage_dir.glob("*.json"))
        assert len(state_files) == 1

        content = state_files[0].read_text()
        assert "search vim" in content or "test_plain" in content


def test_state_manager_migrates_unencrypted_to_encrypted():
    """Test migration from unencrypted to encrypted storage"""
    from luminous_nix.core.state_manager import StateManager, OperationState, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)

        # Step 1: Save unencrypted state
        manager_plain = StateManager(storage_dir=storage_dir, encryption_enabled=False)
        state = OperationState()
        state.operation_id = "migrate_test"
        state.user_query = "list packages"
        state.status = OperationStatus.COMPLETED
        manager_plain.save_state(state)

        # Step 2: Load with encryption enabled - should migrate
        manager_encrypted = StateManager(storage_dir=storage_dir, encryption_enabled=True)
        loaded_state = manager_encrypted.load_state("migrate_test")

        # Verify loaded correctly
        assert loaded_state is not None
        assert loaded_state.operation_id == "migrate_test"
        assert loaded_state.user_query == "list packages"

        # Verify migrated to encrypted format
        encrypted_files = list(storage_dir.glob("*.encrypted"))
        assert len(encrypted_files) == 1


# === Test Key Management ===

def test_key_management_generate_keys():
    """Test key generation through key manager"""
    from luminous_nix.core.key_manager import KeyManager

    with tempfile.TemporaryDirectory() as tmpdir:
        key_dir = Path(tmpdir)
        manager = KeyManager(key_dir=key_dir)

        # Generate new key pair
        success = manager.generate_key_pair("default")
        assert success

        # Verify keys exist
        assert (key_dir / "default_public.pem").exists()
        assert (key_dir / "default_private.pem").exists()

        # Verify can load keys
        public_key = manager.load_public_key("default")
        private_key = manager.load_private_key("default")
        assert public_key is not None
        assert private_key is not None


def test_key_management_rotate_keys():
    """Test key rotation"""
    from luminous_nix.core.key_manager import KeyManager

    with tempfile.TemporaryDirectory() as tmpdir:
        key_dir = Path(tmpdir)
        manager = KeyManager(key_dir=key_dir)

        # Generate initial key pair
        manager.generate_key_pair("default")
        old_public = manager.load_public_key("default")

        # Rotate keys
        success = manager.rotate_keys("default")
        assert success

        # Verify new keys exist
        new_public = manager.load_public_key("default")
        assert new_public is not None

        # Verify keys are different (by comparing serialized forms)
        from luminous_nix.security.pqc import PQCKeyManager
        pqc_manager = PQCKeyManager()
        old_pem = pqc_manager.serialize_public_key(old_public)
        new_pem = pqc_manager.serialize_public_key(new_public)
        assert old_pem != new_pem


def test_key_management_list_keys():
    """Test listing available keys"""
    from luminous_nix.core.key_manager import KeyManager

    with tempfile.TemporaryDirectory() as tmpdir:
        key_dir = Path(tmpdir)
        manager = KeyManager(key_dir=key_dir)

        # Generate multiple key pairs
        manager.generate_key_pair("default")
        manager.generate_key_pair("backup")
        manager.generate_key_pair("test")

        # List keys
        keys = manager.list_keys()
        assert len(keys) == 3
        assert "default" in keys
        assert "backup" in keys
        assert "test" in keys


# === Test Encrypted Backups ===

def test_backup_creates_encrypted_archive():
    """Test creating encrypted backup of operation history"""
    from luminous_nix.core.backup_manager import BackupManager
    from luminous_nix.core.state_manager import StateManager, OperationState, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir) / "storage"
        backup_dir = Path(tmpdir) / "backups"
        storage_dir.mkdir()
        backup_dir.mkdir()

        # Create some operation states
        manager = StateManager(storage_dir=storage_dir, encryption_enabled=True)
        for i in range(5):
            state = OperationState()
            state.operation_id = f"op_{i}"
            state.user_query = f"operation {i}"
            state.status = OperationStatus.COMPLETED
            manager.save_state(state)

        # Create backup
        backup_manager = BackupManager(storage_dir=storage_dir, backup_dir=backup_dir)
        backup_path = backup_manager.create_backup()

        # Verify backup created and encrypted
        assert backup_path.exists()
        assert backup_path.suffix == ".encrypted"

        # Verify backup is encrypted
        backup_content = backup_path.read_bytes()
        assert b"operation" not in backup_content


def test_backup_restore_from_encrypted_archive():
    """Test restoring from encrypted backup"""
    from luminous_nix.core.backup_manager import BackupManager
    from luminous_nix.core.state_manager import StateManager, OperationState, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir) / "storage"
        backup_dir = Path(tmpdir) / "backups"
        restore_dir = Path(tmpdir) / "restored"
        storage_dir.mkdir()
        backup_dir.mkdir()

        # Create states and backup
        manager = StateManager(storage_dir=storage_dir, encryption_enabled=True)
        state = OperationState()
        state.operation_id = "restore_test"
        state.user_query = "important operation"
        state.status = OperationStatus.COMPLETED
        manager.save_state(state)

        backup_manager = BackupManager(storage_dir=storage_dir, backup_dir=backup_dir)
        backup_path = backup_manager.create_backup()

        # Restore to new location
        restore_dir.mkdir()
        success = backup_manager.restore_backup(backup_path, restore_dir)
        assert success

        # Verify restored correctly
        restored_manager = StateManager(storage_dir=restore_dir, encryption_enabled=True)
        restored_state = restored_manager.load_state("restore_test")
        assert restored_state is not None
        assert restored_state.user_query == "important operation"


def test_backup_automatic_rotation():
    """Test automatic backup rotation (keep last N backups)"""
    from luminous_nix.core.backup_manager import BackupManager
    from luminous_nix.core.state_manager import StateManager, OperationState, OperationStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir) / "storage"
        backup_dir = Path(tmpdir) / "backups"
        storage_dir.mkdir()
        backup_dir.mkdir()

        # Create manager with max 3 backups
        manager = StateManager(storage_dir=storage_dir, encryption_enabled=True)
        state = OperationState()
        state.operation_id = "rotation_test"
        state.status = OperationStatus.COMPLETED
        manager.save_state(state)

        backup_manager = BackupManager(
            storage_dir=storage_dir,
            backup_dir=backup_dir,
            max_backups=3
        )

        # Create 5 backups
        for i in range(5):
            backup_manager.create_backup()

        # Verify only 3 backups exist
        backups = list(backup_dir.glob("*.encrypted"))
        assert len(backups) == 3


# === Test Configuration ===

def test_config_encryption_enabled_by_default():
    """Test that encryption is enabled by default in config"""
    from luminous_nix.config.settings import Settings

    settings = Settings()
    assert settings.encryption_enabled is True


def test_config_can_specify_key_location():
    """Test specifying custom key location"""
    from luminous_nix.config.settings import Settings

    with tempfile.TemporaryDirectory() as tmpdir:
        key_dir = Path(tmpdir) / "custom_keys"
        key_dir.mkdir()

        settings = Settings(key_directory=key_dir)
        assert settings.key_directory == key_dir


# === Test Performance ===

def test_encrypted_operations_performance():
    """Test that encrypted operations complete in reasonable time"""
    from luminous_nix.core.state_manager import StateManager, OperationState, OperationStatus
    import time

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)
        manager = StateManager(storage_dir=storage_dir, encryption_enabled=True)

        # Create state
        state = OperationState()
        state.operation_id = "perf_test"
        state.user_query = "performance test"
        state.status = OperationStatus.COMPLETED

        # Measure save time
        start = time.time()
        manager.save_state(state)
        save_time = time.time() - start

        # Should be fast (< 0.5 seconds including encryption)
        assert save_time < 0.5

        # Measure load time
        start = time.time()
        loaded = manager.load_state("perf_test")
        load_time = time.time() - start

        # Should be fast (< 0.5 seconds including decryption)
        assert load_time < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
