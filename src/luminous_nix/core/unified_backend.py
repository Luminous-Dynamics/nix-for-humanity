"""
Unified NixOS Backend - Single source of truth for all NixOS operations.

This consolidates functionality from:
- backend_real.py
- executor.py
- command_executor.py
- nix_real_executor.py
- native_nix_api.py
- native_operations.py
- native_operations_advanced.py

Philosophy: One backend to rule them all, with clear separation of concerns.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

from .unified_intent import Intent, IntentType

# Import unified modules
from .unified_response import (
    Response,
)

# Import existing feature modules (these should exist)
try:
    from .profile_migration import check_and_migrate, profile_migrator
except ImportError:
    profile_migrator = None

    def check_and_migrate():
        return None


try:
    from .search_cache import SearchCache
except ImportError:
    SearchCache = None

try:
    from .config import Config
except ImportError:
    # Simple config fallback
    class Config:
        def __init__(self, timeout=30, preview=False, cache_enabled=False):
            self.timeout = timeout
            self.preview = preview
            self.cache_enabled = cache_enabled


try:
    from .smart_package_discovery import get_smart_discovery
except ImportError:

    def get_smart_discovery():
        return None


# Simple progress context manager
from contextlib import contextmanager


@contextmanager
def progress_context(description):
    print(f"⏳ {description}...")
    yield
    print(f"✅ {description} complete")


logger = logging.getLogger(__name__)


class UnifiedNixBackend:
    """
    The ONE backend for all NixOS operations.

    Features:
    - Real command execution via subprocess
    - subprocess-based operations support (NixOS 25.11+)
    - Profile migration handling
    - Smart package discovery
    - Progress indicators
    - Dry-run mode
    - Comprehensive error handling
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the unified backend."""
        self.config = config or Config()
        self.timeout = self.config.timeout
        self.dry_run = self.config.preview
        self.experimental_features = "nix-command flakes"

        # Initialize profile migration
        migration_error = check_and_migrate()
        if migration_error:
            logger.warning(f"Profile migration issue: {migration_error}")

        # Detect profile type
        self.use_nix_profile = self._detect_profile_type()

        # Initialize caches if enabled
        self.search_cache = SearchCache() if self.config.cache_enabled else None

        # Try to initialize native API if available
        self.native_api = self._init_native_api()

    def _detect_profile_type(self) -> bool:
        """Detect if using new nix profile or old nix-env."""
        profile_path = Path.home() / ".local/state/nix/profiles/profile"
        if profile_path.exists():
            manifest = profile_path / "manifest.json"
            return manifest.exists()
        return False

    def _init_native_api(self) -> Optional[Any]:
        """Initialize subprocess-based operations if available (NixOS 25.11+)."""
        try:
            # Try to import the native API
            import nixos_rebuild
            from nixos_rebuild import models, nix

            return nix
        except ImportError:
            logger.debug("subprocess-based operations not available")
            return None

    # ==================== Main Interface ====================

    def process(self, intent: Intent) -> Response:
        """Process any intent with the appropriate NixOS operation."""

        # Route to appropriate handler
        handlers = {
            IntentType.SEARCH_PACKAGE: self.search,
            IntentType.LIST_INSTALLED: self.list_installed,
            IntentType.INSTALL_PACKAGE: self.install,
            IntentType.REMOVE_PACKAGE: self.remove,
            IntentType.UPDATE_SYSTEM: self.update_system,
            IntentType.CHECK_STATUS: self.get_info,
            IntentType.HELP: self.get_help,
            IntentType.GENERATE_CONFIG: self.generate_config,
            IntentType.MANAGE_FLAKE: self.manage_flake,
            IntentType.MANAGE_GENERATION: self.manage_generation,
            IntentType.HOME_MANAGER: self.home_manager,
        }

        handler = handlers.get(intent.type)
        if handler:
            try:
                return handler(intent)
            except Exception as e:
                logger.error(f"Handler error: {e}")
                return Response(
                    success=False, text=f"Error processing {intent.type}: {str(e)}"
                )
        else:
            return Response(
                success=False, text=f"Operation {intent.type} not yet implemented"
            )

    # ==================== Core Operations ====================

    def search(self, intent: Intent) -> Response:
        """Search for packages using smart discovery."""
        query = intent.entities.get("package", "") or intent.raw_text or ""

        if not query:
            return Response(
                success=False,
                text="Please specify what to search for. Example: 'search firefox'",
            )

        # Use smart discovery first
        discovery = get_smart_discovery()
        smart_matches = discovery.find_packages(query)

        if smart_matches:
            # Format results
            results = []
            for match in smart_matches[:20]:
                results.append(
                    {
                        "name": match.name,
                        "description": match.description or "No description",
                        "score": match.score,
                    }
                )

            # Also check cache if available
            if self.search_cache:
                cached = self.search_cache.get(query)
                if cached:
                    results.extend(cached.get("packages", [])[:5])

            return Response(
                success=True,
                text=f"Found {len(results)} packages matching '{query}'",
                data={"packages": results},
            )

        # Fallback to nix search
        return self._nix_search(query)

    def list_installed(self, intent: Intent) -> Response:
        """List installed packages."""
        if self.use_nix_profile:
            cmd = ["nix", "profile", "list"]
        else:
            cmd = ["nix-env", "-q"]

        result = self._execute_command(cmd)

        if result["success"]:
            packages = result["output"].strip().split("\n")
            return Response(
                success=True,
                text=f"You have {len(packages)} packages installed",
                data={"packages": packages},
            )
        else:
            return Response(
                success=False,
                text="Failed to list packages",
                data={"error": result.get("error")},
            )

    def install(self, intent: Intent) -> Response:
        """Install a package."""
        package = intent.entities.get("package")
        if not package:
            return Response(success=False, text="Please specify a package to install")

        # Check profile migration
        if profile_migrator.needs_migration():
            profile_migrator.migrate_profile()

        # Use appropriate command
        if self.use_nix_profile:
            cmd = ["nix", "profile", "install", f"nixpkgs#{package}"]
        else:
            cmd = ["nix-env", "-iA", f"nixpkgs.{package}"]

        # Add dry-run if needed
        if self.dry_run:
            if "nix" in cmd[0]:
                cmd.insert(2, "--dry-run")
            else:
                cmd.append("--dry-run")

        # Execute with progress
        with progress_context(f"Installing {package}"):
            result = self._execute_command(cmd, timeout=120)

        if result["success"]:
            action = "would be installed" if self.dry_run else "installed successfully"
            return Response(success=True, text=f"{package} {action}", data=result)
        else:
            return Response(
                success=False,
                text=f"Failed to install {package}",
                data={"error": result.get("error")},
            )

    def remove(self, intent: Intent) -> Response:
        """Remove a package."""
        package = intent.entities.get("package")
        if not package:
            return Response(success=False, text="Please specify a package to remove")

        # Check profile migration
        if profile_migrator.needs_migration():
            profile_migrator.migrate_profile()

        # Use appropriate command
        if self.use_nix_profile:
            cmd = ["nix", "profile", "remove", package]
        else:
            cmd = ["nix-env", "-e", package]

        # Add dry-run if needed
        if self.dry_run:
            if "nix" in cmd[0]:
                cmd.insert(2, "--dry-run")
            else:
                cmd.append("--dry-run")

        # Execute with progress
        with progress_context(f"Removing {package}"):
            result = self._execute_command(cmd)

        if result["success"]:
            action = "would be removed" if self.dry_run else "removed successfully"
            return Response(success=True, text=f"{package} {action}", data=result)
        else:
            return Response(
                success=False,
                text=f"Failed to remove {package}",
                data={"error": result.get("error")},
            )

    def update_system(self, intent: Intent) -> Response:
        """Update the system."""
        # For system updates, use subprocess (not native API yet)
        cmd = ["sudo", "nix-channel", "--update"]

        if self.dry_run:
            return Response(
                success=True, text="Would update system channels (dry-run mode)"
            )

        with progress_context("Updating system channels"):
            result = self._execute_command(cmd, timeout=300)

        if result["success"]:
            return Response(
                success=True, text="System channels updated successfully", data=result
            )
        else:
            return Response(
                success=False,
                text="Failed to update system",
                data={"error": result.get("error")},
            )

    def get_info(self, intent: Intent) -> Response:
        """Get package info."""
        package = intent.entities.get("package")
        if not package:
            # Return system info
            return self._get_system_info()

        # Search for package info with timeout
        cmd = ["nix", "search", "nixpkgs", f"^{package}$", "--json"]
        result = self._execute_command(cmd, timeout=5)  # Short timeout

        if result["success"] and result["output"]:
            try:
                info = json.loads(result["output"])
                if info:
                    pkg_key = list(info.keys())[0]
                    pkg_info = info[pkg_key]
                    return Response(
                        success=True,
                        text=f"Package: {package}",
                        data={
                            "name": package,
                            "version": pkg_info.get("version", "unknown"),
                            "description": pkg_info.get(
                                "description", "No description"
                            ),
                        },
                    )
            except json.JSONDecodeError:
                pass

        # Fallback to simpler query
        cmd = ["nix-env", "-qa", package]
        result = self._execute_command(cmd, timeout=5)

        if result["success"] and result["output"]:
            return Response(
                success=True,
                text=f"Package {package} is available",
                data={"output": result["output"]},
            )

        return Response(success=False, text=f"No info found for {package}")

    def get_help(self, intent: Intent) -> Response:
        """Get help information."""
        help_text = """
Luminous Nix - Natural Language NixOS Interface

Available commands:
• search <package> - Search for packages
• install <package> - Install a package
• remove <package> - Remove a package
• list - List installed packages
• update - Update system
• info <package> - Get package information
• generate config - Generate NixOS configuration
• flake init - Initialize a flake
• generations - List system generations
• home-manager - Manage home configuration

Examples:
• "search firefox"
• "install vim"
• "list installed packages"
• "generate web server config"
        """
        return Response(success=True, text=help_text)

    # ==================== Advanced Operations ====================

    def generate_config(self, intent: Intent) -> Response:
        """Generate NixOS configuration."""
        # This would call config_generator module
        return Response(
            success=True,
            text="Configuration generation moved to config_generator module",
        )

    def manage_flake(self, intent: Intent) -> Response:
        """Manage flakes."""
        # This would call flake_manager module
        return Response(
            success=True, text="Flake management moved to flake_manager module"
        )

    def manage_generation(self, intent: Intent) -> Response:
        """Manage system generations."""
        # This would call generation_manager module
        return Response(
            success=True,
            text="Generation management moved to generation_manager module",
        )

    def home_manager(self, intent: Intent) -> Response:
        """Manage home-manager configuration."""
        # This would call home_manager module
        return Response(
            success=True, text="Home management moved to home_manager module"
        )

    # ==================== Internal Helpers ====================

    def _execute_command(self, cmd: list[str], timeout: int = None) -> dict[str, Any]:
        """Execute a command with proper error handling."""
        timeout = timeout or self.timeout

        logger.debug(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={
                    **os.environ,
                    "NIX_CONFIG": f"experimental-features = {self.experimental_features}",
                },
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "returncode": result.returncode,
                "command": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": " ".join(cmd),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": " ".join(cmd)}

    def _nix_search(self, query: str) -> Response:
        """Fallback nix search."""
        cmd = ["nix", "search", "nixpkgs", query, "--json"]
        result = self._execute_command(cmd, timeout=10)

        if result["success"]:
            try:
                packages = json.loads(result["output"])
                # Cache result
                if self.search_cache:
                    self.search_cache.set(query, {"packages": list(packages.keys())})

                return Response(
                    success=True,
                    text=f"Found {len(packages)} packages",
                    data={"packages": packages},
                )
            except json.JSONDecodeError:
                pass

        return Response(
            success=False,
            text=f"Search failed for '{query}'",
            data={"error": result.get("error")},
        )

    def _get_system_info(self) -> Response:
        """Get system information."""
        info = {}

        # Get NixOS version
        result = self._execute_command(["nixos-version"])
        if result["success"]:
            info["nixos_version"] = result["output"].strip()

        # Get channel info
        result = self._execute_command(["nix-channel", "--list"])
        if result["success"]:
            info["channels"] = result["output"].strip().split("\n")

        # Profile type
        info["profile_type"] = "nix profile" if self.use_nix_profile else "nix-env"

        # Native API status
        info["native_api"] = self.native_api is not None

        return Response(success=True, text="System Information", data=info)


# Singleton instance for import compatibility
_backend_instance = None


def get_backend(config: Optional[Config] = None) -> UnifiedNixBackend:
    """Get the singleton backend instance."""
    global _backend_instance
    if _backend_instance is None:
        _backend_instance = UnifiedNixBackend(config)
    return _backend_instance
