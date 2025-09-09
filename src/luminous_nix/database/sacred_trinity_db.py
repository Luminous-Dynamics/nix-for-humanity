"""
Sacred Trinity Database Model
A robust, lock-free database solution combining three approaches:
1. SQLite with WAL mode for persistence
2. In-memory cache for speed
3. Write queue for conflict-free operations
"""

import json
import sqlite3
import threading
import time
from collections import deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import queue


class SacredTrinityDB:
    """
    Trinity database model combining:
    1. Persistence Layer (SQLite with WAL)
    2. Memory Layer (Fast cache)
    3. Queue Layer (Conflict-free writes)
    
    This solves the locking issues while maintaining performance
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the trinity database"""
        # 1. Persistence Layer - SQLite with WAL mode
        if db_path is None:
            db_path = Path.home() / ".cache" / "luminous-nix" / "trinity.db"
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        
        # Create connection with WAL mode for better concurrency
        self.conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        
        # Enable WAL mode for better concurrent access
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=10000")
        self.conn.execute("PRAGMA temp_store=MEMORY")
        
        # 2. Memory Layer - Fast in-memory cache
        self.memory_cache = {}
        self.cache_lock = threading.RLock()
        
        # 3. Queue Layer - Write queue for conflict-free operations
        self.write_queue = queue.Queue()
        self.write_thread = None
        self.stop_writer = threading.Event()
        
        # Initialize schema
        self._init_schema()
        
        # Start write worker
        self._start_write_worker()
        
        # Load recent data into memory
        self._load_to_memory()
    
    def _init_schema(self):
        """Initialize database schema"""
        # Create tables with indexes
        schemas = [
            # Events table
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Key-value store for flexible data
            """
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Analytics aggregates (pre-computed for speed)
            """
            CREATE TABLE IF NOT EXISTS analytics (
                metric_name TEXT PRIMARY KEY,
                metric_value REAL,
                metric_data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Create indexes for performance
            "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id)"
        ]
        
        for schema in schemas:
            self.conn.execute(schema)
        
        self.conn.commit()
    
    def _start_write_worker(self):
        """Start background write worker thread"""
        def write_worker():
            """Process write queue"""
            batch = []
            last_flush = time.time()
            
            while not self.stop_writer.is_set():
                try:
                    # Try to get item with timeout
                    try:
                        operation = self.write_queue.get(timeout=0.1)
                        batch.append(operation)
                    except queue.Empty:
                        pass
                    
                    # Flush batch if:
                    # 1. Batch is large enough (100 items)
                    # 2. Enough time has passed (1 second)
                    # 3. Queue is empty and we have items
                    should_flush = (
                        len(batch) >= 100 or
                        (time.time() - last_flush > 1 and batch) or
                        (self.write_queue.empty() and batch)
                    )
                    
                    if should_flush:
                        self._flush_batch(batch)
                        batch = []
                        last_flush = time.time()
                
                except Exception as e:
                    # Log error but don't crash
                    print(f"Write worker error: {e}")
                    batch = []  # Clear problematic batch
        
        self.write_thread = threading.Thread(target=write_worker, daemon=True)
        self.write_thread.start()
    
    def _flush_batch(self, batch: List[Dict]):
        """Flush a batch of operations to database"""
        if not batch:
            return
        
        cursor = self.conn.cursor()
        
        try:
            # Group operations by type for efficiency
            events = []
            kv_updates = []
            analytics = []
            
            for op in batch:
                op_type = op.get('type')
                
                if op_type == 'event':
                    events.append(op['data'])
                elif op_type == 'kv':
                    kv_updates.append(op['data'])
                elif op_type == 'analytics':
                    analytics.append(op['data'])
            
            # Batch insert events
            if events:
                cursor.executemany(
                    """
                    INSERT INTO events (timestamp, event_type, data, session_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    events
                )
            
            # Batch update key-value pairs
            if kv_updates:
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO kv_store (key, value)
                    VALUES (?, ?)
                    """,
                    kv_updates
                )
            
            # Batch update analytics
            if analytics:
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO analytics (metric_name, metric_value, metric_data)
                    VALUES (?, ?, ?)
                    """,
                    analytics
                )
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Batch flush error: {e}")
            self.conn.rollback()
    
    def _load_to_memory(self):
        """Load recent/important data to memory cache"""
        with self.cache_lock:
            try:
                # Load recent events (last 100)
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT timestamp, event_type, data, session_id
                    FROM events
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)
                
                self.memory_cache['recent_events'] = [
                    {
                        'timestamp': row[0],
                        'event_type': row[1],
                        'data': json.loads(row[2]) if row[2] else {},
                        'session_id': row[3]
                    }
                    for row in cursor.fetchall()
                ]
                
                # Load all key-value pairs
                cursor.execute("SELECT key, value FROM kv_store")
                self.memory_cache['kv'] = {
                    row[0]: json.loads(row[1]) if row[1] else None
                    for row in cursor.fetchall()
                }
                
                # Load analytics
                cursor.execute("SELECT metric_name, metric_value, metric_data FROM analytics")
                self.memory_cache['analytics'] = {
                    row[0]: {
                        'value': row[1],
                        'data': json.loads(row[2]) if row[2] else None
                    }
                    for row in cursor.fetchall()
                }
                
            except Exception as e:
                print(f"Memory load error: {e}")
                self.memory_cache = {
                    'recent_events': [],
                    'kv': {},
                    'analytics': {}
                }
    
    # === Public API ===
    
    def track_event(self, event_type: str, data: Any, session_id: Optional[str] = None):
        """
        Track an event (non-blocking)
        """
        timestamp = time.time()
        
        # Add to memory cache immediately
        with self.cache_lock:
            if 'recent_events' not in self.memory_cache:
                self.memory_cache['recent_events'] = []
            
            event = {
                'timestamp': timestamp,
                'event_type': event_type,
                'data': data,
                'session_id': session_id
            }
            
            self.memory_cache['recent_events'].insert(0, event)
            
            # Keep only last 100 in memory
            self.memory_cache['recent_events'] = self.memory_cache['recent_events'][:100]
        
        # Queue for persistent storage
        self.write_queue.put({
            'type': 'event',
            'data': (timestamp, event_type, json.dumps(data), session_id)
        })
    
    def set_value(self, key: str, value: Any):
        """
        Set a key-value pair (non-blocking)
        """
        # Update memory immediately
        with self.cache_lock:
            if 'kv' not in self.memory_cache:
                self.memory_cache['kv'] = {}
            self.memory_cache['kv'][key] = value
        
        # Queue for persistence
        self.write_queue.put({
            'type': 'kv',
            'data': (key, json.dumps(value))
        })
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value (from memory, instant)
        """
        with self.cache_lock:
            return self.memory_cache.get('kv', {}).get(key, default)
    
    def update_metric(self, metric_name: str, value: float, data: Optional[Any] = None):
        """
        Update an analytics metric (non-blocking)
        """
        # Update memory
        with self.cache_lock:
            if 'analytics' not in self.memory_cache:
                self.memory_cache['analytics'] = {}
            
            self.memory_cache['analytics'][metric_name] = {
                'value': value,
                'data': data
            }
        
        # Queue for persistence
        self.write_queue.put({
            'type': 'analytics',
            'data': (metric_name, value, json.dumps(data) if data else None)
        })
    
    def get_metric(self, metric_name: str) -> Optional[Dict]:
        """
        Get a metric (from memory, instant)
        """
        with self.cache_lock:
            return self.memory_cache.get('analytics', {}).get(metric_name)
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """
        Get recent events (from memory, instant)
        """
        with self.cache_lock:
            events = self.memory_cache.get('recent_events', [])
            return events[:limit]
    
    def query(self, sql: str, params: Tuple = ()) -> List[Tuple]:
        """
        Execute a read query (direct from database)
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def get_analytics_summary(self) -> Dict:
        """
        Get analytics summary (from memory, instant)
        """
        with self.cache_lock:
            return dict(self.memory_cache.get('analytics', {}))
    
    def flush(self):
        """
        Force flush write queue
        """
        # Wait for queue to empty
        while not self.write_queue.empty():
            time.sleep(0.01)
        
        # Give writer time to process
        time.sleep(0.1)
    
    def close(self):
        """
        Clean shutdown
        """
        # Stop writer thread
        self.stop_writer.set()
        if self.write_thread:
            self.write_thread.join(timeout=2)
        
        # Flush remaining items
        remaining = []
        while not self.write_queue.empty():
            try:
                remaining.append(self.write_queue.get_nowait())
            except queue.Empty:
                break
        
        if remaining:
            self._flush_batch(remaining)
        
        # Close connection
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# === Specialized Database Variants ===

class AnalyticsDB(SacredTrinityDB):
    """
    Specialized for analytics with pre-computed aggregates
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize analytics database"""
        if db_path is None:
            db_path = Path.home() / ".cache" / "luminous-nix" / "analytics_trinity.db"
        
        super().__init__(db_path)
        
        # Pre-compute common metrics
        self._init_analytics_tables()
    
    def _init_analytics_tables(self):
        """Initialize analytics-specific tables"""
        schemas = [
            """
            CREATE TABLE IF NOT EXISTS hourly_stats (
                hour INTEGER PRIMARY KEY,
                query_count INTEGER DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                avg_response_ms REAL DEFAULT 0
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS package_stats (
                package_name TEXT PRIMARY KEY,
                search_count INTEGER DEFAULT 0,
                install_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS query_patterns (
                pattern TEXT PRIMARY KEY,
                frequency INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for schema in schemas:
            self.conn.execute(schema)
        
        self.conn.commit()
    
    def increment_package_stat(self, package: str, stat_type: str = 'search'):
        """Increment package statistics"""
        sql = f"""
            INSERT INTO package_stats (package_name, {stat_type}_count)
            VALUES (?, 1)
            ON CONFLICT(package_name) DO UPDATE SET
                {stat_type}_count = {stat_type}_count + 1,
                last_accessed = CURRENT_TIMESTAMP
        """
        
        # Queue the update
        self.write_queue.put({
            'type': 'custom',
            'sql': sql,
            'params': (package,)
        })
    
    def get_hot_packages(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most popular packages"""
        return self.query("""
            SELECT package_name, search_count + install_count as total
            FROM package_stats
            ORDER BY total DESC
            LIMIT ?
        """, (limit,))


class CacheDB(SacredTrinityDB):
    """
    Specialized for high-speed caching
    """
    
    def __init__(self):
        """Initialize cache database (memory-first)"""
        # Use in-memory SQLite for maximum speed
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        
        # Still use trinity architecture but optimized for speed
        self.memory_cache = {}
        self.cache_lock = threading.RLock()
        self.write_queue = queue.Queue()
        self.stop_writer = threading.Event()
        
        self._init_schema()
    
    def set_with_ttl(self, key: str, value: Any, ttl_seconds: int):
        """Set value with time-to-live"""
        expiry = time.time() + ttl_seconds
        
        with self.cache_lock:
            if 'ttl_cache' not in self.memory_cache:
                self.memory_cache['ttl_cache'] = {}
            
            self.memory_cache['ttl_cache'][key] = {
                'value': value,
                'expiry': expiry
            }
    
    def get_with_ttl(self, key: str) -> Optional[Any]:
        """Get value if not expired"""
        with self.cache_lock:
            cache = self.memory_cache.get('ttl_cache', {})
            if key in cache:
                entry = cache[key]
                if entry['expiry'] > time.time():
                    return entry['value']
                else:
                    # Expired, remove it
                    del cache[key]
        
        return None


def get_best_db_for_use_case(use_case: str) -> SacredTrinityDB:
    """
    Get the best database for a specific use case
    
    Use cases:
    - 'analytics': Heavy writes, periodic reads, persistence important
    - 'cache': Ultra-fast reads/writes, persistence optional
    - 'general': Balanced performance and persistence
    """
    if use_case == 'analytics':
        return AnalyticsDB()
    elif use_case == 'cache':
        return CacheDB()
    else:
        return SacredTrinityDB()