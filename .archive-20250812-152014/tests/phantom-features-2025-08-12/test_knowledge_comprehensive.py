#!/usr/bin/env python3
"""
Comprehensive unit tests for the KnowledgeBase module.

This test suite aims to achieve 100% coverage of the knowledge.py module,
testing all database operations, knowledge retrieval methods, and edge cases.
"""

from unittest.mock import Mock, MagicMock, patch, call
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from luminous_nix.core.knowledge import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):
    """Test suite for KnowledgeBase class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.test_dir) / "test_knowledge.db"

        # Store the original init
        self.original_init = KnowledgeBase.__init__

        # Create a custom init that uses our test directory
        test_dir = self.test_dir

        def mock_init(kb_self):
            kb_self.base_dir = Path(test_dir)
            kb_self.db_path = kb_self.base_dir / "test_knowledge.db"
            kb_self._ensure_database()

        # Replace the init method
        KnowledgeBase.__init__ = mock_init

    def tearDown(self):
        """Clean up test fixtures"""
        # Restore the original init
        KnowledgeBase.__init__ = self.original_init
        # Remove the temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _get_db_connection(self):
        """Get a connection to the test database"""
        return sqlite3.connect(self.test_db_path)

    def test_initialization(self):
        """Test KnowledgeBase initialization"""
        kb = KnowledgeBase()
        self.assertEqual(kb.base_dir, Path(self.test_dir))
        self.assertEqual(kb.db_path, self.test_db_path)
        self.assertTrue(self.test_db_path.exists())

    def test_database_creation(self):
        """Test database and tables are created correctly"""
        kb = KnowledgeBase()

        # Check that database file exists
        self.assertTrue(self.test_db_path.exists())

        # Check tables exist
        conn = self._get_db_connection()
        c = conn.cursor()

        # Check solutions table
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='solutions'"
        )
        self.assertIsNotNone(c.fetchone())

        # Check problems table
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems'"
        )
        self.assertIsNotNone(c.fetchone())

        # Check best_practices table
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='best_practices'"
        )
        self.assertIsNotNone(c.fetchone())

        conn.close()

    def test_initial_knowledge_population(self):
        """Test initial knowledge is populated correctly"""
        kb = KnowledgeBase()

        conn = self._get_db_connection()
        c = conn.cursor()

        # Check solutions are populated
        c.execute("SELECT COUNT(*) FROM solutions")
        solution_count = c.fetchone()[0]
        self.assertGreater(solution_count, 0)

        # Check problems are populated
        c.execute("SELECT COUNT(*) FROM problems")
        problem_count = c.fetchone()[0]
        self.assertGreater(problem_count, 0)

        # Check best practices are populated
        c.execute("SELECT COUNT(*) FROM best_practices")
        practice_count = c.fetchone()[0]
        self.assertGreater(practice_count, 0)

        conn.close()

    def test_get_solution_install_package(self):
        """Test getting solution for install_package intent"""
        kb = KnowledgeBase()

        # Test with firefox
        result = kb.get_solution("install_package", "install firefox")
        self.assertIsNotNone(result)
        self.assertTrue(result["found"])
        self.assertEqual(result["package"], "firefox")
        self.assertIn("methods", result)
        self.assertIn("commands", result)
        self.assertGreater(len(result["methods"]), 0)
        self.assertGreater(len(result["commands"]), 0)

        # Test with alias (chrome -> google-chrome)
        result = kb.get_solution("install_package", "install chrome")
        self.assertIsNotNone(result)
        self.assertEqual(result["package"], "google-chrome")

        # Test with vscode alias
        result = kb.get_solution("install_package", "I need code")
        self.assertIsNotNone(result)
        self.assertEqual(result["package"], "vscode")

    def test_get_solution_other_intents(self):
        """Test getting solutions for non-install intents"""
        kb = KnowledgeBase()

        # Test update_system
        result = kb.get_solution("update_system", "update my system")
        self.assertIsNotNone(result)
        self.assertTrue(result["found"])
        self.assertIn("solution", result)
        self.assertIn("example", result)
        self.assertIn("explanation", result)
        self.assertIn("response", result)

        # Test search_package
        result = kb.get_solution("search_package", "search for browsers")
        self.assertIsNotNone(result)
        self.assertTrue(result["found"])

    def test_get_solution_nonexistent_intent(self):
        """Test getting solution for non-existent intent"""
        kb = KnowledgeBase()

        result = kb.get_solution("nonexistent_intent", "do something")
        self.assertIsNone(result)

    def test_get_installation_methods(self):
        """Test getting installation methods for a package"""
        kb = KnowledgeBase()

        methods = kb.get_installation_methods("firefox")
        self.assertIsInstance(methods, list)
        self.assertEqual(len(methods), 5)  # Should have 5 methods

        # Check method structure
        for method in methods:
            self.assertIn("type", method)
            self.assertIn("name", method)
            self.assertIn("description", method)
            self.assertIn("command", method)
            self.assertIn("example", method)

        # Check specific method types
        method_types = [m["type"] for m in methods]
        self.assertIn("declarative", method_types)
        self.assertIn("home-manager", method_types)
        self.assertIn("imperative", method_types)
        self.assertIn("shell", method_types)
        self.assertIn("develop", method_types)

    def test_get_problem_solution(self):
        """Test getting solution for common problems"""
        kb = KnowledgeBase()

        # Test exact match
        result = kb.get_problem_solution("command not found")
        self.assertIsNotNone(result)
        self.assertIn("cause", result)
        self.assertIn("solution", result)
        self.assertIn("prevention", result)

        # Test partial match
        result = kb.get_problem_solution("not found")
        self.assertIsNotNone(result)

        # Test another problem
        result = kb.get_problem_solution("read-only")
        self.assertIsNotNone(result)
        self.assertIn("configuration.nix", result["solution"])

    def test_get_problem_solution_not_found(self):
        """Test getting solution for non-existent problem"""
        kb = KnowledgeBase()

        result = kb.get_problem_solution("some weird problem that does not exist")
        self.assertIsNone(result)

    def test_get_best_practice(self):
        """Test getting best practices"""
        kb = KnowledgeBase()

        # Test package installation best practice
        result = kb.get_best_practice("package_installation")
        self.assertIsNotNone(result)
        self.assertIn("practice", result)
        self.assertIn("reason", result)
        self.assertIn("example", result)
        self.assertIn("declarative", result["practice"])

        # Test system updates best practice
        result = kb.get_best_practice("system_updates")
        self.assertIsNotNone(result)
        self.assertEqual(result["practice"], "Test configuration before switching")
        self.assertEqual(result["reason"], "Prevents breaking your system")

    def test_get_best_practice_not_found(self):
        """Test getting non-existent best practice"""
        kb = KnowledgeBase()

        result = kb.get_best_practice("nonexistent_topic")
        self.assertIsNone(result)

    def test_search_knowledge(self):
        """Test searching across all knowledge"""
        kb = KnowledgeBase()

        # Search for 'install' - should find install_package solution
        results = kb.search_knowledge("install")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

        # Check result structure
        for result in results:
            self.assertIn("type", result)
            self.assertIn(result["type"], ["solution", "problem"])

        # Search for 'declarative' - should find in solutions
        results = kb.search_knowledge("declarative")
        self.assertGreater(len(results), 0)

        # Search for 'configuration' - should find in multiple places
        results = kb.search_knowledge("configuration")
        self.assertGreater(len(results), 0)
        result_types = [r["type"] for r in results]
        # May find in solutions and/or problems

    def test_search_knowledge_no_results(self):
        """Test searching with no results"""
        kb = KnowledgeBase()

        results = kb.search_knowledge("xyzabc123notfound")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    def test_package_name_extraction_edge_cases(self):
        """Test package name extraction with various edge cases"""
        kb = KnowledgeBase()

        # Test with multiple spaces
        result = kb.get_solution("install_package", "install    firefox    please")
        self.assertEqual(result["package"], "firefox")

        # Test with mixed case
        result = kb.get_solution("install_package", "Install FIREFOX")
        self.assertEqual(result["package"], "firefox")

        # Test with no recognizable package
        result = kb.get_solution("install_package", "install the thing")
        self.assertIsNotNone(result)  # Should still return something

        # Test with multiple potential packages (should pick first valid one)
        result = kb.get_solution("install_package", "install git and vim")
        self.assertIn(result["package"], ["git", "vim"])

    def test_database_persistence(self):
        """Test that database persists between instances"""
        # Create first instance and add custom data
        kb1 = KnowledgeBase()
        conn = self._get_db_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO solutions (intent, category, solution, example, explanation, related)
            VALUES ('test_intent', 'test', 'test solution', 'test example', 'test explanation', 'test1,test2')
        """
        )
        conn.commit()
        conn.close()

        # Create second instance and verify data persists
        kb2 = KnowledgeBase()
        result = kb2.get_solution("test_intent", "test query")
        self.assertIsNotNone(result)
        self.assertEqual(result["solution"], "test solution")

    def test_database_creation_when_exists(self):
        """Test database initialization when database already exists"""
        # Create first instance
        kb1 = KnowledgeBase()

        # Verify database exists
        self.assertTrue(self.test_db_path.exists())

        # Create second instance (should not recreate database)
        kb2 = KnowledgeBase()

        # Verify it still has the initial data
        result = kb2.get_solution("install_package", "install firefox")
        self.assertIsNotNone(result)

    def test_sql_injection_prevention(self):
        """Test that SQL injection is prevented"""
        kb = KnowledgeBase()

        # Try SQL injection in get_solution
        malicious_intent = "'; DROP TABLE solutions; --"
        result = kb.get_solution(malicious_intent, "test")
        self.assertIsNone(result)  # Should return None, not crash

        # Verify tables still exist
        conn = self._get_db_connection()
        c = conn.cursor()
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='solutions'"
        )
        self.assertIsNotNone(c.fetchone())
        conn.close()

        # Try SQL injection in search
        malicious_query = "'; DROP TABLE problems; --"
        results = kb.search_knowledge(malicious_query)
        self.assertIsInstance(results, list)  # Should return empty list, not crash

        # Verify table still exists
        conn = self._get_db_connection()
        c = conn.cursor()
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems'"
        )
        self.assertIsNotNone(c.fetchone())
        conn.close()

class TestKnowledgeBaseIntegration(unittest.TestCase):
    """Integration tests for KnowledgeBase with real database operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.original_init = KnowledgeBase.__init__

        # Store test_dir reference for the init method
        test_dir = self.test_dir

        # Override __init__ to use test directory
        def test_init(kb_self):
            kb_self.base_dir = Path(test_dir)
            kb_self.db_path = kb_self.base_dir / "test_knowledge.db"
            kb_self._ensure_database()

        KnowledgeBase.__init__ = test_init

    def tearDown(self):
        """Clean up test fixtures"""
        KnowledgeBase.__init__ = self.original_init
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_workflow(self):
        """Test a complete workflow of operations"""
        kb = KnowledgeBase()

        # Search for install - should find results
        search_results = kb.search_knowledge("install")
        self.assertGreater(len(search_results), 0)

        # Get installation solution
        install_result = kb.get_solution("install_package", "I want to install firefox")
        self.assertIsNotNone(install_result)
        self.assertEqual(install_result["package"], "firefox")

        # Get installation methods
        methods = kb.get_installation_methods("firefox")
        self.assertEqual(len(methods), 5)

        # Get best practice
        practice = kb.get_best_practice("package_installation")
        self.assertIsNotNone(practice)

        # Simulate problem and get solution
        problem_solution = kb.get_problem_solution("command not found")
        self.assertIsNotNone(problem_solution)

    def test_concurrent_access(self):
        """Test that multiple instances can access the database"""
        kb1 = KnowledgeBase()
        kb2 = KnowledgeBase()

        # Both should be able to read
        result1 = kb1.get_solution("install_package", "install vim")
        result2 = kb2.get_solution("install_package", "install vim")

        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1["package"], result2["package"])

if __name__ == "__main__":
    unittest.main()
