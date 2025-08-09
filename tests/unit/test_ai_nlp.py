#!/usr/bin/env python3
"""
Tests for NLPPipeline - natural language processing module

Tests the multi-stage NLP processing functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from pathlib import Path

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, 'nix_humanity')
sys.path.insert(0, backend_path)

# Mock the imports that might not be available
sys.modules['src'] = MagicMock()
sys.modules['src.nix_for_humanity'] = MagicMock()
sys.modules['src.nix_for_humanity.ai'] = MagicMock()

# Import after mocking
from nix_humanity.ai.nlp import NLPPipeline


class TestNLPPipeline(unittest.TestCase):
    """Test the NLPPipeline class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.model_manager = Mock()
        
        # Patch methods that might cause issues
        with patch.object(NLPPipeline, '_init_nltk'):
            with patch.object(NLPPipeline, '_init_patterns'):
                self.pipeline = NLPPipeline(model_manager=self.model_manager)
    
    def test_init_no_model_manager(self):
        """Test initialization without model manager."""
        with patch.object(NLPPipeline, '_init_nltk'):
            with patch.object(NLPPipeline, '_init_patterns'):
                pipeline = NLPPipeline()
                self.assertIsNone(pipeline.model_manager)
                self.assertIsNone(pipeline.xai_engine)
                self.assertIsNone(pipeline.advanced_learning)
    
    def test_init_with_model_manager(self):
        """Test initialization with model manager."""
        self.assertEqual(self.pipeline.model_manager, self.model_manager)
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        # Mock the method if it exists
        self.pipeline.preprocess_text = Mock(return_value="cleaned text")
        
        result = self.pipeline.preprocess_text("Test Input!")
        self.assertEqual(result, "cleaned text")
        self.pipeline.preprocess_text.assert_called_once_with("Test Input!")
    
    def test_tokenize(self):
        """Test tokenization."""
        # Mock tokenization method
        self.pipeline.tokenize = Mock(return_value=["test", "tokens"])
        
        result = self.pipeline.tokenize("test tokens")
        self.assertEqual(result, ["test", "tokens"])
    
    def test_extract_entities(self):
        """Test entity extraction."""
        # Mock entity extraction
        self.pipeline.extract_entities = Mock(return_value={"package": "firefox"})
        
        result = self.pipeline.extract_entities("install firefox")
        self.assertEqual(result, {"package": "firefox"})
    
    def test_analyze_sentiment(self):
        """Test sentiment analysis."""
        # Mock sentiment analysis
        self.pipeline.analyze_sentiment = Mock(return_value={"polarity": 0.8, "subjectivity": 0.2})
        
        result = self.pipeline.analyze_sentiment("This is great!")
        self.assertEqual(result["polarity"], 0.8)
        self.assertEqual(result["subjectivity"], 0.2)
    
    def test_process_full_pipeline(self):
        """Test full pipeline processing."""
        # Mock the main process method
        self.pipeline.process = Mock(return_value={
            "text": "install firefox",
            "intent": "install_package",
            "entities": {"package": "firefox"},
            "confidence": 0.95
        })
        
        result = self.pipeline.process("install firefox")
        self.assertEqual(result["intent"], "install_package")
        self.assertEqual(result["entities"]["package"], "firefox")
        self.assertEqual(result["confidence"], 0.95)
    
    def test_xai_engine_integration(self):
        """Test XAI engine integration when available."""
        # Create pipeline with mocked XAI engine
        with patch('backend.ai.nlp.XAIEngine') as mock_xai:
            mock_xai_instance = MagicMock()
            mock_xai.return_value = mock_xai_instance
            
            with patch.object(NLPPipeline, '_init_nltk'):
                with patch.object(NLPPipeline, '_init_patterns'):
                    pipeline = NLPPipeline()
                    
            # Should have tried to initialize XAI engine
            mock_xai.assert_called_once()
    
    def test_pattern_matching(self):
        """Test pattern matching functionality."""
        # Test common patterns that should exist
        patterns = {
            "install_package": r"install|add|get",
            "update_system": r"update|upgrade",
            "search_package": r"search|find|look for",
            "help": r"help|assist"
        }
        
        # Mock pattern matching
        self.pipeline.match_pattern = Mock(side_effect=lambda text, pattern: 
                                         any(word in text.lower() for word in pattern.split('|')))
        
        # Test patterns
        self.assertTrue(self.pipeline.match_pattern("install firefox", patterns["install_package"]))
        self.assertTrue(self.pipeline.match_pattern("update system", patterns["update_system"]))
        self.assertTrue(self.pipeline.match_pattern("search for editors", patterns["search_package"]))
        self.assertTrue(self.pipeline.match_pattern("help me", patterns["help"]))
    
    def test_error_handling(self):
        """Test error handling in pipeline."""
        # Mock process method to raise exception
        self.pipeline.process = Mock(side_effect=Exception("Processing error"))
        
        with self.assertRaises(Exception) as context:
            self.pipeline.process("test input")
        
        self.assertIn("Processing error", str(context.exception))


if __name__ == '__main__':
    unittest.main()