"""Nix for Humanity - Natural Language NixOS Interface.

Making NixOS accessible to everyone through consciousness-first computing.
"""

__version__ = "1.0.0"

from .core import Intent, IntentType, Response, Command, Context, Request

__all__ = [
    'Intent',
    'IntentType',
    'Response',
    'Command', 
    'Context',
    'Request',
]