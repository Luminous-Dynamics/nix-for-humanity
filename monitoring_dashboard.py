#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard for Luminous Nix
Tracks adoption, performance, and health metrics
"""

import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path


class MetricsDashboard:
    """Real-time metrics tracking for Luminous Nix"""

    def __init__(self):
        self.metrics = {
            "github_stars": 0,
            "github_forks": 0,
            "pypi_downloads": 0,
            "open_issues": 0,
            "closed_issues": 0,
            "pull_requests": 0,
            "discord_members": 0,
            "active_users": 0,
            "queries_today": 0,
            "avg_latency_ms": 0,
            "cache_hit_rate": 0,
            "error_rate": 0,
            "user_accuracy": 96.3,  # Starting baseline
        }

        self.alerts = []
        self.trends = {}

    def fetch_github_metrics(self, repo: str = "Luminous-Dynamics/luminous-nix"):
        """Fetch metrics from GitHub"""
        try:
            # Using gh CLI
            result = subprocess.run(
                ["gh", "api", f"repos/{repo}"], capture_output=True, text=True
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.metrics["github_stars"] = data.get("stargazers_count", 0)
                self.metrics["github_forks"] = data.get("forks_count", 0)
                self.metrics["open_issues"] = data.get("open_issues_count", 0)

            # Get closed issues count
            result = subprocess.run(
                ["gh", "issue", "list", "--state", "closed", "--json", "number"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                issues = json.loads(result.stdout)
                self.metrics["closed_issues"] = len(issues)

        except Exception as e:
            print(f"Error fetching GitHub metrics: {e}")

    def fetch_pypi_metrics(self, package: str = "luminous-nix"):
        """Fetch download stats from PyPI"""
        try:
            # This would use pypistats API in production
            # For now, simulate with placeholder
            import random

            self.metrics["pypi_downloads"] += random.randint(5, 20)
        except Exception as e:
            print(f"Error fetching PyPI metrics: {e}")

    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        score = 0

        # GitHub engagement (30 points)
        if self.metrics["github_stars"] > 0:
            score += min(30, self.metrics["github_stars"] / 10 * 3)

        # Download momentum (20 points)
        if self.metrics["pypi_downloads"] > 0:
            score += min(20, self.metrics["pypi_downloads"] / 50 * 2)

        # Issue resolution (20 points)
        total_issues = self.metrics["open_issues"] + self.metrics["closed_issues"]
        if total_issues > 0:
            resolution_rate = self.metrics["closed_issues"] / total_issues
            score += resolution_rate * 20

        # User accuracy (20 points)
        if self.metrics["user_accuracy"] > 90:
            score += (self.metrics["user_accuracy"] - 90) * 2

        # Performance (10 points)
        if self.metrics["avg_latency_ms"] < 1:
            score += 10
        elif self.metrics["avg_latency_ms"] < 10:
            score += 5

        return min(100, score)

    def detect_alerts(self):
        """Detect issues that need attention"""
        self.alerts = []

        # Critical alerts
        if self.metrics["user_accuracy"] < 95:
            self.alerts.append(
                {
                    "level": "critical",
                    "message": f"User accuracy below target: {self.metrics['user_accuracy']}%",
                }
            )

        if self.metrics["error_rate"] > 5:
            self.alerts.append(
                {
                    "level": "critical",
                    "message": f"High error rate: {self.metrics['error_rate']}%",
                }
            )

        # Warning alerts
        if self.metrics["open_issues"] > 20:
            self.alerts.append(
                {
                    "level": "warning",
                    "message": f"High open issue count: {self.metrics['open_issues']}",
                }
            )

        if self.metrics["avg_latency_ms"] > 10:
            self.alerts.append(
                {
                    "level": "warning",
                    "message": f"Latency above target: {self.metrics['avg_latency_ms']}ms",
                }
            )

        # Info alerts
        if self.metrics["github_stars"] > 50:
            self.alerts.append(
                {
                    "level": "info",
                    "message": f"🎉 Milestone: {self.metrics['github_stars']} stars!",
                }
            )

    def calculate_trends(self):
        """Calculate trend indicators"""
        # This would compare with historical data
        # For now, simulate trends
        self.trends = {
            "stars": "up",
            "downloads": "up",
            "accuracy": "stable",
            "latency": "down",
            "issues": "stable",
        }

    def generate_dashboard(self) -> str:
        """Generate text dashboard"""
        self.fetch_github_metrics()
        self.fetch_pypi_metrics()
        self.detect_alerts()
        self.calculate_trends()

        health_score = self.calculate_health_score()

        dashboard = f"""
╔══════════════════════════════════════════════════════════╗
║         LUMINOUS NIX v0.3.0 - MONITORING DASHBOARD        ║
╠══════════════════════════════════════════════════════════╣
║  Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
║  Health Score: {health_score:.1f}/100 {'🟢' if health_score > 70 else '🟡' if health_score > 40 else '🔴'}                      ║
╚══════════════════════════════════════════════════════════╝

📊 ADOPTION METRICS
┌─────────────────────────────┬──────────────┬─────────┐
│ Metric                      │ Value        │ Trend   │
├─────────────────────────────┼──────────────┼─────────┤
│ GitHub Stars                │ {self.metrics['github_stars']:>12} │ {self._trend_icon(self.trends.get('stars', 'stable'))}      │
│ GitHub Forks                │ {self.metrics['github_forks']:>12} │ {self._trend_icon('stable')}      │
│ PyPI Downloads (week)       │ {self.metrics['pypi_downloads']:>12} │ {self._trend_icon(self.trends.get('downloads', 'stable'))}      │
│ Discord Members             │ {self.metrics['discord_members']:>12} │ {self._trend_icon('stable')}      │
│ Active Users (daily)        │ {self.metrics['active_users']:>12} │ {self._trend_icon('stable')}      │
└─────────────────────────────┴──────────────┴─────────┘

⚡ PERFORMANCE METRICS
┌─────────────────────────────┬──────────────┬─────────┐
│ Metric                      │ Value        │ Status  │
├─────────────────────────────┼──────────────┼─────────┤
│ User Accuracy               │ {self.metrics['user_accuracy']:>11.1f}% │ {'✅' if self.metrics['user_accuracy'] >= 95 else '⚠️'}      │
│ Average Latency             │ {self.metrics['avg_latency_ms']:>10.2f}ms │ {'✅' if self.metrics['avg_latency_ms'] < 1 else '⚠️'}      │
│ Cache Hit Rate              │ {self.metrics['cache_hit_rate']:>11.1f}% │ {'✅' if self.metrics['cache_hit_rate'] > 50 else '⚠️'}      │
│ Error Rate                  │ {self.metrics['error_rate']:>11.1f}% │ {'✅' if self.metrics['error_rate'] < 5 else '🔴'}      │
│ Queries Today               │ {self.metrics['queries_today']:>12} │ -       │
└─────────────────────────────┴──────────────┴─────────┘

🐛 ISSUE TRACKING
┌─────────────────────────────┬──────────────┬─────────┐
│ Type                        │ Count        │ Trend   │
├─────────────────────────────┼──────────────┼─────────┤
│ Open Issues                 │ {self.metrics['open_issues']:>12} │ {self._trend_icon(self.trends.get('issues', 'stable'))}      │
│ Closed Issues               │ {self.metrics['closed_issues']:>12} │ -       │
│ Pull Requests               │ {self.metrics['pull_requests']:>12} │ -       │
│ Resolution Rate             │ {self._resolution_rate():>11.1f}% │ -       │
└─────────────────────────────┴──────────────┴─────────┘
"""

        if self.alerts:
            dashboard += "\n🚨 ALERTS\n"
            for alert in self.alerts:
                icon = (
                    "🔴"
                    if alert["level"] == "critical"
                    else "🟡"
                    if alert["level"] == "warning"
                    else "ℹ️"
                )
                dashboard += f"{icon} {alert['message']}\n"

        return dashboard

    def _trend_icon(self, trend: str) -> str:
        """Get icon for trend"""
        if trend == "up":
            return "↑ 📈"
        elif trend == "down":
            return "↓ 📉"
        else:
            return "→ 📊"

    def _resolution_rate(self) -> float:
        """Calculate issue resolution rate"""
        total = self.metrics["open_issues"] + self.metrics["closed_issues"]
        if total == 0:
            return 0
        return (self.metrics["closed_issues"] / total) * 100

    def generate_json_metrics(self) -> dict:
        """Generate metrics in JSON format for API"""
        return {
            "timestamp": datetime.now().isoformat(),
            "version": "0.3.0",
            "health_score": self.calculate_health_score(),
            "metrics": self.metrics,
            "trends": self.trends,
            "alerts": self.alerts,
        }

    def save_metrics(self, filepath: str = "data/metrics_history.json"):
        """Save metrics to file for historical tracking"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Load existing history
        history = []
        if Path(filepath).exists():
            with open(filepath) as f:
                history = json.load(f)

        # Append current metrics
        history.append(self.generate_json_metrics())

        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        history = [
            m for m in history if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

        # Save updated history
        with open(filepath, "w") as f:
            json.dump(history, f, indent=2)


def run_monitoring_loop():
    """Run continuous monitoring loop"""
    dashboard = MetricsDashboard()

    print("🚀 Starting Luminous Nix Monitoring Dashboard")
    print("Press Ctrl+C to stop")
    print("-" * 60)

    try:
        while True:
            # Clear screen (Unix/Linux)
            print("\033[2J\033[H")

            # Generate and display dashboard
            output = dashboard.generate_dashboard()
            print(output)

            # Save metrics
            dashboard.save_metrics()

            # Update every 60 seconds
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n✅ Monitoring stopped")

        # Save final metrics
        with open("final_metrics.json", "w") as f:
            json.dump(dashboard.generate_json_metrics(), f, indent=2)

        print("Metrics saved to final_metrics.json")


if __name__ == "__main__":
    run_monitoring_loop()
