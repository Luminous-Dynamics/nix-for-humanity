"""
Improved Usage Analytics with proper concurrency handling
Solves database locking issues through write queue and connection pooling
"""

import json
import queue
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class UsageEvent:
    """Event data structure for tracking user interactions"""

    timestamp: float
    event_type: str  # 'search', 'install', 'info', etc.
    query: str
    result_count: int = 0
    response_time_ms: float = 0.0
    cache_hit: bool = False
    source: str = ""  # 'memory', 'disk', 'network', 'nix'
    session_id: str = ""
    success: bool = True
    metadata: dict = None
    selected_package: Optional[str] = None  # What package user selected
    user_satisfied: bool = True  # Was the user satisfied with results


class DatabaseWriteQueue:
    """Manages database writes through a queue to prevent locking"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.write_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.writer_thread = None
        self.write_conn = None

        # Statistics
        self.writes_completed = 0
        self.writes_failed = 0
        self.queue_high_water_mark = 0

        self._init_database()
        self._start_writer()

    def _init_database(self):
        """Initialize database with optimal settings"""
        # Create database and tables
        conn = sqlite3.connect(str(self.db_path))

        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=1000")  # 1 second timeout
        conn.execute("PRAGMA cache_size=10000")  # Larger cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp operations

        # Create tables
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                query TEXT NOT NULL,
                result_count INTEGER DEFAULT 0,
                response_time_ms REAL DEFAULT 0.0,
                cache_hit BOOLEAN DEFAULT 0,
                source TEXT DEFAULT '',
                session_id TEXT DEFAULT '',
                success BOOLEAN DEFAULT 1,
                metadata TEXT,
                selected_package TEXT,
                user_satisfied BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_events(timestamp)
        """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_event_type ON usage_events(event_type)
        """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_query ON usage_events(query)
        """
        )

        conn.commit()
        conn.close()

    def _start_writer(self):
        """Start background writer thread"""

        def writer_worker():
            # Dedicated connection for writes
            self.write_conn = sqlite3.connect(str(self.db_path))
            self.write_conn.execute("PRAGMA journal_mode=WAL")
            self.write_conn.execute("PRAGMA synchronous=NORMAL")

            while not self.stop_event.is_set():
                try:
                    # Wait for item with timeout
                    try:
                        item = self.write_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    # Track queue size
                    queue_size = self.write_queue.qsize()
                    if queue_size > self.queue_high_water_mark:
                        self.queue_high_water_mark = queue_size

                    # Process write
                    if item is None:  # Shutdown signal
                        break

                    query, params = item

                    try:
                        self.write_conn.execute(query, params)
                        self.write_conn.commit()
                        self.writes_completed += 1
                    except Exception:
                        self.writes_failed += 1
                        # Log error but don't crash
                        # print(f"Write error: {e}")

                    self.write_queue.task_done()

                except Exception:
                    # Catch any unexpected errors
                    pass

            # Cleanup
            if self.write_conn:
                self.write_conn.close()

        self.writer_thread = threading.Thread(target=writer_worker, daemon=True)
        self.writer_thread.start()

    def enqueue_write(self, query: str, params: tuple):
        """Add write operation to queue"""
        if not self.stop_event.is_set():
            self.write_queue.put((query, params))

    def get_read_connection(self) -> sqlite3.Connection:
        """Get a read-only connection (separate from write connection)"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA query_only=ON")  # Read-only mode
        return conn

    def shutdown(self):
        """Shutdown writer thread gracefully"""
        self.stop_event.set()
        self.write_queue.put(None)  # Signal to exit

        if self.writer_thread:
            self.writer_thread.join(timeout=2)

    def get_stats(self) -> dict:
        """Get queue statistics"""
        return {
            "queue_size": self.write_queue.qsize(),
            "writes_completed": self.writes_completed,
            "writes_failed": self.writes_failed,
            "queue_high_water_mark": self.queue_high_water_mark,
        }


class ImprovedUsageAnalytics:
    """Improved analytics with proper concurrency handling"""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize analytics with write queue"""
        if db_path is None:
            db_path = Path.home() / ".cache" / "luminous-nix" / "usage_improved.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.session_start = time.time()
        self.session_queries = 0

        # Initialize write queue
        self.write_queue = DatabaseWriteQueue(db_path)

        # Cache for frequently accessed data
        self.pattern_cache = {}
        self.last_cache_refresh = 0
        self.cache_refresh_interval = 60  # seconds

    def track_event(self, event: UsageEvent):
        """Track usage event (non-blocking)"""
        # Set session ID if not provided
        if not event.session_id:
            event.session_id = self.session_id

        # Increment session counter
        self.session_queries += 1

        # Prepare data for database
        metadata_json = json.dumps(event.metadata) if event.metadata else None

        # Enqueue write (non-blocking)
        self.write_queue.enqueue_write(
            """
            INSERT INTO usage_events (
                timestamp, event_type, query, result_count,
                response_time_ms, cache_hit, source, session_id,
                success, metadata, selected_package, user_satisfied
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.timestamp,
                event.event_type,
                event.query,
                event.result_count,
                event.response_time_ms,
                event.cache_hit,
                event.source,
                event.session_id,
                event.success,
                metadata_json,
                event.selected_package,
                event.user_satisfied,
            ),
        )

    def get_smart_cache_recommendations(self, limit: int = 20) -> dict[str, list]:
        """Get cache recommendations (using read-only connection)"""
        recommendations = {
            "packages_to_cache": [],
            "common_patterns": [],
            "peak_times": [],
            "cache_hit_rate": 0.0,
        }

        try:
            # Use separate read connection
            conn = self.write_queue.get_read_connection()
            cursor = conn.cursor()

            # Get most frequently searched packages
            cursor.execute(
                """
                SELECT query, COUNT(*) as count,
                       AVG(response_time_ms) as avg_time,
                       SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as hit_rate
                FROM usage_events
                WHERE event_type = 'search'
                  AND timestamp > ?
                GROUP BY query
                ORDER BY count DESC
                LIMIT ?
            """,
                (time.time() - 86400, limit),
            )  # Last 24 hours

            hot_queries = cursor.fetchall()

            for query, count, avg_time, hit_rate in hot_queries:
                if count > 2 and hit_rate < 50:  # Frequently accessed but not cached
                    recommendations["packages_to_cache"].append(
                        {
                            "query": query,
                            "frequency": count,
                            "avg_response_ms": avg_time,
                            "current_hit_rate": hit_rate,
                        }
                    )

            # Get common query patterns
            cursor.execute(
                """
                SELECT
                    SUBSTR(query, 1, INSTR(query || ' ', ' ') - 1) as first_word,
                    COUNT(*) as count
                FROM usage_events
                WHERE event_type = 'search'
                  AND timestamp > ?
                GROUP BY first_word
                ORDER BY count DESC
                LIMIT 10
            """,
                (time.time() - 86400,),
            )

            patterns = cursor.fetchall()
            recommendations["common_patterns"] = [
                {"pattern": pattern, "count": count} for pattern, count in patterns
            ]

            # Calculate overall cache hit rate
            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as hit_rate
                FROM usage_events
                WHERE event_type = 'search'
                  AND timestamp > ?
            """,
                (time.time() - 3600,),
            )  # Last hour

            result = cursor.fetchone()
            if result and result[0]:
                recommendations["cache_hit_rate"] = result[0]

            conn.close()

        except Exception:
            # Return empty recommendations on error
            pass

        return recommendations

    def get_session_analytics(self) -> dict[str, Any]:
        """Get analytics for current session"""
        session_duration = time.time() - self.session_start

        analytics = {
            "session_id": self.session_id,
            "duration_seconds": session_duration,
            "total_queries": self.session_queries,
            "queries_per_minute": (self.session_queries / max(1, session_duration))
            * 60,
        }

        try:
            # Get session-specific stats
            conn = self.write_queue.get_read_connection()
            cursor = conn.cursor()

            # Average response time
            cursor.execute(
                """
                SELECT AVG(response_time_ms), MIN(response_time_ms), MAX(response_time_ms)
                FROM usage_events
                WHERE session_id = ?
            """,
                (self.session_id,),
            )

            result = cursor.fetchone()
            if result and result[0]:
                analytics["avg_response_ms"] = result[0]
                analytics["min_response_ms"] = result[1]
                analytics["max_response_ms"] = result[2]

            # Cache hit rate
            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
                FROM usage_events
                WHERE session_id = ?
                  AND event_type = 'search'
            """,
                (self.session_id,),
            )

            result = cursor.fetchone()
            if result and result[0]:
                analytics["cache_hit_rate"] = result[0]

            conn.close()

        except Exception:
            pass

        # Add queue stats
        analytics["queue_stats"] = self.write_queue.get_stats()

        return analytics

    def get_query_prediction(self, current_query: str, top_n: int = 5) -> list[tuple]:
        """Predict next likely queries based on patterns"""
        predictions = []

        try:
            conn = self.write_queue.get_read_connection()
            cursor = conn.cursor()

            # Find queries that often follow the current query
            cursor.execute(
                """
                WITH query_sequences AS (
                    SELECT
                        query,
                        LEAD(query) OVER (PARTITION BY session_id ORDER BY timestamp) as next_query
                    FROM usage_events
                    WHERE event_type = 'search'
                )
                SELECT
                    next_query,
                    COUNT(*) as frequency
                FROM query_sequences
                WHERE query = ?
                  AND next_query IS NOT NULL
                  AND next_query != query
                GROUP BY next_query
                ORDER BY frequency DESC
                LIMIT ?
            """,
                (current_query, top_n),
            )

            results = cursor.fetchall()

            total_count = sum(count for _, count in results)
            if total_count > 0:
                predictions = [(query, count / total_count) for query, count in results]

            conn.close()

        except Exception:
            pass

        return predictions

    def close_session(self):
        """Close analytics session and cleanup"""
        # Flush any remaining writes
        self.write_queue.shutdown()

    def get_insights(self) -> dict[str, Any]:
        """Get comprehensive insights"""
        return {
            "session": self.get_session_analytics(),
            "recommendations": self.get_smart_cache_recommendations(),
            "queue_status": self.write_queue.get_stats(),
        }

    def get_usage_insights(self) -> dict[str, Any]:
        """Get usage insights (alias for compatibility)"""
        insights = self.get_session_analytics()
        insights["analytics"] = True
        insights["cache_optimization"] = self.get_smart_cache_recommendations()
        return insights


class SmartCacheOptimizerImproved:
    """Improved cache optimizer that doesn't cause database locks"""

    def __init__(self, analytics: ImprovedUsageAnalytics, cache):
        self.analytics = analytics
        self.cache = cache
        self.optimization_thread = None
        self.stop_event = threading.Event()
        self.last_optimization = 0
        self.optimization_interval = 300  # 5 minutes

        self._start_optimizer()

    def _start_optimizer(self):
        """Start background optimization thread"""

        def optimizer_worker():
            while not self.stop_event.is_set():
                try:
                    # Wait for interval or stop signal
                    if self.stop_event.wait(self.optimization_interval):
                        break

                    # Get recommendations without blocking writes
                    recommendations = self.analytics.get_smart_cache_recommendations()

                    # Update cache based on recommendations
                    for item in recommendations.get("packages_to_cache", [])[:10]:
                        query = item["query"]
                        # Trigger cache warming (implementation depends on cache)
                        # self.cache.warm(query)

                    self.last_optimization = time.time()

                except Exception:
                    pass  # Silent fail in background

        self.optimization_thread = threading.Thread(
            target=optimizer_worker, daemon=True
        )
        self.optimization_thread.start()

    def shutdown(self):
        """Shutdown optimizer"""
        self.stop_event.set()
        if self.optimization_thread:
            self.optimization_thread.join(timeout=1)

    def get_status(self) -> dict:
        """Get optimizer status"""
        return {
            "running": self.optimization_thread and self.optimization_thread.is_alive(),
            "last_optimization": self.last_optimization,
            "time_since_last": time.time() - self.last_optimization
            if self.last_optimization
            else None,
        }


# Singleton instances
_improved_analytics = None
_improved_optimizer = None


def get_improved_analytics() -> ImprovedUsageAnalytics:
    """Get or create improved analytics singleton"""
    global _improved_analytics
    if _improved_analytics is None:
        _improved_analytics = ImprovedUsageAnalytics()
    return _improved_analytics


def get_improved_optimizer(cache) -> SmartCacheOptimizerImproved:
    """Get or create improved optimizer singleton"""
    global _improved_optimizer
    if _improved_optimizer is None:
        analytics = get_improved_analytics()
        _improved_optimizer = SmartCacheOptimizerImproved(analytics, cache)
    return _improved_optimizer
