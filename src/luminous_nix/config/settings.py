"""
Settings - Configuration for PQC encryption and security

This module provides configuration settings for:
- Encryption enabled/disabled
- Key directory location
- Backup configuration
- Security preferences

Week 9-10: PQC Integration
"""

from pathlib import Path
from typing import Optional
import os
import json
import logging

logger = logging.getLogger(__name__)


class Settings:
    """
    Configuration settings for Luminous Nix security features.

    Provides defaults and customization for PQC encryption,
    key management, and backup policies.
    """

    def __init__(
        self,
        key_directory: Optional[Path] = None,
        encryption_enabled: bool = True,
        backup_enabled: bool = True,
        max_backups: int = 10,
        auto_backup_interval_hours: int = 24
    ):
        """
        Initialize settings.

        Args:
            key_directory: Directory for encryption keys
                          (default: ~/.luminous-nix/keys)
            encryption_enabled: Enable encrypted state storage
                               (default: True)
            backup_enabled: Enable automatic backups
                           (default: True)
            max_backups: Maximum number of backups to keep
                        (default: 10)
            auto_backup_interval_hours: Hours between automatic backups
                                       (default: 24)
        """
        # Set defaults
        if key_directory is None:
            home = Path(os.path.expanduser("~"))
            key_directory = home / ".luminous-nix" / "keys"

        self.key_directory = Path(key_directory)
        self.encryption_enabled = encryption_enabled
        self.backup_enabled = backup_enabled
        self.max_backups = max_backups
        self.auto_backup_interval_hours = auto_backup_interval_hours

        # Derived paths
        self.storage_dir = self.key_directory.parent / "storage"
        self.backup_dir = self.key_directory.parent / "backups"
        self.config_file = self.key_directory.parent / "settings.json"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'Settings':
        """
        Load settings from JSON file.

        Args:
            config_path: Path to config file
                        (default: ~/.luminous-nix/settings.json)

        Returns:
            Settings instance
        """
        if config_path is None:
            home = Path(os.path.expanduser("~"))
            config_path = home / ".luminous-nix" / "settings.json"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            logger.info(f"Config not found, using defaults: {config_path}")
            return cls()

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)

            # Convert path strings back to Path objects
            if 'key_directory' in data:
                data['key_directory'] = Path(data['key_directory'])

            return cls(**data)

        except Exception as e:
            logger.error(f"Failed to load settings from {config_path}: {e}")
            return cls()

    def save(self, config_path: Optional[Path] = None):
        """
        Save settings to JSON file.

        Args:
            config_path: Path to config file
                        (default: self.config_file)
        """
        if config_path is None:
            config_path = self.config_file
        else:
            config_path = Path(config_path)

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                'key_directory': str(self.key_directory),
                'encryption_enabled': self.encryption_enabled,
                'backup_enabled': self.backup_enabled,
                'max_backups': self.max_backups,
                'auto_backup_interval_hours': self.auto_backup_interval_hours
            }

            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved settings to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save settings to {config_path}: {e}")

    def to_dict(self) -> dict:
        """
        Convert settings to dictionary.

        Returns:
            Dictionary representation of settings
        """
        return {
            'key_directory': str(self.key_directory),
            'encryption_enabled': self.encryption_enabled,
            'backup_enabled': self.backup_enabled,
            'max_backups': self.max_backups,
            'auto_backup_interval_hours': self.auto_backup_interval_hours,
            'storage_dir': str(self.storage_dir),
            'backup_dir': str(self.backup_dir)
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"Settings(encryption={self.encryption_enabled}, keys={self.key_directory})"


# Global default settings instance
_default_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance.

    Loads from default location on first call, then caches.

    Returns:
        Settings instance
    """
    global _default_settings

    if _default_settings is None:
        _default_settings = Settings.load()

    return _default_settings


def set_settings(settings: Settings):
    """
    Set global settings instance.

    Args:
        settings: Settings instance to use globally
    """
    global _default_settings
    _default_settings = settings


if __name__ == "__main__":
    # Example usage
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create settings
        print("Creating settings...")
        settings = Settings(
            key_directory=tmpdir_path / "keys",
            encryption_enabled=True,
            max_backups=5
        )

        print(f"Settings: {settings}")
        print(f"Key directory: {settings.key_directory}")
        print(f"Encryption enabled: {settings.encryption_enabled}")
        print(f"Max backups: {settings.max_backups}")

        # Save settings
        config_path = tmpdir_path / "settings.json"
        settings.save(config_path)
        print(f"\nSaved to: {config_path}")

        # Load settings
        print("\nLoading settings...")
        loaded = Settings.load(config_path)
        print(f"Loaded: {loaded}")
        print(f"Encryption enabled: {loaded.encryption_enabled}")

        # Dictionary representation
        print("\nDictionary:")
        import json
        print(json.dumps(settings.to_dict(), indent=2))
