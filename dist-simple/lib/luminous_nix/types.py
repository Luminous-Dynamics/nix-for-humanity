"""Shared types for Nix for Humanity.

from typing import Union, Dict, Optional
This module contains types that are used across multiple modules
to avoid circular dependencies.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class BackendResponse:
    """Response from backend operations."""

    success: bool
    data: Any | None = None
    error: str | None = None
    message: str | None = None


@dataclass
class CommandResult:
    """Result of executing a command."""

    success: bool
    output: str
    error: str | None = None
    return_code: int = 0


# Type aliases
ConfigDict = dict[str, Any]
MetricsDict = dict[str, str | int | float]
