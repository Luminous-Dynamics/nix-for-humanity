"""
from typing import List
Digital Wellbeing Score - Replacing engagement metrics with wellness

This implements the research insight that we should optimize for human
wellbeing, not engagement time or click-through rates.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


@dataclass
class WellbeingFactors:
    """Factors contributing to digital wellbeing"""
    flow_time: float  # Time spent in flow state (0-1)
    interruption_rate: float  # How often interrupted (inverse: 1 = never)
    task_completion: float  # Percentage of tasks completed
    learning_progress: float  # Growth in understanding
    stress_level: float  # Inverse of stress (1 = no stress)
    autonomy_preserved: float  # User control maintained
    rest_quality: float  # Quality of breaks taken


class DigitalWellbeingScore:
    """
    Calculates and tracks digital wellbeing instead of engagement
    
    Key principles from research:
    1. Flow state is more valuable than time spent
    2. Task completion matters more than feature usage
    3. Learning indicates healthy interaction
    4. Rest is as important as activity
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg
        
        # Wellbeing component weights
        self.weights = {
            'flow_time': 0.25,
            'interruption_rate': 0.15,
            'task_completion': 0.20,
            'learning_progress': 0.15,
            'stress_level': 0.10,
            'autonomy_preserved': 0.10,
            'rest_quality': 0.05
        }
        
        # History tracking
        self.wellbeing_history = []
        
        # Thresholds for wellbeing states
        self.thresholds = {
            'thriving': 0.8,
            'healthy': 0.6,
            'strained': 0.4,
            'depleted': 0.2
        }
        
    def calculate_wellbeing_score(self, session_data: Dict) -> Dict:
        """
        Calculate overall digital wellbeing score
        
        Returns score and detailed breakdown
        """
        # Extract or calculate individual factors
        factors = self._calculate_factors(session_data)
        
        # Calculate weighted score
        overall_score = sum(
            self.weights[factor] * value
            for factor, value in asdict(factors).items()
        )
        
        # Determine wellbeing state
        state = self._determine_wellbeing_state(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(factors, state)
        
        # Create wellbeing report
        report = {
            'score': overall_score,
            'state': state,
            'factors': asdict(factors),
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
        # Record in history and SKG
        self._record_wellbeing(report)
        
        return report
        
    def _calculate_factors(self, session_data: Dict) -> WellbeingFactors:
        """Calculate individual wellbeing factors from session data"""
        # Flow time calculation
        flow_time = self._calculate_flow_time(session_data)
        
        # Interruption rate (inverse)
        interruptions = session_data.get('interruptions', 0)
        session_duration = session_data.get('duration_minutes', 1)
        interruption_rate = 1 - min(1.0, interruptions / (session_duration / 10))
        
        # Task completion rate
        tasks_started = session_data.get('tasks_started', 1)
        tasks_completed = session_data.get('tasks_completed', 0)
        task_completion = tasks_completed / max(1, tasks_started)
        
        # Learning progress from SKG
        learning_progress = self._assess_learning_progress()
        
        # Stress level (inverse of stress indicators)
        stress_indicators = self._get_stress_indicators()
        stress_level = 1 - stress_indicators
        
        # Autonomy preservation
        forced_actions = session_data.get('forced_actions', 0)
        user_choices = session_data.get('user_choices', 1)
        autonomy_preserved = user_choices / max(1, user_choices + forced_actions)
        
        # Rest quality
        rest_quality = self._assess_rest_quality(session_data)
        
        return WellbeingFactors(
            flow_time=flow_time,
            interruption_rate=interruption_rate,
            task_completion=task_completion,
            learning_progress=learning_progress,
            stress_level=stress_level,
            autonomy_preserved=autonomy_preserved,
            rest_quality=rest_quality
        )
        
    def _calculate_flow_time(self, session_data: Dict) -> float:
        """Calculate proportion of time spent in flow state"""
        cursor = self.skg.conn.cursor()
        
        # Get flow state periods from phenomenological layer
        flow_periods = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'phenomenological'
            AND type = 'cognitive_state'
            AND json_extract(properties, '$.flow_level') > 0.7
            AND created_at > datetime('now', '-1 day')
            ORDER BY created_at
        """).fetchall()
        
        if not flow_periods:
            return 0.0
            
        # Calculate total flow time
        flow_minutes = 0
        for i in range(len(flow_periods) - 1):
            # Estimate duration between flow states
            flow_minutes += 5  # Assume 5 minutes per flow period
            
        total_minutes = session_data.get('duration_minutes', 60)
        return min(1.0, flow_minutes / total_minutes)
        
    def _assess_learning_progress(self) -> float:
        """Assess learning progress from knowledge graph"""
        trajectory = self.skg.phenomenological.get_learning_trajectory()
        
        if not trajectory:
            return 0.5
            
        # Count recent mastery events
        recent_mastery = sum(
            1 for event in trajectory[-20:]
            if event['type'] == 'mastery_milestone'
        )
        
        # Learning progress is ratio of mastery to total events
        return min(1.0, recent_mastery / 10)  # Cap at 10 mastery events
        
    def _get_stress_indicators(self) -> float:
        """Get stress level from current user state"""
        user_state = self.skg.phenomenological.get_current_user_state()
        
        frustration = user_state.get('frustration_level', 0)
        cognitive_load = user_state.get('cognitive_load', 0)
        
        # Combine stress indicators
        stress = (frustration * 0.6 + cognitive_load * 0.4)
        return min(1.0, stress)
        
    def _assess_rest_quality(self, session_data: Dict) -> float:
        """Assess quality of rest and breaks"""
        breaks_taken = session_data.get('breaks_taken', 0)
        break_duration = session_data.get('total_break_minutes', 0)
        session_duration = session_data.get('duration_minutes', 60)
        
        # Ideal break ratio is ~10-15% of session time
        ideal_break_time = session_duration * 0.125
        
        if break_duration == 0:
            return 0.0
            
        # Quality based on duration and frequency
        duration_quality = min(1.0, break_duration / ideal_break_time)
        frequency_quality = min(1.0, breaks_taken / (session_duration / 60))  # One per hour
        
        return (duration_quality + frequency_quality) / 2
        
    def _determine_wellbeing_state(self, score: float) -> str:
        """Determine wellbeing state from score"""
        if score >= self.thresholds['thriving']:
            return 'thriving'
        elif score >= self.thresholds['healthy']:
            return 'healthy'
        elif score >= self.thresholds['strained']:
            return 'strained'
        elif score >= self.thresholds['depleted']:
            return 'depleted'
        else:
            return 'critical'
            
    def _generate_recommendations(self, factors: WellbeingFactors,
                                state: str) -> List[str]:
        """Generate personalized wellbeing recommendations"""
        recommendations = []
        
        # Flow-based recommendations
        if factors.flow_time < 0.3:
            recommendations.append(
                "Consider longer uninterrupted work sessions to achieve flow state"
            )
            
        # Interruption-based recommendations
        if factors.interruption_rate < 0.7:
            recommendations.append(
                "You're being interrupted frequently. Try enabling focus mode"
            )
            
        # Task completion recommendations
        if factors.task_completion < 0.5:
            recommendations.append(
                "Break down large tasks into smaller, completable chunks"
            )
            
        # Stress-based recommendations
        if factors.stress_level < 0.6:
            recommendations.append(
                "High stress detected. Take a mindful break or simplify your current task"
            )
            
        # Rest recommendations
        if factors.rest_quality < 0.5:
            recommendations.append(
                "Remember to take regular breaks. Your brain needs rest to maintain performance"
            )
            
        # State-based recommendations
        if state == 'thriving':
            recommendations.append(
                "You're in a great digital wellbeing state! Keep up these healthy patterns"
            )
        elif state == 'depleted':
            recommendations.append(
                "Your digital wellbeing needs attention. Consider stepping away for a longer break"
            )
            
        return recommendations
        
    def _record_wellbeing(self, report: Dict):
        """Record wellbeing report in history and knowledge graph"""
        self.wellbeing_history.append(report)
        
        # Record in SKG
        wellbeing_id = f"wellbeing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'digital_wellbeing', ?)
        """, (
            wellbeing_id,
            json.dumps(report)
        ))
        
        self.skg.conn.commit()
        
    def get_wellbeing_trends(self, hours: int = 24) -> Dict:
        """Analyze wellbeing trends over time"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_reports = [
            r for r in self.wellbeing_history
            if datetime.fromisoformat(r['timestamp']) > cutoff
        ]
        
        if not recent_reports:
            return {'status': 'no_data'}
            
        # Calculate trends
        scores = [r['score'] for r in recent_reports]
        states = [r['state'] for r in recent_reports]
        
        # Factor averages
        factor_trends = {}
        for factor in WellbeingFactors.__annotations__.keys():
            values = [r['factors'][factor] for r in recent_reports]
            factor_trends[factor] = {
                'average': np.mean(values),
                'trend': self._calculate_trend(values),
                'current': values[-1] if values else 0.5
            }
            
        return {
            'overall_trend': self._calculate_trend(scores),
            'average_score': np.mean(scores),
            'current_state': states[-1] if states else 'unknown',
            'factor_trends': factor_trends,
            'recommendation_summary': self._summarize_recommendations(recent_reports)
        }
        
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
            
        # Simple linear regression for trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'declining'
        else:
            return 'stable'
            
    def _summarize_recommendations(self, reports: List[Dict]) -> List[str]:
        """Summarize most common recommendations"""
        all_recommendations = []
        for report in reports:
            all_recommendations.extend(report.get('recommendations', []))
            
        # Count frequency
        recommendation_counts = {}
        for rec in all_recommendations:
            # Simple similarity grouping by key words
            key = self._extract_recommendation_key(rec)
            recommendation_counts[key] = recommendation_counts.get(key, 0) + 1
            
        # Return top 3 most common
        sorted_recs = sorted(
            recommendation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [rec[0] for rec in sorted_recs[:3]]
        
    def _extract_recommendation_key(self, recommendation: str) -> str:
        """Extract key theme from recommendation"""
        if 'flow' in recommendation.lower():
            return 'Improve flow state access'
        elif 'interrupt' in recommendation.lower():
            return 'Reduce interruptions'
        elif 'break' in recommendation.lower() or 'rest' in recommendation.lower():
            return 'Take better breaks'
        elif 'stress' in recommendation.lower():
            return 'Manage stress levels'
        elif 'task' in recommendation.lower():
            return 'Improve task management'
        else:
            return recommendation[:50]  # First 50 chars
            
    def compare_to_traditional_metrics(self, engagement_data: Dict) -> Dict:
        """
        Compare consciousness-first metrics to traditional engagement metrics
        
        Shows why wellbeing > engagement
        """
        # Traditional metrics
        total_time = engagement_data.get('total_minutes', 0)
        clicks = engagement_data.get('total_clicks', 0)
        features_used = engagement_data.get('features_used', 0)
        
        # Get our metrics
        latest_wellbeing = self.wellbeing_history[-1] if self.wellbeing_history else None
        
        if not latest_wellbeing:
            return {'status': 'no_wellbeing_data'}
            
        comparison = {
            'traditional_metrics': {
                'engagement_time': f"{total_time} minutes",
                'interaction_count': clicks,
                'feature_adoption': features_used
            },
            'consciousness_metrics': {
                'wellbeing_score': latest_wellbeing['score'],
                'flow_time': latest_wellbeing['factors']['flow_time'],
                'task_completion': latest_wellbeing['factors']['task_completion'],
                'stress_level': latest_wellbeing['factors']['stress_level']
            },
            'insight': self._generate_comparison_insight(
                total_time,
                latest_wellbeing
            )
        }
        
        return comparison
        
    def _generate_comparison_insight(self, engagement_time: int,
                                   wellbeing_report: Dict) -> str:
        """Generate insight about metric differences"""
        wellbeing_score = wellbeing_report['score']
        flow_time = wellbeing_report['factors']['flow_time']
        
        if engagement_time > 120 and wellbeing_score < 0.5:
            return "High engagement but low wellbeing - the system may be addictive rather than helpful"
        elif engagement_time < 30 and wellbeing_score > 0.7:
            return "Low engagement but high wellbeing - efficient, focused interactions"
        elif flow_time > 0.7:
            return "High flow state achieved - this is more valuable than raw engagement time"
        else:
            return "Wellbeing metrics provide deeper insight into interaction quality"