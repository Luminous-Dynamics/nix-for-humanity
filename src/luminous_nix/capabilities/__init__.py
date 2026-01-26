"""
Luminous Nix Capabilities

Higher-level capability modules that integrate multiple subsystems:
- WisdomIntegration: Pattern intelligence from the Mycelix WisdomEngine
"""

from .wisdom_integration import (
    WisdomIntegration,
    get_wisdom_integration,
    reset_wisdom_integration,
    WisdomContext,
    WISDOM_AVAILABLE,
)

__all__ = [
    "WisdomIntegration",
    "get_wisdom_integration",
    "reset_wisdom_integration",
    "WisdomContext",
    "WISDOM_AVAILABLE",
]
