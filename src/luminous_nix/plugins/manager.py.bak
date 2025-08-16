"""
Plugin Manager for Nix for Humanity.

Manages the lifecycle of plugins including loading, initialization,
hook management, and execution.

Since: v1.0.0
"""

from typing import Any

from ..core.logging_config import get_logger
from ..types import ExecutionContext, Intent, QueryResult
from .base import Plugin, PluginMetadata, PluginState
from .discovery import PluginDiscovery
from .hooks import HookManager
from .loader import PluginLoader

logger = get_logger(__name__)


class PluginManager:
    """
    Central plugin management system.

    Coordinates plugin discovery, loading, initialization,
    and hook execution throughout the application lifecycle.

    Features:
        - Lazy loading for performance
        - Dependency resolution
        - Hook priority management
        - Error isolation
        - Hot reloading support

    Since: v1.0.0
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize plugin manager.

        Args:
            config: Configuration for plugin system
        """
        self.config = config or {}
        self.discovery = PluginDiscovery()
        self.loader = PluginLoader()
        self.hook_manager = HookManager()

        self.plugins: dict[str, Plugin] = {}
        self.plugin_states: dict[str, PluginState] = {}
        self.disabled_plugins: set[str] = set(self.config.get("disabled_plugins", []))

        # Auto-discover on initialization
        if self.config.get("auto_discover", True):
            self.discover_plugins()

    def discover_plugins(self) -> dict[str, PluginMetadata]:
        """
        Discover all available plugins.

        Returns:
            Dictionary of discovered plugin metadata
        """
        logger.info("Discovering plugins...")
        discovered = self.discovery.discover_all()

        # Update states for newly discovered plugins
        for name in discovered:
            if name not in self.plugin_states:
                self.plugin_states[name] = PluginState.DISCOVERED

        logger.info(f"Found {len(discovered)} plugins")
        return discovered

    def load_plugin(self, name: str) -> bool:
        """
        Load a specific plugin.

        Args:
            name: Plugin name to load

        Returns:
            True if successfully loaded
        """
        if name in self.disabled_plugins:
            logger.info(f"Plugin {name} is disabled")
            return False

        if name in self.plugins:
            logger.debug(f"Plugin {name} already loaded")
            return True

        try:
            # Get plugin metadata
            metadata = self.discovery.get_plugin_info(name)
            if not metadata:
                logger.error(f"Plugin {name} not found")
                return False

            # Check compatibility
            if not metadata.is_compatible():
                logger.error(f"Plugin {name} is not compatible")
                self.plugin_states[name] = PluginState.ERROR
                return False

            # Load dependencies first
            for dep in metadata.dependencies:
                if not self.load_plugin(dep):
                    logger.error(f"Failed to load dependency {dep} for {name}")
                    return False

            # Load the plugin
            plugin = self.loader.load_plugin(name, self.discovery)
            if not plugin:
                logger.error(f"Failed to load plugin {name}")
                self.plugin_states[name] = PluginState.ERROR
                return False

            # Initialize plugin
            if not plugin.initialize():
                logger.error(f"Failed to initialize plugin {name}")
                self.plugin_states[name] = PluginState.ERROR
                return False

            # Register plugin
            self.plugins[name] = plugin
            self.plugin_states[name] = PluginState.LOADED

            # Register hooks
            self._register_plugin_hooks(plugin)

            logger.info(f"Successfully loaded plugin: {name}")
            return True

        except Exception as e:
            logger.error(f"Error loading plugin {name}: {e}")
            self.plugin_states[name] = PluginState.ERROR
            return False

    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin.

        Args:
            name: Plugin name to unload

        Returns:
            True if successfully unloaded
        """
        if name not in self.plugins:
            logger.debug(f"Plugin {name} not loaded")
            return True

        try:
            plugin = self.plugins[name]

            # Cleanup plugin
            plugin.cleanup()

            # Unregister hooks
            self._unregister_plugin_hooks(plugin)

            # Remove from registry
            del self.plugins[name]
            self.plugin_states[name] = PluginState.DISCOVERED

            logger.info(f"Unloaded plugin: {name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin {name}: {e}")
            return False

    def reload_plugin(self, name: str) -> bool:
        """
        Reload a plugin (unload then load).

        Args:
            name: Plugin name to reload

        Returns:
            True if successfully reloaded
        """
        logger.info(f"Reloading plugin: {name}")

        if name in self.plugins:
            if not self.unload_plugin(name):
                return False

        return self.load_plugin(name)

    def enable_plugin(self, name: str) -> bool:
        """
        Enable a disabled plugin.

        Args:
            name: Plugin name to enable

        Returns:
            True if enabled
        """
        if name in self.disabled_plugins:
            self.disabled_plugins.remove(name)
            logger.info(f"Enabled plugin: {name}")
            return self.load_plugin(name)
        return True

    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin.

        Args:
            name: Plugin name to disable

        Returns:
            True if disabled
        """
        self.disabled_plugins.add(name)
        logger.info(f"Disabled plugin: {name}")

        if name in self.plugins:
            return self.unload_plugin(name)
        return True

    def load_all_plugins(self) -> int:
        """
        Load all discovered plugins.

        Returns:
            Number of successfully loaded plugins
        """
        loaded = 0
        for name in self.discovery.discovered_plugins:
            if self.load_plugin(name):
                loaded += 1
        return loaded

    def get_plugin(self, name: str) -> Plugin | None:
        """
        Get a loaded plugin instance.

        Args:
            name: Plugin name

        Returns:
            Plugin instance if loaded, None otherwise
        """
        return self.plugins.get(name)

    def list_loaded_plugins(self) -> list[str]:
        """
        Get list of loaded plugin names.

        Returns:
            List of loaded plugin names
        """
        return list(self.plugins.keys())

    def get_plugin_status(self, name: str) -> PluginState | None:
        """
        Get status of a plugin.

        Args:
            name: Plugin name

        Returns:
            Plugin state if known, None otherwise
        """
        return self.plugin_states.get(name)

    async def handle_intent(
        self, intent: Intent, context: ExecutionContext
    ) -> QueryResult | None:
        """
        Let plugins handle an intent.

        Args:
            intent: Intent to handle
            context: Execution context

        Returns:
            QueryResult from first plugin that handles it
        """
        for plugin in self.plugins.values():
            if plugin.can_handle(intent):
                try:
                    result = await plugin.handle_intent(intent, context)
                    if result:
                        return result
                except Exception as e:
                    logger.error(f"Plugin error handling intent: {e}")

        return None

    def _register_plugin_hooks(self, plugin: Plugin) -> None:
        """Register all hooks from a plugin."""
        hooks = plugin.get_hooks()
        metadata = plugin.get_metadata()

        for hook_name, hook_funcs in hooks.items():
            for func in hook_funcs:
                priority = getattr(func, "_hook_priority", 50)
                self.hook_manager.register_hook(
                    hook_name, func, plugin_name=metadata.name, priority=priority
                )

    def _unregister_plugin_hooks(self, plugin: Plugin) -> None:
        """Unregister all hooks from a plugin."""
        metadata = plugin.get_metadata()
        self.hook_manager.unregister_plugin_hooks(metadata.name)

    async def execute_hook(self, hook_name: str, *args, **kwargs) -> list[Any]:
        """
        Execute all registered hooks for a hook point.

        Args:
            hook_name: Name of the hook point
            *args: Positional arguments for hooks
            **kwargs: Keyword arguments for hooks

        Returns:
            List of results from all hooks
        """
        return await self.hook_manager.execute_hook(hook_name, *args, **kwargs)

    def get_all_commands(self) -> dict[str, str]:
        """
        Get all commands provided by loaded plugins.

        Returns:
            Dictionary mapping command names to plugin names
        """
        commands = {}
        for plugin in self.plugins.values():
            metadata = plugin.get_metadata()
            for cmd in plugin.get_commands():
                commands[cmd] = metadata.name
        return commands

    def search_plugins(self, query: str) -> list[PluginMetadata]:
        """
        Search for plugins matching a query.

        Args:
            query: Search query

        Returns:
            List of matching plugin metadata
        """
        return self.discovery.search_plugins(query)
