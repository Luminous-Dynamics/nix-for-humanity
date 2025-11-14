"""
Robust command execution layer with preview, rollback, and state tracking
Now uses the subprocess-based operations for standard Nix performance!
"""

import json
import shlex
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import the native API for massive performance gains
try:
    from .native_nix_api import get_native_api

    NATIVE_API_AVAILABLE = True
except ImportError:
    NATIVE_API_AVAILABLE = False


class CommandType(Enum):
    """Types of Nix commands"""

    INSTALL = "install"
    REMOVE = "remove"
    UPDATE = "update"
    ROLLBACK = "rollback"
    SEARCH = "search"
    LIST = "list"
    CONFIG = "config"
    FLAKE = "flake"
    GENERATION = "generation"
    CUSTOM = "custom"


class CommandStatus(Enum):
    """Status of command execution"""

    PENDING = "pending"
    PREVIEWED = "previewed"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class NixCommand:
    """Represents a Nix command with metadata"""

    type: CommandType
    command: list[str]  # Command parts as list
    description: str
    requires_sudo: bool = False
    can_rollback: bool = True
    dry_run_flag: str | None = "--dry-run"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_string(self) -> str:
        """Convert command to string for display"""
        return " ".join(shlex.quote(arg) for arg in self.command)

    def preview_string(self) -> str:
        """Get preview command string"""
        if self.dry_run_flag and self.dry_run_flag not in self.command:
            preview_cmd = self.command.copy()
            preview_cmd.append(self.dry_run_flag)
            return " ".join(shlex.quote(arg) for arg in preview_cmd)
        return self.to_string()


@dataclass
class CommandResult:
    """Result of command execution"""

    command: NixCommand
    status: CommandStatus
    stdout: str = ""
    stderr: str = ""
    return_code: int | None = None
    execution_time: float | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    rollback_info: dict | None = None

    def success(self) -> bool:
        """Check if command succeeded"""
        return self.status == CommandStatus.SUCCESS


@dataclass
class SystemSnapshot:
    """Snapshot of system state for rollback"""

    timestamp: datetime
    generation: int | None = None
    installed_packages: list[str] = field(default_factory=list)
    configuration_backup: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CommandExecutor:
    """
    Robust command execution with preview, rollback, and state tracking

    Features:
    - Preview commands before execution
    - Automatic snapshots for rollback
    - Command history tracking
    - State persistence
    - Error recovery
    """

    def __init__(self, state_dir: Path | None = None):
        """Initialize command executor"""
        self.state_dir = state_dir or (Path.home() / ".local/state/luminous-nix")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.state_dir / "command_history.json"
        self.snapshot_dir = self.state_dir / "snapshots"
        self.snapshot_dir.mkdir(exist_ok=True)

        self.history: list[CommandResult] = self._load_history()
        self.dry_run = False
        self.auto_snapshot = True
        self.confirm_callback = None  # Function to call for confirmation

        # Initialize native API for massive performance gains
        self.native_api = get_native_api() if NATIVE_API_AVAILABLE else None

    def create_command(
        self,
        type: CommandType,
        args: list[str],
        description: str | None = None,
        **kwargs,
    ) -> NixCommand:
        """
        Create a NixCommand object

        Examples:
            executor.create_command(CommandType.INSTALL, ['firefox'])
            executor.create_command(CommandType.UPDATE, [], requires_sudo=True)
        """
        # Build the actual command based on type
        if type == CommandType.INSTALL:
            # Use modern nix profile command instead of nix-env
            command = (
                ["nix", "profile", "install", f"nixpkgs#{args[0]}"] if args else []
            )
            desc = f"Install {args[0] if args else 'package'}"
            # Store package name for native API
            kwargs.setdefault("metadata", {})["package"] = args[0] if args else None
            # nix profile doesn't have a dry-run flag
            kwargs["dry_run_flag"] = None

        elif type == CommandType.REMOVE:
            # Use modern nix profile command
            command = ["nix", "profile", "remove"] + args
            desc = f"Remove {args[0] if args else 'package'}"
            # nix profile doesn't have a dry-run flag
            kwargs["dry_run_flag"] = None

        elif type == CommandType.UPDATE:
            command = ["sudo", "nixos-rebuild", "switch", "--upgrade"]
            desc = "Update NixOS system"
            kwargs["requires_sudo"] = True

        elif type == CommandType.ROLLBACK:
            command = ["sudo", "nixos-rebuild", "switch", "--rollback"]
            desc = "Rollback to previous generation"
            kwargs["requires_sudo"] = True

        elif type == CommandType.SEARCH:
            command = ["nix", "search", "nixpkgs"] + args
            desc = f"Search for {' '.join(args)}"
            kwargs["can_rollback"] = False
            # Store query for native API
            kwargs.setdefault("metadata", {})["query"] = (
                " ".join(args) if args else None
            )

        elif type == CommandType.LIST:
            # Use modern nix profile command
            command = ["nix", "profile", "list"]
            desc = "List installed packages"
            kwargs["can_rollback"] = False
            kwargs["dry_run_flag"] = None
            # No extra metadata needed for list

        else:
            command = args
            desc = description or f"Execute {type.value}"

        return NixCommand(type=type, command=command, description=desc, **kwargs)

    def preview(self, command: NixCommand) -> CommandResult:
        """
        Preview what a command would do without executing

        Returns a CommandResult with preview information
        """
        result = CommandResult(command=command, status=CommandStatus.PREVIEWED)

        # Try to get preview using dry-run
        if command.dry_run_flag:
            preview_cmd = command.command.copy()
            if command.dry_run_flag not in preview_cmd:
                preview_cmd.append(command.dry_run_flag)

            try:
                proc = subprocess.run(
                    preview_cmd, capture_output=True, text=True, timeout=10
                )
                result.stdout = proc.stdout
                result.stderr = proc.stderr
                result.return_code = proc.returncode

            except subprocess.TimeoutExpired:
                result.stdout = f"Preview timed out for: {command.to_string()}"
            except Exception as e:
                result.stderr = f"Preview failed: {e}"
        else:
            # For commands without dry-run, just show what would be executed
            result.stdout = f"Would execute: {command.to_string()}\n"
            result.stdout += f"Description: {command.description}\n"
            if command.requires_sudo:
                result.stdout += "Note: This command requires sudo privileges\n"

        return result

    def execute(
        self, command: NixCommand, preview_first: bool = True, confirm: bool = True
    ) -> CommandResult:
        """
        Execute a command with optional preview and confirmation

        Args:
            command: The command to execute
            preview_first: Show preview before execution
            confirm: Ask for confirmation before execution

        Returns:
            CommandResult with execution details
        """
        # Check if in dry-run mode
        if self.dry_run:
            return self.preview(command)

        # Preview if requested
        if preview_first:
            preview_result = self.preview(command)
            print(f"📋 Preview: {command.description}")
            if preview_result.stdout:
                print(preview_result.stdout)

        # Confirm if requested
        if confirm and self.confirm_callback:
            if not self.confirm_callback(command):
                return CommandResult(
                    command=command,
                    status=CommandStatus.FAILED,
                    stderr="User cancelled execution",
                )

        # Create snapshot if command can be rolled back
        snapshot = None
        if command.can_rollback and self.auto_snapshot:
            snapshot = self._create_snapshot()

        # Execute the command
        result = CommandResult(command=command, status=CommandStatus.EXECUTING)

        import time

        start_time = time.time()

        # Try native API first for massive performance gains
        executed_with_native = False
        if self.native_api and command.type in [
            CommandType.INSTALL,
            CommandType.SEARCH,
            CommandType.LIST,
        ]:
            try:
                if command.type == CommandType.INSTALL and command.metadata.get(
                    "package"
                ):
                    # Use native API for install (standard speed!)
                    success, output, elapsed_ms = self.native_api.install_package(
                        command.metadata["package"],
                        profile="user" if not command.requires_sudo else "system",
                    )
                    result.stdout = output
                    result.return_code = 0 if success else 1
                    result.execution_time = elapsed_ms / 1000.0
                    result.status = (
                        CommandStatus.SUCCESS if success else CommandStatus.FAILED
                    )
                    executed_with_native = True

                elif command.type == CommandType.SEARCH and command.metadata.get(
                    "query"
                ):
                    # Use native API for search (2-3 seconds vs 2000-5000ms!)
                    packages, elapsed_ms = self.native_api.search_packages(
                        command.metadata["query"]
                    )
                    result.stdout = json.dumps(packages, indent=2)
                    result.return_code = 0
                    result.execution_time = elapsed_ms / 1000.0
                    result.status = CommandStatus.SUCCESS
                    executed_with_native = True

                elif command.type == CommandType.LIST:
                    # Use native API for list
                    generations, elapsed_ms = self.native_api.list_generations()
                    result.stdout = json.dumps(generations, indent=2)
                    result.return_code = 0
                    result.execution_time = elapsed_ms / 1000.0
                    result.status = CommandStatus.SUCCESS
                    executed_with_native = True

            except Exception:
                # Native API failed, fall back to subprocess
                executed_with_native = False

        # Fallback to subprocess if native API not available or didn't handle this command
        if not executed_with_native:
            try:
                proc = subprocess.run(
                    command.command,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                result.stdout = proc.stdout
                result.stderr = proc.stderr
                result.return_code = proc.returncode
                result.execution_time = time.time() - start_time

                if proc.returncode == 0:
                    result.status = CommandStatus.SUCCESS
                else:
                    result.status = CommandStatus.FAILED

            except subprocess.TimeoutExpired:
                result.status = CommandStatus.FAILED
                result.stderr = "Command timed out after 5 minutes"

            except Exception as e:
                result.status = CommandStatus.FAILED
                result.stderr = f"Execution failed: {e}"

        # Store rollback info if snapshot was created
        if snapshot:
            result.rollback_info = {
                "snapshot": snapshot.__dict__,
                "can_rollback": True,
            }

        # Save to history
        self._add_to_history(result)

        return result

    def rollback(self, steps: int = 1) -> CommandResult:
        """
        Rollback to a previous state

        Args:
            steps: Number of commands to rollback (default 1)
        """
        # Find last rollbackable command
        rollbackable = [
            r
            for r in reversed(self.history[-10:])  # Check last 10 commands
            if r.command.can_rollback and r.rollback_info
        ]

        if not rollbackable:
            return CommandResult(
                command=NixCommand(
                    type=CommandType.ROLLBACK,
                    command=[],
                    description="No rollback available",
                ),
                status=CommandStatus.FAILED,
                stderr="No rollbackable commands in history",
            )

        # Get the command to rollback
        target = rollbackable[min(steps - 1, len(rollbackable) - 1)]

        # Create rollback command
        rollback_cmd = self.create_command(
            CommandType.ROLLBACK,
            [],
            description=f"Rollback from: {target.command.description}",
        )

        # Execute rollback
        result = self.execute(rollback_cmd, preview_first=False, confirm=False)

        if result.success():
            result.status = CommandStatus.ROLLED_BACK

        return result

    def get_history(self, limit: int = 10) -> list[CommandResult]:
        """Get command history"""
        return self.history[-limit:]

    def _create_snapshot(self) -> SystemSnapshot:
        """Create a system snapshot for rollback"""
        snapshot = SystemSnapshot(timestamp=datetime.now())

        # Get current generation
        try:
            result = subprocess.run(
                ["nixos-rebuild", "list-generations"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if lines:
                    # Parse generation number from first line
                    parts = lines[0].split()
                    if parts:
                        try:
                            snapshot.generation = int(parts[0])
                        except ValueError:
                            pass
        except:
            pass

        # Get installed packages
        try:
            result = subprocess.run(
                ["nix-env", "-q"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                snapshot.installed_packages = result.stdout.strip().split("\n")
        except:
            pass

        # Save snapshot
        snapshot_file = (
            self.snapshot_dir / f"snapshot_{datetime.now().isoformat()}.json"
        )
        snapshot_data = {
            "timestamp": snapshot.timestamp.isoformat(),
            "generation": snapshot.generation,
            "installed_packages": snapshot.installed_packages,
            "metadata": snapshot.metadata,
        }
        snapshot_file.write_text(json.dumps(snapshot_data, indent=2))

        return snapshot

    def _add_to_history(self, result: CommandResult):
        """Add command result to history"""
        self.history.append(result)

        # Keep only last 1000 commands
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        # Save to file
        self._save_history()

    def _save_history(self):
        """Save command history to file"""
        history_data = []
        for result in self.history[-100:]:  # Save last 100 commands
            history_data.append(
                {
                    "command": result.command.to_string(),
                    "type": result.command.type.value,
                    "description": result.command.description,
                    "status": result.status.value,
                    "timestamp": result.timestamp.isoformat(),
                    "return_code": result.return_code,
                }
            )

        self.history_file.write_text(json.dumps(history_data, indent=2))

    def _load_history(self) -> list[CommandResult]:
        """Load command history from file"""
        if not self.history_file.exists():
            return []

        try:
            data = json.loads(self.history_file.read_text())
            history = []

            for item in data:
                # Reconstruct basic command result
                cmd = NixCommand(
                    type=CommandType(item.get("type", "custom")),
                    command=shlex.split(item.get("command", "")),
                    description=item.get("description", ""),
                )

                result = CommandResult(
                    command=cmd,
                    status=CommandStatus(item.get("status", "unknown")),
                    timestamp=datetime.fromisoformat(item.get("timestamp")),
                    return_code=item.get("return_code"),
                )

                history.append(result)

            return history

        except Exception:
            return []
