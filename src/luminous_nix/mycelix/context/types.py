"""
Core types for Context Awareness System

Defines enums and data classes for context tracking.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ProjectType(Enum):
    """Types of projects that can be detected"""
    WEB_DEV = "web_development"
    PYTHON = "python"
    RUST = "rust"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    NIX = "nix"
    SYSTEM_CONFIG = "system_configuration"
    DOCUMENTATION = "documentation"
    UNKNOWN = "unknown"


class SessionState(Enum):
    """Current session state based on activity patterns"""
    HIGH_FOCUS = "high_focus"           # Deep work, minimal interruptions
    EXPLORING = "exploring"              # Learning, browsing, trying things
    FRUSTRATED = "frustrated"            # Repeated errors, backtracking
    TIRED = "tired"                      # Slowing down, more errors
    INACTIVE = "inactive"                # No recent activity


class IntentType(Enum):
    """Types of user intent that can be inferred"""
    DEVELOPING = "developing"            # Writing code
    DEBUGGING = "debugging"              # Fixing issues
    CONFIGURING = "configuring"          # Setting up environment
    LEARNING = "learning"                # Exploring/understanding
    MAINTAINING = "maintaining"          # Updating/cleaning
    UNKNOWN = "unknown"                  # Can't determine


class TimeContext(Enum):
    """Time-based context for adaptive behavior"""
    MORNING = "morning"                  # 6am-12pm: Planning-focused
    AFTERNOON = "afternoon"              # 12pm-6pm: Execution-focused
    EVENING = "evening"                  # 6pm-10pm: Reflective
    LATE_NIGHT = "late_night"           # 10pm-6am: Minimal interruptions


@dataclass
class FileActivity:
    """Represents activity on a file"""
    path: Path
    last_modified: datetime
    edit_count: int = 0
    language: Optional[str] = None
    project_type: Optional[ProjectType] = None


@dataclass
class CommandActivity:
    """Represents a command execution"""
    command: str
    timestamp: datetime
    success: bool
    duration_ms: float
    exit_code: int = 0
    project_context: Optional[ProjectType] = None


@dataclass
class Intent:
    """Inferred user intent"""
    intent_type: IntentType
    confidence: float                    # 0.0-1.0
    evidence: List[str] = field(default_factory=list)
    primary_project: Optional[ProjectType] = None
    secondary_projects: List[ProjectType] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"{self.intent_type.value} ({self.confidence:.0%} confident)"


@dataclass
class Context:
    """
    Complete context snapshot

    Represents everything we know about the user's current state:
    - What files they're editing
    - What commands they're running
    - What project type they're working on
    - Their current session state
    - Inferred intent
    """
    # File context
    active_files: List[FileActivity] = field(default_factory=list)
    recent_files: List[FileActivity] = field(default_factory=list)

    # Command context
    recent_commands: List[CommandActivity] = field(default_factory=list)
    command_patterns: Dict[str, int] = field(default_factory=dict)

    # Project context
    primary_project: Optional[ProjectType] = None
    project_confidence: float = 0.0
    working_directory: Optional[Path] = None

    # Session context
    session_state: SessionState = SessionState.INACTIVE
    session_start: datetime = field(default_factory=datetime.now)
    time_context: TimeContext = TimeContext.AFTERNOON

    # Intent
    current_intent: Optional[Intent] = None

    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            "active_files": [str(f.path) for f in self.active_files],
            "recent_commands": [c.command for c in self.recent_commands[-5:]],
            "primary_project": self.primary_project.value if self.primary_project else None,
            "session_state": self.session_state.value,
            "time_context": self.time_context.value,
            "current_intent": str(self.current_intent) if self.current_intent else None,
            "last_updated": self.last_updated.isoformat()
        }

    def summary(self) -> str:
        """Human-readable summary of current context"""
        parts = []

        if self.primary_project:
            parts.append(f"Working on {self.primary_project.value}")

        if self.current_intent:
            parts.append(f"Intent: {self.current_intent}")

        if self.active_files:
            parts.append(f"{len(self.active_files)} active files")

        if self.recent_commands:
            parts.append(f"{len(self.recent_commands)} recent commands")

        parts.append(f"State: {self.session_state.value}")

        return " | ".join(parts)
