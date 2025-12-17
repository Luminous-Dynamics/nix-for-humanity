"""
Specialized Sophia Agents

Domain-specific agents that extend the unified consciousness
with deep expertise in their specialization areas.
"""

from .sophia_nixos import SophiaNixOS
from .sophia_shell import SophiaShell
from .sophia_security import SophiaSecurity

__all__ = [
    "SophiaNixOS",
    "SophiaShell",
    "SophiaSecurity",
]
