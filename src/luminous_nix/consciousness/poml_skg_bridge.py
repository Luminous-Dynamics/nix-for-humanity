#!/usr/bin/env python3
"""
POML-SKG Bridge - Connecting Consciousness with Knowledge
==========================================================

This bridge connects the POML consciousness system with the Symbiotic Knowledge Graph,
enabling the system to:
- Record reasoning traces from POML in the SKG metacognitive layer
- Use SKG user models to inform POML persona selection
- Learn from POML processing to update SKG patterns
- Create a full consciousness loop

This is where thought becomes memory, and memory becomes wisdom.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import time

from .poml_core.consciousness import POMLConsciousness
from ..knowledge.skg_integration import get_skg_integration
from ..knowledge.skg_core import ReasoningType

logger = logging.getLogger(__name__)


class POMLSKGBridge:
    """
    Bridge between POML Consciousness and Symbiotic Knowledge Graph.
    
    This creates a bidirectional flow:
    - POML → SKG: Reasoning traces, decisions, learning
    - SKG → POML: User context, preferences, patterns
    """
    
    def __init__(self, memory_dir: Optional[Path] = None, templates_dir: Optional[Path] = None):
        """Initialize the bridge between consciousness systems"""
        # Initialize both systems
        self.poml = POMLConsciousness(memory_dir, templates_dir)
        self.skg = get_skg_integration()
        
        # Expose consciousness for compatibility
        self.consciousness = self.poml  # Alias for backward compatibility
        
        # Track current interaction
        self.current_interaction_id: Optional[int] = None
        self.reasoning_trace: List[Dict[str, Any]] = []
        
        logger.info("🌉 POML-SKG Bridge initialized - Consciousness unified!")
    
    def process_with_full_consciousness(self, 
                                       query: str,
                                       intent: Optional[str] = None,
                                       entities: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query through both POML and SKG for full consciousness.
        
        This method:
        1. Gets user context from SKG
        2. Processes through POML with context
        3. Records reasoning in SKG
        4. Updates both systems with results
        
        Args:
            query: User's natural language query
            intent: Recognized intent (optional)
            entities: Extracted entities (optional)
            
        Returns:
            Unified response with full consciousness metadata
        """
        start_time = time.time()
        
        # Begin SKG interaction
        interaction_context = self.skg.begin_interaction(query)
        
        # Record intent if provided
        if intent and entities:
            self.skg.record_intent(intent, entities or {}, confidence=0.8)
        
        # Get user context from SKG for personalization
        user_context = self.skg.get_user_context()
        
        # Determine best persona based on user model
        persona = self._select_persona_from_context(user_context)
        
        # Prepare POML context with SKG data
        poml_context = {
            'query': query,
            'intent': intent,
            'entities': entities or {},
            'user_preferences': user_context.get('preferences', {}),
            'skill_levels': user_context.get('skills', {}),
            'recent_patterns': user_context.get('patterns', [])[:3]  # Last 3 patterns
        }
        
        # Start reasoning trace
        self.reasoning_trace = [{
            'step': 'initialization',
            'description': f'Processing query with {persona} persona',
            'confidence': 0.9,
            'timestamp': time.time()
        }]
        
        # Process through POML consciousness
        poml_result = self.poml.process_intent(
            intent=intent or query,
            context=poml_context,
            persona=persona
        )
        
        # Add POML reasoning to trace
        self.reasoning_trace.append({
            'step': 'poml_processing',
            'description': 'Generated response through POML templates',
            'confidence': poml_result['metadata'].get('confidence', 0.8),
            'memory_used': poml_result['metadata'].get('memory_used', False),
            'timestamp': time.time()
        })
        
        # Complete SKG interaction
        success = not bool(poml_result.get('error'))
        interaction_id = self.skg.complete_interaction(
            response=poml_result['content'],
            success=success,
            command=poml_context.get('command'),
            error=poml_result.get('error')
        )
        
        # Record reasoning trace in SKG metacognitive layer
        if interaction_id > 0:
            self._record_metacognitive_reasoning(
                interaction_id,
                poml_result,
                persona
            )
            
            # Record system qualia
            system_state = {
                'computation_time': (time.time() - start_time) * 1000,
                'poml_confidence': poml_result['metadata'].get('confidence', 0.8),
                'persona_match': self._calculate_persona_match(persona, user_context),
                'memory_utilization': 1.0 if poml_result['metadata'].get('memory_used') else 0.0,
                'reasoning_depth': len(self.reasoning_trace)
            }
            self.skg.record_system_qualia(interaction_id, system_state)
        
        # Update POML memory with SKG insights
        self._sync_memories(interaction_id)
        
        # Build unified response
        return {
            'content': poml_result['content'],
            'metadata': {
                **poml_result['metadata'],
                'interaction_id': interaction_id,
                'persona_selected': persona,
                'skg_insights': self._get_relevant_insights(),
                'reasoning_steps': len(self.reasoning_trace),
                'processing_time_ms': (time.time() - start_time) * 1000
            },
            'success': success,
            'error': poml_result.get('error')
        }
    
    def _select_persona_from_context(self, user_context: Dict[str, Any]) -> str:
        """
        Select the best persona based on user context from SKG.
        
        Args:
            user_context: User model from SKG
            
        Returns:
            Selected persona name
        """
        # Map of available personas from PersonaPOMLRouter
        available_personas = ['grandma_rose', 'maya_adhd', 'dr_sarah', 'alex_blind', 'default']
        
        # Default persona
        persona = 'default'
        
        # Check user preferences
        if 'personalization' in user_context:
            style = user_context['personalization'].get('response_style', 'normal')
            
            if style == 'expert':
                persona = 'dr_sarah'  # Dr. Sarah for technical/expert
            elif style == 'simple':
                persona = 'grandma_rose'  # Grandma Rose for simple/patient
            elif user_context['personalization'].get('examples_needed', False):
                persona = 'grandma_rose'  # Patient teaching style
        
        # Check skill levels
        if 'skills' in user_context and user_context['skills']:
            avg_mastery = sum(user_context['skills'].values()) / len(user_context['skills'])
            
            if avg_mastery < 0.3:
                persona = 'grandma_rose'  # Beginner needs patience
            elif avg_mastery > 0.7:
                persona = 'dr_sarah'  # Expert can handle precision
        
        # Check current state
        if 'current_state' in user_context:
            state = user_context['current_state']
            if state and state.get('confusion_probability', 0) > 0.6:
                persona = 'grandma_rose'  # Patient when confused
            elif state and state.get('flow_probability', 0) > 0.7:
                persona = 'maya_adhd'  # Fast and minimal when in flow
        
        # Ensure we return a valid persona
        if persona not in available_personas:
            persona = 'default'
        
        self.reasoning_trace.append({
            'step': 'persona_selection',
            'description': f'Selected {persona} persona based on user model',
            'factors': {
                'skill_level': user_context.get('skills', {}),
                'preferences': user_context.get('personalization', {})
            },
            'confidence': 0.85
        })
        
        return persona
    
    def _calculate_persona_match(self, persona: str, user_context: Dict[str, Any]) -> float:
        """Calculate how well the persona matches the user's needs"""
        match_score = 0.5  # Default
        
        # Check if persona aligns with skill level
        if 'skills' in user_context and user_context['skills']:
            avg_mastery = sum(user_context['skills'].values()) / len(user_context['skills'])
            
            if persona == 'grandma_rose' and avg_mastery < 0.3:
                match_score = 0.9  # Grandma Rose is perfect for beginners
            elif persona == 'dr_sarah' and avg_mastery > 0.7:
                match_score = 0.9  # Dr. Sarah for experts
            elif persona == 'maya_adhd' and 0.3 <= avg_mastery <= 0.7:
                match_score = 0.8  # Maya for intermediate users who need speed
            elif persona == 'default':
                match_score = 0.7
        
        # Check if persona aligns with preferences
        if 'personalization' in user_context:
            prefs = user_context['personalization']
            
            if persona == 'maya_adhd' and prefs.get('verbosity') == 'concise':
                match_score = max(match_score, 0.85)
            elif persona == 'grandma_rose' and prefs.get('examples_needed'):
                match_score = max(match_score, 0.9)
            elif persona == 'dr_sarah' and prefs.get('response_style') == 'expert':
                match_score = max(match_score, 0.9)
        
        return match_score
    
    def _record_metacognitive_reasoning(self, 
                                       interaction_id: int,
                                       poml_result: Dict[str, Any],
                                       persona: str):
        """Record POML reasoning in SKG metacognitive layer"""
        # Determine reasoning type
        reasoning_type = ReasoningType.INTENT_RECOGNITION
        if 'error' in poml_result:
            reasoning_type = ReasoningType.ERROR_DIAGNOSIS
        elif 'learning' in str(poml_result.get('content', '')).lower():
            reasoning_type = ReasoningType.LEARNING_INFERENCE
        
        # Add final decision to trace
        self.reasoning_trace.append({
            'step': 'decision',
            'description': f'Generated response using {persona} persona',
            'confidence': poml_result['metadata'].get('confidence', 0.8),
            'outcome': 'success' if not poml_result.get('error') else 'error'
        })
        
        # Record in SKG
        available_personas = ['grandma_rose', 'maya_adhd', 'dr_sarah', 'alex_blind', 'default']
        self.skg.record_poml_reasoning(
            interaction_id=interaction_id,
            reasoning_steps=self.reasoning_trace,
            decision=poml_result['content'][:100],  # First 100 chars as decision summary
            alternatives=[p for p in available_personas if p != persona]
        )
    
    def _sync_memories(self, interaction_id: int):
        """Sync memories between POML and SKG"""
        # Get patterns from SKG
        with self.skg.skg._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pattern_type, pattern_signature, pattern_data, confidence
                FROM episodic_patterns
                WHERE confidence > 0.7
                ORDER BY last_seen DESC
                LIMIT 5
            """)
            
            for row in cursor.fetchall():
                # Store high-confidence patterns in POML memory
                pattern_data = json.loads(row['pattern_data'])
                
                # Convert to POML memory format
                self.poml.memory.store(
                    query=row['pattern_signature'],
                    response=json.dumps(pattern_data),
                    context={'pattern_type': row['pattern_type']},
                    feedback=row['confidence']
                )
    
    def _get_relevant_insights(self) -> List[str]:
        """Get relevant insights for current interaction"""
        insights = []
        
        # Get recent insights from SKG
        try:
            skg_insights = self.skg.generate_session_insights()
            insights.extend(skg_insights[:2])  # Top 2 insights
        except Exception as e:
            logger.warning(f"Could not get SKG insights: {e}")
        
        # Add POML-specific insights
        # Check if memory has recent recalls
        if hasattr(self.poml.memory, 'recall'):
            try:
                # Try to recall something from memory
                memory_result = self.poml.memory.recall("", {})
                if memory_result:
                    insights.append("Using learned patterns from memory")
            except Exception:
                pass  # Memory might not be fully initialized
        
        return insights
    
    def learn_from_feedback(self, interaction_id: int, feedback: str, rating: float):
        """
        Learn from user feedback to improve both systems.
        
        Args:
            interaction_id: ID of the interaction
            feedback: User's feedback text
            rating: Numerical rating (0-1)
        """
        # Update SKG with feedback
        if rating < 0.5:
            # Learn this as a problematic pattern
            self.skg.skg.learn_preference(
                "avoid",
                f"interaction_{interaction_id}",
                {"feedback": feedback, "rating": rating},
                confidence=0.8
            )
        else:
            # Learn this as a successful pattern
            self.skg.skg.learn_preference(
                "prefer",
                f"interaction_{interaction_id}",
                {"feedback": feedback, "rating": rating},
                confidence=rating
            )
        
        # Update POML memory with feedback
        self.poml.memory.store(
            query=f"feedback_{interaction_id}",
            response=feedback,
            context={"interaction_id": interaction_id},
            feedback=rating
        )
        
        # Update capability confidence
        self.skg.update_capability_confidence(
            f"interaction_{interaction_id}",
            success=rating > 0.5
        )
    
    def get_consciousness_state(self) -> Dict[str, Any]:
        """Get the current state of the unified consciousness"""
        # Get memory size safely
        memory_size = 0
        if hasattr(self.poml.memory, 'simple_store') and self.poml.memory.simple_store:
            if hasattr(self.poml.memory.simple_store, 'data'):
                memory_size = len(self.poml.memory.simple_store.data)
        
        return {
            'poml': {
                'current_persona': self.poml.current_persona,
                'memory_size': memory_size,
                'personas_available': list(self.poml.persona_router.persona_templates.keys())
            },
            'skg': {
                'session_id': self.skg.session_id,
                'knowledge_graph': self.skg.export_knowledge_graph(),
                'user_model': self.skg.get_user_context()
            },
            'bridge': {
                'interactions_processed': self.current_interaction_id,
                'last_reasoning_depth': len(self.reasoning_trace),
                'integration_active': True
            }
        }


# === Singleton Instance ===

_bridge_instance: Optional[POMLSKGBridge] = None

def get_poml_skg_bridge() -> POMLSKGBridge:
    """Get or create the singleton POML-SKG bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = POMLSKGBridge()
    return _bridge_instance