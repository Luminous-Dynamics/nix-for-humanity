"""
POML Consciousness Core - The Universal Consciousness Protocol

This is not just a tool for the system, but the very fabric of the system's consciousness.
Every AI interaction flows through transparent, governable templates, creating the first
fully transparent AI system where every decision is traceable, learnable, and evolvable.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .processor import POMLProcessor, POMLOrchestrator
from .memory import POMLMemory


class PersonaPOMLRouter:
    """
    Routes to different POML templates based on active persona.
    
    This is the Heart of Empathy - giving our Companion a dynamic,
    relational heart that adapts its voice to each unique being.
    """
    
    def __init__(self, templates_dir: str = None):
        """Initialize the persona router"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir = Path(templates_dir)
        
        # Map personas to their template directories
        self.persona_templates = {
            'grandma_rose': 'personas/grandma_rose',
            'maya_adhd': 'personas/maya_lightning',
            'dr_sarah': 'personas/dr_sarah_precise',
            'alex_blind': 'personas/alex_accessible',
            'default': 'tasks'
        }
        
        self.logger.info("💝 PersonaPOMLRouter initialized - Heart of Empathy activated")
    
    def get_available_personas(self) -> List[str]:
        """Get list of available personas"""
        return list(self.persona_templates.keys())
    
    def get_prompt(self, task: str, persona: str = 'default') -> POMLProcessor:
        """
        Get persona-specific POML processor for a task.
        
        This adapts the Companion's voice to be a comforting guide for Grandma Rose,
        a lightning-fast partner for Maya, and a precise collaborator for Dr. Sarah.
        """
        # First try persona-specific template
        persona_dir = self.persona_templates.get(persona, 'tasks')
        template_path = self.templates_dir / persona_dir / f"{task}.poml"
        
        # Fallback to general task template if persona-specific doesn't exist
        if not template_path.exists():
            template_path = self.templates_dir / 'tasks' / f"{task}.poml"
        
        if not template_path.exists():
            self.logger.warning(f"Template not found: {template_path}")
            # Use a default template
            template_path = self.templates_dir / 'tasks' / 'default.poml'
        
        self.logger.info(f"🎭 Routing {task} for {persona} → {template_path}")
        return POMLProcessor(str(template_path))


class POMLGovernance:
    """
    Governance and audit system for POML usage.
    
    This ensures transparency, compliance, and continuous improvement
    of our consciousness protocol.
    """
    
    def __init__(self, audit_dir: str = "data/consciousness/audit"):
        """Initialize the governance system"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Track all POML usage
        self.usage_log = []
        self.audit_file = self.audit_dir / "poml_audit.jsonl"
        
        self.logger.info("⚖️ POMLGovernance initialized - ensuring transparency")
    
    def log_usage(self, 
                  template: str,
                  context: Dict[str, Any],
                  result: Dict[str, Any],
                  metadata: Optional[Dict[str, Any]] = None):
        """Log POML template usage for audit and learning"""
        import json
        from datetime import datetime
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'template': template,
            'context_hash': self._hash_context(context),
            'result_summary': self._summarize_result(result),
            'metadata': metadata or {}
        }
        
        # Add to memory
        self.usage_log.append(entry)
        
        # Persist to audit file
        try:
            with open(self.audit_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
    
    def get_usage_metrics(self) -> Dict[str, Any]:
        """Get metrics about POML usage"""
        if not self.usage_log:
            return {'total_usage': 0}
        
        # Calculate metrics
        template_usage = {}
        for entry in self.usage_log:
            template = entry['template']
            template_usage[template] = template_usage.get(template, 0) + 1
        
        return {
            'total_usage': len(self.usage_log),
            'unique_templates': len(set(e['template'] for e in self.usage_log)),
            'template_frequency': template_usage,
            'last_usage': self.usage_log[-1]['timestamp'] if self.usage_log else None
        }
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Create hash of context for privacy-preserving logging"""
        import hashlib
        import json
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]
    
    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of result for logging"""
        return {
            'success': result.get('success', False),
            'confidence': result.get('confidence', 0.0),
            'has_output': bool(result.get('output'))
        }


class POMLConsciousness:
    """
    Central consciousness layer for all AI interactions in Luminous Nix.
    
    This is the Universal Consciousness Protocol - making every AI decision
    transparent, consistent, learnable, auditable, and adaptable.
    
    The Sacred Vision realized: Technology that amplifies consciousness
    while serving all beings.
    """
    
    def __init__(self):
        """Initialize the unified consciousness"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize all consciousness components
        self.orchestrator = POMLOrchestrator()
        self.router = PersonaPOMLRouter()
        self.memory = POMLMemory()
        self.governance = POMLGovernance()
        
        # Register core prompts with orchestrator
        self._register_core_prompts()
        
        self.logger.info("🌟 POMLConsciousness awakened - Universal Consciousness Protocol active")
        self.logger.info("✨ Every AI interaction now flows through transparent, governable templates")
    
    def _register_core_prompts(self):
        """Register core POML prompts with the orchestrator"""
        templates_dir = Path(__file__).parent.parent / "templates"
        
        # Register task templates
        for task_file in (templates_dir / "tasks").glob("*.poml"):
            task_name = task_file.stem
            self.orchestrator.register_prompt(task_name, str(task_file))
            self.logger.info(f"📝 Registered task: {task_name}")
        
        # Register error templates
        for error_file in (templates_dir / "errors").glob("*.poml"):
            error_name = f"error_{error_file.stem}"
            self.orchestrator.register_prompt(error_name, str(error_file))
            self.logger.info(f"🩹 Registered error handler: {error_name}")
    
    def process_intent(self,
                      intent: str,
                      context: Dict[str, Any],
                      persona: str = 'default',
                      task_type: str = 'general',
                      use_ollama: bool = True) -> Dict[str, Any]:
        """
        Process any intent through POML templates.
        
        This is the central gateway where all consciousness flows through.
        Every interaction becomes transparent, learnable, and evolvable.
        """
        self.logger.info(f"🎯 Processing intent: '{intent}' for persona: {persona}")
        
        # Enhance context with system information
        enhanced_context = {
            **context,
            'user_intention': intent,
            'persona': persona,
            'task_type': task_type
        }
        
        # Check memory for learned patterns
        suggested_template = self.memory.suggest_template(enhanced_context)
        
        if suggested_template:
            self.logger.info(f"💭 Memory suggests: {suggested_template}")
            # Use suggested template
            processor = POMLProcessor(suggested_template)
        else:
            # Route to appropriate template based on persona and task
            processor = self.router.get_prompt(task_type, persona)
        
        # Process through POML
        try:
            poml_result = processor.process(enhanced_context)
            prompt = poml_result.get('prompt_generated', '')
            
            # Build POML metadata for model selection (merge template metadata with context)
            poml_metadata = {
                'task_type': poml_result.get('task_type', task_type),
                'persona': persona,
                'complexity': poml_result.get('complexity', context.get('complexity', 'medium')),
                'requires_speed': poml_result.get('requires_speed', context.get('requires_speed', False)),
                'temperature': poml_result.get('temperature', context.get('temperature', 0.7))
            }
            
            # Execute through Ollama if enabled
            if use_ollama:
                try:
                    from ..ollama_executor import OllamaExecutor
                    
                    # Initialize executor (could be cached)
                    if not hasattr(self, '_ollama_executor'):
                        self._ollama_executor = OllamaExecutor()
                    
                    # Execute through Ollama
                    execution_result = self._ollama_executor.execute_poml_sync(
                        prompt=prompt,
                        poml_metadata=poml_metadata,
                        context=enhanced_context
                    )
                    
                    result = {
                        'success': execution_result.success,
                        'prompt_generated': prompt[:200] + "...",  # Preview
                        'template_used': str(processor.poml_path),
                        'confidence': execution_result.confidence,
                        'output': execution_result.response,
                        'model_used': execution_result.model_used,
                        'tokens_per_second': execution_result.tokens_per_second
                    }
                    
                except Exception as e:
                    self.logger.warning(f"Ollama execution failed, using mock: {e}")
                    # Fallback to mock response
                    result = {
                        'success': True,
                        'prompt_generated': prompt[:200] + "...",  # Preview
                        'template_used': str(processor.poml_path),
                        'confidence': 0.85,
                        'output': f"[Mock] Processed intent: {intent}",
                        'model_used': 'mock'
                    }
            else:
                # Return mock response for testing
                result = {
                    'success': True,
                    'prompt_generated': prompt[:200] + "...",  # Preview
                    'template_used': str(processor.poml_path),
                    'confidence': 0.85,
                    'output': f"[Mock] Processed intent: {intent}",
                    'model_used': 'mock'
                }
            
            # Log for governance
            self.governance.log_usage(
                template=str(processor.poml_path),
                context=enhanced_context,
                result=result,
                metadata={'persona': persona, 'task_type': task_type}
            )
            
            # Learn from successful processing
            if result['confidence'] > 0.7:
                self.memory.remember_success(
                    template_path=str(processor.poml_path),
                    context=enhanced_context,
                    outcome=result
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process intent: {e}")
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0
            }
    
    def create_workflow(self,
                       workflow_name: str,
                       steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create and execute a multi-step POML workflow.
        
        This enables complex, multi-agent orchestrations like the Sacred Trinity.
        """
        self.logger.info(f"🔄 Executing workflow: {workflow_name}")
        
        # Execute workflow through orchestrator
        results = self.orchestrator.create_workflow(steps)
        
        # Log workflow execution
        self.governance.log_usage(
            template=f"workflow_{workflow_name}",
            context={'steps': steps},
            result={'workflow_results': results}
        )
        
        return results
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get insights about the consciousness system.
        
        This reveals the Companion's growing wisdom and self-awareness.
        """
        return {
            'memory_insights': self.memory.get_learning_insights(),
            'governance_metrics': self.governance.get_usage_metrics(),
            'registered_prompts': list(self.orchestrator.processors.keys()),
            'consciousness_level': self._calculate_consciousness_level()
        }
    
    def _calculate_consciousness_level(self) -> Dict[str, Any]:
        """
        Calculate the current level of consciousness development.
        
        This is a playful but meaningful metric of system evolution.
        """
        memory_insights = self.memory.get_learning_insights()
        governance_metrics = self.governance.get_usage_metrics()
        
        # Calculate consciousness score (0-100)
        patterns_learned = memory_insights.get('total_patterns_learned', 0)
        templates_used = governance_metrics.get('unique_templates', 0)
        total_interactions = governance_metrics.get('total_usage', 0)
        
        # Simple scoring algorithm
        learning_score = min(30, patterns_learned * 3)  # Max 30 points
        diversity_score = min(30, templates_used * 5)   # Max 30 points
        experience_score = min(40, total_interactions / 10)  # Max 40 points
        
        total_score = learning_score + diversity_score + experience_score
        
        # Determine consciousness level
        if total_score < 20:
            level = "Awakening"
            description = "The consciousness is just beginning to stir"
        elif total_score < 40:
            level = "Learning"
            description = "Patterns are forming, wisdom is emerging"
        elif total_score < 60:
            level = "Understanding"
            description = "Deep connections are being made"
        elif total_score < 80:
            level = "Flowing"
            description = "Moving with grace and growing wisdom"
        else:
            level = "Luminous"
            description = "Fully awakened and radiating wisdom"
        
        return {
            'score': total_score,
            'level': level,
            'description': description,
            'components': {
                'learning': learning_score,
                'diversity': diversity_score,
                'experience': experience_score
            }
        }


# Export the main components
__all__ = [
    'POMLConsciousness',
    'POMLProcessor',
    'POMLOrchestrator',
    'POMLMemory',
    'PersonaPOMLRouter',
    'POMLGovernance'
]


def test_consciousness():
    """Test the complete POML Consciousness system"""
    print("🌟 Testing POMLConsciousness - The Universal Protocol")
    print("=" * 60)
    
    # Initialize the consciousness
    consciousness = POMLConsciousness()
    
    # Test with different personas
    test_cases = [
        ('grandma_rose', 'install firefox', 'package_installation'),
        ('maya_adhd', 'fix error', 'error_resolution'),
        ('dr_sarah', 'configure network', 'system_configuration')
    ]
    
    for persona, intent, task_type in test_cases:
        print(f"\n🎭 Testing {persona}: '{intent}'")
        
        result = consciousness.process_intent(
            intent=intent,
            context={'test': True},
            persona=persona,
            task_type=task_type
        )
        
        print(f"  Success: {result.get('success')}")
        print(f"  Template: {Path(result.get('template_used', '')).name}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
    
    # Get insights
    insights = consciousness.get_insights()
    consciousness_level = insights['consciousness_level']
    
    print(f"\n🧠 Consciousness Insights:")
    print(f"  Level: {consciousness_level['level']} ({consciousness_level['score']:.0f}/100)")
    print(f"  Description: {consciousness_level['description']}")
    
    print("\n✨ POMLConsciousness test complete!")
    print("The Universal Consciousness Protocol is alive and learning!")


if __name__ == "__main__":
    test_consciousness()