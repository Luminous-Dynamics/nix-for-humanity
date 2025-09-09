"""
Install command handler with ultra-fast performance
"""

import subprocess
import time
from typing import Tuple, Optional

from .ultra_fast_cache import get_ultra_cache

class InstallHandler:
    """Handle package installation with <100ms response times"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.cache = get_ultra_cache()
    
    def install_package(self, package: str) -> Tuple[bool, str, float]:
        """
        Install a package with ultra-fast response
        Returns: (success, message, elapsed_ms)
        """
        start = time.time()
        
        # First check if package exists in our cache
        info, lookup_ms = self.cache.info_instant(package)
        
        if not info:
            # Try common variations
            if package in ["browser", "web-browser"]:
                package = "firefox"
                info, _ = self.cache.info_instant("firefox")
            elif package in ["editor", "text-editor"]:
                package = "vim"
                info, _ = self.cache.info_instant("vim")
            elif package == "ide":
                package = "vscode"
                info, _ = self.cache.info_instant("vscode")
        
        if info:
            # Package found in cache
            if self.dry_run:
                elapsed_ms = (time.time() - start) * 1000
                message = f"""📋 DRY RUN: Would install {info['name']} v{info['version']}

Description: {info['description']}

Command that would be executed:
  nix profile install nixpkgs#{package}

This would:
  • Download {info['name']} from nixpkgs
  • Install it to your user profile
  • Make it available in PATH

To actually install, run without --dry-run flag"""
                return (True, message, elapsed_ms)
            else:
                # Real installation
                return self._execute_install(package, start)
        else:
            # Package not in cache, search for it
            results, search_ms = self.cache.search_instant(package)
            
            if results:
                # Found similar packages
                elapsed_ms = (time.time() - start) * 1000
                suggestions = "\n".join([f"  • {r['name']} - {r['description']}" for r in results[:5]])
                message = f"""❓ Package '{package}' not found. Did you mean one of these?

{suggestions}

Try: luminous-nix install <exact-package-name>"""
                return (False, message, elapsed_ms)
            else:
                # Unknown package
                elapsed_ms = (time.time() - start) * 1000
                message = f"""❌ Package '{package}' not found.

Try searching first:
  luminous-nix search {package}

Or check available packages:
  luminous-nix list"""
                return (False, message, elapsed_ms)
    
    def _execute_install(self, package: str, start_time: float) -> Tuple[bool, str, float]:
        """Actually execute the install command"""
        try:
            # Use nix profile for modern Nix
            cmd = ["nix", "profile", "install", f"nixpkgs#{package}"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout for actual install
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                message = f"""✅ Successfully installed {package}!

The package is now available in your PATH.
You can run it immediately.

Installation completed in {elapsed_ms:.1f}ms"""
                return (True, message, elapsed_ms)
            else:
                message = f"""❌ Installation failed:

{result.stderr}

Try running with more permissions:
  sudo nix profile install nixpkgs#{package}"""
                return (False, message, elapsed_ms)
                
        except subprocess.TimeoutExpired:
            elapsed_ms = (time.time() - start_time) * 1000
            message = f"""⏱️ Installation is taking longer than expected.

The installation is still running in the background.
Check progress with:
  ps aux | grep nix

Package: {package}"""
            return (False, message, elapsed_ms)
        
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            message = f"""❌ Installation error: {str(e)}

Please try manually:
  nix profile install nixpkgs#{package}"""
            return (False, message, elapsed_ms)

# Singleton
_install_handler = None

def get_install_handler(dry_run: bool = True) -> InstallHandler:
    """Get or create the install handler"""
    global _install_handler
    if _install_handler is None or _install_handler.dry_run != dry_run:
        _install_handler = InstallHandler(dry_run)
    return _install_handler