"""
Plugin Loader for Nix for Humanity.

Handles the actual loading and instantiation of plugins from various sources.

Since: v1.0.0
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

from ..core.logging_config import get_logger
from ..security.sandbox import PluginSandbox
from .base import Plugin
from .discovery import PluginDiscovery

logger = get_logger(__name__)


class PluginLoader:
    """
    Loads and instantiates plugins safely.

    Handles different plugin sources (files, modules, packages)
    and provides sandboxing for security.

    Since: v1.0.0
    """

    def __init__(self):
        """Initialize plugin loader."""
        self.loaded_modules: dict[str, Any] = {}
        self.sandbox = PluginSandbox()

    def load_plugin(
        self,
        name: str,
        discovery: PluginDiscovery,
        config: dict[str, Any] | None = None,
    ) -> Plugin | None:
        """
        Load a plugin by name.

        Args:
            name: Plugin name
            discovery: Plugin discovery instance
            config: Plugin configuration

        Returns:
            Plugin instance if successful, None otherwise
        """
        # Check if already loaded as module
        if name in discovery.plugin_modules:
            return self._load_from_class(discovery.plugin_modules[name], config)

        # Check if we have a path
        if name in discovery.plugin_paths:
            return self._load_from_file(discovery.plugin_paths[name], config)

        # Try to load as package
        return self._load_from_package(name, config)

    def _load_from_file(
        self, plugin_path: Path, config: dict[str, Any] | None = None
    ) -> Plugin | None:
        """
        Load plugin from a Python file.

        Args:
            plugin_path: Path to plugin file
            config: Plugin configuration

        Returns:
            Plugin instance if successful
        """
        try:
            if not plugin_path.exists():
                logger.error(f"Plugin file not found: {plugin_path}")
                return None

            # Load module
            module_name = f"plugin_{plugin_path.stem}_{id(plugin_path)}"

            if module_name in self.loaded_modules:
                module = self.loaded_modules[module_name]
            else:
                spec = importlib.util.spec_from_file_location(module_name, plugin_path)

                if not spec or not spec.loader:
                    logger.error(f"Failed to create spec for {plugin_path}")
                    return None

                module = importlib.util.module_from_spec(spec)

                # Sandbox the module if enabled
                if self.sandbox.is_enabled():
                    module = self.sandbox.wrap_module(module)

                spec.loader.exec_module(module)
                self.loaded_modules[module_name] = module

            # Find Plugin subclass
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                logger.error(f"No Plugin class found in {plugin_path}")
                return None

            # Create instance
            return plugin_class(config)

        except Exception as e:
            logger.error(f"Error loading plugin from {plugin_path}: {e}")
            return None

    def _load_from_class(
        self, plugin_class: type[Plugin], config: dict[str, Any] | None = None
    ) -> Plugin | None:
        """
        Load plugin from a class.

        Args:
            plugin_class: Plugin class
            config: Plugin configuration

        Returns:
            Plugin instance if successful
        """
        try:
            return plugin_class(config)
        except Exception as e:
            logger.error(f"Error instantiating plugin class: {e}")
            return None

    def _load_from_package(
        self, package_name: str, config: dict[str, Any] | None = None
    ) -> Plugin | None:
        """
        Load plugin from an installed package.

        Args:
            package_name: Package name
            config: Plugin configuration

        Returns:
            Plugin instance if successful
        """
        try:
            # Try standard import
            module = importlib.import_module(package_name)

            # Find Plugin subclass
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                logger.error(f"No Plugin class found in package {package_name}")
                return None

            # Create instance
            return plugin_class(config)

        except ImportError as e:
            logger.error(f"Failed to import package {package_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading plugin from package {package_name}: {e}")
            return None

    def _find_plugin_class(self, module: Any) -> type[Plugin] | None:
        """
        Find Plugin subclass in a module.

        Args:
            module: Python module to search

        Returns:
            Plugin class if found
        """
        for name in dir(module):
            if name.startswith("_"):
                continue

            obj = getattr(module, name)

            # Check if it's a class and subclass of Plugin
            if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                return obj

        return None

    def reload_module(self, module_name: str) -> bool:
        """
        Reload a plugin module (for hot reloading).

        Args:
            module_name: Module name to reload

        Returns:
            True if successfully reloaded
        """
        try:
            if module_name in self.loaded_modules:
                module = self.loaded_modules[module_name]
                importlib.reload(module)
                logger.info(f"Reloaded module: {module_name}")
                return True

            logger.warning(f"Module not loaded: {module_name}")
            return False

        except Exception as e:
            logger.error(f"Error reloading module {module_name}: {e}")
            return False

    def unload_module(self, module_name: str) -> bool:
        """
        Unload a plugin module.

        Args:
            module_name: Module name to unload

        Returns:
            True if successfully unloaded
        """
        try:
            if module_name in self.loaded_modules:
                del self.loaded_modules[module_name]

                # Remove from sys.modules if present
                if module_name in sys.modules:
                    del sys.modules[module_name]

                logger.info(f"Unloaded module: {module_name}")
                return True

            return True

        except Exception as e:
            logger.error(f"Error unloading module {module_name}: {e}")
            return False
