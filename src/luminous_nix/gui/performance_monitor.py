#!/usr/bin/env python3
"""
📊 Performance Monitoring Dashboard
Tracks and visualizes AI interface generation performance over time
"""

import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class PerformanceMetric:
    """Single performance measurement"""

    timestamp: datetime
    request: str
    generation_time: float  # milliseconds
    component_count: int
    success: bool
    accuracy: float
    persona: str
    memory_usage: float | None = None
    cache_hits: int = 0
    pattern_reuse: bool = False


class PerformanceMonitor:
    """Monitors and tracks performance metrics"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = (
                Path.home() / ".local" / "share" / "luminous-nix" / "performance.db"
            )
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self._init_database()

    def _init_database(self):
        """Initialize performance tracking database"""

        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                request TEXT,
                generation_time REAL,
                component_count INTEGER,
                success BOOLEAN,
                accuracy REAL,
                persona TEXT,
                memory_usage REAL,
                cache_hits INTEGER,
                pattern_reuse BOOLEAN
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_summary (
                date TEXT PRIMARY KEY,
                avg_generation_time REAL,
                avg_accuracy REAL,
                total_requests INTEGER,
                success_rate REAL,
                cache_hit_rate REAL,
                pattern_reuse_rate REAL
            )
        """
        )

        self.conn.commit()

    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO performance_metrics
            VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metric.timestamp.isoformat(),
                metric.request,
                metric.generation_time,
                metric.component_count,
                metric.success,
                metric.accuracy,
                metric.persona,
                metric.memory_usage,
                metric.cache_hits,
                metric.pattern_reuse,
            ),
        )
        self.conn.commit()

    def get_metrics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        persona: str | None = None,
    ) -> list[PerformanceMetric]:
        """Retrieve metrics within date range"""

        query = "SELECT * FROM performance_metrics WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        if persona:
            query += " AND persona = ?"
            params.append(persona)

        query += " ORDER BY timestamp DESC"

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        metrics = []
        for row in cursor.fetchall():
            metrics.append(
                PerformanceMetric(
                    timestamp=datetime.fromisoformat(row[1]),
                    request=row[2],
                    generation_time=row[3],
                    component_count=row[4],
                    success=bool(row[5]),
                    accuracy=row[6],
                    persona=row[7],
                    memory_usage=row[8],
                    cache_hits=row[9],
                    pattern_reuse=bool(row[10]),
                )
            )

        return metrics

    def calculate_summary(self, date: datetime | None = None) -> dict:
        """Calculate daily summary statistics"""

        if date is None:
            date = datetime.now()

        start = date.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)

        metrics = self.get_metrics(start, end)

        if not metrics:
            return {}

        summary = {
            "date": date.date().isoformat(),
            "avg_generation_time": sum(m.generation_time for m in metrics)
            / len(metrics),
            "avg_accuracy": sum(m.accuracy for m in metrics) / len(metrics),
            "total_requests": len(metrics),
            "success_rate": sum(1 for m in metrics if m.success) / len(metrics),
            "cache_hit_rate": sum(m.cache_hits for m in metrics) / len(metrics),
            "pattern_reuse_rate": sum(1 for m in metrics if m.pattern_reuse)
            / len(metrics),
        }

        # Store summary
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO performance_summary
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            tuple(summary.values()),
        )
        self.conn.commit()

        return summary

    def get_trends(self, days: int = 7) -> dict:
        """Get performance trends over time"""

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM performance_summary
            WHERE date >= ?
            ORDER BY date
        """,
            (start_date.date().isoformat(),),
        )

        trends = {
            "dates": [],
            "generation_times": [],
            "accuracy": [],
            "success_rates": [],
            "request_counts": [],
        }

        for row in cursor.fetchall():
            trends["dates"].append(row[0])
            trends["generation_times"].append(row[1])
            trends["accuracy"].append(row[2])
            trends["request_counts"].append(row[3])
            trends["success_rates"].append(row[4])

        return trends

    def identify_bottlenecks(self) -> dict:
        """Identify performance bottlenecks"""

        # Get recent metrics
        recent = self.get_metrics(start_date=datetime.now() - timedelta(days=1))

        if not recent:
            return {}

        bottlenecks = {
            "slow_requests": [],
            "failed_requests": [],
            "low_accuracy": [],
            "complex_requests": [],
        }

        for metric in recent:
            # Slow generation (>100ms)
            if metric.generation_time > 100:
                bottlenecks["slow_requests"].append(
                    {"request": metric.request, "time": metric.generation_time}
                )

            # Failed requests
            if not metric.success:
                bottlenecks["failed_requests"].append(metric.request)

            # Low accuracy (<50%)
            if metric.accuracy < 0.5:
                bottlenecks["low_accuracy"].append(
                    {"request": metric.request, "accuracy": metric.accuracy}
                )

            # Complex requests (>5 components)
            if metric.component_count > 5:
                bottlenecks["complex_requests"].append(
                    {"request": metric.request, "components": metric.component_count}
                )

        return bottlenecks

    def generate_report(self) -> str:
        """Generate performance report"""

        report = []
        report.append("=" * 60)
        report.append("📊 PERFORMANCE MONITORING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Today's summary
        today_summary = self.calculate_summary()
        if today_summary:
            report.append("📅 TODAY'S PERFORMANCE")
            report.append("-" * 40)
            report.append(f"Total Requests: {today_summary['total_requests']}")
            report.append(
                f"Avg Generation Time: {today_summary['avg_generation_time']:.2f}ms"
            )
            report.append(f"Avg Accuracy: {today_summary['avg_accuracy']:.0%}")
            report.append(f"Success Rate: {today_summary['success_rate']:.0%}")
            report.append("")

        # Weekly trends
        trends = self.get_trends(7)
        if trends["dates"]:
            report.append("📈 WEEKLY TRENDS")
            report.append("-" * 40)

            # Calculate trend direction
            if len(trends["generation_times"]) >= 2:
                time_trend = (
                    trends["generation_times"][-1] - trends["generation_times"][0]
                )
                trend_symbol = "📈" if time_trend > 0 else "📉"
                report.append(
                    f"Generation Time: {trend_symbol} {abs(time_trend):.2f}ms"
                )

            if len(trends["accuracy"]) >= 2:
                acc_trend = trends["accuracy"][-1] - trends["accuracy"][0]
                trend_symbol = "📈" if acc_trend > 0 else "📉"
                report.append(f"Accuracy: {trend_symbol} {abs(acc_trend):.0%}")

            report.append("")

        # Bottlenecks
        bottlenecks = self.identify_bottlenecks()
        if any(bottlenecks.values()):
            report.append("⚠️ PERFORMANCE BOTTLENECKS")
            report.append("-" * 40)

            if bottlenecks["slow_requests"]:
                report.append(f"Slow Requests: {len(bottlenecks['slow_requests'])}")

            if bottlenecks["failed_requests"]:
                report.append(f"Failed Requests: {len(bottlenecks['failed_requests'])}")

            if bottlenecks["low_accuracy"]:
                report.append(f"Low Accuracy: {len(bottlenecks['low_accuracy'])}")

            report.append("")

        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 40)

        if today_summary:
            if today_summary["avg_generation_time"] > 50:
                report.append("• Consider implementing caching for common requests")

            if today_summary["avg_accuracy"] < 0.7:
                report.append("• Review NLP parsing rules and component matching")

            if today_summary["pattern_reuse_rate"] < 0.3:
                report.append("• Improve pattern recognition and reuse")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def visualize_dashboard(self):
        """Create simple ASCII dashboard"""

        print("\n" + "=" * 60)
        print("🎯 PERFORMANCE DASHBOARD")
        print("=" * 60)

        # Get recent metrics
        recent = self.get_metrics(start_date=datetime.now() - timedelta(hours=1))

        if recent:
            print("\n📊 Last Hour Statistics")
            print("-" * 40)
            print(f"Requests: {len(recent)}")
            print(
                f"Avg Time: {sum(m.generation_time for m in recent)/len(recent):.2f}ms"
            )
            print(
                f"Success Rate: {sum(1 for m in recent if m.success)/len(recent):.0%}"
            )

        # Show trends as ASCII chart
        trends = self.get_trends(7)
        if trends["generation_times"]:
            print("\n📈 Generation Time Trend (7 days)")
            print("-" * 40)

            max_val = max(trends["generation_times"])
            min_val = min(trends["generation_times"])

            for i, (date, value) in enumerate(
                zip(trends["dates"], trends["generation_times"], strict=False)
            ):
                # Normalize to 0-10 scale for bar
                if max_val > min_val:
                    normalized = int(((value - min_val) / (max_val - min_val)) * 20)
                else:
                    normalized = 10

                bar = "█" * normalized
                print(f"{date[-5:]}: {bar} {value:.2f}ms")

        print("\n" + "=" * 60)


def run_performance_test():
    """Run a performance test and record metrics"""

    import sys

    sys.path.insert(0, str(Path(__file__).parent))

    from nl_interface_builder import NLInterfaceBuilder, UserContext

    monitor = PerformanceMonitor()
    builder = NLInterfaceBuilder()

    test_cases = [
        ("Create a simple button", "beginner"),
        ("Build a dashboard with charts", "intermediate"),
        ("Design a complex IDE interface", "expert"),
    ]

    print("\n🏃 Running Performance Test...")

    for request, persona in test_cases:
        context = UserContext(user_id=f"{persona}_user", expertise_level=persona)

        start_time = time.time()
        try:
            interface = builder.build_interface(request, context)
            generation_time = (time.time() - start_time) * 1000

            # Simple accuracy estimation
            accuracy = 0.5 + (0.1 * len(interface.components))
            accuracy = min(accuracy, 1.0)

            metric = PerformanceMetric(
                timestamp=datetime.now(),
                request=request,
                generation_time=generation_time,
                component_count=len(interface.components),
                success=True,
                accuracy=accuracy,
                persona=persona,
            )

            monitor.record_metric(metric)
            print(f"✅ {request[:30]}... - {generation_time:.2f}ms")

        except Exception as e:
            print(f"❌ {request[:30]}... - Failed: {e}")

    # Generate report
    print("\n" + monitor.generate_report())

    # Show dashboard
    monitor.visualize_dashboard()


if __name__ == "__main__":
    run_performance_test()
