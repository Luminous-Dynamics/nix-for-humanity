"""
Real backend implementation that actually executes NixOS commands.

This replaces the mock backend with real functionality.
"""

import os
from typing import Dict, Any, Optional

from .nix_real_executor import NixRealExecutor
from .intents import Intent, IntentType
from luminous_nix.api.schema import Response, Result


class RealNixBackend:
    """
    Backend that actually executes NixOS commands.
    
    No more mocks! This is the real deal.
    """
    
    def __init__(self):
        """Initialize with real executor"""
        # Check if dry run mode
        self.dry_run = os.getenv("LUMINOUS_DRY_RUN", "false").lower() == "true"
        self.verbose = os.getenv("LUMINOUS_VERBOSE", "0")
        
        # Create real executor
        self.executor = NixRealExecutor(
            timeout=30,
            dry_run=self.dry_run
        )
        
        # Get system info once
        self.system_info = self.executor.get_system_info().get("info", {})
        
    def process(self, intent: Intent) -> Response:
        """
        Process intent with REAL NixOS operations.
        
        Args:
            intent: The parsed intent from user input
            
        Returns:
            Response with real results, not mocked!
        """
        
        # Map intent types to real operations
        if intent.type == IntentType.SEARCH_PACKAGE:
            return self._handle_search(intent)
        elif intent.type == IntentType.LIST_INSTALLED:
            return self._handle_list(intent)
        elif intent.type == IntentType.INSTALL_PACKAGE:
            return self._handle_install(intent)
        elif intent.type == IntentType.REMOVE_PACKAGE:
            return self._handle_remove(intent)
        elif intent.type == IntentType.UPDATE_SYSTEM:
            return self._handle_update(intent)
        elif intent.type == IntentType.CHECK_STATUS:
            return self._handle_info(intent)
        elif intent.type == IntentType.HELP:
            return self._handle_help(intent)
        else:
            return Response(
                success=False,
                text=f"Intent type {intent.type} not yet implemented in real backend"
            )
    
    def _handle_search(self, intent: Intent) -> Response:
        """Handle package search with real nix search"""
        query = intent.entities.get("package", "") or intent.raw_text or ""
        
        if not query or query.lower() in ["packages", "package", ""]:
            return Response(
                success=False,
                text="Please specify what to search for. Example: 'search firefox'"
            )
        
        # Use shorter timeout for search
        self.executor.timeout = 10
        result = self.executor.search_packages(query)
        
        if result.get("timeout"):
            # Search timed out - try simpler approach
            result = self.executor.execute(
                "nix-env",
                ["-qa", f"*{query}*"],
                force_old_style=True
            )
            
        if result.get("success"):
            output = result.get("output", "")
            if result.get("packages"):
                # Structured output
                packages = result["packages"]
                if isinstance(packages, dict):
                    # JSON search results
                    names = [k.split(".")[-1] for k in packages.keys()][:10]
                    message = f"Found {len(packages)} packages matching '{query}':\n"
                    message += "\n".join(f"  • {name}" for name in names)
                else:
                    # Line-based results
                    message = f"Found packages matching '{query}':\n{output}"
            else:
                message = f"Search results for '{query}':\n{output}"
                
            return Response(
                success=True,
                text=message,
                data={"query": query, "results": result.get("packages", [])}
            )
        else:
            return Response(
                success=False,
                text=f"Search failed: {result.get('error', 'Unknown error')}"
            )
    
    def _handle_list(self, intent: Intent) -> Response:
        """Handle listing installed packages"""
        result = self.executor.list_installed()
        
        if result.get("success"):
            packages = result.get("packages", [])
            if packages:
                # Clean up profile list output
                if self.executor.use_nix_profile:
                    # Parse new profile format
                    clean_packages = []
                    for line in packages:
                        if "Name:" in line:
                            name = line.replace("Name:", "").strip()
                            # Remove ANSI codes
                            name = name.replace("\x1b[1m", "").replace("\x1b[0m", "")
                            clean_packages.append(name)
                    packages = clean_packages
                
                message = f"Installed packages ({len(packages)} total):\n"
                message += "\n".join(f"  • {pkg}" for pkg in packages[:20])
                if len(packages) > 20:
                    message += f"\n  ... and {len(packages) - 20} more"
            else:
                message = "No packages installed in current profile"
                
            return Response(
                success=True,
                text=message,
                data={"packages": packages}
            )
        else:
            return Response(
                success=False,
                text=f"Failed to list packages: {result.get('error', 'Unknown error')}"
            )
    
    def _handle_install(self, intent: Intent) -> Response:
        """Handle package installation"""
        package = intent.entities.get("package", "")
        
        if not package:
            return Response(
                success=False,
                text="Please specify a package to install. Example: 'install firefox'"            )
        
        if self.dry_run:
            return Response(
                success=True,
                text=f"DRY RUN: Would install package '{package}'",
                data={"package": package, "dry_run": True}
            )
        
        # Real installation
        if self.executor.use_nix_profile:
            result = self.executor.execute("nix", ["profile", "install", f"nixpkgs#{package}"])
        else:
            result = self.executor.execute("nix-env", ["-iA", f"nixos.{package}"])
        
        if result.get("success"):
            return Response(
                success=True,
                text=f"Successfully installed '{package}'",
                data={"package": package}
            )
        else:
            error = result.get("error", "Unknown error")
            if "attribute" in error.lower() and "not found" in error.lower():
                message = f"Package '{package}' not found. Try: 'search {package}' to find the correct name"
            else:
                message = f"Failed to install '{package}': {error}"
                
            return Response(
                success=False,
                text=message            )
    
    def _handle_remove(self, intent: Intent) -> Response:
        """Handle package removal"""
        package = intent.entities.get("package", "")
        
        if not package:
            return Response(
                success=False,
                text="Please specify a package to remove. Example: 'remove firefox'"            )
        
        if self.dry_run:
            return Response(
                success=True,
                text=f"DRY RUN: Would remove package '{package}'",
                data={"package": package, "dry_run": True}
            )
        
        # Real removal
        if self.executor.use_nix_profile:
            result = self.executor.execute("nix", ["profile", "remove", package])
        else:
            result = self.executor.execute("nix-env", ["-e", package])
        
        if result.get("success"):
            return Response(
                success=True,
                text=f"Successfully removed '{package}'",
                data={"package": package}
            )
        else:
            return Response(
                success=False,
                text=f"Failed to remove '{package}': {result.get('error', 'Unknown error')}"            )
    
    def _handle_update(self, intent: Intent) -> Response:
        """Handle system update"""
        if self.dry_run:
            return Response(
                success=True,
                text="DRY RUN: Would update NixOS channels and packages",
                data={"dry_run": True}
            )
        
        # This needs sudo usually
        return Response(
            type=ResponseType.INFO,
            message="System update requires elevated privileges. Please run:\n  sudo nix-channel --update\n  sudo nixos-rebuild switch",
            success=True
        )
    
    def _handle_info(self, intent: Intent) -> Response:
        """Handle info request"""
        package = intent.entities.get("package", "")
        
        if package:
            # Get package info
            result = self.executor.execute("nix-env", ["-qa", "-A", f"nixos.{package}", "--description"])
            if result.get("success"):
                return Response(
                    type=ResponseType.INFO,
                    message=f"Package info for '{package}':\n{result['output']}",
                    success=True
                )
            else:
                return Response(
                    type=ResponseType.ERROR,
                    message=f"Could not find info for '{package}'",
                    success=False
                )
        else:
            # General system info
            info = self.system_info
            message = "System Information:\n"
            message += f"  NixOS Version: {info.get('nixos_version', 'Unknown')}\n"
            message += f"  Nix Version: {info.get('nix_version', 'Unknown')}\n"
            message += f"  Profile Type: {info.get('profile_type', 'Unknown')}"
            
            return Response(
                success=True,
                text=message,
                data=info
            )
    
    def _handle_help(self, intent: Intent) -> Response:
        """Handle help request"""
        help_text = """
Luminous Nix - Natural Language NixOS Interface

WORKING COMMANDS:
  search <package>   - Search for packages (e.g., 'search firefox')
  list              - List installed packages
  install <package> - Install a package (requires privileges)
  remove <package>  - Remove a package (requires privileges)
  info [package]    - Show package or system info
  help             - Show this help

EXAMPLES:
  ask-nix "search text editor"
  ask-nix "list"
  ask-nix "install vim"
  ask-nix "info firefox"

ENVIRONMENT:
  LUMINOUS_DRY_RUN=true  - Preview commands without executing
  LUMINOUS_VERBOSE=1     - Show detailed output

STATUS: v0.1.0-alpha - Basic functionality only
        """
        
        return Response(
            success=True,
            text=help_text.strip()
        )


def create_real_backend() -> RealNixBackend:
    """Factory function to create real backend"""
    return RealNixBackend()


# Make it compatible with existing imports
Backend = RealNixBackend
NixForHumanityBackend = RealNixBackend
LuminousNixBackend = RealNixBackend

__all__ = ["RealNixBackend", "Backend", "create_real_backend"]