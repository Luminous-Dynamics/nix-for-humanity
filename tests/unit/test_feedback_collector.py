#!/usr/bin/env python3
"""
Comprehensive tests for Feedback Collector

Tests all feedback collection functionality including:
- Database initialization
- Implicit feedback collection
- Explicit feedback collection
- Preference pair creation
- Statistics calculation
- Training data export
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import sqlite3
from pathlib import Path
import tempfile
import json
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

# Import the module we're testing
from feedback_collector import FeedbackCollector


class TestFeedbackCollector(unittest.TestCase):
    """Test the FeedbackCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test database
        self.temp_dir = tempfile.mkdtemp()
        self.test_base_dir = Path(self.temp_dir)
        self.test_data_dir = self.test_base_dir / "data" / "feedback"
        self.test_db_path = self.test_data_dir / "feedback.db"
        
        # Store test_base_dir in class variable for access in mock
        TestFeedbackCollector.test_base_dir = self.test_base_dir
        
        # Patch the __init__ method to set our test base_dir
        def mock_init(self):
            self.base_dir = TestFeedbackCollector.test_base_dir
            self.data_dir = self.base_dir / "data" / "feedback"
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = self.data_dir / "feedback.db"
            self.init_db()
        
        self.init_patch = patch.object(FeedbackCollector, '__init__', mock_init)
        self.init_patch.start()
        
        # Create collector instance
        self.collector = FeedbackCollector()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.init_patch.stop()
        
        # Clean up temp files
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        
        # Clean up directories
        for dir_path in [self.test_data_dir, self.test_base_dir / "data", self.test_base_dir]:
            if dir_path.exists() and dir_path.is_dir():
                try:
                    dir_path.rmdir()
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
    
    def test_init_creates_directories(self):
        """Test that initialization creates necessary directories."""
        self.assertTrue(self.test_data_dir.exists())
        self.assertTrue(self.test_data_dir.is_dir())
    
    def test_init_creates_database(self):
        """Test that initialization creates database with tables."""
        self.assertTrue(self.test_db_path.exists())
        
        # Check tables exist
        conn = sqlite3.connect(self.test_db_path)
        c = conn.cursor()
        
        # Check feedback table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        self.assertIsNotNone(c.fetchone())
        
        # Check preferences table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='preferences'")
        self.assertIsNotNone(c.fetchone())
        
        conn.close()
    
    def test_collect_implicit_feedback_quick_accept(self):
        """Test implicit feedback collection with quick acceptance."""
        feedback = self.collector.collect_implicit_feedback(
            query="install firefox",
            response="Use nix-env -iA nixos.firefox",
            interaction_time=1.5,
            user_action="execute"
        )
        
        self.assertTrue(feedback['helpful'])
        self.assertEqual(feedback['query'], "install firefox")
        self.assertEqual(feedback['response'], "Use nix-env -iA nixos.firefox")
        self.assertEqual(feedback['interaction_time'], 1.5)
        self.assertTrue(feedback['signals']['quick_accept'])
        self.assertTrue(feedback['signals']['execution'])
    
    def test_collect_implicit_feedback_hesitation(self):
        """Test implicit feedback collection with hesitation."""
        feedback = self.collector.collect_implicit_feedback(
            query="complex query",
            response="Complex response",
            interaction_time=15.0,
            user_action="none"
        )
        
        self.assertFalse(feedback['helpful'])
        self.assertTrue(feedback['signals']['hesitation'])
        self.assertFalse(feedback['signals']['quick_accept'])
    
    def test_collect_implicit_feedback_thoughtful_accept(self):
        """Test implicit feedback with thoughtful acceptance."""
        feedback = self.collector.collect_implicit_feedback(
            query="explain generations",
            response="Detailed explanation...",
            interaction_time=5.0,
            user_action="copy"
        )
        
        self.assertTrue(feedback['helpful'])
        self.assertTrue(feedback['signals']['thoughtful_accept'])
        self.assertTrue(feedback['signals']['copy_action'])
    
    def test_collect_explicit_feedback_helpful(self):
        """Test explicit feedback collection when helpful."""
        feedback = self.collector.collect_explicit_feedback(
            query="install vim",
            response="nix-env -iA nixos.vim",
            helpful=True
        )
        
        self.assertTrue(feedback['helpful'])
        self.assertEqual(feedback['query'], "install vim")
        self.assertEqual(feedback['response'], "nix-env -iA nixos.vim")
        self.assertIsNone(feedback.get('better_response'))
    
    def test_collect_explicit_feedback_with_better_response(self):
        """Test explicit feedback with better response creates preference pair."""
        with patch.object(self.collector, '_save_preference') as mock_save_pref:
            feedback = self.collector.collect_explicit_feedback(
                query="install package",
                response="Original response",
                helpful=False,
                better_response="Better response"
            )
            
            self.assertFalse(feedback['helpful'])
            self.assertEqual(feedback['better_response'], "Better response")
            
            # Check preference pair was saved
            mock_save_pref.assert_called_once_with(
                "install package",
                chosen="Better response",
                rejected="Original response"
            )
    
    def test_save_feedback_to_database(self):
        """Test that feedback is saved to database."""
        # Collect feedback
        self.collector.collect_explicit_feedback(
            query="test query",
            response="test response",
            helpful=True
        )
        
        # Check database
        conn = sqlite3.connect(self.test_db_path)
        c = conn.cursor()
        c.execute("SELECT query, response, helpful FROM feedback")
        result = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "test query")
        self.assertEqual(result[1], "test response")
        self.assertEqual(result[2], 1)  # SQLite stores boolean as 0/1
    
    def test_save_preference_to_database(self):
        """Test that preference pairs are saved to database."""
        self.collector._save_preference(
            context="install firefox",
            chosen="Declarative method explanation",
            rejected="Simple command",
            reason="User prefers detailed explanations"
        )
        
        # Check database
        conn = sqlite3.connect(self.test_db_path)
        c = conn.cursor()
        c.execute("SELECT context, chosen, rejected, reason FROM preferences")
        result = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "install firefox")
        self.assertEqual(result[1], "Declarative method explanation")
        self.assertEqual(result[2], "Simple command")
        self.assertEqual(result[3], "User prefers detailed explanations")
    
    def test_get_feedback_stats_empty(self):
        """Test getting stats with no feedback."""
        stats = self.collector.get_feedback_stats()
        
        self.assertEqual(stats['total_feedback'], 0)
        self.assertEqual(stats['helpful_percentage'], 0)
        self.assertEqual(stats['preference_pairs'], 0)
        self.assertEqual(len(stats['recent_feedback']), 0)
    
    def test_get_feedback_stats_with_data(self):
        """Test getting stats with feedback data."""
        # Add some feedback
        self.collector.collect_explicit_feedback("q1", "r1", True)
        self.collector.collect_explicit_feedback("q2", "r2", True)
        self.collector.collect_explicit_feedback("q3", "r3", False)
        self.collector.collect_explicit_feedback("q4", "r4", False, "better")
        
        stats = self.collector.get_feedback_stats()
        
        self.assertEqual(stats['total_feedback'], 4)
        self.assertEqual(stats['helpful_percentage'], 50.0)
        self.assertEqual(stats['preference_pairs'], 1)  # One from q4
        self.assertLessEqual(len(stats['recent_feedback']), 5)
    
    def test_export_for_training(self):
        """Test exporting feedback for training."""
        # Add preference pairs
        self.collector._save_preference(
            "How to install firefox?",
            "I'll help you install Firefox using declarative configuration...",
            "Just run: nix-env -iA nixos.firefox"
        )
        self.collector._save_preference(
            "Update system",
            "To update NixOS, first update channels then rebuild...",
            "sudo nixos-rebuild switch"
        )
        
        # Export
        output_path = self.collector.export_for_training()
        
        self.assertTrue(output_path.exists())
        
        # Check exported data
        with open(output_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        # Check first example
        example1 = json.loads(lines[0])
        self.assertEqual(example1['prompt'], "How to install firefox?")
        self.assertIn("declarative", example1['chosen'])
        self.assertIn("nix-env", example1['rejected'])
    
    def test_export_for_training_custom_path(self):
        """Test exporting to custom path."""
        custom_path = Path(self.temp_dir) / "custom_export.jsonl"
        
        # Add a preference
        self.collector._save_preference("test", "chosen", "rejected")
        
        # Export to custom path
        result_path = self.collector.export_for_training(custom_path)
        
        self.assertEqual(result_path, custom_path)
        self.assertTrue(custom_path.exists())
    
    def test_implicit_feedback_signals(self):
        """Test all implicit feedback signal scenarios."""
        scenarios = [
            # (interaction_time, user_action, expected_helpful)
            (0.5, "execute", True),      # Quick execute
            (1.9, "copy", True),          # Quick copy
            (3.0, "execute", True),       # Thoughtful execute
            (8.0, "copy", True),          # Thoughtful copy
            (12.0, "none", False),        # Hesitation
            (5.0, "retry", False),        # Retry indicates not helpful
        ]
        
        for interaction_time, user_action, expected_helpful in scenarios:
            with self.subTest(time=interaction_time, action=user_action):
                feedback = self.collector.collect_implicit_feedback(
                    "test", "response", interaction_time, user_action
                )
                self.assertEqual(
                    feedback['helpful'], 
                    expected_helpful,
                    f"Expected helpful={expected_helpful} for time={interaction_time}, action={user_action}"
                )
    
    def test_metadata_storage(self):
        """Test that metadata is properly stored."""
        feedback = self.collector.collect_implicit_feedback(
            "test query",
            "test response",
            3.5,
            "copy"
        )
        
        # Check database for metadata
        conn = sqlite3.connect(self.test_db_path)
        c = conn.cursor()
        c.execute("SELECT metadata FROM feedback WHERE query = 'test query'")
        result = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        metadata = json.loads(result[0])
        self.assertIn('thoughtful_accept', metadata)
        self.assertIn('copy_action', metadata)


if __name__ == '__main__':
    unittest.main()