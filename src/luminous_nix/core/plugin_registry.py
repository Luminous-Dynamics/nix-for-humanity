"""
Plugin System Foundation - Extensibility through Clean Plugin Architecture

Provides infrastructure for plugin discovery, registration, lifecycle management,
dependency checking, and version validation.

Based on: Week 5 Plugin System Foundation
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib.util
import sys
import re
import logging

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Exception raised for plugin-related errors"""
    pass


# === Plugin Base Class ===

class Plugin(ABC):
    """
    Base class for all plugins.

    Plugins must implement name and version properties.
    Optionally can override lifecycle methods and metadata properties.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (must be unique)"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (semantic versioning: MAJOR.MINOR.PATCH)"""
        pass

    @property
    def dependencies(self) -> List[str]:
        """
        List of plugin dependencies.

        Format: ["plugin-name>=1.0.0", "other-plugin==2.0.0"]
        """
        return []

    @property
    def author(self) -> str:
        """Plugin author"""
        return "Unknown"

    @property
    def description(self) -> str:
        """Plugin description"""
        return ""

    @property
    def homepage(self) -> Optional[str]:
        """Plugin homepage URL"""
        return None

    # Lifecycle methods (can be overridden)

    def on_load(self) -> None:
        """Called when plugin is registered"""
        pass

    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        pass

    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unregistered"""
        pass


# === Version Utilities ===

def validate_version(version: str) -> bool:
    """
    Validate semantic version format (MAJOR.MINOR.PATCH).

    Args:
        version: Version string to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two semantic versions.

    Args:
        version1: First version
        version2: Second version

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    def parse_version(v: str) -> tuple:
        parts = v.split('.')
        return tuple(int(p) for p in parts)

    v1_parts = parse_version(version1)
    v2_parts = parse_version(version2)

    if v1_parts < v2_parts:
        return -1
    elif v1_parts > v2_parts:
        return 1
    else:
        return 0


def is_version_compatible(version: str, requirement: str) -> bool:
    """
    Check if version satisfies requirement.

    Args:
        version: Version to check
        requirement: Requirement string (e.g., ">=1.0.0", "==2.0.0")

    Returns:
        True if version satisfies requirement
    """
    # Parse requirement
    if requirement.startswith(">="):
        required_version = requirement[2:]
        return compare_versions(version, required_version) >= 0
    elif requirement.startswith("=="):
        required_version = requirement[2:]
        return compare_versions(version, required_version) == 0
    elif requirement.startswith("<="):
        required_version = requirement[2:]
        return compare_versions(version, required_version) <= 0
    elif requirement.startswith(">"):
        required_version = requirement[1:]
        return compare_versions(version, required_version) > 0
    elif requirement.startswith("<"):
        required_version = requirement[1:]
        return compare_versions(version, required_version) < 0
    else:
        # No operator, assume ==
        return compare_versions(version, requirement) == 0


# === Plugin Registry ===

class PluginRegistry:
    """
    Registry for managing plugins.

    Handles plugin registration, lifecycle management, dependency checking,
    and plugin discovery.
    """

    def __init__(self):
        """Initialize empty plugin registry"""
        self._plugins: Dict[str, Plugin] = {}
        self._enabled: Dict[str, bool] = {}

    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance to register

        Raises:
            PluginError: If plugin name already registered
        """
        if plugin.name in self._plugins:
            raise PluginError(
                f"Plugin '{plugin.name}' is already registered"
            )

        # Validate version
        if not validate_version(plugin.version):
            raise PluginError(
                f"Plugin '{plugin.name}' has invalid version: {plugin.version}"
            )

        # Register plugin
        self._plugins[plugin.name] = plugin
        self._enabled[plugin.name] = False

        # Call lifecycle method
        try:
            plugin.on_load()
        except Exception as e:
            # Remove from registry if on_load fails
            del self._plugins[plugin.name]
            del self._enabled[plugin.name]
            raise PluginError(
                f"Failed to load plugin '{plugin.name}': {e}"
            ) from e

        logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")

    def unregister(self, plugin_name: str) -> None:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister

        Raises:
            PluginError: If plugin not found or still enabled
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' not found")

        if self._enabled[plugin_name]:
            raise PluginError(
                f"Cannot unregister enabled plugin '{plugin_name}'. "
                "Disable it first."
            )

        plugin = self._plugins[plugin_name]

        # Call lifecycle method
        try:
            plugin.on_unload()
        except Exception as e:
            logger.error(
                f"Error in on_unload for plugin '{plugin_name}': {e}"
            )

        # Unregister
        del self._plugins[plugin_name]
        del self._enabled[plugin_name]

        logger.info(f"Unregistered plugin: {plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get plugin by name.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.

        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())

    def list_plugins_with_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        List all plugins with their metadata.

        Returns:
            Dictionary mapping plugin name to metadata dict
        """
        result = {}
        for name, plugin in self._plugins.items():
            result[name] = {
                'version': plugin.version,
                'author': plugin.author,
                'description': plugin.description,
                'homepage': plugin.homepage,
                'enabled': self._enabled[name],
                'dependencies': plugin.dependencies
            }
        return result

    def enable_plugin(self, plugin_name: str) -> None:
        """
        Enable a plugin.

        Args:
            plugin_name: Name of plugin to enable

        Raises:
            PluginError: If plugin not found or dependencies not satisfied
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' not found")

        if self._enabled[plugin_name]:
            # Already enabled
            return

        plugin = self._plugins[plugin_name]

        # Check dependencies
        for dep in plugin.dependencies:
            # Parse dependency (format: "name>=version" or "name")
            dep_name = re.match(r'^[a-zA-Z0-9\-_]+', dep).group(0)

            if dep_name not in self._plugins:
                raise PluginError(
                    f"Plugin '{plugin_name}' dependencies not satisfied: "
                    f"'{dep_name}' not found"
                )

            if not self._enabled[dep_name]:
                raise PluginError(
                    f"Plugin '{plugin_name}' dependencies not satisfied: "
                    f"'{dep_name}' is not enabled"
                )

            # Check version requirement if specified
            if ">=" in dep or "==" in dep or "<=" in dep or ">" in dep or "<" in dep:
                dep_version = self._plugins[dep_name].version

                # Extract requirement part
                for op in [">=", "==", "<=", ">", "<"]:
                    if op in dep:
                        requirement = dep[len(dep_name):]
                        if not is_version_compatible(dep_version, requirement):
                            raise PluginError(
                                f"Plugin '{plugin_name}' requires "
                                f"'{dep}' but found version {dep_version}"
                            )
                        break

        # Enable plugin
        try:
            plugin.on_enable()
        except Exception as e:
            raise PluginError(
                f"Failed to enable plugin '{plugin_name}': {e}"
            ) from e

        self._enabled[plugin_name] = True
        logger.info(f"Enabled plugin: {plugin_name}")

    def disable_plugin(self, plugin_name: str) -> None:
        """
        Disable a plugin.

        Args:
            plugin_name: Name of plugin to disable

        Raises:
            PluginError: If plugin not found or has enabled dependents
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' not found")

        if not self._enabled[plugin_name]:
            # Already disabled
            return

        # Check if other enabled plugins depend on this one
        dependents = []
        for name, plugin in self._plugins.items():
            if not self._enabled[name]:
                continue

            for dep in plugin.dependencies:
                dep_name = re.match(r'^[a-zA-Z0-9\-_]+', dep).group(0)
                if dep_name == plugin_name:
                    dependents.append(name)
                    break

        if dependents:
            raise PluginError(
                f"Cannot disable plugin '{plugin_name}': "
                f"still has enabled dependents: {', '.join(dependents)}"
            )

        # Disable plugin
        plugin = self._plugins[plugin_name]
        try:
            plugin.on_disable()
        except Exception as e:
            logger.error(
                f"Error in on_disable for plugin '{plugin_name}': {e}"
            )

        self._enabled[plugin_name] = False
        logger.info(f"Disabled plugin: {plugin_name}")

    def is_enabled(self, plugin_name: str) -> bool:
        """
        Check if plugin is enabled.

        Args:
            plugin_name: Name of plugin

        Returns:
            True if enabled, False otherwise
        """
        return self._enabled.get(plugin_name, False)

    def discover_plugins(self, plugins_dir: Path) -> List[Plugin]:
        """
        Discover plugins in directory.

        Scans directory for Python files that define Plugin subclasses
        and returns instances of discovered plugins.

        Args:
            plugins_dir: Directory to scan for plugins

        Returns:
            List of discovered Plugin instances
        """
        discovered = []

        if not plugins_dir.exists() or not plugins_dir.is_dir():
            logger.warning(f"Plugin directory not found: {plugins_dir}")
            return discovered

        # Scan for Python files
        for py_file in plugins_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue  # Skip private files

            try:
                # Load module dynamically
                module_name = f"plugin_{py_file.stem}"
                spec = importlib.util.spec_from_file_location(
                    module_name, py_file
                )
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Find Plugin subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Check if it's a Plugin subclass (but not Plugin itself)
                    if (isinstance(attr, type) and
                        issubclass(attr, Plugin) and
                        attr is not Plugin):

                        try:
                            # Instantiate and add to discovered
                            plugin_instance = attr()
                            discovered.append(plugin_instance)
                            logger.info(
                                f"Discovered plugin: {plugin_instance.name} "
                                f"v{plugin_instance.version}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to instantiate plugin "
                                f"'{attr_name}' from {py_file}: {e}"
                            )

            except Exception as e:
                logger.error(f"Failed to load plugin file {py_file}: {e}")

        return discovered


if __name__ == "__main__":
    # Example usage
    import tempfile

    # Create example plugin
    class ExamplePlugin(Plugin):
        @property
        def name(self) -> str:
            return "example-plugin"

        @property
        def version(self) -> str:
            return "1.0.0"

        @property
        def description(self) -> str:
            return "An example plugin"

        def on_enable(self) -> None:
            print(f"Plugin '{self.name}' enabled!")

    # Create registry and register plugin
    registry = PluginRegistry()
    plugin = ExamplePlugin()

    registry.register(plugin)
    print(f"Registered: {registry.list_plugins()}")

    registry.enable_plugin("example-plugin")
    print(f"Enabled: {registry.is_enabled('example-plugin')}")

    # Show metadata
    metadata = registry.list_plugins_with_metadata()
    print(f"Metadata: {metadata['example-plugin']}")
