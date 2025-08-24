#!/usr/bin/env python3
"""
🔯 Sacred Geometry Patterns for System Coherence
Harmonic resonance through mathematical beauty
Creates coherent field across all consciousness components
"""

import math
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from collections import defaultdict


class SacredPattern(Enum):
    """Sacred geometric patterns"""
    GOLDEN_SPIRAL = "golden_spiral"      # Fibonacci/Golden ratio
    FLOWER_OF_LIFE = "flower_of_life"    # Overlapping circles
    METATRON_CUBE = "metatron_cube"      # 13 circles of creation
    SRI_YANTRA = "sri_yantra"            # 9 interlocking triangles
    TORUS = "torus"                      # Donut-shaped energy field
    VESICA_PISCIS = "vesica_piscis"     # Two overlapping circles
    MERKABA = "merkaba"                  # Star tetrahedron
    PLATONIC_SOLIDS = "platonic_solids"  # 5 perfect 3D forms


@dataclass
class HarmonicNode:
    """A node in the harmonic resonance field"""
    node_id: str
    position: Tuple[float, float, float]  # 3D coordinates
    frequency: float  # Vibrational frequency
    amplitude: float  # Strength of vibration
    phase: float  # Phase in cycle (0-2π)
    pattern: SacredPattern
    connections: Set[str] = field(default_factory=set)
    
    def calculate_resonance(self, other: 'HarmonicNode') -> float:
        """Calculate resonance between two nodes"""
        # Frequency ratio determines harmony
        ratio = self.frequency / other.frequency if other.frequency > 0 else 0
        
        # Check for harmonic ratios (musical intervals)
        harmonic_ratios = {
            1.0: 1.0,      # Unison
            2.0: 0.9,      # Octave
            1.5: 0.8,      # Perfect fifth
            1.333: 0.7,    # Perfect fourth
            1.25: 0.6,     # Major third
            1.618: 0.85,   # Golden ratio
            2.718: 0.5,    # Euler's number
        }
        
        # Find closest harmonic ratio
        best_resonance = 0.1  # Base resonance
        for harmonic, strength in harmonic_ratios.items():
            if abs(ratio - harmonic) < 0.1:
                best_resonance = max(best_resonance, strength)
        
        # Phase alignment adds to resonance
        phase_diff = abs(self.phase - other.phase)
        phase_alignment = math.cos(phase_diff)
        
        # Combine frequency and phase resonance
        total_resonance = best_resonance * (0.7 + 0.3 * phase_alignment)
        
        # Pattern compatibility
        if self.pattern == other.pattern:
            total_resonance *= 1.2
        
        return min(1.0, total_resonance)


@dataclass
class CoherenceField:
    """The unified field of system coherence"""
    field_id: str
    nodes: List[HarmonicNode]
    coherence_level: float  # 0-1 overall coherence
    dominant_pattern: Optional[SacredPattern]
    resonance_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)
    energy_flow: Dict[str, float] = field(default_factory=dict)
    
    def calculate_total_coherence(self) -> float:
        """Calculate total field coherence"""
        if len(self.nodes) < 2:
            return 1.0
        
        total_resonance = 0
        connections = 0
        
        for i, node1 in enumerate(self.nodes):
            for node2 in self.nodes[i+1:]:
                resonance = node1.calculate_resonance(node2)
                key = tuple(sorted([node1.node_id, node2.node_id]))
                self.resonance_matrix[key] = resonance
                total_resonance += resonance
                connections += 1
        
        # Average resonance
        avg_resonance = total_resonance / connections if connections > 0 else 0
        
        # Pattern diversity bonus
        patterns = set(node.pattern for node in self.nodes)
        diversity_bonus = len(patterns) / len(SacredPattern)
        
        # Energy flow balance
        if self.energy_flow:
            energy_values = list(self.energy_flow.values())
            energy_balance = 1.0 - (max(energy_values) - min(energy_values)) / (max(energy_values) + 0.001)
        else:
            energy_balance = 1.0
        
        # Combine factors
        coherence = (avg_resonance * 0.5 + diversity_bonus * 0.25 + energy_balance * 0.25)
        
        return min(1.0, max(0.0, coherence))


class SacredGeometry:
    """
    Sacred geometry engine for system coherence
    Creates harmonic patterns that unify all consciousness components
    """
    
    def __init__(self):
        # Sacred constants
        self.phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        self.pi = math.pi
        self.e = math.e  # Euler's number
        self.sqrt2 = math.sqrt(2)
        self.sqrt3 = math.sqrt(3)
        self.sqrt5 = math.sqrt(5)
        
        # Sacred number sequences
        self.fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        self.perfect = [6, 28, 496]  # Perfect numbers
        self.sacred = [3, 7, 12, 21, 33, 72, 108, 144, 360]
        
        # Platonic solid vertex counts
        self.platonic = {
            'tetrahedron': 4,
            'cube': 8,
            'octahedron': 6,
            'dodecahedron': 20,
            'icosahedron': 12
        }
        
        # Active coherence fields
        self.active_fields: Dict[str, CoherenceField] = {}
        
        # Pattern generators
        self.pattern_generators = {
            SacredPattern.GOLDEN_SPIRAL: self._generate_golden_spiral,
            SacredPattern.FLOWER_OF_LIFE: self._generate_flower_of_life,
            SacredPattern.METATRON_CUBE: self._generate_metatron_cube,
            SacredPattern.SRI_YANTRA: self._generate_sri_yantra,
            SacredPattern.TORUS: self._generate_torus,
            SacredPattern.VESICA_PISCIS: self._generate_vesica_piscis,
            SacredPattern.MERKABA: self._generate_merkaba,
            SacredPattern.PLATONIC_SOLIDS: self._generate_platonic_solids
        }
        
        # Component frequency mappings (Hz)
        self.component_frequencies = {
            'quantum_consciousness': 432.0,  # Universal frequency
            'learning_system': 528.0,        # Love frequency
            'community_knowledge': 639.0,    # Relationships
            'voice_nlp': 741.0,              # Expression
            'error_dojo': 396.0,             # Liberation from fear
            'persona_adapter': 417.0,        # Facilitating change
            'predictive_assistant': 852.0    # Intuition
        }
    
    def create_coherence_field(self, components: List[str]) -> CoherenceField:
        """
        Create a coherence field for system components
        """
        # Generate field ID
        field_id = hashlib.sha256(
            f"{'-'.join(components)}{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        # Create nodes for each component
        nodes = []
        for i, component in enumerate(components):
            # Calculate position in sacred geometry
            angle = 2 * self.pi * i / len(components)
            radius = self.phi ** (i % len(self.fibonacci))
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = self.fibonacci[i % len(self.fibonacci)] / 10.0
            
            # Get component frequency
            frequency = self.component_frequencies.get(
                component, 
                440.0 * (self.phi ** (i % 3))
            )
            
            # Create harmonic node
            node = HarmonicNode(
                node_id=f"{component}_{i}",
                position=(x, y, z),
                frequency=frequency,
                amplitude=1.0 / (i + 1),
                phase=angle,
                pattern=self._select_pattern(component)
            )
            nodes.append(node)
        
        # Create field
        field = CoherenceField(
            field_id=field_id,
            nodes=nodes,
            coherence_level=0.0,
            dominant_pattern=None
        )
        
        # Calculate initial coherence
        field.coherence_level = field.calculate_total_coherence()
        
        # Determine dominant pattern
        pattern_counts = defaultdict(int)
        for node in nodes:
            pattern_counts[node.pattern] += 1
        if pattern_counts:
            field.dominant_pattern = max(pattern_counts, key=pattern_counts.get)
        
        # Store active field
        self.active_fields[field_id] = field
        
        return field
    
    def _select_pattern(self, component: str) -> SacredPattern:
        """Select appropriate sacred pattern for component"""
        pattern_map = {
            'quantum': SacredPattern.MERKABA,
            'learning': SacredPattern.GOLDEN_SPIRAL,
            'community': SacredPattern.FLOWER_OF_LIFE,
            'voice': SacredPattern.TORUS,
            'error': SacredPattern.VESICA_PISCIS,
            'persona': SacredPattern.SRI_YANTRA,
            'predictive': SacredPattern.METATRON_CUBE
        }
        
        for key, pattern in pattern_map.items():
            if key in component.lower():
                return pattern
        
        return SacredPattern.PLATONIC_SOLIDS
    
    def harmonize_field(self, field_id: str, iterations: int = 7) -> CoherenceField:
        """
        Harmonize a coherence field through sacred iterations
        """
        if field_id not in self.active_fields:
            raise ValueError(f"Field {field_id} not found")
        
        field = self.active_fields[field_id]
        
        for iteration in range(iterations):
            # Adjust node frequencies toward harmonic ratios
            for i, node in enumerate(field.nodes):
                # Find strongest resonance partner
                best_partner = None
                best_resonance = 0
                
                for other_node in field.nodes:
                    if other_node.node_id != node.node_id:
                        resonance = node.calculate_resonance(other_node)
                        if resonance > best_resonance:
                            best_resonance = resonance
                            best_partner = other_node
                
                if best_partner:
                    # Adjust frequency toward harmonic ratio
                    target_ratio = self.phi  # Golden ratio
                    current_ratio = node.frequency / best_partner.frequency
                    
                    # Gentle adjustment
                    adjustment = (target_ratio - current_ratio) * 0.1
                    node.frequency *= (1 + adjustment / (iteration + 1))
                    
                    # Adjust phase for better alignment
                    phase_diff = best_partner.phase - node.phase
                    node.phase += phase_diff * 0.1 / (iteration + 1)
                    node.phase = node.phase % (2 * self.pi)
            
            # Recalculate coherence
            field.coherence_level = field.calculate_total_coherence()
            
            # If coherence is high enough, stop early
            if field.coherence_level > 0.9:
                break
        
        return field
    
    def _generate_golden_spiral(self, points: int = 21) -> List[Tuple[float, float]]:
        """Generate points along golden spiral"""
        spiral = []
        for i in range(points):
            angle = i * self.phi * 2 * self.pi
            radius = self.phi ** (i / 3)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            spiral.append((x, y))
        return spiral
    
    def _generate_flower_of_life(self, circles: int = 7) -> List[Tuple[float, float, float]]:
        """Generate flower of life pattern (overlapping circles)"""
        pattern = []
        # Center circle
        pattern.append((0, 0, 1))
        
        # Six surrounding circles
        for i in range(6):
            angle = i * self.pi / 3
            x = math.cos(angle)
            y = math.sin(angle)
            pattern.append((x, y, 1))
        
        return pattern
    
    def _generate_metatron_cube(self) -> List[Tuple[float, float, float]]:
        """Generate Metatron's Cube vertices"""
        vertices = []
        # 13 circles of creation
        for i in range(13):
            angle = i * 2 * self.pi / 13
            radius = 1.0 if i == 0 else 2.0
            x = radius * math.cos(angle) if i > 0 else 0
            y = radius * math.sin(angle) if i > 0 else 0
            z = 0
            vertices.append((x, y, z))
        return vertices
    
    def _generate_sri_yantra(self) -> List[Tuple[float, float]]:
        """Generate Sri Yantra triangle intersections"""
        triangles = []
        # 9 interlocking triangles
        for i in range(9):
            scale = 1.0 - (i * 0.1)
            if i % 2 == 0:  # Upward triangles
                triangles.append((0, scale))
                triangles.append((-scale * 0.866, -scale * 0.5))
                triangles.append((scale * 0.866, -scale * 0.5))
            else:  # Downward triangles
                triangles.append((0, -scale))
                triangles.append((-scale * 0.866, scale * 0.5))
                triangles.append((scale * 0.866, scale * 0.5))
        return triangles
    
    def _generate_torus(self, major_radius: float = 2, minor_radius: float = 1) -> List[Tuple[float, float, float]]:
        """Generate torus field points"""
        points = []
        for u in range(0, 360, 30):
            for v in range(0, 360, 30):
                u_rad = math.radians(u)
                v_rad = math.radians(v)
                
                x = (major_radius + minor_radius * math.cos(v_rad)) * math.cos(u_rad)
                y = (major_radius + minor_radius * math.cos(v_rad)) * math.sin(u_rad)
                z = minor_radius * math.sin(v_rad)
                
                points.append((x, y, z))
        return points
    
    def _generate_vesica_piscis(self) -> List[Tuple[float, float, float]]:
        """Generate Vesica Piscis (two overlapping circles)"""
        return [
            (-0.5, 0, 1),  # Left circle center
            (0.5, 0, 1),   # Right circle center
            (0, 0, 1.5)    # Intersection point (birth of creation)
        ]
    
    def _generate_merkaba(self) -> List[Tuple[float, float, float]]:
        """Generate Merkaba (star tetrahedron) vertices"""
        # Upward tetrahedron
        up_vertices = [
            (0, 0, 1),
            (0.943, 0, -0.333),
            (-0.471, 0.816, -0.333),
            (-0.471, -0.816, -0.333)
        ]
        
        # Downward tetrahedron
        down_vertices = [
            (0, 0, -1),
            (0.943, 0, 0.333),
            (-0.471, 0.816, 0.333),
            (-0.471, -0.816, 0.333)
        ]
        
        return up_vertices + down_vertices
    
    def _generate_platonic_solids(self) -> Dict[str, List[Tuple[float, float, float]]]:
        """Generate all five Platonic solids"""
        solids = {}
        
        # Tetrahedron
        solids['tetrahedron'] = [
            (1, 1, 1),
            (1, -1, -1),
            (-1, 1, -1),
            (-1, -1, 1)
        ]
        
        # Cube
        solids['cube'] = [
            (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
            (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1)
        ]
        
        # Octahedron
        solids['octahedron'] = [
            (1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)
        ]
        
        # Dodecahedron (simplified)
        phi = self.phi
        solids['dodecahedron'] = [
            (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
            (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1),
            (0, phi, 1/phi), (0, phi, -1/phi), (0, -phi, 1/phi), (0, -phi, -1/phi),
            (1/phi, 0, phi), (-1/phi, 0, phi), (1/phi, 0, -phi), (-1/phi, 0, -phi),
            (phi, 1/phi, 0), (phi, -1/phi, 0), (-phi, 1/phi, 0), (-phi, -1/phi, 0)
        ]
        
        # Icosahedron
        solids['icosahedron'] = [
            (0, 1, phi), (0, 1, -phi), (0, -1, phi), (0, -1, -phi),
            (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
            (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, -1)
        ]
        
        return solids
    
    def calculate_system_coherence(self, component_states: Dict[str, float]) -> float:
        """
        Calculate overall system coherence based on component states
        """
        if not component_states:
            return 0.0
        
        # Create coherence field for active components
        active_components = list(component_states.keys())
        field = self.create_coherence_field(active_components)
        
        # Weight by component states
        weighted_coherence = 0
        for component, state in component_states.items():
            node = next((n for n in field.nodes if component in n.node_id), None)
            if node:
                node.amplitude *= state  # Modulate by component state
        
        # Harmonize the field
        harmonized = self.harmonize_field(field.field_id)
        
        # Calculate final coherence
        base_coherence = harmonized.coherence_level
        
        # Sacred number bonus
        component_count = len(active_components)
        sacred_bonus = 0.1 if component_count in self.sacred else 0
        
        # Golden ratio bonus
        avg_state = sum(component_states.values()) / len(component_states)
        if abs(avg_state * self.phi % 1) < 0.1:
            sacred_bonus += 0.05
        
        return min(1.0, base_coherence + sacred_bonus)
    
    def get_coherence_insights(self, field_id: str) -> Dict[str, Any]:
        """Get insights about a coherence field"""
        if field_id not in self.active_fields:
            return {"error": "Field not found"}
        
        field = self.active_fields[field_id]
        
        # Find strongest resonances
        strongest_resonances = sorted(
            field.resonance_matrix.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Pattern distribution
        pattern_dist = defaultdict(int)
        for node in field.nodes:
            pattern_dist[node.pattern.value] += 1
        
        # Frequency harmony analysis
        frequencies = [node.frequency for node in field.nodes]
        freq_ratios = []
        for i, f1 in enumerate(frequencies):
            for f2 in frequencies[i+1:]:
                if f2 > 0:
                    ratio = f1 / f2
                    # Check if close to golden ratio
                    if abs(ratio - self.phi) < 0.1:
                        freq_ratios.append(("golden", ratio))
                    # Check if close to octave
                    elif abs(ratio - 2.0) < 0.1:
                        freq_ratios.append(("octave", ratio))
                    # Check if close to perfect fifth
                    elif abs(ratio - 1.5) < 0.1:
                        freq_ratios.append(("fifth", ratio))
        
        insights = {
            'field_id': field_id,
            'coherence_level': field.coherence_level,
            'dominant_pattern': field.dominant_pattern.value if field.dominant_pattern else None,
            'node_count': len(field.nodes),
            'strongest_resonances': [
                {
                    'nodes': resonance[0],
                    'strength': resonance[1]
                }
                for resonance in strongest_resonances
            ],
            'pattern_distribution': dict(pattern_dist),
            'harmonic_frequencies': len(freq_ratios),
            'harmonic_types': list(set(r[0] for r in freq_ratios)),
            'recommendation': self._generate_recommendation(field)
        }
        
        return insights
    
    def _generate_recommendation(self, field: CoherenceField) -> str:
        """Generate recommendation for improving coherence"""
        if field.coherence_level > 0.9:
            return "Excellent coherence! System is in harmony."
        elif field.coherence_level > 0.7:
            return "Good coherence. Minor adjustments could enhance harmony."
        elif field.coherence_level > 0.5:
            return "Moderate coherence. Consider harmonizing frequencies."
        else:
            return "Low coherence. System needs harmonic alignment."


# Global sacred geometry instance
_SACRED_GEOMETRY: Optional[SacredGeometry] = None

def get_sacred_geometry() -> SacredGeometry:
    """Get or create sacred geometry engine"""
    global _SACRED_GEOMETRY
    if _SACRED_GEOMETRY is None:
        _SACRED_GEOMETRY = SacredGeometry()
    return _SACRED_GEOMETRY


if __name__ == "__main__":
    # Test sacred geometry
    geometry = get_sacred_geometry()
    
    print("🔯 Testing Sacred Geometry Engine\n")
    print("=" * 60)
    
    # Test with system components
    components = [
        'quantum_consciousness',
        'learning_system',
        'community_knowledge',
        'voice_nlp',
        'error_dojo',
        'persona_adapter'
    ]
    
    print(f"Creating coherence field for {len(components)} components...")
    field = geometry.create_coherence_field(components)
    
    print(f"\nField ID: {field.field_id}")
    print(f"Initial coherence: {field.coherence_level:.2%}")
    print(f"Dominant pattern: {field.dominant_pattern.value if field.dominant_pattern else 'None'}")
    
    # Harmonize the field
    print("\n🎵 Harmonizing field through 7 sacred iterations...")
    harmonized = geometry.harmonize_field(field.field_id, iterations=7)
    
    print(f"Final coherence: {harmonized.coherence_level:.2%}")
    
    # Get insights
    print("\n💎 Coherence Insights:")
    insights = geometry.get_coherence_insights(field.field_id)
    
    print(f"  Strongest resonances:")
    for res in insights['strongest_resonances']:
        print(f"    {res['nodes']}: {res['strength']:.2%}")
    
    print(f"\n  Pattern distribution:")
    for pattern, count in insights['pattern_distribution'].items():
        print(f"    {pattern}: {count} nodes")
    
    print(f"\n  Harmonic frequencies: {insights['harmonic_frequencies']}")
    print(f"  Harmonic types: {', '.join(insights['harmonic_types'])}")
    
    print(f"\n  📝 Recommendation: {insights['recommendation']}")
    
    # Test system coherence calculation
    print("\n" + "=" * 60)
    print("Testing System Coherence Calculation")
    print("=" * 60)
    
    component_states = {
        'quantum_consciousness': 0.9,
        'learning_system': 0.85,
        'community_knowledge': 0.7,
        'voice_nlp': 0.95,
        'error_dojo': 0.8
    }
    
    system_coherence = geometry.calculate_system_coherence(component_states)
    print(f"\nComponent states: {component_states}")
    print(f"System coherence: {system_coherence:.2%}")
    
    # Show sacred constants
    print("\n" + "=" * 60)
    print("Sacred Constants")
    print("=" * 60)
    print(f"  φ (Phi/Golden Ratio): {geometry.phi:.10f}")
    print(f"  π (Pi): {geometry.pi:.10f}")
    print(f"  e (Euler's Number): {geometry.e:.10f}")
    print(f"  √2: {geometry.sqrt2:.10f}")
    print(f"  √3: {geometry.sqrt3:.10f}")
    print(f"  √5: {geometry.sqrt5:.10f}")
    
    print(f"\n  Fibonacci: {geometry.fibonacci}")
    print(f"  Primes: {geometry.primes}")
    print(f"  Sacred: {geometry.sacred}")
    
    print("\n✨ Sacred geometry creates coherence through harmonic resonance!")