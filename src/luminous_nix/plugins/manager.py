"""
Main plugin manager.

Central coordination of plugin system: discovery, loading, and lifecycle.
"""

import logging
from typing import Dict, List, Optional, Set
from pathlib import Path

from .base import Plugin, PluginConfig, PluginContext, PluginInfo, PluginStatus
from .discovery import PluginDiscovery, PluginManifest
from .lifecycle import PluginLifecycleManager
from .validator import PluginValidator
from .config import PluginConfigManager
from .errors import (
    PluginNotFoundError,
    PluginValidationError,
    PluginLoadError
)


class PluginManager:
    """
    Central plugin management system.

    Coordinates plugin discovery, validation, loading, and lifecycle.
    """

    def __init__(self, config: Optional[PluginConfig] = None, auto_load: bool = False):
        """
        Initialize plugin manager.

        Args:
            config: Plugin configuration (uses defaults if None)
            auto_load: Whether to automatically load plugins from config
        """
        self.config = config or PluginConfig()
        self.logger = logging.getLogger(__name__)

        # Systems
        self.discovery = PluginDiscovery(self.config)
        self.validator = PluginValidator(self.config)
        self.lifecycle = PluginLifecycleManager(self.config)
        self.config_manager = PluginConfigManager()

        # Plugin registry
        self._plugins: Dict[str, Plugin] = {}
        self._manifests: Dict[str, PluginManifest] = {}

        # Plugin type registry
        self._plugins_by_type: Dict[str, List[Plugin]] = {
            "operation": [],
            "security": [],
            "hook": [],
            "ai": []
        }

        # Core system references (set by integrate_with_core)
        self._state_manager = None
        self._security = None
        self._ai = None
        self._executor = None

        self.logger.info("Plugin manager initialized")

        # Auto-load plugins if requested
        if auto_load:
            self.auto_load_plugins()

    def discover_plugins(self) -> List[PluginManifest]:
        """
        Discover all available plugins.

        Returns:
            List of discovered plugin manifests
        """
        manifests = self.discovery.discover_all()
        for manifest in manifests:
            self._manifests[manifest.name] = manifest
        return manifests

    def load_plugin(self, plugin_name: str) -> Plugin:
        """
        Load a specific plugin by name.

        Args:
            plugin_name: Name of plugin to load

        Returns:
            Loaded and activated plugin

        Raises:
            PluginNotFoundError: If plugin not found
            PluginValidationError: If plugin invalid
            PluginLoadError: If loading fails
        """
        # Check if already loaded
        if plugin_name in self._plugins:
            self.logger.debug(f"Plugin {plugin_name} already loaded")
            return self._plugins[plugin_name]

        # Find manifest
        if plugin_name not in self._manifests:
            manifest = self.discovery.find_plugin(plugin_name)
            if not manifest:
                raise PluginNotFoundError(f"Plugin '{plugin_name}' not found")
            self._manifests[plugin_name] = manifest
        else:
            manifest = self._manifests[plugin_name]

        # Validate (basic validation - security validation is separate)
        if not self._validate_plugin(manifest):
            raise PluginValidationError(f"Plugin '{plugin_name}' failed validation")

        # Create context
        context = self._create_plugin_context(manifest)

        # Load through lifecycle
        plugin = self.lifecycle.load_plugin(manifest, context)

        # Register
        self._plugins[plugin_name] = plugin
        self._plugins_by_type[plugin.type].append(plugin)

        self.logger.info(f"Loaded plugin: {plugin_name} v{manifest.version}")
        return plugin

    def unload_plugin(self, plugin_name: str):
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Note: Gracefully handles unloading nonexistent plugins (no error)
        """
        if plugin_name not in self._plugins:
            self.logger.debug(f"Plugin '{plugin_name}' not loaded, skipping unload")
            return

        plugin = self._plugins[plugin_name]

        # Unload through lifecycle
        self.lifecycle.unload_plugin(plugin_name)

        # Unregister
        del self._plugins[plugin_name]
        self._plugins_by_type[plugin.type].remove(plugin)

        self.logger.info(f"Unloaded plugin: {plugin_name}")

    def reload_plugin(self, plugin_name: str) -> Plugin:
        """
        Reload a plugin (unload and load again).

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            Reloaded plugin instance

        Raises:
            PluginNotFoundError: If plugin not found
            PluginLoadError: If reload fails
        """
        # Unload if loaded
        if plugin_name in self._plugins:
            self.unload_plugin(plugin_name)

        # Clear cached manifest to force re-discovery
        if plugin_name in self._manifests:
            del self._manifests[plugin_name]

        # Load fresh
        plugin = self.load_plugin(plugin_name)
        self.logger.info(f"Reloaded plugin: {plugin_name}")
        return plugin

    def load_all_plugins(self) -> Dict[str, Plugin]:
        """
        Load all discovered plugins.

        Returns:
            Dict mapping plugin names to loaded plugins

        Note: Failures are logged but don't stop other plugins from loading
        """
        manifests = self.discover_plugins()
        loaded = {}

        for manifest in manifests:
            try:
                plugin = self.load_plugin(manifest.name)
                loaded[manifest.name] = plugin
            except Exception as e:
                self.logger.error(f"Failed to load {manifest.name}: {e}")

        self.logger.info(f"Loaded {len(loaded)}/{len(manifests)} plugins")
        return loaded

    def auto_load_plugins(self) -> Dict[str, Plugin]:
        """
        Auto-load plugins from configuration.

        Loads all plugins in the autoload list from config file.

        Returns:
            Dict mapping plugin names to loaded plugins

        Note: Failures are logged but don't stop other plugins from loading
        """
        # Discover plugins first
        self.discover_plugins()

        # Get autoload list
        autoload_list = self.config_manager.get_autoload_plugins()

        if not autoload_list:
            self.logger.debug("No plugins in autoload list")
            return {}

        self.logger.info(f"Auto-loading {len(autoload_list)} plugin(s)")
        loaded = {}

        for plugin_name in autoload_list:
            try:
                plugin = self.load_plugin(plugin_name)
                loaded[plugin_name] = plugin
                self.logger.info(f"Auto-loaded: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Failed to auto-load {plugin_name}: {e}")

        self.logger.info(f"Auto-loaded {len(loaded)}/{len(autoload_list)} plugins")
        return loaded

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by name.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin if loaded, None otherwise
        """
        return self._plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: str) -> List[Plugin]:
        """
        Get all loaded plugins of a specific type.

        Args:
            plugin_type: Type of plugins to get ("operation", "security", "hook", "ai")

        Returns:
            List of plugins of that type
        """
        return self._plugins_by_type.get(plugin_type, [])

    def get_operation_plugins(self) -> List[Plugin]:
        """
        Get all loaded operation plugins.

        Returns:
            List of operation plugins
        """
        return self.get_plugins_by_type("operation")

    def get_security_plugins(self) -> List[Plugin]:
        """
        Get all loaded security plugins.

        Returns:
            List of security plugins
        """
        return self.get_plugins_by_type("security")

    def get_hook_plugins(self) -> List[Plugin]:
        """
        Get all loaded hook plugins.

        Returns:
            List of hook plugins
        """
        return self.get_plugins_by_type("hook")

    def get_ai_plugins(self) -> List[Plugin]:
        """
        Get all loaded AI plugins.

        Returns:
            List of AI plugins
        """
        return self.get_plugins_by_type("ai")

    def list_plugins(self, include_inactive: bool = False) -> List[PluginInfo]:
        """
        List all plugins.

        Args:
            include_inactive: Include disabled plugins

        Returns:
            List of plugin information
        """
        plugins = []

        for plugin in self._plugins.values():
            if not include_inactive and plugin.status != PluginStatus.ACTIVE:
                continue

            plugins.append(PluginInfo(
                name=plugin.metadata.name,
                version=plugin.metadata.version,
                type=plugin.type,
                status=plugin.status,
                description=plugin.metadata.description,
                author=plugin.metadata.author,
                enabled=plugin.enabled
            ))

        return plugins

    def activate_plugin(self, plugin_name: str):
        """
        Activate a disabled plugin.

        Args:
            plugin_name: Name of plugin to activate
        """
        self.lifecycle.activate_plugin(plugin_name)

    def deactivate_plugin(self, plugin_name: str):
        """
        Deactivate an active plugin.

        Args:
            plugin_name: Name of plugin to deactivate
        """
        self.lifecycle.deactivate_plugin(plugin_name)

    def integrate_with_core(
        self,
        state_manager=None,
        security=None,
        ai=None,
        executor=None
    ):
        """
        Integrate plugin system with core Luminous Nix systems.

        This allows plugins to access core functionality.

        Args:
            state_manager: StateManager instance
            security: Security system instance
            ai: AI system instance
            executor: Executor instance
        """
        self._state_manager = state_manager
        self._security = security
        self._ai = ai
        self._executor = executor

        self.logger.info("Plugin system integrated with core")

    def shutdown(self):
        """Shutdown plugin system and unload all plugins"""
        self.lifecycle.shutdown()
        self._plugins.clear()
        self._plugins_by_type = {k: [] for k in self._plugins_by_type}
        self.logger.info("Plugin system shutdown")

    # Private methods

    def _validate_plugin(self, manifest: PluginManifest) -> bool:
        """
        Validate plugin using security validator.

        Args:
            manifest: Plugin manifest

        Returns:
            True if plugin is valid

        Raises:
            PluginValidationError: If validation fails
        """
        return self.validator.validate(manifest)

    def _create_plugin_context(self, manifest: PluginManifest) -> PluginContext:
        """
        Create plugin context.

        Args:
            manifest: Plugin manifest

        Returns:
            Plugin context with core systems and permissions
        """
        # Create context with core systems
        context = PluginContext(
            state_manager=self._state_manager,
            security=self._security,
            ai=self._ai,
            executor=self._executor
        )

        # Plugin-specific context
        context.plugin_name = manifest.name
        context.plugin_dir = manifest.plugin_dir

        # Permissions (for now, grant all requested - security validation will restrict)
        context.permissions = set(manifest.requires_permissions)

        return context


# Export
__all__ = ['PluginManager']
