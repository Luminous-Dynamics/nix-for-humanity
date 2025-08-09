"""
from typing import Tuple, List
Interruption Calculus - Mathematical framework for interruption decisions

Based on research showing interruptions have significant cognitive costs,
this module implements a calculus for determining when interruptions are justified.
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


@dataclass
class InterruptionCost:
    """Components of interruption cost"""
    context_switch_cost: float  # Cost of switching mental context
    recovery_time_cost: float  # Time to return to previous state
    flow_disruption_cost: float  # Loss of flow state
    stress_induction_cost: float  # Added stress/frustration
    trust_erosion_cost: float  # Damage to user trust
    total_cost: float  # Aggregate cost


@dataclass
class InterruptionValue:
    """Value provided by the interruption"""
    urgency_value: float  # How time-critical
    importance_value: float  # Long-term significance
    prevention_value: float  # Prevents future problems
    learning_value: float  # Educational benefit
    safety_value: float  # Prevents harm/errors
    total_value: float  # Aggregate value


class InterruptionType(Enum):
    """Types of potential interruptions"""
    ERROR_PREVENTION = "error_prevention"
    LEARNING_OPPORTUNITY = "learning_opportunity"
    SYSTEM_UPDATE = "system_update"
    SUGGESTION = "suggestion"
    SOCIAL = "social"
    MAINTENANCE = "maintenance"


class InterruptionCalculus:
    """
    Implements mathematical decision framework for interruptions
    
    Core principle: Interrupt only when Value > Cost + Threshold
    
    Based on research showing:
    1. Interruptions cost 23 minutes of recovery time on average
    2. Flow state interruptions are especially costly
    3. Context switches degrade performance
    4. Trust erodes with poor interruption decisions
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg
        
        # Cost parameters (calibrated from research)
        self.base_context_switch_cost = 0.3  # Base cost of any interruption
        self.flow_multiplier = 3.0  # Flow interruptions are 3x more costly
        self.recovery_time_minutes = 23  # Average from research
        self.trust_erosion_rate = 0.1  # Per poor interruption
        
        # Value parameters
        self.urgency_decay_rate = 0.5  # How quickly urgency decreases
        self.learning_bonus = 0.2  # Bonus for educational interruptions
        
        # Decision threshold
        self.interruption_threshold = 0.2  # Value must exceed cost by 20%
        
        # History tracking
        self.interruption_history = []
        self.decision_accuracy = []
        
    def should_interrupt(self, interruption_type: InterruptionType,
                        content: Dict, context: Dict) -> Tuple[bool, Dict]:
        """
        Calculate whether an interruption is justified
        
        Returns (should_interrupt, decision_details)
        """
        # Calculate interruption cost
        cost = self._calculate_interruption_cost(context)
        
        # Calculate interruption value
        value = self._calculate_interruption_value(interruption_type, content, context)
        
        # Apply decision threshold
        net_benefit = value.total_value - cost.total_cost
        should_interrupt = net_benefit > self.interruption_threshold
        
        # Calculate optimal timing if not immediate
        optimal_timing = self._calculate_optimal_timing(
            cost, value, context
        ) if not should_interrupt else None
        
        # Create decision record
        decision = {
            'should_interrupt': should_interrupt,
            'cost': cost,
            'value': value,
            'net_benefit': net_benefit,
            'optimal_timing': optimal_timing,
            'reasoning': self._generate_reasoning(cost, value, should_interrupt),
            'confidence': self._calculate_decision_confidence(net_benefit),
            'timestamp': datetime.now().isoformat()
        }
        
        # Record decision
        self._record_interruption_decision(decision, interruption_type, content)
        
        return should_interrupt, decision
        
    def _calculate_interruption_cost(self, context: Dict) -> InterruptionCost:
        """Calculate the full cost of interrupting now"""
        # Base context switch cost
        context_switch_cost = self.base_context_switch_cost
        
        # Get current user state
        user_state = context.get('user_state', {})
        flow_level = user_state.get('flow_level', 0)
        cognitive_load = user_state.get('cognitive_load', 0.5)
        frustration = user_state.get('frustration_level', 0)
        
        # Flow disruption cost (exponential with flow level)
        flow_disruption_cost = (flow_level ** 2) * self.flow_multiplier
        
        # Recovery time cost (in normalized units)
        recovery_time_cost = (self.recovery_time_minutes / 60) * (1 + cognitive_load)
        
        # Stress induction cost
        stress_induction_cost = 0.1 + (frustration * 0.3)
        
        # Trust erosion cost (based on recent poor interruptions)
        recent_poor_interruptions = self._count_recent_poor_interruptions()
        trust_erosion_cost = recent_poor_interruptions * self.trust_erosion_rate
        
        # Total cost
        total_cost = (
            context_switch_cost +
            flow_disruption_cost +
            recovery_time_cost +
            stress_induction_cost +
            trust_erosion_cost
        )
        
        return InterruptionCost(
            context_switch_cost=context_switch_cost,
            recovery_time_cost=recovery_time_cost,
            flow_disruption_cost=flow_disruption_cost,
            stress_induction_cost=stress_induction_cost,
            trust_erosion_cost=trust_erosion_cost,
            total_cost=total_cost
        )
        
    def _calculate_interruption_value(self, interruption_type: InterruptionType,
                                    content: Dict, context: Dict) -> InterruptionValue:
        """Calculate the value provided by this interruption"""
        # Base values by type
        type_values = {
            InterruptionType.ERROR_PREVENTION: {
                'urgency': 0.8, 'importance': 0.9, 'prevention': 1.0, 'safety': 0.9
            },
            InterruptionType.LEARNING_OPPORTUNITY: {
                'urgency': 0.3, 'importance': 0.7, 'learning': 0.9
            },
            InterruptionType.SYSTEM_UPDATE: {
                'urgency': 0.5, 'importance': 0.6, 'prevention': 0.4
            },
            InterruptionType.SUGGESTION: {
                'urgency': 0.2, 'importance': 0.4, 'learning': 0.5
            },
            InterruptionType.SOCIAL: {
                'urgency': 0.1, 'importance': 0.3
            },
            InterruptionType.MAINTENANCE: {
                'urgency': 0.4, 'importance': 0.5, 'prevention': 0.6
            }
        }
        
        base_values = type_values.get(interruption_type, {})
        
        # Adjust for specific content
        urgency_value = base_values.get('urgency', 0.3)
        importance_value = base_values.get('importance', 0.5)
        prevention_value = base_values.get('prevention', 0.0)
        learning_value = base_values.get('learning', 0.0)
        safety_value = base_values.get('safety', 0.0)
        
        # Modify based on content specifics
        if content.get('prevents_data_loss'):
            safety_value = max(safety_value, 0.95)
            urgency_value = max(urgency_value, 0.9)
            
        if content.get('fixes_current_problem'):
            importance_value = max(importance_value, 0.8)
            urgency_value = max(urgency_value, 0.7)
            
        if content.get('educational_moment'):
            learning_value += self.learning_bonus
            
        # Apply time decay to urgency
        if 'created_at' in content:
            age_minutes = (datetime.now() - datetime.fromisoformat(
                content['created_at']
            )).seconds / 60
            urgency_value *= math.exp(-self.urgency_decay_rate * age_minutes / 60)
            
        # User-specific adjustments
        user_state = context.get('user_state', {})
        if user_state.get('learning_desire', 0.5) > 0.7:
            learning_value *= 1.5
            
        if user_state.get('urgency_level', 0.5) > 0.7:
            # User is in a hurry - only high urgency matters
            if urgency_value < 0.7:
                urgency_value *= 0.5
                
        # Calculate total value
        total_value = (
            urgency_value * 0.3 +
            importance_value * 0.25 +
            prevention_value * 0.2 +
            learning_value * 0.15 +
            safety_value * 0.1
        )
        
        return InterruptionValue(
            urgency_value=urgency_value,
            importance_value=importance_value,
            prevention_value=prevention_value,
            learning_value=learning_value,
            safety_value=safety_value,
            total_value=total_value
        )
        
    def _calculate_optimal_timing(self, cost: InterruptionCost,
                                value: InterruptionValue,
                                context: Dict) -> Dict:
        """Calculate when this interruption should ideally occur"""
        # Get flow state information
        flow_state = context.get('flow_state', {})
        flow_level = flow_state.get('flow_level', 0)
        
        # If in flow, calculate natural break point
        if flow_level > 0.6:
            interruption_window = flow_state.get('optimal_interruption_window', {})
            wait_minutes = interruption_window.get('wait_minutes', 30)
            
            return {
                'timing': 'wait_for_natural_break',
                'wait_minutes': wait_minutes,
                'reason': interruption_window.get('reason', 'User in flow state')
            }
            
        # If urgency is high but not critical
        elif value.urgency_value > 0.5 and value.urgency_value < 0.8:
            return {
                'timing': 'next_transition',
                'wait_minutes': 5,
                'reason': 'Wait for next natural transition point'
            }
            
        # If low urgency and high cognitive load
        elif value.urgency_value < 0.3 and context.get('cognitive_load', 0) > 0.7:
            return {
                'timing': 'defer_to_break',
                'wait_minutes': 15,
                'reason': 'User under high cognitive load'
            }
            
        else:
            return {
                'timing': 'soon',
                'wait_minutes': 2,
                'reason': 'Brief delay for graceful interruption'
            }
            
    def _generate_reasoning(self, cost: InterruptionCost,
                          value: InterruptionValue,
                          should_interrupt: bool) -> str:
        """Generate human-readable reasoning for the decision"""
        if should_interrupt:
            if value.safety_value > 0.8:
                return "Critical safety issue justifies immediate interruption"
            elif value.urgency_value > 0.7:
                return "High urgency outweighs interruption cost"
            elif cost.total_cost < 0.3:
                return "Low interruption cost makes this acceptable"
            else:
                return f"Value ({value.total_value:.2f}) exceeds cost ({cost.total_cost:.2f})"
        else:
            if cost.flow_disruption_cost > 1.0:
                return "User in deep flow - interruption would be too costly"
            elif value.total_value < 0.3:
                return "Interruption value too low to justify"
            elif cost.trust_erosion_cost > 0.3:
                return "Recent poor interruptions - protecting trust"
            else:
                return f"Cost ({cost.total_cost:.2f}) exceeds value ({value.total_value:.2f})"
                
    def _calculate_decision_confidence(self, net_benefit: float) -> float:
        """Calculate confidence in the interruption decision"""
        # Higher absolute net benefit = higher confidence
        confidence = min(1.0, abs(net_benefit) * 2)
        
        # Adjust based on decision history accuracy
        if self.decision_accuracy:
            historical_accuracy = sum(self.decision_accuracy[-10:]) / len(self.decision_accuracy[-10:])
            confidence *= (0.5 + 0.5 * historical_accuracy)
            
        return confidence
        
    def _count_recent_poor_interruptions(self) -> int:
        """Count recent interruptions that were poorly received"""
        recent_cutoff = datetime.now() - timedelta(hours=1)
        
        poor_count = 0
        for record in self.interruption_history[-20:]:  # Last 20 interruptions
            if 'user_feedback' in record:
                if record['user_feedback'] == 'negative':
                    timestamp = datetime.fromisoformat(record['timestamp'])
                    if timestamp > recent_cutoff:
                        poor_count += 1
                        
        return poor_count
        
    def _record_interruption_decision(self, decision: Dict,
                                    interruption_type: InterruptionType,
                                    content: Dict):
        """Record interruption decision for learning"""
        record = {
            'decision': decision,
            'type': interruption_type.value,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.interruption_history.append(record)
        
        # Record in SKG
        decision_id = f"interruption_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'interruption_decision', ?)
        """, (
            decision_id,
            json.dumps(record)
        ))
        
        self.skg.conn.commit()
        
    def record_interruption_outcome(self, decision_id: str,
                                  user_reaction: str,
                                  value_realized: bool):
        """
        Record how the interruption was received
        
        This enables learning from decisions
        """
        # Find the decision record
        for record in self.interruption_history:
            if decision_id in record.get('timestamp', ''):
                record['user_feedback'] = user_reaction
                record['value_realized'] = value_realized
                
                # Update decision accuracy
                predicted_value = record['decision']['should_interrupt']
                actual_value = user_reaction == 'positive' and value_realized
                self.decision_accuracy.append(1 if predicted_value == actual_value else 0)
                
                break
                
        # Learn from outcome
        self._learn_from_outcome(user_reaction, value_realized)
        
    def _learn_from_outcome(self, user_reaction: str, value_realized: bool):
        """Adjust parameters based on interruption outcomes"""
        if user_reaction == 'negative' and not value_realized:
            # Interruption was poor - increase threshold
            self.interruption_threshold *= 1.1
            
        elif user_reaction == 'positive' and value_realized:
            # Good interruption - slightly decrease threshold
            self.interruption_threshold *= 0.95
            
        # Keep threshold in reasonable bounds
        self.interruption_threshold = max(0.1, min(0.5, self.interruption_threshold))
        
    def get_interruption_analytics(self) -> Dict:
        """Get analytics on interruption decisions"""
        if not self.interruption_history:
            return {'status': 'no_interruption_history'}
            
        # Calculate metrics
        total_interruptions = len(self.interruption_history)
        allowed_interruptions = sum(
            1 for r in self.interruption_history
            if r['decision']['should_interrupt']
        )
        
        # Outcome analysis
        with_feedback = [
            r for r in self.interruption_history
            if 'user_feedback' in r
        ]
        
        positive_outcomes = sum(
            1 for r in with_feedback
            if r['user_feedback'] == 'positive'
        )
        
        # Type analysis
        type_distribution = {}
        for record in self.interruption_history:
            int_type = record['type']
            type_distribution[int_type] = type_distribution.get(int_type, 0) + 1
            
        # Cost-value analysis
        avg_cost = np.mean([
            r['decision']['cost']['total_cost']
            for r in self.interruption_history
        ])
        
        avg_value = np.mean([
            r['decision']['value']['total_value']
            for r in self.interruption_history
        ])
        
        return {
            'total_decisions': total_interruptions,
            'interruptions_allowed': allowed_interruptions,
            'interruption_rate': allowed_interruptions / total_interruptions if total_interruptions > 0 else 0,
            'positive_outcome_rate': positive_outcomes / len(with_feedback) if with_feedback else 0,
            'decision_accuracy': sum(self.decision_accuracy) / len(self.decision_accuracy) if self.decision_accuracy else 0,
            'type_distribution': type_distribution,
            'average_cost': avg_cost,
            'average_value': avg_value,
            'current_threshold': self.interruption_threshold,
            'recommendations': self._generate_interruption_recommendations()
        }
        
    def _generate_interruption_recommendations(self) -> List[str]:
        """Generate recommendations for interruption strategy"""
        recommendations = []
        
        if self.decision_accuracy and sum(self.decision_accuracy[-10:]) / len(self.decision_accuracy[-10:]) < 0.6:
            recommendations.append("Decision accuracy is low - consider adjusting value calculations")
            
        if self.interruption_threshold > 0.4:
            recommendations.append("High interruption threshold - user may be missing valuable interruptions")
            
        recent_poor = self._count_recent_poor_interruptions()
        if recent_poor > 2:
            recommendations.append("Multiple poor interruptions recently - be more conservative")
            
        return recommendations