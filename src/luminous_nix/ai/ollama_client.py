"""
Ollama integration for AI-powered natural language understanding
"""

import subprocess
import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

class OllamaClient:
    """Client for interacting with Ollama AI models"""
    
    def __init__(self):
        """Initialize Ollama client with model selection based on query type"""
        self.models = {
            'quick': 'nix-quick:latest',      # Fast responses (637 MB)
            'coder': 'nix-coder:latest',      # Code/config help (1.9 GB)
            'empathy': 'nix-empathy:latest',  # User support (2.0 GB)
            'expert': 'nix-expert:latest',    # Complex issues (4.4 GB)
            'general': 'mistral:7b',          # General purpose (4.4 GB)
            'tiny': 'qwen:0.5b',              # Ultra-fast (394 MB)
        }
        
        # Select default model based on available memory
        self.default_model = self._select_default_model()
        self.timeout = 30  # seconds
        
    def _select_default_model(self) -> str:
        """Select best model based on system resources"""
        # For now, use the quick NixOS model as default
        # In future, could check available RAM/GPU
        return self.models.get('quick', 'qwen:0.5b')
    
    def _select_model_for_query(self, query: str) -> str:
        """Select the best model based on query type"""
        query_lower = query.lower()
        
        # Quick queries - use fast model
        if any(word in query_lower for word in ['install', 'remove', 'list', 'search']):
            return self.models['quick']
        
        # Code/config queries - use coder model
        if any(word in query_lower for word in ['config', 'configuration', 'code', 'script', 'flake']):
            return self.models['coder']
        
        # Error/help queries - use empathy model
        if any(word in query_lower for word in ['error', 'help', 'why', "doesn't work", 'broken']):
            return self.models['empathy']
        
        # Complex system queries - use expert model
        if any(word in query_lower for word in ['kernel', 'driver', 'boot', 'network', 'systemd']):
            return self.models['expert']
        
        # Default to quick model
        return self.models['quick']
    
    def ask(self, prompt: str, model: Optional[str] = None, context: Optional[Dict] = None) -> Optional[str]:
        """
        Ask Ollama a question and get a response
        
        Args:
            prompt: The question or command to process
            model: Optional specific model to use
            context: Optional context about the user/system
            
        Returns:
            The AI response or None if failed
        """
        # Select model if not specified
        if not model:
            model = self._select_model_for_query(prompt)
        
        # Build the full prompt with context
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            # Use ollama run command for simplicity
            result = subprocess.run(
                ['ollama', 'run', model, full_prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
            else:
                # Fallback to simpler model if failed
                if model != self.models['tiny']:
                    return self.ask(prompt, model=self.models['tiny'], context=context)
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ AI response timed out, trying faster model...")
            if model != self.models['tiny']:
                return self.ask(prompt, model=self.models['tiny'], context=context)
            return None
            
        except Exception as e:
            if os.environ.get('LUMINOUS_VERBOSE'):
                print(f"❌ Ollama error: {e}")
            return None
    
    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Build a contextualized prompt for better AI responses"""
        
        # Start with system context
        full_prompt = "You are a helpful NixOS assistant. "
        
        # Add persona context if specified
        if context and 'persona' in context:
            persona_prompts = {
                'grandma': "Explain things simply and gently, avoiding technical jargon. ",
                'developer': "Provide technical details and code examples. ",
                'beginner': "Explain step by step with clear examples. ",
                'expert': "Be concise and technical. "
            }
            full_prompt += persona_prompts.get(context['persona'], "")
        
        # Add the user's question
        full_prompt += f"\n\nUser question: {prompt}"
        
        # Add instruction for response format
        full_prompt += "\n\nProvide a clear, helpful response. If this is a command, explain what it will do first."
        
        return full_prompt
    
    def parse_intent(self, query: str) -> Dict[str, Any]:
        """
        Use AI to understand the user's intent
        
        Returns:
            Dictionary with:
            - intent: The primary intent (install, search, configure, etc.)
            - entities: Extracted entities (package names, etc.)
            - confidence: How confident the AI is
            - suggestion: What to do next
        """
        prompt = f"""Analyze this NixOS query and return JSON with: intent, entities, confidence, suggestion.
Query: {query}

Example response:
{{"intent": "install", "entities": ["firefox"], "confidence": 0.9, "suggestion": "Install Firefox browser"}}

Response:"""
        
        response = self.ask(prompt, model=self.models['tiny'])
        
        if response:
            try:
                # Try to parse JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        
        # Fallback to basic parsing
        return self._basic_intent_parsing(query)
    
    def _basic_intent_parsing(self, query: str) -> Dict[str, Any]:
        """Fallback basic intent parsing without AI"""
        query_lower = query.lower()
        
        if 'install' in query_lower:
            return {
                'intent': 'install',
                'entities': self._extract_package_name(query_lower, 'install'),
                'confidence': 0.7,
                'suggestion': 'Install package'
            }
        elif 'search' in query_lower or 'find' in query_lower:
            return {
                'intent': 'search',
                'entities': self._extract_search_term(query_lower),
                'confidence': 0.7,
                'suggestion': 'Search for packages'
            }
        elif 'remove' in query_lower or 'uninstall' in query_lower:
            return {
                'intent': 'remove',
                'entities': self._extract_package_name(query_lower, 'remove'),
                'confidence': 0.7,
                'suggestion': 'Remove package'
            }
        else:
            return {
                'intent': 'unknown',
                'entities': [],
                'confidence': 0.3,
                'suggestion': 'Please clarify what you want to do'
            }
    
    def _extract_package_name(self, query: str, action: str) -> List[str]:
        """Extract package name from query"""
        words = query.split()
        packages = []
        
        # Find the action word
        if action in words:
            idx = words.index(action)
            # Get everything after the action word
            remaining = words[idx + 1:]
            
            # Filter out articles and common words
            ignore = {'a', 'an', 'the', 'some', 'for', 'to', 'please'}
            for word in remaining:
                if word not in ignore:
                    packages.append(word)
                    break  # Take first non-ignored word
        
        # Special cases for common descriptions
        query_lower = query.lower()
        if not packages:
            if 'browser' in query_lower or 'web browser' in query_lower:
                packages = ['firefox']
            elif 'editor' in query_lower or 'text editor' in query_lower:
                packages = ['vim']
            elif 'terminal' in query_lower:
                packages = ['alacritty']
        
        return packages
    
    def _extract_search_term(self, query: str) -> List[str]:
        """Extract search terms from query"""
        words = query.split()
        search_words = {'search', 'find', 'look', 'for'}
        terms = [w for w in words if w not in search_words and len(w) > 2]
        return terms[:3]  # Return up to 3 terms
    
    def explain_error(self, error_message: str) -> Optional[str]:
        """Use AI to explain an error message in simple terms"""
        prompt = f"""Explain this NixOS error in simple terms and suggest a solution:
Error: {error_message}

Provide a brief, helpful explanation and solution."""
        
        return self.ask(prompt, model=self.models.get('empathy', self.models['tiny']))
    
    def suggest_packages(self, description: str) -> Optional[List[str]]:
        """Use AI to suggest packages based on a description"""
        prompt = f"""Suggest NixOS packages for: {description}
List up to 5 relevant package names, one per line."""
        
        response = self.ask(prompt, model=self.models.get('coder', self.models['quick']))
        
        if response:
            # Extract package names from response
            lines = response.strip().split('\n')
            packages = []
            for line in lines:
                # Clean up the line and extract package name
                line = line.strip().strip('- ').strip('* ')
                if line and not line.startswith('#'):
                    # Take first word as package name
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
            return packages[:5]
        return None


class SocraticOllama(OllamaClient):
    """Socratic questioning mode for Ollama - asks clarifying questions"""
    
    def ask_clarifying_question(self, query: str, category: str) -> Optional[str]:
        """Generate a clarifying question based on the query"""
        
        prompt = f"""The user wants to {query} related to {category}.
Generate a helpful clarifying question to better understand their needs.
Keep it simple and friendly. One question only.

Example: "What kind of {category} would work best for you?"

Question:"""
        
        response = self.ask(prompt, model=self.models.get('empathy', self.models['tiny']))
        return response.strip() if response else None
    
    def generate_options(self, category: str) -> Optional[Dict[str, str]]:
        """Generate options for a category"""
        
        prompt = f"""Generate 4 options for choosing a {category} on NixOS.
Format as JSON with number keys and description values.

Example:
{{"1": "Fast and minimal", "2": "Feature-rich", "3": "Privacy-focused", "4": "Developer-oriented"}}

Options:"""
        
        response = self.ask(prompt, model=self.models.get('quick', self.models['tiny']))
        
        if response:
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        
        # Fallback options
        return {
            "1": "Simple and easy",
            "2": "Powerful and flexible",
            "3": "Lightweight and fast",
            "4": "Full-featured"
        }