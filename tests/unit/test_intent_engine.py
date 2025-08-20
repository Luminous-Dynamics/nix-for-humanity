#!/usr/bin/env python3
"""
Unit tests for the IntentRecognizer component
"""

import unittest
from pathlib import Path

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


from luminous_nix.core.intents import Intent, IntentType
from luminous_nix.core.intents import IntentRecognizer

class TestIntentRecognizer(unittest.TestCase):
    """Test the IntentRecognizer component"""
    
    def setUp(self):
        """Create intent engine for testing"""
        self.engine = IntentRecognizer()
        
    def test_recognize_install_patterns(self):
        """Test recognition of install intent patterns"""
        test_cases = [
            "install firefox",
            "add vim",
            "get python3",
            "download docker",
            "i need nodejs",
            "i want vscode",
            "need emacs",
            "want git",
            "get me htop",
            "firefox please"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE, f"Failed to recognize install intent in: '{text}'")
                self.assertIsNotNone(intent.entities.get("package"))
                self.assertGreater(intent.confidence, 0.9)
                
    def test_recognize_remove_patterns(self):
        """Test recognition of remove intent patterns"""
        test_cases = [
            "remove firefox",
            "uninstall vim",
            "delete python3",
            "firefox is gone"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.REMOVE)
                self.assertIsNotNone(intent.entities.get("package"))
                
    def test_recognize_update_patterns(self):
        """Test recognition of update intent patterns"""
        test_cases = [
            "update_system",
            "upgrade",
            "update system",
            "upgrade everything",
            "update all",
            "system update",
            "system upgrade",
            "make everything current",
            "update my system"  # This was failing before
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM, f"Failed to recognize update intent in: '{text}'")
                
    def test_recognize_search_patterns(self):
        """Test recognition of search intent patterns"""
        test_cases = [
            "search firefox",
            "find python",
            "look for editor",
            "what is docker",
            "is there vim",
            "show me nodejs"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE)
                self.assertIsNotNone(intent.entities.get("package"))
                
    def test_recognize_rollback_patterns(self):
        """Test recognition of rollback intent patterns"""
        test_cases = [
            "rollback",
            "revert",
            "undo",
            "go back",
            "previous generation"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.ROLLBACK)
                
    def test_recognize_info_patterns(self):
        """Test recognition of info intent patterns"""
        test_cases = [
            "list packages",
            "system info"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.EXPLAIN)
                
    def test_recognize_help_patterns(self):
        """Test recognition of help intent patterns"""
        test_cases = [
            "help",
            "help me",
            "what can you do",
            "how do i use this",
            "how do i install"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.HELP)
                
    def test_recognize_unknown_patterns(self):
        """Test handling of unknown patterns"""
        test_cases = [
            "random gibberish",
            "do something weird",
            "make coffee",
            "compile the kernel",
            ""
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.UNKNOWN)
                self.assertEqual(intent.confidence, 0.0)
                
    def test_package_aliases(self):
        """Test package alias resolution"""
        test_cases = [
            ("install browser", "firefox"),
            ("get web browser", "firefox"),
            ("add chrome", "google-chrome"),
            ("install vscode", "vscode"),
            ("get code", "vscode"),
            ("install vim", "vim"),
            ("add vi", "vim"),
            ("get editor", "vim"),
            ("install text editor", "vim"),
            ("add python", "python3"),
            ("get node", "nodejs"),
            ("install docker", "docker")
        ]
        
        for text, expected_target in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.entities.get("package"), expected_target)
                
    def test_case_insensitivity(self):
        """Test that recognition is case insensitive"""
        test_cases = [
            "INSTALL FIREFOX",
            "Install Firefox",
            "iNsTaLl FiReFoX"
        ]
        
        for text in test_cases:
            intent = self.engine.recognize(text)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
            self.assertEqual(intent.entities.get("package"), "firefox")
            
    def test_extract_package_name(self):
        """Test package name extraction from text"""
        test_cases = [
            ("i need the firefox browser please", "firefox"),  # Should resolve alias
            ("install that vim editor for me", "vim"),  # Should resolve alias
            ("get python3 now", "python3"),
            ("i want vscode", "vscode"),
            ("", None),
            ("the a an for me", None)  # Only noise words
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.engine.extract_package_name(text)
                self.assertEqual(result, expected)
                
    def test_suggest_alternatives(self):
        """Test alternative suggestions for misspellings"""
        # Test Firefox misspellings
        firefox_typos = ["fierfix", "firfox"]
        for typo in firefox_typos:
            suggestions = self.engine.suggest_alternatives(f"install {typo}")
            self.assertTrue(any("firefox" in s for s in suggestions))
            
        # Test Python misspellings
        python_typos = ["pyton", "pythn"]
        for typo in python_typos:
            suggestions = self.engine.suggest_alternatives(f"get {typo}")
            self.assertTrue(any("python" in s for s in suggestions))
            
        # Test editor suggestions
        editor_queries = ["install editor", "get ide"]
        for query in editor_queries:
            suggestions = self.engine.suggest_alternatives(query)
            self.assertTrue(any("vim" in s or "vscode" in s for s in suggestions))
            
        # Test no suggestions for correct input
        suggestions = self.engine.suggest_alternatives("install firefox")
        self.assertEqual(len(suggestions), 0)
        
    def test_metadata_preservation(self):
        """Test that original input is preserved in metadata"""
        test_input = "INSTALL Firefox PLEASE"
        intent = self.engine.recognize(test_input)
        
        self.assertIn('original_input', intent.metadata)
        # Note: The input is lowercased in the metadata
        self.assertEqual(intent.metadata['original_input'], test_input.strip().lower())
        
    def test_package_update_patterns(self):
        """Test that package update patterns work correctly"""
        # Package updates should be treated as install intents (installing newer version)
        test_cases = [
            ("update firefox", IntentType.INSTALL_PACKAGE, "firefox"),
            ("upgrade vim", IntentType.INSTALL_PACKAGE, "vim"),
            ("update python3", IntentType.INSTALL_PACKAGE, "python3"),
            ("upgrade nodejs", IntentType.INSTALL_PACKAGE, "nodejs"),
        ]
        
        for text, expected_type, expected_target in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, expected_type)
                self.assertEqual(intent.entities.get("package"), expected_target)
                
    def test_system_vs_package_update_distinction(self):
        """Test that system updates are distinguished from package updates"""
        # These should be system updates (UPDATE intent)
        system_updates = [
            "update system",
            "upgrade everything", 
            "update all",
            "system update",
            "update my system",
            "upgrade the whole system"
        ]
        
        for text in system_updates:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM)
                self.assertIsNone(intent.entities.get("package"))
                
        # These should be package installs (INSTALL intent)
        package_updates = [
            "update firefox",
            "upgrade vim",
            "update python3"
        ]
        
        for text in package_updates:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertIsNotNone(intent.entities.get("package"))
                
    def test_info_patterns_extended(self):
        """Test extended info patterns including new additions"""
        test_cases = [
            "show installed",      # New pattern added
            "show me installed",   # Existing pattern
            "what is installed",   # Existing pattern
            "list packages",       # Existing pattern
            "system info"          # Existing pattern
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.EXPLAIN)


if __name__ == '__main__':
    unittest.main()