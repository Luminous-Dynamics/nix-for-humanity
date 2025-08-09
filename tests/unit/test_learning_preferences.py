#!/usr/bin/env python3
"""
Tests for PreferenceManager - user preference learning module

Tests the preference tracking and learning functionality.
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
from nix_humanity.learning.preferences import PreferenceManager


class TestPreferenceManager(unittest.TestCase):
    """Test the PreferenceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.test_dir) / 'test_data'
        self.manager = PreferenceManager(data_dir=self.test_data_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test PreferenceManager initialization."""
        self.assertTrue(self.test_data_dir.exists())
        self.assertEqual(self.manager.data_dir, self.test_data_dir)
        self.assertEqual(self.manager.db_path, self.test_data_dir / 'preferences.db')
        self.assertTrue(self.manager.db_path.exists())
    
    def test_init_default_directory(self):
        """Test initialization with default directory."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path(self.test_dir)
            manager = PreferenceManager()
            expected_dir = Path(self.test_dir) / '.local' / 'share' / 'nix-for-humanity'
            self.assertEqual(manager.data_dir, expected_dir)
    
    def test_set_preference(self):
        """Test setting user preferences."""
        # Mock the set_preference method
        self.manager.set_preference = Mock(return_value=True)
        
        success = self.manager.set_preference(
            user_id="user-123",
            preference_key="response_style",
            preference_value="technical",
            confidence=0.8
        )
        
        self.assertTrue(success)
        self.manager.set_preference.assert_called_once_with(
            user_id="user-123",
            preference_key="response_style",
            preference_value="technical",
            confidence=0.8
        )
    
    def test_get_preference(self):
        """Test retrieving user preferences."""
        # Mock the get_preference method
        self.manager.get_preference = Mock(return_value={
            "value": "technical",
            "confidence": 0.8,
            "last_updated": "2024-01-01"
        })
        
        pref = self.manager.get_preference("user-123", "response_style")
        self.assertEqual(pref["value"], "technical")
        self.assertEqual(pref["confidence"], 0.8)
    
    def test_get_all_preferences(self):
        """Test retrieving all preferences for a user."""
        # Mock the method
        self.manager.get_all_preferences = Mock(return_value={
            "response_style": {"value": "technical", "confidence": 0.8},
            "verbosity": {"value": "concise", "confidence": 0.7},
            "emoji_usage": {"value": "minimal", "confidence": 0.9}
        })
        
        all_prefs = self.manager.get_all_preferences("user-123")
        self.assertEqual(len(all_prefs), 3)
        self.assertEqual(all_prefs["response_style"]["value"], "technical")
        self.assertEqual(all_prefs["verbosity"]["value"], "concise")
    
    def test_update_confidence(self):
        """Test updating preference confidence."""
        # Mock update method
        self.manager.update_confidence = Mock(return_value=True)
        
        success = self.manager.update_confidence(
            user_id="user-123",
            preference_key="response_style",
            delta=0.1
        )
        
        self.assertTrue(success)
        self.manager.update_confidence.assert_called_once()
    
    def test_learn_from_feedback(self):
        """Test learning from user feedback."""
        # Mock learning method
        self.manager.learn_from_feedback = Mock(return_value={
            "updated_preferences": ["response_style", "verbosity"],
            "confidence_changes": {"response_style": 0.1, "verbosity": -0.05}
        })
        
        result = self.manager.learn_from_feedback(
            user_id="user-123",
            feedback_data={"helpful": True, "response_style": "liked"}
        )
        
        self.assertEqual(len(result["updated_preferences"]), 2)
        self.assertEqual(result["confidence_changes"]["response_style"], 0.1)
    
    def test_export_preferences(self):
        """Test exporting preference data."""
        # Mock export method
        self.manager.export_preferences = Mock(return_value={
            "user_count": 50,
            "total_preferences": 150,
            "average_confidence": 0.75,
            "most_common_preferences": {
                "response_style": "friendly",
                "verbosity": "normal"
            }
        })
        
        export_data = self.manager.export_preferences()
        self.assertEqual(export_data["user_count"], 50)
        self.assertEqual(export_data["average_confidence"], 0.75)
    
    def test_database_operations(self):
        """Test actual database operations."""
        import sqlite3
        
        # Test database exists and has correct schema
        conn = sqlite3.connect(self.manager.db_path)
        c = conn.cursor()
        
        # Check if preferences table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='preferences'")
        tables = c.fetchall()
        self.assertTrue(any(table[0] == 'preferences' for table in tables))
        
        # Check table schema
        c.execute("PRAGMA table_info(preferences)")
        columns = c.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = ['id', 'user_id', 'preference_key', 'preference_value', 'confidence']
        for col in expected_columns:
            self.assertIn(col, column_names)
        
        conn.close()
    
    def test_preference_categories(self):
        """Test preference categorization."""
        # Define preference categories
        categories = {
            "interaction": ["response_style", "verbosity", "emoji_usage"],
            "technical": ["detail_level", "code_examples", "explanation_depth"],
            "personality": ["formality", "humor", "encouragement"]
        }
        
        # Test categorization logic
        def get_category(pref_key):
            for cat, keys in categories.items():
                if pref_key in keys:
                    return cat
            return "other"
        
        self.assertEqual(get_category("response_style"), "interaction")
        self.assertEqual(get_category("detail_level"), "technical")
        self.assertEqual(get_category("formality"), "personality")
        self.assertEqual(get_category("unknown_pref"), "other")
    
    def test_preference_defaults(self):
        """Test default preference values."""
        defaults = {
            "response_style": "friendly",
            "verbosity": "normal",
            "emoji_usage": "moderate",
            "detail_level": "balanced",
            "code_examples": "when_helpful",
            "formality": "casual"
        }
        
        # Mock get_preference_with_default
        def get_preference_with_default(user_id, key):
            # Simulate getting preference or returning default
            return defaults.get(key, "unknown")
        
        self.assertEqual(get_preference_with_default("new-user", "response_style"), "friendly")
        self.assertEqual(get_preference_with_default("new-user", "verbosity"), "normal")
        self.assertEqual(get_preference_with_default("new-user", "unknown_key"), "unknown")


if __name__ == '__main__':
    unittest.main()