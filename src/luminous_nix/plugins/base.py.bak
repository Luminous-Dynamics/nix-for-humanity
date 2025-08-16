"""
Base Plugin Classes and Interfaces.

Defines the foundation for all plugins in the Nix for Humanity ecosystem.

Since: v1.0.0
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    import semver

    SEMVER_AVAILABLE = True
except ImportError:
    SEMVER_AVAILABLE = False

    # Simple fallback for version comparison
    class semver:
        @staticmethod
        def VersionInfo(major=0, minor=0, patch=0):
            return f"{major}.{minor}.{patch}"


# Import from where they actually exist
try:
    from ..core.intents import Intent
except ImportError:
    from ..core.unified_backend import Intent

from ..constants import API_VERSION
from ..types import ExecutionContext, QueryResult


class PluginState(Enum):
    """Plugin lifecycle states."""

    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """
    Plugin metadata and configuration.

    Attributes:
        name: Unique plugin identifier
        version: Semantic version string
        author: Plugin author name
        description: What the plugin does
        homepage: Plugin documentation URL
        license: License identifier (e.g., MIT, GPL-3.0)
        requires: Minimum Nix for Humanity version
        dependencies: Other plugins required
        keywords: Searchable tags
        hooks: List of hooks this plugin provides
        commands: New commands added by plugin
        config_schema: JSON schema for plugin config

    Since: v1.0.0
    """

    name: str
    version: str
    author: str
    description: str
    homepage: str | None = None
    license: str = "MIT"
    requires: str = ">=1.0.0"
    dependencies: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] | None = None

    def is_compatible(self) -> bool:
        """Check if plugin is compatible with current version."""
        try:
            current = semver.VersionInfo.parse(API_VERSION.replace("v", ""))
            required = semver.VersionInfo.parse(
                self.requires.replace(">=", "").replace("v", "")
            )
            return current >= required
        except:
            return True  # Assume compatible if can't parse

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "homepage": self.homepage,
            "license": self.license,
            "requires": self.requires,
            "dependencies": self.dependencies,
            "keywords": self.keywords,
            "hooks": self.hooks,
            "commands": self.commands,
        }


class PluginHook:
    """
    Decorator for plugin hook methods.

    Usage:
        @PluginHook("pre_execute", priority=10)
        def before_command(self, query: str) -> str:
            return query.lower()

    Since: v1.0.0
    """

    def __init__(self, hook_name: str, priority: int = 50):
        """
        Initialize hook decorator.

        Args:
            hook_name: Name of the hook point
            priority: Execution priority (lower = earlier)
        """
        self.hook_name = hook_name
        self.priority = priority

    def __call__(self, func: Callable) -> Callable:
        """Apply decorator to function."""
        func._hook_name = self.hook_name
        func._hook_priority = self.priority
        return func


class Plugin(ABC):
    """
    Base class for all plugins.

    Subclass this to create a new plugin. Implement the required
    methods and use @PluginHook decorators to hook into the system.

    Example:
        class MyPlugin(Plugin):
            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="my_plugin",
                    version="1.0.0",
                    author="Me",
                    description="My awesome plugin"
                )

            @PluginHook("pre_execute")
            def preprocess(self, query: str) -> str:
                return query.replace("plz", "please")

    Since: v1.0.0
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize plugin with configuration.

        Args:
            config: Plugin-specific configuration
        """
        self.config = config or {}
        self.state = PluginState.DISCOVERED
        self._hooks: dict[str, list[Callable]] = {}
        self._discover_hooks()

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.

        Returns:
            PluginMetadata object describing the plugin
        """
        pass

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Called when plugin is loaded. Override to perform setup.

        Returns:
            True if initialization successful
        """
        return True

    def cleanup(self) -> None:
        """
        Cleanup plugin resources.

        Called when plugin is unloaded. Override to cleanup.
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate plugin configuration.

        Returns:
            True if configuration is valid
        """
        metadata = self.get_metadata()
        if not metadata.config_schema:
            return True

        # TODO: Implement JSON schema validation
        return True

    def can_handle(self, intent: Intent) -> bool:
        """
        Check if plugin can handle an intent.

        Args:
            intent: The intent to check

        Returns:
            True if plugin can handle this intent
        """
        return False

    async def handle_intent(
        self, intent: Intent, context: ExecutionContext
    ) -> QueryResult | None:
        """
        Handle an intent if capable.

        Args:
            intent: Intent to handle
            context: Execution context

        Returns:
            QueryResult if handled, None otherwise
        """
        return None

    def get_commands(self) -> list[str]:
        """
        Get list of commands provided by plugin.

        Returns:
            List of command names
        """
        return self.get_metadata().commands

    def _discover_hooks(self) -> None:
        """Discover hook methods in the plugin."""
        for name in dir(self):
            if name.startswith("_"):
                continue

            attr = getattr(self, name)
            if callable(attr) and hasattr(attr, "_hook_name"):
                hook_name = attr._hook_name
                if hook_name not in self._hooks:
                    self._hooks[hook_name] = []
                self._hooks[hook_name].append(attr)

    def get_hooks(self) -> dict[str, list[Callable]]:
        """Get all hooks provided by this plugin."""
        return self._hooks


class BuiltinPlugin(Plugin):
    """
    Base class for built-in plugins.

    Built-in plugins are shipped with Nix for Humanity and
    provide core functionality that can be disabled but not removed.

    Since: v1.0.0
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize builtin plugin."""
        super().__init__(config)
        self.builtin = True
