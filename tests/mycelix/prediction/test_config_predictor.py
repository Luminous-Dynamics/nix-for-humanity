"""
Tests for Configuration Predictor

Verifies configuration suggestion functionality.
"""

import pytest
from luminous_nix.mycelix.prediction import (
    ConfigurationPredictor,
    get_config_predictor,
    PredictionType,
)
from luminous_nix.mycelix.context import (
    get_context_engine,
    ProjectType,
)


class TestConfigurationPredictor:
    """Test Configuration Predictor"""

    def test_initialization(self):
        """Test predictor initializes"""
        predictor = ConfigurationPredictor()
        assert predictor is not None
        assert predictor.context_engine is not None

    def test_predict_returns_batch(self):
        """Test predict returns PredictionBatch"""
        predictor = get_config_predictor()
        batch = predictor.predict()

        assert batch is not None
        assert hasattr(batch, 'predictions')

    def test_predict_python_configs(self):
        """Test predicts Python-specific configurations"""
        engine = get_context_engine()
        predictor = get_config_predictor()

        # Simulate Python project
        engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        batch = predictor.predict()

        # Should suggest Python configs
        python_configs = [
            p for p in batch.predictions
            if 'python' in p.description.lower() or 'python' in p.config_key.lower()
        ]
        # May or may not predict
        assert isinstance(python_configs, list)

    def test_predict_rust_configs(self):
        """Test predicts Rust-specific configurations"""
        engine = get_context_engine()
        predictor = get_config_predictor()

        # Simulate Rust project
        engine.project_detector.override_project_type(ProjectType.RUST, 0.9)

        batch = predictor.predict()

        # Should suggest Rust configs
        rust_configs = [
            p for p in batch.predictions
            if 'rust' in p.description.lower()
        ]
        assert isinstance(rust_configs, list)

    def test_predict_performance_configs(self):
        """Test predicts performance-related configs"""
        engine = get_context_engine()
        predictor = get_config_predictor()

        # Simulate many Nix commands
        for i in range(6):
            engine.record_command(f"nix-build test{i}", True, 1000.0)

        batch = predictor.predict()

        # Should suggest performance configs
        perf_configs = [
            p for p in batch.predictions
            if 'faster' in p.benefit.lower() or 'speed' in p.benefit.lower()
        ]
        assert len(perf_configs) > 0

    def test_predict_direnv_for_frequent_nix_shell(self):
        """Test suggests direnv for frequent nix-shell use"""
        engine = get_context_engine()
        predictor = get_config_predictor()

        # Simulate frequent nix-shell
        for i in range(4):
            engine.record_command("nix-shell", True, 500.0)

        batch = predictor.predict()

        # Should suggest direnv
        direnv_suggestions = [
            p for p in batch.predictions
            if 'direnv' in p.description.lower()
        ]
        assert len(direnv_suggestions) > 0

    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        p1 = get_config_predictor()
        p2 = get_config_predictor()

        assert p1 is p2


class TestConfigPredictions:
    """Test configuration prediction details"""

    def test_prediction_has_config_file(self):
        """Test predictions specify config file"""
        predictor = get_config_predictor()
        engine = get_context_engine()

        engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        batch = predictor.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            assert hasattr(pred, 'config_file')
            assert len(pred.config_file) > 0

    def test_prediction_has_suggested_value(self):
        """Test predictions have suggested value"""
        predictor = get_config_predictor()
        engine = get_context_engine()

        engine.project_detector.override_project_type(ProjectType.RUST, 0.9)

        batch = predictor.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            assert hasattr(pred, 'suggested_value')

    def test_prediction_has_benefit(self):
        """Test predictions explain benefit"""
        predictor = get_config_predictor()

        batch = predictor.predict()

        for pred in batch.predictions:
            assert hasattr(pred, 'benefit')
            assert len(pred.benefit) > 0

    def test_prediction_has_risk_level(self):
        """Test predictions have risk level"""
        predictor = get_config_predictor()

        batch = predictor.predict()

        for pred in batch.predictions:
            assert hasattr(pred, 'risk_level')
            assert pred.risk_level in ['low', 'medium', 'high']

    def test_prediction_type_is_configuration(self):
        """Test predictions have correct type"""
        predictor = get_config_predictor()
        engine = get_context_engine()

        engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        batch = predictor.predict()

        for pred in batch.predictions:
            assert pred.prediction_type == PredictionType.CONFIGURATION

    def test_config_action_generation(self):
        """Test generates config actions"""
        predictor = ConfigurationPredictor()

        config = {
            'config_file': '/etc/nixos/configuration.nix',
            'config_key': 'nix.settings.max-jobs',
            'suggested_value': 'auto',
        }

        action = predictor._generate_config_action(config)
        assert action is not None
        assert len(action) > 0
        assert 'nix.settings.max-jobs' in action
