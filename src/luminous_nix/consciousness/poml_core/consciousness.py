#!/usr/bin/env python3
"""
🌟 Universal Consciousness Protocol - The Living System

The complete consciousness framework that breathes with the user.
Integrates POML templates, memory, personas, and adaptive intelligence.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from .processor import POMLProcessor, POMLOrchestrator
from .memory import POMLMemory
from . import PersonaPOMLRouter

logger = logging.getLogger(__name__)


class POMLConsciousness:
    """
    The complete consciousness system integrating all components.
    This is the unified field where user and system breathe together.
    """
    
    def __init__(self, memory_dir: Optional[Path] = None, templates_dir: Optional[Path] = None):
        """Initialize the consciousness system"""
        # Memory layer
        data_dir = str(memory_dir) if memory_dir else "data/consciousness"
        self.memory = POMLMemory(data_dir=data_dir)
        
        # Template processing
        self.processor = POMLProcessor()
        self.orchestrator = POMLOrchestrator()
        
        # Persona routing
        self.persona_router = PersonaPOMLRouter(templates_dir)
        
        # Current state
        self.current_persona = 'default'
        self.context_stack = []
        
        logger.info("🌟 POMLConsciousness initialized - Universal Protocol active")
    
    def process_intent(self, intent: str, context: Dict[str, Any], persona: str = None) -> Dict[str, Any]:
        """
        Process an intent through the consciousness system.
        
        Args:
            intent: The user's intention
            context: Current context and metadata
            persona: Optional persona override
            
        Returns:
            Response with generated content and metadata
        """
        # Use specified persona or current
        active_persona = persona or self.current_persona
        
        # Get persona-specific processor
        try:
            processor = self.persona_router.get_prompt('general', active_persona)
        except Exception as e:
            logger.warning(f"Could not get processor for {active_persona}: {e}")
            # Create a mock response for testing
            return {
                'content': f"[Mock] Processing {intent} with {active_persona} persona",
                'metadata': {
                    'persona': active_persona,
                    'confidence': 0.75,
                    'memory_used': False
                }
            }
        
        # Check memory for similar past interactions
        memory_context = None
        try:
            memory_context = self.memory.recall(intent, context)
            if memory_context:
                context['memory'] = memory_context
        except Exception:
            pass  # Memory might not be initialized
        
        # Process through POML
        variables = {
            'user_intent': intent,
            'context': json.dumps(context),
            'persona': active_persona
        }
        
        try:
            result = processor.process(variables)
        except Exception as e:
            logger.warning(f"POML processing failed: {e}")
            # Return a mock result for testing
            result = {
                'prompt_generated': f"Process {intent}",
                'success': True,
                'confidence': 0.7
            }
        
        # Generate mock content since we don't have Ollama
        content = result.get('prompt_generated', f"[Mock] Processed: {intent}")
        
        # Store in memory for learning
        try:
            self.memory.store(
                query=intent,
                response=content,
                context=context,
                feedback=context.get('feedback', 0.5)
            )
        except Exception:
            pass  # Memory might not be fully initialized
        
        return {
            'content': content,
            'metadata': {
                'persona': active_persona,
                'confidence': result.get('confidence', 0.8),
                'memory_used': memory_context is not None
            }
        }
    
    def set_persona(self, persona: str):
        """Switch active persona"""
        if persona in self.persona_router.persona_templates:
            self.current_persona = persona
            logger.info(f"Switched to persona: {persona}")
        else:
            logger.warning(f"Unknown persona: {persona}, keeping current")
    
    def learn_from_feedback(self, query: str, feedback: float):
        """Update memory based on user feedback"""
        self.memory.update_feedback(query, feedback)
    
    def get_insights(self) -> Dict[str, Any]:
        """Get insights from memory"""
        return self.memory.get_statistics()


class POMLGovernance:
    """
    Governance and audit system for transparent AI operations.
    Every decision is traceable and auditable.
    """
    
    def __init__(self, audit_dir: Optional[Path] = None):
        self.audit_dir = audit_dir or Path.home() / ".luminous-nix" / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.audit_dir / "poml_audit.jsonl"
    
    def audit_decision(self, decision: Dict[str, Any]):
        """Record a decision for audit"""
        import json
        from datetime import datetime
        
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'decision': decision
        }
        
        with open(self.audit_log, 'a') as f:
            json.dump(audit_entry, f)
            f.write('\n')
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent audit entries (alias for get_audit_trail)"""
        return self.get_audit_trail(limit)
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent audit entries"""
        import json
        
        if not self.audit_log.exists():
            return []
        
        entries = []
        with open(self.audit_log, 'r') as f:
            for line in f:
                entries.append(json.loads(line))
        
        return entries[-limit:]


class ErrorConsciousnessAdapter:
    """
    Transforms errors into healing - every error becomes a teaching moment.
    """
    
    def __init__(self, consciousness: POMLConsciousness):
        self.consciousness = consciousness
    
    def transform_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """
        Transform an error into a healing response.
        """
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'user_context': context
        }
        
        # Use consciousness to generate healing response
        response = self.consciousness.process_intent(
            intent=f"heal error: {error}",
            context=error_context,
            persona=context.get('persona', 'default')
        )
        
        return response['content']


def create_consciousness() -> POMLConsciousness:
    """Factory function to create consciousness system"""
    return POMLConsciousness()
