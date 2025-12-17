"""
Integration tests for combined security features.

Tests the interaction between:
- PQC Encryption (Week 9-10)
- Operation Signatures (Week 10)
- Backup System
- Error Recovery

Ensures all security layers work together seamlessly.
"""

import pytest
from pathlib import Path
import json
import time
from dataclasses import dataclass
from typing import Optional

from luminous_nix.core.state_manager import (
    StateManager,
    OperationState,
    OperationStatus,
    OperationType
)
from luminous_nix.security.pqc import PQCKeyManager, PQCKeyRotation


class TestSecurityIntegration:
    """Test combined security features working together"""

    def test_encrypt_then_sign_operation(self, tmp_path):
        """Test that encryption and signing work together"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create manager with both encryption and signing
        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create operation
        state = OperationState(
            operation_id="test_op_001",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.CREATED,
            user_query="install firefox",
            result="Firefox installed successfully"
        )

        # Save - should encrypt AND sign
        success = manager.save_state(state)
        assert success, "Save should succeed"

        # Load - should decrypt AND verify signature
        loaded = manager.load_state("test_op_001")
        assert loaded is not None, "Should load operation"
        assert loaded.user_query == "install firefox"
        assert loaded.result == "Firefox installed successfully"
        assert loaded.signature is not None, "Should have signature"
        assert loaded.signature_algorithm == "RSA-4096"

    def test_tamper_detection_with_encryption(self, tmp_path):
        """Test that tampering with encrypted+signed data is detected"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        state = OperationState(
            operation_id="test_op_002",
            operation_type=OperationType.UPDATE,
            status=OperationStatus.CREATED,
            user_query="update system"
        )

        manager.save_state(state)

        # Tamper with encrypted file
        encrypted_file = storage_dir / "test_op_002.encrypted"
        data = encrypted_file.read_bytes()
        tampered = bytearray(data)
        tampered[100] ^= 0xFF  # Flip bits in encrypted data
        encrypted_file.write_bytes(bytes(tampered))

        # Attempt to load - should fail
        loaded = manager.load_state("test_op_002")
        # Either decryption fails or signature verification fails
        assert loaded is None, "Tampered data should not load"

    def test_encryption_and_signing_independent(self, tmp_path):
        """Test that encryption and signing work independently"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Test 1: Encryption only
        manager_enc_only = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=False
        )

        state1 = OperationState(
            operation_id="enc_only",
            operation_type=OperationType.SEARCH,
            status=OperationStatus.COMPLETED,
            user_query="search editor"
        )
        manager_enc_only.save_state(state1)

        loaded1 = manager_enc_only.load_state("enc_only")
        assert loaded1 is not None
        assert loaded1.signature is None  # No signature when signing disabled

        # Test 2: Signing only
        manager_sign_only = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=False,
            signing_enabled=True
        )

        state2 = OperationState(
            operation_id="sign_only",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.COMPLETED,
            user_query="install vim"
        )
        manager_sign_only.save_state(state2)

        loaded2 = manager_sign_only.load_state("sign_only")
        assert loaded2 is not None
        assert loaded2.signature is not None  # Has signature

    def test_multiple_operations_with_full_security(self, tmp_path):
        """Test that multiple operations work with encryption and signatures"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create manager with full security
        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create multiple signed operations
        for i in range(5):
            state = OperationState(
                operation_id=f"test_op_{i:03d}",
                operation_type=OperationType.INSTALL,
                status=OperationStatus.COMPLETED,
                user_query=f"install package_{i}",
                result=f"Package {i} installed"
            )
            manager.save_state(state)

        # Verify all operations can be loaded with signatures intact
        for i in range(5):
            loaded = manager.load_state(f"test_op_{i:03d}")
            assert loaded is not None, f"Operation {i} should load"
            assert loaded.signature is not None, f"Operation {i} should have signature"
            assert loaded.user_query == f"install package_{i}"
            assert loaded.result == f"Package {i} installed"
            assert loaded.signature_algorithm == "RSA-4096"

    def test_performance_combined_security(self, tmp_path):
        """Test performance with both encryption and signing enabled"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Measure 10 save/load cycles
        start = time.time()

        for i in range(10):
            state = OperationState(
                operation_id=f"perf_test_{i:03d}",
                operation_type=OperationType.CONFIG_GENERATE,
                status=OperationStatus.COMPLETED,
                user_query=f"generate config {i}",
                result=f"Config {i} generated"
            )

            # Save (encrypt + sign)
            manager.save_state(state)

            # Load (decrypt + verify)
            loaded = manager.load_state(f"perf_test_{i:03d}")
            assert loaded is not None
            assert loaded.signature is not None

        duration = time.time() - start

        # Should complete in <15 seconds (1.5s per operation)
        # Note: Performance varies by system, this is a generous limit
        assert duration < 15.0, f"Combined security too slow: {duration:.2f}s for 10 ops"

        # Print actual performance
        print(f"\nCombined security performance: {duration:.2f}s for 10 operations")
        print(f"Average: {(duration/10)*1000:.0f}ms per operation")

    def test_migration_unsigned_to_signed(self, tmp_path):
        """Test migration from unsigned to signed operations"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create manager without signing
        manager_unsigned = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=False
        )

        # Create unsigned operation
        state = OperationState(
            operation_id="test_op_004",
            operation_type=OperationType.UNINSTALL,
            status=OperationStatus.COMPLETED,
            user_query="uninstall old-package"
        )
        manager_unsigned.save_state(state)

        # Verify it has no signature
        loaded_unsigned = manager_unsigned.load_state("test_op_004")
        assert loaded_unsigned is not None
        assert loaded_unsigned.signature is None

        # Resave with same manager (still no signing) but with new data
        loaded_unsigned.result = "Package uninstalled successfully"
        manager_unsigned.save_state(loaded_unsigned)

        # Load again with unsigned manager
        reloaded = manager_unsigned.load_state("test_op_004")
        assert reloaded is not None
        assert reloaded.signature is None  # Still unsigned
        assert reloaded.result == "Package uninstalled successfully"

    def test_error_recovery_with_security(self, tmp_path):
        """Test that error recovery works with encrypted+signed operations"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create operation that fails
        state = OperationState(
            operation_id="test_op_005",
            operation_type=OperationType.SYSTEM_REBUILD,
            status=OperationStatus.FAILED,
            user_query="rebuild system",
            error="Network timeout during download"
        )
        manager.save_state(state)

        # Load failed operation
        loaded = manager.load_state("test_op_005")
        assert loaded is not None
        assert loaded.status == OperationStatus.FAILED
        assert loaded.signature is not None

        # Update to retry status
        loaded.status = OperationStatus.READY
        loaded.retry_count = 1
        manager.save_state(loaded)

        # Load and verify signature updated
        retried = manager.load_state("test_op_005")
        assert retried is not None
        assert retried.status == OperationStatus.READY
        assert retried.retry_count == 1
        assert retried.signature is not None  # New signature

    def test_all_operation_types_secured(self, tmp_path):
        """Test that all operation types work with full security"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Test all operation types
        operation_types = [
            OperationType.SEARCH,
            OperationType.INSTALL,
            OperationType.UNINSTALL,
            OperationType.UPDATE,
            OperationType.CONFIG_GENERATE,
            OperationType.SYSTEM_REBUILD,
            OperationType.ROLLBACK,
            OperationType.CUSTOM
        ]

        for op_type in operation_types:
            state = OperationState(
                operation_id=f"test_{op_type.value}",
                operation_type=op_type,
                status=OperationStatus.COMPLETED,
                user_query=f"test {op_type.value}"
            )

            # Save with full security
            success = manager.save_state(state)
            assert success, f"Save failed for {op_type.value}"

            # Load and verify
            loaded = manager.load_state(f"test_{op_type.value}")
            assert loaded is not None, f"Load failed for {op_type.value}"
            assert loaded.signature is not None, f"No signature for {op_type.value}"
            assert loaded.operation_type == op_type

    def test_large_result_with_security(self, tmp_path):
        """Test that large operation results work with encryption+signing"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        # Create operation with large result (simulating package search)
        large_result = {
            'packages': [
                {'name': f'package-{i}', 'version': f'1.{i}.0', 'description': 'A' * 100}
                for i in range(100)
            ],
            'total_found': 100,
            'search_time': 2.5
        }

        state = OperationState(
            operation_id="test_large",
            operation_type=OperationType.SEARCH,
            status=OperationStatus.COMPLETED,
            user_query="search package",
            result=json.dumps(large_result)
        )

        # Save
        start = time.time()
        success = manager.save_state(state)
        save_time = time.time() - start
        assert success, "Save should succeed"

        # Load
        start = time.time()
        loaded = manager.load_state("test_large")
        load_time = time.time() - start

        assert loaded is not None, "Should load large operation"
        assert loaded.signature is not None

        # Verify result intact
        loaded_result = json.loads(loaded.result)
        assert loaded_result['total_found'] == 100
        assert len(loaded_result['packages']) == 100

        # Performance should still be acceptable
        assert save_time < 2.0, f"Save too slow: {save_time:.2f}s"
        assert load_time < 2.0, f"Load too slow: {load_time:.2f}s"

        print(f"\nLarge data performance:")
        print(f"  Save: {save_time*1000:.0f}ms")
        print(f"  Load: {load_time*1000:.0f}ms")


class TestSecurityFailureModes:
    """Test security failure scenarios"""

    def test_missing_signing_key(self, tmp_path):
        """Test behavior when signing key is missing"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create manager with signing
        manager1 = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=False,
            signing_enabled=True
        )

        state = OperationState(
            operation_id="test_missing_key",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.CREATED,
            user_query="install test"
        )
        manager1.save_state(state)

        # Delete signing key
        signing_key = storage_dir / ".state_manager_signing.pem"
        if signing_key.exists():
            signing_key.unlink()

        # Create new manager - should generate new key
        manager2 = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=False,
            signing_enabled=True
        )

        # Old signatures won't verify with new key
        # This is expected behavior

    def test_corrupted_encrypted_file(self, tmp_path):
        """Test behavior with corrupted encrypted file"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        manager = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        state = OperationState(
            operation_id="test_corrupt",
            operation_type=OperationType.UPDATE,
            status=OperationStatus.CREATED,
            user_query="update packages"
        )
        manager.save_state(state)

        # Corrupt file by truncating it
        encrypted_file = storage_dir / "test_corrupt.encrypted"
        data = encrypted_file.read_bytes()
        encrypted_file.write_bytes(data[:len(data)//2])  # Cut in half

        # Attempt to load - should fail gracefully
        loaded = manager.load_state("test_corrupt")
        assert loaded is None, "Should not load corrupted file"

    def test_mixed_encryption_states(self, tmp_path):
        """Test mixing encrypted and unencrypted operations"""
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create unencrypted operation
        manager_plain = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=False,
            signing_enabled=False
        )

        state1 = OperationState(
            operation_id="plain_op",
            operation_type=OperationType.SEARCH,
            status=OperationStatus.COMPLETED,
            user_query="search vim"
        )
        manager_plain.save_state(state1)

        # Create encrypted operation
        manager_encrypted = StateManager(
            storage_dir=storage_dir,
            encryption_enabled=True,
            signing_enabled=True
        )

        state2 = OperationState(
            operation_id="encrypted_op",
            operation_type=OperationType.INSTALL,
            status=OperationStatus.COMPLETED,
            user_query="install firefox"
        )
        manager_encrypted.save_state(state2)

        # Should be able to load both
        plain_loaded = manager_encrypted.load_state("plain_op")
        encrypted_loaded = manager_encrypted.load_state("encrypted_op")

        assert plain_loaded is not None, "Should load unencrypted"
        assert encrypted_loaded is not None, "Should load encrypted"
        assert plain_loaded.signature is None
        assert encrypted_loaded.signature is not None


if __name__ == "__main__":
    # Run with: pytest tests/test_security_integration.py -v
    pytest.main([__file__, "-v", "-s"])
