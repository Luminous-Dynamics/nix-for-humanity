"""
Nix for Humanity - Making NixOS accessible through natural conversation.

A revolutionary AI partner that transforms NixOS from command-line complexity
into natural conversation. Consciousness-first design with local-first privacy.
"""

__version__ = "0.5.2"
__author__ = "Tristan Stoltz"
__email__ = "tristan.stoltz@gmail.com"

# Core exports
from nix_humanity.core.engine import NixForHumanityBackend, create_backend
from nix_humanity.core.intents import Intent, IntentType, IntentRecognizer
from nix_humanity.core.executor import SafeExecutor
from nix_humanity.core.knowledge import KnowledgeBase
from nix_humanity.core.personality import PersonalityManager, PersonalityStyle

# API exports
from nix_humanity.api.schema import Request, Response, Result

__all__ = [
    # Version
    "__version__",
    
    # Core classes
    "NixForHumanityBackend",
    "create_backend",
    "Intent",
    "IntentType", 
    "IntentRecognizer",
    "SafeExecutor",
    "KnowledgeBase",
    "PersonalityManager",
    "PersonalityStyle",
    
    # API types
    "Request",
    "Response",
    "Result",
]

# Package metadata
__doc__ = """
Nix for Humanity makes NixOS accessible to everyone through natural language.

Key Features:
- Natural language understanding for NixOS commands
- 10 adaptive personality styles 
- Local-first privacy with all processing on-device
- Revolutionary Python-Nix integration (10x-1500x faster)
- Beautiful TUI with Textual
- Voice interface support
- Consciousness-first design

Usage:
    from nix_humanity import create_backend
    
    backend = create_backend()
    response = backend.process(Request(query="install firefox"))
    print(response.text)
"""