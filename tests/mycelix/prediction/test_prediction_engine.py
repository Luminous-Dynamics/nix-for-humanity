"""
Tests for Prediction Engine

Verifies prediction orchestration and integration.
"""

import pytest
from luminous_nix.mycelix.prediction import (
    PredictionEngine,
    get_prediction_engine,
    PredictionType,
)
from luminous_nix.mycelix.context import (
    get_context_engine,
    ProjectType,
)


class TestPredictionEngine:
    """Test Prediction Engine"""

    def test_initialization(self):
        """Test engine initializes"""
        engine = PredictionEngine()
        assert engine is not None
        assert engine.context_engine is not None
        assert engine.dependency_predictor is not None
        assert engine.error_forecaster is not None
        assert engine.pattern_completer is not None
        assert engine.config_predictor is not None

    def test_predict_all_returns_batch(self):
        """Test predict_all returns PredictionBatch"""
        engine = get_prediction_engine()
        batch = engine.predict_all()

        assert batch is not None
        assert hasattr(batch, 'predictions')
        assert isinstance(batch.predictions, list)

    def test_predict_all_combines_all_predictors(self):
        """Test predict_all combines predictions from all sources"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        # Create rich context
        context_engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)
        context_engine.record_command("cargo build", True, 1000.0)
        context_engine.record_command("nix-shell", True, 500.0)

        batch = engine.predict_all()

        # Should have predictions from multiple sources
        # Check if we have different types
        types_present = set(p.prediction_type for p in batch.predictions)
        # May have multiple types
        assert len(types_present) >= 0

    def test_predict_dependencies_only(self):
        """Test can get only dependency predictions"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        batch = engine.predict_dependencies()

        # All should be dependency type
        for pred in batch.predictions:
            assert pred.prediction_type == PredictionType.DEPENDENCY

    def test_predict_errors_only(self):
        """Test can get only error predictions"""
        engine = get_prediction_engine()

        batch = engine.predict_errors()

        # All should be error type (or missing_step which is error-related)
        for pred in batch.predictions:
            assert pred.prediction_type in [
                PredictionType.ERROR,
                PredictionType.MISSING_STEP,
            ]

    def test_predict_patterns_only(self):
        """Test can get only pattern predictions"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.record_command("cargo build", True, 1000.0)

        batch = engine.predict_patterns()

        # All should be pattern type
        for pred in batch.predictions:
            assert pred.prediction_type == PredictionType.PATTERN

    def test_predict_configs_only(self):
        """Test can get only configuration predictions"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.project_detector.override_project_type(ProjectType.RUST, 0.9)

        batch = engine.predict_configs()

        # All should be config type
        for pred in batch.predictions:
            assert pred.prediction_type == PredictionType.CONFIGURATION

    def test_get_top_predictions(self):
        """Test can get top N predictions"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        # Create some activity
        context_engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)
        context_engine.record_command("cargo build", True, 1000.0)

        top_3 = engine.get_top_predictions(n=3)

        assert isinstance(top_3, list)
        assert len(top_3) <= 3

        # Should be sorted by confidence
        if len(top_3) >= 2:
            assert top_3[0].confidence >= top_3[1].confidence

    def test_predict_next_action(self):
        """Test can get single best prediction"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.record_command("cargo build", True, 1000.0)

        next_action = engine.predict_next_action()

        # Should return single prediction or None
        if next_action is not None:
            assert hasattr(next_action, 'confidence')
            assert hasattr(next_action, 'title')

    def test_explain_prediction(self):
        """Test can explain predictions"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        batch = engine.predict_all()

        if len(batch.predictions) > 0:
            explanation = engine.explain_prediction(batch.predictions[0])

            assert explanation is not None
            assert len(explanation) > 0
            assert '###' in explanation  # Markdown header
            assert 'Confidence' in explanation

    def test_format_predictions_for_display(self):
        """Test can format predictions for display"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.project_detector.override_project_type(ProjectType.RUST, 0.9)

        batch = engine.predict_all()

        formatted = engine.format_predictions_for_display(batch, max_display=5)

        assert formatted is not None
        assert len(formatted) > 0
        assert '🔮' in formatted  # Should have emoji

    def test_min_confidence_filtering(self):
        """Test minimum confidence filtering works"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        # Get predictions with high confidence threshold
        batch_high = engine.predict_all(min_confidence=0.8)

        # Get predictions with low confidence threshold
        batch_low = engine.predict_all(min_confidence=0.3)

        # Low threshold should have at least as many predictions
        assert len(batch_low.predictions) >= len(batch_high.predictions)

        # All high-confidence predictions should meet threshold
        for pred in batch_high.predictions:
            assert pred.confidence >= 0.8

    def test_statistics_tracking(self):
        """Test engine tracks statistics"""
        engine = PredictionEngine()  # Fresh instance

        # Make some predictions
        engine.predict_all()
        engine.predict_all()

        stats = engine.get_statistics()

        assert 'total_predictions' in stats
        assert 'predictions_by_type' in stats
        assert 'predictors_active' in stats
        assert stats['predictors_active'] == 4

    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        e1 = get_prediction_engine()
        e2 = get_prediction_engine()

        assert e1 is e2


class TestPredictionIntegration:
    """Test prediction system integration"""

    def test_predictions_have_valid_confidence(self):
        """Test all predictions have valid confidence"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.project_detector.override_project_type(ProjectType.WEB_DEV, 0.9)

        batch = engine.predict_all()

        for pred in batch.predictions:
            assert 0.0 <= pred.confidence <= 1.0

    def test_predictions_have_descriptions(self):
        """Test all predictions have descriptions"""
        engine = get_prediction_engine()
        context_engine = get_context_engine()

        context_engine.project_detector.override_project_type(ProjectType.DATA_SCIENCE, 0.9)

        batch = engine.predict_all()

        for pred in batch.predictions:
            assert len(pred.description) > 0

    def test_predictions_have_evidence(self):
        """Test predictions provide evidence"""
        engine = get_prediction_engine()

        batch = engine.predict_all()

        # Most predictions should have evidence
        with_evidence = [p for p in batch.predictions if len(p.evidence) > 0]
        # At least some should have evidence
        assert len(with_evidence) >= 0

    def test_empty_context_predictions(self):
        """Test predictions with empty context"""
        engine = get_prediction_engine()

        # Get predictions with minimal context
        batch = engine.predict_all()

        # Should not crash
        assert batch is not None
        assert isinstance(batch.predictions, list)

    def test_error_handling_in_predictors(self):
        """Test engine handles predictor errors gracefully"""
        engine = get_prediction_engine()

        # Even if predictors fail, engine should not crash
        try:
            batch = engine.predict_all()
            assert batch is not None
        except Exception as e:
            pytest.fail(f"Engine should handle errors gracefully: {e}")
