#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Plugin Loader for Nix for Humanity
Dynamically discovers, loads, and manages plugins
"""

import os
import sys
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
import logging
from collections import defaultdict

from .plugin_base import PluginBase, PersonalityPlugin, FeaturePlugin, PluginInfo


class PluginLoader:
    """Manages plugin discovery, loading, and lifecycle"""
    
    def __init__(self, plugin_dirs: List[str] = None):
        """
        Initialize the plugin loader
        
        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.logger = logging.getLogger(__name__)
        
        # Default plugin directories
        if plugin_dirs is None:
            base_dir = Path(__file__).parent.parent
            plugin_dirs = [
                str(base_dir / "plugins"),
                str(base_dir / "plugins" / "personality"),
                str(base_dir / "plugins" / "features"),
                str(base_dir / "plugins" / "integrations"),
            ]
        
        self.plugin_dirs = [Path(d) for d in plugin_dirs if os.path.exists(d)]
        self.plugins: Dict[str, PluginBase] = {}
        self.personality_plugins: Dict[str, PersonalityPlugin] = {}
        self.feature_plugins: Dict[str, FeaturePlugin] = {}
        self.intent_handlers: Dict[str, List[FeaturePlugin]] = defaultdict(list)
        
    def discover_plugins(self) -> List[str]:
        """
        Discover all available plugins in plugin directories
        
        Returns:
            List of discovered plugin module names
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            for file_path in plugin_dir.glob("*.py"):
                if file_path.name.startswith("_"):
                    continue  # Skip private modules
                    
                module_name = file_path.stem
                discovered.append(module_name)
                self.logger.debug(f"Discovered plugin: {module_name} in {plugin_dir}")
                
        return discovered
    
    def load_plugin(self, module_name: str) -> Optional[PluginBase]:
        """
        Load a single plugin by module name
        
        Args:
            module_name: Name of the plugin module to load
            
        Returns:
            Loaded plugin instance or None if loading failed
        """
        # Check if already loaded
        if module_name in self.plugins:
            return self.plugins[module_name]
        
        # Search for the plugin file
        plugin_file = None
        for plugin_dir in self.plugin_dirs:
            potential_file = plugin_dir / f"{module_name}.py"
            if potential_file.exists():
                plugin_file = potential_file
                break
        
        if not plugin_file:
            self.logger.error(f"Plugin file not found: {module_name}.py")
            return None
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if not spec or not spec.loader:
                self.logger.error(f"Failed to create spec for {module_name}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find plugin classes in the module
            plugin_instance = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj not in [PluginBase, PersonalityPlugin, FeaturePlugin]):
                    
                    # Create instance
                    plugin_instance = obj()
                    break
            
            if not plugin_instance:
                # Only log in debug mode to reduce noise
                self.logger.debug(f"No plugin class found in {module_name}")
                return None
            
            # Store the plugin
            self.plugins[module_name] = plugin_instance
            
            # Categorize the plugin
            if isinstance(plugin_instance, PersonalityPlugin):
                self.personality_plugins[module_name] = plugin_instance
            elif isinstance(plugin_instance, FeaturePlugin):
                self.feature_plugins[module_name] = plugin_instance
                # Register intent handlers
                for intent in plugin_instance.get_supported_intents():
                    self.intent_handlers[intent].append(plugin_instance)
            
            self.logger.info(f"Successfully loaded plugin: {module_name}")
            return plugin_instance
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {module_name}: {e}")
            return None
    
    def load_all_plugins(self) -> Dict[str, PluginBase]:
        """
        Discover and load all available plugins
        
        Returns:
            Dictionary of loaded plugins
        """
        discovered = self.discover_plugins()
        
        for module_name in discovered:
            self.load_plugin(module_name)
            
        return self.plugins
    
    def initialize_plugins(self, context: Dict[str, Any]) -> Dict[str, bool]:
        """
        Initialize all loaded plugins
        
        Args:
            context: System context to pass to plugins
            
        Returns:
            Dictionary mapping plugin names to initialization success
        """
        results = {}
        
        for name, plugin in self.plugins.items():
            try:
                success = plugin.initialize(context)
                results[name] = success
                if not success:
                    self.logger.warning(f"Plugin {name} initialization failed")
            except Exception as e:
                self.logger.error(f"Error initializing plugin {name}: {e}")
                results[name] = False
                
        return results
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a specific plugin by name"""
        return self.plugins.get(name)
    
    def get_intent_handlers(self, intent: str) -> List[FeaturePlugin]:
        """Get all plugins that can handle a specific intent"""
        return self.intent_handlers.get(intent, [])
    
    def find_handler(self, intent: str, context: Dict[str, Any]) -> Optional[FeaturePlugin]:
        """
        Find the best plugin to handle a given intent
        
        Args:
            intent: The intent to handle
            context: Request context
            
        Returns:
            The best plugin to handle the intent, or None
        """
        handlers = self.get_intent_handlers(intent)
        
        # Find plugins that can handle this specific request
        capable_handlers = []
        for handler in handlers:
            if handler.can_handle(intent, context):
                capable_handlers.append(handler)
        
        if not capable_handlers:
            return None
            
        # TODO: Add priority/scoring system for plugin selection
        # For now, use simple priority ordering: newer plugins first
        if len(capable_handlers) == 1:
            return capable_handlers[0]
            
        # Sort by plugin priority (if available) or by load order
        sorted_handlers = sorted(capable_handlers, 
                               key=lambda p: getattr(p.info, 'priority', 50), 
                               reverse=True)
        return sorted_handlers[0]
    
    def apply_personality(self, response: str, personality: str, context: Dict[str, Any]) -> str:
        """
        Apply personality transformation to a response
        
        Args:
            response: The base response
            personality: The personality style to apply
            context: Request context
            
        Returns:
            Transformed response
        """
        # Find personality plugin
        personality_plugin = None
        for name, plugin in self.personality_plugins.items():
            if personality in plugin.info.capabilities:
                personality_plugin = plugin
                break
                
        if personality_plugin:
            return personality_plugin.apply_personality(response, context)
            
        return response
    
    def get_all_commands(self) -> List[str]:
        """Get all commands provided by plugins"""
        commands = []
        for plugin in self.plugins.values():
            commands.extend(plugin.get_commands())
        return commands
    
    def get_all_flags(self) -> List[Dict[str, Any]]:
        """Get all command-line flags provided by plugins"""
        flags = []
        for plugin in self.plugins.values():
            flags.extend(plugin.get_flags())
        return flags
    
    def collect_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Collect metrics from all plugins"""
        metrics = {}
        for name, plugin in self.plugins.items():
            try:
                plugin_metrics = plugin.collect_metrics()
                if plugin_metrics:
                    metrics[name] = plugin_metrics
            except Exception as e:
                self.logger.error(f"Error collecting metrics from {name}: {e}")
        return metrics
    
    def unload_plugin(self, name: str) -> bool:
        """
        Unload a specific plugin
        
        Args:
            name: Name of the plugin to unload
            
        Returns:
            True if successfully unloaded
        """
        if name not in self.plugins:
            return False
            
        plugin = self.plugins[name]
        
        try:
            # Call cleanup
            plugin.cleanup()
            
            # Remove from registries
            del self.plugins[name]
            
            if name in self.personality_plugins:
                del self.personality_plugins[name]
                
            if name in self.feature_plugins:
                feature_plugin = self.feature_plugins[name]
                # Remove from intent handlers
                for intent in feature_plugin.get_supported_intents():
                    if feature_plugin in self.intent_handlers[intent]:
                        self.intent_handlers[intent].remove(feature_plugin)
                del self.feature_plugins[name]
                
            # Remove from sys.modules
            if name in sys.modules:
                del sys.modules[name]
                
            self.logger.info(f"Successfully unloaded plugin: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {name}: {e}")
            return False
    
    def reload_plugin(self, name: str, context: Dict[str, Any]) -> bool:
        """
        Reload a plugin (unload and load again)
        
        Args:
            name: Name of the plugin to reload
            context: System context for re-initialization
            
        Returns:
            True if successfully reloaded
        """
        # Unload first
        if not self.unload_plugin(name):
            return False
            
        # Load again
        plugin = self.load_plugin(name)
        if not plugin:
            return False
            
        # Re-initialize
        try:
            return plugin.initialize(context)
        except Exception as e:
            self.logger.error(f"Error re-initializing plugin {name}: {e}")
            return False
    
    def get_plugin_info(self) -> Dict[str, PluginInfo]:
        """Get information about all loaded plugins"""
        info = {}
        for name, plugin in self.plugins.items():
            info[name] = plugin.info
        return info