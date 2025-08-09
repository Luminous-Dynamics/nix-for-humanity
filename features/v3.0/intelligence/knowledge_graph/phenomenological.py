"""
from typing import Tuple, List
Phenomenological Layer - User's subjective experience modeling

This layer models the user's internal state:
- Cognitive load and flow states
- Emotional/affective states
- Learning progress and struggles
- Goals and intentions
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math


class PhenomenologicalLayer:
    """
    Models the user's subjective, lived experience.
    This is the AI's answer to "What is it like to be you?"
    """
    
    def __init__(self, conn):
        self.conn = conn
        self._init_schema()
        self._init_user_model()
        
    def _init_schema(self):
        """Initialize phenomenological-specific schema elements"""
        cursor = self.conn.cursor()
        
        # Create indices for user state queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_phenom_user_states
            ON nodes(type, created_at) WHERE layer = 'phenomenological'
        """)
        
        self.conn.commit()
        
    def _init_user_model(self):
        """Initialize the base user model if not exists"""
        cursor = self.conn.cursor()
        
        # Check if user model exists
        user = cursor.execute("""
            SELECT id FROM nodes 
            WHERE layer = 'phenomenological' 
            AND type = 'user_model'
            LIMIT 1
        """).fetchone()
        
        if not user:
            # Create initial user model
            cursor.execute("""
                INSERT INTO nodes (id, layer, type, properties)
                VALUES ('user_primary', 'phenomenological', 'user_model', ?)
            """, (
                json.dumps({
                    'expertise_level': 'beginner',
                    'learning_style': 'unknown',
                    'preferred_pace': 'moderate',
                    'current_goals': []
                }),
            ))
            self.conn.commit()
            
    def infer_cognitive_state(self, event_pattern: Dict) -> str:
        """
        Infer user's cognitive state from behavioral patterns
        
        This implements computational phenomenology - inferring internal
        states from observable behaviors
        """
        state_id = f"cognitive_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze patterns to infer state
        cognitive_load = self._calculate_cognitive_load(event_pattern)
        flow_level = self._calculate_flow_level(event_pattern)
        frustration = self._calculate_frustration_level(event_pattern)
        
        properties = {
            'cognitive_load': cognitive_load,
            'flow_level': flow_level,
            'frustration_level': frustration,
            'inferred_from': event_pattern,
            'timestamp': datetime.now().isoformat()
        }
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'phenomenological', 'cognitive_state', ?)
        """, (state_id, json.dumps(properties)))
        
        # Link to user model
        edge_id = f"edge_state_{state_id}_user"
        cursor.execute("""
            INSERT INTO edges (id, type, from_node, to_node, properties)
            VALUES (?, 'IS_STATE_OF', ?, 'user_primary', ?)
        """, (
            edge_id,
            state_id,
            json.dumps({'current': True})
        ))
        
        self.conn.commit()
        return state_id
        
    def _calculate_cognitive_load(self, pattern: Dict) -> float:
        """Calculate cognitive load from behavioral patterns"""
        # Factors that increase cognitive load
        error_rate = pattern.get('error_rate', 0)
        task_switches = pattern.get('context_switches', 0)
        help_queries = pattern.get('help_requests', 0)
        
        # Normalize to 0-1 scale
        load = min(1.0, (error_rate * 0.4 + 
                        task_switches * 0.01 + 
                        help_queries * 0.1))
        
        return load
        
    def _calculate_flow_level(self, pattern: Dict) -> float:
        """Calculate flow state level from patterns"""
        # Factors indicating flow state
        uninterrupted_time = pattern.get('uninterrupted_minutes', 0)
        success_rate = pattern.get('success_rate', 0)
        input_rate = pattern.get('keypress_rate', 0)
        
        # Flow is high with sustained, successful, active work
        flow = min(1.0, (
            (min(uninterrupted_time, 60) / 60) * 0.4 +
            success_rate * 0.4 +
            (min(input_rate, 100) / 100) * 0.2
        ))
        
        return flow
        
    def _calculate_frustration_level(self, pattern: Dict) -> float:
        """Calculate frustration from error patterns"""
        # Rapid repeated errors indicate frustration
        repeated_errors = pattern.get('repeated_error_count', 0)
        error_velocity = pattern.get('errors_per_minute', 0)
        
        frustration = min(1.0, (
            repeated_errors * 0.1 +
            error_velocity * 0.2
        ))
        
        return frustration
        
    def record_struggle_point(self, concept_id: str, 
                            intensity: float = 0.5) -> str:
        """Record that user is struggling with a concept"""
        struggle_id = f"struggle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'phenomenological', 'struggle_point', ?)
        """, (
            struggle_id,
            json.dumps({
                'intensity': intensity,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        # Link to concept
        edge_id = f"edge_struggle_{struggle_id}_{concept_id}"
        cursor.execute("""
            INSERT INTO edges (id, type, from_node, to_node, properties)
            VALUES (?, 'STRUGGLED_WITH', ?, ?, ?)
        """, (
            edge_id,
            struggle_id,
            concept_id,
            json.dumps({'intensity': intensity})
        ))
        
        self.conn.commit()
        return struggle_id
        
    def record_mastery_moment(self, concept_id: str,
                            confidence: float = 0.8) -> str:
        """Record that user has mastered a concept"""
        mastery_id = f"mastery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'phenomenological', 'mastery_milestone', ?)
        """, (
            mastery_id,
            json.dumps({
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        # Link to concept
        edge_id = f"edge_mastery_{mastery_id}_{concept_id}"
        cursor.execute("""
            INSERT INTO edges (id, type, from_node, to_node, properties)
            VALUES (?, 'MASTERED', ?, ?, ?)
        """, (
            edge_id,
            mastery_id,
            concept_id,
            json.dumps({'confidence': confidence})
        ))
        
        self.conn.commit()
        return mastery_id
        
    def get_current_user_state(self) -> Dict:
        """Get the user's current cognitive and affective state"""
        cursor = self.conn.cursor()
        
        # Get most recent cognitive state
        state = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'phenomenological'
            AND type = 'cognitive_state'
            ORDER BY created_at DESC
            LIMIT 1
        """).fetchone()
        
        if state:
            return json.loads(state['properties'])
            
        return {
            'cognitive_load': 0.3,
            'flow_level': 0.0,
            'frustration_level': 0.0
        }
        
    def get_learning_trajectory(self) -> List[Dict]:
        """Get the user's learning trajectory over time"""
        cursor = self.conn.cursor()
        
        # Get all mastery and struggle events
        results = cursor.execute("""
            SELECT 
                n.type,
                n.properties,
                n.created_at,
                e.to_node as concept_id
            FROM nodes n
            JOIN edges e ON n.id = e.from_node
            WHERE n.layer = 'phenomenological'
            AND n.type IN ('struggle_point', 'mastery_milestone')
            ORDER BY n.created_at
        """).fetchall()
        
        trajectory = []
        for row in results:
            event = {
                'type': row['type'],
                'concept': row['concept_id'],
                'timestamp': row['created_at'],
                'properties': json.loads(row['properties'])
            }
            trajectory.append(event)
            
        return trajectory
        
    def should_offer_help(self) -> Tuple[bool, str]:
        """Determine if the AI should proactively offer help"""
        current_state = self.get_current_user_state()
        
        # High cognitive load + low flow = likely needs help
        if (current_state['cognitive_load'] > 0.7 and 
            current_state['flow_level'] < 0.3):
            return True, "high_cognitive_load"
            
        # High frustration = definitely needs help
        if current_state['frustration_level'] > 0.6:
            return True, "high_frustration"
            
        # In flow = don't interrupt
        if current_state['flow_level'] > 0.7:
            return False, "in_flow_state"
            
        return False, "stable_state"