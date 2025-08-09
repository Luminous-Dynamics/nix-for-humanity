"""Mock Metrics Collector for testing without heavy dependencies."""

import json
import time
import random
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


from typing import Optional
class MockMetricsCollector:
    """Lightweight mock of Metrics Collector for testing."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.timers = {}
        self.flow_states = deque(maxlen=100)
        self.performance_data = []
        
    def record_interaction(self, interaction: Dict) -> None:
        """Record an interaction metric."""
        timestamp = datetime.now().isoformat()
        
        # Extract metrics from interaction
        metrics_entry = {
            'timestamp': timestamp,
            'type': interaction.get('type', 'unknown'),
            'duration': interaction.get('duration', random.uniform(0.1, 2.0)),
            'success': interaction.get('success', True),
            'user_satisfaction': interaction.get('satisfaction', random.uniform(0.6, 1.0))
        }
        
        self.metrics['interactions'].append(metrics_entry)
        self.counters[f"interaction_{interaction.get('type', 'unknown')}"] += 1
        
    def start_timer(self, name: str) -> None:
        """Start a named timer."""
        self.timers[name] = time.time()
        
    def stop_timer(self, name: str) -> Optional[float]:
        """Stop a named timer and return duration."""
        if name in self.timers:
            duration = time.time() - self.timers[name]
            del self.timers[name]
            
            self.performance_data.append({
                'name': name,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
            return duration
        return None
        
    def record_flow_state(self, state: Dict) -> None:
        """Record flow state measurement."""
        flow_entry = {
            'timestamp': datetime.now().isoformat(),
            'coherence': state.get('coherence', random.uniform(0.5, 0.9)),
            'focus_level': state.get('focus', random.uniform(0.4, 1.0)),
            'interruption_count': state.get('interruptions', 0),
            'productivity_score': state.get('productivity', random.uniform(0.6, 0.95))
        }
        
        self.flow_states.append(flow_entry)
        self.metrics['flow_states'].append(flow_entry)
        
    def calculate_digital_wellbeing_score(self) -> Dict:
        """Calculate Digital Well-being Score."""
        if not self.flow_states:
            return {
                'score': 0.5,
                'components': {
                    'focus': 0.5,
                    'flow': 0.5,
                    'balance': 0.5,
                    'satisfaction': 0.5
                }
            }
            
        # Mock calculation
        recent_states = list(self.flow_states)[-10:]
        
        avg_coherence = sum(s['coherence'] for s in recent_states) / len(recent_states)
        avg_focus = sum(s['focus_level'] for s in recent_states) / len(recent_states)
        avg_productivity = sum(s['productivity_score'] for s in recent_states) / len(recent_states)
        
        # Calculate interruption penalty
        total_interruptions = sum(s['interruption_count'] for s in recent_states)
        interruption_penalty = max(0, 1 - (total_interruptions * 0.1))
        
        # Overall score
        wellbeing_score = (avg_coherence + avg_focus + avg_productivity + interruption_penalty) / 4
        
        return {
            'score': wellbeing_score,
            'components': {
                'focus': avg_focus,
                'flow': avg_coherence,
                'balance': interruption_penalty,
                'satisfaction': avg_productivity
            },
            'trend': 'improving' if wellbeing_score > 0.7 else 'stable'
        }
        
    def get_performance_summary(self) -> Dict:
        """Get performance summary."""
        if not self.performance_data:
            return {
                'average_response_time': 0,
                'p95_response_time': 0,
                'total_operations': 0
            }
            
        durations = [p['duration'] for p in self.performance_data]
        durations.sort()
        
        return {
            'average_response_time': sum(durations) / len(durations),
            'p95_response_time': durations[int(len(durations) * 0.95)] if durations else 0,
            'total_operations': len(durations),
            'fastest_operation': min(durations) if durations else 0,
            'slowest_operation': max(durations) if durations else 0
        }
        
    def get_interaction_summary(self) -> Dict:
        """Get interaction summary."""
        interactions = self.metrics.get('interactions', [])
        
        if not interactions:
            return {
                'total_interactions': 0,
                'success_rate': 0,
                'average_satisfaction': 0,
                'interaction_types': {}
            }
            
        success_count = sum(1 for i in interactions if i.get('success', False))
        satisfaction_scores = [i.get('user_satisfaction', 0) for i in interactions]
        
        # Count by type
        type_counts = defaultdict(int)
        for interaction in interactions:
            type_counts[interaction.get('type', 'unknown')] += 1
            
        return {
            'total_interactions': len(interactions),
            'success_rate': success_count / len(interactions),
            'average_satisfaction': sum(satisfaction_scores) / len(satisfaction_scores),
            'interaction_types': dict(type_counts)
        }
        
    def get_sacred_metrics(self) -> Dict:
        """Get consciousness-first metrics."""
        wellbeing = self.calculate_digital_wellbeing_score()
        
        # Mock sacred metrics
        return {
            'consciousness_coherence': wellbeing['components']['flow'],
            'attention_preservation': wellbeing['components']['focus'],
            'sacred_pause_effectiveness': random.uniform(0.7, 0.95),
            'flow_state_duration': random.uniform(20, 60),  # minutes
            'interruption_recovery_time': random.uniform(1, 5),  # minutes
            'digital_wellbeing_score': wellbeing['score']
        }
        
    def export_metrics(self) -> Dict:
        """Export all metrics."""
        return {
            'summary': {
                'performance': self.get_performance_summary(),
                'interactions': self.get_interaction_summary(),
                'wellbeing': self.calculate_digital_wellbeing_score(),
                'sacred': self.get_sacred_metrics()
            },
            'counters': dict(self.counters),
            'recent_flow_states': list(self.flow_states)[-10:],
            'timestamp': datetime.now().isoformat()
        }
        
    def save_state(self, path: Path) -> None:
        """Save metrics state to file."""
        state = {
            'metrics': dict(self.metrics),
            'counters': dict(self.counters),
            'flow_states': list(self.flow_states),
            'performance_data': self.performance_data[-100:]  # Keep last 100
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(state, f, indent=2, default=str)
            
    def load_state(self, path: Path) -> None:
        """Load metrics state from file."""
        if path.exists():
            with open(path, 'r') as f:
                state = json.load(f)
                self.metrics = defaultdict(list, state.get('metrics', {}))
                self.counters = defaultdict(int, state.get('counters', {}))
                self.flow_states = deque(state.get('flow_states', []), maxlen=100)
                self.performance_data = state.get('performance_data', [])