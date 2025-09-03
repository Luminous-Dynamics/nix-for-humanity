"""Backend compatibility layer - imports from engine."""

from .engine import NixForHumanityBackend, create_backend

# For backward compatibility
Backend = NixForHumanityBackend

__all__ = ["Backend", "NixForHumanityBackend", "create_backend"]
