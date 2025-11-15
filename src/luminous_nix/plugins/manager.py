"""
Plugin Manager - Manages plugin lifecycle and registration

This is the heart of our extensibility - allowing the community
to extend Luminous Nix without touching core code.
"""

import importlib.util
import logging
from pathlib import Path
from typing import Any, Optional

from .base import Plugin, PluginInfo

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugins for Luminous Nix.

    Features:
    - Dynamic plugin loading
    - Dependency management
    - Hook system
    - Plugin isolation
    """

    def __init__(self, plugin_dir: Optional[Path] = None):
        """
        Initialize plugin manager.

        Args:
            plugin_dir: Directory containing plugins
        """
        self.plugin_dir = (
            plugin_dir or Path.home() / ".config" / "luminous-nix" / "plugins"
        )
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.plugins: dict[str, Plugin] = {}
        self.commands: dict[str, callable] = {}
        self.hooks: dict[str, list[callable]] = {
            "pre_search": [],
            "post_search": [],
            "pre_install": [],
            "post_install": [],
            "pre_remove": [],
            "post_remove": [],
        }

        # Plugin context with services
        self.context = {}

    def set_context(self, context: dict[str, Any]):
        """
        Set plugin context with services.

        Args:
            context: Dictionary with services like SearchService, CacheService, etc.
        """
        self.context = context

    def load_plugin(self, plugin_path: Path) -> bool:
        """
        Load a plugin from file.

        Args:
            plugin_path: Path to plugin file

        Returns:
            True if loaded successfully
        """
        try:
            # Load plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_path.stem}", plugin_path
            )

            if not spec or not spec.loader:
                logger.error(f"Failed to load plugin spec: {plugin_path}")
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Plugin class
            plugin_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                    plugin_class = obj
                    break

            if not plugin_class:
                logger.error(f"No Plugin class found in {plugin_path}")
                return False

            # 2-5 secondsiate plugin
            plugin = plugin_class()

            # Initialize plugin
            if not plugin.initialize(self.context):
                logger.error(f"Plugin initialization failed: {plugin_path}")
                return False

            # Register plugin
            info = plugin.get_info()
            self.plugins[info.name] = plugin

            # Register commands
            for cmd_name, handler in plugin.get_commands().items():
                self.register_command(info.name, cmd_name, handler)

            logger.info(f"Loaded plugin: {info.name} v{info.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return False

    def load_all_plugins(self):
        """Load all plugins from plugin directory"""

        # Load built-in plugins first
        self._load_builtin_plugins()

        # Load user plugins
        for plugin_file in self.plugin_dir.glob("*.py"):
            if not plugin_file.name.startswith("_"):
                self.load_plugin(plugin_file)

    def _load_builtin_plugins(self):
        """Load built-in plugins"""

        builtin_dir = Path(__file__).parent / "builtin"
        if builtin_dir.exists():
            for plugin_file in builtin_dir.glob("*.py"):
                if not plugin_file.name.startswith("_"):
                    self.load_plugin(plugin_file)

    def register_command(self, plugin_name: str, command: str, handler: callable):
        """
        Register a plugin command.

        Args:
            plugin_name: Name of plugin
            command: Command name
            handler: Command handler
        """
        full_command = f"{plugin_name}:{command}"
        self.commands[full_command] = handler

        # Also register without prefix if no conflict
        if command not in self.commands:
            self.commands[command] = handler

    def execute_command(self, command: str, *args, **kwargs) -> Any:
        """
        Execute a plugin command.

        Args:
            command: Command name
            *args: Command arguments
            **kwargs: Command keyword arguments

        Returns:
            Command result
        """
        if command in self.commands:
            handler = self.commands[command]
            if isinstance(handler, dict):
                handler = handler["handler"]
            return handler(*args, **kwargs)

        # Try with plugin prefix
        for cmd_name, handler in self.commands.items():
            if cmd_name.endswith(f":{command}"):
                if isinstance(handler, dict):
                    handler = handler["handler"]
                return handler(*args, **kwargs)

        raise ValueError(f"Unknown command: {command}")

    def enhance_search(self, query: str, results: list) -> list:
        """
        Let plugins enhance search results.

        Args:
            query: Search query
            results: Current results

        Returns:
            Enhanced results
        """
        # Run pre-search hooks
        for hook in self.hooks["pre_search"]:
            hook(query)

        # Let each plugin enhance results
        for plugin in self.plugins.values():
            results = plugin.enhance_search(query, results)

        # Run post-search hooks
        for hook in self.hooks["post_search"]:
            hook(query, results)

        return results

    def get_config_templates(self) -> dict[str, Any]:
        """
        Get all configuration templates from plugins.

        Returns:
            Dictionary of templates
        """
        templates = {}

        for plugin_name, plugin in self.plugins.items():
            plugin_templates = plugin.get_config_templates()
            for template_name, template in plugin_templates.items():
                full_name = f"{plugin_name}:{template_name}"
                templates[full_name] = template

        return templates

    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """
        Trigger a hook.

        Args:
            hook_name: Name of hook
            *args: Hook arguments
            **kwargs: Hook keyword arguments
        """
        if hook_name in self.hooks:
            for handler in self.hooks[hook_name]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Hook {hook_name} failed: {e}")

    def register_hook(self, hook_name: str, handler: callable):
        """
        Register a hook handler.

        Args:
            hook_name: Name of hook
            handler: Hook handler
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(handler)

    def list_plugins(self) -> list[PluginInfo]:
        """
        List all loaded plugins.

        Returns:
            List of plugin information
        """
        return [plugin.get_info() for plugin in self.plugins.values()]

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a specific plugin.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(name)

    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin.

        Args:
            name: Plugin name

        Returns:
            True if unloaded successfully
        """
        if name not in self.plugins:
            return False

        plugin = self.plugins[name]

        # Call shutdown
        plugin.shutdown()

        # Remove commands
        commands_to_remove = []
        for cmd_name in self.commands:
            if cmd_name.startswith(f"{name}:"):
                commands_to_remove.append(cmd_name)

        for cmd in commands_to_remove:
            del self.commands[cmd]

        # Remove plugin
        del self.plugins[name]

        logger.info(f"Unloaded plugin: {name}")
        return True

    def reload_plugin(self, name: str) -> bool:
        """
        Reload a plugin.

        Args:
            name: Plugin name

        Returns:
            True if reloaded successfully
        """
        # Find plugin file
        plugin_file = self.plugin_dir / f"{name}.py"
        if not plugin_file.exists():
            # Try builtin
            plugin_file = Path(__file__).parent / "builtin" / f"{name}.py"

        if not plugin_file.exists():
            return False

        # Unload if loaded
        if name in self.plugins:
            self.unload_plugin(name)

        # Load again
        return self.load_plugin(plugin_file)
