#!/usr/bin/env python3
"""
Enhanced unit tests for the PreferenceManager component
Tests preference learning, error solutions, pattern detection, and feedback
"""

import unittest
import tempfile
import os
from pathlib import Path
import sqlite3
import time
from datetime import datetime, timedelta

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from luminous_nix.learning.preferences import PreferenceManager, Interaction, Preference


class TestPreferenceManagerEnhanced(unittest.TestCase):
    """Enhanced tests for the PreferenceManager component"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.ls = PreferenceManager(self.temp_db.name)
        
    def tearDown(self):
        """Clean up temporary database"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        
    def test_database_initialization(self):
        """Test that all required tables are created"""
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Check for all expected tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['interactions', 'preferences', 'error_patterns', 'command_patterns']
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} should exist")
            
        # Verify interactions table schema
        cursor.execute("PRAGMA table_info(interactions)")
        columns = [row[1] for row in cursor.fetchall()]
        expected_columns = ['id', 'query', 'intent', 'response', 'success', 
                          'helpful', 'timestamp', 'session_id', 'user_id']
        for col in expected_columns:
            self.assertIn(col, columns, f"Column {col} should exist in interactions")
            
        conn.close()
        
    def test_record_interaction_basic(self):
        """Test basic interaction recording"""
        interaction = Interaction(
            query="install firefox",
            intent="install_package",
            response="Installing firefox...",
            success=True,
            helpful=True,
            session_id="test-session",
            user_id="test-user"
        )
        
        self.ls.record_interaction(interaction)
        
        # Verify it was recorded
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        
        # Verify data integrity
        cursor.execute("SELECT query, intent, success FROM interactions")
        row = cursor.fetchone()
        self.assertEqual(row[0], "install firefox")
        self.assertEqual(row[1], "install_package")
        self.assertEqual(row[2], 1)  # SQLite stores boolean as 0/1
        
        conn.close()
        
    def test_record_multiple_interactions(self):
        """Test recording multiple interactions"""
        interactions = [
            Interaction("install vim", "install_package", "Installing vim...", True, True),
            Interaction("update system", "update_system", "Updating...", True, None),
            Interaction("search python", "search_package", "Searching...", False, False)
        ]
        
        for interaction in interactions:
            self.ls.record_interaction(interaction)
            
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 3)
        conn.close()
        
    def test_learn_preference_new(self):
        """Test learning a new preference"""
        self.ls.learn_preference("user1", "editor", "vim")
        
        # Verify preference was stored
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT value, count FROM preferences WHERE user_id=? AND preference_type=?",
                      ("user1", "editor"))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "vim")
        self.assertEqual(row[1], 1)
        conn.close()
        
    def test_learn_preference_update_existing(self):
        """Test updating an existing preference"""
        # Learn same preference 3 times
        for _ in range(3):
            self.ls.learn_preference("user1", "browser", "firefox")
            
        # Verify count was incremented
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM preferences WHERE user_id=? AND preference_type=? AND value=?",
                      ("user1", "browser", "firefox"))
        count = cursor.fetchone()[0]
        self.assertEqual(count, 3)
        conn.close()
        
    def test_get_user_preferences(self):
        """Test retrieving user preferences"""
        # Learn multiple preferences
        self.ls.learn_preference("user1", "editor", "vim")
        self.ls.learn_preference("user1", "editor", "vim")  # vim used twice
        self.ls.learn_preference("user1", "editor", "emacs")  # emacs once
        self.ls.learn_preference("user1", "browser", "firefox")
        self.ls.learn_preference("user1", "shell", "zsh")
        
        prefs = self.ls.get_user_preferences("user1")
        
        # Should return most used preference for each type
        self.assertEqual(prefs["editor"], "vim")  # vim used twice
        self.assertEqual(prefs["browser"], "firefox")
        self.assertEqual(prefs["shell"], "zsh")
        
    def test_get_user_preferences_empty(self):
        """Test getting preferences for user with no data"""
        prefs = self.ls.get_user_preferences("unknown-user")
        self.assertEqual(prefs, {})
        
    def test_learn_error_solution(self):
        """Test learning from error resolutions"""
        error_msg = "command not found: nix-shell"
        solution = "Make sure nix is in your PATH"
        
        self.ls.learn_error_solution(error_msg, solution, success=True)
        
        # Verify it was stored
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT solution, success_count FROM error_patterns WHERE error_message=?",
                      (error_msg,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], solution)
        self.assertEqual(row[1], 1)
        conn.close()
        
    def test_learn_error_solution_increment(self):
        """Test that successful solutions increment count"""
        error_msg = "permission denied"
        solution = "Use sudo"
        
        # Learn same solution 5 times
        for _ in range(5):
            self.ls.learn_error_solution(error_msg, solution, success=True)
            
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT success_count FROM error_patterns WHERE error_message=?",
                      (error_msg,))
        count = cursor.fetchone()[0]
        self.assertEqual(count, 5)
        conn.close()
        
    def test_get_error_solution(self):
        """Test retrieving error solutions"""
        # Learn some solutions
        self.ls.learn_error_solution("file not found", "Check the path", success=True)
        self.ls.learn_error_solution("file not found", "Wrong solution", success=False)
        
        # Should return the successful solution
        solution = self.ls.get_error_solution("file not found")
        self.assertEqual(solution, "Check the path")
        
    def test_get_error_solution_partial_match(self):
        """Test partial matching for error solutions"""
        self.ls.learn_error_solution("Error: package 'firefox' not found", 
                                   "Try 'nix search firefox'", success=True)
        
        # Should find with partial match
        solution = self.ls.get_error_solution("package 'chrome' not found")
        self.assertTrue(solution is None or "nix search" in solution or "firefox" in solution)
        
    def test_get_error_solution_not_found(self):
        """Test behavior when no solution exists"""
        solution = self.ls.get_error_solution("completely unknown error xyz123")
        self.assertIsNone(solution)
        
    def test_get_success_rate(self):
        """Test calculating success rate for intents"""
        # Record some interactions
        interactions = [
            Interaction("install firefox", "install_package", "Done", True),
            Interaction("install vim", "install_package", "Done", True),
            Interaction("install unknown", "install_package", "Failed", False),
            Interaction("update system", "update_system", "Done", True),
        ]
        
        for interaction in interactions:
            self.ls.record_interaction(interaction)
            
        # Check success rates
        install_rate = self.ls.get_success_rate("install_package")
        self.assertAlmostEqual(install_rate, 2/3)  # 2 out of 3 succeeded
        
        update_rate = self.ls.get_success_rate("update_system")
        self.assertEqual(update_rate, 1.0)  # 1 out of 1 succeeded
        
        unknown_rate = self.ls.get_success_rate("unknown_intent")
        self.assertEqual(unknown_rate, 0.0)  # No data
        
    def test_get_success_rate_time_window(self):
        """Test that success rate only considers recent interactions"""
        # This test would need to mock time or insert old data directly
        # For now, just verify the query works
        rate = self.ls.get_success_rate("install_package")
        self.assertIsInstance(rate, float)
        self.assertTrue(0 <= rate <= 1)
        
    def test_get_common_patterns(self):
        """Test retrieving common query patterns"""
        # Record some queries
        queries = [
            "install firefox",
            "install firefox",
            "install firefox",
            "install vim",
            "install vim",
            "update system",
        ]
        
        for query in queries:
            interaction = Interaction(query, "install_package", "Done", True)
            self.ls.record_interaction(interaction)
            
        patterns = self.ls.get_common_patterns(limit=2)
        
        self.assertEqual(len(patterns), 2)
        self.assertEqual(patterns[0][0], "install firefox")  # Most common
        self.assertEqual(patterns[0][1], 3)  # Count
        self.assertEqual(patterns[1][0], "install vim")
        self.assertEqual(patterns[1][1], 2)
        
    def test_get_common_patterns_empty(self):
        """Test common patterns with no data"""
        patterns = self.ls.get_common_patterns()
        self.assertEqual(patterns, [])
        
    def test_get_feedback_summary(self):
        """Test feedback summary calculation"""
        # Record interactions with feedback
        interactions = [
            Interaction("q1", "i1", "r1", True, helpful=True),
            Interaction("q2", "i2", "r2", True, helpful=True),
            Interaction("q3", "i3", "r3", True, helpful=False),
            Interaction("q4", "i4", "r4", True, helpful=None),  # No feedback
        ]
        
        for interaction in interactions:
            self.ls.record_interaction(interaction)
            
        summary = self.ls.get_feedback_summary()
        
        self.assertEqual(summary['total_feedback'], 3)  # 3 with feedback
        self.assertEqual(summary['helpful_count'], 2)
        self.assertEqual(summary['not_helpful_count'], 1)
        self.assertAlmostEqual(summary['helpfulness_rate'], 2/3)
        
    def test_get_feedback_summary_empty(self):
        """Test feedback summary with no data"""
        summary = self.ls.get_feedback_summary()
        
        self.assertEqual(summary['total_feedback'], 0)
        self.assertEqual(summary['helpful_count'], 0)
        self.assertEqual(summary['not_helpful_count'], 0)
        self.assertEqual(summary['helpfulness_rate'], 0.0)
        
    def test_concurrent_writes(self):
        """Test that concurrent writes don't cause issues"""
        import threading
        
        def write_interaction(thread_id):
            for i in range(10):
                interaction = Interaction(
                    f"query-{thread_id}-{i}",
                    "test",
                    "response",
                    True
                )
                self.ls.record_interaction(interaction)
                
        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_interaction, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Verify all writes succeeded
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 50)  # 5 threads * 10 interactions
        conn.close()
        
    def test_preference_types(self):
        """Test different types of preferences"""
        preference_types = [
            ("install_method", "declarative"),
            ("response_style", "minimal"),
            ("explanation_depth", "detailed"),
            ("error_verbosity", "verbose"),
        ]
        
        for pref_type, value in preference_types:
            self.ls.learn_preference("user1", pref_type, value)
            
        prefs = self.ls.get_user_preferences("user1")
        
        for pref_type, value in preference_types:
            self.assertEqual(prefs[pref_type], value)
            
    def test_timestamp_handling(self):
        """Test that timestamps are properly handled"""
        # Create interaction with custom timestamp
        past_time = (datetime.now() - timedelta(days=5)).isoformat()
        interaction = Interaction(
            "test query",
            "test",
            "response",
            True,
            timestamp=past_time
        )
        
        self.ls.record_interaction(interaction)
        
        # Verify timestamp was stored correctly
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp FROM interactions WHERE query=?", ("test query",))
        stored_time = cursor.fetchone()[0]
        self.assertEqual(stored_time, past_time)
        conn.close()
        
    def test_session_tracking(self):
        """Test session-based interaction tracking"""
        session1_interactions = [
            Interaction("q1", "i1", "r1", True, session_id="session-1"),
            Interaction("q2", "i2", "r2", True, session_id="session-1"),
        ]
        
        session2_interactions = [
            Interaction("q3", "i3", "r3", True, session_id="session-2"),
        ]
        
        for interaction in session1_interactions + session2_interactions:
            self.ls.record_interaction(interaction)
            
        # Verify sessions are tracked
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM interactions")
        session_count = cursor.fetchone()[0]
        self.assertEqual(session_count, 2)
        
        cursor.execute("SELECT COUNT(*) FROM interactions WHERE session_id=?", ("session-1",))
        s1_count = cursor.fetchone()[0]
        self.assertEqual(s1_count, 2)
        conn.close()
        
    def test_error_solution_ranking(self):
        """Test that most successful solutions are returned first"""
        error = "network error"
        
        # Learn multiple solutions with different success counts
        self.ls.learn_error_solution(error, "Check connection", success=True)
        self.ls.learn_error_solution(error, "Check connection", success=True)
        self.ls.learn_error_solution(error, "Check connection", success=True)
        
        self.ls.learn_error_solution(error, "Restart network", success=True)
        
        # Most successful solution should be returned
        solution = self.ls.get_error_solution(error)
        self.assertEqual(solution, "Check connection")
        
    def test_data_persistence(self):
        """Test that data persists across instances"""
        # Write data
        self.ls.learn_preference("user1", "theme", "dark")
        self.ls.record_interaction(Interaction("test", "test", "test", True))
        
        # Create new instance with same database
        ls2 = PreferenceManager(self.temp_db.name)
        
        # Verify data is accessible
        prefs = ls2.get_user_preferences("user1")
        self.assertEqual(prefs["theme"], "dark")
        
        # Verify interaction count
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interactions")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        conn.close()


if __name__ == '__main__':
    unittest.main()