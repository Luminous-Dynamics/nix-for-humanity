#!/usr/bin/env python3
"""
Comprehensive unit tests for NixForHumanityBackend - Consciousness-First Testing

Testing all aspects of the unified backend that serves all frontend adapters.
Uses deterministic test implementations instead of mocks to verify
real behavior and interactions.
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from luminous_nix.api.schema import Request, Response, Result
from luminous_nix.core.engine import NixForHumanityBackend, create_backend
from luminous_nix.core import Intent, IntentType
from tests.test_utils.mocks import (
    TestDatabase,
    TestExecutionBackend,
    TestKnowledgeBase,
    TestLearningEngine,
    TestNLPEngine,
)

class TestNixForHumanityBackend:
    """Test suite for NixForHumanityBackend - Consciousness-First Testing"""

    @pytest.fixture
    def test_nlp_engine(self):
        """Create test NLP engine with deterministic behavior"""
        return TestNLPEngine()

    @pytest.fixture
    def test_executor(self):
        """Create test execution backend"""
        return TestExecutionBackend()

    @pytest.fixture
    def test_knowledge_base(self):
        """Create test knowledge base"""
        return TestKnowledgeBase()

    @pytest.fixture
    def test_database(self):
        """Create test database"""
        return TestDatabase()

    @pytest.fixture
    def test_learning_engine(self, test_database):
        """Create test learning engine"""
        return TestLearningEngine(test_database)

    @pytest.fixture
    def backend(self, test_nlp_engine, test_executor, test_knowledge_base):
        """Create backend with test dependencies"""
        # Using dependency injection instead of mocking
        backend = NixForHumanityBackend()
        backend.intent_recognizer = test_nlp_engine
        backend.executor = test_executor
        backend.knowledge = test_knowledge_base
        backend._has_python_api = False
        return backend

    @pytest.fixture
    def backend_with_progress(self):
        """Create backend with progress tracking"""
        progress_calls = []

        def progress_callback(message, progress):
            progress_calls.append((message, progress))

        backend = NixForHumanityBackend(progress_callback)
        backend.progress_calls = progress_calls
        return backend

    # Test Initialization

    def test_init_basic(self):
        """Test basic initialization"""
        backend = NixForHumanityBackend()
        assert backend.intent_recognizer is not None
        assert backend.executor is not None
        assert backend.knowledge is not None
        assert backend.progress_callback is None

    def test_init_with_progress_callback(self):
        """Test initialization with progress callback"""
        progress_calls = []

        def test_callback(message, progress):
            progress_calls.append((message, progress))

        backend = NixForHumanityBackend(test_callback)
        assert backend.progress_callback == test_callback

        # Test progress callback works
        backend.progress_callback("Test", 0.5)
        assert progress_calls == [("Test", 0.5)]

    def test_init_nixos_api_detection(self):
        """Test NixOS API detection with deterministic behavior"""
        backend = NixForHumanityBackend()

        # Should have API availability flag
        assert hasattr(backend, "_has_python_api")
        assert isinstance(backend._has_python_api, bool)

        # If API not available, should still work
        if not backend._has_python_api:
            # Should have fallback executor
            assert backend.executor is not None

    # Test Path Finding

    def test_process_request_basic(self, backend):
        """Test basic request processing"""
        # Setup
        request = Request(text="install firefox", context={})
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.95,
            raw_input="install firefox",
        )
        backend.intent_recognizer.recognize = lambda x: intent

        # Execute
        response = backend.process_request(request)

        # Verify
        assert response.success
        assert response.intent == intent
        assert len(response.plan) > 0
        assert "firefox" in response.explanation

    def test_process_request_with_execution(self, backend):
        """Test request processing with execution"""
        # Setup
        request = Request(
            text="update system", context={"execute": True, "dry_run": False}
        )
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.98,
            raw_input="update system",
        )
        backend.intent_recognizer.recognize = lambda x: intent
        backend.executor.execute = lambda *args: Result(
            success=True, output="System updated successfully", error=None
        )

        # Execute
        response = backend.process_request(request)

        # Verify
        assert response.success
        assert response.result is not None
        assert response.result.success
        # mock_executor.execute.assert_called_once()

    def test_process_request_dry_run(self, backend):
        """Test request processing in dry run mode"""
        # Setup
        request = Request(
            text="install vim", context={"execute": True, "dry_run": True}
        )
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "vim"},
            confidence=0.92,
            raw_input="install vim",
        )
        backend.intent_recognizer.recognize = lambda x: intent

        # Execute
        response = backend.process_request(request)

        # Verify
        assert response.success
        assert response.result is None  # No execution, dry run

    def test_process_request_with_progress(self, backend_with_progress):
        """Test request processing with progress callbacks"""
        # Setup
        backend = backend_with_progress
        request = Request(text="search emacs", context={})
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={"query": "emacs"},
            confidence=0.88,
            raw_input="search emacs",
        )
        backend.intent_recognizer.recognize = lambda x: intent

        # Execute
        response = backend.process_request(request)

        # Verify progress calls
        progress_messages = [call[0] for call in backend.progress_calls]
        assert "Analyzing request..." in progress_messages
        assert "Planning actions..." in progress_messages
        assert "Generating response..." in progress_messages
        assert "Complete!" in progress_messages

    def test_process_request_error_handling(self, backend):
        """Test error handling in request processing"""
        # Setup
        request = Request(text="do something", context={})

        def raise_error(x):
            raise Exception("Test error")

        backend.intent_recognizer.recognize = raise_error

        # Execute
        response = backend.process_request(request)

        # Verify
        assert not response.success
        assert response.intent.type == IntentType.UNKNOWN
        assert "Test error" in response.explanation
        assert len(response.suggestions) > 0

    # Test Action Planning

    def test_plan_actions_install_package(self, backend):
        """Test action planning for package installation"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "neovim"},
            confidence=0.95,
            raw_input="install neovim",
        )
        request = Request(text="install neovim", context={})

        plan = backend._plan_actions(intent, request)

        assert len(plan) > 0
        assert any("neovim" in action for action in plan)
        assert any("install_package" in action.lower() for action in plan)

    def test_plan_actions_update_system(self, backend):
        """Test action planning for system update"""
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.97,
            raw_input="update my system",
        )
        request = Request(text="update my system", context={})

        plan = backend._plan_actions(intent, request)

        assert len(plan) > 0
        assert any("update_system" in action.lower() for action in plan)

    def test_plan_actions_with_python_api(self, backend):
        """Test action planning when Python API is available"""
        backend._has_python_api = True
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "git"},
            confidence=0.93,
            raw_input="install git",
        )
        request = Request(text="install git", context={})

        plan = backend._plan_actions(intent, request)

        assert any("Python API" in action for action in plan)

    # Test Explanation Generation

    def test_explain_install_package(self, backend):
        """Test explanation generation for package installation"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.96,
            raw_input="install firefox",
        )
        plan = ["Install firefox", "Verify installation"]

        explanation = backend._explain(intent, plan, None)

        assert "firefox" in explanation
        assert "install" in explanation.lower()

    def test_explain_with_success_result(self, backend):
        """Test explanation with successful result"""
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.94,
            raw_input="update system",
        )
        plan = ["Update system"]
        result = Result(success=True, output="Updated", error=None)

        explanation = backend._explain(intent, plan, result)

        assert "successfully" in explanation.lower()

    def test_explain_with_error_result(self, backend):
        """Test explanation with error result"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "vim"},
            confidence=0.91,
            raw_input="install vim",
        )
        plan = ["Install vim"]
        result = Result(success=False, output="", error="Package not found")

        explanation = backend._explain(intent, plan, result)

        assert "error" in explanation.lower()
        assert "Package not found" in explanation

    # Test Suggestions

    def test_get_suggestions_install_success(self, backend):
        """Test suggestions after successful installation"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "emacs"},
            confidence=0.89,
            raw_input="install emacs",
        )
        result = Result(success=True, output="Installed", error=None)

        suggestions = backend._get_suggestions(intent, result)

        assert len(suggestions) > 0
        assert any("emacs" in s for s in suggestions)
        assert any("configuration.nix" in s for s in suggestions)

    def test_get_suggestions_unknown_intent(self, backend):
        """Test suggestions for unknown intent"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            entities={},
            confidence=0.3,
            raw_input="do the thing",
        )

        suggestions = backend._get_suggestions(intent, None)

        assert len(suggestions) > 0
        assert any("install" in s.lower() for s in suggestions)

    # Test Command Extraction

    def test_extract_commands_install(self, backend):
        """Test command extraction from install plan"""
        plan = [
            "Use nix profile install nixpkgs#firefox",
            "Verify firefox installation",
        ]

        commands = backend._extract_commands(plan)

        assert len(commands) > 0
        assert commands[0]["command"] == "nix profile install nixpkgs#firefox"
        assert commands[0]["description"] == "Install package"

    def test_extract_commands_update(self, backend):
        """Test command extraction from update plan"""
        plan = [
            "Update channels: sudo nix-channel --update",
            "Rebuild system: sudo nixos-rebuild switch",
        ]

        commands = backend._extract_commands(plan)

        assert len(commands) == 2
        assert commands[0]["command"] == "sudo nix-channel --update"
        assert commands[1]["command"] == "sudo nixos-rebuild switch"

    # Test Native API Integration

    def test_should_use_native_api_enabled(self, backend):
        """Test native API detection when enabled"""
        os.environ["LUMINOUS_NIX_PYTHON_BACKEND"] = "true"
        request = Request(text="update system", context={})

        should_use = backend._should_use_native_api(request)

        assert should_use

        # Cleanup
        if "LUMINOUS_NIX_PYTHON_BACKEND" in os.environ:
            del os.environ["LUMINOUS_NIX_PYTHON_BACKEND"]

    def test_should_use_native_api_disabled(self, backend):
        """Test native API detection when disabled"""
        if "LUMINOUS_NIX_PYTHON_BACKEND" in os.environ:
            del os.environ["LUMINOUS_NIX_PYTHON_BACKEND"]
        request = Request(text="update system", context={})

        should_use = backend._should_use_native_api(request)

        assert not should_use

    def test_should_use_native_api_non_nixos_operation(self, backend):
        """Test native API detection for non-NixOS operations"""
        os.environ["LUMINOUS_NIX_PYTHON_BACKEND"] = "true"
        request = Request(text="explain generations", context={})

        should_use = backend._should_use_native_api(request)

        assert (
            should_use  # "explain" is not nixos_operations but might still use native
        )

        # Cleanup
        if "LUMINOUS_NIX_PYTHON_BACKEND" in os.environ:
            del os.environ["LUMINOUS_NIX_PYTHON_BACKEND"]

    def test_process_sync(self, backend):
        """Test synchronous processing"""
        # Setup
        request = Request(query="install firefox", context={"personality": "minimal"})
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.94,
            raw_input="install firefox",
        )
        backend.intent_recognizer.recognize = lambda x: intent
        backend.knowledge.get_solution = lambda *args: {
            "methods": [
                {
                    "name": "Declarative",
                    "description": "Add to configuration.nix",
                    "example": "environment.systemPackages = [ pkgs.firefox ];",
                }
            ],
            "explanation": "Firefox is a web browser",
        }

        # Execute
        response = backend.process(request)

        # Verify
        assert response.success
        assert "firefox" in response.text
        assert len(response.commands) > 0

    def test_process_sync_error(self, backend):
        """Test synchronous processing error handling"""
        # Setup
        request = Request(query="do something", context={})

        def raise_error(x):
            raise Exception("Test error")

        backend.intent_recognizer.recognize = raise_error

        # Execute
        response = backend.process(request)

        # Verify
        assert not response.success
        assert "Test error" in response.text

    # Test Response Building

    def test_build_response_text_minimal_personality(self, backend):
        """Test response building with minimal personality"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "git"},
            confidence=0.90,
            raw_input="install git",
        )
        knowledge = {
            "methods": [
                {
                    "name": "nix-env",
                    "description": "User profile installation",
                    "example": "nix-env -iA nixos.git",
                }
            ],
            "package": "git",
        }

        response_text = backend._build_response_text(intent, knowledge, "minimal")

        assert "git" in response_text
        assert "nix-env" in response_text
        assert "😊" not in response_text  # No emojis in minimal

    def test_build_response_text_friendly_personality(self, backend):
        """Test response building with friendly personality"""
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.93,
            raw_input="update system",
        )
        knowledge = {
            "solution": "Run nixos-rebuild switch to update",
            "example": "sudo nixos-rebuild switch",
            "explanation": "This rebuilds and activates the configuration",
        }

        response_text = backend._build_response_text(intent, knowledge, "friendly")

        assert "Hi there!" in response_text
        assert "😊" in response_text
        assert "clarification" in response_text

    def test_build_response_text_symbiotic_personality(self, backend):
        """Test response building with symbiotic personality"""
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={"query": "editor"},
            confidence=0.87,
            raw_input="search editor",
        )
        knowledge = {"response": "Found several editors: vim, emacs, vscode"}

        response_text = backend._build_response_text(intent, knowledge, "symbiotic")

        assert "🤝" in response_text
        assert "learning" in response_text
        assert "feedback" in response_text.lower()

    def test_build_response_text_no_knowledge(self, backend):
        """Test response building when no knowledge available"""
        intent = Intent(
            type=IntentType.UNKNOWN, entities={}, confidence=0.2, raw_input="xyz abc"
        )

        response_text = backend._build_response_text(intent, None, "minimal")

        assert "not sure" in response_text
        assert "installing packages" in response_text

    # Test Learning (Placeholder)

    def test_learn_debug_mode(self, backend):
        """Test learning in debug mode"""
        os.environ["DEBUG"] = "true"
        request = Request(text="install vim", context={})
        response = Response(
            success=True, text="Installing vim", data={"intent": "install_package"}
        )

        # Should not raise
        backend._learn(request, response)

        # Cleanup
        if "DEBUG" in os.environ:
            del os.environ["DEBUG"]

    # Test Factory Function

    def test_create_backend(self):
        """Test backend factory function"""
        from unittest.mock import Mock, MagicMock, patch, call
        callback = MagicMock()
        backend = create_backend(callback)

        assert isinstance(backend, NixForHumanityBackend)
        assert backend.progress_callback == callback

    def test_create_backend_no_callback(self):
        """Test backend factory without callback"""
        backend = create_backend()

        assert isinstance(backend, NixForHumanityBackend)
        assert backend.progress_callback is None

    # Test Edge Cases

    def test_process_request_empty_text(self, backend):
        """Test processing request with empty text"""
        request = Request(text="", context={})

        response = backend.process_request(request)

        # Should handle gracefully
        assert response is not None
        assert not response.success or response.intent.type == IntentType.UNKNOWN

    def test_extract_commands_empty_plan(self, backend):
        """Test command extraction from empty plan"""
        commands = backend._extract_commands([])

        assert commands == []

    def test_get_suggestions_none_result(self, backend):
        """Test suggestions with None result"""
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.85,
            raw_input="update_system",
        )

        suggestions = backend._get_suggestions(intent, None)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

if __name__ == "__main__":
    pytest.main()
