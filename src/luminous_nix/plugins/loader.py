"""
Plugin loading system.

Loads plugin modules and instantiates plugin classes.
"""

import sys
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Optional, Type

from .base import Plugin, PluginConfig, PluginContext
from .discovery import PluginManifest
from .errors import PluginLoadError, PluginDependencyError


class PluginLoader:
    """
    Loads plugins from manifests.

    Handles module loading, class instantiation, and context injection.
    """

    def __init__(self, config: PluginConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._loaded_modules = {}

    @property
    def _module_cache(self):
        """Backwards compatibility alias for _loaded_modules"""
        return self._loaded_modules

    def load_plugin(
        self,
        manifest: PluginManifest,
        context: Optional[PluginContext] = None
    ) -> Plugin:
        """
        Load a plugin from its manifest.

        Args:
            manifest: Plugin manifest with entry point information
            context: Plugin context to inject

        Returns:
            Loaded and initialized plugin instance

        Raises:
            PluginLoadError: If plugin fails to load
        """
        plugin_name = manifest.name

        try:
            # 1. Load the module
            plugin_module = self._load_module(manifest)

            # 2. Get the plugin class
            plugin_class = self._get_plugin_class(plugin_module, manifest)

            # 3. Validate it's a Plugin subclass
            if not issubclass(plugin_class, Plugin):
                raise PluginLoadError(
                    f"Plugin class {manifest.entry_point_class} is not a Plugin subclass"
                )

            # 4. Instantiate the plugin
            plugin_instance = plugin_class()

            # 5. Inject context
            if context:
                plugin_instance.context = context

            # 6. Validate context if needed
            if not plugin_instance.validate_context():
                self.logger.warning(
                    f"Plugin {plugin_name} context validation failed"
                )

            self.logger.info(f"Loaded plugin: {plugin_name} v{manifest.version}")
            return plugin_instance

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise PluginLoadError(f"Failed to load plugin {plugin_name}: {e}")

    def _load_module(self, manifest: PluginManifest):
        """
        Load the plugin module.

        Args:
            manifest: Plugin manifest

        Returns:
            Loaded Python module

        Raises:
            PluginLoadError: If module fails to load
        """
        plugin_name = manifest.name
        module_name = manifest.entry_point_module

        # Check if already loaded
        cache_key = f"{plugin_name}:{module_name}"
        if cache_key in self._loaded_modules:
            return self._loaded_modules[cache_key]

        # Construct module file path
        module_file = manifest.plugin_dir / f"{module_name}.py"

        if not module_file.exists():
            raise PluginLoadError(
                f"Module file not found: {module_file}"
            )

        # Add plugin directory to sys.path for dependency imports
        plugin_dir_str = str(manifest.plugin_dir)
        added_to_path = False
        if plugin_dir_str not in sys.path:
            sys.path.insert(0, plugin_dir_str)
            added_to_path = True

        try:
            # Load module directly from file (avoids sys.modules contamination)
            # Use unique module name to prevent conflicts
            unique_module_name = f"{plugin_name}.{module_name}"

            spec = importlib.util.spec_from_file_location(
                unique_module_name,
                module_file
            )

            if spec is None or spec.loader is None:
                raise PluginLoadError(
                    f"Failed to create module spec for {module_file}"
                )

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self._loaded_modules[cache_key] = module
            return module

        except Exception as e:
            if isinstance(e, PluginLoadError):
                raise
            raise PluginLoadError(
                f"Failed to load module {module_name}: {e}"
            )
        finally:
            # Remove from sys.path to avoid pollution
            if added_to_path and plugin_dir_str in sys.path:
                sys.path.remove(plugin_dir_str)

    def _get_plugin_class(self, module, manifest: PluginManifest) -> Type[Plugin]:
        """
        Get the plugin class from the module.

        Args:
            module: Loaded Python module
            manifest: Plugin manifest

        Returns:
            Plugin class

        Raises:
            PluginLoadError: If class not found
        """
        class_name = manifest.entry_point_class

        if not hasattr(module, class_name):
            raise PluginLoadError(
                f"Module {manifest.entry_point_module} does not have class {class_name}"
            )

        return getattr(module, class_name)

    def unload_plugin(self, plugin):
        """
        Unload a plugin.

        Args:
            plugin: Plugin instance or plugin name string
        """
        # Get plugin name
        if isinstance(plugin, str):
            plugin_name = plugin
        else:
            # Call cleanup if it's a Plugin object
            try:
                plugin.cleanup()
            except Exception as e:
                self.logger.error(f"Error during plugin cleanup: {e}")
            plugin_name = plugin.metadata.name

        # Remove from cache
        keys_to_remove = [
            k for k in self._loaded_modules.keys()
            if k.startswith(f"{plugin_name}:")
        ]
        for key in keys_to_remove:
            del self._loaded_modules[key]

    def clear_cache(self):
        """Clear the module cache"""
        self._loaded_modules.clear()


# Export
__all__ = ['PluginLoader']
