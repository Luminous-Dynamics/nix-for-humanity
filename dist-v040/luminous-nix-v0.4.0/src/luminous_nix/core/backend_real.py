"""
Real backend implementation that actually executes NixOS commands.

This replaces the mock backend with real functionality.
Now uses the subprocess-based operations for standard Nix performance!
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
from .profile_migration import profile_migrator

# Import the REAL performance improvements
try:
    from .enhanced_cache import get_enhanced_cache
    CACHE_AVAILABLE = True
except ImportError:
    try:
        from .fast_package_cache import get_fast_cache
        CACHE_AVAILABLE = True
    except ImportError:
        CACHE_AVAILABLE = False

# Import cache management commands
try:
    from .cache_commands import get_cache_commands
    CACHE_COMMANDS_AVAILABLE = True
except ImportError:
    CACHE_COMMANDS_AVAILABLE = False

try:
    from .package_index import get_package_index
    INDEX_AVAILABLE = True
except ImportError:
    INDEX_AVAILABLE = False

# Import the native API (currently doesn't actually work)
try:
    from .native_nix_api import get_native_api
    NATIVE_API_AVAILABLE = True
except ImportError:
    NATIVE_API_AVAILABLE = False


class RealNixBackend:
    """
    Backend that actually executes NixOS commands.
    
    No more mocks! This is the real deal.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize with real executor"""
        # Use provided config or create default
        self.config = config or Config()
        
        # Initialize the REAL performance improvements
        # Enhanced cache with fuzzy matching and background warming
        try:
            self.cache = get_enhanced_cache() if CACHE_AVAILABLE else None
        except:
            # Fall back to fast cache if enhanced not available
            self.cache = get_fast_cache() if CACHE_AVAILABLE else None
        
        # Cache management commands
        self.cache_commands = get_cache_commands() if CACHE_COMMANDS_AVAILABLE else None
        
        # Package index for full searches (optional, takes long to build)
        self.package_index = get_package_index() if INDEX_AVAILABLE else None
        
        # Try to use native API (doesn't actually work yet)
        self.native_api = get_native_api() if NATIVE_API_AVAILABLE else None
        
        # Create real executor with config settings (fallback for when native API not available)
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
        if self.native_api:
            # Use subprocess (standard speed)
            self.system_info = {"native_api": True, "performance": "standard speed"}
        else:
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
        elif "cache" in intent.raw_text.lower() and self.cache_commands:
            # Handle cache management commands
            return self.cache_commands.handle_cache_command(intent)
        else:
            return Response(
                success=False,
                text=f"Intent type {intent.type} not yet implemented in real backend"
            )
    
    def _handle_search(self, intent: Intent) -> Response:
        """Handle package search with REAL performance improvements"""
        query = intent.entities.get("package", "") or intent.raw_text or ""
        
        if not query or query.lower() in ["packages", "package", ""]:
            return Response(
                success=False,
                text="Please specify what to search for. Example: 'search firefox'"
            )
        
        # Try the REAL fast path first - enhanced cache with fuzzy matching
        if self.cache:
            try:
                # This actually works and is fast with fuzzy matching!
                if hasattr(self.cache, 'fuzzy_search'):
                    packages, elapsed_ms, match_type = self.cache.fuzzy_search(query, limit=30)
                    from_cache = match_type != "none"
                else:
                    # Fall back to regular search
                    packages, elapsed_ms, from_cache = self.cache.search(query, limit=30)
                    match_type = "exact" if from_cache else "none"
                
                if packages:
                    results = []
                    for pkg in packages:
                        results.append({
                            "name": pkg["name"],
                            "description": pkg.get("description", pkg.get("desc", "")),
                            "version": pkg.get("version", ""),
                            "source": pkg.get("source", "cache")
                        })
                    
                    # Check if this was a fuzzy match with correction
                    if packages and "_suggested" in packages[0]:
                        suggested = packages[0]["_suggested"]
                        original = packages[0]["_original_query"]
                        title = f"🔍 Search results for '{suggested}' (corrected from '{original}')"
                    else:
                        title = f"🔍 Search results for '{query}'"
                    
                    # Show packages in beautiful table
                    show_packages(results, title=title)
                    
                    # Show real performance and match type
                    if hasattr(self.cache, 'fuzzy_search'):
                        if match_type == "fuzzy":
                            perf_note = f" (fuzzy match, {elapsed_ms:.0f}ms)"
                        elif match_type == "alias":
                            perf_note = f" (alias match, {elapsed_ms:.0f}ms)"
                        elif from_cache:
                            perf_note = f" (cached, {elapsed_ms:.0f}ms)"
                        else:
                            perf_note = f" ({elapsed_ms:.0f}ms)"
                    else:
                        if from_cache:
                            perf_note = f" (cached, {elapsed_ms:.0f}ms)"
                        else:
                            perf_note = f" ({elapsed_ms:.0f}ms)"
                    
                    message = f"Found {len(results)} packages for '{query}'{perf_note}"
                    
                    return Response(
                        success=True,
                        text=message,
                        data={
                            "query": query, 
                            "results": results, 
                            "cached_search": from_cache,
                            "search_time_ms": elapsed_ms
                        }
                    )
            except Exception as e:
                # Cache search failed, fall back to other methods
                import traceback
                print(f"Cache search failed: {e}")
                traceback.print_exc()
        
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
            if self.native_api:
                # Use native API for standard speed search (2-3 seconds vs 2000-5000ms!)
                try:
                    packages, elapsed_ms = self.native_api.search_packages(query)
                    for pkg in packages[:10]:  # Only first 10
                        results.append({
                            "name": pkg.get("name", ""),
                            "description": pkg.get("description", ""),
                            "version": pkg.get("version", "")
                        })
                except Exception as e:
                    # Fallback if native API fails
                    results = [{"name": f"Try: nix-env -qa '*{query}*'", "description": "Run this command for full results"}]
            else:
                # Fallback to subprocess only if native API not available
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
        
        # Real installation using correct command for profile type
        install_cmd = profile_migrator.get_correct_command("install", package)
        if install_cmd:
            if install_cmd[0] == "nix":
                result = self.executor.execute(install_cmd[0], install_cmd[1:])
            else:
                result = self.executor.execute(install_cmd[0], install_cmd[1:])
        else:
            # Fallback
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
        
        # Real removal using correct command for profile type
        remove_cmd = profile_migrator.get_correct_command("remove", package)
        if remove_cmd and remove_cmd[0] == "nix" and "profile" in remove_cmd:
            # For nix profile, we need to find the package number first
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
        elif remove_cmd:
            # Use nix-env command
            result = self.executor.execute(remove_cmd[0], remove_cmd[1:])
        else:
            # Fallback
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
        """Handle info request with proper timeout handling"""
        import subprocess
        package = intent.entities.get("package", "")
        
        if package:
            # Try quick search first (faster than nix-env -qa)
            try:
                # Use nix search which is generally faster
                result = subprocess.run(
                    ["nix", "search", "nixpkgs", f"^{package}$"],
                    capture_output=True,
                    text=True,
                    timeout=5  # 5 second timeout
                )
                
                if result.returncode == 0 and result.stdout:
                    # Parse the search output for better formatting
                    lines = result.stdout.strip().split("\n")
                    if lines:
                        # Extract key info from search output
                        info_text = f"Package: {package}\n"
                        for line in lines:
                            if "Description:" in line:
                                info_text += line.strip() + "\n"
                            elif package in line.lower():
                                info_text += line.strip() + "\n"
                        
                        return Response(
                            success=True,
                            text=f"Package info for '{package}':\n{info_text}"
                        )
                
                # If exact match fails, try partial match
                result = subprocess.run(
                    ["nix", "search", "nixpkgs", package],
                    capture_output=True,
                    text=True,
                    timeout=3  # Even shorter timeout for partial
                )
                
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split("\n")[:5]  # First 5 matches
                    return Response(
                        success=True,
                        text=f"Package info for '{package}':\n" + "\n".join(lines)
                    )
                    
                return Response(
                    success=False,
                    text=f"Package '{package}' not found. Try: search {package}"
                )
                
            except subprocess.TimeoutExpired:
                # Provide helpful fallback
                return Response(
                    success=True,
                    text=f"Package info lookup timed out.\n" +
                         f"Try these alternatives:\n" +
                         f"  • nix search nixpkgs {package}\n" +
                         f"  • Visit: https://search.nixos.org/packages?query={package}\n" +
                         f"  • Use: ask-nix 'search {package}' for quick results"
                )
            except Exception as e:
                return Response(
                    success=False,
                    text=f"Error getting package info: {str(e)}"
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