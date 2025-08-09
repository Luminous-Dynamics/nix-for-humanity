"""
from typing import List, Optional
Flow State Detector - Identifying and protecting flow states

Based on Csikszentmihalyi's research on flow and optimal experience,
adapted for human-AI interaction contexts.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


@dataclass
class FlowIndicators:
    """Indicators of flow state based on research"""
    challenge_skill_balance: float  # Task difficulty matches ability (0-1)
    clear_goals: float  # Clarity of objectives (0-1)
    immediate_feedback: float  # Quick response to actions (0-1)
    deep_concentration: float  # Focused attention (0-1)
    time_transformation: float  # Altered time perception (0-1)
    intrinsic_motivation: float  # Self-driven engagement (0-1)
    sense_of_control: float  # Feeling of agency (0-1)
    self_consciousness_loss: float  # Ego dissolution (0-1)
    autotelic_experience: float  # Activity is its own reward (0-1)


class FlowStateDetector:
    """
    Detects and monitors flow states to protect deep work
    
    Key insights:
    1. Flow is fragile and must be protected
    2. Flow indicators can be inferred from behavior
    3. Different tasks have different flow profiles
    4. Flow state is the optimal human experience
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg
        
        # Flow tracking
        self.current_flow_level = 0.0
        self.flow_start_time = None
        self.flow_history = []
        
        # Flow patterns by task type
        self.task_flow_profiles = {
            'coding': {'optimal_duration': 90, 'warmup_time': 15},
            'learning': {'optimal_duration': 45, 'warmup_time': 10},
            'configuration': {'optimal_duration': 30, 'warmup_time': 5},
            'troubleshooting': {'optimal_duration': 60, 'warmup_time': 20},
            'exploration': {'optimal_duration': 120, 'warmup_time': 10}
        }
        
        # Behavioral indicators
        self.behavior_buffer = []
        self.last_assessment_time = None
        
    def assess_flow_state(self, interaction_data: Dict) -> Dict:
        """
        Assess current flow state from multiple indicators
        
        Returns flow assessment with level and recommendations
        """
        # Update behavior buffer
        self._update_behavior_buffer(interaction_data)
        
        # Calculate flow indicators
        indicators = self._calculate_flow_indicators()
        
        # Calculate overall flow level
        flow_level = self._calculate_flow_level(indicators)
        
        # Detect flow state changes
        flow_state = self._determine_flow_state(flow_level)
        
        # Generate flow protection recommendations
        protection_measures = self._recommend_flow_protection(flow_state, indicators)
        
        # Create assessment report
        assessment = {
            'flow_level': flow_level,
            'flow_state': flow_state,
            'indicators': indicators,
            'protection_measures': protection_measures,
            'optimal_interruption_window': self._calculate_interruption_window(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Update tracking
        self._update_flow_tracking(flow_level, flow_state)
        
        # Record in SKG
        self._record_flow_assessment(assessment)
        
        return assessment
        
    def _update_behavior_buffer(self, interaction_data: Dict):
        """Update rolling buffer of behavioral data"""
        behavior_point = {
            'timestamp': datetime.now(),
            'response_time': interaction_data.get('response_time', 0),
            'input_length': len(interaction_data.get('user_input', '')),
            'error_occurred': interaction_data.get('error', False),
            'task_type': interaction_data.get('task_type', 'unknown'),
            'success': interaction_data.get('success', True)
        }
        
        self.behavior_buffer.append(behavior_point)
        
        # Keep only recent 30 minutes
        cutoff = datetime.now() - timedelta(minutes=30)
        self.behavior_buffer = [
            b for b in self.behavior_buffer
            if b['timestamp'] > cutoff
        ]
        
    def _calculate_flow_indicators(self) -> FlowIndicators:
        """Calculate flow indicators from behavioral patterns"""
        if len(self.behavior_buffer) < 3:
            # Not enough data - return neutral indicators
            return FlowIndicators(
                challenge_skill_balance=0.5,
                clear_goals=0.5,
                immediate_feedback=0.5,
                deep_concentration=0.5,
                time_transformation=0.5,
                intrinsic_motivation=0.5,
                sense_of_control=0.5,
                self_consciousness_loss=0.5,
                autotelic_experience=0.5
            )
            
        # Challenge-skill balance from error rate
        errors = sum(1 for b in self.behavior_buffer if b['error_occurred'])
        error_rate = errors / len(self.behavior_buffer)
        challenge_skill_balance = 1 - abs(error_rate - 0.15)  # Optimal is ~15% errors
        
        # Clear goals from task consistency
        task_types = [b['task_type'] for b in self.behavior_buffer]
        most_common_task = max(set(task_types), key=task_types.count)
        task_consistency = task_types.count(most_common_task) / len(task_types)
        clear_goals = task_consistency
        
        # Immediate feedback from response times
        response_times = [b['response_time'] for b in self.behavior_buffer]
        avg_response_time = np.mean(response_times)
        immediate_feedback = 1 / (1 + avg_response_time / 1000)  # Faster is better
        
        # Deep concentration from input consistency
        input_lengths = [b['input_length'] for b in self.behavior_buffer]
        if len(input_lengths) > 1:
            input_variance = np.var(input_lengths)
            deep_concentration = 1 / (1 + input_variance / 100)
        else:
            deep_concentration = 0.5
            
        # Time transformation from session duration
        session_duration = (self.behavior_buffer[-1]['timestamp'] - 
                          self.behavior_buffer[0]['timestamp']).seconds / 60
        
        if session_duration > 30:
            time_transformation = min(1.0, session_duration / 60)  # Peak at 60+ minutes
        else:
            time_transformation = session_duration / 30
            
        # Get additional indicators from phenomenological layer
        user_state = self.skg.phenomenological.get_current_user_state()
        
        # Intrinsic motivation from learning trajectory
        learning_trajectory = self.skg.phenomenological.get_learning_trajectory()
        recent_mastery = sum(
            1 for event in learning_trajectory[-10:]
            if event['type'] == 'mastery_milestone'
        )
        intrinsic_motivation = min(1.0, recent_mastery / 3)
        
        # Sense of control from success rate
        successes = sum(1 for b in self.behavior_buffer if b['success'])
        sense_of_control = successes / len(self.behavior_buffer)
        
        # Self-consciousness loss from cognitive state
        cognitive_load = user_state.get('cognitive_load', 0.5)
        self_consciousness_loss = max(0, 1 - cognitive_load) if cognitive_load > 0.3 else 0.5
        
        # Autotelic experience from engagement patterns
        engagement = user_state.get('flow_level', 0.5)
        autotelic_experience = engagement
        
        return FlowIndicators(
            challenge_skill_balance=challenge_skill_balance,
            clear_goals=clear_goals,
            immediate_feedback=immediate_feedback,
            deep_concentration=deep_concentration,
            time_transformation=time_transformation,
            intrinsic_motivation=intrinsic_motivation,
            sense_of_control=sense_of_control,
            self_consciousness_loss=self_consciousness_loss,
            autotelic_experience=autotelic_experience
        )
        
    def _calculate_flow_level(self, indicators: FlowIndicators) -> float:
        """Calculate overall flow level from indicators"""
        # Weighted average of indicators
        weights = {
            'challenge_skill_balance': 0.15,
            'clear_goals': 0.10,
            'immediate_feedback': 0.10,
            'deep_concentration': 0.15,
            'time_transformation': 0.10,
            'intrinsic_motivation': 0.10,
            'sense_of_control': 0.10,
            'self_consciousness_loss': 0.10,
            'autotelic_experience': 0.10
        }
        
        indicator_dict = indicators.__dict__
        flow_level = sum(
            weights[key] * value
            for key, value in indicator_dict.items()
        )
        
        return flow_level
        
    def _determine_flow_state(self, flow_level: float) -> str:
        """Determine categorical flow state"""
        if flow_level >= 0.8:
            return 'deep_flow'
        elif flow_level >= 0.6:
            return 'flow'
        elif flow_level >= 0.4:
            return 'near_flow'
        elif flow_level >= 0.2:
            return 'struggle'
        else:
            return 'disconnected'
            
    def _recommend_flow_protection(self, flow_state: str,
                                 indicators: FlowIndicators) -> List[Dict]:
        """Recommend measures to protect or enhance flow"""
        recommendations = []
        
        if flow_state in ['deep_flow', 'flow']:
            # Protect existing flow
            recommendations.append({
                'action': 'block_interruptions',
                'priority': 'high',
                'reason': 'User is in flow state - protect at all costs'
            })
            
            recommendations.append({
                'action': 'maintain_challenge_level',
                'priority': 'medium',
                'reason': 'Keep tasks at current difficulty to maintain flow'
            })
            
        elif flow_state == 'near_flow':
            # Help achieve flow
            if indicators.challenge_skill_balance < 0.6:
                recommendations.append({
                    'action': 'adjust_difficulty',
                    'priority': 'high',
                    'reason': 'Task difficulty not matched to skill level'
                })
                
            if indicators.clear_goals < 0.6:
                recommendations.append({
                    'action': 'clarify_objectives',
                    'priority': 'medium',
                    'reason': 'Unclear goals preventing flow entry'
                })
                
        elif flow_state == 'struggle':
            # Address blockers
            if indicators.deep_concentration < 0.4:
                recommendations.append({
                    'action': 'reduce_distractions',
                    'priority': 'high',
                    'reason': 'Cannot achieve deep concentration'
                })
                
            if indicators.sense_of_control < 0.4:
                recommendations.append({
                    'action': 'increase_autonomy',
                    'priority': 'medium',
                    'reason': 'Lack of control preventing flow'
                })
                
        return recommendations
        
    def _calculate_interruption_window(self) -> Optional[Dict]:
        """Calculate optimal window for necessary interruptions"""
        if not self.flow_start_time:
            return {'status': 'no_active_flow_session'}
            
        # Get current task profile
        current_task = self._identify_current_task()
        profile = self.task_flow_profiles.get(
            current_task,
            {'optimal_duration': 60, 'warmup_time': 10}
        )
        
        # Calculate time in flow
        flow_duration = (datetime.now() - self.flow_start_time).seconds / 60
        
        # Natural break points
        if flow_duration < profile['warmup_time']:
            return {
                'window': 'warmup_phase',
                'wait_minutes': profile['warmup_time'] - flow_duration,
                'reason': 'User still entering flow state'
            }
            
        elif flow_duration > profile['optimal_duration'] - 10:
            return {
                'window': 'natural_break_approaching',
                'wait_minutes': max(0, profile['optimal_duration'] - flow_duration),
                'reason': 'Natural flow break approaching'
            }
            
        else:
            # In deep flow - calculate next break
            next_break = profile['optimal_duration'] - flow_duration
            return {
                'window': 'deep_flow',
                'wait_minutes': next_break,
                'reason': 'User in deep flow - wait for natural break'
            }
            
    def _identify_current_task(self) -> str:
        """Identify current task type from behavior"""
        if not self.behavior_buffer:
            return 'unknown'
            
        # Get most recent task types
        recent_tasks = [b['task_type'] for b in self.behavior_buffer[-5:]]
        if recent_tasks:
            return max(set(recent_tasks), key=recent_tasks.count)
            
        return 'unknown'
        
    def _update_flow_tracking(self, flow_level: float, flow_state: str):
        """Update flow tracking variables"""
        self.current_flow_level = flow_level
        
        # Track flow session start/end
        if flow_state in ['flow', 'deep_flow'] and not self.flow_start_time:
            self.flow_start_time = datetime.now()
            
        elif flow_state not in ['flow', 'deep_flow'] and self.flow_start_time:
            # Flow session ended
            duration = (datetime.now() - self.flow_start_time).seconds / 60
            self.flow_history.append({
                'duration_minutes': duration,
                'peak_level': self.current_flow_level,
                'end_time': datetime.now().isoformat()
            })
            self.flow_start_time = None
            
        self.last_assessment_time = datetime.now()
        
    def _record_flow_assessment(self, assessment: Dict):
        """Record flow assessment in knowledge graph"""
        assessment_id = f"flow_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'phenomenological', 'flow_assessment', ?)
        """, (
            assessment_id,
            json.dumps(assessment)
        ))
        
        self.skg.conn.commit()
        
    def get_flow_report(self) -> Dict:
        """Generate comprehensive flow state report"""
        # Calculate flow statistics
        total_flow_time = sum(
            session['duration_minutes']
            for session in self.flow_history
        )
        
        avg_flow_duration = (
            total_flow_time / len(self.flow_history)
            if self.flow_history else 0
        )
        
        # Get flow quality distribution
        flow_quality = {
            'deep_flow_sessions': sum(
                1 for s in self.flow_history
                if s['peak_level'] >= 0.8
            ),
            'flow_sessions': sum(
                1 for s in self.flow_history
                if 0.6 <= s['peak_level'] < 0.8
            ),
            'near_flow_sessions': sum(
                1 for s in self.flow_history
                if s['peak_level'] < 0.6
            )
        }
        
        return {
            'current_flow_level': self.current_flow_level,
            'in_flow_session': self.flow_start_time is not None,
            'total_flow_minutes': total_flow_time,
            'average_flow_duration': avg_flow_duration,
            'flow_sessions_today': len(self.flow_history),
            'flow_quality': flow_quality,
            'optimal_conditions': self._identify_optimal_flow_conditions()
        }
        
    def _identify_optimal_flow_conditions(self) -> Dict:
        """Identify conditions that promote flow for this user"""
        if not self.flow_history:
            return {'status': 'insufficient_data'}
            
        # Analyze successful flow sessions
        successful_flows = [
            s for s in self.flow_history
            if s['peak_level'] >= 0.7
        ]
        
        if not successful_flows:
            return {'status': 'no_successful_flows_yet'}
            
        # Extract patterns (simplified for now)
        return {
            'average_duration': np.mean([s['duration_minutes'] for s in successful_flows]),
            'best_time_of_day': self._identify_best_flow_time(),
            'recommended_session_length': 60,  # Would be calculated from data
            'key_factors': [
                'Clear task objectives',
                'Minimal interruptions',
                'Appropriate challenge level'
            ]
        }
        
    def _identify_best_flow_time(self) -> str:
        """Identify time of day with best flow states"""
        # Simplified - would analyze timestamps
        return 'morning'  # Placeholder
        
    def suggest_flow_enhancement(self) -> Optional[Dict]:
        """Suggest ways to enhance flow state"""
        if self.current_flow_level >= 0.7:
            return None  # Already in good flow
            
        # Get current indicators
        indicators = self._calculate_flow_indicators()
        
        # Find weakest indicator
        indicator_values = indicators.__dict__
        weakest = min(indicator_values.items(), key=lambda x: x[1])
        
        suggestions = {
            'challenge_skill_balance': {
                'suggestion': 'Adjust task difficulty',
                'action': 'Try a slightly easier or harder task'
            },
            'clear_goals': {
                'suggestion': 'Clarify objectives',
                'action': 'Break down your current task into clear steps'
            },
            'immediate_feedback': {
                'suggestion': 'Seek faster feedback',
                'action': 'Use test-driven development or incremental validation'
            },
            'deep_concentration': {
                'suggestion': 'Eliminate distractions',
                'action': 'Enable focus mode and close unnecessary applications'
            },
            'intrinsic_motivation': {
                'suggestion': 'Connect with purpose',
                'action': 'Remind yourself why this task matters to you'
            }
        }
        
        suggestion = suggestions.get(weakest[0])
        if suggestion:
            return {
                'weak_area': weakest[0],
                'current_level': weakest[1],
                'suggestion': suggestion['suggestion'],
                'action': suggestion['action']
            }
            
        return None