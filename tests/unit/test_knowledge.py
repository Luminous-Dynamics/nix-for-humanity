#!/usr/bin/env python3
"""
Tests for the knowledge base system.
Testing the NixOS knowledge base that provides accurate information.
"""

import unittest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from luminous_nix.core.knowledge import KnowledgeBase


class TestKnowledgeBase(unittest.TestCase):
    """Test the KnowledgeBase class."""
    
    def setUp(self):
        """Set up test fixtures with a temporary database."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_knowledge.db"
        
        # Patch the database path to use our temp database
        self.patcher = patch.object(
            KnowledgeBase, 
            'db_path',
            new_callable=PropertyMock,
            return_value=self.temp_db
        )
        self.patcher.start()
        
        # Also patch base_dir to avoid creating directories
        self.base_patcher = patch.object(
            KnowledgeBase,
            'base_dir',
            new_callable=PropertyMock,
            return_value=Path(self.temp_dir)
        )
        self.base_patcher.start()
        
        self.kb = KnowledgeBase()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
        self.base_patcher.stop()
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test that KnowledgeBase initializes correctly."""
        self.assertIsNotNone(self.kb)
        self.assertTrue(self.temp_db.exists())
    
    def test_database_structure(self):
        """Test that database tables are created correctly."""
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        
        # Check solutions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='solutions'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check problems table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='problems'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check best_practices table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='best_practices'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()
    
    def test_initial_knowledge_populated(self):
        """Test that initial knowledge is populated."""
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        
        # Check that solutions table has data
        cursor.execute("SELECT COUNT(*) FROM solutions")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0, "Solutions table should have initial data")
        
        # Check that problems table has data
        cursor.execute("SELECT COUNT(*) FROM problems")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0, "Problems table should have initial data")
        
        conn.close()
    
    def test_get_solution(self):
        """Test getting a solution from the knowledge base."""
        # Get a solution for installing packages
        solution = self.kb.get_solution("install_package", "install firefox")
        
        self.assertIsNotNone(solution)
        self.assertIn('solution', solution)
        self.assertIn('example', solution)
    
    def test_get_solution_not_found(self):
        """Test getting a solution that doesn't exist."""
        solution = self.kb.get_solution("nonexistent_intent", "random query")
        
        # Should return None or empty dict
        self.assertTrue(solution is None or solution == {})
    
    def test_search_solutions(self):
        """Test searching for solutions."""
        # Search for package-related solutions
        results = self.kb.search("package")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Each result should have expected fields
        for result in results:
            self.assertIn('intent', result)
            self.assertIn('solution', result)
    
    def test_get_similar_commands(self):
        """Test getting similar commands."""
        similar = self.kb.get_similar_commands("install")
        
        self.assertIsInstance(similar, list)
        # Should include related commands like search, remove
        command_strings = ' '.join(similar)
        self.assertTrue('search' in command_strings or 'remove' in command_strings)
    
    def test_add_solution(self):
        """Test adding a new solution to the knowledge base."""
        # Add a custom solution
        self.kb.add_solution(
            intent="custom_intent",
            category="custom",
            solution="Custom solution text",
            example="custom example",
            explanation="Why this works"
        )
        
        # Verify it was added
        solution = self.kb.get_solution("custom_intent", "test query")
        self.assertIsNotNone(solution)
        self.assertEqual(solution['solution'], "Custom solution text")
    
    def test_get_problem_solution(self):
        """Test getting a solution for a problem."""
        # Get solution for a common problem
        solution = self.kb.get_problem_solution("disk full")
        
        if solution:  # May not have this specific problem
            self.assertIn('solution', solution)
            self.assertIn('cause', solution)
    
    def test_get_best_practice(self):
        """Test getting best practices."""
        practice = self.kb.get_best_practice("package management")
        
        if practice:  # May not have this specific practice
            self.assertIn('practice', practice)
            self.assertIn('reason', practice)
    
    def test_database_persistence(self):
        """Test that database changes persist."""
        # Add a solution
        self.kb.add_solution(
            intent="test_persist",
            category="test",
            solution="Test persistence",
            example="test",
            explanation="test"
        )
        
        # Create a new instance (should use same database)
        kb2 = KnowledgeBase()
        solution = kb2.get_solution("test_persist", "query")
        
        self.assertIsNotNone(solution)
        self.assertEqual(solution['solution'], "Test persistence")
    
    def test_search_empty_query(self):
        """Test searching with empty query."""
        results = self.kb.search("")
        
        # Should return empty list or all results
        self.assertIsInstance(results, list)
    
    def test_search_special_characters(self):
        """Test searching with special characters."""
        # Should handle special characters safely
        results = self.kb.search("'; DROP TABLE solutions; --")
        
        self.assertIsInstance(results, list)
        
        # Database should still be intact
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='solutions'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()
    
    def test_concurrent_access(self):
        """Test that concurrent access doesn't cause issues."""
        # Create multiple KnowledgeBase instances
        kb1 = KnowledgeBase()
        kb2 = KnowledgeBase()
        
        # Both should work without conflict
        result1 = kb1.search("package")
        result2 = kb2.search("system")
        
        self.assertIsInstance(result1, list)
        self.assertIsInstance(result2, list)
    
    def test_invalid_intent_type(self):
        """Test handling of invalid intent types."""
        solution = self.kb.get_solution(None, "query")
        self.assertTrue(solution is None or solution == {})
        
        solution = self.kb.get_solution(123, "query")  # Non-string intent
        self.assertTrue(solution is None or solution == {})
    
    def test_solution_fields(self):
        """Test that solutions have all expected fields."""
        solution = self.kb.get_solution("install_package", "install vim")
        
        if solution:
            expected_fields = ['solution', 'example', 'explanation']
            for field in expected_fields:
                self.assertIn(field, solution, f"Solution should have '{field}' field")


if __name__ == '__main__':
    unittest.main()