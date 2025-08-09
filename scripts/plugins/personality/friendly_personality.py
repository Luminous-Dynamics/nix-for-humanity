#!/usr/bin/env python3
"""
from typing import Dict
Friendly Personality Plugin
Provides warm, helpful responses with encouragement
"""

from typing import Dict, Any
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.plugin_base import PersonalityPlugin, PluginInfo


class FriendlyPersonalityPlugin(PersonalityPlugin):
    """Friendly personality - warm and helpful"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="friendly_personality",
            version="1.0.0",
            description="Friendly personality style - warm, helpful, and encouraging",
            author="Nix for Humanity Team",
            capabilities=["friendly", "warm", "helpful", "default"]
        )
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        self._initialized = True
        return True
    
    def apply_personality(self, response: str, context: Dict[str, Any]) -> str:
        """
        Apply friendly personality - add warmth and helpfulness
        
        Args:
            response: The base response to transform
            context: Additional context about the request
            
        Returns:
            Friendly response
        """
        # Check if response already has friendly elements
        has_greeting = any(phrase in response.lower() for phrase in ['hi', 'hello', 'i\'ll help'])
        has_closing = any(phrase in response.lower() for phrase in ['let me know', 'need help', 'good luck'])
        
        # Build friendly response
        parts = []
        
        # Add greeting if not present
        if not has_greeting:
            intent = context.get('intent', {}).get('action', '')
            if intent == 'install_package':
                parts.append("Hi there! I'll help you install that.")
            elif intent == 'search_package':
                parts.append("Let me search for that package!")
            elif intent == 'update_system':
                parts.append("Great! Let's update your system.")
            else:
                parts.append("Hi there!")
        
        # Add the main response
        parts.append(response)
        
        # Add helpful closing if not present
        if not has_closing:
            if context.get('success', True):
                parts.append("\nLet me know if you need any clarification! 😊")
            else:
                parts.append("\nDon't worry, we'll figure this out together! Let me know if you need help.")
        
        return '\n\n'.join(filter(None, parts))
    
    def cleanup(self) -> None:
        """Cleanup when plugin is unloaded"""
        pass
    
    def get_flags(self) -> list:
        """Return command-line flags this plugin adds"""
        return [
            {
                'flag': '--friendly',
                'help': 'Use friendly personality (warm and helpful)',
                'action': 'store_const',
                'const': 'friendly',
                'dest': 'personality'
            }
        ]