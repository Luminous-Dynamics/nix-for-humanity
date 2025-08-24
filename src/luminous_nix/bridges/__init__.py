"""
Integration Bridges for Luminous Nix

This module contains bridges that connect aspirational features to working components,
enabling progressive activation as features become ready.
"""

from .poml_cli_bridge import POMLtoCLIBridge
from .store_trinity_bridge import StoreTrinityBridge
from .tui_backend_bridge import TUIBackendBridge

__all__ = [
    'POMLtoCLIBridge',
    'StoreTrinityBridge',
    'TUIBackendBridge',
]