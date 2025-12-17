"""
Plugin lifecycle management.

Manages plugin state transitions and lifecycle events.
"""

import logging
from typing import Dict, List, Optional

from .base import Plugin, PluginStatus, PluginConfig, LifecycleEvent
from .discovery import PluginManifest
from .loader import PluginLoader
from .errors import PluginLoadError


class PluginLifecycleManager:
    """
    Manages plugin lifecycle.

    Handles state transitions, activation/deactivation, and cleanup.
    """

    def __init__(self, config: PluginConfig):
        self.config = config
        self.loader = PluginLoader(config)
        self.logger = logging.getLogger(__name__)

        # Plugin state tracking
        self._plugins: Dict[str, Plugin] = {}
        self._states: Dict[str, PluginStatus] = {}

        # Lifecycle event callbacks
        self._event_callbacks: Dict[LifecycleEvent, List[callable]] = {}

    def load_plugin(self, manifest: PluginManifest, context=None) -> Plugin:
        """
        Load a plugin through its lifecycle.

        States: DISCOVERED → VALIDATED → LOADED → INITIALIZED → ACTIVE

        Args:
            manifest: Plugin manifest
            context: Plugin context

        Returns:
            Loaded and activated plugin

        Raises:
            PluginLoadError: If any lifecycle stage fails
        """
        plugin_name = manifest.name

        try:
            # State: DISCOVERED
            self._set_state(plugin_name, PluginStatus.DISCOVERED)
            self._emit_event(LifecycleEvent.DISCOVERED, manifest)

            # State: VALIDATED (validation happens in PluginManager)
            self._set_state(plugin_name, PluginStatus.VALIDATED)
            self._emit_event(LifecycleEvent.VALIDATED, manifest)

            # State: LOADED
            plugin = self.loader.load_plugin(manifest, context)
            self._plugins[plugin_name] = plugin
            plugin.status = PluginStatus.LOADED
            self._set_state(plugin_name, PluginStatus.LOADED)
            self._emit_event(LifecycleEvent.LOADED, plugin)

            # State: INITIALIZED
            plugin.status = PluginStatus.INITIALIZED
            self._set_state(plugin_name, PluginStatus.INITIALIZED)
            self._emit_event(LifecycleEvent.INITIALIZED, plugin)

            # State: ACTIVE
            plugin.activate()
            plugin.status = PluginStatus.ACTIVE
            self._set_state(plugin_name, PluginStatus.ACTIVE)
            self._emit_event(LifecycleEvent.ACTIVATED, plugin)

            self.logger.info(f"Plugin {plugin_name} activated successfully")
            return plugin

        except Exception as e:
            self.logger.error(f"Plugin {plugin_name} lifecycle failed: {e}")
            self._set_state(plugin_name, PluginStatus.FAILED)
            self._emit_event(LifecycleEvent.FAILED, plugin_name, error=e)
            raise PluginLoadError(f"Failed to load {plugin_name}: {e}")

    def unload_plugin(self, plugin_name: str):
        """
        Unload a plugin.

        States: ACTIVE → DISABLED → UNLOADED

        Args:
            plugin_name: Name of plugin to unload
        """
        if plugin_name not in self._plugins:
            self.logger.warning(f"Plugin {plugin_name} not loaded")
            return

        plugin = self._plugins[plugin_name]

        try:
            # Deactivate
            if plugin.status == PluginStatus.ACTIVE:
                plugin.deactivate()
                plugin.status = PluginStatus.DISABLED
                self._set_state(plugin_name, PluginStatus.DISABLED)
                self._emit_event(LifecycleEvent.DEACTIVATED, plugin)

            # Cleanup if available
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()

            # Unload
            self.loader.unload_plugin(plugin)
            del self._plugins[plugin_name]
            del self._states[plugin_name]
            self._emit_event(LifecycleEvent.UNLOADED, plugin_name)

            self.logger.info(f"Plugin {plugin_name} unloaded successfully")

        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
            plugin.status = PluginStatus.ERROR
            self._set_state(plugin_name, PluginStatus.ERROR)
            self._emit_event(LifecycleEvent.FAILED, plugin, error=e)

    def activate_plugin(self, plugin_name: str):
        """
        Activate a disabled plugin.

        Args:
            plugin_name: Name of plugin to activate
        """
        if plugin_name not in self._plugins:
            raise PluginLoadError(f"Plugin {plugin_name} not loaded")

        plugin = self._plugins[plugin_name]

        if plugin.status == PluginStatus.ACTIVE:
            self.logger.debug(f"Plugin {plugin_name} already active")
            return

        try:
            plugin.activate()
            plugin.status = PluginStatus.ACTIVE
            self._set_state(plugin_name, PluginStatus.ACTIVE)
            self._emit_event(LifecycleEvent.ACTIVATED, plugin)

            self.logger.info(f"Plugin {plugin_name} activated")

        except Exception as e:
            self.logger.error(f"Failed to activate {plugin_name}: {e}")
            plugin.status = PluginStatus.ERROR
            self._set_state(plugin_name, PluginStatus.ERROR)
            self._emit_event(LifecycleEvent.FAILED, plugin, error=e)
            raise

    def deactivate_plugin(self, plugin_name: str):
        """
        Deactivate an active plugin.

        Args:
            plugin_name: Name of plugin to deactivate
        """
        if plugin_name not in self._plugins:
            raise PluginLoadError(f"Plugin {plugin_name} not loaded")

        plugin = self._plugins[plugin_name]

        if plugin.status != PluginStatus.ACTIVE:
            self.logger.debug(f"Plugin {plugin_name} not active")
            return

        try:
            plugin.deactivate()
            plugin.status = PluginStatus.DISABLED
            self._set_state(plugin_name, PluginStatus.DISABLED)
            self._emit_event(LifecycleEvent.DEACTIVATED, plugin)

            self.logger.info(f"Plugin {plugin_name} deactivated")

        except Exception as e:
            self.logger.error(f"Failed to deactivate {plugin_name}: {e}")
            plugin.status = PluginStatus.ERROR
            self._set_state(plugin_name, PluginStatus.ERROR)
            self._emit_event(LifecycleEvent.FAILED, plugin, error=e)
            raise

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name"""
        return self._plugins.get(plugin_name)

    def get_state(self, plugin_name: str) -> Optional[PluginStatus]:
        """Get the state of a plugin"""
        return self._states.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """List all loaded plugin names"""
        return list(self._plugins.keys())

    def _set_state(self, plugin_name: str, state: PluginStatus):
        """Set plugin state"""
        self._states[plugin_name] = state
        self.logger.debug(f"Plugin {plugin_name} state: {state.value}")

    def register_event_callback(self, event: LifecycleEvent, callback: callable):
        """
        Register a callback for lifecycle events.

        Args:
            event: Event to listen for
            callback: Function to call when event occurs
        """
        if event not in self._event_callbacks:
            self._event_callbacks[event] = []
        self._event_callbacks[event].append(callback)

    def unregister_event_callback(self, event: LifecycleEvent, callback: callable):
        """
        Unregister a callback for lifecycle events.

        Args:
            event: Event to stop listening for
            callback: Function to remove from callbacks
        """
        if event in self._event_callbacks and callback in self._event_callbacks[event]:
            self._event_callbacks[event].remove(callback)

    def on_event(self, event: LifecycleEvent, callback: callable):
        """
        Register a callback for lifecycle events (alias for register_event_callback).

        Args:
            event: Event to listen for
            callback: Function to call when event occurs
        """
        self.register_event_callback(event, callback)

    def _emit_event(self, event: LifecycleEvent, *args, **kwargs):
        """Emit a lifecycle event"""
        if event not in self._event_callbacks:
            return  # No callbacks registered for this event

        for callback in self._event_callbacks[event]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Event callback error: {e}")

    def shutdown(self):
        """Shutdown all plugins"""
        plugin_names = list(self._plugins.keys())
        for plugin_name in plugin_names:
            try:
                self.unload_plugin(plugin_name)
            except Exception as e:
                self.logger.error(f"Error shutting down {plugin_name}: {e}")


# Export
__all__ = ['PluginLifecycleManager', 'LifecycleEvent']
