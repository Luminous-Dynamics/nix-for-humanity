#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Metrics Collection and Observability for Nix for Humanity
Provides comprehensive monitoring of system performance and health
"""

import time
import json
import sqlite3
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Represents a single metric measurement"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Represents a health check result"""
    name: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    message: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and manages metrics for the Nix for Humanity backend
    
    Features:
    - Real-time metrics collection
    - Historical data storage
    - Alerting on thresholds
    - Export to various formats
    - Performance analytics
    """
    
    def __init__(self, db_path: Optional[Path] = None, retention_days: int = 7):
        self.db_path = db_path or Path.home() / '.nix-humanity' / 'metrics.db'
        self.retention_days = retention_days
        self.metrics_buffer = deque(maxlen=10000)  # In-memory buffer
        self.aggregated_metrics = defaultdict(lambda: defaultdict(list))
        self.health_checks = {}
        self.alert_handlers = []
        self._lock = threading.Lock()
        self._init_db()
        self._start_background_tasks()
        
    def _init_db(self):
        """Initialize SQLite database for metrics storage"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    tags TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp REAL NOT NULL,
                    details TEXT
                )
            """)
            
            # Create indexes separately
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp ON metrics(name, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_health_name_timestamp ON health_checks(name, timestamp)")
            
    def _start_background_tasks(self):
        """Start background tasks for metrics processing"""
        # Start flush thread
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, 
                     metadata: Optional[Dict[str, Any]] = None):
        """Record a single metric"""
        metric = Metric(
            name=name,
            value=value,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        with self._lock:
            self.metrics_buffer.append(metric)
            
            # Update aggregated metrics
            if 'values' not in self.aggregated_metrics[name]:
                self.aggregated_metrics[name]['values'] = []
                self.aggregated_metrics[name]['timestamps'] = []
                self.aggregated_metrics[name]['count'] = 0
                
            self.aggregated_metrics[name]['values'].append(value)
            self.aggregated_metrics[name]['timestamps'].append(metric.timestamp)
            self.aggregated_metrics[name]['count'] += 1
            
        # Check alerts
        self._check_alerts(metric)
        
    def record_operation(self, operation_type: str, duration: float, success: bool,
                        error: Optional[str] = None):
        """Record an operation metric with standard tags"""
        self.record_metric(
            f"operation.{operation_type}.duration",
            duration,
            tags={
                'success': str(success).lower(),
                'operation': operation_type
            },
            metadata={'error': error} if error else {}
        )
        
        # Record success/failure count
        self.record_metric(
            f"operation.{operation_type}.{'success' if success else 'failure'}",
            1.0,
            tags={'operation': operation_type}
        )
        
    def record_cache_hit(self, cache_name: str, hit: bool):
        """Record cache hit/miss"""
        self.record_metric(
            f"cache.{cache_name}.{'hit' if hit else 'miss'}",
            1.0,
            tags={'cache': cache_name}
        )
        
    def record_health_check(self, name: str, healthy: bool, message: str = "",
                           details: Optional[Dict[str, Any]] = None):
        """Record a health check result"""
        status = 'healthy' if healthy else 'unhealthy'
        
        check = HealthCheck(
            name=name,
            status=status,
            message=message,
            details=details or {}
        )
        
        with self._lock:
            self.health_checks[name] = check
            
        # Persist to database
        self._persist_health_check(check)
        
        # Alert if unhealthy
        if not healthy:
            self._trigger_alert(f"Health check '{name}' failed: {message}")
            
    def get_metrics_summary(self, time_window: timedelta = timedelta(minutes=5)) -> Dict[str, Any]:
        """Get summary of recent metrics"""
        cutoff_time = time.time() - time_window.total_seconds()
        summary = {}
        
        with self._lock:
            for name, data in self.aggregated_metrics.items():
                recent_values = [v for v, t in zip(data['values'], data['timestamps']) 
                               if t >= cutoff_time]
                
                if recent_values:
                    summary[name] = {
                        'count': len(recent_values),
                        'mean': sum(recent_values) / len(recent_values),
                        'min': min(recent_values),
                        'max': max(recent_values),
                        'latest': recent_values[-1]
                    }
                    
        return summary
        
    def get_operation_stats(self) -> Dict[str, Any]:
        """Get operation statistics"""
        stats = {}
        
        # Query from database for comprehensive stats
        with sqlite3.connect(str(self.db_path)) as conn:
            # Success rates by operation
            cursor = conn.execute("""
                SELECT 
                    tags,
                    COUNT(*) as count,
                    AVG(value) as avg_duration
                FROM metrics
                WHERE name LIKE 'operation.%.duration'
                AND timestamp > ?
                GROUP BY tags
            """, (time.time() - 3600,))  # Last hour
            
            for row in cursor:
                tags = json.loads(row[0]) if row[0] else {}
                operation = tags.get('operation', 'unknown')
                success = tags.get('success', 'true') == 'true'
                
                if operation not in stats:
                    stats[operation] = {
                        'total': 0,
                        'success': 0,
                        'failure': 0,
                        'avg_duration': 0
                    }
                    
                stats[operation]['total'] += row[1]
                if success:
                    stats[operation]['success'] += row[1]
                else:
                    stats[operation]['failure'] += row[1]
                    
                stats[operation]['avg_duration'] = row[2]
                
        # Calculate success rates
        for op_stats in stats.values():
            if op_stats['total'] > 0:
                op_stats['success_rate'] = op_stats['success'] / op_stats['total']
                
        return stats
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        stats = {}
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("""
                SELECT 
                    tags,
                    COUNT(*) as count
                FROM metrics
                WHERE name LIKE 'cache.%'
                AND timestamp > ?
                GROUP BY tags
            """, (time.time() - 3600,))  # Last hour
            
            for row in cursor:
                tags = json.loads(row[0]) if row[0] else {}
                cache_name = tags.get('cache', 'unknown')
                
                if cache_name not in stats:
                    stats[cache_name] = {'hits': 0, 'misses': 0}
                    
                if 'hit' in row[0]:
                    stats[cache_name]['hits'] += row[1]
                else:
                    stats[cache_name]['misses'] += row[1]
                    
        # Calculate hit rates
        for cache_stats in stats.values():
            total = cache_stats['hits'] + cache_stats['misses']
            if total > 0:
                cache_stats['hit_rate'] = cache_stats['hits'] / total
                
        return stats
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        with self._lock:
            checks = list(self.health_checks.values())
            
        healthy_count = sum(1 for c in checks if c.status == 'healthy')
        total_count = len(checks)
        
        if total_count == 0:
            overall_status = 'unknown'
        elif healthy_count == total_count:
            overall_status = 'healthy'
        elif healthy_count > total_count / 2:
            overall_status = 'degraded'
        else:
            overall_status = 'unhealthy'
            
        return {
            'status': overall_status,
            'healthy': healthy_count,
            'total': total_count,
            'checks': {c.name: c.status for c in checks}
        }
        
    def add_alert_handler(self, handler: Callable[[str], None]):
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
        
    def export_metrics(self, format: str = 'json', 
                      time_range: Optional[timedelta] = None) -> str:
        """Export metrics in various formats"""
        if time_range:
            start_time = time.time() - time_range.total_seconds()
        else:
            start_time = 0
            
        metrics = []
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("""
                SELECT name, value, timestamp, tags, metadata
                FROM metrics
                WHERE timestamp > ?
                ORDER BY timestamp
            """, (start_time,))
            
            for row in cursor:
                metrics.append({
                    'name': row[0],
                    'value': row[1],
                    'timestamp': row[2],
                    'tags': json.loads(row[3]) if row[3] else {},
                    'metadata': json.loads(row[4]) if row[4] else {}
                })
                
        if format == 'json':
            return json.dumps(metrics, indent=2)
        elif format == 'prometheus':
            return self._format_prometheus(metrics)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _format_prometheus(self, metrics: List[Dict[str, Any]]) -> str:
        """Format metrics in Prometheus exposition format"""
        lines = []
        
        for metric in metrics:
            name = metric['name'].replace('.', '_')
            tags = ','.join(f'{k}="{v}"' for k, v in metric['tags'].items())
            
            if tags:
                lines.append(f"{name}{{{tags}}} {metric['value']} {int(metric['timestamp'] * 1000)}")
            else:
                lines.append(f"{name} {metric['value']} {int(metric['timestamp'] * 1000)}")
                
        return '\n'.join(lines)
        
    def _flush_loop(self):
        """Background loop to flush metrics to database"""
        while True:
            time.sleep(10)  # Flush every 10 seconds
            self._flush_metrics()
            
    def _flush_metrics(self):
        """Flush buffered metrics to database"""
        if not self.metrics_buffer:
            return
            
        with self._lock:
            metrics_to_flush = list(self.metrics_buffer)
            self.metrics_buffer.clear()
            
        with sqlite3.connect(str(self.db_path)) as conn:
            for metric in metrics_to_flush:
                conn.execute("""
                    INSERT INTO metrics (name, value, timestamp, tags, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    metric.name,
                    metric.value,
                    metric.timestamp,
                    json.dumps(metric.tags),
                    json.dumps(metric.metadata)
                ))
                
    def _cleanup_loop(self):
        """Background loop to clean old metrics"""
        while True:
            time.sleep(3600)  # Run hourly
            self._cleanup_old_data()
            
    def _cleanup_old_data(self):
        """Remove metrics older than retention period"""
        cutoff_time = time.time() - (self.retention_days * 86400)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_time,))
            conn.execute("DELETE FROM health_checks WHERE timestamp < ?", (cutoff_time,))
            
    def _persist_health_check(self, check: HealthCheck):
        """Persist health check to database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT INTO health_checks (name, status, message, timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                check.name,
                check.status,
                check.message,
                check.timestamp,
                json.dumps(check.details)
            ))
            
    def _check_alerts(self, metric: Metric):
        """Check if metric triggers any alerts"""
        # Example alert conditions
        if metric.name == 'operation.update_system.duration' and metric.value > 60:
            self._trigger_alert(f"System update took {metric.value:.1f}s (threshold: 60s)")
            
        elif metric.name.endswith('.failure') and metric.value > 0:
            self._trigger_alert(f"Operation failure: {metric.name}")
            
    def _trigger_alert(self, message: str):
        """Trigger an alert"""
        logger.warning(f"ALERT: {message}")
        
        for handler in self.alert_handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")


# Singleton instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Convenience functions
def record_metric(name: str, value: float, **kwargs):
    """Record a metric using the global collector"""
    get_metrics_collector().record_metric(name, value, **kwargs)
    

def record_operation(operation_type: str, duration: float, success: bool, **kwargs):
    """Record an operation using the global collector"""
    get_metrics_collector().record_operation(operation_type, duration, success, **kwargs)
    

def record_health_check(name: str, healthy: bool, **kwargs):
    """Record a health check using the global collector"""
    get_metrics_collector().record_health_check(name, healthy, **kwargs)


# Context manager for timing operations
class timed_operation:
    """Context manager for timing operations"""
    
    def __init__(self, operation_type: str):
        self.operation_type = operation_type
        self.start_time = None
        self.success = True
        self.error = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            self.success = False
            self.error = str(exc_val)
            
        record_operation(
            self.operation_type,
            duration,
            self.success,
            error=self.error
        )
        
        return False  # Don't suppress exceptions


# Demo usage
if __name__ == "__main__":
    import random
    
    collector = get_metrics_collector()
    
    # Add alert handler
    collector.add_alert_handler(lambda msg: print(f"🚨 ALERT: {msg}"))
    
    # Simulate some metrics
    for i in range(10):
        # Record operations
        with timed_operation("test_operation") as op:
            time.sleep(random.uniform(0.1, 0.5))
            if random.random() < 0.1:  # 10% failure rate
                op.success = False
                raise Exception("Random failure")
                
        # Record cache hits/misses
        record_metric("cache.test.hit" if random.random() < 0.7 else "cache.test.miss", 1.0)
        
        # Record custom metrics
        record_metric("custom.metric", random.gauss(50, 10))
        
    # Record health checks
    record_health_check("database", True, "Database connection healthy")
    record_health_check("api", random.random() < 0.9, "API responding")
    
    # Get summaries
    print("\n📊 Metrics Summary:")
    print(json.dumps(collector.get_metrics_summary(), indent=2))
    
    print("\n📈 Operation Stats:")
    print(json.dumps(collector.get_operation_stats(), indent=2))
    
    print("\n💾 Cache Stats:")
    print(json.dumps(collector.get_cache_stats(), indent=2))
    
    print("\n🏥 Health Status:")
    print(json.dumps(collector.get_health_status(), indent=2))
    
    # Export metrics
    print("\n📤 Prometheus Export Sample:")
    print(collector.export_metrics('prometheus', timedelta(minutes=1))[:500] + "...")