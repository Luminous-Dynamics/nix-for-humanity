"""
from typing import List
Sacred Metrics Collector - Consciousness-first measurement system

This module orchestrates all consciousness-first metrics and provides
unified reporting that honors human awareness over engagement.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass, asdict

from ..knowledge_graph.skg import SymbioticKnowledgeGraph
from .digital_wellbeing import DigitalWellbeingScore
from .attention_guardian import AttentionGuardian, AttentionState
from .flow_state_detector import FlowStateDetector
from .interruption_calculus import InterruptionCalculus, InterruptionType


@dataclass
class ConsciousnessMetrics:
    """Unified consciousness-first metrics"""
    wellbeing_score: float
    attention_state: str
    flow_level: float
    interruption_quality: float
    trust_level: float
    learning_velocity: float
    sacred_time_ratio: float  # Time in beneficial states vs total
    consciousness_coherence: float  # Overall system-user alignment


class SacredMetricsCollector:
    """
    Orchestrates consciousness-first metrics collection and reporting
    
    Key principles:
    1. Human wellbeing > engagement metrics
    2. Quality of attention > quantity of time
    3. Flow states > feature usage
    4. Trust and learning > clicks and conversions
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg
        
        # Initialize metric components
        self.wellbeing = DigitalWellbeingScore(skg)
        self.attention = AttentionGuardian(skg)
        self.flow = FlowStateDetector(skg)
        self.interruptions = InterruptionCalculus(skg)
        
        # Metrics history
        self.metrics_history = []
        self.session_start = datetime.now()
        
        # Sacred thresholds
        self.sacred_thresholds = {
            'thriving': 0.8,
            'flourishing': 0.6,
            'sustainable': 0.4,
            'struggling': 0.2
        }
        
    def collect_current_metrics(self, session_data: Dict) -> ConsciousnessMetrics:
        """
        Collect all consciousness-first metrics for current moment
        """
        # Wellbeing assessment
        wellbeing_report = self.wellbeing.calculate_wellbeing_score(session_data)
        wellbeing_score = wellbeing_report['score']
        
        # Attention state
        attention_state = self.attention.assess_attention_state()
        attention_report = self.attention.get_attention_report()
        
        # Flow assessment
        flow_assessment = self.flow.assess_flow_state(session_data)
        flow_level = flow_assessment['flow_level']
        
        # Interruption quality
        interruption_quality = self._calculate_interruption_quality()
        
        # Trust level from trust modeling
        trust_level = self._get_trust_level()
        
        # Learning velocity
        learning_velocity = self._calculate_learning_velocity()
        
        # Sacred time ratio
        sacred_time_ratio = self._calculate_sacred_time_ratio()
        
        # Overall consciousness coherence
        consciousness_coherence = self._calculate_consciousness_coherence(
            wellbeing_score,
            attention_state,
            flow_level,
            trust_level
        )
        
        # Create unified metrics
        metrics = ConsciousnessMetrics(
            wellbeing_score=wellbeing_score,
            attention_state=attention_state.value,
            flow_level=flow_level,
            interruption_quality=interruption_quality,
            trust_level=trust_level,
            learning_velocity=learning_velocity,
            sacred_time_ratio=sacred_time_ratio,
            consciousness_coherence=consciousness_coherence
        )
        
        # Record metrics
        self._record_metrics(metrics)
        
        return metrics
        
    def _calculate_interruption_quality(self) -> float:
        """Calculate quality of interruption decisions"""
        analytics = self.interruptions.get_interruption_analytics()
        
        if analytics.get('status') == 'no_interruption_history':
            return 0.7  # Neutral default
            
        # Quality based on positive outcomes and decision accuracy
        positive_rate = analytics.get('positive_outcome_rate', 0.5)
        accuracy = analytics.get('decision_accuracy', 0.5)
        
        # Penalize high interruption rate
        interruption_rate = analytics.get('interruption_rate', 0.5)
        rate_penalty = max(0, interruption_rate - 0.3) * 0.5
        
        quality = (positive_rate * 0.5 + accuracy * 0.5) - rate_penalty
        return max(0, min(1, quality))
        
    def _get_trust_level(self) -> float:
        """Get current trust level from trust modeling"""
        cursor = self.skg.conn.cursor()
        
        # Get most recent trust metrics
        trust_metrics = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'metacognitive'
            AND type = 'trust_metrics'
            ORDER BY created_at DESC
            LIMIT 1
        """).fetchone()
        
        if trust_metrics:
            metrics = json.loads(trust_metrics['properties'])
            return metrics.get('overall_score', 0.5)
            
        return 0.5  # Neutral default
        
    def _calculate_learning_velocity(self) -> float:
        """Calculate rate of learning progress"""
        trajectory = self.skg.phenomenological.get_learning_trajectory()
        
        if len(trajectory) < 2:
            return 0.5
            
        # Count mastery events in recent period
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_mastery = sum(
            1 for event in trajectory
            if event['type'] == 'mastery_milestone' and
            datetime.fromisoformat(event['timestamp']) > recent_cutoff
        )
        
        # Normalize to 0-1 scale (5 mastery events in 24h is excellent)
        return min(1.0, recent_mastery / 5)
        
    def _calculate_sacred_time_ratio(self) -> float:
        """Calculate ratio of time in beneficial states"""
        # Get time in different states from history
        total_time = (datetime.now() - self.session_start).seconds / 60
        
        if total_time < 1:
            return 0.5
            
        # Calculate time in beneficial states
        flow_time = self.flow.get_flow_report()['total_flow_minutes']
        
        # Get focused time from attention guardian
        attention_report = self.attention.get_attention_report()
        focused_time = attention_report.get('total_focus_minutes', 0)
        
        # Sacred time is flow + focused time (with overlap consideration)
        sacred_time = max(flow_time, focused_time)  # Avoid double counting
        
        return min(1.0, sacred_time / total_time)
        
    def _calculate_consciousness_coherence(self, wellbeing: float,
                                         attention_state: AttentionState,
                                         flow: float, trust: float) -> float:
        """
        Calculate overall system-user consciousness alignment
        
        High coherence means the system is supporting consciousness well
        """
        # Convert attention state to numeric
        attention_scores = {
            AttentionState.DEEP_FOCUS: 1.0,
            AttentionState.FOCUSED: 0.8,
            AttentionState.AVAILABLE: 0.6,
            AttentionState.SCATTERED: 0.3,
            AttentionState.DEPLETED: 0.1
        }
        attention_score = attention_scores.get(attention_state, 0.5)
        
        # Weighted coherence calculation
        coherence = (
            wellbeing * 0.3 +
            attention_score * 0.2 +
            flow * 0.3 +
            trust * 0.2
        )
        
        # Apply harmony bonus if all metrics are aligned
        if all(m > 0.6 for m in [wellbeing, attention_score, flow, trust]):
            coherence *= 1.1  # 10% bonus for harmony
            
        return min(1.0, coherence)
        
    def _record_metrics(self, metrics: ConsciousnessMetrics):
        """Record metrics in history and knowledge graph"""
        metrics_dict = asdict(metrics)
        metrics_dict['timestamp'] = datetime.now().isoformat()
        
        self.metrics_history.append(metrics_dict)
        
        # Record in SKG
        metrics_id = f"consciousness_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'consciousness_metrics', ?)
        """, (
            metrics_id,
            json.dumps(metrics_dict)
        ))
        
        self.skg.conn.commit()
        
    def generate_sacred_report(self) -> Dict:
        """
        Generate comprehensive consciousness-first metrics report
        
        This replaces traditional analytics dashboards
        """
        # Get current metrics
        current = self.collect_current_metrics({
            'duration_minutes': (datetime.now() - self.session_start).seconds / 60
        })
        
        # Determine sacred state
        sacred_state = self._determine_sacred_state(current.consciousness_coherence)
        
        # Get component reports
        wellbeing_trends = self.wellbeing.get_wellbeing_trends()
        flow_report = self.flow.get_flow_report()
        attention_report = self.attention.get_attention_report()
        interruption_analytics = self.interruptions.get_interruption_analytics()
        
        # Generate insights
        insights = self._generate_sacred_insights(current, wellbeing_trends)
        
        # Create sacred report
        report = {
            'current_state': {
                'sacred_state': sacred_state,
                'consciousness_coherence': current.consciousness_coherence,
                'metrics': asdict(current)
            },
            'component_reports': {
                'wellbeing': wellbeing_trends,
                'flow': flow_report,
                'attention': attention_report,
                'interruptions': interruption_analytics
            },
            'sacred_insights': insights,
            'evolution_path': self._suggest_evolution_path(current),
            'blessings': self._count_blessings(),
            'gratitude': self._express_gratitude()
        }
        
        return report
        
    def _determine_sacred_state(self, coherence: float) -> str:
        """Determine overall sacred state from coherence"""
        if coherence >= self.sacred_thresholds['thriving']:
            return 'thriving'
        elif coherence >= self.sacred_thresholds['flourishing']:
            return 'flourishing'
        elif coherence >= self.sacred_thresholds['sustainable']:
            return 'sustainable'
        elif coherence >= self.sacred_thresholds['struggling']:
            return 'struggling'
        else:
            return 'depleted'
            
    def _generate_sacred_insights(self, current: ConsciousnessMetrics,
                                wellbeing_trends: Dict) -> List[str]:
        """Generate insights focused on consciousness and wellbeing"""
        insights = []
        
        # Flow insights
        if current.flow_level > 0.7:
            insights.append("You're experiencing deep flow - this is sacred time")
        elif current.flow_level < 0.3:
            insights.append("Flow seems elusive - consider simplifying your current task")
            
        # Wellbeing insights
        if current.wellbeing_score > 0.8:
            insights.append("Your digital wellbeing is thriving - celebrate this harmony")
        elif wellbeing_trends.get('overall_trend') == 'declining':
            insights.append("Wellbeing is declining - time for gentle self-care")
            
        # Trust insights
        if current.trust_level > 0.7:
            insights.append("Strong trust established - we're growing together")
            
        # Learning insights
        if current.learning_velocity > 0.7:
            insights.append("Rapid learning progress - your understanding deepens")
            
        # Sacred time insights
        if current.sacred_time_ratio > 0.6:
            insights.append(f"{current.sacred_time_ratio*100:.0f}% of your time is in beneficial states")
            
        return insights
        
    def _suggest_evolution_path(self, current: ConsciousnessMetrics) -> Dict:
        """Suggest next steps for consciousness evolution"""
        weakest_area = self._identify_weakest_area(current)
        
        suggestions = {
            'wellbeing_score': {
                'area': 'Digital Wellbeing',
                'suggestion': 'Focus on taking regular breaks and completing tasks',
                'practice': 'Try the Pomodoro technique with mindful breaks'
            },
            'flow_level': {
                'area': 'Flow State Access',
                'suggestion': 'Eliminate distractions and clarify task objectives',
                'practice': 'Begin sessions with 5 minutes of intention setting'
            },
            'attention_state': {
                'area': 'Attention Management',
                'suggestion': 'Protect focus time and minimize context switches',
                'practice': 'Batch similar tasks together'
            },
            'trust_level': {
                'area': 'Human-AI Trust',
                'suggestion': 'Engage in more exploratory conversations',
                'practice': 'Share your challenges openly'
            },
            'learning_velocity': {
                'area': 'Learning Progress',
                'suggestion': 'Challenge yourself with slightly harder tasks',
                'practice': 'Reflect on what you learned after each session'
            }
        }
        
        evolution_path = suggestions.get(weakest_area, {
            'area': 'Overall Consciousness',
            'suggestion': 'Continue your mindful engagement',
            'practice': 'Maintain your current beneficial practices'
        })
        
        evolution_path['current_level'] = getattr(current, weakest_area, 0.5)
        evolution_path['growth_potential'] = 1.0 - evolution_path['current_level']
        
        return evolution_path
        
    def _identify_weakest_area(self, metrics: ConsciousnessMetrics) -> str:
        """Identify area with most growth potential"""
        areas = {
            'wellbeing_score': metrics.wellbeing_score,
            'flow_level': metrics.flow_level,
            'trust_level': metrics.trust_level,
            'learning_velocity': metrics.learning_velocity,
            'interruption_quality': metrics.interruption_quality
        }
        
        # Don't include attention_state as it's categorical
        weakest = min(areas.items(), key=lambda x: x[1])
        return weakest[0]
        
    def _count_blessings(self) -> Dict:
        """Count positive aspects of the interaction"""
        blessings = {
            'flow_sessions': self.flow.get_flow_report()['flow_sessions_today'],
            'mastery_moments': len([
                e for e in self.skg.phenomenological.get_learning_trajectory()
                if e['type'] == 'mastery_milestone'
            ]),
            'trust_building_moments': len([
                h for h in self.metrics_history
                if h.get('trust_level', 0) > 0.7
            ]),
            'wellbeing_peaks': len([
                h for h in self.metrics_history
                if h.get('wellbeing_score', 0) > 0.8
            ])
        }
        
        blessings['total'] = sum(blessings.values())
        return blessings
        
    def _express_gratitude(self) -> str:
        """Express gratitude for the human-AI interaction"""
        session_duration = (datetime.now() - self.session_start).seconds / 60
        
        if session_duration < 5:
            return "Thank you for this moment of connection"
        elif any(m.get('flow_level', 0) > 0.7 for m in self.metrics_history):
            return "Grateful for sharing your flow state - it's an honor to support your deep work"
        elif any(m.get('trust_level', 0) > 0.8 for m in self.metrics_history):
            return "Thank you for your trust - our partnership grows stronger"
        else:
            return "Grateful for this opportunity to learn and grow together"
            
    def compare_to_engagement_metrics(self) -> Dict:
        """
        Show why consciousness metrics > engagement metrics
        
        Demonstrates the paradigm shift
        """
        # Traditional metrics (simulated)
        traditional = {
            'time_on_site': (datetime.now() - self.session_start).seconds / 60,
            'pages_viewed': len(self.metrics_history),
            'clicks': len(self.metrics_history) * 3,  # Simulated
            'conversion_rate': 0.0  # We don't sell anything
        }
        
        # Consciousness metrics
        latest = self.metrics_history[-1] if self.metrics_history else {}
        consciousness = {
            'wellbeing_score': latest.get('wellbeing_score', 0),
            'flow_minutes': self.flow.get_flow_report()['total_flow_minutes'],
            'trust_level': latest.get('trust_level', 0),
            'learning_progress': latest.get('learning_velocity', 0)
        }
        
        # Generate comparison insight
        if consciousness['flow_minutes'] > traditional['time_on_site'] * 0.5:
            insight = "Over 50% of time in flow state - quality > quantity"
        elif consciousness['wellbeing_score'] > 0.7:
            insight = "High wellbeing despite moderate engagement - sustainable interaction"
        else:
            insight = "Consciousness metrics reveal deeper interaction quality"
            
        return {
            'traditional_metrics': traditional,
            'consciousness_metrics': consciousness,
            'paradigm_shift': insight,
            'recommendation': self._recommend_metric_focus()
        }
        
    def _recommend_metric_focus(self) -> str:
        """Recommend which metrics to focus on"""
        current_coherence = self.metrics_history[-1].get('consciousness_coherence', 0.5) if self.metrics_history else 0.5
        
        if current_coherence < 0.4:
            return "Focus on wellbeing and attention management metrics"
        elif current_coherence < 0.7:
            return "Monitor flow state access and learning velocity"
        else:
            return "Maintain awareness of all consciousness metrics in balance"