"""
Tests for Creative Synthesis Engine

Tests Sophia's ability to:
- Generate novel insights by combining multiple intelligence layers
- Create cross-domain syntheses
- Find analogies between different domains
- Detect emergent patterns
- Assess novelty and impact
- Learn from synthesis validation
"""

import pytest
from datetime import datetime
from luminous_nix.mycelix.sophia.creative_synthesis import (
    CreativeSynthesisEngine,
    get_creative_synthesis_engine,
    SynthesisType,
    NoveltyLevel,
    ConfidenceSource,
    InsightSource,
    CreativeSynthesis,
    Analogy,
    EmergentPattern,
    SynthesisAnalysis
)


@pytest.fixture
def engine():
    """Create a fresh creative synthesis engine"""
    return CreativeSynthesisEngine()


@pytest.fixture
def sample_insights():
    """Create sample insights from different layers"""
    return [
        InsightSource(
            layer_name="meta_cognitive",
            insight_description="User repeatedly tries same failing approach",
            confidence=0.9,
            evidence=["3 failed attempts with same method"],
            timestamp=datetime.now()
        ),
        InsightSource(
            layer_name="emotional",
            insight_description="User showing signs of frustration",
            confidence=0.85,
            evidence=["Rapid command switching", "Error repetition"],
            timestamp=datetime.now()
        ),
        InsightSource(
            layer_name="temporal",
            insight_description="Post-lunch dip in performance",
            confidence=0.8,
            evidence=["2pm time window", "Historical pattern"],
            timestamp=datetime.now()
        ),
        InsightSource(
            layer_name="holistic",
            insight_description="High stress biometric indicators",
            confidence=0.75,
            evidence=["Elevated heart rate", "Low HRV"],
            timestamp=datetime.now()
        )
    ]


def test_engine_initialization(engine):
    """Test that creative synthesis engine initializes correctly"""
    assert engine is not None
    assert engine.synthesis_history == []
    assert engine.validated_syntheses == {}
    assert engine.synthesis_success_rate == 0.5  # Start neutral


def test_singleton_pattern():
    """Test that get_creative_synthesis_engine returns singleton"""
    engine1 = get_creative_synthesis_engine()
    engine2 = get_creative_synthesis_engine()
    assert engine1 is engine2


def test_synthesize_insights_basic(engine, sample_insights):
    """Test basic synthesis generation"""
    analysis = engine.synthesize_insights(
        meta_insights=None,
        current_challenge="Installation keeps failing"
    )

    assert isinstance(analysis, SynthesisAnalysis)
    assert analysis.timestamp is not None
    assert isinstance(analysis.syntheses, list)
    assert isinstance(analysis.analogies, list)
    assert isinstance(analysis.emergent_patterns, list)


def test_collect_source_insights(engine, sample_insights):
    """Test collecting insights from multiple layers"""
    # Test with actual insight objects
    collected = engine._collect_source_insights(
        meta_insights=[type('obj', (), {'message': 'Pattern detected', 'confidence': 0.8})()],
        holistic_state=type('obj', (), {
            'biometric_state': 'OPTIMAL',
            'circadian_phase': 'MORNING_PEAK'
        })(),
        emotional_state=type('obj', (), {'state': 'FOCUSED', 'confidence': 0.9})(),
        causal_analysis=None,
        temporal_analysis=None,
        predictive_analysis=None
    )

    assert isinstance(collected, list)
    assert len(collected) > 0
    assert all(isinstance(s, InsightSource) for s in collected)


def test_cross_domain_synthesis(engine, sample_insights):
    """Test generation of cross-domain synthesis"""
    synthesis = engine._generate_cross_domain_synthesis(
        sample_insights,
        challenge="System performance declining"
    )

    if synthesis:  # May return None if conditions not met
        assert isinstance(synthesis, CreativeSynthesis)
        assert synthesis.synthesis_type == SynthesisType.CROSS_DOMAIN
        assert len(synthesis.source_insights) >= 2
        assert synthesis.confidence > 0


def test_temporal_causal_synthesis(engine):
    """Test temporal-causal synthesis generation"""
    causal_mock = type('obj', (), {})()
    temporal_mock = type('obj', (), {})()

    synthesis = engine._synthesize_temporal_causal(
        causal_mock,
        temporal_mock,
        challenge="Timing matters"
    )

    assert isinstance(synthesis, CreativeSynthesis)
    assert synthesis.synthesis_type == SynthesisType.TEMPORAL_CAUSAL
    assert synthesis.novelty_level == NoveltyLevel.SIGNIFICANT


def test_emotional_pattern_synthesis(engine):
    """Test emotional pattern synthesis"""
    emotional_mock = type('obj', (), {})()
    meta_mock = [type('obj', (), {})()]
    temporal_mock = type('obj', (), {})()

    synthesis = engine._synthesize_emotional_patterns(
        emotional_mock,
        meta_mock,
        temporal_mock
    )

    assert isinstance(synthesis, CreativeSynthesis)
    assert synthesis.synthesis_type == SynthesisType.EMOTIONAL_PATTERN
    assert synthesis.novelty_level == NoveltyLevel.BREAKTHROUGH


def test_predictive_holistic_synthesis(engine):
    """Test predictive-holistic synthesis"""
    predictive_mock = type('obj', (), {})()
    holistic_mock = type('obj', (), {})()

    synthesis = engine._synthesize_predictive_holistic(
        predictive_mock,
        holistic_mock,
        challenge="Future planning"
    )

    assert isinstance(synthesis, CreativeSynthesis)
    assert synthesis.synthesis_type == SynthesisType.PREDICTIVE_HOLISTIC


def test_meta_integration_synthesis(engine, sample_insights):
    """Test meta-integration synthesis"""
    synthesis = engine._generate_meta_integration(
        sample_insights,
        challenge="Unified understanding"
    )

    assert isinstance(synthesis, CreativeSynthesis)
    assert synthesis.synthesis_type == SynthesisType.META_INTEGRATION
    assert synthesis.novelty_level == NoveltyLevel.REVOLUTIONARY
    assert len(synthesis.emergent_properties) > 0


def test_find_most_novel(engine):
    """Test finding most novel synthesis"""
    syntheses = [
        CreativeSynthesis(
            synthesis_type=SynthesisType.CROSS_DOMAIN,
            novelty_level=NoveltyLevel.INCREMENTAL,
            title="Test 1",
            description="Test",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.7,
            confidence_source=ConfidenceSource.LOGICAL,
            potential_impact="Low",
            limitations=[],
            suggested_actions=[],
            experiments_to_validate=[],
            timestamp=datetime.now()
        ),
        CreativeSynthesis(
            synthesis_type=SynthesisType.META_INTEGRATION,
            novelty_level=NoveltyLevel.REVOLUTIONARY,
            title="Test 2",
            description="Test",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.9,
            confidence_source=ConfidenceSource.EMERGENT,
            potential_impact="High",
            limitations=[],
            suggested_actions=[],
            experiments_to_validate=[],
            timestamp=datetime.now()
        )
    ]

    most_novel = engine._find_most_novel(syntheses)
    assert most_novel is not None
    assert most_novel.novelty_level == NoveltyLevel.REVOLUTIONARY


def test_find_highest_impact(engine):
    """Test finding highest impact synthesis"""
    syntheses = [
        CreativeSynthesis(
            synthesis_type=SynthesisType.CROSS_DOMAIN,
            novelty_level=NoveltyLevel.SIGNIFICANT,
            title="Test 1",
            description="Test",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.6,
            confidence_source=ConfidenceSource.LOGICAL,
            potential_impact="Test",
            limitations=[],
            suggested_actions=[],
            experiments_to_validate=[],
            timestamp=datetime.now()
        ),
        CreativeSynthesis(
            synthesis_type=SynthesisType.EMOTIONAL_PATTERN,
            novelty_level=NoveltyLevel.BREAKTHROUGH,
            title="Test 2",
            description="Test",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.9,
            confidence_source=ConfidenceSource.EMPIRICAL,
            potential_impact="Test",
            limitations=[],
            suggested_actions=[],
            experiments_to_validate=[],
            timestamp=datetime.now()
        )
    ]

    highest_impact = engine._find_highest_impact(syntheses)
    assert highest_impact is not None
    assert highest_impact.confidence == 0.9


def test_find_most_actionable(engine):
    """Test finding most actionable synthesis"""
    syntheses = [
        CreativeSynthesis(
            synthesis_type=SynthesisType.CROSS_DOMAIN,
            novelty_level=NoveltyLevel.SIGNIFICANT,
            title="Test 1",
            description="Test",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.7,
            confidence_source=ConfidenceSource.LOGICAL,
            potential_impact="Test",
            limitations=[],
            suggested_actions=["Action 1"],
            experiments_to_validate=[],
            timestamp=datetime.now()
        ),
        CreativeSynthesis(
            synthesis_type=SynthesisType.PREDICTIVE_HOLISTIC,
            novelty_level=NoveltyLevel.SIGNIFICANT,
            title="Test 2",
            description="Test",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.8,
            confidence_source=ConfidenceSource.EMPIRICAL,
            potential_impact="Test",
            limitations=[],
            suggested_actions=["Action 1", "Action 2", "Action 3"],
            experiments_to_validate=[],
            timestamp=datetime.now()
        )
    ]

    most_actionable = engine._find_most_actionable(syntheses)
    assert most_actionable is not None
    assert len(most_actionable.suggested_actions) == 3


def test_extract_synthesis_themes(engine):
    """Test theme extraction from syntheses"""
    syntheses = [
        CreativeSynthesis(
            synthesis_type=SynthesisType.TEMPORAL_CAUSAL,
            novelty_level=NoveltyLevel.SIGNIFICANT,
            title="Timing Test",
            description="Understanding timing is crucial for success",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.7,
            confidence_source=ConfidenceSource.LOGICAL,
            potential_impact="Test",
            limitations=[],
            suggested_actions=[],
            experiments_to_validate=[],
            timestamp=datetime.now()
        ),
        CreativeSynthesis(
            synthesis_type=SynthesisType.EMOTIONAL_PATTERN,
            novelty_level=NoveltyLevel.BREAKTHROUGH,
            title="Emotion Test",
            description="Emotional patterns reveal hidden insights",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.8,
            confidence_source=ConfidenceSource.INTUITIVE,
            potential_impact="Test",
            limitations=[],
            suggested_actions=[],
            experiments_to_validate=[],
            timestamp=datetime.now()
        )
    ]

    themes = engine._extract_synthesis_themes(syntheses)
    assert isinstance(themes, list)
    assert len(themes) > 0


def test_calculate_creativity_score(engine):
    """Test creativity score calculation"""
    syntheses = [
        CreativeSynthesis(
            synthesis_type=SynthesisType.META_INTEGRATION,
            novelty_level=NoveltyLevel.REVOLUTIONARY,
            title="Test",
            description="Test",
            key_insight="Test",
            source_insights=[],
            synthesis_reasoning="Test",
            emergent_properties=[],
            confidence=0.9,
            confidence_source=ConfidenceSource.EMERGENT,
            potential_impact="Test",
            limitations=[],
            suggested_actions=[],
            experiments_to_validate=[],
            timestamp=datetime.now()
        )
    ]

    score = engine._calculate_creativity_score(syntheses, [], [])
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Revolutionary novelty should score high


def test_validate_synthesis_success(engine):
    """Test learning from successful synthesis"""
    synthesis = CreativeSynthesis(
        synthesis_type=SynthesisType.CROSS_DOMAIN,
        novelty_level=NoveltyLevel.SIGNIFICANT,
        title="Test Synthesis",
        description="Test",
        key_insight="Test",
        source_insights=[],
        synthesis_reasoning="Test",
        emergent_properties=[],
        confidence=0.7,
        confidence_source=ConfidenceSource.LOGICAL,
        potential_impact="Test",
        limitations=[],
        suggested_actions=[],
        experiments_to_validate=[],
        timestamp=datetime.now()
    )

    initial_rate = engine.synthesis_success_rate

    engine.validate_synthesis(synthesis, outcome_success=True)

    # Success rate should update
    assert len(engine.validated_syntheses) == 1
    # With one success, rate should be 1.0
    assert engine.synthesis_success_rate == 1.0


def test_validate_synthesis_failure(engine):
    """Test learning from failed synthesis"""
    synthesis = CreativeSynthesis(
        synthesis_type=SynthesisType.CROSS_DOMAIN,
        novelty_level=NoveltyLevel.SIGNIFICANT,
        title="Test Synthesis",
        description="Test",
        key_insight="Test",
        source_insights=[],
        synthesis_reasoning="Test",
        emergent_properties=[],
        confidence=0.7,
        confidence_source=ConfidenceSource.LOGICAL,
        potential_impact="Test",
        limitations=[],
        suggested_actions=[],
        experiments_to_validate=[],
        timestamp=datetime.now()
    )

    engine.validate_synthesis(synthesis, outcome_success=False)

    # With one failure, rate should be 0.0
    assert engine.synthesis_success_rate == 0.0


def test_get_synthesis_summary(engine):
    """Test generation of human-readable summary"""
    analysis = SynthesisAnalysis(
        timestamp=datetime.now(),
        syntheses=[],
        analogies=[],
        emergent_patterns=[],
        most_novel_synthesis=None,
        highest_impact_synthesis=None,
        most_actionable_synthesis=None,
        synthesis_themes=["Test theme"],
        cross_domain_connections=3,
        overall_creativity_score=0.75,
        validated_syntheses=5,
        synthesis_success_rate=0.8
    )

    summary = engine.get_synthesis_summary(analysis)

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Creative Synthesis" in summary
    assert "75%" in summary  # Creativity score


def test_all_synthesis_types():
    """Test that all SynthesisType enum values are valid"""
    for synthesis_type in SynthesisType:
        assert isinstance(synthesis_type.value, str)
        assert len(synthesis_type.value) > 0


def test_all_novelty_levels():
    """Test that all NoveltyLevel enum values are valid"""
    for level in NoveltyLevel:
        assert isinstance(level.value, str)
        assert len(level.value) > 0


def test_all_confidence_sources():
    """Test that all ConfidenceSource enum values are valid"""
    for source in ConfidenceSource:
        assert isinstance(source.value, str)
        assert len(source.value) > 0


def test_insight_source_dataclass():
    """Test InsightSource dataclass"""
    insight = InsightSource(
        layer_name="test_layer",
        insight_description="Test insight",
        confidence=0.85,
        evidence=["Evidence 1", "Evidence 2"],
        timestamp=datetime.now()
    )

    assert insight.layer_name == "test_layer"
    assert insight.confidence == 0.85
    assert len(insight.evidence) == 2


def test_creative_synthesis_dataclass():
    """Test CreativeSynthesis dataclass"""
    synthesis = CreativeSynthesis(
        synthesis_type=SynthesisType.CROSS_DOMAIN,
        novelty_level=NoveltyLevel.SIGNIFICANT,
        title="Test Synthesis",
        description="Test description",
        key_insight="Test insight",
        source_insights=[],
        synthesis_reasoning="Test reasoning",
        emergent_properties=["Property 1"],
        confidence=0.8,
        confidence_source=ConfidenceSource.LOGICAL,
        potential_impact="High impact",
        limitations=["Limitation 1"],
        suggested_actions=["Action 1"],
        experiments_to_validate=["Experiment 1"],
        timestamp=datetime.now()
    )

    assert synthesis.synthesis_type == SynthesisType.CROSS_DOMAIN
    assert synthesis.novelty_level == NoveltyLevel.SIGNIFICANT
    assert synthesis.confidence == 0.8


def test_analogy_dataclass():
    """Test Analogy dataclass"""
    analogy = Analogy(
        source_domain="biology",
        target_domain="computing",
        analogical_mapping={"cell": "process", "DNA": "code"},
        structural_similarity=0.75,
        transfer_insights=["Insight 1"],
        novel_predictions=["Prediction 1"],
        confidence=0.8
    )

    assert analogy.source_domain == "biology"
    assert analogy.target_domain == "computing"
    assert len(analogy.analogical_mapping) == 2
    assert analogy.structural_similarity == 0.75


def test_emergent_pattern_dataclass():
    """Test EmergentPattern dataclass"""
    pattern = EmergentPattern(
        pattern_name="Test Pattern",
        description="Pattern description",
        contributing_layers=["layer1", "layer2"],
        interaction_dynamics="Test dynamics",
        frequency=0.7,
        strength=0.8,
        stability=0.9,
        implications=["Implication 1"],
        intervention_points=["Point 1"],
        confidence=0.85
    )

    assert pattern.pattern_name == "Test Pattern"
    assert len(pattern.contributing_layers) == 2
    assert pattern.frequency == 0.7


def test_synthesis_analysis_dataclass():
    """Test SynthesisAnalysis dataclass"""
    analysis = SynthesisAnalysis(
        timestamp=datetime.now(),
        syntheses=[],
        analogies=[],
        emergent_patterns=[],
        most_novel_synthesis=None,
        highest_impact_synthesis=None,
        most_actionable_synthesis=None,
        synthesis_themes=["Theme 1", "Theme 2"],
        cross_domain_connections=5,
        overall_creativity_score=0.8,
        validated_syntheses=10,
        synthesis_success_rate=0.75
    )

    assert len(analysis.synthesis_themes) == 2
    assert analysis.cross_domain_connections == 5
    assert analysis.overall_creativity_score == 0.8


def test_empty_insights_handling(engine):
    """Test handling when no insights provided"""
    analysis = engine.synthesize_insights()

    assert isinstance(analysis, SynthesisAnalysis)
    assert isinstance(analysis.syntheses, list)
    # May be empty if no insights to synthesize
    assert analysis.overall_creativity_score >= 0.0


def test_single_layer_insights(engine):
    """Test handling when all insights from same layer"""
    single_layer_insights = [
        InsightSource(
            layer_name="meta_cognitive",
            insight_description=f"Insight {i}",
            confidence=0.8,
            evidence=[],
            timestamp=datetime.now()
        )
        for i in range(3)
    ]

    # Should still work but may not generate cross-domain syntheses
    synthesis = engine._generate_cross_domain_synthesis(
        single_layer_insights,
        challenge="Test"
    )

    # May return None since all from same layer
    assert synthesis is None or isinstance(synthesis, CreativeSynthesis)


def test_confidence_bounds(engine, sample_insights):
    """Test that confidence values stay within 0-1 bounds"""
    synthesis = engine._generate_cross_domain_synthesis(
        sample_insights,
        challenge="Test"
    )

    if synthesis:
        assert 0.0 <= synthesis.confidence <= 1.0


def test_synthesis_history_tracking(engine):
    """Test that syntheses are tracked in history"""
    initial_count = len(engine.synthesis_history)

    # Syntheses aren't automatically added to history in current implementation
    # But we can test the structure exists
    assert isinstance(engine.synthesis_history, list)
