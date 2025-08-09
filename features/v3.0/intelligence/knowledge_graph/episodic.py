"""
from typing import List, Optional
Episodic Layer - History of user-AI interactions

This layer serves as the AI's long-term memory, storing:
- User commands and queries
- AI responses and actions
- Errors and resolutions
- Learning moments and breakthroughs
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class EpisodicLayer:
    """
    The temporal record of the user-AI relationship.
    This is the shared journey log that enables learning from past experience.
    """
    
    def __init__(self, conn):
        self.conn = conn
        self._init_schema()
        
    def _init_schema(self):
        """Initialize episodic-specific schema elements"""
        cursor = self.conn.cursor()
        
        # Create indices for temporal queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodic_time 
            ON nodes(created_at) WHERE layer = 'episodic'
        """)
        
        # Create a view for interaction sequences
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS interaction_sequence AS
            SELECT 
                n.id,
                n.properties,
                n.created_at,
                e.type as next_type,
                e.to_node as next_id
            FROM nodes n
            LEFT JOIN edges e ON n.id = e.from_node AND e.type = 'FOLLOWED_BY'
            WHERE n.layer = 'episodic'
            ORDER BY n.created_at
        """)
        
        self.conn.commit()
        
    def record_interaction(self, user_input: str, ai_response: str,
                         interaction_type: str = 'query',
                         metadata: Optional[Dict] = None) -> str:
        """Record a user-AI interaction"""
        interaction_id = f"interaction_{uuid.uuid4().hex[:8]}"
        
        properties = {
            'user_input': user_input,
            'ai_response': ai_response,
            'type': interaction_type,
            'timestamp': datetime.now().isoformat()
        }
        
        if metadata:
            properties.update(metadata)
            
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'episodic', 'interaction', ?)
        """, (
            interaction_id,
            json.dumps(properties)
        ))
        
        # Link to previous interaction if exists
        last_interaction = cursor.execute("""
            SELECT id FROM nodes 
            WHERE layer = 'episodic' 
            AND type = 'interaction'
            AND id != ?
            ORDER BY created_at DESC 
            LIMIT 1
        """, (interaction_id,)).fetchone()
        
        if last_interaction:
            edge_id = f"edge_sequence_{last_interaction['id']}_{interaction_id}"
            cursor.execute("""
                INSERT INTO edges (id, type, from_node, to_node, properties)
                VALUES (?, 'FOLLOWED_BY', ?, ?, ?)
            """, (
                edge_id,
                last_interaction['id'],
                interaction_id,
                json.dumps({'temporal': True})
            ))
            
        self.conn.commit()
        return interaction_id
        
    def record_error(self, error_message: str, context: Dict,
                    interaction_id: Optional[str] = None) -> str:
        """Record an error event"""
        error_id = f"error_{uuid.uuid4().hex[:8]}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'episodic', 'error', ?)
        """, (
            error_id,
            json.dumps({
                'message': error_message,
                'context': context,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        # Link to interaction if provided
        if interaction_id:
            edge_id = f"edge_error_{interaction_id}_{error_id}"
            cursor.execute("""
                INSERT INTO edges (id, type, from_node, to_node, properties)
                VALUES (?, 'RESULTED_IN', ?, ?, ?)
            """, (
                edge_id,
                interaction_id,
                error_id,
                json.dumps({'error_type': 'execution'})
            ))
            
        self.conn.commit()
        return error_id
        
    def record_resolution(self, error_id: str, solution: str,
                         success: bool = True) -> str:
        """Record how an error was resolved"""
        resolution_id = f"resolution_{uuid.uuid4().hex[:8]}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'episodic', 'resolution', ?)
        """, (
            resolution_id,
            json.dumps({
                'solution': solution,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        # Link error to resolution
        edge_id = f"edge_resolved_{error_id}_{resolution_id}"
        cursor.execute("""
            INSERT INTO edges (id, type, from_node, to_node, properties)
            VALUES (?, 'RESOLVED_BY', ?, ?, ?)
        """, (
            edge_id,
            error_id,
            resolution_id,
            json.dumps({'repair_time': datetime.now().isoformat()})
        ))
        
        self.conn.commit()
        return resolution_id
        
    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """Get recent interactions in chronological order"""
        cursor = self.conn.cursor()
        
        results = cursor.execute("""
            SELECT id, properties, created_at
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [
            {
                'id': row['id'],
                'properties': json.loads(row['properties']),
                'created_at': row['created_at']
            }
            for row in results
        ]
        
    def find_similar_errors(self, error_context: Dict, limit: int = 5) -> List[Dict]:
        """Find similar past errors and their resolutions"""
        cursor = self.conn.cursor()
        
        # Simple similarity based on error type
        # In production, this would use vector similarity
        results = cursor.execute("""
            SELECT 
                e.properties as error,
                r.properties as resolution
            FROM nodes e
            LEFT JOIN edges edge ON e.id = edge.from_node
            LEFT JOIN nodes r ON edge.to_node = r.id
            WHERE e.layer = 'episodic'
            AND e.type = 'error'
            AND edge.type = 'RESOLVED_BY'
            ORDER BY e.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [
            {
                'error': json.loads(row['error']),
                'resolution': json.loads(row['resolution']) if row['resolution'] else None
            }
            for row in results
        ]
        
    def calculate_error_recovery_stats(self) -> Dict:
        """Calculate statistics about error recovery efficiency"""
        cursor = self.conn.cursor()
        
        # Count total errors and resolved errors
        total_errors = cursor.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE layer = 'episodic' AND type = 'error'
        """).fetchone()[0]
        
        resolved_errors = cursor.execute("""
            SELECT COUNT(DISTINCT e.id)
            FROM nodes e
            JOIN edges edge ON e.id = edge.from_node
            WHERE e.layer = 'episodic' 
            AND e.type = 'error'
            AND edge.type = 'RESOLVED_BY'
        """).fetchone()[0]
        
        return {
            'total_errors': total_errors,
            'resolved_errors': resolved_errors,
            'resolution_rate': resolved_errors / total_errors if total_errors > 0 else 0,
            'unresolved_errors': total_errors - resolved_errors
        }