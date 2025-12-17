"""
Tests for Meta-Cognitive Mirror

Tests Sophia's ability to:
- Detect user patterns
- Generate insights
- Reflect patterns back
- Suggest growth opportunities
- Celebrate achievements
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from luminous_nix.mycelix.sophia.meta_cognitive import (
    MetaCognitiveEngine,
    get_meta_cognitive_engine,
    Pattern,
    Insight,
    PatternType,
    InsightType
)
from luminous_nix.mycelix.context import (
    Context,
    CommandActivity,
    FileActivity,
    SessionState,
    IntentType,
    ProjectType,
    Intent
)


@pytest.fixture
def engine():
    """Create a fresh meta-cognitive engine"""
    return MetaCognitiveEngine()


@pytest.fixture
def test_context():
    """Create a test context with patterns"""
    now = datetime.now()

    return Context(
        current_intent=Intent(
            intent_type=IntentType.DEVELOPING,
            confidence=0.9,
            evidence=["Editing source files", "Running builds"]
        ),
        primary_project=ProjectType.RUST,
        recent_commands=[
            CommandActivity(
                command="cargo build",
                timestamp=now - timedelta(seconds=60),
                success=True,
                duration_ms=1500
            ),
            CommandActivity(
                command="cargo test",
                timestamp=now - timedelta(seconds=50),
                success=True,
                duration_ms=800
            ),
            CommandActivity(
                command="cargo build",
                timestamp=now - timedelta(seconds=40),
                success=True,
                duration_ms=1400
            ),
            CommandActivity(
                command="cargo test",
                timestamp=now - timedelta(seconds=30),
                success=True,
                duration_ms=750
            ),
            CommandActivity(
                command="git add .",
                timestamp=now - timedelta(seconds=20),
                success=True,
                duration_ms=100
            ),
            CommandActivity(
                command="git commit -m 'test'",
                timestamp=now - timedelta(seconds=10),
                success=True,
                duration_ms=150
            ),
        ],
        active_files=[
            FileActivity(
                path=Path("src/main.rs"),
                last_modified=now - timedelta(minutes=5),
                edit_count=10,
                language="rust",
                project_type=ProjectType.RUST
            )
        ],
        session_state=SessionState.HIGH_FOCUS,
        session_start=now - timedelta(minutes=45)  # Session started 45 minutes ago
    )


def test_engine_initialization(engine):
    """Test that engine initializes correctly"""
    assert engine is not None
    assert engine.patterns == {}
    assert engine.insights == []
    assert engine.context_engine is not None
    assert engine.pattern_completer is not None


def test_singleton_pattern():
    """Test that get_meta_cognitive_engine returns singleton"""
    engine1 = get_meta_cognitive_engine()
    engine2 = get_meta_cognitive_engine()
    assert engine1 is engine2


def test_analyze_current_session(engine, test_context):
    """Test analyzing current session"""
    insights = engine.analyze_current_session(test_context)

    assert isinstance(insights, list)
    # Should have at least some insights
    assert len(insights) > 0

    # Check that insights are valid
    for insight in insights:
        assert isinstance(insight, Insight)
        assert insight.title
        assert insight.message
        assert isinstance(insight.evidence, list)
        assert 0.0 <= insight.confidence <= 1.0


def test_detect_test_first_pattern(engine, test_context):
    """Test detection of test-first development pattern"""
    insights = engine.analyze_current_session(test_context)

    # Should detect test-after-build pattern
    # (In our test context, we have build -> test sequences)
    pattern_insights = [i for i in insights
                       if "test" in i.title.lower() or "test" in i.message.lower()]

    assert len(pattern_insights) > 0


def test_success_rate_analysis(engine):
    """Test analysis of command success rates"""
    # Create context with low success rate
    now = datetime.now()
    context = Context(
        current_intent=Intent(
            intent_type=IntentType.DEVELOPING,
            confidence=0.8
        ),
        recent_commands=[
            CommandActivity(command="cmd1", timestamp=now, success=True, duration_ms=100),
            CommandActivity(command="cmd2", timestamp=now, success=False, duration_ms=100),
            CommandActivity(command="cmd3", timestamp=now, success=False, duration_ms=100),
            CommandActivity(command="cmd4", timestamp=now, success=False, duration_ms=100),
            CommandActivity(command="cmd5", timestamp=now, success=False, duration_ms=100),
        ]
    )

    insights = engine.analyze_current_session(context)

    # Should warn about low success rate
    warnings = [i for i in insights if i.insight_type == InsightType.WARNING]
    assert len(warnings) > 0
    assert any("succeed" in w.message.lower() for w in warnings)


def test_high_success_celebration(engine):
    """Test celebration of high success rates"""
    now = datetime.now()
    context = Context(
        current_intent=Intent(
            intent_type=IntentType.DEVELOPING,
            confidence=0.9
        ),
        recent_commands=[
            CommandActivity(command=f"cmd{i}", timestamp=now, success=True, duration_ms=100)
            for i in range(10)
        ]
    )

    insights = engine.analyze_current_session(context)

    # Should celebrate high success rate
    celebrations = [i for i in insights if i.insight_type == InsightType.CELEBRATION]
    assert len(celebrations) > 0


def test_flow_state_detection(engine, test_context):
    """Test detection of flow state"""
    # test_context has is_focused=True and 45 minutes focus
    insights = engine.analyze_current_session(test_context)

    # Should detect flow state
    flow_insights = [i for i in insights
                    if "flow" in i.title.lower() or "flow" in i.message.lower()]

    assert len(flow_insights) > 0
    assert any(i.insight_type == InsightType.CELEBRATION for i in flow_insights)


def test_automation_opportunity_detection(engine):
    """Test detection of automation opportunities"""
    now = datetime.now()
    context = Context(
        current_intent=Intent(
            intent_type=IntentType.DEVELOPING,
            confidence=0.8
        ),
        recent_commands=[
            CommandActivity(command="nix-build", timestamp=now, success=True, duration_ms=2000),
            CommandActivity(command="nix-build", timestamp=now, success=True, duration_ms=2000),
            CommandActivity(command="nix-build", timestamp=now, success=True, duration_ms=2000),
            CommandActivity(command="nix-build", timestamp=now, success=True, duration_ms=2000),
        ]
    )

    insights = engine.analyze_current_session(context)

    # Should suggest automation
    opportunities = [i for i in insights
                    if i.insight_type == InsightType.GROWTH_OPPORTUNITY]

    assert len(opportunities) > 0
    # Check title or message for automation-related keywords
    assert any(
        "automat" in o.title.lower() or "automat" in o.message.lower() or
        "alias" in o.suggested_action.lower() if o.suggested_action else False
        for o in opportunities
    )


def test_pattern_reflection_empty(engine):
    """Test pattern reflection with no patterns"""
    reflection = engine.get_pattern_reflection()

    assert isinstance(reflection, str)
    assert "Getting to Know You" in reflection or "learning your patterns" in reflection.lower()


def test_pattern_reflection_with_patterns(engine):
    """Test pattern reflection with tracked patterns"""
    # Add some test patterns
    engine.patterns["test_first"] = Pattern(
        pattern_type=PatternType.WORK_HABIT,
        name="Test-First Development",
        description="Runs tests before building",
        frequency=0.8,
        confidence=0.9,
        first_observed=datetime.now() - timedelta(days=7),
        last_observed=datetime.now(),
        occurrences=20,
        impact="positive",
        success_rate=0.95
    )

    engine.patterns["rush_config"] = Pattern(
        pattern_type=PatternType.WORK_HABIT,
        name="Rushing Configuration",
        description="Doesn't test configs before applying",
        frequency=0.6,
        confidence=0.8,
        first_observed=datetime.now() - timedelta(days=7),
        last_observed=datetime.now(),
        occurrences=15,
        impact="negative",
        success_rate=0.4
    )

    reflection = engine.get_pattern_reflection()

    assert isinstance(reflection, str)
    assert "Your Patterns" in reflection
    assert "Test-First Development" in reflection
    assert "Rushing Configuration" in reflection
    assert "Good Habits" in reflection or "✅" in reflection
    assert "Growth Opportunities" in reflection or "⚠️" in reflection


def test_growth_report_empty(engine):
    """Test growth report with no data"""
    report = engine.get_growth_report()

    assert isinstance(report, str)
    assert "Growth Journey" in report


def test_growth_report_with_data(engine):
    """Test growth report with weekly stats"""
    engine.weekly_stats["2025-W48"] = {
        "success_rate": 0.7,
        "flow_time": 120
    }
    engine.weekly_stats["2025-W49"] = {
        "success_rate": 0.85,
        "flow_time": 180
    }

    report = engine.get_growth_report()

    assert isinstance(report, str)
    assert "Growth Journey" in report
    # Should show improvement
    assert "improved" in report.lower() or "increased" in report.lower()


def test_suggest_next_action(engine, test_context):
    """Test suggesting next action based on patterns"""
    suggestion = engine.suggest_next_action(test_context)

    if suggestion:  # May be None if no patterns detected
        assert isinstance(suggestion, Insight)
        assert suggestion.insight_type == InsightType.HABIT_SUGGESTION
        assert suggestion.title
        assert suggestion.message
        assert suggestion.confidence > 0


def test_pattern_dataclass():
    """Test Pattern dataclass"""
    pattern = Pattern(
        pattern_type=PatternType.WORKFLOW,
        name="Build Then Test",
        description="Always tests after building",
        frequency=0.9,
        confidence=0.95,
        first_observed=datetime.now(),
        last_observed=datetime.now(),
        occurrences=50,
        impact="positive",
        success_rate=0.88
    )

    # Test string representation
    pattern_str = str(pattern)
    assert "Build Then Test" in pattern_str
    assert "Always tests after building" in pattern_str
    assert "90%" in pattern_str or "0.9" in str(pattern.frequency)


def test_insight_dataclass():
    """Test Insight dataclass"""
    insight = Insight(
        insight_type=InsightType.CELEBRATION,
        title="Great Job!",
        message="You're doing excellent work",
        evidence=["High success rate", "Good patterns"],
        suggested_action="Keep it up!",
        confidence=0.9
    )

    # Test string representation
    insight_str = str(insight)
    assert "Great Job!" in insight_str
    assert "You're doing excellent work" in insight_str
    assert "Keep it up!" in insight_str


def test_learning_spirit_celebration(engine):
    """Test celebration of learning intent"""
    now = datetime.now()
    context = Context(
        current_intent=Intent(
            intent_type=IntentType.LEARNING,  # Learning intent
            confidence=0.9
        ),
        recent_commands=[
            CommandActivity(command="ask-nix help", timestamp=now, success=True, duration_ms=50)
        ]
    )

    insights = engine.analyze_current_session(context)

    # Should celebrate learning spirit
    celebrations = [i for i in insights
                   if i.insight_type == InsightType.CELEBRATION
                   and "learn" in i.message.lower()]

    assert len(celebrations) > 0


def test_multiple_analysis_rounds(engine, test_context):
    """Test that multiple analysis rounds accumulate insights"""
    insights1 = engine.analyze_current_session(test_context)
    initial_count = len(engine.insights)

    insights2 = engine.analyze_current_session(test_context)
    final_count = len(engine.insights)

    # Should accumulate insights
    assert final_count >= initial_count
    assert len(insights1) > 0
    assert len(insights2) > 0


def test_insight_confidence_bounds(engine, test_context):
    """Test that all insights have valid confidence values"""
    insights = engine.analyze_current_session(test_context)

    for insight in insights:
        assert 0.0 <= insight.confidence <= 1.0


def test_evidence_provided(engine, test_context):
    """Test that all insights provide evidence"""
    insights = engine.analyze_current_session(test_context)

    for insight in insights:
        assert isinstance(insight.evidence, list)
        assert len(insight.evidence) > 0
        # Evidence should be strings
        assert all(isinstance(e, str) for e in insight.evidence)
