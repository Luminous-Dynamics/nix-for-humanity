"""
Tests for Pattern Completer

Verifies pattern learning and prediction functionality.
"""

import pytest
from luminous_nix.mycelix.prediction import (
    PatternCompleter,
    get_pattern_completer,
    PredictionType,
)
from luminous_nix.mycelix.context import get_context_engine


class TestPatternCompleter:
    """Test Pattern Completer"""

    def test_initialization(self):
        """Test completer initializes"""
        completer = PatternCompleter()
        assert completer is not None
        assert completer.context_engine is not None

    def test_predict_returns_batch(self):
        """Test predict returns PredictionBatch"""
        completer = get_pattern_completer()
        batch = completer.predict()

        assert batch is not None
        assert hasattr(batch, 'predictions')

    def test_predict_build_then_test_pattern(self):
        """Test predicts test after build"""
        engine = get_context_engine()
        completer = get_pattern_completer()

        # Simulate build command
        engine.record_command("cargo build", True, 2000.0)

        batch = completer.predict()

        # Should predict test next
        test_predictions = [
            p for p in batch.predictions
            if 'test' in p.predicted_next_step.lower()
        ]
        assert len(test_predictions) > 0

    def test_predict_commit_then_push_pattern(self):
        """Test predicts push after commit"""
        engine = get_context_engine()
        completer = get_pattern_completer()

        # Simulate git commit
        engine.record_command("git commit -m 'test'", True, 500.0)

        batch = completer.predict()

        # Should predict push next
        push_predictions = [
            p for p in batch.predictions
            if 'push' in p.predicted_next_step.lower()
        ]
        assert len(push_predictions) > 0

    def test_predict_add_then_commit_pattern(self):
        """Test predicts commit after add"""
        engine = get_context_engine()
        completer = get_pattern_completer()

        # Simulate git add
        engine.record_command("git add .", True, 200.0)

        batch = completer.predict()

        # Should predict commit next
        commit_predictions = [
            p for p in batch.predictions
            if 'commit' in p.predicted_next_step.lower()
        ]
        assert len(commit_predictions) > 0

    def test_learn_from_sequences(self):
        """Test learns patterns from command sequences"""
        engine = get_context_engine()
        completer = get_pattern_completer()

        # Create a pattern by running commands
        engine.record_command("make build", True, 1000.0)
        engine.record_command("make test", True, 2000.0)
        engine.record_command("make build", True, 1000.0)
        engine.record_command("make test", True, 2000.0)

        # Should learn the pattern
        completer._learn_from_context(engine.get_current_context())

        stats = completer.get_pattern_statistics()
        assert stats['total_sequences_learned'] > 0

    def test_command_simplification(self):
        """Test command simplification works"""
        completer = PatternCompleter()

        simplified = completer._simplify_command("git commit -m 'long message here'")
        assert simplified == "git commit"

        simplified = completer._simplify_command("cargo build --release")
        assert simplified == "cargo build"

    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        c1 = get_pattern_completer()
        c2 = get_pattern_completer()

        assert c1 is c2


class TestPatternPredictions:
    """Test pattern prediction details"""

    def test_prediction_has_frequency(self):
        """Test predictions include frequency"""
        completer = get_pattern_completer()
        engine = get_context_engine()

        engine.record_command("cargo build", True, 1000.0)

        batch = completer.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            assert hasattr(pred, 'pattern_frequency')
            assert 0.0 <= pred.pattern_frequency <= 1.0

    def test_prediction_has_timing_info(self):
        """Test predictions include timing information"""
        completer = get_pattern_completer()
        engine = get_context_engine()

        engine.record_command("git commit", True, 500.0)

        batch = completer.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            assert hasattr(pred, 'typical_delay_seconds')
            assert pred.typical_delay_seconds >= 0

    def test_prediction_has_suggested_action(self):
        """Test predictions include suggested actions"""
        completer = get_pattern_completer()
        engine = get_context_engine()

        engine.record_command("cargo build", True, 1000.0)

        batch = completer.predict()

        if len(batch.predictions) > 0:
            pred = batch.predictions[0]
            # May or may not have suggested action
            assert hasattr(pred, 'suggested_action')

    def test_prediction_type_is_pattern(self):
        """Test predictions have correct type"""
        completer = get_pattern_completer()
        engine = get_context_engine()

        engine.record_command("cargo build", True, 1000.0)

        batch = completer.predict()

        for pred in batch.predictions:
            assert pred.prediction_type == PredictionType.PATTERN

    def test_pattern_statistics(self):
        """Test can get pattern statistics"""
        completer = get_pattern_completer()

        stats = completer.get_pattern_statistics()

        assert 'total_sequences_learned' in stats
        assert 'unique_commands_seen' in stats
        assert isinstance(stats['total_sequences_learned'], int)
