"""
Test suite for revolutionary behavioral detection system.

Tests all components:
1. Behavioral feature extraction
2. Neural network classifier
3. Continuous learning
4. Archetype evolution tracking
5. Integration layer
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from luminous_nix.ai.behavioral_features import (
    BehavioralFeatureExtractor, BehavioralSignal, BehavioralFeatures
)
from luminous_nix.ai.behavioral_classifier import (
    ArchetypeClassifier, BehavioralArchetypeDetector
)
from luminous_nix.ai.continuous_learner import ContinuousLearner, TrainingExample
from luminous_nix.ai.archetype_evolution import ArchetypeEvolutionTracker
from luminous_nix.ai.behavioral_integration import BehavioralIntegrationLayer
from luminous_nix.ai.user_profiler import UserArchetype, TechnicalLevel


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def feature_extractor():
    """Create feature extractor"""
    return BehavioralFeatureExtractor()


@pytest.fixture
def detector():
    """Create behavioral detector"""
    return BehavioralArchetypeDetector()


@pytest.fixture
def learner(detector):
    """Create continuous learner"""
    return ContinuousLearner(detector)


@pytest.fixture
def evolution_tracker():
    """Create evolution tracker"""
    return ArchetypeEvolutionTracker(user_id="test_user")


@pytest.fixture
def integration_layer():
    """Create integration layer"""
    return BehavioralIntegrationLayer(user_id="test_user")


# === Behavioral Feature Extraction Tests ===

def test_signal_recording(feature_extractor):
    """Test recording behavioral signals"""
    signal = BehavioralSignal(
        user_id="test_user",
        timestamp="2025-12-03T10:00:00",
        query="how does nix work?",
        query_type="explain",
        asked_why_how=True,
        deep_question=True
    )

    feature_extractor.record_signal(signal)

    assert len(feature_extractor.signals["test_user"]) == 1
    assert feature_extractor.signals["test_user"][0].asked_why_how is True


def test_feature_extraction_learner_pattern(feature_extractor):
    """Test extracting Learner behavioral features"""
    # Simulate Learner behavior: lots of why/how questions, full reading
    for i in range(10):
        signal = BehavioralSignal(
            user_id="test_user",
            timestamp=f"2025-12-03T10:{i:02d}:00",
            query=f"why does {i} work this way?",
            query_type="explain",
            asked_why_how=True,
            deep_question=True,
            reading_time_ms=5000,  # Reads fully
            requested_teaching=True
        )
        feature_extractor.record_signal(signal)

    features = feature_extractor.extract_features("test_user")

    # Learner indicators
    assert features.why_how_question_ratio > 0.7  # Lots of why/how
    assert features.teaching_participation_rate > 0.5  # Engages with teaching
    assert features.avg_reading_time_ratio > 0.5  # Reads responses


def test_feature_extraction_pragmatist_pattern(feature_extractor):
    """Test extracting Pragmatist behavioral features"""
    # Simulate Pragmatist behavior: quick actions, skip reading
    for i in range(10):
        signal = BehavioralSignal(
            user_id="test_user",
            timestamp=f"2025-12-03T10:{i:02d}:00",
            query=f"install package{i}",
            command_used=f"nix-env -iA package{i}",
            query_type="install",
            immediate_action=True,  # Acts immediately
            skipped=True,  # Skips reading
            reading_time_ms=500,  # Minimal reading
            automation_request=True
        )
        feature_extractor.record_signal(signal)

    features = feature_extractor.extract_features("test_user")

    # Pragmatist indicators
    assert features.immediate_action_rate > 0.7  # Acts fast
    assert features.skipping_frequency > 0.7  # Skips reading
    assert features.automation_preference > 0.5  # Wants automation


def test_feature_extraction_explorer_pattern(feature_extractor):
    """Test extracting Explorer behavioral features"""
    # Simulate Explorer behavior: alternatives, curiosity
    for i in range(10):
        signal = BehavioralSignal(
            user_id="test_user",
            timestamp=f"2025-12-03T10:{i:02d}:00",
            query=f"what are alternatives to package{i}?",
            query_type="search",
            requested_alternatives=True,
            experimentation=True,
            documentation_reading=True
        )
        feature_extractor.record_signal(signal)

    features = feature_extractor.extract_features("test_user")

    # Explorer indicators
    assert features.alternative_exploration_rate > 0.7  # Explores alternatives
    assert features.curiosity_score > 0.5  # High curiosity
    assert features.experimentation_frequency > 0.5  # Experiments


def test_feature_extraction_creator_pattern(feature_extractor):
    """Test extracting Creator behavioral features"""
    # Simulate Creator behavior: customization, complex commands
    for i in range(10):
        signal = BehavioralSignal(
            user_id="test_user",
            timestamp=f"2025-12-03T10:{i:02d}:00",
            query=f"how to customize module {i}?",
            command_used="nix-build",  # Complex command
            query_type="config",
            customization_attempt=True,
            experimentation=True
        )
        feature_extractor.record_signal(signal)

    features = feature_extractor.extract_features("test_user")

    # Creator indicators
    assert features.customization_frequency > 0.7  # High customization
    assert features.experimentation_frequency > 0.7  # Experiments
    assert features.command_complexity > 0.5  # Complex commands


def test_feature_to_numpy_conversion(feature_extractor):
    """Test converting features to numpy array"""
    features = BehavioralFeatures()
    array = feature_extractor.to_numpy_array(features)

    assert array.shape == (27,)  # 27 features
    assert array.dtype == 'float32'


# === Neural Network Classifier Tests ===

def test_classifier_architecture():
    """Test neural network architecture"""
    classifier = ArchetypeClassifier(input_size=27, hidden_sizes=[64, 32, 16])

    assert classifier.input_size == 27
    assert classifier.hidden_sizes == [64, 32, 16]


def test_detector_cold_start(detector):
    """Test detector in cold start mode"""
    archetype, confidence = detector.cold_start_mode()

    assert archetype == UserArchetype.LEARNER  # Safe default
    assert confidence == 0.0  # No confidence yet


def test_detector_detection(detector):
    """Test archetype detection"""
    archetype, probabilities, confidence = detector.detect_archetype("test_user")

    # Should return an archetype
    assert isinstance(archetype, UserArchetype)

    # Should return probabilities for all 4 archetypes
    assert len(probabilities) == 4
    assert all(0 <= p <= 1 for p in probabilities.values())

    # Confidence should be between 0 and 1
    assert 0 <= confidence <= 1


def test_detector_archetype_blend(detector):
    """Test archetype blending (users are mixtures)"""
    blend = detector.get_archetype_blend("test_user")

    # Should have all 4 archetypes
    assert len(blend) == 4

    # Should sum to ~1.0 (probabilities)
    total = sum(blend.values())
    assert 0.95 <= total <= 1.05  # Allow small floating point error


def test_detector_explanation(detector):
    """Test explainable AI"""
    explanation = detector.explain_classification("test_user")

    # Should have required fields
    assert "archetype" in explanation
    assert "confidence" in explanation
    assert "probabilities" in explanation
    assert "key_indicators" in explanation
    assert "data_quality" in explanation


# === Continuous Learning Tests ===

def test_learner_add_observation(learner, detector):
    """Test adding observation to learner"""
    features = BehavioralFeatures()

    learner.add_observation(
        features=features,
        true_archetype=UserArchetype.LEARNER,
        confidence=1.0,
        user_id="test_user",
        source="confirmed"
    )

    assert len(learner.training_examples) == 1
    assert learner.examples_since_retrain == 1


def test_learner_should_retrain(learner, detector):
    """Test retrain threshold"""
    features = BehavioralFeatures()

    # Add examples below threshold
    for i in range(learner.retrain_threshold - 1):
        learner.add_observation(
            features=features,
            true_archetype=UserArchetype.LEARNER,
            confidence=1.0,
            source="confirmed"
        )

    assert not learner.should_retrain()

    # Add one more to reach threshold
    learner.add_observation(
        features=features,
        true_archetype=UserArchetype.LEARNER,
        confidence=1.0,
        source="confirmed"
    )

    assert learner.should_retrain()


def test_learner_learning_status(learner, detector):
    """Test getting learning status"""
    status = learner.get_learning_status()

    assert "total_examples" in status
    assert "real_examples" in status
    assert "synthetic_examples" in status
    assert "data_quality" in status
    assert "model_maturity" in status


def test_learner_model_maturity(learner, detector):
    """Test model maturity calculation"""
    # Bootstrap phase
    status = learner.get_learning_status()
    assert status["model_maturity"] == "bootstrap"

    # Add real examples
    features = BehavioralFeatures()
    for i in range(50):
        learner.add_observation(
            features=features,
            true_archetype=UserArchetype.LEARNER,
            confidence=1.0,
            source="confirmed"
        )

    status = learner.get_learning_status()
    # Should move to "learning" with real data
    assert status["model_maturity"] in ["learning", "mature"]


# === Archetype Evolution Tests ===

def test_evolution_cold_start_status(evolution_tracker):
    """Test cold-start status detection"""
    status = evolution_tracker.get_cold_start_status()

    assert status["phase"] == "cold_start"
    assert status["interactions"] == 0
    assert status["confidence"] == 0.0


def test_evolution_record_snapshot(evolution_tracker):
    """Test recording evolution snapshot"""
    evolution_tracker.record_snapshot(
        archetype=UserArchetype.LEARNER,
        confidence=0.7,
        probabilities={
            "learner": 0.7,
            "pragmatist": 0.1,
            "explorer": 0.1,
            "creator": 0.1
        },
        technical_level=TechnicalLevel.BEGINNER,
        data_quality=0.2
    )

    assert len(evolution_tracker.snapshots) == 1


def test_evolution_phase_transitions(evolution_tracker):
    """Test cold_start → warming_up → warm → established"""
    # Cold start (0 interactions)
    status = evolution_tracker.get_cold_start_status()
    assert status["phase"] == "cold_start"

    # Add 10 snapshots → warming up
    for i in range(10):
        evolution_tracker.record_snapshot(
            archetype=UserArchetype.LEARNER,
            confidence=0.5,
            probabilities={"learner": 0.5, "pragmatist": 0.3, "explorer": 0.1, "creator": 0.1},
            technical_level=TechnicalLevel.BEGINNER,
            data_quality=0.2 + i * 0.05
        )

    status = evolution_tracker.get_cold_start_status()
    assert status["phase"] == "warming_up"

    # Add more for warm phase
    for i in range(40):
        evolution_tracker.record_snapshot(
            archetype=UserArchetype.LEARNER,
            confidence=0.7,
            probabilities={"learner": 0.7, "pragmatist": 0.15, "explorer": 0.1, "creator": 0.05},
            technical_level=TechnicalLevel.INTERMEDIATE,
            data_quality=0.5
        )

    status = evolution_tracker.get_cold_start_status()
    assert status["phase"] == "warm"


def test_evolution_archetype_shift_detection(evolution_tracker):
    """Test detecting archetype shifts"""
    # Record stable Learner period
    for i in range(10):
        evolution_tracker.record_snapshot(
            archetype=UserArchetype.LEARNER,
            confidence=0.8,
            probabilities={"learner": 0.8, "pragmatist": 0.1, "explorer": 0.05, "creator": 0.05},
            technical_level=TechnicalLevel.BEGINNER,
            data_quality=0.5
        )

    # Shift to Explorer
    for i in range(5):
        evolution_tracker.record_snapshot(
            archetype=UserArchetype.EXPLORER,
            confidence=0.7,
            probabilities={"learner": 0.1, "pragmatist": 0.1, "explorer": 0.7, "creator": 0.1},
            technical_level=TechnicalLevel.INTERMEDIATE,
            data_quality=0.6
        )

    shift = evolution_tracker.detect_archetype_shift()

    # Should detect shift
    assert shift is not None
    assert shift["from_archetype"] == "learner"
    assert shift["to_archetype"] == "explorer"


# === Integration Layer Tests ===

def test_integration_record_interaction(integration_layer):
    """Test recording interaction in integration layer"""
    integration_layer.record_interaction(
        query="how does nix work?",
        response="Nix is a package manager...",
        reading_time_ms=3000,
        user_action="asked_clarification"
    )

    assert len(integration_layer.session_signals) == 1


def test_integration_get_prediction(integration_layer):
    """Test getting prediction from integration layer"""
    prediction = integration_layer.get_current_prediction()

    assert "archetype" in prediction
    assert "probabilities" in prediction
    assert "confidence" in prediction
    assert "explanation" in prediction
    assert "cold_start" in prediction
    assert "learning" in prediction


def test_integration_confirm_archetype(integration_layer):
    """Test confirming archetype triggers learning"""
    # Record some interactions first
    for i in range(5):
        integration_layer.record_interaction(
            query=f"why does {i} work?",
            response="Because...",
            user_action="executed"
        )

    # Confirm archetype
    integration_layer.confirm_archetype(
        true_archetype=UserArchetype.LEARNER,
        confidence=1.0,
        source="user_confirmed"
    )

    # Should add to training data
    assert len(integration_layer.learner.training_examples) > 0


def test_integration_learning_dashboard(integration_layer):
    """Test getting complete learning dashboard"""
    # Record interactions
    for i in range(10):
        integration_layer.record_interaction(
            query=f"query {i}",
            response=f"response {i}",
            user_action="executed"
        )

    dashboard = integration_layer.get_learning_dashboard()

    assert "prediction" in dashboard
    assert "evolution_history" in dashboard
    assert "session_stats" in dashboard
    assert dashboard["session_stats"]["interactions_this_session"] == 10


# === End-to-End Integration Test ===

def test_full_behavioral_detection_flow(temp_data_dir):
    """Test complete flow: signal → features → prediction → learning → evolution"""
    # Setup
    detector = BehavioralArchetypeDetector()
    learner = ContinuousLearner(detector, data_dir=temp_data_dir)
    evolution = ArchetypeEvolutionTracker(user_id="flow_test", data_dir=temp_data_dir)
    integration = BehavioralIntegrationLayer(user_id="flow_test")

    # 1. Simulate Learner behavior
    for i in range(20):
        integration.record_interaction(
            query=f"why does concept {i} work this way?",
            response="Detailed explanation...",
            reading_time_ms=5000,
            user_action="executed"
        )

    # 2. Get prediction (should trend toward Learner)
    prediction = integration.get_current_prediction()
    archetype = prediction["archetype"]

    # 3. User confirms archetype
    integration.confirm_archetype(
        true_archetype=UserArchetype.LEARNER,
        confidence=1.0,
        source="user_confirmed"
    )

    # 4. Check learning occurred
    learning_status = learner.get_learning_status()
    assert learning_status["real_examples"] > 0

    # 5. Check evolution tracked
    cold_start = evolution.get_cold_start_status()
    assert cold_start["interactions"] > 0

    # Success! Full flow works
    assert True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
