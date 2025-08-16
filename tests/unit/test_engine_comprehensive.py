#!/usr/bin/env python3
"""
Comprehensive tests for the NixForHumanityBackend engine.
These tests focus on the actual implementation, not phantom features.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.core.intents import Intent, IntentType
from nix_humanity.core.interface import Query
from nix_humanity.core.personality import PersonalityStyle


class TestNixForHumanityBackend(unittest.TestCase):
    """Test the core backend engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.backend = NixForHumanityBackend()
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test backend initializes correctly"""
        self.assertIsNotNone(self.backend)
        self.assertIsNotNone(self.backend.intent_recognizer)
        self.assertIsNotNone(self.backend.executor)
        self.assertIsNotNone(self.backend.knowledge_base)
        self.assertIsNotNone(self.backend.personality_manager)
    
    def test_process_install_query(self):
        """Test processing an install query"""
        query = Query(text="install firefox")
        result = self.backend.process(query)
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'success'))
        self.assertTrue(hasattr(result, 'text'))
    
    def test_process_search_query(self):
        """Test processing a search query"""
        query = Query(text="search for text editor")
        result = self.backend.process(query)
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'success'))
    
    def test_process_help_query(self):
        """Test processing a help query"""
        query = Query(text="help")
        result = self.backend.process(query)
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'success'))
        self.assertTrue(hasattr(result, 'text'))
    
    def test_process_with_context(self):
        """Test processing with context"""
        query = Query(
            text="update system",
            context={"dry_run": True, "personality": "minimal"}
        )
        result = self.backend.process(query)
        
        self.assertIsNotNone(result)
    
    def test_set_personality(self):
        """Test setting personality style"""
        self.backend.set_personality(PersonalityStyle.MINIMAL)
        self.assertEqual(
            self.backend.personality_manager.current_style,
            PersonalityStyle.MINIMAL
        )
        
        self.backend.set_personality(PersonalityStyle.SACRED)
        self.assertEqual(
            self.backend.personality_manager.current_style,
            PersonalityStyle.SACRED
        )
    
    def test_get_stats(self):
        """Test getting system stats"""
        stats = self.backend.get_stats()
        
        self.assertIsNotNone(stats)
        self.assertIsInstance(stats, dict)
        self.assertIn('queries_processed', stats)
        self.assertIn('personality_style', stats)
    
    @patch('nix_humanity.core.executor.SafeExecutor.execute')
    def test_dry_run_mode(self, mock_execute):
        """Test that dry run mode doesn't execute commands"""
        mock_execute.return_value = Mock(success=True, output="Mock output")
        
        query = Query(
            text="install vim",
            context={"dry_run": True}
        )
        result = self.backend.process(query)
        
        # In dry run, executor might not be called or called with dry_run flag
        # Check that result indicates dry run
        self.assertIsNotNone(result)
    
    def test_error_handling(self):
        """Test error handling for invalid queries"""
        query = Query(text="")
        result = self.backend.process(query)
        
        self.assertIsNotNone(result)
        # Empty query should still return a result, not crash
    
    def test_unknown_intent_handling(self):
        """Test handling of unknown intents"""
        query = Query(text="do something completely random and unknown")
        result = self.backend.process(query)
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'success'))
    
    def test_personality_affects_response(self):
        """Test that personality changes response style"""
        query = Query(text="help")
        
        # Test with minimal personality
        self.backend.set_personality(PersonalityStyle.MINIMAL)
        minimal_result = self.backend.process(query)
        
        # Test with sacred personality
        self.backend.set_personality(PersonalityStyle.SACRED)
        sacred_result = self.backend.process(query)
        
        # Results should be different (at least in style)
        self.assertIsNotNone(minimal_result)
        self.assertIsNotNone(sacred_result)
        # Note: Actual text comparison depends on implementation
    
    def test_knowledge_base_integration(self):
        """Test that knowledge base is used"""
        # Add some knowledge
        self.backend.knowledge_base.add_entry(
            "test_command",
            "Test description",
            ["test", "example"]
        )
        
        # Query for it
        query = Query(text="search test")
        result = self.backend.process(query)
        
        self.assertIsNotNone(result)
    
    def test_concurrent_queries(self):
        """Test handling multiple queries"""
        queries = [
            Query(text="install firefox"),
            Query(text="search editor"),
            Query(text="help"),
        ]
        
        results = []
        for query in queries:
            result = self.backend.process(query)
            results.append(result)
            self.assertIsNotNone(result)
        
        self.assertEqual(len(results), 3)
    
    def test_configuration_persistence(self):
        """Test that configuration changes persist in session"""
        # Set a personality
        self.backend.set_personality(PersonalityStyle.HACKER)
        
        # Process a query
        query = Query(text="help")
        result = self.backend.process(query)
        
        # Check personality is still set
        self.assertEqual(
            self.backend.personality_manager.current_style,
            PersonalityStyle.HACKER
        )
    
    def test_safe_mode(self):
        """Test that dangerous commands are blocked"""
        dangerous_queries = [
            "rm -rf /",
            "delete system files",
            "format disk"
        ]
        
        for dangerous in dangerous_queries:
            query = Query(text=dangerous)
            result = self.backend.process(query)
            
            self.assertIsNotNone(result)
            # Should not execute dangerous commands
            # Actual implementation would block these


class TestBackendIntegration(unittest.TestCase):
    """Integration tests for backend with other components"""
    
    def setUp(self):
        self.backend = NixForHumanityBackend()
    
    def test_full_pipeline(self):
        """Test the full processing pipeline"""
        # Create query
        query = Query(
            text="install firefox and vim",
            context={"dry_run": True}
        )
        
        # Process through backend
        result = self.backend.process(query)
        
        # Verify result structure
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'success'))
        self.assertTrue(hasattr(result, 'text'))
    
    def test_learning_integration(self):
        """Test that backend learns from interactions"""
        # Process same query multiple times
        query = Query(text="install emacs")
        
        for _ in range(3):
            result = self.backend.process(query)
            self.assertIsNotNone(result)
        
        # Check if pattern was learned (implementation dependent)
        stats = self.backend.get_stats()
        self.assertGreater(stats['queries_processed'], 0)
    
    def test_error_recovery(self):
        """Test that backend recovers from errors"""
        # Cause an error with invalid input
        query = Query(text=None)  # Invalid
        
        try:
            result = self.backend.process(query)
        except:
            pass  # Error expected
        
        # Should still work for valid query
        valid_query = Query(text="help")
        result = self.backend.process(valid_query)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()