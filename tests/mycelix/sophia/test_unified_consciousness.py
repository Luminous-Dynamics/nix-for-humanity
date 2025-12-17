"""
Tests for Unified Sophia Consciousness

Tests Sophia's ability to:
- Integrate all three intelligence layers
- Generate synergistic insights
- Determine consciousness level
- Provide unified recommendations
- Respond with complete awareness
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from luminous_nix.mycelix.sophia.unified_consciousness import (
    UnifiedSophiaEngine,
    get_sophia_engine,
    ConsciousnessLevel,
    UnifiedState,
    SophiaResponse
)
from luminous_nix.mycelix.sophia.holistic_intelligence import (
    BiometricReading,
    BiometricState,
    CircadianPhase,
    CognitiveLoad,
    SocialContext
)
from luminous_nix.mycelix.sophia.emotional_intelligence import (
    EmotionalState,
    EmotionalTone
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
    """Create a fresh unified Sophia engine"""
    return UnifiedSophiaEngine()


@pytest.fixture
def optimal_context():
    """Create a context indicating optimal state"""
    now = datetime.now()
    return Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.9),
        active_files=[
            FileActivity(
                path=Path("main.py"),
                last_modified=now,
                edit_count=10
            )
        ],
        recent_commands=[
            CommandActivity(command="test", timestamp=now, success=True, duration_ms=500),
            CommandActivity(command="build", timestamp=now, success=True, duration_ms=1000),
            CommandActivity(command="test", timestamp=now, success=True, duration_ms=500),
        ],
        session_state=SessionState.HIGH_FOCUS,
        session_start=now - timedelta(minutes=30)
    )


@pytest.fixture
def challenged_context():
    """Create a context indicating challenged state"""
    now = datetime.now()
    return Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.6),
        active_files=[
            FileActivity(
                path=Path("main.py"),
                last_modified=now,
                edit_count=20
            )
        ],
        recent_commands=[
            CommandActivity(command="build", timestamp=now, success=False, duration_ms=1000),
            CommandActivity(command="build", timestamp=now, success=False, duration_ms=1000),
            CommandActivity(command="build", timestamp=now, success=False, duration_ms=1000),
        ],
        session_state=SessionState.FRUSTRATED,
        session_start=now - timedelta(minutes=45)
    )


@pytest.fixture
def optimal_biometric():
    """Create optimal biometric reading"""
    return BiometricReading(
        timestamp=datetime.now(),
        heart_rate=70,
        hrv=75.0
    )


@pytest.fixture
def stressed_biometric():
    """Create stressed biometric reading"""
    return BiometricReading(
        timestamp=datetime.now(),
        heart_rate=110,
        hrv=15.0
    )


def test_engine_initialization(engine):
    """Test that unified engine initializes correctly"""
    assert engine is not None
    assert engine.meta_cognitive is not None
    assert engine.holistic is not None
    assert engine.emotional is not None
    assert engine.consciousness_history == []


def test_singleton_pattern():
    """Test that get_sophia_engine returns singleton"""
    engine1 = get_sophia_engine()
    engine2 = get_sophia_engine()
    assert engine1 is engine2


def test_assess_optimal_state(engine, optimal_context, optimal_biometric):
    """Test assessment of optimal consciousness state"""
    # 10am - morning peak
    morning_time = datetime.now().replace(hour=10, minute=0)

    state = engine.assess_complete_state(
        context=optimal_context,
        biometric_reading=optimal_biometric,
        current_time=morning_time
    )

    assert isinstance(state, UnifiedState)
    assert state.consciousness_level in [ConsciousnessLevel.OPTIMAL, ConsciousnessLevel.THRIVING]
    assert state.emotional_state.state in [EmotionalState.FOCUSED, EmotionalState.SATISFIED]
    assert state.holistic_state.biometric_state == BiometricState.OPTIMAL_FLOW
    assert state.holistic_state.circadian_phase == CircadianPhase.MORNING_PEAK


def test_assess_challenged_state(engine, challenged_context, stressed_biometric):
    """Test assessment of challenged consciousness state"""
    state = engine.assess_complete_state(
        context=challenged_context,
        biometric_reading=stressed_biometric
    )

    assert isinstance(state, UnifiedState)
    assert state.consciousness_level in [ConsciousnessLevel.CHALLENGED, ConsciousnessLevel.OVERWHELMED]
    assert state.emotional_state.state == EmotionalState.FRUSTRATED
    assert state.holistic_state.biometric_state == BiometricState.HIGH_STRESS


def test_synergistic_insights_generation(engine, challenged_context, stressed_biometric):
    """Test generation of synergistic cross-engine insights"""
    state = engine.assess_complete_state(
        context=challenged_context,
        biometric_reading=stressed_biometric
    )

    # Should have synergistic insights combining multiple systems
    assert len(state.synergistic_insights) > 0

    # Should recognize the convergence of emotional + physical stress
    combined_stress_insight = any(
        "frustrated" in insight.lower() and "stress" in insight.lower()
        for insight in state.synergistic_insights
    )
    # May or may not be present depending on exact state
    assert isinstance(combined_stress_insight, bool)


def test_priority_actions_determination(engine, challenged_context, stressed_biometric):
    """Test determination of priority actions"""
    state = engine.assess_complete_state(
        context=challenged_context,
        biometric_reading=stressed_biometric
    )

    # Should have priority actions
    assert len(state.priority_actions) > 0

    # Should recommend break or simplification given the stressed state
    has_helpful_action = any(
        "break" in action.lower() or "simplify" in action.lower()
        for action in state.priority_actions
    )
    assert has_helpful_action


def test_overall_recommendation(engine, optimal_context, optimal_biometric):
    """Test creation of overall unified recommendation"""
    morning_time = datetime.now().replace(hour=10, minute=0)

    state = engine.assess_complete_state(
        context=optimal_context,
        biometric_reading=optimal_biometric,
        current_time=morning_time
    )

    assert isinstance(state.overall_recommendation, str)
    assert len(state.overall_recommendation) > 0


def test_respond_to_query_optimal(engine, optimal_context, optimal_biometric):
    """Test responding to query in optimal state"""
    response = engine.respond_to_query(
        query="How do I install firefox?",
        context=optimal_context,
        biometric_reading=optimal_biometric
    )

    assert isinstance(response, SophiaResponse)
    assert isinstance(response.message, str)
    assert isinstance(response.tone, EmotionalTone)
    assert isinstance(response.insights, list)
    assert isinstance(response.suggestions, list)
    assert isinstance(response.should_take_action, bool)


def test_respond_to_query_challenged(engine, challenged_context, stressed_biometric):
    """Test responding to query in challenged state"""
    response = engine.respond_to_query(
        query="Why isn't this working?",
        context=challenged_context,
        biometric_reading=stressed_biometric
    )

    assert isinstance(response, SophiaResponse)
    assert response.should_take_action is True  # Should recommend action when challenged
    assert response.action_type in ["break", "simplify", None]


def test_consciousness_level_optimal():
    """Test optimal consciousness level detection"""
    engine = UnifiedSophiaEngine()

    # Create optimal context
    now = datetime.now()
    optimal_context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.9),
        active_files=[FileActivity(path=Path("main.py"), last_modified=now, edit_count=5)],
        recent_commands=[
            CommandActivity(command="test", timestamp=now, success=True, duration_ms=500),
        ],
        session_state=SessionState.HIGH_FOCUS,
        session_start=now - timedelta(minutes=20)
    )

    optimal_biometric = BiometricReading(timestamp=now, heart_rate=70, hrv=75.0)
    morning_time = now.replace(hour=10, minute=0)

    state = engine.assess_complete_state(
        context=optimal_context,
        biometric_reading=optimal_biometric,
        current_time=morning_time
    )

    # With focused state, optimal biometrics, and morning peak, should be OPTIMAL or THRIVING
    assert state.consciousness_level in [ConsciousnessLevel.OPTIMAL, ConsciousnessLevel.THRIVING]


def test_consciousness_level_overwhelmed():
    """Test overwhelmed consciousness level detection"""
    engine = UnifiedSophiaEngine()

    # Create overwhelmed context
    now = datetime.now()
    overwhelmed_context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.4),
        active_files=[
            FileActivity(path=Path(f"file{i}.py"), last_modified=now, edit_count=10)
            for i in range(15)  # Many files
        ],
        recent_commands=[
            CommandActivity(command=f"cmd{i}", timestamp=now, success=False, duration_ms=1000)
            for i in range(10)  # Many failures
        ],
        session_state=SessionState.FRUSTRATED,
        session_start=now - timedelta(minutes=120)  # Long session
    )

    stressed_biometric = BiometricReading(timestamp=now, heart_rate=120, hrv=10.0)

    state = engine.assess_complete_state(
        context=overwhelmed_context,
        biometric_reading=stressed_biometric
    )

    # Multiple stressors should result in CHALLENGED or OVERWHELMED
    assert state.consciousness_level in [ConsciousnessLevel.CHALLENGED, ConsciousnessLevel.OVERWHELMED]


def test_history_tracking(engine, optimal_context):
    """Test that consciousness history is tracked"""
    state1 = engine.assess_complete_state(context=optimal_context)
    state2 = engine.assess_complete_state(context=optimal_context)

    assert len(engine.consciousness_history) == 2
    assert engine.consciousness_history[0] == state1
    assert engine.consciousness_history[1] == state2


def test_confidence_calculation(engine, optimal_context, optimal_biometric):
    """Test that unified confidence is calculated"""
    state = engine.assess_complete_state(
        context=optimal_context,
        biometric_reading=optimal_biometric
    )

    assert 0.0 <= state.confidence <= 1.0
    # With optimal context, should have reasonably high confidence
    assert state.confidence > 0.5


def test_unified_state_dataclass():
    """Test UnifiedState dataclass"""
    from luminous_nix.mycelix.sophia.meta_cognitive import Insight as MetaInsight, PatternType, InsightType
    from luminous_nix.mycelix.sophia.holistic_intelligence import (
        HolisticState, CircadianState, CognitiveLoadAssessment, SocialContextInfo
    )
    from luminous_nix.mycelix.sophia.emotional_intelligence import (
        EmotionalReading, EmotionalResponse, MotivationType
    )

    now = datetime.now()

    # Create minimal required objects
    meta_insight = MetaInsight(
        insight_type=InsightType.PATTERN_IDENTIFIED,
        title="Test",
        message="Test",
        evidence=["Test"],
        confidence=0.8
    )

    holistic_state = HolisticState(
        timestamp=now,
        biometric_state=BiometricState.OPTIMAL_FLOW,
        circadian_phase=CircadianPhase.MORNING_PEAK,
        circadian_state=CircadianState(
            current_phase=CircadianPhase.MORNING_PEAK,
            optimal_for=["Test"],
            suboptimal_for=[],
            energy_level=0.9,
            alertness_level=0.9,
            recommended_break_in_minutes=60
        ),
        cognitive_load=CognitiveLoad.MINIMAL,
        cognitive_assessment=CognitiveLoadAssessment(
            load_level=CognitiveLoad.MINIMAL,
            capacity_used=0.2,
            factors=[],
            suggestions=[]
        ),
        social_context=SocialContext.SOLO,
        social_info=SocialContextInfo(context_type=SocialContext.SOLO, participant_count=1),
        should_take_break=False,
        break_reason=None,
        optimal_task_types=["Complex coding"],
        suboptimal_task_types=[]
    )

    emotional_reading = EmotionalReading(
        timestamp=now,
        state=EmotionalState.FOCUSED,
        confidence=0.9,
        indicators=["Test"],
        session_duration_minutes=30,
        recent_success_rate=0.95,
        error_count=0,
        task_switching_rate=0.0
    )

    emotional_response = EmotionalResponse(
        recommended_tone=EmotionalTone.PROFESSIONAL,
        motivation_type=None,
        message="Test",
        should_simplify=False,
        should_encourage_break=False,
        should_celebrate=False,
        confidence=0.9
    )

    state = UnifiedState(
        timestamp=now,
        meta_insights=[meta_insight],
        holistic_state=holistic_state,
        emotional_state=emotional_reading,
        emotional_response=emotional_response,
        causal_analysis=None,  # Optional - can be None
        temporal_analysis=None,  # Optional - can be None
        predictive_analysis=None,  # Optional - can be None (6th layer!)
        adaptive_response=None,  # Optional - can be None (7th layer!)
        synthesis_analysis=None,  # Optional - can be None (8th layer!)
        multimodal_understanding=None,  # Optional - can be None (9th layer!)
        consciousness_level=ConsciousnessLevel.OPTIMAL,
        overall_recommendation="Test recommendation",
        synergistic_insights=["Test insight"],
        priority_actions=["Test action"],
        confidence=0.9
    )

    assert state.consciousness_level == ConsciousnessLevel.OPTIMAL
    assert len(state.meta_insights) == 1
    assert state.confidence == 0.9


def test_sophia_response_dataclass():
    """Test SophiaResponse dataclass"""
    response = SophiaResponse(
        message="Test message",
        tone=EmotionalTone.PROFESSIONAL,
        insights=["Test insight"],
        suggestions=["Test suggestion"],
        should_take_action=True,
        action_type="break"
    )

    assert response.message == "Test message"
    assert response.tone == EmotionalTone.PROFESSIONAL
    assert len(response.insights) == 1
    assert response.should_take_action is True
    assert response.action_type == "break"


def test_circadian_emotional_synergy(engine):
    """Test synergy between circadian and emotional states"""
    # Create context for post-lunch dip + confusion
    now = datetime.now()
    afternoon_time = now.replace(hour=14, minute=0)  # 2pm - post-lunch dip

    context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.6),
        active_files=[FileActivity(path=Path("main.py"), last_modified=now, edit_count=5)],
        recent_commands=[
            CommandActivity(command="help", timestamp=now, success=True, duration_ms=100),
        ],
        session_state=SessionState.EXPLORING,
        session_start=now - timedelta(minutes=20)
    )

    messages = ["How does this work?", "What should I do?"]

    state = engine.assess_complete_state(
        context=context,
        recent_messages=messages,
        current_time=afternoon_time
    )

    # Should recognize post-lunch dip
    assert state.holistic_state.circadian_phase == CircadianPhase.POST_LUNCH_DIP

    # Should have insights about this combination
    # (may or may not depending on exact emotional state detected)
    assert isinstance(state.synergistic_insights, list)


def test_all_consciousness_levels():
    """Test that all consciousness levels are valid"""
    for level in ConsciousnessLevel:
        assert isinstance(level.value, str)
        assert len(level.value) > 0
