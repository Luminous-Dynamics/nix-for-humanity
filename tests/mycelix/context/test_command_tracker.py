"""Tests for CommandTracker"""

import pytest
from datetime import datetime, timedelta

from luminous_nix.mycelix.context.command_tracker import CommandTracker
from luminous_nix.mycelix.context.types import ProjectType


class TestCommandTracker:
    """Test CommandTracker functionality"""

    def test_initialization(self):
        """Test CommandTracker initialization"""
        tracker = CommandTracker(history_size=100, recent_window_minutes=30)

        assert tracker.history_size == 100
        assert tracker.recent_window.total_seconds() == 30 * 60

    def test_record_command(self):
        """Test recording a command"""
        tracker = CommandTracker()

        tracker.record_command(
            command="cargo build",
            success=True,
            duration_ms=1500.0,
            exit_code=0
        )

        recent = tracker.get_recent_commands(limit=10)

        assert len(recent) == 1
        assert recent[0].command == "cargo build"
        assert recent[0].success is True
        assert recent[0].duration_ms == 1500.0

    def test_get_recent_commands(self):
        """Test getting recent commands"""
        tracker = CommandTracker()

        # Record multiple commands
        commands = ["npm install", "npm start", "git commit"]
        for cmd in commands:
            tracker.record_command(cmd, True, 100.0)

        recent = tracker.get_recent_commands(limit=10)

        assert len(recent) == 3
        # Should be in reverse order (most recent first)
        assert recent[0].command == "git commit"

    def test_get_command_patterns(self):
        """Test command pattern detection"""
        tracker = CommandTracker()

        # Record repeated commands
        tracker.record_command("git status", True, 50.0)
        tracker.record_command("git status", True, 50.0)
        tracker.record_command("git status", True, 50.0)
        tracker.record_command("cargo build", True, 1000.0)

        patterns = tracker.get_command_patterns()

        assert len(patterns) >= 2
        # "git status" should be most common
        assert patterns[0][0] == "git status"
        assert patterns[0][1] == 3

    def test_get_recent_failures(self):
        """Test getting recent failed commands"""
        tracker = CommandTracker()

        tracker.record_command("cargo build", False, 500.0, exit_code=1)
        tracker.record_command("npm test", True, 1000.0)
        tracker.record_command("cargo build", False, 500.0, exit_code=1)

        failures = tracker.get_recent_failures(limit=10)

        assert len(failures) == 2
        assert all(not cmd.success for cmd in failures)

    def test_detect_frustration_pattern(self):
        """Test frustration pattern detection"""
        tracker = CommandTracker()

        # Simulate frustration: multiple failures
        for i in range(5):
            tracker.record_command("cargo build", False, 500.0, exit_code=1)
            tracker.record_command("cargo build", False, 500.0, exit_code=1)

        is_frustrated = tracker.detect_frustration_pattern()

        assert is_frustrated is True

    def test_no_frustration_on_success(self):
        """Test no frustration detected with mostly successful commands"""
        tracker = CommandTracker()

        # Mostly successful commands with variety (not repeated)
        commands = ["git status", "git diff", "git log", "npm test", "cargo check"]
        for i in range(15):
            tracker.record_command(commands[i % len(commands)], True, 50.0)

        is_frustrated = tracker.detect_frustration_pattern()

        assert is_frustrated is False

    def test_infer_workflow_development(self):
        """Test workflow inference for development"""
        tracker = CommandTracker()

        tracker.record_command("git status", True, 50.0)
        tracker.record_command("npm install", True, 5000.0)
        tracker.record_command("git commit -m 'test'", True, 100.0)

        workflow = tracker.infer_workflow()

        assert workflow is not None
        assert "development" in workflow.lower() or "version control" in workflow.lower()

    def test_infer_workflow_nixos(self):
        """Test workflow inference for NixOS"""
        tracker = CommandTracker()

        tracker.record_command("nix-build", True, 10000.0)
        tracker.record_command("nixos-rebuild switch", True, 15000.0)

        workflow = tracker.infer_workflow()

        assert workflow is not None
        assert "nixos" in workflow.lower() or "configuration" in workflow.lower()

    def test_predict_next_command_git(self):
        """Test command prediction for git workflow"""
        tracker = CommandTracker()

        tracker.record_command("git add .", True, 50.0)

        prediction = tracker.predict_next_command()

        assert prediction == "git commit"

    def test_predict_next_command_cargo(self):
        """Test command prediction for Rust workflow"""
        tracker = CommandTracker()

        tracker.record_command("cargo build", True, 1500.0)

        prediction = tracker.predict_next_command()

        assert prediction == "cargo run"

    def test_get_project_context_from_commands(self):
        """Test project type inference from commands"""
        tracker = CommandTracker()

        tracker.record_command("cargo build", True, 1500.0)
        tracker.record_command("cargo test", True, 2000.0)
        tracker.record_command("rustc --version", True, 50.0)

        project = tracker.get_project_context_from_commands()

        assert project == ProjectType.RUST

    def test_infer_project_from_command(self):
        """Test project inference from individual commands"""
        tracker = CommandTracker()

        assert tracker._infer_project_from_command("cargo build") == ProjectType.RUST
        assert tracker._infer_project_from_command("npm install") == ProjectType.JAVASCRIPT
        assert tracker._infer_project_from_command("python main.py") == ProjectType.PYTHON
        assert tracker._infer_project_from_command("nix-build") == ProjectType.NIX
        assert tracker._infer_project_from_command("nixos-rebuild") == ProjectType.SYSTEM_CONFIG

    def test_get_stats(self):
        """Test statistics generation"""
        tracker = CommandTracker()

        tracker.record_command("test1", True, 100.0)
        tracker.record_command("test2", True, 200.0)
        tracker.record_command("test3", False, 150.0, exit_code=1)

        stats = tracker.get_stats()

        assert stats["total_commands"] == 3
        assert stats["recent_commands"] == 3
        assert 0.6 < stats["success_rate"] < 0.7  # 2/3 success
        assert stats["avg_duration_ms"] == pytest.approx(150.0)

    def test_clear_history(self):
        """Test clearing command history"""
        tracker = CommandTracker()

        tracker.record_command("test", True, 100.0)

        assert len(tracker._command_history) == 1

        tracker.clear_history()

        assert len(tracker._command_history) == 0
        assert len(tracker._command_counts) == 0
