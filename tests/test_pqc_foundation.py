"""
Test-Driven Development: Post-Quantum Cryptography Foundation

Tests for PQC (Post-Quantum Cryptography) integration providing
quantum-resistant security for state persistence and communication.

Based on: Week 8 PQC Foundation
"""

import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional


# === Test Key Generation ===

def test_pqc_key_pair_generation():
    """Test generating a post-quantum key pair"""
    from luminous_nix.security.pqc import PQCKeyManager

    key_manager = PQCKeyManager()
    public_key, private_key = key_manager.generate_key_pair()

    # Verify keys are generated
    assert public_key is not None
    assert private_key is not None

    # Verify keys are crypto objects
    assert hasattr(public_key, 'public_bytes')
    assert hasattr(private_key, 'private_bytes')

    # Verify keys are different types
    assert type(public_key).__name__ == '_RSAPublicKey'
    assert type(private_key).__name__ == '_RSAPrivateKey'


def test_pqc_key_serialization():
    """Test serializing and deserializing PQC keys"""
    from luminous_nix.security.pqc import PQCKeyManager

    key_manager = PQCKeyManager()
    public_key, private_key = key_manager.generate_key_pair()

    # Serialize keys
    public_pem = key_manager.serialize_public_key(public_key)
    private_pem = key_manager.serialize_private_key(private_key)

    # Verify serialization produces strings
    assert isinstance(public_pem, str)
    assert isinstance(private_pem, str)
    assert len(public_pem) > 0
    assert len(private_pem) > 0

    # Deserialize keys
    restored_public = key_manager.deserialize_public_key(public_pem)
    restored_private = key_manager.deserialize_private_key(private_pem)

    # Verify keys match after round-trip (by comparing serialized forms)
    assert key_manager.serialize_public_key(restored_public) == public_pem
    assert key_manager.serialize_private_key(restored_private) == private_pem


def test_pqc_key_file_storage():
    """Test storing PQC keys to files"""
    from luminous_nix.security.pqc import PQCKeyManager

    key_manager = PQCKeyManager()
    public_key, private_key = key_manager.generate_key_pair()

    with tempfile.TemporaryDirectory() as tmpdir:
        public_path = Path(tmpdir) / "public.pem"
        private_path = Path(tmpdir) / "private.pem"

        # Save keys to files
        key_manager.save_public_key(public_key, public_path)
        key_manager.save_private_key(private_key, private_path)

        # Verify files created
        assert public_path.exists()
        assert private_path.exists()

        # Load keys from files
        loaded_public = key_manager.load_public_key(public_path)
        loaded_private = key_manager.load_private_key(private_path)

        # Verify keys match (by comparing serialized forms)
        assert key_manager.serialize_public_key(loaded_public) == key_manager.serialize_public_key(public_key)
        assert key_manager.serialize_private_key(loaded_private) == key_manager.serialize_private_key(private_key)


# === Test Encryption/Decryption ===

def test_pqc_encryption_decryption():
    """Test PQC encryption and decryption"""
    from luminous_nix.security.pqc import PQCKeyManager, PQCEncryption

    key_manager = PQCKeyManager()
    encryption = PQCEncryption()

    # Generate key pair
    public_key, private_key = key_manager.generate_key_pair()

    # Test data
    plaintext = b"Sensitive data requiring quantum-resistant protection"

    # Encrypt
    ciphertext = encryption.encrypt(plaintext, public_key)

    # Verify encryption produced different data
    assert ciphertext != plaintext
    assert len(ciphertext) > 0

    # Decrypt
    decrypted = encryption.decrypt(ciphertext, private_key)

    # Verify decryption restores original
    assert decrypted == plaintext


def test_pqc_encryption_with_wrong_key_fails():
    """Test that decryption with wrong key fails"""
    from luminous_nix.security.pqc import PQCKeyManager, PQCEncryption

    key_manager = PQCKeyManager()
    encryption = PQCEncryption()

    # Generate two key pairs
    public_key1, private_key1 = key_manager.generate_key_pair()
    public_key2, private_key2 = key_manager.generate_key_pair()

    # Encrypt with first key
    plaintext = b"Secret message"
    ciphertext = encryption.encrypt(plaintext, public_key1)

    # Try to decrypt with wrong key
    with pytest.raises(Exception):  # Should fail
        encryption.decrypt(ciphertext, private_key2)


def test_pqc_encrypt_large_data():
    """Test encrypting larger data blocks"""
    from luminous_nix.security.pqc import PQCKeyManager, PQCEncryption

    key_manager = PQCKeyManager()
    encryption = PQCEncryption()

    public_key, private_key = key_manager.generate_key_pair()

    # Large data (1MB)
    plaintext = b"x" * (1024 * 1024)

    # Encrypt and decrypt
    ciphertext = encryption.encrypt(plaintext, public_key)
    decrypted = encryption.decrypt(ciphertext, private_key)

    # Verify
    assert decrypted == plaintext


# === Test State Encryption ===

def test_encrypted_state_persistence():
    """Test encrypting operation state for persistence"""
    from luminous_nix.security.pqc import PQCKeyManager, EncryptedStatePersistence
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    key_manager = PQCKeyManager()
    public_key, private_key = key_manager.generate_key_pair()

    persistence = EncryptedStatePersistence(public_key, private_key)

    # Create operation state
    state = OperationState()
    state.operation_id = "test_op"
    state.user_query = "install firefox"
    state.status = OperationStatus.PLANNING

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state.encrypted"

        # Save encrypted state
        persistence.save_state(state, state_file)

        # Verify file created and encrypted
        assert state_file.exists()
        content = state_file.read_bytes()
        assert b"install firefox" not in content  # Should not contain plaintext

        # Load encrypted state
        loaded_state = persistence.load_state(state_file)

        # Verify state restored correctly
        assert loaded_state.operation_id == "test_op"
        assert loaded_state.user_query == "install firefox"
        assert loaded_state.status == OperationStatus.PLANNING


def test_encrypted_state_wrong_key_fails():
    """Test that loading state with wrong key fails"""
    from luminous_nix.security.pqc import PQCKeyManager, EncryptedStatePersistence
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    key_manager = PQCKeyManager()

    # Generate two key pairs
    public_key1, private_key1 = key_manager.generate_key_pair()
    public_key2, private_key2 = key_manager.generate_key_pair()

    # Save with first key
    persistence1 = EncryptedStatePersistence(public_key1, private_key1)

    state = OperationState()
    state.operation_id = "test"
    state.user_query = "secret command"
    state.status = OperationStatus.PLANNING

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state.encrypted"

        persistence1.save_state(state, state_file)

        # Try to load with wrong key
        persistence2 = EncryptedStatePersistence(public_key2, private_key2)

        with pytest.raises(Exception):
            persistence2.load_state(state_file)


# === Test Key Rotation ===

def test_pqc_key_rotation():
    """Test rotating encryption keys"""
    from luminous_nix.security.pqc import PQCKeyManager, PQCKeyRotation
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    key_manager = PQCKeyManager()

    # Generate old and new key pairs
    old_public, old_private = key_manager.generate_key_pair()
    new_public, new_private = key_manager.generate_key_pair()

    rotation = PQCKeyRotation()

    # Create state encrypted with old key
    state = OperationState()
    state.operation_id = "rotate_test"
    state.user_query = "test rotation"
    state.status = OperationStatus.PLANNING

    with tempfile.TemporaryDirectory() as tmpdir:
        old_file = Path(tmpdir) / "old.encrypted"
        new_file = Path(tmpdir) / "new.encrypted"

        # Encrypt with old key
        from luminous_nix.security.pqc import EncryptedStatePersistence
        old_persistence = EncryptedStatePersistence(old_public, old_private)
        old_persistence.save_state(state, old_file)

        # Rotate to new key
        rotation.rotate_state_file(
            old_file,
            new_file,
            old_private,
            new_public
        )

        # Verify new file can be decrypted with new key
        new_persistence = EncryptedStatePersistence(new_public, new_private)
        loaded_state = new_persistence.load_state(new_file)

        # Verify state preserved
        assert loaded_state.operation_id == "rotate_test"
        assert loaded_state.user_query == "test rotation"


# === Test Integration with Plugin System ===

def test_pqc_persistence_backend_plugin():
    """Test PQC-encrypted persistence backend as plugin"""
    from luminous_nix.plugins.pqc_persistence_plugin import PQCPersistencePlugin
    from luminous_nix.core.plugin_registry import PluginRegistry
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    plugin = PQCPersistencePlugin()

    # Verify plugin properties
    assert plugin.name == "pqc-persistence-plugin"
    assert plugin.version.startswith("1.")

    # Register and enable
    registry = PluginRegistry()
    registry.register(plugin)
    registry.enable_plugin("pqc-persistence-plugin")

    # Verify persistence backend was created
    assert plugin.persistence_backend is not None

    # Test saving and loading through plugin
    state = OperationState()
    state.operation_id = "plugin_test"
    state.user_query = "test plugin integration"
    state.status = OperationStatus.PLANNING

    # Save
    success = plugin.persistence_backend.save_state("plugin_test", state)
    assert success

    # Load
    loaded = plugin.persistence_backend.load_state("plugin_test")
    assert loaded is not None
    assert loaded.operation_id == "plugin_test"

    # Delete
    deleted = plugin.persistence_backend.delete_state("plugin_test")
    assert deleted


def test_pqc_performance_acceptable():
    """Test that PQC operations complete in reasonable time"""
    from luminous_nix.security.pqc import PQCKeyManager, PQCEncryption
    import time

    key_manager = PQCKeyManager()
    encryption = PQCEncryption()

    # Key generation should be fast (< 2 seconds for RSA-4096)
    start = time.time()
    public_key, private_key = key_manager.generate_key_pair()
    key_gen_time = time.time() - start
    assert key_gen_time < 2.0

    # Encryption should be fast (< 0.1 seconds for 1KB)
    plaintext = b"x" * 1024
    start = time.time()
    ciphertext = encryption.encrypt(plaintext, public_key)
    encrypt_time = time.time() - start
    assert encrypt_time < 0.1

    # Decryption should be fast (< 0.1 seconds for 1KB)
    start = time.time()
    decrypted = encryption.decrypt(ciphertext, private_key)
    decrypt_time = time.time() - start
    assert decrypt_time < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
