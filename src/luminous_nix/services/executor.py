"""
NixOS Executor Service - Clean command execution

Single responsibility: Execute NixOS commands safely and reliably.
No search logic, no caching, just execution.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import subprocess
import logging
import os
import shutil

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Clean execution result"""

    success: bool
    output: str
    error: str
    return_code: int
    command: str

    @property
    def failed(self) -> bool:
        return not self.success


class NixExecutor:
    """
    Clean executor service with single responsibility.

    This service ONLY executes NixOS commands. It doesn't:
    - Search for packages (that's SearchService's job)
    - Cache results (that's CacheService's job)
    - Generate configs (that's ConfigGenerator's job)
    """

    def __init__(self, timeout: int = 30, dry_run: bool = False):
        """
        Initialize executor.

        Args:
            timeout: Command timeout in seconds
            dry_run: If True, show commands without executing
        """
        self.timeout = timeout
        self.dry_run = dry_run
        self.use_nix_profile = self._detect_profile_type()

    def install(self, package: str) -> ExecutionResult:
        """
        Install a package.

        Args:
            package: Package name to install

        Returns:
            ExecutionResult with success status
        """
        if self.use_nix_profile:
            # New nix profile command
            cmd = ["nix", "profile", "install", f"nixpkgs#{package}"]
        else:
            # Legacy nix-env command
            cmd = ["nix-env", "-iA", f"nixos.{package}"]

        return self._execute(cmd, f"install {package}")

    def remove(self, package: str) -> ExecutionResult:
        """
        Remove a package.

        Args:
            package: Package name to remove

        Returns:
            ExecutionResult with success status
        """
        if self.use_nix_profile:
            # Need to find package ID first
            list_result = self._execute(["nix", "profile", "list"], "list profiles")
            if list_result.success:
                # Find package in output
                package_id = self._find_package_id(list_result.output, package)
                if package_id:
                    cmd = ["nix", "profile", "remove", package_id]
                else:
                    return ExecutionResult(
                        success=False,
                        output="",
                        error=f"Package {package} not found in profile",
                        return_code=1,
                        command=f"remove {package}",
                    )
            else:
                return list_result
        else:
            # Legacy nix-env command
            cmd = ["nix-env", "-e", package]

        return self._execute(cmd, f"remove {package}")

    def list_installed(self) -> ExecutionResult:
        """
        List installed packages.

        Returns:
            ExecutionResult with package list in output
        """
        if self.use_nix_profile:
            cmd = ["nix", "profile", "list"]
        else:
            cmd = ["nix-env", "-q"]

        return self._execute(cmd, "list installed")

    def update_channel(self) -> ExecutionResult:
        """
        Update NixOS channel.

        Returns:
            ExecutionResult with update status
        """
        # This typically requires sudo
        cmd = ["nix-channel", "--update"]
        return self._execute(cmd, "update channel", needs_sudo=True)

    def rebuild_system(self, operation: str = "switch") -> ExecutionResult:
        """
        Rebuild NixOS system.

        Args:
            operation: Rebuild operation (switch, boot, test, dry-build)

        Returns:
            ExecutionResult with rebuild status
        """
        # This requires sudo
        cmd = ["nixos-rebuild", operation]
        return self._execute(cmd, f"rebuild {operation}", needs_sudo=True)

    def garbage_collect(self, delete_old: bool = False) -> ExecutionResult:
        """
        Run garbage collection to free disk space.

        Args:
            delete_old: Also delete old generations

        Returns:
            ExecutionResult with GC status
        """
        cmd = ["nix-collect-garbage"]
        if delete_old:
            cmd.append("-d")

        return self._execute(cmd, "garbage collect")

    def build_flake(self, flake_ref: str) -> ExecutionResult:
        """
        Build a flake.

        Args:
            flake_ref: Flake reference to build

        Returns:
            ExecutionResult with build status
        """
        cmd = ["nix", "build", flake_ref]
        return self._execute(cmd, f"build {flake_ref}")

    def develop(self, flake_ref: str = ".") -> ExecutionResult:
        """
        Enter development shell.

        Args:
            flake_ref: Flake reference for dev shell

        Returns:
            ExecutionResult with shell command
        """
        cmd = ["nix", "develop", flake_ref, "-c", "echo", "Development shell ready"]
        return self._execute(cmd, f"develop {flake_ref}")

    def _execute(
        self, cmd: List[str], description: str, needs_sudo: bool = False
    ) -> ExecutionResult:
        """
        Execute a command.

        Private method that does the actual execution.
        """
        # Add sudo if needed
        if needs_sudo and not self.dry_run:
            if shutil.which("sudo"):
                cmd = ["sudo"] + cmd
            else:
                return ExecutionResult(
                    success=False,
                    output="",
                    error="This operation requires sudo privileges",
                    return_code=1,
                    command=" ".join(cmd),
                )

        # Dry run - just show what would be executed
        if self.dry_run:
            cmd_str = " ".join(cmd)
            return ExecutionResult(
                success=True,
                output=f"[DRY RUN] Would execute: {cmd_str}",
                error="",
                return_code=0,
                command=cmd_str,
            )

        # Execute the command
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout
            )

            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                command=" ".join(cmd),
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Command timed out after {self.timeout} seconds",
                return_code=-1,
                command=" ".join(cmd),
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                return_code=-1,
                command=" ".join(cmd),
            )

    def _detect_profile_type(self) -> bool:
        """
        Detect whether to use new nix profile or legacy nix-env.

        Returns:
            True if should use nix profile commands
        """
        # Check if nix profile is available
        try:
            result = subprocess.run(
                ["nix", "profile", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except:
            return False

    def _find_package_id(self, profile_output: str, package_name: str) -> Optional[str]:
        """
        Find package ID in nix profile list output.

        Args:
            profile_output: Output from nix profile list
            package_name: Name of package to find

        Returns:
            Package ID or None if not found
        """
        for line in profile_output.splitlines():
            if package_name in line:
                # First field is usually the ID
                parts = line.split()
                if parts:
                    return parts[0]
        return None
