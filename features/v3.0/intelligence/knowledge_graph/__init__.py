"""
Symbiotic Knowledge Graph (SKG) - Four-layer architecture for consciousness-first AI

The SKG implements a four-layer knowledge representation:
1. Ontological Layer - Objective truth about the domain (NixOS)
2. Episodic Layer - History of user-AI interactions
3. Phenomenological Layer - User's subjective experience
4. Metacognitive Layer - AI's self-awareness and introspection
"""

from .ontological import OntologicalLayer
from .episodic import EpisodicLayer
from .phenomenological import PhenomenologicalLayer
from .metacognitive import MetacognitiveLayer
from .skg import SymbioticKnowledgeGraph

__all__ = [
    'OntologicalLayer',
    'EpisodicLayer', 
    'PhenomenologicalLayer',
    'MetacognitiveLayer',
    'SymbioticKnowledgeGraph'
]