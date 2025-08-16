#!/usr/bin/env python3
"""
AI Development Assistant for Luminous Nix
Integrates local LLMs for code review, simplification suggestions, and NixOS expertise.

Philosophy: AI as partner, not replacement. Simple interface, sophisticated assistance.
"""

import subprocess
import json
from typing import Dict, Any, Optional
from pathlib import Path


class AIDevAssistant:
    """Simple, elegant AI integration for development."""
    
    def __init__(self):
        self.models = {
            'nix-expert': 'For NixOS configuration and best practices',
            'nix-coder': 'For code generation and refactoring', 
            'nix-quick': 'For fast responses and simple queries',
            'nix-empathy': 'For user experience and documentation'
        }
        
    def ask(self, prompt: str, model: str = 'nix-quick') -> str:
        """Ask a local LLM for assistance."""
        try:
            # Simple ollama integration
            result = subprocess.run(
                ['ollama', 'run', model, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            return f"AI unavailable: {e}"
    
    def review_code(self, file_path: str) -> str:
        """Get AI review focused on simple elegance."""
        code = Path(file_path).read_text()
        
        prompt = f"""Review this code for THE LUMINOUS WAY principles:
        1. Could this be simpler?
        2. Does complexity emerge from simple rules?
        3. Are we trusting the platform?
        4. Could 10x less code achieve this?
        
        Code:
        {code[:1000]}  # First 1000 chars for context
        
        Provide specific simplification suggestions."""
        
        return self.ask(prompt, 'nix-coder')
    
    def suggest_deletion(self, directory: str) -> str:
        """AI helps identify complexity to delete."""
        prompt = f"""Following THE LUMINOUS WAY of simple elegance,
        what files in {directory} are likely candidates for deletion?
        Look for:
        - Duplicate functionality
        - Over-engineered solutions
        - Features that could emerge from simpler rules
        - Code that reimplements platform features"""
        
        return self.ask(prompt, 'nix-expert')
    
    def simplify(self, code: str) -> str:
        """Get simpler version of code."""
        prompt = f"""Simplify this code following THE LUMINOUS WAY:
        - Remove unnecessary complexity
        - Trust platform features
        - Use simple rules for emergent behavior
        - Aim for 10x less code
        
        Original:
        {code}
        
        Simplified version:"""
        
        return self.ask(prompt, 'nix-coder')
    
    def test_philosophy(self, feature_description: str) -> str:
        """Test if a feature aligns with our philosophy."""
        prompt = f"""Does this feature align with THE LUMINOUS WAY?
        
        Feature: {feature_description}
        
        Apply the Litmus Test:
        1. Does it serve simple elegance?
        2. Could emergent behavior handle this?
        3. Are we adding or removing complexity?
        4. Does it trust the platform?
        5. Will users need less or more?
        
        Answer: PASS or FAIL with explanation."""
        
        return self.ask(prompt, 'nix-empathy')


# Integration with development workflow
if __name__ == '__main__':
    import sys
    
    assistant = AIDevAssistant()
    
    if len(sys.argv) < 2:
        print("Usage: ai_dev_assistant.py [review|delete|simplify|test] <args>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'review' and len(sys.argv) > 2:
        print(assistant.review_code(sys.argv[2]))
    elif command == 'delete':
        directory = sys.argv[2] if len(sys.argv) > 2 else 'src/'
        print(assistant.suggest_deletion(directory))
    elif command == 'simplify':
        code = sys.stdin.read() if not sys.stdin.isatty() else sys.argv[2]
        print(assistant.simplify(code))
    elif command == 'test' and len(sys.argv) > 2:
        feature = ' '.join(sys.argv[2:])
        print(assistant.test_philosophy(feature))
    else:
        print(f"Unknown command: {command}")