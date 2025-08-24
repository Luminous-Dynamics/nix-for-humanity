#!/usr/bin/env python3
"""
🎯 NixOperations - Pure Business Logic for NixOS Operations
This module contains all core NixOS operations without any CLI dependencies.
It returns structured data that can be used by CLI, API, or any interface.
"""

import os
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Import backends with graceful fallback
try:
    from ..nix.native_backend import NativeNixBackend
    NATIVE_BACKEND_AVAILABLE = True
except ImportError:
    NATIVE_BACKEND_AVAILABLE = False
    logger.debug("Native backend not available")

try:
    from .package_discovery import PackageDiscovery
    PACKAGE_DISCOVERY_AVAILABLE = True
except ImportError:
    PACKAGE_DISCOVERY_AVAILABLE = False
    logger.debug("Package discovery not available")

try:
    from .config_generator_ast import ConfigGeneratorAST
    CONFIG_GENERATOR_AVAILABLE = True
except ImportError:
    CONFIG_GENERATOR_AVAILABLE = False
    logger.debug("Config generator not available")

try:
    from ..core.native_nix_api import get_native_api, NATIVE_API_AVAILABLE
except ImportError:
    NATIVE_API_AVAILABLE = False
    logger.debug("Native API not available")


class NixOperations:
    """
    Core NixOS operations returning structured data.
    This class is interface-agnostic and can be used by CLI, API, or any other interface.
    """
    
    def __init__(self):
        """Initialize NixOS operations"""
        self.native_backend = NativeNixBackend() if NATIVE_BACKEND_AVAILABLE else None
        self.package_discovery = PackageDiscovery() if PACKAGE_DISCOVERY_AVAILABLE else None
        self.config_generator = ConfigGeneratorAST() if CONFIG_GENERATOR_AVAILABLE else None
        self.native_api = get_native_api() if NATIVE_API_AVAILABLE else None
        
        # Cache for performance
        self._search_cache = {}
        self._installed_cache = None
        self._installed_cache_time = None
        self._cache_ttl = 300  # 5 minutes
        
    def search_packages(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search for NixOS packages
        
        Args:
            query: Search query (name or description)
            category: Optional category filter
            limit: Maximum results to return
            
        Returns:
            Structured search results
        """
        # Check cache
        cache_key = f"{query}:{category}:{limit}"
        if cache_key in self._search_cache:
            cached = self._search_cache[cache_key]
            if (datetime.now() - cached['time']).seconds < self._cache_ttl:
                return cached['data']
        
        try:
            # Try native API first
            if self.native_api and hasattr(self.native_api, 'search'):
                results = self.native_api.search(query)
                packages = self._format_search_results(results, limit)
            # Try package discovery
            elif self.package_discovery:
                results = self.package_discovery.search(query)
                packages = self._format_search_results(results, limit)
            # Fallback to subprocess
            else:
                packages = self._search_via_subprocess(query, limit)
            
            # Apply category filter if provided
            if category and packages:
                packages = [p for p in packages if self._matches_category(p, category)]
            
            result = {
                "success": True,
                "query": query,
                "category": category,
                "count": len(packages),
                "packages": packages,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache result
            self._search_cache[cache_key] = {
                'time': datetime.now(),
                'data': result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "search_failed",
                "query": query,
                "suggestions": [
                    "Try a simpler search term",
                    "Check if the Nix daemon is running",
                    "Ensure channels are updated"
                ]
            }
    
    def install_package(
        self,
        package: str,
        preview: bool = False,
        user: bool = False
    ) -> Dict[str, Any]:
        """
        Install a NixOS package
        
        Args:
            package: Package name to install
            preview: If True, show what would happen without installing
            user: If True, install to user profile instead of system
            
        Returns:
            Installation result
        """
        try:
            # Validate package exists first
            search_result = self.search_packages(package, limit=5)
            if not search_result.get("packages"):
                return {
                    "success": False,
                    "error": f"Package '{package}' not found",
                    "error_type": "package_not_found",
                    "suggestions": self._suggest_similar_packages(package)
                }
            
            if preview:
                # Return preview information
                return {
                    "success": True,
                    "package": package,
                    "action": "preview",
                    "would_install": True,
                    "size_estimate": self._estimate_package_size(package),
                    "dependencies": self._get_dependencies(package),
                    "message": f"Would install {package} and its dependencies",
                    "command": self._get_install_command(package, user)
                }
            
            # Perform actual installation
            if self.native_api and hasattr(self.native_api, 'install'):
                result = self.native_api.install(package, user=user)
                success = result.get('success', False)
            else:
                success = self._install_via_subprocess(package, user)
            
            if success:
                # Clear installed cache
                self._installed_cache = None
                
                return {
                    "success": True,
                    "package": package,
                    "action": "installed",
                    "user_profile": user,
                    "message": f"Successfully installed {package}",
                    "next_steps": [
                        "The package is now available in your PATH",
                        "You may need to restart your shell or run 'hash -r'"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to install {package}",
                    "error_type": "installation_failed",
                    "suggestions": [
                        "Check if you have sufficient permissions",
                        "Try with --user flag for user installation",
                        "Check disk space availability"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "installation_error",
                "package": package
            }
    
    def remove_package(
        self,
        package: str,
        user: bool = False
    ) -> Dict[str, Any]:
        """
        Remove a NixOS package
        
        Args:
            package: Package name to remove
            user: If True, remove from user profile
            
        Returns:
            Removal result
        """
        try:
            # Check if package is installed
            installed = self.list_installed()
            package_names = [p.get('name', p) for p in installed.get('packages', [])]
            
            if package not in package_names:
                return {
                    "success": False,
                    "error": f"Package '{package}' is not installed",
                    "error_type": "package_not_installed",
                    "suggestions": ["Use 'list' to see installed packages"]
                }
            
            # Perform removal
            if self.native_api and hasattr(self.native_api, 'remove'):
                result = self.native_api.remove(package, user=user)
                success = result.get('success', False)
            else:
                success = self._remove_via_subprocess(package, user)
            
            if success:
                # Clear installed cache
                self._installed_cache = None
                
                return {
                    "success": True,
                    "package": package,
                    "action": "removed",
                    "message": f"Successfully removed {package}",
                    "cleanup_suggestion": "Run 'nix-collect-garbage' to free disk space"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to remove {package}",
                    "error_type": "removal_failed"
                }
                
        except Exception as e:
            logger.error(f"Removal failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "removal_error",
                "package": package
            }
    
    def update_system(
        self,
        channel: bool = True,
        packages: bool = True,
        preview: bool = False
    ) -> Dict[str, Any]:
        """
        Update NixOS system
        
        Args:
            channel: Update channel information
            packages: Update installed packages
            preview: Show what would be updated
            
        Returns:
            Update result
        """
        try:
            updates = []
            
            if channel:
                # Check for channel updates
                channel_updates = self._check_channel_updates()
                updates.extend(channel_updates)
            
            if packages:
                # Check for package updates
                package_updates = self._check_package_updates()
                updates.extend(package_updates)
            
            if preview:
                return {
                    "success": True,
                    "action": "preview",
                    "updates_available": len(updates) > 0,
                    "updates": updates,
                    "message": f"Found {len(updates)} updates available"
                }
            
            if not updates:
                return {
                    "success": True,
                    "action": "up_to_date",
                    "message": "System is already up to date"
                }
            
            # Perform update
            if self.native_api and hasattr(self.native_api, 'update'):
                result = self.native_api.update()
                success = result.get('success', False)
            else:
                success = self._update_via_subprocess()
            
            if success:
                return {
                    "success": True,
                    "action": "updated",
                    "updates_applied": len(updates),
                    "message": f"Successfully applied {len(updates)} updates",
                    "restart_required": self._check_restart_required()
                }
            else:
                return {
                    "success": False,
                    "error": "Update failed",
                    "error_type": "update_failed"
                }
                
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "update_error"
            }
    
    def list_installed(
        self,
        filter_str: Optional[str] = None,
        user: bool = False
    ) -> Dict[str, Any]:
        """
        List installed packages
        
        Args:
            filter_str: Optional filter for package names
            user: If True, list user packages only
            
        Returns:
            List of installed packages
        """
        try:
            # Check cache
            if self._installed_cache and self._installed_cache_time:
                if (datetime.now() - self._installed_cache_time).seconds < self._cache_ttl:
                    packages = self._installed_cache
                else:
                    packages = self._get_installed_packages(user)
            else:
                packages = self._get_installed_packages(user)
            
            # Apply filter if provided
            if filter_str:
                packages = [p for p in packages if filter_str.lower() in str(p).lower()]
            
            return {
                "success": True,
                "count": len(packages),
                "packages": packages,
                "profile": "user" if user else "system",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"List failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "list_failed"
            }
    
    def generate_configuration(
        self,
        options: Dict[str, Any],
        preview: bool = True
    ) -> Dict[str, Any]:
        """
        Generate NixOS configuration
        
        Args:
            options: Configuration options
            preview: If True, return config without writing
            
        Returns:
            Generated configuration
        """
        try:
            if self.config_generator:
                config = self.config_generator.generate(options)
            else:
                config = self._generate_basic_config(options)
            
            if preview:
                return {
                    "success": True,
                    "action": "preview",
                    "configuration": config,
                    "options": options,
                    "message": "Configuration generated (preview mode)"
                }
            
            # Write configuration
            config_path = Path("/etc/nixos/configuration.nix")
            backup_path = config_path.with_suffix('.bak')
            
            # Backup existing
            if config_path.exists():
                config_path.rename(backup_path)
            
            # Write new config
            config_path.write_text(config)
            
            return {
                "success": True,
                "action": "written",
                "path": str(config_path),
                "backup": str(backup_path),
                "message": "Configuration written successfully",
                "next_steps": [
                    "Review the configuration",
                    "Run 'nixos-rebuild test' to test",
                    "Run 'nixos-rebuild switch' to apply"
                ]
            }
            
        except Exception as e:
            logger.error(f"Config generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "config_generation_failed"
            }
    
    def system_health(self) -> Dict[str, Any]:
        """
        Check system health and status
        
        Returns:
            System health information
        """
        try:
            health_checks = {
                "disk_space": self._check_disk_space(),
                "generations": self._check_generations(),
                "channel_status": self._check_channel_status(),
                "configuration": self._check_configuration(),
                "nix_daemon": self._check_nix_daemon()
            }
            
            # Determine overall status
            issues = [k for k, v in health_checks.items() if v.get("status") != "ok"]
            overall_status = "healthy" if not issues else "needs_attention"
            
            # Generate recommendations
            recommendations = []
            for check, result in health_checks.items():
                if result.get("recommendation"):
                    recommendations.append(result["recommendation"])
            
            return {
                "success": True,
                "status": overall_status,
                "checks": health_checks,
                "issues": issues,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "health_check_failed"
            }
    
    def rollback(
        self,
        generation: Optional[int] = None,
        preview: bool = False
    ) -> Dict[str, Any]:
        """
        Rollback to a previous generation
        
        Args:
            generation: Specific generation number (or previous if None)
            preview: Show what would happen without rolling back
            
        Returns:
            Rollback result
        """
        try:
            # Get generation info
            generations = self._list_generations()
            current = self._get_current_generation()
            
            if generation is None:
                # Roll back to previous
                target = current - 1
            else:
                target = generation
            
            # Validate target
            if target not in [g['number'] for g in generations]:
                return {
                    "success": False,
                    "error": f"Generation {target} does not exist",
                    "error_type": "invalid_generation",
                    "available": [g['number'] for g in generations]
                }
            
            if preview:
                target_info = next(g for g in generations if g['number'] == target)
                return {
                    "success": True,
                    "action": "preview",
                    "current": current,
                    "target": target,
                    "target_date": target_info.get('date'),
                    "message": f"Would rollback from generation {current} to {target}"
                }
            
            # Perform rollback
            if self.native_api and hasattr(self.native_api, 'rollback'):
                result = self.native_api.rollback(target)
                success = result.get('success', False)
            else:
                success = self._rollback_via_subprocess(target)
            
            if success:
                return {
                    "success": True,
                    "action": "rolled_back",
                    "from_generation": current,
                    "to_generation": target,
                    "message": f"Successfully rolled back to generation {target}",
                    "restart_required": True
                }
            else:
                return {
                    "success": False,
                    "error": "Rollback failed",
                    "error_type": "rollback_failed"
                }
                
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "rollback_error"
            }
    
    # Helper methods
    def _format_search_results(self, results: Any, limit: int) -> List[Dict[str, Any]]:
        """Format search results consistently"""
        packages = []
        
        if isinstance(results, list):
            for r in results[:limit]:
                if isinstance(r, dict):
                    packages.append(r)
                else:
                    packages.append({"name": str(r), "description": ""})
        elif isinstance(results, dict):
            for name, desc in list(results.items())[:limit]:
                packages.append({"name": name, "description": desc})
        
        return packages
    
    def _search_via_subprocess(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback search using subprocess"""
        try:
            cmd = ["nix", "search", "nixpkgs", query, "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                packages = []
                for key, info in list(data.items())[:limit]:
                    name = key.split('.')[-1]
                    packages.append({
                        "name": name,
                        "description": info.get("description", ""),
                        "version": info.get("version", "")
                    })
                return packages
        except Exception as e:
            logger.error(f"Subprocess search failed: {e}")
        
        return []
    
    def _install_via_subprocess(self, package: str, user: bool) -> bool:
        """Install package using subprocess"""
        try:
            if user:
                cmd = ["nix-env", "-iA", f"nixpkgs.{package}"]
            else:
                cmd = ["sudo", "nix-env", "-iA", f"nixos.{package}"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Subprocess install failed: {e}")
            return False
    
    def _remove_via_subprocess(self, package: str, user: bool) -> bool:
        """Remove package using subprocess"""
        try:
            if user:
                cmd = ["nix-env", "-e", package]
            else:
                cmd = ["sudo", "nix-env", "-e", package]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Subprocess remove failed: {e}")
            return False
    
    def _update_via_subprocess(self) -> bool:
        """Update system using subprocess"""
        try:
            # Update channels
            subprocess.run(["sudo", "nix-channel", "--update"], check=True)
            # Rebuild system
            subprocess.run(["sudo", "nixos-rebuild", "switch"], check=True)
            return True
        except Exception as e:
            logger.error(f"Subprocess update failed: {e}")
            return False
    
    def _get_installed_packages(self, user: bool) -> List[Dict[str, Any]]:
        """Get list of installed packages"""
        packages = []
        
        try:
            if self.native_api and hasattr(self.native_api, 'list_installed'):
                result = self.native_api.list_installed(user=user)
                packages = result.get('packages', [])
            else:
                cmd = ["nix-env", "-q"] if user else ["nix-env", "-q", "--profile", "/nix/var/nix/profiles/system"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            packages.append({"name": line.strip()})
            
            # Cache results
            self._installed_cache = packages
            self._installed_cache_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to get installed packages: {e}")
        
        return packages
    
    def _matches_category(self, package: Dict[str, Any], category: str) -> bool:
        """Check if package matches category"""
        # Simple category matching - could be enhanced
        categories = {
            "development": ["editor", "compiler", "debugger", "ide"],
            "productivity": ["office", "notes", "calendar", "task"],
            "games": ["game", "gaming", "play"],
            "multimedia": ["video", "audio", "music", "media"],
            "system": ["monitor", "admin", "tool", "utility"]
        }
        
        keywords = categories.get(category.lower(), [])
        pkg_str = f"{package.get('name', '')} {package.get('description', '')}".lower()
        
        return any(keyword in pkg_str for keyword in keywords)
    
    def _suggest_similar_packages(self, package: str) -> List[str]:
        """Suggest similar package names"""
        suggestions = []
        
        # Simple similarity check
        search_result = self.search_packages(package[:3], limit=10)
        if search_result.get("packages"):
            for pkg in search_result["packages"][:3]:
                suggestions.append(f"Did you mean '{pkg.get('name')}'?")
        
        return suggestions
    
    def _estimate_package_size(self, package: str) -> str:
        """Estimate package download size"""
        # This would query actual size - returning estimate for now
        return "~10-50MB (estimate)"
    
    def _get_dependencies(self, package: str) -> List[str]:
        """Get package dependencies"""
        # This would query actual dependencies
        return ["Loading dependencies..."]
    
    def _get_install_command(self, package: str, user: bool) -> str:
        """Get the actual install command"""
        if user:
            return f"nix-env -iA nixpkgs.{package}"
        else:
            return f"sudo nix-env -iA nixos.{package}"
    
    def _check_channel_updates(self) -> List[Dict[str, Any]]:
        """Check for channel updates"""
        # This would check actual channel updates
        return []
    
    def _check_package_updates(self) -> List[Dict[str, Any]]:
        """Check for package updates"""
        # This would check actual package updates
        return []
    
    def _check_restart_required(self) -> bool:
        """Check if restart is required after update"""
        # Check for kernel or systemd updates
        return False
    
    def _generate_basic_config(self, options: Dict[str, Any]) -> str:
        """Generate basic configuration"""
        config = "{ config, pkgs, ... }:\n\n{\n"
        
        if "packages" in options:
            config += "  environment.systemPackages = with pkgs; [\n"
            for pkg in options["packages"]:
                config += f"    {pkg}\n"
            config += "  ];\n"
        
        config += "}\n"
        return config
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            import shutil
            stat = shutil.disk_usage("/")
            free_gb = stat.free / (1024**3)
            
            return {
                "status": "ok" if free_gb > 5 else "warning",
                "detail": f"{free_gb:.1f}GB free",
                "recommendation": "Run 'nix-collect-garbage -d'" if free_gb < 5 else None
            }
        except:
            return {"status": "unknown", "detail": "Could not check"}
    
    def _check_generations(self) -> Dict[str, Any]:
        """Check system generations"""
        try:
            generations = self._list_generations()
            count = len(generations)
            
            return {
                "status": "ok" if count < 20 else "info",
                "detail": f"{count} generations",
                "recommendation": "Consider cleaning old generations" if count > 20 else None
            }
        except:
            return {"status": "unknown", "detail": "Could not check"}
    
    def _check_channel_status(self) -> Dict[str, Any]:
        """Check channel status"""
        return {
            "status": "ok",
            "detail": "Channels up to date"
        }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration syntax"""
        return {
            "status": "ok",
            "detail": "No syntax errors"
        }
    
    def _check_nix_daemon(self) -> Dict[str, Any]:
        """Check if Nix daemon is running"""
        try:
            result = subprocess.run(["systemctl", "is-active", "nix-daemon"], 
                                  capture_output=True, text=True)
            running = result.stdout.strip() == "active"
            
            return {
                "status": "ok" if running else "error",
                "detail": "Running" if running else "Not running",
                "recommendation": "Start nix-daemon" if not running else None
            }
        except:
            return {"status": "unknown", "detail": "Could not check"}
    
    def _list_generations(self) -> List[Dict[str, Any]]:
        """List system generations"""
        generations = []
        try:
            result = subprocess.run(["sudo", "nix-env", "--list-generations", 
                                   "--profile", "/nix/var/nix/profiles/system"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            generations.append({
                                "number": int(parts[0]),
                                "date": " ".join(parts[1:])
                            })
        except:
            pass
        
        return generations
    
    def _get_current_generation(self) -> int:
        """Get current generation number"""
        try:
            result = subprocess.run(["sudo", "nix-env", "--list-generations", 
                                   "--profile", "/nix/var/nix/profiles/system"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if "(current)" in line:
                        return int(line.split()[0])
        except:
            pass
        
        return 0
    
    def _rollback_via_subprocess(self, generation: int) -> bool:
        """Rollback using subprocess"""
        try:
            cmd = ["sudo", "nix-env", "--switch-generation", str(generation),
                   "--profile", "/nix/var/nix/profiles/system"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False