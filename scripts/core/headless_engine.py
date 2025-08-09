#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Headless Core Engine for Nix for Humanity
The intelligent brain that can serve multiple frontends
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import our existing components
from nix_knowledge_engine import NixOSKnowledgeEngine
from feedback_collector import FeedbackCollector
from core.plugin_manager import get_plugin_manager

# Import learning and cache systems
try:
    import importlib.util
    
    # Import command learning system
    spec = importlib.util.spec_from_file_location("command_learning_system", 
        os.path.join(parent_dir, "command-learning-system.py"))
    command_learning_system = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(command_learning_system)
    CommandLearningSystem = command_learning_system.CommandLearningSystem
    
    # Import package cache manager
    spec = importlib.util.spec_from_file_location("package_cache_manager", 
        os.path.join(parent_dir, "package-cache-manager.py"))
    package_cache_manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package_cache_manager)
    IntelligentPackageCache = package_cache_manager.IntelligentPackageCache
    
    ADVANCED_FEATURES = True
except Exception as e:
    print(f"Warning: Advanced features not available: {e}")
    ADVANCED_FEATURES = False
    
    # Dummy implementations
    class CommandLearningSystem:
        def __init__(self):
            pass
        def learn_from_outcome(self, *args, **kwargs):
            pass
        def get_success_rate(self, *args, **kwargs):
            return 0.0
    
    class IntelligentPackageCache:
        def __init__(self):
            pass
        def get_cached_search(self, *args, **kwargs):
            return None
        def cache_search_results(self, *args, **kwargs):
            pass
        def search_with_fallback(self, *args, **kwargs):
            return [], False
        def get_cache_stats(self, *args, **kwargs):
            return {'total_packages': 0, 'cache_age': 'N/A'}


class ExecutionMode(Enum):
    """Execution modes for commands"""
    DRY_RUN = "dry_run"
    SAFE = "safe"
    FULL = "full"
    LEARNING = "learning"


@dataclass
class Intent:
    """Represents a parsed user intent"""
    action: str
    package: Optional[str] = None
    query: str = ""
    confidence: float = 1.0
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class Context:
    """Context for processing requests"""
    user_id: str = "anonymous"
    session_id: str = ""
    personality: str = "friendly"
    capabilities: List[str] = None
    execution_mode: ExecutionMode = ExecutionMode.DRY_RUN
    collect_feedback: bool = True
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())[:8]
        if self.capabilities is None:
            self.capabilities = ["text"]


@dataclass
class Response:
    """Response from the engine"""
    text: str
    intent: Intent
    commands: List[str] = None
    confidence: float = 1.0
    visual: Optional[Dict[str, Any]] = None
    voice: Optional[str] = None
    feedback_request: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.commands is None:
            self.commands = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "text": self.text,
            "intent": asdict(self.intent),
            "commands": self.commands,
            "confidence": self.confidence,
            "visual": self.visual,
            "voice": self.voice,
            "feedback_request": self.feedback_request,
            "metadata": self.metadata
        }


class HeadlessEngine:
    """
    The core intelligent engine that powers Nix for Humanity
    Can be used by any frontend (CLI, GUI, API, Voice)
    """
    
    def __init__(self):
        """Initialize the headless engine"""
        # Core components
        self.knowledge = NixOSKnowledgeEngine()
        self.feedback = FeedbackCollector()
        self.plugin_manager = None
        
        # Advanced features
        if ADVANCED_FEATURES:
            self.learning = CommandLearningSystem()
            self.cache = IntelligentPackageCache()
        else:
            self.learning = None
            self.cache = None
        
        # Initialize plugin system
        try:
            self.plugin_manager = get_plugin_manager()
            self.plugin_manager.load_all_plugins()
        except Exception as e:
            print(f"Warning: Plugin system initialization failed: {e}")
            self.plugin_manager = None
        
        # Engine state
        self.sessions = {}  # Track active sessions
        self.start_time = datetime.now()
    
    def process(self, input_text: str, context: Context = None) -> Response:
        """
        Main entry point for processing user input
        
        Args:
            input_text: Natural language input from user
            context: Context for processing (user, session, preferences)
            
        Returns:
            Response object with text, commands, and metadata
        """
        if context is None:
            context = Context()
        
        # Extract intent
        intent = self._extract_intent(input_text)
        # Convert context to dict, handling enums
        context_dict = asdict(context)
        context_dict['execution_mode'] = context.execution_mode.value
        intent.context = context_dict
        
        # Check if plugins can handle this
        if self.plugin_manager:
            plugin_result = self._try_plugin_handling(intent, context)
            if plugin_result:
                return plugin_result
        
        # Get solution from knowledge base
        solution = self.knowledge.get_solution(intent.__dict__)
        
        # Format response
        response_text = self.knowledge.format_response(
            intent.__dict__, 
            solution
        )
        
        # Apply personality
        final_text = self._apply_personality(response_text, intent, context)
        
        # Build response object
        response = Response(
            text=final_text,
            intent=intent,
            commands=self._extract_commands(solution),
            confidence=intent.confidence,
            visual=self._generate_visual(solution, context),
            feedback_request=self._generate_feedback_request(context)
        )
        
        # Track interaction
        self._track_interaction(intent, response, context)
        
        return response
    
    def _extract_intent(self, input_text: str) -> Intent:
        """Extract intent from natural language input"""
        raw_intent = self.knowledge.extract_intent(input_text)
        
        return Intent(
            action=raw_intent.get('action', 'unknown'),
            package=raw_intent.get('package'),
            query=input_text,
            confidence=self._calculate_confidence(raw_intent)
        )
    
    def _calculate_confidence(self, raw_intent: Dict[str, Any]) -> float:
        """Calculate confidence score for intent extraction"""
        # Simple heuristic for now
        if raw_intent.get('action') == 'unknown':
            return 0.3
        elif raw_intent.get('package'):
            return 0.9
        else:
            return 0.7
    
    def _try_plugin_handling(self, intent: Intent, context: Context) -> Optional[Response]:
        """Try to handle intent with plugins"""
        if not self.plugin_manager:
            return None
        
        plugin_context = {
            'query': intent.query,
            'intent': asdict(intent),
            'session_id': context.session_id,
            'dry_run': context.execution_mode == ExecutionMode.DRY_RUN,
            'personality': context.personality
        }
        
        result = self.plugin_manager.handle_intent(intent.action, plugin_context)
        
        if result and result.get('success'):
            # Plugin handled it
            text = result.get('response', '')
            text = self._apply_personality(text, intent, context)
            
            return Response(
                text=text,
                intent=intent,
                commands=result.get('commands', []),
                confidence=result.get('confidence', 0.9),
                visual=result.get('visual'),
                feedback_request=self._generate_feedback_request(context)
            )
        
        return None
    
    def _apply_personality(self, text: str, intent: Intent, context: Context) -> str:
        """Apply personality transformation to response"""
        if self.plugin_manager:
            plugin_context = {
                'query': intent.query,
                'personality': context.personality,
                'session_id': context.session_id
            }
            transformed = self.plugin_manager.apply_personality(text, plugin_context)
            if transformed != text:
                return transformed
        
        # Fallback to basic personalities
        if context.personality == 'minimal':
            # Strip extra formatting
            lines = text.split('\n')
            essential_lines = [
                line for line in lines 
                if line.strip() and not line.startswith(('💡', '🌟', '✨'))
            ]
            return '\n'.join(essential_lines)
        
        elif context.personality == 'symbiotic':
            return f"{text}\n\n🤝 I'm still learning! Was this helpful?"
        
        return text
    
    def _extract_commands(self, solution: Dict[str, Any]) -> List[str]:
        """Extract executable commands from solution"""
        commands = []
        
        if solution.get('methods'):
            # Installation methods
            for method in solution['methods']:
                if method.get('example'):
                    commands.append(method['example'])
        
        elif solution.get('example'):
            # Direct example
            commands.append(solution['example'])
        
        return commands
    
    def _generate_visual(self, solution: Dict[str, Any], context: Context) -> Optional[Dict[str, Any]]:
        """Generate visual representation for GUI frontends"""
        if 'visual' not in context.capabilities:
            return None
        
        if solution.get('methods'):
            return {
                'type': 'options',
                'title': 'Installation Methods',
                'choices': [
                    {
                        'id': method['type'],
                        'name': method['name'],
                        'description': method['description'],
                        'command': method['example']
                    }
                    for method in solution['methods']
                ]
            }
        
        return None
    
    def _generate_feedback_request(self, context: Context) -> Optional[Dict[str, Any]]:
        """Generate feedback request if enabled"""
        if not context.collect_feedback:
            return None
        
        if context.personality == 'symbiotic':
            return {
                'type': 'detailed',
                'prompt': 'How can I improve?',
                'options': ['perfect', 'helpful', 'partially helpful', 'not helpful']
            }
        else:
            return {
                'type': 'simple',
                'prompt': 'Was this helpful?',
                'options': ['yes', 'no']
            }
    
    def _track_interaction(self, intent: Intent, response: Response, context: Context):
        """Track interaction for learning and analytics"""
        if self.feedback and context.collect_feedback:
            # Use the actual FeedbackCollector interface
            self.feedback.collect_implicit_feedback(
                query=intent.query,
                response=response.text,
                interaction_time=0.1,  # TODO: Measure actual time - integrate performance monitoring
                user_action='query'  # TODO: Track actual action - implement action classification
            )
        
        if self.learning and intent.action == 'install_package':
            # Track for command learning
            self.learning.record_command(
                intent.action,
                intent.query,
                f"install {intent.package}"
            )
    
    def collect_feedback(self, session_id: str, feedback: Dict[str, Any]) -> bool:
        """
        Collect explicit feedback for an interaction
        
        Args:
            session_id: Session identifier
            feedback: Feedback data (rating, helpful, improved_response, etc.)
            
        Returns:
            True if feedback was collected successfully
        """
        if not self.feedback:
            return False
        
        try:
            if feedback.get('helpful') is not None:
                self.feedback.collect_explicit_feedback(
                    query=feedback.get('query', ''),
                    response=feedback.get('response', ''),
                    helpful=feedback['helpful'],
                    better_response=feedback.get('improved_response')
                )
            
            # TODO: Implement preference tracking - integrate with learning system
            # if feedback.get('preference'):
            #     self.feedback.update_preferences(
            #         preferences={
            #             'personality': feedback.get('personality'),
            #             'response_style': feedback.get('response_style')
            #         },
            #         session_id=session_id
            #     )
            
            return True
        except Exception as e:
            print(f"Error collecting feedback: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        stats = {
            'uptime': str(datetime.now() - self.start_time),
            'active_sessions': len(self.sessions),
            'plugins_loaded': 0,
            'cache_stats': {'total_packages': 0},
            'feedback_stats': {'total': 0}
        }
        
        if self.plugin_manager:
            plugin_info = self.plugin_manager.get_plugin_info()
            stats['plugins_loaded'] = plugin_info['total_plugins']
        
        if self.cache:
            stats['cache_stats'] = self.cache.get_cache_stats()
        
        if self.feedback:
            feedback_stats = self.feedback.get_feedback_stats()
            stats['feedback_stats'] = {
                'total': feedback_stats['total_feedback'],
                'helpfulness_rate': feedback_stats['helpful_percentage'],
                'preference_pairs': feedback_stats['preference_pairs']
            }
        
        return stats
    
    def shutdown(self):
        """Clean shutdown of the engine"""
        # Save any pending data
        if self.learning:
            # Save learning data
            pass
        
        # Clean up plugins
        if self.plugin_manager:
            # Plugin cleanup
            pass
        
        print("Headless engine shutdown complete")


# Simple test
if __name__ == "__main__":
    engine = HeadlessEngine()
    
    # Test queries
    test_queries = [
        "How do I install Firefox?",
        "Update my system",
        "My wifi isn't working"
    ]
    
    print("🧠 Headless Engine Test\n")
    
    for query in test_queries:
        print(f"❓ Query: {query}")
        
        # Create context
        context = Context(
            personality="friendly",
            capabilities=["text", "visual"]
        )
        
        # Process
        response = engine.process(query, context)
        
        print(f"🎯 Intent: {response.intent.action}")
        print(f"💬 Response: {response.text[:200]}...")
        if response.commands:
            print(f"📦 Commands: {response.commands[0]}")
        print()
    
    # Show stats
    stats = engine.get_stats()
    print(f"\n📊 Engine Stats: {json.dumps(stats, indent=2)}")