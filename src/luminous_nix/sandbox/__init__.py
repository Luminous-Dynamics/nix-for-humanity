"""
Sandbox System for Safe AI Self-Modification

This module provides a complete sandboxing and safety system that allows
the AI to modify its own code without risking system integrity.
"""

from .sandbox_manager import (
    SandboxManager,
    SafetyValidator,
    ModificationRequest
)

from .safe_modifier import (
    SafeModificationSystem,
    AIImprovement
)

__all__ = [
    'SandboxManager',
    'SafetyValidator', 
    'ModificationRequest',
    'SafeModificationSystem',
    'AIImprovement'
]