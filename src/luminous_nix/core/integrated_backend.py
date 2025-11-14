"""
Service Integration Layer - Connects beautiful architecture to production
"""

from typing import Any

from ..services.cache import CacheService
from ..services.config_generator import ConfigGenerator
from ..services.executor import NixExecutor

# Import the clean services
from ..services.search import SearchService

# Try to import semantic search if numpy is available
try:
    from ..services.semantic_search import SemanticSearchService

    HAS_SEMANTIC_SEARCH = True
except ImportError:
    HAS_SEMANTIC_SEARCH = False

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

        # Only initialize semantic search if available
        if HAS_SEMANTIC_SEARCH:
            self.semantic_search = SemanticSearchService()
        else:
            self.semantic_search = None

        # Keep the real backend for now as fallback
        self.real_backend = RealNixBackend()

        if HAS_SEMANTIC_SEARCH:
            print("✅ Integrated backend initialized with semantic search")
        else:
            print("✅ Integrated backend initialized (semantic search unavailable)")

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search for packages using clean service"""
        # Try cache first
        cached = self.cache_service.get(f"search:{query}")
        if cached:
            return cached

        # Use semantic search if available, otherwise regular search
        if self.semantic_search:
            results = self.semantic_search.find_packages(query)
        else:
            results = self.search_service.search(query)

        # Cache the results
        self.cache_service.set(f"search:{query}", results)

        return results

    def install(self, package: str, dry_run: bool = False) -> dict[str, Any]:
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
    if "_integrated_backend" not in globals():
        _integrated_backend = IntegratedBackend()
    return _integrated_backend
