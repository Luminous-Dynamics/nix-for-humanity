"""
🌟 Luminous Nix UI Module - Consciousness-First Terminal Interface

This module provides the TUI (Terminal User Interface) components for Luminous Nix,
including adaptive complexity, personality integration, and consciousness visualization.
"""

from .adaptive_interface import AdaptiveInterface
from .main_app import LuminousNixTUI

# Import UX-TUI integration (optional - may not have all dependencies)
try:
    from .ux_tui_integration import (
        UXTUIBridge,
        get_ux_tui_bridge,
        get_adaptive_config,
        get_complexity_level,
        format_for_user,
        record_interaction,
    )
    UX_INTEGRATION_AVAILABLE = True
except ImportError:
    UX_INTEGRATION_AVAILABLE = False

# Import adaptive complexity system
try:
    from .adaptive_complexity import (
        AdaptiveUISystem,
        UIComplexityLevel,
        AdaptiveUIConfig,
    )
    ADAPTIVE_COMPLEXITY_AVAILABLE = True
except ImportError:
    ADAPTIVE_COMPLEXITY_AVAILABLE = False

__all__ = [
    "AdaptiveInterface",
    "LuminousNixTUI",
    "UX_INTEGRATION_AVAILABLE",
    "ADAPTIVE_COMPLEXITY_AVAILABLE",
]

# Conditional exports
if UX_INTEGRATION_AVAILABLE:
    __all__.extend([
        "UXTUIBridge",
        "get_ux_tui_bridge",
        "get_adaptive_config",
        "get_complexity_level",
        "format_for_user",
        "record_interaction",
    ])

if ADAPTIVE_COMPLEXITY_AVAILABLE:
    __all__.extend([
        "AdaptiveUISystem",
        "UIComplexityLevel",
        "AdaptiveUIConfig",
    ])
