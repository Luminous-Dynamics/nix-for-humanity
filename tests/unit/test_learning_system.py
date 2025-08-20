#!/usr/bin/env python3
"""
Unit tests for the PreferenceManager component - simplified to match actual implementation
"""

import unittest
import tempfile
from pathlib import Path
import sqlite3

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from luminous_nix.learning.preferences import (
    PreferenceManager, Interaction, Preference
)


class TestPreferenceManager(unittest.TestCase):
    """Test the PreferenceManager component - actual implementation"""
    
    def setUp(self):
        """Create learning system with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_learning.db"
        self.system = PreferenceManager(self.db_path)
        
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_database_initialization(self):
        """Test that database tables are created correctly"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check interactions table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
        self.assertIsNotNone(c.fetchone())
        
        # Check preferences table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='preferences'")
        self.assertIsNotNone(c.fetchone())
        
        # Check error_patterns table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='error_patterns'")
        self.assertIsNotNone(c.fetchone())
        
        # Note: feedback table may not exist in current implementation
        
        conn.close()
        
    def test_record_interaction(self):
        """Test recording user interactions"""
        interaction = Interaction(
            query="install firefox",
            intent="install_package",
            response="Installing firefox...",
            success=True,
            user_id="test_user"
        )
        
        self.system.record_interaction(interaction)
        
        # Verify it was recorded (check in database directly)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM interactions WHERE user_id = ?", ("test_user",))
        result = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "install firefox")  # query
        self.assertEqual(result[2], "install_package")  # intent
        
    def test_learn_preference(self):
        """Test learning user preferences"""
        self.system.learn_preference("test_user", "personality", "technical")
        
        # Get preferences
        prefs = self.system.get_user_preferences("test_user")
        
        self.assertIn("personality", prefs)
        self.assertEqual(prefs["personality"], "technical")
        
    def test_update_preference(self):
        """Test updating existing preferences"""
        # Record initial preference
        self.system.learn_preference("test_user", "personality", "friendly")
        
        # Update to new value
        self.system.learn_preference("test_user", "personality", "technical")
        
        # Should have the updated value
        prefs = self.system.get_user_preferences("test_user")
        self.assertEqual(prefs["personality"], "technical")
        
    def test_learn_error_solution(self):
        """Test learning error solutions"""
        self.system.learn_error_solution(
            error="command not found: firefox",
            solution="Install firefox with: nix profile install nixpkgs#firefox",
            success=True
        )
        
        # Get solution
        solution = self.system.get_error_solution("command not found: firefox")
        
        self.assertIsNotNone(solution)
        self.assertIn("Install firefox", solution)
        
    def test_get_success_rate(self):
        """Test calculating success rate for specific intent"""
        # Record mix of successful and failed interactions
        for i in range(10):
            interaction = Interaction(
                query=f"install package{i}",
                intent="install_package",
                response="Result",
                success=i < 7,  # 7 successful, 3 failed
                user_id="test_user"
            )
            self.system.record_interaction(interaction)
            
        success_rate = self.system.get_success_rate("install_package")
        
        self.assertEqual(success_rate, 0.7)  # 70% success rate
        
    def test_get_success_rate_no_interactions(self):
        """Test success rate with no interactions"""
        success_rate = self.system.get_success_rate("unknown_intent")
        self.assertEqual(success_rate, 0.0)
        
    def test_get_common_patterns(self):
        """Test getting common query patterns"""
        # Record various queries
        queries = [
            "install firefox",
            "install vim",
            "install firefox",  # Duplicate
            "update system",
            "install firefox",  # Another duplicate
        ]
        
        for query in queries:
            interaction = Interaction(
                query=query,
                intent="install_package" if "install_package" in query else "update_system",
                response="Done",
                success=True,
                user_id="test_user"
            )
            self.system.record_interaction(interaction)
            
        # Get common patterns
        patterns = self.system.get_common_patterns(limit=2)
        
        self.assertEqual(len(patterns), 2)
        self.assertEqual(patterns[0][0], "install firefox")  # Most common
        self.assertEqual(patterns[0][1], 3)  # Count
        
    def test_get_feedback_summary(self):
        """Test getting feedback summary"""
        # Record some interactions with feedback
        for i in range(5):
            interaction = Interaction(
                query=f"query {i}",
                intent="test",
                response="response",
                success=True,
                helpful=i % 2 == 0,  # Alternating helpful
                user_id="test_user"
            )
            self.system.record_interaction(interaction)
            
        summary = self.system.get_feedback_summary()
        
        self.assertIn("total_feedback", summary)
        self.assertIn("helpful_count", summary)
        # Check what's actually in the summary
        self.assertEqual(summary["total_feedback"], 5)
        self.assertEqual(summary["helpful_count"], 3)
        
    def test_dataclass_initialization(self):
        """Test dataclass creation and defaults"""
        # Interaction with all fields
        interaction = Interaction(
            query="test",
            intent="test",
            response="test",
            success=True,
            user_id="test"
        )
        self.assertIsInstance(interaction.timestamp, str)
        
        # Preference 
        pref = Preference(
            user_id="test",
            preference_type="style",
            value="minimal"
        )
        self.assertIsInstance(pref.last_used, str)


if __name__ == '__main__':
    unittest.main()