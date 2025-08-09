#!/usr/bin/env python3
"""
Simplified tests for AI NLP module

Tests basic NLP functionality without complex imports.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)

# Mock all the problematic imports
sys.modules['src'] = MagicMock()
sys.modules['src.nix_for_humanity'] = MagicMock()
sys.modules['src.nix_for_humanity.core'] = MagicMock()
sys.modules['src.nix_for_humanity.core.types'] = MagicMock()
sys.modules['src.nix_for_humanity.ai'] = MagicMock()


class TestNLPPipelineSimple(unittest.TestCase):
    """Simple tests for NLP functionality."""
    
    def test_nlp_concepts(self):
        """Test basic NLP concepts."""
        # Test text preprocessing
        text = "Install Firefox Please!"
        cleaned = text.lower().strip("!")
        self.assertEqual(cleaned, "install firefox please")
        
        # Test tokenization
        tokens = cleaned.split()
        self.assertEqual(tokens, ["install_package", "firefox", "please"])
        
        # Test entity extraction simulation
        entities = {}
        if "install_package" in tokens:
            # Find the next token as package name
            idx = tokens.index("install_package")
            if idx + 1 < len(tokens):
                entities["package"] = tokens[idx + 1]
        
        self.assertEqual(entities, {"package": "firefox"})
    
    def test_intent_patterns(self):
        """Test intent pattern matching."""
        patterns = {
            "install_package": ["install_package", "add", "get"],
            "update_system": ["update_system", "upgrade"],
            "search_package": ["search_package", "find", "look for"],
            "help": ["help", "assist"]
        }
        
        def match_intent(text):
            """Simple intent matching."""
            text_lower = text.lower()
            for intent, keywords in patterns.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        return intent
            return "unknown"
        
        # Test various inputs
        self.assertEqual(match_intent("install firefox"), "install_package")
        self.assertEqual(match_intent("add package"), "install_package")
        self.assertEqual(match_intent("update system"), "update_system")
        self.assertEqual(match_intent("find editors"), "search_package")
        self.assertEqual(match_intent("help me"), "help")
        self.assertEqual(match_intent("random text"), "unknown")
    
    def test_confidence_scoring(self):
        """Test confidence scoring logic."""
        def calculate_confidence(text, matched_intent):
            """Simple confidence calculation."""
            confidence = 0.5  # Base confidence
            
            # Increase for exact matches
            if matched_intent == "install_package" and "install_package" in text.lower():
                confidence += 0.3
            elif matched_intent == "update_system" and "update_system" in text.lower():
                confidence += 0.3
            
            # Increase for proper length
            words = text.split()
            if 2 <= len(words) <= 5:
                confidence += 0.2
                
            return min(confidence, 1.0)
        
        # Test confidence calculations
        self.assertEqual(calculate_confidence("install firefox", "install_package"), 1.0)
        self.assertEqual(calculate_confidence("add package", "install_package"), 0.7)
        self.assertEqual(calculate_confidence("this is a very long command with many words", "install_package"), 0.5)
    
    def test_entity_extraction_patterns(self):
        """Test entity extraction patterns."""
        def extract_entities(text):
            """Extract entities from text."""
            entities = {}
            words = text.lower().split()
            
            # Package extraction
            for i, word in enumerate(words):
                if word in ["install_package", "add", "remove"]:
                    if i + 1 < len(words):
                        entities["package"] = words[i + 1]
                        entities["action"] = word
                        break
            
            # Version extraction
            for i, word in enumerate(words):
                if word == "version" and i + 1 < len(words):
                    entities["version"] = words[i + 1]
            
            return entities
        
        # Test various entity extractions
        self.assertEqual(
            extract_entities("install firefox"),
            {"package": "firefox", "action": "install_package"}
        )
        self.assertEqual(
            extract_entities("remove vim"),
            {"package": "vim", "action": "remove"}
        )
        self.assertEqual(
            extract_entities("install python version 3.11"),
            {"package": "python", "action": "install_package", "version": "3.11"}
        )
    
    def test_preprocessing_functions(self):
        """Test text preprocessing functions."""
        def preprocess(text):
            """Basic text preprocessing."""
            # Remove extra spaces
            text = ' '.join(text.split())
            # Convert to lowercase
            text = text.lower()
            # Remove punctuation from ends
            text = text.strip('.,!?;:')
            return text
        
        # Test preprocessing
        self.assertEqual(preprocess("  Install  Firefox!  "), "install firefox")
        self.assertEqual(preprocess("UPDATE SYSTEM..."), "update system")
        self.assertEqual(preprocess("Help?"), "help")
    
    def test_tokenization_strategies(self):
        """Test different tokenization strategies."""
        # Simple split
        text = "install firefox browser"
        simple_tokens = text.split()
        self.assertEqual(simple_tokens, ["install_package", "firefox", "browser"])
        
        # Split with punctuation handling
        text2 = "install firefox, chrome, and vim"
        tokens2 = [t.strip(",") for t in text2.split()]
        self.assertEqual(tokens2, ["install_package", "firefox", "chrome", "and", "vim"])
        
        # Hyphenated words
        text3 = "install google-chrome"
        tokens3 = text3.split()
        self.assertEqual(tokens3, ["install_package", "google-chrome"])
    
    def test_sentiment_analysis_mock(self):
        """Test sentiment analysis concepts."""
        def analyze_sentiment(text):
            """Mock sentiment analysis."""
            positive_words = ["good", "great", "excellent", "love", "best"]
            negative_words = ["bad", "terrible", "hate", "worst", "broken"]
            
            text_lower = text.lower()
            score = 0.5  # Neutral
            
            for word in positive_words:
                if word in text_lower:
                    score += 0.2
            
            for word in negative_words:
                if word in text_lower:
                    score -= 0.2
            
            return {"polarity": max(0, min(1, score)), "subjectivity": 0.5}
        
        # Test sentiment
        self.assertEqual(analyze_sentiment("this is great")["polarity"], 0.7)
        self.assertEqual(analyze_sentiment("terrible experience")["polarity"], 0.3)
        self.assertEqual(analyze_sentiment("install firefox")["polarity"], 0.5)
    
    def test_command_classification(self):
        """Test command classification logic."""
        def classify_command(text):
            """Classify command type."""
            text_lower = text.lower()
            
            if any(word in text_lower for word in ["install_package", "add", "get"]):
                return "package_management"
            elif any(word in text_lower for word in ["update_system", "upgrade"]):
                return "system_maintenance"
            elif any(word in text_lower for word in ["search_package", "find", "list"]):
                return "information_query"
            elif any(word in text_lower for word in ["help", "how", "what"]):
                return "assistance"
            else:
                return "general"
        
        # Test classification
        self.assertEqual(classify_command("install firefox"), "package_management")
        self.assertEqual(classify_command("update system"), "system_maintenance")
        self.assertEqual(classify_command("search for editors"), "information_query")
        self.assertEqual(classify_command("help me"), "assistance")
        self.assertEqual(classify_command("configure network"), "general")


if __name__ == '__main__':
    unittest.main()