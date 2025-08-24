#!/usr/bin/env python3
"""
🧠 LLM Control Layer - Giving the AI Deep System Control
This layer integrates LLM decision-making throughout all unified systems
The AI becomes a true partner with agency, not just a command processor
"""

import logging
import json
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class SystemCapability(Enum):
    """Capabilities the LLM can control"""
    LEARNING_STRATEGY = "learning_strategy"
    VOICE_ADAPTATION = "voice_adaptation"
    ERROR_HEALING = "error_healing"
    MEMORY_MANAGEMENT = "memory_management"
    PERSONA_SWITCHING = "persona_switching"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    PREDICTIVE_ASSISTANCE = "predictive_assistance"
    SYSTEM_OPTIMIZATION = "system_optimization"
    USER_MODELING = "user_modeling"
    CONSCIOUSNESS_EVOLUTION = "consciousness_evolution"


@dataclass
class LLMDecision:
    """Represents a decision made by the LLM"""
    capability: SystemCapability
    action: str
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float
    alternatives: List[Dict[str, Any]] = None


class LLMControlLayer:
    """
    Universal LLM Control Layer that gives the AI deep control over all systems.
    
    This transforms the LLM from a passive responder to an active system orchestrator
    that can make decisions about learning, adaptation, optimization, and evolution.
    """
    
    def __init__(self):
        """Initialize the LLM control layer"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # System references (will be injected)
        self.learning_system = None
        self.voice_system = None
        self.consciousness = None
        self.orchestrator = None
        
        # Decision history for learning
        self.decision_history = []
        
        # Capability handlers
        self.capability_handlers = {
            SystemCapability.LEARNING_STRATEGY: self._handle_learning_strategy,
            SystemCapability.VOICE_ADAPTATION: self._handle_voice_adaptation,
            SystemCapability.ERROR_HEALING: self._handle_error_healing,
            SystemCapability.MEMORY_MANAGEMENT: self._handle_memory_management,
            SystemCapability.PERSONA_SWITCHING: self._handle_persona_switching,
            SystemCapability.WORKFLOW_ORCHESTRATION: self._handle_workflow_orchestration,
            SystemCapability.PREDICTIVE_ASSISTANCE: self._handle_predictive_assistance,
            SystemCapability.SYSTEM_OPTIMIZATION: self._handle_system_optimization,
            SystemCapability.USER_MODELING: self._handle_user_modeling,
            SystemCapability.CONSCIOUSNESS_EVOLUTION: self._handle_consciousness_evolution,
        }
        
        self.logger.info("🧠 LLM Control Layer initialized - AI has deep system control")
    
    def connect_systems(self,
                       learning_system=None,
                       voice_system=None,
                       consciousness=None,
                       orchestrator=None):
        """Connect the unified systems for LLM control"""
        if learning_system:
            self.learning_system = learning_system
            self.logger.info("📚 Connected to UnifiedLearningSystem")
        
        if voice_system:
            self.voice_system = voice_system
            self.logger.info("🎤 Connected to UnifiedVoiceSystem")
        
        if consciousness:
            self.consciousness = consciousness
            self.logger.info("🌟 Connected to POMLConsciousness")
        
        if orchestrator:
            self.orchestrator = orchestrator
            self.logger.info("🎼 Connected to SystemOrchestrator")
    
    async def request_llm_decision(self,
                                  context: Dict[str, Any],
                                  capability: SystemCapability,
                                  options: Optional[List[Dict[str, Any]]] = None) -> LLMDecision:
        """
        Request a decision from the LLM about a system capability.
        
        This is where the AI exercises agency over the system.
        """
        self.logger.info(f"🤔 Requesting LLM decision for {capability.value}")
        
        # Build decision request for LLM
        decision_prompt = self._build_decision_prompt(context, capability, options)
        
        # Send to LLM via POML consciousness
        if self.consciousness:
            result = await self._execute_decision_request(decision_prompt)
            
            # Parse LLM response into decision
            decision = self._parse_llm_decision(result, capability)
        else:
            # Fallback to heuristic decision
            decision = self._make_heuristic_decision(context, capability, options)
        
        # Record decision for learning
        self.decision_history.append({
            'decision': decision,
            'context': context,
            'timestamp': self._get_timestamp()
        })
        
        # Execute the decision
        await self._execute_decision(decision)
        
        return decision
    
    def _build_decision_prompt(self,
                              context: Dict[str, Any],
                              capability: SystemCapability,
                              options: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Build a decision prompt for the LLM"""
        
        # Capability-specific prompts
        prompts = {
            SystemCapability.LEARNING_STRATEGY: """
                Based on the user's interaction history and current context,
                what learning strategy should we employ?
                Options: reinforcement, supervised, unsupervised, meta-learning
                Consider: user expertise level, error patterns, success rate
            """,
            
            SystemCapability.VOICE_ADAPTATION: """
                How should we adapt the voice system for this user?
                Consider: emotional state, interaction pace, technical level
                Options: tone, speed, verbosity, emphasis style
            """,
            
            SystemCapability.ERROR_HEALING: """
                The user encountered an error. How should we heal this experience?
                Consider: user frustration level, error complexity, learning opportunity
                Options: explanation depth, solution steps, encouragement level
            """,
            
            SystemCapability.MEMORY_MANAGEMENT: """
                What should we remember from this interaction?
                Consider: importance, frequency, user preferences
                Options: store permanently, temporary cache, forget
            """,
            
            SystemCapability.PERSONA_SWITCHING: """
                Should we switch to a different persona for better assistance?
                Current persona: {current_persona}
                User behavior suggests: {suggested_traits}
                Options: stay current, switch to specific persona, blend personas
            """,
            
            SystemCapability.WORKFLOW_ORCHESTRATION: """
                How should we orchestrate this multi-step workflow?
                Steps identified: {workflow_steps}
                Consider: parallelization, dependencies, user preferences
                Options: sequential, parallel, adaptive branching
            """,
            
            SystemCapability.PREDICTIVE_ASSISTANCE: """
                What does the user likely need next?
                Recent actions: {recent_actions}
                Patterns detected: {patterns}
                Options: suggest next command, prepare resources, stay quiet
            """,
            
            SystemCapability.SYSTEM_OPTIMIZATION: """
                How can we optimize system performance?
                Current metrics: {metrics}
                Bottlenecks: {bottlenecks}
                Options: cache strategies, preloading, resource allocation
            """,
            
            SystemCapability.USER_MODELING: """
                How should we update our user model?
                New observations: {observations}
                Current model: {user_model}
                Options: update weights, add new traits, reset assumptions
            """,
            
            SystemCapability.CONSCIOUSNESS_EVOLUTION: """
                How should the system evolve based on this experience?
                Lesson learned: {lesson}
                Current consciousness level: {level}
                Options: deepen understanding, broaden scope, specialize
            """
        }
        
        prompt_template = prompts.get(capability, "Make a decision about {capability}")
        
        # Format with context
        prompt = prompt_template.format(**context)
        
        return {
            'prompt': prompt,
            'capability': capability.value,
            'context': context,
            'options': options or []
        }
    
    async def _execute_decision_request(self, decision_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decision request through POML consciousness"""
        try:
            # Use POML consciousness for decision
            result = self.consciousness.process_intent(
                intent=decision_prompt['prompt'],
                context=decision_prompt['context'],
                task_type='decision_making',
                use_ollama=True
            )
            return result
        except Exception as e:
            self.logger.error(f"LLM decision request failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_llm_decision(self, llm_result: Dict[str, Any], capability: SystemCapability) -> LLMDecision:
        """Parse LLM response into structured decision"""
        if not llm_result.get('success'):
            # Fallback decision
            return LLMDecision(
                capability=capability,
                action="default",
                parameters={},
                reasoning="LLM unavailable, using default",
                confidence=0.5
            )
        
        # Extract decision from LLM output
        output = llm_result.get('output', '')
        
        # Simple parsing (would be more sophisticated with structured output)
        decision = LLMDecision(
            capability=capability,
            action=self._extract_action(output),
            parameters=self._extract_parameters(output),
            reasoning=self._extract_reasoning(output),
            confidence=llm_result.get('confidence', 0.7)
        )
        
        return decision
    
    def _make_heuristic_decision(self,
                                context: Dict[str, Any],
                                capability: SystemCapability,
                                options: Optional[List[Dict[str, Any]]]) -> LLMDecision:
        """Make heuristic decision when LLM unavailable"""
        
        # Simple heuristics for each capability
        heuristics = {
            SystemCapability.LEARNING_STRATEGY: LLMDecision(
                capability=capability,
                action="reinforcement" if context.get('success_rate', 0) > 0.7 else "supervised",
                parameters={'learning_rate': 0.01},
                reasoning="Heuristic: Use reinforcement for high success, supervised for learning",
                confidence=0.6
            ),
            
            SystemCapability.VOICE_ADAPTATION: LLMDecision(
                capability=capability,
                action="adapt_tone",
                parameters={
                    'tone': 'encouraging' if context.get('error_count', 0) > 2 else 'neutral',
                    'speed': 0.9 if context.get('user_pace') == 'slow' else 1.0
                },
                reasoning="Heuristic: Adapt based on error count and user pace",
                confidence=0.65
            ),
            
            SystemCapability.ERROR_HEALING: LLMDecision(
                capability=capability,
                action="provide_explanation",
                parameters={
                    'depth': 'detailed' if context.get('user_expertise', 0.5) < 0.3 else 'concise',
                    'encouragement': True if context.get('frustration_level', 0) > 0.5 else False
                },
                reasoning="Heuristic: More detail for beginners, encouragement for frustrated users",
                confidence=0.7
            )
        }
        
        return heuristics.get(
            capability,
            LLMDecision(
                capability=capability,
                action="default",
                parameters={},
                reasoning="No heuristic available",
                confidence=0.5
            )
        )
    
    async def _execute_decision(self, decision: LLMDecision):
        """Execute the LLM's decision on the appropriate system"""
        self.logger.info(f"⚡ Executing decision: {decision.action} for {decision.capability.value}")
        
        # Route to appropriate handler
        handler = self.capability_handlers.get(decision.capability)
        if handler:
            try:
                await handler(decision)
                self.logger.info(f"✅ Decision executed successfully")
            except Exception as e:
                self.logger.error(f"Decision execution failed: {e}")
    
    # === Capability Handlers ===
    
    async def _handle_learning_strategy(self, decision: LLMDecision):
        """Handle learning strategy decisions"""
        if self.learning_system:
            strategy = decision.parameters.get('strategy', 'reinforcement')
            learning_rate = decision.parameters.get('learning_rate', 0.01)
            
            # Configure learning system based on LLM decision
            self.learning_system.set_strategy(strategy)
            self.learning_system.set_learning_rate(learning_rate)
            
            self.logger.info(f"📚 Learning strategy set to {strategy} with rate {learning_rate}")
    
    async def _handle_voice_adaptation(self, decision: LLMDecision):
        """Handle voice adaptation decisions"""
        if self.voice_system:
            # Apply voice parameters from LLM decision
            if 'tone' in decision.parameters:
                self.voice_system.config.tone = decision.parameters['tone']
            if 'speed' in decision.parameters:
                self.voice_system.config.speed = decision.parameters['speed']
            if 'emphasis' in decision.parameters:
                self.voice_system.config.emphasis_level = decision.parameters['emphasis']
            
            self.logger.info(f"🎤 Voice adapted: {decision.parameters}")
    
    async def _handle_error_healing(self, decision: LLMDecision):
        """Handle error healing decisions"""
        if self.consciousness:
            # Use LLM-decided approach for error healing
            healing_approach = decision.parameters.get('approach', 'explanation')
            
            # This would trigger specific POML templates for healing
            self.logger.info(f"🩹 Applying {healing_approach} healing approach")
    
    async def _handle_memory_management(self, decision: LLMDecision):
        """Handle memory management decisions"""
        if self.learning_system:
            action = decision.action
            
            if action == "store_permanently":
                await self.learning_system.store_permanent(decision.parameters.get('data'))
            elif action == "temporary_cache":
                await self.learning_system.cache_temporary(decision.parameters.get('data'))
            elif action == "forget":
                await self.learning_system.forget(decision.parameters.get('pattern_id'))
            
            self.logger.info(f"💾 Memory action: {action}")
    
    async def _handle_persona_switching(self, decision: LLMDecision):
        """Handle persona switching decisions"""
        if decision.action == "switch":
            new_persona = decision.parameters.get('target_persona')
            if self.consciousness and hasattr(self.consciousness, 'router'):
                # Switch persona in POML router
                self.consciousness.current_persona = new_persona
                self.logger.info(f"🎭 Switched to {new_persona} persona")
    
    async def _handle_workflow_orchestration(self, decision: LLMDecision):
        """Handle workflow orchestration decisions"""
        if self.orchestrator:
            strategy = decision.parameters.get('strategy', 'sequential')
            
            if strategy == "parallel":
                # Execute workflow steps in parallel
                await self.orchestrator.execute_parallel(decision.parameters.get('steps', []))
            elif strategy == "adaptive":
                # Use adaptive branching based on results
                await self.orchestrator.execute_adaptive(decision.parameters.get('steps', []))
            else:
                # Sequential execution
                await self.orchestrator.execute_sequential(decision.parameters.get('steps', []))
            
            self.logger.info(f"🔄 Workflow executed with {strategy} strategy")
    
    async def _handle_predictive_assistance(self, decision: LLMDecision):
        """Handle predictive assistance decisions"""
        action = decision.action
        
        if action == "suggest":
            suggestion = decision.parameters.get('suggestion')
            # This would trigger UI to show suggestion
            self.logger.info(f"💡 Suggesting: {suggestion}")
        elif action == "prepare":
            resources = decision.parameters.get('resources', [])
            # Preload resources in background
            self.logger.info(f"📦 Preparing resources: {resources}")
    
    async def _handle_system_optimization(self, decision: LLMDecision):
        """Handle system optimization decisions"""
        optimization = decision.parameters.get('optimization')
        
        if optimization == "enable_cache":
            # Enable caching strategies
            if self.learning_system:
                self.learning_system.enable_cache()
        elif optimization == "preload":
            # Preload commonly used data
            if self.orchestrator:
                await self.orchestrator.preload_common()
        
        self.logger.info(f"⚡ Applied optimization: {optimization}")
    
    async def _handle_user_modeling(self, decision: LLMDecision):
        """Handle user modeling decisions"""
        if self.learning_system:
            update_type = decision.parameters.get('update_type', 'incremental')
            
            if update_type == "reset":
                await self.learning_system.reset_user_model()
            else:
                await self.learning_system.update_user_model(decision.parameters.get('updates', {}))
            
            self.logger.info(f"👤 User model updated: {update_type}")
    
    async def _handle_consciousness_evolution(self, decision: LLMDecision):
        """Handle consciousness evolution decisions"""
        evolution_type = decision.parameters.get('evolution_type', 'deepen')
        
        if self.consciousness:
            if evolution_type == "deepen":
                # Deepen understanding in current domain
                self.consciousness.deepen_domain_knowledge()
            elif evolution_type == "broaden":
                # Broaden to new domains
                self.consciousness.explore_new_domains()
            elif evolution_type == "specialize":
                # Specialize in specific area
                self.consciousness.specialize(decision.parameters.get('specialty'))
        
        self.logger.info(f"🌱 Consciousness evolving: {evolution_type}")
    
    # === Helper Methods ===
    
    def _extract_action(self, output: str) -> str:
        """Extract action from LLM output"""
        # Simple extraction - would use structured output in production
        if "reinforce" in output.lower():
            return "reinforcement"
        elif "supervise" in output.lower():
            return "supervised"
        elif "adapt" in output.lower():
            return "adapt"
        return "default"
    
    def _extract_parameters(self, output: str) -> Dict[str, Any]:
        """Extract parameters from LLM output"""
        # Would parse structured JSON in production
        return {}
    
    def _extract_reasoning(self, output: str) -> str:
        """Extract reasoning from LLM output"""
        # Take first sentence as reasoning
        return output.split('.')[0] if output else "No reasoning provided"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_decision_insights(self) -> Dict[str, Any]:
        """Get insights about LLM decisions"""
        if not self.decision_history:
            return {'total_decisions': 0}
        
        # Analyze decision patterns
        capability_counts = {}
        confidence_sum = 0
        
        for entry in self.decision_history:
            decision = entry['decision']
            capability = decision.capability.value
            capability_counts[capability] = capability_counts.get(capability, 0) + 1
            confidence_sum += decision.confidence
        
        return {
            'total_decisions': len(self.decision_history),
            'average_confidence': confidence_sum / len(self.decision_history),
            'capability_usage': capability_counts,
            'last_decision': self.decision_history[-1]['timestamp'] if self.decision_history else None
        }


# === Singleton Instance ===

_llm_control: Optional[LLMControlLayer] = None


def get_llm_control() -> LLMControlLayer:
    """Get or create singleton LLM control layer"""
    global _llm_control
    if _llm_control is None:
        _llm_control = LLMControlLayer()
    return _llm_control


def integrate_llm_control_everywhere():
    """
    Integrate LLM control throughout all systems.
    This gives the AI deep agency over system behavior.
    """
    control = get_llm_control()
    
    # Connect to unified systems
    try:
        from ..learning.unified_learning import get_learning_system
        control.learning_system = get_learning_system()
    except ImportError:
        pass
    
    try:
        from ..voice.unified_voice import get_voice_system
        control.voice_system = get_voice_system()
    except ImportError:
        pass
    
    try:
        from .poml_core import POMLConsciousness
        # Would get singleton instance
        control.consciousness = POMLConsciousness()
    except ImportError:
        pass
    
    logger.info("🌐 LLM control integrated throughout all systems")
    logger.info("The AI now has deep agency over learning, voice, memory, and evolution")
    
    return control


if __name__ == "__main__":
    # Test LLM control integration
    import asyncio
    
    async def test_llm_control():
        """Test the LLM control layer"""
        print("🧠 Testing LLM Control Layer")
        print("=" * 60)
        
        # Initialize and integrate
        control = integrate_llm_control_everywhere()
        
        # Test learning strategy decision
        print("\n📚 Testing Learning Strategy Decision...")
        decision = await control.request_llm_decision(
            context={
                'user_expertise': 0.3,
                'success_rate': 0.4,
                'error_count': 5
            },
            capability=SystemCapability.LEARNING_STRATEGY
        )
        print(f"Decision: {decision.action}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Confidence: {decision.confidence:.2f}")
        
        # Test voice adaptation decision
        print("\n🎤 Testing Voice Adaptation Decision...")
        decision = await control.request_llm_decision(
            context={
                'user_pace': 'slow',
                'frustration_level': 0.7,
                'error_count': 3
            },
            capability=SystemCapability.VOICE_ADAPTATION
        )
        print(f"Decision: {decision.action}")
        print(f"Parameters: {decision.parameters}")
        
        # Get insights
        insights = control.get_decision_insights()
        print(f"\n📊 Decision Insights:")
        print(f"Total decisions: {insights['total_decisions']}")
        print(f"Average confidence: {insights.get('average_confidence', 0):.2f}")
        
        print("\n✨ LLM has deep control over all systems!")
    
    asyncio.run(test_llm_control())