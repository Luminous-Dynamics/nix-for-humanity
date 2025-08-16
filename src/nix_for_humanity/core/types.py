"""Core types for consciousness-first NixOS interaction."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List


@dataclass
class Command:
    """A NixOS command with consciousness awareness."""
    command: str
    description: str
    dry_run: bool = True
    success: Optional[bool] = None
    output: Optional[str] = None
    consciousness_preserved: bool = True


@dataclass
class Context:
    """Execution context with consciousness state."""
    execute: bool = False
    dry_run: bool = True
    personality: str = "friendly"
    frontend: str = "cli"
    session_id: Optional[str] = None
    user_preferences: Dict[str, Any] = None
    consciousness_level: float = 0.5
    
    def __post_init__(self):
        """Initialize user preferences if not provided."""
        if self.user_preferences is None:
            self.user_preferences = {}


@dataclass
class Request:
    """Request with consciousness-first principles."""
    query: str
    context: Optional[Context] = None
    
    def __post_init__(self):
        """Initialize context if not provided."""
        if self.context is None:
            self.context = Context()