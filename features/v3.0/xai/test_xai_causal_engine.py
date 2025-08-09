"""
Unit tests for the Causal XAI engine
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from nix_humanity.xai.causal_engine import (
    CausalXAI,
    CausalExplanation,
    ExplanationLevel,
    ConfidenceLevel,
    DecisionNode,
    ContributingFactor
)


class TestCausalXAI(unittest.TestCase):
    """Test the Causal XAI engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.xai_engine = CausalXAI()
    
    def test_simple_explanation(self):
        """Test generating a simple explanation"""
        explanation = self.xai_engine.explain_decision(
            "install firefox",
            {"intent": "install_package", "package": "firefox"},
            ExplanationLevel.SIMPLE
        )
        
        self.assertTrue(isinstance(explanation, CausalExplanation))
        self.assertEqual(explanation.decision, "install firefox")
        self.assertEqual(explanation.confidence, ConfidenceLevel.HIGH)
        self.assertIn("install Firefox", explanation.simple_explanation)
        self.assertGreater(len(explanation.contributing_factors), 0)
    
    def test_detailed_explanation(self):
        """Test generating a detailed explanation"""
        explanation = self.xai_engine.explain_decision(
            "install firefox",
            {"intent": "install_package", "package": "firefox"},
            ExplanationLevel.DETAILED
        )
        
        self.assertIsNotNone(explanation.detailed_reasoning)
        self.assertIn("package availability", explanation.detailed_reasoning)
        self.assertIn("system compatibility", explanation.detailed_reasoning)
    
    def test_expert_explanation(self):
        """Test generating an expert-level explanation"""
        explanation = self.xai_engine.explain_decision(
            "install firefox",
            {"intent": "install_package", "package": "firefox"},
            ExplanationLevel.EXPERT
        )
        
        self.assertIsNotNone(explanation.decision_tree)
        self.assertTrue(isinstance(explanation.decision_tree, DecisionNode))
        self.assertIsNotNone(explanation.causal_graph)
        self.assertIn("nodes", explanation.causal_graph)
        self.assertIn("edges", explanation.causal_graph)
    
    def test_confidence_levels(self):
        """Test different confidence level scenarios"""
        # High confidence - exact match
        explanation = self.xai_engine.explain_decision(
            "install firefox",
            {"intent": "install_package", "package": "firefox", "exact_match": True}
        )
        self.assertEqual(explanation.confidence, ConfidenceLevel.HIGH)
        
        # Medium confidence - fuzzy match
        explanation = self.xai_engine.explain_decision(
            "install fierfix",
            {"intent": "install_package", "package": "firefox", "fuzzy_match": True}
        )
        self.assertEqual(explanation.confidence, ConfidenceLevel.MEDIUM)
        
        # Low confidence - ambiguous
        explanation = self.xai_engine.explain_decision(
            "get that thing",
            {"intent": "unknown", "ambiguous": True}
        )
        self.assertEqual(explanation.confidence, ConfidenceLevel.LOW)
    
    def test_alternative_paths(self):
        """Test generation of alternative paths"""
        explanation = self.xai_engine.explain_decision(
            "install firefox",
            {"intent": "install_package", "package": "firefox"}
        )
        
        self.assertGreater(len(explanation.alternative_paths), 0)
        
        # Check alternatives contain expected options
        alternatives = [alt["decision"] for alt in explanation.alternative_paths]
        self.assertTrue(any("declarative" in alt.lower() for alt in alternatives))
        self.assertTrue(any("temporary" in alt.lower() for alt in alternatives))
    
    def test_contributing_factors(self):
        """Test contributing factor analysis"""
        explanation = self.xai_engine.explain_decision(
            "update system",
            {"intent": "system_update", "current_time": "14:00"}
        )
        
        factors = explanation.contributing_factors
        self.assertGreater(len(factors), 0)
        
        # Verify factor structure
        for factor in factors:
            self.assertTrue(isinstance(factor, ContributingFactor))
            self.assertTrue(0 < factor.confidence <= 1)
            self.assertTrue(factor.description)
            self.assertTrue(isinstance(factor.contributing_factors, list))
    
    def test_uncertainty_handling(self):
        """Test handling of uncertain decisions"""
        explanation = self.xai_engine.explain_decision(
            "do something",
            {"intent": "unknown", "vague": True}
        )
        
        self.assertEqual(explanation.confidence, ConfidenceLevel.LOW)
        self.assertGreater(len(explanation.uncertainty_factors), 0)
        self.assertIn("vague input", str(explanation.uncertainty_factors).lower())
    
    def test_system_state_impact(self):
        """Test how system state affects explanations"""
        # Normal state
        normal_explanation = self.xai_engine.explain_decision(
            "install firefox",
            {"intent": "install_package", "system_state": "normal"}
        )
        
        # Degraded state
        degraded_explanation = self.xai_engine.explain_decision(
            "install firefox",
            {"intent": "install_package", "system_state": "low_memory", "low_memory": True}
        )
        
        # Degraded state should have lower confidence
        self.assertLess(degraded_explanation.confidence_score, normal_explanation.confidence_score)
    
    def test_causal_pattern_matching(self):
        """Test causal pattern recognition"""
        patterns_tested = [
            ("install firefox", "install_package"),
            ("update my system", "system_update"),
            ("why is wifi not working", "network_diagnosis"),
            ("show disk usage", "system_info")
        ]
        
        for decision, expected_pattern in patterns_tested:
            explanation = self.xai_engine.explain_decision(
                decision,
                {"intent": expected_pattern}
            )
            
            # Should recognize the pattern
            self.assertTrue(any(
                expected_pattern in factor.description.lower() 
                for factor in explanation.contributing_factors
            ))
    
    def test_temporal_reasoning(self):
        """Test temporal aspects of reasoning"""
        # Late night system update
        late_explanation = self.xai_engine.explain_decision(
            "update system",
            {"intent": "system_update", "current_hour": 2}
        )
        
        # Business hours system update  
        business_explanation = self.xai_engine.explain_decision(
            "update system",
            {"intent": "system_update", "current_hour": 14}
        )
        
        # Late night should have different reasoning
        self.assertIn("unusual time", late_explanation.detailed_reasoning.lower())
        self.assertLess(late_explanation.confidence_score, business_explanation.confidence_score)
    
    def test_decision_tree_generation(self):
        """Test decision tree generation for expert level"""
        explanation = self.xai_engine.explain_decision(
            "install firefox declaratively",
            {"intent": "install_package", "method": "declarative"},
            ExplanationLevel.EXPERT
        )
        
        tree = explanation.decision_tree
        self.assertIsNotNone(tree)
        self.assertEqual(tree.decision, "install firefox declaratively")
        self.assertGreater(len(tree.children), 0)
        
        # Check tree has expected structure
        self.assertTrue(any(child.decision == "Check if already installed" for child in tree.children))
        self.assertTrue(any(child.decision == "Verify package availability" for child in tree.children))
    
    def test_explanation_completeness(self):
        """Test that explanations are complete at all levels"""
        levels = [ExplanationLevel.SIMPLE, ExplanationLevel.DETAILED, ExplanationLevel.EXPERT]
        
        for level in levels:
            explanation = self.xai_engine.explain_decision(
                "install firefox",
                {"intent": "install_package"},
                level
            )
            
            # All explanations should have basic fields
            self.assertTrue(explanation.decision)
            self.assertTrue(explanation.confidence)
            self.assertTrue(explanation.timestamp)
            self.assertTrue(explanation.contributing_factors)
            
            # Level-specific checks
            if level == ExplanationLevel.SIMPLE:
                self.assertTrue(explanation.simple_explanation)
            elif level == ExplanationLevel.DETAILED:
                self.assertTrue(explanation.detailed_reasoning)
            elif level == ExplanationLevel.EXPERT:
                self.assertTrue(explanation.decision_tree)
                self.assertTrue(explanation.causal_graph)


class TestDecisionNode(unittest.TestCase):
    """Test the DecisionNode class"""
    
    def test_node_creation(self):
        """Test creating decision nodes"""
        node = DecisionNode(
            decision="Install Firefox",
            confidence=0.9,
            reasoning="User requested Firefox installation"
        )
        
        self.assertEqual(node.decision, "Install Firefox")
        self.assertEqual(node.confidence, 0.9)
        self.assertEqual(node.reasoning, "User requested Firefox installation")
        self.assertEqual(node.children, [])
    
    def test_node_hierarchy(self):
        """Test building node hierarchies"""
        root = DecisionNode("Install Package", 0.95)
        child1 = DecisionNode("Check availability", 0.9)
        child2 = DecisionNode("Verify permissions", 0.85)
        
        root.children = [child1, child2]
        
        self.assertEqual(len(root.children), 2)
        self.assertEqual(root.children[0].decision, "Check availability")
        self.assertEqual(root.children[1].decision, "Verify permissions")


class TestContributingFactor(unittest.TestCase):
    """Test the ContributingFactor class"""
    
    def test_factor_creation(self):
        """Test creating contributing factors"""
        factor = ContributingFactor(
            description="Package exists in nixpkgs",
            confidence=0.95,
            contributing_factors=["nixpkgs index checked", "package metadata valid"]
        )
        
        self.assertEqual(factor.description, "Package exists in nixpkgs")
        self.assertEqual(factor.confidence, 0.95)
        self.assertEqual(len(factor.contributing_factors), 2)
    
    def test_factor_confidence_bounds(self):
        """Test confidence bounds validation"""
        # Should accept valid confidence
        factor = ContributingFactor("Test", 0.5)
        self.assertEqual(factor.confidence, 0.5)
        
        # Should handle edge cases
        factor_low = ContributingFactor("Test", 0.0)
        self.assertEqual(factor_low.confidence, 0.0)
        
        factor_high = ContributingFactor("Test", 1.0)
        self.assertEqual(factor_high.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
