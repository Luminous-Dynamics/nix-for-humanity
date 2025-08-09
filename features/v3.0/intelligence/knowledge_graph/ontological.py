"""
from typing import List
Ontological Layer - Objective truth about the NixOS domain

This layer contains the formal knowledge structure of NixOS:
- Concepts (derivations, flakes, modules)
- Skills (packaging, configuration, debugging)
- Tools (nix-build, nixos-rebuild, nix-shell)
- Relationships (dependencies, tensions, supersedes)
"""

import json
from typing import Dict, List, Optional
from datetime import datetime


class OntologicalLayer:
    """
    The foundational layer containing objective, universal knowledge
    about NixOS. This is the "map of truth" that doesn't change
    based on user experience.
    """
    
    def __init__(self, conn):
        self.conn = conn
        self._init_schema()
        self._seed_core_concepts()
        
    def _init_schema(self):
        """Initialize ontological-specific schema elements"""
        cursor = self.conn.cursor()
        
        # Create indices for common ontological queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ontological_concepts 
            ON nodes(type) WHERE layer = 'ontological'
        """)
        
        self.conn.commit()
        
    def _seed_core_concepts(self):
        """Seed the layer with core NixOS concepts if empty"""
        cursor = self.conn.cursor()
        
        # Check if already seeded
        count = cursor.execute(
            "SELECT COUNT(*) FROM nodes WHERE layer = 'ontological'"
        ).fetchone()[0]
        
        if count > 0:
            return
            
        # Core concepts to seed
        core_concepts = [
            {
                'id': 'concept_derivation',
                'type': 'concept',
                'properties': {
                    'name': 'derivation',
                    'description': 'The fundamental building block of Nix',
                    'complexity': 'foundational'
                }
            },
            {
                'id': 'concept_flake',
                'type': 'concept',
                'properties': {
                    'name': 'flake',
                    'description': 'Modern Nix project structure with pinned dependencies',
                    'complexity': 'intermediate'
                }
            },
            {
                'id': 'concept_module',
                'type': 'concept', 
                'properties': {
                    'name': 'module',
                    'description': 'NixOS configuration unit with options and config',
                    'complexity': 'intermediate'
                }
            },
            {
                'id': 'concept_overlay',
                'type': 'concept',
                'properties': {
                    'name': 'overlay',
                    'description': 'Method to extend and override packages in nixpkgs',
                    'complexity': 'advanced'
                }
            }
        ]
        
        # Insert concepts
        for concept in core_concepts:
            cursor.execute("""
                INSERT OR IGNORE INTO nodes (id, layer, type, properties)
                VALUES (?, 'ontological', ?, ?)
            """, (
                concept['id'],
                concept['type'],
                json.dumps(concept['properties'])
            ))
            
        # Add relationships
        relationships = [
            ('concept_flake', 'SUPERSEDES', 'concept_derivation', 
             {'reason': 'provides better dependency management'}),
            ('concept_overlay', 'MODIFIES', 'concept_derivation',
             {'reason': 'allows package customization'}),
            ('concept_module', 'USES', 'concept_derivation',
             {'reason': 'modules evaluate to derivations'})
        ]
        
        for from_id, rel_type, to_id, props in relationships:
            edge_id = f"edge_{from_id}_{rel_type}_{to_id}"
            cursor.execute("""
                INSERT OR IGNORE INTO edges (id, type, from_node, to_node, properties)
                VALUES (?, ?, ?, ?, ?)
            """, (
                edge_id,
                rel_type,
                from_id,
                to_id,
                json.dumps(props)
            ))
            
        self.conn.commit()
        
    def add_concept(self, name: str, description: str, 
                   complexity: str = 'intermediate') -> str:
        """Add a new concept to the ontological layer"""
        concept_id = f"concept_{name.lower().replace(' ', '_')}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'ontological', 'concept', ?)
        """, (
            concept_id,
            json.dumps({
                'name': name,
                'description': description,
                'complexity': complexity
            })
        ))
        self.conn.commit()
        
        return concept_id
        
    def add_skill(self, name: str, description: str,
                  required_concepts: List[str]) -> str:
        """Add a new skill and link it to required concepts"""
        skill_id = f"skill_{name.lower().replace(' ', '_')}"
        
        cursor = self.conn.cursor()
        
        # Add the skill node
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'ontological', 'skill', ?)
        """, (
            skill_id,
            json.dumps({
                'name': name,
                'description': description
            })
        ))
        
        # Link to required concepts
        for concept_id in required_concepts:
            edge_id = f"edge_{skill_id}_requires_{concept_id}"
            cursor.execute("""
                INSERT INTO edges (id, type, from_node, to_node, properties)
                VALUES (?, 'REQUIRES', ?, ?, ?)
            """, (
                edge_id,
                skill_id,
                concept_id,
                json.dumps({'strength': 'strong'})
            ))
            
        self.conn.commit()
        return skill_id
        
    def find_concepts_in_tension(self) -> List[Dict]:
        """Find concepts that are in philosophical tension"""
        cursor = self.conn.cursor()
        
        results = cursor.execute("""
            SELECT 
                n1.properties as concept1,
                n2.properties as concept2,
                e.properties as tension_reason
            FROM edges e
            JOIN nodes n1 ON e.from_node = n1.id
            JOIN nodes n2 ON e.to_node = n2.id
            WHERE e.type = 'IN_TENSION_WITH'
            AND n1.layer = 'ontological'
            AND n2.layer = 'ontological'
        """).fetchall()
        
        return [
            {
                'concept1': json.loads(row['concept1']),
                'concept2': json.loads(row['concept2']),
                'reason': json.loads(row['tension_reason'])
            }
            for row in results
        ]
        
    def get_learning_path(self, target_skill: str) -> List[str]:
        """Get the optimal learning path to a skill"""
        # This would use graph traversal to find prerequisites
        # For now, return a simple path
        cursor = self.conn.cursor()
        
        # Find all concepts required by the skill
        results = cursor.execute("""
            SELECT n.id, n.properties
            FROM edges e
            JOIN nodes n ON e.to_node = n.id
            WHERE e.from_node = ?
            AND e.type = 'REQUIRES'
            ORDER BY json_extract(n.properties, '$.complexity')
        """, (target_skill,)).fetchall()
        
        return [row['id'] for row in results]