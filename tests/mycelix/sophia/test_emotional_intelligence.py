"""
Tests for Emotional Intelligence Engine

Tests Sophia's ability to:
- Detect user emotional state
- Analyze message sentiment
- Provide appropriate responses
- Generate motivational messages
- Learn emotional patterns
- Adapt tone based on state
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from luminous_nix.mycelix.sophia.emotional_intelligence import (
    EmotionalIntelligenceEngine,
    get_emotional_intelligence_engine,
    EmotionalState,
    EmotionalTone,
    MotivationType,
    EmotionalReading,
    EmotionalResponse,
    EmotionalInsight
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
    """Create a fresh emotional intelligence engine"""
    return EmotionalIntelligenceEngine()


@pytest.fixture
def frustrated_context():
    """Create a context indicating frustration"""
    now = datetime.now()
    return Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.8),
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
            CommandActivity(command="test", timestamp=now, success=False, duration_ms=500),
        ],
        session_state=SessionState.INACTIVE,
        session_start=now - timedelta(minutes=30)
    )


@pytest.fixture
def focused_context():
    """Create a context indicating deep focus"""
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
            CommandActivity(command="commit", timestamp=now, success=True, duration_ms=200),
        ],
        session_state=SessionState.HIGH_FOCUS,
        session_start=now - timedelta(minutes=45)
    )


@pytest.fixture
def tired_context():
    """Create a context indicating fatigue"""
    now = datetime.now()
    return Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.5),
        active_files=[
            FileActivity(
                path=Path("config.py"),
                last_modified=now,
                edit_count=3
            )
        ],
        recent_commands=[
            CommandActivity(command="list", timestamp=now, success=True, duration_ms=100),
        ],
        session_state=SessionState.INACTIVE,
        session_start=now - timedelta(minutes=130)  # Over 2 hours
    )


def test_engine_initialization(engine):
    """Test that engine initializes correctly"""
    assert engine is not None
    assert engine.emotional_history == []
    assert engine.learned_patterns == []


def test_singleton_pattern():
    """Test that get_emotional_intelligence_engine returns singleton"""
    engine1 = get_emotional_intelligence_engine()
    engine2 = get_emotional_intelligence_engine()
    assert engine1 is engine2


def test_detect_frustrated_state(engine, frustrated_context):
    """Test detection of frustrated emotional state"""
    reading = engine.assess_emotional_state(context=frustrated_context)

    assert reading.state == EmotionalState.FRUSTRATED
    assert reading.confidence > 0.7
    assert reading.error_count == 4
    assert reading.recent_success_rate < 0.5


def test_detect_focused_state(engine, focused_context):
    """Test detection of focused emotional state"""
    reading = engine.assess_emotional_state(context=focused_context)

    assert reading.state == EmotionalState.FOCUSED
    assert reading.confidence > 0.7
    assert reading.recent_success_rate > 0.8


def test_detect_tired_state(engine, tired_context):
    """Test detection of tired emotional state"""
    reading = engine.assess_emotional_state(context=tired_context)

    assert reading.state == EmotionalState.TIRED
    assert reading.confidence > 0.7
    assert reading.session_duration_minutes > 120


def test_message_sentiment_frustration(engine):
    """Test detection of frustration in messages"""
    messages = [
        "Why is this not working?",
        "This is broken again",
        "Help! I'm stuck"
    ]

    indicators = engine._analyze_message_sentiment(messages)

    assert len(indicators) > 0
    assert any("Frustration" in i for i in indicators)


def test_message_sentiment_excitement(engine):
    """Test detection of excitement in messages"""
    messages = [
        "This is awesome!",
        "Wow that's so cool!",
        "Amazing, it works perfectly!"
    ]

    indicators = engine._analyze_message_sentiment(messages)

    assert len(indicators) > 0
    assert any("Excitement" in i for i in indicators)


def test_message_sentiment_confusion(engine):
    """Test detection of confusion in messages"""
    messages = [
        "How do I do this?",
        "What does this mean?",
        "I'm confused about how this works"
    ]

    indicators = engine._analyze_message_sentiment(messages)

    assert len(indicators) > 0
    assert any("Confusion" in i for i in indicators)


def test_appropriate_response_frustrated(engine):
    """Test appropriate response for frustrated state"""
    response = engine.get_appropriate_response(EmotionalState.FRUSTRATED)

    assert response.recommended_tone == EmotionalTone.EMPATHETIC
    assert response.motivation_type == MotivationType.ENCOURAGEMENT
    assert response.should_simplify is True
    assert "challenge" in response.message.lower() or "together" in response.message.lower()


def test_appropriate_response_focused(engine):
    """Test appropriate response for focused state"""
    response = engine.get_appropriate_response(EmotionalState.FOCUSED)

    assert response.recommended_tone == EmotionalTone.PROFESSIONAL
    assert response.should_simplify is False
    assert "flow" in response.message.lower() or "focused" in response.message.lower()


def test_appropriate_response_excited(engine):
    """Test appropriate response for excited state"""
    response = engine.get_appropriate_response(EmotionalState.EXCITED)

    assert response.recommended_tone == EmotionalTone.ENTHUSIASTIC
    assert response.should_celebrate is True
    assert "enthusiasm" in response.message.lower() or "love" in response.message.lower()


def test_appropriate_response_tired(engine):
    """Test appropriate response for tired state"""
    response = engine.get_appropriate_response(EmotionalState.TIRED)

    assert response.recommended_tone == EmotionalTone.GENTLE
    assert response.motivation_type == MotivationType.BREAK_SUGGESTION
    assert response.should_encourage_break is True
    assert "break" in response.message.lower() or "rest" in response.message.lower()


def test_appropriate_response_confused(engine):
    """Test appropriate response for confused state"""
    response = engine.get_appropriate_response(EmotionalState.CONFUSED)

    assert response.recommended_tone == EmotionalTone.PATIENT
    assert response.motivation_type == MotivationType.SIMPLIFICATION
    assert response.should_simplify is True


def test_motivational_message_encouragement(engine):
    """Test encouragement motivational messages"""
    message = engine.generate_motivational_message(MotivationType.ENCOURAGEMENT)

    assert isinstance(message, str)
    assert len(message) > 0
    # Should contain encouraging words (broader list to match all possible messages)
    encouraging_words = ['progress', 'learning', 'growing', 'keep', 'challenge', 'expert', 'beginner', 'figure']
    assert any(word in message.lower() for word in encouraging_words)


def test_motivational_message_celebration(engine):
    """Test celebration motivational messages"""
    message = engine.generate_motivational_message(MotivationType.CELEBRATION)

    assert isinstance(message, str)
    assert len(message) > 0
    # Should contain celebratory words
    celebration_words = ['excellent', 'great', 'well done', 'nailed', 'success']
    assert any(word in message.lower() for word in celebration_words)


def test_motivational_message_break(engine):
    """Test break suggestion messages"""
    message = engine.generate_motivational_message(MotivationType.BREAK_SUGGESTION)

    assert isinstance(message, str)
    assert len(message) > 0
    # Should contain break-related words
    break_words = ['break', 'rest', 'breather', 'walk']
    assert any(word in message.lower() for word in break_words)


def test_learn_emotional_pattern(engine):
    """Test learning emotional patterns"""
    pattern = "User gets frustrated with build errors"
    evidence = ["3 failed builds in 10 minutes", "Frustration detected in messages"]
    suggestion = "Offer step-by-step debugging"

    insight = engine.learn_emotional_pattern(
        pattern=pattern,
        evidence=evidence,
        suggestion=suggestion,
        confidence=0.85
    )

    assert isinstance(insight, EmotionalInsight)
    assert insight.pattern == pattern
    assert insight.evidence == evidence
    assert insight.suggestion == suggestion
    assert insight.confidence == 0.85

    # Should be in learned patterns
    patterns = engine.get_emotional_patterns()
    assert insight in patterns


def test_emotional_reading_dataclass():
    """Test EmotionalReading dataclass"""
    now = datetime.now()
    reading = EmotionalReading(
        timestamp=now,
        state=EmotionalState.FOCUSED,
        confidence=0.9,
        indicators=["High success rate", "Deep focus state"],
        session_duration_minutes=45,
        recent_success_rate=0.95,
        error_count=0,
        task_switching_rate=0.1
    )

    assert reading.state == EmotionalState.FOCUSED
    assert reading.confidence == 0.9
    assert len(reading.indicators) == 2


def test_emotional_response_dataclass():
    """Test EmotionalResponse dataclass"""
    response = EmotionalResponse(
        recommended_tone=EmotionalTone.EMPATHETIC,
        motivation_type=MotivationType.ENCOURAGEMENT,
        message="Test message",
        should_simplify=True,
        should_encourage_break=False,
        should_celebrate=False,
        confidence=0.8
    )

    assert response.recommended_tone == EmotionalTone.EMPATHETIC
    assert response.motivation_type == MotivationType.ENCOURAGEMENT
    assert response.should_simplify is True


def test_emotional_history_tracking(engine, focused_context, frustrated_context):
    """Test that emotional history is tracked"""
    reading1 = engine.assess_emotional_state(context=focused_context)
    reading2 = engine.assess_emotional_state(context=frustrated_context)

    assert len(engine.emotional_history) == 2
    assert engine.emotional_history[0] == reading1
    assert engine.emotional_history[1] == reading2


def test_confident_state_with_history(engine, focused_context):
    """Test that confidence increases with consistent state history"""
    # Create multiple readings with same state
    for _ in range(6):
        engine.assess_emotional_state(context=focused_context)

    # Get response after history
    response = engine.get_appropriate_response(EmotionalState.FOCUSED)

    # Confidence should be high due to consistent history
    assert response.confidence > 0.85


def test_detect_anxious_state(engine):
    """Test detection of anxious state from high task switching"""
    now = datetime.now()
    context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.6),
        active_files=[
            FileActivity(
                path=Path("file1.py"),
                last_modified=now,
                edit_count=5,
                project_type=ProjectType.PYTHON
            ),
            FileActivity(
                path=Path("file2.rs"),
                last_modified=now,
                edit_count=3,
                project_type=ProjectType.RUST
            ),
            FileActivity(
                path=Path("file3.ts"),
                last_modified=now,
                edit_count=2,
                project_type=ProjectType.JAVASCRIPT
            )
        ],
        recent_commands=[
            CommandActivity(command="build", timestamp=now, success=True, duration_ms=1000),
        ],
        session_state=SessionState.EXPLORING,
        session_start=now - timedelta(minutes=10)
    )

    reading = engine.assess_emotional_state(context=context)

    # Should detect anxiety from high project switching
    assert reading.state == EmotionalState.ANXIOUS
    assert reading.task_switching_rate > 0


def test_detect_satisfied_state(engine):
    """Test detection of satisfied state"""
    now = datetime.now()
    context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.8),
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
            CommandActivity(command="commit", timestamp=now, success=True, duration_ms=200),
        ],
        session_state=SessionState.EXPLORING,
        session_start=now - timedelta(minutes=20)
    )

    reading = engine.assess_emotional_state(context=context)

    # High success rate with few errors
    assert reading.state == EmotionalState.SATISFIED
    assert reading.recent_success_rate > 0.75


def test_detect_confused_from_messages(engine):
    """Test detection of confusion from messages"""
    # Create a neutral context (not frustrated) so confusion can be detected
    now = datetime.now()
    neutral_context = Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.6),
        active_files=[
            FileActivity(
                path=Path("main.py"),
                last_modified=now,
                edit_count=5
            )
        ],
        recent_commands=[
            CommandActivity(command="list", timestamp=now, success=True, duration_ms=100),
            CommandActivity(command="search", timestamp=now, success=True, duration_ms=200),
        ],
        session_state=SessionState.EXPLORING,
        session_start=now - timedelta(minutes=15)
    )

    messages = [
        "How does this work?",
        "What am I supposed to do here?",
        "I don't understand why this fails"
    ]

    reading = engine.assess_emotional_state(
        context=neutral_context,
        recent_messages=messages
    )

    # Should detect confusion from multiple question indicators
    assert reading.state == EmotionalState.CONFUSED
    assert any("Confusion" in indicator for indicator in reading.indicators)


def test_detect_excitement_from_messages(engine, focused_context):
    """Test detection of excitement from messages"""
    messages = [
        "Wow this is amazing!",
        "Perfect! That worked!"
    ]

    reading = engine.assess_emotional_state(
        context=focused_context,
        recent_messages=messages
    )

    # Should detect excitement from enthusiasm + good success rate
    assert reading.state == EmotionalState.EXCITED
    assert any("Excitement" in indicator for indicator in reading.indicators)


def test_all_motivation_types(engine):
    """Test that all motivation types generate valid messages"""
    for motivation_type in MotivationType:
        message = engine.generate_motivational_message(motivation_type)
        assert isinstance(message, str)
        assert len(message) > 0


def test_all_emotional_states_have_responses(engine):
    """Test that all emotional states have appropriate responses"""
    for state in EmotionalState:
        response = engine.get_appropriate_response(state)
        assert isinstance(response, EmotionalResponse)
        assert isinstance(response.recommended_tone, EmotionalTone)
        assert isinstance(response.message, str)
        assert len(response.message) > 0


def test_emotional_insight_dataclass():
    """Test EmotionalInsight dataclass"""
    insight = EmotionalInsight(
        pattern="Test pattern",
        evidence=["Evidence 1", "Evidence 2"],
        suggestion="Test suggestion",
        confidence=0.85
    )

    assert insight.pattern == "Test pattern"
    assert len(insight.evidence) == 2
    assert insight.suggestion == "Test suggestion"
    assert insight.confidence == 0.85
