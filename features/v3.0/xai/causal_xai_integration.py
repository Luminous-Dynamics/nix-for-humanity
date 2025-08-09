#!/usr/bin/env python3
"""
from typing import Dict, Optional
Causal XAI Integration for ask-nix
Seamlessly integrates causal explanations into the existing command flow
"""

import sys
import os
from typing import Dict, Optional, Any
from pathlib import Path

# Add scripts directory to path
script_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, script_dir)

# Import the causal XAI engine
from causal_xai_engine import CausalXAIEngine, ExplanationDepth, CausalExplanation


class XAIEnhancedKnowledgeEngine:
    """Wrapper that adds causal explanations to the existing knowledge engine"""
    
    def __init__(self, base_engine, enable_xai: bool = True):
        self.base_engine = base_engine
        self.enable_xai = enable_xai
        self.xai_engine = CausalXAIEngine() if enable_xai else None
        
        # Default explanation depth based on personality
        self.depth_mapping = {
            'minimal': ExplanationDepth.SIMPLE,
            'friendly': ExplanationDepth.STANDARD,
            'encouraging': ExplanationDepth.STANDARD,
            'technical': ExplanationDepth.TECHNICAL,
            'symbiotic': ExplanationDepth.DETAILED
        }
    
    def extract_intent(self, query: str) -> Dict:
        """Extract intent with XAI confidence scoring"""
        # Use base engine for intent extraction
        intent = self.base_engine.extract_intent(query)
        
        # Add XAI confidence if enabled
        if self.enable_xai and self.xai_engine:
            context = {'explicit_request': True}
            confidence = self.xai_engine._calculate_confidence(intent, context)
            intent['xai_confidence'] = confidence
        
        return intent
    
    def get_solution(self, intent: Dict) -> Dict:
        """Get solution with causal explanation"""
        # Get base solution
        solution = self.base_engine.get_solution(intent)
        
        # Add causal explanation if enabled
        if self.enable_xai and self.xai_engine and solution.get('found', False):
            context = {
                'explicit_request': True,
                'user_history': hasattr(self.base_engine, 'db_path')
            }
            
            # Generate explanation
            explanation = self.xai_engine.explain_intent(
                intent, 
                context,
                ExplanationDepth.STANDARD
            )
            
            # Add to solution
            solution['explanation'] = explanation
            solution['quick_why'] = self.xai_engine.get_quick_explanation(
                intent.get('action', 'unknown'),
                intent.get('package', '')
            )
        
        return solution
    
    def format_response(self, intent: Dict, solution: Dict, personality: str = 'friendly') -> str:
        """Format response with optional causal explanation"""
        # Get base response
        base_response = self.base_engine.format_response(intent, solution)
        
        # Add explanation if available and XAI is enabled
        if self.enable_xai and 'explanation' in solution:
            explanation = solution['explanation']
            depth = self.depth_mapping.get(personality, ExplanationDepth.STANDARD)
            
            # Format explanation for display
            explanation_text = self.xai_engine.format_explanation_for_display(
                explanation, 
                depth,
                self._personality_to_persona(personality)
            )
            
            # Insert explanation into response
            if personality == 'minimal':
                # Just add the quick why for minimal
                base_response += f"\n\n💡 {solution.get('quick_why', '')}"
            else:
                # Add formatted explanation
                base_response += f"\n\n**Why am I suggesting this?**\n{explanation_text}"
        
        return base_response
    
    def _personality_to_persona(self, personality: str) -> Optional[str]:
        """Map personality style to persona for language adjustment"""
        mapping = {
            'friendly': None,  # Default, no adjustment
            'encouraging': 'maya_adhd',  # Concise for ADHD
            'minimal': 'dr_sarah',  # Technical
            'technical': 'dr_sarah',  # Technical
            'symbiotic': None  # Default
        }
        return mapping.get(personality)
    
    def explain_error(self, error: str, intent: Dict) -> Dict[str, Any]:
        """Provide causal explanation for errors"""
        if not self.enable_xai or not self.xai_engine:
            return {
                'message': error,
                'suggestions': ['Check the error message', 'Try again']
            }
        
        # Get XAI error explanation
        context = {
            'intent': intent,
            'error': error
        }
        
        error_explanation = self.xai_engine.explain_error(error, context)
        
        return {
            'message': error,
            'why': error_explanation.get('why', 'Unknown error'),
            'suggestions': error_explanation.get('how_to_fix', []),
            'confidence': error_explanation.get('confidence', 0.5),
            'understood': error_explanation.get('understood', False)
        }


def add_xai_to_response(response: str, intent: Dict, personality: str = 'friendly', 
                       show_confidence: bool = True, show_factors: bool = False) -> str:
    """Standalone function to add XAI explanations to any response"""
    
    xai_engine = CausalXAIEngine()
    
    # Determine explanation depth
    depth_map = {
        'minimal': ExplanationDepth.SIMPLE,
        'friendly': ExplanationDepth.STANDARD,
        'encouraging': ExplanationDepth.STANDARD,
        'technical': ExplanationDepth.DETAILED,
        'symbiotic': ExplanationDepth.DETAILED
    }
    depth = depth_map.get(personality, ExplanationDepth.STANDARD)
    
    # Generate explanation
    context = {'explicit_request': True}
    explanation = xai_engine.explain_intent(intent, context, depth)
    
    # Quick explanation for action
    quick_why = xai_engine.get_quick_explanation(
        intent.get('action', 'unknown'),
        intent.get('package', '')
    )
    
    # Add to response based on personality
    if personality == 'minimal':
        return f"{response}\n\n💡 {quick_why}"
    
    # Format explanation
    xai_engine.user_preferences['include_confidence'] = show_confidence
    xai_engine.user_preferences['show_alternatives'] = (depth != ExplanationDepth.SIMPLE)
    
    explanation_text = xai_engine.format_explanation_for_display(
        explanation,
        depth,
        None  # No persona adjustment needed
    )
    
    # Combine
    enhanced_response = f"{response}\n\n"
    
    if show_confidence and explanation.confidence < 0.7:
        enhanced_response += "⚠️ Note: I'm somewhat uncertain about this, but here's my best analysis:\n\n"
    
    enhanced_response += explanation_text
    
    return enhanced_response


def create_xai_enhanced_engine(base_engine_class, enable_xai: bool = True):
    """Factory function to create XAI-enhanced version of any knowledge engine"""
    
    class XAIEnhanced(base_engine_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Store references to parent methods to avoid recursion
            self._parent_extract_intent = super().extract_intent
            self._parent_get_solution = super().get_solution
            self._parent_format_response = super().format_response
            
            # Create a minimal wrapper that uses parent methods
            parent_wrapper = type('ParentWrapper', (), {
                'extract_intent': self._parent_extract_intent,
                'get_solution': self._parent_get_solution,
                'format_response': self._parent_format_response,
                'db_path': getattr(self, 'db_path', None)
            })()
            
            self.xai_wrapper = XAIEnhancedKnowledgeEngine(parent_wrapper, enable_xai)
        
        def extract_intent(self, query: str) -> Dict:
            return self.xai_wrapper.extract_intent(query)
        
        def get_solution(self, intent: Dict) -> Dict:
            return self.xai_wrapper.get_solution(intent)
        
        def format_response(self, intent: Dict, solution: Dict, personality: str = 'friendly') -> str:
            # Check if we have a personality parameter in the solution
            if 'personality' in solution:
                personality = solution['personality']
            return self.xai_wrapper.format_response(intent, solution, personality)
    
    return XAIEnhanced


# Convenience function for testing
def demo_xai_explanation():
    """Demonstrate XAI explanations"""
    from nix_knowledge_engine import NixOSKnowledgeEngine
    
    # Create enhanced engine
    XAIEngine = create_xai_enhanced_engine(NixOSKnowledgeEngine)
    engine = XAIEngine()
    
    # Test queries
    test_queries = [
        ("install firefox", 'minimal'),
        ("update my system", 'friendly'),
        ("why should I use nix profile instead of nix-env?", 'technical'),
        ("remove unused packages", 'encouraging')
    ]
    
    print("🧠 Causal XAI Demonstration\n" + "="*50 + "\n")
    
    for query, personality in test_queries:
        print(f"Query: '{query}' (Personality: {personality})")
        print("-" * 40)
        
        # Extract intent
        intent = engine.extract_intent(query)
        print(f"Intent: {intent.get('action')} (Confidence: {intent.get('xai_confidence', 0):.2f})")
        
        # Get solution with explanation
        solution = engine.get_solution(intent)
        
        # Format response
        response = engine.format_response(intent, solution, personality)
        print(response)
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    demo_xai_explanation()