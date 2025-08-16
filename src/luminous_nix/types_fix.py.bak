"""
Temporary fix for missing types.

This module provides the missing Intent type that should be in types.py
but is actually in core modules.
"""

# Import Intent from where it actually exists
try:
    from .core.intents import Intent, IntentType
except ImportError:
    try:
        from .core.unified_backend import Intent, IntentType
    except ImportError:
        # Fallback definition
        from dataclasses import dataclass
        from enum import Enum
        from typing import Any

        class IntentType(Enum):
            INSTALL = "install"
            SEARCH = "search"
            UPDATE = "update"
            REMOVE = "remove"
            BUILD = "build"
            UNKNOWN = "unknown"

        @dataclass
        class Intent:
            type: IntentType
            query: str
            params: dict[str, Any] | None = None
            context: dict[str, Any] | None = None


# Re-export everything from the real types module
from .types import *

# Add the missing Intent to exports
__all__ = ["Intent", "IntentType", "ExecutionContext", "QueryResult"]
