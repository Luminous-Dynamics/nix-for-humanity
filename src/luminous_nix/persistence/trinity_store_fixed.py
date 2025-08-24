#!/usr/bin/env python3
"""
🔱 The Data Trinity - Fixed Import Handling
Temporal (DuckDB) | Semantic (ChromaDB) | Relational (Kùzu)

This version gracefully handles missing system libraries and
provides helpful messages about using nix-shell.
"""

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Check if we're in nix-shell
IN_NIX_SHELL = os.environ.get('IN_NIX_SHELL') is not None

# The Data Trinity - with intelligent fallback
DUCKDB_AVAILABLE = False
CHROMADB_AVAILABLE = False
KUZU_AVAILABLE = False

# Try to import with better error handling
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError as e:
    if "libstdc++" in str(e):
        if not IN_NIX_SHELL:
            logger.debug("DuckDB requires system libraries. Run in nix-shell for full functionality.")
    else:
        logger.debug(f"DuckDB not installed: {e}")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError as e:
    if "libstdc++" in str(e) or "sqlite3" in str(e):
        if not IN_NIX_SHELL:
            logger.debug("ChromaDB requires system libraries. Run in nix-shell for full functionality.")
    else:
        logger.debug(f"ChromaDB not installed: {e}")
    
try:
    import kuzu
    KUZU_AVAILABLE = True
except ImportError as e:
    if "libstdc++" in str(e):
        if not IN_NIX_SHELL:
            logger.debug("Kùzu requires system libraries. Run in nix-shell for full functionality.")
    else:
        logger.debug(f"Kùzu not installed: {e}")

# If nothing is available but we're not in nix-shell, show helpful message once
if not any([DUCKDB_AVAILABLE, CHROMADB_AVAILABLE, KUZU_AVAILABLE]) and not IN_NIX_SHELL:
    # Only show this once per session
    if not os.environ.get('TRINITY_WARNING_SHOWN'):
        logger.info("💡 Tip: Run 'nix-shell' to enable Data Trinity databases for enhanced memory")
        os.environ['TRINITY_WARNING_SHOWN'] = '1'


@dataclass
class LearningEvent:
    """Represents a learning moment in the user's journey"""
    timestamp: datetime
    user_id: str
    command: str
    concept: str
    success: bool
    error_message: Optional[str]
    context: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class ConceptRelation:
    """Represents how concepts relate to each other"""
    from_concept: str
    to_concept: str
    relation_type: str  # "requires", "builds_on", "similar_to", "opposite_of"
    strength: float  # 0.0 to 1.0


class InMemoryFallbackStore:
    """
    Fallback storage when Data Trinity databases aren't available.
    Provides basic functionality using Python data structures.
    """
    
    def __init__(self, data_dir: Path):
        """Initialize in-memory fallback storage"""
        self.data_dir = data_dir
        self.data_file = data_dir / "fallback_store.json"
        self.data = self._load_data()
        logger.debug(f"📝 Using in-memory fallback store at {self.data_file}")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'learning_events': [],
            'concepts': {},
            'patterns': [],
            'memories': []
        }
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save fallback store: {e}")
    
    def add_learning_event(self, event: Dict[str, Any]):
        """Add a learning event"""
        self.data['learning_events'].append(event)
        
        # Keep only last 1000 events
        if len(self.data['learning_events']) > 1000:
            self.data['learning_events'] = self.data['learning_events'][-1000:]
        
        self._save_data()
    
    def add_concept(self, concept: str, metadata: Dict[str, Any]):
        """Add or update a concept"""
        self.data['concepts'][concept] = metadata
        self._save_data()
    
    def add_pattern(self, pattern: Dict[str, Any]):
        """Add a pattern"""
        self.data['patterns'].append(pattern)
        
        # Keep only last 100 patterns
        if len(self.data['patterns']) > 100:
            self.data['patterns'] = self.data['patterns'][-100:]
        
        self._save_data()
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple text search across all data"""
        results = []
        query_lower = query.lower()
        
        # Search learning events
        for event in self.data['learning_events']:
            if query_lower in str(event).lower():
                results.append({'type': 'event', 'data': event})
        
        # Search concepts
        for concept, metadata in self.data['concepts'].items():
            if query_lower in concept.lower() or query_lower in str(metadata).lower():
                results.append({'type': 'concept', 'data': {'concept': concept, **metadata}})
        
        # Search patterns
        for pattern in self.data['patterns']:
            if query_lower in str(pattern).lower():
                results.append({'type': 'pattern', 'data': pattern})
        
        return results[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data"""
        return {
            'total_events': len(self.data['learning_events']),
            'total_concepts': len(self.data['concepts']),
            'total_patterns': len(self.data['patterns']),
            'storage_type': 'in-memory fallback'
        }


class TrinityStore:
    """
    🔱 Unified interface to the Data Trinity
    
    Intelligently uses available databases or falls back to
    in-memory storage when system libraries aren't available.
    """
    
    def __init__(self, data_dir: Path = None):
        """Initialize the Data Trinity with intelligent fallback"""
        self.data_dir = data_dir or Path.home() / '.local' / 'share' / 'luminous-nix' / 'trinity'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Track what's available
        self.using_trinity = False
        self.temporal = None
        self.semantic = None
        self.relational = None
        
        # Try to initialize the trinity
        if DUCKDB_AVAILABLE or CHROMADB_AVAILABLE or KUZU_AVAILABLE:
            self.using_trinity = True
            
            if DUCKDB_AVAILABLE:
                # Import the actual store classes only if available
                from .trinity_store import TemporalStore
                self.temporal = TemporalStore(self.data_dir)
                logger.info("   ⏰ Temporal (DuckDB) - Active")
            
            if CHROMADB_AVAILABLE:
                from .trinity_store import SemanticStore
                self.semantic = SemanticStore(self.data_dir)
                logger.info("   🧠 Semantic (ChromaDB) - Active")
            
            if KUZU_AVAILABLE:
                from .trinity_store import RelationalStore
                self.relational = RelationalStore(self.data_dir)
                logger.info("   🕸️ Relational (Kùzu) - Active")
        
        # Use fallback if nothing is available
        if not self.using_trinity:
            self.fallback = InMemoryFallbackStore(self.data_dir)
            logger.debug("📝 Using fallback storage (run in nix-shell for full Data Trinity)")
        else:
            self.fallback = None
    
    def record_learning_moment(self, 
                               user_id: str,
                               command: str,
                               concept: str,
                               success: bool,
                               context: Dict[str, Any] = None) -> str:
        """
        Record a learning moment across available databases.
        """
        event_id = hashlib.sha256(
            f"{user_id}{command}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        event_data = {
            'event_id': event_id,
            'timestamp': datetime.now(),
            'user_id': user_id,
            'command': command,
            'concept': concept,
            'success': success,
            'context': context or {}
        }
        
        if self.using_trinity:
            # Use actual trinity stores if available
            if self.temporal:
                self.temporal.add_learning_event(LearningEvent(**event_data))
            if self.semantic:
                self.semantic.store_concept(concept, {'command': command, **context})
            if self.relational:
                # Extract relationships from context
                pass
        else:
            # Use fallback
            self.fallback.add_learning_event(event_data)
            self.fallback.add_concept(concept, {'commands': [command], 'context': context})
        
        return event_id
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search across all available stores.
        """
        if self.using_trinity:
            results = []
            if self.semantic:
                semantic_results = self.semantic.search_similar(query, limit)
                results.extend([{'type': 'semantic', 'data': r} for r in semantic_results])
            # Add temporal and relational search if needed
            return results[:limit]
        else:
            return self.fallback.search(query, limit)
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get insights from available stores.
        """
        if self.using_trinity:
            insights = {'using': 'Data Trinity'}
            if self.temporal:
                insights['temporal'] = 'Active'
            if self.semantic:
                insights['semantic'] = 'Active'
            if self.relational:
                insights['relational'] = 'Active'
            return insights
        else:
            return self.fallback.get_stats()
    
    def close(self):
        """Clean up connections"""
        if self.temporal and hasattr(self.temporal, 'close'):
            self.temporal.close()
        if self.semantic and hasattr(self.semantic, 'close'):
            self.semantic.close()
        if self.relational and hasattr(self.relational, 'close'):
            self.relational.close()


# Helper function for easy import
def create_trinity_store(data_dir: Path = None) -> TrinityStore:
    """
    Create a TrinityStore with intelligent fallback.
    
    Will use Data Trinity databases if available (in nix-shell),
    otherwise falls back to in-memory storage.
    """
    return TrinityStore(data_dir)