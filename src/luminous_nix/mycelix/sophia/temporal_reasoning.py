"""
Temporal Reasoning Engine - Revolutionary Time-Aware Intelligence

Makes Sophia understand TIME and RHYTHMS:
- When do we work best? (optimal timing)
- What patterns repeat? (rhythmic cycles)
- What's happening over time? (temporal trends)
- When should we do X? (timing recommendations)
- How do things change? (temporal evolution)

This is paradigm-shifting because most AI is time-blind - Sophia understands
our natural rhythms and works WITH time, not against it.

Example:
"We're most productive 9-11am on Tuesdays"
"Our error rate increases after 2 hours of focus"
"This type of task works best in morning peak"
"We should take a break - our rhythm is dipping"
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, time
from enum import Enum
from typing import List, Optional, Dict, Tuple
from collections import defaultdict
import statistics

from ..context import Context, CommandActivity, FileActivity, SessionState


class TemporalPattern(Enum):
    """Type of temporal pattern"""
    DAILY_RHYTHM = "daily_rhythm"              # Daily cycle (circadian)
    WEEKLY_RHYTHM = "weekly_rhythm"            # Weekly pattern
    SESSION_RHYTHM = "session_rhythm"          # Within-session pattern
    SEASONAL = "seasonal"                      # Long-term cycles
    ULTRADIAN = "ultradian"                    # 90-120 min cycles


class TimeOfDay(Enum):
    """Granular time-of-day categories"""
    EARLY_MORNING = "early_morning"      # 6-8am: Fresh start
    MORNING_PEAK = "morning_peak"        # 8-11am: Peak cognitive
    LATE_MORNING = "late_morning"        # 11am-12pm: Pre-lunch
    LUNCH_TIME = "lunch_time"            # 12-1pm: Break time
    EARLY_AFTERNOON = "early_afternoon"  # 1-3pm: Post-lunch dip
    AFTERNOON_PEAK = "afternoon_peak"    # 3-5pm: Second wind
    EVENING = "evening"                  # 5-8pm: Winding down
    NIGHT = "night"                      # 8pm-12am: Late work
    LATE_NIGHT = "late_night"           # 12am-6am: Very late


class DayOfWeek(Enum):
    """Day of week awareness"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class TemporalEvent:
    """An event with temporal context"""
    timestamp: datetime
    event_type: str  # "command", "error", "success", "break", etc.
    event_data: Dict
    context_snapshot: Optional[Context] = None


@dataclass
class RhythmicPattern:
    """A discovered rhythmic pattern"""
    pattern_type: TemporalPattern
    description: str

    # Pattern characteristics
    cycle_length: timedelta  # How long is one cycle?
    peak_times: List[time]   # When does this peak?
    trough_times: List[time] # When does this dip?

    # Evidence
    observations: int        # How many cycles observed
    confidence: float        # 0.0-1.0
    evidence: List[str]

    # Impact
    productivity_multiplier: float  # 1.0 = baseline, >1 = better, <1 = worse


@dataclass
class TemporalTrend:
    """A trend over time"""
    metric: str              # What's changing? "productivity", "errors", etc.
    direction: str           # "increasing", "decreasing", "stable"
    magnitude: float         # How much? (percentage change)
    timeframe: timedelta     # Over what period?
    confidence: float
    evidence: List[str]


@dataclass
class TimingRecommendation:
    """When to do something"""
    task_type: str           # What should we do?
    optimal_time: time       # When is best?
    optimal_day: Optional[DayOfWeek]
    reason: str              # Why this timing?
    expected_benefit: str    # What improvement?
    confidence: float


@dataclass
class TemporalAnalysis:
    """Complete temporal understanding"""
    timestamp: datetime

    # Current temporal state
    current_time_of_day: TimeOfDay
    current_day: DayOfWeek
    session_duration: timedelta

    # Discovered patterns
    rhythmic_patterns: List[RhythmicPattern]
    temporal_trends: List[TemporalTrend]

    # Recommendations
    timing_recommendations: List[TimingRecommendation]

    # Current state assessment
    current_productivity_estimate: float  # 0.0-1.0 based on rhythms
    optimal_task_types_now: List[str]
    suboptimal_task_types_now: List[str]

    # Meta
    confidence: float
    analysis_notes: List[str]


class TemporalReasoningEngine:
    """
    Revolutionary Temporal Reasoning Engine

    Enables Sophia to understand TIME and work WITH our natural rhythms:
    - Daily circadian rhythms
    - Weekly patterns
    - Session-based patterns (ultradian)
    - Long-term trends
    - Optimal timing for different tasks

    This transforms Sophia from time-blind to time-aware partnership.
    """

    def __init__(self):
        # Event history for temporal analysis
        self.temporal_history: List[TemporalEvent] = []

        # Discovered patterns
        self.discovered_rhythms: List[RhythmicPattern] = []

        # Performance by time (for learning)
        self.performance_by_hour: Dict[int, List[float]] = defaultdict(list)
        self.performance_by_day: Dict[int, List[float]] = defaultdict(list)

        # Session tracking
        self.session_starts: List[datetime] = []
        self.session_productivity: List[Tuple[timedelta, float]] = []

    def record_event(
        self,
        event_type: str,
        event_data: Dict,
        context: Optional[Context] = None
    ):
        """
        Record a temporal event for pattern learning

        Args:
            event_type: Type of event ("command", "error", "success", etc.)
            event_data: Event-specific data
            context: Current context snapshot
        """
        event = TemporalEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            event_data=event_data,
            context_snapshot=context
        )

        self.temporal_history.append(event)

        # Update performance tracking if this is a measurable event
        if event_type == "command":
            success = event_data.get("success", True)
            hour = event.timestamp.hour
            day = event.timestamp.weekday()

            performance = 1.0 if success else 0.0
            self.performance_by_hour[hour].append(performance)
            self.performance_by_day[day].append(performance)

    def analyze_temporal_state(
        self,
        context: Optional[Context] = None,
        current_time: Optional[datetime] = None
    ) -> TemporalAnalysis:
        """
        Analyze complete temporal state

        Args:
            context: Current session context
            current_time: Current time (for testing)

        Returns:
            TemporalAnalysis with complete time understanding
        """
        now = current_time or datetime.now()

        # Determine current temporal position
        time_of_day = self._classify_time_of_day(now.time())
        day_of_week = DayOfWeek(now.weekday())

        # Calculate session duration
        session_duration = timedelta(0)
        if context and context.session_start:
            session_duration = now - context.session_start

        # Discover rhythmic patterns
        rhythmic_patterns = self._discover_rhythmic_patterns()

        # Identify temporal trends
        temporal_trends = self._identify_temporal_trends()

        # Generate timing recommendations
        timing_recommendations = self._generate_timing_recommendations()

        # Estimate current productivity based on rhythms
        current_productivity = self._estimate_current_productivity(now)

        # Determine optimal/suboptimal task types for now
        optimal_tasks, suboptimal_tasks = self._classify_task_timing(
            time_of_day,
            current_productivity
        )

        # Calculate confidence
        confidence = self._calculate_temporal_confidence()

        # Generate notes
        notes = []
        if current_productivity < 0.5:
            notes.append("We're in a natural low-energy period - this is expected")
        if session_duration > timedelta(hours=2):
            notes.append("Long session - ultradian rhythm suggests a break soon")
        if len(rhythmic_patterns) < 3:
            notes.append("Still learning our rhythms - patterns will improve with more data")

        return TemporalAnalysis(
            timestamp=now,
            current_time_of_day=time_of_day,
            current_day=day_of_week,
            session_duration=session_duration,
            rhythmic_patterns=rhythmic_patterns,
            temporal_trends=temporal_trends,
            timing_recommendations=timing_recommendations,
            current_productivity_estimate=current_productivity,
            optimal_task_types_now=optimal_tasks,
            suboptimal_task_types_now=suboptimal_tasks,
            confidence=confidence,
            analysis_notes=notes
        )

    def _classify_time_of_day(self, current_time: time) -> TimeOfDay:
        """Classify current time into granular category"""
        hour = current_time.hour

        if 6 <= hour < 8:
            return TimeOfDay.EARLY_MORNING
        elif 8 <= hour < 11:
            return TimeOfDay.MORNING_PEAK
        elif 11 <= hour < 12:
            return TimeOfDay.LATE_MORNING
        elif 12 <= hour < 13:
            return TimeOfDay.LUNCH_TIME
        elif 13 <= hour < 15:
            return TimeOfDay.EARLY_AFTERNOON
        elif 15 <= hour < 17:
            return TimeOfDay.AFTERNOON_PEAK
        elif 17 <= hour < 20:
            return TimeOfDay.EVENING
        elif 20 <= hour < 24:
            return TimeOfDay.NIGHT
        else:  # 0-6
            return TimeOfDay.LATE_NIGHT

    def _discover_rhythmic_patterns(self) -> List[RhythmicPattern]:
        """Discover rhythmic patterns in our work"""
        patterns = []

        # Daily rhythm (based on hour-by-hour performance)
        if len(self.performance_by_hour) > 0:
            daily_pattern = self._analyze_daily_rhythm()
            if daily_pattern:
                patterns.append(daily_pattern)

        # Weekly rhythm (based on day-by-day performance)
        if len(self.performance_by_day) > 0:
            weekly_pattern = self._analyze_weekly_rhythm()
            if weekly_pattern:
                patterns.append(weekly_pattern)

        # Ultradian rhythm (90-120 minute cycles within sessions)
        ultradian_pattern = self._analyze_ultradian_rhythm()
        if ultradian_pattern:
            patterns.append(ultradian_pattern)

        return patterns

    def _analyze_daily_rhythm(self) -> Optional[RhythmicPattern]:
        """Analyze daily (circadian) rhythm"""
        # Find peak and trough hours
        hourly_avg = {}
        for hour, performances in self.performance_by_hour.items():
            if len(performances) >= 3:  # Need at least 3 samples
                hourly_avg[hour] = statistics.mean(performances)

        if len(hourly_avg) < 4:  # Need data from multiple hours
            return None

        # Find peaks and troughs
        sorted_hours = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [time(hour=h) for h, _ in sorted_hours[:2]]
        trough_hours = [time(hour=h) for h, _ in sorted_hours[-2:]]

        # Calculate productivity multiplier
        avg_performance = statistics.mean(hourly_avg.values())
        peak_performance = sorted_hours[0][1]
        multiplier = peak_performance / avg_performance if avg_performance > 0 else 1.0

        return RhythmicPattern(
            pattern_type=TemporalPattern.DAILY_RHYTHM,
            description=f"We're most productive around {peak_hours[0].hour}:00",
            cycle_length=timedelta(hours=24),
            peak_times=peak_hours,
            trough_times=trough_hours,
            observations=sum(len(p) for p in self.performance_by_hour.values()),
            confidence=min(0.9, len(hourly_avg) / 12),  # More hours = higher confidence
            evidence=[f"Success rate at {h}:00 is {p:.0%}" for h, p in sorted_hours[:3]],
            productivity_multiplier=multiplier
        )

    def _analyze_weekly_rhythm(self) -> Optional[RhythmicPattern]:
        """Analyze weekly rhythm"""
        # Find peak and trough days
        daily_avg = {}
        for day, performances in self.performance_by_day.items():
            if len(performances) >= 3:
                daily_avg[day] = statistics.mean(performances)

        if len(daily_avg) < 3:
            return None

        sorted_days = sorted(daily_avg.items(), key=lambda x: x[1], reverse=True)

        # Map day numbers to names
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        best_day = day_names[sorted_days[0][0]]

        return RhythmicPattern(
            pattern_type=TemporalPattern.WEEKLY_RHYTHM,
            description=f"We're most productive on {best_day}s",
            cycle_length=timedelta(days=7),
            peak_times=[],  # Not hour-specific
            trough_times=[],
            observations=sum(len(p) for p in self.performance_by_day.values()),
            confidence=min(0.8, len(daily_avg) / 7),
            evidence=[f"{day_names[d]}: {p:.0%} success rate" for d, p in sorted_days],
            productivity_multiplier=1.0
        )

    def _analyze_ultradian_rhythm(self) -> Optional[RhythmicPattern]:
        """Analyze ultradian (90-120 min) rhythm within sessions"""
        # This would require more sophisticated session tracking
        # For now, return a generic pattern based on known research
        if len(self.temporal_history) < 20:
            return None

        return RhythmicPattern(
            pattern_type=TemporalPattern.ULTRADIAN,
            description="Energy peaks in 90-minute cycles within sessions",
            cycle_length=timedelta(minutes=90),
            peak_times=[],
            trough_times=[],
            observations=len(self.temporal_history),
            confidence=0.6,  # Based on research, not our specific data yet
            evidence=["General ultradian rhythm pattern"],
            productivity_multiplier=1.0
        )

    def _identify_temporal_trends(self) -> List[TemporalTrend]:
        """Identify trends over time"""
        trends = []

        # Look at recent vs older history
        if len(self.temporal_history) > 20:
            midpoint = len(self.temporal_history) // 2
            older_events = self.temporal_history[:midpoint]
            recent_events = self.temporal_history[midpoint:]

            # Count successes in each half
            older_successes = sum(
                1 for e in older_events
                if e.event_type == "command" and e.event_data.get("success")
            )
            recent_successes = sum(
                1 for e in recent_events
                if e.event_type == "command" and e.event_data.get("success")
            )

            older_total = sum(1 for e in older_events if e.event_type == "command")
            recent_total = sum(1 for e in recent_events if e.event_type == "command")

            if older_total > 0 and recent_total > 0:
                older_rate = older_successes / older_total
                recent_rate = recent_successes / recent_total
                change = (recent_rate - older_rate) / older_rate if older_rate > 0 else 0

                if abs(change) > 0.1:  # At least 10% change
                    direction = "increasing" if change > 0 else "decreasing"
                    trends.append(TemporalTrend(
                        metric="success_rate",
                        direction=direction,
                        magnitude=abs(change),
                        timeframe=recent_events[-1].timestamp - recent_events[0].timestamp,
                        confidence=0.7,
                        evidence=[f"Recent: {recent_rate:.0%}, Earlier: {older_rate:.0%}"]
                    ))

        return trends

    def _generate_timing_recommendations(self) -> List[TimingRecommendation]:
        """Generate recommendations for when to do things"""
        recommendations = []

        # Based on discovered daily rhythm
        if len(self.performance_by_hour) > 0:
            # Find best hour
            hourly_avg = {
                hour: statistics.mean(perfs)
                for hour, perfs in self.performance_by_hour.items()
                if len(perfs) >= 3
            }

            if hourly_avg:
                best_hour = max(hourly_avg.items(), key=lambda x: x[1])[0]
                recommendations.append(TimingRecommendation(
                    task_type="Complex problem-solving",
                    optimal_time=time(hour=best_hour),
                    optimal_day=None,
                    reason=f"Our success rate peaks around {best_hour}:00",
                    expected_benefit="30-50% higher success rate",
                    confidence=0.8
                ))

        # Generic research-based recommendations
        recommendations.append(TimingRecommendation(
            task_type="Deep focus work",
            optimal_time=time(hour=9),
            optimal_day=None,
            reason="Morning cognitive peak (general pattern)",
            expected_benefit="Maximum concentration and clarity",
            confidence=0.6
        ))

        recommendations.append(TimingRecommendation(
            task_type="Routine tasks",
            optimal_time=time(hour=14),
            optimal_day=None,
            reason="Post-lunch dip - better for familiar work",
            expected_benefit="Matches lower energy level",
            confidence=0.6
        ))

        return recommendations

    def _estimate_current_productivity(self, current_time: datetime) -> float:
        """Estimate current productivity based on temporal patterns"""
        hour = current_time.hour

        # If we have historical data for this hour
        if hour in self.performance_by_hour and len(self.performance_by_hour[hour]) >= 3:
            return statistics.mean(self.performance_by_hour[hour])

        # Otherwise use circadian pattern approximation
        # Peak at 10am and 3pm, dip at 2pm and late night
        if 9 <= hour <= 11:
            return 0.9  # Morning peak
        elif 15 <= hour <= 17:
            return 0.8  # Afternoon peak
        elif 13 <= hour <= 15:
            return 0.5  # Post-lunch dip
        elif hour >= 22 or hour <= 5:
            return 0.4  # Late night/early morning
        else:
            return 0.7  # Baseline

    def _classify_task_timing(
        self,
        time_of_day: TimeOfDay,
        productivity: float
    ) -> Tuple[List[str], List[str]]:
        """Determine what tasks are optimal/suboptimal now"""

        # High productivity times
        if productivity > 0.7:
            optimal = [
                "Complex problem-solving",
                "Creative work",
                "Learning new concepts",
                "Critical decisions"
            ]
            suboptimal = [
                "Routine emails",
                "Administrative tasks"
            ]
        # Medium productivity times
        elif productivity > 0.5:
            optimal = [
                "Code review",
                "Documentation",
                "Planning",
                "Collaboration"
            ]
            suboptimal = [
                "Complex debugging",
                "Architecture decisions"
            ]
        # Low productivity times
        else:
            optimal = [
                "Routine tasks",
                "Organizing",
                "Reading",
                "Light research"
            ]
            suboptimal = [
                "Complex problem-solving",
                "Critical decisions",
                "Learning new concepts"
            ]

        return optimal, suboptimal

    def _calculate_temporal_confidence(self) -> float:
        """Calculate confidence in temporal analysis"""
        # Based on amount of historical data
        if len(self.temporal_history) < 10:
            return 0.3
        elif len(self.temporal_history) < 50:
            return 0.5
        elif len(self.temporal_history) < 100:
            return 0.7
        else:
            return 0.9

    def get_rhythm_summary(self) -> str:
        """Get human-readable summary of our rhythms"""
        patterns = self._discover_rhythmic_patterns()

        if not patterns:
            return "Still learning our rhythms - need more interaction to discover patterns."

        parts = ["Our discovered rhythms:\n"]

        for pattern in patterns:
            parts.append(f"\n• {pattern.description}")
            if pattern.peak_times:
                peak_str = ", ".join(t.strftime("%I:%M %p") for t in pattern.peak_times)
                parts.append(f"  Peak: {peak_str}")
            parts.append(f"  Confidence: {pattern.confidence:.0%}")

        return "".join(parts)


# Global singleton
_temporal_reasoning_engine: Optional[TemporalReasoningEngine] = None


def get_temporal_reasoning_engine() -> TemporalReasoningEngine:
    """Get the global temporal reasoning engine singleton"""
    global _temporal_reasoning_engine
    if _temporal_reasoning_engine is None:
        _temporal_reasoning_engine = TemporalReasoningEngine()
    return _temporal_reasoning_engine
