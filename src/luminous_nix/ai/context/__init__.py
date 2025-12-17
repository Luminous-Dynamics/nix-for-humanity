"""
Context gathering subsystem for AI.
Provides complete system and user understanding.
"""

from .system_context import SystemContext, SystemContextGatherer
from .user_context import UserContext, UserContextManager, SkillLevel

__all__ = [
    'SystemContext',
    'SystemContextGatherer',
    'UserContext',
    'UserContextManager',
    'SkillLevel'
]
