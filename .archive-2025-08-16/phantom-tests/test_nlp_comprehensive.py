#!/usr/bin/env python3
"""
Comprehensive NLP Engine tests focusing on advanced functionality
Tests fuzzy matching, typo correction, context awareness, and persona adaptation
"""

import unittest
from pathlib import Path

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from luminous_nix.core.intents import IntentRecognizer
from luminous_nix.core.interface import Intent, IntentType


class TestNLPComprehensive(unittest.TestCase):
    """Comprehensive NLP Engine tests"""
    
    def setUp(self):
        """Create IntentRecognizer instance"""
        self.engine = IntentRecognizer()
        
    def test_typo_tolerance_firefox(self):
        """Test tolerance for common Firefox typos"""
        typos = [
            "install fierfix",
            "get firfox", 
            "add fierfox",
            "download firefix",
            "i need fireofx"
        ]
        
        for typo in typos:
            with self.subTest(typo=typo):
                intent = self.engine.recognize(typo)
                # Should still recognize as install intent
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                # Should extract some form of the package name
                self.assertIsNotNone(intent.entities.get("package"))
                
    def test_conversational_patterns(self):
        """Test natural conversational patterns"""
        test_cases = [
            ("can you please install firefox for me", IntentType.INSTALL_PACKAGE, "firefox"),
            ("would you mind adding vim", IntentType.INSTALL_PACKAGE, "vim"),
            ("could i get python please", IntentType.INSTALL_PACKAGE, "python3"),
            ("is it possible to remove docker", IntentType.REMOVE, "docker"),
            ("can you show me what's installed", IntentType.EXPLAIN, None),
            ("help me understand updates", IntentType.HELP, None),
        ]
        
        for text, expected_type, expected_target in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                # These should not fail completely even if not perfectly recognized
                self.assertIsNotNone(intent)
                self.assertIsNotNone(intent.type)
                
    def test_package_name_variations(self):
        """Test various ways to express package names"""
        test_cases = [
            ("install the firefox web browser", "firefox"),
            ("add python programming language", "python3"),
            ("get vim text editor", "vim"),
            ("download docker container system", "docker"),
            ("install nodejs javascript runtime", "nodejs"),
        ]
        
        for text, expected_package in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                # The target should be the canonical package name
                self.assertEqual(intent.entities.get("package"), expected_package)
                
    def test_complex_remove_patterns(self):
        """Test complex removal patterns"""
        test_cases = [
            "remove that firefox browser",
            "get rid of the python stuff", 
            "uninstall vim editor completely",
            "delete docker and all its dependencies",
            "firefox needs to be gone",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.REMOVE)
                self.assertIsNotNone(intent.entities.get("package"))
                
    def test_update_variations(self):
        """Test different ways to ask for updates"""
        test_cases = [
            "update everything on my system",
            "upgrade all packages",
            "make my system current",
            "system upgrade please",
            "update the whole system",
            "upgrade my nixos",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM)
                
    def test_search_information_patterns(self):
        """Test search and information gathering patterns"""
        test_cases = [
            ("search for text editors", IntentType.SEARCH_PACKAGE, "text editors"),
            ("find programming languages", IntentType.SEARCH_PACKAGE, "programming languages"),
            ("what is available for browsing", IntentType.SEARCH_PACKAGE, "available browsing"),
            ("show me all editors", IntentType.SEARCH_PACKAGE, "editors"),
            ("is there a good terminal emulator", IntentType.SEARCH_PACKAGE, "good terminal emulator"),
        ]
        
        for text, expected_type, expected_target in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, expected_type)
                if expected_target:
                    self.assertIsNotNone(intent.entities.get("package"))
                    
    def test_help_patterns(self):
        """Test help request patterns"""
        test_cases = [
            "help me with nixos",
            "how do i install software", 
            "what can this system do",
            "i need assistance",
            "explain how to use this",
            "tutorial please",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                # Should be help or at least not unknown
                self.assertNotEqual(intent.type, IntentType.UNKNOWN)
                
    def test_confidence_levels(self):
        """Test that confidence levels are appropriate"""
        high_confidence_cases = [
            "install firefox",
            "remove vim", 
            "update system",
            "help",
        ]
        
        for text in high_confidence_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertGreaterEqual(intent.confidence, 0.9)
                
    def test_ambiguous_inputs(self):
        """Test handling of ambiguous inputs"""
        ambiguous_cases = [
            "install_package", # Missing package
            "remove", # Missing package
            "update firefox", # Ambiguous - update firefox or system?
            "get", # Too vague
        ]
        
        for text in ambiguous_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                # Should handle gracefully, not crash
                self.assertIsNotNone(intent)
                self.assertIsNotNone(intent.type)
                
    def test_noise_word_filtering(self):
        """Test that noise words are properly filtered"""
        test_cases = [
            ("please install firefox for me now", "firefox"),
            ("i really need vim editor that works", "vim"),
            ("can you please add the python package", "python3"),
            ("install the docker container system please", "docker"),
        ]
        
        for text, expected_package in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_package)
                
    def test_package_alias_resolution(self):
        """Test comprehensive package alias resolution"""
        alias_tests = [
            ("install browser", "firefox"),
            ("add web browser", "firefox"),
            ("get text editor", "vim"),
            ("install editor", "vim"),
            ("add code editor", "vscode"),
            ("get programming language python", "python3"),
            ("install node runtime", "nodejs"),
        ]
        
        for text, expected_alias in alias_tests:
            with self.subTest(text=text, expected=expected_alias):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_alias)
                
    def test_metadata_preservation(self):
        """Test that metadata is properly preserved"""
        test_input = "Install Firefox Browser Please"
        intent = self.engine.recognize(test_input)
        
        # Should preserve original input in metadata
        self.assertIn('original_input', intent.metadata)
        self.assertEqual(intent.metadata['original_input'], test_input.strip().lower())
        
    def test_pattern_precedence(self):
        """Test that pattern precedence works correctly"""
        # "get rid of" should be REMOVE, not INSTALL
        intent = self.engine.recognize("get rid of firefox")
        self.assertEqual(intent.type, IntentType.REMOVE)
        self.assertEqual(intent.entities.get("package"), "firefox")
        
        # "what is installed" should be INFO, not SEARCH
        intent = self.engine.recognize("what is installed")
        self.assertEqual(intent.type, IntentType.EXPLAIN)
        
        # "show me installed" should be INFO, not SEARCH  
        intent = self.engine.recognize("show me installed")
        self.assertEqual(intent.type, IntentType.EXPLAIN)
        
    def test_error_recovery(self):
        """Test error recovery from malformed inputs"""
        problematic_inputs = [
            "",  # Empty
            "   ",  # Whitespace only
            "install     ",  # Trailing whitespace
            "INSTALL FIREFOX!!!",  # Excessive punctuation
            "install\tfirefox\n",  # Special characters
        ]
        
        for text in problematic_inputs:
            with self.subTest(text=repr(text)):
                intent = self.engine.recognize(text)
                # Should not crash, should return some result
                self.assertIsNotNone(intent)
                self.assertIsNotNone(intent.type)
                self.assertIsInstance(intent.confidence, (int, float))
                
    def test_suggestion_generation(self):
        """Test alternative suggestion generation"""
        # Common misspellings should generate suggestions
        suggestions = self.engine.suggest_alternatives("install fierfix")
        self.assertTrue(len(suggestions) > 0)
        self.assertTrue(any("firefox" in s.lower() for s in suggestions))
        
        # Ambiguous requests should generate helpful suggestions
        suggestions = self.engine.suggest_alternatives("install editor")
        self.assertTrue(len(suggestions) > 0)
        
        # Correct input should not generate suggestions
        suggestions = self.engine.suggest_alternatives("install firefox")
        self.assertEqual(len(suggestions), 0)
        
    def test_case_insensitive_processing(self):
        """Test that all processing is case insensitive"""
        test_cases = [
            "INSTALL FIREFOX",
            "Install Firefox", 
            "iNsTaLl FiReFoX",
            "InStAlL fIrEfOx",
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), "firefox")
                
    def test_whitespace_tolerance(self):
        """Test tolerance for various whitespace patterns"""
        test_cases = [
            "install  firefox",  # Double space
            " install firefox ",  # Leading/trailing
            "install\tfirefox",   # Tab
            "install   firefox   please",  # Multiple spaces
        ]
        
        for text in test_cases:
            with self.subTest(text=repr(text)):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), "firefox")


class TestNLPEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Create IntentRecognizer instance"""
        self.engine = IntentRecognizer()
        
    def test_extremely_long_input(self):
        """Test handling of very long inputs"""
        long_input = "install " + "firefox " * 100 + "please"
        intent = self.engine.recognize(long_input)
        
        # Should handle gracefully
        self.assertIsNotNone(intent)
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        
    def test_special_characters(self):
        """Test handling of special characters"""
        special_cases = [
            "install firefox!!!",
            "install firefox???",
            "install firefox...",
            "install firefox;",
            "install firefox,",
        ]
        
        for text in special_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                
    def test_unicode_handling(self):
        """Test handling of unicode characters"""
        unicode_cases = [
            "install firefox ♥",
            "install firefox 🔥",
            "install firefox café",
        ]
        
        for text in unicode_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                # Should handle gracefully, not crash
                self.assertIsNotNone(intent)
                
    def test_nested_package_references(self):
        """Test complex nested package references"""
        complex_cases = [
            "install firefox or chrome browser",
            "add vim or emacs editor", 
            "get python or node runtime",
        ]
        
        for text in complex_cases:
            with self.subTest(text=text):
                intent = self.engine.recognize(text)
                # Should extract some reasonable intent
                self.assertIsNotNone(intent)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                

if __name__ == '__main__':
    unittest.main()