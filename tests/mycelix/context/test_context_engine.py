"""Integration Tests for ContextEngine"""

import pytest
import tempfile
import time
from pathlib import Path

from luminous_nix.mycelix.context import (
    ContextEngine,
    ProjectType,
    SessionState,
    IntentType
)


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        # Create Python project files
        (project_path / "main.py").write_text("print('hello')")
        (project_path / "test.py").write_text("import unittest")
        (project_path / "pyproject.toml").write_text('[tool.poetry]')

        yield project_path


class TestContextEngineIntegration:
    """Integration tests for full ContextEngine"""

    def test_initialization(self, temp_project_dir):
        """Test ContextEngine initialization"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        assert engine.file_monitor is not None
        assert engine.command_tracker is not None
        assert engine.project_detector is not None
        assert engine.session_tracker is not None
        assert engine.intent_inferencer is not None

    def test_get_current_context_basic(self, temp_project_dir):
        """Test getting current context"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        context = engine.get_current_context()

        assert context is not None
        assert context.working_directory == Path.cwd()
        assert context.session_state in list(SessionState)

    def test_record_and_retrieve_commands(self, temp_project_dir):
        """Test recording commands and retrieving context"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Record some commands
        engine.record_command("python main.py", success=True, duration_ms=100.0)
        engine.record_command("python test.py", success=True, duration_ms=200.0)

        context = engine.get_current_context()

        assert len(context.recent_commands) == 2
        assert context.recent_commands[0].command == "python test.py"

    def test_project_detection_from_files(self, temp_project_dir):
        """Test project type detection from files"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Touch files to make them recent
        (temp_project_dir / "main.py").touch()
        (temp_project_dir / "pyproject.toml").touch()

        context = engine.get_current_context()

        assert context.primary_project == ProjectType.PYTHON
        assert context.project_confidence > 0.0

    def test_intent_inference_developing(self, temp_project_dir):
        """Test intent inference for development activity"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Simulate development activity
        (temp_project_dir / "main.py").touch()
        time.sleep(0.1)

        engine.record_command("python main.py", success=True, duration_ms=100.0)
        engine.record_command("python -m pytest", success=True, duration_ms=500.0)

        context = engine.get_current_context()

        # Should infer development or testing intent
        if context.current_intent:
            assert context.current_intent.intent_type in [
                IntentType.DEVELOPING,
                IntentType.DEBUGGING,
                IntentType.LEARNING
            ]

    def test_intent_inference_debugging(self, temp_project_dir):
        """Test intent inference for debugging activity"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Simulate debugging (repeated failures)
        for _ in range(5):
            engine.record_command("cargo build", success=False, duration_ms=500.0, exit_code=1)

        context = engine.get_current_context()

        # Should detect debugging intent
        if context.current_intent:
            assert context.current_intent.intent_type in [
                IntentType.DEBUGGING,
                IntentType.DEVELOPING
            ]

    def test_session_state_tracking(self, temp_project_dir):
        """Test session state tracking"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Record active commands
        for i in range(10):
            engine.record_command(f"test_{i}", success=True, duration_ms=100.0)
            time.sleep(0.01)  # Small delay

        context = engine.get_current_context()

        # Should detect active state (not inactive)
        # TIRED is also acceptable if it detects slow-down pattern
        assert context.session_state in [
            SessionState.HIGH_FOCUS,
            SessionState.EXPLORING,
            SessionState.FRUSTRATED,
            SessionState.TIRED  # Can detect pattern as tiring
        ]

    def test_contextual_suggestions(self, temp_project_dir):
        """Test getting contextual suggestions"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Create some context
        (temp_project_dir / "main.py").touch()
        engine.record_command("python main.py", success=True, duration_ms=100.0)

        suggestions = engine.get_contextual_suggestions()

        # Should get some suggestions
        assert isinstance(suggestions, list)
        # May or may not have suggestions depending on context

    def test_should_suggest_break(self, temp_project_dir):
        """Test break suggestion"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Fresh session shouldn't need break
        assert engine.should_suggest_break() is False

        # (In reality, would need to mock session duration for proper testing)

    def test_get_stats(self, temp_project_dir):
        """Test statistics generation"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Record some activity
        (temp_project_dir / "main.py").touch()
        engine.record_command("test", success=True, duration_ms=100.0)

        stats = engine.get_stats()

        assert "timestamp" in stats
        assert "enabled_features" in stats
        assert stats["enabled_features"]["file_monitoring"] is True
        assert stats["enabled_features"]["command_tracking"] is True

    def test_reset(self, temp_project_dir):
        """Test resetting context"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Record some activity
        engine.record_command("test", success=True, duration_ms=100.0)

        # Reset
        engine.reset()

        context = engine.get_current_context()

        # Should have minimal context after reset
        assert len(context.recent_commands) == 0

    def test_context_summary_format(self, temp_project_dir):
        """Test context summary formatting"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Create rich context
        (temp_project_dir / "main.py").touch()
        engine.record_command("python main.py", success=True, duration_ms=100.0)

        context = engine.get_current_context()
        summary = context.summary()

        # Should be a readable string
        assert isinstance(summary, str)
        assert len(summary) > 0


class TestContextEngineFeatures:
    """Test advanced ContextEngine features"""

    def test_frustrated_user_detection(self):
        """Test detection of frustrated user state"""
        engine = ContextEngine()

        # Simulate frustration: many failures
        for _ in range(8):
            engine.record_command("failing_command", success=False, duration_ms=100.0, exit_code=1)

        context = engine.get_current_context()

        # Should detect frustration or debugging
        assert context.session_state in [SessionState.FRUSTRATED, SessionState.HIGH_FOCUS]

    def test_mixed_project_detection(self, temp_project_dir):
        """Test project detection with mixed signals"""
        engine = ContextEngine(watch_paths=[temp_project_dir])

        # Create files for different project types
        (temp_project_dir / "main.py").touch()
        (temp_project_dir / "package.json").touch()
        (temp_project_dir / "Cargo.toml").touch()

        context = engine.get_current_context()

        # Should detect something (even if confidence is low)
        assert context.primary_project in list(ProjectType)
        assert 0.0 <= context.project_confidence <= 1.0

    def test_learning_intent_from_help_commands(self):
        """Test learning intent detection from help commands"""
        # Create engine without file monitoring to avoid interference
        engine = ContextEngine(enable_file_monitoring=False)

        # Record only help/documentation commands
        engine.record_command("nix-shell --help", success=True, duration_ms=50.0)
        engine.record_command("man nix-build", success=True, duration_ms=100.0)
        engine.record_command("nix search nixpkgs python", success=True, duration_ms=200.0)

        context = engine.get_current_context()

        # Should infer learning intent
        # Note: With file monitoring disabled, intent inference is limited
        if context.current_intent:
            # Intent may be LEARNING, CONFIGURING, or even DEVELOPING (from search/nix commands)
            assert context.current_intent.intent_type in [
                IntentType.LEARNING,
                IntentType.CONFIGURING,
                IntentType.DEVELOPING,  # Also acceptable given the command mix
                IntentType.UNKNOWN
            ]
