"""
Context Builder

Helper utilities to build proper Context objects from minimal data.
Provides convenient constructors for testing and integration.
"""

from typing import Dict, Any, Optional, Union, List
from .types import (
    Context,
    FileActivity,
    CommandActivity,
    Intent,
    IntentType,
    ProjectType,
    SessionState,
    TimeContext,
)
from datetime import datetime
from pathlib import Path


def build_context(
    user_id: str = "default_user",
    query: str = "",
    recent_commands: Optional[List[CommandActivity]] = None,
    **kwargs
) -> Context:
    """
    Build a proper Context object from minimal data

    Args:
        user_id: User identifier (stored in metadata, not Context)
        query: Current query string (stored in metadata)
        recent_commands: List of recent command activities
        **kwargs: Additional context fields

    Returns:
        Fully populated Context object
    """
    # Convert recent_commands if provided as list of dicts
    if recent_commands is None:
        recent_commands = []

    # Create context with sensible defaults
    context = Context(
        active_files=kwargs.get("active_files", []),
        recent_files=kwargs.get("recent_files", []),
        recent_commands=recent_commands,
        command_patterns=kwargs.get("command_patterns", {}),
        primary_project=kwargs.get("primary_project"),
        project_confidence=kwargs.get("project_confidence", 0.0),
        working_directory=kwargs.get("working_directory"),
        session_state=kwargs.get("session_state", SessionState.INACTIVE),
        session_start=kwargs.get("session_start", datetime.now()),
        time_context=kwargs.get("time_context", _get_time_context()),
        current_intent=kwargs.get("current_intent"),
        last_updated=datetime.now(),
    )

    return context


def build_test_context(
    query: str = "",
    user_id: str = "test_user",
    **kwargs
) -> Context:
    """
    Build a context suitable for testing

    Args:
        query: Query string (metadata)
        user_id: User identifier (metadata)
        **kwargs: Additional context fields

    Returns:
        Test context object
    """
    return build_context(
        user_id=user_id,
        query=query,
        **kwargs
    )


def ensure_context(context: Union[Dict[str, Any], Context]) -> Context:
    """
    Ensure we have a proper Context object

    If given a dict, converts it to Context.
    If given a Context, returns it as-is.

    Args:
        context: Dict or Context object

    Returns:
        Proper Context object
    """
    if isinstance(context, Context):
        return context

    if isinstance(context, dict):
        # Extract known fields from dict
        user_id = context.get("user_id", "default_user")
        query = context.get("query", "")

        # Convert recent_commands if present
        recent_commands = []
        if "recent_commands" in context:
            cmds = context["recent_commands"]
            if isinstance(cmds, list):
                # If already CommandActivity objects, use them
                if cmds and isinstance(cmds[0], CommandActivity):
                    recent_commands = cmds
                # Otherwise assume dicts and skip for now
                else:
                    recent_commands = []

        # Build context from dict
        return build_context(
            user_id=user_id,
            query=query,
            recent_commands=recent_commands,
            **{k: v for k, v in context.items()
               if k not in ["user_id", "query", "recent_commands"]}
        )

    # Fallback: create default context
    return build_context()


def build_command_context(
    command: str,
    success: bool = True,
    duration_ms: float = 100.0,
    exit_code: int = 0,
    user_id: str = "default_user",
) -> Context:
    """
    Build context for a command execution

    Args:
        command: Command that was executed
        success: Whether command succeeded
        duration_ms: Execution duration
        exit_code: Command exit code
        user_id: User identifier (metadata)

    Returns:
        Context with command history
    """
    # Create command record
    cmd = CommandActivity(
        command=command,
        timestamp=datetime.now(),
        success=success,
        duration_ms=duration_ms,
        exit_code=exit_code,
    )

    # Infer session state based on success
    session_state = SessionState.HIGH_FOCUS if success else SessionState.FRUSTRATED

    # Build context with command
    context = build_context(
        user_id=user_id,
        recent_commands=[cmd],
        session_state=session_state,
    )

    return context


def build_multi_command_context(
    commands: List[tuple],
    user_id: str = "default_user",
) -> Context:
    """
    Build context with multiple commands in history

    Args:
        commands: List of (command, success, duration_ms, exit_code) tuples
        user_id: User identifier (metadata)

    Returns:
        Context with command history
    """
    # Build command records
    cmd_records = []
    success_count = 0

    for command, success, duration_ms, exit_code in commands:
        cmd = CommandActivity(
            command=command,
            timestamp=datetime.now(),
            success=success,
            duration_ms=duration_ms,
            exit_code=exit_code,
        )
        cmd_records.append(cmd)

        if success:
            success_count += 1

    # Infer session state based on success rate
    success_rate = success_count / len(commands) if commands else 0.0

    if success_rate < 0.5:
        # Many failures - frustrated
        session_state = SessionState.FRUSTRATED
    elif success_rate > 0.8:
        # Mostly success - high focus
        session_state = SessionState.HIGH_FOCUS
    else:
        # Mixed - exploring
        session_state = SessionState.EXPLORING

    # Build context
    context = build_context(
        user_id=user_id,
        recent_commands=cmd_records,
        session_state=session_state,
    )

    return context


def _get_time_context() -> TimeContext:
    """Get current time context based on hour of day"""
    hour = datetime.now().hour

    if 6 <= hour < 12:
        return TimeContext.MORNING
    elif 12 <= hour < 18:
        return TimeContext.AFTERNOON
    elif 18 <= hour < 22:
        return TimeContext.EVENING
    else:
        return TimeContext.LATE_NIGHT
