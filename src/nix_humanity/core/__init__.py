"""
v1.0 exports - Core functionality only
"""

# v1.0 components
from .backend import NixForHumanityBackend
from .intents import IntentRecognizer, Intent, IntentType
from .executor import SafeExecutor
from .knowledge import KnowledgeBase
from .error_handler import ErrorHandler
from .personality import PersonalityManager as PersonalitySystem

__all__ = ['NixForHumanityBackend', 'IntentRecognizer', 'Intent', 'IntentType', 'SafeExecutor', 'KnowledgeBase', 'ErrorHandler', 'PersonalitySystem']
