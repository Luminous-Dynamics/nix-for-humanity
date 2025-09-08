#!/usr/bin/env python3
"""
ML Health Predictor - Advanced machine learning for predictive system health

This module uses machine learning models to predict system health issues
before they occur, enabling proactive maintenance and optimization.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from collections import deque
import pickle


class HealthMetric(Enum):
    """System health metrics"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_LATENCY = "network_latency"
    SERVICE_UPTIME = "service_uptime"
    ERROR_RATE = "error_rate"
    BUILD_TIME = "build_time"
    PACKAGE_CONFLICTS = "package_conflicts"
    CONFIG_COMPLEXITY = "config_complexity"
    SECURITY_SCORE = "security_score"


class PredictionType(Enum):
    """Types of health predictions"""
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SERVICE_FAILURE = "service_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_VULNERABILITY = "security_vulnerability"
    CONFIGURATION_DRIFT = "configuration_drift"
    DEPENDENCY_CONFLICT = "dependency_conflict"


class HealthTrend(Enum):
    """Health trend indicators"""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    CRITICAL = "critical"


@dataclass
class HealthDataPoint:
    """Single health measurement"""
    metric: HealthMetric
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthPrediction:
    """Health prediction result"""
    type: PredictionType
    probability: float
    time_horizon: timedelta
    affected_metrics: List[HealthMetric]
    recommended_actions: List[str]
    confidence: float
    explanation: str


@dataclass
class SystemHealthProfile:
    """Complete system health profile"""
    current_health: Dict[HealthMetric, float]
    trends: Dict[HealthMetric, HealthTrend]
    predictions: List[HealthPrediction]
    risk_score: float
    optimization_opportunities: List[str]
    last_updated: datetime


class MLHealthPredictor:
    """
    Machine learning-based health predictor for NixOS systems
    
    Uses multiple ML techniques:
    - Time series analysis for trend detection
    - Anomaly detection for outliers
    - Pattern recognition for failure prediction
    - Correlation analysis for root cause identification
    """
    
    def __init__(self, model_dir: Optional[Path] = None):
        """Initialize the ML health predictor"""
        self.logger = logging.getLogger(__name__)
        
        # Model storage
        self.model_dir = model_dir or Path.home() / ".luminous_nix" / "ml_models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Data collection
        self.metric_history: Dict[HealthMetric, deque] = {
            metric: deque(maxlen=1000)
            for metric in HealthMetric
        }
        
        # ML models (simplified for demonstration)
        self.trend_models = {}
        self.anomaly_models = {}
        self.prediction_models = {}
        
        # Thresholds and parameters
        self.thresholds = self._initialize_thresholds()
        self.correlation_matrix = np.zeros((len(HealthMetric), len(HealthMetric)))
        
        # Load or initialize models
        self._load_or_initialize_models()
        
        self.logger.info("ML Health Predictor initialized")
    
    def _initialize_thresholds(self) -> Dict[HealthMetric, Dict[str, float]]:
        """Initialize health metric thresholds"""
        return {
            HealthMetric.CPU_USAGE: {
                "warning": 70.0,
                "critical": 90.0,
                "anomaly": 2.0  # Standard deviations
            },
            HealthMetric.MEMORY_USAGE: {
                "warning": 80.0,
                "critical": 95.0,
                "anomaly": 2.5
            },
            HealthMetric.DISK_USAGE: {
                "warning": 80.0,
                "critical": 90.0,
                "anomaly": 1.5
            },
            HealthMetric.ERROR_RATE: {
                "warning": 5.0,
                "critical": 10.0,
                "anomaly": 3.0
            },
            HealthMetric.BUILD_TIME: {
                "warning": 300,  # 5 minutes
                "critical": 600,  # 10 minutes
                "anomaly": 2.0
            },
            HealthMetric.SECURITY_SCORE: {
                "warning": 70.0,
                "critical": 50.0,
                "anomaly": 2.0
            }
        }
    
    def _load_or_initialize_models(self):
        """Load existing models or initialize new ones"""
        models_path = self.model_dir / "health_models.pkl"
        
        if models_path.exists():
            try:
                with open(models_path, 'rb') as f:
                    saved_models = pickle.load(f)
                    self.trend_models = saved_models.get('trend', {})
                    self.anomaly_models = saved_models.get('anomaly', {})
                    self.prediction_models = saved_models.get('prediction', {})
                    self.logger.info("Loaded existing ML models")
            except Exception as e:
                self.logger.warning(f"Failed to load models: {e}")
                self._initialize_new_models()
        else:
            self._initialize_new_models()
    
    def _initialize_new_models(self):
        """Initialize new ML models"""
        # Simple models for demonstration
        # In production, use sklearn, tensorflow, or pytorch
        
        for metric in HealthMetric:
            # Trend detection (moving average based)
            self.trend_models[metric] = {
                'window_size': 20,
                'trend_threshold': 0.1
            }
            
            # Anomaly detection (z-score based)
            self.anomaly_models[metric] = {
                'mean': 0.0,
                'std': 1.0,
                'threshold': self.thresholds.get(metric, {}).get('anomaly', 2.0)
            }
            
            # Prediction (simple linear extrapolation)
            self.prediction_models[metric] = {
                'coefficients': [0.0, 0.0],  # Linear regression coefficients
                'confidence': 0.5
            }
        
        self.logger.info("Initialized new ML models")
    
    def collect_metric(self, metric: HealthMetric, value: float, 
                       context: Optional[Dict] = None) -> None:
        """Collect a health metric data point"""
        
        datapoint = HealthDataPoint(
            metric=metric,
            value=value,
            timestamp=datetime.now(),
            context=context or {}
        )
        
        self.metric_history[metric].append(datapoint)
        
        # Update models with new data
        self._update_models(metric, datapoint)
    
    def _update_models(self, metric: HealthMetric, datapoint: HealthDataPoint):
        """Update ML models with new data"""
        
        history = list(self.metric_history[metric])
        if len(history) < 2:
            return
        
        values = [dp.value for dp in history]
        
        # Update anomaly detection parameters
        if len(values) >= 10:
            self.anomaly_models[metric]['mean'] = np.mean(values[-100:])
            self.anomaly_models[metric]['std'] = np.std(values[-100:])
        
        # Update trend detection
        if len(values) >= 20:
            recent = np.mean(values[-10:])
            older = np.mean(values[-20:-10])
            trend_change = (recent - older) / (older + 0.001)
            
            if abs(trend_change) > self.trend_models[metric]['trend_threshold']:
                # Significant trend detected
                self.logger.debug(f"Trend detected in {metric.value}: {trend_change:.2%}")
        
        # Update prediction model (simple linear regression)
        if len(values) >= 30:
            x = np.arange(len(values[-30:]))
            y = np.array(values[-30:])
            
            # Simple least squares
            A = np.vstack([x, np.ones(len(x))]).T
            coeffs = np.linalg.lstsq(A, y, rcond=None)[0]
            self.prediction_models[metric]['coefficients'] = coeffs.tolist()
    
    def analyze_current_health(self) -> SystemHealthProfile:
        """Analyze current system health"""
        
        current_health = {}
        trends = {}
        
        # Analyze each metric
        for metric in HealthMetric:
            history = list(self.metric_history[metric])
            
            if not history:
                current_health[metric] = 0.0
                trends[metric] = HealthTrend.STABLE
                continue
            
            # Current value
            current_health[metric] = history[-1].value
            
            # Determine trend
            trends[metric] = self._determine_trend(metric, history)
        
        # Generate predictions
        predictions = self._generate_predictions(current_health, trends)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(current_health, predictions)
        
        # Identify optimization opportunities
        opportunities = self._identify_optimizations(current_health, trends)
        
        return SystemHealthProfile(
            current_health=current_health,
            trends=trends,
            predictions=predictions,
            risk_score=risk_score,
            optimization_opportunities=opportunities,
            last_updated=datetime.now()
        )
    
    def _determine_trend(self, metric: HealthMetric, 
                        history: List[HealthDataPoint]) -> HealthTrend:
        """Determine the trend for a metric"""
        
        if len(history) < 10:
            return HealthTrend.STABLE
        
        values = [dp.value for dp in history[-20:]]
        
        # Calculate trend
        recent_avg = np.mean(values[-5:])
        older_avg = np.mean(values[-10:-5])
        
        change_rate = (recent_avg - older_avg) / (older_avg + 0.001)
        
        # Check against thresholds
        thresholds = self.thresholds.get(metric, {})
        
        if recent_avg > thresholds.get('critical', float('inf')):
            return HealthTrend.CRITICAL
        elif change_rate > 0.2:
            return HealthTrend.DEGRADING
        elif change_rate < -0.1:
            return HealthTrend.IMPROVING
        else:
            return HealthTrend.STABLE
    
    def _generate_predictions(self, current_health: Dict[HealthMetric, float],
                            trends: Dict[HealthMetric, HealthTrend]) -> List[HealthPrediction]:
        """Generate health predictions"""
        
        predictions = []
        
        # Resource exhaustion prediction
        for metric in [HealthMetric.CPU_USAGE, HealthMetric.MEMORY_USAGE, 
                      HealthMetric.DISK_USAGE]:
            if metric not in current_health:
                continue
            
            current = current_health[metric]
            trend = trends.get(metric, HealthTrend.STABLE)
            
            if trend == HealthTrend.DEGRADING and current > 60:
                # Predict time to exhaustion
                model = self.prediction_models.get(metric, {})
                coeffs = model.get('coefficients', [0, 0])
                
                if coeffs[0] > 0:  # Positive slope
                    # Simple linear extrapolation
                    time_to_critical = (90 - current) / (coeffs[0] + 0.001)
                    
                    predictions.append(HealthPrediction(
                        type=PredictionType.RESOURCE_EXHAUSTION,
                        probability=min(0.9, current / 100 + 0.2),
                        time_horizon=timedelta(hours=max(1, time_to_critical)),
                        affected_metrics=[metric],
                        recommended_actions=[
                            f"Monitor {metric.value} closely",
                            "Consider resource optimization",
                            "Plan for capacity increase"
                        ],
                        confidence=0.7,
                        explanation=f"{metric.value} showing degradation trend, may reach critical levels"
                    ))
        
        # Service failure prediction
        error_rate = current_health.get(HealthMetric.ERROR_RATE, 0)
        if error_rate > 3 and trends.get(HealthMetric.ERROR_RATE) == HealthTrend.DEGRADING:
            predictions.append(HealthPrediction(
                type=PredictionType.SERVICE_FAILURE,
                probability=min(0.8, error_rate / 10),
                time_horizon=timedelta(hours=6),
                affected_metrics=[HealthMetric.ERROR_RATE, HealthMetric.SERVICE_UPTIME],
                recommended_actions=[
                    "Review service logs",
                    "Check dependency health",
                    "Prepare rollback plan"
                ],
                confidence=0.75,
                explanation="Increasing error rate detected, service stability at risk"
            ))
        
        # Performance degradation prediction
        build_time = current_health.get(HealthMetric.BUILD_TIME, 0)
        if build_time > 180 and trends.get(HealthMetric.BUILD_TIME) == HealthTrend.DEGRADING:
            predictions.append(HealthPrediction(
                type=PredictionType.PERFORMANCE_DEGRADATION,
                probability=0.7,
                time_horizon=timedelta(days=3),
                affected_metrics=[HealthMetric.BUILD_TIME, HealthMetric.CPU_USAGE],
                recommended_actions=[
                    "Clean build cache",
                    "Review recent configuration changes",
                    "Consider system optimization"
                ],
                confidence=0.65,
                explanation="Build times increasing, system performance may degrade"
            ))
        
        return predictions
    
    def _calculate_risk_score(self, current_health: Dict[HealthMetric, float],
                             predictions: List[HealthPrediction]) -> float:
        """Calculate overall system risk score (0-100)"""
        
        risk_components = []
        
        # Current metric risks
        for metric, value in current_health.items():
            thresholds = self.thresholds.get(metric, {})
            warning = thresholds.get('warning', float('inf'))
            critical = thresholds.get('critical', float('inf'))
            
            if value >= critical:
                risk_components.append(0.9)
            elif value >= warning:
                risk_components.append(0.5)
            else:
                risk_components.append(value / (warning + 0.001) * 0.3)
        
        # Prediction risks
        for prediction in predictions:
            risk_components.append(
                prediction.probability * 0.7
            )
        
        # Calculate weighted average
        if risk_components:
            risk_score = np.mean(risk_components) * 100
        else:
            risk_score = 0.0
        
        return min(100.0, risk_score)
    
    def _identify_optimizations(self, current_health: Dict[HealthMetric, float],
                               trends: Dict[HealthMetric, HealthTrend]) -> List[str]:
        """Identify optimization opportunities"""
        
        optimizations = []
        
        # High resource usage
        if current_health.get(HealthMetric.MEMORY_USAGE, 0) > 70:
            optimizations.append("Consider memory optimization: review running services")
        
        if current_health.get(HealthMetric.DISK_USAGE, 0) > 70:
            optimizations.append("Disk cleanup recommended: run garbage collection")
        
        # Slow builds
        if current_health.get(HealthMetric.BUILD_TIME, 0) > 180:
            optimizations.append("Optimize build process: consider using binary cache")
        
        # Config complexity
        if current_health.get(HealthMetric.CONFIG_COMPLEXITY, 0) > 80:
            optimizations.append("Simplify configuration: consider modularization")
        
        # Security
        if current_health.get(HealthMetric.SECURITY_SCORE, 100) < 80:
            optimizations.append("Security improvements available: run security audit")
        
        return optimizations
    
    def predict_failure_probability(self, metric: HealthMetric, 
                                   horizon_hours: int = 24) -> Tuple[float, str]:
        """Predict probability of failure for a specific metric"""
        
        history = list(self.metric_history[metric])
        
        if len(history) < 10:
            return 0.0, "Insufficient data for prediction"
        
        values = [dp.value for dp in history]
        
        # Simple prediction using linear extrapolation
        model = self.prediction_models.get(metric, {})
        coeffs = model.get('coefficients', [0, 0])
        
        # Project future value
        future_steps = horizon_hours
        projected_value = coeffs[0] * (len(values) + future_steps) + coeffs[1]
        
        # Calculate failure probability
        thresholds = self.thresholds.get(metric, {})
        critical = thresholds.get('critical', float('inf'))
        
        if projected_value >= critical:
            probability = min(0.95, projected_value / critical)
            explanation = f"Projected to reach critical threshold in {horizon_hours} hours"
        elif projected_value >= thresholds.get('warning', float('inf')):
            probability = min(0.5, projected_value / critical)
            explanation = f"May reach warning threshold in {horizon_hours} hours"
        else:
            probability = 0.1
            explanation = "Low risk of failure"
        
        return probability, explanation
    
    def get_correlation_insights(self) -> Dict[str, List[str]]:
        """Get insights about metric correlations"""
        
        insights = {}
        
        # Calculate correlations
        metrics_data = {}
        for metric in HealthMetric:
            history = list(self.metric_history[metric])
            if len(history) >= 20:
                metrics_data[metric] = [dp.value for dp in history[-20:]]
        
        if len(metrics_data) < 2:
            return {"info": ["Insufficient data for correlation analysis"]}
        
        # Find strong correlations
        strong_correlations = []
        
        for m1 in metrics_data:
            for m2 in metrics_data:
                if m1 != m2:
                    corr = np.corrcoef(metrics_data[m1], metrics_data[m2])[0, 1]
                    
                    if abs(corr) > 0.7:
                        strong_correlations.append(
                            f"{m1.value} and {m2.value}: {corr:.2f} correlation"
                        )
        
        if strong_correlations:
            insights["correlations"] = strong_correlations
        
        # Identify patterns
        patterns = []
        
        # High CPU often correlates with build time
        if (HealthMetric.CPU_USAGE in metrics_data and 
            HealthMetric.BUILD_TIME in metrics_data):
            corr = np.corrcoef(
                metrics_data[HealthMetric.CPU_USAGE],
                metrics_data[HealthMetric.BUILD_TIME]
            )[0, 1]
            
            if corr > 0.5:
                patterns.append("Build times increase with CPU usage")
        
        if patterns:
            insights["patterns"] = patterns
        
        return insights
    
    def train_on_historical_data(self, historical_data: List[Dict]) -> bool:
        """Train models on historical data"""
        
        try:
            for record in historical_data:
                metric = HealthMetric(record['metric'])
                value = float(record['value'])
                timestamp = datetime.fromisoformat(record['timestamp'])
                context = record.get('context', {})
                
                datapoint = HealthDataPoint(
                    metric=metric,
                    value=value,
                    timestamp=timestamp,
                    context=context
                )
                
                self.metric_history[metric].append(datapoint)
            
            # Retrain models
            for metric in HealthMetric:
                if len(self.metric_history[metric]) >= 10:
                    self._update_models(metric, self.metric_history[metric][-1])
            
            self.logger.info(f"Trained on {len(historical_data)} historical records")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to train on historical data: {e}")
            return False
    
    def save_models(self) -> bool:
        """Save trained models to disk"""
        
        try:
            models_path = self.model_dir / "health_models.pkl"
            
            models_data = {
                'trend': self.trend_models,
                'anomaly': self.anomaly_models,
                'prediction': self.prediction_models,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(models_path, 'wb') as f:
                pickle.dump(models_data, f)
            
            self.logger.info("Saved ML models to disk")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")
            return False
    
    def generate_health_report(self) -> str:
        """Generate a comprehensive health report"""
        
        profile = self.analyze_current_health()
        
        report = []
        report.append("=" * 60)
        report.append("SYSTEM HEALTH REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {profile.last_updated}")
        report.append(f"Risk Score: {profile.risk_score:.1f}/100")
        report.append("")
        
        # Current metrics
        report.append("CURRENT METRICS:")
        for metric, value in profile.current_health.items():
            trend = profile.trends.get(metric, HealthTrend.STABLE)
            trend_symbol = {
                HealthTrend.IMPROVING: "↑",
                HealthTrend.STABLE: "→",
                HealthTrend.DEGRADING: "↓",
                HealthTrend.CRITICAL: "⚠"
            }.get(trend, "?")
            
            report.append(f"  {metric.value:20} {value:8.2f} {trend_symbol}")
        
        # Predictions
        if profile.predictions:
            report.append("\nPREDICTIONS:")
            for pred in profile.predictions:
                report.append(f"  • {pred.type.value}")
                report.append(f"    Probability: {pred.probability:.1%}")
                report.append(f"    Time horizon: {pred.time_horizon}")
                report.append(f"    {pred.explanation}")
        
        # Optimization opportunities
        if profile.optimization_opportunities:
            report.append("\nOPTIMIZATION OPPORTUNITIES:")
            for opp in profile.optimization_opportunities:
                report.append(f"  • {opp}")
        
        # Correlations
        correlations = self.get_correlation_insights()
        if correlations:
            report.append("\nCORRELATION INSIGHTS:")
            for category, items in correlations.items():
                for item in items:
                    report.append(f"  • {item}")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Test the ML health predictor"""
    
    predictor = MLHealthPredictor()
    
    # Simulate some metrics
    import random
    
    print("Simulating health metrics...")
    for _ in range(50):
        predictor.collect_metric(
            HealthMetric.CPU_USAGE,
            random.uniform(30, 80) + random.gauss(0, 5)
        )
        predictor.collect_metric(
            HealthMetric.MEMORY_USAGE,
            random.uniform(40, 85) + random.gauss(0, 3)
        )
        predictor.collect_metric(
            HealthMetric.ERROR_RATE,
            max(0, random.gauss(2, 1))
        )
    
    # Generate report
    report = predictor.generate_health_report()
    print(report)
    
    # Test predictions
    prob, explanation = predictor.predict_failure_probability(
        HealthMetric.CPU_USAGE,
        horizon_hours=24
    )
    print(f"\nCPU failure probability (24h): {prob:.1%}")
    print(f"Explanation: {explanation}")


if __name__ == "__main__":
    main()