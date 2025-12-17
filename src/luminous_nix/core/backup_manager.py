"""
BackupManager - Encrypted backups for operation history

This module provides encrypted backup and restore functionality:
- Create encrypted archives of operation state
- Restore from encrypted backups
- Automatic backup rotation

Week 9-10: PQC Integration
"""

from pathlib import Path
from typing import Optional, List
import logging
from datetime import datetime
import tarfile
import tempfile
import shutil

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Manages encrypted backups of operation history.

    Creates encrypted tar.gz archives and supports restoration
    with automatic rotation to keep only N most recent backups.
    """

    def __init__(
        self,
        storage_dir: Path,
        backup_dir: Path,
        max_backups: int = 10
    ):
        """
        Initialize BackupManager.

        Args:
            storage_dir: Directory containing operation states to backup
            backup_dir: Directory to store backup archives
            max_backups: Maximum number of backups to keep (default: 10)
        """
        self.storage_dir = Path(storage_dir)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Initialize PQC encryption
        try:
            from luminous_nix.security.pqc import PQCKeyManager, PQCEncryption
            self.key_manager = PQCKeyManager()
            self.public_key, self.private_key = self.key_manager.generate_key_pair()
            self.encryption = PQCEncryption()
        except ImportError as e:
            logger.error(f"Failed to import PQC module: {e}")
            raise

    def create_backup(self) -> Path:
        """
        Create encrypted backup of all operation states.

        Returns:
            Path to created backup file

        Raises:
            Exception if backup creation fails
        """
        try:
            # Generate backup filename with timestamp (including microseconds for uniqueness)
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            microseconds = now.microsecond // 1000  # milliseconds (0-999)
            backup_name = f"backup_{timestamp}_{microseconds:03d}"

            # Create temporary directory for tar archive
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                tar_path = tmpdir_path / f"{backup_name}.tar.gz"

                # Create tar.gz archive of storage directory
                logger.info(f"Creating tar archive from {self.storage_dir}")
                with tarfile.open(tar_path, "w:gz") as tar:
                    # Add files from storage_dir directly (no arcname to avoid subdirectory)
                    for item in self.storage_dir.iterdir():
                        tar.add(item, arcname=item.name)

                # Read archive data
                archive_data = tar_path.read_bytes()
                logger.info(f"Archive size: {len(archive_data)} bytes")

                # Encrypt archive
                encrypted_data = self.encryption.encrypt(archive_data, self.public_key)
                logger.info(f"Encrypted size: {len(encrypted_data)} bytes")

                # Save encrypted backup
                backup_path = self.backup_dir / f"{backup_name}.encrypted"
                backup_path.write_bytes(encrypted_data)

                logger.info(f"Created encrypted backup: {backup_path}")

                # Rotate old backups
                self._rotate_backups()

                return backup_path

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    def restore_backup(self, backup_path: Path, restore_dir: Path) -> bool:
        """
        Restore from encrypted backup.

        Args:
            backup_path: Path to encrypted backup file
            restore_dir: Directory to restore into

        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            restore_dir = Path(restore_dir)

            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False

            # Read encrypted backup
            encrypted_data = backup_path.read_bytes()
            logger.info(f"Reading encrypted backup: {len(encrypted_data)} bytes")

            # Decrypt
            archive_data = self.encryption.decrypt(encrypted_data, self.private_key)
            logger.info(f"Decrypted archive: {len(archive_data)} bytes")

            # Extract to temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                tar_path = tmpdir_path / "backup.tar.gz"

                # Write decrypted archive
                tar_path.write_bytes(archive_data)

                # Extract tar archive
                logger.info(f"Extracting to {restore_dir}")
                with tarfile.open(tar_path, "r:gz") as tar:
                    # Extract to restore directory
                    tar.extractall(path=restore_dir)

                logger.info(f"Successfully restored backup to {restore_dir}")
                return True

        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    def list_backups(self) -> List[Path]:
        """
        List all available backups.

        Returns:
            List of backup file paths, sorted by creation time (newest first)
        """
        try:
            backups = list(self.backup_dir.glob("backup_*.encrypted"))
            # Sort by modification time, newest first
            backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return backups
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    def delete_backup(self, backup_path: Path) -> bool:
        """
        Delete a backup file.

        Args:
            backup_path: Path to backup file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            if backup_path.exists():
                backup_path.unlink()
                logger.info(f"Deleted backup: {backup_path}")
                return True
            else:
                logger.warning(f"Backup not found: {backup_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False

    def _rotate_backups(self):
        """
        Rotate backups to keep only max_backups most recent.

        Automatically called after creating a backup.
        """
        try:
            backups = self.list_backups()

            if len(backups) > self.max_backups:
                # Delete oldest backups
                to_delete = backups[self.max_backups:]
                logger.info(f"Rotating backups: deleting {len(to_delete)} old backups")

                for backup_path in to_delete:
                    self.delete_backup(backup_path)

        except Exception as e:
            logger.error(f"Failed to rotate backups: {e}")

    def get_backup_info(self, backup_path: Path) -> Optional[dict]:
        """
        Get information about a backup file.

        Args:
            backup_path: Path to backup file

        Returns:
            Dictionary with backup metadata or None if not found
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                return None

            stat = backup_path.stat()

            # Parse timestamp from filename
            name = backup_path.stem  # removes .encrypted
            timestamp_str = name.replace("backup_", "")

            try:
                # Try new format with milliseconds first
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S_%f")
            except ValueError:
                try:
                    # Fall back to old format without milliseconds
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                except ValueError:
                    # Fall back to file modification time
                    timestamp = datetime.fromtimestamp(stat.st_mtime)

            return {
                'path': backup_path,
                'size': stat.st_size,
                'created': timestamp,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            }

        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test structure
        storage_dir = tmpdir_path / "storage"
        backup_dir = tmpdir_path / "backups"
        restore_dir = tmpdir_path / "restored"

        storage_dir.mkdir()
        backup_dir.mkdir()
        restore_dir.mkdir()

        # Create some test files
        (storage_dir / "test1.txt").write_text("Test data 1")
        (storage_dir / "test2.txt").write_text("Test data 2")

        # Create backup manager
        manager = BackupManager(
            storage_dir=storage_dir,
            backup_dir=backup_dir,
            max_backups=3
        )

        # Create backup
        print("Creating backup...")
        backup_path = manager.create_backup()
        print(f"Backup created: {backup_path}")

        # Get backup info
        info = manager.get_backup_info(backup_path)
        print(f"Backup info: {info}")

        # List backups
        backups = manager.list_backups()
        print(f"Available backups: {len(backups)}")

        # Restore backup
        print("\nRestoring backup...")
        success = manager.restore_backup(backup_path, restore_dir)
        print(f"Restore success: {success}")

        # Check restored files
        restored_files = list((restore_dir / "storage").glob("*.txt"))
        print(f"Restored files: {[f.name for f in restored_files]}")

        # Test rotation
        print("\nTesting backup rotation...")
        for i in range(5):
            manager.create_backup()

        backups = manager.list_backups()
        print(f"Backups after rotation (max=3): {len(backups)}")
