"""Core functionality for Luminous Nix - Unified and Simplified."""

import warnings

# Import unified modules
try:
    # Primary unified modules
    from .config import Config
    from .first_run_wizard import FirstRunWizard
    from .flake_manager import FlakeManager
    from .generation_manager import GenerationManager
    from .home_manager import HomeManager

    # Feature-specific modules (kept separate)
    from .knowledge import KnowledgeBase
    from .nixos_doctor import NixOSDoctor
    from .plugin_system import PluginManager as PluginSystem
    from .profile_migration import profile_migrator
    from .progress_indicator import ProgressIndicator, progress_context
    from .search_cache import SearchCache

    # Smart features
    from .smart_package_discovery import get_smart_discovery
    from .unified_backend import UnifiedNixBackend, get_backend
    from .unified_errors import (
        ErrorCategory,
        ErrorIntelligence,
        ErrorIntelligenceEngine,
        ErrorRecovery,
        analyze_error,
        attempt_recovery,
        format_error,
    )
    from .unified_intent import (
        Intent,
        IntentPipeline,
        IntentRecognizer,
        IntentType,
        SecurityValidator,
        create_intent,
        is_safe,
    )
    from .unified_response import (
        ProgressReporter,
        Response,
        ResponseBuilder,
        ResponseFormatter,
        ResponseType,
        error_response,
        format_response,
        output,
        package_response,
        progress,
        show_packages,
        success_response,
    )

except ImportError as e:
    warnings.warn(f"Some unified modules not available: {e}")
    # Try to import legacy modules for compatibility
    try:
        from .backend_real import RealNixBackend as UnifiedNixBackend
        from .config import Config
        from .error_intelligence import ErrorIntelligence as ErrorIntelligenceEngine
        from .intent_pipeline import IntentPipeline
        from .intents import Intent, IntentRecognizer
        from .knowledge import KnowledgeBase
        from .responses import Response
    except ImportError:
        pass

# Backward compatibility aliases
try:
    # Old backend names -> Unified backend (if it exists)
    if "UnifiedNixBackend" in globals():
        RealNixBackend = UnifiedNixBackend
        NixForHumanityBackend = UnifiedNixBackend
        CommandExecutor = UnifiedNixBackend
        Executor = UnifiedNixBackend
        NixRealExecutor = UnifiedNixBackend
    else:
        # UnifiedNixBackend not available, try engine backend
        from .engine import LuminousNixBackend

        RealNixBackend = LuminousNixBackend
        NixForHumanityBackend = LuminousNixBackend
        UnifiedNixBackend = LuminousNixBackend
        CommandExecutor = LuminousNixBackend
        Executor = LuminousNixBackend

    # Old core names
    from .luminous_core import LuminousNixCore

    NixForHumanityCore = LuminousNixCore
except Exception:
    # Fallback: use engine backend if available
    try:
        from .engine import LuminousNixBackend

        LuminousNixCore = LuminousNixBackend
        NixForHumanityCore = LuminousNixBackend
        RealNixBackend = LuminousNixBackend
        UnifiedNixBackend = LuminousNixBackend
    except:
        pass

# Export all
__all__ = [
    # Unified modules
    "UnifiedNixBackend",
    "get_backend",
    "Intent",
    "IntentType",
    "IntentPipeline",
    "IntentRecognizer",
    "SecurityValidator",
    "create_intent",
    "is_safe",
    "ErrorIntelligence",
    "ErrorIntelligenceEngine",
    "ErrorRecovery",
    "ErrorCategory",
    "analyze_error",
    "format_error",
    "attempt_recovery",
    "Response",
    "ResponseType",
    "ResponseFormatter",
    "ResponseBuilder",
    "ProgressReporter",
    "format_response",
    "success_response",
    "error_response",
    "package_response",
    "output",
    "show_packages",
    "progress",
    # Feature modules
    "KnowledgeBase",
    "Config",
    "profile_migrator",
    "FlakeManager",
    "HomeManager",
    "GenerationManager",
    "NixOSDoctor",
    "FirstRunWizard",
    "PluginSystem",
    "get_smart_discovery",
    "SearchCache",
    "ProgressIndicator",
    "progress_context",
    # Backward compatibility
    "RealNixBackend",
    "NixForHumanityBackend",
    "CommandExecutor",
    "LuminousNixCore",
    "NixForHumanityCore",
]
