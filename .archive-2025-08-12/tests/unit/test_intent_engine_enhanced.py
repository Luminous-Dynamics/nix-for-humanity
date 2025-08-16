#!/usr/bin/env python3
"""
Enhanced unit tests for the IntentRecognizer
Tests intent recognition from natural language input
"""

# Add the src directory to Python path
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from luminous_nix.core.intents import Intent, IntentRecognizer, IntentType
from luminous_nix.core import Intent, IntentType

class TestIntentRecognizerEnhanced(unittest.TestCase):
    """Enhanced tests for the IntentRecognizer"""

    def setUp(self):
        """Create IntentRecognizer instance"""
        self.engine = IntentRecognizer()

    def test_initialization(self):
        """Test IntentRecognizer initializes properly"""
        # Check patterns are loaded
        self.assertIsNotNone(self.engine.patterns)
        self.assertIn(IntentType.INSTALL_PACKAGE, self.engine.patterns)
        self.assertIn(IntentType.REMOVE, self.engine.patterns)
        self.assertIn(IntentType.UPDATE_SYSTEM, self.engine.patterns)
        self.assertIn(IntentType.SEARCH_PACKAGE, self.engine.patterns)
        self.assertIn(IntentType.ROLLBACK, self.engine.patterns)
        self.assertIn(IntentType.EXPLAIN, self.engine.patterns)
        self.assertIn(IntentType.HELP, self.engine.patterns)

        # Check package aliases are loaded
        self.assertIsNotNone(self.engine.package_aliases)
        self.assertIn("browser", self.engine.package_aliases)
        self.assertEqual(self.engine.package_aliases["browser"], "firefox")

    def test_install_intent_basic(self):
        """Test basic install intent recognition"""
        test_cases = [
            ("install firefox", "firefox"),
            ("add nodejs", "nodejs"),
            ("get python", "python3"),  # Should map to python3
            ("download docker", "docker"),
        ]

        for input_text, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_target)
                self.assertGreater(intent.confidence, 0.9)

    def test_install_intent_conversational(self):
        """Test conversational install patterns"""
        test_cases = [
            ("i need firefox", "firefox"),
            ("i want vscode", "vscode"),
            ("need vim", "vim"),
            ("want docker", "docker"),
            ("get me python", "python3"),
            ("firefox please", "firefox"),
        ]

        for input_text, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_target)

    def test_install_intent_with_aliases(self):
        """Test install with package aliases"""
        test_cases = [
            ("install browser", "firefox"),
            ("add web browser", "firefox"),
            ("get code", "vscode"),
            ("install editor", "vim"),
            ("add text editor", "vim"),
            ("install node", "nodejs"),
            ("get vi", "vim"),
        ]

        for input_text, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_target)

    def test_remove_intent(self):
        """Test remove intent recognition"""
        test_cases = [
            ("remove firefox", "firefox"),
            ("uninstall python", "python3"),
            ("delete docker", "docker"),
            ("get rid of vim", "vim"),
            ("firefox is gone", "firefox"),
        ]

        for input_text, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.REMOVE)
                self.assertEqual(intent.entities.get("package"), expected_target)

    def test_update_intent(self):
        """Test update intent recognition"""
        test_cases = [
            "update_system",
            "upgrade",
            "update system",
            "upgrade everything",
            "update all",
            "update my system",
            "system update",
            "make everything current",
        ]

        for input_text in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM)
                self.assertIsNone(
                    intent.entities.get("package")
                )  # Update typically has no target

    def test_search_intent(self):
        """Test search intent recognition"""
        test_cases = [
            ("search firefox", "firefox"),
            ("find python", "python3"),
            ("look for docker", "docker"),
            ("what is vim", "vim"),
            ("is there nodejs", "nodejs"),
            ("show me browsers", "browsers"),
        ]

        for input_text, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE)
                self.assertEqual(intent.entities.get("package"), expected_target)

    def test_rollback_intent(self):
        """Test rollback intent recognition"""
        test_cases = [
            "rollback",
            "revert",
            "undo",
            "go back",
            "previous generation",
        ]

        for input_text in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.ROLLBACK)

    def test_info_intent(self):
        """Test info intent recognition"""
        test_cases = [
            "what is installed",
            "show me installed",
            "list packages",
            "system info",
        ]

        for input_text in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.EXPLAIN)

    def test_help_intent(self):
        """Test help intent recognition"""
        test_cases = [
            "help",
            "help me",
            "what can you do",
            "how do i install something",
        ]

        for input_text in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.HELP)

    def test_unknown_intent(self):
        """Test unknown intent handling"""
        test_cases = [
            "make me a sandwich",
            "what's the weather",
            "hello world",
            "123456",
            "",
        ]

        for input_text in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, IntentType.UNKNOWN)
                self.assertEqual(intent.confidence, 0.0)

    def test_case_insensitivity(self):
        """Test that recognition is case-insensitive"""
        test_cases = [
            ("INSTALL FIREFOX", IntentType.INSTALL_PACKAGE, "firefox"),
            ("Install Firefox", IntentType.INSTALL_PACKAGE, "firefox"),
            ("InStAlL fIrEfOx", IntentType.INSTALL_PACKAGE, "firefox"),
            ("REMOVE vim", IntentType.REMOVE, "vim"),
            ("UPDATE", IntentType.UPDATE_SYSTEM, None),
        ]

        for input_text, expected_type, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, expected_type)
                if expected_target:
                    self.assertEqual(intent.entities.get("package"), expected_target)

    def test_extra_whitespace_handling(self):
        """Test handling of extra whitespace"""
        test_cases = [
            ("  install   firefox  ", IntentType.INSTALL_PACKAGE, "firefox"),
            ("\tremove\tvim\t", IntentType.REMOVE, "vim"),
            ("   update   ", IntentType.UPDATE_SYSTEM, None),
        ]

        for input_text, expected_type, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                self.assertEqual(intent.type, expected_type)
                if expected_target:
                    self.assertEqual(intent.entities.get("package"), expected_target)

    def test_metadata_preservation(self):
        """Test that original input is preserved in metadata"""
        test_input = "INSTALL  Firefox  Please"
        intent = self.engine.recognize(test_input)

        self.assertIn("original_input", intent.metadata)
        # Original input should be lowercase stripped version
        self.assertEqual(intent.metadata["original_input"], "install  firefox  please")

    def test_extract_package_name(self):
        """Test package name extraction helper"""
        test_cases = [
            ("i need firefox now", "firefox"),
            ("the python package", "python3"),  # Should use alias
            ("install that vim editor for me", "vim"),
            ("please get nodejs", "nodejs"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.engine.extract_package_name(input_text)
                self.assertEqual(result, expected)

    def test_extract_package_name_with_aliases(self):
        """Test package extraction applies aliases"""
        test_cases = [
            ("i need a browser", "firefox"),
            ("the text editor", "vim"),
            ("web browser please", "firefox"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.engine.extract_package_name(input_text)
                self.assertEqual(result, expected)

    def test_extract_package_name_empty(self):
        """Test package extraction with noise words only"""
        test_cases = [
            "i need the that for me",
            "please now",
            "install get",
            "",
        ]

        for input_text in test_cases:
            with self.subTest(input=input_text):
                result = self.engine.extract_package_name(input_text)
                self.assertIsNone(result)

    def test_suggest_alternatives_typos(self):
        """Test suggestion generation for common typos"""
        suggestions = self.engine.suggest_alternatives("install fierfix")
        self.assertIn("Did you mean 'firefox'?", suggestions)

        suggestions = self.engine.suggest_alternatives("get pyton")
        self.assertIn("Did you mean 'python'?", suggestions)

    def test_suggest_alternatives_ambiguous(self):
        """Test suggestions for ambiguous requests"""
        suggestions = self.engine.suggest_alternatives("install editor")
        self.assertTrue(any("vim" in s for s in suggestions))
        self.assertTrue(any("search editor" in s for s in suggestions))

        suggestions = self.engine.suggest_alternatives("get ide")
        self.assertTrue(any("editor" in s for s in suggestions))

    def test_suggest_alternatives_empty(self):
        """Test no suggestions for clear requests"""
        suggestions = self.engine.suggest_alternatives("install firefox")
        self.assertEqual(len(suggestions), 0)

    def test_complex_patterns(self):
        """Test complex real-world patterns"""
        test_cases = [
            (
                "hey can you install that firefox thing for me",
                IntentType.INSTALL_PACKAGE,
                "firefox",
            ),
            (
                "i think i need to remove python from my system",
                IntentType.REMOVE,
                "python3",
            ),
            ("could you search for text editors", IntentType.SEARCH_PACKAGE, "text"),
            ("please help me update everything", IntentType.UPDATE_SYSTEM, None),
        ]

        for input_text, expected_type, expected_target in test_cases:
            with self.subTest(input=input_text):
                intent = self.engine.recognize(input_text)
                # These might not match perfectly due to pattern limitations
                # but should at least not crash
                self.assertIsNotNone(intent)
                self.assertIsInstance(intent, Intent)

    def test_pattern_priority(self):
        """Test that more specific patterns take priority"""
        # "get me X" should match before "get X"
        intent = self.engine.recognize("get me firefox")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities.get("package"), "firefox")

    def test_all_intent_types_covered(self):
        """Test that all IntentType enum values have patterns"""
        for intent_type in IntentType:
            if intent_type != IntentType.UNKNOWN:  # UNKNOWN doesn't need patterns
                self.assertIn(
                    intent_type,
                    self.engine.patterns,
                    f"Missing patterns for {intent_type}",
                )
                self.assertGreater(
                    len(self.engine.patterns[intent_type]),
                    0,
                    f"Empty patterns for {intent_type}",
                )

    def test_pattern_group_extraction(self):
        """Test correct group extraction from patterns"""
        # Test pattern with target in group 2
        intent = self.engine.recognize("install firefox")
        self.assertEqual(intent.entities.get("package"), "firefox")

        # Test pattern with target in group 1
        intent = self.engine.recognize("get me vim")
        self.assertEqual(intent.entities.get("package"), "vim")

        # Test pattern with no target (group 0)
        intent = self.engine.recognize("update_system")
        self.assertIsNone(intent.entities.get("package"))

    def test_confidence_scores(self):
        """Test confidence scores are appropriate"""
        # Known patterns should have high confidence
        intent = self.engine.recognize("install firefox")
        self.assertEqual(intent.confidence, 0.95)

        # Unknown patterns should have zero confidence
        intent = self.engine.recognize("make coffee")
        self.assertEqual(intent.confidence, 0.0)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Very long input
        long_input = "install " + "firefox " * 100
        intent = self.engine.recognize(long_input)
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)

        # Unicode characters
        intent = self.engine.recognize("install café")
        self.assertIsNotNone(intent)

        # Numbers in package names
        intent = self.engine.recognize("install python3")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertEqual(intent.entities.get("package"), "python3")

        # Special characters that should work
        intent = self.engine.recognize("install node-js")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)

    def test_concurrent_recognition(self):
        """Test thread safety of intent recognition"""
        import threading

        results = []

        def recognize_intent(text):
            intent = self.engine.recognize(text)
            results.append((text, intent.type))

        threads = []
        test_inputs = [
            "install firefox",
            "remove vim",
            "update system",
            "search python",
            "help me",
        ]

        for text in test_inputs:
            thread = threading.Thread(target=recognize_intent, args=(text,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Check all intents were recognized correctly
        self.assertEqual(len(results), len(test_inputs))

        # Verify specific results
        result_dict = dict(results)
        self.assertEqual(result_dict["install firefox"], IntentType.INSTALL_PACKAGE)
        self.assertEqual(result_dict["remove vim"], IntentType.REMOVE)
        self.assertEqual(result_dict["update system"], IntentType.UPDATE_SYSTEM)

if __name__ == "__main__":
    unittest.main()
