"""
from typing import List, Dict
Symbiotic Knowledge Graph - Unified four-layer knowledge representation
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Using SQLite as a lightweight alternative to Kùzu for initial implementation
import sqlite3


@dataclass
class GraphNode:
    """Base class for all graph nodes"""
    id: str
    type: str
    properties: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class GraphEdge:
    """Base class for all graph edges"""
    id: str
    type: str
    from_node: str
    to_node: str
    properties: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class SymbioticKnowledgeGraph:
    """
    Four-layer knowledge graph for symbiotic AI
    
    This graph unifies objective knowledge, personal history,
    subjective experience, and self-awareness into a single
    queryable structure.
    """
    
    def __init__(self, db_path: str = "./skg.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Initialize the four layers
        from .ontological import OntologicalLayer
        from .episodic import EpisodicLayer
        from .phenomenological import PhenomenologicalLayer
        from .metacognitive import MetacognitiveLayer
        
        self.ontological = OntologicalLayer(self.conn)
        self.episodic = EpisodicLayer(self.conn)
        self.phenomenological = PhenomenologicalLayer(self.conn)
        self.metacognitive = MetacognitiveLayer(self.conn)
        
        # Create schema
        self._create_schema()
        
        # Initialize cross-layer connections
        self._init_layer_connections()
        
    def _create_schema(self):
        """Create the unified graph schema"""
        cursor = self.conn.cursor()
        
        # Nodes table - stores all nodes from all layers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                layer TEXT NOT NULL,
                type TEXT NOT NULL,
                properties TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Edges table - stores all relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                from_node TEXT NOT NULL,
                to_node TEXT NOT NULL,
                properties TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_node) REFERENCES nodes(id),
                FOREIGN KEY (to_node) REFERENCES nodes(id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_layer ON nodes(layer)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(layer, type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_node)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_node)")
        
        self.conn.commit()
        
    def _init_layer_connections(self):
        """Initialize cross-layer connection patterns"""
        # These define how the layers can connect to each other
        self.cross_layer_patterns = {
            # Episodic events can be linked to ontological concepts
            ('episodic', 'ontological'): ['INVOLVES', 'USES', 'REFERENCES'],
            
            # Phenomenological states can be linked to episodic events
            ('phenomenological', 'episodic'): ['DURING', 'CAUSED_BY', 'FOLLOWED'],
            
            # Phenomenological states can struggle with ontological concepts
            ('phenomenological', 'ontological'): ['STRUGGLED_WITH', 'MASTERED', 'LEARNING'],
            
            # Metacognitive components can analyze any layer
            ('metacognitive', 'ontological'): ['MODELS', 'UNDERSTANDS'],
            ('metacognitive', 'episodic'): ['TRACES', 'ANALYZES'],
            ('metacognitive', 'phenomenological'): ['INFERS', 'PREDICTS']
        }
        
    def add_node(self, layer: str, node: GraphNode) -> str:
        """Add a node to the specified layer"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, ?, ?, ?)
        """, (
            node.id,
            layer,
            node.type,
            json.dumps(node.properties)
        ))
        self.conn.commit()
        return node.id
        
    def add_edge(self, edge: GraphEdge) -> str:
        """Add an edge between nodes"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO edges (id, type, from_node, to_node, properties)
            VALUES (?, ?, ?, ?, ?)
        """, (
            edge.id,
            edge.type,
            edge.from_node,
            edge.to_node,
            json.dumps(edge.properties)
        ))
        self.conn.commit()
        return edge.id
        
    def query_cross_layer(self, query: str) -> List[Dict]:
        """
        Execute a cross-layer query
        
        This is where the magic happens - we can query across
        all four layers to find deep insights
        """
        cursor = self.conn.cursor()
        results = cursor.execute(query).fetchall()
        return [dict(row) for row in results]
        
    def find_learning_moments(self, user_id: str) -> List[Dict]:
        """
        Find moments where struggle led to mastery
        
        This queries across episodic, phenomenological, and ontological layers
        """
        query = """
            SELECT 
                e.properties as event,
                p.properties as user_state,
                o.properties as concept,
                edges1.type as struggle_type,
                edges2.type as mastery_type
            FROM nodes e
            JOIN edges edges1 ON e.id = edges1.from_node
            JOIN nodes p ON edges1.to_node = p.id
            JOIN edges edges2 ON p.id = edges2.from_node
            JOIN nodes o ON edges2.to_node = o.id
            WHERE e.layer = 'episodic'
            AND p.layer = 'phenomenological'
            AND o.layer = 'ontological'
            AND edges1.type = 'CAUSED_BY'
            AND edges2.type IN ('STRUGGLED_WITH', 'MASTERED')
            ORDER BY e.created_at
        """
        return self.query_cross_layer(query)
        
    def get_trust_context(self) -> Dict:
        """
        Get the current trust context by querying metacognitive 
        and phenomenological layers
        """
        query = """
            SELECT 
                m.properties as ai_state,
                p.properties as user_state
            FROM nodes m
            JOIN edges e ON m.id = e.from_node
            JOIN nodes p ON e.to_node = p.id
            WHERE m.layer = 'metacognitive'
            AND p.layer = 'phenomenological'
            AND e.type = 'INFERS'
            AND m.type = 'trust_model'
            ORDER BY m.created_at DESC
            LIMIT 1
        """
        results = self.query_cross_layer(query)
        if results:
            return {
                'ai_state': json.loads(results[0]['ai_state']),
                'user_state': json.loads(results[0]['user_state'])
            }
        return {'ai_state': {}, 'user_state': {}}
        
    def close(self):
        """Close the database connection"""
        self.conn.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()