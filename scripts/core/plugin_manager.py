#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Plugin Manager for Nix for Humanity
Simplified plugin management for ask-nix command
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_loader import PluginLoader
from core.plugin_base import PluginBase, PersonalityPlugin, FeaturePlugin


class PluginManager:
    """Simplified plugin manager for ask-nix integration"""
    
    def __init__(self):
        """Initialize the plugin manager"""
        # Get plugin directories
        base_dir = Path(__file__).parent.parent
        plugin_dirs = [
            str(base_dir / "plugins"),
            str(base_dir / "plugins" / "personality"),
            str(base_dir / "plugins" / "features"),
        ]
        
        # Create plugin loader
        self.loader = PluginLoader(plugin_dirs)
        self.plugins_loaded = False
        self.active_personality = "friendly"  # Default
        
    def load_all_plugins(self, context: Dict[str, Any] = None) -> bool:
        """
        Load all available plugins
        
        Args:
            context: System context to pass to plugins
            
        Returns:
            True if plugins loaded successfully
        """
        if self.plugins_loaded:
            return True
            
        # Default context if none provided
        if context is None:
            context = {
                'cache_dir': os.path.expanduser('~/.cache/nix-for-humanity'),
                'data_dir': os.path.expanduser('~/.local/share/nix-for-humanity'),
                'config': {}
            }
        
        # Load plugins
        self.loader.load_all_plugins()
        
        # Initialize plugins
        init_results = self.loader.initialize_plugins(context)
        
        # Check for failures
        failed = [name for name, success in init_results.items() if not success]
        if failed:
            print(f"Warning: Failed to initialize plugins: {', '.join(failed)}")
        
        self.plugins_loaded = True
        return len(failed) == 0
    
    def set_personality(self, personality: str) -> bool:
        """
        Set the active personality
        
        Args:
            personality: Name of personality to use
            
        Returns:
            True if personality was set
        """
        # Check if we have a plugin that supports this personality
        for plugin in self.loader.personality_plugins.values():
            if personality in plugin.info.capabilities:
                self.active_personality = personality
                return True
        
        print(f"Warning: No plugin found for personality '{personality}'")
        return False
    
    def apply_personality(self, response: str, context: Dict[str, Any] = None) -> str:
        """
        Apply the active personality to a response
        
        Args:
            response: The base response
            context: Additional context
            
        Returns:
            Transformed response
        """
        if not self.plugins_loaded:
            self.load_all_plugins()
        
        if context is None:
            context = {}
        
        # Add personality to context
        context['personality'] = self.active_personality
        
        # Apply personality transformation
        return self.loader.apply_personality(response, self.active_personality, context)
    
    def handle_intent(self, intent: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find and execute a plugin to handle the given intent
        
        Args:
            intent: The intent to handle
            context: Request context
            
        Returns:
            Plugin response or None if no handler found
        """
        if not self.plugins_loaded:
            self.load_all_plugins()
        
        # Find a handler for this intent
        handler = self.loader.find_handler(intent, context)
        
        if handler:
            try:
                return handler.handle(intent, context)
            except Exception as e:
                return {
                    'success': False,
                    'response': f"Plugin error: {str(e)}",
                    'data': None,
                    'actions': []
                }
        
        return None
    
    def get_all_flags(self) -> List[Dict[str, Any]]:
        """Get all command-line flags from plugins"""
        if not self.plugins_loaded:
            self.load_all_plugins()
            
        return self.loader.get_all_flags()
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about loaded plugins"""
        if not self.plugins_loaded:
            self.load_all_plugins()
            
        info = self.loader.get_plugin_info()
        
        return {
            'total_plugins': len(info),
            'personality_plugins': len(self.loader.personality_plugins),
            'feature_plugins': len(self.loader.feature_plugins),
            'plugins': {name: {
                'version': plugin.version,
                'description': plugin.description,
                'capabilities': plugin.capabilities
            } for name, plugin in info.items()}
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all plugins"""
        if not self.plugins_loaded:
            self.load_all_plugins()
            
        return self.loader.collect_metrics()


# Singleton instance for easy import
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """Get the singleton plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager