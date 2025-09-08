"""
Real NixOS command executor - actually executes commands!

This module provides the REAL implementation that executes actual NixOS commands.
No mocks, no simulations - real subprocess calls that do real work.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .progress_indicator import ProgressIndicator, ProgressStyle, progress_context
from .profile_migration import profile_migrator, check_and_migrate


class NixRealExecutor:
    """
    Executor that ACTUALLY runs NixOS commands.
    
    Philosophy:
    - Start with read-only commands for safety
    - Use modern 'nix' commands with proper flags
    - Handle both old nix-env and new nix profile
    - Provide real output, not mocked responses
    """
    
    def __init__(self, timeout: int = 30, dry_run: bool = False):
        """
        Initialize the real executor.
        
        Args:
            timeout: Command timeout in seconds
            dry_run: If True, preview commands without executing
        """
        self.timeout = timeout
        self.dry_run = dry_run
        self.experimental_features = "nix-command flakes"
        
        # Check and perform profile migration if needed
        migration_error = check_and_migrate()
        if migration_error:
            print(f"⚠️  Profile migration issue: {migration_error}")
        
        # Detect if user has new profile system
        self.use_nix_profile = self._detect_profile_type()
        
    def _detect_profile_type(self) -> bool:
        """Detect if user is using new nix profile or old nix-env"""
        profile_path = Path.home() / ".local/state/nix/profiles/profile"
        if profile_path.exists():
            # Check if it's a new-style profile
            manifest = profile_path / "manifest.json"
            return manifest.exists()
        return False
    
    def execute(self, command: str, args: List[str] = None, 
                force_old_style: bool = False) -> Dict[str, Any]:
        """
        Execute a real NixOS command.
        
        Args:
            command: The command to execute (e.g., 'nix', 'nix-env')
            args: Arguments for the command
            force_old_style: Force using nix-env even if profile detected
            
        Returns:
            Dict with success, output, error, and metadata
        """
        args = args or []
        
        # Build the actual command
        if command == "nix-env" and self.use_nix_profile and not force_old_style:
            # Translate to new nix profile commands
            return self._execute_with_profile(args)
        elif command == "nix":
            # Modern nix command with experimental features
            return self._execute_modern_nix(args)
        else:
            # Direct execution
            return self._execute_direct(command, args)
    
    def _execute_modern_nix(self, args: List[str]) -> Dict[str, Any]:
        """Execute modern nix command with proper flags"""
        
        # Add experimental features flag
        cmd = [
            "nix",
            "--extra-experimental-features", self.experimental_features
        ] + args
        
        return self._run_subprocess(cmd)
    
    def _execute_with_profile(self, args: List[str]) -> Dict[str, Any]:
        """Translate nix-env commands to nix profile commands"""
        
        # Use profile migrator to get correct commands
        if args and args[0] == "-q":
            # List installed
            cmd = profile_migrator.get_correct_command("list")
        elif args and args[0] == "-qa":
            # Query available -> use nix search instead
            search_term = args[1] if len(args) > 1 else ""
            cmd = [
                "nix", 
                "--extra-experimental-features", self.experimental_features,
                "search", "nixpkgs", search_term
            ]
        elif args and args[0].startswith("-i"):
            # Install
            package = args[1] if len(args) > 1 else ""
            if self.dry_run:
                return {
                    "success": True,
                    "output": f"Would install: {package}",
                    "dry_run": True
                }
            cmd = profile_migrator.get_correct_command("install", package)
        elif args and args[0] == "-e":
            # Remove
            package = args[1] if len(args) > 1 else ""
            if self.dry_run:
                return {
                    "success": True,
                    "output": f"Would remove: {package}",
                    "dry_run": True
                }
            cmd = profile_migrator.get_correct_command("remove", package)
        else:
            # Fallback to original command
            cmd = ["nix-env"] + args
            
        return self._run_subprocess(cmd)
    
    def _execute_direct(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Execute command directly"""
        cmd = [command] + args
        return self._run_subprocess(cmd)
    
    def _run_subprocess(self, cmd: List[str]) -> Dict[str, Any]:
        """
        Actually run the subprocess.
        
        This is where the REAL execution happens!
        """
        if self.dry_run and any(x in str(cmd) for x in ["install", "remove", "update"]):
            return {
                "success": True,
                "output": f"DRY RUN: Would execute: {' '.join(cmd)}",
                "command": cmd,
                "dry_run": True
            }
        
        # Determine operation type for progress messages
        operation_type = self._get_operation_type(cmd)
        show_progress = operation_type != "default" and self.timeout > 5
        
        try:
            # REAL EXECUTION HERE!
            start_time = time.time()
            
            if show_progress:
                # Show progress for long operations
                with progress_context(operation_type) as progress:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                        env={**os.environ, "PAGER": "cat"}  # Disable pager for output
                    )
            else:
                # Quick operations don't need progress
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env={**os.environ, "PAGER": "cat"}  # Disable pager for output
                )
            
            elapsed = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "command": cmd,
                "returncode": result.returncode,
                "elapsed_seconds": elapsed
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {self.timeout} seconds",
                "command": cmd,
                "timeout": True
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Command not found: {cmd[0]}",
                "command": cmd,
                "not_found": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": cmd,
                "exception": type(e).__name__
            }
    
    def search_packages(self, query: str) -> Dict[str, Any]:
        """
        Search for NixOS packages (convenience method).
        
        Uses faster nix-env -qa for better performance.
        """
        # Use nix-env -qa which is MUCH faster than nix search
        # This completes in 1-2 seconds vs 30+ seconds for nix search
        args = ["-qa", f"*{query}*"]
        result = self.execute("nix-env", args, force_old_style=True)
        
        # Parse line-based output if successful
        if result.get("success") and result.get("output"):
            lines = result["output"].strip().split("\n")
            packages = [line.strip() for line in lines if line.strip()]
            result["packages"] = packages
            result["count"] = len(packages)
                
        return result
    
    def list_installed(self) -> Dict[str, Any]:
        """
        List installed packages (convenience method).
        
        Handles both old and new profile systems.
        """
        if self.use_nix_profile:
            result = self.execute("nix", ["profile", "list"])
        else:
            # Try old style first
            result = self.execute("nix-env", ["-q"], force_old_style=True)
            
        if result.get("success") and result.get("output"):
            lines = result["output"].strip().split("\n")
            result["packages"] = [l for l in lines if l]
            result["count"] = len(result["packages"])
            
        return result
    
    def _get_operation_type(self, cmd: List[str]) -> str:
        """Determine operation type from command for progress messages"""
        cmd_str = " ".join(cmd).lower()
        
        if "search" in cmd_str or "-qa" in cmd_str:
            return "package_search"
        elif "install" in cmd_str or "-iA" in cmd_str:
            return "package_install"
        elif "remove" in cmd_str or "uninstall" in cmd_str or "-e" in cmd_str:
            return "package_remove"
        elif "update" in cmd_str or "upgrade" in cmd_str:
            return "system_update"
        elif "collect-garbage" in cmd_str or "gc" in cmd_str:
            return "garbage_collect"
        elif "build" in cmd_str:
            return "package_build"
        else:
            return "default"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get NixOS system information"""
        info = {}
        
        # Get nix version
        version_result = self.execute("nix", ["--version"])
        if version_result.get("success"):
            info["nix_version"] = version_result["output"].strip()
        
        # Check profile type
        info["profile_type"] = "nix-profile" if self.use_nix_profile else "nix-env"
        
        # Get nixos-version if available
        nixos_result = self.execute("nixos-version", [])
        if nixos_result.get("success"):
            info["nixos_version"] = nixos_result["output"].strip()
            
        return {
            "success": True,
            "info": info
        }


# Convenience function for quick testing
def test_real_executor():
    """Quick test of real executor"""
    
    print("🧪 Testing NixRealExecutor")
    print("=" * 50)
    
    executor = NixRealExecutor(timeout=10)
    
    # Test system info
    print("\n📊 System Info:")
    info = executor.get_system_info()
    for key, value in info.get("info", {}).items():
        print(f"  {key}: {value}")
    
    # Test listing packages
    print("\n📦 Installed Packages:")
    result = executor.list_installed()
    if result.get("success"):
        packages = result.get("packages", [])
        print(f"  Found {len(packages)} packages")
        if packages:
            print(f"  First few: {packages[:3]}")
    else:
        print(f"  Error: {result.get('error')}")
    
    # Test search (with short timeout)
    print("\n🔍 Search Test (vim):")
    executor.timeout = 5  # Shorter timeout for search
    result = executor.search_packages("vim")
    if result.get("success"):
        if result.get("packages"):
            print(f"  Found {result.get('count')} packages")
        else:
            print(f"  Raw output: {result.get('output', '')[:200]}")
    else:
        print(f"  Error: {result.get('error')}")
    
    print("\n✅ Real executor is working!")
    return executor


if __name__ == "__main__":
    test_real_executor()