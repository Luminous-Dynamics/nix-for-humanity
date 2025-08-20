"""
Persistence layer for Luminous Nix

Provides data storage with graceful fallback:
- Primary: Data Trinity (DuckDB, ChromaDB, Kùzu)
- Fallback: SimpleStore (SQLite + JSON)
"""

from .simple_store import SimpleStore, UnifiedPersistence

__all__ = ['SimpleStore', 'UnifiedPersistence']