#!/usr/bin/env python3
"""
📊 Pattern Analysis Dashboard for UI Evolution
Visualizes usage patterns and provides optimization insights
"""

import json
import time
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
import sys

sys.path.insert(0, str(Path(__file__).parent))

from error_handler import (
    safe_database_operation,
    get_logger,
    error_collector
)

from learning_persistence import LearningDatabase
from performance_monitor import PerformanceMonitor
from feedback_collection_system import FeedbackCollector, FeedbackType
from ab_testing_framework import ABTestingEngine, VariationType


@dataclass
class UsagePattern:
    """Represents a detected usage pattern"""
    
    id: str
    name: str
    description: str
    pattern_type: str  # workflow, feature, navigation, etc.
    frequency: int
    confidence: float  # 0-1 confidence in pattern detection
    
    # Pattern details
    sequence: List[str]  # Sequence of actions
    users_affected: int
    time_frame: str  # daily, weekly, monthly
    
    # Pattern metrics
    avg_completion_time: float
    success_rate: float
    abandonment_points: List[str]
    
    # Optimization potential
    optimization_score: float  # 0-1, higher = more potential
    suggested_improvements: List[str]


@dataclass
class TrendAnalysis:
    """Analysis of trends over time"""
    
    metric_name: str
    direction: str  # increasing, decreasing, stable
    change_rate: float  # percentage per time period
    confidence: float
    
    # Data points
    time_series: List[Tuple[datetime, float]]
    
    # Statistical analysis
    mean: float
    std_dev: float
    median: float
    
    # Predictions
    next_period_prediction: float
    confidence_interval: Tuple[float, float]


@dataclass
class InsightReport:
    """Actionable insight from pattern analysis"""
    
    id: str
    title: str
    description: str
    category: str  # ux, performance, adoption, engagement
    priority: str  # high, medium, low
    
    # Supporting data
    evidence: List[Dict[str, Any]]
    confidence: float
    
    # Recommendations
    recommendations: List[str]
    expected_impact: str
    implementation_effort: str  # low, medium, high
    
    # Tracking
    created_at: datetime
    acknowledged: bool = False
    implemented: bool = False


class PatternAnalyzer:
    """Main pattern analysis engine"""
    
    def __init__(self):
        self.learning_db = LearningDatabase()
        self.performance_monitor = PerformanceMonitor()
        self.feedback_collector = FeedbackCollector()
        self.ab_testing = ABTestingEngine()
        
        # Storage for patterns and insights
        self.detected_patterns: List[UsagePattern] = []
        self.trend_analyses: List[TrendAnalysis] = []
        self.insights: List[InsightReport] = []
        
        # Analysis configuration
        self.min_pattern_frequency = 3  # Minimum occurrences to be a pattern
        self.confidence_threshold = 0.7  # Minimum confidence to report
        self.analysis_window_days = 30  # Look back period
        
        # Initialize database tables
        self._init_database()
    
    def _init_database(self):
        """Initialize pattern storage in database"""
        
        cursor = self.learning_db.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_patterns (
                id TEXT PRIMARY KEY,
                name TEXT,
                pattern_type TEXT,
                sequence TEXT,
                frequency INTEGER,
                confidence REAL,
                users_affected INTEGER,
                avg_completion_time REAL,
                success_rate REAL,
                optimization_score REAL,
                detected_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                category TEXT,
                priority TEXT,
                confidence REAL,
                evidence TEXT,
                recommendations TEXT,
                created_at TEXT,
                acknowledged BOOLEAN,
                implemented BOOLEAN
            )
        """)
        
        # Create tables for demo analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface_type TEXT,
                action_sequence TEXT,
                completion_time REAL,
                success BOOLEAN,
                timestamp TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interface_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                components_used TEXT,
                satisfaction_score REAL,
                timestamp TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                navigation_path TEXT,
                total_time REAL,
                started_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT,
                interface_context TEXT,
                timestamp TEXT
            )
        """)
        
        self.learning_db.conn.commit()
    
    def analyze_usage_patterns(self) -> List[UsagePattern]:
        """Analyze and detect usage patterns"""
        
        patterns = []
        
        # Analyze workflow patterns
        workflow_patterns = self._analyze_workflow_patterns()
        patterns.extend(workflow_patterns)
        
        # Analyze feature usage patterns
        feature_patterns = self._analyze_feature_patterns()
        patterns.extend(feature_patterns)
        
        # Analyze navigation patterns
        nav_patterns = self._analyze_navigation_patterns()
        patterns.extend(nav_patterns)
        
        # Analyze error patterns
        error_patterns = self._analyze_error_patterns()
        patterns.extend(error_patterns)
        
        # Filter by confidence
        patterns = [p for p in patterns if p.confidence >= self.confidence_threshold]
        
        # Store detected patterns
        self.detected_patterns = patterns
        self._store_patterns(patterns)
        
        return patterns
    
    @safe_database_operation(default_return=[])
    def _analyze_workflow_patterns(self) -> List[UsagePattern]:
        """Detect common workflow patterns"""
        
        patterns = []
        logger = get_logger(__name__)
        
        try:
            # Query interaction sequences from database
            cursor = self.learning_db.conn.cursor()
            cursor.execute("""
                SELECT interface_type, action_sequence, COUNT(*) as frequency,
                       AVG(completion_time) as avg_time, AVG(success) as success_rate
                FROM user_interactions
                WHERE timestamp > datetime('now', '-30 days')
                GROUP BY interface_type, action_sequence
                HAVING frequency >= ?
            """, (self.min_pattern_frequency,))
            
            for row in cursor.fetchall():
                if row[1]:  # If action_sequence exists
                    try:
                        sequence = json.loads(row[1]) if row[1].startswith('[') else [row[1]]
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in action_sequence: {row[1]}")
                        sequence = [row[1]]
                    
                    pattern = UsagePattern(
                        id=f"workflow_{hash(row[0] + row[1])}",
                        name=f"Common {row[0]} Workflow",
                        description=f"Frequently used workflow in {row[0]}",
                        pattern_type="workflow",
                        frequency=row[2],
                        confidence=min(1.0, row[2] / 10),  # Higher frequency = higher confidence
                        sequence=sequence,
                        users_affected=row[2],  # Approximate
                        time_frame="monthly",
                        avg_completion_time=row[3] or 0,
                        success_rate=row[4] or 0,
                        abandonment_points=[],
                        optimization_score=self._calculate_optimization_score(row[4], row[3]),
                        suggested_improvements=[]
                    )
                    
                    patterns.append(pattern)
        except Exception as e:
            logger.error(f"Failed to analyze workflow patterns: {e}")
            error_collector.add_error(
                "pattern_analysis_error",
                str(e),
                {"pattern_type": "workflow"}
            )
        
        return patterns
    
    def _analyze_feature_patterns(self) -> List[UsagePattern]:
        """Detect feature usage patterns"""
        
        patterns = []
        
        # Analyze which features are used together
        cursor = self.learning_db.conn.cursor()
        cursor.execute("""
            SELECT components_used, COUNT(*) as frequency,
                   AVG(satisfaction_score) as avg_satisfaction
            FROM interface_interactions
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY components_used
            HAVING frequency >= ?
        """, (self.min_pattern_frequency,))
        
        for row in cursor.fetchall():
            if row[0]:
                components = json.loads(row[0]) if row[0].startswith('[') else [row[0]]
                
                pattern = UsagePattern(
                    id=f"feature_{hash(row[0])}",
                    name="Feature Combination Pattern",
                    description=f"Common feature combination: {', '.join(components[:3])}",
                    pattern_type="feature",
                    frequency=row[1],
                    confidence=min(1.0, row[1] / 10),
                    sequence=components,
                    users_affected=row[1],
                    time_frame="monthly",
                    avg_completion_time=0,
                    success_rate=row[2] / 5 if row[2] else 0,  # Convert satisfaction to success
                    abandonment_points=[],
                    optimization_score=self._calculate_feature_optimization_score(row[2]),
                    suggested_improvements=self._suggest_feature_improvements(components)
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_navigation_patterns(self) -> List[UsagePattern]:
        """Detect navigation patterns"""
        
        patterns = []
        
        # Analyze navigation sequences
        cursor = self.learning_db.conn.cursor()
        cursor.execute("""
            SELECT navigation_path, COUNT(*) as frequency,
                   AVG(total_time) as avg_time
            FROM user_sessions
            WHERE started_at > datetime('now', '-30 days')
            GROUP BY navigation_path
            HAVING frequency >= ?
        """, (self.min_pattern_frequency,))
        
        for row in cursor.fetchall():
            if row[0]:
                path = json.loads(row[0]) if row[0].startswith('[') else row[0].split('->')
                
                pattern = UsagePattern(
                    id=f"nav_{hash(row[0])}",
                    name="Navigation Pattern",
                    description=f"Common path: {' → '.join(path[:3])}",
                    pattern_type="navigation",
                    frequency=row[1],
                    confidence=min(1.0, row[1] / 10),
                    sequence=path,
                    users_affected=row[1],
                    time_frame="monthly",
                    avg_completion_time=row[2] or 0,
                    success_rate=1.0,  # Navigation typically succeeds
                    abandonment_points=self._find_abandonment_points(path),
                    optimization_score=self._calculate_nav_optimization_score(row[2], len(path)),
                    suggested_improvements=self._suggest_nav_improvements(path)
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_error_patterns(self) -> List[UsagePattern]:
        """Detect error patterns"""
        
        patterns = []
        
        # Analyze common error sequences
        cursor = self.learning_db.conn.cursor()
        cursor.execute("""
            SELECT error_type, interface_context, COUNT(*) as frequency
            FROM error_logs
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY error_type, interface_context
            HAVING frequency >= ?
        """, (self.min_pattern_frequency,))
        
        for row in cursor.fetchall():
            pattern = UsagePattern(
                id=f"error_{hash(row[0] + row[1])}",
                name=f"Error Pattern: {row[0]}",
                description=f"Recurring error in {row[1]}",
                pattern_type="error",
                frequency=row[2],
                confidence=min(1.0, row[2] / 5),  # Errors need less frequency
                sequence=[row[0], row[1]],
                users_affected=row[2],
                time_frame="monthly",
                avg_completion_time=0,
                success_rate=0,  # Errors mean failure
                abandonment_points=[row[1]],  # Where error occurs
                optimization_score=1.0,  # Errors always need fixing
                suggested_improvements=[f"Fix {row[0]} in {row[1]}"]
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def analyze_trends(self) -> List[TrendAnalysis]:
        """Analyze trends over time"""
        
        trends = []
        
        # Analyze key metrics over time
        metrics_to_analyze = [
            "user_engagement",
            "task_completion_rate",
            "average_satisfaction",
            "error_rate",
            "performance_score"
        ]
        
        for metric in metrics_to_analyze:
            trend = self._analyze_metric_trend(metric)
            if trend:
                trends.append(trend)
        
        self.trend_analyses = trends
        return trends
    
    def _analyze_metric_trend(self, metric_name: str) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific metric"""
        
        # Get time series data
        time_series = self._get_metric_time_series(metric_name)
        
        if len(time_series) < 3:
            return None  # Not enough data
        
        # Calculate statistics
        values = [v for _, v in time_series]
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        median_val = statistics.median(values)
        
        # Determine trend direction
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_mean = statistics.mean(first_half)
        second_mean = statistics.mean(second_half)
        
        change_rate = ((second_mean - first_mean) / first_mean * 100) if first_mean > 0 else 0
        
        if change_rate > 5:
            direction = "increasing"
        elif change_rate < -5:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # Simple prediction (linear extrapolation)
        if len(values) >= 2:
            recent_change = values[-1] - values[-2]
            prediction = values[-1] + recent_change
        else:
            prediction = mean_val
        
        # Confidence interval (simplified)
        confidence_margin = std_dev * 1.96  # 95% confidence
        confidence_interval = (
            prediction - confidence_margin,
            prediction + confidence_margin
        )
        
        return TrendAnalysis(
            metric_name=metric_name,
            direction=direction,
            change_rate=change_rate,
            confidence=min(1.0, len(values) / 30),  # More data = higher confidence
            time_series=time_series,
            mean=mean_val,
            std_dev=std_dev,
            median=median_val,
            next_period_prediction=prediction,
            confidence_interval=confidence_interval
        )
    
    def generate_insights(self) -> List[InsightReport]:
        """Generate actionable insights from patterns and trends"""
        
        insights = []
        
        # Insights from usage patterns
        for pattern in self.detected_patterns:
            if pattern.optimization_score > 0.7:
                insight = self._create_pattern_insight(pattern)
                if insight:
                    insights.append(insight)
        
        # Insights from trends
        for trend in self.trend_analyses:
            if abs(trend.change_rate) > 10:  # Significant change
                insight = self._create_trend_insight(trend)
                if insight:
                    insights.append(insight)
        
        # Insights from A/B tests
        ab_insights = self._generate_ab_insights()
        insights.extend(ab_insights)
        
        # Insights from feedback
        feedback_insights = self._generate_feedback_insights()
        insights.extend(feedback_insights)
        
        # Prioritize insights
        insights.sort(key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}[x.priority],
            x.confidence
        ), reverse=True)
        
        self.insights = insights
        self._store_insights(insights)
        
        return insights
    
    def _create_pattern_insight(self, pattern: UsagePattern) -> Optional[InsightReport]:
        """Create insight from usage pattern"""
        
        if pattern.pattern_type == "workflow" and pattern.success_rate < 0.7:
            return InsightReport(
                id=f"insight_workflow_{pattern.id}",
                title=f"Optimize {pattern.name}",
                description=f"This workflow has a {pattern.success_rate:.1%} success rate and could be improved",
                category="ux",
                priority="high" if pattern.frequency > 10 else "medium",
                evidence=[{
                    "pattern_id": pattern.id,
                    "frequency": pattern.frequency,
                    "success_rate": pattern.success_rate
                }],
                confidence=pattern.confidence,
                recommendations=pattern.suggested_improvements or [
                    "Simplify the workflow",
                    "Add clearer instructions",
                    "Reduce the number of steps"
                ],
                expected_impact=f"Could improve success rate by {(1-pattern.success_rate)*0.5:.0%}",
                implementation_effort="medium",
                created_at=datetime.now()
            )
        
        elif pattern.pattern_type == "error":
            return InsightReport(
                id=f"insight_error_{pattern.id}",
                title=f"Fix Recurring Error: {pattern.name}",
                description=pattern.description,
                category="performance",
                priority="high",
                evidence=[{
                    "pattern_id": pattern.id,
                    "frequency": pattern.frequency,
                    "users_affected": pattern.users_affected
                }],
                confidence=pattern.confidence,
                recommendations=pattern.suggested_improvements,
                expected_impact="Eliminate errors for affected users",
                implementation_effort="low",
                created_at=datetime.now()
            )
        
        return None
    
    def _create_trend_insight(self, trend: TrendAnalysis) -> Optional[InsightReport]:
        """Create insight from trend analysis"""
        
        if trend.metric_name == "error_rate" and trend.direction == "increasing":
            return InsightReport(
                id=f"insight_trend_errors",
                title="Rising Error Rate Detected",
                description=f"Error rate has increased by {trend.change_rate:.1f}% recently",
                category="performance",
                priority="high",
                evidence=[{
                    "metric": trend.metric_name,
                    "change_rate": trend.change_rate,
                    "current_value": trend.time_series[-1][1] if trend.time_series else 0
                }],
                confidence=trend.confidence,
                recommendations=[
                    "Investigate recent changes",
                    "Add more error handling",
                    "Improve validation"
                ],
                expected_impact="Reduce errors to previous levels",
                implementation_effort="medium",
                created_at=datetime.now()
            )
        
        elif trend.metric_name == "user_engagement" and trend.direction == "decreasing":
            return InsightReport(
                id=f"insight_trend_engagement",
                title="Declining User Engagement",
                description=f"User engagement has decreased by {abs(trend.change_rate):.1f}%",
                category="engagement",
                priority="high",
                evidence=[{
                    "metric": trend.metric_name,
                    "change_rate": trend.change_rate,
                    "prediction": trend.next_period_prediction
                }],
                confidence=trend.confidence,
                recommendations=[
                    "Survey users for feedback",
                    "Simplify onboarding",
                    "Add engaging features"
                ],
                expected_impact="Restore engagement levels",
                implementation_effort="high",
                created_at=datetime.now()
            )
        
        return None
    
    def _generate_ab_insights(self) -> List[InsightReport]:
        """Generate insights from A/B testing"""
        
        insights = []
        recommendations = self.ab_testing.get_optimization_recommendations()
        
        for rec in recommendations:
            insight = InsightReport(
                id=f"insight_ab_{rec['type']}",
                title=f"A/B Test Winner: {rec['recommendation']}",
                description=rec['reason'],
                category="ux",
                priority="medium",
                evidence=[{
                    "test_type": rec['type'],
                    "confidence": rec['confidence'],
                    "parameters": rec['parameters']
                }],
                confidence=rec['confidence'],
                recommendations=[rec['recommendation']],
                expected_impact=rec['reason'],
                implementation_effort="low",
                created_at=datetime.now()
            )
            insights.append(insight)
        
        return insights
    
    def _generate_feedback_insights(self) -> List[InsightReport]:
        """Generate insights from user feedback"""
        
        insights = []
        summary = self.feedback_collector.get_feedback_summary()
        
        if summary['average_sentiment'] < 0:
            insight = InsightReport(
                id="insight_feedback_negative",
                title="Negative User Sentiment",
                description=f"Average user sentiment is {summary['average_sentiment']:.2f}",
                category="ux",
                priority="high",
                evidence=[{
                    "average_sentiment": summary['average_sentiment'],
                    "total_feedback": summary['total_feedback']
                }],
                confidence=min(1.0, summary['total_feedback'] / 100),
                recommendations=[
                    "Review negative feedback",
                    "Identify pain points",
                    "Implement quick wins"
                ],
                expected_impact="Improve user satisfaction",
                implementation_effort="medium",
                created_at=datetime.now()
            )
            insights.append(insight)
        
        if summary['task_completion_rate'] < 0.7:
            insight = InsightReport(
                id="insight_feedback_completion",
                title="Low Task Completion Rate",
                description=f"Only {summary['task_completion_rate']:.1%} of tasks are completed",
                category="ux",
                priority="high",
                evidence=[{
                    "completion_rate": summary['task_completion_rate']
                }],
                confidence=0.9,
                recommendations=[
                    "Simplify task flows",
                    "Add progress indicators",
                    "Provide better guidance"
                ],
                expected_impact="Increase completion by 20%",
                implementation_effort="medium",
                created_at=datetime.now()
            )
            insights.append(insight)
        
        return insights
    
    def _calculate_optimization_score(self, success_rate: float, completion_time: float) -> float:
        """Calculate optimization potential score"""
        
        # Lower success rate = higher optimization potential
        success_factor = 1 - (success_rate or 0)
        
        # Longer completion time = higher optimization potential
        time_factor = min(1.0, (completion_time or 0) / 60)  # Normalize to 60 seconds
        
        return (success_factor * 0.7 + time_factor * 0.3)
    
    def _calculate_feature_optimization_score(self, satisfaction: float) -> float:
        """Calculate feature optimization score"""
        if satisfaction is None:
            return 0.5
        return 1 - (satisfaction / 5)  # Lower satisfaction = higher potential
    
    def _calculate_nav_optimization_score(self, time: float, steps: int) -> float:
        """Calculate navigation optimization score"""
        # More steps and time = higher optimization potential
        return min(1.0, (steps / 10) * 0.5 + (time / 30) * 0.5)
    
    def _suggest_feature_improvements(self, components: List[str]) -> List[str]:
        """Suggest improvements for feature combinations"""
        suggestions = []
        
        if len(components) > 5:
            suggestions.append("Consider breaking into smaller interfaces")
        
        if "search" in str(components).lower() and "filter" not in str(components).lower():
            suggestions.append("Add filtering capabilities")
        
        if "list" in str(components).lower() and "pagination" not in str(components).lower():
            suggestions.append("Add pagination for large lists")
        
        return suggestions
    
    def _suggest_nav_improvements(self, path: List[str]) -> List[str]:
        """Suggest navigation improvements"""
        suggestions = []
        
        if len(path) > 3:
            suggestions.append("Add shortcuts to reduce navigation depth")
        
        if path[0] == path[-1]:
            suggestions.append("User returned to start - consider adding direct navigation")
        
        return suggestions
    
    def _find_abandonment_points(self, path: List[str]) -> List[str]:
        """Find where users typically abandon"""
        # Simplified - in reality would analyze incomplete sessions
        if len(path) > 5:
            return [path[len(path)//2]]  # Middle point as example
        return []
    
    def _get_metric_time_series(self, metric_name: str) -> List[Tuple[datetime, float]]:
        """Get time series data for a metric"""
        # This would query actual metric data
        # For demo, generate sample data
        
        time_series = []
        now = datetime.now()
        
        for i in range(30):
            date = now - timedelta(days=30-i)
            
            if metric_name == "user_engagement":
                value = 0.7 + (i/30) * 0.1  # Increasing trend
            elif metric_name == "task_completion_rate":
                value = 0.8 - (i/30) * 0.05  # Decreasing trend
            elif metric_name == "average_satisfaction":
                value = 3.5 + (i/30) * 0.3  # Increasing
            elif metric_name == "error_rate":
                value = 0.05 + (i/30) * 0.02  # Increasing (bad)
            else:
                value = 0.5  # Stable
            
            time_series.append((date, value))
        
        return time_series
    
    @safe_database_operation(default_return=None)
    def _store_patterns(self, patterns: List[UsagePattern]):
        """Store detected patterns in database"""
        
        logger = get_logger(__name__)
        cursor = self.learning_db.conn.cursor()
        
        for pattern in patterns:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO usage_patterns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.id,
                    pattern.name,
                    pattern.pattern_type,
                    json.dumps(pattern.sequence),
                    pattern.frequency,
                    pattern.confidence,
                    pattern.users_affected,
                    pattern.avg_completion_time,
                    pattern.success_rate,
                    pattern.optimization_score,
                    datetime.now().isoformat()
                ))
            except Exception as e:
                logger.error(f"Failed to store pattern {pattern.id}: {e}")
                error_collector.add_error(
                    "pattern_storage_error",
                    str(e),
                    {"pattern_id": pattern.id}
                )
        
        try:
            self.learning_db.conn.commit()
        except Exception as e:
            logger.error(f"Failed to commit patterns: {e}")
            self.learning_db.conn.rollback()
    
    @safe_database_operation(default_return=None)
    def _store_insights(self, insights: List[InsightReport]):
        """Store insights in database"""
        
        logger = get_logger(__name__)
        cursor = self.learning_db.conn.cursor()
        
        for insight in insights:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO insights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    insight.id,
                    insight.title,
                    insight.description,
                    insight.category,
                    insight.priority,
                    insight.confidence,
                    json.dumps(insight.evidence),
                    json.dumps(insight.recommendations),
                    insight.created_at.isoformat(),
                    insight.acknowledged,
                    insight.implemented
                ))
            except Exception as e:
                logger.error(f"Failed to store insight {insight.id}: {e}")
                error_collector.add_error(
                    "insight_storage_error",
                    str(e),
                    {"insight_id": insight.id}
                )
        
        try:
            self.learning_db.conn.commit()
        except Exception as e:
            logger.error(f"Failed to commit insights: {e}")
            self.learning_db.conn.rollback()
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for dashboard visualization"""
        
        logger = get_logger(__name__)
        
        # Run analyses with error handling
        try:
            patterns = self.analyze_usage_patterns()
        except Exception as e:
            logger.error(f"Failed to analyze patterns: {e}")
            patterns = []
        
        try:
            trends = self.analyze_trends()
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            trends = []
        
        try:
            insights = self.generate_insights()
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            insights = []
        
        # Get current metrics with error handling
        try:
            feedback_summary = self.feedback_collector.get_feedback_summary()
        except Exception as e:
            logger.error(f"Failed to get feedback summary: {e}")
            feedback_summary = {"average_sentiment": 0, "task_completion_rate": 0, "total_feedback": 0}
        
        try:
            performance_metrics = self.performance_monitor.calculate_summary()
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            performance_metrics = {"avg_generation_time": 0}
        
        ab_results = []
        try:
            for test_id in self.ab_testing.active_tests:
                ab_results.append(self.ab_testing.get_test_results(test_id))
        except Exception as e:
            logger.error(f"Failed to get A/B test results: {e}")
        
        return {
            "overview": {
                "total_patterns": len(patterns),
                "total_insights": len(insights),
                "high_priority_insights": len([i for i in insights if i.priority == "high"]),
                "active_ab_tests": len(self.ab_testing.active_tests)
            },
            "patterns": [
                {
                    "name": p.name,
                    "type": p.pattern_type,
                    "frequency": p.frequency,
                    "confidence": p.confidence,
                    "optimization_score": p.optimization_score,
                    "success_rate": p.success_rate
                }
                for p in patterns[:10]  # Top 10
            ],
            "trends": [
                {
                    "metric": t.metric_name,
                    "direction": t.direction,
                    "change_rate": t.change_rate,
                    "current_value": t.time_series[-1][1] if t.time_series else 0,
                    "prediction": t.next_period_prediction
                }
                for t in trends
            ],
            "insights": [
                {
                    "title": i.title,
                    "category": i.category,
                    "priority": i.priority,
                    "confidence": i.confidence,
                    "impact": i.expected_impact,
                    "effort": i.implementation_effort
                }
                for i in insights[:5]  # Top 5
            ],
            "metrics": {
                "user_satisfaction": feedback_summary.get("average_sentiment", 0),
                "task_completion": feedback_summary.get("task_completion_rate", 0),
                "avg_generation_time": performance_metrics.get("avg_generation_time", 0),
                "total_feedback": feedback_summary.get("total_feedback", 0)
            },
            "ab_tests": ab_results[:3]  # Top 3 active tests
        }


def demo_pattern_analysis():
    """Demonstrate pattern analysis dashboard"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        📊 PATTERN ANALYSIS DASHBOARD DEMO                          ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    analyzer = PatternAnalyzer()
    
    # Generate dashboard data
    print("\n🔍 Analyzing Patterns...")
    dashboard_data = analyzer.generate_dashboard_data()
    
    # Display overview
    print("\n📈 DASHBOARD OVERVIEW")
    print("-" * 60)
    overview = dashboard_data["overview"]
    print(f"   Total Patterns Detected: {overview['total_patterns']}")
    print(f"   Insights Generated: {overview['total_insights']}")
    print(f"   High Priority Issues: {overview['high_priority_insights']}")
    print(f"   Active A/B Tests: {overview['active_ab_tests']}")
    
    # Display top patterns
    if dashboard_data["patterns"]:
        print("\n🔄 TOP USAGE PATTERNS")
        print("-" * 60)
        for pattern in dashboard_data["patterns"][:5]:
            print(f"\n   📌 {pattern['name']}")
            print(f"      Type: {pattern['type']}")
            print(f"      Frequency: {pattern['frequency']} occurrences")
            print(f"      Success Rate: {pattern['success_rate']:.1%}")
            print(f"      Optimization Potential: {pattern['optimization_score']:.1%}")
    
    # Display trends
    if dashboard_data["trends"]:
        print("\n📊 KEY TRENDS")
        print("-" * 60)
        for trend in dashboard_data["trends"]:
            arrow = "↗️" if trend["direction"] == "increasing" else "↘️" if trend["direction"] == "decreasing" else "→"
            print(f"\n   {arrow} {trend['metric'].replace('_', ' ').title()}")
            print(f"      Direction: {trend['direction']}")
            print(f"      Change Rate: {trend['change_rate']:+.1f}%")
            print(f"      Current: {trend['current_value']:.2f}")
            print(f"      Predicted: {trend['prediction']:.2f}")
    
    # Display insights
    if dashboard_data["insights"]:
        print("\n💡 TOP INSIGHTS & RECOMMENDATIONS")
        print("-" * 60)
        for insight in dashboard_data["insights"]:
            priority_icon = "🔴" if insight["priority"] == "high" else "🟡" if insight["priority"] == "medium" else "🟢"
            print(f"\n   {priority_icon} {insight['title']}")
            print(f"      Category: {insight['category']}")
            print(f"      Expected Impact: {insight['impact']}")
            print(f"      Implementation Effort: {insight['effort']}")
            print(f"      Confidence: {insight['confidence']:.0%}")
    
    # Display current metrics
    print("\n📊 CURRENT METRICS")
    print("-" * 60)
    metrics = dashboard_data["metrics"]
    print(f"   User Satisfaction: {metrics['user_satisfaction']:.2f}")
    print(f"   Task Completion: {metrics['task_completion']:.1%}")
    print(f"   Avg Generation Time: {metrics['avg_generation_time']:.0f}ms")
    print(f"   Total Feedback: {metrics['total_feedback']}")
    
    print("""

═══════════════════════════════════════════════════════════════════════
✨ Pattern Analysis Dashboard Features:

1. Pattern Detection:
   • Workflow patterns
   • Feature usage patterns
   • Navigation patterns
   • Error patterns

2. Trend Analysis:
   • Time series analysis
   • Statistical predictions
   • Change detection
   • Confidence intervals

3. Insight Generation:
   • Actionable recommendations
   • Priority scoring
   • Impact assessment
   • Implementation effort

4. Dashboard Visualization:
   • Real-time metrics
   • Pattern visualization
   • Trend charts
   • A/B test results

5. Optimization Guidance:
   • Success rate improvement
   • Performance optimization
   • UX enhancements
   • Error reduction

Next Steps:
• Connect to real usage data
• Add machine learning models
• Create interactive visualizations
• Implement automated optimizations
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_pattern_analysis()