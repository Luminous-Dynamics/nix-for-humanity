#!/usr/bin/env python3
"""
🔌 Hello Plugin - First Working Plugin for Luminous Nix

This simple plugin demonstrates the plugin system capabilities:
1. Plugin discovery and loading
2. Command registration
3. Integration with core system

This will activate the Plugin System feature!
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class HelloPlugin:
    """
    A simple greeting plugin that demonstrates plugin capabilities.
    """
    
    # Plugin metadata (required for all plugins)
    PLUGIN_INFO = {
        'name': 'hello',
        'version': '1.0.0',
        'description': 'A friendly greeting plugin',
        'author': 'Luminous Dynamics',
        'commands': ['hello', 'greet', 'welcome'],
        'readiness': 0.75  # This plugin is ready for use
    }
    
    def __init__(self):
        """Initialize the plugin"""
        self.greetings = {
            'default': "Hello! I'm the Hello Plugin, here to brighten your day!",
            'morning': "Good morning! Hope you have a luminous day ahead!",
            'evening': "Good evening! Time to wind down with some sacred computing.",
            'technical': "Greetings, fellow consciousness explorer!",
            'grandma_rose': "Hello dear! How lovely to see you today!",
            'maya': "Hey! Quick greeting for you! ⚡",
            'dr_sarah': "Greetings. Plugin system operational and ready."
        }
        logger.info(f"🔌 {self.PLUGIN_INFO['name']} plugin initialized")
    
    def get_commands(self) -> List[str]:
        """Return list of commands this plugin handles"""
        return self.PLUGIN_INFO['commands']
    
    def can_handle(self, command: str) -> bool:
        """Check if this plugin can handle the given command"""
        cmd_lower = command.lower()
        return any(cmd in cmd_lower for cmd in self.PLUGIN_INFO['commands'])
    
    def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a plugin command.
        
        Args:
            command: The command to execute
            context: Optional context with user info, preferences, etc.
            
        Returns:
            Response dictionary with result and metadata
        """
        # Determine greeting style based on context
        persona = 'default'
        if context:
            persona = context.get('persona', 'default')
            time_of_day = context.get('time_of_day')
            if time_of_day:
                if 'morning' in time_of_day:
                    persona = 'morning'
                elif 'evening' in time_of_day:
                    persona = 'evening'
        
        # Get appropriate greeting
        greeting = self.greetings.get(persona, self.greetings['default'])
        
        # Parse command for specific requests
        if 'technical' in command.lower():
            greeting = self.greetings['technical']
        elif 'warmly' in command.lower():
            greeting = "🌟 " + greeting + " 🌟"
        
        return {
            'success': True,
            'output': greeting,
            'metadata': {
                'plugin': self.PLUGIN_INFO['name'],
                'version': self.PLUGIN_INFO['version'],
                'persona_used': persona,
                'command_handled': command
            }
        }
    
    def get_help(self) -> str:
        """Return help text for this plugin"""
        return f"""
{self.PLUGIN_INFO['name']} Plugin v{self.PLUGIN_INFO['version']}
{self.PLUGIN_INFO['description']}

Available commands:
  hello         - Simple greeting
  greet         - Friendly greeting
  welcome       - Welcome message
  
Options:
  --technical   - Technical greeting
  --warmly      - Extra warm greeting
  
Examples:
  ask-nix hello
  ask-nix greet --warmly
  ask-nix welcome --technical
"""


# Plugin registration function (required)
def register_plugin():
    """
    Factory function to create and return plugin instance.
    This is called by the plugin loader.
    """
    return HelloPlugin()


# Direct testing
if __name__ == "__main__":
    # Test the plugin
    plugin = HelloPlugin()
    
    print("Testing Hello Plugin")
    print("=" * 40)
    
    # Test basic command
    result = plugin.execute("hello")
    print(f"Basic: {result['output']}")
    
    # Test with context
    result = plugin.execute("greet", {'persona': 'grandma_rose'})
    print(f"Grandma Rose: {result['output']}")
    
    # Test technical
    result = plugin.execute("hello technical")
    print(f"Technical: {result['output']}")
    
    # Test warmly
    result = plugin.execute("greet warmly")
    print(f"Warmly: {result['output']}")
    
    print("\nPlugin test complete!")