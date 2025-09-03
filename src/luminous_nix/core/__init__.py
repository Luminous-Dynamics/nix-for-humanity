"""Core functionality for Luminous Nix."""

try:
    # Import from actual existing modules
    # Import Command from api module since it's not in core
    from ..api import Command
    from .backend_real import RealNixBackend
    from .command_executor import CommandExecutor
    from .intents import Intent, IntentRecognizer
    from .knowledge import KnowledgeBase
    from .luminous_core import LuminousNixCore
    from .responses import Response

    # Legacy name support
    NixForHumanityCore = LuminousNixCore
    NixForHumanityBackend = RealNixBackend  # Backward compatibility alias

    __all__ = [
        "Intent",
        "IntentRecognizer",
        "CommandExecutor",
        "KnowledgeBase",
        "Command",
        "Response",
        "RealNixBackend",
        "NixForHumanityBackend",  # Backward compatibility
        "LuminousNixCore",
        "NixForHumanityCore",  # Legacy name
    ]
except ImportError as e:
    # More informative error handling
    import warnings

    warnings.warn(f"Some core components not available: {e}")
    __all__ = []
