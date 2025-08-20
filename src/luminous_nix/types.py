"""Shared types for Nix for Humanity.

from typing import Union, Dict, Optional
This module contains types that are used across multiple modules
to avoid circular dependencies.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum


@dataclass
class BackendResponse:
    """Response from backend operations."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


@dataclass
class CommandResult:
    """Result of executing a command."""
    success: bool
    output: str
    error: Optional[str] = None
    return_code: int = 0


# Type aliases
ConfigDict = Dict[str, Any]
MetricsDict = Dict[str, Union[str, int, float]]