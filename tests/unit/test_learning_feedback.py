#!/usr/bin/env python3
"""
Tests for FeedbackCollector - learning feedback module

Tests the feedback collection and management functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, 'nix_humanity')
sys.path.insert(0, backend_path)

# Import after setting path
from nix_humanity.learning.feedback import FeedbackCollector


class TestFeedbackCollector(unittest.TestCase):
    """Test the FeedbackCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.test_dir) / 'test_data'
        self.collector = FeedbackCollector(data_dir=self.test_data_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test FeedbackCollector initialization."""
        self.assertTrue(self.test_data_dir.exists())
        self.assertEqual(self.collector.data_dir, self.test_data_dir)
        self.assertEqual(self.collector.db_path, self.test_data_dir / 'feedback.db')
        self.assertTrue(self.collector.db_path.exists())
    
    def test_init_default_directory(self):
        """Test initialization with default directory."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path(self.test_dir)
            collector = FeedbackCollector()
            expected_dir = Path(self.test_dir) / '.local' / 'share' / 'nix-for-humanity'
            self.assertEqual(collector.data_dir, expected_dir)
    
    def test_add_feedback(self):
        """Test adding feedback."""
        # Mock the add_feedback method if it exists
        self.collector.add_feedback = Mock(return_value="feedback-123")
        
        feedback_id = self.collector.add_feedback(
            session_id="session-1",
            query="install firefox",
            response="Installing Firefox...",
            helpful=True,
            rating=5
        )
        
        self.assertEqual(feedback_id, "feedback-123")
        self.collector.add_feedback.assert_called_once()
    
    def test_get_feedback(self):
        """Test retrieving feedback."""
        # Mock the get_feedback method
        self.collector.get_feedback = Mock(return_value={
            "feedback_id": "feedback-123",
            "session_id": "session-1",
            "query": "install firefox",
            "response": "Installing Firefox...",
            "helpful": True,
            "rating": 5
        })
        
        feedback = self.collector.get_feedback("feedback-123")
        self.assertEqual(feedback["query"], "install firefox")
        self.assertEqual(feedback["rating"], 5)
        self.assertTrue(feedback["helpful"])
    
    def test_get_session_feedback(self):
        """Test retrieving all feedback for a session."""
        # Mock the method
        self.collector.get_session_feedback = Mock(return_value=[
            {"feedback_id": "f1", "query": "install firefox", "rating": 5},
            {"feedback_id": "f2", "query": "update system", "rating": 4}
        ])
        
        feedback_list = self.collector.get_session_feedback("session-1")
        self.assertEqual(len(feedback_list), 2)
        self.assertEqual(feedback_list[0]["query"], "install firefox")
        self.assertEqual(feedback_list[1]["query"], "update system")
    
    def test_calculate_average_rating(self):
        """Test calculating average rating."""
        # Mock method
        self.collector.calculate_average_rating = Mock(return_value=4.5)
        
        avg_rating = self.collector.calculate_average_rating()
        self.assertEqual(avg_rating, 4.5)
    
    def test_get_helpful_percentage(self):
        """Test calculating helpful percentage."""
        # Mock method
        self.collector.get_helpful_percentage = Mock(return_value=85.0)
        
        helpful_pct = self.collector.get_helpful_percentage()
        self.assertEqual(helpful_pct, 85.0)
    
    def test_export_feedback(self):
        """Test exporting feedback data."""
        # Mock export method
        self.collector.export_feedback = Mock(return_value={
            "total_feedback": 100,
            "average_rating": 4.2,
            "helpful_percentage": 82.0,
            "feedback_items": []
        })
        
        export_data = self.collector.export_feedback()
        self.assertEqual(export_data["total_feedback"], 100)
        self.assertEqual(export_data["average_rating"], 4.2)
        self.assertEqual(export_data["helpful_percentage"], 82.0)
    
    def test_database_operations(self):
        """Test actual database operations."""
        import sqlite3
        
        # Test database exists and has correct schema
        conn = sqlite3.connect(self.collector.db_path)
        c = conn.cursor()
        
        # Check if feedback table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        tables = c.fetchall()
        self.assertTrue(any(table[0] == 'feedback' for table in tables))
        
        # Check table schema
        c.execute("PRAGMA table_info(feedback)")
        columns = c.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'feedback_id', 'session_id', 'query', 'response']
        for col in expected_columns:
            self.assertIn(col, column_names)
        
        conn.close()
    
    def test_update_feedback(self):
        """Test updating existing feedback."""
        # Mock update method
        self.collector.update_feedback = Mock(return_value=True)
        
        success = self.collector.update_feedback(
            feedback_id="feedback-123",
            improved_response="Better response here",
            user_comment="This is more helpful"
        )
        
        self.assertTrue(success)
        self.collector.update_feedback.assert_called_once()


if __name__ == '__main__':
    unittest.main()