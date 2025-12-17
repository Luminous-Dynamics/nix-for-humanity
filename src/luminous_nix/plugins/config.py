"""
Plugin configuration management.

Handles persistent storage of plugin settings including:
- Enabled plugins (auto-load on startup)
- Plugin preferences
- Installation sources
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)

# Import tomllib for Python 3.11+, fallback to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None
        logger.warning("No TOML library available - plugin config will not persist")


@dataclass
class PluginConfigData:
    """Plugin configuration data structure."""

    # Plugins to auto-load on startup
    autoload: List[str] = field(default_factory=list)

    # Plugin-specific settings (future use)
    plugin_settings: Dict[str, Dict] = field(default_factory=dict)

    # Installation sources for updates (future use)
    sources: Dict[str, str] = field(default_factory=dict)


class PluginConfigManager:
    """
    Manages persistent plugin configuration.

    Configuration file location: ~/.config/luminous-nix/plugins.toml

    Features:
    - Auto-load enabled plugins on startup
    - Save plugin state across sessions
    - Plugin-specific settings storage
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize plugin configuration manager.

        Args:
            config_path: Optional custom config file path
                        Default: ~/.config/luminous-nix/plugins.toml
        """
        if config_path is None:
            config_dir = Path.home() / ".config" / "luminous-nix"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "plugins.toml"
        else:
            self.config_path = config_path

        self.config = PluginConfigData()
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            logger.info(f"No plugin config found at {self.config_path}, using defaults")
            return

        if tomllib is None:
            logger.warning("Cannot load plugin config - no TOML library available")
            return

        try:
            with open(self.config_path, 'rb') as f:
                data = tomllib.load(f)

            # Load autoload list
            self.config.autoload = data.get('autoload', [])

            # Load plugin settings
            self.config.plugin_settings = data.get('plugins', {})

            # Load sources
            self.config.sources = data.get('sources', {})

            logger.info(f"Loaded plugin config from {self.config_path}")
            logger.debug(f"Auto-load plugins: {self.config.autoload}")
        except Exception as e:
            logger.error(f"Failed to load plugin config: {e}")

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Build TOML content
            lines = []
            lines.append("# Luminous Nix Plugin Configuration")
            lines.append("# Auto-generated - modify with 'ask-nix plugins autoload' commands")
            lines.append("")

            # Autoload section
            lines.append("# Plugins to automatically load on startup")
            lines.append("autoload = [")
            for plugin in self.config.autoload:
                lines.append(f'    "{plugin}",')
            lines.append("]")
            lines.append("")

            # Sources section (future use)
            if self.config.sources:
                lines.append("# Plugin installation sources")
                lines.append("[sources]")
                for name, source in self.config.sources.items():
                    lines.append(f'{name} = "{source}"')
                lines.append("")

            # Plugin settings (future use)
            if self.config.plugin_settings:
                lines.append("# Plugin-specific settings")
                for plugin, settings in self.config.plugin_settings.items():
                    lines.append(f"[plugins.{plugin}]")
                    for key, value in settings.items():
                        if isinstance(value, str):
                            lines.append(f'{key} = "{value}"')
                        else:
                            lines.append(f'{key} = {value}')
                    lines.append("")

            # Write to file
            content = "\n".join(lines)
            self.config_path.write_text(content)
            logger.info(f"Saved plugin config to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save plugin config: {e}")

    def get_autoload_plugins(self) -> List[str]:
        """Get list of plugins to auto-load."""
        return self.config.autoload.copy()

    def add_to_autoload(self, plugin_name: str) -> bool:
        """
        Add plugin to auto-load list.

        Args:
            plugin_name: Name of plugin to auto-load

        Returns:
            True if added, False if already in list
        """
        if plugin_name in self.config.autoload:
            return False

        self.config.autoload.append(plugin_name)
        self._save_config()
        logger.info(f"Added '{plugin_name}' to auto-load")
        return True

    def remove_from_autoload(self, plugin_name: str) -> bool:
        """
        Remove plugin from auto-load list.

        Args:
            plugin_name: Name of plugin to remove

        Returns:
            True if removed, False if not in list
        """
        if plugin_name not in self.config.autoload:
            return False

        self.config.autoload.remove(plugin_name)
        self._save_config()
        logger.info(f"Removed '{plugin_name}' from auto-load")
        return True

    def is_autoload(self, plugin_name: str) -> bool:
        """Check if plugin is in auto-load list."""
        return plugin_name in self.config.autoload

    def set_plugin_setting(self, plugin_name: str, key: str, value: any) -> None:
        """
        Set a plugin-specific setting.

        Args:
            plugin_name: Name of plugin
            key: Setting key
            value: Setting value
        """
        if plugin_name not in self.config.plugin_settings:
            self.config.plugin_settings[plugin_name] = {}

        self.config.plugin_settings[plugin_name][key] = value
        self._save_config()

    def get_plugin_setting(self, plugin_name: str, key: str, default=None) -> any:
        """
        Get a plugin-specific setting.

        Args:
            plugin_name: Name of plugin
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        return self.config.plugin_settings.get(plugin_name, {}).get(key, default)

    def set_plugin_source(self, plugin_name: str, source: str) -> None:
        """
        Record plugin installation source.

        Args:
            plugin_name: Name of plugin
            source: Installation source (URL, path, etc.)
        """
        self.config.sources[plugin_name] = source
        self._save_config()

    def get_plugin_source(self, plugin_name: str) -> Optional[str]:
        """Get plugin installation source."""
        return self.config.sources.get(plugin_name)


# Global config instance
_config_manager: Optional[PluginConfigManager] = None


def get_config_manager() -> PluginConfigManager:
    """Get or create global plugin config manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = PluginConfigManager()
    return _config_manager
