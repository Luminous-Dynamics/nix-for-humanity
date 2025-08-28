"""Error handling utilities for Luminous Nix."""


class LuminousNixError(Exception):
    """Base exception for Luminous Nix."""

    pass


class CommandNotFoundError(LuminousNixError):
    """Raised when a command cannot be found."""

    pass


class BackendError(LuminousNixError):
    """Raised when a backend operation fails."""

    pass
