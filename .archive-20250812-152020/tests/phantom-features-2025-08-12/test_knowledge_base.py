#!/usr/bin/env python3
"""
Unit tests for the KnowledgeBase component
"""

import json
import sqlite3

# Add the src directory to Python path
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from luminous_nix.core import IntentType
from luminous_nix.core.knowledge import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):
    """Test the KnowledgeBase component"""

    def setUp(self):
        """Create a temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_knowledge.db"
        self.kb = KnowledgeBase(self.db_path)

    def tearDown(self):
        """Clean up temporary files"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_database_initialization(self):
        """Test that database tables are created correctly"""
        conn = sqlite3.connect(self.db_path)
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

        # Check package_cache table exists
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='package_cache'"
        )
        self.assertIsNotNone(c.fetchone())

        conn.close()

    def test_get_solution_install(self):
        """Test getting installation solution"""
        solution = self.kb.get_solution(IntentType.INSTALL_PACKAGE)

        self.assertTrue(solution["found"])
        self.assertIn("install", solution["solution"].lower())
        self.assertIsNotNone(solution["example"])
        self.assertIsNotNone(solution["explanation"])

    def test_get_solution_unknown(self):
        """Test handling of unknown intent"""
        # Create a mock unknown intent type
        solution = self.kb.get_solution(None)

        self.assertFalse(solution["found"])
        self.assertIn("don't understand", solution["suggestion"])

    def test_get_install_methods(self):
        """Test getting installation methods for a package"""
        methods = self.kb.get_install_methods("firefox")

        self.assertEqual(len(methods), 4)  # Should have 4 methods

        # Check method names
        method_names = [m["name"] for m in methods]
        self.assertIn("Declarative (Recommended)", method_names)
        self.assertIn("Home Manager", method_names)
        self.assertIn("Imperative (Quick)", method_names)
        self.assertIn("Temporary Shell", method_names)

        # Check each method has required fields
        for method in methods:
            self.assertIn("name", method)
            self.assertIn("description", method)
            self.assertIn("command", method)
            self.assertIn("example", method)
            self.assertIn("firefox", method["example"])

    def test_cache_search_results(self):
        """Test caching and retrieving search results"""
        # Cache some results
        test_results = [
            {"name": "firefox", "version": "120.0", "description": "Web browser"},
            {
                "name": "firefox-esr",
                "version": "115.0",
                "description": "Extended support",
            },
        ]

        self.kb.cache_search_results("firefox", test_results)

        # Retrieve cached results
        cached = self.kb.get_cached_search("firefox")

        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 2)
        self.assertEqual(cached[0]["name"], "firefox")

    def test_cache_expiry(self):
        """Test that cache expires after 24 hours"""
        # This would require mocking time, so we'll just verify the SQL is correct
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Insert old cache entry
        c.execute(
            """
            INSERT INTO package_cache (search_term, results, timestamp)
            VALUES (?, ?, datetime('now', '-2 day'))
        """,
            ("old_search", json.dumps([{"name": "old"}])),
        )
        conn.commit()
        conn.close()

        # Should not retrieve old cache
        cached = self.kb.get_cached_search("old_search")
        self.assertIsNone(cached)

    def test_get_problem_solution(self):
        """Test finding solutions for common problems"""
        # Test command not found
        solution = self.kb.get_problem_solution("command not found")
        self.assertIsNotNone(solution)
        self.assertEqual(solution["symptom"], "command not found")
        self.assertIn("Install package", solution["solution"])

        # Test read-only file system
        solution = self.kb.get_problem_solution("read-only file system")
        self.assertIsNotNone(solution)
        self.assertIn("configuration.nix", solution["solution"])

    def test_get_problem_solution_not_found(self):
        """Test when no problem solution is found"""
        solution = self.kb.get_problem_solution("some random error that does not exist")
        self.assertIsNone(solution)

    def test_solutions_have_all_intent_types(self):
        """Test that we have solutions for all main intent types"""
        intent_types = [
            IntentType.INSTALL_PACKAGE,
            IntentType.REMOVE,
            IntentType.UPDATE_SYSTEM,
            IntentType.SEARCH_PACKAGE,
            IntentType.ROLLBACK,
            IntentType.EXPLAIN,
            IntentType.HELP,
        ]

        for intent_type in intent_types:
            solution = self.kb.get_solution(intent_type)
            self.assertTrue(
                solution["found"], f"No solution found for intent type: {intent_type}"
            )

    def test_package_info_dataclass(self):
        """Test the PackageInfo dataclass"""
        # Test with minimal info
        pkg = PackageInfo(name="firefox")
        self.assertEqual(pkg.name, "firefox")
        self.assertIsNone(pkg.description)
        self.assertIsNone(pkg.version)
        self.assertEqual(pkg.installation_methods, [])

        # Test with full info
        methods = [{"name": "Imperative", "command": "nix profile install"}]
        pkg2 = PackageInfo(
            name="firefox",
            description="Web browser",
            version="120.0",
            installation_methods=methods,
        )
        self.assertEqual(pkg2.description, "Web browser")
        self.assertEqual(pkg2.version, "120.0")
        self.assertEqual(len(pkg2.installation_methods), 1)

if __name__ == "__main__":
    unittest.main()
