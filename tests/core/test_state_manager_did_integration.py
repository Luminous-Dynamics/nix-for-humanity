"""
Tests for State Manager + DID Integration (Week 2)

Verifies that StateManager:
1. Loads user DID on initialization
2. Attaches DID to all operations
3. Persists DID in operation state
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from luminous_nix.core.state_manager import StateManager, OperationType
from luminous_nix.mycelix.identity import DIDManager


class TestStateManagerDIDIntegration:
    """Test State Manager + DID integration"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_state_manager_loads_existing_did(self, temp_storage):
        """Test that StateManager loads existing DID on init"""
        # Step 1: Create a DID
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        user_did = did_mgr.create_did(passphrase="test123")

        # Step 2: Create state manager (should auto-load DID)
        state_mgr = StateManager(storage_dir=temp_storage / "state")

        # Verify DID was loaded
        assert state_mgr._did_manager is not None
        assert state_mgr._current_user_did is not None
        assert state_mgr._current_user_did.did == user_did.did

    def test_state_manager_attaches_did_to_operations(self, temp_storage):
        """Test that StateManager attaches DID to all new operations"""
        # Step 1: Create a DID
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        user_did = did_mgr.create_did(passphrase="test123")

        # Step 2: Create state manager
        state_mgr = StateManager(storage_dir=temp_storage / "state")

        # Step 3: Create an operation
        op = state_mgr.create_operation(
            user_query="search firefox",
            user_id="test_user"
        )

        # Verify DID was attached
        assert op.user_did is not None
        assert op.user_did == user_did.did
        assert op.user_did.startswith("did:mycelix:luminous_nix:")
        assert op.assurance_level == "E0"

    def test_operation_did_persists_across_restarts(self, temp_storage):
        """Test that DID in operations persists across StateManager restarts"""
        # Step 1: Create DID and operation
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        user_did = did_mgr.create_did(passphrase="test123")

        state_mgr = StateManager(storage_dir=temp_storage / "state")
        op = state_mgr.create_operation(user_query="install vim")
        operation_id = op.operation_id

        # Verify DID attached
        assert op.user_did == user_did.did

        # Step 2: Create new StateManager instance (simulate restart)
        state_mgr2 = StateManager(storage_dir=temp_storage / "state")

        # Load the operation
        loaded_op = state_mgr2.get_operation(operation_id)

        # Verify DID persisted
        assert loaded_op is not None
        assert loaded_op.user_did == user_did.did
        assert loaded_op.assurance_level == "E0"

    def test_operations_without_did(self, temp_storage):
        """Test that operations work even without a DID"""
        # Create state manager WITHOUT creating a DID first
        state_mgr = StateManager(storage_dir=temp_storage / "state")

        # Create operation
        op = state_mgr.create_operation(user_query="search vim")

        # Should work, just without DID
        assert op is not None
        assert op.user_did is None
        assert op.assurance_level is None

    def test_multiple_operations_share_same_did(self, temp_storage):
        """Test that multiple operations share the same user DID"""
        # Create DID
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        user_did = did_mgr.create_did(passphrase="test123")

        # Create state manager
        state_mgr = StateManager(storage_dir=temp_storage / "state")

        # Create multiple operations
        op1 = state_mgr.create_operation(user_query="search vim")
        op2 = state_mgr.create_operation(user_query="install firefox")
        op3 = state_mgr.create_operation(user_query="update system")

        # All should have same DID
        assert op1.user_did == user_did.did
        assert op2.user_did == user_did.did
        assert op3.user_did == user_did.did

    def test_did_serialization_to_dict(self, temp_storage):
        """Test that DID fields are included in to_dict() serialization"""
        # Create DID and operation
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        user_did = did_mgr.create_did(passphrase="test123")

        state_mgr = StateManager(storage_dir=temp_storage / "state")
        op = state_mgr.create_operation(user_query="search vim")

        # Serialize to dict
        op_dict = op.to_dict()

        # Verify DID fields in serialized data
        assert 'user_did' in op_dict
        assert 'assurance_level' in op_dict
        assert op_dict['user_did'] == user_did.did
        assert op_dict['assurance_level'] == "E0"

    def test_did_deserialization_from_dict(self, temp_storage):
        """Test that DID fields are correctly deserialized from dict"""
        # Create DID and operation
        did_mgr = DIDManager(storage_path=temp_storage / "identity")
        user_did = did_mgr.create_did(passphrase="test123")

        state_mgr = StateManager(storage_dir=temp_storage / "state")
        op = state_mgr.create_operation(user_query="search vim")

        # Serialize and deserialize
        op_dict = op.to_dict()

        from luminous_nix.core.state_manager import OperationState
        op_restored = OperationState.from_dict(op_dict)

        # Verify DID fields restored
        assert op_restored.user_did == user_did.did
        assert op_restored.assurance_level == "E0"


# Integration test
def test_complete_did_state_flow():
    """Test complete flow: DID creation → Operation → Persistence → Reload"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # Step 1: Create DID
        did_mgr = DIDManager(storage_path=storage_path / "identity")
        user_did = did_mgr.create_did(passphrase="test123")
        print(f"✅ Created DID: {user_did.did}")

        # Step 2: Create StateManager (auto-loads DID)
        state_mgr = StateManager(storage_dir=storage_path / "state")
        assert state_mgr._current_user_did.did == user_did.did
        print(f"✅ StateManager loaded DID")

        # Step 3: Create operation (DID auto-attached)
        op = state_mgr.create_operation(user_query="install firefox")
        assert op.user_did == user_did.did
        print(f"✅ Operation has DID: {op.user_did}")

        # Step 4: Simulate restart - create new StateManager
        state_mgr2 = StateManager(storage_dir=storage_path / "state")

        # Step 5: Load operation
        loaded_op = state_mgr2.get_operation(op.operation_id)
        assert loaded_op.user_did == user_did.did
        print(f"✅ DID persisted across restart: {loaded_op.user_did}")

        print("\n✅ Complete DID + State integration test passed!")
