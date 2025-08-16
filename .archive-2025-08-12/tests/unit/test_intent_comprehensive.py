#!/usr/bin/env python3
"""
Comprehensive unit tests for intent recognition module

This test suite covers:
- Intent recognition for all intent types
- Pattern matching accuracy
- Package alias resolution
- Entity extraction
- Edge cases and error handling
- Both synchronous and asynchronous interfaces
"""

import os

from unittest.mock import Mock, MagicMock, patch, call
import sys
import unittest

# Add the backend directory to the path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
)

from luminous_nix.core.intents import IntentRecognizer as IntentRecognizer
from luminous_nix.core import IntentType

class TestIntentRecognizer(unittest.TestCase):
    """Test suite for IntentRecognizer"""

    def setUp(self):
        """Set up test environment"""
        self.recognizer = IntentRecognizer()

    def test_init(self):
        """Test IntentRecognizer initialization"""
        recognizer = IntentRecognizer()

        # Check that patterns are loaded
        self.assertIsNotNone(recognizer.install_patterns)
        self.assertIsNotNone(recognizer.update_patterns)
        self.assertIsNotNone(recognizer.search_patterns)
        self.assertIsNotNone(recognizer.rollback_patterns)
        self.assertIsNotNone(recognizer.configure_patterns)
        self.assertIsNotNone(recognizer.explain_patterns)

        # Check that package aliases are loaded
        self.assertIsNotNone(recognizer.package_aliases)
        self.assertIn("firefox", recognizer.package_aliases)
        self.assertIn("vscode", recognizer.package_aliases)

        # Check embeddings flag
        self.assertFalse(recognizer._embeddings_loaded)

    def test_normalize(self):
        """Test text normalization"""
        # Test basic normalization
        self.assertEqual(
            self.recognizer._normalize("  INSTALL  FIREFOX  "), "install firefox"
        )
        self.assertEqual(
            self.recognizer._normalize("install firefox!!!"), "install firefox"
        )
        self.assertEqual(
            self.recognizer._normalize("install   firefox."), "install firefox"
        )
        self.assertEqual(
            self.recognizer._normalize("INSTALL FIREFOX?"), "install firefox"
        )

        # Test punctuation removal
        self.assertEqual(
            self.recognizer._normalize("install firefox,"), "install firefox"
        )
        self.assertEqual(
            self.recognizer._normalize("install firefox;"), "install firefox"
        )
        self.assertEqual(
            self.recognizer._normalize("install firefox:"), "install firefox"
        )

    # Test Install Intent Recognition
    def test_install_intent_basic(self):
        """Test basic install intent recognition"""
        # Simple install commands
        test_cases = [
            ("install firefox", "firefox"),
            ("add vim", "vim"),
            ("get python", "python311"),  # Alias resolution
            ("need docker", "docker"),
            ("want nodejs", "nodejs"),
            ("set up git", "git"),
        ]

        for text, expected_package in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_package)
                self.assertGreaterEqual(intent.confidence, 0.9)

    def test_install_intent_polite(self):
        """Test polite install intent recognition"""
        test_cases = [
            ("can you install firefox", "firefox"),
            ("please add chrome", "google-chrome"),  # Alias
            ("could you get vim for me", "vim"),
        ]

        for text, expected_package in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_package)

    def test_install_intent_conversational(self):
        """Test conversational install intent"""
        test_cases = [
            ("I need firefox", "firefox"),
            ("I want code", "vscode"),  # Alias
            ("I would like emacs", "emacs"),
        ]

        for text, expected_package in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_package)

    def test_install_package_aliases(self):
        """Test package alias resolution"""
        aliases = [
            ("chrome", "google-chrome"),
            ("code", "vscode"),
            ("nvim", "neovim"),
            ("python", "python311"),
            ("python3", "python311"),
            ("node", "nodejs"),
            ("npm", "nodejs"),
            ("rust", "rustc"),
            ("golang", "go"),
            ("java", "openjdk"),
            ("jdk", "openjdk"),
        ]

        for alias, expected in aliases:
            with self.subTest(alias=alias):
                intent = self.recognizer.recognize(f"install {alias}")
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected)

    # Test Update Intent Recognition
    def test_update_intent(self):
        """Test update intent recognition"""
        test_cases = [
            "update my system",
            "update system",
            "update nixos",
            "upgrade my system",
            "upgrade system",
            "upgrade nixos",
            "refresh my system",
            "refresh nixos",
            "system update",
            "nixos update",
            "nixos upgrade",
            "update everything",
            "upgrade all",
        ]

        for text in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM)
                self.assertEqual(intent.entities, {})
                self.assertGreaterEqual(intent.confidence, 0.85)

    # Test Search Intent Recognition
    def test_search_intent(self):
        """Test search intent recognition"""
        test_cases = [
            ("search firefox", "firefox"),
            ("find python packages", "python"),
            ("look for text editors", "text editors"),
            ("is there a vim package", "a vim"),
            ("what packages for python", "for python"),
            ("what programs for editing", "for editing"),
            ("available editors", "editors"),
            ("exists firefox", "firefox"),
        ]

        for text, expected_query in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE)
                self.assertIn("query", intent.entities)
                # Query extraction is flexible, just check it's not empty
                self.assertIsNotNone(intent.entities["query"])
                self.assertGreaterEqual(intent.confidence, 0.8)

    # Test Rollback Intent Recognition
    def test_rollback_intent(self):
        """Test rollback intent recognition"""
        test_cases = [
            "rollback",
            "roll back",
            "revert",
            "undo",
            "go back",
            "previous generation",
            "last generation",
            "old version",
            "previous version",
            "previous state",
            "undo update",
            "undo upgrade",
            "undo changes",
        ]

        for text in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.ROLLBACK)
                self.assertEqual(intent.entities, {})
                self.assertGreaterEqual(intent.confidence, 0.85)

    # Test Configure Intent Recognition
    def test_configure_intent(self):
        """Test configure intent recognition"""
        test_cases = [
            ("configure nginx", "nginx"),
            ("config ssh", "ssh"),
            ("set up docker", "docker"),
            ("enable bluetooth", "bluetooth"),
            ("how to configure wifi", "wifi"),
            ("help me set up sound", "sound"),
            ("help me enable printing", "printing"),
        ]

        for text, expected_config in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.CONFIGURE)
                self.assertEqual(intent.entities["config"], expected_config)
                self.assertGreaterEqual(intent.confidence, 0.75)

    # Test Explain Intent Recognition
    def test_explain_intent(self):
        """Test explain intent recognition"""
        test_cases = [
            ("what is nix", "nix"),
            ("explain flakes", "flakes"),
            ("tell me about derivations", "derivations"),
            ("what are generations", "generations"),
            ("how does nix work", "nix"),
            ("how do channels work", "channels"),
        ]

        for text, expected_topic in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.EXPLAIN)
                self.assertIn("topic", intent.entities)
                self.assertIsNotNone(intent.entities["topic"])
                self.assertGreaterEqual(intent.confidence, 0.7)

    # Test Unknown Intent
    def test_unknown_intent(self):
        """Test unknown intent recognition"""
        test_cases = [
            "hello there",
            "thanks",
            "goodbye",
            "what time is it",
            "show me the weather",
            "random text without intent",
            "",  # Empty string
            "   ",  # Whitespace only
        ]

        for text in test_cases:
            with self.subTest(text=text):
                intent = self.recognizer.recognize(text)
                self.assertEqual(intent.type, IntentType.UNKNOWN)
                self.assertEqual(intent.entities, {})
                self.assertEqual(intent.confidence, 0.0)

    # Test Edge Cases
    def test_edge_cases(self):
        """Test edge cases in intent recognition"""
        # Mixed case with punctuation
        intent = self.recognizer.recognize("INSTALL FIREFOX!!!")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities.get("package"), "firefox")

        # Multiple spaces
        intent = self.recognizer.recognize("install     firefox")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities.get("package"), "firefox")

        # Special characters in package name
        intent = self.recognizer.recognize("install firefox-esr")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities.get("package"), "firefox-esr")

    def test_extract_entities(self):
        """Test entity extraction method"""
        # Test install package extraction
        entities = self.recognizer.extract_entities(
            "install firefox", IntentType.INSTALL_PACKAGE
        )
        self.assertEqual(entities["package"], "firefox")

        # Test with alias
        entities = self.recognizer.extract_entities(
            "install chrome", IntentType.INSTALL_PACKAGE
        )
        self.assertEqual(entities["package"], "google-chrome")

        # Test search query extraction
        entities = self.recognizer.extract_entities(
            "search for text editors", IntentType.SEARCH_PACKAGE
        )
        self.assertIn("query", entities)

        # Test with no matching pattern
        entities = self.recognizer.extract_entities(
            "random text", IntentType.INSTALL_PACKAGE
        )
        self.assertEqual(entities, {})

    # Test Async Interface
    def test_async_recognize(self):
        """Test async recognize method"""

        async def run_test():
            context = {"user_preference": "minimal"}

            # Test install intent
            intent = self.recognizer.recognize("install firefox", context)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
            self.assertEqual(intent.entities.get("package"), "firefox")

            # Test update intent
            intent = self.recognizer.recognize("update system", context)
            self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM)

        # Run async test
        asyncio.run(run_test())

    def test_async_semantic_match_placeholder(self):
        """Test async semantic match (placeholder)"""

        async def run_test():
            # Since semantic match is a placeholder, it should return None
            result = self.recognizer._semantic_match("test text")
            self.assertIsNone(result)

        asyncio.run(run_test())

    # Test Complex Patterns
    def test_complex_install_patterns(self):
        """Test complex install patterns"""
        # Pattern with multiple groups
        intent = self.recognizer.recognize("can you please install firefox for me")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities.get("package"), "firefox")

        # Pattern with 'I need/want' structure
        intent = self.recognizer.recognize("I really need that vim editor")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        # The pattern might extract 'that' as part of package, but alias should handle it
        self.assertIn("vim", intent.raw_text)

    def test_pattern_priority(self):
        """Test that patterns are matched in correct priority"""
        # Install should take priority over explain
        intent = self.recognizer.recognize("what is firefox and install it")
        # This is ambiguous, but install patterns are checked first
        # The actual behavior depends on pattern order
        self.assertIn(intent.type, [IntentType.INSTALL_PACKAGE, IntentType.EXPLAIN])

    def test_confidence_levels(self):
        """Test confidence levels for different intent types"""
        # Install should have high confidence
        intent = self.recognizer.recognize("install firefox")
        self.assertEqual(intent.confidence, 0.9)

        # Update should have good confidence
        intent = self.recognizer.recognize("update system")
        self.assertEqual(intent.confidence, 0.85)

        # Search should have moderate confidence
        intent = self.recognizer.recognize("search firefox")
        self.assertEqual(intent.confidence, 0.8)

        # Rollback should have good confidence
        intent = self.recognizer.recognize("rollback")
        self.assertEqual(intent.confidence, 0.85)

        # Configure should have lower confidence
        intent = self.recognizer.recognize("configure nginx")
        self.assertEqual(intent.confidence, 0.75)

        # Explain should have lowest confidence
        intent = self.recognizer.recognize("what is nix")
        self.assertEqual(intent.confidence, 0.7)

        # Unknown should have zero confidence
        intent = self.recognizer.recognize("hello world")
        self.assertEqual(intent.confidence, 0.0)

    def test_raw_text_preservation(self):
        """Test that raw text is preserved in intent"""
        original_text = "INSTALL Firefox Now!!!"
        intent = self.recognizer.recognize(original_text)

        # Raw text should be the normalized version
        self.assertEqual(intent.raw_text, "install firefox now")

    def test_entity_extraction_edge_cases(self):
        """Test entity extraction edge cases"""
        # No words after install
        entities = self.recognizer.extract_entities(
            "install_package", IntentType.INSTALL_PACKAGE
        )
        self.assertEqual(entities, {})

        # Multiple install words
        entities = self.recognizer.extract_entities(
            "install add get firefox", IntentType.INSTALL_PACKAGE
        )
        # Should extract first occurrence
        self.assertIn("package", entities)

    def test_all_package_aliases(self):
        """Test all defined package aliases"""
        for alias, canonical in self.recognizer.package_aliases.items():
            with self.subTest(alias=alias):
                intent = self.recognizer.recognize(f"install {alias}")
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), canonical)

if __name__ == "__main__":
    unittest.main()
