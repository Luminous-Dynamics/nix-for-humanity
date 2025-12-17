"""
Comprehensive Observability System
Full observability with metrics, tracing, and dashboards

Features:
1. Real-time metrics collection
2. Distributed tracing
3. Structured logging
4. Live dashboards
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque
from contextlib import contextmanager
import json
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


@dataclass
class Span:
    """A tracing span representing an operation"""
    span_id: str
    operation: str
    parent_span_id: Optional[str]
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict] = field(default_factory=list)
    status: str = 'started'  # started, ok, error
    error: Optional[Exception] = None

    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


@dataclass
class Metric:
    """A single metric measurement"""
    name: str
    value: float
    metric_type: str  # counter, gauge, histogram
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class LogEntry:
    """Structured log entry"""
    level: str
    message: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    span_id: Optional[str] = None
    error: Optional[str] = None


class MetricsCollector:
    """
    Collects and stores metrics

    Supports:
    - Counters (increment only)
    - Gauges (set to value)
    - Histograms (track distributions)
    """

    def __init__(self, retention_size: int = 10000):
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=retention_size)
        )

        # Store all metrics
        self.metrics_history: deque = deque(maxlen=retention_size)

    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict] = None) -> None:
        """Increment a counter"""
        key = self._make_key(name, labels)
        self.counters[key] += value

        self._record_metric(Metric(
            name=name,
            value=self.counters[key],
            metric_type='counter',
            labels=labels or {}
        ))

    def gauge(self, name: str, value: float, labels: Optional[Dict] = None) -> None:
        """Set a gauge value"""
        key = self._make_key(name, labels)
        self.gauges[key] = value

        self._record_metric(Metric(
            name=name,
            value=value,
            metric_type='gauge',
            labels=labels or {}
        ))

    def histogram(self, name: str, value: float, labels: Optional[Dict] = None) -> None:
        """Record histogram value"""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)

        self._record_metric(Metric(
            name=name,
            value=value,
            metric_type='histogram',
            labels=labels or {}
        ))

    def get_counter(self, name: str, labels: Optional[Dict] = None) -> float:
        """Get counter value"""
        key = self._make_key(name, labels)
        return self.counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: Optional[Dict] = None) -> Optional[float]:
        """Get gauge value"""
        key = self._make_key(name, labels)
        return self.gauges.get(key)

    def get_histogram_stats(
        self,
        name: str,
        labels: Optional[Dict] = None
    ) -> Optional[Dict[str, float]]:
        """Get histogram statistics (p50, p95, p99, avg, min, max)"""
        key = self._make_key(name, labels)
        values = list(self.histograms.get(key, []))

        if not values:
            return None

        sorted_values = sorted(values)

        return {
            'count': len(values),
            'avg': statistics.mean(values),
            'min': min(values),
            'max': max(values),
            'p50': self._percentile(sorted_values, 0.50),
            'p95': self._percentile(sorted_values, 0.95),
            'p99': self._percentile(sorted_values, 0.99),
        }

    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile from sorted values"""
        if not sorted_values:
            return 0.0

        index = int(len(sorted_values) * percentile)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]

    def _make_key(self, name: str, labels: Optional[Dict] = None) -> str:
        """Create key from name and labels"""
        if not labels:
            return name

        label_str = ','.join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _record_metric(self, metric: Metric) -> None:
        """Record metric to history"""
        self.metrics_history.append(metric)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {
                name: self.get_histogram_stats(name)
                for name in set(m.name for m in self.metrics_history if m.metric_type == 'histogram')
            }
        }


class DistributedTracer:
    """
    Distributed tracing system

    Tracks operation spans and their relationships
    """

    def __init__(self, max_spans: int = 10000):
        self.spans: Dict[str, Span] = {}
        self.active_spans: List[str] = []
        self.span_history: deque = deque(maxlen=max_spans)

        self._span_counter = 0

    @contextmanager
    def span(self, operation: str, parent_span_id: Optional[str] = None):
        """Create and manage a tracing span"""

        # Generate span ID
        self._span_counter += 1
        span_id = f"span_{self._span_counter}_{int(time.time() * 1000)}"

        # Create span
        span = Span(
            span_id=span_id,
            operation=operation,
            parent_span_id=parent_span_id or (self.active_spans[-1] if self.active_spans else None),
            start_time=time.time(),
        )

        self.spans[span_id] = span
        self.active_spans.append(span_id)

        try:
            yield span

            # Mark as successful
            span.end_time = time.time()
            span.status = 'ok'

        except Exception as e:
            # Record error
            span.end_time = time.time()
            span.status = 'error'
            span.error = e
            raise

        finally:
            # Remove from active
            if self.active_spans and self.active_spans[-1] == span_id:
                self.active_spans.pop()

            # Add to history
            self.span_history.append(span)

    def set_attribute(self, span_id: str, key: str, value: Any) -> None:
        """Set span attribute"""
        if span_id in self.spans:
            self.spans[span_id].attributes[key] = value

    def add_event(self, span_id: str, event: str, attributes: Optional[Dict] = None) -> None:
        """Add event to span"""
        if span_id in self.spans:
            self.spans[span_id].events.append({
                'event': event,
                'timestamp': time.time(),
                'attributes': attributes or {}
            })

    def record_exception(self, span_id: str, exception: Exception) -> None:
        """Record exception in span"""
        if span_id in self.spans:
            span = self.spans[span_id]
            span.status = 'error'
            span.error = exception

    def get_trace(self, span_id: str) -> List[Span]:
        """Get full trace (span and all parents)"""
        trace = []
        current_span_id = span_id

        while current_span_id:
            if current_span_id in self.spans:
                span = self.spans[current_span_id]
                trace.append(span)
                current_span_id = span.parent_span_id
            else:
                break

        return list(reversed(trace))  # Root first

    def get_trace_tree(self, root_span_id: str) -> Dict:
        """Get trace as tree structure"""

        def build_tree(span_id: str) -> Dict:
            if span_id not in self.spans:
                return {}

            span = self.spans[span_id]

            # Find children
            children = [
                build_tree(s.span_id)
                for s in self.spans.values()
                if s.parent_span_id == span_id
            ]

            return {
                'span_id': span.span_id,
                'operation': span.operation,
                'duration_ms': span.duration_ms,
                'status': span.status,
                'attributes': span.attributes,
                'children': children
            }

        return build_tree(root_span_id)


class StructuredLogger:
    """
    Structured logging with context

    Provides searchable, contextual logs
    """

    def __init__(self, max_entries: int = 10000):
        self.log_entries: deque = deque(maxlen=max_entries)
        self.current_context: Dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """Set logging context"""
        self.current_context.update(kwargs)

    def clear_context(self) -> None:
        """Clear logging context"""
        self.current_context.clear()

    def log(
        self,
        level: str,
        message: str,
        span_id: Optional[str] = None,
        **context
    ) -> None:
        """Log with structure"""

        # Merge contexts
        full_context = {**self.current_context, **context}

        entry = LogEntry(
            level=level,
            message=message,
            timestamp=datetime.now(),
            context=full_context,
            span_id=span_id
        )

        self.log_entries.append(entry)

        # Also log to standard logger
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"{message} | Context: {json.dumps(full_context)}")

    def info(self, message: str, **context) -> None:
        """Log info level"""
        self.log(level='INFO', message=message, **context)

    def warning(self, message: str, **context) -> None:
        """Log warning level"""
        self.log(level='WARNING', message=message, **context)

    def error(self, message: str, error: Optional[Exception] = None, **context) -> None:
        """Log error level"""
        entry_context = {**context}
        if error:
            entry_context['error'] = str(error)
            entry_context['error_type'] = type(error).__name__

        self.log(level='ERROR', message=message, **entry_context)

    def search(
        self,
        level: Optional[str] = None,
        message_contains: Optional[str] = None,
        context_key: Optional[str] = None,
        limit: int = 100
    ) -> List[LogEntry]:
        """Search log entries"""

        results = []

        for entry in reversed(self.log_entries):
            # Level filter
            if level and entry.level != level:
                continue

            # Message filter
            if message_contains and message_contains.lower() not in entry.message.lower():
                continue

            # Context filter
            if context_key and context_key not in entry.context:
                continue

            results.append(entry)

            if len(results) >= limit:
                break

        return results


class RealtimeDashboard:
    """
    Real-time observability dashboard

    Provides live system health view
    """

    def __init__(self, metrics: MetricsCollector, tracer: DistributedTracer, logger: StructuredLogger):
        self.metrics = metrics
        self.tracer = tracer
        self.logger = logger

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""

        # Query metrics
        query_stats = self.metrics.get_histogram_stats('query_duration')
        queries_total = self.metrics.get_counter('queries_total')
        queries_success = self.metrics.get_counter('queries_success')
        queries_error = self.metrics.get_counter('queries_error')

        # Calculate success rate
        success_rate = 0.0
        if queries_total > 0:
            success_rate = queries_success / queries_total

        # Recent errors
        recent_errors = self.logger.search(level='ERROR', limit=10)

        # Active operations
        active_spans = len(self.tracer.active_spans)

        return {
            'status': 'healthy' if success_rate > 0.95 else 'degraded',
            'queries': {
                'total': int(queries_total),
                'success': int(queries_success),
                'error': int(queries_error),
                'success_rate': success_rate,
            },
            'performance': query_stats or {},
            'active_operations': active_spans,
            'recent_errors': len(recent_errors),
            'timestamp': datetime.now().isoformat()
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""

        metrics = self.metrics.get_all_metrics()

        return {
            'metrics': metrics,
            'spans': {
                'total': len(self.tracer.span_history),
                'active': len(self.tracer.active_spans)
            },
            'logs': {
                'total': len(self.logger.log_entries),
                'errors': len(self.logger.search(level='ERROR', limit=1000))
            }
        }

    def render_dashboard(self) -> str:
        """Render text dashboard"""

        health = self.get_system_health()
        perf = self.get_performance_report()

        dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║          📊 Sophia Observability Dashboard                   ║
╚══════════════════════════════════════════════════════════════╝

System Status: {health['status'].upper()}
Timestamp: {health['timestamp']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Queries
   Total: {health['queries']['total']:,}
   Success: {health['queries']['success']:,} ({health['queries']['success_rate']:.1%})
   Errors: {health['queries']['error']:,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ Performance (Query Duration)
   Average: {health['performance'].get('avg', 0):.0f}ms
   P50: {health['performance'].get('p50', 0):.0f}ms
   P95: {health['performance'].get('p95', 0):.0f}ms
   P99: {health['performance'].get('p99', 0):.0f}ms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏃 Active Operations: {health['active_operations']}
🚨 Recent Errors: {health['recent_errors']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Observability Stats
   Traces: {perf['spans']['total']:,} (Active: {perf['spans']['active']})
   Logs: {perf['logs']['total']:,} (Errors: {perf['logs']['errors']})
        """

        return dashboard.strip()


class ObservabilitySystem:
    """
    Complete observability system

    Integrates metrics, tracing, logging, and dashboards
    """

    def __init__(self):
        self.metrics = MetricsCollector()
        self.tracer = DistributedTracer()
        self.logger = StructuredLogger()
        self.dashboard = RealtimeDashboard(self.metrics, self.tracer, self.logger)

    def traced(self, operation: str):
        """Decorator for automatic tracing"""
        def decorator(func: Callable):
            async def async_wrapper(*args, **kwargs):
                with self.tracer.span(operation) as span:
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        self.tracer.record_exception(span.span_id, e)
                        raise

            def sync_wrapper(*args, **kwargs):
                with self.tracer.span(operation) as span:
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        self.tracer.record_exception(span.span_id, e)
                        raise

            # Return appropriate wrapper
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    @contextmanager
    def operation(self, name: str):
        """Context manager for instrumented operations"""

        self.metrics.increment('operations_total')
        start_time = time.time()

        with self.tracer.span(name) as span:
            try:
                yield span

                # Success
                duration = time.time() - start_time
                self.metrics.histogram('operation_duration', duration * 1000)
                self.metrics.increment('operations_success')

                self.logger.info(
                    f"Operation '{name}' completed",
                    duration_ms=duration * 1000,
                    span_id=span.span_id
                )

            except Exception as e:
                # Error
                duration = time.time() - start_time
                self.metrics.increment('operations_error')
                self.metrics.increment(f'error_{type(e).__name__}')

                self.logger.error(
                    f"Operation '{name}' failed",
                    error=e,
                    duration_ms=duration * 1000,
                    span_id=span.span_id
                )

                raise

    def show_dashboard(self) -> None:
        """Print dashboard to console"""
        print(self.dashboard.render_dashboard())


# Example usage
async def example_observability():
    """Demonstrate observability system"""

    import asyncio

    obs = ObservabilitySystem()

    # Simulate some operations
    for i in range(10):
        with obs.operation(f'process_query_{i}') as span:
            obs.tracer.set_attribute(span.span_id, 'query', f'test query {i}')

            # Simulate work
            await asyncio.sleep(0.01 * (i + 1))

            if i == 7:
                # Simulate error
                obs.logger.error(f"Error in query {i}", error=ValueError("Test error"))

    # Show dashboard
    print("\n")
    obs.show_dashboard()

    # Get specific metrics
    print("\n📊 Detailed Metrics:")
    stats = obs.metrics.get_histogram_stats('operation_duration')
    if stats:
        print(f"   Operations: {stats['count']}")
        print(f"   Avg duration: {stats['avg']:.0f}ms")
        print(f"   P95: {stats['p95']:.0f}ms")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_observability())
