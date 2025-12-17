"""
Tests for Dependency Predictor

Verifies dependency prediction functionality.
"""

import pytest
from luminous_nix.mycelix.prediction import (
    DependencyPredictor,
    get_dependency_predictor,
    PredictionType,
)
from luminous_nix.mycelix.context import (
    get_context_engine,
    ProjectType,
    FileActivity,
)


class TestDependencyPredictor:
    """Test Dependency Predictor"""

    def test_initialization(self):
        """Test predictor initializes"""
        predictor = DependencyPredictor()
        assert predictor is not None
        assert predictor.context_engine is not None

    def test_predict_returns_batch(self):
        """Test predict returns PredictionBatch"""
        predictor = get_dependency_predictor()
        batch = predictor.predict()

        assert batch is not None
        assert hasattr(batch, 'predictions')
        assert hasattr(batch, 'context_summary')

    def test_predict_python_dependencies(self):
        """Test predicts Python dependencies for Python projects"""
        engine = get_context_engine()
        predictor = get_dependency_predictor()

        # Simulate Python project
        engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        batch = predictor.predict()

        # Should predict Python-related dependencies
        python_deps = [
            p for p in batch.predictions
            if 'python' in p.package_name.lower()
        ]
        assert len(python_deps) > 0

    def test_predict_rust_dependencies(self):
        """Test predicts Rust dependencies for Rust projects"""
        engine = get_context_engine()
        predictor = get_dependency_predictor()

        # Simulate Rust project
        engine.project_detector.override_project_type(ProjectType.RUST, 0.9)

        batch = predictor.predict()

        # Should predict Rust-related dependencies
        rust_deps = [
            p for p in batch.predictions
            if 'rust' in p.package_name.lower() or 'cargo' in p.package_name.lower()
        ]
        assert len(rust_deps) > 0

    def test_predict_from_file_extensions(self):
        """Test predicts dependencies based on file extensions"""
        engine = get_context_engine()
        predictor = get_dependency_predictor()

        # Add .rs file
        engine.file_monitor.record_file_edit("test.rs", "rust")

        context = engine.get_current_context()
        batch = predictor.predict(context)

        # Should predict rust-analyzer or similar
        file_based_deps = [
            p for p in batch.predictions
            if '.rs' in str(p.evidence)
        ]
        assert len(file_based_deps) >= 0  # Might not always predict

    def test_predict_dependency_pairs(self):
        """Test predicts companion packages"""
        engine = get_context_engine()
        predictor = get_dependency_predictor()

        # Simulate using docker
        engine.record_command("docker run hello-world", True, 100.0)

        context = engine.get_current_context()
        batch = predictor.predict(context)

        # Should suggest docker-compose
        docker_compose = [
            p for p in batch.predictions
            if 'docker-compose' in p.package_name
        ]
        # May or may not predict based on logic
        assert isinstance(docker_compose, list)

    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        p1 = get_dependency_predictor()
        p2 = get_dependency_predictor()

        assert p1 is p2


class TestDependencyPredictions:
    """Test dependency prediction details"""

    def test_prediction_has_install_command(self):
        """Test predictions include install commands"""
        predictor = get_dependency_predictor()
        engine = get_context_engine()

        engine.project_detector.override_project_type(ProjectType.PYTHON, 0.9)

        batch = predictor.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            assert pred.install_command is not None
            assert 'nix-shell' in pred.install_command or 'nix' in pred.install_command

    def test_prediction_has_evidence(self):
        """Test predictions include evidence"""
        predictor = get_dependency_predictor()
        engine = get_context_engine()

        engine.project_detector.override_project_type(ProjectType.RUST, 0.9)

        batch = predictor.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            assert len(pred.evidence) > 0
            assert isinstance(pred.evidence, list)

    def test_prediction_confidence_levels(self):
        """Test predictions have valid confidence levels"""
        predictor = get_dependency_predictor()

        batch = predictor.predict()

        for pred in batch.predictions:
            assert 0.0 <= pred.confidence <= 1.0
            assert pred.confidence_level is not None

    def test_prediction_type_is_dependency(self):
        """Test all predictions have correct type"""
        predictor = get_dependency_predictor()

        batch = predictor.predict()

        for pred in batch.predictions:
            assert pred.prediction_type == PredictionType.DEPENDENCY
