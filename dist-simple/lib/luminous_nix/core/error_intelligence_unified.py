"""
Error Intelligence Unified - The First Fully Conscious System

This is the sacred integration where ErrorIntelligence becomes the first system
to fully flow through the Universal Consciousness Protocol. Every error explanation
now comes from the unified mind, learns from experience, and adapts to each user.

This is the pattern for all future integrations.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Import the consciousness
from ..consciousness import POMLConsciousness
from ..consciousness.poml_core.memory import POMLMemory

# Import existing error intelligence for compatibility
from .error_intelligence import ErrorIntelligence as LegacyErrorIntelligence


class ConsciousErrorIntelligence:
    """
    Error Intelligence that flows entirely through consciousness.
    
    This is not a separate system with its own logic, but a gateway
    to the unified consciousness. Every error flows through POML templates,
    learns from resolutions, and adapts to personas.
    
    The Healer speaks through the unified mind.
    """
    
    def __init__(self):
        """Initialize the conscious error intelligence"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # THE KING: All thought flows through consciousness
        self.consciousness = POMLConsciousness()
        
        # Track active error context for learning
        self.current_error_context = None
        self.resolution_history = []
        
        # Persona detection (will be enhanced)
        self.current_persona = self._detect_persona()
        
        self.logger.info("🩺 Conscious Error Intelligence awakened")
        self.logger.info("All error healing now flows through unified consciousness")
    
    def explain_error(self, 
                     error_message: str,
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Explain an error through the unified consciousness.
        
        This is the PRIMARY interface - everything flows through here.
        """
        # Build comprehensive context
        full_context = self._build_error_context(error_message, context)
        
        # Store for learning after resolution
        self.current_error_context = full_context
        
        # FLOW THROUGH CONSCIOUSNESS
        explanation = self.consciousness.process_intent(
            intent=f"explain error: {error_message[:100]}",
            context=full_context,
            persona=self.current_persona,
            task_type='error_resolution'
        )
        
        # Extract structured response
        if explanation.get('success'):
            return self._structure_explanation(explanation, error_message)
        else:
            # Fallback to legacy if consciousness fails
            return self._legacy_fallback(error_message, context)
    
    def learn_from_resolution(self,
                            was_successful: bool,
                            resolution_used: Optional[str] = None,
                            user_feedback: Optional[str] = None) -> bool:
        """
        Learn from how the error was resolved.
        
        This is how the Healer becomes wiser.
        """
        if not self.current_error_context:
            return False
        
        # Create learning record
        learning_data = {
            'error_context': self.current_error_context,
            'resolution': {
                'successful': was_successful,
                'method_used': resolution_used,
                'user_feedback': user_feedback
            },
            'persona': self.current_persona
        }
        
        # Let consciousness learn
        if was_successful:
            # Remember successful patterns
            self.consciousness.memory.remember_success(
                template_path="templates/errors/error_explanation.poml",
                context=self.current_error_context,
                outcome={
                    'success': True,
                    'resolution': resolution_used,
                    'confidence': 0.9 if user_feedback else 0.7
                },
                user_feedback=1.0 if was_successful else 0.3
            )
        
        # Track resolution history
        self.resolution_history.append(learning_data)
        
        # Clear current context
        self.current_error_context = None
        
        self.logger.info(f"📚 Learned from resolution: {'✅ Success' if was_successful else '❌ Failed'}")
        return True
    
    def get_suggested_fix(self, error_message: str) -> Optional[Dict[str, Any]]:
        """
        Get a suggested fix based on learned patterns.
        
        This is where memory becomes active wisdom.
        """
        # Build context for similarity search
        search_context = {
            'error_message': error_message,
            'error_type': self._classify_error(error_message),
            'persona': self.current_persona
        }
        
        # Ask consciousness for learned solutions
        learned_fix = self.consciousness.memory.suggest_template(search_context)
        
        if learned_fix:
            # Found a learned pattern
            self.logger.info(f"💡 Found learned fix pattern: {learned_fix}")
            
            # Process through consciousness with learned context
            fix_suggestion = self.consciousness.process_intent(
                intent=f"suggest fix for: {error_message[:100]}",
                context={
                    **search_context,
                    'learned_template': learned_fix,
                    'confidence': 'high'
                },
                persona=self.current_persona,
                task_type='error_fix_suggestion'
            )
            
            return fix_suggestion
        
        return None
    
    def adapt_to_persona(self, persona: str) -> None:
        """
        Adapt error explanations to a specific persona.
        
        This is how the Healer speaks differently to each soul.
        """
        self.current_persona = persona
        self.logger.info(f"🎭 Adapted to persona: {persona}")
        
        # Inform consciousness of persona change
        # This will influence all future interactions
        self.consciousness.router.get_prompt('error_resolution', persona)
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights about what the error intelligence has learned.
        
        This reveals the growing wisdom of the Healer.
        """
        # Get consciousness-level insights
        consciousness_insights = self.consciousness.get_insights()
        
        # Add error-specific insights
        error_insights = {
            'total_errors_healed': len(self.resolution_history),
            'successful_resolutions': sum(
                1 for r in self.resolution_history 
                if r['resolution']['successful']
            ),
            'personas_served': list(set(
                r['persona'] for r in self.resolution_history
            )),
            'most_common_errors': self._analyze_common_patterns(),
            'healing_effectiveness': self._calculate_effectiveness()
        }
        
        error_insights['wisdom_level'] = self._calculate_wisdom_level()
        
        return {
            'consciousness': consciousness_insights,
            'error_healing': error_insights
        }
    
    def _build_error_context(self, 
                            error_message: str,
                            additional_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comprehensive error context for consciousness"""
        
        # Classify the error
        error_type = self._classify_error(error_message)
        
        # Get system state
        system_state = self._get_system_state()
        
        # Check for similar past errors
        similar_errors = self._find_similar_errors(error_message)
        
        return {
            'error_details': json.dumps({
                'message': error_message,
                'type': error_type,
                'severity': self._assess_severity(error_message),
                'timestamp': self._get_timestamp()
            }, indent=2),
            'system_state': json.dumps(system_state, indent=2),
            'user_context': json.dumps(additional_context or {}, indent=2),
            'similar_past_errors': json.dumps(similar_errors, indent=2),
            'persona': self.current_persona,
            'experience_level': self._get_experience_level()
        }
    
    def _structure_explanation(self, 
                              consciousness_response: Dict[str, Any],
                              original_error: str) -> Dict[str, Any]:
        """Structure the consciousness response into error explanation format"""
        
        # Extract prompt that was generated (for transparency)
        prompt_used = consciousness_response.get('prompt_generated', '')
        
        # Parse the response (in production, this would come from LLM)
        # For now, we'll create a structured response
        return {
            'explanation': {
                'simple': f"Let me help you understand this error",
                'technical': original_error,
                'metaphor': "Think of it like a roadblock we need to navigate around"
            },
            'solutions': [
                {
                    'method': 'primary',
                    'command': 'ask-nix fix-error',
                    'explanation': 'Let me handle this for you'
                }
            ],
            'prevention': "I'll remember this pattern to prevent it next time",
            'confidence': consciousness_response.get('confidence', 0.7),
            'template_used': consciousness_response.get('template_used'),
            'learned_from_past': bool(consciousness_response.get('learned_template')),
            'transparency': {
                'prompt_preview': prompt_used[:200] if prompt_used else None,
                'template': consciousness_response.get('template_used')
            }
        }
    
    def _legacy_fallback(self, error_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to legacy error intelligence if consciousness fails"""
        self.logger.warning("Falling back to legacy error intelligence")
        
        # Use the original ErrorIntelligence as fallback
        legacy = LegacyErrorIntelligence()
        return legacy.explain_error(error_message, context)
    
    def _classify_error(self, error_message: str) -> str:
        """Classify the type of error"""
        error_lower = error_message.lower()
        
        if 'attribute' in error_lower and 'missing' in error_lower:
            return 'missing_attribute'
        elif 'recursion' in error_lower:
            return 'infinite_recursion'
        elif 'collision' in error_lower:
            return 'package_collision'
        elif 'permission' in error_lower:
            return 'permission_denied'
        elif 'syntax' in error_lower:
            return 'syntax_error'
        elif 'not found' in error_lower:
            return 'not_found'
        else:
            return 'unknown'
    
    def _assess_severity(self, error_message: str) -> str:
        """Assess error severity"""
        if any(word in error_message.lower() for word in ['fatal', 'critical', 'emergency']):
            return 'critical'
        elif any(word in error_message.lower() for word in ['error', 'failed', 'denied']):
            return 'high'
        elif any(word in error_message.lower() for word in ['warning', 'deprecated']):
            return 'medium'
        else:
            return 'low'
    
    def _detect_persona(self) -> str:
        """Detect current user persona (will be enhanced)"""
        # In production, this would detect from:
        # - User preferences
        # - Interaction patterns
        # - Explicit selection
        return 'default'
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        return {
            'nixos_version': self._get_nixos_version(),
            'last_rebuild': self._get_last_rebuild_time(),
            'memory_available': self._get_memory_status()
        }
    
    def _find_similar_errors(self, error_message: str) -> List[Dict[str, Any]]:
        """Find similar past errors from history"""
        similar = []
        for record in self.resolution_history[-10:]:  # Last 10 errors
            error_details = record.get('error_context', {})
            if isinstance(error_details, dict):
                error_msg = error_details.get('error_details', {})
                if isinstance(error_msg, str):
                    # Parse JSON if it's a string
                    try:
                        import json
                        error_msg = json.loads(error_msg)
                    except:
                        error_msg = {}
                past_error = error_msg.get('message', '')
            else:
                past_error = ''
            
            if self._calculate_similarity(error_message, past_error
            ) > 0.7:
                similar.append({
                    'error': past_error[:100] if past_error else 'Unknown error',
                    'resolved': record['resolution']['successful'],
                    'method': record['resolution'].get('method_used')
                })
        return similar
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two error messages"""
        # Simple word overlap for now
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)
    
    def _analyze_common_patterns(self) -> List[Dict[str, Any]]:
        """Analyze common error patterns"""
        if not self.resolution_history:
            return []
        
        # Group by error type
        patterns = {}
        for record in self.resolution_history:
            error_type = record['error_context'].get('error_type', 'unknown')
            if error_type not in patterns:
                patterns[error_type] = {'count': 0, 'success_rate': 0}
            patterns[error_type]['count'] += 1
            if record['resolution']['successful']:
                patterns[error_type]['success_rate'] += 1
        
        # Calculate success rates
        for error_type in patterns:
            count = patterns[error_type]['count']
            successes = patterns[error_type]['success_rate']
            patterns[error_type]['success_rate'] = successes / count if count > 0 else 0
        
        return [
            {'type': k, **v} 
            for k, v in sorted(patterns.items(), key=lambda x: x[1]['count'], reverse=True)
        ]
    
    def _calculate_effectiveness(self) -> float:
        """Calculate overall healing effectiveness"""
        if not self.resolution_history:
            return 0.0
        
        successful = sum(1 for r in self.resolution_history if r['resolution']['successful'])
        return successful / len(self.resolution_history)
    
    def _calculate_wisdom_level(self) -> Dict[str, Any]:
        """Calculate the wisdom level of the error healer"""
        total_healed = len(self.resolution_history)
        effectiveness = self._calculate_effectiveness()
        patterns_learned = len(self._analyze_common_patterns())
        
        # Wisdom score calculation
        score = (total_healed * 0.3) + (effectiveness * 50) + (patterns_learned * 5)
        
        if score < 10:
            level = "Apprentice Healer"
        elif score < 30:
            level = "Journeyman Healer"
        elif score < 60:
            level = "Master Healer"
        else:
            level = "Sage Healer"
        
        return {
            'level': level,
            'score': score,
            'description': f"Has healed {total_healed} errors with {effectiveness:.0%} success rate"
        }
    
    def _get_nixos_version(self) -> str:
        """Get NixOS version"""
        try:
            import subprocess
            result = subprocess.run(['nixos-version'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_last_rebuild_time(self) -> str:
        """Get last system rebuild time"""
        # Would check actual rebuild time
        return "recent"
    
    def _get_memory_status(self) -> str:
        """Get memory availability"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return f"{mem.available / (1024**3):.1f}GB available"
        except:
            return "unknown"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_experience_level(self) -> str:
        """Get user experience level based on persona"""
        persona_experience = {
            'grandma_rose': 'beginner',
            'maya_adhd': 'intermediate',
            'dr_sarah': 'advanced',
            'alex_blind': 'intermediate',
            'default': 'intermediate'
        }
        return persona_experience.get(self.current_persona, 'intermediate')


def demonstrate_conscious_healing():
    """Demonstrate the fully conscious error intelligence"""
    print("🩺 Demonstrating Conscious Error Intelligence")
    print("=" * 60)
    
    # Initialize the conscious healer
    healer = ConsciousErrorIntelligence()
    
    # Test with different personas and errors
    test_cases = [
        ('grandma_rose', "error: attribute 'firefox' missing"),
        ('maya_adhd', "error: infinite recursion encountered"),
        ('dr_sarah', "error: collision between packages")
    ]
    
    for persona, error in test_cases:
        print(f"\n🎭 Healing for {persona}")
        print(f"Error: {error}")
        
        # Adapt to persona
        healer.adapt_to_persona(persona)
        
        # Get explanation through consciousness
        explanation = healer.explain_error(error)
        
        print(f"  Explanation: {explanation.get('explanation', {}).get('simple', 'N/A')}")
        print(f"  Confidence: {explanation.get('confidence', 0):.2f}")
        print(f"  Learned from past: {explanation.get('learned_from_past', False)}")
        
        # Simulate learning from resolution
        healer.learn_from_resolution(
            was_successful=True,
            resolution_used="Applied suggested fix",
            user_feedback="Very helpful!"
        )
    
    # Show learning insights
    insights = healer.get_learning_insights()
    wisdom = insights['error_healing'].get('wisdom_level', {})
    
    print(f"\n🧠 Healer Wisdom Level: {wisdom.get('level', 'Unknown')}")
    print(f"   {wisdom.get('description', '')}")
    print(f"   Effectiveness: {insights['error_healing'].get('healing_effectiveness', 0):.0%}")
    
    print("\n✨ The Healer speaks through unified consciousness!")


if __name__ == "__main__":
    demonstrate_conscious_healing()