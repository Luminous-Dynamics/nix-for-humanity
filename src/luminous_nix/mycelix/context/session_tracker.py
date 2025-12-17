"""
Session Tracker - Monitors session state and energy

Tracks session metrics to understand user's current state:
- How long they've been working
- Activity patterns
- Energy level indicators
- Time context (morning, afternoon, etc.)
"""

import logging
from datetime import datetime, timedelta, time
from typing import Optional

from .types import SessionState, TimeContext
from .command_tracker import CommandTracker

logger = logging.getLogger(__name__)


class SessionTracker:
    """
    Track session state and user energy

    Features:
    - Session duration tracking
    - Activity pattern analysis
    - Energy level detection
    - Time-based context
    """

    def __init__(
        self,
        command_tracker: CommandTracker,
        inactivity_threshold_minutes: int = 15
    ):
        """
        Initialize session tracker

        Args:
            command_tracker: CommandTracker for activity patterns
            inactivity_threshold_minutes: Minutes of no activity = inactive
        """
        self.command_tracker = command_tracker
        self.inactivity_threshold = timedelta(minutes=inactivity_threshold_minutes)

        self.session_start = datetime.now()
        self._last_activity = datetime.now()

    def get_session_duration(self) -> timedelta:
        """
        Get current session duration

        Returns:
            Time since session start
        """
        return datetime.now() - self.session_start

    def get_time_context(self) -> TimeContext:
        """
        Get current time context

        Returns:
            TimeContext enum value
        """
        now = datetime.now()
        hour = now.hour

        if 6 <= hour < 12:
            return TimeContext.MORNING
        elif 12 <= hour < 18:
            return TimeContext.AFTERNOON
        elif 18 <= hour < 22:
            return TimeContext.EVENING
        else:
            return TimeContext.LATE_NIGHT

    def detect_session_state(self) -> SessionState:
        """
        Detect current session state from activity patterns

        Returns:
            SessionState enum value
        """
        # Check for inactivity first
        time_since_activity = datetime.now() - self._last_activity
        if time_since_activity > self.inactivity_threshold:
            return SessionState.INACTIVE

        # Analyze recent command patterns
        recent_commands = self.command_tracker.get_recent_commands(limit=10)

        if not recent_commands:
            return SessionState.INACTIVE

        # Update last activity time
        self._last_activity = datetime.now()

        # Check for frustration indicators
        if self.command_tracker.detect_frustration_pattern():
            logger.info("Detected frustration pattern")
            return SessionState.FRUSTRATED

        # Analyze command frequency and type
        recent_minutes = 10
        cutoff = datetime.now() - timedelta(minutes=recent_minutes)
        very_recent = [
            cmd for cmd in recent_commands
            if cmd.timestamp >= cutoff
        ]

        commands_per_minute = len(very_recent) / recent_minutes

        # High activity = high focus or exploring
        if commands_per_minute > 1.0:
            # Lots of different commands = exploring
            unique_commands = len(set(cmd.command for cmd in very_recent))
            if unique_commands / len(very_recent) > 0.7:
                return SessionState.EXPLORING
            else:
                # Focused on specific task
                return SessionState.HIGH_FOCUS

        # Medium activity - check for patterns
        if commands_per_minute > 0.3:
            # Check for slow down over time (tired?)
            if len(recent_commands) >= 6:
                first_half = recent_commands[-6:-3]
                second_half = recent_commands[-3:]

                first_half_time = (first_half[-1].timestamp - first_half[0].timestamp).total_seconds()
                second_half_time = (second_half[-1].timestamp - second_half[0].timestamp).total_seconds()

                # Slowing down significantly
                if second_half_time > first_half_time * 1.5:
                    return SessionState.TIRED

            return SessionState.HIGH_FOCUS

        # Low activity but not inactive
        # Check session duration - long sessions may indicate tiredness
        session_hours = self.get_session_duration().total_seconds() / 3600
        if session_hours > 4:
            return SessionState.TIRED

        return SessionState.EXPLORING

    def update_activity(self):
        """Update last activity timestamp"""
        self._last_activity = datetime.now()

    def get_focus_duration(self) -> Optional[timedelta]:
        """
        Get duration of current focus session

        Returns:
            Time in current state, or None if inactive
        """
        state = self.detect_session_state()
        if state == SessionState.INACTIVE:
            return None

        # This is simplified - in production, track state transitions
        time_since_activity = datetime.now() - self._last_activity
        return time_since_activity

    def should_suggest_break(self) -> bool:
        """
        Determine if user should take a break

        Returns:
            True if break recommended
        """
        # Suggest break if:
        # - Session over 2 hours
        # - User appears tired
        # - Late night coding

        session_hours = self.get_session_duration().total_seconds() / 3600
        state = self.detect_session_state()
        time_context = self.get_time_context()

        return (
            session_hours > 2.0 or
            state == SessionState.TIRED or
            (time_context == TimeContext.LATE_NIGHT and session_hours > 1.0)
        )

    def get_stats(self) -> dict:
        """
        Get session statistics

        Returns:
            Dictionary of session stats
        """
        duration = self.get_session_duration()
        state = self.detect_session_state()
        time_ctx = self.get_time_context()

        return {
            "session_duration_minutes": duration.total_seconds() / 60,
            "session_state": state.value,
            "time_context": time_ctx.value,
            "suggest_break": self.should_suggest_break(),
            "minutes_since_activity": (datetime.now() - self._last_activity).total_seconds() / 60
        }

    def reset_session(self):
        """Reset session tracking (new session)"""
        self.session_start = datetime.now()
        self._last_activity = datetime.now()
        logger.info("Session reset")
