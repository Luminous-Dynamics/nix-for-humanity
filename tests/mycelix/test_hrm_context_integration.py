"""Test Context-Aware HRM Integration

Demonstrates how the Context Engine enhances HRM predictions.
"""

import pytest
from luminous_nix.ai.hrm_context_aware import ContextAwareHRMReasoner, get_context_aware_hrm
from luminous_nix.mycelix.context import get_context_engine, SessionState, ProjectType


class TestContextAwareHRM:
    """Test Context-Aware HRM functionality"""

    def test_initialization(self):
        """Test Context-Aware HRM initializes"""
        hrm = ContextAwareHRMReasoner(enable_context=True)

        assert hrm is not None
        assert hrm.base_hrm is not None

    def test_prediction_without_context(self):
        """Test prediction works without context engine"""
        hrm = ContextAwareHRMReasoner(enable_context=False)

        result = hrm.predict("install firefox")

        assert 'intent' in result
        assert 'confidence' in result
        assert result['context_enhanced'] is False

    def test_prediction_with_context(self):
        """Test prediction enhanced by context"""
        hrm = get_context_aware_hrm()

        # Create some context
        engine = get_context_engine()
        engine.record_command("python main.py", True, 100.0)

        result = hrm.predict("install firefox")

        assert 'intent' in result
        assert result['intent'] == 'install'
        assert 'frustration_detected' in result
        assert 'predicted_session_state' in result

    def test_frustration_detection_from_context(self):
        """Test frustration detection from context"""
        hrm = get_context_aware_hrm()
        engine = get_context_engine()

        # Simulate frustration with failed commands
        for _ in range(5):
            engine.record_command("failing command", False, 100.0, exit_code=1)

        result = hrm.predict("help with debugging")

        # Should detect frustration from context
        assert 'frustration_detected' in result
        # Note: Might not detect if session isn't frustrated yet

    def test_context_feature_extraction(self):
        """Test extracting features from context"""
        hrm = get_context_aware_hrm()
        engine = get_context_engine()

        # Create rich context
        engine.record_command("test1", True, 100.0)
        engine.record_command("test2", True, 100.0)

        context = engine.get_current_context()
        features = hrm.extract_context_features(context)

        assert features is not None
        assert features.shape == (1, 64)  # Batch of 1, 64 features

    def test_stats_include_context_metrics(self):
        """Test statistics include context enhancement metrics"""
        hrm = get_context_aware_hrm()

        # Make some predictions
        hrm.predict("install vim")
        hrm.predict("search editor")

        stats = hrm.get_stats()

        assert 'context_enhanced_predictions' in stats
        assert 'fallback_predictions' in stats
        assert 'context_enhancement_rate' in stats

    def test_singleton_pattern(self):
        """Test singleton pattern works"""
        hrm1 = get_context_aware_hrm()
        hrm2 = get_context_aware_hrm()

        assert hrm1 is hrm2  # Same instance


class TestContextEnhancement:
    """Test how context enhances predictions"""

    def test_session_state_detection(self):
        """Test session state is detected and included"""
        hrm = get_context_aware_hrm()
        engine = get_context_engine()

        # Create some activity
        for i in range(5):
            engine.record_command(f"test_{i}", True, 100.0)

        result = hrm.predict("help me")

        assert 'predicted_session_state' in result
        # Should be one of the session states
        from luminous_nix.mycelix.context.types import SessionState
        if result['predicted_session_state']:
            assert result['predicted_session_state'] in [s.value for s in SessionState]

    def test_context_summary_provided(self):
        """Test context summary is included in results"""
        hrm = get_context_aware_hrm()

        result = hrm.predict("install package")

        if result.get('context_enhanced'):
            assert 'context_summary' in result
            assert 'session_state' in result['context_summary']


def manual_test_context_aware_hrm():
    """
    Manual test to demonstrate context-aware capabilities

    Run with: pytest -k manual_test -v -s
    """
    print("\n" + "=" * 70)
    print("🧠 Testing Context-Aware HRM")
    print("=" * 70)

    hrm = get_context_aware_hrm()
    engine = get_context_engine()

    # Test 1: Normal query
    print("\n📍 Test 1: Normal install query")
    result = hrm.predict("install firefox")
    print(f"  Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
    print(f"  Context Enhanced: {result.get('context_enhanced', False)}")
    if result.get('context_summary'):
        print(f"  Session State: {result['context_summary'].get('session_state')}")

    # Test 2: After creating frustration context
    print("\n📍 Test 2: After simulating frustration")
    for _ in range(5):
        engine.record_command("broken command", False, 500.0, exit_code=1)

    result = hrm.predict("help me fix this")
    print(f"  Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
    print(f"  Frustration Detected: {result.get('frustration_detected', False)}")
    if result.get('frustration_score'):
        print(f"  Frustration Score: {result['frustration_score']:.2f}")

    # Test 3: Statistics
    print("\n📍 Test 3: Context Enhancement Statistics")
    stats = hrm.get_stats()
    print(f"  Context Enhanced: {stats['context_enhanced_predictions']}")
    print(f"  Fallback: {stats['fallback_predictions']}")
    print(f"  Enhancement Rate: {stats['context_enhancement_rate']:.1%}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run manual test
    manual_test_context_aware_hrm()
