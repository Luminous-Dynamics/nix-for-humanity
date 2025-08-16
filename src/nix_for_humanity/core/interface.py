"""Core interface definitions for consciousness-first computing."""

from enum import Enum
from typing import Any, Dict, Optional, List
from dataclasses import dataclass


class IntentType(Enum):
    """Types of user intents."""
    QUERY = "query"
    INSTALL = "install"
    UPDATE = "update"
    SEARCH = "search"
    CONFIGURE = "configure"
    ROLLBACK = "rollback"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """User intent with consciousness awareness."""
    type: IntentType
    text: str
    context: Dict[str, Any]
    confidence: float = 0.8
    consciousness_level: float = 0.5


@dataclass
class Response:
    """Response with consciousness preservation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    commands: Optional[List[Dict[str, Any]]] = None
    consciousness_level: float = 0.5
    
    @property
    def text(self) -> str:
        """Alias for message for compatibility."""
        return self.message