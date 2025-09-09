"""Native Python-Nix integration for high performance.

This module exports the subprocess-based operations that provides
standard Nix performance improvements by using subprocess.
"""

# Import from the core native API module
try:
    from ..core.native_nix_api import NativeNixAPI, get_native_api
    NATIVE_API_AVAILABLE = True
except ImportError:
    NATIVE_API_AVAILABLE = False
    NativeNixAPI = None
    get_native_api = None

# For backward compatibility, provide a unified interface
if NATIVE_API_AVAILABLE:
    # Create singleton instance
    _api = get_native_api()
    
    # Export commonly used methods
    search_packages = _api.search_packages if _api else None
    install_package = _api.install_package if _api else None
    build_configuration = _api.build_configuration if _api else None
    list_generations = _api.list_generations if _api else None

__all__ = [
    "NativeNixAPI",
    "get_native_api",
    "NATIVE_API_AVAILABLE",
    "search_packages",
    "install_package",
    "build_configuration",
    "list_generations",
]
