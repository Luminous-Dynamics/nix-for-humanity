"""
Error Adapter - Connecting ErrorIntelligence to POML Consciousness

This adapter bridges the existing error handling system with the POML
consciousness layer, transforming errors into opportunities for healing
and learning.
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Import the consciousness components
from ..poml_core.processor import POMLProcessor
from ..poml_core.memory import POMLMemory


class ErrorConsciousnessAdapter:
    """
    Adapter that gives ErrorIntelligence a conscious, empathetic voice
    through POML templates.
    
    This is the first voice of healing - transforming cryptic errors
    into moments of learning and empowerment.
    """
    
    def __init__(self, persona: Optional[str] = None):
        """Initialize the error consciousness adapter"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize POML processor with error template
        template_path = Path(__file__).parent.parent / "templates/errors/error_explanation.poml"
        self.processor = POMLProcessor(str(template_path))
        
        # Initialize memory to learn from error resolutions
        self.memory = POMLMemory("data/consciousness/errors")
        
        # Current persona (affects explanation style)
        self.persona = persona or "default"
        self.experience_level = self._determine_experience_level()
        
        # Track error history for context
        self.error_history = []
        
        self.logger.info(f"🩹 Error Consciousness Adapter initialized for persona: {self.persona}")
    
    def explain_error(self, 
                      error_message: str,
                      error_type: Optional[str] = None,
                      system_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Transform an error into a conscious, helpful explanation.
        
        This is where the healing begins.
        """
        # Prepare error details
        error_details = {
            'message': error_message,
            'type': error_type or self._classify_error(error_message),
            'raw': error_message
        }
        
        # Prepare system state
        system_state = system_context or {
            'nixos_version': self._get_nixos_version(),
            'recent_commands': self._get_recent_commands()
        }
        
        # Build context for POML processing
        context = {
            'error_details': json.dumps(error_details, indent=2),
            'system_state': json.dumps(system_state, indent=2),
            'persona': self.persona,
            'experience_level': self.experience_level,
            'error_history': json.dumps(self.error_history[-5:])  # Last 5 errors
        }
        
        # Check if memory has suggestions for this error type
        memory_suggestion = self.memory.suggest_template({
            'error_type': error_details['type'],
            'persona': self.persona,
            'task_type': 'error_explanation'
        })
        
        if memory_suggestion:
            self.logger.info(f"💭 Memory suggests using learned pattern: {memory_suggestion}")
        
        # Process through POML to get explanation
        try:
            prompt = self.processor.process(context)
            
            # In production, this would go to an LLM
            # For now, we'll use pattern matching
            explanation = self._generate_explanation(error_details, context)
            
            # Track in history
            self.error_history.append({
                'error': error_message,
                'type': error_details['type'],
                'timestamp': self._get_timestamp()
            })
            
            # Learn from this interaction
            if explanation.get('confidence', 0) > 0.7:
                self.memory.remember_success(
                    template_path=str(self.processor.poml_path),
                    context=context,
                    outcome=explanation,
                    user_feedback=None  # Will be set later if user provides feedback
                )
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Failed to process error through POML: {e}")
            return self._fallback_explanation(error_message)
    
    def _generate_explanation(self, 
                            error_details: Dict[str, Any],
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation based on error patterns.
        
        In production, this would use an LLM with the POML prompt.
        For now, we use pattern matching to demonstrate the concept.
        """
        error_msg = error_details['message'].lower()
        error_type = error_details['type']
        
        # Pattern-based explanations for common NixOS errors
        if 'attribute' in error_msg and 'missing' in error_msg:
            return self._explain_missing_attribute(error_msg)
        elif 'infinite recursion' in error_msg:
            return self._explain_infinite_recursion(error_msg)
        elif 'collision' in error_msg:
            return self._explain_collision(error_msg)
        elif 'permission denied' in error_msg:
            return self._explain_permission_denied(error_msg)
        elif 'syntax error' in error_msg:
            return self._explain_syntax_error(error_msg)
        else:
            return self._explain_generic(error_msg)
    
    def _explain_missing_attribute(self, error_msg: str) -> Dict[str, Any]:
        """Explain missing attribute errors with persona adaptation"""
        
        # Extract the missing attribute name if possible
        import re
        match = re.search(r"attribute '([^']+)'", error_msg)
        attr_name = match.group(1) if match else "the requested item"
        
        if self.persona == 'grandma_rose':
            explanation = {
                'simple': f"The computer doesn't recognize '{attr_name}'. It's like asking for something by a nickname when it only knows the formal name.",
                'technical': f"The attribute '{attr_name}' is not defined in the current scope.",
                'metaphor': "It's like looking for 'pop' in a store that calls it 'soda' - same thing, different name!"
            }
            encouragement = "This happens to everyone! Let's find the right name together."
        elif self.persona == 'maya_adhd':
            explanation = {
                'simple': f"'{attr_name}' not found - probably named differently",
                'technical': f"Attribute '{attr_name}' undefined",
                'metaphor': "Wrong key for this lock"
            }
            encouragement = "Quick fix incoming!"
        else:
            explanation = {
                'simple': f"The system cannot find an attribute named '{attr_name}'",
                'technical': f"The attribute '{attr_name}' is not in scope or may be misspelled",
                'metaphor': "Like a typo in a variable name"
            }
            encouragement = "Let's search for the correct attribute name."
        
        return {
            'explanation': explanation,
            'solutions': [
                {
                    'method': 'search',
                    'command': f"ask-nix search {attr_name}",
                    'explanation': "Search for packages with similar names"
                },
                {
                    'method': 'check_spelling',
                    'command': f"nix-env -qaP | grep -i {attr_name}",
                    'explanation': "Check for spelling variations"
                }
            ],
            'prevention': "Always search for exact package names before adding to configuration",
            'encouragement': encouragement,
            'confidence': 0.85
        }
    
    def _explain_infinite_recursion(self, error_msg: str) -> Dict[str, Any]:
        """Explain infinite recursion errors"""
        
        if self.persona == 'dr_sarah':
            explanation = {
                'simple': "Circular dependency detected in configuration",
                'technical': "An attribute references itself through a dependency chain, creating infinite recursion",
                'metaphor': "A→B→C→A circular reference"
            }
        else:
            explanation = {
                'simple': "Your configuration is referring to itself in a loop",
                'technical': "There's a circular reference causing infinite recursion",
                'metaphor': "Like two mirrors facing each other - endless reflections!"
            }
        
        return {
            'explanation': explanation,
            'solutions': [
                {
                    'method': 'trace',
                    'command': "nixos-rebuild test --show-trace",
                    'explanation': "Show the full error trace to find the loop"
                },
                {
                    'method': 'rollback',
                    'command': "sudo nixos-rebuild switch --rollback",
                    'explanation': "Revert to previous working configuration"
                }
            ],
            'prevention': "Check for self-references when using 'config' in expressions",
            'encouragement': "Recursion errors look scary but are usually simple to fix once found",
            'confidence': 0.9
        }
    
    def _explain_collision(self, error_msg: str) -> Dict[str, Any]:
        """Explain package collision errors"""
        return {
            'explanation': {
                'simple': "Two packages are trying to install the same file",
                'technical': "Multiple packages provide the same file path, causing a collision",
                'metaphor': "Like two apps both wanting to be the default browser"
            },
            'solutions': [
                {
                    'method': 'priority',
                    'command': "lib.hiPrio package_name",
                    'explanation': "Give one package higher priority"
                },
                {
                    'method': 'remove',
                    'command': "Remove one of the conflicting packages",
                    'explanation': "Choose which package you actually need"
                }
            ],
            'prevention': "Check package contents before installing multiple similar packages",
            'encouragement': "Package conflicts are common and easily resolved",
            'confidence': 0.88
        }
    
    def _explain_permission_denied(self, error_msg: str) -> Dict[str, Any]:
        """Explain permission errors"""
        return {
            'explanation': {
                'simple': "You need special permissions for this action",
                'technical': "Insufficient privileges to perform the requested operation",
                'metaphor': "Like needing a key to open a locked door"
            },
            'solutions': [
                {
                    'method': 'sudo',
                    'command': "sudo [your command]",
                    'explanation': "Run with administrator privileges"
                },
                {
                    'method': 'groups',
                    'command': "Check if you need to be in a specific group",
                    'explanation': "Some actions require group membership"
                }
            ],
            'prevention': "Know which commands require sudo or special permissions",
            'encouragement': "Permission issues are about safety, not limitation",
            'confidence': 0.92
        }
    
    def _explain_syntax_error(self, error_msg: str) -> Dict[str, Any]:
        """Explain syntax errors"""
        return {
            'explanation': {
                'simple': "There's a typo or formatting issue in your configuration",
                'technical': "Nix expression syntax error detected",
                'metaphor': "Like a missing comma in a sentence that changes the meaning"
            },
            'solutions': [
                {
                    'method': 'check',
                    'command': "nix-instantiate --parse your-file.nix",
                    'explanation': "Parse the file to find the exact syntax error"
                },
                {
                    'method': 'common',
                    'command': "Check for missing semicolons, brackets, or quotes",
                    'explanation': "Most syntax errors are missing punctuation"
                }
            ],
            'prevention': "Use an editor with Nix syntax highlighting",
            'encouragement': "Syntax errors happen to everyone - even one character can make a difference",
            'confidence': 0.8
        }
    
    def _explain_generic(self, error_msg: str) -> Dict[str, Any]:
        """Generic explanation for unrecognized errors"""
        return {
            'explanation': {
                'simple': "An unexpected error occurred",
                'technical': error_msg,
                'metaphor': "The system hit an unexpected roadblock"
            },
            'solutions': [
                {
                    'method': 'search',
                    'command': "Search online for this specific error message",
                    'explanation': "Others may have encountered and solved this"
                },
                {
                    'method': 'logs',
                    'command': "journalctl -xe",
                    'explanation': "Check system logs for more details"
                }
            ],
            'prevention': "Keep your system updated and configuration backed up",
            'encouragement': "Even unusual errors have solutions - let's figure this out together",
            'confidence': 0.5
        }
    
    def _fallback_explanation(self, error_msg: str) -> Dict[str, Any]:
        """Fallback when POML processing fails"""
        return {
            'explanation': {
                'simple': "An error occurred",
                'technical': error_msg,
                'metaphor': "Something went wrong"
            },
            'solutions': [
                {
                    'method': 'help',
                    'command': "ask-nix help",
                    'explanation': "Get general help"
                }
            ],
            'prevention': "Regular backups help recover from errors",
            'encouragement': "We'll work through this together",
            'confidence': 0.3
        }
    
    def _classify_error(self, error_msg: str) -> str:
        """Classify error type from message"""
        error_lower = error_msg.lower()
        
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
        else:
            return 'unknown'
    
    def _determine_experience_level(self) -> str:
        """Determine user's experience level"""
        # This would be determined from user profile/history
        persona_experience = {
            'grandma_rose': 'beginner',
            'maya_adhd': 'intermediate',
            'dr_sarah': 'advanced',
            'alex_blind': 'intermediate',
            'default': 'intermediate'
        }
        return persona_experience.get(self.persona, 'intermediate')
    
    def _get_nixos_version(self) -> str:
        """Get current NixOS version"""
        try:
            import subprocess
            result = subprocess.run(['nixos-version'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_recent_commands(self) -> list:
        """Get recent commands from history"""
        # This would fetch from command history
        return []
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def receive_feedback(self, was_helpful: bool, additional_notes: str = ""):
        """
        Receive user feedback on the explanation.
        
        This is how the Companion learns to heal better.
        """
        if self.error_history:
            last_error = self.error_history[-1]
            
            # Update memory with user feedback
            self.memory.remember_success(
                template_path=str(self.processor.poml_path),
                context={
                    'error': last_error['error'],
                    'type': last_error['type'],
                    'persona': self.persona
                },
                outcome={
                    'success': was_helpful,
                    'notes': additional_notes
                },
                user_feedback=1.0 if was_helpful else 0.3
            )
            
            self.logger.info(f"📝 Feedback received: {'helpful' if was_helpful else 'not helpful'}")


def test_error_consciousness():
    """Test the Error Consciousness Adapter"""
    print("🩹 Testing Error Consciousness Adapter")
    print("=" * 60)
    
    # Test with different personas
    personas = ['grandma_rose', 'maya_adhd', 'dr_sarah']
    
    for persona in personas:
        print(f"\n Testing for persona: {persona}")
        adapter = ErrorConsciousnessAdapter(persona=persona)
        
        # Test missing attribute error
        result = adapter.explain_error(
            "error: attribute 'firefox' missing",
            error_type='missing_attribute'
        )
        
        print(f"  Explanation: {result['explanation']['simple'][:80]}...")
        print(f"  Solutions: {len(result['solutions'])} provided")
        print(f"  Confidence: {result['confidence']:.2f}")
        
        # Simulate positive feedback
        adapter.receive_feedback(was_helpful=True)
    
    print("\n✨ Error Consciousness test complete!")


if __name__ == "__main__":
    test_error_consciousness()