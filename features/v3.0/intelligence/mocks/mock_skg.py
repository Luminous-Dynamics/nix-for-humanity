"""Mock Symbiotic Knowledge Graph for testing without numpy/scipy dependencies."""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


from typing import List, Optional
class MockOntologicalLayer:
    """Mock ontological layer"""
    def __init__(self):
        self.concepts = {}
        
    def add_concept(self, name, type, properties):
        self.concepts[name] = {'type': type, 'properties': properties}
        
    def get_concept(self, name):
        return self.concepts.get(name)
        
    def link_concepts(self, concept1, concept2, relation):
        pass


class MockEpisodicLayer:
    """Mock episodic layer"""
    def __init__(self):
        self.interactions = []
        
    def record_interaction(self, user_input, timestamp):
        interaction_id = f"int_{len(self.interactions)}"
        self.interactions.append({
            'id': interaction_id,
            'input': user_input,
            'timestamp': timestamp
        })
        return interaction_id
        
    def record_ai_response(self, interaction_id, response, success):
        pass
        
    def get_recent_interactions(self, limit=10):
        return self.interactions[-limit:]


class MockPhenomenologicalLayer:
    """Mock phenomenological layer"""
    def record_experience(self, experience):
        pass


class MockMetacognitiveLayer:
    """Mock metacognitive layer"""
    def record_meta_learning(self, learning):
        pass


class MockSymbioticKnowledgeGraph:
    """Lightweight mock of SymbioticKnowledgeGraph for testing."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.nodes = {}
        self.edges = {}
        self.patterns = []
        self.interactions = []
        
        # Initialize the four layers to match the real SKG interface
        self.ontological = MockOntologicalLayer()
        self.episodic = MockEpisodicLayer()
        self.phenomenological = MockPhenomenologicalLayer()
        self.metacognitive = MockMetacognitiveLayer()
        
    def add_node(self, node_id: str, node_type: str, data: Dict) -> None:
        """Add a node to the graph."""
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            'data': data,
            'created_at': datetime.now().isoformat()
        }
        
    def add_edge(self, source: str, target: str, edge_type: str, weight: float = 1.0) -> None:
        """Add an edge between nodes."""
        edge_id = f"{source}-{target}"
        self.edges[edge_id] = {
            'source': source,
            'target': target,
            'type': edge_type,
            'weight': weight,
            'created_at': datetime.now().isoformat()
        }
        
    def update_from_interaction(self, interaction: Dict) -> Dict:
        """Update graph based on interaction."""
        self.interactions.append(interaction)
        
        # Mock pattern extraction
        if len(self.interactions) % 5 == 0:
            pattern = {
                'id': f"pattern_{len(self.patterns)}",
                'type': 'usage_pattern',
                'confidence': random.uniform(0.6, 0.95),
                'interactions': len(self.interactions)
            }
            self.patterns.append(pattern)
            
        return {
            'nodes_updated': random.randint(1, 3),
            'edges_updated': random.randint(0, 2),
            'patterns_detected': len(self.patterns)
        }
        
    def get_recommendations(self, context: Dict) -> List[Dict]:
        """Get recommendations based on current context."""
        recommendations = []
        
        # Mock recommendations based on interaction count
        if len(self.interactions) > 10:
            recommendations.append({
                'type': 'command_suggestion',
                'content': 'You might want to try: nix-env -qaP',
                'confidence': 0.8
            })
            
        if len(self.interactions) > 20:
            recommendations.append({
                'type': 'workflow_optimization',
                'content': 'Consider using nix-shell for development',
                'confidence': 0.85
            })
            
        return recommendations
        
    def get_causal_chain(self, effect: str) -> List[Dict]:
        """Get causal chain for an effect."""
        # Mock causal chain
        chains = {
            'package_conflict': [
                {'cause': 'multiple_versions', 'probability': 0.7},
                {'cause': 'dependency_mismatch', 'probability': 0.3}
            ],
            'build_failure': [
                {'cause': 'missing_dependency', 'probability': 0.6},
                {'cause': 'compilation_error', 'probability': 0.4}
            ]
        }
        
        return chains.get(effect, [{'cause': 'unknown', 'probability': 1.0}])
        
    def detect_patterns(self) -> List[Dict]:
        """Detect patterns in the graph."""
        return self.patterns
        
    def export_insights(self) -> Dict:
        """Export insights from the graph."""
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'patterns_detected': len(self.patterns),
            'interactions_processed': len(self.interactions),
            'top_patterns': self.patterns[-3:] if self.patterns else []
        }
        
    def save_state(self, path: Path) -> None:
        """Save graph state to file."""
        state = {
            'nodes': self.nodes,
            'edges': self.edges,
            'patterns': self.patterns,
            'interactions': self.interactions[-100:]  # Keep last 100
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
            
    def load_state(self, path: Path) -> None:
        """Load graph state from file."""
        if path.exists():
            with open(path, 'r') as f:
                state = json.load(f)
                self.nodes = state.get('nodes', {})
                self.edges = state.get('edges', {})
                self.patterns = state.get('patterns', [])
                self.interactions = state.get('interactions', [])
                
    def record_interaction(self, user_id: str, intent: str, context: Dict, outcome: str, metadata: Optional[Dict] = None) -> Dict:
        """Record an interaction in the knowledge graph."""
        interaction = {
            'user_id': user_id,
            'intent': intent,
            'context': context,
            'outcome': outcome,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        self.interactions.append(interaction)
        
        # Update nodes and edges based on interaction
        self.update_from_interaction(interaction)
        
        return interaction