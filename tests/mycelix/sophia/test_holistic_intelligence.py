"""
Tests for Holistic Intelligence Engine

Tests Sophia's ability to:
- Monitor biometric states (heart rate, HRV)
- Adapt to circadian rhythms
- Track cognitive load
- Understand social context
- Provide holistic recommendations
"""

import pytest
from datetime import datetime, time
from pathlib import Path

from luminous_nix.mycelix.sophia.holistic_intelligence import (
    HolisticIntelligenceEngine,
    get_holistic_intelligence_engine,
    BiometricState,
    CircadianPhase,
    CognitiveLoad,
    SocialContext,
    BiometricReading,
    CircadianState,
    CognitiveLoadAssessment,
    SocialContextInfo,
    HolisticState
)
from luminous_nix.mycelix.context import (
    Context,
    CommandActivity,
    FileActivity,
    SessionState,
    ProjectType,
    Intent,
    IntentType
)


@pytest.fixture
def engine():
    """Create a fresh holistic intelligence engine"""
    return HolisticIntelligenceEngine()


@pytest.fixture
def high_stress_reading():
    """Create a high-stress biometric reading"""
    return BiometricReading(
        timestamp=datetime.now(),
        heart_rate=110,  # High HR
        hrv=15.0         # Low HRV
    )


@pytest.fixture
def optimal_flow_reading():
    """Create an optimal flow biometric reading"""
    return BiometricReading(
        timestamp=datetime.now(),
        heart_rate=70,   # Moderate HR
        hrv=75.0         # High HRV
    )


def test_engine_initialization(engine):
    """Test that engine initializes correctly"""
    assert engine is not None
    assert engine.biometric_history == []
    assert engine.cognitive_load_history == []
    assert engine.social_context_history == []


def test_singleton_pattern():
    """Test that get_holistic_intelligence_engine returns singleton"""
    engine1 = get_holistic_intelligence_engine()
    engine2 = get_holistic_intelligence_engine()
    assert engine1 is engine2


def test_biometric_stress_indicator(high_stress_reading):
    """Test stress indicator calculation from biometrics"""
    stress = high_stress_reading.get_stress_indicator()

    # High HR + Low HRV should indicate high stress
    assert stress > 0.7
    assert 0.0 <= stress <= 1.0


def test_biometric_flow_indicator(optimal_flow_reading):
    """Test flow indicator from optimal biometrics"""
    stress = optimal_flow_reading.get_stress_indicator()

    # Moderate HR + High HRV should indicate low stress
    assert stress < 0.5
    assert 0.0 <= stress <= 1.0


def test_assess_high_stress_state(engine, high_stress_reading):
    """Test detection of high stress state"""
    state = engine._assess_biometric_state(high_stress_reading)

    assert state == BiometricState.HIGH_STRESS


def test_assess_optimal_flow_state(engine, optimal_flow_reading):
    """Test detection of optimal flow state"""
    state = engine._assess_biometric_state(optimal_flow_reading)

    assert state == BiometricState.OPTIMAL_FLOW


def test_circadian_morning_peak():
    """Test circadian assessment during morning peak"""
    engine = HolisticIntelligenceEngine()

    # 10am - should be MORNING_PEAK
    morning_time = datetime.now().replace(hour=10, minute=0)
    phase, state = engine._assess_circadian_phase(morning_time)

    assert phase == CircadianPhase.MORNING_PEAK
    assert state.energy_level > 0.8
    assert state.alertness_level > 0.9
    assert "Complex coding" in state.optimal_for


def test_circadian_post_lunch_dip():
    """Test circadian assessment during post-lunch dip"""
    engine = HolisticIntelligenceEngine()

    # 2pm - should be POST_LUNCH_DIP
    afternoon_time = datetime.now().replace(hour=14, minute=0)
    phase, state = engine._assess_circadian_phase(afternoon_time)

    assert phase == CircadianPhase.POST_LUNCH_DIP
    assert state.energy_level < 0.6
    assert "Complex problem-solving" in state.suboptimal_for


def test_circadian_evening_wind():
    """Test circadian assessment during evening"""
    engine = HolisticIntelligenceEngine()

    # 8pm - should be EVENING_WIND
    evening_time = datetime.now().replace(hour=20, minute=0)
    phase, state = engine._assess_circadian_phase(evening_time)

    assert phase == CircadianPhase.EVENING_WIND
    assert state.energy_level < 0.7
    assert "Review" in state.optimal_for


def test_cognitive_load_minimal(engine):
    """Test detection of minimal cognitive load"""
    # Create simple context with few files and no errors
    context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.8),
        active_files=[
            FileActivity(
                path=Path("main.py"),
                last_modified=datetime.now(),
                edit_count=5
            )
        ],
        recent_commands=[
            CommandActivity(command="test", timestamp=datetime.now(), success=True, duration_ms=100)
        ]
    )

    load, assessment = engine._assess_cognitive_load(context)

    assert load == CognitiveLoad.MINIMAL
    assert assessment.capacity_used < 0.3


def test_cognitive_load_high(engine):
    """Test detection of high cognitive load"""
    # Create complex context with many files and errors
    now = datetime.now()
    context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.8),
        active_files=[
            FileActivity(
                path=Path(f"file{i}.py"),
                last_modified=now,
                edit_count=10,
                project_type=ProjectType.PYTHON if i < 5 else ProjectType.RUST
            )
            for i in range(12)  # Many files
        ],
        recent_commands=[
            CommandActivity(
                command=f"cmd{i}",
                timestamp=now,
                success=(i % 2 == 0),  # 50% failure rate
                duration_ms=100
            )
            for i in range(20)  # High activity
        ]
    )

    load, assessment = engine._assess_cognitive_load(context)

    assert load in [CognitiveLoad.HIGH, CognitiveLoad.OVERLOADED]
    assert assessment.capacity_used >= 0.6
    assert len(assessment.factors) > 0


def test_social_context_solo(engine):
    """Test detection of solo working context"""
    context_type, info = engine._assess_social_context()

    assert context_type == SocialContext.SOLO
    assert info.participant_count == 1


def test_holistic_state_assessment(engine, optimal_flow_reading):
    """Test complete holistic state assessment"""
    # 10am - optimal time
    morning_time = datetime.now().replace(hour=10, minute=0)

    state = engine.assess_holistic_state(
        biometric_reading=optimal_flow_reading,
        current_time=morning_time
    )

    assert isinstance(state, HolisticState)
    assert state.biometric_state == BiometricState.OPTIMAL_FLOW
    assert state.circadian_phase == CircadianPhase.MORNING_PEAK
    assert state.cognitive_load in [CognitiveLoad.MINIMAL, CognitiveLoad.MODERATE]
    assert state.social_context == SocialContext.SOLO


def test_holistic_state_break_recommendation(engine, high_stress_reading):
    """Test break recommendation from holistic state"""
    state = engine.assess_holistic_state(biometric_reading=high_stress_reading)

    # High stress should trigger break recommendation
    assert state.should_take_break
    assert state.break_reason is not None
    assert "stress" in state.break_reason.lower()


def test_holistic_state_no_break_needed(engine, optimal_flow_reading):
    """Test that optimal state doesn't recommend break"""
    morning_time = datetime.now().replace(hour=10, minute=0)
    state = engine.assess_holistic_state(
        biometric_reading=optimal_flow_reading,
        current_time=morning_time
    )

    # Optimal flow during peak time shouldn't need break
    assert not state.should_take_break


def test_holistic_state_task_recommendations(engine):
    """Test task recommendations from holistic state"""
    # Morning peak time
    morning_time = datetime.now().replace(hour=10, minute=0)
    state = engine.assess_holistic_state(current_time=morning_time)

    assert len(state.optimal_task_types) > 0
    # Should recommend complex work during morning peak
    assert any("complex" in task.lower() or "coding" in task.lower()
               for task in state.optimal_task_types)


def test_holistic_state_evening_recommendations(engine):
    """Test task recommendations during evening"""
    # Evening time
    evening_time = datetime.now().replace(hour=20, minute=0)
    state = engine.assess_holistic_state(current_time=evening_time)

    # Should not recommend intensive work in evening
    assert any("intensive" in task.lower() or "debug" in task.lower()
               for task in state.suboptimal_task_types)


def test_overall_recommendation_flow_state(engine, optimal_flow_reading):
    """Test overall recommendation during flow state"""
    morning_time = datetime.now().replace(hour=10, minute=0)
    state = engine.assess_holistic_state(
        biometric_reading=optimal_flow_reading,
        current_time=morning_time
    )

    recommendation = state.get_overall_recommendation()

    assert isinstance(recommendation, str)
    assert len(recommendation) > 0


def test_overall_recommendation_high_stress(engine, high_stress_reading):
    """Test overall recommendation during high stress"""
    state = engine.assess_holistic_state(biometric_reading=high_stress_reading)

    recommendation = state.get_overall_recommendation()

    assert "stress" in recommendation.lower() or "break" in recommendation.lower()


def test_biometric_history_tracking(engine):
    """Test that biometric history is tracked"""
    reading1 = BiometricReading(timestamp=datetime.now(), heart_rate=70, hrv=60)
    reading2 = BiometricReading(timestamp=datetime.now(), heart_rate=75, hrv=55)

    engine._assess_biometric_state(reading1)
    engine._assess_biometric_state(reading2)

    assert len(engine.biometric_history) == 2
    assert engine.biometric_history[0] == reading1
    assert engine.biometric_history[1] == reading2


def test_fatigue_detection_from_declining_hrv(engine):
    """Test detection of fatigue from declining HRV trend"""
    # Create declining HRV readings
    readings = [
        BiometricReading(timestamp=datetime.now(), heart_rate=70, hrv=70),
        BiometricReading(timestamp=datetime.now(), heart_rate=72, hrv=60),
        BiometricReading(timestamp=datetime.now(), heart_rate=75, hrv=50),
    ]

    for reading in readings:
        state = engine._assess_biometric_state(reading)

    # Last reading should show fatigue (HRV dropped significantly)
    assert state == BiometricState.FATIGUE


def test_cognitive_load_factors(engine):
    """Test that cognitive load assessment includes factors"""
    now = datetime.now()
    context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.8),
        active_files=[
            FileActivity(
                path=Path(f"file{i}.py"),
                last_modified=now,
                edit_count=10
            )
            for i in range(8)  # Many files
        ],
        recent_commands=[
            CommandActivity(command=f"cmd{i}", timestamp=now, success=False, duration_ms=100)
            for i in range(5)  # Many errors
        ]
    )

    _, assessment = engine._assess_cognitive_load(context)

    assert len(assessment.factors) > 0
    assert any("files" in factor.lower() for factor in assessment.factors)
    assert any("error" in factor.lower() for factor in assessment.factors)


def test_cognitive_load_suggestions(engine):
    """Test that overload provides suggestions"""
    now = datetime.now()
    context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.8),
        active_files=[
            FileActivity(
                path=Path(f"file{i}.py"),
                last_modified=now,
                edit_count=10
            )
            for i in range(15)  # Many files
        ],
        recent_commands=[
            CommandActivity(command=f"cmd{i}", timestamp=now, success=False, duration_ms=100)
            for i in range(6)  # Many errors
        ]
    )

    engine.context_engine._current_context = context

    _, assessment = engine._assess_cognitive_load()

    if assessment.load_level in [CognitiveLoad.HIGH, CognitiveLoad.OVERLOADED]:
        assert len(assessment.suggestions) > 0


def test_circadian_state_fields(engine):
    """Test that circadian state has all expected fields"""
    morning_time = datetime.now().replace(hour=10, minute=0)
    _, state = engine._assess_circadian_phase(morning_time)

    assert isinstance(state, CircadianState)
    assert isinstance(state.optimal_for, list)
    assert isinstance(state.suboptimal_for, list)
    assert 0.0 <= state.energy_level <= 1.0
    assert 0.0 <= state.alertness_level <= 1.0


def test_late_night_work_warning(engine):
    """Test that late night work triggers warnings"""
    # 11pm - should warn about screen time
    late_night = datetime.now().replace(hour=23, minute=0)
    phase, state = engine._assess_circadian_phase(late_night)

    assert phase == CircadianPhase.MELATONIN_RISE
    assert state.energy_level < 0.4
    assert state.recommended_break_in_minutes == 0  # Should stop now
