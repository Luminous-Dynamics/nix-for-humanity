#!/usr/bin/env python3
"""
Simple test of the Causal XAI engine
Demonstrates explanations without full ask-nix flow
"""

import sys
import os

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Import our engines
from causal_xai_engine import CausalXAIEngine, ExplanationDepth
from nix_knowledge_engine import NixOSKnowledgeEngine

def test_xai():
    """Test XAI explanations for common NixOS operations"""
    
    print("🧠 Causal XAI Engine Test")
    print("=" * 60)
    
    # Initialize engines
    xai_engine = CausalXAIEngine()
    knowledge_engine = NixOSKnowledgeEngine()
    
    # Test scenarios
    test_cases = [
        {
            'query': 'install firefox',
            'depth': ExplanationDepth.SIMPLE,
            'persona': 'grandma_rose'
        },
        {
            'query': 'update my system',
            'depth': ExplanationDepth.STANDARD,
            'persona': None
        },
        {
            'query': 'remove unused packages',
            'depth': ExplanationDepth.DETAILED,
            'persona': 'maya_adhd'
        },
        {
            'query': 'why is my disk full?',
            'depth': ExplanationDepth.TECHNICAL,
            'persona': 'dr_sarah'
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 Query: '{test['query']}'")
        print(f"   Depth: {test['depth'].value}")
        if test['persona']:
            print(f"   Persona: {test['persona']}")
        print("-" * 60)
        
        # Extract intent
        intent = knowledge_engine.extract_intent(test['query'])
        print(f"\n🎯 Detected Intent: {intent.get('action', 'unknown')}")
        if intent.get('package'):
            print(f"   Package: {intent['package']}")
        
        # Generate explanation
        context = {
            'explicit_request': True,
            'channels_updated_recently': True,
            'similar_success_rate': 0.85,
            'user_did_before': test['query'] == 'install firefox'
        }
        
        explanation = xai_engine.explain_intent(intent, context, test['depth'])
        
        # Format and display
        formatted = xai_engine.format_explanation_for_display(
            explanation, 
            test['depth'],
            test['persona']
        )
        
        print(f"\n💡 Explanation:\n{formatted}")
        print("\n" + "=" * 60)
    
    # Test error explanation
    print("\n🚨 Error Explanation Test")
    print("-" * 60)
    
    error = "error: attribute 'firefox' missing"
    error_explanation = xai_engine.explain_error(error, {'action': 'install', 'package': 'firefox'})
    
    print(f"Error: {error}")
    print(f"\n❓ Why: {error_explanation['why']}")
    print("\n💡 How to fix:")
    for fix in error_explanation['how_to_fix']:
        print(f"   • {fix}")
    print(f"\n🎯 Confidence: {error_explanation['confidence']:.0%}")

def test_xai_integration():
    """Test XAI integration with knowledge engine"""
    
    print("\n\n🔗 Testing XAI Integration")
    print("=" * 60)
    
    from causal_xai_integration import create_xai_enhanced_engine
    
    # Create enhanced engine
    XAIEngine = create_xai_enhanced_engine(NixOSKnowledgeEngine)
    engine = XAIEngine()
    
    # Test with different personalities
    personalities = ['minimal', 'friendly', 'technical', 'symbiotic']
    query = "install vscode"
    
    for personality in personalities:
        print(f"\n🎭 Personality: {personality}")
        print("-" * 40)
        
        # Process query
        intent = engine.extract_intent(query)
        solution = engine.get_solution(intent)
        response = engine.format_response(intent, solution, personality)
        
        print(response)
        print()

if __name__ == "__main__":
    test_xai()
    test_xai_integration()