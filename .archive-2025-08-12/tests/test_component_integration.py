#!/usr/bin/env python3
"""
Simple component-level test for research integration
"""

import os
import sys
from pathlib import Path

# Add the backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Enable mock components
os.environ["LUMINOUS_NIX_SKG_PATH"] = "./test_skg.db"

def test_backend_initialization():
    """Test if backend initializes with research components"""
    print("🧪 Testing Backend Initialization")
    print("=" * 50)

    try:
        from luminous_nix.core.engine import NixForHumanityBackend

        # Create backend
        print("Creating backend...")
        backend = NixForHumanityBackend()

        # Check components
        print(f"\n✓ Backend created successfully")
        print(f"✓ SKG Available: {backend.skg is not None}")
        print(f"✓ Trust Engine: {backend.trust_engine is not None}")
        print(f"✓ Metrics Collector: {backend.metrics_collector is not None}")
        print(f"✓ Consciousness Guard: {backend.consciousness_guard is not None}")

        # Test basic operations if components are available
        if backend.skg:
            print("\n📊 Testing SKG operations...")
            # Mock SKG should handle basic operations
            backend.skg.ontological.add_concept("test", "concept", {})
            print("✓ SKG concept addition works")

        if backend.trust_engine:
            print("\n🤝 Testing Trust Engine...")
            trust_result = backend.trust_engine.process_interaction(
                "test_id", "install firefox", "I'll help you install firefox"
            )
            print(f"✓ Trust level: {trust_result.get('trust_level', 'N/A')}")

        if backend.metrics_collector:
            print("\n📈 Testing Metrics Collector...")
            metrics = backend.metrics_collector.collect_current_metrics(
                {
                    "session_start": 0,
                    "interruptions": 0,
                    "breaks_taken": 0,
                    "focus_duration": 0,
                }
            )
            print(f"✓ Wellbeing score: {metrics.wellbeing_score}")

        print("\n✅ All component tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

def test_mock_components_directly():
    """Test mock components work correctly"""
    print("\n\n🔧 Testing Mock Components Directly")
    print("=" * 50)

    try:
        from unittest.mock import Mock, MagicMock, patch, call
        # MockSymbioticKnowledgeGraph,
        # MockTrustEngine,
        # MockSacredMetricsCollector,
        # MockConsciousnessGuard

        # Test SKG
        print("\n1️⃣ Testing Mock SKG...")
        skg = MockSymbioticKnowledgeGraph()
        skg.update_from_interaction({"type": "test"})
        print("✓ Mock SKG works")

        # Test Trust Engine
        print("\n2️⃣ Testing Mock Trust Engine...")
        trust = MockTrustEngine(skg)
        result = trust.process_interaction("id1", "help", "sure!")
        print(f"✓ Trust state: {result['trust_state'].value}")

        # Test Metrics
        print("\n3️⃣ Testing Mock Metrics...")
        metrics = MockSacredMetricsCollector(skg)
        m = metrics.collect_current_metrics({})
        print(f"✓ Wellbeing: {m.wellbeing_score}")

        # Test Consciousness Guard
        print("\n4️⃣ Testing Mock Consciousness Guard...")
        guard = MockConsciousnessGuard()
        with guard.sacred_context("test"):
            print("✓ Sacred context works")

        print("\n✅ All mock components work correctly!")
        return True

    except Exception as e:
        print(f"\n❌ Mock test failed: {e}")

        traceback.print_exc()
        return False

def test_request_processing():
    """Test basic request processing"""
    print("\n\n🌐 Testing Request Processing")
    print("=" * 50)

    try:
        from luminous_nix.api.schema import Request

        backend = NixForHumanityBackend()

        # Create simple request with dict context
        request = Request(
            query="install firefox",
            context={"personality": "friendly", "execute": False},
        )

        print("Processing request...")
        response = backend.process(request)

        print(f"\n✓ Response success: {response.success}")
        print(f"✓ Response text: {response.text[:100]}...")

        if hasattr(response, "data") and response.data:
            print(f"✓ Intent detected: {response.data.get('intent', 'unknown')}")

        print("\n✅ Request processing works!")
        return True

    except Exception as e:
        print(f"\n❌ Request processing failed: {e}")

        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Component Integration Test Suite")
    print("=" * 60)

    # Run tests
    test1 = test_backend_initialization()
    test2 = test_mock_components_directly()
    test3 = test_request_processing()

    # Summary
    print("\n\n📊 Test Summary")
    print("=" * 50)
    print(f"Backend Init: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Mock Components: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print(f"Request Processing: {'✅ PASSED' if test3 else '❌ FAILED'}")

    # Cleanup
    test_db = Path("./test_skg.db")
    if test_db.exists():
        test_db.unlink()
        print(f"\n🧹 Cleaned up test database")

    all_passed = test1 and test2 and test3
    print(f"\n{'✅ All tests passed!' if all_passed else '❌ Some tests failed'}")
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
