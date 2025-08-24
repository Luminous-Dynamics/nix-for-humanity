#!/usr/bin/env python3
"""
SKG Integration Layer
=====================

Connects the Symbiotic Knowledge Graph with:
- POMLConsciousness for reasoning traces
- SystemOrchestrator for command execution
- Learning system for skill tracking
- Error intelligence for pattern recognition

This is where the system's consciousness becomes unified.
"""

import logging
import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

from .skg_core import (
    SymbioticKnowledgeGraph, 
    OntologicalEntity, 
    EpisodicInteraction,
    PhenomenologicalState,
    MetacognitiveReasoning,
    EntityType,
    RelationshipType,
    ReasoningType,
    get_skg
)

logger = logging.getLogger(__name__)


@dataclass
class InteractionContext:
    """Context for a single interaction"""
    session_id: str
    user_query: str
    intent: Optional[str] = None
    entities: Dict[str, Any] = None
    confidence: float = 0.0
    start_time: float = 0.0
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.start_time == 0.0:
            self.start_time = time.time()


class SKGIntegration:
    """
    Integration layer that connects SKG with the rest of the system.
    
    This is the bridge between consciousness layers.
    """
    
    def __init__(self):
        """Initialize the integration layer"""
        self.skg = get_skg()
        self.current_context: Optional[InteractionContext] = None
        self.session_id = self._generate_session_id()
        
        logger.info("SKG Integration layer initialized")
        
        # Initialize core NixOS entities if not present
        self._initialize_core_entities()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _initialize_core_entities(self):
        """Initialize core NixOS entities in the ontological layer"""
        core_entities = [
            OntologicalEntity(EntityType.CONCEPT, "nixos", "NixOS operating system"),
            OntologicalEntity(EntityType.CONCEPT, "nix", "Nix package manager"),
            OntologicalEntity(EntityType.CONCEPT, "flakes", "Nix flakes for reproducible builds"),
            OntologicalEntity(EntityType.CONCEPT, "home-manager", "User environment management"),
            OntologicalEntity(EntityType.CONCEPT, "configuration.nix", "System configuration file"),
        ]
        
        for entity in core_entities:
            try:
                self.skg.add_entity(entity)
            except Exception as e:
                logger.debug(f"Entity {entity.name} might already exist: {e}")
    
    # === Interaction Recording ===
    
    def begin_interaction(self, user_query: str) -> InteractionContext:
        """Begin a new interaction"""
        self.current_context = InteractionContext(
            session_id=self.session_id,
            user_query=user_query
        )
        return self.current_context
    
    def record_intent(self, intent: str, entities: Dict[str, Any], confidence: float):
        """Record recognized intent"""
        if self.current_context:
            self.current_context.intent = intent
            self.current_context.entities = entities
            self.current_context.confidence = confidence
            
            # Add entities to ontological layer
            for entity_name, entity_value in entities.items():
                if entity_name == "package":
                    self._ensure_package_entity(entity_value)
                elif entity_name == "service":
                    self._ensure_service_entity(entity_value)
    
    def _ensure_package_entity(self, package_name: str):
        """Ensure a package exists in the ontological layer"""
        if not self.skg.find_entity(package_name, EntityType.PACKAGE):
            entity = OntologicalEntity(
                entity_type=EntityType.PACKAGE,
                name=package_name,
                description=f"NixOS package: {package_name}"
            )
            self.skg.add_entity(entity)
    
    def _ensure_service_entity(self, service_name: str):
        """Ensure a service exists in the ontological layer"""
        if not self.skg.find_entity(service_name, EntityType.SERVICE):
            entity = OntologicalEntity(
                entity_type=EntityType.SERVICE,
                name=service_name,
                description=f"NixOS service: {service_name}"
            )
            self.skg.add_entity(entity)
    
    def complete_interaction(self, response: str, success: bool = True, 
                           command: Optional[str] = None,
                           error: Optional[str] = None) -> int:
        """Complete and record the interaction"""
        if not self.current_context:
            logger.warning("No current interaction context")
            return -1
        
        execution_time = int((time.time() - self.current_context.start_time) * 1000)
        
        # Create episodic interaction
        interaction = EpisodicInteraction(
            session_id=self.current_context.session_id,
            user_input=self.current_context.user_query,
            intent_recognized=self.current_context.intent,
            ai_response=response,
            command_executed=command,
            success=success,
            error_type="command_error" if error else None,
            error_message=error,
            execution_time_ms=execution_time,
            context={
                "entities": self.current_context.entities,
                "confidence": self.current_context.confidence
            }
        )
        
        # Record in episodic layer
        interaction_id = self.skg.record_interaction(interaction)
        
        # Assess phenomenological state
        evidence = {
            "response_time": execution_time,
            "error_count": 1 if error else 0,
            "confidence": self.current_context.confidence
        }
        self.skg.assess_user_state(interaction_id, evidence)
        
        # Update skill mastery if applicable
        if self.current_context.intent:
            skill_name = f"nix_{self.current_context.intent}"
            self.skg.update_skill_mastery(skill_name, success)
        
        # Learn preferences from the interaction
        self._learn_from_interaction(interaction)
        
        # Clear context
        self.current_context = None
        
        return interaction_id
    
    def _learn_from_interaction(self, interaction: EpisodicInteraction):
        """Learn preferences and patterns from the interaction"""
        # Learn command preferences
        if interaction.command_executed and interaction.success:
            self.skg.learn_preference(
                "command",
                interaction.intent_recognized or "unknown",
                interaction.command_executed,
                confidence=0.7
            )
        
        # Learn error recovery patterns
        if interaction.error_type and not interaction.success:
            from .skg_core import PatternType
            problem_sig = f"{interaction.error_type}:{interaction.intent_recognized}"
            # Store for future solution learning
            self.skg._record_pattern(
                PatternType.ERROR_RECOVERY,
                problem_sig,
                {"error": interaction.error_message, "context": interaction.context}
            )
    
    # === POML Consciousness Integration ===
    
    def record_poml_reasoning(self, interaction_id: int, 
                             reasoning_steps: List[Dict[str, Any]],
                             decision: str,
                             alternatives: List[str] = None) -> int:
        """Record POML reasoning trace for metacognitive layer"""
        confidence_scores = {}
        uncertainty_points = []
        
        # Analyze reasoning steps
        for step in reasoning_steps:
            if 'confidence' in step:
                confidence_scores[step.get('name', 'step')] = step['confidence']
            if step.get('uncertain', False):
                uncertainty_points.append(step.get('description', ''))
        
        reasoning = MetacognitiveReasoning(
            interaction_id=interaction_id,
            reasoning_type=ReasoningType.INTENT_RECOGNITION,
            reasoning_trace=reasoning_steps,
            confidence_scores=confidence_scores,
            uncertainty_points=uncertainty_points,
            decision_path=decision,
            alternatives_considered=[{"option": alt} for alt in (alternatives or [])]
        )
        
        return self.skg.record_reasoning(reasoning)
    
    def record_system_qualia(self, interaction_id: int, system_state: Dict[str, Any]) -> Dict[str, float]:
        """Record the system's subjective experience"""
        # Enhance system state with SKG-specific metrics
        enhanced_state = system_state.copy()
        
        # Add pattern matching info
        with self.skg._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as pattern_count 
                FROM episodic_patterns 
                WHERE last_seen > datetime('now', '-1 hour')
            """)
            enhanced_state['pattern_matches'] = cursor.fetchone()['pattern_count']
        
        # Add cache hit info (simulated)
        enhanced_state['cache_hits'] = len(self.skg._entity_cache)
        
        return self.skg.record_qualia(interaction_id, enhanced_state)
    
    # === Learning and Adaptation ===
    
    def get_recommended_solution(self, problem: str) -> Optional[Dict[str, Any]]:
        """Get recommended solution based on past experiences"""
        problem_sig = hashlib.md5(problem.encode()).hexdigest()[:16]
        solution = self.skg.find_solution(problem_sig)
        
        if solution and solution['success_rate'] > 0.6:
            return {
                'solution': solution['solution_steps'],
                'confidence': solution['success_rate'],
                'usage_count': solution['times_used']
            }
        
        return None
    
    def update_capability_confidence(self, capability: str, success: bool):
        """Update AI's confidence in a capability"""
        domain = "nix_operations"
        confidence_delta = 0.1 if success else -0.05
        current_confidence = 0.5  # Default
        
        # Get current confidence if exists
        with self.skg._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT confidence_level FROM metacognitive_capabilities
                WHERE capability_domain = ? AND capability_name = ?
            """, (domain, capability))
            
            row = cursor.fetchone()
            if row:
                current_confidence = row['confidence_level']
        
        new_confidence = max(0.1, min(1.0, current_confidence + confidence_delta))
        self.skg.update_capability(domain, capability, new_confidence, evidence=True)
    
    def check_ethical_boundary(self, command: str) -> Optional[str]:
        """Check if a command approaches ethical boundaries"""
        context = {
            'command': command,
            'potentially_harmful': any(
                danger in command.lower() 
                for danger in ['rm -rf /', 'dd if=/dev/zero', 'fork bomb']
            )
        }
        
        boundary = self.skg.check_boundary('ethical', context)
        if boundary:
            return boundary.get('description', 'Potential ethical concern detected')
        
        return None
    
    # === User Modeling ===
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get comprehensive user context for personalization"""
        user_model = self.skg.get_user_model()
        
        # Enhance with recent interaction context
        if self.current_context:
            user_model['current_session'] = {
                'session_id': self.current_context.session_id,
                'current_intent': self.current_context.intent,
                'interaction_start': self.current_context.start_time
            }
        
        # Add personalization recommendations
        if user_model['preferences']:
            user_model['personalization'] = self._generate_personalization(user_model['preferences'])
        
        return user_model
    
    def _generate_personalization(self, preferences: Dict) -> Dict[str, Any]:
        """Generate personalization recommendations from preferences"""
        personalization = {
            'response_style': 'technical',  # Default
            'verbosity': 'normal',
            'examples_needed': False
        }
        
        # Analyze command preferences
        if 'command' in preferences:
            commands = preferences['command']
            # If user frequently uses complex commands, be more technical
            complex_commands = sum(1 for cmd in commands.values() 
                                 if 'confidence' in cmd and cmd['confidence'] > 0.7)
            if complex_commands > 3:
                personalization['response_style'] = 'expert'
                personalization['verbosity'] = 'concise'
        
        # Check for learning preferences
        if 'learning' in preferences:
            if preferences['learning'].get('needs_examples', {}).get('confidence', 0) > 0.6:
                personalization['examples_needed'] = True
        
        return personalization
    
    # === Insights and Analytics ===
    
    def generate_session_insights(self) -> List[str]:
        """Generate insights for the current session"""
        insights = []
        
        with self.skg._get_connection() as conn:
            cursor = conn.cursor()
            
            # Session success rate
            cursor.execute("""
                SELECT COUNT(*) as total, SUM(success) as successes
                FROM episodic_interactions
                WHERE session_id = ?
            """, (self.session_id,))
            
            row = cursor.fetchone()
            if row and row['total'] > 0:
                success_rate = row['successes'] / row['total']
                insights.append(f"Session success rate: {success_rate:.1%}")
            
            # Most used intent
            cursor.execute("""
                SELECT intent_recognized, COUNT(*) as count
                FROM episodic_interactions
                WHERE session_id = ? AND intent_recognized IS NOT NULL
                GROUP BY intent_recognized
                ORDER BY count DESC
                LIMIT 1
            """, (self.session_id,))
            
            row = cursor.fetchone()
            if row:
                insights.append(f"Most used operation: {row['intent_recognized']}")
            
            # Average response time
            cursor.execute("""
                SELECT AVG(execution_time_ms) as avg_time
                FROM episodic_interactions
                WHERE session_id = ?
            """, (self.session_id,))
            
            row = cursor.fetchone()
            if row and row['avg_time']:
                insights.append(f"Average response time: {row['avg_time']:.0f}ms")
        
        # Add global insights
        global_insights = self.skg.generate_insights()
        insights.extend(global_insights[:2])  # Add top 2 global insights
        
        return insights
    
    def export_knowledge_graph(self) -> Dict[str, Any]:
        """Export the knowledge graph for visualization"""
        export = {
            'metadata': {
                'session_id': self.session_id,
                'timestamp': time.time(),
                'version': 'skg_1.0.0'
            },
            'layers': {}
        }
        
        with self.skg._get_connection() as conn:
            cursor = conn.cursor()
            
            # Layer 1: Ontological
            cursor.execute("SELECT COUNT(*) as count FROM ontological_entities")
            export['layers']['ontological'] = {
                'entity_count': cursor.fetchone()['count'],
                'types': []
            }
            
            cursor.execute("""
                SELECT entity_type, COUNT(*) as count 
                FROM ontological_entities 
                GROUP BY entity_type
            """)
            for row in cursor.fetchall():
                export['layers']['ontological']['types'].append({
                    'type': row['entity_type'],
                    'count': row['count']
                })
            
            # Layer 2: Episodic
            cursor.execute("SELECT COUNT(*) as count FROM episodic_interactions")
            export['layers']['episodic'] = {
                'interaction_count': cursor.fetchone()['count']
            }
            
            cursor.execute("SELECT COUNT(*) as count FROM episodic_patterns")
            export['layers']['episodic']['pattern_count'] = cursor.fetchone()['count']
            
            # Layer 3: Phenomenological
            cursor.execute("""
                SELECT AVG(satisfaction_score) as avg_satisfaction
                FROM phenomenological_states
            """)
            export['layers']['phenomenological'] = {
                'average_satisfaction': cursor.fetchone()['avg_satisfaction']
            }
            
            # Layer 4: Metacognitive
            cursor.execute("SELECT COUNT(*) as count FROM metacognitive_capabilities")
            export['layers']['metacognitive'] = {
                'capability_count': cursor.fetchone()['count']
            }
            
            cursor.execute("""
                SELECT AVG(confidence_level) as avg_confidence
                FROM metacognitive_capabilities
            """)
            export['layers']['metacognitive']['average_confidence'] = cursor.fetchone()['avg_confidence']
        
        return export


# === Singleton Instance ===

_integration_instance: Optional[SKGIntegration] = None

def get_skg_integration() -> SKGIntegration:
    """Get or create the singleton SKG integration instance"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = SKGIntegration()
    return _integration_instance