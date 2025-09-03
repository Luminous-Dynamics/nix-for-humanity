"""Luminous Nix - Natural Language Interface for NixOS.

A tool that makes NixOS accessible through natural conversation.
"""

__version__ = "0.4.1"
__author__ = "Tristan Stoltz"
__email__ = "tristan.stoltz@gmail.com"

# Import core functionality
try:
    from .core.command_executor import CommandExecutor
    from .core.intents import Intent, IntentType
    from .core.responses import Response
    from .knowledge.knowledge_base import KnowledgeBase
    from .nlp.intent_recognition import IntentRecognizer
except ImportError:
    # Graceful degradation during restructuring
    pass

# Import frontends
try:
    from .frontends.cli import CLI
except ImportError:
    pass

__all__ = [
    "__version__",
    "CommandExecutor",
    "Intent",
    "IntentType",
    "Response",
    "IntentRecognizer",
    "KnowledgeBase",
    "CLI",
]
