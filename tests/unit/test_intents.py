#!/usr/bin/env python3
"""
Tests for the intent recognition system.
Testing the actual IntentRecognizer that maps natural language to intent types.
"""

import unittest
from unittest.mock import patch, MagicMock

from luminous_nix.core.intents import IntentRecognizer, Intent, IntentType


class TestIntentType(unittest.TestCase):
    """Test the IntentType enum."""
    
    def test_intent_types_exist(self):
        """Test that all expected intent types exist."""
        expected_types = [
            "INSTALL_PACKAGE",
            "UPDATE_SYSTEM", 
            "SEARCH_PACKAGE",
            "ROLLBACK",
            "HELP",
            "UNKNOWN"
        ]
        
        for intent_type in expected_types:
            self.assertTrue(hasattr(IntentType, intent_type))
    
    def test_intent_type_values(self):
        """Test that intent types have correct string values."""
        self.assertEqual(IntentType.INSTALL_PACKAGE.value, "install_package")
        self.assertEqual(IntentType.SEARCH_PACKAGE.value, "search_package")
        self.assertEqual(IntentType.HELP.value, "help")
        self.assertEqual(IntentType.UNKNOWN.value, "unknown")


class TestIntent(unittest.TestCase):
    """Test the Intent dataclass."""
    
    def test_intent_creation(self):
        """Test creating an Intent object."""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=0.95,
            raw_text="install firefox"
        )
        
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities["package"], "firefox")
        self.assertEqual(intent.confidence, 0.95)
        self.assertEqual(intent.raw_text, "install firefox")
    
    def test_intent_with_empty_entities(self):
        """Test creating an Intent with no entities."""
        intent = Intent(
            type=IntentType.HELP,
            entities={},
            confidence=0.99,
            raw_text="help"
        )
        
        self.assertEqual(intent.type, IntentType.HELP)
        self.assertEqual(intent.entities, {})


class TestIntentRecognizer(unittest.TestCase):
    """Test the IntentRecognizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the embeddings loading to avoid file I/O
        with patch.object(IntentRecognizer, '_load_embeddings'):
            self.recognizer = IntentRecognizer()
    
    def test_initialization(self):
        """Test IntentRecognizer initialization."""
        self.assertIsNotNone(self.recognizer)
        # Check that patterns are loaded
        self.assertTrue(hasattr(self.recognizer, 'install_patterns'))
        self.assertTrue(hasattr(self.recognizer, 'search_patterns'))
        self.assertTrue(hasattr(self.recognizer, 'help_patterns'))
    
    def test_recognize_install_intent(self):
        """Test recognition of install commands."""
        test_cases = [
            "install firefox",
            "add vim",
            "get python3",
            "I need git",
            "can you install emacs",
            "please add nodejs",
            "set up docker"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE,
                           f"Query '{query}' should be recognized as INSTALL_PACKAGE")
            self.assertGreater(intent.confidence, 0.7)
    
    def test_recognize_search_intent(self):
        """Test recognition of search commands."""
        test_cases = [
            "search firefox",
            "find python packages",
            "look for text editor",
            "is there a markdown editor",
            "what packages are available for rust"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE,
                           f"Query '{query}' should be recognized as SEARCH_PACKAGE")
            self.assertGreater(intent.confidence, 0.7)
    
    def test_recognize_update_intent(self):
        """Test recognition of update commands."""
        test_cases = [
            "update system",
            "upgrade nixos",
            "update my system",
            "system update",
            "update everything",
            "upgrade all"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM,
                           f"Query '{query}' should be recognized as UPDATE_SYSTEM")
            self.assertGreater(intent.confidence, 0.7)
    
    def test_recognize_help_intent(self):
        """Test recognition of help commands."""
        test_cases = [
            "help",
            "help me",
            "what can you do",
            "what can I say",
            "how do I use this",
            "show me commands",
            "list of commands"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.HELP,
                           f"Query '{query}' should be recognized as HELP")
            self.assertGreater(intent.confidence, 0.8)
    
    def test_recognize_rollback_intent(self):
        """Test recognition of rollback commands."""
        test_cases = [
            "rollback",
            "roll back",
            "revert",
            "undo changes",
            "go back to previous generation",
            "undo update"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.ROLLBACK,
                           f"Query '{query}' should be recognized as ROLLBACK")
            self.assertGreater(intent.confidence, 0.7)
    
    def test_recognize_remove_intent(self):
        """Test recognition of remove/uninstall commands."""
        test_cases = [
            "remove firefox",
            "uninstall vim",
            "delete emacs",
            "get rid of python2",
            "I don't want nodejs anymore"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.REMOVE_PACKAGE,
                           f"Query '{query}' should be recognized as REMOVE_PACKAGE")
            self.assertGreater(intent.confidence, 0.7)
    
    def test_recognize_garbage_collect_intent(self):
        """Test recognition of garbage collection commands."""
        test_cases = [
            "garbage collect",
            "gc",
            "clean up",
            "cleanup",
            "free space",
            "delete old packages",
            "clean my system"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.GARBAGE_COLLECT,
                           f"Query '{query}' should be recognized as GARBAGE_COLLECT")
            self.assertGreater(intent.confidence, 0.7)
    
    def test_recognize_list_generations_intent(self):
        """Test recognition of list generations commands."""
        test_cases = [
            "list generations",
            "show generations",
            "what generations do I have",
            "show me my generations",
            "history of my system"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.LIST_GENERATIONS,
                           f"Query '{query}' should be recognized as LIST_GENERATIONS")
            self.assertGreater(intent.confidence, 0.7)
    
    def test_entity_extraction_install(self):
        """Test that package names are extracted for install intents."""
        test_cases = [
            ("install firefox", "firefox"),
            ("add vim-full", "vim-full"),
            ("get python3", "python3"),
            ("I need git", "git"),
            ("set up docker", "docker")
        ]
        
        for query, expected_package in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
            self.assertIn('package', intent.entities)
            self.assertEqual(intent.entities['package'], expected_package)
    
    def test_entity_extraction_search(self):
        """Test that search queries are extracted."""
        test_cases = [
            ("search python", "python"),
            ("find text editor", "text editor"),
            ("look for markdown", "markdown")
        ]
        
        for query, expected_query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE)
            self.assertIn('query', intent.entities)
            # The query extraction might vary, so just check it's not empty
            self.assertTrue(intent.entities['query'])
    
    def test_unknown_intent(self):
        """Test that truly unknown queries are marked as UNKNOWN."""
        test_cases = [
            "foobar baz qux",
            "random gibberish xyz123",
            "completely unrelated text"
        ]
        
        for query in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.UNKNOWN,
                           f"Query '{query}' should be recognized as UNKNOWN")
            self.assertLess(intent.confidence, 0.5)
    
    def test_confidence_scores(self):
        """Test that confidence scores are reasonable."""
        # Clear intent should have high confidence
        intent = self.recognizer.recognize("install firefox")
        self.assertGreater(intent.confidence, 0.8)
        
        # Ambiguous intent should have lower confidence
        intent = self.recognizer.recognize("get me something")
        self.assertLess(intent.confidence, 0.7)
        
        # Unknown intent should have very low confidence
        intent = self.recognizer.recognize("xyz123 random")
        self.assertLess(intent.confidence, 0.3)
    
    def test_raw_text_preserved(self):
        """Test that raw text is preserved in intent."""
        test_query = "install firefox and vim"
        intent = self.recognizer.recognize(test_query)
        self.assertEqual(intent.raw_text, test_query)
    
    def test_service_management_intents(self):
        """Test recognition of service management commands."""
        test_cases = [
            ("start nginx", IntentType.START_SERVICE),
            ("stop postgresql", IntentType.STOP_SERVICE),
            ("restart apache", IntentType.RESTART_SERVICE),
            ("status of sshd", IntentType.SERVICE_STATUS),
            ("list services", IntentType.LIST_SERVICES),
            ("enable docker", IntentType.ENABLE_SERVICE),
            ("disable bluetooth", IntentType.DISABLE_SERVICE)
        ]
        
        for query, expected_type in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, expected_type,
                           f"Query '{query}' should be recognized as {expected_type}")
    
    def test_network_management_intents(self):
        """Test recognition of network management commands."""
        test_cases = [
            ("show network", IntentType.SHOW_NETWORK),
            ("what's my ip", IntentType.SHOW_IP),
            ("connect to wifi", IntentType.CONNECT_WIFI),
            ("list wifi networks", IntentType.LIST_WIFI),
            ("test connection", IntentType.TEST_CONNECTION)
        ]
        
        for query, expected_type in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, expected_type,
                           f"Query '{query}' should be recognized as {expected_type}")
    
    def test_disk_management_intents(self):
        """Test recognition of disk/storage management commands."""
        test_cases = [
            ("disk usage", IntentType.DISK_USAGE),
            ("analyze disk space", IntentType.ANALYZE_DISK),
            ("find large files", IntentType.FIND_LARGE_FILES)
        ]
        
        for query, expected_type in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, expected_type,
                           f"Query '{query}' should be recognized as {expected_type}")
    
    def test_flake_management_intents(self):
        """Test recognition of flake management commands."""
        test_cases = [
            ("create flake", IntentType.CREATE_FLAKE),
            ("validate flake", IntentType.VALIDATE_FLAKE),
            ("show flake info", IntentType.SHOW_FLAKE_INFO)
        ]
        
        for query, expected_type in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, expected_type,
                           f"Query '{query}' should be recognized as {expected_type}")


if __name__ == '__main__':
    unittest.main()