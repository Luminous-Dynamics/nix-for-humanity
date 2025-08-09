#!/usr/bin/env python3
"""
Simple integration tests without pytest dependency
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.core.intents import IntentRecognizer, IntentType
from nix_humanity.core.executor import SafeExecutor
from nix_humanity.core.knowledge import KnowledgeBase
from nix_humanity.api.schema import Request, Response, Result


class SimpleIntegrationTests:
    """Simple integration tests without pytest"""
    
    def __init__(self):
        self.backend = NixForHumanityBackend()
        self.recognizer = IntentRecognizer()
        self.executor = SafeExecutor()
        self.executor.dry_run = True  # Set dry_run after initialization
        self.knowledge = KnowledgeBase()
        self.passed = 0
        self.failed = 0
    
    def assert_equal(self, actual, expected, message=""):
        """Simple assertion helper"""
        if actual != expected:
            raise AssertionError(f"{message}: Expected {expected}, got {actual}")
    
    def assert_true(self, condition, message=""):
        """Simple assertion helper"""
        if not condition:
            raise AssertionError(f"{message}: Condition was false")
    
    def assert_in(self, item, container, message=""):
        """Simple assertion helper"""
        if item not in container:
            raise AssertionError(f"{message}: {item} not found in {container}")
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        try:
            test_func()
            print(f"✅ {test_name}")
            self.passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: {e}")
            self.failed += 1
        except Exception as e:
            print(f"💥 {test_name}: {type(e).__name__}: {e}")
            self.failed += 1
    
    def test_intent_recognition_packages(self):
        """Test package command recognition"""
        test_cases = [
            ("install firefox", IntentType.INSTALL_PACKAGE),
            ("remove vim", IntentType.REMOVE_PACKAGE),
            ("search text editor", IntentType.SEARCH_PACKAGE),
            ("update my system", IntentType.UPDATE_SYSTEM),
            ("list installed packages", IntentType.LIST_INSTALLED),
        ]
        
        for query, expected_type in test_cases:
            intent = self.recognizer.recognize(query)
            self.assert_equal(intent.type, expected_type, f"Query: {query}")
    
    def test_intent_recognition_services(self):
        """Test service command recognition"""
        test_cases = [
            ("start nginx", IntentType.START_SERVICE),
            ("stop docker", IntentType.STOP_SERVICE),
            ("restart ssh", IntentType.RESTART_SERVICE),
            ("is nginx running", IntentType.SERVICE_STATUS),
            ("list services", IntentType.LIST_SERVICES),
        ]
        
        for query, expected_type in test_cases:
            intent = self.recognizer.recognize(query)
            self.assert_equal(intent.type, expected_type, f"Query: {query}")
    
    def test_intent_recognition_users(self):
        """Test user command recognition"""
        test_cases = [
            ("create user alice", IntentType.CREATE_USER),
            ("list users", IntentType.LIST_USERS),
            ("add alice to docker group", IntentType.ADD_USER_TO_GROUP),
            ("change password bob", IntentType.CHANGE_PASSWORD),
            ("grant alice sudo", IntentType.GRANT_SUDO),
        ]
        
        for query, expected_type in test_cases:
            intent = self.recognizer.recognize(query)
            self.assert_equal(intent.type, expected_type, f"Query: {query}")
    
    def test_knowledge_base_solutions(self):
        """Test knowledge base has solutions"""
        intent_types = [
            'install_package', 'remove_package', 'update_system',
            'start_service', 'create_user', 'disk_usage'
        ]
        
        for intent_type in intent_types:
            solution = self.knowledge.get_solution(intent_type)
            self.assert_true(solution is not None, f"No solution for {intent_type}")
            self.assert_true('solution' in solution, f"Missing solution text for {intent_type}")
    
    def test_backend_help_request(self):
        """Test backend processes help request"""
        request = Request(query="help", context={'personality': 'friendly', 'execute': False})
        response = self.backend.process(request)
        
        self.assert_true(response.success, "Help request failed")
        self.assert_true(len(response.text) > 100, "Help text too short")
        self.assert_in("Package Management", response.text, "Missing package section")
        self.assert_in("System Maintenance", response.text, "Missing system section")
    
    def test_backend_install_request(self):
        """Test backend processes install request"""
        request = Request(query="install firefox", context={'personality': 'minimal', 'execute': False})
        response = self.backend.process(request)
        
        self.assert_true(response.success, "Install request failed")
        self.assert_in("firefox", response.text.lower(), "Missing package name")
    
    def test_backend_service_request(self):
        """Test backend processes service request"""
        request = Request(query="start nginx", context={'personality': 'friendly', 'execute': False})
        response = self.backend.process(request)
        
        self.assert_true(response.success, "Service request failed")
        self.assert_in("nginx", response.text.lower(), "Missing service name")
        self.assert_in("systemctl", response.text.lower(), "Missing systemctl command")
    
    def test_backend_unknown_command(self):
        """Test backend handles unknown commands"""
        request = Request(
            query="do something completely random",
            context={'personality': 'friendly', 'execute': False}
        )
        response = self.backend.process(request)
        
        self.assert_true(response.success, "Should still return response")
        self.assert_true(
            "not sure" in response.text.lower() or "help" in response.text.lower(),
            "Should indicate uncertainty"
        )
    
    async def test_executor_dry_run(self):
        """Test executor in dry-run mode"""
        # Test package installation
        result = await self.executor._execute_install_package("test-package")
        self.assert_true(result.success, "Dry-run install failed")
        self.assert_in("Would install", result.output, "Missing dry-run indicator")
        
        # Test service start
        result = await self.executor._execute_start_service("nginx")
        self.assert_true(result.success, "Dry-run service start failed")
        self.assert_in("Would start", result.output, "Missing dry-run indicator")
    
    def run_all_tests(self):
        """Run all tests and report results"""
        print("🧪 Running Simple Integration Tests")
        print("=" * 60)
        
        # Synchronous tests
        print("\n📦 Intent Recognition Tests")
        print("-" * 40)
        self.run_test("Package Commands", self.test_intent_recognition_packages)
        self.run_test("Service Commands", self.test_intent_recognition_services)
        self.run_test("User Commands", self.test_intent_recognition_users)
        
        print("\n📚 Knowledge Base Tests")
        print("-" * 40)
        self.run_test("Solution Coverage", self.test_knowledge_base_solutions)
        
        print("\n🎯 Backend Integration Tests")
        print("-" * 40)
        self.run_test("Help Request", self.test_backend_help_request)
        self.run_test("Install Request", self.test_backend_install_request)
        self.run_test("Service Request", self.test_backend_service_request)
        self.run_test("Unknown Command", self.test_backend_unknown_command)
        
        # Async tests
        print("\n🏃 Executor Tests")
        print("-" * 40)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.run_test("Dry Run Safety", lambda: loop.run_until_complete(self.test_executor_dry_run()))
        loop.close()
        
        # Summary
        print("\n" + "=" * 60)
        total = self.passed + self.failed
        print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
        if total > 0:
            print(f"🎯 Success Rate: {self.passed/total*100:.1f}%")
        
        return self.failed == 0


if __name__ == "__main__":
    tests = SimpleIntegrationTests()
    success = tests.run_all_tests()
    sys.exit(0 if success else 1)