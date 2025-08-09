#!/usr/bin/env python3
"""
from typing import List, Dict
Install Instructions Plugin
Provides installation instructions for packages without actually executing
"""

from typing import Dict, Any, List
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.plugin_base import FeaturePlugin, PluginInfo


class InstallInstructionsPlugin(FeaturePlugin):
    """Plugin for providing package installation instructions"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="install_instructions",
            version="1.0.0",
            description="Provides installation instructions for NixOS packages",
            author="Nix for Humanity Team",
            capabilities=["install", "instructions", "guide"],
            dependencies=["nix-knowledge-engine"]
        )
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        # Store reference to knowledge engine if available
        self.knowledge_engine = context.get('knowledge_engine')
        self._initialized = True
        return True
    
    def get_supported_intents(self) -> List[str]:
        """Return list of intents this plugin supports"""
        return ["install_package", "install_instructions"]
    
    def handle(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle installation instruction request
        
        Args:
            intent: The intent (install_package)
            context: Request context with package info
            
        Returns:
            Installation instructions
        """
        package = context.get('package', '')
        execute = context.get('execute', False)
        
        if not package:
            return {
                'success': False,
                'response': "I need a package name to provide installation instructions.",
                'data': None,
                'actions': []
            }
        
        # Get installation methods
        methods = self._get_install_methods(package)
        
        # Format response based on execution mode
        if execute:
            # If execution is requested, we don't handle it - let main command handle
            return {
                'success': False,
                'response': "This plugin provides instructions only. Use --execute flag with main command.",
                'data': None,
                'actions': []
            }
        
        # Build instruction response
        response = f"I'll help you install {package}! Here are your options:\n\n"
        
        for i, method in enumerate(methods, 1):
            response += f"{i}. **{method['name']}** - {method['description']}\n"
            response += f"   ```\n   {method['example']}\n   ```\n\n"
        
        response += "💡 Declarative installation (option 1) is recommended for reproducibility.\n\n"
        response += "To execute the installation, use:\n"
        response += f"```\nask-nix --execute \"install {package}\"\n```"
        
        return {
            'success': True,
            'response': response,
            'data': {
                'package': package,
                'methods': methods
            },
            'actions': [
                {
                    'type': 'show_instructions',
                    'package': package,
                    'methods_shown': len(methods)
                }
            ]
        }
    
    def _get_install_methods(self, package: str) -> List[Dict[str, str]]:
        """Get installation methods for a package"""
        return [
            {
                'name': 'Declarative (Recommended)',
                'description': 'Add to your system configuration for permanent installation',
                'example': f'# Edit /etc/nixos/configuration.nix\nenvironment.systemPackages = with pkgs; [ {package} ];\n\n# Then rebuild:\nsudo nixos-rebuild switch'
            },
            {
                'name': 'Home Manager',
                'description': 'User-specific declarative installation',
                'example': f'# Edit ~/.config/home-manager/home.nix\nhome.packages = with pkgs; [ {package} ];\n\n# Then apply:\nhome-manager switch'
            },
            {
                'name': 'Imperative',
                'description': 'Quick installation for current user',
                'example': f'nix-env -iA nixos.{package}'
            },
            {
                'name': 'Temporary Shell',
                'description': 'Try without installing',
                'example': f'nix-shell -p {package}'
            }
        ]
    
    def enhance_response(self, response: str, context: Dict[str, Any]) -> str:
        """
        Enhance responses from other plugins with installation tips
        """
        # If this is a search result, add installation hint
        if context.get('intent', {}).get('action') == 'search_package':
            if 'To install' not in response:
                response += "\n\n💡 Tip: To see installation instructions for any package, use:\n"
                response += "```\nask-nix \"install [package-name]\"\n```"
        
        return response