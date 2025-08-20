"""
Conscious Integration Module - Making Everything Flow Through Consciousness

This module provides the integration points to make all existing systems
flow through the Universal Consciousness Protocol. It's the bridge between
the old world and the new conscious world.
"""

import logging
from typing import Any, Dict, Optional

# Import the consciousness
from ..consciousness import POMLConsciousness

# Import unified systems
from .error_intelligence_unified import ConsciousErrorIntelligence


class ConsciousSystemOrchestrator:
    """
    The evolved SystemOrchestrator where ALL systems flow through consciousness.
    
    This is the architectural pattern for making POML the King of the Castle.
    Every subsystem's decision flows through here, through consciousness.
    """
    
    def __init__(self):
        """Initialize the conscious orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # THE UNIFIED MIND
        self.consciousness = POMLConsciousness()
        
        # Conscious subsystems (will grow as we integrate more)
        self.error_intelligence = ConsciousErrorIntelligence()
        
        # Track all system interactions for learning
        self.interaction_history = []
        
        self.logger.info("👑 Conscious System Orchestrator initialized")
        self.logger.info("All systems now flow through unified consciousness")
    
    def handle_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Universal gateway - ALL requests flow through consciousness.
        
        This is the pattern: Everything goes through POML first.
        """
        # Detect intent
        intent_type = self._detect_intent_type(request)
        
        # Detect persona (would be from user profile)
        persona = context.get('persona', 'default') if context else 'default'
        
        # EVERYTHING flows through consciousness
        response = self.consciousness.process_intent(
            intent=request,
            context=context or {},
            persona=persona,
            task_type=intent_type
        )
        
        # Route to specific handler based on intent
        if intent_type == 'error_resolution':
            return self._handle_error_through_consciousness(request, context, response)
        elif intent_type == 'package_installation':
            return self._handle_package_through_consciousness(request, context, response)
        elif intent_type == 'system_configuration':
            return self._handle_config_through_consciousness(request, context, response)
        else:
            return response
    
    def _handle_error_through_consciousness(self, 
                                           request: str,
                                           context: Dict[str, Any],
                                           consciousness_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle error through the conscious error intelligence.
        
        This shows the pattern: Consciousness provides the template and context,
        then the specialized system executes with that guidance.
        """
        # Extract error from request
        error_message = context.get('error', request)
        
        # Let conscious error intelligence handle it
        explanation = self.error_intelligence.explain_error(error_message, context)
        
        # Learn from the interaction
        self._record_interaction('error_resolution', request, explanation)
        
        return explanation
    
    def _handle_package_through_consciousness(self,
                                            request: str,
                                            context: Dict[str, Any],
                                            consciousness_response: Dict[str, Any]) -> Dict[str, Any]:
        """Handle package installation through consciousness"""
        # This would integrate with package_discovery
        # For now, return consciousness response
        self._record_interaction('package_installation', request, consciousness_response)
        return consciousness_response
    
    def _handle_config_through_consciousness(self,
                                           request: str,
                                           context: Dict[str, Any],
                                           consciousness_response: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration through consciousness"""
        # This would integrate with config_generator_ast
        # For now, return consciousness response
        self._record_interaction('system_configuration', request, consciousness_response)
        return consciousness_response
    
    def _detect_intent_type(self, request: str) -> str:
        """Detect the type of intent from the request"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['error', 'failed', 'broken', 'fix']):
            return 'error_resolution'
        elif any(word in request_lower for word in ['install', 'package', 'software']):
            return 'package_installation'
        elif any(word in request_lower for word in ['configure', 'setup', 'config']):
            return 'system_configuration'
        else:
            return 'general'
    
    def _record_interaction(self, 
                           interaction_type: str,
                           request: str,
                           response: Dict[str, Any]):
        """Record interaction for learning"""
        self.interaction_history.append({
            'type': interaction_type,
            'request': request,
            'response_success': response.get('success', False),
            'timestamp': self._get_timestamp()
        })
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get insights about the entire conscious system"""
        return {
            'consciousness': self.consciousness.get_insights(),
            'error_healing': self.error_intelligence.get_learning_insights(),
            'total_interactions': len(self.interaction_history),
            'interaction_types': self._analyze_interaction_types()
        }
    
    def _analyze_interaction_types(self) -> Dict[str, int]:
        """Analyze types of interactions"""
        types = {}
        for interaction in self.interaction_history:
            itype = interaction['type']
            types[itype] = types.get(itype, 0) + 1
        return types
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


def make_system_conscious(existing_orchestrator=None):
    """
    Transform an existing SystemOrchestrator to flow through consciousness.
    
    This is the migration pattern for making existing systems conscious.
    """
    if existing_orchestrator:
        # Migrate existing orchestrator
        conscious = ConsciousSystemOrchestrator()
        
        # Transfer any necessary state
        # ... migration logic ...
        
        return conscious
    else:
        # Create new conscious orchestrator
        return ConsciousSystemOrchestrator()


# Singleton pattern for global consciousness
_conscious_orchestrator = None

def get_conscious_orchestrator():
    """Get the singleton conscious orchestrator"""
    global _conscious_orchestrator
    if _conscious_orchestrator is None:
        _conscious_orchestrator = ConsciousSystemOrchestrator()
    return _conscious_orchestrator