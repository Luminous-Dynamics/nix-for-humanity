#!/usr/bin/env python3
"""
Run integration tests without pytest
"""

import sys
import traceback
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tests.integration.test_real_commands import TestRealIntegration

def run_test(test_method, *args):
    """Run a single test and report results"""
    try:
        test_method(*args)
        print(f"✅ {test_method.__name__}")
        return True
    except AssertionError as e:
        print(f"❌ {test_method.__name__}: {e}")
        return False
    except Exception as e:
        print(f"💥 {test_method.__name__}: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("🧪 Running Real Integration Tests")
    print("=" * 60)
    
    # Create test instance and fixtures
    test_suite = TestRealIntegration()
    
    # Create fixtures
    backend = test_suite.backend()
    recognizer = test_suite.recognizer()
    executor = test_suite.executor()
    knowledge = test_suite.knowledge()
    
    # Set executor to dry_run mode
    executor.dry_run = True
    
    # Track results
    passed = 0
    failed = 0
    
    print("\n📦 Intent Recognition Tests - Packages")
    print("-" * 40)
    if run_test(test_suite.test_intent_recognition_package_commands, recognizer):
        passed += 1
    else:
        failed += 1
    
    print("\n🔧 Intent Recognition Tests - System")
    print("-" * 40)
    if run_test(test_suite.test_intent_recognition_system_commands, recognizer):
        passed += 1
    else:
        failed += 1
    
    print("\n⚡ Intent Recognition Tests - Services")
    print("-" * 40)
    if run_test(test_suite.test_intent_recognition_service_commands, recognizer):
        passed += 1
    else:
        failed += 1
    
    print("\n👤 Intent Recognition Tests - Users")
    print("-" * 40)
    if run_test(test_suite.test_intent_recognition_user_commands, recognizer):
        passed += 1
    else:
        failed += 1
    
    print("\n📚 Knowledge Base Tests")
    print("-" * 40)
    if run_test(test_suite.test_knowledge_base_has_solutions, knowledge):
        passed += 1
    else:
        failed += 1
    
    if run_test(test_suite.test_knowledge_base_help_response, knowledge):
        passed += 1
    else:
        failed += 1
    
    print("\n🏃 Executor Tests (Dry Run)")
    print("-" * 40)
    # Skip async tests for now as they require asyncio
    print("⏭️  Skipping async executor tests (require asyncio runtime)")
    
    print("\n🎯 Full Backend Integration Tests")
    print("-" * 40)
    if run_test(test_suite.test_backend_processes_help_request, backend):
        passed += 1
    else:
        failed += 1
    
    if run_test(test_suite.test_backend_processes_install_request, backend):
        passed += 1
    else:
        failed += 1
    
    if run_test(test_suite.test_backend_processes_service_request, backend):
        passed += 1
    else:
        failed += 1
    
    if run_test(test_suite.test_backend_personality_adaptation, backend):
        passed += 1
    else:
        failed += 1
    
    if run_test(test_suite.test_backend_unknown_command_handling, backend):
        passed += 1
    else:
        failed += 1
    
    if run_test(test_suite.test_backend_enhanced_responses, backend):
        passed += 1
    else:
        failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print(f"🎯 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)