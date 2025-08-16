#!/usr/bin/env python3
"""
Simple tests for core modules to establish baseline coverage.
These tests focus on what actually exists in the codebase.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from nix_humanity.core.intents import Intent, IntentType, IntentRecognizer
from nix_humanity.core.personality import PersonalityStyle, PersonalityManager
from nix_humanity.core.responses import ResponseGenerator


class TestIntentRecognizer(unittest.TestCase):
    """Test intent recognition"""
    
    def setUp(self):
        self.recognizer = IntentRecognizer()
    
    def test_recognize_install(self):
        """Test recognizing install intent"""
        intent = self.recognizer.recognize("install firefox")
        self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
        self.assertIn("firefox", intent.entities.get("packages", []))
    
    def test_recognize_search(self):
        """Test recognizing search intent"""
        intent = self.recognizer.recognize("search for text editor")
        self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE)
        self.assertIn("text editor", intent.raw_text)
    
    def test_recognize_update(self):
        """Test recognizing update intent"""
        intent = self.recognizer.recognize("update system")
        self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM)
    
    def test_recognize_help(self):
        """Test recognizing help intent"""
        intent = self.recognizer.recognize("help")
        self.assertEqual(intent.type, IntentType.HELP)
    
    def test_recognize_unknown(self):
        """Test unknown intent handling"""
        intent = self.recognizer.recognize("something completely random")
        self.assertEqual(intent.type, IntentType.UNKNOWN)


class TestPersonalityManager(unittest.TestCase):
    """Test personality management"""
    
    def setUp(self):
        self.manager = PersonalityManager()
    
    def test_default_personality(self):
        """Test default personality is friendly"""
        self.assertEqual(self.manager.current_style, PersonalityStyle.FRIENDLY)
    
    def test_set_personality(self):
        """Test setting different personalities"""
        self.manager.set_style(PersonalityStyle.MINIMAL)
        self.assertEqual(self.manager.current_style, PersonalityStyle.MINIMAL)
        
        self.manager.set_style(PersonalityStyle.SACRED)
        self.assertEqual(self.manager.current_style, PersonalityStyle.SACRED)
    
    def test_get_traits(self):
        """Test getting personality traits"""
        traits = self.manager.get_traits()
        self.assertIsNotNone(traits)
        self.assertIsNotNone(traits.verbosity)
        self.assertIsNotNone(traits.formality)
    
    def test_all_personalities_available(self):
        """Test all 10 personalities are available"""
        styles = [
            PersonalityStyle.MINIMAL,
            PersonalityStyle.FRIENDLY,
            PersonalityStyle.ENCOURAGING,
            PersonalityStyle.PLAYFUL,
            PersonalityStyle.SACRED,
            PersonalityStyle.PROFESSIONAL,
            PersonalityStyle.TEACHER,
            PersonalityStyle.COMPANION,
            PersonalityStyle.HACKER,
            PersonalityStyle.ZEN
        ]
        for style in styles:
            self.manager.set_style(style)
            self.assertEqual(self.manager.current_style, style)


class TestResponseGenerator(unittest.TestCase):
    """Test response generation"""
    
    def setUp(self):
        self.generator = ResponseGenerator()
    
    def test_generate_install_response(self):
        """Test generating install response"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"packages": ["firefox"]},
            confidence=0.9,
            raw_text="install firefox"
        )
        response = self.generator.generate(intent)
        self.assertIsNotNone(response)
        self.assertIn("firefox", response.summary.lower())
    
    def test_generate_with_personality(self):
        """Test response changes with personality"""
        intent = Intent(
            type=IntentType.HELP,
            entities={},
            confidence=0.9,
            raw_text="help"
        )
        
        # Test minimal personality
        self.generator.set_personality(PersonalityStyle.MINIMAL)
        minimal_response = self.generator.generate(intent)
        
        # Test sacred personality
        self.generator.set_personality(PersonalityStyle.SACRED)
        sacred_response = self.generator.generate(intent)
        
        # Responses should be different
        self.assertNotEqual(minimal_response.summary, sacred_response.summary)


if __name__ == '__main__':
    unittest.main()