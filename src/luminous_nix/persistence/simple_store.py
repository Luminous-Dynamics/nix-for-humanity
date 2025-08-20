#!/usr/bin/env python3
"""
🗄️ Simple Persistence Layer - Fallback when Data Trinity is unavailable

This provides basic data persistence using JSON files when the full
Data Trinity (DuckDB, ChromaDB, Kùzu) is not available.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SimpleStore:
    """
    Simple JSON/SQLite based persistence fallback.
    
    This provides basic storage when advanced databases aren't available,
    ensuring the system can always persist essential data.
    """
    
    def __init__(self, data_dir: Path = None):
        """Initialize simple store with JSON and SQLite fallback."""
        self.data_dir = data_dir or Path.home() / '.local' / 'share' / 'nix-for-humanity' / 'data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite for structured data
        self.db_path = self.data_dir / 'simple_store.db'
        self._init_db()
        
        # JSON files for complex objects
        self.json_dir = self.data_dir / 'json'
        self.json_dir.mkdir(exist_ok=True)
        
        logger.info(f"📦 Simple store initialized at {self.data_dir}")
    
    def _init_db(self):
        """Initialize SQLite database with basic schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                intent TEXT,
                action TEXT,
                result TEXT,
                success INTEGER,
                user_id TEXT
            )
        """)
        
        # Errors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                error_type TEXT,
                error_message TEXT,
                solution TEXT,
                context TEXT
            )
        """)
        
        # Configurations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                name TEXT,
                description TEXT,
                config_json TEXT
            )
        """)
        
        # Preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                user_id TEXT PRIMARY KEY,
                preferences_json TEXT,
                last_updated TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    # === Interaction Storage ===
    
    def store_interaction(self, intent: str, action: str, result: str, 
                         success: bool, user_id: str = 'default') -> int:
        """Store a user interaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions (timestamp, intent, action, result, success, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), intent, action, result, int(success), user_id))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return interaction_id
    
    def get_recent_interactions(self, limit: int = 10, user_id: str = None) -> List[Dict]:
        """Get recent interactions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT * FROM interactions 
                WHERE user_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM interactions 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    # === Error Storage ===
    
    def store_error(self, error_type: str, error_message: str, 
                   solution: str, context: str = None) -> int:
        """Store an error and its solution."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO errors (timestamp, error_type, error_message, solution, context)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), error_type, error_message, solution, context))
        
        error_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return error_id
    
    def find_similar_errors(self, error_message: str, limit: int = 5) -> List[Dict]:
        """Find similar errors (simple substring matching)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple LIKE matching - not as good as semantic search but works
        cursor.execute("""
            SELECT * FROM errors 
            WHERE error_message LIKE ?
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (f'%{error_message[:30]}%', limit))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    # === Configuration Storage ===
    
    def store_configuration(self, name: str, description: str, config: Dict) -> int:
        """Store a configuration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO configurations (timestamp, name, description, config_json)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), name, description, json.dumps(config)))
        
        config_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return config_id
    
    def get_configuration(self, name: str) -> Optional[Dict]:
        """Get a configuration by name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT config_json FROM configurations 
            WHERE name = ?
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    # === Preference Storage ===
    
    def store_preferences(self, user_id: str, preferences: Dict):
        """Store user preferences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO preferences (user_id, preferences_json, last_updated)
            VALUES (?, ?, ?)
        """, (user_id, json.dumps(preferences), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT preferences_json FROM preferences 
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    # === JSON Storage for Complex Objects ===
    
    def store_json(self, key: str, data: Any):
        """Store arbitrary data as JSON."""
        file_path = self.json_dir / f"{key}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_json(self, key: str) -> Optional[Any]:
        """Load JSON data."""
        file_path = self.json_dir / f"{key}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def list_json_keys(self) -> List[str]:
        """List all JSON keys."""
        return [f.stem for f in self.json_dir.glob("*.json")]
    
    # === Statistics ===
    
    def get_statistics(self) -> Dict[str, int]:
        """Get storage statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count interactions
        cursor.execute("SELECT COUNT(*) FROM interactions")
        stats['interactions'] = cursor.fetchone()[0]
        
        # Count errors
        cursor.execute("SELECT COUNT(*) FROM errors")
        stats['errors'] = cursor.fetchone()[0]
        
        # Count configurations
        cursor.execute("SELECT COUNT(*) FROM configurations")
        stats['configurations'] = cursor.fetchone()[0]
        
        # Count users with preferences
        cursor.execute("SELECT COUNT(*) FROM preferences")
        stats['users'] = cursor.fetchone()[0]
        
        conn.close()
        
        # Count JSON files
        stats['json_objects'] = len(list(self.json_dir.glob("*.json")))
        
        return stats


class UnifiedPersistence:
    """
    Unified persistence interface that uses Data Trinity when available,
    falls back to SimpleStore otherwise.
    """
    
    def __init__(self, data_dir: Path = None):
        """Initialize with best available storage backend."""
        self.data_dir = data_dir or Path.home() / '.local' / 'share' / 'nix-for-humanity' / 'data'
        
        # Try to initialize Data Trinity
        self.duckdb_available = False
        self.chromadb_available = False
        self.kuzu_available = False
        
        try:
            import duckdb
            self.duckdb_available = True
            logger.info("✅ DuckDB available")
        except ImportError:
            logger.info("⚠️ DuckDB not available")
        
        try:
            import chromadb
            self.chromadb_available = True
            logger.info("✅ ChromaDB available")
        except ImportError:
            logger.info("⚠️ ChromaDB not available")
        
        try:
            import kuzu
            self.kuzu_available = True
            logger.info("✅ Kùzu available")
        except ImportError:
            logger.info("⚠️ Kùzu not available")
        
        # Always initialize SimpleStore as fallback
        self.simple_store = SimpleStore(data_dir)
        
        # Initialize advanced stores if available
        if self.chromadb_available:
            try:
                from luminous_nix.memory.semantic_memory import SemanticMemoryField
                self.semantic_memory = SemanticMemoryField(self.data_dir / 'chromadb')
            except Exception as e:
                logger.warning(f"Could not initialize semantic memory: {e}")
                self.semantic_memory = None
        else:
            self.semantic_memory = None
    
    def store_interaction(self, intent: str, action: str, result: str, success: bool):
        """Store interaction using best available method."""
        # Always store in simple store
        self.simple_store.store_interaction(intent, action, result, success)
        
        # Also store in semantic memory if available
        if self.semantic_memory:
            try:
                self.semantic_memory.remember_interaction(intent, action, result, success)
            except Exception as e:
                logger.warning(f"Could not store in semantic memory: {e}")
    
    def find_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """Find similar items using best available method."""
        if self.semantic_memory:
            try:
                return self.semantic_memory.recall_similar(query, n_results=limit)
            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")
        
        # Fallback to simple search
        return self.simple_store.find_similar_errors(query, limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get combined statistics from all stores."""
        stats = {'simple_store': self.simple_store.get_statistics()}
        
        if self.semantic_memory:
            try:
                stats['semantic_memory'] = self.semantic_memory.get_statistics()
            except:
                pass
        
        return stats