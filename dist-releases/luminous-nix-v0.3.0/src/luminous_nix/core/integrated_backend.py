"""
Service Integration Layer - Connects beautiful architecture to production
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

# Import the clean services
from ..services.search import SearchService
from ..services.cache import CacheService
from ..services.executor import NixExecutor
from ..services.config_generator import ConfigGenerator
from ..services.semantic_search import SemanticSearchService

# Import the production backend
from ..core.backend_real import RealNixBackend

class IntegratedBackend:
    """
    Integrates beautiful service architecture with production backend.
    This replaces the messy backend_real.py with clean services.
    """
    
    def __init__(self):
        """Initialize all services"""
        # Initialize clean services
        self.search_service = SearchService()
        self.cache_service = CacheService()
        self.executor = NixExecutor()
        self.config_generator = ConfigGenerator()
        self.semantic_search = SemanticSearchService()
        
        # Keep the real backend for now as fallback
        self.real_backend = RealNixBackend()
        
        print("✅ Integrated backend initialized with clean services")
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages using clean service"""
        # Try cache first
        cached = self.cache_service.get(f"search:{query}")
        if cached:
            return cached
        
        # Use semantic search for better results
        results = self.semantic_search.find_packages(query)
        
        # Cache the results
        self.cache_service.set(f"search:{query}", results)
        
        return results
    
    def install(self, package: str, dry_run: bool = False) -> Dict[str, Any]:
        """Install package using clean executor"""
        return self.executor.install_package(package, dry_run)
    
    def generate_config(self, intent: str) -> str:
        """Generate NixOS configuration from intent"""
        return self.config_generator.generate_from_intent(intent)
    
    def process(self, intent: Any) -> Any:
        """Process intent - fallback to real backend for now"""
        # This allows gradual migration
        return self.real_backend.process(intent)

def get_integrated_backend() -> IntegratedBackend:
    """Get or create singleton integrated backend"""
    global _integrated_backend
    if '_integrated_backend' not in globals():
        _integrated_backend = IntegratedBackend()
    return _integrated_backend
