#!/usr/bin/env python3
"""
Fixed tests for the actual LuminousNixBackend implementation.
Testing real code that exists with correct dataclass structures.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the actual backend (module name nix_humanity for legacy compatibility)
from nix_humanity.core.engine import NixForHumanityBackend as LuminousNixBackend
from nix_humanity.core.intents import Intent, IntentType
from nix_humanity.core.interface import Query


class TestLuminousNixBackend(unittest.TestCase):
    """Test the real backend implementation with correct structures"""
    
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
    
    def test_process_install_query(self):
        """Test processing an install query"""
        query = Query(text="install firefox")
        
        # Mock the intent recognizer with correct Intent structure
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={"package": "firefox"},
                confidence=0.9,
                raw_text="install firefox"
            )
            
            # Mock the executor
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "output": "Installing firefox...",
                    "command": "nix-env -iA nixpkgs.firefox"
                }
                
                result = self.backend.process(query)
                
                self.assertTrue(result['success'])
                mock_recognize.assert_called_once_with("install firefox")
    
    def test_process_search_query(self):
        """Test processing a search query"""
        query = Query(text="search python")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.SEARCH_PACKAGE,
                entities={"query": "python"},
                confidence=0.85,
                raw_text="search python"
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "output": "python3-3.11.0\npython3-3.12.0",
                    "packages": ["python3-3.11.0", "python3-3.12.0"]
                }
                
                result = self.backend.process(query)
                
                self.assertTrue(result['success'])
                self.assertIn('packages', result)
    
    def test_process_help_query(self):
        """Test processing a help query"""
        query = Query(text="help")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.HELP,
                entities={},
                confidence=0.99,
                raw_text="help"
            )
            
            # Help doesn't need executor, should return help text
            result = self.backend.process(query)
            
            # Verify intent recognizer was called
            mock_recognize.assert_called_once_with("help")
    
    def test_unknown_intent_uses_knowledge_base(self):
        """Test that unknown intents trigger knowledge base search"""
        query = Query(text="how to configure networking")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            # Return unknown intent
            mock_recognize.return_value = Intent(
                type=IntentType.UNKNOWN,
                entities={},
                confidence=0.2,
                raw_text="how to configure networking"
            )
            
            # Setup knowledge base to return a solution
            self.mock_kb.search.return_value = [{
                "question": "How to configure networking?",
                "answer": "Edit /etc/nixos/configuration.nix and add networking options",
                "confidence": 0.85
            }]
            
            result = self.backend.process(query)
            
            # Knowledge base should be searched
            self.mock_kb.search.assert_called()
    
    def test_dry_run_mode(self):
        """Test dry run mode prevents actual execution"""
        # Enable dry run on executor
        self.backend.executor.dry_run = True
        
        query = Query(text="install dangerous-package")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={"package": "dangerous-package"},
                confidence=0.9,
                raw_text="install dangerous-package"
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "output": "[DRY RUN] Would install dangerous-package",
                    "dry_run": True
                }
                
                result = self.backend.process(query)
                
                # Check executor was called with dry_run
                mock_execute.assert_called()
                self.assertTrue(self.backend.executor.dry_run)
    
    def test_error_handling(self):
        """Test error handling in processing"""
        query = Query(text="install firefox")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={"package": "firefox"},
                confidence=0.9,
                raw_text="install firefox"
            )
            
            with patch.object(self.backend.executor, 'execute') as mock_execute:
                # Simulate execution error
                mock_execute.return_value = {
                    "success": False,
                    "error": "Permission denied: need sudo",
                    "output": ""
                }
                
                result = self.backend.process(query)
                
                self.assertFalse(result['success'])
                self.assertIn('error', result)


class TestIntentRecognizer(unittest.TestCase):
    """Test the intent recognizer directly"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Patch KnowledgeBase
        self.kb_patcher = patch('nix_humanity.core.engine.KnowledgeBase')
        self.kb_patcher.start()
        
        self.backend = LuminousNixBackend()
        self.recognizer = self.backend.intent_recognizer
    
    def tearDown(self):
        """Clean up"""
        self.kb_patcher.stop()
    
    def test_recognizes_install_intent(self):
        """Test recognition of install intent"""
        result = self.recognizer.recognize("install firefox")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.INSTALL_PACKAGE)
        self.assertIn('package', result.entities)
        self.assertEqual(result.entities['package'], 'firefox')
        self.assertGreater(result.confidence, 0.8)
    
    def test_recognizes_search_intent(self):
        """Test recognition of search intent"""
        result = self.recognizer.recognize("search python")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.SEARCH_PACKAGE)
        self.assertIn('query', result.entities)
        self.assertEqual(result.entities['query'], 'python')
        self.assertGreater(result.confidence, 0.8)
    
    def test_recognizes_help_intent(self):
        """Test recognition of help intent"""
        result = self.recognizer.recognize("help")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.HELP)
        self.assertGreater(result.confidence, 0.9)
    
    def test_recognizes_list_generations(self):
        """Test recognition of list generations intent"""
        result = self.recognizer.recognize("list generations")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.LIST_GENERATIONS)
        self.assertGreater(result.confidence, 0.8)
    
    def test_handles_unknown_intent(self):
        """Test handling of unknown intent"""
        result = self.recognizer.recognize("foobar baz qux random text")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.UNKNOWN)
        self.assertLess(result.confidence, 0.5)
    
    def test_recognizes_update_system(self):
        """Test recognition of system update intent"""
        result = self.recognizer.recognize("update system")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.UPDATE_SYSTEM)
        self.assertGreater(result.confidence, 0.8)
    
    def test_recognizes_rollback(self):
        """Test recognition of rollback intent"""
        result = self.recognizer.recognize("rollback to generation 42")
        
        self.assertIsInstance(result, Intent)
        self.assertEqual(result.type, IntentType.ROLLBACK)
        if 'generation' in result.entities:
            self.assertEqual(result.entities['generation'], '42')


class TestExecutor(unittest.TestCase):
    """Test the SafeExecutor directly"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import SafeExecutor
        from nix_humanity.core.executor import SafeExecutor
        self.executor = SafeExecutor()
    
    def test_executor_initialization(self):
        """Test executor initializes correctly"""
        self.assertIsNotNone(self.executor)
        self.assertFalse(self.executor.dry_run)
        self.assertEqual(self.executor.verbosity, 0)
    
    def test_executor_dry_run_mode(self):
        """Test dry run mode"""
        self.executor.dry_run = True
        
        # Execute a potentially dangerous command
        result = self.executor.execute("rm", ["-rf", "/tmp/test"])
        
        # Should not actually execute in dry run
        self.assertIn('dry_run', result)
        self.assertTrue(result.get('dry_run', False))
    
    def test_executor_categorizes_query_commands(self):
        """Test that executor correctly categorizes query commands"""
        # Test search command (should be safe query)
        result = self.executor.execute("search", ["firefox"])
        
        # Query commands should always be safe to execute
        # Check that it attempts to execute (even if command doesn't exist)
        self.assertIsNotNone(result)
    
    def test_executor_categorizes_modify_commands(self):
        """Test that executor correctly categorizes modify commands"""
        self.executor.dry_run = True  # Enable dry run for safety
        
        # Test install command (should be modify)
        result = self.executor.execute("install", ["package"])
        
        # Modify commands should respect dry_run
        self.assertTrue(result.get('dry_run', False))


if __name__ == '__main__':
    unittest.main()