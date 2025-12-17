"""
TCDM (Temporal Consistency Distribution Metric) Calculator

Measures the consistency and naturalness of user interaction timing patterns.
Higher scores indicate more human-like, consistent temporal behavior.

Components:
- Inter-arrival time consistency (regular vs erratic)
- Session pattern detection (natural breaks)
- Circadian rhythm alignment (day/night patterns)
"""

from typing import List
from datetime import datetime, timedelta
import statistics
import logging

from .matl_types import Interaction

logger = logging.getLogger(__name__)


class TCDMCalculator:
    """
    Calculate Temporal Consistency Distribution Metric (TCDM) score.

    Score Range: 0.0-1.0
    - 0.0: Erratic, bot-like timing
    - 0.5: Neutral, average
    - 1.0: Highly consistent, human-like timing
    """

    def __init__(self):
        # Minimum interactions needed for reliable score
        self.min_interactions = 5

        # Typical human parameters
        self.min_human_interval_seconds = 2.0  # < 2s is suspicious (too fast)
        self.max_session_gap_minutes = 30  # > 30min indicates new session
        self.typical_sleep_hours = (22, 7)  # 10pm - 7am (local time)

    def calculate(self, interactions: List[Interaction]) -> float:
        """
        Calculate TCDM score from user interactions.

        Args:
            interactions: List of user interactions (must be time-sorted)

        Returns:
            float: TCDM score (0.0-1.0)
        """
        if not interactions:
            return 0.0

        if len(interactions) < self.min_interactions:
            # Not enough data, return neutral score
            return 0.5

        # Sort interactions by timestamp (ensure chronological order)
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)

        # Calculate sub-components
        interval_consistency = self._calculate_interval_consistency(sorted_interactions)
        session_naturalness = self._calculate_session_naturalness(sorted_interactions)
        circadian_alignment = self._calculate_circadian_alignment(sorted_interactions)

        # Weighted combination
        # Interval consistency is most important (50%)
        # Session naturalness is secondary (30%)
        # Circadian alignment is tertiary (20%)
        tcdm = (
            0.5 * interval_consistency +
            0.3 * session_naturalness +
            0.2 * circadian_alignment
        )

        return max(0.0, min(1.0, tcdm))  # Clamp to [0, 1]

    def _calculate_interval_consistency(self, interactions: List[Interaction]) -> float:
        """
        Calculate inter-arrival time consistency.

        Measures:
        - Coefficient of variation (CV) of intervals
        - Detection of bot-like perfectly regular timing
        - Detection of suspiciously fast actions

        Returns:
            float: Interval consistency score (0.0-1.0)
        """
        if len(interactions) < 2:
            return 0.5

        # Calculate inter-arrival times (in seconds)
        intervals = []
        for i in range(1, len(interactions)):
            delta = interactions[i].timestamp - interactions[i-1].timestamp
            intervals.append(delta.total_seconds())

        # Check for suspiciously fast actions (<2s)
        fast_actions = sum(1 for interval in intervals if interval < self.min_human_interval_seconds)
        fast_action_ratio = fast_actions / len(intervals)

        # Penalize if too many fast actions (>30% is suspicious)
        fast_penalty = 0.0
        if fast_action_ratio > 0.3:
            fast_penalty = (fast_action_ratio - 0.3) * 1.5  # Scale to penalty

        # Calculate coefficient of variation (std dev / mean)
        # Low CV = very regular (bot-like), High CV = erratic
        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return 0.0

        std_dev = statistics.stdev(intervals) if len(intervals) > 1 else 0.0
        cv = std_dev / mean_interval

        # Ideal CV for human behavior: 0.3-0.8
        # Too low (< 0.2) = bot-like regularity
        # Too high (> 1.5) = erratic/random
        cv_score = 0.0
        if cv < 0.2:
            # Too regular - bot-like
            cv_score = cv / 0.2 * 0.5  # Scale to [0, 0.5]
        elif 0.2 <= cv <= 0.8:
            # Ideal human range
            cv_score = 1.0
        elif 0.8 < cv <= 1.5:
            # Slightly erratic but acceptable
            cv_score = 1.0 - ((cv - 0.8) / 0.7) * 0.3  # Scale from 1.0 to 0.7
        else:
            # Too erratic
            cv_score = max(0.0, 0.7 - (cv - 1.5) * 0.2)

        # Combine metrics
        consistency = (
            0.6 * cv_score +
            0.4 * (1.0 - fast_penalty)
        )

        return max(0.0, min(1.0, consistency))

    def _calculate_session_naturalness(self, interactions: List[Interaction]) -> float:
        """
        Calculate session pattern naturalness.

        Measures:
        - Natural session breaks (gaps > 30min)
        - Reasonable session durations
        - Absence of 24/7 activity

        Returns:
            float: Session naturalness score (0.0-1.0)
        """
        if len(interactions) < self.min_interactions:
            return 0.5

        # Detect sessions (gaps > 30 minutes indicate new session)
        sessions = []
        current_session = [interactions[0]]

        for i in range(1, len(interactions)):
            time_gap = (interactions[i].timestamp - interactions[i-1].timestamp).total_seconds() / 60
            if time_gap > self.max_session_gap_minutes:
                # New session
                sessions.append(current_session)
                current_session = [interactions[i]]
            else:
                current_session.append(interactions[i])

        # Add last session
        sessions.append(current_session)

        # Calculate session metrics
        session_durations = []
        for session in sessions:
            if len(session) > 1:
                duration = (session[-1].timestamp - session[0].timestamp).total_seconds() / 60
                session_durations.append(duration)

        # Average session duration
        if not session_durations:
            return 0.5

        avg_session_duration = statistics.mean(session_durations)

        # Typical human session: 5-60 minutes
        session_duration_score = 0.0
        if 5 <= avg_session_duration <= 60:
            session_duration_score = 1.0
        elif avg_session_duration < 5:
            # Too short - suspicious
            session_duration_score = avg_session_duration / 5.0
        else:
            # Too long - possibly automated
            session_duration_score = max(0.0, 1.0 - (avg_session_duration - 60) / 120)

        # Number of sessions
        total_time_span = (interactions[-1].timestamp - interactions[0].timestamp).total_seconds() / 3600  # hours
        sessions_per_day = len(sessions) / (total_time_span / 24) if total_time_span > 0 else 0

        # Typical human: 1-5 sessions per day
        session_frequency_score = 0.0
        if 1 <= sessions_per_day <= 5:
            session_frequency_score = 1.0
        elif sessions_per_day < 1:
            session_frequency_score = sessions_per_day
        else:
            # Too many sessions - suspicious
            session_frequency_score = max(0.0, 1.0 - (sessions_per_day - 5) / 10)

        # Combine
        naturalness = (
            0.6 * session_duration_score +
            0.4 * session_frequency_score
        )

        return max(0.0, min(1.0, naturalness))

    def _calculate_circadian_alignment(self, interactions: List[Interaction]) -> float:
        """
        Calculate circadian rhythm alignment.

        Measures:
        - Activity during typical waking hours
        - Reduced activity during sleep hours (10pm - 7am)
        - Natural day/night pattern

        Returns:
            float: Circadian alignment score (0.0-1.0)
        """
        if len(interactions) < self.min_interactions:
            return 0.5

        # Count interactions during sleep hours (10pm - 7am)
        sleep_start, sleep_end = self.typical_sleep_hours
        sleep_interactions = 0
        wake_interactions = 0

        for interaction in interactions:
            hour = interaction.timestamp.hour
            if sleep_start <= hour or hour < sleep_end:
                sleep_interactions += 1
            else:
                wake_interactions += 1

        total = len(interactions)
        sleep_ratio = sleep_interactions / total

        # Ideal: <20% during sleep hours
        # Suspicious: >50% during sleep hours (no sleep = bot)
        circadian_score = 0.0
        if sleep_ratio <= 0.2:
            circadian_score = 1.0
        elif sleep_ratio <= 0.5:
            # Acceptable but not ideal (shift workers, etc.)
            circadian_score = 1.0 - ((sleep_ratio - 0.2) / 0.3) * 0.3  # Scale to 0.7-1.0
        else:
            # Too much sleep-time activity - suspicious
            circadian_score = max(0.0, 0.7 - (sleep_ratio - 0.5) * 1.4)

        return max(0.0, min(1.0, circadian_score))

    def get_explanation(self, interactions: List[Interaction]) -> dict:
        """
        Get detailed explanation of TCDM score.

        Returns:
            dict: Score breakdown with explanations
        """
        if not interactions:
            return {
                'score': 0.0,
                'message': 'No interactions yet',
                'components': {}
            }

        score = self.calculate(interactions)
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)

        interval_consistency = self._calculate_interval_consistency(sorted_interactions)
        session_naturalness = self._calculate_session_naturalness(sorted_interactions)
        circadian_alignment = self._calculate_circadian_alignment(sorted_interactions)

        return {
            'score': score,
            'components': {
                'interval_consistency': {
                    'score': interval_consistency,
                    'weight': 0.5,
                    'description': 'Inter-arrival time consistency and naturalness'
                },
                'session_naturalness': {
                    'score': session_naturalness,
                    'weight': 0.3,
                    'description': 'Natural session patterns and breaks'
                },
                'circadian_alignment': {
                    'score': circadian_alignment,
                    'weight': 0.2,
                    'description': 'Alignment with natural day/night rhythms'
                }
            },
            'interpretation': self._interpret_score(score),
            'interactions_analyzed': len(interactions)
        }

    def _interpret_score(self, score: float) -> str:
        """Interpret TCDM score for users"""
        if score >= 0.8:
            return "Excellent - Highly consistent human-like patterns"
        elif score >= 0.6:
            return "Good - Natural temporal behavior"
        elif score >= 0.4:
            return "Fair - Some irregular patterns"
        else:
            return "Low - Unusual temporal patterns detected"
