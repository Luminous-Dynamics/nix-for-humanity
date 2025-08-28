"""Core functionality for Luminous Nix."""

try:
    # Import from actual existing modules
    # Import Command from api module since it's not in core
    from ..api import Command
    from .command_executor import CommandExecutor
    from .engine import NixForHumanityBackend
    from .intents import Intent, IntentRecognizer
    from .knowledge import KnowledgeBase
    from .luminous_core import LuminousNixCore
    from .responses import Response

    # Legacy name support
    NixForHumanityCore = LuminousNixCore

    __all__ = [
        "Intent",
        "IntentRecognizer",
        "CommandExecutor",
        "KnowledgeBase",
        "Command",
        "Response",
        "NixForHumanityBackend",
        "LuminousNixCore",
        "NixForHumanityCore",  # Legacy name
    ]
except ImportError as e:
    # More informative error handling
    import warnings

    warnings.warn(f"Some core components not available: {e}")
    __all__ = []
