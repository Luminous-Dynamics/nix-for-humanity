"""
Usage Analytics & Smart Caching System
Tracks user behavior, optimizes cache, and provides insights
"""

import hashlib
import json
import sqlite3
import threading
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class UsageEvent:
    """Represents a single usage event"""

    timestamp: float
    event_type: str  # search, install, info, etc.
    query: str
    result_count: int
    response_time_ms: float
    cache_hit: bool
    source: str  # semantic, cache, nix
    selected_package: Optional[str] = None
    user_satisfied: Optional[bool] = None
    session_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class UsageAnalytics:
    """
    Advanced analytics system that tracks usage patterns
    and provides insights for optimization
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize analytics with persistent storage"""
        # Use standard SQLite for now (Sacred Trinity DB not yet implemented)
        if db_path is None:
            db_path = Path.home() / ".cache" / "luminous-nix" / "analytics.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path

        # Create connection with WAL mode for better concurrency
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        # Enable WAL mode for concurrent reads/writes
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA busy_timeout=100")  # 100ms timeout - fail fast
        self.conn.execute("PRAGMA cache_size=10000")  # Larger cache
        self.lock = threading.Lock()

        # In-memory analytics
        self.session_id = self._generate_session_id()
        self.session_start = time.time()
        self.current_session = {
            "events": [],
            "total_queries": 0,
            "cache_hits": 0,
            "avg_response_ms": 0.0,
            "unique_queries": set(),
            "packages_selected": Counter(),
        }

        # Smart caching metrics
        self.cache_optimization = {
            "hot_packages": Counter(),  # Frequently accessed
            "cold_packages": set(),  # Rarely accessed
            "peak_hours": defaultdict(int),  # Usage by hour
            "query_patterns": defaultdict(list),  # Common query patterns
            "predictive_cache": {},  # Query → likely next queries
        }

        # Initialize database schema
        self._init_database()

        # Load historical data
        self._load_historical_data()

    def _init_database(self):
        """Initialize database schema"""
        with self.lock:
            cursor = self.conn.cursor()

            # Events table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    event_type TEXT,
                    query TEXT,
                    result_count INTEGER,
                    response_time_ms REAL,
                    cache_hit BOOLEAN,
                    source TEXT,
                    selected_package TEXT,
                    user_satisfied BOOLEAN,
                    session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Query patterns table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS query_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT UNIQUE,
                    frequency INTEGER DEFAULT 1,
                    avg_response_ms REAL,
                    success_rate REAL,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Package popularity table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS package_popularity (
                    package_name TEXT PRIMARY KEY,
                    search_count INTEGER DEFAULT 0,
                    install_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    avg_response_ms REAL
                )
            """
            )

            # Session summaries table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS session_summaries (
                    session_id TEXT PRIMARY KEY,
                    start_time REAL,
                    end_time REAL,
                    total_queries INTEGER,
                    cache_hit_rate REAL,
                    avg_response_ms REAL,
                    unique_queries INTEGER,
                    packages_installed INTEGER
                )
            """
            )

            # Create indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON usage_events(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_query ON usage_events(query)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_session ON usage_events(session_id)"
            )

            self.conn.commit()

    def track_event(self, event: UsageEvent):
        """Track a usage event"""
        # Update session metrics
        self.current_session["events"].append(event)
        self.current_session["total_queries"] += 1

        if event.cache_hit:
            self.current_session["cache_hits"] += 1

        self.current_session["unique_queries"].add(event.query)

        if event.selected_package:
            self.current_session["packages_selected"][event.selected_package] += 1
            self.cache_optimization["hot_packages"][event.selected_package] += 1

        # Update average response time
        self._update_avg_response_time(event.response_time_ms)

        # Track peak hours
        hour = datetime.now().hour
        self.cache_optimization["peak_hours"][hour] += 1

        # Store in database
        self._store_event(event)

        # Update query patterns
        self._update_query_patterns(event)

        # Update predictive cache
        self._update_predictive_cache(event)

    def _update_avg_response_time(self, new_time: float):
        """Update moving average response time"""
        alpha = 0.1  # Weight for new value
        if self.current_session["avg_response_ms"] == 0:
            self.current_session["avg_response_ms"] = new_time
        else:
            self.current_session["avg_response_ms"] = (
                alpha * new_time + (1 - alpha) * self.current_session["avg_response_ms"]
            )

    def _store_event(self, event: UsageEvent):
        """Store event in database"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO usage_events (
                        timestamp, event_type, query, result_count,
                        response_time_ms, cache_hit, source,
                        selected_package, user_satisfied, session_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        event.timestamp,
                        event.event_type,
                        event.query,
                        event.result_count,
                        event.response_time_ms,
                        event.cache_hit,
                        event.source,
                        event.selected_package,
                        event.user_satisfied,
                        event.session_id or self.session_id,
                    ),
                )

                # Update package popularity
                if event.selected_package:
                    cursor.execute(
                        """
                        INSERT INTO package_popularity (package_name, search_count, avg_response_ms)
                        VALUES (?, 1, ?)
                        ON CONFLICT(package_name) DO UPDATE SET
                            search_count = search_count + 1,
                            last_accessed = CURRENT_TIMESTAMP,
                            avg_response_ms = (avg_response_ms + ?) / 2
                    """,
                        (
                            event.selected_package,
                            event.response_time_ms,
                            event.response_time_ms,
                        ),
                    )

                self.conn.commit()
            except sqlite3.OperationalError as e:
                if "locked" in str(e):
                    # Skip this event if database is locked
                    print(f"Warning: Database locked, skipping event: {event.query}")
                else:
                    raise

    def _update_query_patterns(self, event: UsageEvent):
        """Identify and update query patterns"""
        # Extract pattern from query (simplified)
        words = event.query.lower().split()
        if len(words) >= 2:
            # Create patterns from word combinations
            for i in range(len(words) - 1):
                pattern = f"{words[i]} {words[i+1]}"

                with self.lock:
                    try:
                        cursor = self.conn.cursor()
                        cursor.execute(
                            """
                            INSERT INTO query_patterns (pattern, frequency, avg_response_ms)
                            VALUES (?, 1, ?)
                            ON CONFLICT(pattern) DO UPDATE SET
                                frequency = frequency + 1,
                                avg_response_ms = (avg_response_ms + ?) / 2,
                                last_seen = CURRENT_TIMESTAMP
                        """,
                            (pattern, event.response_time_ms, event.response_time_ms),
                        )
                        self.conn.commit()
                    except sqlite3.OperationalError:
                        pass  # Skip if database is locked

                # Track in memory
                self.cache_optimization["query_patterns"][pattern].append(event.query)

    def _update_predictive_cache(self, event: UsageEvent):
        """Update predictive cache based on query sequences"""
        # Simple Markov chain approach
        if len(self.current_session["events"]) >= 2:
            prev_event = self.current_session["events"][-2]
            prev_query = prev_event.query.lower()
            curr_query = event.query.lower()

            if prev_query not in self.cache_optimization["predictive_cache"]:
                self.cache_optimization["predictive_cache"][prev_query] = Counter()

            self.cache_optimization["predictive_cache"][prev_query][curr_query] += 1

    def get_smart_cache_recommendations(self) -> dict[str, Any]:
        """Get recommendations for cache optimization"""
        recommendations = {
            "packages_to_cache": [],
            "packages_to_remove": [],
            "optimal_cache_size": 0,
            "peak_usage_hours": [],
            "common_patterns": [],
            "predictive_prefetch": [],
        }

        # Get hot packages (top 20% most accessed) - no DB access
        total_accesses = sum(self.cache_optimization["hot_packages"].values())
        if total_accesses > 0:
            threshold = total_accesses * 0.2
            hot_packages = [
                pkg
                for pkg, count in self.cache_optimization["hot_packages"].most_common()
                if count
                >= threshold / max(1, len(self.cache_optimization["hot_packages"]))
            ]
            recommendations["packages_to_cache"] = hot_packages[:100]

        # Identify cold packages - quick DB access with timeout
        try:
            with self.lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "PRAGMA busy_timeout=100"
                )  # 100ms timeout for this query
                cursor.execute(
                    """
                    SELECT package_name FROM package_popularity
                    WHERE julianday('now') - julianday(last_accessed) > 7
                    ORDER BY search_count ASC
                    LIMIT 50
                """
                )
                cold_packages = [row[0] for row in cursor.fetchall()]
                recommendations["packages_to_remove"] = cold_packages
        except sqlite3.OperationalError:
            # Skip if database is busy
            pass

        # Calculate optimal cache size based on usage - no DB access
        unique_packages_per_session = len(self.current_session["packages_selected"])
        recommendations["optimal_cache_size"] = max(50, unique_packages_per_session * 3)

        # Identify peak hours - no DB access
        if self.cache_optimization["peak_hours"]:
            sorted_hours = sorted(
                self.cache_optimization["peak_hours"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
            recommendations["peak_usage_hours"] = [hour for hour, _ in sorted_hours[:3]]

        # Common query patterns - quick DB access
        try:
            with self.lock:
                cursor = self.conn.cursor()
                cursor.execute("PRAGMA busy_timeout=100")  # 100ms timeout
                cursor.execute(
                    """
                    SELECT pattern, frequency FROM query_patterns
                    ORDER BY frequency DESC
                    LIMIT 10
                """
                )
                recommendations["common_patterns"] = [
                    {"pattern": row[0], "frequency": row[1]}
                    for row in cursor.fetchall()
                ]
        except sqlite3.OperationalError:
            # Use in-memory patterns if DB is busy
            patterns = list(self.cache_optimization["query_patterns"].keys())[:10]
            recommendations["common_patterns"] = [
                {
                    "pattern": p,
                    "frequency": len(self.cache_optimization["query_patterns"][p]),
                }
                for p in patterns
            ]

        # Predictive prefetch suggestions - no DB access
        if self.cache_optimization["predictive_cache"]:
            predictions = []
            for query, next_queries in self.cache_optimization[
                "predictive_cache"
            ].items():
                if next_queries:
                    most_likely = next_queries.most_common(1)[0]
                    predictions.append(
                        {
                            "after": query,
                            "prefetch": most_likely[0],
                            "probability": most_likely[1] / sum(next_queries.values()),
                        }
                    )

            # Sort by probability
            predictions.sort(key=lambda x: x["probability"], reverse=True)
            recommendations["predictive_prefetch"] = predictions[:10]

        return recommendations

    def get_usage_insights(self) -> dict[str, Any]:
        """Get comprehensive usage insights"""
        insights = {"session": {}, "performance": {}, "patterns": {}, "trends": {}}

        # Session insights
        cache_hit_rate = 0
        if self.current_session["total_queries"] > 0:
            cache_hit_rate = (
                self.current_session["cache_hits"]
                / self.current_session["total_queries"]
                * 100
            )

        insights["session"] = {
            "duration_minutes": (time.time() - self.session_start) / 60,
            "total_queries": self.current_session["total_queries"],
            "unique_queries": len(self.current_session["unique_queries"]),
            "cache_hit_rate": cache_hit_rate,
            "avg_response_ms": self.current_session["avg_response_ms"],
            "top_packages": self.current_session["packages_selected"].most_common(5),
        }

        # Performance insights
        with self.lock:
            cursor = self.conn.cursor()

            # Average response time by source
            cursor.execute(
                """
                SELECT source, AVG(response_time_ms) as avg_ms, COUNT(*) as count
                FROM usage_events
                WHERE timestamp > ?
                GROUP BY source
            """,
                (time.time() - 86400,),
            )  # Last 24 hours

            perf_by_source = {
                row[0]: {"avg_ms": row[1], "count": row[2]} for row in cursor.fetchall()
            }

            insights["performance"] = {
                "by_source": perf_by_source,
                "cache_effectiveness": cache_hit_rate,
                "avg_response_ms": self.current_session["avg_response_ms"],
            }

            # Pattern insights
            cursor.execute(
                """
                SELECT pattern, frequency, avg_response_ms
                FROM query_patterns
                ORDER BY frequency DESC
                LIMIT 5
            """
            )

            top_patterns = [
                {"pattern": row[0], "frequency": row[1], "avg_ms": row[2]}
                for row in cursor.fetchall()
            ]

            insights["patterns"] = {
                "top_patterns": top_patterns,
                "unique_patterns": len(self.cache_optimization["query_patterns"]),
            }

            # Trend insights
            cursor.execute(
                """
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as queries,
                    AVG(response_time_ms) as avg_ms
                FROM usage_events
                WHERE timestamp > ?
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            """,
                (time.time() - 604800,),
            )  # Last 7 days

            daily_trends = [
                {"date": row[0], "queries": row[1], "avg_ms": row[2]}
                for row in cursor.fetchall()
            ]

            insights["trends"] = {
                "daily": daily_trends,
                "peak_hours": sorted(
                    self.cache_optimization["peak_hours"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:3],
            }

        return insights

    def export_analytics(self, format: str = "json") -> str:
        """Export analytics data"""
        data = {
            "session": self.current_session,
            "insights": self.get_usage_insights(),
            "recommendations": self.get_smart_cache_recommendations(),
            "timestamp": time.time(),
        }

        # Convert sets and Counters to serializable formats
        data["session"]["unique_queries"] = list(data["session"]["unique_queries"])
        data["session"]["packages_selected"] = dict(
            data["session"]["packages_selected"]
        )

        if format == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            # Could add CSV, etc.
            return json.dumps(data, indent=2, default=str)

    def close_session(self):
        """Close current session and save summary"""
        # Save session summary
        try:
            with self.lock:
                cursor = self.conn.cursor()

                cache_hit_rate = 0
                if self.current_session["total_queries"] > 0:
                    cache_hit_rate = (
                        self.current_session["cache_hits"]
                        / self.current_session["total_queries"]
                    )

                cursor.execute(
                    """
                    INSERT INTO session_summaries (
                        session_id, start_time, end_time, total_queries,
                        cache_hit_rate, avg_response_ms, unique_queries,
                        packages_installed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        self.session_id,
                        self.session_start,
                        time.time(),
                        self.current_session["total_queries"],
                        cache_hit_rate,
                        self.current_session["avg_response_ms"],
                        len(self.current_session["unique_queries"]),
                        len(self.current_session["packages_selected"]),
                    ),
                )

                self.conn.commit()
        except sqlite3.OperationalError as e:
            # Database locked during shutdown is OK - we tried our best
            if "locked" not in str(e):
                print(f"Error closing session: {e}")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        data = f"{time.time()}{id(self)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def _load_historical_data(self):
        """Load historical data for analysis"""
        with self.lock:
            cursor = self.conn.cursor()

            # Load hot packages from last 30 days
            cursor.execute(
                """
                SELECT package_name, search_count
                FROM package_popularity
                WHERE julianday('now') - julianday(last_accessed) < 30
                ORDER BY search_count DESC
                LIMIT 100
            """
            )

            for row in cursor.fetchall():
                self.cache_optimization["hot_packages"][row[0]] = row[1]

            # Load common patterns
            cursor.execute(
                """
                SELECT pattern, frequency
                FROM query_patterns
                WHERE julianday('now') - julianday(last_seen) < 7
                ORDER BY frequency DESC
                LIMIT 50
            """
            )

            for row in cursor.fetchall():
                pattern = row[0]
                self.cache_optimization["query_patterns"][pattern] = []

    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.close_session()
            self.conn.close()
        except:
            pass


class SmartCacheOptimizer:
    """
    Optimizes cache based on usage analytics
    """

    def __init__(self, analytics: UsageAnalytics, cache):
        """Initialize with analytics and cache"""
        self.analytics = analytics
        self.cache = cache
        self.optimization_thread = None
        self.stop_optimization = threading.Event()

        # Start optimization thread
        self._start_optimization()

    def _start_optimization(self):
        """Start background optimization thread"""

        def optimize_worker():
            while not self.stop_optimization.is_set():
                try:
                    # Wait 5 minutes between optimizations
                    if self.stop_optimization.wait(300):
                        break

                    # Get recommendations
                    recommendations = self.analytics.get_smart_cache_recommendations()

                    # Apply optimizations
                    self._apply_cache_optimizations(recommendations)

                except Exception:
                    pass  # Silent fail

        self.optimization_thread = threading.Thread(target=optimize_worker, daemon=True)
        self.optimization_thread.start()

    def _apply_cache_optimizations(self, recommendations: dict):
        """Apply cache optimizations based on recommendations"""
        # Add hot packages to L1 cache
        if hasattr(self.cache, "l1_cache"):
            for package in recommendations["packages_to_cache"][:50]:
                if package not in self.cache.l1_cache:
                    # In production, fetch real data
                    self.cache.l1_cache[package] = {
                        "name": package,
                        "version": "optimized",
                        "description": f"Popular package: {package}",
                    }

        # Remove cold packages from L1
        if hasattr(self.cache, "l1_cache"):
            for package in recommendations["packages_to_remove"]:
                if package in self.cache.l1_cache:
                    del self.cache.l1_cache[package]

        # Prefetch based on predictions
        for prediction in recommendations["predictive_prefetch"][:5]:
            query = prediction["prefetch"]
            if prediction["probability"] > 0.5:
                # Prefetch likely next query
                threading.Thread(
                    target=self.cache.search_hybrid, args=(query,), daemon=True
                ).start()

    def shutdown(self):
        """Stop optimization thread"""
        self.stop_optimization.set()
        if self.optimization_thread:
            self.optimization_thread.join(timeout=1)
