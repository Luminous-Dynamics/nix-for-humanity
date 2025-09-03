"""
Real backend implementation that actually executes NixOS commands.

This replaces the mock backend with real functionality.
"""

import os
from typing import Dict, Any, Optional

from .nix_real_executor import NixRealExecutor
from .intents import Intent, IntentType
from luminous_nix.api.schema import Response, Result
from .search_cache import SearchCache
from .config import Config
from .smart_package_discovery import get_smart_discovery
from .enhanced_output import output, show_packages, progress


class RealNixBackend:
    """
    Backend that actually executes NixOS commands.
    
    No more mocks! This is the real deal.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize with real executor"""
        # Use provided config or create default
        self.config = config or Config()
        
        # Create real executor with config settings
        self.executor = NixRealExecutor(
            timeout=self.config.timeout,
            dry_run=self.config.preview  # preview mode = dry run
        )
        
        # Initialize search cache if enabled
        if self.config.cache_enabled:
            self.search_cache = SearchCache()
        else:
            self.search_cache = None
        
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
        """Handle package search with smart discovery"""
        query = intent.entities.get("package", "") or intent.raw_text or ""
        
        if not query or query.lower() in ["packages", "package", ""]:
            return Response(
                success=False,
                text="Please specify what to search for. Example: 'search firefox'"
            )
        
        # Use smart discovery first
        discovery = get_smart_discovery()
        smart_matches = discovery.find_packages(query)
        
        if smart_matches:
            # Format smart results with beautiful output
            results = []
            
            for match in smart_matches[:20]:  # Top 20 matches
                results.append({
                    "name": match.name,
                    "description": match.description or "No description available",
                    "version": match.confidence,  # Using confidence as version placeholder
                    "reason": match.match_reason
                })
            
            # Show packages in beautiful table
            show_packages(results, title=f"🔍 Search results for '{query}'")
            
            # Add suggestion if it was a typo
            correction = discovery.suggest_correction(query)
            if correction and correction != query.lower():
                output.suggest_commands([correction])
            
            # Still return Response for API compatibility
            message = f"Found {len(results)} packages for '{query}'"
            return Response(
                success=True,
                text=message,
                data={"query": query, "results": results, "smart_search": True}
            )
        
        # Quick common package lookup (< 1 second)
        # This is a workaround until we can optimize nix-env -qa
        common_packages = {
            "vim": ["vim", "neovim", "vim-full", "vim-darwin", "vim-configurable"],
            "firefox": ["firefox", "firefox-esr", "firefox-devedition", "firefox-bin"],
            "editor": ["vim", "neovim", "emacs", "nano", "vscode", "sublime3"],
            "browser": ["firefox", "chromium", "brave", "google-chrome", "vivaldi"],
            "python": ["python3", "python312", "python311", "python310", "python39"],
            "terminal": ["alacritty", "kitty", "wezterm", "terminator", "gnome-terminal"],
            "git": ["git", "git-lfs", "gitFull", "git-interactive-rebase-tool"],
            "docker": ["docker", "docker-compose", "docker-client", "docker-machine"],
        }
        
        # Check if we have common results
        query_lower = query.lower()
        results = []
        
        for key, packages in common_packages.items():
            if query_lower in key or key in query_lower:
                for pkg in packages:
                    results.append({"name": pkg, "description": f"Package: {pkg}"})
        
        # If no common results, try limited real search
        if not results:
            try:
                # Very quick timeout to avoid hanging
                import subprocess
                result = subprocess.run(
                    ["nix-env", "-qa", f"*{query}*"],
                    capture_output=True,
                    text=True,
                    timeout=1  # Only 1 second timeout
                )
                
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split("\n")[:10]  # Only first 10
                    for line in lines:
                        if line.strip():
                            results.append({"name": line.strip(), "description": ""})
            except:
                # If search fails, return helpful message
                results = [{"name": f"Try: nix-env -qa '*{query}*'", "description": "Run this command for full results"}]
        
        # Format results
        if results:
            # Format the results nicely
            shown = results[:15]  # Show first 15 results
            message = f"Found {len(results)} packages matching '{query}':\n"
            for pkg in shown:
                name = pkg.get("name", "")
                desc = pkg.get("description", "")
                if desc and desc != f"Package: {name}":  # Skip default descriptions
                    message += f"  • {name} - {desc[:60]}\n"
                else:
                    message += f"  • {name}\n"
            if len(results) > 15:
                message += f"  ... and {len(results) - 15} more"
        else:
            message = f"No packages found matching '{query}'"
            
        return Response(
            success=True,
            text=message,
            data={"query": query, "results": results}
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
        
        if self.config.preview:
            return Response(
                success=True,
                text=f"PREVIEW: Would install package '{package}'",
                data={"package": package, "preview": True}
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
        
        if self.config.preview:
            return Response(
                success=True,
                text=f"PREVIEW: Would remove package '{package}'",
                data={"package": package, "preview": True}
            )
        
        # Real removal
        if self.executor.use_nix_profile:
            # First, list profiles to find the package
            list_result = self.executor.execute("nix", ["profile", "list"])
            if list_result.get("success"):
                # Find the package in the profile list
                package_num = None
                for line in list_result.get("output", "").splitlines():
                    if package in line:
                        # Extract the profile number (first field)
                        parts = line.split()
                        if parts:
                            package_num = parts[0]
                            break
                
                if package_num:
                    # Remove by profile number
                    result = self.executor.execute("nix", ["profile", "remove", package_num])
                else:
                    # Package not found in profile
                    result = {
                        "success": False,
                        "error": f"Package '{package}' not found in profile"
                    }
            else:
                result = list_result
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
        if self.config.preview:
            return Response(
                success=True,
                text="PREVIEW: Would update NixOS channels and packages",
                data={"preview": True}
            )
        
        # This needs sudo usually
        return Response(
            success=True,
            text="System update requires elevated privileges. Please run:\n  sudo nix-channel --update\n  sudo nixos-rebuild switch"
        )
    
    def _handle_info(self, intent: Intent) -> Response:
        """Handle info request"""
        package = intent.entities.get("package", "")
        
        if package:
            # Get package info
            result = self.executor.execute("nix-env", ["-qa", "-A", f"nixos.{package}", "--description"])
            if result.get("success"):
                return Response(
                    success=True,
                    text=f"Package info for '{package}':\n{result['output']}"
                )
            else:
                return Response(
                    success=False,
                    text=f"Could not find info for '{package}'"
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