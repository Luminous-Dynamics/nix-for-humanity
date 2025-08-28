"""
Store to Trinity Bridge - Progressive Data Persistence Integration

This bridge connects the working SimpleStore to the aspirational Data Trinity
(DuckDB, ChromaDB, Kùzu), enabling gradual migration from in-memory to
persistent, intelligent storage.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class StorageMode(Enum):
    """Progressive storage modes"""
    MEMORY_ONLY = "memory"        # Current: SimpleStore in-memory
    MEMORY_BACKED = "backed"       # SimpleStore with JSON backup
    DUCKDB_TEMPORAL = "duckdb"    # DuckDB for time-series
    CHROMADB_SEMANTIC = "chromadb" # ChromaDB for semantic search
    KUZU_GRAPH = "kuzu"           # Kùzu for relationships
    TRINITY_UNIFIED = "trinity"    # All three working together


@dataclass
class StorageEvent:
    """Event for storage operations"""
    timestamp: str
    operation: str  # save, load, query, delete
    key: str
    value: Any
    storage_mode: StorageMode
    success: bool
    metadata: Dict[str, Any]


class StoreTrinityBridge:
    """
    Bridges SimpleStore to Data Trinity with progressive activation.
    
    This allows gradual migration from in-memory storage to the full
    trinity of specialized databases as each becomes ready.
    """
    
    def __init__(self, readiness: float = 0.4):
        """
        Initialize bridge with readiness level.
        
        Args:
            readiness: Current readiness (0.0 to 1.0)
                      0.0-0.2: Memory only
                      0.2-0.4: Memory with JSON backup
                      0.4-0.6: DuckDB activated
                      0.6-0.8: ChromaDB added
                      0.8-1.0: Full Trinity with Kùzu
        """
        self.readiness = readiness
        self.storage_mode = self._determine_storage_mode()
        
        # Storage backends (progressively activated)
        self.memory_store: Dict[str, Any] = {}
        self.backup_path = Path.home() / '.local' / 'share' / 'luminous-nix' / 'store_backup.json'
        self.duckdb_path = Path.home() / '.local' / 'share' / 'luminous-nix' / 'temporal.duckdb'
        self.chromadb_path = Path.home() / '.local' / 'share' / 'luminous-nix' / 'semantic'
        self.kuzu_path = Path.home() / '.local' / 'share' / 'luminous-nix' / 'graph'
        
        # Event history for temporal patterns
        self.events: List[StorageEvent] = []
        
        # Initialize available backends
        self._initialize_backends()
        
    def _determine_storage_mode(self) -> StorageMode:
        """Determine storage mode based on readiness"""
        if self.readiness < 0.2:
            return StorageMode.MEMORY_ONLY
        elif self.readiness < 0.4:
            return StorageMode.MEMORY_BACKED
        elif self.readiness < 0.6:
            return StorageMode.DUCKDB_TEMPORAL
        elif self.readiness < 0.8:
            return StorageMode.CHROMADB_SEMANTIC
        elif self.readiness < 1.0:
            return StorageMode.KUZU_GRAPH
        else:
            return StorageMode.TRINITY_UNIFIED
    
    def _initialize_backends(self):
        """Initialize storage backends based on readiness"""
        # Always have memory store
        logger.info(f"Storage mode: {self.storage_mode.value} (readiness: {self.readiness:.1%})")
        
        # Initialize JSON backup if ready
        if self.readiness >= 0.2:
            self._initialize_json_backup()
        
        # Initialize DuckDB if ready
        if self.readiness >= 0.4:
            self._initialize_duckdb()
        
        # Initialize ChromaDB if ready
        if self.readiness >= 0.6:
            self._initialize_chromadb()
        
        # Initialize Kùzu if ready
        if self.readiness >= 0.8:
            self._initialize_kuzu()
    
    def _initialize_json_backup(self):
        """Initialize JSON backup storage"""
        self.backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing backup if available
        if self.backup_path.exists():
            try:
                with open(self.backup_path, 'r') as f:
                    self.memory_store = json.load(f)
                logger.info(f"Loaded {len(self.memory_store)} items from backup")
            except Exception as e:
                logger.warning(f"Failed to load backup: {e}")
    
    def _initialize_duckdb(self):
        """Initialize DuckDB for temporal patterns"""
        try:
            import duckdb
            
            self.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
            self.duckdb_conn = duckdb.connect(str(self.duckdb_path))
            
            # Create events table for temporal analysis
            self.duckdb_conn.execute("""
                CREATE TABLE IF NOT EXISTS storage_events (
                    timestamp TIMESTAMP,
                    operation VARCHAR,
                    key VARCHAR,
                    value JSON,
                    success BOOLEAN,
                    metadata JSON
                )
            """)
            
            # Create key-value table with temporal tracking
            self.duckdb_conn.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key VARCHAR PRIMARY KEY,
                    value JSON,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP
                )
            """)
            
            logger.info("✅ DuckDB initialized for temporal storage")
            
        except ImportError:
            logger.warning("DuckDB not available - install with: pip install duckdb")
            self.readiness = min(self.readiness, 0.39)  # Cap readiness
            self.storage_mode = StorageMode.MEMORY_BACKED
        except Exception as e:
            logger.error(f"Failed to initialize DuckDB: {e}")
            self.readiness = min(self.readiness, 0.39)
            self.storage_mode = StorageMode.MEMORY_BACKED
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB for semantic search"""
        try:
            import chromadb
            
            self.chromadb_path.mkdir(parents=True, exist_ok=True)
            self.chromadb_client = chromadb.PersistentClient(path=str(self.chromadb_path))
            
            # Create collection for semantic search
            self.semantic_collection = self.chromadb_client.get_or_create_collection(
                name="luminous_nix_memory",
                metadata={"description": "Semantic memory for Luminous Nix"}
            )
            
            logger.info("✅ ChromaDB initialized for semantic storage")
            
        except ImportError:
            logger.warning("ChromaDB not available - install with: pip install chromadb")
            self.readiness = min(self.readiness, 0.59)
            self.storage_mode = StorageMode.DUCKDB_TEMPORAL
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.readiness = min(self.readiness, 0.59)
            self.storage_mode = StorageMode.DUCKDB_TEMPORAL
    
    def _initialize_kuzu(self):
        """Initialize Kùzu for graph relationships"""
        try:
            import kuzu
            
            self.kuzu_path.mkdir(parents=True, exist_ok=True)
            self.kuzu_db = kuzu.Database(str(self.kuzu_path))
            self.kuzu_conn = kuzu.Connection(self.kuzu_db)
            
            # Create nodes for entities
            self.kuzu_conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS Entity(
                    id STRING PRIMARY KEY,
                    type STRING,
                    data JSON,
                    created_at TIMESTAMP
                )
            """)
            
            # Create relationships
            self.kuzu_conn.execute("""
                CREATE REL TABLE IF NOT EXISTS Related(
                    FROM Entity TO Entity,
                    relationship STRING,
                    strength DOUBLE,
                    metadata JSON
                )
            """)
            
            logger.info("✅ Kùzu initialized for graph storage")
            
        except ImportError:
            logger.warning("Kùzu not available - install with: pip install kuzu")
            self.readiness = min(self.readiness, 0.79)
            self.storage_mode = StorageMode.CHROMADB_SEMANTIC
        except Exception as e:
            logger.error(f"Failed to initialize Kùzu: {e}")
            self.readiness = min(self.readiness, 0.79)
            self.storage_mode = StorageMode.CHROMADB_SEMANTIC
    
    def save(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save data with progressive storage activation.
        
        Args:
            key: Storage key
            value: Value to store
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        success = False
        timestamp = datetime.now().isoformat()
        
        # Always save to memory
        self.memory_store[key] = value
        success = True
        
        # Progressive storage based on mode
        if self.readiness >= 0.2:  # MEMORY_BACKED threshold
            success = success and self._save_to_json()
        
        if self.readiness >= 0.4:  # DUCKDB_TEMPORAL threshold
            success = success and self._save_to_duckdb(key, value, timestamp)
        
        if self.readiness >= 0.6:  # CHROMADB_SEMANTIC threshold
            success = success and self._save_to_chromadb(key, value, metadata)
        
        if self.readiness >= 0.8:  # KUZU_GRAPH threshold
            success = success and self._save_to_kuzu(key, value, metadata)
        
        # Record event
        event = StorageEvent(
            timestamp=timestamp,
            operation="save",
            key=key,
            value=value,
            storage_mode=self.storage_mode,
            success=success,
            metadata=metadata or {}
        )
        self.events.append(event)
        
        # Adjust readiness based on success
        if success:
            self.adjust_readiness(0.001)  # Small increase
        else:
            self.adjust_readiness(-0.01)  # Larger decrease
        
        return success
    
    def _save_to_json(self) -> bool:
        """Save memory store to JSON backup"""
        try:
            with open(self.backup_path, 'w') as f:
                json.dump(self.memory_store, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON backup: {e}")
            return False
    
    def _save_to_duckdb(self, key: str, value: Any, timestamp: str) -> bool:
        """Save to DuckDB with temporal tracking"""
        if not hasattr(self, 'duckdb_conn'):
            return False
        
        try:
            # Upsert into key-value store
            self.duckdb_conn.execute("""
                INSERT INTO kv_store (key, value, created_at, updated_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    updated_at = EXCLUDED.updated_at,
                    access_count = kv_store.access_count + 1,
                    last_accessed = EXCLUDED.last_accessed
            """, [key, json.dumps(value), timestamp, timestamp, timestamp])
            
            return True
        except Exception as e:
            logger.error(f"Failed to save to DuckDB: {e}")
            return False
    
    def _save_to_chromadb(self, key: str, value: Any, metadata: Optional[Dict[str, Any]]) -> bool:
        """Save to ChromaDB for semantic search"""
        if not hasattr(self, 'semantic_collection'):
            return False
        
        try:
            # Convert value to text for embedding
            text = json.dumps(value) if not isinstance(value, str) else value
            
            # Add to collection
            self.semantic_collection.upsert(
                ids=[key],
                documents=[text],
                metadatas=[metadata or {"key": key}]
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to save to ChromaDB: {e}")
            return False
    
    def _save_to_kuzu(self, key: str, value: Any, metadata: Optional[Dict[str, Any]]) -> bool:
        """Save to Kùzu graph database"""
        if not hasattr(self, 'kuzu_conn'):
            return False
        
        try:
            # Create or update entity node
            self.kuzu_conn.execute("""
                MERGE (e:Entity {id: $key})
                SET e.type = $type, e.data = $data, e.created_at = $timestamp
            """, {
                "key": key,
                "type": metadata.get("type", "unknown") if metadata else "unknown",
                "data": json.dumps(value),
                "timestamp": datetime.now().isoformat()
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to save to Kùzu: {e}")
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """
        Load data with progressive storage querying.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None
        """
        value = None
        timestamp = datetime.now().isoformat()
        
        # Try progressive loading based on readiness
        if self.readiness >= 0.8:  # KUZU_GRAPH threshold
            # Try Kùzu first (most connected data)
            value = self._load_from_kuzu(key)
        
        if value is None and self.readiness >= 0.6:  # CHROMADB_SEMANTIC threshold
            # Try ChromaDB (semantic memory)
            value = self._load_from_chromadb(key)
        
        if value is None and self.readiness >= 0.4:  # DUCKDB_TEMPORAL threshold
            # Try DuckDB (temporal storage)
            value = self._load_from_duckdb(key)
        
        if value is None:
            # Fall back to memory store
            value = self.memory_store.get(key)
        
        # Record event
        event = StorageEvent(
            timestamp=timestamp,
            operation="load",
            key=key,
            value=value,
            storage_mode=self.storage_mode,
            success=value is not None,
            metadata={}
        )
        self.events.append(event)
        
        return value
    
    def _load_from_duckdb(self, key: str) -> Optional[Any]:
        """Load from DuckDB"""
        if not hasattr(self, 'duckdb_conn'):
            return None
        
        try:
            result = self.duckdb_conn.execute("""
                UPDATE kv_store 
                SET access_count = access_count + 1,
                    last_accessed = CAST(? AS TIMESTAMP)
                WHERE key = ?
                RETURNING value
            """, [datetime.now().isoformat(), key]).fetchone()
            
            if result:
                return json.loads(result[0])
        except Exception as e:
            logger.error(f"Failed to load from DuckDB: {e}")
        
        return None
    
    def _load_from_chromadb(self, key: str) -> Optional[Any]:
        """Load from ChromaDB"""
        if not hasattr(self, 'semantic_collection'):
            return None
        
        try:
            result = self.semantic_collection.get(ids=[key])
            if result['documents']:
                doc = result['documents'][0]
                try:
                    return json.loads(doc)
                except:
                    return doc
        except Exception as e:
            logger.error(f"Failed to load from ChromaDB: {e}")
        
        return None
    
    def _load_from_kuzu(self, key: str) -> Optional[Any]:
        """Load from Kùzu"""
        if not hasattr(self, 'kuzu_conn'):
            return None
        
        try:
            result = self.kuzu_conn.execute("""
                MATCH (e:Entity {id: $key})
                RETURN e.data
            """, {"key": key}).get_next()
            
            if result:
                return json.loads(result[0])
        except Exception as e:
            logger.error(f"Failed to load from Kùzu: {e}")
        
        return None
    
    def query_temporal(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Query temporal patterns (DuckDB feature).
        
        Args:
            pattern: SQL pattern for temporal query
            
        Returns:
            List of matching records
        """
        if not hasattr(self, 'duckdb_conn'):
            logger.warning("DuckDB not available for temporal queries")
            return []
        
        try:
            # Example: Find most accessed keys in last hour
            if pattern == "recent_popular":
                results = self.duckdb_conn.execute("""
                    SELECT key, value, access_count, last_accessed
                    FROM kv_store
                    WHERE last_accessed > datetime('now', '-1 hour')
                    ORDER BY access_count DESC
                    LIMIT 10
                """).fetchall()
                
                return [
                    {
                        "key": r[0],
                        "value": json.loads(r[1]),
                        "access_count": r[2],
                        "last_accessed": r[3]
                    }
                    for r in results
                ]
        except Exception as e:
            logger.error(f"Temporal query failed: {e}")
        
        return []
    
    def search_semantic(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search (ChromaDB feature).
        
        Args:
            query: Search query
            n_results: Number of results
            
        Returns:
            List of semantically similar items
        """
        if not hasattr(self, 'semantic_collection'):
            logger.warning("ChromaDB not available for semantic search")
            return []
        
        try:
            results = self.semantic_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return [
                {
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None,
                    "metadata": results['metadatas'][0][i] if 'metadatas' in results else {}
                }
                for i in range(len(results['ids'][0]))
            ]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
        
        return []
    
    def find_related(self, key: str, relationship: str = "related") -> List[Dict[str, Any]]:
        """
        Find related entities (Kùzu feature).
        
        Args:
            key: Entity key
            relationship: Type of relationship
            
        Returns:
            List of related entities
        """
        if not hasattr(self, 'kuzu_conn'):
            logger.warning("Kùzu not available for graph queries")
            return []
        
        try:
            results = self.kuzu_conn.execute("""
                MATCH (e1:Entity {id: $key})-[r:Related {relationship: $rel}]->(e2:Entity)
                RETURN e2.id, e2.data, r.strength
                ORDER BY r.strength DESC
            """, {"key": key, "rel": relationship}).get_all()
            
            return [
                {
                    "id": r[0],
                    "data": json.loads(r[1]),
                    "strength": r[2]
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Graph query failed: {e}")
        
        return []
    
    def adjust_readiness(self, delta: float):
        """Adjust readiness level based on performance"""
        old_readiness = self.readiness
        self.readiness = max(0.0, min(1.0, self.readiness + delta))
        
        # Check if storage mode should change
        new_mode = self._determine_storage_mode()
        if new_mode != self.storage_mode:
            logger.info(f"Storage mode advancing: {self.storage_mode.value} → {new_mode.value}")
            self.storage_mode = new_mode
            self._initialize_backends()  # Re-initialize with new mode
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        total_events = len(self.events)
        successful_events = sum(1 for e in self.events if e.success)
        success_rate = successful_events / total_events if total_events > 0 else 0
        
        # Count events by operation
        operations = {}
        for event in self.events:
            operations[event.operation] = operations.get(event.operation, 0) + 1
        
        return {
            'readiness': self.readiness,
            'storage_mode': self.storage_mode.value,
            'total_events': total_events,
            'success_rate': success_rate,
            'operations': operations,
            'memory_items': len(self.memory_store),
            'backends_available': {
                'json_backup': self.readiness >= 0.2,
                'duckdb': hasattr(self, 'duckdb_conn'),
                'chromadb': hasattr(self, 'semantic_collection'),
                'kuzu': hasattr(self, 'kuzu_conn')
            }
        }
    
    def progressive_test(self) -> bool:
        """Test bridge with progressive complexity"""
        test_data = [
            ("simple_key", "simple_value"),
            ("complex_key", {"nested": {"data": [1, 2, 3]}}),
            ("temporal_key", {"timestamp": datetime.now().isoformat()}),
        ]
        
        results = []
        for key, value in test_data:
            # Test save and load
            save_success = self.save(key, value)
            loaded = self.load(key)
            load_success = loaded == value
            
            results.append(save_success and load_success)
            logger.info(f"Test {key}: save={save_success}, load={load_success}")
        
        # Test advanced features if available
        if self.readiness >= 0.4:  # DUCKDB_TEMPORAL threshold
            temporal_results = self.query_temporal("recent_popular")
            logger.info(f"Temporal query returned {len(temporal_results)} results")
        
        if self.readiness >= 0.6:  # CHROMADB_SEMANTIC threshold
            semantic_results = self.search_semantic("test query")
            logger.info(f"Semantic search returned {len(semantic_results)} results")
        
        # Adjust readiness based on results
        if all(results):
            self.adjust_readiness(0.05)
            return True
        else:
            self.adjust_readiness(-0.02)
            return False


# Integration helper
def integrate_with_simple_store(simple_store, trinity_store=None):
    """
    Helper to integrate SimpleStore with Trinity Bridge.
    
    This allows existing code to progressively use advanced storage.
    """
    bridge = StoreTrinityBridge(readiness=0.4)  # Start with DuckDB ready
    
    class EnhancedStore:
        """Enhanced store with progressive Trinity features"""
        
        def __init__(self):
            self.bridge = bridge
            self.simple = simple_store
        
        def save(self, key: str, value: Any) -> bool:
            """Save with progressive persistence"""
            return self.bridge.save(key, value)
        
        def load(self, key: str) -> Optional[Any]:
            """Load with progressive querying"""
            return self.bridge.load(key)
        
        def search(self, query: str) -> List[Any]:
            """Semantic search if available"""
            if self.bridge.readiness >= 0.6:  # CHROMADB_SEMANTIC threshold
                return self.bridge.search_semantic(query)
            else:
                # Fallback to simple search
                return [v for k, v in self.bridge.memory_store.items() 
                       if query.lower() in str(v).lower()]
        
        def get_popular(self) -> List[Any]:
            """Get popular items if temporal tracking available"""
            if self.bridge.readiness >= 0.4:  # DUCKDB_TEMPORAL threshold
                return self.bridge.query_temporal("recent_popular")
            else:
                # Fallback to recent items
                return list(self.bridge.memory_store.values())[-10:]
    
    return EnhancedStore()