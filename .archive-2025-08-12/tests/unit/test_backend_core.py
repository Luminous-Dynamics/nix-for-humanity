#!/usr/bin/env python3
import pytest
import os

# Skip if not on NixOS
if not os.path.exists("/nix/store"):
    pytest.skip("NixOS required for this test", allow_module_level=True)

"""
import subprocess
Comprehensive tests for NixForHumanityBackend

Tests all backend functionality including:
- Initialization and API detection
- Request processing pipeline
- Intent planning and execution
- Error handling
- Native API integration
- Learning system
"""

import asyncio

from unittest.mock import Mock, MagicMock, patch, call
import sys
import unittest
from pathlib import Path

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, "luminous_nix")
sys.path.insert(0, backend_path)

# Import the module we're testing
from luminous_nix.api.schema import Request, Response, Result
from luminous_nix.core.engine import NixForHumanityBackend, create_backend
from luminous_nix.core import Intent, IntentType

class TestNixForHumanityBackend(unittest.TestCase):
    """Test the NixForHumanityBackend class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the imports that might not be available
        self.mock_intent_recognizer = Mock()
        self.mock_executor = Mock()
        self.mock_knowledge = Mock()

        # Patch the dependencies
        self.patches = [
            patch(
                "core.backend.IntentRecognizer",
                return_value=self.mock_intent_recognizer,
            ),
            patch("core.backend.SafeExecutor", return_value=self.mock_executor),
            patch("core.backend.KnowledgeBase", return_value=self.mock_knowledge),
            patch("core.backend.NATIVE_INTEGRATION_AVAILABLE", False),
            patch("core.backend.NativeOperations", False),
        ]

        for p in self.patches:
            p.start()

        # Create backend instance
        self.progress_callback = Mock()
        self.backend = NixForHumanityBackend(self.progress_callback)

    def tearDown(self):
        """Clean up test fixtures."""
        for p in self.patches:
            p.stop()

    def test_init_creates_components(self):
        """Test that initialization creates all necessary components."""
        self.assertEqual(self.backend.intent_recognizer, self.mock_intent_recognizer)
        self.assertEqual(self.backend.executor, self.mock_executor)
        self.assertEqual(self.backend.knowledge, self.mock_knowledge)
        self.assertEqual(self.backend.progress_callback, self.progress_callback)
        self.assertIsNone(self.backend.nix_integration)

    def test_init_nixos_api_with_path(self):
        """Test nixos API initialization when path is found."""
        # Create a new backend with mocked path finding
        with patch(
            "core.backend.NixForHumanityBackend._find_nixos_rebuild_path"
        ) as mock_find:
            mock_find.return_value = Path("/mock/path")

            with patch("sys.path", []) as mock_syspath:
                backend = NixForHumanityBackend()

                # Check that path was added
                self.assertIn("/mock/path", mock_syspath)

    def test_find_nixos_rebuild_path_known_paths(self):
        """Test finding nixos-rebuild path from known locations."""
        # Mock Path.exists
        with patch("pathlib.Path.exists") as mock_exists:
            # First path exists
            mock_exists.side_effect = [True, True]  # path exists, nixos_rebuild exists

            result = self.backend._find_nixos_rebuild_path()

            expected_path = Path(
                "/nix/store/nmg1ksa23fpsl631x3n8lnp9467vqiqi-nixos-rebuild-ng-0.0.0/lib/python3.13/site-packages"
            )
            self.assertEqual(result, expected_path)

    def test_find_nixos_rebuild_path_via_which(self):
        """Test finding nixos-rebuild path via which command."""
        with patch(
            "pathlib.Path.exists", return_value=False
        ):  # Known paths don't exist
            with patch("subprocess.run") as mock_run:
                # Mock successful which command
                mock_run.return_value = Mock(
                    returncode=0, stdout="/nix/store/abc/bin/nixos-rebuild\n"
                )

                # Mock the path resolution
                with patch("pathlib.Path.resolve") as mock_resolve:
                    mock_resolve.return_value = Path("/nix/store/abc/bin/nixos-rebuild")

                    # Mock parents and site-packages check
                    mock_parent = Mock()
                    mock_site_packages = Mock()
                    mock_site_packages.exists.return_value = True

                    with patch.object(Path, "parents", [mock_parent]):
                        with patch.object(mock_parent, "__truediv__") as mock_div:
                            mock_div.return_value = mock_site_packages

                            result = self.backend._find_nixos_rebuild_path()

                            # Should find via which command
                            mock_run.assert_called_once()

    @patch("core.backend.asyncio.create_task")
    async def test_process_request_success(self, mock_create_task):
        """Test successful request processing."""
        # Setup mocks
        request = Request(query="install firefox", context={})

        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.9,
            raw_input="install firefox",
        )

        # Mock async recognize method
        self.mock_intent_recognizer.recognize = AsyncMock(return_value=intent)

        # Mock input validation
        with patch(
            "backend.security.input_validator.InputValidator.validate_input"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "sanitized_input": "install firefox",
            }

            # Process request
            response = await self.backend.process_request(request)

            # Verify response
            self.assertIsInstance(response, Response)
            self.assertEqual(response.intent, intent)
            self.assertTrue(response.success)

            # Verify progress callbacks
            self.progress_callback.assert_any_call("Analyzing request...", 0.2)
            self.progress_callback.assert_any_call("Planning actions...", 0.4)

            # Verify learning task was created
            mock_create_task.assert_called_once()

    async def test_process_request_invalid_input(self):
        """Test request processing with invalid input."""
        request = Request(query="<script>alert('xss')</script>", context={})

        # Mock input validation failure
        with patch(
            "backend.security.input_validator.InputValidator.validate_input"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "reason": "Potential XSS attack detected",
                "suggestions": ["Please remove script tags"],
            }

            response = await self.backend.process_request(request)

            # Verify error response
            self.assertFalse(response.success)
            self.assertIn("XSS attack", response.result.error)
            self.assertEqual(response.suggestions, ["Please remove script tags"])

    async def test_process_request_with_execution(self):
        """Test request processing with command execution."""
        request = Request(
            query="install vim", context={"execute": True, "dry_run": False}
        )

        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "vim"},
            confidence=0.9,
            raw_input="install vim",
        )

        # Mock async methods
        self.mock_intent_recognizer.recognize = AsyncMock(return_value=intent)
        self.mock_executor.execute = AsyncMock(
            return_value=Result(
                success=True, output="Package vim installed successfully", error=None
            )
        )

        with patch(
            "backend.security.input_validator.InputValidator.validate_input"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "sanitized_input": "install vim",
            }

            with patch("core.backend.asyncio.create_task"):
                response = await self.backend.process_request(request)

                # Verify execution was called
                self.mock_executor.execute.assert_called_once()

                # Verify response
                self.assertTrue(response.success)
                self.assertIsNotNone(response.result)
                self.assertTrue(response.result.success)

    async def test_process_request_exception_handling(self):
        """Test exception handling in request processing."""
        request = Request(query="test error", context={})

        # Mock recognize to raise exception
        self.mock_intent_recognizer.recognize = AsyncMock(
            side_effect=Exception("Test error")
        )

        with patch(
            "backend.security.input_validator.InputValidator.validate_input"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "sanitized_input": "test error",
            }

            response = await self.backend.process_request(request)

            # Verify error response
            self.assertFalse(response.success)
            self.assertIsNotNone(response.result.error)
            self.assertEqual(response.intent.type, IntentType.UNKNOWN)

    async def test_plan_actions_install_package(self):
        """Test action planning for package installation."""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.9,
            raw_input="install firefox",
        )

        request = Request(query="install firefox", context={})

        # Test without Python API
        self.backend._has_python_api = False
        plan = await self.backend._plan_actions(intent, request)

        self.assertIn("Use nix profile install nixpkgs#firefox", plan[0])
        self.assertIn("Verify firefox installation", plan[1])

        # Test with Python API
        self.backend._has_python_api = True
        plan = await self.backend._plan_actions(intent, request)

        self.assertIn("Use Python API to install firefox", plan[0])

    async def test_plan_actions_update_system(self):
        """Test action planning for system update."""
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.9,
            raw_input="update system",
        )

        request = Request(query="update system", context={})

        self.backend._has_python_api = False
        plan = await self.backend._plan_actions(intent, request)

        self.assertIn("sudo nix-channel --update", plan[0])
        self.assertIn("sudo nixos-rebuild switch", plan[1])

    def test_explain_with_entities(self):
        """Test explanation generation with entity substitution."""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "vim"},
            confidence=0.9,
            raw_input="install vim",
        )

        plan = ["Install vim"]
        result = Result(success=True, output="Success", error=None)

        explanation = self.backend._explain(intent, plan, result)

        self.assertIn("vim", explanation)
        self.assertIn("successfully", explanation)

    def test_get_suggestions_install_success(self):
        """Test suggestion generation for successful installation."""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.9,
            raw_input="install firefox",
        )

        result = Result(success=True, output="Installed", error=None)

        suggestions = self.backend._get_suggestions(intent, result)

        self.assertIn("run firefox from your terminal", suggestions[0])
        self.assertIn("configuration.nix", suggestions[1])

    def test_extract_commands(self):
        """Test command extraction from plan."""
        plan = [
            "Use nix profile install nixpkgs#firefox",
            "Update channels: sudo nix-channel --update",
            "Rebuild system: sudo nixos-rebuild switch",
        ]

        commands = self.backend._extract_commands(plan)

        self.assertEqual(len(commands), 3)
        self.assertEqual(commands[0]["command"], "nix profile install nixpkgs#firefox")
        self.assertEqual(commands[1]["command"], "sudo nix-channel --update")
        self.assertEqual(commands[2]["command"], "sudo nixos-rebuild switch")

    def test_should_use_native_api(self):
        """Test native API usage decision."""
        # Without environment variable
        with patch.dict(os.environ, {}, clear=True):
            request = Request(query="update system", context={})
            self.assertFalse(self.backend._should_use_native_api(request))

        # With environment variable
        with patch.dict(os.environ, {"LUMINOUS_NIX_PYTHON_BACKEND": "true"}):
            # NixOS operation
            request = Request(query="update system", context={})
            self.assertTrue(self.backend._should_use_native_api(request))

            # Non-NixOS operation
            request = Request(query="what is the weather", context={})
            self.assertFalse(self.backend._should_use_native_api(request))

    def test_process_sync(self):
        """Test synchronous process method."""
        request = Request(query="install firefox", context={"personality": "friendly"})

        # Mock intent recognition
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.9,
            raw_input="install firefox",
        )
        self.mock_intent_recognizer.recognize.return_value = intent

        # Mock knowledge response
        self.mock_knowledge.get_solution.return_value = {
            "package": "firefox",
            "methods": [
                {
                    "name": "User Profile",
                    "description": "Install to user profile",
                    "example": "nix profile install nixpkgs#firefox",
                }
            ],
            "explanation": "Firefox is a popular web browser",
        }

        response = self.backend.process(request)

        self.assertIsInstance(response, Response)
        self.assertTrue(response.success)
        self.assertIn("firefox", response.text)
        self.assertIn("friendly", response.text)  # Should have friendly personality

    def test_build_response_text_personalities(self):
        """Test response text building with different personalities."""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "vim"},
            confidence=0.9,
            raw_input="install vim",
        )

        knowledge = {
            "package": "vim",
            "solution": "Install vim using nix",
            "example": "nix profile install nixpkgs#vim",
            "explanation": "Vim is a text editor",
        }

        # Test different personalities
        personalities = {
            "minimal": lambda t: "nix profile install" in t and "😊" not in t,
            "friendly": lambda t: "Hi there!" in t and "😊" in t,
            "encouraging": lambda t: "Great question!" in t and "🌟" in t,
            "technical": lambda t: "declarative configuration paradigm" in t,
            "symbiotic": lambda t: "🤝" in t and "learning" in t,
        }

        for personality, check_fn in personalities.items():
            response_text = self.backend._build_response_text(
                intent, knowledge, personality
            )
            self.assertTrue(
                check_fn(response_text),
                f"Personality {personality} failed check. Response: {response_text}",
            )

    def test_create_backend_function(self):
        """Test the create_backend convenience function."""
        progress_cb = Mock()
        backend = create_backend(progress_cb)

        self.assertIsInstance(backend, NixForHumanityBackend)
        self.assertEqual(backend.progress_callback, progress_cb)

    async def test_learn_method(self):
        """Test the learning method (placeholder)."""
        request = Request(query="test", context={})
        response = Response(
            success=True, text="test response", commands=[], data={"intent": "test"}
        )

        with patch.dict(os.environ, {"DEBUG": "1"}):
            with patch("builtins.print") as mock_print:
                await self.backend._learn(request, response)

                # Should print debug info
                mock_print.assert_called_once()
                call_args = mock_print.call_args[0][0]
                self.assertIn("Learning from:", call_args)
                self.assertIn("test", call_args)

class TestBackendAsyncIntegration(unittest.TestCase):
    """Test async integration aspects of the backend."""

    def setUp(self):
        """Set up async test environment."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up async environment."""
        self.loop.close()

    def test_async_to_sync_conversion(self):
        """Test that async methods work in sync context."""
        with (
            patch("core.backend.IntentRecognizer"),
            patch("core.backend.SafeExecutor"),
            patch("core.backend.KnowledgeBase"),
        ):
            backend = NixForHumanityBackend()

            # Mock the sync process method
            with patch.object(backend, "_process_sync") as mock_sync:
                mock_sync.return_value = Response(
                    success=True, text="test", commands=[], data={}
                )

                request = Request(query="test", context={})
                response = backend.process(request)

                self.assertIsInstance(response, Response)
                mock_sync.assert_called_once_with(request)

if __name__ == "__main__":
    unittest.main()
