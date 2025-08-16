"""
Plugin Discovery System.

Automatically discovers plugins from multiple sources:
- Built-in plugins directory
- User plugins directory
- System plugins directory
- Python packages with naming convention

Since: v1.0.0
"""

import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import pkg_resources

from ..constants import MAX_FILE_SIZE_MB
from ..core.logging_config import get_logger
from .base import Plugin, PluginMetadata

logger = get_logger(__name__)


class PluginDiscovery:
    """
    Discovers and catalogs available plugins.

    Searches multiple locations for plugins and maintains
    a registry of discovered plugins with their metadata.

    Since: v1.0.0
    """

    # Plugin discovery paths
    BUILTIN_DIR = Path(__file__).parent / "builtin"
    USER_DIR = Path.home() / ".config" / "nix-humanity" / "plugins"
    SYSTEM_DIR = Path("/usr/share/nix-humanity/plugins")

    # Plugin naming convention for packages
    PACKAGE_PREFIX = "nix_humanity_plugin_"

    def __init__(self):
        """Initialize plugin discovery system."""
        self.discovered_plugins: dict[str, PluginMetadata] = {}
        self.plugin_paths: dict[str, Path] = {}
        self.plugin_modules: dict[str, Any] = {}

    def discover_all(self) -> dict[str, PluginMetadata]:
        """
        Discover all available plugins.

        Returns:
            Dictionary mapping plugin names to metadata
        """
        self.discovered_plugins.clear()
        self.plugin_paths.clear()

        # Discover from all sources
        self._discover_builtin_plugins()
        self._discover_user_plugins()
        self._discover_system_plugins()
        self._discover_package_plugins()

        logger.info(f"Discovered {len(self.discovered_plugins)} plugins")
        return self.discovered_plugins

    def _discover_builtin_plugins(self) -> None:
        """Discover built-in plugins."""
        if not self.BUILTIN_DIR.exists():
            logger.debug("Built-in plugins directory not found")
            return

        for plugin_file in self.BUILTIN_DIR.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                metadata = self._load_plugin_metadata(plugin_file)
                if metadata:
                    self.discovered_plugins[metadata.name] = metadata
                    self.plugin_paths[metadata.name] = plugin_file
                    logger.debug(f"Discovered builtin plugin: {metadata.name}")
            except Exception as e:
                logger.warning(f"Failed to load builtin plugin {plugin_file}: {e}")

    def _discover_user_plugins(self) -> None:
        """Discover user-installed plugins."""
        if not self.USER_DIR.exists():
            logger.debug("User plugins directory not found")
            return

        for plugin_dir in self.USER_DIR.iterdir():
            if not plugin_dir.is_dir():
                continue

            manifest_file = plugin_dir / "manifest.json"
            if not manifest_file.exists():
                continue

            try:
                with open(manifest_file) as f:
                    manifest = json.load(f)

                metadata = PluginMetadata(**manifest)
                self.discovered_plugins[metadata.name] = metadata
                self.plugin_paths[metadata.name] = plugin_dir / "plugin.py"
                logger.debug(f"Discovered user plugin: {metadata.name}")
            except Exception as e:
                logger.warning(f"Failed to load user plugin {plugin_dir}: {e}")

    def _discover_system_plugins(self) -> None:
        """Discover system-wide plugins."""
        if not self.SYSTEM_DIR.exists():
            logger.debug("System plugins directory not found")
            return

        # Similar to user plugins
        for plugin_dir in self.SYSTEM_DIR.iterdir():
            if not plugin_dir.is_dir():
                continue

            manifest_file = plugin_dir / "manifest.json"
            if not manifest_file.exists():
                continue

            try:
                with open(manifest_file) as f:
                    manifest = json.load(f)

                metadata = PluginMetadata(**manifest)
                self.discovered_plugins[metadata.name] = metadata
                self.plugin_paths[metadata.name] = plugin_dir / "plugin.py"
                logger.debug(f"Discovered system plugin: {metadata.name}")
            except Exception as e:
                logger.warning(f"Failed to load system plugin {plugin_dir}: {e}")

    def _discover_package_plugins(self) -> None:
        """Discover plugins installed as Python packages."""
        for entry_point in pkg_resources.iter_entry_points("nix_humanity.plugins"):
            try:
                plugin_class = entry_point.load()

                # Create temporary instance to get metadata
                temp_instance = plugin_class()
                metadata = temp_instance.get_metadata()

                self.discovered_plugins[metadata.name] = metadata
                self.plugin_modules[metadata.name] = plugin_class
                logger.debug(f"Discovered package plugin: {metadata.name}")
            except Exception as e:
                logger.warning(f"Failed to load package plugin {entry_point.name}: {e}")

    def _load_plugin_metadata(self, plugin_file: Path) -> PluginMetadata | None:
        """
        Load metadata from a plugin file.

        Args:
            plugin_file: Path to plugin Python file

        Returns:
            PluginMetadata if successful, None otherwise
        """
        try:
            # Check file size
            if plugin_file.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                logger.warning(f"Plugin file too large: {plugin_file}")
                return None

            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_file.stem}", plugin_file
            )
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Plugin subclass
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                    # Create instance to get metadata
                    instance = obj()
                    return instance.get_metadata()

            return None

        except Exception as e:
            logger.error(f"Error loading plugin metadata from {plugin_file}: {e}")
            return None

    def get_plugin_info(self, name: str) -> PluginMetadata | None:
        """
        Get information about a specific plugin.

        Args:
            name: Plugin name

        Returns:
            PluginMetadata if found, None otherwise
        """
        return self.discovered_plugins.get(name)

    def list_plugins(
        self,
        filter_compatible: bool = True,
        filter_keywords: list[str] | None = None,
    ) -> list[PluginMetadata]:
        """
        List discovered plugins with optional filtering.

        Args:
            filter_compatible: Only show compatible plugins
            filter_keywords: Filter by keywords

        Returns:
            List of plugin metadata
        """
        plugins = list(self.discovered_plugins.values())

        if filter_compatible:
            plugins = [p for p in plugins if p.is_compatible()]

        if filter_keywords:
            plugins = [
                p for p in plugins if any(kw in p.keywords for kw in filter_keywords)
            ]

        return plugins

    def search_plugins(self, query: str) -> list[PluginMetadata]:
        """
        Search for plugins matching a query.

        Args:
            query: Search query

        Returns:
            List of matching plugins
        """
        query_lower = query.lower()
        results = []

        for metadata in self.discovered_plugins.values():
            # Search in name, description, and keywords
            if (
                query_lower in metadata.name.lower()
                or query_lower in metadata.description.lower()
                or any(query_lower in kw.lower() for kw in metadata.keywords)
            ):
                results.append(metadata)

        return results
