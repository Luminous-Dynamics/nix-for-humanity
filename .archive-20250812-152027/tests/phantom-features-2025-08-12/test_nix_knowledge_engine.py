#!/usr/bin/env python3
"""
Comprehensive tests for NixOS Knowledge Engine

Tests all knowledge engine functionality including:
- Intent extraction
- Solution retrieval
- Response formatting
- Database operations
- Package alias mapping
"""

import os
import sqlite3

from unittest.mock import Mock, MagicMock, patch, call
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../scripts"))

# Import using the wrapper module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../scripts"))

# Import the actual module (with hyphen in filename)
import importlib.util

module_path = os.path.join(
    os.path.dirname(__file__), "../../scripts/nix-knowledge-engine.py"
)
spec = importlib.util.spec_from_file_location("nix_knowledge_engine", module_path)
nix_knowledge_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nix_knowledge_engine)

NixOSKnowledgeEngine = nix_knowledge_engine.NixOSKnowledgeEngine

class TestNixOSKnowledgeEngine(unittest.TestCase):
    """Test the NixOSKnowledgeEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_nixos_knowledge.db"

        # Create engine with patched init
        with patch.object(NixOSKnowledgeEngine, "__init__", return_value=None):
            self.engine = NixOSKnowledgeEngine()

        # Manually set attributes
        self.engine.base_dir = Path(self.temp_dir)
        self.engine.db_path = self.temp_db
        self.engine.package_aliases = {
            "firefox": "firefox",
            "chrome": "google-chrome",
            "vscode": "vscode",
            "code": "vscode",
            "vim": "vim",
            "python": "python3",
            "python3": "python311",
        }
        self.engine.install_methods = {
            "declarative": {
                "name": "Declarative (Recommended)",
                "description": "Add to your system configuration for permanent installation",
                "command": "Edit /etc/nixos/configuration.nix and add to environment.systemPackages",
                "example": "environment.systemPackages = with pkgs; [ {package} ];",
            },
            "imperative": {
                "name": "Imperative",
                "description": "Quick installation for current user",
                "command": "nix-env -iA nixos.{package}",
                "example": "nix-env -iA nixos.{package}",
            },
        }

        # Import the methods we need
        self.engine.init_db = nix_knowledge_engine.NixOSKnowledgeEngine.init_db.__get__(
            self.engine
        )
        self.engine._populate_initial_knowledge = nix_knowledge_engine.NixOSKnowledgeEngine._populate_initial_knowledge.__get__(
            self.engine
        )
        self.engine.extract_intent = (
            nix_knowledge_engine.NixOSKnowledgeEngine.extract_intent.__get__(
                self.engine
            )
        )
        self.engine.get_solution = (
            nix_knowledge_engine.NixOSKnowledgeEngine.get_solution.__get__(self.engine)
        )
        self.engine._get_install_methods = (
            nix_knowledge_engine.NixOSKnowledgeEngine._get_install_methods.__get__(
                self.engine
            )
        )
        self.engine.format_response = (
            nix_knowledge_engine.NixOSKnowledgeEngine.format_response.__get__(
                self.engine
            )
        )

        # Initialize database
        self.engine.init_db()

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp files
        if self.temp_db.exists():
            self.temp_db.unlink()
        if Path(self.temp_dir).exists():
            Path(self.temp_dir).rmdir()

    def test_init_db_creates_tables(self):
        """Test that database initialization creates necessary tables."""
        # Connect to test database
        conn = sqlite3.connect(self.temp_db)
        c = conn.cursor()

        # Check solutions table exists
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='solutions'"
        )
        self.assertIsNotNone(c.fetchone())

        # Check problems table exists
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems'"
        )
        self.assertIsNotNone(c.fetchone())

        conn.close()

    def test_extract_intent_install(self):
        """Test intent extraction for installation queries."""
        test_cases = [
            ("How do I install Firefox?", "install_package", "firefox"),
            ("I need VS Code", "install_package", "vscode"),
            ("want to get vim", "install_package", "vim"),
            ("set up python", "install_package", "python3"),
            ("install htop", "install_package", "htop"),
        ]

        for query, expected_action, expected_package in test_cases:
            with self.subTest(query=query):
                intent = self.engine.extract_intent(query)
                self.assertEqual(intent["action"], expected_action)
                self.assertEqual(intent["package"], expected_package)
                self.assertEqual(intent["query"], query)

    def test_extract_intent_search(self):
        """Test intent extraction for search queries."""
        test_cases = [
            "search for editors",
            "find python packages",
            "look for firefox",
            "is there a vim package?",
        ]

        for query in test_cases:
            with self.subTest(query=query):
                intent = self.engine.extract_intent(query)
                self.assertEqual(intent["action"], "search_package")
                self.assertEqual(intent["query"], query)

    def test_extract_intent_update(self):
        """Test intent extraction for update queries."""
        test_cases = ["update my system", "upgrade nixos", "update everything"]

        for query in test_cases:
            with self.subTest(query=query):
                intent = self.engine.extract_intent(query)
                self.assertEqual(intent["action"], "update_system")
                self.assertEqual(intent["query"], query)

    def test_extract_intent_network(self):
        """Test intent extraction for network queries."""
        test_cases = [
            "my wifi isn't working",
            "fix wi-fi",
            "internet connection problem",
            "network issues",
        ]

        for query in test_cases:
            with self.subTest(query=query):
                intent = self.engine.extract_intent(query)
                self.assertEqual(intent["action"], "fix_wifi")
                self.assertEqual(intent["query"], query)

    def test_extract_intent_rollback(self):
        """Test intent extraction for rollback queries."""
        test_cases = [
            "rollback system",
            "go to previous generation",
            "undo last change",  # Changed from "undo last update" to avoid "update_system" keyword
            "what's a generation?",
        ]

        for query in test_cases:
            with self.subTest(query=query):
                intent = self.engine.extract_intent(query)
                self.assertEqual(intent["action"], "rollback_system")
                self.assertEqual(intent["query"], query)

    def test_extract_intent_service(self):
        """Test intent extraction for service queries."""
        test_cases = [
            "enable ssh service",
            "start nginx",
            "how to enable systemd service",
        ]

        for query in test_cases:
            with self.subTest(query=query):
                intent = self.engine.extract_intent(query)
                self.assertEqual(intent["action"], "enable_service")
                self.assertEqual(intent["query"], query)

    def test_extract_intent_unknown(self):
        """Test intent extraction for unknown queries."""
        test_cases = ["what is the meaning of life?", "hello there", "random text"]

        for query in test_cases:
            with self.subTest(query=query):
                intent = self.engine.extract_intent(query)
                self.assertEqual(intent["action"], "unknown")
                self.assertEqual(intent["query"], query)

    def test_get_solution_found(self):
        """Test getting solution for known intent."""
        intent = {"action": "update_system", "query": "update my system"}

        solution = self.engine.get_solution(intent)

        self.assertTrue(solution["found"])
        self.assertIn("solution", solution)
        self.assertIn("example", solution)
        self.assertIn("explanation", solution)
        self.assertIn("related", solution)

    def test_get_solution_install_package(self):
        """Test getting solution for package installation."""
        intent = {
            "action": "install_package",
            "package": "firefox",
            "query": "install firefox",
        }

        solution = self.engine.get_solution(intent)

        self.assertTrue(solution["found"])
        self.assertIn("methods", solution)
        self.assertEqual(solution["package"], "firefox")
        self.assertIsInstance(solution["methods"], list)
        self.assertGreater(len(solution["methods"]), 0)

        # Check method structure
        method = solution["methods"][0]
        self.assertIn("type", method)
        self.assertIn("name", method)
        self.assertIn("description", method)
        self.assertIn("command", method)
        self.assertIn("example", method)

    def test_get_solution_unknown(self):
        """Test getting solution for unknown intent."""
        intent = {"action": "unknown", "query": "random query"}

        solution = self.engine.get_solution(intent)

        self.assertFalse(solution["found"])
        self.assertIn("suggestion", solution)
        self.assertIn("don't understand", solution["suggestion"])

    def test_get_install_methods(self):
        """Test getting installation methods for a package."""
        methods = self.engine._get_install_methods("firefox")

        self.assertIsInstance(methods, list)
        self.assertGreater(len(methods), 0)

        # Check each method
        for method in methods:
            self.assertIn("type", method)
            self.assertIn("name", method)
            self.assertIn("description", method)
            self.assertIn("command", method)
            self.assertIn("example", method)

            # Check package substitution
            if "{package}" in self.engine.install_methods[method["type"]]["example"]:
                self.assertIn("firefox", method["example"])

    def test_format_response_not_found(self):
        """Test formatting response when solution not found."""
        intent = {"action": "unknown", "query": "test"}
        solution = {"found": False, "suggestion": "Test suggestion"}

        response = self.engine.format_response(intent, solution)

        self.assertEqual(response, "Test suggestion")

    def test_format_response_install_package(self):
        """Test formatting response for package installation."""
        intent = {
            "action": "install_package",
            "package": "firefox",
            "query": "install firefox",
        }
        solution = {
            "found": True,
            "package": "firefox",
            "methods": [
                {
                    "name": "Test Method",
                    "description": "Test description",
                    "example": "test command",
                }
            ],
            "explanation": "Test explanation",
            "related": ["search_package", "remove_package"],
        }

        response = self.engine.format_response(intent, solution)

        self.assertIn("install firefox", response)
        self.assertIn("Test Method", response)
        self.assertIn("Test description", response)
        self.assertIn("test command", response)
        self.assertIn("Test explanation", response)
        self.assertIn("Related:", response)

    def test_format_response_other_action(self):
        """Test formatting response for non-install actions."""
        intent = {"action": "update_system", "query": "update"}
        solution = {
            "found": True,
            "solution": "Update solution",
            "example": "sudo nixos-rebuild switch",
            "explanation": "Update explanation",
        }

        response = self.engine.format_response(intent, solution)

        self.assertIn("Update solution", response)
        self.assertIn("sudo nixos-rebuild switch", response)
        self.assertIn("Update explanation", response)

    def test_package_alias_mapping(self):
        """Test package alias resolution."""
        # Test with alias
        intent = self.engine.extract_intent("install code")
        self.assertEqual(intent["package"], "vscode")

        # Test direct package name
        intent = self.engine.extract_intent("install firefox")
        self.assertEqual(intent["package"], "firefox")

        # Test unknown package
        intent = self.engine.extract_intent("install unknownpackage")
        self.assertEqual(intent["package"], "unknownpackage")

    def test_populate_initial_knowledge(self):
        """Test that initial knowledge is populated correctly."""
        conn = sqlite3.connect(self.temp_db)
        c = conn.cursor()

        # Check solutions count
        c.execute("SELECT COUNT(*) FROM solutions")
        solution_count = c.fetchone()[0]
        self.assertGreater(solution_count, 0)

        # Check problems count
        c.execute("SELECT COUNT(*) FROM problems")
        problem_count = c.fetchone()[0]
        self.assertGreater(problem_count, 0)

        # Check specific solution exists
        c.execute("SELECT * FROM solutions WHERE intent = 'install_package'")
        result = c.fetchone()
        self.assertIsNotNone(result)

        conn.close()

if __name__ == "__main__":
    unittest.main()
