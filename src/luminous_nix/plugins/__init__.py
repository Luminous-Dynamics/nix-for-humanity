"""
Luminous Nix Plugin System

Provides extensibility for custom operations, security enhancements,
and system integrations while maintaining security guarantees.
"""

from .base import (
    Plugin,
    PluginMetadata,
    PluginConfig,
    PluginContext,
    PluginInfo,
    PluginStatus,
    LifecycleEvent
)

from .interfaces import (
    OperationPlugin,
    SecurityPlugin,
    HookPlugin,
    AIPlugin
)

from .manager import PluginManager
from .errors import (
    PluginError,
    PluginNotFoundError,
    PluginValidationError,
    PluginPermissionError,
    PluginLoadError
)

__all__ = [
    # Base classes
    'Plugin',
    'PluginMetadata',
    'PluginConfig',
    'PluginContext',
    'PluginInfo',
    'PluginStatus',
    'LifecycleEvent',

    # Plugin interfaces
    'OperationPlugin',
    'SecurityPlugin',
    'HookPlugin',
    'AIPlugin',

    # Manager
    'PluginManager',

    # Errors
    'PluginError',
    'PluginNotFoundError',
    'PluginValidationError',
    'PluginPermissionError',
    'PluginLoadError',
]

__version__ = '1.0.0'
