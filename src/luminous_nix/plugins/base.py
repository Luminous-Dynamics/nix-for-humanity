"""
Plugin Base - Clean plugin architecture for extensibility

This enables the community to extend Luminous Nix without
modifying core code. Beautiful architecture in action!
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Plugin metadata"""

    name: str
    version: str
    description: str
    author: str
    capabilities: list[str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "capabilities": self.capabilities,
        }


class Plugin(ABC):
    """
    Base class for all Luminous Nix plugins.

    Plugins can:
    - Add new commands
    - Enhance search
    - Provide new config templates
    - Add UI elements
    - Integrate external services
    """

    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        pass

    @abstractmethod
    def initialize(self, context: dict[str, Any]) -> bool:
        """
        Initialize the plugin.

        Args:
            context: Plugin context with services

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def get_commands(self) -> dict[str, callable]:
        """
        Get commands provided by this plugin.

        Returns:
            Dictionary mapping command names to handlers
        """
        pass

    def enhance_search(self, query: str, results: list) -> list:
        """
        Enhance search results.

        Args:
            query: Search query
            results: Current results

        Returns:
            Enhanced results
        """
        return results

    def get_config_templates(self) -> dict[str, str]:
        """
        Get configuration templates.

        Returns:
            Dictionary mapping template names to configs
        """
        return {}

    def on_install(self, package: str) -> None:
        """
        Hook called after package installation.

        Args:
            package: Installed package name
        """
        pass

    def on_remove(self, package: str) -> None:
        """
        Hook called after package removal.

        Args:
            package: Removed package name
        """
        pass

    def shutdown(self) -> None:
        """Cleanup when plugin is unloaded"""
        pass


class CommandPlugin(Plugin):
    """
    Base class for plugins that add commands.

    Simplifies creating command-based plugins.
    """

    def __init__(self):
        self.commands = {}
        self._register_commands()

    @abstractmethod
    def _register_commands(self):
        """Register plugin commands"""
        pass

    def get_commands(self) -> dict[str, callable]:
        """Get registered commands"""
        return self.commands

    def register_command(self, name: str, handler: callable, description: str = ""):
        """
        Register a command.

        Args:
            name: Command name
            handler: Command handler function
            description: Command description
        """
        self.commands[name] = {"handler": handler, "description": description}


class SearchPlugin(Plugin):
    """
    Base class for plugins that enhance search.

    Simplifies creating search enhancement plugins.
    """

    @abstractmethod
    def search(self, query: str) -> list:
        """
        Perform custom search.

        Args:
            query: Search query

        Returns:
            Search results
        """
        pass

    def enhance_search(self, query: str, results: list) -> list:
        """
        Enhance existing search results.

        Args:
            query: Search query
            results: Current results

        Returns:
            Enhanced results
        """
        # Add custom search results
        custom_results = self.search(query)

        # Merge with existing results
        if custom_results:
            # Add custom results but avoid duplicates
            seen = {r.get("name") for r in results if isinstance(r, dict)}
            for result in custom_results:
                if isinstance(result, dict) and result.get("name") not in seen:
                    results.append(result)

        return results


class ConfigPlugin(Plugin):
    """
    Base class for plugins that provide configurations.

    Simplifies creating config template plugins.
    """

    def __init__(self):
        self.templates = {}
        self._register_templates()

    @abstractmethod
    def _register_templates(self):
        """Register configuration templates"""
        pass

    def get_config_templates(self) -> dict[str, str]:
        """Get registered templates"""
        return self.templates

    def register_template(self, name: str, config: str, description: str = ""):
        """
        Register a configuration template.

        Args:
            name: Template name
            config: NixOS configuration
            description: Template description
        """
        self.templates[name] = {"config": config, "description": description}
