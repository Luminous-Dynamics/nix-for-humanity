#!/usr/bin/env python3
"""
from typing import Dict, List
Plugin Base Interface for Nix for Humanity
Defines the contract that all plugins must follow
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class PluginInfo:
    """Metadata about a plugin"""
    name: str
    version: str
    description: str
    author: str = "Nix for Humanity Team"
    capabilities: List[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.dependencies is None:
            self.dependencies = []


class PluginBase(ABC):
    """Base class for all Nix for Humanity plugins"""
    
    def __init__(self):
        self.info = self.get_info()
        self._initialized = False
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with system context
        
        Args:
            context: Dictionary containing:
                - knowledge_engine: NixOS knowledge engine instance
                - config: System configuration
                - cache_dir: Path to cache directory
                - data_dir: Path to data directory
                
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def can_handle(self, intent: str, context: Dict[str, Any]) -> bool:
        """
        Check if this plugin can handle the given intent
        
        Args:
            intent: The detected intent (e.g., "install_package", "search", etc.)
            context: Additional context about the request
            
        Returns:
            True if this plugin should handle the request
        """
        pass
    
    @abstractmethod
    def handle(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the request
        
        Args:
            intent: The detected intent
            context: Request context including query, parsed data, etc.
            
        Returns:
            Dictionary with:
                - success: bool
                - response: str (formatted response)
                - data: Any (additional data)
                - actions: List[Dict] (actions taken or to be taken)
        """
        pass
    
    def cleanup(self) -> None:
        """Optional cleanup when plugin is unloaded"""
        pass
    
    def get_commands(self) -> List[str]:
        """Return list of commands this plugin adds"""
        return []
    
    def get_flags(self) -> List[Dict[str, Any]]:
        """Return list of command-line flags this plugin adds"""
        return []
    
    def enhance_response(self, response: str, context: Dict[str, Any]) -> str:
        """
        Optional: Enhance/modify responses from other plugins
        Used for personality plugins, formatting plugins, etc.
        """
        return response
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Optional: Return plugin metrics for monitoring"""
        return {}


class PersonalityPlugin(PluginBase):
    """Base class for personality plugins"""
    
    @abstractmethod
    def apply_personality(self, response: str, context: Dict[str, Any]) -> str:
        """Apply personality transformation to response"""
        pass
    
    def can_handle(self, intent: str, context: Dict[str, Any]) -> bool:
        """Personality plugins don't handle intents directly"""
        return False
    
    def handle(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Personality plugins don't handle requests directly"""
        return {"success": False, "response": "Personality plugins enhance other responses"}


class FeaturePlugin(PluginBase):
    """Base class for feature plugins that add new capabilities"""
    
    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """Return list of intents this plugin supports"""
        pass
    
    def can_handle(self, intent: str, context: Dict[str, Any]) -> bool:
        """Default implementation checks supported intents"""
        return intent in self.get_supported_intents()