#!/usr/bin/env python3
"""
Real integration tests for Nix for Humanity commands
These tests verify actual command execution paths without mocks
"""

import pytest
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


class TestRealIntegration:
    """Real integration tests without mocks"""
    
    @pytest.fixture
    def backend(self):
        """Create a real backend instance"""
        return NixForHumanityBackend()
    
    @pytest.fixture
    def recognizer(self):
        """Create a real intent recognizer"""
        return IntentRecognizer()
    
    @pytest.fixture
    def executor(self):
        """Create a real executor (dry-run mode for safety)"""
        executor = SafeExecutor()
        executor.dry_run = True  # Set dry_run after initialization
        return executor
    
    @pytest.fixture
    def knowledge(self):
        """Create a real knowledge base"""
        return KnowledgeBase()
    
    # Intent Recognition Tests
    
    def test_intent_recognition_package_commands(self, recognizer):
        """Test real intent recognition for package commands"""
        test_cases = [
            ("install firefox", IntentType.INSTALL_PACKAGE, {"package": "firefox"}),
            ("remove vim", IntentType.REMOVE_PACKAGE, {"package": "vim"}),
            ("search text editor", IntentType.SEARCH_PACKAGE, {"query": "text editor"}),
            ("update my system", IntentType.UPDATE_SYSTEM, {}),
            ("list installed packages", IntentType.LIST_INSTALLED, {}),
        ]
        
        for query, expected_type, expected_entities in test_cases:
            intent = recognizer.recognize(query)
            assert intent.type == expected_type, f"Failed for query: {query}"
            for key, value in expected_entities.items():
                assert intent.entities.get(key) == value, f"Entity mismatch for {key} in query: {query}"
    
    def test_intent_recognition_system_commands(self, recognizer):
        """Test real intent recognition for system commands"""
        test_cases = [
            ("garbage collect", IntentType.GARBAGE_COLLECT, {}),
            ("list generations", IntentType.LIST_GENERATIONS, {}),
            ("rollback", IntentType.ROLLBACK, {}),
            ("switch to generation 42", IntentType.SWITCH_GENERATION, {"generation": 42}),
            ("rebuild", IntentType.REBUILD, {"rebuild_type": "switch"}),
        ]
        
        for query, expected_type, expected_entities in test_cases:
            intent = recognizer.recognize(query)
            assert intent.type == expected_type, f"Failed for query: {query}"
            for key, value in expected_entities.items():
                assert intent.entities.get(key) == value, f"Entity mismatch for {key} in query: {query}"
    
    def test_intent_recognition_service_commands(self, recognizer):
        """Test real intent recognition for service commands"""
        test_cases = [
            ("start nginx", IntentType.START_SERVICE, {"service": "nginx"}),
            ("stop docker", IntentType.STOP_SERVICE, {"service": "docker"}),
            ("restart ssh", IntentType.RESTART_SERVICE, {"service": "ssh"}),
            ("is nginx running", IntentType.SERVICE_STATUS, {"service": "nginx"}),
            ("list services", IntentType.LIST_SERVICES, {}),
        ]
        
        for query, expected_type, expected_entities in test_cases:
            intent = recognizer.recognize(query)
            assert intent.type == expected_type, f"Failed for query: {query}"
            for key, value in expected_entities.items():
                assert intent.entities.get(key) == value, f"Entity mismatch for {key} in query: {query}"
    
    def test_intent_recognition_user_commands(self, recognizer):
        """Test real intent recognition for user commands"""
        test_cases = [
            ("create user alice", IntentType.CREATE_USER, {"username": "alice"}),
            ("list users", IntentType.LIST_USERS, {}),
            ("add alice to docker group", IntentType.ADD_USER_TO_GROUP, {"username": "alice", "group": "docker"}),
            ("change password bob", IntentType.CHANGE_PASSWORD, {"username": "bob"}),
            ("grant alice sudo", IntentType.GRANT_SUDO, {"username": "alice"}),
        ]
        
        for query, expected_type, expected_entities in test_cases:
            intent = recognizer.recognize(query)
            assert intent.type == expected_type, f"Failed for query: {query}"
            for key, value in expected_entities.items():
                assert intent.entities.get(key) == value, f"Entity mismatch for {key} in query: {query}"
    
    # Knowledge Base Tests
    
    def test_knowledge_base_has_solutions(self, knowledge):
        """Test that knowledge base has solutions for all intent types"""
        intent_types_to_test = [
            'install_package', 'remove_package', 'update_system',
            'list_generations', 'garbage_collect', 'start_service',
            'create_user', 'disk_usage', 'show_network'
        ]
        
        for intent_type in intent_types_to_test:
            solution = knowledge.get_solution(intent_type)
            assert solution is not None, f"No solution found for {intent_type}"
            assert 'solution' in solution, f"Solution missing for {intent_type}"
            assert 'example' in solution, f"Example missing for {intent_type}"
    
    def test_knowledge_base_help_response(self, knowledge):
        """Test that help response is comprehensive"""
        help_response = knowledge._get_help_response()
        assert help_response is not None
        assert 'response' in help_response
        
        # Check that help text includes key sections
        help_text = help_response['response']
        assert "Package Management" in help_text
        assert "System Maintenance" in help_text
        assert "Service Management" in help_text
        assert "User Management" in help_text
        assert "Storage Management" in help_text
    
    # Executor Tests (Dry Run)
    
    @pytest.mark.asyncio
    async def test_executor_dry_run_safety(self, executor):
        """Test that executor respects dry-run mode"""
        # Test package installation (should not actually install)
        result = await executor._execute_install_package("test-package")
        assert result.success
        assert "Would install" in result.output
        
        # Test service start (should not actually start)
        result = await executor._execute_start_service("nginx")
        assert result.success
        assert "Would start" in result.output
        
        # Test user creation (should not actually create)
        result = await executor._execute_create_user("testuser")
        assert result.success
        assert "Would create" in result.output
    
    @pytest.mark.asyncio
    async def test_executor_input_validation(self, executor):
        """Test that executor validates inputs properly"""
        # Test missing package name
        result = await executor._execute_install_package(None)
        assert not result.success
        assert "package name" in result.error.lower()
        
        # Test missing service name
        result = await executor._execute_start_service(None)
        assert not result.success
        assert "service name" in result.error.lower()
        
        # Test missing username
        result = await executor._execute_create_user(None)
        assert not result.success
        assert "username" in result.error.lower()
    
    # Full Backend Integration Tests
    
    def test_backend_processes_help_request(self, backend):
        """Test full backend processing of help request"""
        request = Request(query="help", context={'personality': 'friendly', 'execute': False})
        response = backend.process(request)
        
        assert response.success
        assert len(response.text) > 100  # Should have substantial help text
        assert "Package Management" in response.text
        assert "System Maintenance" in response.text
    
    def test_backend_processes_install_request(self, backend):
        """Test full backend processing of install request"""
        request = Request(query="install firefox", context={'personality': 'minimal', 'execute': False})
        response = backend.process(request)
        
        assert response.success
        assert "firefox" in response.text.lower()
        assert any(cmd.get('command', '').startswith('nix profile install') for cmd in response.commands)
    
    def test_backend_processes_service_request(self, backend):
        """Test full backend processing of service request"""
        request = Request(query="start nginx", context={'personality': 'friendly', 'execute': False})
        response = backend.process(request)
        
        assert response.success
        assert "nginx" in response.text.lower()
        assert "systemctl" in response.text.lower()
    
    def test_backend_personality_adaptation(self, backend):
        """Test that backend adapts to different personalities"""
        personalities = ['minimal', 'friendly', 'encouraging', 'technical', 'symbiotic']
        
        for personality in personalities:
            request = Request(
                query="install vim",
                context={'personality': personality, 'execute': False}
            )
            response = backend.process(request)
            
            assert response.success
            # Each personality should produce different response styles
            if personality == 'minimal':
                assert len(response.text) < 500  # Should be concise
            elif personality == 'friendly':
                assert "😊" in response.text or "Hi there!" in response.text
            elif personality == 'encouraging':
                assert "awesome" in response.text.lower() or "great" in response.text.lower()
    
    def test_backend_unknown_command_handling(self, backend):
        """Test that backend handles unknown commands gracefully"""
        request = Request(
            query="do something completely random that doesn't exist",
            context={'personality': 'friendly', 'execute': False}
        )
        response = backend.process(request)
        
        assert response.success  # Should still return a response
        assert "not sure" in response.text.lower() or "help" in response.text.lower()
    
    # Enhanced Response System Tests
    
    def test_backend_enhanced_responses(self, backend):
        """Test that enhanced response system works when enabled"""
        os.environ['NIX_HUMANITY_ENHANCED_RESPONSES'] = 'true'
        
        request = Request(
            query="install docker",
            context={'personality': 'friendly', 'execute': False}
        )
        response = backend.process(request)
        
        assert response.success
        # Check for two-path response indicators
        if hasattr(response, 'data') and response.data and 'paths' in response.data:
            paths = response.data['paths']
            assert len(paths) >= 2  # Should have multiple solution paths
            assert any('imperative' in str(path).lower() for path in paths)
            assert any('declarative' in str(path).lower() for path in paths)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])