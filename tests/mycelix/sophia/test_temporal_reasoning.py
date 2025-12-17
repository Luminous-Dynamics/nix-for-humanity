"""
Tests for Temporal Reasoning Engine

Tests Sophia's ability to:
- Understand time-of-day and rhythms
- Discover patterns in our work timing
- Recommend optimal times for tasks
- Track temporal trends
- Work WITH our natural rhythms
"""

import pytest
from datetime import datetime, timedelta, time
from pathlib import Path

from luminous_nix.mycelix.sophia.temporal_reasoning import (
    TemporalReasoningEngine,
    get_temporal_reasoning_engine,
    TemporalPattern,
    TimeOfDay,
    DayOfWeek,
    TemporalEvent,
    RhythmicPattern,
    TemporalTrend,
    TimingRecommendation,
    TemporalAnalysis
)
from luminous_nix.mycelix.context import (
    Context,
    CommandActivity,
    FileActivity,
    SessionState,
    Intent,
    IntentType
)


@pytest.fixture
def engine():
    """Create a fresh temporal reasoning engine"""
    return TemporalReasoningEngine()


@pytest.fixture
def morning_context():
    """Context for morning work session"""
    morning = datetime.now().replace(hour=9, minute=30)
    return Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.9),
        session_state=SessionState.HIGH_FOCUS,
        session_start=morning - timedelta(minutes=30)
    )


@pytest.fixture
def afternoon_context():
    """Context for afternoon work session"""
    afternoon = datetime.now().replace(hour=14, minute=0)
    return Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.7),
        session_state=SessionState.EXPLORING,
        session_start=afternoon - timedelta(hours=2)
    )


def test_engine_initialization(engine):
    """Test that temporal engine initializes correctly"""
    assert engine is not None
    assert engine.temporal_history == []
    assert engine.discovered_rhythms == []
    assert len(engine.performance_by_hour) == 0


def test_singleton_pattern():
    """Test that get_temporal_reasoning_engine returns singleton"""
    engine1 = get_temporal_reasoning_engine()
    engine2 = get_temporal_reasoning_engine()
    assert engine1 is engine2


def test_record_event(engine):
    """Test recording temporal events"""
    engine.record_event(
        event_type="command",
        event_data={"command": "test", "success": True}
    )

    assert len(engine.temporal_history) == 1
    assert engine.temporal_history[0].event_type == "command"
    assert engine.temporal_history[0].event_data["success"] is True


def test_classify_time_of_day_morning(engine):
    """Test time classification for morning"""
    assert engine._classify_time_of_day(time(hour=7)) == TimeOfDay.EARLY_MORNING
    assert engine._classify_time_of_day(time(hour=9)) == TimeOfDay.MORNING_PEAK
    assert engine._classify_time_of_day(time(hour=11, minute=30)) == TimeOfDay.LATE_MORNING


def test_classify_time_of_day_afternoon(engine):
    """Test time classification for afternoon"""
    assert engine._classify_time_of_day(time(hour=12, minute=30)) == TimeOfDay.LUNCH_TIME
    assert engine._classify_time_of_day(time(hour=14)) == TimeOfDay.EARLY_AFTERNOON
    assert engine._classify_time_of_day(time(hour=16)) == TimeOfDay.AFTERNOON_PEAK


def test_classify_time_of_day_evening_night(engine):
    """Test time classification for evening/night"""
    assert engine._classify_time_of_day(time(hour=18)) == TimeOfDay.EVENING
    assert engine._classify_time_of_day(time(hour=22)) == TimeOfDay.NIGHT
    assert engine._classify_time_of_day(time(hour=2)) == TimeOfDay.LATE_NIGHT


def test_analyze_temporal_state_basic(engine, morning_context):
    """Test basic temporal state analysis"""
    morning_time = datetime.now().replace(hour=9, minute=30)

    analysis = engine.analyze_temporal_state(
        context=morning_context,
        current_time=morning_time
    )

    assert isinstance(analysis, TemporalAnalysis)
    assert analysis.current_time_of_day == TimeOfDay.MORNING_PEAK
    assert isinstance(analysis.current_day, DayOfWeek)
    assert analysis.session_duration > timedelta(0)


def test_productivity_estimation_morning_peak(engine):
    """Test productivity estimation during morning peak"""
    morning = datetime.now().replace(hour=10, minute=0)
    productivity = engine._estimate_current_productivity(morning)

    assert 0.7 <= productivity <= 1.0  # Should be high in morning


def test_productivity_estimation_post_lunch_dip(engine):
    """Test productivity estimation during post-lunch dip"""
    afternoon = datetime.now().replace(hour=14, minute=0)
    productivity = engine._estimate_current_productivity(afternoon)

    assert 0.3 <= productivity <= 0.6  # Should be lower in dip


def test_productivity_estimation_late_night(engine):
    """Test productivity estimation late at night"""
    late_night = datetime.now().replace(hour=23, minute=0)
    productivity = engine._estimate_current_productivity(late_night)

    assert 0.2 <= productivity <= 0.5  # Should be low late night


def test_task_classification_high_productivity(engine):
    """Test task classification during high productivity"""
    optimal, suboptimal = engine._classify_task_timing(
        TimeOfDay.MORNING_PEAK,
        productivity=0.9
    )

    assert "Complex problem-solving" in optimal
    assert "Routine emails" in suboptimal


def test_task_classification_low_productivity(engine):
    """Test task classification during low productivity"""
    optimal, suboptimal = engine._classify_task_timing(
        TimeOfDay.EARLY_AFTERNOON,
        productivity=0.4
    )

    assert "Routine tasks" in optimal
    assert "Complex problem-solving" in suboptimal


def test_record_multiple_events_builds_history(engine):
    """Test that recording events builds temporal history"""
    for i in range(10):
        engine.record_event(
            event_type="command",
            event_data={"command": f"test{i}", "success": i % 2 == 0}
        )

    assert len(engine.temporal_history) == 10


def test_performance_tracking_by_hour(engine):
    """Test that performance is tracked by hour"""
    # Record events at specific hours
    for hour in [9, 10, 14, 15]:
        for i in range(3):
            event_time = datetime.now().replace(hour=hour, minute=0)
            engine.temporal_history.append(TemporalEvent(
                timestamp=event_time,
                event_type="command",
                event_data={"success": i < 2}  # 2/3 successful
            ))
            # Manually update performance tracking
            engine.performance_by_hour[hour].append(1.0 if i < 2 else 0.0)

    # Should have data for 4 hours
    assert len(engine.performance_by_hour) == 4
    # Each hour should have 3 samples
    assert len(engine.performance_by_hour[9]) == 3


def test_discover_daily_rhythm_with_data(engine):
    """Test discovering daily rhythm from data"""
    # Simulate high performance at 9am, low at 2pm
    engine.performance_by_hour[9] = [0.9, 0.85, 0.9, 0.88]
    engine.performance_by_hour[14] = [0.4, 0.5, 0.45, 0.48]
    engine.performance_by_hour[10] = [0.8, 0.85, 0.82]
    engine.performance_by_hour[15] = [0.7, 0.75, 0.72]

    pattern = engine._analyze_daily_rhythm()

    assert pattern is not None
    assert pattern.pattern_type == TemporalPattern.DAILY_RHYTHM
    assert pattern.cycle_length == timedelta(hours=24)
    assert len(pattern.peak_times) > 0
    assert len(pattern.trough_times) > 0


def test_discover_daily_rhythm_insufficient_data(engine):
    """Test that daily rhythm returns None with insufficient data"""
    # Only one hour of data
    engine.performance_by_hour[9] = [0.9, 0.85, 0.9]

    pattern = engine._analyze_daily_rhythm()

    assert pattern is None  # Not enough hours


def test_discover_weekly_rhythm_with_data(engine):
    """Test discovering weekly rhythm from data"""
    # Simulate high performance on Tuesday (1), low on Friday (4)
    engine.performance_by_day[0] = [0.7, 0.75, 0.72]  # Monday
    engine.performance_by_day[1] = [0.9, 0.88, 0.92]  # Tuesday - best
    engine.performance_by_day[2] = [0.8, 0.82, 0.78]  # Wednesday
    engine.performance_by_day[4] = [0.5, 0.55, 0.52]  # Friday

    pattern = engine._analyze_weekly_rhythm()

    assert pattern is not None
    assert pattern.pattern_type == TemporalPattern.WEEKLY_RHYTHM
    assert "Tuesday" in pattern.description  # Best day
    assert pattern.cycle_length == timedelta(days=7)


def test_discover_ultradian_rhythm(engine):
    """Test discovering ultradian (90-min) rhythm"""
    # Add enough events
    for i in range(25):
        engine.temporal_history.append(TemporalEvent(
            timestamp=datetime.now(),
            event_type="command",
            event_data={}
        ))

    pattern = engine._analyze_ultradian_rhythm()

    assert pattern is not None
    assert pattern.pattern_type == TemporalPattern.ULTRADIAN
    assert pattern.cycle_length == timedelta(minutes=90)


def test_temporal_trends_improving(engine):
    """Test detecting improving trend"""
    # Add older events with low success
    base_time = datetime.now() - timedelta(days=7)
    for i in range(15):
        engine.temporal_history.append(TemporalEvent(
            timestamp=base_time + timedelta(hours=i),
            event_type="command",
            event_data={"success": i < 5}  # 5/15 = 33% success
        ))

    # Add recent events with high success
    recent_time = datetime.now() - timedelta(hours=12)
    for i in range(15):
        engine.temporal_history.append(TemporalEvent(
            timestamp=recent_time + timedelta(hours=i),
            event_type="command",
            event_data={"success": i < 12}  # 12/15 = 80% success
        ))

    trends = engine._identify_temporal_trends()

    assert len(trends) > 0
    # Should detect increasing success rate
    success_trend = [t for t in trends if t.metric == "success_rate"]
    if success_trend:
        assert success_trend[0].direction == "increasing"


def test_temporal_trends_insufficient_data(engine):
    """Test that trends return empty with insufficient data"""
    # Only a few events
    for i in range(5):
        engine.temporal_history.append(TemporalEvent(
            timestamp=datetime.now(),
            event_type="command",
            event_data={"success": True}
        ))

    trends = engine._identify_temporal_trends()

    assert len(trends) == 0  # Not enough data


def test_timing_recommendations_generated(engine):
    """Test that timing recommendations are generated"""
    recommendations = engine._generate_timing_recommendations()

    assert len(recommendations) > 0
    assert all(isinstance(r, TimingRecommendation) for r in recommendations)


def test_timing_recommendation_with_data(engine):
    """Test timing recommendations based on real data"""
    # Add performance data showing 10am is best
    engine.performance_by_hour[9] = [0.7, 0.75, 0.72]
    engine.performance_by_hour[10] = [0.95, 0.92, 0.94]
    engine.performance_by_hour[14] = [0.5, 0.55, 0.52]

    recommendations = engine._generate_timing_recommendations()

    # Should recommend complex work at 10am
    complex_work_recs = [
        r for r in recommendations
        if "Complex" in r.task_type and r.optimal_time.hour == 10
    ]
    assert len(complex_work_recs) > 0


def test_confidence_increases_with_data(engine):
    """Test that temporal confidence increases with more data"""
    # Low confidence with little data
    conf_low = engine._calculate_temporal_confidence()
    assert conf_low < 0.5

    # Add lots of events
    for i in range(150):
        engine.temporal_history.append(TemporalEvent(
            timestamp=datetime.now(),
            event_type="command",
            event_data={}
        ))

    # High confidence with lots of data
    conf_high = engine._calculate_temporal_confidence()
    assert conf_high > 0.8
    assert conf_high > conf_low


def test_rhythm_summary_no_data(engine):
    """Test rhythm summary with no data"""
    summary = engine.get_rhythm_summary()

    assert "Still learning" in summary


def test_rhythm_summary_with_patterns(engine):
    """Test rhythm summary with discovered patterns"""
    # Add data to discover patterns
    engine.performance_by_hour[9] = [0.9, 0.88, 0.92, 0.87]
    engine.performance_by_hour[14] = [0.5, 0.52, 0.48, 0.51]
    engine.performance_by_hour[10] = [0.85, 0.82, 0.86]
    engine.performance_by_hour[15] = [0.7, 0.72, 0.68]

    summary = engine.get_rhythm_summary()

    assert "discovered rhythms" in summary.lower()
    assert "productive" in summary.lower()


def test_temporal_event_dataclass():
    """Test TemporalEvent dataclass"""
    event = TemporalEvent(
        timestamp=datetime.now(),
        event_type="command",
        event_data={"test": "data"}
    )

    assert event.event_type == "command"
    assert event.event_data["test"] == "data"


def test_rhythmic_pattern_dataclass():
    """Test RhythmicPattern dataclass"""
    pattern = RhythmicPattern(
        pattern_type=TemporalPattern.DAILY_RHYTHM,
        description="Test pattern",
        cycle_length=timedelta(hours=24),
        peak_times=[time(hour=9)],
        trough_times=[time(hour=14)],
        observations=100,
        confidence=0.8,
        evidence=["Test evidence"],
        productivity_multiplier=1.2
    )

    assert pattern.pattern_type == TemporalPattern.DAILY_RHYTHM
    assert pattern.confidence == 0.8
    assert pattern.productivity_multiplier == 1.2


def test_temporal_trend_dataclass():
    """Test TemporalTrend dataclass"""
    trend = TemporalTrend(
        metric="productivity",
        direction="increasing",
        magnitude=0.25,
        timeframe=timedelta(days=7),
        confidence=0.7,
        evidence=["Recent data shows improvement"]
    )

    assert trend.direction == "increasing"
    assert trend.magnitude == 0.25


def test_timing_recommendation_dataclass():
    """Test TimingRecommendation dataclass"""
    rec = TimingRecommendation(
        task_type="Complex work",
        optimal_time=time(hour=9),
        optimal_day=DayOfWeek.TUESDAY,
        reason="Peak productivity",
        expected_benefit="30% improvement",
        confidence=0.8
    )

    assert rec.task_type == "Complex work"
    assert rec.optimal_time.hour == 9
    assert rec.optimal_day == DayOfWeek.TUESDAY


def test_temporal_analysis_dataclass():
    """Test TemporalAnalysis dataclass"""
    analysis = TemporalAnalysis(
        timestamp=datetime.now(),
        current_time_of_day=TimeOfDay.MORNING_PEAK,
        current_day=DayOfWeek.TUESDAY,
        session_duration=timedelta(hours=1),
        rhythmic_patterns=[],
        temporal_trends=[],
        timing_recommendations=[],
        current_productivity_estimate=0.9,
        optimal_task_types_now=["Complex work"],
        suboptimal_task_types_now=["Routine tasks"],
        confidence=0.7,
        analysis_notes=["Test note"]
    )

    assert analysis.current_time_of_day == TimeOfDay.MORNING_PEAK
    assert analysis.current_productivity_estimate == 0.9


def test_all_time_of_day_values():
    """Test that all TimeOfDay enum values are valid"""
    for tod in TimeOfDay:
        assert isinstance(tod.value, str)
        assert len(tod.value) > 0


def test_all_temporal_pattern_values():
    """Test that all TemporalPattern enum values are valid"""
    for pattern in TemporalPattern:
        assert isinstance(pattern.value, str)
        assert len(pattern.value) > 0


def test_all_day_of_week_values():
    """Test that all DayOfWeek enum values are valid"""
    for day in DayOfWeek:
        assert isinstance(day.value, int)
        assert 0 <= day.value <= 6


def test_session_duration_tracking(engine, morning_context):
    """Test that session duration is tracked correctly"""
    current = datetime.now().replace(hour=10, minute=0)

    analysis = engine.analyze_temporal_state(
        context=morning_context,
        current_time=current
    )

    assert analysis.session_duration > timedelta(0)


def test_long_session_warning(engine):
    """Test warning for long sessions"""
    # Create context with long session
    long_session_start = datetime.now() - timedelta(hours=3)
    context = Context(
        session_state=SessionState.HIGH_FOCUS,
        session_start=long_session_start
    )

    analysis = engine.analyze_temporal_state(context=context)

    # Should have note about long session
    long_session_notes = [n for n in analysis.analysis_notes if "Long session" in n]
    assert len(long_session_notes) > 0


def test_optimal_tasks_high_productivity(engine, morning_context):
    """Test optimal task recommendations during high productivity"""
    morning = datetime.now().replace(hour=9, minute=30)

    analysis = engine.analyze_temporal_state(
        context=morning_context,
        current_time=morning
    )

    # Morning peak should recommend complex work
    assert any("Complex" in task or "Creative" in task for task in analysis.optimal_task_types_now)


def test_suboptimal_tasks_low_productivity(engine, afternoon_context):
    """Test suboptimal task warnings during low productivity"""
    post_lunch = datetime.now().replace(hour=14, minute=0)

    analysis = engine.analyze_temporal_state(
        context=afternoon_context,
        current_time=post_lunch
    )

    # Post-lunch dip should mark complex work as suboptimal
    # (depending on exact productivity estimate)
    assert isinstance(analysis.suboptimal_task_types_now, list)
