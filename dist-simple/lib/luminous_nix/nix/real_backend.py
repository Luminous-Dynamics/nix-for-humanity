#!/usr/bin/env python3
"""
Real NixOS Backend - Actually interacts with NixOS!
No mocks, no fakes - this is the real thing.
"""

import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RealNixBackend:
    """Real NixOS backend that actually runs commands."""
    
    def __init__(self, timeout: int = 30, dry_run: bool = False):
        """Initialize the real backend.
        
        Args:
            timeout: Command timeout in seconds
            dry_run: If True, preview commands without executing
        """
        self.timeout = timeout
        self.dry_run = dry_run or os.environ.get("LUMINOUS_DRY_RUN", "").lower() in ["true", "1", "yes"]
        self._package_cache = None
        
    def search_packages(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages using real nix-env.
        
        Args:
            query: Search query
            
        Returns:
            List of package dictionaries
        """
        try:
            # Use nix search for better results
            cmd = ["nix", "search", "nixpkgs", query, "--json"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse nix search JSON output
                packages_json = json.loads(result.stdout)
                packages = []
                
                for pkg_path, pkg_info in packages_json.items():
                    # Extract package name from path (e.g., "legacyPackages.x86_64-linux.firefox")
                    name = pkg_path.split(".")[-1]
                    packages.append({
                        "name": name,
                        "version": pkg_info.get("version", "unknown"),
                        "description": pkg_info.get("description", ""),
                        "pname": pkg_info.get("pname", name)
                    })
                
                return packages[:20]  # Limit results
                
            # Fallback to nix-env if nix search fails
            cmd = ["nix-env", "-qaP", f".*{query}.*"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                return self._parse_nix_env_output(result.stdout)
                
        except subprocess.TimeoutExpired:
            logger.warning(f"Search timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Search failed: {e}")
            
        return []
    
    def _parse_nix_env_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse nix-env -qaP output."""
        packages = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split(None, 1)
                if len(parts) >= 1:
                    attr_path = parts[0]
                    name = attr_path.split('.')[-1]
                    # Try to extract version from name
                    version_match = re.search(r'-(\d+[\d.]+)', name)
                    version = version_match.group(1) if version_match else "unknown"
                    
                    packages.append({
                        "name": name,
                        "version": version,
                        "attr_path": attr_path,
                        "description": ""
                    })
        
        return packages[:20]  # Limit results
    
    def install_package(self, package: str, channel: str = "nixpkgs") -> Tuple[bool, str]:
        """Install a package using nix-env.
        
        Args:
            package: Package name to install
            channel: Nix channel to use
            
        Returns:
            Tuple of (success, message)
        """
        if self.dry_run:
            return True, f"[DRY RUN] Would install: {package}"
        
        try:
            # Try modern nix profile first
            cmd = ["nix", "profile", "install", f"{channel}#{package}"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout * 2  # Installation can take longer
            )
            
            if result.returncode == 0:
                return True, f"Successfully installed {package}"
            
            # Fallback to nix-env
            cmd = ["nix-env", "-iA", f"{channel}.{package}"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout * 2
            )
            
            if result.returncode == 0:
                return True, f"Successfully installed {package}"
            else:
                error_msg = result.stderr or result.stdout
                # Check for common errors
                if "attribute" in error_msg and "not found" in error_msg:
                    return False, f"Package '{package}' not found. Try searching first."
                return False, f"Installation failed: {error_msg[:200]}"
                
        except subprocess.TimeoutExpired:
            return False, f"Installation timed out after {self.timeout * 2}s"
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def remove_package(self, package: str) -> Tuple[bool, str]:
        """Remove a package using nix-env.
        
        Args:
            package: Package name to remove
            
        Returns:
            Tuple of (success, message)
        """
        if self.dry_run:
            return True, f"[DRY RUN] Would remove: {package}"
        
        try:
            # Try modern nix profile first
            cmd = ["nix", "profile", "remove", package]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                return True, f"Successfully removed {package}"
            
            # Fallback to nix-env
            cmd = ["nix-env", "-e", package]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                return True, f"Successfully removed {package}"
            else:
                error_msg = result.stderr or result.stdout
                return False, f"Removal failed: {error_msg[:200]}"
                
        except subprocess.TimeoutExpired:
            return False, f"Removal timed out after {self.timeout}s"
        except Exception as e:
            return False, f"Removal error: {str(e)}"
    
    def list_installed(self) -> List[Dict[str, Any]]:
        """List installed packages using real nix-env.
        
        Returns:
            List of installed package dictionaries
        """
        try:
            # Try modern nix profile first
            cmd = ["nix", "profile", "list", "--json"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0 and result.stdout:
                profile_data = json.loads(result.stdout)
                packages = []
                for item in profile_data.get("elements", {}).values():
                    if "attrPath" in item:
                        name = item["attrPath"].split(".")[-1]
                        packages.append({
                            "name": name,
                            "version": item.get("version", "unknown"),
                            "store_path": item.get("storePaths", [""])[0]
                        })
                return packages
            
            # Fallback to nix-env
            cmd = ["nix-env", "-q", "--installed"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                packages = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        # Parse package-version format
                        match = re.match(r'^(.+?)-(\d[\d.]*)$', line)
                        if match:
                            packages.append({
                                "name": match.group(1),
                                "version": match.group(2)
                            })
                        else:
                            packages.append({
                                "name": line,
                                "version": "unknown"
                            })
                return packages
                
        except subprocess.TimeoutExpired:
            logger.warning(f"List command timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"List failed: {e}")
            
        return []
    
    def get_package_info(self, package: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a package.
        
        Args:
            package: Package name
            
        Returns:
            Package information dictionary or None
        """
        try:
            # Use nix eval to get package info
            cmd = ["nix", "eval", "--json", f"nixpkgs#{package}.meta"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0 and result.stdout:
                meta = json.loads(result.stdout)
                return {
                    "name": package,
                    "description": meta.get("description", ""),
                    "homepage": meta.get("homepage", ""),
                    "license": str(meta.get("license", {}).get("fullName", "unknown")),
                    "maintainers": [m.get("name", "") for m in meta.get("maintainers", [])]
                }
                
        except Exception as e:
            logger.debug(f"Could not get package info: {e}")
            
        # Fallback to basic search
        packages = self.search_packages(package)
        for pkg in packages:
            if pkg["name"] == package:
                return pkg
                
        return None
    
    def update_system(self) -> Tuple[bool, str]:
        """Update the system using nixos-rebuild or nix-channel.
        
        Returns:
            Tuple of (success, message)
        """
        if self.dry_run:
            return True, "[DRY RUN] Would update system"
        
        try:
            # Check if we're on NixOS
            if Path("/etc/nixos/configuration.nix").exists():
                # NixOS system - use nixos-rebuild
                cmd = ["sudo", "nixos-rebuild", "switch"]
                # Note: This will likely timeout, but we start it
                result = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return True, "System update started in background. Check system logs for progress."
            else:
                # Non-NixOS - update channels
                cmd = ["nix-channel", "--update"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout * 2
                )
                
                if result.returncode == 0:
                    return True, "Successfully updated nix channels"
                else:
                    return False, f"Update failed: {result.stderr[:200]}"
                    
        except subprocess.TimeoutExpired:
            return True, "Update started but taking longer than expected. Check system logs."
        except Exception as e:
            return False, f"Update error: {str(e)}"
    
    def garbage_collect(self) -> Tuple[bool, str]:
        """Run nix garbage collection.
        
        Returns:
            Tuple of (success, message)
        """
        if self.dry_run:
            return True, "[DRY RUN] Would run garbage collection"
        
        try:
            cmd = ["nix-collect-garbage", "-d"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout * 2
            )
            
            if result.returncode == 0:
                # Parse freed space from output
                output = result.stdout
                freed_match = re.search(r'(\d+(?:\.\d+)?)\s*(MiB|GiB|KiB)', output)
                if freed_match:
                    freed = f"{freed_match.group(1)} {freed_match.group(2)}"
                    return True, f"Garbage collection complete. Freed {freed}"
                return True, "Garbage collection complete"
            else:
                return False, f"Garbage collection failed: {result.stderr[:200]}"
                
        except subprocess.TimeoutExpired:
            return False, f"Garbage collection timed out after {self.timeout * 2}s"
        except Exception as e:
            return False, f"Garbage collection error: {str(e)}"
    
    def validate_config(self, config_path: str) -> Tuple[bool, str]:
        """Validate a NixOS configuration file.
        
        Args:
            config_path: Path to configuration.nix
            
        Returns:
            Tuple of (valid, message)
        """
        try:
            # Use nixos-rebuild dry-build to validate
            cmd = ["nixos-rebuild", "dry-build", "-I", f"nixos-config={config_path}"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                return True, "Configuration is valid"
            else:
                error = result.stderr or result.stdout
                # Extract useful error message
                error_lines = error.split('\n')
                for line in error_lines:
                    if "error:" in line.lower():
                        return False, f"Invalid configuration: {line}"
                return False, f"Invalid configuration: {error[:200]}"
                
        except subprocess.TimeoutExpired:
            return False, "Validation timed out - configuration may be too complex"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def build_package_cache(self) -> bool:
        """Build a cache of available packages.
        
        Returns:
            True if cache was built successfully
        """
        try:
            logger.info("Building package cache (this may take a minute)...")
            
            # Get all packages with JSON output
            cmd = ["nix-env", "-qaP", "--json"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # Give more time for full package list
            )
            
            if result.returncode == 0 and result.stdout:
                self._package_cache = json.loads(result.stdout)
                logger.info(f"Cached {len(self._package_cache)} packages")
                return True
                
        except subprocess.TimeoutExpired:
            logger.warning("Package cache build timed out")
        except Exception as e:
            logger.error(f"Failed to build package cache: {e}")
            
        return False


# Singleton instance for reuse
_backend_instance = None

def get_backend(timeout: int = 30, dry_run: bool = False) -> RealNixBackend:
    """Get or create the singleton backend instance.
    
    Args:
        timeout: Command timeout in seconds
        dry_run: If True, preview commands without executing
        
    Returns:
        RealNixBackend instance
    """
    global _backend_instance
    if _backend_instance is None:
        _backend_instance = RealNixBackend(timeout=timeout, dry_run=dry_run)
    return _backend_instance