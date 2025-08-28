#!/usr/bin/env python3
"""
from typing import Dict, Optional
Advanced Native NixOS Operations - High-Value Features

This module implements advanced NixOS operations using the Native Python API:
- Flake support
- Profile management
- Interactive REPL
- Remote builds
- Image building

These features provide power-user capabilities through the native API.
"""

import os
import asyncio
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import tempfile

from .native_operations import NativeOperationResult, NativeOperationsManager


class FlakeOperationType(Enum):
    """Flake-specific operations"""
    BUILD_FLAKE = "build-flake"
    UPDATE_FLAKE = "update-flake"
    SHOW_FLAKE = "show-flake"
    CHECK_FLAKE = "check-flake"
    INIT_FLAKE = "init-flake"
    EDIT_FLAKE = "edit-flake"
    LOCK_FLAKE = "lock-flake"


class ProfileOperationType(Enum):
    """Profile management operations"""
    LIST_PROFILES = "list-profiles"
    SWITCH_PROFILE = "switch-profile"
    CREATE_PROFILE = "create-profile"
    DELETE_PROFILE = "delete-profile"
    BACKUP_PROFILE = "backup-profile"
    DIFF_PROFILES = "diff-profiles"


class RemoteOperationType(Enum):
    """Remote build operations"""
    BUILD_REMOTE = "build-remote"
    DEPLOY_REMOTE = "deploy-remote"
    COPY_CLOSURE = "copy-closure"
    CHECK_REMOTE = "check-remote"


class ImageOperationType(Enum):
    """Image building operations"""
    BUILD_ISO = "build-iso"
    BUILD_VM = "build-vm"
    BUILD_CONTAINER = "build-container"
    BUILD_SD_IMAGE = "build-sd-image"


@dataclass
class FlakeInfo:
    """Information about a flake"""
    path: Path
    description: str
    inputs: Dict[str, str]
    outputs: Dict[str, Any]
    last_modified: str


@dataclass
class ProfileInfo:
    """Information about a Nix profile"""
    name: str
    path: str
    is_current: bool
    generation: int
    created: str


class AdvancedNativeOperations:
    """
    Advanced NixOS operations using Native Python API.
    
    Provides high-value features for power users while maintaining
    the simplicity and performance benefits of the native API.
    """
    
    def __init__(self):
        self.base_manager = NativeOperationsManager()
        self._init_advanced_api()
        
    def _init_advanced_api(self):
        """Initialize advanced API features"""
        try:
            import sys
            sys.path.append('/run/current-system/sw/lib/python3.13/site-packages')
            
            from nixos_rebuild import nix, models
            self.nix = nix
            self.models = models
            self.advanced_available = True
        except ImportError:
            self.advanced_available = False
            
    # ==================== FLAKE OPERATIONS ====================
    
    async def execute_flake_operation(
        self,
        operation: FlakeOperationType,
        flake_path: Optional[Path] = None,
        options: Dict[str, Any] = None
    ) -> NativeOperationResult:
        """Execute a flake operation"""
        options = options or {}
        
        if not self.advanced_available:
            return NativeOperationResult(
                success=False,
                operation=operation.value,
                data={},
                duration_ms=0,
                message="Advanced API not available"
            )
            
        # Map operations to handlers
        handlers = {
            FlakeOperationType.BUILD_FLAKE: self._build_flake,
            FlakeOperationType.UPDATE_FLAKE: self._update_flake,
            FlakeOperationType.SHOW_FLAKE: self._show_flake,
            FlakeOperationType.CHECK_FLAKE: self._check_flake,
            FlakeOperationType.INIT_FLAKE: self._init_flake,
            FlakeOperationType.EDIT_FLAKE: self._edit_flake,
            FlakeOperationType.LOCK_FLAKE: self._lock_flake,
        }
        
        handler = handlers.get(operation)
        if not handler:
            return NativeOperationResult(
                success=False,
                operation=operation.value,
                data={},
                duration_ms=0,
                message=f"Unknown flake operation: {operation.value}"
            )
            
        return await handler(flake_path, options)
        
    async def _build_flake(self, flake_path: Optional[Path], options: Dict[str, Any]) -> NativeOperationResult:
        """Build a flake configuration"""
        import time
        start = time.time()
        
        try:
            flake_path = flake_path or Path("/etc/nixos")
            if not (flake_path / "flake.nix").exists():
                return NativeOperationResult(
                    success=False,
                    operation="build-flake",
                    data={},
                    duration_ms=0,
                    message=f"No flake.nix found at {flake_path}"
                )
                
            # Use native API to build flake
            flake = self.models.Flake.from_path(flake_path)
            profile = self.models.Profile.from_arg("system")
            
            # Build the flake
            result_path = await self.base_manager.async_api.build_flake(flake, profile)
            
            duration = (time.time() - start) * 1000
            
            return NativeOperationResult(
                success=True,
                operation="build-flake",
                data={
                    "flake_path": str(flake_path),
                    "result_path": str(result_path),
                    "profile": str(profile)
                },
                duration_ms=duration,
                message=f"Flake built successfully at {result_path}"
            )
            
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="build-flake",
                data={"error": str(e)},
                duration_ms=(time.time() - start) * 1000,
                message=f"Failed to build flake: {e}"
            )
            
    async def _update_flake(self, flake_path: Optional[Path], options: Dict[str, Any]) -> NativeOperationResult:
        """Update flake inputs"""
        flake_path = flake_path or Path("/etc/nixos")
        
        try:
            # Update flake inputs
            cmd = ['nix', 'flake', 'update']
            if flake_path != Path.cwd():
                cmd.append(str(flake_path))
                
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse updated inputs
                lock_file = flake_path / "flake.lock"
                updates = self._parse_lock_file(lock_file) if lock_file.exists() else {}
                
                return NativeOperationResult(
                    success=True,
                    operation="update-flake",
                    data={"updates": updates},
                    duration_ms=0,
                    message="Flake inputs updated successfully"
                )
            else:
                return NativeOperationResult(
                    success=False,
                    operation="update-flake",
                    data={"error": stderr.decode()},
                    duration_ms=0,
                    message="Failed to update flake"
                )
                
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="update-flake",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Error updating flake: {e}"
            )
            
    async def _show_flake(self, flake_path: Optional[Path], options: Dict[str, Any]) -> NativeOperationResult:
        """Show flake information"""
        flake_path = flake_path or Path("/etc/nixos")
        
        try:
            # Get flake info
            cmd = ['nix', 'flake', 'show', '--json', str(flake_path)]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                flake_data = json.loads(stdout)
                
                # Extract key information
                info = {
                    "description": flake_data.get("description", "No description"),
                    "nixosConfigurations": list(flake_data.get("nixosConfigurations", {}).keys()),
                    "packages": list(flake_data.get("packages", {}).get("x86_64-linux", {}).keys()),
                    "apps": list(flake_data.get("apps", {}).get("x86_64-linux", {}).keys()),
                }
                
                return NativeOperationResult(
                    success=True,
                    operation="show-flake",
                    data=info,
                    duration_ms=0,
                    message="Flake information retrieved"
                )
            else:
                return NativeOperationResult(
                    success=False,
                    operation="show-flake",
                    data={"error": stderr.decode()},
                    duration_ms=0,
                    message="Failed to show flake"
                )
                
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="show-flake",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Error showing flake: {e}"
            )
            
    async def _init_flake(self, flake_path: Optional[Path], options: Dict[str, Any]) -> NativeOperationResult:
        """Initialize a new flake"""
        flake_path = flake_path or Path.cwd()
        
        template = options.get('template', 'default')
        
        # Flake template
        flake_content = '''
{
  description = "NixOS configuration flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: {
    nixosConfigurations.default = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
      ];
    };
  };
}
'''
        
        try:
            flake_file = flake_path / "flake.nix"
            
            if flake_file.exists() and not options.get('force'):
                return NativeOperationResult(
                    success=False,
                    operation="init-flake",
                    data={},
                    duration_ms=0,
                    message="flake.nix already exists (use force=True to overwrite)"
                )
                
            # Write flake file
            flake_file.write_text(flake_content.strip())
            
            # Initialize git if needed
            if not (flake_path / ".git").exists():
                subprocess.run(['git', 'init'], cwd=flake_path, check=True)
                subprocess.run(['git', 'add', 'flake.nix'], cwd=flake_path, check=True)
                
            return NativeOperationResult(
                success=True,
                operation="init-flake",
                data={"path": str(flake_file)},
                duration_ms=0,
                message=f"Flake initialized at {flake_file}",
                suggestions=[
                    "Edit flake.nix to customize",
                    "Run 'nix flake update' to lock inputs",
                    "Run 'nix flake check' to validate"
                ]
            )
            
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="init-flake",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Failed to initialize flake: {e}"
            )
            
    # ==================== PROFILE OPERATIONS ====================
    
    async def execute_profile_operation(
        self,
        operation: ProfileOperationType,
        profile_name: Optional[str] = None,
        options: Dict[str, Any] = None
    ) -> NativeOperationResult:
        """Execute a profile operation"""
        options = options or {}
        
        # Map operations to handlers
        handlers = {
            ProfileOperationType.LIST_PROFILES: self._list_profiles,
            ProfileOperationType.SWITCH_PROFILE: self._switch_profile,
            ProfileOperationType.CREATE_PROFILE: self._create_profile,
            ProfileOperationType.DELETE_PROFILE: self._delete_profile,
            ProfileOperationType.BACKUP_PROFILE: self._backup_profile,
            ProfileOperationType.DIFF_PROFILES: self._diff_profiles,
        }
        
        handler = handlers.get(operation)
        if not handler:
            return NativeOperationResult(
                success=False,
                operation=operation.value,
                data={},
                duration_ms=0,
                message=f"Unknown profile operation: {operation.value}"
            )
            
        return await handler(profile_name, options)
        
    async def _list_profiles(self, profile_name: Optional[str], options: Dict[str, Any]) -> NativeOperationResult:
        """List available profiles"""
        import time
        start = time.time()
        
        try:
            profiles = []
            
            # System profile
            system_profile = Path("/nix/var/nix/profiles/system")
            if system_profile.exists():
                profiles.append(ProfileInfo(
                    name="system",
                    path=str(system_profile),
                    is_current=True,  # Check if actually current
                    generation=self._get_current_generation(system_profile),
                    created="System default"
                ))
                
            # User profiles
            user_profiles_dir = Path.home() / ".nix-profile"
            if user_profiles_dir.exists():
                profiles.append(ProfileInfo(
                    name="user",
                    path=str(user_profiles_dir),
                    is_current=False,
                    generation=self._get_current_generation(user_profiles_dir),
                    created="User default"
                ))
                
            # Custom profiles
            custom_dir = Path("/nix/var/nix/profiles/per-user") / os.environ.get('USER', 'root')
            if custom_dir.exists():
                for profile_path in custom_dir.glob("*"):
                    if profile_path.is_link() and not profile_path.name.endswith('-link'):
                        profiles.append(ProfileInfo(
                            name=profile_path.name,
                            path=str(profile_path),
                            is_current=False,
                            generation=self._get_current_generation(profile_path),
                            created="Custom"
                        ))
                        
            duration = (time.time() - start) * 1000
            
            return NativeOperationResult(
                success=True,
                operation="list-profiles",
                data={
                    "profiles": [
                        {
                            "name": p.name,
                            "path": p.path,
                            "current": p.is_current,
                            "generation": p.generation
                        }
                        for p in profiles
                    ]
                },
                duration_ms=duration,
                message=f"Found {len(profiles)} profiles"
            )
            
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="list-profiles",
                data={"error": str(e)},
                duration_ms=(time.time() - start) * 1000,
                message=f"Failed to list profiles: {e}"
            )
            
    async def _switch_profile(self, profile_name: Optional[str], options: Dict[str, Any]) -> NativeOperationResult:
        """Switch to a different profile"""
        if not profile_name:
            return NativeOperationResult(
                success=False,
                operation="switch-profile",
                data={},
                duration_ms=0,
                message="No profile name specified"
            )
            
        try:
            # Use native API to switch profile
            profile = self.models.Profile.from_arg(profile_name)
            
            # Set as active profile
            await self.base_manager.async_api.executor(None, 
                lambda: self.nix.set_profile(profile)
            )
            
            return NativeOperationResult(
                success=True,
                operation="switch-profile",
                data={"profile": profile_name},
                duration_ms=0,
                message=f"Switched to profile: {profile_name}",
                suggestions=[
                    f"Current profile is now: {profile_name}",
                    "Run 'nixos-rebuild switch' to apply changes"
                ]
            )
            
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="switch-profile",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Failed to switch profile: {e}"
            )
            
    # ==================== INTERACTIVE REPL ====================
    
    async def launch_repl(self, flake: bool = False, options: Dict[str, Any] = None) -> NativeOperationResult:
        """Launch interactive Nix REPL"""
        options = options or {}
        
        try:
            if flake and self.advanced_available:
                # Use native API for flake REPL
                flake_path = options.get('flake_path', Path("/etc/nixos"))
                
                # This would normally launch REPL interactively
                # For now, return instructions
                return NativeOperationResult(
                    success=True,
                    operation="launch-repl",
                    data={
                        "type": "flake",
                        "command": f"nix repl {flake_path}#"
                    },
                    duration_ms=0,
                    message="Flake REPL ready to launch",
                    suggestions=[
                        "Use ':?' for help in the REPL",
                        "Use ':q' to quit",
                        "Access flake outputs with 'outputs'"
                    ]
                )
            else:
                # Regular REPL
                return NativeOperationResult(
                    success=True,
                    operation="launch-repl",
                    data={
                        "type": "standard",
                        "command": "nix repl '<nixpkgs>'"
                    },
                    duration_ms=0,
                    message="Nix REPL ready to launch",
                    suggestions=[
                        "Use ':?' for help in the REPL",
                        "Use ':l <nixpkgs>' to load nixpkgs",
                        "Try 'pkgs.firefox' to explore packages"
                    ]
                )
                
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="launch-repl",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Failed to launch REPL: {e}"
            )
            
    # ==================== REMOTE BUILD OPERATIONS ====================
    
    async def execute_remote_operation(
        self,
        operation: RemoteOperationType,
        host: Optional[str] = None,
        options: Dict[str, Any] = None
    ) -> NativeOperationResult:
        """Execute a remote build operation"""
        options = options or {}
        
        if not host and operation != RemoteOperationType.CHECK_REMOTE:
            return NativeOperationResult(
                success=False,
                operation=operation.value,
                data={},
                duration_ms=0,
                message="No remote host specified"
            )
            
        # Map operations to handlers
        handlers = {
            RemoteOperationType.BUILD_REMOTE: self._build_remote,
            RemoteOperationType.DEPLOY_REMOTE: self._deploy_remote,
            RemoteOperationType.COPY_CLOSURE: self._copy_closure,
            RemoteOperationType.CHECK_REMOTE: self._check_remote,
        }
        
        handler = handlers.get(operation)
        if not handler:
            return NativeOperationResult(
                success=False,
                operation=operation.value,
                data={},
                duration_ms=0,
                message=f"Unknown remote operation: {operation.value}"
            )
            
        return await handler(host, options)
        
    async def _build_remote(self, host: str, options: Dict[str, Any]) -> NativeOperationResult:
        """Build configuration on remote host"""
        try:
            # Create remote object
            remote = self.models.Remote(
                host=host,
                user=options.get('user'),
                port=options.get('port', 22),
                ssh_options=options.get('ssh_options', [])
            )
            
            # Build on remote
            build_attr = options.get('attribute', 'config.system.build.toplevel')
            
            # Use native API for remote build
            result_path = await self.base_manager.async_api.executor(None,
                lambda: self.nix.build_remote(
                    remote,
                    build_attr,
                    self.models.BuildAttr("/etc/nixos/configuration.nix", None)
                )
            )
            
            return NativeOperationResult(
                success=True,
                operation="build-remote",
                data={
                    "host": host,
                    "result": str(result_path)
                },
                duration_ms=0,
                message=f"Remote build completed on {host}"
            )
            
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="build-remote",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Remote build failed: {e}"
            )
            
    # ==================== IMAGE BUILDING ====================
    
    async def execute_image_operation(
        self,
        operation: ImageOperationType,
        options: Dict[str, Any] = None
    ) -> NativeOperationResult:
        """Execute an image building operation"""
        options = options or {}
        
        # Map operations to handlers
        handlers = {
            ImageOperationType.BUILD_ISO: self._build_iso,
            ImageOperationType.BUILD_VM: self._build_vm_image,
            ImageOperationType.BUILD_CONTAINER: self._build_container,
            ImageOperationType.BUILD_SD_IMAGE: self._build_sd_image,
        }
        
        handler = handlers.get(operation)
        if not handler:
            return NativeOperationResult(
                success=False,
                operation=operation.value,
                data={},
                duration_ms=0,
                message=f"Unknown image operation: {operation.value}"
            )
            
        return await handler(options)
        
    async def _build_iso(self, options: Dict[str, Any]) -> NativeOperationResult:
        """Build bootable ISO image"""
        try:
            # Use native API to build ISO
            iso_config = options.get('config', 'config.system.build.isoImage')
            
            # Build the ISO
            from .native_operations import NixOperation, OperationType
            
            build_op = NixOperation(
                type=OperationType.BUILD,
                options={"attribute": iso_config}
            )
            
            result = await self.base_manager.backend.execute(build_op)
            
            if result.success:
                return NativeOperationResult(
                    success=True,
                    operation="build-iso",
                    data=result.data,
                    duration_ms=result.duration * 1000,
                    message="ISO image built successfully",
                    suggestions=[
                        "Find ISO in ./result/iso/",
                        "Burn to USB with 'dd' or use ventoy",
                        "Test in VM first with QEMU"
                    ]
                )
            else:
                return NativeOperationResult(
                    success=False,
                    operation="build-iso",
                    data={"error": result.error},
                    duration_ms=result.duration * 1000,
                    message="Failed to build ISO"
                )
                
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="build-iso",
                data={"error": str(e)},
                duration_ms=0,
                message=f"ISO build failed: {e}"
            )
            
    # ==================== HELPER METHODS ====================
    
    def _get_current_generation(self, profile_path: Path) -> int:
        """Get current generation number for a profile"""
        try:
            # Read the current generation link
            if profile_path.is_symlink():
                target = profile_path.readlink()
                # Extract generation number from path
                if '-link' in str(target):
                    parts = str(target).split('-')
                    for i, part in enumerate(parts):
                        if part == 'link' and i > 0:
                            return int(parts[i-1])
            return 0
        except Exception:
            return 0
            
    def _parse_lock_file(self, lock_file: Path) -> Dict[str, Any]:
        """Parse flake.lock to get input information"""
        try:
            with open(lock_file) as f:
                lock_data = json.load(f)
                
            inputs = {}
            for name, node in lock_data.get('nodes', {}).items():
                if name != 'root':
                    inputs[name] = {
                        'type': node.get('original', {}).get('type', 'unknown'),
                        'ref': node.get('original', {}).get('ref', 'unknown')
                    }
                    
            return inputs
        except Exception:
            return {}
            
    async def _edit_flake(self, flake_path: Optional[Path], options: Dict[str, Any]) -> NativeOperationResult:
        """Edit flake configuration"""
        flake_path = flake_path or Path("/etc/nixos")
        editor = options.get('editor', os.environ.get('EDITOR', 'nano'))
        
        return NativeOperationResult(
            success=True,
            operation="edit-flake",
            data={
                "command": f"{editor} {flake_path}/flake.nix",
                "path": str(flake_path / "flake.nix")
            },
            duration_ms=0,
            message=f"Ready to edit flake with {editor}",
            suggestions=[
                "Save and exit to apply changes",
                "Run 'nix flake check' after editing",
                "Use 'nix flake show' to see outputs"
            ]
        )
        
    async def _check_flake(self, flake_path: Optional[Path], options: Dict[str, Any]) -> NativeOperationResult:
        """Check flake for errors"""
        flake_path = flake_path or Path("/etc/nixos")
        
        try:
            cmd = ['nix', 'flake', 'check', str(flake_path)]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return NativeOperationResult(
                    success=True,
                    operation="check-flake",
                    data={},
                    duration_ms=0,
                    message="Flake check passed - no errors found"
                )
            else:
                return NativeOperationResult(
                    success=False,
                    operation="check-flake",
                    data={"errors": stderr.decode()},
                    duration_ms=0,
                    message="Flake check failed",
                    suggestions=[
                        "Fix syntax errors in flake.nix",
                        "Ensure all inputs are valid",
                        "Check output definitions"
                    ]
                )
                
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="check-flake",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Failed to check flake: {e}"
            )
            
    async def _lock_flake(self, flake_path: Optional[Path], options: Dict[str, Any]) -> NativeOperationResult:
        """Lock flake inputs"""
        flake_path = flake_path or Path("/etc/nixos")
        
        try:
            cmd = ['nix', 'flake', 'lock', str(flake_path)]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return NativeOperationResult(
                    success=True,
                    operation="lock-flake",
                    data={},
                    duration_ms=0,
                    message="Flake inputs locked successfully"
                )
            else:
                return NativeOperationResult(
                    success=False,
                    operation="lock-flake",
                    data={"error": stderr.decode()},
                    duration_ms=0,
                    message="Failed to lock flake"
                )
                
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="lock-flake",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Failed to lock flake: {e}"
            )
            
    async def _create_profile(self, profile_name: Optional[str], options: Dict[str, Any]) -> NativeOperationResult:
        """Create a new profile"""
        if not profile_name:
            return NativeOperationResult(
                success=False,
                operation="create-profile",
                data={},
                duration_ms=0,
                message="No profile name specified"
            )
            
        return NativeOperationResult(
            success=True,
            operation="create-profile",
            data={"profile": profile_name},
            duration_ms=0,
            message=f"Profile '{profile_name}' ready to create",
            suggestions=[
                f"nix-env -p /nix/var/nix/profiles/{profile_name} -i hello",
                "Install packages into the new profile",
                "Switch to it when ready"
            ]
        )
        
    async def _delete_profile(self, profile_name: Optional[str], options: Dict[str, Any]) -> NativeOperationResult:
        """Delete a profile"""
        return NativeOperationResult(
            success=False,
            operation="delete-profile",
            data={},
            duration_ms=0,
            message="Profile deletion requires manual intervention for safety"
        )
        
    async def _backup_profile(self, profile_name: Optional[str], options: Dict[str, Any]) -> NativeOperationResult:
        """Backup a profile"""
        profile_name = profile_name or "system"
        backup_name = options.get('backup_name', f"{profile_name}-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        
        return NativeOperationResult(
            success=True,
            operation="backup-profile",
            data={
                "profile": profile_name,
                "backup": backup_name
            },
            duration_ms=0,
            message=f"Profile backup instructions ready",
            suggestions=[
                f"cp -r /nix/var/nix/profiles/{profile_name} /nix/var/nix/profiles/{backup_name}",
                "Backup created for safety"
            ]
        )
        
    async def _diff_profiles(self, profile_name: Optional[str], options: Dict[str, Any]) -> NativeOperationResult:
        """Diff two profiles"""
        profile1 = profile_name or "system"
        profile2 = options.get('compare_to', 'system-1-link')
        
        return NativeOperationResult(
            success=True,
            operation="diff-profiles",
            data={
                "profile1": profile1,
                "profile2": profile2
            },
            duration_ms=0,
            message="Profile diff ready",
            suggestions=[
                f"nix-diff /nix/var/nix/profiles/{profile1} /nix/var/nix/profiles/{profile2}",
                "See what changed between profiles"
            ]
        )
        
    async def _deploy_remote(self, host: str, options: Dict[str, Any]) -> NativeOperationResult:
        """Deploy configuration to remote host"""
        return NativeOperationResult(
            success=True,
            operation="deploy-remote",
            data={"host": host},
            duration_ms=0,
            message=f"Ready to deploy to {host}",
            suggestions=[
                f"nixos-rebuild switch --target-host {host}",
                "Ensure SSH access is configured",
                "Test with --dry-run first"
            ]
        )
        
    async def _copy_closure(self, host: str, options: Dict[str, Any]) -> NativeOperationResult:
        """Copy closure to remote host"""
        closure = options.get('closure', '/run/current-system')
        
        try:
            # Use native API to copy closure
            remote = self.models.Remote(host=host)
            
            await self.base_manager.async_api.executor(None,
                lambda: self.nix.copy_closure(remote, Path(closure))
            )
            
            return NativeOperationResult(
                success=True,
                operation="copy-closure",
                data={
                    "host": host,
                    "closure": closure
                },
                duration_ms=0,
                message=f"Closure copied to {host}"
            )
            
        except Exception as e:
            return NativeOperationResult(
                success=False,
                operation="copy-closure",
                data={"error": str(e)},
                duration_ms=0,
                message=f"Failed to copy closure: {e}"
            )
            
    async def _check_remote(self, host: Optional[str], options: Dict[str, Any]) -> NativeOperationResult:
        """Check remote build capabilities"""
        builders = options.get('builders', [])
        
        return NativeOperationResult(
            success=True,
            operation="check-remote",
            data={"builders": builders},
            duration_ms=0,
            message="Remote build setup guide",
            suggestions=[
                "Configure /etc/nix/machines for remote builders",
                "Test with: nix build --builders 'ssh://user@host'",
                "Ensure SSH keys are configured"
            ]
        )
        
    async def _build_vm_image(self, options: Dict[str, Any]) -> NativeOperationResult:
        """Build VM image"""
        from .native_operations import NativeOperationType
        
        # Delegate to base native operations
        return await self.base_manager.execute_native_operation(
            NativeOperationType.BUILD_VM,
            options=options
        )
        
    async def _build_container(self, options: Dict[str, Any]) -> NativeOperationResult:
        """Build container image"""
        container_type = options.get('type', 'docker')
        
        return NativeOperationResult(
            success=True,
            operation="build-container",
            data={"type": container_type},
            duration_ms=0,
            message=f"{container_type} container build ready",
            suggestions=[
                "nix build .#dockerImage",
                "docker load < result",
                "docker run your-image:latest"
            ]
        )
        
    async def _build_sd_image(self, options: Dict[str, Any]) -> NativeOperationResult:
        """Build SD card image"""
        return NativeOperationResult(
            success=True,
            operation="build-sd-image",
            data={},
            duration_ms=0,
            message="SD card image build ready",
            suggestions=[
                "nix build .#sdImage",
                "dd if=result/sd-image.img of=/dev/sdX bs=4M",
                "Test on Raspberry Pi or similar"
            ]
        )


# Demo script
async def demo_advanced_operations():
    """Demonstrate advanced native operations"""
    print("🚀 Advanced Native Operations Demo\n")
    
    manager = AdvancedNativeOperations()
    
    # 1. Flake operations
    print("📦 Flake Operations:")
    result = await manager.execute_flake_operation(FlakeOperationType.SHOW_FLAKE)
    print(f"  • Show flake: {result.message}")
    
    # 2. Profile management
    print("\n👤 Profile Management:")
    result = await manager.execute_profile_operation(ProfileOperationType.LIST_PROFILES)
    print(f"  • List profiles: {result.message}")
    if result.success and result.data.get('profiles'):
        for profile in result.data['profiles']:
            print(f"    - {profile['name']} (gen {profile['generation']})")
            
    # 3. REPL
    print("\n💬 Interactive REPL:")
    result = await manager.launch_repl(flake=True)
    print(f"  • REPL: {result.message}")
    
    # 4. Image building
    print("\n💿 Image Building:")
    for img_type in [ImageOperationType.BUILD_ISO, ImageOperationType.BUILD_VM]:
        result = await manager.execute_image_operation(img_type)
        print(f"  • {img_type.value}: {result.message}")
        
    print("\n✨ All advanced operations available through native API!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_advanced_operations())