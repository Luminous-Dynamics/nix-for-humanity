"""Core interface definitions for nix_humanity.

This module provides the interface types needed by the test suite.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Query:
    """Represents a user query with consciousness-first principles."""
    text: str
    context: Optional[Dict[str, Any]] = None
    consciousness_level: float = 0.5
    
    def __post_init__(self):
        """Initialize context if not provided."""
        if self.context is None:
            self.context = {}