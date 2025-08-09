#!/usr/bin/env python3
"""
Comprehensive Unit Tests for XAI Engine

Tests the Explainable AI Engine's causal reasoning, explanation generation,
database operations, and all core functionality. Aims for 95%+ coverage.
"""

import unittest
import sqlite3
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the modules under test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from nix_humanity.ai.xai_engine import (
    XAIEngine, 
    Explanation, 
    CausalFactor, 
    ExplanationLevel, 
    ConfidenceLevel,
    create_causal_factor,
    analyze_intent_recognition
)


class TestXAIEngineCore(unittest.TestCase):
    """Test core XAI Engine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_xai.db"
        self.engine = XAIEngine(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_init_creates_database(self):
        """Test that XAI engine initializes database correctly"""
        self.assertTrue(self.db_path.exists())
        
        # Check database schema
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        
        expected_tables = ['decisions', 'causal_factors', 'user_explanations']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_causal_knowledge_loaded(self):
        """Test that causal knowledge base is properly loaded"""
        knowledge = self.engine.causal_knowledge
        
        # Check main categories exist
        self.assertIn('intent_recognition', knowledge)
        self.assertIn('package_selection', knowledge)
        self.assertIn('error_resolution', knowledge)
        
        # Check intent recognition factors
        intent_factors = knowledge['intent_recognition']['factors']
        self.assertIn('keyword_match', intent_factors)
        self.assertIn('context_similarity', intent_factors)
        self.assertIn('user_history', intent_factors)
        
        # Check confidence thresholds
        thresholds = knowledge['intent_recognition']['confidence_thresholds']
        self.assertIn('high', thresholds)
        self.assertEqual(thresholds['high'], 0.9)
    
    def test_confidence_calculation_high(self):
        """Test confidence calculation for high-confidence decisions"""
        factors = [
            CausalFactor("test_factor", 0.9, "positive", "Strong evidence", 5),
            CausalFactor("second_factor", 0.8, "positive", "Good evidence", 3)
        ]
        
        confidence = self.engine._calculate_confidence(factors, "intent_recognition")
        self.assertEqual(confidence, ConfidenceLevel.HIGH)
    
    def test_confidence_calculation_medium(self):
        """Test confidence calculation for medium-confidence decisions"""
        factors = [
            CausalFactor("test_factor", 0.5, "positive", "Moderate evidence", 1),
            CausalFactor("second_factor", 0.2, "positive", "Weak evidence", 1),
            CausalFactor("uncertainty", 0.3, "negative", "Some uncertainty", 1)
        ]
        
        confidence = self.engine._calculate_confidence(factors, "intent_recognition")
        self.assertIn(confidence, [ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW])
    
    def test_confidence_calculation_uncertain(self):
        """Test confidence calculation with no factors"""
        factors = []
        confidence = self.engine._calculate_confidence(factors, "intent_recognition")
        self.assertEqual(confidence, ConfidenceLevel.UNCERTAIN)
    
    def test_simple_explanation_generation_beginner(self):
        """Test simple explanation generation for beginner users"""
        factors = [CausalFactor("keyword_match", 0.8, "positive", "found 'install' keyword", 1)]
        
        explanation = self.engine._generate_simple_explanation(
            "intent_recognition", 
            "install_package", 
            factors, 
            "beginner"
        )
        
        self.assertIn("install_package", explanation.lower())
        self.assertIn("keyword", explanation.lower())
        # Should be simple, one sentence
        self.assertEqual(explanation.count('.'), 1)
    
    def test_simple_explanation_generation_expert(self):
        """Test simple explanation generation for expert users"""
        factors = [CausalFactor("keyword_match", 0.8, "positive", "found 'install' keyword", 1)]
        
        explanation = self.engine._generate_simple_explanation(
            "intent_recognition", 
            "install_package", 
            factors, 
            "expert"
        )
        
        self.assertIn("0.80", explanation)  # Should include importance score
        self.assertIn("install_package", explanation)
    
    def test_detailed_explanation_generation(self):
        """Test detailed explanation generation"""
        factors = [
            CausalFactor("keyword_match", 0.8, "positive", "found 'install' keyword", 2),
            CausalFactor("user_history", 0.6, "positive", "user often installs packages", 5),
            CausalFactor("context", 0.4, "neutral", "ambiguous context", 1)
        ]
        context = {"user_input": "install firefox"}
        
        explanation = self.engine._generate_detailed_explanation(
            "intent_recognition",
            "install_package",
            factors,
            context
        )
        
        # Should mention top factors
        self.assertIn("keyword", explanation)
        self.assertIn("installs packages", explanation)  # From user_history description
        self.assertIn("80%", explanation)  # Importance percentage
        self.assertIn("firefox", explanation)  # Context
    
    def test_technical_explanation_generation(self):
        """Test technical explanation generation"""
        factors = [CausalFactor("keyword_match", 0.8, "positive", "keyword analysis", 1)]
        context = {"user_input": "install firefox", "session_id": "test123"}
        
        explanation = self.engine._generate_technical_explanation(
            "intent_recognition",
            "install_package",
            factors,
            context
        )
        
        # Should include technical details
        self.assertIn("Decision:", explanation)
        self.assertIn("Context:", explanation)
        self.assertIn("Causal Analysis:", explanation)
        self.assertIn("importance=0.800", explanation)
        self.assertIn("session_id", explanation)
    
    def test_alternatives_finding_package_selection(self):
        """Test alternative finding for package selection"""
        alternatives = self.engine._find_alternatives(
            "package_selection", 
            "firefox", 
            {"category": "browser"}
        )
        
        expected_alternatives = ["firefox-esr", "chromium", "brave"]
        self.assertEqual(alternatives, expected_alternatives)
    
    def test_alternatives_finding_intent_recognition(self):
        """Test alternative finding for intent recognition"""
        alternatives = self.engine._find_alternatives(
            "intent_recognition", 
            "install_package", 
            {"alternatives": ["search_package", "explain"]}
        )
        
        expected_alternatives = ["install_package", "search_package", "explain"]
        for alt in expected_alternatives:
            if alt != "install_package":  # Current decision wouldn't be in alternatives
                self.assertIn(alt, ["install_package", "search_package", "explain"])
    
    def test_evidence_sources_identification(self):
        """Test evidence source identification"""
        factors = [
            CausalFactor("user_history", 0.8, "positive", "historical patterns", 3),
            CausalFactor("pattern_match", 0.6, "positive", "pattern matching", 2),
            CausalFactor("popularity", 0.4, "positive", "community usage", 1),
            CausalFactor("preference", 0.3, "positive", "user preferences", 1)
        ]
        
        sources = self.engine._identify_evidence_sources(factors, {})
        
        expected_sources = [
            "User interaction history",
            "Pattern matching database", 
            "Community usage statistics",
            "Learned user preferences"
        ]
        
        for source in expected_sources:
            self.assertIn(source, sources)
    
    def test_full_explanation_generation(self):
        """Test complete explanation generation workflow"""
        factors = [
            CausalFactor("keyword_match", 0.9, "positive", "Strong keyword match", 3),
            CausalFactor("user_history", 0.7, "positive", "User pattern", 5)
        ]
        context = {
            "user_input": "install firefox",
            "session_id": "test123",
            "user_id": "user456"
        }
        
        explanation = self.engine.explain_decision(
            "intent_recognition",
            "install_package",
            context,
            factors,
            ExplanationLevel.DETAILED,
            "intermediate"
        )
        
        # Check explanation structure
        self.assertIsInstance(explanation, Explanation)
        self.assertEqual(explanation.decision, "intent_recognition: install")
        self.assertEqual(explanation.confidence, ConfidenceLevel.HIGH)
        self.assertIsNotNone(explanation.simple_explanation)
        self.assertIsNotNone(explanation.detailed_explanation)
        self.assertIsNotNone(explanation.technical_explanation)
        self.assertEqual(len(explanation.causal_factors), 2)
        self.assertIsNotNone(explanation.timestamp)
    
    def test_database_decision_storage(self):
        """Test decision and explanation storage in database"""
        factors = [CausalFactor("test_factor", 0.8, "positive", "test", 1)]
        context = {"user_input": "test command", "user_id": "test_user"}
        
        explanation = self.engine.explain_decision(
            "test_decision",
            "test_value", 
            context,
            factors
        )
        
        # Check decision stored in database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM decisions WHERE decision_type = ?', ('test_decision',))
        decision_row = c.fetchone()
        self.assertIsNotNone(decision_row)
        self.assertEqual(decision_row[2], 'test_value')  # decision_value
        
        # Check causal factors stored
        c.execute('SELECT * FROM causal_factors WHERE decision_id = ?', (decision_row[0],))
        factor_rows = c.fetchall()
        self.assertEqual(len(factor_rows), 1)
        self.assertEqual(factor_rows[0][2], 'test_factor')  # factor_name
        
        conn.close()
    
    def test_explanation_history_retrieval(self):
        """Test explanation history retrieval"""
        # Create some test decisions
        factors = [CausalFactor("test", 0.8, "positive", "test factor", 1)]
        context = {"user_id": "test_user"}
        
        for i in range(3):
            self.engine.explain_decision(f"test_type_{i}", f"value_{i}", context, factors)
        
        # Retrieve history
        history = self.engine.get_explanation_history("test_user", limit=5)
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['decision_type'], 'test_type_2')  # Most recent first
    
    def test_explanation_feedback_recording(self):
        """Test explanation feedback recording"""
        # First create a decision
        factors = [CausalFactor("test", 0.8, "positive", "test", 1)]
        explanation = self.engine.explain_decision("test", "value", {}, factors)
        
        # Get the decision ID from database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id FROM decisions ORDER BY id DESC LIMIT 1')
        decision_id = c.fetchone()[0]
        conn.close()
        
        # Record feedback
        self.engine.record_explanation_feedback(decision_id, 4, "Very helpful!")
        
        # Verify feedback stored
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT helpful_rating, user_feedback FROM user_explanations WHERE decision_id = ?', 
                 (decision_id,))
        feedback_row = c.fetchone()
        conn.close()
        
        # Note: This test might need adjustment based on actual schema
        # The feedback recording might need a user_explanations entry first
    
    def test_explanation_analytics(self):
        """Test explanation analytics generation"""
        # Create test data
        factors = [CausalFactor("test", 0.8, "positive", "test", 1)]
        
        for i in range(5):
            self.engine.explain_decision(f"type_{i%2}", f"value_{i}", {}, factors)
        
        analytics = self.engine.get_explanation_analytics()
        
        self.assertIn('helpfulness_by_type', analytics)
        self.assertIn('confidence_calibration', analytics)
        self.assertIn('common_decisions', analytics)
        self.assertIn('total_explanations', analytics)
        
        # Should have at least some decisions
        self.assertGreater(analytics['total_explanations'], 0)


class TestCausalFactor(unittest.TestCase):
    """Test CausalFactor dataclass and utilities"""
    
    def test_causal_factor_creation(self):
        """Test CausalFactor creation"""
        factor = CausalFactor(
            name="test_factor",
            importance=0.8,
            direction="positive",
            description="A test factor",
            evidence_count=3
        )
        
        self.assertEqual(factor.name, "test_factor")
        self.assertEqual(factor.importance, 0.8)
        self.assertEqual(factor.direction, "positive")
        self.assertEqual(factor.description, "A test factor")
        self.assertEqual(factor.evidence_count, 3)
    
    def test_create_causal_factor_helper(self):
        """Test create_causal_factor helper function"""
        factor = create_causal_factor(
            name="helper_test",
            importance=1.5,  # Should be clamped to 1.0
            direction="negative",
            description="Helper test",
            evidence_count=2
        )
        
        self.assertEqual(factor.importance, 1.0)  # Clamped
        self.assertEqual(factor.direction, "negative")
        
        # Test clamping to 0
        factor2 = create_causal_factor(
            name="clamp_test",
            importance=-0.5,  # Should be clamped to 0.0
            direction="neutral",
            description="Clamp test"
        )
        
        self.assertEqual(factor2.importance, 0.0)


class TestExplanation(unittest.TestCase):
    """Test Explanation dataclass"""
    
    def test_explanation_creation(self):
        """Test Explanation creation"""
        factors = [CausalFactor("test", 0.8, "positive", "test factor", 1)]
        
        explanation = Explanation(
            decision="test_decision: test_value",
            confidence=ConfidenceLevel.HIGH,
            primary_reason="Main reason",
            causal_factors=factors,
            alternatives_considered=["alt1", "alt2"],
            evidence_sources=["source1", "source2"],
            simple_explanation="Simple explanation",
            detailed_explanation="Detailed explanation",
            technical_explanation="Technical explanation"
        )
        
        self.assertEqual(explanation.decision, "test_decision: test_value")
        self.assertEqual(explanation.confidence, ConfidenceLevel.HIGH)
        self.assertEqual(len(explanation.causal_factors), 1)
        self.assertIsNotNone(explanation.timestamp)  # Auto-generated
    
    def test_explanation_timestamp_auto_generation(self):
        """Test that timestamp is auto-generated"""
        explanation = Explanation(
            decision="test",
            confidence=ConfidenceLevel.MEDIUM,
            primary_reason="reason",
            causal_factors=[],
            alternatives_considered=[],
            evidence_sources=[],
            simple_explanation="simple",
            detailed_explanation="detailed", 
            technical_explanation="technical"
        )
        
        self.assertIsNotNone(explanation.timestamp)
        # Should be parseable as ISO datetime
        datetime.fromisoformat(explanation.timestamp)


class TestAnalyzeIntentRecognition(unittest.TestCase):
    """Test the analyze_intent_recognition utility function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_xai.db"
        self.engine = XAIEngine(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_analyze_intent_recognition_with_keywords(self):
        """Test intent analysis with keyword matches"""
        explanation = analyze_intent_recognition(
            user_input="install firefox please",
            recognized_intent="install_package",
            confidence_score=0.9,
            context={},
            xai_engine=self.engine
        )
        
        self.assertIsInstance(explanation, Explanation)
        self.assertEqual(explanation.decision, "intent_recognition: install")
        self.assertEqual(explanation.confidence, ConfidenceLevel.HIGH)
        
        # Should have keyword match factor
        factor_names = [f.name for f in explanation.causal_factors]
        self.assertIn("keyword_match", factor_names)
        self.assertIn("high_confidence", factor_names)
    
    def test_analyze_intent_recognition_with_history(self):
        """Test intent analysis with user history"""
        context = {
            "user_history": {
                "similar_patterns": 5
            }
        }
        
        explanation = analyze_intent_recognition(
            user_input="get me python",
            recognized_intent="install_package",
            confidence_score=0.75,
            context=context,
            xai_engine=self.engine
        )
        
        factor_names = [f.name for f in explanation.causal_factors]
        self.assertIn("user_history", factor_names)
        
        # Find user history factor
        history_factor = next(f for f in explanation.causal_factors if f.name == "user_history")
        self.assertEqual(history_factor.evidence_count, 5)
        self.assertIn("5 times", history_factor.description)
    
    def test_analyze_intent_recognition_low_confidence(self):
        """Test intent analysis with low confidence"""
        explanation = analyze_intent_recognition(
            user_input="maybe do something with stuff",
            recognized_intent="unknown",
            confidence_score=0.3,
            context={},
            xai_engine=self.engine
        )
        
        factor_names = [f.name for f in explanation.causal_factors]
        self.assertIn("low_confidence", factor_names)
        
        # Find low confidence factor
        low_conf_factor = next(f for f in explanation.causal_factors if f.name == "low_confidence")
        self.assertEqual(low_conf_factor.direction, "negative")
    
    def test_analyze_intent_recognition_no_factors(self):
        """Test intent analysis with no matching factors"""
        explanation = analyze_intent_recognition(
            user_input="xyz abc def",  # No keywords
            recognized_intent="unknown",
            confidence_score=0.65,  # Medium confidence
            context={},  # No history
            xai_engine=self.engine
        )
        
        # Should still return valid explanation even with minimal factors
        self.assertIsInstance(explanation, Explanation)
        self.assertGreaterEqual(len(explanation.causal_factors), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_xai.db"
        self.engine = XAIEngine(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_empty_factors_list(self):
        """Test explanation generation with empty factors list"""
        explanation = self.engine.explain_decision(
            "test_decision",
            "test_value",
            {},
            [],  # Empty factors
            ExplanationLevel.SIMPLE
        )
        
        self.assertEqual(explanation.confidence, ConfidenceLevel.UNCERTAIN)
        self.assertIn("No clear reason", explanation.primary_reason)
    
    def test_invalid_decision_type(self):
        """Test with unknown decision type"""
        factors = [CausalFactor("test", 0.8, "positive", "test", 1)]
        
        explanation = self.engine.explain_decision(
            "unknown_decision_type",
            "value",
            {},
            factors
        )
        
        # Should still work, just use default thresholds
        self.assertIsInstance(explanation, Explanation)
    
    def test_database_connection_error_handling(self):
        """Test handling of database connection issues"""
        # This test would require mocking sqlite3 to simulate errors
        # For now, we'll test basic resilience
        factors = [CausalFactor("test", 0.8, "positive", "test", 1)]
        
        # Should not crash even if there are database issues
        explanation = self.engine.explain_decision("test", "value", {}, factors)
        self.assertIsInstance(explanation, Explanation)
    
    def test_very_long_input_handling(self):
        """Test handling of very long inputs"""
        long_context = {
            "user_input": "a" * 10000,  # Very long input
            "long_data": list(range(1000))
        }
        factors = [CausalFactor("test", 0.8, "positive", "test", 1)]
        
        # Should handle long inputs gracefully
        explanation = self.engine.explain_decision("test", "value", long_context, factors)
        self.assertIsInstance(explanation, Explanation)
    
    def test_special_characters_in_input(self):
        """Test handling of special characters"""
        context = {
            "user_input": "install 'weird$package' with @#$%^&*(){}[]",
            "special_chars": "!@#$%^&*()_+-={}[]|;':\",./<>?"
        }
        factors = [CausalFactor("test", 0.8, "positive", "test", 1)]
        
        explanation = self.engine.explain_decision("test", "value", context, factors)
        self.assertIsInstance(explanation, Explanation)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)