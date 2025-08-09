"""
from typing import Tuple, List, Optional
Attention Guardian - Protecting user attention as a sacred resource

This module implements attention protection mechanisms based on
consciousness-first computing principles.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


class AttentionState(Enum):
    """States of user attention"""
    DEEP_FOCUS = "deep_focus"  # In flow, do not disturb
    FOCUSED = "focused"  # Working well, minimize interruptions
    AVAILABLE = "available"  # Open to interactions
    SCATTERED = "scattered"  # Attention fragmented, needs support
    DEPLETED = "depleted"  # Attention exhausted, needs rest


class InterruptionPriority(Enum):
    """Priority levels for potential interruptions"""
    EMERGENCY = 5  # System critical issues only
    HIGH = 4  # Important but not urgent
    MEDIUM = 3  # Normal priority
    LOW = 2  # Can wait
    AMBIENT = 1  # Background information only


class AttentionGuardian:
    """
    Guards user attention as a precious resource
    
    Key principles:
    1. Attention is finite and sacred
    2. Deep work is more valuable than shallow multitasking
    3. Interruptions should be justified by their value
    4. The system should protect focus, not fragment it
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg
        
        # Attention tracking
        self.attention_history = []
        self.current_state = AttentionState.AVAILABLE
        self.focus_start_time = None
        
        # Interruption management
        self.pending_notifications = []
        self.interruption_budget = 3  # Max interruptions per hour
        self.interruptions_this_hour = 0
        self.last_interruption_time = None
        
        # Attention restoration
        self.suggested_break_time = None
        self.focus_session_count = 0
        
    def assess_attention_state(self) -> AttentionState:
        """
        Assess current attention state from multiple signals
        """
        # Get user's cognitive state
        user_state = self.skg.phenomenological.get_current_user_state()
        
        # Get recent interaction patterns
        interaction_pattern = self._analyze_interaction_patterns()
        
        # Calculate attention metrics
        cognitive_load = user_state.get('cognitive_load', 0.5)
        flow_level = user_state.get('flow_level', 0.0)
        frustration = user_state.get('frustration_level', 0.0)
        
        # Determine state
        if flow_level > 0.7:
            new_state = AttentionState.DEEP_FOCUS
        elif flow_level > 0.4 and cognitive_load < 0.7:
            new_state = AttentionState.FOCUSED
        elif frustration > 0.6 or cognitive_load > 0.8:
            new_state = AttentionState.SCATTERED
        elif self._is_attention_depleted(interaction_pattern):
            new_state = AttentionState.DEPLETED
        else:
            new_state = AttentionState.AVAILABLE
            
        # Update state if changed
        if new_state != self.current_state:
            self._transition_attention_state(new_state)
            
        return self.current_state
        
    def should_allow_interruption(self, priority: InterruptionPriority,
                                context: Dict) -> Tuple[bool, str]:
        """
        Determine if an interruption should be allowed
        
        Returns (allowed, reason)
        """
        current_state = self.assess_attention_state()
        
        # Deep focus - only emergencies
        if current_state == AttentionState.DEEP_FOCUS:
            if priority == InterruptionPriority.EMERGENCY:
                return True, "Emergency override of deep focus"
            else:
                self._queue_notification(priority, context)
                return False, "User in deep focus - notification queued"
                
        # Focused - high priority or above
        elif current_state == AttentionState.FOCUSED:
            if priority.value >= InterruptionPriority.HIGH.value:
                return self._check_interruption_budget(priority, context)
            else:
                self._queue_notification(priority, context)
                return False, "User focused - only high priority interruptions allowed"
                
        # Scattered - be very careful
        elif current_state == AttentionState.SCATTERED:
            if priority.value >= InterruptionPriority.HIGH.value:
                # Only if it helps refocus
                if context.get('helps_focus', False):
                    return True, "Interruption may help refocus scattered attention"
            return False, "User's attention is scattered - avoiding additional interruptions"
            
        # Depleted - no interruptions except emergency
        elif current_state == AttentionState.DEPLETED:
            if priority == InterruptionPriority.EMERGENCY:
                return True, "Emergency override of depleted state"
            return False, "User's attention is depleted - rest needed"
            
        # Available - check budget
        else:
            return self._check_interruption_budget(priority, context)
            
    def _check_interruption_budget(self, priority: InterruptionPriority,
                                  context: Dict) -> Tuple[bool, str]:
        """Check if we're within interruption budget"""
        # Reset hourly counter if needed
        if self.last_interruption_time:
            time_since = datetime.now() - self.last_interruption_time
            if time_since > timedelta(hours=1):
                self.interruptions_this_hour = 0
                
        # Check budget
        if self.interruptions_this_hour >= self.interruption_budget:
            # High priority can exceed budget slightly
            if priority.value >= InterruptionPriority.HIGH.value:
                if self.interruptions_this_hour < self.interruption_budget + 1:
                    return True, "High priority interruption exceeding budget"
            
            self._queue_notification(priority, context)
            return False, f"Interruption budget exceeded ({self.interruption_budget}/hour)"
            
        # Within budget
        return True, "Within interruption budget"
        
    def record_interruption(self, interruption_type: str,
                          accepted: bool, user_response: Optional[str] = None):
        """Record an interruption event"""
        self.interruptions_this_hour += 1
        self.last_interruption_time = datetime.now()
        
        # Record in attention history
        interruption_record = {
            'type': interruption_type,
            'accepted': accepted,
            'user_response': user_response,
            'attention_state': self.current_state.value,
            'timestamp': datetime.now().isoformat()
        }
        
        self.attention_history.append(interruption_record)
        
        # Update focus tracking
        if self.focus_start_time and accepted:
            focus_duration = (datetime.now() - self.focus_start_time).seconds / 60
            if focus_duration > 10:  # Significant focus session interrupted
                self._record_focus_interruption(focus_duration)
                
        # Record in SKG
        self._record_attention_event('interruption', interruption_record)
        
    def _analyze_interaction_patterns(self) -> Dict:
        """Analyze recent interaction patterns for attention signals"""
        cursor = self.skg.conn.cursor()
        
        # Get recent interactions
        recent = cursor.execute("""
            SELECT properties, created_at
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            AND created_at > datetime('now', '-30 minutes')
            ORDER BY created_at DESC
        """).fetchall()
        
        if not recent:
            return {'pattern': 'no_data'}
            
        # Calculate interaction velocity
        interaction_times = [
            datetime.fromisoformat(r['created_at'].replace(' ', 'T'))
            for r in recent
        ]
        
        if len(interaction_times) > 1:
            # Average time between interactions
            deltas = [
                (interaction_times[i] - interaction_times[i+1]).seconds
                for i in range(len(interaction_times)-1)
            ]
            avg_delta = sum(deltas) / len(deltas)
            
            pattern = {
                'velocity': 'high' if avg_delta < 60 else 'normal',
                'interaction_count': len(recent),
                'avg_seconds_between': avg_delta
            }
        else:
            pattern = {
                'velocity': 'low',
                'interaction_count': len(recent),
                'avg_seconds_between': 0
            }
            
        return pattern
        
    def _is_attention_depleted(self, pattern: Dict) -> bool:
        """Check if attention is depleted based on patterns"""
        # High velocity interactions suggest depletion
        if pattern.get('velocity') == 'high' and pattern.get('interaction_count', 0) > 20:
            return True
            
        # Long session without breaks
        if self.focus_session_count > 3 and not self.suggested_break_time:
            return True
            
        # Check attention history for depletion signals
        recent_interruptions = sum(
            1 for event in self.attention_history[-10:]
            if event.get('type') == 'interruption' and event.get('accepted')
        )
        
        return recent_interruptions > 5
        
    def _transition_attention_state(self, new_state: AttentionState):
        """Handle attention state transitions"""
        old_state = self.current_state
        self.current_state = new_state
        
        # Start focus timer if entering focus
        if new_state in [AttentionState.DEEP_FOCUS, AttentionState.FOCUSED]:
            if not self.focus_start_time:
                self.focus_start_time = datetime.now()
                self.focus_session_count += 1
                
        # Stop focus timer if leaving focus
        elif old_state in [AttentionState.DEEP_FOCUS, AttentionState.FOCUSED]:
            if self.focus_start_time:
                duration = (datetime.now() - self.focus_start_time).seconds / 60
                self._record_focus_session(duration)
                self.focus_start_time = None
                
        # Suggest break if depleted
        if new_state == AttentionState.DEPLETED:
            self.suggested_break_time = datetime.now() + timedelta(minutes=15)
            
        # Log transition
        self._record_attention_event('state_transition', {
            'from': old_state.value,
            'to': new_state.value,
            'timestamp': datetime.now().isoformat()
        })
        
    def _queue_notification(self, priority: InterruptionPriority, context: Dict):
        """Queue a notification for later delivery"""
        self.pending_notifications.append({
            'priority': priority,
            'context': context,
            'queued_at': datetime.now().isoformat()
        })
        
        # Sort by priority
        self.pending_notifications.sort(
            key=lambda x: x['priority'].value,
            reverse=True
        )
        
    def get_pending_notifications(self) -> List[Dict]:
        """Get pending notifications that can now be delivered"""
        current_state = self.assess_attention_state()
        
        deliverable = []
        
        if current_state == AttentionState.AVAILABLE:
            # Deliver all pending
            deliverable = self.pending_notifications
            self.pending_notifications = []
            
        elif current_state == AttentionState.FOCUSED:
            # Deliver high priority only
            deliverable = [
                n for n in self.pending_notifications
                if n['priority'].value >= InterruptionPriority.HIGH.value
            ]
            self.pending_notifications = [
                n for n in self.pending_notifications
                if n['priority'].value < InterruptionPriority.HIGH.value
            ]
            
        return deliverable
        
    def suggest_break(self) -> Optional[Dict]:
        """Suggest a break if needed"""
        if self.suggested_break_time and datetime.now() >= self.suggested_break_time:
            suggestion = {
                'type': 'rest_break',
                'duration_minutes': 15,
                'reason': self._get_break_reason(),
                'activities': self._suggest_break_activities()
            }
            
            # Reset suggestion
            self.suggested_break_time = None
            
            return suggestion
            
        # Check if focus session is too long
        if self.focus_start_time:
            focus_duration = (datetime.now() - self.focus_start_time).seconds / 60
            if focus_duration > 90:  # 90 minute focus limit
                return {
                    'type': 'focus_break',
                    'duration_minutes': 10,
                    'reason': 'Extended focus session - your brain needs a break',
                    'activities': ['stretch', 'hydrate', 'look at something distant']
                }
                
        return None
        
    def _get_break_reason(self) -> str:
        """Get reason for break suggestion"""
        if self.current_state == AttentionState.DEPLETED:
            return "Your attention is depleted and needs restoration"
        elif self.focus_session_count > 3:
            return "You've had multiple focus sessions - time for a longer break"
        else:
            return "Regular breaks maintain sustainable productivity"
            
    def _suggest_break_activities(self) -> List[str]:
        """Suggest break activities based on state"""
        if self.current_state == AttentionState.DEPLETED:
            return [
                'Take a walk outside',
                'Do some gentle stretching',
                'Practice breathing exercises',
                'Listen to calming music'
            ]
        else:
            return [
                'Stand and stretch',
                'Get a drink of water',
                'Look out a window',
                'Do a brief meditation'
            ]
            
    def _record_focus_session(self, duration_minutes: float):
        """Record a completed focus session"""
        session_record = {
            'duration_minutes': duration_minutes,
            'quality': self._assess_focus_quality(duration_minutes),
            'ended_by': 'natural' if duration_minutes > 25 else 'interrupted',
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_attention_event('focus_session', session_record)
        
    def _record_focus_interruption(self, duration_minutes: float):
        """Record an interrupted focus session"""
        interruption_record = {
            'duration_before_interruption': duration_minutes,
            'potential_loss_minutes': max(0, 90 - duration_minutes),
            'timestamp': datetime.now().isoformat()
        }
        
        self._record_attention_event('focus_interruption', interruption_record)
        
    def _assess_focus_quality(self, duration: float) -> str:
        """Assess quality of focus session"""
        if duration < 15:
            return 'shallow'
        elif duration < 45:
            return 'moderate'
        elif duration < 90:
            return 'deep'
        else:
            return 'extended'
            
    def _record_attention_event(self, event_type: str, data: Dict):
        """Record attention event in knowledge graph"""
        event_id = f"attention_{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', ?, ?)
        """, (
            event_id,
            f'attention_{event_type}',
            json.dumps(data)
        ))
        
        self.skg.conn.commit()
        
    def get_attention_report(self) -> Dict:
        """Generate comprehensive attention report"""
        # Calculate focus metrics
        total_focus_time = sum(
            event.get('duration_minutes', 0)
            for event in self.attention_history
            if event.get('type') == 'focus_session'
        )
        
        # Calculate interruption metrics
        total_interruptions = sum(
            1 for event in self.attention_history
            if event.get('type') == 'interruption'
        )
        
        accepted_interruptions = sum(
            1 for event in self.attention_history
            if event.get('type') == 'interruption' and event.get('accepted')
        )
        
        return {
            'current_state': self.current_state.value,
            'total_focus_minutes': total_focus_time,
            'focus_sessions': self.focus_session_count,
            'interruptions': {
                'total': total_interruptions,
                'accepted': accepted_interruptions,
                'rejected': total_interruptions - accepted_interruptions,
                'this_hour': self.interruptions_this_hour
            },
            'pending_notifications': len(self.pending_notifications),
            'recommendations': self._generate_attention_recommendations()
        }
        
    def _generate_attention_recommendations(self) -> List[str]:
        """Generate recommendations for attention management"""
        recommendations = []
        
        if self.current_state == AttentionState.SCATTERED:
            recommendations.append("Consider breaking your current task into smaller pieces")
            recommendations.append("Try a 5-minute meditation to refocus")
            
        elif self.current_state == AttentionState.DEPLETED:
            recommendations.append("Your attention needs rest - take a real break")
            recommendations.append("Avoid complex tasks until you've recovered")
            
        if self.interruptions_this_hour > 2:
            recommendations.append("You're being interrupted frequently - consider focus mode")
            
        if self.focus_session_count > 4:
            recommendations.append("Great focus today! Remember to balance with restoration")
            
        return recommendations