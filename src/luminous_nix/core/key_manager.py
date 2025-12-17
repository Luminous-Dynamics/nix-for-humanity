"""
KeyManager - PQC key pair management for encrypted state persistence

This module provides key lifecycle management for post-quantum cryptography:
- Key generation and storage
- Key rotation with versioning
- Key listing and metadata

Week 9-10: PQC Integration
"""

from pathlib import Path
from typing import List, Optional, Any, Tuple
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class KeyManager:
    """
    Manages encryption keys for StateManager and BackupManager.

    Provides lifecycle management for PQC key pairs including
    generation, rotation, and secure storage.
    """

    def __init__(self, key_dir: Optional[Path] = None):
        """
        Initialize KeyManager with key storage directory.

        Args:
            key_dir: Directory for key storage. Defaults to ~/.luminous-nix/keys
        """
        import os

        if key_dir is None:
            home = Path(os.path.expanduser("~"))
            key_dir = home / ".luminous-nix" / "keys"

        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)

        # Initialize PQC key manager
        try:
            from luminous_nix.security.pqc import PQCKeyManager
            self.pqc_manager = PQCKeyManager()
        except ImportError as e:
            logger.error(f"Failed to import PQC module: {e}")
            raise

    def generate_key_pair(self, name: str) -> bool:
        """
        Generate a new PQC key pair.

        Args:
            name: Key pair name (e.g., "default", "backup")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate key pair
            public_key, private_key = self.pqc_manager.generate_key_pair()

            # Save keys
            public_path = self.key_dir / f"{name}_public.pem"
            private_path = self.key_dir / f"{name}_private.pem"

            self.pqc_manager.save_public_key(public_key, public_path)
            self.pqc_manager.save_private_key(private_key, private_path)

            # Save metadata
            self._save_metadata(name, {
                'created_at': datetime.now().isoformat(),
                'algorithm': 'RSA-4096',  # Placeholder for Kyber-1024
                'version': 1,
                'active': True
            })

            logger.info(f"Generated key pair: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate key pair {name}: {e}")
            return False

    def load_public_key(self, name: str) -> Optional[Any]:
        """
        Load public key by name.

        Args:
            name: Key pair name

        Returns:
            Public key object or None if not found
        """
        try:
            public_path = self.key_dir / f"{name}_public.pem"
            if not public_path.exists():
                logger.warning(f"Public key not found: {name}")
                return None

            return self.pqc_manager.load_public_key(public_path)

        except Exception as e:
            logger.error(f"Failed to load public key {name}: {e}")
            return None

    def load_private_key(self, name: str) -> Optional[Any]:
        """
        Load private key by name.

        Args:
            name: Key pair name

        Returns:
            Private key object or None if not found
        """
        try:
            private_path = self.key_dir / f"{name}_private.pem"
            if not private_path.exists():
                logger.warning(f"Private key not found: {name}")
                return None

            return self.pqc_manager.load_private_key(private_path)

        except Exception as e:
            logger.error(f"Failed to load private key {name}: {e}")
            return None

    def rotate_keys(self, name: str) -> bool:
        """
        Rotate a key pair (generate new keys, backup old ones).

        Args:
            name: Key pair name to rotate

        Returns:
            True if successful, False otherwise
        """
        try:
            # Backup existing keys
            public_path = self.key_dir / f"{name}_public.pem"
            private_path = self.key_dir / f"{name}_private.pem"

            if public_path.exists() and private_path.exists():
                # Get current version
                metadata = self._load_metadata(name)
                version = metadata.get('version', 1)

                # Backup old keys
                backup_suffix = f".v{version}.backup"
                public_backup = self.key_dir / f"{name}_public{backup_suffix}.pem"
                private_backup = self.key_dir / f"{name}_private{backup_suffix}.pem"

                import shutil
                shutil.copy2(public_path, public_backup)
                shutil.copy2(private_path, private_backup)

                logger.info(f"Backed up keys to version {version}")

            # Generate new key pair
            public_key, private_key = self.pqc_manager.generate_key_pair()

            # Save new keys
            self.pqc_manager.save_public_key(public_key, public_path)
            self.pqc_manager.save_private_key(private_key, private_path)

            # Update metadata
            metadata = self._load_metadata(name) or {}
            metadata['version'] = metadata.get('version', 1) + 1
            metadata['rotated_at'] = datetime.now().isoformat()
            self._save_metadata(name, metadata)

            logger.info(f"Rotated key pair: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to rotate keys {name}: {e}")
            return False

    def list_keys(self) -> List[str]:
        """
        List all key pair names.

        Returns:
            List of key pair names
        """
        try:
            # Find all public keys (they come in pairs)
            public_keys = list(self.key_dir.glob("*_public.pem"))

            # Extract names (remove suffix)
            names = []
            for key_path in public_keys:
                name = key_path.stem.replace("_public", "")
                names.append(name)

            return sorted(names)

        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []

    def delete_key_pair(self, name: str) -> bool:
        """
        Delete a key pair.

        Args:
            name: Key pair name to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            public_path = self.key_dir / f"{name}_public.pem"
            private_path = self.key_dir / f"{name}_private.pem"
            metadata_path = self.key_dir / f"{name}_metadata.json"

            deleted = False
            if public_path.exists():
                public_path.unlink()
                deleted = True
            if private_path.exists():
                private_path.unlink()
                deleted = True
            if metadata_path.exists():
                metadata_path.unlink()

            if deleted:
                logger.info(f"Deleted key pair: {name}")
            else:
                logger.warning(f"Key pair not found: {name}")

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete key pair {name}: {e}")
            return False

    def get_key_metadata(self, name: str) -> Optional[dict]:
        """
        Get metadata for a key pair.

        Args:
            name: Key pair name

        Returns:
            Metadata dictionary or None if not found
        """
        return self._load_metadata(name)

    def _save_metadata(self, name: str, metadata: dict):
        """Save key metadata to JSON file"""
        metadata_path = self.key_dir / f"{name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _load_metadata(self, name: str) -> Optional[dict]:
        """Load key metadata from JSON file"""
        metadata_path = self.key_dir / f"{name}_metadata.json"
        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata for {name}: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        key_dir = Path(tmpdir) / "keys"

        # Create manager
        manager = KeyManager(key_dir=key_dir)

        # Generate key pair
        print("Generating default key pair...")
        success = manager.generate_key_pair("default")
        print(f"Success: {success}")

        # List keys
        keys = manager.list_keys()
        print(f"Available keys: {keys}")

        # Load keys
        public_key = manager.load_public_key("default")
        private_key = manager.load_private_key("default")
        print(f"Loaded keys: public={public_key is not None}, private={private_key is not None}")

        # Get metadata
        metadata = manager.get_key_metadata("default")
        print(f"Metadata: {metadata}")

        # Rotate keys
        print("\nRotating keys...")
        success = manager.rotate_keys("default")
        print(f"Success: {success}")

        # Check new version
        metadata = manager.get_key_metadata("default")
        print(f"New version: {metadata.get('version')}")
