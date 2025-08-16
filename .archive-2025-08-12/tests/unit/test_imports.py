#!/usr/bin/env python3
"""
Quick import test to verify major import path fixes
"""

def test_bkt_imports():
    """Test Bayesian Knowledge Tracer imports"""
    try:
        from luminous_nix.research.dynamic_user_modeling import (
            BayesianKnowledgeTracer,
            BKTParameters,
            NixOSSkillGraph,
            SkillObservation,
        )

        print("✅ BKT imports: SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ BKT imports: FAILED - {e}")
        return False

def test_cli_adapter_imports():
    """Test CLI adapter imports"""
    try:
        from frontends.cli.adapter import CLIAdapter

        print("✅ CLI adapter imports: SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ CLI adapter imports: FAILED - {e}")
        return False

def test_consciousness_backend_imports():
    """Test consciousness test backend imports"""
    try:
        from tests.fixtures.sacred_test_base import (
            ConsciousnessTestBackend,
            SacredTestBase,
        )

        print("✅ Test backend imports: SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ Test backend imports: FAILED - {e}")
        return False

def test_core_interface_imports():
    """Test core interface imports"""
    try:
        from luminous_nix.core.interface import Intent, IntentType, Response

        print("✅ Core interface imports: SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ Core interface imports: FAILED - {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing import path fixes...\n")

    tests = [
        test_bkt_imports,
        test_cli_adapter_imports,
        test_consciousness_backend_imports,
        test_core_interface_imports,
    ]

    results = []
    for test in tests:
        results.append(test())
        print()

    passed = sum(results)
    total = len(results)

    print(f"📊 Import Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All import path fixes successful!")
        exit(0)
    else:
        print("⚠️  Some import issues remain")
        exit(1)
