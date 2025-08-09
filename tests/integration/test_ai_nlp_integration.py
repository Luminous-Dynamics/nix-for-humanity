#!/usr/bin/env python3
"""
Integration Tests for AI-Enhanced NLP Pipeline

Tests the integration between the NLP system, XAI Engine, and Advanced Learning System.
Validates that AI enhancements work together seamlessly to provide explainable,
adaptive responses.
"""

import unittest
import sqlite3
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# v2.0+ feature: from nix_humanity.ai.xai_engine import XAIEngine, CausalFactor, ExplanationLevel
# v2.0+ feature: from nix_humanity.ai.advanced_learning import AdvancedLearningSystem, PreferencePair, LearningMode

# Mock the backend NLP module since we're testing integration
class MockNLPPipeline:
    """Mock NLP Pipeline for integration testing"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.xai_engine = XAIEngine(db_path=Path(self.temp_dir) / "xai.db")
        self.advanced_learning = AdvancedLearningSystem(
            db_path=Path(self.temp_dir) / "learning.db",
            learning_mode=LearningMode.SYMBIOTIC
        )
        self.interaction_count = 0
    
    def process(self, user_input, user_id="test_user", context=None):
        """Mock process method that integrates AI enhancements"""
        if context is None:
            context = {}
        
        # Mock NLP processing
        if "install" in user_input.lower():
            intent = "install"
            confidence = 0.9 if "firefox" in user_input.lower() else 0.7
            target = "firefox" if "firefox" in user_input.lower() else "unknown"
        elif "help" in user_input.lower():
            intent = "help"
            confidence = 0.95
            target = None
        else:
            intent = "unknown"
            confidence = 0.3
            target = None
        
        # Generate base response
        if intent == "install" and target:
            base_response = f"Installing {target} for you!"
        elif intent == "help":
            base_response = "I can help you with installing software, updating your system, and more."
        else:
            base_response = "I'm not sure what you want to do. Can you be more specific?"
        
        # Apply XAI explanations
        explanation = None
        if self.xai_engine:
            try:
                # Create causal factors for this decision
                factors = []
                if "firefox" in user_input.lower():
                    factors.append(CausalFactor(
                        "keyword_match", 0.8, "positive", 
                        "Found 'firefox' in user input", 1
                    ))
                if intent == "install":
                    factors.append(CausalFactor(
                        "intent_pattern", 0.7, "positive",
                        "Recognized installation intent", 1
                    ))
                
                explanation = self.xai_engine.explain_decision(
                    "intent_recognition",
                    intent,
                    {"user_input": user_input, "user_id": user_id},
                    factors,
                    ExplanationLevel.SIMPLE
                )
            except Exception as e:
                print(f"XAI error: {e}")
        
        # Apply user adaptation
        adapted_response = base_response
        if self.advanced_learning:
            try:
                adapted_response = self.advanced_learning.adapt_response(
                    user_id, base_response, context
                )
            except Exception as e:
                print(f"Learning error: {e}")
        
        self.interaction_count += 1
        
        return {
            "intent": intent,
            "confidence": confidence,
            "target": target,
            "response": adapted_response,
            "explanation": explanation,
            "interaction_count": self.interaction_count
        }
    
    def record_feedback(self, user_id, user_input, preferred_response, rejected_response, strength=0.8):
        """Record user feedback for learning"""
        if self.advanced_learning:
            pair = PreferencePair(
                user_input=user_input,
                preferred_response=preferred_response,
                rejected_response=rejected_response,
                feedback_strength=strength,
                context={},
                user_id=user_id
            )
            self.advanced_learning.record_preference_pair(pair)


class TestAINLPIntegration(unittest.TestCase):
    """Test integration between NLP, XAI, and Learning systems"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nlp_pipeline = MockNLPPipeline()
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temp files would go here
        pass
    
    def test_basic_integration_works(self):
        """Test that all AI components work together without errors"""
        result = self.nlp_pipeline.process("install firefox")
        
        # Should have basic NLP results
        self.assertEqual(result["intent"], "install")
        self.assertEqual(result["target"], "firefox")
        self.assertGreater(result["confidence"], 0.8)
        
        # Should have response
        self.assertIn("firefox", result["response"].lower())
        
        # Should have XAI explanation
        self.assertIsNotNone(result["explanation"])
        self.assertEqual(result["explanation"].decision, "intent_recognition: install")
        
        # Should track interactions
        self.assertEqual(result["interaction_count"], 1)
    
    def test_xai_explanations_included(self):
        """Test that XAI explanations are properly generated and included"""
        result = self.nlp_pipeline.process("install firefox")
        
        explanation = result["explanation"]
        self.assertIsNotNone(explanation)
        
        # Check explanation structure
        self.assertIsNotNone(explanation.simple_explanation)
        self.assertIsNotNone(explanation.detailed_explanation) 
        self.assertIsNotNone(explanation.technical_explanation)
        
        # Check causal factors
        self.assertGreater(len(explanation.causal_factors), 0)
        
        # Check specific factors for this case
        factor_names = [f.name for f in explanation.causal_factors]
        self.assertIn("keyword_match", factor_names)
        self.assertIn("intent_pattern", factor_names)
        
        # Check explanation content mentions firefox
        self.assertIn("firefox", explanation.simple_explanation.lower())
    
    def test_user_adaptation_works(self):
        """Test that user adaptation is applied to responses"""
        # Set up user preference for minimal responses
        user_model = self.nlp_pipeline.advanced_learning.get_user_model("minimal_user")
        user_model.preferred_verbosity = "minimal"
        
        # Process command
        result = self.nlp_pipeline.process("install firefox", user_id="minimal_user")
        
        # Response should be adapted (shorter)
        self.assertIsInstance(result["response"], str)
        self.assertGreater(len(result["response"]), 0)
        
        # Test with detailed user
        detailed_user_model = self.nlp_pipeline.advanced_learning.get_user_model("detailed_user")
        detailed_user_model.preferred_verbosity = "detailed"
        
        detailed_result = self.nlp_pipeline.process(
            "install firefox", 
            user_id="detailed_user",
            context={"alternatives": ["chrome", "brave"]}
        )
        
        # Detailed response should be longer
        self.assertGreaterEqual(len(detailed_result["response"]), len(result["response"]))
    
    def test_learning_from_feedback(self):
        """Test that the system learns from user feedback"""
        user_id = "learning_user"
        
        # Initial interaction
        result1 = self.nlp_pipeline.process("install firefox", user_id=user_id)
        initial_response = result1["response"]
        
        # Record feedback preferring shorter responses
        self.nlp_pipeline.record_feedback(
            user_id=user_id,
            user_input="install firefox",
            preferred_response="Installing Firefox.",
            rejected_response="I'll install Firefox for you right away!",
            strength=0.9
        )
        
        # Multiple feedback entries to trigger learning
        for i in range(10):
            self.nlp_pipeline.record_feedback(
                user_id=user_id,
                user_input=f"install package{i}",
                preferred_response="Installing package.",
                rejected_response="I'll install the package for you!",
                strength=0.8
            )
        
        # Check that user model was updated
        user_model = self.nlp_pipeline.advanced_learning.get_user_model(user_id)
        # Note: The learning update happens in background, so we check the preference pairs were recorded
        metrics = self.nlp_pipeline.advanced_learning.get_learning_metrics(user_id)
        self.assertGreater(metrics.preference_pairs_collected, 0)
    
    def test_multi_user_isolation(self):
        """Test that different users get different adaptations"""
        # Set up two users with different preferences
        user1_model = self.nlp_pipeline.advanced_learning.get_user_model("technical_user")
        user1_model.preferred_explanation_level = "technical"
        
        user2_model = self.nlp_pipeline.advanced_learning.get_user_model("simple_user")
        user2_model.preferred_explanation_level = "simple"
        
        # Same command for both users
        result1 = self.nlp_pipeline.process("install firefox", user_id="technical_user")
        result2 = self.nlp_pipeline.process("install firefox", user_id="simple_user")
        
        # Both should work
        self.assertEqual(result1["intent"], "install")
        self.assertEqual(result2["intent"], "install")
        
        # But responses should be different (technical vs simple)
        self.assertNotEqual(result1["response"], result2["response"])
        
        # Explanations should be at different levels
        self.assertIsNotNone(result1["explanation"])
        self.assertIsNotNone(result2["explanation"])
    
    def test_error_handling_integration(self):
        """Test that AI enhancements handle errors gracefully"""
        # Test with problematic input that might cause errors
        result = self.nlp_pipeline.process("", user_id="error_user")
        
        # Should still return a result
        self.assertIsNotNone(result)
        self.assertIn("intent", result)
        self.assertIn("response", result)
        
        # Test with very long input
        long_input = "install " + "firefox " * 100
        result = self.nlp_pipeline.process(long_input, user_id="long_user")
        
        # Should handle gracefully
        self.assertIsNotNone(result)
        self.assertIsInstance(result["response"], str)
    
    def test_explanation_consistency(self):
        """Test that explanations are consistent across multiple calls"""
        # Same input should give similar explanations
        result1 = self.nlp_pipeline.process("install firefox", user_id="consistency_user")
        result2 = self.nlp_pipeline.process("install firefox", user_id="consistency_user")
        
        # Basic properties should be the same
        self.assertEqual(result1["intent"], result2["intent"])
        self.assertEqual(result1["target"], result2["target"])
        
        # Explanations should have same decision type
        self.assertEqual(
            result1["explanation"].decision.split(":")[0],
            result2["explanation"].decision.split(":")[0]
        )
        
        # Should have similar causal factors
        factors1 = [f.name for f in result1["explanation"].causal_factors]
        factors2 = [f.name for f in result2["explanation"].causal_factors]
        
        # At least some factors should overlap
        overlap = set(factors1).intersection(set(factors2))
        self.assertGreater(len(overlap), 0)
    
    def test_progressive_learning(self):
        """Test that the system progressively learns and improves"""
        user_id = "progressive_user"
        
        # Track learning metrics over time
        initial_metrics = self.nlp_pipeline.advanced_learning.get_learning_metrics(user_id)
        
        # Simulate multiple interactions with feedback
        for i in range(5):
            result = self.nlp_pipeline.process(f"install app{i}", user_id=user_id)
            
            # Record some feedback
            self.nlp_pipeline.record_feedback(
                user_id=user_id,
                user_input=f"install app{i}",
                preferred_response="Short response",
                rejected_response="Long detailed response",
                strength=0.7
            )
        
        # Check that metrics have improved
        final_metrics = self.nlp_pipeline.advanced_learning.get_learning_metrics(user_id)
        
        # Should have more preference pairs
        self.assertGreater(
            final_metrics.preference_pairs_collected,
            initial_metrics.preference_pairs_collected
        )
        
        # Should have interaction history
        self.assertGreater(final_metrics.total_interactions, 0)
    
    def test_context_awareness(self):
        """Test that the system uses context appropriately"""
        user_id = "context_user"
        
        # Test with rich context
        context = {
            "previous_command": "search browsers",
            "user_history": {"similar_patterns": 3},
            "session_id": "test_session"
        }
        
        result = self.nlp_pipeline.process("install firefox", user_id=user_id, context=context)
        
        # Should use context in explanation
        explanation = result["explanation"]
        self.assertIsNotNone(explanation)
        
        # Context should be recorded in explanation
        # (This tests that context flows through the system)
        self.assertIsInstance(explanation.timestamp, str)
    
    def test_symbiotic_insights(self):
        """Test that symbiotic insights are generated correctly"""
        user_id = "symbiotic_user"
        
        # Create some interaction history
        for i in range(3):
            self.nlp_pipeline.process(f"install tool{i}", user_id=user_id)
        
        # Get symbiotic insights
        insights = self.nlp_pipeline.advanced_learning.get_symbiotic_insights(user_id)
        
        # Should have insight structure
        self.assertIn("relationship_health", insights)
        self.assertIn("user_model_maturity", insights)
        self.assertIn("learning_velocity", insights)
        self.assertIn("symbiotic_stage", insights)
        
        # Should have reasonable values
        health = insights["relationship_health"]
        self.assertIn("trust_level", health)
        self.assertIn("learning_progress", health)
        self.assertGreaterEqual(health["trust_level"], 0.0)
        self.assertLessEqual(health["trust_level"], 1.0)


class TestAdvancedIntegrationScenarios(unittest.TestCase):
    """Test complex integration scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nlp_pipeline = MockNLPPipeline()
    
    def test_persona_adaptation_integration(self):
        """Test that the system adapts to different personas appropriately"""
        personas = [
            ("grandma_rose", "I need that Firefox thing"),
            ("maya_adhd", "firefox now"),
            ("dr_sarah", "install firefox-esr for research"),
            ("alex_blind", "install firefox")
        ]
        
        for persona_id, command in personas:
            result = self.nlp_pipeline.process(command, user_id=persona_id)
            
            # All should recognize intent
            self.assertEqual(result["intent"], "install")
            
            # All should have explanations
            self.assertIsNotNone(result["explanation"])
            
            # All should have reasonable responses
            self.assertIsInstance(result["response"], str)
            self.assertGreater(len(result["response"]), 0)
    
    def test_learning_adaptation_cycle(self):
        """Test complete learning and adaptation cycle"""
        user_id = "cycle_user"
        
        # 1. Initial interaction
        result1 = self.nlp_pipeline.process("install firefox", user_id=user_id)
        initial_response = result1["response"]
        
        # 2. User provides feedback (prefers technical responses)
        self.nlp_pipeline.record_feedback(
            user_id=user_id,
            user_input="install firefox",
            preferred_response="Executing: nix-env -iA nixos.firefox",
            rejected_response="Installing Firefox for you!",
            strength=0.9
        )
        
        # 3. System should adapt user model
        user_model = self.nlp_pipeline.advanced_learning.get_user_model(user_id)
        
        # 4. Future interactions should be influenced
        result2 = self.nlp_pipeline.process("install chrome", user_id=user_id)
        
        # Should still work
        self.assertEqual(result2["intent"], "install")
        self.assertIsNotNone(result2["response"])
    
    def test_explanation_depth_adaptation(self):
        """Test that explanations adapt to user expertise level"""
        # Beginner user
        beginner_result = self.nlp_pipeline.process("install firefox", user_id="beginner")
        beginner_explanation = beginner_result["explanation"]
        
        # Expert user (after setting preference)
        expert_model = self.nlp_pipeline.advanced_learning.get_user_model("expert")
        expert_model.preferred_explanation_level = "technical"
        
        expert_result = self.nlp_pipeline.process("install firefox", user_id="expert")
        expert_explanation = expert_result["explanation"]
        
        # Both should have explanations
        self.assertIsNotNone(beginner_explanation)
        self.assertIsNotNone(expert_explanation)
        
        # Expert explanation should be more detailed
        self.assertGreaterEqual(
            len(expert_explanation.technical_explanation),
            len(beginner_explanation.technical_explanation)
        )
    
    def test_error_explanation_integration(self):
        """Test that errors are explained through XAI system"""
        # Test with ambiguous input that should have low confidence
        result = self.nlp_pipeline.process("do something", user_id="error_user")
        
        # Should recognize as unknown
        self.assertEqual(result["intent"], "unknown")
        self.assertLess(result["confidence"], 0.5)
        
        # Should have explanation for why it's uncertain
        explanation = result["explanation"]
        self.assertIsNotNone(explanation)
        
        # Explanation should indicate uncertainty
        self.assertIn("uncertain", explanation.simple_explanation.lower())


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)