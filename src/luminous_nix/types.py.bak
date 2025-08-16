"""
Type Definitions for Nix for Humanity.

Central type definitions used throughout the Nix for Humanity codebase.
Provides TypedDict definitions, Protocols, type aliases, and type variables
for consistent type safety across all modules.

Key Features:
    - TypedDict definitions for structured data
    - Protocol definitions for interfaces
    - Type aliases for clarity
    - Generic type variables for flexibility

Usage Example:
    >>> from nix_for_humanity.types import QueryResult, Intent
    >>> result: QueryResult = {
    ...     "success": True,
    ...     "message": "Package installed",
    ...     "data": {"package": "firefox"}
    ... }

Dependencies:
    - Required: typing (standard library)
    - Optional: typing_extensions (for older Python versions)

Note:
    This module uses runtime_checkable protocols and TypedDict
    for maximum compatibility and runtime validation support.

Since: v1.0.0
"""

from collections.abc import Awaitable, Callable
from typing import Any, Optional, TypeVar, Union

try:
    from typing import Literal, Protocol, TypedDict  # Python 3.8+
except ImportError:
    # Fallback for older Python versions

    Protocol = object  # Simple fallback
    Literal = Union  # Simple fallback

# For optional fields in TypedDict (Python 3.11+)
try:
    from typing import NotRequired
except ImportError:
    NotRequired = Optional  # Fallback
from dataclasses import dataclass

# Import core types that are referenced elsewhere
from nix_for_humanity.core.intents import Intent, IntentType

# Type variables
T = TypeVar("T")
ResultType = TypeVar("ResultType")


# Literal types for specific strings
IntentLiteral = Literal[
    "install",
    "remove",
    "search",
    "update",
    "rollback",
    "generate_config",
    "translate_error",
    "query",
    "learn",
    "unknown",
]

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


# TypedDicts for structured data
class PackageInfo(dict):
    """
    Information about a Nix package.

    Represents metadata and details about a package in the Nix store.
    Used for package search results and information queries.

    Attributes:
        name (str): Package name (e.g., 'firefox', 'python311')
        version (str, optional): Package version string
        description (str, optional): Human-readable description
        homepage (str, optional): Project homepage URL
        license (str, optional): License identifier

    Example:
        >>> info: PackageInfo = {
        ...     "name": "firefox",
        ...     "version": "120.0",
        ...     "description": "Web browser"
        ... }

    Since: v1.0.0
    """

    name: str
    version: NotRequired[str]
    description: NotRequired[str]
    homepage: NotRequired[str]
    license: NotRequired[str]


class CommandResult(dict):
    """
    Result from command execution.

    Contains output and status from executing a Nix command.

    Since: v1.0.0
    """

    success: bool
    output: str
    error: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]
    execution_time: NotRequired[float]


class CacheEntry(dict):
    """
    Cache entry structure.

    Stores cached query results with metadata.

    Since: v1.0.0
    """

    query: str
    result: Any
    timestamp: float
    context: NotRequired[dict[str, Any]]


class ConfigDict(dict):
    """
    Configuration dictionary.

    User preferences and runtime settings.

    Since: v1.0.0
    """

    dry_run: NotRequired[bool]
    debug: NotRequired[bool]
    caching: NotRequired[bool]
    learning: NotRequired[bool]
    timeout: NotRequired[int]
    log_level: NotRequired[LogLevel]


# Common result types
@dataclass
class QueryResult:
    """
    Result from a query execution.

    Since: v1.0.0
    """

    success: bool
    output: str | None = None
    error: str | None = None
    suggestions: list[str] | None = None
    data: dict[str, Any] | None = None


# Protocols for duck typing
@dataclass
class ExecutionContext:
    """
    Context for command execution.

    Maintains state and settings for command execution.

    Since: v1.0.0
    """

    user_id: str | None = None
    session_id: str | None = None
    dry_run: bool = False
    timeout: int = 30
    environment: dict[str, str] = None

    def __post_init__(self):
        if self.environment is None:
            self.environment = {}


class CommandExecutorProtocol(Protocol):
    """
    Protocol for command executors.

    Interface for command execution implementations.

    Since: v1.0.0
    """

    def execute(self, intent: str, **kwargs: Any) -> "ExecutionResult":
        """Execute a command"""
        ...


class CacheProtocol(Protocol):
    """
    Protocol for cache implementations.

    Interface for caching backends.

    Since: v1.0.0
    """

    def get(self, key: str, context: dict[str, Any] | None = None) -> Any | None:
        """Get cached value"""
        ...

    def set(self, key: str, value: Any, context: dict[str, Any] | None = None) -> None:
        """Set cached value"""
        ...

    def clear(self) -> None:
        """Clear cache"""
        ...


class PluginProtocol(Protocol):
    """Protocol for plugins"""

    @property
    def name(self) -> str:
        """Plugin name"""
        ...

    def can_handle(self, intent: "Intent") -> bool:
        """Check if plugin can handle intent"""
        ...

    async def process(self, intent: "Intent", context: "Context") -> Optional["Result"]:
        """Process intent"""
        ...


# Callback types
ProgressCallback = Callable[[float, str], None]
ErrorCallback = Callable[[Exception], None]
HookCallback = Union[Callable[[Any], Any], Callable[[Any], Awaitable[Any]]]


# Response types
class SuccessResponse(dict):
    """Successful response structure"""

    success: Literal[True]
    output: str
    metadata: NotRequired[dict[str, Any]]
    cached: NotRequired[bool]


class ErrorResponse(dict):
    """Error response structure"""

    success: Literal[False]
    error: str
    suggestions: NotRequired[list[str]]
    learn_more: NotRequired[list[str]]


Response = Union[SuccessResponse, ErrorResponse]


# Complex types
QueryOptions = dict[str, str | int | bool | list[str]]
PluginConfig = dict[str, Any]
HookRegistry = dict[str, list[HookCallback]]


# Async types
AsyncResult = Awaitable[ResultType]
AsyncGenerator = Awaitable[list[T]]


# Validation types
class ValidationResult(dict):
    """Result from input validation"""

    valid: bool
    sanitized_input: str
    reason: NotRequired[str]
    suggestions: NotRequired[list[str]]


# Learning types
class LearningData(dict):
    """Data for learning system"""

    query: str
    intent: str
    success: bool
    timestamp: float
    context: NotRequired[dict[str, Any]]
    feedback: NotRequired[str]


# Export all types
__all__ = [
    # Type variables
    "T",
    "ResultType",
    # Core types
    "Intent",
    "IntentType",
    # Literals
    "IntentLiteral",
    "LogLevel",
    # TypedDicts
    "PackageInfo",
    "CommandResult",
    "CacheEntry",
    "ConfigDict",
    "SuccessResponse",
    "ErrorResponse",
    "Response",
    "ValidationResult",
    "LearningData",
    # Protocols
    "CommandExecutorProtocol",
    "CacheProtocol",
    "PluginProtocol",
    # Dataclasses
    "ExecutionContext",
    # Callbacks
    "ProgressCallback",
    "ErrorCallback",
    "HookCallback",
    # Complex types
    "QueryOptions",
    "PluginConfig",
    "HookRegistry",
    "AsyncResult",
    "AsyncGenerator",
]
