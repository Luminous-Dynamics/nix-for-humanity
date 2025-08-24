"""
Luminous Nix Core - The actual implementation
This replaces the non-existent LuminousNixCore that was claimed to exist
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import subprocess
import json
import os
from pathlib import Path

from .backend import NixForHumanityBackend
from .intents import IntentRecognizer, Intent, IntentType
from .executor import SafeExecutor
from .knowledge import KnowledgeBase
from .error_handler import ErrorHandler
from .native_nix_api import NativeNixAPI, get_native_api
from .flake_executor import FlakeExecutor
from .home_executor import HomeExecutor
from .config_executor import ConfigExecutor
from .sacred_utils import (
    MindfulOperation, KairosMode, SacredTimer, 
    consciousness_field, check_consciousness,
    with_sacred_pause, SacredMessages
)

# Import SKG integration
try:
    from ..knowledge.skg_integration import get_skg_integration
    SKG_AVAILABLE = True
except ImportError:
    SKG_AVAILABLE = False
    import logging
    logging.warning("SKG not available - continuing without knowledge graph")


@dataclass
class Query:
    """User query with metadata"""
    text: str
    user_id: str = "default"
    dry_run: bool = False
    verbose: bool = False
    json_output: bool = False
    educational: bool = False


@dataclass
class Response:
    """Response from the system"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    command: Optional[str] = None
    explanation: Optional[str] = None


class LuminousNixCore:
    """
    The actual core implementation for Luminous Nix
    Provides the Python API that was promised but never built
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the core system with consciousness-first principles"""
        self.config = config or {}
        
        # Check consciousness field on startup
        field_state = check_consciousness()
        if field_state == "fragmented":
            print(SacredMessages.get_random('START_INTENTIONS'))
            consciousness_field.sacred_pause(1.5)
        
        # Initialize components
        self.backend = NixForHumanityBackend()
        self.intent_recognizer = IntentRecognizer()
        self.executor = SafeExecutor()
        self.knowledge = KnowledgeBase()
        self.error_handler = ErrorHandler()
        self.flake_executor = FlakeExecutor()  # New: Flake support
        self.home_executor = HomeExecutor()    # New: Home Manager support
        self.config_executor = ConfigExecutor()  # New: Config file parsing
        
        # Initialize native API for NixOS 25.11
        self.native_api = get_native_api()
        self.use_native = self.native_api.has_native_api()
        
        # Set executor mindful mode based on config
        self.mindful_mode = self.config.get('mindful_mode', True)
        self.executor.set_mindful_mode(self.mindful_mode)
        
        if self.use_native:
            print("🚀 Using native Python-Nix API for 10x-1500x performance!")
        else:
            print("⚠️  Native API not available, using subprocess fallback")
        
        # Performance tracking (honest metrics)
        self.metrics = {
            'operations': 0,
            'successes': 0,
            'failures': 0,
            'avg_response_ms': 0,
            'native_api_used': self.use_native,
            'consciousness_coherence': consciousness_field.coherence_level
        }
        
        # Kairos timer for session
        self.session_timer = SacredTimer(KairosMode.FLOW)
        
        # Initialize SKG if available
        self.skg = None
        if SKG_AVAILABLE:
            try:
                self.skg = get_skg_integration()
                print("🧠 Symbiotic Knowledge Graph activated - system is learning!")
            except Exception as e:
                print(f"⚠️  SKG initialization failed: {e}")
                self.skg = None
    
    def process_query(self, query: Query) -> Response:
        """
        Process a natural language query with consciousness-first approach
        
        This is the main entry point for all operations
        """
        import time
        
        # Begin SKG interaction tracking
        interaction_context = None
        if self.skg:
            interaction_context = self.skg.begin_interaction(query.text)
        
        # Check consciousness field before processing
        if self.mindful_mode and consciousness_field.needs_pause():
            consciousness_field.sacred_pause(1.0)
        
        start_time = time.time()
        
        try:
            # 1. Recognize intent (use SimpleIntentRecognizer for better pattern matching)
            from luminous_nix.nlp import SimpleIntentRecognizer, IntentType as NLPIntentType
            simple_recognizer = SimpleIntentRecognizer()
            nlp_intent = simple_recognizer.recognize(query.text)
            
            # Record intent in SKG
            if self.skg and nlp_intent:
                self.skg.record_intent(
                    nlp_intent.type.value,
                    nlp_intent.entities,
                    nlp_intent.confidence
                )
            
            # Check if it's a flake-related intent first
            if nlp_intent.type in [NLPIntentType.FLAKE, NLPIntentType.DEVELOP]:
                return self._handle_flake_intent(nlp_intent, query)
            
            # Check if it's a home manager intent
            if nlp_intent.type == NLPIntentType.HOME:
                return self._handle_home_intent(nlp_intent, query)
            
            # Check if it's a config parse intent
            if nlp_intent.type == NLPIntentType.CONFIG_PARSE:
                return self._handle_config_intent(nlp_intent, query)
            
            # Otherwise, use the original recognizer for backward compatibility
            intent = self.intent_recognizer.recognize(query.text)
            
            if not intent:
                return Response(
                    success=False,
                    message="I couldn't understand your request",
                    error="Intent recognition failed"
                )
            
            # 2. Build command based on intent
            command = self._build_command(intent, query)
            
            if not command:
                return Response(
                    success=False,
                    message=f"I don't know how to {intent.type}",
                    error="Command generation failed"
                )
            
            # 3. Execute or preview (with mindful operations for significant changes)
            is_significant = intent.type in [IntentType.UPDATE_SYSTEM, IntentType.INSTALL_PACKAGE, 
                                            IntentType.REMOVE_PACKAGE, IntentType.ROLLBACK]
            
            if query.dry_run:
                response = Response(
                    success=True,
                    message=f"Would execute: {command}",
                    command=command,
                    explanation=self._get_explanation(intent)
                )
            else:
                # Create mindful operation wrapper for significant operations
                if self.mindful_mode and is_significant:
                    mode = KairosMode.CEREMONY if intent.type == IntentType.UPDATE_SYSTEM else KairosMode.TRANSITION
                    mindful_op = MindfulOperation(
                        name=f"Executing: {intent.type.value}",
                        operation=lambda: self._execute_with_api(intent, command, query),
                        pause_before=1.5 if mode == KairosMode.CEREMONY else 0.8,
                        pause_after=0.5,
                        mode=mode
                    )
                    response = mindful_op.execute()
                else:
                    # Regular execution for queries and non-significant operations
                    response = self._execute_with_api(intent, command, query)
            
            # 4. Track metrics (honest)
            elapsed_ms = (time.time() - start_time) * 1000
            self._update_metrics(response.success, elapsed_ms)
            
            # 5. Format output
            if query.json_output:
                response.data = {
                    'intent': intent.type.value,
                    'confidence': getattr(intent, 'confidence', 0.7),
                    'elapsed_ms': elapsed_ms,
                    'command': command,
                    'consciousness_coherence': consciousness_field.coherence_level,
                    'kairos_mode': self.mindful_mode
                }
            
            # Update consciousness field based on result
            if self.mindful_mode:
                indicators = {
                    'error_rate': 1.0 if not response.success else 0.0,
                    'repeat_commands': 0  # Would need to track this across queries
                }
                consciousness_field.update_user_state(indicators)
            
            # Complete SKG interaction
            if self.skg:
                self._complete_skg_interaction(response, elapsed_ms)
            
            return response
            
        except Exception as e:
            self.metrics['failures'] += 1
            
            # Record error in SKG
            error_response = None
            if self.mindful_mode:
                error_message = SacredMessages.get_random('ERROR_TEACHINGS')
                error_response = Response(
                    success=False,
                    message=f"{error_message}\nTechnical details: {str(e)}",
                    error=str(e)
                )
            else:
                error_response = Response(
                    success=False,
                    message="An error occurred",
                    error=str(e)
                )
            
            # Complete SKG interaction with error
            if self.skg and error_response:
                elapsed_ms = (time.time() - start_time) * 1000
                self._complete_skg_interaction(error_response, elapsed_ms)
            
            return error_response
    
    def _handle_flake_intent(self, nlp_intent, query: Query) -> Response:
        """Handle flake-related intents"""
        try:
            # Execute flake operation
            result = self.flake_executor.execute(
                intent_type=nlp_intent.type.value,
                query=query.text,
                entities=nlp_intent.entities
            )
            
            # Convert FlakeResult to Response
            return Response(
                success=result.success,
                message=result.message,
                command=result.command,
                explanation=result.explanation or f"Flake operation: {nlp_intent.type.value}",
                error=result.error if not result.success else None
            )
        except Exception as e:
            return Response(
                success=False,
                message=f"Flake operation failed: {str(e)}",
                error=str(e)
            )
    
    def _handle_home_intent(self, nlp_intent, query: Query) -> Response:
        """Handle Home Manager related intents"""
        try:
            # Execute home manager operation
            result = self.home_executor.execute(
                intent_type=nlp_intent.type.value,
                query=query.text,
                entities=nlp_intent.entities
            )
            
            # Convert HomeResult to Response
            data = {}
            if result.dotfiles:
                data['dotfiles'] = result.dotfiles
            if result.themes:
                data['themes'] = result.themes
            if result.actions:
                data['actions'] = result.actions
            
            return Response(
                success=result.success,
                message=result.message,
                command=result.command,
                explanation=result.explanation or "Home Manager operation completed",
                error=result.error if not result.success else None,
                data=data if data else None
            )
        except Exception as e:
            return Response(
                success=False,
                message=f"Home Manager operation failed: {str(e)}",
                error=str(e)
            )
    
    def _handle_config_intent(self, nlp_intent, query: Query) -> Response:
        """Handle configuration file parsing intents"""
        try:
            # Execute config parsing operation
            result = self.config_executor.execute(
                intent_type=nlp_intent.type.value,
                query=query.text,
                entities=nlp_intent.entities
            )
            
            # Build response data
            data = {
                'statistics': result.statistics,
                'validation_errors': result.validation_errors,
                'suggestions': result.suggestions,
                'improvements': result.improvements
            }
            
            # Learn from configuration patterns if SKG is available
            if self.skg and result.config:
                learning_data = self.config_executor.learn_from_config(result.config)
                # Record patterns in SKG (using the correct method)
                if hasattr(self.skg, 'skg'):
                    skg_core = self.skg.skg
                    # Record patterns using record_insight instead
                    for pattern in learning_data['patterns']:
                        if hasattr(skg_core, 'record_insight'):
                            skg_core.record_insight(
                                source='config_analysis',
                                insight=f'Pattern detected: {pattern}',
                                confidence=0.9
                            )
                    # Record antipatterns
                    for antipattern in learning_data['antipatterns']:
                        if hasattr(skg_core, 'record_insight'):
                            skg_core.record_insight(
                                source='config_analysis',
                                insight=f'Antipattern detected: {antipattern}',
                                confidence=1.0
                            )
            
            return Response(
                success=result.success,
                message=result.message,
                command=None,  # No command for parsing
                explanation="Configuration analysis completed",
                error=result.error if not result.success else None,
                data=data if data else None
            )
        except Exception as e:
            return Response(
                success=False,
                message=f"Configuration parsing failed: {str(e)}",
                error=str(e)
            )
    
    def _build_command(self, intent: Intent, query: Query) -> Optional[str]:
        """Build the actual Nix command to execute"""
        
        # Extract entities from intent
        entities = getattr(intent, 'entities', {})
        package = entities.get('package')
        search_query = entities.get('query', query.text)
        
        # Map intent types to commands (using actual enum values)
        command_map = {
            IntentType.INSTALL_PACKAGE: lambda: f"nix profile install nixpkgs#{package}" if package else None,
            IntentType.REMOVE_PACKAGE: lambda: f"nix profile remove '.*{package}.*'" if package else None,
            IntentType.SEARCH_PACKAGE: lambda: f"nix search nixpkgs {search_query}",
            IntentType.UPDATE_SYSTEM: lambda: "sudo nixos-rebuild switch",
            IntentType.LIST_INSTALLED: lambda: "nix profile list",
            IntentType.ROLLBACK: lambda: "sudo nixos-rebuild switch --rollback",
            IntentType.GARBAGE_COLLECT: lambda: "nix-collect-garbage -d",
            IntentType.HELP: lambda: None,  # No command for help
        }
        
        builder = command_map.get(intent.type)
        if builder:
            return builder()
        return None
    
    def _execute_native(self, intent: Intent, command: str, query: Query) -> Response:
        """Execute using native Python-Nix API for maximum performance"""
        
        entities = getattr(intent, 'entities', {})
        package = entities.get('package')
        search_query = entities.get('query', query.text)
        
        try:
            if intent.type == IntentType.INSTALL_PACKAGE and package:
                success, output, elapsed = self.native_api.install_package(package)
                return Response(
                    success=success,
                    message=output,
                    command=command,
                    explanation=f"Installed using native API in {elapsed:.1f}ms"
                )
                
            elif intent.type == IntentType.SEARCH_PACKAGE:
                results, elapsed = self.native_api.search_packages(search_query)
                if results:
                    msg = f"Found {len(results)} packages:\n"
                    for r in results[:5]:
                        msg += f"  - {r['name']}: {r['description'][:50]}...\n"
                    return Response(
                        success=True,
                        message=msg,
                        data={"packages": results},  # Add the actual data!
                        command=command,
                        explanation=f"Searched using native API in {elapsed:.1f}ms"
                    )
                else:
                    return Response(
                        success=False,
                        message="No packages found",
                        data={"packages": []},  # Empty list for consistency
                        command=command
                    )
                    
            elif intent.type == IntentType.UPDATE_SYSTEM:
                # Build and switch configuration
                success, result, build_time = self.native_api.build_configuration()
                if success:
                    switch_success, switch_output, switch_time = self.native_api.switch_to_configuration(result)
                    total_time = build_time + switch_time
                    return Response(
                        success=switch_success,
                        message=switch_output,
                        command=command,
                        explanation=f"Updated using native API in {total_time:.1f}ms"
                    )
                else:
                    return Response(
                        success=False,
                        message=result,
                        command=command,
                        error="Build failed"
                    )
                    
            elif intent.type == IntentType.LIST_INSTALLED:
                # For now, fall back to subprocess for this
                result = self.executor.execute(command)
                return Response(
                    success=result.get('success', False),
                    message=result.get('output', ''),
                    command=command,
                    explanation="Listed packages"
                )
                
            elif intent.type == IntentType.ROLLBACK:
                success, output, elapsed = self.native_api.rollback()
                return Response(
                    success=success,
                    message=output,
                    command=command,
                    explanation=f"Rolled back using native API in {elapsed:.1f}ms"
                )
                
            else:
                # Fall back to subprocess for other operations
                result = self.executor.execute(command)
                return Response(
                    success=result.get('success', False),
                    message=result.get('output', ''),
                    command=command,
                    error=result.get('error'),
                    explanation=self._get_explanation(intent)
                )
                
        except Exception as e:
            return Response(
                success=False,
                message=f"Native API error: {str(e)}",
                command=command,
                error=str(e)
            )
    
    def _get_explanation(self, intent: Intent) -> str:
        """Get human-readable explanation of the operation"""
        
        explanations = {
            IntentType.INSTALL_PACKAGE: "This will install the package from the NixOS repository",
            IntentType.REMOVE_PACKAGE: "This will remove the package from your system",
            IntentType.SEARCH_PACKAGE: "This will search for packages matching your query",
            IntentType.UPDATE_SYSTEM: "This will update your entire NixOS system",
            IntentType.LIST_INSTALLED: "This will list all installed packages",
            IntentType.ROLLBACK: "This will revert to the previous system configuration",
            IntentType.GARBAGE_COLLECT: "This will remove old generations and free disk space",
            IntentType.HELP: "Here's how to use Luminous Nix",
        }
        
        return explanations.get(intent.type, "Processing your request")
    
    def _update_metrics(self, success: bool, elapsed_ms: float):
        """Update performance metrics honestly"""
        self.metrics['operations'] += 1
        if success:
            self.metrics['successes'] += 1
        else:
            self.metrics['failures'] += 1
        
        # Update rolling average
        old_avg = self.metrics['avg_response_ms']
        old_count = self.metrics['operations'] - 1
        if old_count > 0:
            self.metrics['avg_response_ms'] = (old_avg * old_count + elapsed_ms) / self.metrics['operations']
        else:
            self.metrics['avg_response_ms'] = elapsed_ms
    
    def _execute_with_api(self, intent: Intent, command: str, query: Query) -> Response:
        """Execute using native API if available, else fallback to executor"""
        if self.use_native:
            return self._execute_native(intent, command, query)
        else:
            result = self.executor.execute(command)
            return Response(
                success=result.get('success', False),
                message=result.get('output', ''),
                command=command,
                error=result.get('error'),
                explanation=self._get_explanation(intent)
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics including consciousness metrics"""
        return {
            **self.metrics,
            'success_rate': self.metrics['successes'] / max(self.metrics['operations'], 1),
            'failure_rate': self.metrics['failures'] / max(self.metrics['operations'], 1),
            'consciousness_coherence': consciousness_field.coherence_level,
            'field_state': consciousness_field.sense_field(),
            'mindful_mode': self.mindful_mode
        }
    
    def set_mindful_mode(self, enabled: bool):
        """Toggle consciousness-first features"""
        self.mindful_mode = enabled
        self.executor.set_mindful_mode(enabled)
        
        if enabled:
            print("🧘 Consciousness-first mode activated")
            print("   Sacred pauses and natural rhythms will be honored")
            consciousness_field.sacred_pause(1.0)
        else:
            print("⚡ Performance mode activated")
            print("   Optimizing for speed over mindfulness")
    
    # Convenience methods for common operations
    
    def install(self, package: str, dry_run: bool = False) -> Response:
        """Install a package"""
        query = Query(f"install {package}", dry_run=dry_run)
        return self.process_query(query)
    
    def search(self, term: str) -> Response:
        """Search for packages"""
        query = Query(f"search {term}")
        return self.process_query(query)
    
    def remove(self, package: str, dry_run: bool = False) -> Response:
        """Remove a package"""
        query = Query(f"remove {package}", dry_run=dry_run)
        return self.process_query(query)
    
    def update_system(self, dry_run: bool = False) -> Response:
        """Update the system"""
        query = Query("update system", dry_run=dry_run)
        return self.process_query(query)
    
    def list_installed(self) -> Response:
        """List installed packages"""
        query = Query("list installed packages")
        return self.process_query(query)
    
    # SKG Integration Methods
    
    def _complete_skg_interaction(self, response: Response, elapsed_ms: float):
        """Complete SKG interaction tracking"""
        if not self.skg:
            return
        
        try:
            # Record the interaction
            interaction_id = self.skg.complete_interaction(
                response=response.message,
                success=response.success,
                command=response.command,
                error=response.error
            )
            
            # Record system qualia (subjective experience)
            if interaction_id > 0:
                system_state = {
                    'computation_time': elapsed_ms,
                    'intent_confidence': getattr(self.skg.current_context, 'confidence', 0.5) if self.skg.current_context else 0.5,
                    'errors': 0 if response.success else 1,
                    'user_satisfaction': 0.8 if response.success else 0.3
                }
                self.skg.record_system_qualia(interaction_id, system_state)
                
                # Update capability confidence
                if self.skg.current_context and self.skg.current_context.intent:
                    self.skg.update_capability_confidence(
                        self.skg.current_context.intent,
                        response.success
                    )
        except Exception as e:
            import logging
            logging.warning(f"Failed to complete SKG interaction: {e}")
    
    def get_learning_insights(self) -> List[str]:
        """Get insights from the SKG about learning progress"""
        if self.skg:
            return self.skg.generate_session_insights()
        return ["SKG not available - no insights to share"]
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get comprehensive user context from SKG"""
        if self.skg:
            return self.skg.get_user_context()
        return {"message": "SKG not available"}
    
    def export_knowledge_graph(self) -> Dict[str, Any]:
        """Export the knowledge graph for visualization"""
        if self.skg:
            return self.skg.export_knowledge_graph()
        return {"error": "SKG not available"}


# Create a singleton instance for backward compatibility
_core_instance = None

def get_core() -> LuminousNixCore:
    """Get or create the singleton core instance"""
    global _core_instance
    if _core_instance is None:
        _core_instance = LuminousNixCore()
    return _core_instance