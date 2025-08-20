#!/usr/bin/env python3
"""
Simplified tests for SafeExecutor - focusing on synchronous methods

Tests the safe execution of NixOS commands with security validation,
rollback support, and progress reporting.
"""

import os

from unittest.mock import Mock, MagicMock, patch, call
import sys
import unittest

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, "luminous_nix")
sys.path.insert(0, backend_path)

# Mock the imports that might not be available
sys.modules["luminous_nix.python"] = MagicMock()
sys.modules["luminous_nix.python.native_nix_backend"] = MagicMock()

# Import after mocking
from luminous_nix.core.executor import ValidationResult
from luminous_nix.core import SafeExecutor
from luminous_nix.core import Intent, IntentType

class TestValidationResult(unittest.TestCase):
    """Test the ValidationResult class."""

    def test_validation_result_creation(self):
        """Test creating ValidationResult objects."""
        # Valid result
        result = ValidationResult(valid=True, reason="All checks passed")
        self.assertTrue(result.valid)
        self.assertEqual(result.reason, "All checks passed")

        # Invalid result
        result = ValidationResult(valid=False, reason="Dangerous pattern detected")
        self.assertFalse(result.valid)
        self.assertEqual(result.reason, "Dangerous pattern detected")

class TestSafeExecutor(unittest.TestCase):
    """Test the SafeExecutor class - synchronous methods only."""

    def setUp(self):
        """Set up test fixtures."""
        self.progress_callback = Mock()

        # Create executor
        with patch("backend.core.executor.SafeExecutor._init_python_api"):
            self.executor = SafeExecutor(progress_callback=self.progress_callback)
            self.executor._has_python_api = False
            self.executor.native_backend = None

    def test_init(self):
        """Test SafeExecutor initialization."""
        with patch("backend.core.executor.SafeExecutor._init_python_api") as mock_init:
            executor = SafeExecutor()
            self.assertIsNone(executor.progress_callback)
            self.assertFalse(executor.dry_run)
            mock_init.assert_called_once()

        # With progress callback
        callback = Mock()
        with patch("backend.core.executor.SafeExecutor._init_python_api"):
            executor = SafeExecutor(progress_callback=callback)
            self.assertEqual(executor.progress_callback, callback)

    def test_get_operation_type(self):
        """Test mapping intent to operation type."""
        test_cases = [
            (IntentType.INSTALL_PACKAGE, "install-package"),
            (IntentType.UPDATE_SYSTEM, "modify-configuration"),
            (IntentType.CONFIGURE, "modify-configuration"),
            (IntentType.ROLLBACK, "modify-configuration"),
            (IntentType.SEARCH_PACKAGE, "read-file"),
            (IntentType.EXPLAIN, "read-file"),
            (IntentType.HELP, "read-file"),
            (IntentType.REMOVE_PACKAGE, "remove-package"),
            (IntentType.UNKNOWN, "unknown"),
        ]

        for intent_type, expected_op in test_cases:
            intent = Intent(
                type=intent_type, entities={}, confidence=1.0, raw_text="test"
            )
            result = self.executor._get_operation_type(intent)
            self.assertEqual(result, expected_op)

    def test_progress_wrapper(self):
        """Test progress callback wrapper."""
        self.executor._progress_wrapper("Installing package", 0.5)
        self.progress_callback.assert_called_once_with("Installing package", 0.5)

        # Test without callback
        with patch("backend.core.executor.SafeExecutor._init_python_api"):
            executor = SafeExecutor()
            # Should not raise error
            executor._progress_wrapper("Test", 0.1)

    def test_validate_package_name(self):
        """Test package name validation."""
        # Valid packages
        valid_packages = [
            "firefox",
            "google-chrome",
            "python3",
            "lib-test",
            "package_name",
            "pkg123",
        ]

        for pkg in valid_packages:
            self.assertTrue(
                self.executor._validate_package_name(pkg),
                f"Package '{pkg}' should be valid",
            )

        # Invalid packages
        invalid_packages = [
            None,
            "",
            "a" * 101,  # Too long
            "../etc/passwd",  # Path traversal
            "pkg;rm -rf /",  # Shell injection
            ".hidden",  # Starts with dot
            "-flag",  # Starts with dash
            "sudo",  # Special name
            "..",  # Special name
            "pkg$var",  # Shell variable
        ]

        for pkg in invalid_packages:
            self.assertFalse(
                self.executor._validate_package_name(pkg),
                f"Package '{pkg}' should be invalid",
            )

    def test_validate_search_query(self):
        """Test search query validation."""
        # Valid queries
        valid_queries = ["firefox", "text editor", "python development", "web-browser"]

        for query in valid_queries:
            self.assertTrue(
                self.executor._validate_search_query(query),
                f"Query '{query}' should be valid",
            )

        # Invalid queries
        invalid_queries = [
            None,
            "",
            "a" * 201,  # Too long
            "search; rm -rf /",  # Shell injection
            "query | cat /etc/passwd",  # Pipe
            "search`whoami`",  # Command substitution
            "<script>alert(1)</script>",  # XSS attempt
        ]

        for query in invalid_queries:
            self.assertFalse(
                self.executor._validate_search_query(query),
                f"Query '{query}' should be invalid",
            )

    def test_validate_command_args(self):
        """Test command argument validation."""
        # Valid commands
        valid_commands = [
            ["nix", "search", "firefox"],
            ["sudo", "nixos-rebuild", "switch"],
            ["nix-env", "-i", "package"],
            ["nix-channel", "--update"],
        ]

        for cmd in valid_commands:
            self.assertTrue(
                self.executor._validate_command_args(cmd),
                f"Command {cmd} should be valid",
            )

        # Invalid commands
        invalid_commands = [
            None,
            [],
            ["rm", "-rf", "/"],  # Not whitelisted
            ["nix", "search; rm -rf /"],  # Shell injection
            ["wget", "http://example.com"],  # Not whitelisted
            ["curl", "http://example.com"],  # Not whitelisted
        ]

        for cmd in invalid_commands:
            self.assertFalse(
                self.executor._validate_command_args(cmd),
                f"Command {cmd} should be invalid",
            )

    def test_validate_execution_request(self):
        """Test comprehensive execution request validation."""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=1.0,
            raw_text="install firefox",
        )

        # Valid request
        result = self.executor._validate_execution_request(["install firefox"], intent)
        self.assertTrue(result.valid)
        self.assertEqual(result.reason, "Validation passed")

        # Too many actions
        long_plan = [f"action{i}" for i in range(25)]
        result = self.executor._validate_execution_request(long_plan, intent)
        self.assertFalse(result.valid)
        self.assertIn("too complex", result.reason)

        # Invalid action type
        result = self.executor._validate_execution_request([123], intent)
        self.assertFalse(result.valid)
        self.assertIn("Invalid action type", result.reason)

        # Dangerous pattern
        result = self.executor._validate_execution_request(["rm -rf /"], intent)
        self.assertFalse(result.valid)
        self.assertIn("Unsafe pattern", result.reason)

    def test_create_rebuild_script(self):
        """Test creating rebuild script for background execution."""
        script_path = self.executor._create_rebuild_script()

        self.assertTrue(script_path.exists())
        self.assertEqual(script_path.name, "nixos-rebuild-wrapper.sh")

        # Check script content
        content = script_path.read_text()
        self.assertIn("nixos-rebuild switch", content)
        self.assertIn("/tmp/nixos-rebuild.log", content)

        # Check permissions
        stat_info = script_path.stat()
        self.assertEqual(stat_info.st_mode & 0o777, 0o755)

        # Cleanup
        script_path.unlink()

    def test_new_intent_types_mapping(self):
        """Test operation type mapping for new intent types."""
        new_intent_types = [
            (IntentType.GARBAGE_COLLECT, "modify-configuration"),
            (IntentType.LIST_GENERATIONS, "read-file"),
            (IntentType.SWITCH_GENERATION, "modify-configuration"),
            (IntentType.REBUILD, "modify-configuration"),
            (IntentType.EDIT_CONFIG, "read-file"),
            (IntentType.SHOW_CONFIG, "read-file"),
            (IntentType.CHECK_STATUS, "read-file"),
            (IntentType.LIST_INSTALLED, "read-file"),
        ]

        for intent_type, expected_op in new_intent_types:
            intent = Intent(
                type=intent_type, entities={}, confidence=1.0, raw_text="test"
            )
            result = self.executor._get_operation_type(intent)
            self.assertEqual(
                result,
                expected_op,
                f"Intent type {intent_type} should map to {expected_op}",
            )

if __name__ == "__main__":
    unittest.main()
