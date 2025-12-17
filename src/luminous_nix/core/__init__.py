"""Core functionality for Luminous Nix - Unified and Simplified."""

import warnings

# Import unified modules
try:
    # Primary unified modules
    from .unified_backend import UnifiedNixBackend, get_backend
    from .unified_intent import (
        Intent, IntentType, IntentPipeline, IntentRecognizer,
        SecurityValidator, create_intent, is_safe
    )
    from .unified_errors import (
        ErrorIntelligence, ErrorIntelligenceEngine, ErrorRecovery,
        ErrorCategory, analyze_error, format_error, attempt_recovery
    )
    from .unified_response import (
        Response, ResponseType, ResponseFormatter, ResponseBuilder,
        ProgressReporter, format_response, success_response, error_response,
        package_response, output, show_packages, progress
    )
    
    # Feature-specific modules (kept separate)
    from .knowledge import KnowledgeBase
    from .config import Config
    from .profile_migration import profile_migrator
    from .flake_manager import FlakeManager
    from .home_manager import HomeManager
    from .generation_manager import GenerationManager
    from .nixos_doctor import NixOSDoctor
    from .first_run_wizard import FirstRunWizard
    from .plugin_system import PluginManager as PluginSystem

    # Week 9-10: PQC Integration
    from .key_manager import KeyManager
    from .backup_manager import BackupManager
    
    # Smart features
    from .smart_package_discovery import get_smart_discovery
    from .search_cache import SearchCache
    from .progress_indicator import ProgressIndicator, progress_context
    
except ImportError as e:
    warnings.warn(f"Some unified modules not available: {e}")
    # Try to import legacy modules for compatibility
    try:
        from .backend_real import RealNixBackend as UnifiedNixBackend
        from .intents import Intent, IntentRecognizer
        from .intent_pipeline import IntentPipeline
        from .responses import Response
        from .error_intelligence import ErrorIntelligence as ErrorIntelligenceEngine
        from .knowledge import KnowledgeBase
        from .config import Config
    except ImportError:
        pass

# Backward compatibility aliases
try:
    # Old backend names -> Unified backend
    RealNixBackend = UnifiedNixBackend
    NixForHumanityBackend = UnifiedNixBackend
    CommandExecutor = UnifiedNixBackend
    Executor = UnifiedNixBackend
    NixRealExecutor = UnifiedNixBackend
    
    # Old core names
    from .luminous_core import LuminousNixCore
    NixForHumanityCore = LuminousNixCore
except:
    # If luminous_core doesn't exist, use UnifiedNixBackend
    LuminousNixCore = UnifiedNixBackend
    NixForHumanityCore = UnifiedNixBackend

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

    # Week 9-10: PQC Integration
    "KeyManager",
    "BackupManager",
    
    # Backward compatibility
    "RealNixBackend",
    "NixForHumanityBackend",
    "CommandExecutor",
    "LuminousNixCore",
    "NixForHumanityCore",
]
