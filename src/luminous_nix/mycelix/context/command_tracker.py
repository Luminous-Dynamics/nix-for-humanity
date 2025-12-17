"""
Command Tracker - Analyzes command history patterns

Tracks command execution to understand:
- What the user is trying to accomplish
- Common command patterns
- Error patterns
- Workflow sequences
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter, deque

from .types import CommandActivity, ProjectType

logger = logging.getLogger(__name__)


class CommandTracker:
    """
    Track command execution patterns

    Features:
    - Record command history
    - Detect command patterns
    - Identify repeated failures
    - Suggest next likely command
    """

    # Command to project type hints
    COMMAND_PROJECT_HINTS = {
        "cargo": ProjectType.RUST,
        "rustc": ProjectType.RUST,
        "npm": ProjectType.JAVASCRIPT,
        "node": ProjectType.JAVASCRIPT,
        "yarn": ProjectType.JAVASCRIPT,
        "python": ProjectType.PYTHON,
        "pip": ProjectType.PYTHON,
        "poetry": ProjectType.PYTHON,
        "nix-build": ProjectType.NIX,
        "nix develop": ProjectType.NIX,
        "nix-shell": ProjectType.NIX,
        "nixos-rebuild": ProjectType.SYSTEM_CONFIG,
        "vim": ProjectType.UNKNOWN,
        "code": ProjectType.UNKNOWN,
        "git": ProjectType.UNKNOWN,
    }

    def __init__(
        self,
        history_size: int = 1000,
        recent_window_minutes: int = 60
    ):
        """
        Initialize command tracker

        Args:
            history_size: Maximum commands to keep in memory
            recent_window_minutes: How recent is "recent" for commands
        """
        self.history_size = history_size
        self.recent_window = timedelta(minutes=recent_window_minutes)

        self._command_history: deque[CommandActivity] = deque(maxlen=history_size)
        self._command_counts: Counter[str] = Counter()

    def record_command(
        self,
        command: str,
        success: bool,
        duration_ms: float,
        exit_code: int = 0,
        project_context: Optional[ProjectType] = None
    ):
        """
        Record a command execution

        Args:
            command: The command that was executed
            success: Whether it succeeded
            duration_ms: How long it took
            exit_code: Exit code (0 = success)
            project_context: Project context if known
        """
        # Infer project from command if not provided
        if not project_context:
            project_context = self._infer_project_from_command(command)

        activity = CommandActivity(
            command=command,
            timestamp=datetime.now(),
            success=success,
            duration_ms=duration_ms,
            exit_code=exit_code,
            project_context=project_context
        )

        self._command_history.append(activity)
        self._command_counts[command] += 1

        logger.debug(
            f"Recorded command: {command[:50]}... "
            f"({'success' if success else 'failed'}, {duration_ms}ms)"
        )

    def get_recent_commands(self, limit: int = 20) -> List[CommandActivity]:
        """
        Get recent commands

        Args:
            limit: Maximum commands to return

        Returns:
            List of recent CommandActivity objects
        """
        cutoff = datetime.now() - self.recent_window

        recent = [
            cmd for cmd in self._command_history
            if cmd.timestamp >= cutoff
        ]

        return list(reversed(recent))[:limit]

    def get_command_patterns(self) -> List[Tuple[str, int]]:
        """
        Get most common command patterns

        Returns:
            List of (command, count) tuples, sorted by frequency
        """
        return self._command_counts.most_common(20)

    def get_recent_failures(self, limit: int = 10) -> List[CommandActivity]:
        """
        Get recent failed commands

        Args:
            limit: Maximum failures to return

        Returns:
            List of failed commands
        """
        cutoff = datetime.now() - self.recent_window

        failures = [
            cmd for cmd in self._command_history
            if not cmd.success and cmd.timestamp >= cutoff
        ]

        return list(reversed(failures))[:limit]

    def detect_frustration_pattern(self) -> bool:
        """
        Detect if user is showing signs of frustration

        Returns:
            True if frustration detected (many recent failures or retries)
        """
        recent = self.get_recent_commands(limit=10)

        if len(recent) < 5:
            return False

        # Count failures in recent commands
        failures = sum(1 for cmd in recent if not cmd.success)

        # Count repeated commands (retrying same thing)
        command_text = [cmd.command for cmd in recent[-5:]]
        repeated = len(command_text) - len(set(command_text))

        # Frustration indicators:
        # - >40% failure rate in recent commands
        # - Multiple retries of same command
        return (failures / len(recent) > 0.4) or (repeated >= 2)

    def infer_workflow(self) -> Optional[str]:
        """
        Infer current workflow from command patterns

        Returns:
            Description of likely workflow, or None
        """
        recent = self.get_recent_commands(limit=5)
        if not recent:
            return None

        commands = [cmd.command.split()[0] if cmd.command else "" for cmd in recent]

        # Common workflow patterns
        if "git" in commands and any(cmd in commands for cmd in ["npm", "cargo", "python"]):
            return "Development workflow (code + version control)"

        if "nix-build" in commands or "nixos-rebuild" in commands:
            return "NixOS configuration workflow"

        if "cargo build" in " ".join(cmd.command for cmd in recent):
            return "Rust development workflow"

        if any("test" in cmd.command for cmd in recent):
            return "Testing workflow"

        if "docker" in commands:
            return "Containerization workflow"

        return None

    def predict_next_command(self) -> Optional[str]:
        """
        Predict the next likely command based on patterns

        Returns:
            Predicted command, or None if unclear
        """
        recent = self.get_recent_commands(limit=3)
        if len(recent) < 1:
            return None

        # Get full last command
        last_full_cmd = recent[0].command

        # Pattern-based predictions (check full command)
        predictions = {
            "git add": "git commit",
            "git commit": "git push",
            "cargo build": "cargo run",
            "nix-build": "nix-shell",
            "npm install": "npm start",
            "make": "make install",
        }

        for pattern, next_cmd in predictions.items():
            if pattern in last_full_cmd:
                return next_cmd

        return None

    def get_project_context_from_commands(self) -> Optional[ProjectType]:
        """
        Infer project type from recent commands

        Returns:
            Most likely ProjectType based on commands
        """
        recent = self.get_recent_commands(limit=10)
        if not recent:
            return None

        # Count evidence for each project type
        evidence: Counter[ProjectType] = Counter()

        for cmd in recent:
            if cmd.project_context:
                evidence[cmd.project_context] += 1

        if not evidence:
            return None

        # Return most common project type
        return evidence.most_common(1)[0][0]

    def _infer_project_from_command(self, command: str) -> Optional[ProjectType]:
        """Infer project type from command text"""
        command_lower = command.lower()

        for hint, project_type in self.COMMAND_PROJECT_HINTS.items():
            if hint in command_lower:
                return project_type

        return None

    def get_stats(self) -> Dict[str, any]:
        """
        Get command tracking statistics

        Returns:
            Dictionary of statistics
        """
        recent = self.get_recent_commands()

        if not recent:
            return {
                "total_commands": 0,
                "recent_commands": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0
            }

        successful = [cmd for cmd in recent if cmd.success]
        total_duration = sum(cmd.duration_ms for cmd in recent)

        return {
            "total_commands": len(self._command_history),
            "recent_commands": len(recent),
            "success_rate": len(successful) / len(recent) if recent else 0.0,
            "avg_duration_ms": total_duration / len(recent) if recent else 0.0,
            "most_common": self._command_counts.most_common(5)
        }

    def clear_history(self):
        """Clear command history"""
        self._command_history.clear()
        self._command_counts.clear()
