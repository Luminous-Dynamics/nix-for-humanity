"""Native Python-Nix integration for high performance."""

# Import what's actually available
try:
    from .native_backend import (
        NativeNixBackend,
        ProgressReporter,
        create_native_backend,
        estimate_completion,
        find_nixos_rebuild_module,
    )

    native_backend_available = True
except ImportError:
    native_backend_available = False

# Import our new Python API
from .python_api import NixAction, NixPythonAPI, NixResult, get_nix_api

__all__ = ["NixPythonAPI", "get_nix_api", "NixAction", "NixResult"]

# Add native backend exports if available
if native_backend_available:
    __all__.extend(
        [
            "find_nixos_rebuild_module",
            "create_native_backend",
            "NativeNixBackend",
            "ProgressReporter",
            "estimate_completion",
        ]
    )
