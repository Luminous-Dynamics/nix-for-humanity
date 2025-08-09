"""
CLI Frontend for Nix for Humanity

The command-line interface adapter that connects the ask-nix command
to the unified backend.
"""

from .adapter import CLIAdapter, main

__all__ = ["CLIAdapter", "main"]