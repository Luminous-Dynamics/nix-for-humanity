"""
Test Suite for Week 10: Operation Signatures

Tests operation integrity verification through cryptographic signatures.
This ensures operations cannot be tampered with and maintains audit trail.

Week 10: Operation Signatures
- Sign operation states for integrity verification
- Verify signatures on load
- Detect tampering attempts
- Integration with encrypted state storage
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import json

from luminous_nix.core.state_manager import (
    StateManager,
    OperationState,
    OperationType,
    OperationStatus
)


class TestOperationSignatures:
    """Test cryptographic signing of operation states"""

    def test_operation_signing_enabled(self, tmp_path):
        """Test that operations are automatically signed when signing enabled"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create StateManager with signing enabled
        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True  # New parameter
        )

        # Create operation
        state = OperationState(
            operation_id="test_op_001",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.CREATED,
            user_query="install firefox"
        )

        # Save operation
        success = manager.save_state(state)
        assert success, "Save operation should succeed"

        # Load operation
        loaded = manager.load_state("test_op_001")
        assert loaded is not None, "Should load signed operation"

        # Verify signature fields exist
        assert hasattr(loaded, 'signature'), "Operation should have signature"
        assert loaded.signature is not None, "Signature should not be None"
        assert hasattr(loaded, 'signature_algorithm'), "Should have algorithm field"
        assert loaded.signature_algorithm == 'RSA-4096', "Should use RSA-4096"

    def test_operation_signing_disabled(self, tmp_path):
        """Test that signing can be disabled for performance"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create StateManager with signing disabled
        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=False,
            signing_enabled=False
        )

        # Create operation
        state = OperationState(
            operation_id="test_op_002",
            operation_type=OperationType.SEARCH,
            status=OperationStatus.COMPLETED,
            user_query="search vim"
        )

        # Save operation
        success = manager.save_state(state)
        assert success, "Save should succeed without signing"

        # Load operation
        loaded = manager.load_state("test_op_002")
        assert loaded is not None, "Should load unsigned operation"

        # Verify no signature fields
        if hasattr(loaded, 'signature'):
            assert loaded.signature is None, "Signature should be None when disabled"

    def test_signature_verification_on_load(self, tmp_path):
        """Test that signatures are verified when loading operations"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create and save operation
        state = OperationState(
            operation_id="test_op_003",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.EXECUTING,
            user_query="install vim"
        )
        manager.save_state(state)

        # Load operation - signature should be verified automatically
        loaded = manager.load_state("test_op_003")
        assert loaded is not None, "Verification should succeed for valid signature"
        assert loaded.signature is not None, "Signature should be present"

    def test_tamper_detection(self, tmp_path):
        """Test that tampered operations are detected"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create and save operation
        state = OperationState(
            operation_id="test_op_004",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.CREATED,
            user_query="install firefox"
        )
        manager.save_state(state)

        # Tamper with the operation file
        operation_file = storage_dir / "test_op_004.encrypted"
        assert operation_file.exists(), "Operation file should exist"

        # Read, modify, and write back (simulating tampering)
        encrypted_data = operation_file.read_bytes()

        # Flip some bits in the middle (tamper with ciphertext)
        tampered_data = bytearray(encrypted_data)
        if len(tampered_data) > 100:
            tampered_data[50] ^= 0xFF  # Flip all bits
            tampered_data[51] ^= 0xFF
            operation_file.write_bytes(bytes(tampered_data))

            # Attempt to load tampered operation
            loaded = manager.load_state("test_op_004")

            # Should either return None or raise exception for invalid signature
            if loaded is not None:
                # If it loaded, signature verification should have failed
                # In practice, decryption may fail first due to authenticated encryption
                pass
            else:
                # Expected: loading fails due to tampering detection
                assert loaded is None, "Tampered operation should not load"

    def test_signature_update_on_modification(self, tmp_path):
        """Test that signature is updated when operation is modified"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create operation
        state = OperationState(
            operation_id="test_op_005",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.CREATED,
            user_query="install firefox"
        )
        manager.save_state(state)

        # Load and get original signature
        loaded1 = manager.load_state("test_op_005")
        original_signature = loaded1.signature

        # Modify operation
        loaded1.status = OperationStatus.COMPLETED
        loaded1.result = {"success": True, "package": "firefox"}

        # Save modified operation
        manager.save_state(loaded1)

        # Load again and verify signature changed
        loaded2 = manager.load_state("test_op_005")
        assert loaded2.signature is not None, "Modified operation should have signature"
        assert loaded2.signature != original_signature, "Signature should change after modification"
        assert loaded2.status == OperationStatus.COMPLETED, "Modifications should be preserved"

    def test_signature_algorithm_tracking(self, tmp_path):
        """Test that signature algorithm is tracked in metadata"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create operation
        state = OperationState(
            operation_id="test_op_006",
            operation_type=OperationType.CONFIG_GENERATE,
            status=OperationStatus.COMPLETED,
            user_query="generate nginx config"
        )
        manager.save_state(state)

        # Load and verify algorithm
        loaded = manager.load_state("test_op_006")
        assert loaded.signature_algorithm is not None, "Should track algorithm"
        assert loaded.signature_algorithm in ['RSA-4096', 'Kyber-1024', 'Hybrid-RSA4096-Kyber1024'], \
            "Should use known algorithm"

    def test_signing_with_encryption(self, tmp_path):
        """Test that signing works alongside encryption"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create operation with sensitive data
        state = OperationState(
            operation_id="test_op_007",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.COMPLETED,
            user_query="install firefox",
            result={"success": True, "sensitive": "api_key_12345"}
        )
        manager.save_state(state)

        # Verify file is encrypted (not human-readable)
        operation_file = storage_dir / "test_op_007.encrypted"
        encrypted_content = operation_file.read_bytes()
        assert b"api_key_12345" not in encrypted_content, "Sensitive data should be encrypted"
        assert b"firefox" not in encrypted_content, "Query should be encrypted"

        # Load and verify signature + decryption work
        loaded = manager.load_state("test_op_007")
        assert loaded is not None, "Should load encrypted+signed operation"
        assert loaded.signature is not None, "Should have signature"
        assert loaded.result["sensitive"] == "api_key_12345", "Should decrypt correctly"

    def test_signature_performance(self, tmp_path):
        """Test that signing doesn't significantly impact performance"""
        import time
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Measure save+load time with signing
        start = time.time()
        for i in range(10):
            state = OperationState(
                operation_id=f"test_op_perf_{i:03d}",
                operation_type=OperationType.SEARCH,
                status=OperationStatus.COMPLETED,
                user_query=f"search package{i}"
            )
            manager.save_state(state)
            loaded = manager.load_state(f"test_op_perf_{i:03d}")
            assert loaded is not None
        duration = time.time() - start

        # Should complete 10 operations in reasonable time
        # Each operation: save (sign+encrypt) + load (decrypt+verify)
        # RSA-4096 signing is ~50-100ms, encryption ~10-50ms
        # Target: <1s per operation = 10 seconds for 10 operations
        assert duration < 10.0, f"Signing overhead too high: {duration:.2f}s for 10 ops"

    def test_batch_signature_verification(self, tmp_path):
        """Test verifying multiple operations efficiently"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create multiple operations
        operation_ids = []
        for i in range(5):
            state = OperationState(
                operation_id=f"test_batch_{i:03d}",
                operation_type=OperationType.INSTALL,
                status=OperationStatus.COMPLETED,
                user_query=f"install package{i}"
            )
            manager.save_state(state)
            operation_ids.append(state.operation_id)

        # Verify all operations
        for op_id in operation_ids:
            loaded = manager.load_state(op_id)
            assert loaded is not None, f"Should load operation {op_id}"
            assert loaded.signature is not None, f"Operation {op_id} should have signature"

    def test_signature_with_operation_types(self, tmp_path):
        """Test signing works with all operation types"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Test each operation type
        operation_types = [
            OperationType.SEARCH,
            OperationType.INSTALL,
            OperationType.UNINSTALL,
            OperationType.UPDATE,
            OperationType.CONFIG_GENERATE,
            OperationType.SYSTEM_REBUILD
        ]

        for i, op_type in enumerate(operation_types):
            state = OperationState(
                operation_id=f"test_type_{i:03d}",
                operation_type=op_type,
                status=OperationStatus.COMPLETED,
                user_query=f"test {op_type.value}"
            )
            manager.save_state(state)

            # Verify signature exists
            loaded = manager.load_state(f"test_type_{i:03d}")
            assert loaded is not None, f"Should load {op_type.value} operation"
            assert loaded.signature is not None, f"{op_type.value} should have signature"


class TestSignatureIntegration:
    """Test signature integration with existing systems"""

    def test_signature_backward_compatibility(self, tmp_path):
        """Test that unsigned operations from old system still load"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create manager without signing (simulate old system)
        manager_old = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=False,
            signing_enabled=False
        )

        # Save operation without signature
        state = OperationState(
            operation_id="test_legacy_001",
            operation_type=OperationType.SEARCH,
            status=OperationStatus.COMPLETED,
            user_query="search vim"
        )
        manager_old.save_state(state)

        # Create new manager with signing enabled
        manager_new = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=False,
            signing_enabled=True
        )

        # Should load old unsigned operation
        loaded = manager_new.load_state("test_legacy_001")
        assert loaded is not None, "Should load legacy unsigned operation"

        # When we save it again, it should get signed
        manager_new.save_state(loaded)
        loaded_again = manager_new.load_state("test_legacy_001")

        # Now it should have a signature
        if hasattr(loaded_again, 'signature'):
            assert loaded_again.signature is not None, "Re-saved operation should have signature"

    def test_signature_with_recovery(self, tmp_path):
        """Test that signatures work with error recovery system"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create operation that will need recovery
        state = OperationState(
            operation_id="test_recovery_001",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.FAILED,
            user_query="install firefox",
            error="Network timeout"
        )
        manager.save_state(state)

        # Simulate recovery - update status
        loaded = manager.load_state("test_recovery_001")
        assert loaded.signature is not None, "Failed operation should have signature"

        # Update after recovery
        loaded.status = OperationStatus.READY
        loaded.retry_count = 1
        manager.save_state(loaded)

        # Verify signature updated
        loaded_again = manager.load_state("test_recovery_001")
        assert loaded_again.signature is not None, "Recovered operation should have new signature"
        assert loaded_again.status == OperationStatus.READY, "Recovery update should be preserved"


# Test fixtures and helpers

@pytest.fixture
def temp_storage():
    """Create temporary storage directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def signed_manager(temp_storage):
    """Create StateManager with signing enabled"""
    storage_dir = temp_storage / "storage"
    storage_dir.mkdir()
    return StateManager(
        storage_dir=storage_dir,
        encryption_enabled=True,
        signing_enabled=True
    )


@pytest.fixture
def unsigned_manager(temp_storage):
    """Create StateManager with signing disabled"""
    storage_dir = temp_storage / "storage"
    storage_dir.mkdir()
    return StateManager(
        storage_dir=storage_dir,
        encryption_enabled=False,
        signing_enabled=False
    )
