"""
Tests for Multi-Modal Understanding Engine

Tests Sophia's ability to:
- Understand screenshots and visual information
- Parse and analyze log files semantically
- Interpret terminal output and system state
- Integrate multiple modalities
- Connect visual information to other intelligence layers
- Generate actionable insights from multi-sensory input
"""

import pytest
from datetime import datetime
from luminous_nix.mycelix.sophia.multimodal_understanding import (
    MultiModalUnderstandingEngine,
    get_multimodal_understanding_engine,
    ModalityType,
    UnderstandingLevel,
    VisualElement,
    ModalityInput,
    VisualAnalysis,
    LogAnalysis,
    SystemStateAnalysis,
    MultiModalUnderstanding,
    MultiModalAnalysis
)


@pytest.fixture
def engine():
    """Create a fresh multi-modal understanding engine"""
    return MultiModalUnderstandingEngine()


@pytest.fixture
def error_screenshot_input():
    """Create sample error screenshot input"""
    return ModalityInput(
        modality_type=ModalityType.SCREENSHOT,
        content="Error: Permission denied\nCommand failed with exit code 1",
        timestamp=datetime.now(),
        metadata={"source": "terminal_screenshot"}
    )


@pytest.fixture
def log_file_input():
    """Create sample log file input"""
    log_content = """
    2025-12-04 10:00:00 INFO: Starting service
    2025-12-04 10:00:15 ERROR: Connection failed
    2025-12-04 10:00:30 ERROR: Retry attempt 1 failed
    2025-12-04 10:00:45 ERROR: Retry attempt 2 failed
    2025-12-04 10:01:00 WARN: Service degraded
    """
    return ModalityInput(
        modality_type=ModalityType.LOG_FILE,
        content=log_content,
        timestamp=datetime.now(),
        metadata={"log_type": "application"}
    )


@pytest.fixture
def terminal_output_input():
    """Create sample terminal output input"""
    return ModalityInput(
        modality_type=ModalityType.TERMINAL_OUTPUT,
        content="$ npm install\nnpm ERR! code EACCES\nnpm ERR! Permission denied",
        timestamp=datetime.now(),
        metadata={"command": "npm install"}
    )


def test_engine_initialization(engine):
    """Test that multi-modal engine initializes correctly"""
    assert engine is not None
    assert engine.understanding_history == []
    assert isinstance(engine.visual_patterns, dict)
    assert isinstance(engine.log_patterns, dict)


def test_singleton_pattern():
    """Test that get_multimodal_understanding_engine returns singleton"""
    engine1 = get_multimodal_understanding_engine()
    engine2 = get_multimodal_understanding_engine()
    assert engine1 is engine2


def test_understand_error_screenshot(engine, error_screenshot_input):
    """Test understanding of error screenshot"""
    understanding = engine.understand(error_screenshot_input)

    assert isinstance(understanding, MultiModalUnderstanding)
    assert understanding.modality_type == ModalityType.SCREENSHOT
    assert understanding.visual_analysis is not None
    assert "permission" in understanding.primary_insight.lower()
    assert understanding.confidence > 0


def test_understand_log_file(engine, log_file_input):
    """Test understanding of log file"""
    understanding = engine.understand(log_file_input)

    assert isinstance(understanding, MultiModalUnderstanding)
    assert understanding.modality_type == ModalityType.LOG_FILE
    assert understanding.log_analysis is not None
    assert len(understanding.log_analysis.error_messages) > 0
    assert understanding.confidence > 0


def test_understand_terminal_output(engine, terminal_output_input):
    """Test understanding of terminal output"""
    understanding = engine.understand(terminal_output_input)

    assert isinstance(understanding, MultiModalUnderstanding)
    assert understanding.modality_type == ModalityType.TERMINAL_OUTPUT
    assert understanding.visual_analysis is not None
    assert VisualElement.ERROR_INDICATOR in understanding.visual_analysis.detected_elements


def test_analyze_screenshot_detects_elements(engine):
    """Test that screenshot analysis detects visual elements"""
    content = "Error: File not found"
    visual = engine._analyze_screenshot(content)

    assert isinstance(visual, VisualAnalysis)
    assert VisualElement.ERROR_INDICATOR in visual.detected_elements
    assert visual.extracted_text is not None
    assert visual.confidence > 0


def test_analyze_screenshot_success_indicators(engine):
    """Test detection of success indicators"""
    content = "Success: Installation complete"
    visual = engine._analyze_screenshot(content)

    # Should not have error indicator
    assert VisualElement.ERROR_INDICATOR not in visual.detected_elements


def test_analyze_log_file_extracts_errors(engine):
    """Test that log analysis extracts error messages"""
    log_content = """
    INFO: Starting
    ERROR: Connection failed
    ERROR: Database unavailable
    WARN: Retrying
    """
    log = engine._analyze_log_file(log_content)

    assert isinstance(log, LogAnalysis)
    assert len(log.error_messages) >= 2
    assert len(log.warning_messages) >= 1
    assert log.confidence > 0


def test_analyze_log_file_infers_root_cause(engine):
    """Test that log analysis infers root cause"""
    log_content = """
    ERROR: Permission denied accessing /var/log
    ERROR: Failed to write to /var/log/app.log
    """
    log = engine._analyze_log_file(log_content)

    assert log.root_cause is not None
    assert "permission" in log.root_cause.lower()


def test_analyze_terminal_output_detects_prompt(engine):
    """Test terminal output detection of command prompt"""
    content = "$ ls -la\ntotal 42"
    visual = engine._analyze_terminal_output(content)

    assert VisualElement.COMMAND_PROMPT in visual.detected_elements
    assert VisualElement.TERMINAL in visual.detected_elements


def test_analyze_terminal_output_success(engine):
    """Test terminal output with success indicators"""
    content = "$ make\nBuild successful\nTests passed"
    visual = engine._analyze_terminal_output(content)

    assert VisualElement.SUCCESS_INDICATOR in visual.detected_elements
    assert "satisfaction_likely" in visual.emotional_indicators


def test_analyze_system_state(engine):
    """Test system state analysis"""
    state = engine._analyze_system_state({
        "cpu": "75%",
        "memory": "60%",
        "disk": "90%"
    })

    assert isinstance(state, SystemStateAnalysis)
    assert state.state_type is not None
    assert state.confidence > 0


def test_generate_primary_insight_error(engine):
    """Test primary insight generation from error"""
    visual = VisualAnalysis(
        detected_elements=[VisualElement.ERROR_INDICATOR],
        extracted_text="Error: Permission denied",
        dominant_colors=["red"],
        layout_description="Error message",
        likely_application="terminal",
        user_intent="Command execution",
        emotional_indicators=["frustration_likely"],
        confidence=0.8
    )

    insight = engine._generate_primary_insight(
        visual, None, None, ModalityType.SCREENSHOT
    )

    assert "error" in insight.lower()
    assert len(insight) > 0


def test_connect_to_patterns(engine):
    """Test connection to meta-cognitive patterns"""
    recent_patterns = ["repeated_failures", "permission_issues", "user_frustration"]

    connections = engine._connect_to_patterns(recent_patterns)

    assert isinstance(connections, list)
    assert len(connections) > 0
    assert any("pattern" in c.lower() for c in connections)


def test_assess_emotional_context_from_visual(engine):
    """Test emotional context assessment from visual cues"""
    visual = VisualAnalysis(
        detected_elements=[VisualElement.ERROR_INDICATOR],
        extracted_text="Error",
        dominant_colors=["red"],
        layout_description="Error",
        likely_application="terminal",
        user_intent="Command",
        emotional_indicators=["frustration_likely"],
        confidence=0.8
    )

    context = engine._assess_emotional_context(None, visual, None)

    assert context is not None
    assert "frustration" in context.lower()


def test_infer_causal_chain_from_log(engine):
    """Test causal chain inference from log"""
    log = LogAnalysis(
        log_type="system",
        time_range=(datetime.now(), datetime.now()),
        error_messages=["Error 1"],
        warning_messages=[],
        key_events=[],
        root_cause="Permission issue",
        error_progression=[],
        critical_timestamps=[],
        related_patterns=[],
        suggested_actions=[],
        confidence=0.8
    )

    chain = engine._infer_causal_chain(log, None)

    assert chain is not None
    assert "permission" in chain.lower()


def test_generate_predictions_from_log(engine):
    """Test prediction generation from log analysis"""
    log = LogAnalysis(
        log_type="system",
        time_range=(datetime.now(), datetime.now()),
        error_messages=["E1", "E2", "E3", "E4"],
        warning_messages=[],
        key_events=[],
        root_cause=None,
        error_progression=[],
        critical_timestamps=[],
        related_patterns=[],
        suggested_actions=[],
        confidence=0.8
    )

    predictions = engine._generate_predictions(None, log, None)

    assert isinstance(predictions, list)
    assert len(predictions) > 0


def test_suggest_actions_permission_error(engine):
    """Test action suggestions for permission errors"""
    visual = VisualAnalysis(
        detected_elements=[VisualElement.ERROR_INDICATOR],
        extracted_text="Permission denied",
        dominant_colors=["red"],
        layout_description="Error",
        likely_application="terminal",
        user_intent="Command",
        emotional_indicators=[],
        confidence=0.8
    )

    actions = engine._suggest_actions(visual, None, None, "Permission error")

    assert isinstance(actions, list)
    assert len(actions) > 0
    assert any("sudo" in a.lower() or "permission" in a.lower() for a in actions)


def test_assess_understanding_level_surface(engine):
    """Test understanding level assessment - surface"""
    level = engine._assess_understanding_level(None, None, None, None, None)

    assert level == UnderstandingLevel.SURFACE


def test_assess_understanding_level_integrated(engine):
    """Test understanding level assessment - integrated"""
    visual = VisualAnalysis(
        detected_elements=[],
        extracted_text="",
        dominant_colors=[],
        layout_description="",
        likely_application=None,
        user_intent=None,
        emotional_indicators=[],
        confidence=0.8
    )

    level = engine._assess_understanding_level(
        visual, "log", "state", "context", "emotional"
    )

    assert level == UnderstandingLevel.INTEGRATED


def test_calculate_confidence_single_source(engine):
    """Test confidence calculation with single source"""
    visual = VisualAnalysis(
        detected_elements=[],
        extracted_text="",
        dominant_colors=[],
        layout_description="",
        likely_application=None,
        user_intent=None,
        emotional_indicators=[],
        confidence=0.75
    )

    confidence = engine._calculate_confidence(visual, None, None)

    assert confidence == 0.75


def test_calculate_confidence_multiple_sources(engine):
    """Test confidence calculation with multiple sources"""
    visual = VisualAnalysis(
        detected_elements=[],
        extracted_text="",
        dominant_colors=[],
        layout_description="",
        likely_application=None,
        user_intent=None,
        emotional_indicators=[],
        confidence=0.8
    )

    log = LogAnalysis(
        log_type="",
        time_range=(datetime.now(), datetime.now()),
        error_messages=[],
        warning_messages=[],
        key_events=[],
        root_cause=None,
        error_progression=[],
        critical_timestamps=[],
        related_patterns=[],
        suggested_actions=[],
        confidence=0.6
    )

    confidence = engine._calculate_confidence(visual, log, None)

    assert 0.6 <= confidence <= 0.8  # Average of 0.8 and 0.6


def test_analyze_multiple_inputs(engine, error_screenshot_input, log_file_input):
    """Test analyzing multiple inputs together"""
    inputs = [error_screenshot_input, log_file_input]

    analysis = engine.analyze_multiple(inputs)

    assert isinstance(analysis, MultiModalAnalysis)
    assert len(analysis.understandings) == 2
    assert analysis.overall_confidence > 0
    assert isinstance(analysis.unified_narrative, str)


def test_cross_modal_synthesis(engine):
    """Test cross-modal insight synthesis"""
    understanding1 = MultiModalUnderstanding(
        modality_type=ModalityType.SCREENSHOT,
        understanding_level=UnderstandingLevel.SEMANTIC,
        visual_analysis=VisualAnalysis(
            detected_elements=[VisualElement.ERROR_INDICATOR],
            extracted_text="Error",
            dominant_colors=[],
            layout_description="",
            likely_application=None,
            user_intent=None,
            emotional_indicators=[],
            confidence=0.8
        ),
        log_analysis=None,
        system_state_analysis=None,
        primary_insight="Visual error detected",
        supporting_evidence=[],
        confidence=0.8,
        meta_cognitive_connections=[],
        emotional_context=None,
        causal_chain=None,
        temporal_context=None,
        predictive_insights=[],
        suggested_actions=[],
        questions_to_ask=[],
        timestamp=datetime.now()
    )

    understanding2 = MultiModalUnderstanding(
        modality_type=ModalityType.LOG_FILE,
        understanding_level=UnderstandingLevel.SEMANTIC,
        visual_analysis=None,
        log_analysis=LogAnalysis(
            log_type="",
            time_range=(datetime.now(), datetime.now()),
            error_messages=["Error 1"],
            warning_messages=[],
            key_events=[],
            root_cause=None,
            error_progression=[],
            critical_timestamps=[],
            related_patterns=[],
            suggested_actions=[],
            confidence=0.8
        ),
        system_state_analysis=None,
        primary_insight="Log errors detected",
        supporting_evidence=[],
        confidence=0.8,
        meta_cognitive_connections=[],
        emotional_context=None,
        causal_chain=None,
        temporal_context=None,
        predictive_insights=[],
        suggested_actions=[],
        questions_to_ask=[],
        timestamp=datetime.now()
    )

    insights = engine._synthesize_cross_modal([understanding1, understanding2])

    assert isinstance(insights, list)
    # May have insights about correlation
    if insights:
        assert any("correlated" in i.lower() or "confirm" in i.lower() for i in insights)


def test_unified_narrative_generation(engine):
    """Test unified narrative generation"""
    understandings = [
        MultiModalUnderstanding(
            modality_type=ModalityType.SCREENSHOT,
            understanding_level=UnderstandingLevel.SEMANTIC,
            visual_analysis=None,
            log_analysis=None,
            system_state_analysis=None,
            primary_insight="Error detected visually",
            supporting_evidence=[],
            confidence=0.8,
            meta_cognitive_connections=[],
            emotional_context=None,
            causal_chain=None,
            temporal_context=None,
            predictive_insights=[],
            suggested_actions=[],
            questions_to_ask=[],
            timestamp=datetime.now()
        )
    ]

    narrative = engine._create_unified_narrative(understandings)

    assert isinstance(narrative, str)
    assert len(narrative) > 0
    assert "multi-modal" in narrative.lower()


def test_identify_missing_context(engine):
    """Test identification of missing context"""
    understandings = []  # No understandings

    missing = engine._identify_missing_context(understandings)

    assert isinstance(missing, list)
    assert len(missing) > 0  # Should identify what's missing


def test_assess_consciousness_impact(engine):
    """Test consciousness impact assessment"""
    understandings = [
        MultiModalUnderstanding(
            modality_type=ModalityType.SCREENSHOT,
            understanding_level=UnderstandingLevel.SEMANTIC,
            visual_analysis=VisualAnalysis(
                detected_elements=[VisualElement.ERROR_INDICATOR, VisualElement.ERROR_INDICATOR],
                extracted_text="",
                dominant_colors=[],
                layout_description="",
                likely_application=None,
                user_intent=None,
                emotional_indicators=[],
                confidence=0.8
            ),
            log_analysis=None,
            system_state_analysis=None,
            primary_insight="Errors",
            supporting_evidence=[],
            confidence=0.8,
            meta_cognitive_connections=[],
            emotional_context=None,
            causal_chain=None,
            temporal_context=None,
            predictive_insights=[],
            suggested_actions=[],
            questions_to_ask=[],
            timestamp=datetime.now()
        )
    ]

    impact = engine._assess_consciousness_impact(understandings)

    assert isinstance(impact, str)
    assert len(impact) > 0


def test_get_understanding_summary(engine, error_screenshot_input):
    """Test human-readable summary generation"""
    understanding = engine.understand(error_screenshot_input)

    summary = engine.get_understanding_summary(understanding)

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Multi-Modal" in summary


def test_understanding_history_tracking(engine, error_screenshot_input):
    """Test that understandings are tracked in history"""
    initial_count = len(engine.understanding_history)

    engine.understand(error_screenshot_input)

    assert len(engine.understanding_history) == initial_count + 1


def test_all_modality_types():
    """Test that all ModalityType enum values are valid"""
    for modality in ModalityType:
        assert isinstance(modality.value, str)
        assert len(modality.value) > 0


def test_all_understanding_levels():
    """Test that all UnderstandingLevel enum values are valid"""
    for level in UnderstandingLevel:
        assert isinstance(level.value, str)
        assert len(level.value) > 0


def test_all_visual_elements():
    """Test that all VisualElement enum values are valid"""
    for element in VisualElement:
        assert isinstance(element.value, str)
        assert len(element.value) > 0


def test_modality_input_dataclass():
    """Test ModalityInput dataclass"""
    input_data = ModalityInput(
        modality_type=ModalityType.SCREENSHOT,
        content="Test content",
        timestamp=datetime.now(),
        metadata={"key": "value"}
    )

    assert input_data.modality_type == ModalityType.SCREENSHOT
    assert input_data.content == "Test content"
    assert "key" in input_data.metadata


def test_visual_analysis_dataclass():
    """Test VisualAnalysis dataclass"""
    analysis = VisualAnalysis(
        detected_elements=[VisualElement.TEXT, VisualElement.BUTTON],
        extracted_text="Sample text",
        dominant_colors=["red", "blue"],
        layout_description="Two-column layout",
        likely_application="browser",
        user_intent="Browsing",
        emotional_indicators=["neutral"],
        confidence=0.85
    )

    assert len(analysis.detected_elements) == 2
    assert analysis.extracted_text == "Sample text"
    assert analysis.confidence == 0.85


def test_log_analysis_dataclass():
    """Test LogAnalysis dataclass"""
    analysis = LogAnalysis(
        log_type="application",
        time_range=(datetime.now(), datetime.now()),
        error_messages=["Error 1", "Error 2"],
        warning_messages=["Warning 1"],
        key_events=["Event 1"],
        root_cause="Network issue",
        error_progression=["Progressive errors"],
        critical_timestamps=[datetime.now()],
        related_patterns=["Pattern 1"],
        suggested_actions=["Action 1"],
        confidence=0.8
    )

    assert analysis.log_type == "application"
    assert len(analysis.error_messages) == 2
    assert analysis.root_cause == "Network issue"


def test_system_state_analysis_dataclass():
    """Test SystemStateAnalysis dataclass"""
    analysis = SystemStateAnalysis(
        state_type="resources",
        current_values={"cpu": "50%", "memory": "60%"},
        trend="increasing",
        anomalies=["high_cpu"],
        severity="moderate",
        likely_causes=["Heavy load"],
        predicted_outcomes=["System slowdown"],
        confidence=0.75
    )

    assert analysis.state_type == "resources"
    assert len(analysis.current_values) == 2
    assert analysis.trend == "increasing"


def test_multimodal_understanding_dataclass():
    """Test MultiModalUnderstanding dataclass"""
    understanding = MultiModalUnderstanding(
        modality_type=ModalityType.SCREENSHOT,
        understanding_level=UnderstandingLevel.SEMANTIC,
        visual_analysis=None,
        log_analysis=None,
        system_state_analysis=None,
        primary_insight="Test insight",
        supporting_evidence=["Evidence 1"],
        confidence=0.8,
        meta_cognitive_connections=["Connection 1"],
        emotional_context="Neutral",
        causal_chain="Cause -> Effect",
        temporal_context="Recent",
        predictive_insights=["Prediction 1"],
        suggested_actions=["Action 1"],
        questions_to_ask=["Question 1"],
        timestamp=datetime.now()
    )

    assert understanding.modality_type == ModalityType.SCREENSHOT
    assert understanding.understanding_level == UnderstandingLevel.SEMANTIC
    assert understanding.primary_insight == "Test insight"


def test_multimodal_analysis_dataclass():
    """Test MultiModalAnalysis dataclass"""
    analysis = MultiModalAnalysis(
        timestamp=datetime.now(),
        understandings=[],
        cross_modal_insights=["Insight 1"],
        unified_narrative="Test narrative",
        overall_confidence=0.8,
        missing_context=["Context 1"],
        consciousness_impact="Moderate impact"
    )

    assert len(analysis.cross_modal_insights) == 1
    assert analysis.unified_narrative == "Test narrative"
    assert analysis.overall_confidence == 0.8


def test_empty_content_handling(engine):
    """Test handling of empty content"""
    empty_input = ModalityInput(
        modality_type=ModalityType.SCREENSHOT,
        content="",
        timestamp=datetime.now(),
        metadata={}
    )

    understanding = engine.understand(empty_input)

    assert isinstance(understanding, MultiModalUnderstanding)
    assert understanding.confidence >= 0.0


def test_confidence_bounds(engine, error_screenshot_input):
    """Test that confidence values stay within 0-1 bounds"""
    understanding = engine.understand(error_screenshot_input)

    assert 0.0 <= understanding.confidence <= 1.0

    if understanding.visual_analysis:
        assert 0.0 <= understanding.visual_analysis.confidence <= 1.0
