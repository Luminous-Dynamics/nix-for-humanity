"""
Context Awareness System for Conscious Co-Pilot

This module provides context-aware intelligence that understands what the user
is doing, enabling proactive assistance and adaptive behavior.

Components:
- ContextEngine: Main orchestrator for context awareness
- FileMonitor: Tracks file editing patterns
- CommandTracker: Analyzes command history
- ProjectDetector: Infers project type and goals
- SessionTracker: Monitors session state and duration
- IntentInferencer: Predicts user intent from context

Week 9-10 Implementation: Phase 1 of Conscious Co-Pilot Vision
"""

from .context_engine import ContextEngine, get_context_engine
from .file_monitor import FileMonitor
from .command_tracker import CommandTracker
from .project_detector import ProjectDetector, ProjectType
from .session_tracker import SessionTracker, SessionState
from .intent_inferencer import IntentInferencer, Intent, IntentType
from .types import Context, FileActivity, CommandActivity, TimeContext
from .builder import (
    build_context,
    build_test_context,
    ensure_context,
    build_command_context,
    build_multi_command_context,
)

__all__ = [
    # Main engine
    "ContextEngine",
    "get_context_engine",

    # Monitors
    "FileMonitor",
    "CommandTracker",
    "ProjectDetector",
    "SessionTracker",
    "IntentInferencer",

    # Types
    "Context",
    "FileActivity",
    "CommandActivity",
    "TimeContext",
    "ProjectType",
    "SessionState",
    "Intent",
    "IntentType",

    # Builders
    "build_context",
    "build_test_context",
    "ensure_context",
    "build_command_context",
    "build_multi_command_context",
]
