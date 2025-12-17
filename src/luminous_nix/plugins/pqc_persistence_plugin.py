"""
PQC Persistence Plugin

Provides quantum-resistant encrypted state persistence through the
PersistenceBackend extension point.

Features:
- Encrypted state storage
- Quantum-resistant cryptography
- Key management integration
- Seamless plugin integration
"""

from typing import Any, Optional, List
from pathlib import Path
import tempfile

from luminous_nix.core.plugin_registry import Plugin
from luminous_nix.core.extension_points import PersistenceBackend
from luminous_nix.security.pqc import PQCKeyManager, EncryptedStatePersistence
from luminous_nix.core.state_manager import OperationState


class PQCPersistenceBackend(PersistenceBackend):
    """
    PersistenceBackend using PQC encryption.

    Stores operation state with quantum-resistant encryption.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize PQC persistence backend.

        Args:
            storage_dir: Directory for encrypted state files
        """
        # Generate key pair for this instance
        key_manager = PQCKeyManager()
        self.public_key, self.private_key = key_manager.generate_key_pair()

        # Initialize encrypted persistence
        self.persistence = EncryptedStatePersistence(
            self.public_key,
            self.private_key
        )

        # Storage directory
        if storage_dir is None:
            # Use temporary directory for testing
            self.temp_dir = tempfile.mkdtemp()
            self.storage_dir = Path(self.temp_dir)
        else:
            self.temp_dir = None
            self.storage_dir = storage_dir
            self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_state_path(self, operation_id: str) -> Path:
        """Get file path for operation state"""
        return self.storage_dir / f"{operation_id}.encrypted"

    def save_state(self, operation_id: str, state: OperationState) -> bool:
        """
        Save operation state with encryption.

        Args:
            operation_id: ID of operation
            state: OperationState to save

        Returns:
            True if saved successfully
        """
        try:
            state_path = self._get_state_path(operation_id)
            self.persistence.save_state(state, state_path)
            return True
        except Exception:
            return False

    def load_state(self, operation_id: str) -> Optional[OperationState]:
        """
        Load encrypted operation state.

        Args:
            operation_id: ID of operation

        Returns:
            OperationState if found, None otherwise
        """
        try:
            state_path = self._get_state_path(operation_id)
            if not state_path.exists():
                return None
            return self.persistence.load_state(state_path)
        except Exception:
            return None

    def delete_state(self, operation_id: str) -> bool:
        """
        Delete encrypted operation state.

        Args:
            operation_id: ID of operation

        Returns:
            True if deleted successfully
        """
        try:
            state_path = self._get_state_path(operation_id)
            if state_path.exists():
                state_path.unlink()
                return True
            return False
        except Exception:
            return False

    def list_operations(self) -> List[str]:
        """
        List all operation IDs.

        Returns:
            List of operation IDs
        """
        try:
            operations = []
            for path in self.storage_dir.glob("*.encrypted"):
                operation_id = path.stem  # Filename without .encrypted
                operations.append(operation_id)
            return operations
        except Exception:
            return []


class PQCPersistencePlugin(Plugin):
    """
    Plugin providing quantum-resistant encrypted state persistence.

    Demonstrates PersistenceBackend extension point with PQC security.

    Example:
        >>> plugin = PQCPersistencePlugin()
        >>> registry.register(plugin)
        >>> registry.enable_plugin("pqc-persistence-plugin")
        >>> # Now state is encrypted with PQC
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize PQC persistence plugin.

        Args:
            storage_dir: Optional directory for encrypted state files
        """
        super().__init__()
        self.storage_dir = storage_dir
        self.persistence_backend: Optional[PQCPersistenceBackend] = None

    @property
    def name(self) -> str:
        """Plugin name"""
        return "pqc-persistence-plugin"

    @property
    def version(self) -> str:
        """Plugin version"""
        return "1.0.0"

    @property
    def author(self) -> str:
        """Plugin author"""
        return "Luminous Dynamics"

    @property
    def description(self) -> str:
        """Plugin description"""
        return "Quantum-resistant encrypted state persistence"

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        pass

    def on_enable(self) -> None:
        """
        Called when plugin is enabled.

        Creates and registers the PQC persistence backend.
        """
        self.persistence_backend = PQCPersistenceBackend(self.storage_dir)

    def on_disable(self) -> None:
        """
        Called when plugin is disabled.

        Cleans up persistence backend.
        """
        self.persistence_backend = None

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        pass


if __name__ == "__main__":
    # Example usage
    print("PQC Persistence Plugin Example")
    print("-" * 50)

    # Create plugin
    plugin = PQCPersistencePlugin()

    # Simulate plugin lifecycle
    plugin.on_load()
    plugin.on_enable()

    # Test persistence
    from luminous_nix.core.state_manager import OperationState, OperationStatus

    state = OperationState()
    state.operation_id = "example_op"
    state.user_query = "install firefox"
    state.status = OperationStatus.PLANNING

    # Save
    success = plugin.persistence_backend.save_state("example_op", state)
    print(f"Save: {success}")

    # Load
    loaded = plugin.persistence_backend.load_state("example_op")
    print(f"Load: {loaded.operation_id if loaded else None}")

    # List
    operations = plugin.persistence_backend.list_operations()
    print(f"Operations: {operations}")

    # Delete
    deleted = plugin.persistence_backend.delete_state("example_op")
    print(f"Delete: {deleted}")

    # Disable plugin
    plugin.on_disable()

    print("\nPQC Persistence Plugin Ready ✅")
