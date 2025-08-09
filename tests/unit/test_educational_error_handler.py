#!/usr/bin/env python3
"""
Tests for educational-error-handler.py

Tests the educational error handling functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import re
from pathlib import Path

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, scripts_path)

# Import with hyphenated filename
import importlib.util
spec = importlib.util.spec_from_file_location(
    "educational_error_handler",
    os.path.join(scripts_path, 'educational-error-handler.py')
)
educational_error_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(educational_error_handler)

# Import the classes we need
ErrorCategory = educational_error_handler.ErrorCategory
CommandError = educational_error_handler.CommandError
EducationalErrorHandler = educational_error_handler.EducationalErrorHandler


class TestErrorCategory(unittest.TestCase):
    """Test the ErrorCategory enum."""
    
    def test_error_categories(self):
        """Test that all error categories are defined."""
        # Check all expected categories exist
        self.assertEqual(ErrorCategory.USER_INPUT.value, "user_input")
        self.assertEqual(ErrorCategory.SYSTEM.value, "system")
        self.assertEqual(ErrorCategory.PERMISSION.value, "permission")
        self.assertEqual(ErrorCategory.NOT_FOUND.value, "not_found")
        self.assertEqual(ErrorCategory.SAFETY.value, "safety")
        self.assertEqual(ErrorCategory.NETWORK.value, "network")
        self.assertEqual(ErrorCategory.DISK_SPACE.value, "disk_space")
        self.assertEqual(ErrorCategory.DEPENDENCY.value, "dependency")
        self.assertEqual(ErrorCategory.CONFIGURATION.value, "configuration")
        self.assertEqual(ErrorCategory.UNKNOWN.value, "unknown")


class TestCommandError(unittest.TestCase):
    """Test the CommandError exception class."""
    
    def test_command_error_creation(self):
        """Test creating a CommandError."""
        error = CommandError(
            user_message="Package not found",
            suggestions=["Try searching for a similar package"],
            technical="nixpkgs.firefox not in scope",
            learnable=True,
            category=ErrorCategory.NOT_FOUND,
            recovery_commands=[{"command": "nix search firefox", "description": "Search for firefox"}]
        )
        
        self.assertEqual(error.user_message, "Package not found")
        self.assertEqual(len(error.suggestions), 1)
        self.assertEqual(error.technical, "nixpkgs.firefox not in scope")
        self.assertTrue(error.learnable)
        self.assertEqual(error.category, ErrorCategory.NOT_FOUND)
        self.assertEqual(len(error.recovery_commands), 1)
    
    def test_command_error_defaults(self):
        """Test CommandError with default values."""
        error = CommandError(
            user_message="Something went wrong",
            suggestions=["Please try again"]
        )
        
        self.assertEqual(error.user_message, "Something went wrong")
        self.assertEqual(len(error.suggestions), 1)
        self.assertIsNone(error.technical)
        self.assertTrue(error.learnable)
        self.assertEqual(error.category, ErrorCategory.UNKNOWN)
        self.assertEqual(len(error.recovery_commands), 0)
    
    def test_command_error_str(self):
        """Test CommandError string representation."""
        error = CommandError(
            user_message="Test error",
            suggestions=["Test suggestion"]
        )
        
        self.assertEqual(str(error), "Test error")


class TestEducationalErrorHandler(unittest.TestCase):
    """Test the EducationalErrorHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = EducationalErrorHandler()
    
    def test_initialization(self):
        """Test handler initialization."""
        # Check that error patterns are initialized
        self.assertIsInstance(self.handler.error_patterns, list)
        self.assertGreater(len(self.handler.error_patterns), 0)
        
        # Check that persona adaptations are initialized
        self.assertIsNotNone(self.handler.persona_adaptations)
    
    def test_error_pattern_structure(self):
        """Test error pattern structure."""
        # Check first error pattern
        pattern = self.handler.error_patterns[0]
        
        # Should have required keys
        self.assertIn('pattern', pattern)
        self.assertIn('category', pattern)
        self.assertIn('handler', pattern)
        
        # Pattern should be a string
        self.assertIsInstance(pattern['pattern'], str)
        
        # Category should be ErrorCategory
        self.assertIsInstance(pattern['category'], ErrorCategory)
        
        # Handler should be callable
        self.assertTrue(callable(pattern['handler']))
    
    def test_package_not_found_pattern(self):
        """Test package not found error pattern."""
        # Find package not found pattern
        package_pattern = None
        for pattern in self.handler.error_patterns:
            if pattern['category'] == ErrorCategory.NOT_FOUND:
                package_pattern = pattern
                break
        
        self.assertIsNotNone(package_pattern)
        
        # Test pattern matching
        import re
        test_errors = [
            "attribute 'firefox' is missing",
            "no such package",
            "Package 'vim' not found"
        ]
        
        for error in test_errors:
            # At least one NOT_FOUND pattern should match
            matched = False
            for pattern in self.handler.error_patterns:
                if pattern['category'] == ErrorCategory.NOT_FOUND:
                    if re.search(pattern['pattern'], error, re.IGNORECASE):
                        matched = True
                        break
            self.assertTrue(matched, f"No pattern matched: {error}")
    
    def test_permission_error_pattern(self):
        """Test permission error pattern."""
        # Test permission error patterns
        permission_errors = [
            "permission denied",
            "operation not permitted",
            "access denied",
            "sudo required",
            "requires root",
            "must be root"
        ]
        
        for error in permission_errors:
            # At least one PERMISSION pattern should match
            matched = False
            for pattern in self.handler.error_patterns:
                if pattern['category'] == ErrorCategory.PERMISSION:
                    if re.search(pattern['pattern'], error, re.IGNORECASE):
                        matched = True
                        break
            self.assertTrue(matched, f"No permission pattern matched: {error}")
    
    def test_network_error_pattern(self):
        """Test network error pattern."""
        # Test network error patterns
        network_errors = [
            "network error",
            "connection refused",
            "timeout",
            "cannot reach",
            "SSL error",
            "certificate error"
        ]
        
        for error in network_errors:
            # At least one NETWORK pattern should match
            matched = False
            for pattern in self.handler.error_patterns:
                if pattern['category'] == ErrorCategory.NETWORK:
                    if re.search(pattern['pattern'], error, re.IGNORECASE):
                        matched = True
                        break
            self.assertTrue(matched, f"No network pattern matched: {error}")
    
    def test_disk_space_error_pattern(self):
        """Test disk space error pattern."""
        # Test disk space error patterns
        disk_errors = [
            "no space left",
            "disk full",
            "insufficient space"
        ]
        
        for error in disk_errors:
            # At least one DISK_SPACE pattern should match
            matched = False
            for pattern in self.handler.error_patterns:
                if pattern['category'] == ErrorCategory.DISK_SPACE:
                    if re.search(pattern['pattern'], error, re.IGNORECASE):
                        matched = True
                        break
            self.assertTrue(matched, f"No disk space pattern matched: {error}")


if __name__ == '__main__':
    unittest.main()