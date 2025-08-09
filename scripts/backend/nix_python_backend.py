#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
🐍 Nix Python Backend - Direct NixOS API Integration
The foundation of speed and reliability for Nix for Humanity
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Attempt to import nixos-rebuild-ng modules
def find_nixos_rebuild_module():
    """Locate nixos-rebuild-ng in nix store"""
    try:
        # Method 1: Use which to find nixos-rebuild
        result = subprocess.run(['which', 'nixos-rebuild'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            rebuild_path = Path(result.stdout.strip())
            # Follow symlinks to get real path
            real_path = rebuild_path.resolve()
            # Extract nix store path
            nix_package = str(real_path.parent.parent)
            
            # Try Python 3.13 first, then fallback
            for python_version in ['python3.13', 'python3.12', 'python3.11']:
                python_path = Path(nix_package) / 'lib' / python_version / 'site-packages'
                if python_path.exists():
                    return str(python_path)
    except Exception as e:
        print(f"⚠️  Error finding nixos-rebuild: {e}")
    
    # Method 2: Known path (fallback) - updated
    known_path = "/nix/store/lwmjrs31xfgn2q1a0b9f81a61ka4ym6z-nixos-rebuild-ng-0.0.0/lib/python3.13/site-packages"
    if Path(known_path).exists():
        return known_path
    
    return None

# Try to import nixos-rebuild modules
NIXOS_REBUILD_AVAILABLE = False
nixos_path = find_nixos_rebuild_module()
if nixos_path:
    sys.path.insert(0, nixos_path)
    try:
        from nixos_rebuild import models, nix, services
        from nixos_rebuild.models import Action, BuildAttr, Profile, Flake
        NIXOS_REBUILD_AVAILABLE = True
        print(f"✅ nixos-rebuild-ng API loaded from: {nixos_path}")
    except ImportError as e:
        print(f"⚠️  Could not import nixos-rebuild modules: {e}")


class OperationType(Enum):
    """Types of NixOS operations"""
    SWITCH = "switch"
    BOOT = "boot"
    TEST = "test"
    BUILD = "build"
    DRY_BUILD = "dry-build"
    ROLLBACK = "rollback"
    LIST_GENERATIONS = "list-generations"
    DELETE_GENERATIONS = "delete-generations"


@dataclass
class OperationResult:
    """Result of a NixOS operation"""
    success: bool
    operation: OperationType
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProgressCallback:
    """Handle progress updates for long operations"""
    
    def __init__(self, callback=None):
        self.callback = callback or self.default_callback
        self.start_time = time.time()
        
    def default_callback(self, message: str, progress: float):
        """Default progress printer"""
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:.1f}s] {progress*100:.0f}% - {message}")
    
    def __call__(self, message: str, progress: float = 0.0):
        self.callback(message, progress)


class NixPythonBackend:
    """
    Direct Python API integration with NixOS
    This is the speed and reliability foundation
    """
    
    def __init__(self, progress_callback=None):
        self.api_available = NIXOS_REBUILD_AVAILABLE
        self.progress = ProgressCallback(progress_callback)
        self.profile = self._get_system_profile()
        
    def _get_system_profile(self):
        """Get the system profile object"""
        if self.api_available:
            try:
                return Profile.from_arg("system")
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        return None
    
    def rebuild_system(self, 
                      operation: OperationType = OperationType.SWITCH,
                      flake: Optional[str] = None,
                      dry_run: bool = False) -> OperationResult:
        """
        Rebuild NixOS system using direct Python API
        
        This is the crown jewel - no subprocess, no timeouts!
        """
        start_time = time.time()
        
        if not self.api_available:
            return self._fallback_rebuild(operation, flake, dry_run)
        
        try:
            self.progress("Starting NixOS rebuild", 0.1)
            
            # Map our operation to nixos-rebuild Action
            action_map = {
                OperationType.SWITCH: Action.SWITCH,
                OperationType.BOOT: Action.BOOT,
                OperationType.TEST: Action.TEST,
                OperationType.BUILD: Action.BUILD,
                OperationType.DRY_BUILD: Action.DRY_BUILD,
            }
            
            if operation not in action_map:
                return OperationResult(
                    success=False,
                    operation=operation,
                    message=f"Operation {operation} not supported via API",
                    duration=time.time() - start_time,
                    error="Unsupported operation"
                )
            
            action = action_map[operation]
            
            # Build the system
            self.progress("Building system configuration", 0.3)
            
            if flake:
                # Flake-based build
                flake_obj = Flake.from_arg(flake)
                build_attr = BuildAttr.from_arg(flake_obj.attr or "nixosConfigurations.$(hostname)")
                path = nix.build_flake(build_attr, flake_obj)
            else:
                # Traditional build
                build_attr = BuildAttr.from_arg("config.system.build.toplevel")
                path = nix.build(build_attr)
            
            self.progress("Applying configuration", 0.7)
            
            # Apply the configuration
            if action in [Action.SWITCH, Action.BOOT, Action.TEST]:
                nix.switch_to_configuration(path, action, self.profile)
            
            self.progress("Rebuild complete", 1.0)
            
            duration = time.time() - start_time
            return OperationResult(
                success=True,
                operation=operation,
                message=f"Successfully performed {operation.value}",
                duration=duration,
                details={
                    'build_path': str(path),
                    'profile': str(self.profile),
                    'api_used': True
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Rebuild failed: {str(e)}",
                duration=duration,
                error=str(e)
            )
    
    def rollback(self, generation: Optional[int] = None) -> OperationResult:
        """Rollback to previous generation using API"""
        start_time = time.time()
        
        if not self.api_available:
            return self._fallback_rollback(generation)
        
        try:
            self.progress("Rolling back system", 0.5)
            
            if generation is None:
                # Roll back to previous
                nix.rollback(self.profile)
                message = "Rolled back to previous generation"
            else:
                # Roll back to specific generation
                nix.switch_generation(self.profile, generation)
                message = f"Switched to generation {generation}"
            
            self.progress("Rollback complete", 1.0)
            
            return OperationResult(
                success=True,
                operation=OperationType.ROLLBACK,
                message=message,
                duration=time.time() - start_time,
                details={'api_used': True}
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                operation=OperationType.ROLLBACK,
                message=f"Rollback failed: {str(e)}",
                duration=time.time() - start_time,
                error=str(e)
            )
    
    def list_generations(self) -> OperationResult:
        """List system generations"""
        start_time = time.time()
        
        try:
            # This works even without the API
            result = subprocess.run(
                ['sudo', 'nix-env', '--list-generations', 
                 '--profile', '/nix/var/nix/profiles/system'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                generations = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 3:
                            generations.append({
                                'number': int(parts[0]),
                                'date': ' '.join(parts[1:3]),
                                'current': '(current)' in line
                            })
                
                return OperationResult(
                    success=True,
                    operation=OperationType.LIST_GENERATIONS,
                    message=f"Found {len(generations)} generations",
                    duration=time.time() - start_time,
                    details={'generations': generations}
                )
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            return OperationResult(
                success=False,
                operation=OperationType.LIST_GENERATIONS,
                message=f"Failed to list generations: {str(e)}",
                duration=time.time() - start_time,
                error=str(e)
            )
    
    def install_package(self, package: str, user: bool = True) -> OperationResult:
        """
        Install a package using nix profile (modern approach)
        
        Note: For system packages, rebuild is preferred
        """
        start_time = time.time()
        
        try:
            self.progress(f"Installing {package}", 0.3)
            
            if user:
                # User installation with nix profile
                cmd = ['nix', 'profile', 'install', f'nixpkgs#{package}']
            else:
                # System installation requires configuration edit
                return OperationResult(
                    success=False,
                    operation=OperationType.BUILD,
                    message="System packages should be added to configuration.nix",
                    duration=time.time() - start_time,
                    details={
                        'suggestion': f'Add to environment.systemPackages: pkgs.{package}',
                        'file': '/etc/nixos/configuration.nix'
                    }
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.progress(f"Installed {package}", 1.0)
                return OperationResult(
                    success=True,
                    operation=OperationType.BUILD,
                    message=f"Successfully installed {package}",
                    duration=time.time() - start_time,
                    details={'method': 'nix profile'}
                )
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            return OperationResult(
                success=False,
                operation=OperationType.BUILD,
                message=f"Failed to install {package}: {str(e)}",
                duration=time.time() - start_time,
                error=str(e)
            )
    
    def search_packages(self, query: str) -> List[Dict[str, str]]:
        """Search for packages using nix search"""
        try:
            result = subprocess.run(
                ['nix', 'search', 'nixpkgs', query, '--json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                packages = []
                for key, info in data.items():
                    # Extract package name from flake reference
                    name = key.split('.')[-1]
                    packages.append({
                        'name': name,
                        'version': info.get('version', 'unknown'),
                        'description': info.get('description', '')
                    })
                return packages[:10]  # Limit to 10 results
            
        except Exception as e:
            print(f"Search error: {e}")
        
        return []
    
    def _fallback_rebuild(self, operation: OperationType, flake: Optional[str], 
                         dry_run: bool) -> OperationResult:
        """Fallback to subprocess when API not available"""
        start_time = time.time()
        
        try:
            cmd = ['sudo', 'nixos-rebuild', operation.value]
            if dry_run:
                cmd.append('--dry-run')
            if flake:
                cmd.extend(['--flake', flake])
            
            # Run in background to avoid timeout
            log_file = Path("/tmp/nixos-rebuild-fallback.log")
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT
                )
            
            # Give immediate response
            return OperationResult(
                success=True,
                operation=operation,
                message=f"Rebuild started in background. Check {log_file} for progress",
                duration=time.time() - start_time,
                details={
                    'api_used': False,
                    'log_file': str(log_file),
                    'pid': process.pid
                }
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                operation=operation,
                message=f"Failed to start rebuild: {str(e)}",
                duration=time.time() - start_time,
                error=str(e)
            )
    
    def _fallback_rollback(self, generation: Optional[int]) -> OperationResult:
        """Fallback rollback using subprocess"""
        start_time = time.time()
        
        try:
            if generation is None:
                cmd = ['sudo', 'nixos-rebuild', 'switch', '--rollback']
            else:
                # Switch to specific generation
                cmd = ['sudo', 'nix-env', '--switch-generation', str(generation),
                       '--profile', '/nix/var/nix/profiles/system']
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return OperationResult(
                    success=True,
                    operation=OperationType.ROLLBACK,
                    message="Rollback successful",
                    duration=time.time() - start_time,
                    details={'api_used': False}
                )
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            return OperationResult(
                success=False,
                operation=OperationType.ROLLBACK,
                message=f"Rollback failed: {str(e)}",
                duration=time.time() - start_time,
                error=str(e)
            )


def demonstrate_backend():
    """Demonstrate the Python backend capabilities"""
    print("🐍 Nix Python Backend Demonstration")
    print("=" * 60)
    
    def progress_printer(msg, progress):
        bar_length = 40
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r[{bar}] {progress*100:.0f}% - {msg}", end='', flush=True)
        if progress >= 1.0:
            print()  # New line when complete
    
    backend = NixPythonBackend(progress_callback=progress_printer)
    
    print(f"\n📊 Backend Status:")
    print(f"  API Available: {backend.api_available}")
    print(f"  Profile: {backend.profile}")
    
    # Demonstrate operations
    print("\n🔍 Searching for packages:")
    packages = backend.search_packages("firefox")
    for pkg in packages[:3]:
        print(f"  - {pkg['name']} ({pkg['version']}): {pkg['description'][:50]}...")
    
    print("\n📋 Listing generations:")
    result = backend.list_generations()
    if result.success:
        gens = result.details['generations']
        for gen in gens[-3:]:  # Show last 3
            current = " [CURRENT]" if gen['current'] else ""
            print(f"  - Generation {gen['number']} ({gen['date']}){current}")
    
    print("\n✨ Backend ready for integration!")


if __name__ == "__main__":
    demonstrate_backend()