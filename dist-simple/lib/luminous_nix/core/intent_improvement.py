"""Continuous improvement system for intent recognition.

This module provides tools for:
1. Collecting user feedback
2. Analyzing pattern effectiveness
3. Persisting learning data
4. Monitoring performance
5. Suggesting improvements
"""

import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import logging

from .intents import IntentType, Intent

logger = logging.getLogger(__name__)


@dataclass
class IntentFeedback:
    """User feedback on intent recognition."""
    query: str
    recognized_intent: str
    correct_intent: str
    confidence: float
    timestamp: float
    user_satisfaction: Optional[int] = None  # 1-5 scale
    notes: Optional[str] = None


@dataclass
class PatternMetrics:
    """Metrics for a specific pattern."""
    pattern: str
    intent_type: str
    matches: int
    correct: int
    incorrect: int
    avg_confidence: float
    avg_latency_ms: float
    
    @property
    def accuracy(self) -> float:
        total = self.correct + self.incorrect
        return self.correct / total if total > 0 else 0.0
        
    @property
    def performance_score(self) -> float:
        """Combined score considering accuracy and speed."""
        # High accuracy and low latency = high score
        latency_factor = max(0, 1 - (self.avg_latency_ms / 100))  # Penalize >100ms
        return self.accuracy * 0.7 + latency_factor * 0.3


class IntentLearningDatabase:
    """Persistent storage for intent learning data."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize learning database."""
        if db_path is None:
            db_path = Path.home() / ".local/share/luminous-nix/intent_learning.db"
            
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    recognized_intent TEXT NOT NULL,
                    correct_intent TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    user_satisfaction INTEGER,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS corrections (
                    query TEXT PRIMARY KEY,
                    correct_intent TEXT NOT NULL,
                    correction_count INTEGER DEFAULT 1,
                    last_corrected REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_metrics (
                    pattern TEXT PRIMARY KEY,
                    intent_type TEXT NOT NULL,
                    matches INTEGER DEFAULT 0,
                    correct INTEGER DEFAULT 0,
                    incorrect INTEGER DEFAULT 0,
                    total_confidence REAL DEFAULT 0,
                    total_latency_ms REAL DEFAULT 0,
                    last_updated REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    latency_ms REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            
    def add_feedback(self, feedback: IntentFeedback):
        """Store user feedback."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO feedback (
                    query, recognized_intent, correct_intent, 
                    confidence, timestamp, user_satisfaction, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.query,
                feedback.recognized_intent,
                feedback.correct_intent,
                feedback.confidence,
                feedback.timestamp,
                feedback.user_satisfaction,
                feedback.notes
            ))
            
            # Update corrections table if this is a correction
            if feedback.recognized_intent != feedback.correct_intent:
                conn.execute("""
                    INSERT INTO corrections (query, correct_intent, last_corrected)
                    VALUES (?, ?, ?)
                    ON CONFLICT(query) DO UPDATE SET
                        correct_intent = excluded.correct_intent,
                        correction_count = correction_count + 1,
                        last_corrected = excluded.last_corrected
                """, (feedback.query, feedback.correct_intent, feedback.timestamp))
                
    def get_corrections(self) -> Dict[str, str]:
        """Get all learned corrections."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT query, correct_intent FROM corrections
                ORDER BY correction_count DESC
            """)
            return {row[0]: row[1] for row in cursor}
            
    def update_pattern_metrics(self, pattern: str, intent_type: str, 
                              correct: bool, confidence: float, latency_ms: float):
        """Update metrics for a pattern."""
        with sqlite3.connect(self.db_path) as conn:
            if correct:
                conn.execute("""
                    INSERT INTO pattern_metrics (
                        pattern, intent_type, matches, correct, 
                        total_confidence, total_latency_ms, last_updated
                    ) VALUES (?, ?, 1, 1, ?, ?, ?)
                    ON CONFLICT(pattern) DO UPDATE SET
                        matches = matches + 1,
                        correct = correct + 1,
                        total_confidence = total_confidence + excluded.total_confidence,
                        total_latency_ms = total_latency_ms + excluded.total_latency_ms,
                        last_updated = excluded.last_updated
                """, (pattern, intent_type, confidence, latency_ms, time.time()))
            else:
                conn.execute("""
                    INSERT INTO pattern_metrics (
                        pattern, intent_type, matches, incorrect,
                        total_confidence, total_latency_ms, last_updated
                    ) VALUES (?, ?, 1, 1, ?, ?, ?)
                    ON CONFLICT(pattern) DO UPDATE SET
                        matches = matches + 1,
                        incorrect = incorrect + 1,
                        total_confidence = total_confidence + excluded.total_confidence,
                        total_latency_ms = total_latency_ms + excluded.total_latency_ms,
                        last_updated = excluded.last_updated
                """, (pattern, intent_type, confidence, latency_ms, time.time()))
                
    def get_pattern_metrics(self) -> List[PatternMetrics]:
        """Get metrics for all patterns."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT pattern, intent_type, matches, correct, incorrect,
                       total_confidence, total_latency_ms
                FROM pattern_metrics
                ORDER BY matches DESC
            """)
            
            metrics = []
            for row in cursor:
                pattern, intent_type, matches, correct, incorrect, total_conf, total_latency = row
                metrics.append(PatternMetrics(
                    pattern=pattern,
                    intent_type=intent_type,
                    matches=matches,
                    correct=correct,
                    incorrect=incorrect,
                    avg_confidence=total_conf / matches if matches > 0 else 0,
                    avg_latency_ms=total_latency / matches if matches > 0 else 0
                ))
            return metrics
            
    def log_query(self, query: str, intent: str, confidence: float, latency_ms: float):
        """Log a query for analysis."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO query_history (query, intent, confidence, latency_ms, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (query, intent, confidence, latency_ms, time.time()))


class IntentAnalyzer:
    """Analyzes intent recognition patterns and suggests improvements."""
    
    def __init__(self, db: IntentLearningDatabase):
        """Initialize analyzer with database."""
        self.db = db
        
    def analyze_failures(self) -> Dict[str, any]:
        """Analyze recognition failures."""
        with sqlite3.connect(self.db.db_path) as conn:
            # Get feedback where recognized != correct
            cursor = conn.execute("""
                SELECT recognized_intent, correct_intent, COUNT(*) as count
                FROM feedback
                WHERE recognized_intent != correct_intent
                GROUP BY recognized_intent, correct_intent
                ORDER BY count DESC
                LIMIT 10
            """)
            
            confusion_matrix = []
            for row in cursor:
                confusion_matrix.append({
                    'recognized': row[0],
                    'correct': row[1],
                    'count': row[2]
                })
                
            # Get most corrected queries
            cursor = conn.execute("""
                SELECT query, correct_intent, correction_count
                FROM corrections
                ORDER BY correction_count DESC
                LIMIT 10
            """)
            
            most_corrected = []
            for row in cursor:
                most_corrected.append({
                    'query': row[0],
                    'correct_intent': row[1],
                    'corrections': row[2]
                })
                
            return {
                'confusion_matrix': confusion_matrix,
                'most_corrected': most_corrected
            }
            
    def analyze_performance(self) -> Dict[str, any]:
        """Analyze performance metrics."""
        metrics = self.db.get_pattern_metrics()
        
        if not metrics:
            return {'status': 'No data available'}
            
        # Find best and worst performing patterns
        sorted_by_accuracy = sorted(metrics, key=lambda m: m.accuracy)
        sorted_by_speed = sorted(metrics, key=lambda m: m.avg_latency_ms)
        sorted_by_overall = sorted(metrics, key=lambda m: m.performance_score, reverse=True)
        
        return {
            'total_patterns': len(metrics),
            'avg_accuracy': sum(m.accuracy for m in metrics) / len(metrics),
            'avg_latency_ms': sum(m.avg_latency_ms for m in metrics) / len(metrics),
            'best_patterns': [
                {
                    'pattern': m.pattern,
                    'accuracy': m.accuracy,
                    'latency_ms': m.avg_latency_ms,
                    'score': m.performance_score
                }
                for m in sorted_by_overall[:5]
            ],
            'worst_patterns': [
                {
                    'pattern': m.pattern,
                    'accuracy': m.accuracy,
                    'latency_ms': m.avg_latency_ms,
                    'score': m.performance_score
                }
                for m in sorted_by_overall[-5:]
            ],
            'slowest_patterns': [
                {
                    'pattern': m.pattern,
                    'latency_ms': m.avg_latency_ms
                }
                for m in sorted_by_speed[-5:]
            ]
        }
        
    def suggest_improvements(self) -> List[str]:
        """Suggest improvements based on analysis."""
        suggestions = []
        
        # Analyze failures
        failures = self.analyze_failures()
        if failures['confusion_matrix']:
            top_confusion = failures['confusion_matrix'][0]
            suggestions.append(
                f"Pattern confusion: '{top_confusion['recognized']}' is often "
                f"mistaken for '{top_confusion['correct']}' ({top_confusion['count']} times). "
                f"Consider adjusting pattern priority or specificity."
            )
            
        # Analyze performance
        perf = self.analyze_performance()
        if 'avg_accuracy' in perf and perf['avg_accuracy'] < 0.8:
            suggestions.append(
                f"Overall accuracy is {perf['avg_accuracy']:.1%}. "
                f"Consider enabling LLM assistance for ambiguous queries."
            )
            
        if 'worst_patterns' in perf and perf['worst_patterns']:
            worst = perf['worst_patterns'][0]
            suggestions.append(
                f"Pattern '{worst['pattern'][:50]}...' has {worst['accuracy']:.1%} accuracy. "
                f"Consider rewriting or removing this pattern."
            )
            
        if 'slowest_patterns' in perf and perf['slowest_patterns']:
            slowest = perf['slowest_patterns'][0]
            if slowest['latency_ms'] > 10:
                suggestions.append(
                    f"Pattern '{slowest['pattern'][:50]}...' takes {slowest['latency_ms']:.1f}ms. "
                    f"Consider optimizing this regex pattern."
                )
                
        # Check for most corrected queries
        if failures['most_corrected']:
            top_corrected = failures['most_corrected'][0]
            suggestions.append(
                f"Query '{top_corrected['query']}' has been corrected {top_corrected['corrections']} times. "
                f"Add a specific pattern for this query mapping to {top_corrected['correct_intent']}."
            )
            
        return suggestions


class IntentImprovementDashboard:
    """Dashboard for monitoring and improving intent recognition."""
    
    def __init__(self):
        """Initialize dashboard."""
        self.db = IntentLearningDatabase()
        self.analyzer = IntentAnalyzer(self.db)
        
    def get_summary(self) -> Dict[str, any]:
        """Get dashboard summary."""
        with sqlite3.connect(self.db.db_path) as conn:
            # Get basic stats
            feedback_count = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
            correction_count = conn.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
            query_count = conn.execute("SELECT COUNT(*) FROM query_history").fetchone()[0]
            
            # Get recent accuracy
            recent = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN recognized_intent = correct_intent THEN 1 ELSE 0 END) as correct
                FROM feedback
                WHERE timestamp > ?
            """, (time.time() - 86400,)).fetchone()  # Last 24 hours
            
            recent_accuracy = recent[1] / recent[0] if recent[0] > 0 else None
            
        return {
            'stats': {
                'total_feedback': feedback_count,
                'total_corrections': correction_count,
                'total_queries': query_count,
                'recent_accuracy': recent_accuracy
            },
            'failures': self.analyzer.analyze_failures(),
            'performance': self.analyzer.analyze_performance(),
            'suggestions': self.analyzer.suggest_improvements()
        }
        
    def print_dashboard(self):
        """Print a text dashboard to console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print(" Intent Recognition Improvement Dashboard")
        print("="*60)
        
        print("\n📊 Statistics:")
        stats = summary['stats']
        print(f"  Total Feedback: {stats['total_feedback']}")
        print(f"  Total Corrections: {stats['total_corrections']}")
        print(f"  Total Queries: {stats['total_queries']}")
        if stats['recent_accuracy'] is not None:
            print(f"  Recent Accuracy (24h): {stats['recent_accuracy']:.1%}")
            
        print("\n❌ Top Recognition Failures:")
        for item in summary['failures']['confusion_matrix'][:3]:
            print(f"  {item['recognized']} → {item['correct']} ({item['count']} times)")
            
        print("\n📈 Performance Metrics:")
        perf = summary['performance']
        if 'avg_accuracy' in perf:
            print(f"  Average Accuracy: {perf['avg_accuracy']:.1%}")
            print(f"  Average Latency: {perf['avg_latency_ms']:.1f}ms")
            
        print("\n💡 Improvement Suggestions:")
        for i, suggestion in enumerate(summary['suggestions'][:3], 1):
            print(f"  {i}. {suggestion}")
            
        print("\n" + "="*60)