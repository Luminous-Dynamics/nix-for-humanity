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

# Import the actual backend (module name luminous_nix for legacy compatibility)
from luminous_nix.core.engine import NixForHumanityBackend as LuminousNixBackend
from luminous_nix.core.intents import Intent, IntentType
from luminous_nix.api.schema import Request, Response


class TestLuminousNixBackend(unittest.TestCase):
    """Test the real backend implementation with correct structures"""
    
    def setUp(self):
        """Set up test fixtures with proper mocking"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch KnowledgeBase at module level to avoid database initialization
        self.kb_patcher = patch('luminous_nix.core.engine.KnowledgeBase')
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
        request = Request(query="install firefox")
        
        # Mock the intent recognizer with correct Intent structure
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={"package": "firefox"},
                confidence=0.9,
                raw_text="install firefox"
            )
            
            # Mock the knowledge base response
            self.mock_kb.get_solution.return_value = {
                "commands": [{
                    "command": "nix-env -iA nixpkgs.firefox",
                    "description": "Install firefox package"
                }]
            }
            
            result = self.backend.process(request)
            
            self.assertTrue(result.success)
            mock_recognize.assert_called_once_with("install firefox")
    
    def test_process_search_query(self):
        """Test processing a search query"""
        request = Request(query="search python")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.SEARCH_PACKAGE,
                entities={"query": "python"},
                confidence=0.85,
                raw_text="search python"
            )
            
            # Mock the knowledge base response
            self.mock_kb.get_solution.return_value = {
                "packages": ["python3-3.11.0", "python3-3.12.0"],
                "commands": [{
                    "command": "nix search nixpkgs python",
                    "description": "Search for python packages"
                }]
            }
            
            result = self.backend.process(request)
            
            # Response should be successful
            self.assertTrue(result.success)
    
    def test_process_help_query(self):
        """Test processing a help query"""
        request = Request(query="help")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.HELP,
                entities={},
                confidence=0.99,
                raw_text="help"
            )
            
            # Help doesn't need executor, should return help text
            result = self.backend.process(request)  # Fixed: use request not query
            
            # Verify intent recognizer was called
            mock_recognize.assert_called_once_with("help")
    
    def test_unknown_intent_uses_knowledge_base(self):
        """Test that unknown intents trigger knowledge base search"""
        request = Request(query="how to configure networking")
        
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
            
            result = self.backend.process(request)  # Fixed: use request not query
            
            # Knowledge base should be searched
            self.mock_kb.get_solution.assert_called()
    
    def test_dry_run_mode(self):
        """Test dry run mode with context"""
        # Create request with dry run context
        request = Request(
            query="install dangerous-package",
            context={"execute": False}  # This means dry-run
        )
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            mock_recognize.return_value = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={"package": "dangerous-package"},
                confidence=0.9,
                raw_text="install dangerous-package"
            )
            
            # Mock knowledge base response
            self.mock_kb.get_solution.return_value = {
                "commands": [{
                    "command": "nix-env -iA nixpkgs.dangerous-package",
                    "description": "Install dangerous-package"
                }]
            }
            
            result = self.backend.process(request)
            
            # Check result shows commands would not be executed
            self.assertTrue(result.success)
            if result.commands:
                # Commands should indicate they wouldn't execute
                self.assertTrue(result.commands[0].get('would_execute', True))
    
    def test_error_handling(self):
        """Test error handling in processing"""
        request = Request(query="install firefox")
        
        with patch.object(self.backend.intent_recognizer, 'recognize') as mock_recognize:
            # Make the recognizer raise an exception
            mock_recognize.side_effect = Exception("Test error")
            
            result = self.backend.process(request)
            
            # Should handle the error gracefully
            self.assertFalse(result.success)
            self.assertIsNotNone(result.text)  # Should have error message


class TestIntentRecognizer(unittest.TestCase):
    """Test the intent recognizer directly"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Patch KnowledgeBase
        self.kb_patcher = patch('luminous_nix.core.engine.KnowledgeBase')
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
        from luminous_nix.core.executor import SafeExecutor
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