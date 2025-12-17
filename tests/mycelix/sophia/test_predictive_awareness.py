"""
Tests for Predictive Awareness Engine

Tests Sophia's ability to:
- Predict next actions before they happen
- Anticipate problems before they occur
- Recognize workflow patterns
- Intervene proactively when helpful
- Learn from prediction outcomes
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from luminous_nix.mycelix.sophia.predictive_awareness import (
    PredictiveAwarenessEngine,
    get_predictive_awareness_engine,
    PredictionType,
    InterventionTiming,
    PredictionConfidence,
    Prediction,
    ProactiveIntervention,
    WorkflowPattern,
    PredictiveAnalysis
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
    """Create a fresh predictive awareness engine"""
    return PredictiveAwarenessEngine()


@pytest.fixture
def basic_context():
    """Basic context for testing"""
    now = datetime.now()
    return Context(
        current_intent=Intent(intent_type=IntentType.DEVELOPING, confidence=0.8),
        active_files=[
            FileActivity(path=Path("main.py"), last_modified=now, edit_count=3)
        ],
        recent_commands=[
            CommandActivity(command="edit", timestamp=now, success=True, duration_ms=100),
        ],
        session_state=SessionState.HIGH_FOCUS,
        session_start=now - timedelta(minutes=15)
    )


def test_engine_initialization(engine):
    """Test that predictive awareness engine initializes correctly"""
    assert engine is not None
    assert engine.learned_workflows == {}
    assert engine.prediction_history == []
    assert len(engine.prediction_accuracy) == 5  # 5 prediction types


def test_singleton_pattern():
    """Test that get_predictive_awareness_engine returns singleton"""
    engine1 = get_predictive_awareness_engine()
    engine2 = get_predictive_awareness_engine()
    assert engine1 is engine2


def test_analyze_and_predict_basic(engine, basic_context):
    """Test basic prediction analysis"""
    analysis = engine.analyze_and_predict(
        context=basic_context,
        recent_actions=["edit file", "save file"]
    )

    assert isinstance(analysis, PredictiveAnalysis)
    assert analysis.timestamp is not None
    assert isinstance(analysis.predictions, list)
    assert isinstance(analysis.most_likely_next_actions, list)
    assert 0.0 <= analysis.overall_confidence <= 1.0


def test_predict_next_actions(engine):
    """Test prediction of next actions"""
    recent_actions = ["edit file", "save file", "run tests"]

    analysis = engine.analyze_and_predict(recent_actions=recent_actions)

    assert len(analysis.most_likely_next_actions) > 0
    for action, probability in analysis.most_likely_next_actions:
        assert isinstance(action, str)
        assert 0.0 <= probability <= 1.0


def test_anticipate_repeated_action_problem(engine):
    """Test detection of repeated failed actions"""
    # Repeat same action 3 times
    recent_actions = ["rebuild", "rebuild", "rebuild"]

    analysis = engine.analyze_and_predict(recent_actions=recent_actions)

    # Should detect the repeated action pattern
    problems = analysis.anticipated_problems
    assert len(problems) > 0
    assert any("repeat" in p.description.lower() for p in problems)


def test_proactive_intervention_high_confidence(engine):
    """Test proactive intervention for high-confidence problems"""
    recent_actions = ["build", "build", "build"]  # Stuck pattern

    analysis = engine.analyze_and_predict(recent_actions=recent_actions)

    # Should have proactive interventions for this problem
    assert len(analysis.proactive_interventions) > 0

    intervention = analysis.proactive_interventions[0]
    assert isinstance(intervention, ProactiveIntervention)
    assert intervention.urgency in [InterventionTiming.IMMEDIATE, InterventionTiming.SOON]
    assert intervention.confidence > 0.7


def test_workflow_pattern_recognition(engine):
    """Test recognition of workflow patterns"""
    # Learn a workflow first
    engine.learn_workflow_pattern(
        "test-first-development",
        ["write test", "run test", "write code", "run test"],
        success=True
    )

    # Now test recognition
    recent_actions = ["write test", "run test"]

    analysis = engine.analyze_and_predict(recent_actions=recent_actions)

    # Should recognize the active workflow
    assert len(analysis.active_workflows) > 0
    workflow = analysis.active_workflows[0]
    assert workflow.pattern_name == "test-first-development"


def test_learn_from_outcome_correct(engine):
    """Test learning from correct predictions"""
    prediction = Prediction(
        prediction_type=PredictionType.NEXT_ACTION,
        description="User will run tests",
        reasoning="Test-first pattern",
        confidence=0.8,
        confidence_level=PredictionConfidence.HIGH,
        suggested_action=None,
        intervention_timing=InterventionTiming.WHEN_ASKED,
        evidence=["Pattern match"],
        potential_impact="Better preparation",
        timestamp=datetime.now()
    )

    initial_accuracy = engine.prediction_accuracy[PredictionType.NEXT_ACTION]

    engine.learn_from_outcome(prediction, "ran tests", was_correct=True)

    # Accuracy should improve
    new_accuracy = engine.prediction_accuracy[PredictionType.NEXT_ACTION]
    assert new_accuracy > initial_accuracy


def test_learn_from_outcome_incorrect(engine):
    """Test learning from incorrect predictions"""
    prediction = Prediction(
        prediction_type=PredictionType.NEXT_ACTION,
        description="User will run tests",
        reasoning="Test-first pattern",
        confidence=0.8,
        confidence_level=PredictionConfidence.HIGH,
        suggested_action=None,
        intervention_timing=InterventionTiming.WHEN_ASKED,
        evidence=["Pattern match"],
        potential_impact="Better preparation",
        timestamp=datetime.now()
    )

    initial_accuracy = engine.prediction_accuracy[PredictionType.NEXT_ACTION]

    engine.learn_from_outcome(prediction, "took a break", was_correct=False)

    # Accuracy should decrease
    new_accuracy = engine.prediction_accuracy[PredictionType.NEXT_ACTION]
    assert new_accuracy < initial_accuracy


def test_learn_workflow_pattern_new(engine):
    """Test learning a new workflow pattern"""
    steps = ["edit", "test", "commit"]

    engine.learn_workflow_pattern("simple-workflow", steps, success=True)

    assert "simple-workflow" in engine.learned_workflows
    workflow = engine.learned_workflows["simple-workflow"]
    assert workflow.typical_steps == steps
    assert workflow.success_rate == 1.0


def test_learn_workflow_pattern_update(engine):
    """Test updating an existing workflow pattern"""
    steps = ["edit", "test", "commit"]

    # Learn it once
    engine.learn_workflow_pattern("simple-workflow", steps, success=True)
    initial_frequency = engine.learned_workflows["simple-workflow"].frequency

    # Learn it again (should update frequency)
    engine.learn_workflow_pattern("simple-workflow", steps, success=True)

    workflow = engine.learned_workflows["simple-workflow"]
    assert workflow.frequency > initial_frequency


def test_prediction_dataclass():
    """Test Prediction dataclass"""
    pred = Prediction(
        prediction_type=PredictionType.NEXT_ACTION,
        description="Test prediction",
        reasoning="Test reasoning",
        confidence=0.85,
        confidence_level=PredictionConfidence.HIGH,
        suggested_action="Test action",
        intervention_timing=InterventionTiming.SOON,
        evidence=["Evidence 1", "Evidence 2"],
        potential_impact="Test impact",
        timestamp=datetime.now()
    )

    assert pred.prediction_type == PredictionType.NEXT_ACTION
    assert pred.confidence == 0.85
    assert len(pred.evidence) == 2


def test_proactive_intervention_dataclass():
    """Test ProactiveIntervention dataclass"""
    intervention = ProactiveIntervention(
        trigger="Test trigger",
        message="Test message",
        action_offer="Test offer",
        timing_rationale="Test rationale",
        urgency=InterventionTiming.SOON,
        expected_benefit="Test benefit",
        confidence=0.8
    )

    assert intervention.urgency == InterventionTiming.SOON
    assert intervention.confidence == 0.8


def test_workflow_pattern_dataclass():
    """Test WorkflowPattern dataclass"""
    workflow = WorkflowPattern(
        pattern_name="test-workflow",
        description="Test description",
        typical_steps=["step1", "step2"],
        current_step_index=0,
        frequency=0.5,
        last_seen=datetime.now(),
        success_rate=0.9,
        predicted_next_steps=[("step3", 0.8)]
    )

    assert workflow.pattern_name == "test-workflow"
    assert len(workflow.typical_steps) == 2
    assert workflow.success_rate == 0.9


def test_predictive_analysis_dataclass():
    """Test PredictiveAnalysis dataclass"""
    now = datetime.now()

    analysis = PredictiveAnalysis(
        timestamp=now,
        predictions=[],
        proactive_interventions=[],
        active_workflows=[],
        most_likely_next_actions=[("action1", 0.7)],
        anticipated_problems=[],
        overall_confidence=0.75
    )

    assert analysis.timestamp == now
    assert len(analysis.most_likely_next_actions) == 1
    assert analysis.overall_confidence == 0.75


def test_all_prediction_types():
    """Test that all PredictionType enum values are valid"""
    for pred_type in PredictionType:
        assert isinstance(pred_type.value, str)
        assert len(pred_type.value) > 0


def test_all_intervention_timings():
    """Test that all InterventionTiming enum values are valid"""
    for timing in InterventionTiming:
        assert isinstance(timing.value, str)
        assert len(timing.value) > 0


def test_all_prediction_confidence_levels():
    """Test that all PredictionConfidence enum values are valid"""
    for confidence in PredictionConfidence:
        assert isinstance(confidence.value, str)
        assert len(confidence.value) > 0


def test_probability_to_confidence_conversion(engine):
    """Test conversion of probability to confidence levels"""
    assert engine._probability_to_confidence(0.95) == PredictionConfidence.VERY_HIGH
    assert engine._probability_to_confidence(0.80) == PredictionConfidence.HIGH
    assert engine._probability_to_confidence(0.60) == PredictionConfidence.MODERATE
    assert engine._probability_to_confidence(0.35) == PredictionConfidence.LOW
    assert engine._probability_to_confidence(0.10) == PredictionConfidence.VERY_LOW


def test_calculate_workflow_match(engine):
    """Test workflow matching calculation"""
    recent = ["edit file", "run test"]
    workflow = ["edit file", "run test", "commit"]

    match_score = engine._calculate_workflow_match(recent, workflow)

    assert 0.0 <= match_score <= 1.0
    assert match_score > 0.0  # Should have some match


def test_calculate_overall_confidence(engine):
    """Test overall confidence calculation"""
    predictions = [
        Prediction(
            prediction_type=PredictionType.NEXT_ACTION,
            description="Test",
            reasoning="Test",
            confidence=0.8,
            confidence_level=PredictionConfidence.HIGH,
            suggested_action=None,
            intervention_timing=InterventionTiming.WHEN_ASKED,
            evidence=[],
            potential_impact="Test",
            timestamp=datetime.now()
        ),
        Prediction(
            prediction_type=PredictionType.POTENTIAL_PROBLEM,
            description="Test",
            reasoning="Test",
            confidence=0.6,
            confidence_level=PredictionConfidence.MODERATE,
            suggested_action=None,
            intervention_timing=InterventionTiming.SOON,
            evidence=[],
            potential_impact="Test",
            timestamp=datetime.now()
        )
    ]

    confidence = engine._calculate_overall_confidence(predictions)

    assert 0.0 <= confidence <= 1.0


def test_get_prediction_summary(engine):
    """Test generation of human-readable summary"""
    analysis = engine.analyze_and_predict(
        recent_actions=["edit", "test", "edit"]
    )

    summary = engine.get_prediction_summary(analysis)

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Predictive Analysis" in summary


def test_learning_opportunity_prediction(engine):
    """Test prediction of learning opportunities"""
    # Long session with many actions
    recent_actions = [f"action{i}" for i in range(10)]

    analysis = engine.analyze_and_predict(recent_actions=recent_actions)

    # Should suggest learning opportunity
    learning_preds = [
        p for p in analysis.predictions
        if p.prediction_type == PredictionType.LEARNING_OPPORTUNITY
    ]
    assert len(learning_preds) > 0


def test_prediction_history_tracking(engine):
    """Test that predictions are tracked"""
    prediction = Prediction(
        prediction_type=PredictionType.NEXT_ACTION,
        description="Test",
        reasoning="Test",
        confidence=0.8,
        confidence_level=PredictionConfidence.HIGH,
        suggested_action=None,
        intervention_timing=InterventionTiming.WHEN_ASKED,
        evidence=[],
        potential_impact="Test",
        timestamp=datetime.now()
    )

    initial_count = len(engine.prediction_history)
    engine.prediction_history.append(prediction)

    assert len(engine.prediction_history) == initial_count + 1


def test_empty_recent_actions(engine):
    """Test handling of empty recent actions"""
    analysis = engine.analyze_and_predict(recent_actions=[])

    # Should still produce valid analysis
    assert isinstance(analysis, PredictiveAnalysis)
    assert analysis.overall_confidence >= 0.0


def test_intervention_urgency_levels(engine):
    """Test different intervention urgency levels"""
    # High-confidence problem should get immediate/soon timing
    recent_actions = ["fail", "fail", "fail"]

    analysis = engine.analyze_and_predict(recent_actions=recent_actions)

    if analysis.proactive_interventions:
        intervention = analysis.proactive_interventions[0]
        assert intervention.urgency in [
            InterventionTiming.IMMEDIATE,
            InterventionTiming.SOON
        ]


def test_confidence_bounds(engine):
    """Test that all confidence values stay within 0-1 bounds"""
    analysis = engine.analyze_and_predict(
        recent_actions=["action1", "action2", "action3"]
    )

    # Overall confidence
    assert 0.0 <= analysis.overall_confidence <= 1.0

    # Prediction confidences
    for pred in analysis.predictions:
        assert 0.0 <= pred.confidence <= 1.0

    # Intervention confidences
    for intervention in analysis.proactive_interventions:
        assert 0.0 <= intervention.confidence <= 1.0

    # Action probabilities
    for action, prob in analysis.most_likely_next_actions:
        assert 0.0 <= prob <= 1.0
