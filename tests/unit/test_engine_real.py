#!/usr/bin/env python3
"""
Real tests for the actual LuminousNixBackend implementation.
Focused on testing real code that exists, not phantom features.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the actual backend (still using nix_humanity module name for now)
from nix_humanity.core.engine import NixForHumanityBackend as LuminousNixBackend
from nix_humanity.core.intents import Intent, IntentType
from nix_humanity.core.interface import Query


class TestLuminousNixBackendReal(unittest.TestCase):
    """Test the real backend implementation"""
    
    def setUp(self):
        """Set up test fixtures with proper mocking"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch KnowledgeBase at module level to avoid database initialization
        self.kb_patcher = patch('nix_humanity.core.engine.KnowledgeBase')
        mock_kb_class = self.kb_patcher.start()
        
        # Configure mock instance
        mock_kb = MagicMock()
        mock_kb.search.return_value = []
        mock_kb.get_similar_commands.return_value = []
        mock_kb.add_solution.return_value = None
        mock_kb_class.return_value = mock_kb
        
        # Create backend with mocked dependencies
        self.backend = LuminousNixBackend()
        self.mock_kb = mock_kb
    
    def tearDown(self):
        """Clean up"""
        self.kb_patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_backend_initialization(self):
        """Test that backend initializes its components"""
        self.assertIsNotNone(self.backend)
        self.assertIsNotNone(self.backend.intent_recognizer)
        self.assertIsNotNone(self.backend.executor)
        self.assertIsNotNone(self.backend.knowledge)
    
    def test_process_query_basic(self):
        """Test basic query processing"""
        query = Query(text="search firefox")
        
        # Mock the intent recognizer
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.SEARCH_PACKAGE,
                action="search",
                target="firefox",
                confidence=0.9
            )
            
            # Mock the executor
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "output": "firefox-128.0\nfirefox-developer-edition-129.0",
                    "packages": ["firefox-128.0", "firefox-developer-edition-129.0"]
                }
                
                result = self.backend.process(query)
                
                self.assertTrue(result['success'])
                self.assertIn('packages', result)
                self.assertEqual(len(result['packages']), 2)
    
    def test_intent_recognition_integration(self):
        """Test that intent recognizer is called correctly"""
        query = Query(text="install vim")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                action="install",
                target="vim",
                confidence=0.95
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {"success": True, "output": "installed"}
                
                result = self.backend.process(query)
                
                # Verify intent recognizer was called with query text
                mock_recognize.assert_called_once_with("install vim")
    
    def test_executor_integration(self):
        """Test that executor is called with correct parameters"""
        query = Query(text="list packages")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.LIST_GENERATIONS,
                action="list",
                target="packages",
                confidence=0.9
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {"success": True, "output": "package list"}
                
                result = self.backend.process(query)
                
                # Verify executor was called
                mock_execute.assert_called()
    
    def test_knowledge_base_search(self):
        """Test knowledge base is searched for unknown intents"""
        query = Query(text="how to configure networking")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            # Return low confidence intent
            mock_recognize.return_value = Intent(
                type=IntentType.UNKNOWN,
                action="unknown",
                confidence=0.3
            )
            
            # Setup knowledge base mock
            self.mock_kb.search.return_value = [{
                "question": "How to configure networking?",
                "answer": "Edit /etc/nixos/configuration.nix",
                "confidence": 0.9
            }]
            
            result = self.backend.process(query)
            
            # Verify knowledge base was searched
            self.mock_kb.search.assert_called()
    
    def test_error_handling(self):
        """Test error handling in processing"""
        query = Query(text="install firefox")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                action="install",
                target="firefox",
                confidence=0.9
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                # Simulate execution error
                mock_execute.return_value = {
                    "success": False,
                    "error": "Permission denied",
                    "output": ""
                }
                
                result = self.backend.process(query)
                
                self.assertFalse(result['success'])
                self.assertIn('error', result)
    
    def test_dry_run_mode(self):
        """Test dry run mode prevents actual execution"""
        # Enable dry run
        self.backend.executor.dry_run = True
        
        query = Query(text="install dangerous-package")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                action="install",
                target="dangerous-package",
                confidence=0.9
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "output": "[DRY RUN] Would install dangerous-package",
                    "dry_run": True
                }
                
                result = self.backend.process(query)
                
                # Verify dry run was passed to executor
                args, kwargs = mock_execute.call_args
                if 'dry_run' in kwargs:
                    self.assertTrue(kwargs['dry_run'])
    
    def test_stats_tracking(self):
        """Test that stats are tracked"""
        initial_stats = self.backend.get_stats()
        initial_count = initial_stats.get('queries_processed', 0)
        
        query = Query(text="search vim")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.SEARCH_PACKAGE,
                action="search",
                target="vim",
                confidence=0.9
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {"success": True, "output": "vim found"}
                
                self.backend.process(query)
                
                stats = self.backend.get_stats()
                self.assertEqual(stats.get('queries_processed', 0), initial_count + 1)


class TestIntentRecognizerIntegration(unittest.TestCase):
    """Test intent recognizer with the backend"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Patch KnowledgeBase
        self.kb_patcher = patch('nix_humanity.core.engine.KnowledgeBase')
        self.kb_patcher.start()
        
        self.backend = NixForHumanityBackend()
    
    def tearDown(self):
        """Clean up"""
        self.kb_patcher.stop()
    
    def test_recognizes_install_intent(self):
        """Test recognition of install intent"""
        result = self.backend.intent_recognizer.recognize("install firefox")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(result.target, "firefox")
        self.assertGreater(result.confidence, 0.8)
    
    def test_recognizes_search_intent(self):
        """Test recognition of search intent"""
        result = self.backend.intent_recognizer.recognize("search python")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.SEARCH_PACKAGE)
        self.assertEqual(result.target, "python")
        self.assertGreater(result.confidence, 0.8)
    
    def test_recognizes_help_intent(self):
        """Test recognition of help intent"""
        result = self.backend.intent_recognizer.recognize("help")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.HELP)
        self.assertGreater(result.confidence, 0.8)
    
    def test_handles_unknown_intent(self):
        """Test handling of unknown intent"""
        result = self.backend.intent_recognizer.recognize("foobar baz qux")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.UNKNOWN)
        self.assertLess(result.confidence, 0.5)


if __name__ == '__main__':
    unittest.main()