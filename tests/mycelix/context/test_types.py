"""Tests for Context types and enums"""

import pytest
from datetime import datetime
from pathlib import Path

from luminous_nix.mycelix.context.types import (
    ProjectType,
    SessionState,
    IntentType,
    TimeContext,
    FileActivity,
    CommandActivity,
    Intent,
    Context
)


class TestEnums:
    """Test enum types"""

    def test_project_type_enum(self):
        """Test ProjectType enum has expected values"""
        assert ProjectType.WEB_DEV.value == "web_development"
        assert ProjectType.PYTHON.value == "python"
        assert ProjectType.RUST.value == "rust"
        assert ProjectType.UNKNOWN.value == "unknown"

    def test_session_state_enum(self):
        """Test SessionState enum has expected values"""
        assert SessionState.HIGH_FOCUS.value == "high_focus"
        assert SessionState.EXPLORING.value == "exploring"
        assert SessionState.FRUSTRATED.value == "frustrated"

    def test_intent_type_enum(self):
        """Test IntentType enum has expected values"""
        assert IntentType.DEVELOPING.value == "developing"
        assert IntentType.DEBUGGING.value == "debugging"
        assert IntentType.CONFIGURING.value == "configuring"


class TestFileActivity:
    """Test FileActivity dataclass"""

    def test_file_activity_creation(self):
        """Test creating FileActivity"""
        path = Path("/test/file.py")
        timestamp = datetime.now()

        activity = FileActivity(
            path=path,
            last_modified=timestamp,
            edit_count=5,
            language="python",
            project_type=ProjectType.PYTHON
        )

        assert activity.path == path
        assert activity.last_modified == timestamp
        assert activity.edit_count == 5
        assert activity.language == "python"
        assert activity.project_type == ProjectType.PYTHON


class TestCommandActivity:
    """Test CommandActivity dataclass"""

    def test_command_activity_creation(self):
        """Test creating CommandActivity"""
        timestamp = datetime.now()

        activity = CommandActivity(
            command="cargo build",
            timestamp=timestamp,
            success=True,
            duration_ms=1500.0,
            exit_code=0,
            project_context=ProjectType.RUST
        )

        assert activity.command == "cargo build"
        assert activity.success is True
        assert activity.duration_ms == 1500.0
        assert activity.project_context == ProjectType.RUST


class TestIntent:
    """Test Intent dataclass"""

    def test_intent_creation(self):
        """Test creating Intent"""
        intent = Intent(
            intent_type=IntentType.DEVELOPING,
            confidence=0.85,
            evidence=["Editing source files", "Running build commands"],
            primary_project=ProjectType.RUST
        )

        assert intent.intent_type == IntentType.DEVELOPING
        assert intent.confidence == 0.85
        assert len(intent.evidence) == 2
        assert intent.primary_project == ProjectType.RUST

    def test_intent_str_representation(self):
        """Test Intent string representation"""
        intent = Intent(
            intent_type=IntentType.DEBUGGING,
            confidence=0.75
        )

        assert "debugging" in str(intent)
        assert "75%" in str(intent)


class TestContext:
    """Test Context dataclass"""

    def test_context_creation(self):
        """Test creating Context"""
        context = Context()

        assert context.active_files == []
        assert context.recent_files == []
        assert context.recent_commands == []
        assert context.primary_project is None
        assert context.session_state == SessionState.INACTIVE

    def test_context_to_dict(self):
        """Test Context serialization"""
        context = Context(
            primary_project=ProjectType.PYTHON,
            session_state=SessionState.HIGH_FOCUS
        )

        data = context.to_dict()

        assert data["primary_project"] == "python"
        assert data["session_state"] == "high_focus"
        assert "last_updated" in data

    def test_context_summary(self):
        """Test Context summary generation"""
        intent = Intent(
            intent_type=IntentType.DEVELOPING,
            confidence=0.9
        )

        context = Context(
            primary_project=ProjectType.RUST,
            current_intent=intent,
            session_state=SessionState.HIGH_FOCUS
        )

        summary = context.summary()

        assert "rust" in summary.lower()
        assert "developing" in summary.lower()
        assert "high_focus" in summary

    def test_context_with_files_and_commands(self):
        """Test Context with file and command activity"""
        file_activity = FileActivity(
            path=Path("/test/main.py"),
            last_modified=datetime.now()
        )

        cmd_activity = CommandActivity(
            command="python test.py",
            timestamp=datetime.now(),
            success=True,
            duration_ms=100.0
        )

        context = Context(
            active_files=[file_activity],
            recent_commands=[cmd_activity]
        )

        assert len(context.active_files) == 1
        assert len(context.recent_commands) == 1

        summary = context.summary()
        assert "1 active files" in summary
        assert "1 recent commands" in summary
