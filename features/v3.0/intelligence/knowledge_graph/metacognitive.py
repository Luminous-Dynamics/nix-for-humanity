"""
from typing import List, Dict, Optional
Metacognitive Layer - AI's self-awareness and introspection

This layer enables the AI to:
- Model its own capabilities and limitations
- Track its decision-making processes
- Learn from its own performance
- Explain its reasoning transparently
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from functools import wraps
import traceback


class MetacognitiveLayer:
    """
    The AI's model of itself - enabling self-awareness,
    self-explanation, and self-improvement.
    """
    
    def __init__(self, conn):
        self.conn = conn
        self._init_schema()
        self._init_self_model()
        
    def _init_schema(self):
        """Initialize metacognitive-specific schema elements"""
        cursor = self.conn.cursor()
        
        # Create indices for performance analysis
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metacog_activations
            ON nodes(type, created_at) WHERE layer = 'metacognitive'
        """)
        
        # View for analyzing component performance
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS component_performance AS
            SELECT 
                json_extract(properties, '$.component') as component,
                json_extract(properties, '$.execution_time') as exec_time,
                json_extract(properties, '$.success') as success,
                created_at
            FROM nodes
            WHERE layer = 'metacognitive'
            AND type = 'activation'
        """)
        
        self.conn.commit()
        
    def _init_self_model(self):
        """Initialize the AI's model of its own architecture"""
        cursor = self.conn.cursor()
        
        # Check if self-model exists
        self_model = cursor.execute("""
            SELECT id FROM nodes 
            WHERE layer = 'metacognitive' 
            AND type = 'self_model'
            LIMIT 1
        """).fetchone()
        
        if not self_model:
            # Create initial self-model
            cursor.execute("""
                INSERT INTO nodes (id, layer, type, properties)
                VALUES ('ai_self_model', 'metacognitive', 'self_model', ?)
            """, (
                json.dumps({
                    'version': '0.5.2',
                    'capabilities': {
                        'natural_language': 0.7,
                        'nix_knowledge': 0.8,
                        'learning_ability': 0.5,
                        'error_recovery': 0.6
                    },
                    'known_limitations': [
                        'Complex multi-step procedures',
                        'Visual/GUI understanding',
                        'Real-time system monitoring'
                    ]
                }),
            ))
            self.conn.commit()
            
    def trace_activation(self, component_name: str):
        """
        Decorator to trace component activations
        
        This is the key to self-awareness - knowing what we're doing
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                activation_id = f"activation_{component_name}_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
                start_time = time.time()
                success = True
                error_msg = None
                result = None
                
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    # Record the activation
                    execution_time = time.time() - start_time
                    self._record_activation(
                        activation_id,
                        component_name,
                        execution_time,
                        success,
                        error_msg
                    )
                    
                return result
            return wrapper
        return decorator
        
    def _record_activation(self, activation_id: str, component: str,
                          execution_time: float, success: bool,
                          error_msg: Optional[str] = None):
        """Record a component activation in the knowledge graph"""
        cursor = self.conn.cursor()
        
        properties = {
            'component': component,
            'execution_time': execution_time,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if error_msg:
            properties['error'] = error_msg
            
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'activation', ?)
        """, (activation_id, json.dumps(properties)))
        
        # Link to component model if exists
        component_id = f"component_{component}"
        component_exists = cursor.execute("""
            SELECT id FROM nodes WHERE id = ? AND layer = 'metacognitive'
        """, (component_id,)).fetchone()
        
        if component_exists:
            edge_id = f"edge_activation_{activation_id}_{component_id}"
            cursor.execute("""
                INSERT INTO edges (id, type, from_node, to_node, properties)
                VALUES (?, 'INSTANCE_OF', ?, ?, ?)
            """, (
                edge_id,
                activation_id,
                component_id,
                json.dumps({'runtime': True})
            ))
            
        self.conn.commit()
        
    def register_component(self, name: str, component_type: str,
                          capabilities: Dict[str, float]) -> str:
        """Register an AI component in the self-model"""
        component_id = f"component_{name}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'ai_component', ?)
        """, (
            component_id,
            json.dumps({
                'name': name,
                'type': component_type,
                'capabilities': capabilities,
                'reliability': 1.0  # Starts optimistic
            })
        ))
        
        self.conn.commit()
        return component_id
        
    def explain_decision(self, decision_id: str, 
                        reasoning_steps: List[Dict]) -> str:
        """Record the reasoning behind a decision for transparency"""
        explanation_id = f"explanation_{decision_id}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'explanation', ?)
        """, (
            explanation_id,
            json.dumps({
                'decision': decision_id,
                'reasoning_steps': reasoning_steps,
                'confidence': self._calculate_confidence(reasoning_steps),
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.conn.commit()
        return explanation_id
        
    def _calculate_confidence(self, reasoning_steps: List[Dict]) -> float:
        """Calculate confidence based on reasoning quality"""
        if not reasoning_steps:
            return 0.0
            
        # Factors that increase confidence
        has_evidence = any('evidence' in step for step in reasoning_steps)
        has_precedent = any('similar_case' in step for step in reasoning_steps)
        clear_logic = len(reasoning_steps) >= 2
        
        confidence = 0.3  # Base confidence
        if has_evidence:
            confidence += 0.3
        if has_precedent:
            confidence += 0.2
        if clear_logic:
            confidence += 0.2
            
        return min(1.0, confidence)
        
    def analyze_performance(self, time_window_hours: int = 24) -> Dict:
        """Analyze the AI's recent performance"""
        cursor = self.conn.cursor()
        
        # Get activation statistics
        stats = cursor.execute("""
            SELECT 
                component,
                COUNT(*) as total_calls,
                AVG(exec_time) as avg_time,
                SUM(CASE WHEN success = 'true' THEN 1 ELSE 0 END) as successes,
                MIN(exec_time) as min_time,
                MAX(exec_time) as max_time
            FROM component_performance
            WHERE datetime(created_at) > datetime('now', '-{} hours')
            GROUP BY component
        """.format(time_window_hours)).fetchall()
        
        performance = {}
        for row in stats:
            performance[row['component']] = {
                'total_calls': row['total_calls'],
                'avg_execution_time': row['avg_time'],
                'success_rate': row['successes'] / row['total_calls'] if row['total_calls'] > 0 else 0,
                'min_time': row['min_time'],
                'max_time': row['max_time']
            }
            
        return performance
        
    def identify_weak_points(self) -> List[Dict]:
        """Identify components or patterns that need improvement"""
        cursor = self.conn.cursor()
        
        # Find components with high failure rates
        weak_components = cursor.execute("""
            SELECT 
                component,
                COUNT(*) as total,
                SUM(CASE WHEN success = 'false' THEN 1 ELSE 0 END) as failures
            FROM component_performance
            GROUP BY component
            HAVING failures > 0.2 * total
        """).fetchall()
        
        weaknesses = []
        for comp in weak_components:
            failure_rate = comp['failures'] / comp['total']
            weaknesses.append({
                'component': comp['component'],
                'failure_rate': failure_rate,
                'recommendation': self._generate_improvement_recommendation(
                    comp['component'], failure_rate
                )
            })
            
        return weaknesses
        
    def _generate_improvement_recommendation(self, component: str, 
                                           failure_rate: float) -> str:
        """Generate recommendations for improving weak components"""
        if failure_rate > 0.5:
            return f"Critical: {component} failing frequently. Consider retraining or redesign."
        elif failure_rate > 0.3:
            return f"Warning: {component} needs attention. Review error patterns."
        else:
            return f"Monitor: {component} showing some failures. Track patterns."
            
    def get_self_assessment(self) -> Dict:
        """Get the AI's assessment of its own capabilities"""
        cursor = self.conn.cursor()
        
        # Get self model
        self_model = cursor.execute("""
            SELECT properties FROM nodes
            WHERE layer = 'metacognitive'
            AND type = 'self_model'
            LIMIT 1
        """).fetchone()
        
        if self_model:
            model = json.loads(self_model['properties'])
            
            # Add performance data
            performance = self.analyze_performance()
            
            return {
                'capabilities': model['capabilities'],
                'known_limitations': model['known_limitations'],
                'recent_performance': performance,
                'weak_points': self.identify_weak_points(),
                'overall_health': self._calculate_overall_health(performance)
            }
            
        return {
            'error': 'Self-model not initialized'
        }
        
    def _calculate_overall_health(self, performance: Dict) -> float:
        """Calculate overall system health score"""
        if not performance:
            return 0.5
            
        # Average success rate across all components
        success_rates = [
            comp['success_rate'] 
            for comp in performance.values()
        ]
        
        if success_rates:
            return sum(success_rates) / len(success_rates)
        return 0.5