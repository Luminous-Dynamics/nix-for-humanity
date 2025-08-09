#!/usr/bin/env python3
"""
from typing import List, Dict
Package Search Plugin
Handles package searching functionality with caching
"""

from typing import Dict, Any, List
import sys
import os
import importlib.util

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.plugin_base import FeaturePlugin, PluginInfo


class PackageSearchPlugin(FeaturePlugin):
    """Plugin for searching NixOS packages"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="package_search",
            version="1.0.0",
            description="Search for NixOS packages with intelligent caching",
            author="Nix for Humanity Team",
            capabilities=["search", "find", "lookup", "cache"],
            dependencies=["package-cache-manager"]
        )
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin with cache manager"""
        try:
            # Try to import the package cache manager
            cache_module_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 
                'package-cache-manager.py'
            )
            
            if os.path.exists(cache_module_path):
                spec = importlib.util.spec_from_file_location(
                    "package_cache_manager", 
                    cache_module_path
                )
                package_cache_manager = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(package_cache_manager)
                
                self.cache_manager = package_cache_manager.IntelligentPackageCache()
            else:
                # Fallback if cache manager not available
                self.cache_manager = None
                
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Warning: Could not initialize package cache: {e}")
            self.cache_manager = None
            self._initialized = True
            return True
    
    def get_supported_intents(self) -> List[str]:
        """Return list of intents this plugin supports"""
        return ["search_package", "find_package", "lookup_package"]
    
    def handle(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle package search request
        
        Args:
            intent: The intent (search_package, etc.)
            context: Request context with query and other data
            
        Returns:
            Search results
        """
        query = context.get('query', '')
        package_name = context.get('package', '')
        
        # Extract search term
        search_term = package_name or self._extract_search_term(query)
        
        if not search_term:
            return {
                'success': False,
                'response': "I need a package name to search for. Try: 'search for firefox'",
                'data': None,
                'actions': []
            }
        
        # Search using cache if available
        if self.cache_manager:
            results, from_cache = self.cache_manager.search_with_fallback(search_term)
            cache_status = "cached" if from_cache else "fresh"
        else:
            # Fallback to basic search
            import subprocess
            try:
                result = subprocess.run(
                    ['nix', 'search', 'nixpkgs', search_term],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                results = self._parse_search_output(result.stdout)
                cache_status = "no-cache"
            except Exception as e:
                return {
                    'success': False,
                    'response': f"Search failed: {str(e)}",
                    'data': None,
                    'actions': []
                }
        
        # Format response
        if not results:
            response = f"No packages found matching '{search_term}'.\n\n"
            response += "Try:\n"
            response += "• Checking the spelling\n"
            response += "• Using a more general term\n"
            response += "• Searching at https://search.nixos.org"
        else:
            response = f"Found {len(results)} packages matching '{search_term}':\n\n"
            
            # Show top 5 results
            for i, result in enumerate(results[:5], 1):
                name = result.get('name', 'unknown')
                desc = result.get('description', 'No description')
                response += f"{i}. **{name}**\n"
                response += f"   {desc}\n\n"
            
            if len(results) > 5:
                response += f"... and {len(results) - 5} more results.\n\n"
            
            response += "To install any of these, use:\n"
            response += f"```\nask-nix \"install {results[0]['name']}\"\n```"
        
        return {
            'success': True,
            'response': response,
            'data': {
                'results': results,
                'cache_status': cache_status,
                'search_term': search_term
            },
            'actions': [
                {
                    'type': 'search',
                    'target': search_term,
                    'result_count': len(results)
                }
            ]
        }
    
    def _extract_search_term(self, query: str) -> str:
        """Extract search term from natural language query"""
        query_lower = query.lower()
        
        # Remove common search phrases
        for phrase in ['search for', 'find', 'look for', 'search', 'is there']:
            if phrase in query_lower:
                query_lower = query_lower.replace(phrase, '')
        
        # Clean up and return
        return query_lower.strip()
    
    def _parse_search_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse nix search output into structured results"""
        results = []
        current_package = None
        
        for line in output.split('\n'):
            if line.startswith('* '):
                # New package
                if current_package:
                    results.append(current_package)
                
                # Extract package name
                parts = line.split(' ', 2)
                if len(parts) >= 2:
                    current_package = {
                        'name': parts[1].strip(),
                        'description': ''
                    }
            elif line.strip() and current_package:
                # Description line
                current_package['description'] = line.strip()
        
        # Don't forget the last package
        if current_package:
            results.append(current_package)
        
        return results
    
    def get_commands(self) -> List[str]:
        """Return list of commands this plugin adds"""
        return ["search", "find"]
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Return plugin metrics"""
        if self.cache_manager:
            stats = self.cache_manager.get_cache_stats()
            return {
                'cache_size': stats.get('total_packages', 0),
                'cache_age': stats.get('cache_age', 'unknown')
            }
        return {}