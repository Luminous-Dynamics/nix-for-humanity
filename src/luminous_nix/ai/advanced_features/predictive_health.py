#!/usr/bin/env python3
"""
Predictive System Health - Predict and prevent issues before they happen
Uses historical data and patterns to forecast system health issues
"""

import logging
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math

logger = logging.getLogger(__name__)


class HealthMetric(Enum):
    """System health metrics to monitor"""

    DISK_USAGE = "disk_usage"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_TEMPERATURE = "cpu_temperature"
    PACKAGE_AGE = "package_age"
    BUILD_TIME = "build_time"
    ERROR_RATE = "error_rate"
    BOOT_TIME = "boot_time"
    SERVICE_FAILURES = "service_failures"
    NETWORK_LATENCY = "network_latency"
    SWAP_USAGE = "swap_usage"


class HealthStatus(Enum):
    """Overall health status"""

    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILING = "failing"


@dataclass
class HealthDataPoint:
    """Single health measurement"""

    metric: HealthMetric
    timestamp: datetime
    value: float
    unit: str


@dataclass
class HealthPrediction:
    """Prediction for a health metric"""

    metric: HealthMetric
    current_value: float
    predicted_value: float
    time_horizon: timedelta
    confidence: float
    trend: str  # rising, falling, stable
    risk_level: str  # low, medium, high
    recommendation: str


@dataclass
class SystemHealthReport:
    """Complete system health analysis and predictions"""

    timestamp: datetime
    overall_status: HealthStatus
    health_score: float  # 0-100

    # Current metrics
    current_metrics: Dict[HealthMetric, float]

    # Predictions
    predictions: List[HealthPrediction]

    # Issues detected
    immediate_issues: List[str]
    predicted_issues: List[Tuple[str, datetime]]  # (issue, predicted_time)

    # Recommendations
    preventive_actions: List[str]
    optimization_suggestions: List[str]

    # Risk assessment
    risk_factors: Dict[str, float]  # factor: risk_score
    estimated_time_to_failure: Optional[timedelta]

    confidence: float


class PredictiveHealthMonitor:
    """
    Monitors system health and predicts future issues
    Uses historical data to forecast problems before they occur
    """

    def __init__(self, db_path: str = "~/.luminous-nix/health.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        # Thresholds for health metrics
        self.thresholds = {
            HealthMetric.DISK_USAGE: {"warning": 80, "critical": 90},
            HealthMetric.MEMORY_PRESSURE: {"warning": 70, "critical": 85},
            HealthMetric.CPU_TEMPERATURE: {"warning": 70, "critical": 85},
            HealthMetric.PACKAGE_AGE: {"warning": 30, "critical": 90},  # days
            HealthMetric.BUILD_TIME: {"warning": 300, "critical": 600},  # seconds
            HealthMetric.ERROR_RATE: {"warning": 5, "critical": 20},  # per hour
            HealthMetric.BOOT_TIME: {"warning": 60, "critical": 120},  # seconds
            HealthMetric.SERVICE_FAILURES: {"warning": 2, "critical": 5},  # count
            HealthMetric.NETWORK_LATENCY: {"warning": 100, "critical": 500},  # ms
            HealthMetric.SWAP_USAGE: {"warning": 50, "critical": 80},  # percent
        }

        # Prediction models (simplified - would use ML in production)
        self.trend_window = 7  # days for trend analysis
        self.prediction_horizon = 7  # days to predict ahead

    def analyze_health(self) -> SystemHealthReport:
        """
        Perform complete system health analysis with predictions

        Returns:
            SystemHealthReport with current status and predictions
        """
        try:
            # Collect current metrics
            current_metrics = self._collect_current_metrics()

            # Store metrics
            self._store_metrics(current_metrics)

            # Load historical data
            historical = self._load_historical_data()

            # Generate predictions
            predictions = self._generate_predictions(historical, current_metrics)

            # Assess overall health
            overall_status = self._assess_overall_status(current_metrics, predictions)
            health_score = self._calculate_health_score(current_metrics, predictions)

            # Identify issues
            immediate = self._identify_immediate_issues(current_metrics)
            predicted = self._identify_predicted_issues(predictions)

            # Generate recommendations
            preventive = self._generate_preventive_actions(predictions, predicted)
            optimizations = self._generate_optimizations(current_metrics, predictions)

            # Risk assessment
            risk_factors = self._assess_risk_factors(current_metrics, predictions)
            time_to_failure = self._estimate_time_to_failure(predictions)

            return SystemHealthReport(
                timestamp=datetime.now(),
                overall_status=overall_status,
                health_score=health_score,
                current_metrics=current_metrics,
                predictions=predictions,
                immediate_issues=immediate,
                predicted_issues=predicted,
                preventive_actions=preventive,
                optimization_suggestions=optimizations,
                risk_factors=risk_factors,
                estimated_time_to_failure=time_to_failure,
                confidence=0.85,
            )

        except Exception as e:
            logger.error(f"Health analysis failed: {e}")
            return self._create_fallback_report(str(e))

    def predict_metric(
        self, metric: HealthMetric, days_ahead: int = 7
    ) -> HealthPrediction:
        """
        Predict future value of specific metric

        Args:
            metric: Metric to predict
            days_ahead: How many days to predict ahead

        Returns:
            HealthPrediction for the metric
        """
        try:
            # Load historical data for metric
            history = self._load_metric_history(metric)

            if len(history) < 3:
                # Not enough data for prediction
                return self._create_simple_prediction(metric)

            # Calculate trend using linear regression
            trend, confidence = self._calculate_trend(history)

            # Project future value
            current_value = history[-1]["value"] if history else 0
            predicted_value = current_value + (trend * days_ahead)

            # Determine risk level
            risk_level = self._assess_risk_level(metric, predicted_value)

            # Generate recommendation
            recommendation = self._generate_metric_recommendation(
                metric, current_value, predicted_value, trend
            )

            return HealthPrediction(
                metric=metric,
                current_value=current_value,
                predicted_value=predicted_value,
                time_horizon=timedelta(days=days_ahead),
                confidence=confidence,
                trend="rising" if trend > 0 else "falling" if trend < 0 else "stable",
                risk_level=risk_level,
                recommendation=recommendation,
            )

        except Exception as e:
            logger.error(f"Prediction failed for {metric}: {e}")
            return self._create_simple_prediction(metric)

    def monitor_continuous(self, callback=None):
        """
        Start continuous health monitoring

        Args:
            callback: Function to call with health reports
        """
        # Would implement continuous monitoring loop
        pass

    def _init_database(self):
        """Initialize health metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                value REAL NOT NULL,
                unit TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_metric_timestamp 
            ON health_metrics(metric, timestamp)
        """
        )

        conn.commit()
        conn.close()

    def _collect_current_metrics(self) -> Dict[HealthMetric, float]:
        """Collect current system health metrics"""
        metrics = {}

        # Disk usage
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")
            metrics[HealthMetric.DISK_USAGE] = (used / total) * 100
        except:
            metrics[HealthMetric.DISK_USAGE] = 0

        # Memory pressure
        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                metrics[HealthMetric.MEMORY_PRESSURE] = (
                    (total - available) / total
                ) * 100
        except:
            metrics[HealthMetric.MEMORY_PRESSURE] = 0

        # CPU temperature (example for thermal zone 0)
        try:
            temp = int(Path("/sys/class/thermal/thermal_zone0/temp").read_text())
            metrics[HealthMetric.CPU_TEMPERATURE] = temp / 1000  # Convert to Celsius
        except:
            metrics[HealthMetric.CPU_TEMPERATURE] = 50  # Default

        # Boot time
        try:
            import subprocess

            result = subprocess.run(
                ["systemd-analyze", "time"], capture_output=True, text=True
            )
            if result.returncode == 0:
                # Parse boot time from output
                import re

                match = re.search(r"(\d+\.\d+)s \(kernel\)", result.stdout)
                if match:
                    metrics[HealthMetric.BOOT_TIME] = float(match.group(1))
        except:
            metrics[HealthMetric.BOOT_TIME] = 30  # Default

        # Swap usage
        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()
                swap_total = int(lines[14].split()[1])
                swap_free = int(lines[15].split()[1])
                if swap_total > 0:
                    metrics[HealthMetric.SWAP_USAGE] = (
                        (swap_total - swap_free) / swap_total
                    ) * 100
                else:
                    metrics[HealthMetric.SWAP_USAGE] = 0
        except:
            metrics[HealthMetric.SWAP_USAGE] = 0

        # Package age (simplified - would check actual package dates)
        metrics[HealthMetric.PACKAGE_AGE] = 15  # Days since last update

        # Error rate (would parse logs)
        metrics[HealthMetric.ERROR_RATE] = 2  # Errors per hour

        # Service failures (would check systemd)
        metrics[HealthMetric.SERVICE_FAILURES] = 0

        # Network latency (would ping gateway)
        metrics[HealthMetric.NETWORK_LATENCY] = 20  # ms

        # Build time (last nixos-rebuild)
        metrics[HealthMetric.BUILD_TIME] = 180  # seconds

        return metrics

    def _store_metrics(self, metrics: Dict[HealthMetric, float]):
        """Store metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now()
        for metric, value in metrics.items():
            cursor.execute(
                """
                INSERT INTO health_metrics (metric, timestamp, value, unit)
                VALUES (?, ?, ?, ?)
            """,
                (metric.value, timestamp, value, self._get_unit(metric)),
            )

        conn.commit()
        conn.close()

    def _load_historical_data(self) -> Dict[HealthMetric, List[Dict]]:
        """Load historical health data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        historical = {}
        for metric in HealthMetric:
            cursor.execute(
                """
                SELECT timestamp, value FROM health_metrics
                WHERE metric = ? AND timestamp > ?
                ORDER BY timestamp
            """,
                (metric.value, datetime.now() - timedelta(days=self.trend_window)),
            )

            historical[metric] = [
                {"timestamp": datetime.fromisoformat(row[0]), "value": row[1]}
                for row in cursor.fetchall()
            ]

        conn.close()
        return historical

    def _load_metric_history(self, metric: HealthMetric) -> List[Dict]:
        """Load history for specific metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, value FROM health_metrics
            WHERE metric = ? AND timestamp > ?
            ORDER BY timestamp
        """,
            (metric.value, datetime.now() - timedelta(days=self.trend_window)),
        )

        history = [
            {"timestamp": datetime.fromisoformat(row[0]), "value": row[1]}
            for row in cursor.fetchall()
        ]

        conn.close()
        return history

    def _generate_predictions(
        self,
        historical: Dict[HealthMetric, List[Dict]],
        current: Dict[HealthMetric, float],
    ) -> List[HealthPrediction]:
        """Generate predictions for all metrics"""
        predictions = []

        for metric in HealthMetric:
            prediction = self.predict_metric(metric, self.prediction_horizon)
            predictions.append(prediction)

        return predictions

    def _calculate_trend(self, history: List[Dict]) -> Tuple[float, float]:
        """Calculate trend using linear regression"""
        if len(history) < 2:
            return 0.0, 0.0

        # Convert to numeric x, y values
        x_values = list(range(len(history)))
        y_values = [point["value"] for point in history]

        # Calculate linear regression
        n = len(x_values)
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0, 0.0

        slope = numerator / denominator

        # Calculate confidence (simplified R-squared)
        y_pred = [slope * x + (y_mean - slope * x_mean) for x in x_values]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(y_values, y_pred))
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)

        confidence = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return slope, max(0, min(1, confidence))

    def _assess_overall_status(
        self, current: Dict[HealthMetric, float], predictions: List[HealthPrediction]
    ) -> HealthStatus:
        """Assess overall system health status"""
        critical_count = 0
        warning_count = 0

        # Check current metrics
        for metric, value in current.items():
            thresholds = self.thresholds.get(metric, {})
            if value >= thresholds.get("critical", float("inf")):
                critical_count += 1
            elif value >= thresholds.get("warning", float("inf")):
                warning_count += 1

        # Check predictions
        for pred in predictions:
            if pred.risk_level == "high":
                critical_count += 1
            elif pred.risk_level == "medium":
                warning_count += 1

        if critical_count > 2:
            return HealthStatus.FAILING
        elif critical_count > 0:
            return HealthStatus.CRITICAL
        elif warning_count > 3:
            return HealthStatus.WARNING
        elif warning_count > 0:
            return HealthStatus.GOOD
        else:
            return HealthStatus.EXCELLENT

    def _calculate_health_score(
        self, current: Dict[HealthMetric, float], predictions: List[HealthPrediction]
    ) -> float:
        """Calculate overall health score (0-100)"""
        scores = []

        for metric, value in current.items():
            thresholds = self.thresholds.get(metric, {})
            critical = thresholds.get("critical", 100)
            warning = thresholds.get("warning", 80)

            if value >= critical:
                score = 0
            elif value >= warning:
                score = 50 * (critical - value) / (critical - warning)
            else:
                score = 50 + 50 * (warning - value) / warning

            scores.append(max(0, min(100, score)))

        return statistics.mean(scores) if scores else 50

    def _identify_immediate_issues(
        self, current: Dict[HealthMetric, float]
    ) -> List[str]:
        """Identify immediate health issues"""
        issues = []

        for metric, value in current.items():
            thresholds = self.thresholds.get(metric, {})
            if value >= thresholds.get("critical", float("inf")):
                issues.append(f"{metric.value}: {value:.1f} (critical)")
            elif value >= thresholds.get("warning", float("inf")):
                issues.append(f"{metric.value}: {value:.1f} (warning)")

        return issues

    def _identify_predicted_issues(
        self, predictions: List[HealthPrediction]
    ) -> List[Tuple[str, datetime]]:
        """Identify predicted future issues"""
        issues = []

        for pred in predictions:
            if pred.risk_level == "high":
                predicted_time = datetime.now() + pred.time_horizon
                issues.append(
                    (f"{pred.metric.value} will reach critical level", predicted_time)
                )

        return issues

    def _generate_preventive_actions(
        self,
        predictions: List[HealthPrediction],
        predicted_issues: List[Tuple[str, datetime]],
    ) -> List[str]:
        """Generate preventive action recommendations"""
        actions = []

        for pred in predictions:
            if pred.risk_level in ["high", "medium"]:
                if pred.metric == HealthMetric.DISK_USAGE:
                    actions.append("Run garbage collection: nix-collect-garbage -d")
                elif pred.metric == HealthMetric.MEMORY_PRESSURE:
                    actions.append("Consider adding swap or closing heavy applications")
                elif pred.metric == HealthMetric.PACKAGE_AGE:
                    actions.append("Update packages: nixos-rebuild switch --upgrade")
                elif pred.metric == HealthMetric.CPU_TEMPERATURE:
                    actions.append("Check cooling system and reduce CPU load")

        return actions

    def _generate_optimizations(
        self, current: Dict[HealthMetric, float], predictions: List[HealthPrediction]
    ) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []

        if current.get(HealthMetric.BOOT_TIME, 0) > 45:
            suggestions.append("Optimize boot time by disabling unnecessary services")

        if current.get(HealthMetric.BUILD_TIME, 0) > 300:
            suggestions.append("Enable binary caches to speed up rebuilds")

        if current.get(HealthMetric.SWAP_USAGE, 0) > 30:
            suggestions.append("Consider adding more RAM or optimizing memory usage")

        return suggestions

    def _assess_risk_factors(
        self, current: Dict[HealthMetric, float], predictions: List[HealthPrediction]
    ) -> Dict[str, float]:
        """Assess risk factors"""
        risks = {}

        # Disk risk
        disk_usage = current.get(HealthMetric.DISK_USAGE, 0)
        risks["disk_failure"] = min(100, disk_usage * 1.2)

        # Performance risk
        memory = current.get(HealthMetric.MEMORY_PRESSURE, 0)
        swap = current.get(HealthMetric.SWAP_USAGE, 0)
        risks["performance_degradation"] = min(100, (memory + swap) / 2)

        # Stability risk
        errors = current.get(HealthMetric.ERROR_RATE, 0)
        failures = current.get(HealthMetric.SERVICE_FAILURES, 0)
        risks["system_instability"] = min(100, (errors * 5 + failures * 20))

        return risks

    def _estimate_time_to_failure(
        self, predictions: List[HealthPrediction]
    ) -> Optional[timedelta]:
        """Estimate time until system failure"""
        critical_predictions = [p for p in predictions if p.risk_level == "high"]

        if not critical_predictions:
            return None

        # Find soonest critical issue
        soonest = min(p.time_horizon for p in critical_predictions)
        return soonest

    def _assess_risk_level(self, metric: HealthMetric, predicted_value: float) -> str:
        """Assess risk level for predicted value"""
        thresholds = self.thresholds.get(metric, {})

        if predicted_value >= thresholds.get("critical", float("inf")):
            return "high"
        elif predicted_value >= thresholds.get("warning", float("inf")):
            return "medium"
        else:
            return "low"

    def _generate_metric_recommendation(
        self, metric: HealthMetric, current: float, predicted: float, trend: float
    ) -> str:
        """Generate recommendation for specific metric"""
        if metric == HealthMetric.DISK_USAGE:
            if predicted > 90:
                return (
                    f"Disk will be full in {int(predicted - current)} days. Clean now!"
                )
            elif predicted > 80:
                return "Schedule disk cleanup soon"
        elif metric == HealthMetric.MEMORY_PRESSURE:
            if trend > 0:
                return "Memory usage trending up. Identify memory leaks"
        elif metric == HealthMetric.PACKAGE_AGE:
            if predicted > 60:
                return "Packages becoming outdated. Schedule update"

        return "Monitor and maintain current practices"

    def _get_unit(self, metric: HealthMetric) -> str:
        """Get unit for metric"""
        units = {
            HealthMetric.DISK_USAGE: "%",
            HealthMetric.MEMORY_PRESSURE: "%",
            HealthMetric.CPU_TEMPERATURE: "°C",
            HealthMetric.PACKAGE_AGE: "days",
            HealthMetric.BUILD_TIME: "seconds",
            HealthMetric.ERROR_RATE: "/hour",
            HealthMetric.BOOT_TIME: "seconds",
            HealthMetric.SERVICE_FAILURES: "count",
            HealthMetric.NETWORK_LATENCY: "ms",
            HealthMetric.SWAP_USAGE: "%",
        }
        return units.get(metric, "")

    def _create_simple_prediction(self, metric: HealthMetric) -> HealthPrediction:
        """Create simple prediction when insufficient data"""
        return HealthPrediction(
            metric=metric,
            current_value=0,
            predicted_value=0,
            time_horizon=timedelta(days=7),
            confidence=0.1,
            trend="unknown",
            risk_level="low",
            recommendation="Insufficient data for prediction",
        )

    def _create_fallback_report(self, error: str) -> SystemHealthReport:
        """Create fallback report on error"""
        return SystemHealthReport(
            timestamp=datetime.now(),
            overall_status=HealthStatus.WARNING,
            health_score=50,
            current_metrics={},
            predictions=[],
            immediate_issues=[f"Health monitoring error: {error}"],
            predicted_issues=[],
            preventive_actions=["Fix health monitoring system"],
            optimization_suggestions=[],
            risk_factors={},
            estimated_time_to_failure=None,
            confidence=0.1,
        )
