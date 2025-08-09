#!/usr/bin/env python3
"""
from typing import Dict
Minimal Personality Plugin
Provides just the facts with no extra decoration
"""

from typing import Dict, Any
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.plugin_base import PersonalityPlugin, PluginInfo


class MinimalPersonalityPlugin(PersonalityPlugin):
    """Minimal personality - just the facts"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="minimal_personality",
            version="1.0.0",
            description="Minimal personality style - just the facts, no fluff",
            author="Nix for Humanity Team",
            capabilities=["minimal", "concise", "direct"]
        )
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        self._initialized = True
        return True
    
    def apply_personality(self, response: str, context: Dict[str, Any]) -> str:
        """
        Apply minimal personality - strip down to essentials
        
        Args:
            response: The base response to transform
            context: Additional context about the request
            
        Returns:
            Minimized response
        """
        # Remove any emoji
        import re
        response = re.sub(r'[^\x00-\x7F]+', '', response)
        
        # Remove greeting lines
        lines = response.split('\n')
        filtered_lines = []
        
        skip_patterns = [
            'hi there', 'hello', 'great question', 'awesome',
            'let me help', "i'll help", 'thank you', 'you\'re welcome',
            '!', '😊', '🌟', '💡'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            # Skip lines that are just greetings or encouragement
            if any(pattern in line_lower for pattern in skip_patterns):
                continue
            # Skip empty lines
            if not line.strip():
                continue
            filtered_lines.append(line)
        
        # Join back together
        result = '\n'.join(filtered_lines).strip()
        
        # If the result is too verbose, just return the example/command
        if len(result) > 200 and 'example' in context:
            # Try to extract just the command/example
            if '```' in result:
                # Extract code block
                code_match = re.search(r'```[^\n]*\n(.*?)```', result, re.DOTALL)
                if code_match:
                    return code_match.group(1).strip()
            
            # Look for lines that look like commands
            for line in result.split('\n'):
                if line.strip().startswith(('$', '#', 'nix', 'sudo')):
                    return line.strip()
        
        return result
    
    def cleanup(self) -> None:
        """Cleanup when plugin is unloaded"""
        pass
    
    def get_flags(self) -> list:
        """Return command-line flags this plugin adds"""
        return [
            {
                'flag': '--minimal',
                'help': 'Use minimal personality (just the facts)',
                'action': 'store_const',
                'const': 'minimal',
                'dest': 'personality'
            }
        ]