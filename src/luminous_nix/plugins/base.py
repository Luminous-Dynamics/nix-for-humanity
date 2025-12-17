"""
Base plugin classes and types.

Defines core plugin infrastructure used by all plugin types.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from abc import ABC, abstractmethod
import logging


class PluginStatus(Enum):
    """Plugin lifecycle status"""
    DISCOVERED = "discovered"      # Found but not loaded
    VALIDATED = "validated"        # Security validation passed
    LOADED = "loaded"              # Code loaded into memory
    INITIALIZED = "initialized"    # __init__ called
    ACTIVE = "active"              # Available for use
    DISABLED = "disabled"          # Disabled by user
    FAILED = "failed"              # Failed to load/initialize
    ERROR = "error"                # Runtime error occurred


class LifecycleEvent(Enum):
    """Plugin lifecycle events for callbacks"""
    DISCOVERED = "discovered"      # Plugin discovered
    VALIDATED = "validated"        # Validation completed
    LOADED = "loaded"              # Plugin loaded
    INITIALIZED = "initialized"    # Plugin initialized
    ACTIVATED = "activated"        # Plugin activated
    DEACTIVATED = "deactivated"    # Plugin deactivated
    FAILED = "failed"              # Plugin failed
    UNLOADED = "unloaded"          # Plugin unloaded


@dataclass
class PluginMetadata:
    """Plugin metadata from manifest"""
    name: str
    version: str
    author: str
    description: str

    # Optional fields
    email: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None

    # Plugin capabilities
    operation_types: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    requires_permissions: List[str] = field(default_factory=list)

    # Dependencies
    requires_plugins: List[str] = field(default_factory=list)
    recommends_plugins: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)

    # Requirements
    min_luminous_version: Optional[str] = None
    min_python_version: Optional[str] = None
    api_version: str = "1.0"


@dataclass
class PluginConfig:
    """Plugin system configuration"""
    # Plugin discovery paths
    plugin_paths: List[Path] = field(default_factory=lambda: [
        Path("/usr/share/luminous-nix/plugins"),     # System plugins
        Path.home() / ".local/share/luminous-nix/plugins",  # User plugins
        Path(".luminous-nix/plugins"),                # Project plugins
        Path("examples/plugins")                      # Example plugins (for development)
    ])

    # Security settings
    require_signatures: bool = False
    trusted_signers: Set[str] = field(default_factory=set)
    allow_unsigned_plugins: bool = True

    # Performance settings
    lazy_loading: bool = True
    parallel_loading: bool = True
    max_load_time_ms: int = 100

    # Sandboxing settings
    enable_sandboxing: bool = True
    enforce_permissions: bool = True

    # Logging
    log_level: str = "INFO"


@dataclass
class PluginContext:
    """Context provided to plugins for accessing core systems"""
    # Core systems (injected by PluginManager)
    state_manager: Optional[Any] = None
    security: Optional[Any] = None
    ai: Optional[Any] = None
    executor: Optional[Any] = None

    # Plugin-specific
    plugin_name: str = ""
    plugin_dir: Optional[Path] = None
    permissions: Set[str] = field(default_factory=set)

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)

    def has_permission(self, permission: str) -> bool:
        """Check if plugin has a specific permission"""
        return permission in self.permissions


@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    name: str
    version: str
    type: str
    status: PluginStatus
    description: str = ""
    author: str = ""
    enabled: bool = True


class Plugin(ABC):
    """
    Base class for all plugins.

    All plugin types (Operation, Security, Hook, AI) inherit from this base.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"luminous_nix.plugins.{self.__class__.__name__}")
        self._status = PluginStatus.INITIALIZED
        self._context: Optional[PluginContext] = None
        self._enabled = True

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Plugin metadata - must be implemented by subclasses"""
        pass

    @property
    def type(self) -> str:
        """Plugin type - determined by class hierarchy"""
        # Will be overridden by specific plugin types
        return "unknown"

    @property
    def status(self) -> PluginStatus:
        """Current plugin status"""
        return self._status

    @status.setter
    def status(self, value: PluginStatus):
        """Set plugin status"""
        self._status = value
        self.logger.debug(f"Plugin {self.metadata.name} status: {value.value}")

    @property
    def context(self) -> Optional[PluginContext]:
        """Plugin execution context"""
        return self._context

    @context.setter
    def context(self, value: PluginContext):
        """Set plugin context (called by PluginManager)"""
        self._context = value

    @property
    def enabled(self) -> bool:
        """Whether plugin is enabled"""
        return self._enabled

    def activate(self):
        """
        Called when plugin is activated.

        Override to perform activation tasks (e.g., connect to services,
        initialize resources).
        """
        self.status = PluginStatus.ACTIVE
        self.logger.info(f"Plugin {self.metadata.name} activated")

    def deactivate(self):
        """
        Called when plugin is deactivated.

        Override to perform cleanup tasks (e.g., disconnect from services,
        release resources).
        """
        self.status = PluginStatus.DISABLED
        self.logger.info(f"Plugin {self.metadata.name} deactivated")

    def cleanup(self):
        """
        Called when plugin is being unloaded.

        Override to perform final cleanup.
        """
        self.logger.info(f"Plugin {self.metadata.name} cleanup")

    def validate_context(self) -> bool:
        """
        Validate that plugin context has required systems.

        Override to add custom validation.
        """
        return self._context is not None

    def check_permission(self, permission: str) -> bool:
        """Check if plugin has a specific permission"""
        if not self._context:
            return False
        return self._context.has_permission(permission)

    def require_permission(self, permission: str):
        """Require a specific permission or raise error"""
        if not self.check_permission(permission):
            from .errors import PluginPermissionError
            raise PluginPermissionError(
                f"Plugin {self.metadata.name} requires permission: {permission}"
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.metadata.name} v{self.metadata.version}>"


class PluginHook:
    """Base class for hook implementations"""

    def __init__(self, name: str):
        self.name = name
        self.callbacks: List[callable] = []

    def register(self, callback: callable):
        """Register a callback for this hook"""
        self.callbacks.append(callback)

    def unregister(self, callback: callable):
        """Unregister a callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def trigger(self, *args, **kwargs):
        """Trigger all callbacks for this hook"""
        for callback in self.callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logging.error(f"Hook {self.name} callback error: {e}")
