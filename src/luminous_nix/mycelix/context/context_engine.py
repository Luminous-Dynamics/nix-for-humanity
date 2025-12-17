"""
Context Engine - Main orchestrator for Context Awareness

Coordinates all context monitoring components to provide a unified view
of the user's current state and intent.

This is the main entry point for the Conscious Co-Pilot's context awareness.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from .types import Context, SessionState, TimeContext, Intent
from .file_monitor import FileMonitor
from .command_tracker import CommandTracker
from .project_detector import ProjectDetector
from .session_tracker import SessionTracker
from .intent_inferencer import IntentInferencer

logger = logging.getLogger(__name__)


class ContextEngine:
    """
    Main Context Awareness Engine

    Coordinates all monitoring components to provide:
    - Current context snapshot
    - Real-time context updates
    - Context-based predictions
    - Intent inference

    This is the foundation for Conscious Co-Pilot's revolutionary features:
    - Predictive assistance
    - Adaptive personality
    - Proactive suggestions
    """

    def __init__(
        self,
        watch_paths: Optional[list[Path]] = None,
        enable_file_monitoring: bool = True,
        enable_command_tracking: bool = True
    ):
        """
        Initialize Context Engine

        Args:
            watch_paths: Directories to monitor for file changes
            enable_file_monitoring: Enable file activity tracking
            enable_command_tracking: Enable command history tracking
        """
        self.watch_paths = watch_paths or [Path.cwd()]
        self.enable_file_monitoring = enable_file_monitoring
        self.enable_command_tracking = enable_command_tracking

        # Initialize monitoring components
        logger.info("Initializing Context Engine...")

        self.file_monitor = FileMonitor(
            watch_paths=self.watch_paths,
            recent_window_minutes=30
        ) if enable_file_monitoring else None

        self.command_tracker = CommandTracker(
            history_size=1000,
            recent_window_minutes=60
        ) if enable_command_tracking else None

        # Initialize analysis components
        if self.file_monitor and self.command_tracker:
            self.project_detector = ProjectDetector(
                file_monitor=self.file_monitor,
                command_tracker=self.command_tracker
            )

            self.session_tracker = SessionTracker(
                command_tracker=self.command_tracker,
                inactivity_threshold_minutes=15
            )

            self.intent_inferencer = IntentInferencer(
                file_monitor=self.file_monitor,
                command_tracker=self.command_tracker,
                project_detector=self.project_detector,
                session_tracker=self.session_tracker
            )
        else:
            logger.warning("Context Engine initialized with limited functionality")
            self.project_detector = None
            self.session_tracker = None
            self.intent_inferencer = None

        logger.info("Context Engine initialized successfully")

    def get_current_context(self) -> Context:
        """
        Get current context snapshot

        Returns:
            Complete Context object with all current information
        """
        context = Context()

        # Gather file context
        if self.file_monitor:
            context.active_files = self.file_monitor.get_active_files(threshold_minutes=5)
            context.recent_files = self.file_monitor.get_recent_files(limit=20)

        # Gather command context
        if self.command_tracker:
            context.recent_commands = self.command_tracker.get_recent_commands(limit=20)
            context.command_patterns = dict(self.command_tracker.get_command_patterns())

        # Detect project
        if self.project_detector:
            project, confidence = self.project_detector.detect_project()
            context.primary_project = project
            context.project_confidence = confidence

        # Get session state
        if self.session_tracker:
            context.session_state = self.session_tracker.detect_session_state()
            context.session_start = self.session_tracker.session_start
            context.time_context = self.session_tracker.get_time_context()

        # Infer intent
        if self.intent_inferencer:
            context.current_intent = self.intent_inferencer.infer_intent()

        # Set working directory
        context.working_directory = Path.cwd()
        context.last_updated = datetime.now()

        logger.debug(f"Context snapshot: {context.summary()}")

        return context

    def record_command(
        self,
        command: str,
        success: bool,
        duration_ms: float,
        exit_code: int = 0
    ):
        """
        Record a command execution

        Args:
            command: The command that was executed
            success: Whether it succeeded
            duration_ms: How long it took
            exit_code: Exit code (0 = success)
        """
        if not self.command_tracker:
            return

        self.command_tracker.record_command(
            command=command,
            success=success,
            duration_ms=duration_ms,
            exit_code=exit_code
        )

        # Update session activity
        if self.session_tracker:
            self.session_tracker.update_activity()

        logger.debug(f"Recorded command: {command[:50]}...")

    def should_suggest_break(self) -> bool:
        """
        Check if user should take a break

        Returns:
            True if break recommended
        """
        if not self.session_tracker:
            return False

        return self.session_tracker.should_suggest_break()

    def get_contextual_suggestions(self) -> list[str]:
        """
        Get context-aware suggestions

        Returns:
            List of helpful suggestions based on current context
        """
        suggestions = []

        if not (self.intent_inferencer and self.project_detector and self.session_tracker):
            return suggestions

        # Get current context
        context = self.get_current_context()

        # Session-based suggestions
        if self.should_suggest_break():
            suggestions.append("💡 You've been working for a while. Consider taking a short break!")

        # Frustration detection
        if context.session_state == SessionState.FRUSTRATED:
            suggestions.append("🤔 Having trouble? Let me help you debug or find documentation")

        # Project-specific suggestions
        if context.primary_project and context.project_confidence > 0.6:
            project_suggestions = self.project_detector.get_project_suggestions(context.primary_project)
            suggestions.extend(project_suggestions[:2])  # Top 2 suggestions

        # Intent-based suggestions
        if context.current_intent and context.current_intent.confidence > 0.6:
            next_need = self.intent_inferencer.get_next_likely_need(context.current_intent)
            if next_need:
                suggestions.append(f"🎯 Next step: {next_need}")

        return suggestions

    def get_stats(self) -> dict:
        """
        Get comprehensive context statistics

        Returns:
            Dictionary of all context stats
        """
        stats = {
            "timestamp": datetime.now().isoformat(),
            "enabled_features": {
                "file_monitoring": self.enable_file_monitoring,
                "command_tracking": self.enable_command_tracking
            }
        }

        if self.file_monitor:
            stats["file_activity"] = {
                "active_files": len(self.file_monitor.get_active_files()),
                "recent_files": len(self.file_monitor.get_recent_files()),
                "language_distribution": self.file_monitor.get_language_distribution()
            }

        if self.command_tracker:
            stats["command_activity"] = self.command_tracker.get_stats()

        if self.session_tracker:
            stats["session"] = self.session_tracker.get_stats()

        if self.project_detector:
            project, confidence = self.project_detector.detect_project()
            stats["project"] = {
                "type": project.value if project else None,
                "confidence": confidence
            }

        return stats

    def reset(self):
        """Reset all context (new session)"""
        if self.file_monitor:
            self.file_monitor.clear_cache()

        if self.command_tracker:
            self.command_tracker.clear_history()

        if self.session_tracker:
            self.session_tracker.reset_session()

        logger.info("Context Engine reset")


# Singleton instance for global access
_context_engine: Optional[ContextEngine] = None


def get_context_engine(
    watch_paths: Optional[list[Path]] = None,
    enable_file_monitoring: bool = True,
    enable_command_tracking: bool = True
) -> ContextEngine:
    """
    Get or create the global ContextEngine instance

    Args:
        watch_paths: Directories to monitor
        enable_file_monitoring: Enable file monitoring
        enable_command_tracking: Enable command tracking

    Returns:
        Singleton ContextEngine instance
    """
    global _context_engine

    if _context_engine is None:
        _context_engine = ContextEngine(
            watch_paths=watch_paths,
            enable_file_monitoring=enable_file_monitoring,
            enable_command_tracking=enable_command_tracking
        )

    return _context_engine
