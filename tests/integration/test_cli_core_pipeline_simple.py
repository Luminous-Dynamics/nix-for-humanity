#!/usr/bin/env python3
"""
Simplified integration tests for the CLI → Core → Executor pipeline.
Tests the complete flow from user input to command execution.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nix_humanity.core.intents import (
    Request, Response, Context, Intent, IntentType
)
from nix_humanity.core.engine import NixForHumanityBackend as Engine
from nix_humanity.core.interface import Query

class TestSimplePipeline(unittest.TestCase):
    """Test basic pipeline functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        
        # Initialize engine with config
        config = {
            'knowledge_db_path': self.temp_db.name,
            'dry_run': True,
            'default_personality': 'friendly'
        }
        self.engine = Engine(config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
    
    def test_basic_install_flow(self):
        """Test basic install command flow."""
        # Create real Request object
        request = Request(
            query="install vim",
            context=Context(dry_run=True, execute=False)
        )
        response = self.engine.process(request)
        
        # Basic checks - response is a real Response object
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.text)
        self.assertTrue(len(response.text) > 0)
        
        # Check intent was recognized
        self.assertIsNotNone(response.intent)
        self.assertEqual(response.intent.type, IntentType.INSTALL)
        
    def test_help_flow(self):
        """Test help query flow."""
        request = Request(
            query="help",
            context=Context(dry_run=True)
        )
        response = self.engine.process(request)
        
        # Should get help text
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.text)
        self.assertIn('help', response.text.lower())
        
    def test_search_flow(self):
        """Test search query flow."""
        request = Request(
            query="search firefox",
            context=Context(dry_run=True)
        )
        response = self.engine.process(request)
        
        # Should recognize search intent
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent.type, IntentType.SEARCH)
        
    def test_personality_affects_response(self):
        """Test that personality changes response style."""
        # Test with minimal personality
        request1 = Request(
            query="install firefox",
            context=Context(
                dry_run=True,
                personality="minimal"
            )
        )
        response1 = self.engine.process(request1)
        
        # Test with friendly personality
        request2 = Request(
            query="install firefox",
            context=Context(
                dry_run=True,
                personality="friendly"
            )
        )
        response2 = self.engine.process(request2)
        
        # Both should be real Response objects
        self.assertIsInstance(response1, Response)
        self.assertIsInstance(response2, Response)
        
        # Responses should be different
        self.assertNotEqual(response1.text, response2.text)
        
        # Minimal should be shorter
        self.assertLess(len(response1.text), len(response2.text))

if __name__ == '__main__':
    unittest.main()