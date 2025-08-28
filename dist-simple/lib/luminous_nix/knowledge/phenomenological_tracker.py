#!/usr/bin/env python3
"""
Enhanced Phenomenological State Tracking
=========================================

This module provides sophisticated tracking of user emotional and cognitive states,
enabling the system to adapt its responses based on the user's phenomenological experience.

The phenomenological layer captures:
- Emotional states (frustration, satisfaction, flow)
- Cognitive load (confusion, clarity, overwhelm)
- Learning momentum (progress, stagnation, breakthrough)
- Interaction quality (engagement, disconnection)
"""

import logging
import time
import math
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """User emotional states"""
    FRUSTRATED = "frustrated"
    SATISFIED = "satisfied"
    CURIOUS = "curious"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    FLOWING = "flowing"
    NEUTRAL = "neutral"


class CognitiveLoad(Enum):
    """Cognitive load levels"""
    OVERWHELMED = "overwhelmed"
    HIGH = "high"
    OPTIMAL = "optimal"
    LOW = "low"
    BORED = "bored"


@dataclass
class PhenomenologicalSnapshot:
    """A snapshot of the user's phenomenological state at a moment in time"""
    timestamp: float
    emotional_state: EmotionalState
    cognitive_load: CognitiveLoad
    flow_probability: float  # 0.0 to 1.0
    confusion_probability: float  # 0.0 to 1.0
    satisfaction_score: float  # 0.0 to 1.0
    engagement_level: float  # 0.0 to 1.0
    learning_momentum: float  # -1.0 to 1.0 (negative = stuck, positive = progressing)
    stress_indicators: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


class PhenomenologicalTracker:
    """
    Advanced phenomenological state tracking for consciousness-first computing.
    
    This tracker uses multiple signals to infer the user's emotional and cognitive state:
    - Response time patterns
    - Error frequencies
    - Query complexity progression
    - Interaction patterns
    - Success/failure ratios
    """
    
    def __init__(self):
        """Initialize the phenomenological tracker"""
        self.state_history: List[PhenomenologicalSnapshot] = []
        self.interaction_buffer: List[Dict[str, Any]] = []
        self.baseline_response_time = 5000  # 5 seconds baseline
        self.error_window = []  # Recent errors for pattern detection
        self.success_window = []  # Recent successes
        
        # Adaptive thresholds that learn from user
        self.thresholds = {
            'fast_response': 2000,  # ms
            'slow_response': 10000,  # ms
            'error_threshold': 0.3,  # 30% error rate indicates frustration
            'flow_threshold': 0.8,  # 80% success with fast responses
            'confusion_threshold': 0.5  # Multiple similar queries
        }
        
        logger.info("🧠 PhenomenologicalTracker initialized - sensing user states")
    
    def analyze_interaction(self, 
                           interaction: Dict[str, Any],
                           response_time_ms: int,
                           success: bool,
                           error_type: Optional[str] = None) -> PhenomenologicalSnapshot:
        """
        Analyze an interaction to infer phenomenological state.
        
        Args:
            interaction: The interaction details
            response_time_ms: How long the response took
            success: Whether the interaction succeeded
            error_type: Type of error if failed
            
        Returns:
            Phenomenological snapshot of inferred state
        """
        # Add to history windows
        self.interaction_buffer.append({
            'interaction': interaction,
            'response_time': response_time_ms,
            'success': success,
            'error_type': error_type,
            'timestamp': time.time()
        })
        
        # Keep windows to last 10 interactions
        if len(self.interaction_buffer) > 10:
            self.interaction_buffer.pop(0)
        
        if success:
            self.success_window.append(time.time())
        else:
            self.error_window.append(time.time())
        
        # Trim windows to last 5 minutes
        cutoff = time.time() - 300
        self.success_window = [t for t in self.success_window if t > cutoff]
        self.error_window = [t for t in self.error_window if t > cutoff]
        
        # Calculate state indicators
        flow_prob = self._calculate_flow_probability(response_time_ms)
        confusion_prob = self._calculate_confusion_probability()
        satisfaction = self._calculate_satisfaction_score()
        engagement = self._calculate_engagement_level(response_time_ms)
        momentum = self._calculate_learning_momentum()
        
        # Determine emotional state
        emotional_state = self._infer_emotional_state(
            flow_prob, confusion_prob, satisfaction, success
        )
        
        # Determine cognitive load
        cognitive_load = self._infer_cognitive_load(
            response_time_ms, confusion_prob, len(self.error_window)
        )
        
        # Calculate stress indicators
        stress_indicators = self._calculate_stress_indicators()
        
        # Create snapshot
        snapshot = PhenomenologicalSnapshot(
            timestamp=time.time(),
            emotional_state=emotional_state,
            cognitive_load=cognitive_load,
            flow_probability=flow_prob,
            confusion_probability=confusion_prob,
            satisfaction_score=satisfaction,
            engagement_level=engagement,
            learning_momentum=momentum,
            stress_indicators=stress_indicators,
            context={
                'response_time_ms': response_time_ms,
                'success': success,
                'error_type': error_type,
                'query': interaction.get('query', '')
            }
        )
        
        # Add to history
        self.state_history.append(snapshot)
        
        # Adapt thresholds based on user patterns
        self._adapt_thresholds()
        
        return snapshot
    
    def _calculate_flow_probability(self, response_time_ms: int) -> float:
        """Calculate probability of flow state"""
        if len(self.interaction_buffer) < 3:
            return 0.5  # Not enough data
        
        # Flow indicators:
        # - Quick responses
        # - High success rate
        # - Consistent interaction pattern
        
        recent_success_rate = len(self.success_window) / max(
            len(self.success_window) + len(self.error_window), 1
        )
        
        # Fast response indicates confidence
        speed_score = max(0, 1 - (response_time_ms / self.thresholds['slow_response']))
        
        # Consistency in recent interactions
        if len(self.interaction_buffer) >= 3:
            recent_times = [i['response_time'] for i in self.interaction_buffer[-3:]]
            time_variance = math.sqrt(sum((t - sum(recent_times)/3)**2 for t in recent_times) / 3)
            consistency_score = max(0, 1 - (time_variance / 5000))  # Normalize variance
        else:
            consistency_score = 0.5
        
        # Combine factors
        flow_prob = (recent_success_rate * 0.4 + speed_score * 0.3 + consistency_score * 0.3)
        
        return min(1.0, max(0.0, flow_prob))
    
    def _calculate_confusion_probability(self) -> float:
        """Calculate probability of confusion"""
        if len(self.interaction_buffer) < 2:
            return 0.0
        
        # Confusion indicators:
        # - Repeated similar queries
        # - Increasing response times
        # - Recent errors
        
        # Check for repeated queries (simplified - could use embedding similarity)
        recent_queries = [i['interaction'].get('query', '').lower() 
                         for i in self.interaction_buffer[-5:]]
        
        # Count similar queries
        similarity_count = 0
        for i, q1 in enumerate(recent_queries):
            for q2 in recent_queries[i+1:]:
                if self._query_similarity(q1, q2) > 0.7:
                    similarity_count += 1
        
        repetition_score = min(1.0, similarity_count / 3)
        
        # Check if response times are increasing
        if len(self.interaction_buffer) >= 3:
            times = [i['response_time'] for i in self.interaction_buffer[-3:]]
            increasing = all(times[i] <= times[i+1] for i in range(len(times)-1))
            time_trend_score = 0.5 if increasing else 0.0
        else:
            time_trend_score = 0.0
        
        # Recent error rate
        error_score = min(1.0, len(self.error_window) / 5)
        
        # Combine factors
        confusion_prob = (repetition_score * 0.4 + time_trend_score * 0.3 + error_score * 0.3)
        
        return min(1.0, max(0.0, confusion_prob))
    
    def _query_similarity(self, q1: str, q2: str) -> float:
        """Simple query similarity check (could be enhanced with embeddings)"""
        # Simple word overlap for now
        words1 = set(q1.split())
        words2 = set(q2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_satisfaction_score(self) -> float:
        """Calculate overall satisfaction"""
        if not self.interaction_buffer:
            return 0.5
        
        # Satisfaction based on:
        # - Success rate
        # - Response times meeting expectations
        # - Absence of repeated failures
        
        total = len(self.success_window) + len(self.error_window)
        if total == 0:
            return 0.5
        
        success_rate = len(self.success_window) / total
        
        # Check if response times are reasonable
        recent_times = [i['response_time'] for i in self.interaction_buffer[-5:]]
        reasonable_times = sum(1 for t in recent_times if t < self.thresholds['slow_response'])
        time_satisfaction = reasonable_times / len(recent_times) if recent_times else 0.5
        
        # Check for repeated failures
        if len(self.error_window) >= 2:
            # Errors close together indicate frustration
            error_gaps = [self.error_window[i+1] - self.error_window[i] 
                         for i in range(len(self.error_window)-1)]
            avg_gap = sum(error_gaps) / len(error_gaps) if error_gaps else 300
            frustration_penalty = max(0, 1 - (30 / avg_gap))  # Penalty if errors < 30s apart
        else:
            frustration_penalty = 0
        
        satisfaction = (success_rate * 0.5 + time_satisfaction * 0.3 + (1 - frustration_penalty) * 0.2)
        
        return min(1.0, max(0.0, satisfaction))
    
    def _calculate_engagement_level(self, response_time_ms: int) -> float:
        """Calculate user engagement level"""
        # Quick responses indicate engagement
        # But too quick might indicate disengagement (just clicking through)
        
        if response_time_ms < 500:  # Too fast, might be clicking through
            return 0.3
        elif response_time_ms < self.thresholds['fast_response']:
            return 0.9  # Engaged and responding quickly
        elif response_time_ms < self.thresholds['slow_response']:
            return 0.7  # Normally engaged
        else:
            # Slow response might indicate thinking or disengagement
            # Check pattern
            if len(self.interaction_buffer) >= 2:
                prev_time = self.interaction_buffer[-2]['response_time']
                if prev_time > self.thresholds['slow_response']:
                    return 0.3  # Consistently slow = disengaged
                else:
                    return 0.5  # Might be thinking
            return 0.5
    
    def _calculate_learning_momentum(self) -> float:
        """Calculate learning momentum (-1 to 1)"""
        if len(self.interaction_buffer) < 3:
            return 0.0
        
        # Positive momentum: decreasing errors, increasing success, query progression
        # Negative momentum: repeated errors, stagnation
        
        # Success trend
        recent = self.interaction_buffer[-5:]
        recent_success = sum(1 for i in recent if i['success'])
        older = self.interaction_buffer[-10:-5] if len(self.interaction_buffer) >= 10 else []
        older_success = sum(1 for i in older if i['success']) if older else recent_success
        
        success_trend = (recent_success - older_success) / 5
        
        # Query complexity progression (simplified)
        recent_queries = [i['interaction'].get('query', '') for i in recent]
        complexity_progression = len(set(recent_queries)) / len(recent_queries)  # Variety indicates progress
        
        momentum = (success_trend * 0.6 + (complexity_progression - 0.5) * 2 * 0.4)
        
        return min(1.0, max(-1.0, momentum))
    
    def _infer_emotional_state(self, 
                               flow_prob: float,
                               confusion_prob: float,
                               satisfaction: float,
                               success: bool) -> EmotionalState:
        """Infer emotional state from indicators"""
        if flow_prob > 0.7:
            return EmotionalState.FLOWING
        elif confusion_prob > 0.6:
            return EmotionalState.CONFUSED
        elif satisfaction < 0.3:
            return EmotionalState.FRUSTRATED
        elif satisfaction > 0.7 and success:
            return EmotionalState.SATISFIED
        elif confusion_prob > 0.4:
            return EmotionalState.ANXIOUS
        elif success and satisfaction > 0.5:
            return EmotionalState.CONFIDENT
        elif satisfaction > 0.4:
            return EmotionalState.CURIOUS
        else:
            return EmotionalState.NEUTRAL
    
    def _infer_cognitive_load(self,
                              response_time_ms: int,
                              confusion_prob: float,
                              error_count: int) -> CognitiveLoad:
        """Infer cognitive load from indicators"""
        if confusion_prob > 0.7 or error_count > 3:
            return CognitiveLoad.OVERWHELMED
        elif response_time_ms > self.thresholds['slow_response'] or confusion_prob > 0.5:
            return CognitiveLoad.HIGH
        elif response_time_ms < self.thresholds['fast_response'] and confusion_prob < 0.2:
            if response_time_ms < 1000:  # Very fast
                return CognitiveLoad.BORED
            else:
                return CognitiveLoad.LOW
        else:
            return CognitiveLoad.OPTIMAL
    
    def _calculate_stress_indicators(self) -> Dict[str, float]:
        """Calculate various stress indicators"""
        indicators = {}
        
        if len(self.interaction_buffer) >= 2:
            # Response time variance (high variance = stress)
            times = [i['response_time'] for i in self.interaction_buffer[-5:]]
            if len(times) >= 2:
                mean_time = sum(times) / len(times)
                variance = sum((t - mean_time)**2 for t in times) / len(times)
                indicators['time_variance'] = min(1.0, variance / 10000000)  # Normalize
            
            # Error clustering (errors close together = stress)
            if len(self.error_window) >= 2:
                gaps = [self.error_window[i+1] - self.error_window[i] 
                       for i in range(len(self.error_window)-1)]
                avg_gap = sum(gaps) / len(gaps)
                indicators['error_clustering'] = max(0, 1 - (avg_gap / 60))  # Normalize to 1 minute
            
            # Interaction frequency (too fast = stress)
            interaction_gaps = []
            for i in range(1, len(self.interaction_buffer)):
                gap = self.interaction_buffer[i]['timestamp'] - self.interaction_buffer[i-1]['timestamp']
                interaction_gaps.append(gap)
            
            if interaction_gaps:
                avg_gap = sum(interaction_gaps) / len(interaction_gaps)
                indicators['interaction_pressure'] = max(0, 1 - (avg_gap / 10))  # Normalize to 10 seconds
        
        return indicators
    
    def _adapt_thresholds(self):
        """Adapt thresholds based on user's patterns"""
        if len(self.interaction_buffer) < 20:
            return  # Not enough data
        
        # Adapt response time thresholds
        all_times = [i['response_time'] for i in self.interaction_buffer]
        sorted_times = sorted(all_times)
        
        # Fast response = 25th percentile
        self.thresholds['fast_response'] = sorted_times[len(sorted_times) // 4]
        
        # Slow response = 75th percentile
        self.thresholds['slow_response'] = sorted_times[3 * len(sorted_times) // 4]
        
        # Update baseline
        self.baseline_response_time = sum(all_times) / len(all_times)
    
    def get_current_state(self) -> Optional[PhenomenologicalSnapshot]:
        """Get the current phenomenological state"""
        if self.state_history:
            return self.state_history[-1]
        return None
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of recent phenomenological states"""
        if not self.state_history:
            return {
                'current_state': None,
                'trend': 'unknown',
                'recommendations': []
            }
        
        current = self.state_history[-1]
        
        # Calculate trends if we have history
        if len(self.state_history) >= 3:
            recent_satisfaction = [s.satisfaction_score for s in self.state_history[-3:]]
            satisfaction_trend = 'improving' if recent_satisfaction[-1] > recent_satisfaction[0] else 'declining'
            
            recent_confusion = [s.confusion_probability for s in self.state_history[-3:]]
            confusion_trend = 'increasing' if recent_confusion[-1] > recent_confusion[0] else 'decreasing'
        else:
            satisfaction_trend = 'stable'
            confusion_trend = 'stable'
        
        # Generate recommendations
        recommendations = []
        
        if current.emotional_state == EmotionalState.FRUSTRATED:
            recommendations.append("Consider simpler explanations or breaking down the task")
        elif current.emotional_state == EmotionalState.CONFUSED:
            recommendations.append("Provide more examples or clarification")
        elif current.emotional_state == EmotionalState.FLOWING:
            recommendations.append("Maintain current pace and complexity")
        
        if current.cognitive_load == CognitiveLoad.OVERWHELMED:
            recommendations.append("Reduce complexity and provide step-by-step guidance")
        elif current.cognitive_load == CognitiveLoad.BORED:
            recommendations.append("Increase challenge or introduce new concepts")
        
        if current.learning_momentum < -0.3:
            recommendations.append("User may be stuck - offer alternative approaches")
        elif current.learning_momentum > 0.5:
            recommendations.append("User is progressing well - consider advancing topics")
        
        return {
            'current_state': {
                'emotional': current.emotional_state.value,
                'cognitive_load': current.cognitive_load.value,
                'flow_probability': current.flow_probability,
                'confusion_probability': current.confusion_probability,
                'satisfaction_score': current.satisfaction_score,
                'engagement_level': current.engagement_level,
                'learning_momentum': current.learning_momentum
            },
            'trends': {
                'satisfaction': satisfaction_trend,
                'confusion': confusion_trend
            },
            'recommendations': recommendations,
            'stress_indicators': current.stress_indicators
        }
    
    def export_history(self) -> List[Dict[str, Any]]:
        """Export phenomenological history for analysis"""
        return [
            {
                'timestamp': s.timestamp,
                'emotional_state': s.emotional_state.value,
                'cognitive_load': s.cognitive_load.value,
                'flow_probability': s.flow_probability,
                'confusion_probability': s.confusion_probability,
                'satisfaction_score': s.satisfaction_score,
                'engagement_level': s.engagement_level,
                'learning_momentum': s.learning_momentum,
                'stress_indicators': s.stress_indicators,
                'context': s.context
            }
            for s in self.state_history
        ]


# Singleton instance
_tracker_instance: Optional[PhenomenologicalTracker] = None

def get_phenomenological_tracker() -> PhenomenologicalTracker:
    """Get or create the singleton phenomenological tracker"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PhenomenologicalTracker()
    return _tracker_instance