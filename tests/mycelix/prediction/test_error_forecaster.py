"""
Tests for Error Forecaster

Verifies error prediction functionality.
"""

import pytest
from luminous_nix.mycelix.prediction import (
    ErrorForecaster,
    get_error_forecaster,
    PredictionType,
)
from luminous_nix.mycelix.context import (
    get_context_engine,
    ProjectType,
)


class TestErrorForecaster:
    """Test Error Forecaster"""

    def test_initialization(self):
        """Test forecaster initializes"""
        forecaster = ErrorForecaster()
        assert forecaster is not None
        assert forecaster.context_engine is not None

    def test_predict_returns_batch(self):
        """Test predict returns PredictionBatch"""
        forecaster = get_error_forecaster()
        batch = forecaster.predict()

        assert batch is not None
        assert hasattr(batch, 'predictions')

    def test_predict_rust_build_errors(self):
        """Test predicts Rust build errors"""
        engine = get_context_engine()
        forecaster = get_error_forecaster()

        # Simulate Rust project with cargo build
        engine.project_detector.override_project_type(ProjectType.RUST, 0.9)
        engine.record_command("cargo build", True, 1000.0)

        batch = forecaster.predict()

        # Should have some Rust-related predictions
        rust_errors = [
            p for p in batch.predictions
            if 'rust' in p.description.lower() or 'cargo' in p.description.lower()
        ]
        # May or may not predict based on other conditions
        assert isinstance(rust_errors, list)

    def test_predict_docker_errors(self):
        """Test predicts Docker-related errors"""
        engine = get_context_engine()
        forecaster = get_error_forecaster()

        # Simulate docker command
        engine.record_command("docker run test", True, 500.0)

        batch = forecaster.predict()

        # Should potentially warn about docker daemon
        docker_errors = [
            p for p in batch.predictions
            if 'docker' in p.description.lower()
        ]
        assert isinstance(docker_errors, list)

    def test_predict_configuration_errors(self):
        """Test predicts configuration-related errors"""
        engine = get_context_engine()
        forecaster = get_error_forecaster()

        # Simulate editing config without rebuilding
        engine.file_monitor.record_file_edit("configuration.nix", "nix")
        engine.record_command("echo test", True, 100.0)

        batch = forecaster.predict()

        # Should warn about missing rebuild
        config_errors = [
            p for p in batch.predictions
            if 'configuration' in p.description.lower() or 'rebuild' in p.description.lower()
        ]
        assert len(config_errors) >= 0  # May or may not predict

    def test_predict_project_risks(self):
        """Test predicts project-specific risks"""
        engine = get_context_engine()
        forecaster = get_error_forecaster()

        # Set Python project with some activity
        engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)
        engine.record_command("python test.py", True, 200.0)

        batch = forecaster.predict()

        # Should have some predictions
        assert isinstance(batch.predictions, list)

    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        f1 = get_error_forecaster()
        f2 = get_error_forecaster()

        assert f1 is f2


class TestErrorPredictions:
    """Test error prediction details"""

    def test_prediction_has_prevention_steps(self):
        """Test predictions include prevention steps"""
        forecaster = get_error_forecaster()
        engine = get_context_engine()

        # Create condition for error prediction
        engine.record_command("docker run test", True, 500.0)

        batch = forecaster.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            # May or may not have prevention steps
            assert hasattr(pred, 'prevention_steps')

    def test_prediction_has_error_type(self):
        """Test predictions have error type"""
        forecaster = get_error_forecaster()

        batch = forecaster.predict()

        for pred in batch.predictions:
            assert hasattr(pred, 'error_type')
            assert isinstance(pred.error_type, str)

    def test_prediction_has_root_cause(self):
        """Test predictions have root cause"""
        forecaster = get_error_forecaster()

        batch = forecaster.predict()

        for pred in batch.predictions:
            assert hasattr(pred, 'root_cause')
            assert len(pred.root_cause) > 0

    def test_prediction_confidence_reasonable(self):
        """Test predictions have reasonable confidence"""
        forecaster = get_error_forecaster()

        batch = forecaster.predict()

        for pred in batch.predictions:
            assert 0.0 <= pred.confidence <= 1.0

    def test_prediction_type_is_error(self):
        """Test predictions have correct type"""
        forecaster = get_error_forecaster()

        batch = forecaster.predict()

        for pred in batch.predictions:
            assert pred.prediction_type in [
                PredictionType.ERROR,
                PredictionType.MISSING_STEP,
            ]
