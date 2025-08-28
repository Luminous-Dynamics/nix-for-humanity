#!/usr/bin/env python3
"""
Package Discovery - Bridge to Native NixOS Package Search

This module provides package search functionality by connecting
to the native NixOS API.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import native API
try:
    from .native_nix_api import get_native_api
    NATIVE_API_AVAILABLE = True
except ImportError:
    NATIVE_API_AVAILABLE = False
    logger.warning("Native API not available for package discovery")


@dataclass
class PackageInfo:
    """Simple package information"""
    name: str
    version: str = ""
    description: str = ""
    
    def __str__(self):
        if self.version:
            return f"{self.name} ({self.version}): {self.description[:50]}..."
        return f"{self.name}: {self.description[:50]}..."


class PackageDiscovery:
    """
    Discovers and searches NixOS packages using the native API
    """
    
    def __init__(self):
        """Initialize package discovery with native API"""
        self.native_api = None
        if NATIVE_API_AVAILABLE:
            try:
                self.native_api = get_native_api()
                logger.info("Package discovery initialized with native API")
            except Exception as e:
                logger.error(f"Failed to initialize native API: {e}")
        else:
            logger.warning("Package discovery running without native API")
    
    def search_packages(self, query: str, limit: int = 10) -> List[PackageInfo]:
        """
        Search for packages matching the query
        
        Args:
            query: Search term
            limit: Maximum number of results
            
        Returns:
            List of PackageInfo objects
        """
        if not self.native_api:
            logger.warning(f"No native API available for search: {query}")
            return []
        
        try:
            # Use native API search
            results, _ = self.native_api.search_packages(query)
            
            # Convert to PackageInfo objects
            packages = []
            for result in results[:limit]:
                # Handle both dict and object formats
                if isinstance(result, dict):
                    packages.append(PackageInfo(
                        name=result.get('name', ''),
                        version=result.get('version', ''),
                        description=result.get('description', '')
                    ))
                else:
                    # Assume it has attributes
                    packages.append(PackageInfo(
                        name=getattr(result, 'name', ''),
                        version=getattr(result, 'version', ''),
                        description=getattr(result, 'description', '')
                    ))
            
            logger.info(f"Found {len(packages)} packages for query: {query}")
            return packages
            
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []
    
    def find_package(self, name: str) -> Optional[PackageInfo]:
        """
        Find a specific package by exact name
        
        Args:
            name: Exact package name
            
        Returns:
            PackageInfo if found, None otherwise
        """
        results = self.search_packages(name, limit=50)
        
        # Look for exact match
        for pkg in results:
            if pkg.name == name:
                return pkg
        
        # Look for close match (starts with name)
        for pkg in results:
            if pkg.name.startswith(name):
                return pkg
        
        return None
    
    def suggest_alternatives(self, query: str) -> List[str]:
        """
        Suggest alternative search terms or packages
        
        Args:
            query: Original search query
            
        Returns:
            List of suggested alternatives
        """
        suggestions = []
        
        # Common alternatives
        alternatives = {
            'firefox': ['firefox-esr', 'firefox-bin', 'librewolf'],
            'chrome': ['chromium', 'google-chrome', 'ungoogled-chromium'],
            'vscode': ['vscodium', 'code-server'],
            'vim': ['neovim', 'vim-full', 'gvim'],
            'python': ['python3', 'python311', 'python312'],
            'node': ['nodejs', 'nodejs-18_x', 'nodejs-20_x'],
        }
        
        # Check if we have known alternatives
        if query.lower() in alternatives:
            suggestions.extend(alternatives[query.lower()])
        
        # Try fuzzy search if no results
        results = self.search_packages(query, limit=5)
        if not results and len(query) > 3:
            # Try with partial query
            partial = query[:3]
            results = self.search_packages(partial, limit=5)
            suggestions.extend([r.name for r in results])
        
        return suggestions[:5]  # Limit suggestions


# Singleton instance
_discovery_instance = None

def get_package_discovery() -> PackageDiscovery:
    """Get or create the singleton PackageDiscovery instance"""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = PackageDiscovery()
    return _discovery_instance