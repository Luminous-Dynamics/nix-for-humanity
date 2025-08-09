#!/usr/bin/env python3
"""
Enhanced NixOS Knowledge Engine with AI Licensing Advisor
Combines NixOS knowledge with AI model licensing guidance
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nix_knowledge_engine import NixOSKnowledgeEngine
from ai_licensing_advisor_wrapper import AILicensingAdvisor

class EnhancedNixOSKnowledgeEngine(NixOSKnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.ai_advisor = AILicensingAdvisor()
        
    def extract_intent(self, query: str) -> dict:
        """Extended intent extraction including AI licensing queries"""
        query_lower = query.lower()
        
        # AI licensing patterns
        if any(word in query_lower for word in ['license', 'licensing', 'commercial', 'legal', 'copyright']):
            # Check if it's about AI models
            if any(word in query_lower for word in ['ai', 'model', 'llm', 'gpt', 'llama', 'mistral', 
                                                     'stable diffusion', 'whisper', 'bert', 'neural']):
                # Extract model name if present
                model_name = None
                ai_models = ['llama', 'mistral', 'gpt', 'bert', 'whisper', 'stable-diffusion', 
                            'falcon', 'gemma', 'claude', 'yolo', 'clip', 'musicgen']
                
                for model in ai_models:
                    if model in query_lower:
                        model_name = model
                        break
                        
                return {
                    'action': 'check_ai_license',
                    'model': model_name,
                    'query': query
                }
                
        # AI model recommendation patterns
        elif any(phrase in query_lower for phrase in ['which ai', 'what model', 'recommend model', 
                                                      'best model for', 'ai for']):
            use_case = query  # Full query is the use case
            return {
                'action': 'recommend_ai_model',
                'use_case': use_case,
                'query': query
            }
            
        # License compatibility patterns
        elif 'compatible' in query_lower and any(word in query_lower for word in ['license', 'gpl', 'mit', 'apache']):
            return {
                'action': 'check_license_compatibility',
                'query': query
            }
            
        # Fall back to original intent extraction
        return super().extract_intent(query)
        
    def get_solution(self, intent: dict) -> dict:
        """Extended solution getter including AI licensing"""
        action = intent.get('action', 'unknown')
        
        # Handle AI licensing queries
        if action == 'check_ai_license':
            model_name = intent.get('model')
            if not model_name:
                # Try to extract from query
                words = intent['query'].lower().split()
                for word in words:
                    if self.ai_advisor.check_model_license(word):
                        model_name = word
                        break
                        
            if model_name:
                model_info = self.ai_advisor.check_model_license(model_name)
                if model_info:
                    return {
                        'found': True,
                        'action': 'ai_license',
                        'model_info': model_info,
                        'formatted': self.ai_advisor.format_license_advice(model_info)
                    }
                else:
                    return {
                        'found': True,
                        'action': 'ai_license',
                        'suggestion': f"I don't have licensing information for '{model_name}'. Try checking the model's official documentation or repository."
                    }
            else:
                return {
                    'found': True,
                    'action': 'ai_license',
                    'suggestion': "Please specify which AI model you'd like licensing information for. For example: 'What's the license for Llama 2?' or 'Can I use Mistral commercially?'"
                }
                
        elif action == 'recommend_ai_model':
            use_case = intent.get('use_case', '')
            recommendations = self.ai_advisor.recommend_models_for_use_case(use_case)
            
            return {
                'found': True,
                'action': 'ai_recommendation',
                'recommendations': recommendations,
                'use_case': use_case
            }
            
        elif action == 'check_license_compatibility':
            # Extract license names from query
            query_lower = intent['query'].lower()
            licenses = []
            
            known_licenses = ['mit', 'apache', 'gpl', 'agpl', 'bsd', 'cc-by', 'cc0']
            for license in known_licenses:
                if license in query_lower:
                    licenses.append(license.upper() if len(license) <= 3 else f"{license.title()}")
                    
            if len(licenses) >= 2:
                compat = self.ai_advisor.check_license_compatibility(licenses[0], licenses[1])
                return {
                    'found': True,
                    'action': 'license_compatibility',
                    'license_a': licenses[0],
                    'license_b': licenses[1],
                    'compatibility': compat
                }
            else:
                return {
                    'found': True,
                    'action': 'license_compatibility',
                    'suggestion': "Please specify two licenses to check compatibility. For example: 'Is MIT compatible with GPL?'"
                }
                
        # Fall back to original solution getter
        return super().get_solution(intent)
        
    def format_response(self, intent: dict, solution: dict) -> str:
        """Extended response formatter including AI licensing"""
        if not solution.get('found'):
            return solution.get('suggestion', "I don't understand that query.")
            
        action = solution.get('action')
        
        if action == 'ai_license':
            if solution.get('formatted'):
                return solution['formatted']
            else:
                return solution.get('suggestion', "No licensing information available.")
                
        elif action == 'ai_recommendation':
            recommendations = solution.get('recommendations', [])
            use_case = solution.get('use_case', 'general use')
            
            if not recommendations:
                return f"No models found for use case: {use_case}"
                
            response = f"🤖 **AI Model Recommendations for: {use_case}**\n\n"
            
            # Group by license type
            safe_commercial = []
            conditional = []
            non_commercial = []
            
            for model in recommendations:
                if "Yes - Safe" in model['commercial_use']:
                    safe_commercial.append(model)
                elif "Conditional" in model['commercial_use'] or "copyleft" in model['commercial_use'].lower():
                    conditional.append(model)
                else:
                    non_commercial.append(model)
                    
            if safe_commercial:
                response += "✅ **Fully Commercial-Friendly Models:**\n"
                for model in safe_commercial[:5]:  # Limit to top 5
                    response += f"- **{model['model_name']}** ({model['license']}) - {model['model_type']}\n"
                    if model.get('notes'):
                        response += f"  💡 {model['notes']}\n"
                response += "\n"
                
            if conditional:
                response += "⚠️ **Conditional/Restricted Models:**\n"
                for model in conditional[:3]:
                    response += f"- **{model['model_name']}** ({model['license']}) - {model['commercial_use']}\n"
                    if model.get('notes'):
                        response += f"  💡 {model['notes']}\n"
                response += "\n"
                
            if non_commercial and 'research' in use_case.lower():
                response += "🎓 **Research-Only Models:**\n"
                for model in non_commercial[:3]:
                    response += f"- **{model['model_name']}** ({model['license']})\n"
                    
            response += "\n💡 **Tip**: Always verify the license terms before deploying in production!"
            
            return response
            
        elif action == 'license_compatibility':
            compat = solution.get('compatibility', {})
            license_a = solution.get('license_a', 'License A')
            license_b = solution.get('license_b', 'License B')
            
            response = f"🔍 **License Compatibility Check**\n\n"
            response += f"Checking: **{license_a}** ↔️ **{license_b}**\n\n"
            
            if compat.get('compatible') is True:
                response += "✅ **Compatible**: These licenses can be used together\n"
            elif compat.get('compatible') is False:
                response += "❌ **Incompatible**: These licenses cannot be combined\n"
            else:
                response += "❓ **Unknown**: No compatibility information available\n"
                
            if compat.get('notes'):
                response += f"\n💡 **Details**: {compat['notes']}"
                
            return response
            
        # Fall back to original formatter
        return super().format_response(intent, solution)


def main():
    """Test the enhanced knowledge engine"""
    engine = EnhancedNixOSKnowledgeEngine()
    
    test_queries = [
        # Original NixOS queries
        "How do I install Firefox?",
        "Update my system",
        
        # New AI licensing queries
        "What's the license for Llama 2?",
        "Can I use Mistral-7B commercially?",
        "Which AI model should I use for a commercial SaaS application?",
        "Is MIT compatible with GPL?",
        "What AI models are safe for my startup?",
        "Tell me about Stable Diffusion licensing",
        "Can I use YOLO v8 in a proprietary product?",
    ]
    
    print("🧠 Enhanced NixOS Knowledge Engine with AI Licensing\n")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 50)
        
        # Extract intent
        intent = engine.extract_intent(query)
        print(f"🎯 Intent: {intent['action']}")
        
        # Get solution
        solution = engine.get_solution(intent)
        
        # Format response
        response = engine.format_response(intent, solution)
        print(f"\n💬 Response:\n{response}")
        print("=" * 60)


if __name__ == "__main__":
    main()