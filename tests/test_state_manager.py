"""
Tests for StateManager - Operation state tracking and persistence

Test-Driven Development: These tests are written FIRST, then we implement
until all tests pass.

Based on design from: DEEP_DIVE_STATE_MANAGEMENT.md
"""

import pytest
from datetime import datetime, timedelta
import tempfile
from pathlib import Path
import json


# === Test OperationStatus Enum ===

def test_operation_status_enum():
    """Test OperationStatus enum exists with correct values"""
    from luminous_nix.core.state_manager import OperationStatus

    assert hasattr(OperationStatus, 'CREATED')
    assert hasattr(OperationStatus, 'ANALYZING')
    assert hasattr(OperationStatus, 'PLANNING')
    assert hasattr(OperationStatus, 'READY')
    assert hasattr(OperationStatus, 'EXECUTING')
    assert hasattr(OperationStatus, 'PAUSED')
    assert hasattr(OperationStatus, 'COMPLETED')
    assert hasattr(OperationStatus, 'FAILED')
    assert hasattr(OperationStatus, 'ROLLED_BACK')
    assert hasattr(OperationStatus, 'ROLLBACK_FAILED')
    assert hasattr(OperationStatus, 'CANCELLED')


def test_operation_status_is_terminal():
    """Test is_terminal() method"""
    from luminous_nix.core.state_manager import OperationStatus

    # Terminal states
    assert OperationStatus.COMPLETED.is_terminal() is True
    assert OperationStatus.FAILED.is_terminal() is True
    assert OperationStatus.ROLLED_BACK.is_terminal() is True
    assert OperationStatus.CANCELLED.is_terminal() is True

    # Non-terminal states
    assert OperationStatus.CREATED.is_terminal() is False
    assert OperationStatus.EXECUTING.is_terminal() is False
    assert OperationStatus.PAUSED.is_terminal() is False


def test_operation_status_is_active():
    """Test is_active() method"""
    from luminous_nix.core.state_manager import OperationStatus

    # Active states
    assert OperationStatus.ANALYZING.is_active() is True
    assert OperationStatus.PLANNING.is_active() is True
    assert OperationStatus.EXECUTING.is_active() is True

    # Inactive states
    assert OperationStatus.CREATED.is_active() is False
    assert OperationStatus.COMPLETED.is_active() is False
    assert OperationStatus.PAUSED.is_active() is False


# === Test LayerState ===

def test_layer_state_creation():
    """Test creating a LayerState"""
    from luminous_nix.core.state_manager import LayerState

    layer = LayerState(
        layer_number=1,
        layer_name="Semantic Understanding",
        status="pending"
    )

    assert layer.layer_number == 1
    assert layer.layer_name == "Semantic Understanding"
    assert layer.status == "pending"
    assert layer.started_at is None
    assert layer.completed_at is None
    assert layer.duration_ms is None


def test_layer_state_to_dict():
    """Test LayerState serialization"""
    from luminous_nix.core.state_manager import LayerState

    layer = LayerState(
        layer_number=1,
        layer_name="Test Layer",
        status="complete",
        input_data={'input': 'data'},
        output_data={'output': 'result'}
    )

    data = layer.to_dict()

    assert data['layer_number'] == 1
    assert data['layer_name'] == "Test Layer"
    assert data['status'] == "complete"
    assert data['input_data'] == {'input': 'data'}
    assert data['output_data'] == {'output': 'result'}


# === Test OperationState ===

def test_operation_state_creation():
    """Test creating an OperationState"""
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    state = OperationState(
        user_query="install firefox",
        user_id="test_user"
    )

    assert state.operation_id is not None  # Auto-generated UUID
    assert state.user_query == "install firefox"
    assert state.user_id == "test_user"
    assert state.status == OperationStatus.CREATED
    assert state.created_at is not None
    assert len(state.layers) == 6  # All 6 layers initialized


def test_operation_state_layer_initialization():
    """Test that all 6 layers are initialized"""
    from luminous_nix.core.state_manager import OperationState

    state = OperationState(user_query="test")

    assert len(state.layers) == 6

    # Check layer names
    assert state.layers[1].layer_name == "Semantic Understanding"
    assert state.layers[2].layer_name == "Context Analysis"
    assert state.layers[3].layer_name == "Strategy Selection"
    assert state.layers[4].layer_name == "Execution"
    assert state.layers[5].layer_name == "Adaptive Monitoring"
    assert state.layers[6].layer_name == "Learning"

    # All should be pending initially
    for layer in state.layers.values():
        assert layer.status == "pending"


def test_operation_state_start_layer():
    """Test starting a layer"""
    from luminous_nix.core.state_manager import OperationState

    state = OperationState(user_query="test")

    # Start layer 1
    state.start_layer(1, {'query': 'install firefox'})

    layer = state.layers[1]
    assert layer.status == "in_progress"
    assert layer.started_at is not None
    assert layer.input_data == {'query': 'install firefox'}


def test_operation_state_complete_layer():
    """Test completing a layer"""
    from luminous_nix.core.state_manager import OperationState

    state = OperationState(user_query="test")

    # Start and complete layer
    state.start_layer(1)
    state.complete_layer(1, {'intent': 'install', 'package': 'firefox'})

    layer = state.layers[1]
    assert layer.status == "complete"
    assert layer.completed_at is not None
    assert layer.duration_ms is not None
    assert layer.duration_ms > 0
    assert layer.output_data == {'intent': 'install', 'package': 'firefox'}


def test_operation_state_fail_layer():
    """Test failing a layer"""
    from luminous_nix.core.state_manager import OperationState

    state = OperationState(user_query="test")

    state.start_layer(1)
    state.fail_layer(1, "Network timeout")

    layer = state.layers[1]
    assert layer.status == "failed"
    assert layer.completed_at is not None
    assert "Network timeout" in layer.errors


def test_operation_state_get_current_layer():
    """Test getting current layer in progress"""
    from luminous_nix.core.state_manager import OperationState

    state = OperationState(user_query="test")

    # No layer in progress initially
    assert state.get_current_layer() is None

    # Start layer 1
    state.start_layer(1)
    current = state.get_current_layer()
    assert current is not None
    assert current.layer_number == 1

    # Complete layer 1, start layer 2
    state.complete_layer(1)
    state.start_layer(2)
    current = state.get_current_layer()
    assert current.layer_number == 2


def test_operation_state_get_progress_percent():
    """Test progress calculation"""
    from luminous_nix.core.state_manager import OperationState

    state = OperationState(user_query="test")

    # Initially 0%
    assert state.get_progress_percent() == 0.0

    # Complete layer 1: 1/6 ≈ 16.7%
    state.start_layer(1)
    state.complete_layer(1)
    progress = state.get_progress_percent()
    assert abs(progress - (1/6)) < 0.01

    # Complete all layers: 100%
    for i in range(2, 7):
        state.start_layer(i)
        state.complete_layer(i)
    assert state.get_progress_percent() == 1.0


def test_operation_state_serialization():
    """Test to_dict / from_dict round trip"""
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    # Create state with some data
    state1 = OperationState(
        user_query="install firefox",
        user_id="test_user",
        tags={'install', 'browser'}
    )
    state1.status = OperationStatus.EXECUTING
    state1.start_layer(1)
    state1.complete_layer(1, {'intent': 'install'})

    # Serialize
    data = state1.to_dict()

    # Deserialize
    state2 = OperationState.from_dict(data)

    # Verify
    assert state2.operation_id == state1.operation_id
    assert state2.user_query == state1.user_query
    assert state2.user_id == state1.user_id
    assert state2.status == state1.status
    assert state2.tags == state1.tags
    assert state2.layers[1].status == "complete"


# === Test StateManager ===

@pytest.fixture
def temp_state_dir():
    """Create temporary directory for state storage"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_state_manager_creation(temp_state_dir):
    """Test creating StateManager"""
    from luminous_nix.core.state_manager import StateManager

    db_path = temp_state_dir / "test.db"
    json_dir = temp_state_dir / "json"

    manager = StateManager(db_path=db_path, json_dir=json_dir)

    assert manager.db_path == db_path
    assert manager.json_dir == json_dir
    assert db_path.parent.exists()
    assert json_dir.exists()


def test_state_manager_create_operation(temp_state_dir):
    """Test creating an operation"""
    from luminous_nix.core.state_manager import StateManager

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )

    state = manager.create_operation(
        user_query="install firefox",
        user_id="test_user",
        tags={'install'}
    )

    assert state.operation_id is not None
    assert state.user_query == "install firefox"
    assert state.user_id == "test_user"
    assert 'install' in state.tags


def test_state_manager_get_operation(temp_state_dir):
    """Test retrieving an operation"""
    from luminous_nix.core.state_manager import StateManager

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )

    # Create operation
    state1 = manager.create_operation("test query")
    op_id = state1.operation_id

    # Retrieve it
    state2 = manager.get_operation(op_id)

    assert state2 is not None
    assert state2.operation_id == op_id
    assert state2.user_query == "test query"


def test_state_manager_update_operation(temp_state_dir):
    """Test updating an operation"""
    from luminous_nix.core.state_manager import StateManager, OperationStatus

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )

    # Create and modify
    state = manager.create_operation("test")
    state.status = OperationStatus.EXECUTING
    state.start_layer(1)

    manager.update_operation(state)

    # Retrieve and verify
    retrieved = manager.get_operation(state.operation_id)
    assert retrieved.status == OperationStatus.EXECUTING
    assert retrieved.layers[1].status == "in_progress"


def test_state_manager_list_operations(temp_state_dir):
    """Test listing operations with filters"""
    from luminous_nix.core.state_manager import StateManager, OperationStatus

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )

    # Create multiple operations
    state1 = manager.create_operation("op1", user_id="user1")
    state2 = manager.create_operation("op2", user_id="user2")
    state3 = manager.create_operation("op3", user_id="user1")

    # List all
    all_ops = manager.list_operations()
    assert len(all_ops) >= 3

    # List by user
    user1_ops = manager.list_operations(user_id="user1")
    assert len(user1_ops) == 2

    # List by status
    state1.status = OperationStatus.COMPLETED
    manager.update_operation(state1)

    completed = manager.list_operations(status=OperationStatus.COMPLETED)
    assert len(completed) == 1
    assert completed[0].operation_id == state1.operation_id


def test_state_manager_get_active_operations(temp_state_dir):
    """Test getting active (non-terminal) operations"""
    from luminous_nix.core.state_manager import StateManager, OperationStatus

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )

    # Create operations in different states
    state1 = manager.create_operation("active1")
    state1.status = OperationStatus.EXECUTING
    manager.update_operation(state1)

    state2 = manager.create_operation("active2")
    state2.status = OperationStatus.ANALYZING
    manager.update_operation(state2)

    state3 = manager.create_operation("completed")
    state3.status = OperationStatus.COMPLETED
    manager.update_operation(state3)

    # Get active
    active = manager.get_active_operations()

    assert len(active) >= 2
    active_ids = {op.operation_id for op in active}
    assert state1.operation_id in active_ids
    assert state2.operation_id in active_ids
    assert state3.operation_id not in active_ids


def test_state_manager_json_backup(temp_state_dir):
    """Test that JSON backup is created"""
    from luminous_nix.core.state_manager import StateManager

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )

    state = manager.create_operation("test")

    # Check JSON file exists
    json_files = list(temp_state_dir.glob("json/**/*.json"))
    assert len(json_files) > 0

    # Check JSON content
    json_file = json_files[0]
    with open(json_file) as f:
        data = json.load(f)

    assert data['operation_id'] == state.operation_id
    assert data['user_query'] == "test"


def test_state_manager_delete_operation(temp_state_dir):
    """Test deleting an operation"""
    from luminous_nix.core.state_manager import StateManager

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )

    state = manager.create_operation("test")
    op_id = state.operation_id

    # Delete
    manager.delete_operation(op_id)

    # Verify deleted
    retrieved = manager.get_operation(op_id)
    assert retrieved is None


# === Test StateTransitionValidator ===

def test_state_transition_valid():
    """Test valid state transitions"""
    from luminous_nix.core.state_manager import StateTransitionValidator, OperationStatus

    # CREATED → ANALYZING
    assert StateTransitionValidator.can_transition(
        OperationStatus.CREATED,
        OperationStatus.ANALYZING
    ) is True

    # EXECUTING → COMPLETED
    assert StateTransitionValidator.can_transition(
        OperationStatus.EXECUTING,
        OperationStatus.COMPLETED
    ) is True

    # FAILED → ROLLED_BACK
    assert StateTransitionValidator.can_transition(
        OperationStatus.FAILED,
        OperationStatus.ROLLED_BACK
    ) is True


def test_state_transition_invalid():
    """Test invalid state transitions"""
    from luminous_nix.core.state_manager import StateTransitionValidator, OperationStatus

    # CREATED → EXECUTING (must go through ANALYZING, PLANNING first)
    assert StateTransitionValidator.can_transition(
        OperationStatus.CREATED,
        OperationStatus.EXECUTING
    ) is False

    # COMPLETED → ANALYZING (terminal states can't transition)
    assert StateTransitionValidator.can_transition(
        OperationStatus.COMPLETED,
        OperationStatus.ANALYZING
    ) is False


def test_state_transition_validate_raises():
    """Test that validate_transition raises on invalid transition"""
    from luminous_nix.core.state_manager import (
        StateTransitionValidator,
        OperationState,
        OperationStatus
    )

    state = OperationState(user_query="test")
    state.status = OperationStatus.COMPLETED

    with pytest.raises(ValueError, match="[Ii]nvalid transition"):
        StateTransitionValidator.validate_transition(
            state,
            OperationStatus.ANALYZING
        )


# === Test CrashRecoveryManager ===

def test_crash_recovery_resumable_operations(temp_state_dir):
    """Test recovering resumable operations after crash"""
    from luminous_nix.core.state_manager import (
        StateManager,
        CrashRecoveryManager,
        OperationStatus
    )

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )
    recovery = CrashRecoveryManager(manager)

    # Create operation that was executing
    state = manager.create_operation("test")
    state.status = OperationStatus.EXECUTING
    state.resumable = True
    state.checkpoint_data = {'step': 3}
    manager.update_operation(state)

    # Simulate crash recovery
    recovered = recovery.recover_on_startup()

    assert len(recovered) >= 1
    recovered_op = next(
        (op for op in recovered if op.operation_id == state.operation_id),
        None
    )
    assert recovered_op is not None
    assert recovered_op.status == OperationStatus.PAUSED


def test_crash_recovery_non_resumable(temp_state_dir):
    """Test that non-resumable operations are failed"""
    from luminous_nix.core.state_manager import (
        StateManager,
        CrashRecoveryManager,
        OperationStatus
    )

    manager = StateManager(
        db_path=temp_state_dir / "test.db",
        json_dir=temp_state_dir / "json"
    )
    recovery = CrashRecoveryManager(manager)

    # Create non-resumable operation
    state = manager.create_operation("test")
    state.status = OperationStatus.EXECUTING
    state.resumable = False
    manager.update_operation(state)

    # Recover
    recovered = recovery.recover_on_startup()

    # Should not be in recovered list
    recovered_ids = {op.operation_id for op in recovered}
    assert state.operation_id not in recovered_ids

    # Should be marked as failed
    state = manager.get_operation(state.operation_id)
    assert state.status == OperationStatus.FAILED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
