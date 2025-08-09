#!/usr/bin/env python3
"""
Enhanced NixOS Knowledge Engine with AI Environment Architect integration
Extends the base knowledge engine with AI/ML environment generation capabilities
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import base modules
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from nix_knowledge_engine import NixOSKnowledgeEngine
from ai_environment_integration import AIEnvironmentIntegration

class EnhancedNixOSKnowledgeEngine(NixOSKnowledgeEngine):
    """Extended knowledge engine with AI environment generation"""
    
    def __init__(self):
        super().__init__()
        self.ai_integration = AIEnvironmentIntegration()
        
        # Add AI environment patterns to knowledge base
        self._add_ai_environment_knowledge()
    
    def _add_ai_environment_knowledge(self):
        """Add AI/ML environment knowledge to database"""
        conn = self.db_connect()
        c = conn.cursor()
        
        # Add AI environment solutions
        ai_solutions = [
            ('create_ai_environment', 'environment', 
             'Generate a complete Nix flake for AI/ML development',
             'nix develop # After generating flake.nix',
             'Creates optimized environment with all dependencies',
             'install_package,search_package'),
             
            ('setup_jupyter', 'environment',
             'Create Jupyter notebook environment with Nix',
             'Generated via AI Environment Architect',
             'Pure Nix approach for data science',
             'create_ai_environment'),
             
            ('setup_llm_local', 'environment',
             'Set up local LLM environment with CUDA support',
             'Includes llama-cpp-python and dependencies',
             'Run large language models locally',
             'create_ai_environment'),
             
            ('setup_ml_stack', 'environment',
             'Create complete ML development stack',
             'TensorFlow, PyTorch, or scikit-learn',
             'Everything needed for machine learning',
             'create_ai_environment')
        ]
        
        for solution in ai_solutions:
            c.execute('''
                INSERT OR IGNORE INTO solutions 
                (intent, category, solution, example, explanation, related)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', solution)
        
        conn.commit()
        conn.close()
    
    def extract_intent(self, query: str) -> Dict:
        """Extended intent extraction including AI environments"""
        query_lower = query.lower()
        
        # Check if it's an AI environment request first
        if self.ai_integration.is_environment_request(query):
            return {
                'action': 'create_ai_environment',
                'query': query,
                'subtype': self._determine_ai_subtype(query)
            }
        
        # Fall back to parent intent extraction
        return super().extract_intent(query)
    
    def _determine_ai_subtype(self, query: str) -> str:
        """Determine specific type of AI environment requested"""
        query_lower = query.lower()
        
        if 'jupyter' in query_lower or 'notebook' in query_lower:
            return 'jupyter'
        elif 'llama' in query_lower or 'local llm' in query_lower:
            return 'llm_local'
        elif 'stable diffusion' in query_lower or 'image' in query_lower:
            return 'stable_diffusion'
        elif 'tensorflow' in query_lower or 'keras' in query_lower:
            return 'tensorflow'
        elif 'pytorch' in query_lower or 'torch' in query_lower:
            return 'pytorch'
        elif 'scikit' in query_lower or 'sklearn' in query_lower:
            return 'sklearn'
        else:
            return 'general'
    
    def get_solution(self, intent: Dict) -> Dict:
        """Extended solution handling for AI environments"""
        action = intent.get('action', 'unknown')
        
        if action == 'create_ai_environment':
            # Handle AI environment generation
            response = self.ai_integration.handle_environment_request(intent['query'])
            
            return {
                'found': True,
                'action': 'create_ai_environment',
                'solution': 'AI/ML environment configuration generated',
                'response': response,
                'subtype': intent.get('subtype', 'general')
            }
        
        # Fall back to parent solution handling
        return super().get_solution(intent)
    
    def format_response(self, intent: Dict, solution: Dict) -> str:
        """Extended response formatting for AI environments"""
        if intent['action'] == 'create_ai_environment' and solution['found']:
            # Use AI integration formatter
            response = solution['response']
            return self.ai_integration.format_response(response)
        
        # Fall back to parent formatting
        return super().format_response(intent, solution)
    
    def db_connect(self):
        """Get database connection"""
        import sqlite3
        return sqlite3.connect(self.db_path)


def main():
    """Test the enhanced engine"""
    engine = EnhancedNixOSKnowledgeEngine()
    
    test_queries = [
        # Traditional queries
        "How do I install Firefox?",
        "Update my system",
        
        # AI environment queries
        "Create an AI environment with PyTorch and CUDA",
        "I want to set up a Jupyter notebook for machine learning",
        "Help me run Llama locally",
        "Set up stable diffusion environment",
        "Create a TensorFlow development environment"
    ]
    
    print("🧠 Enhanced NixOS Knowledge Engine Test\n")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 50)
        
        # Extract intent
        intent = engine.extract_intent(query)
        print(f"🎯 Intent: {intent['action']}")
        if intent.get('subtype'):
            print(f"📌 Subtype: {intent['subtype']}")
        
        # Get solution
        solution = engine.get_solution(intent)
        
        # Format response
        response = engine.format_response(intent, solution)
        print(f"\n💬 Response:\n{response}")
        print("=" * 60)


if __name__ == "__main__":
    main()