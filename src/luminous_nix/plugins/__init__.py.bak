"""
Plugin System for Nix for Humanity.

Provides extensibility through a plugin architecture that allows
third-party developers to add custom functionality, commands,
and integrations without modifying core code.

Key Features:
    - Automatic plugin discovery from multiple sources
    - Hook-based architecture for intercepting operations
    - Sandboxed execution for security
    - Hot-reloading support for development
    - Plugin dependencies and version management
    - Configuration override capabilities

Plugin Sources:
    1. Built-in plugins (./builtin/)
    2. User plugins (~/.config/nix-humanity/plugins/)
    3. System plugins (/usr/share/nix-humanity/plugins/)
    4. Python packages (nix_humanity_plugin_*)

Usage Example:
    >>> from nix_for_humanity.plugins import PluginManager
    >>> manager = PluginManager()
    >>> manager.discover_plugins()
    >>> manager.load_plugin("my_plugin")

Since: v1.0.0
"""

from .base import Plugin, PluginHook, PluginMetadata
from .discovery import PluginDiscovery
from .hooks import Hook, HookPriority, hook
from .loader import PluginLoader
from .manager import PluginManager

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginHook",
    "PluginManager",
    "PluginDiscovery",
    "PluginLoader",
    "hook",
    "Hook",
    "HookPriority",
]
