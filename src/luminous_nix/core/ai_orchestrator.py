"""
AI Orchestrator - Manages all AI/LLM integrations
Now with Gemma3+HRM hybrid support (restored 2025-12-02)
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Import available AI systems
try:
    from ..ai.hrm_reasoner import HRMNixOSReasoner
    HRM_AVAILABLE = True
except ImportError:
    HRM_AVAILABLE = False
    print("⚠️  HRM integration not available")

try:
    from ..ai.gemma3_hrm_hybrid import Gemma3HRMHybrid
    GEMMA_HYBRID_AVAILABLE = True
except ImportError:
    GEMMA_HYBRID_AVAILABLE = False

try:
    from ..ai.ollama_integration import OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Ollama integration not available")

try:
    from ..ai.config_generator import AIConfigGenerator
    CONFIG_GEN_AVAILABLE = True
except ImportError:
    CONFIG_GEN_AVAILABLE = False

try:
    from ..ai.error_resolver import ErrorResolver
    ERROR_RESOLVER_AVAILABLE = True
except ImportError:
    ERROR_RESOLVER_AVAILABLE = False

@dataclass
class AIResponse:
    """Unified AI response"""
    success: bool
    result: Any
    source: str  # Which AI system provided this
    confidence: float = 0.0
    
class AIOrchestrator:
    """
    Orchestrates all AI/LLM systems for enhanced intelligence.
    
    Features:
    - Natural language understanding via Ollama
    - Config generation from descriptions
    - Intelligent error resolution
    - Fallback to basic NLP if LLMs unavailable
    """
    
    def __init__(self):
        """Initialize available AI systems"""
        self.gemma_hybrid = None
        self.hrm = None
        self.ollama = None
        self.config_gen = None
        self.error_resolver = None
        self.plugin_manager = None

        # Initialize Gemma3+HRM hybrid first (best understanding for NixOS)
        if GEMMA_HYBRID_AVAILABLE:
            try:
                self.gemma_hybrid = Gemma3HRMHybrid()
                print("🚀 Gemma3+HRM hybrid system loaded (enhanced semantic understanding!)")
            except Exception as e:
                print(f"⚠️  Gemma3+HRM hybrid initialization failed: {e}")

        # Initialize HRM as fallback (fastest, most accurate for simple NixOS tasks)
        if HRM_AVAILABLE:
            try:
                from pathlib import Path
                model_path = Path(__file__).parent.parent.parent.parent / "models" / "hrm-nixos-v1" / "best_model.pt"
                self.hrm = HRMNixOSReasoner(str(model_path))
                if model_path.exists():
                    self.hrm.load_model(str(model_path))
                    print("🚀 HRM v1 AI system loaded (3000x faster!)")
                else:
                    print("⚠️  HRM model file not found, will use simulation mode")
            except Exception as e:
                print(f"⚠️  HRM initialization failed: {e}")
        
        # Initialize Ollama as fallback for general knowledge
        if OLLAMA_AVAILABLE and os.getenv("LUMINOUS_AI_ENABLED", "").lower() == "true":
            try:
                self.ollama = OllamaClient()
                if self.ollama.available:
                    print("✅ Ollama AI system connected (fallback)")
                else:
                    print("⚠️  Ollama installed but not running")
            except Exception as e:
                print(f"⚠️  Ollama initialization failed: {e}")
        
        # Initialize other AI systems
        if CONFIG_GEN_AVAILABLE:
            try:
                self.config_gen = AIConfigGenerator()
                print("✅ AI Config Generator initialized")
            except:
                pass
                
        if ERROR_RESOLVER_AVAILABLE:
            try:
                self.error_resolver = ErrorResolver()
                print("✅ AI Error Resolver initialized")
            except:
                pass

        # Initialize plugin manager for plugin recommendations
        try:
            from ..plugins.manager import PluginManager
            self.plugin_manager = PluginManager()
            # Discover plugins so we can recommend them
            self.plugin_manager.discover_plugins()
            print("✅ Plugin system integrated with AI")
        except Exception as e:
            print(f"⚠️  Plugin manager initialization failed: {e}")
    
    def understand_query(self, query: str) -> AIResponse:
        """
        Use AI to understand user query with intent and entities.
        
        Uses intelligent routing:
        - HRM for NixOS-specific tasks (3000x faster!)
        - Ollama for general knowledge questions
        - Pattern matching as final fallback
        """
        # Determine if this is a NixOS task (hybrid/HRM excel at these)
        nix_keywords = ['install', 'package', 'error', 'config', 'dependency', 'collision',
                       'setup', 'enable', 'build', 'derivation', 'overlay', 'flake']
        is_nix_task = any(keyword in query.lower() for keyword in nix_keywords)

        # Try Gemma3+HRM hybrid first for NixOS tasks (best understanding!)
        if self.gemma_hybrid and is_nix_task:
            try:
                result = self.gemma_hybrid.process_query(query)
                return AIResponse(
                    success=True,
                    result={
                        'intent': result.intent.value,
                        'entities': result.entities,
                        'reasoning_path': result.reasoning_path,
                        'model': 'Gemma3+HRM-hybrid'
                    },
                    source="gemma_hybrid",
                    confidence=result.confidence
                )
            except Exception as e:
                print(f"Gemma3+HRM hybrid processing failed: {e}, trying HRM")

        # Try HRM for NixOS tasks (instant response!)
        if self.hrm and is_nix_task:
            try:
                from ..ai.hrm_reasoner import ReasoningTask
                task = ReasoningTask(
                    task_type="config" if "config" in query else "dependency",
                    description=query,
                    constraints=[],
                    current_state={},
                    goal_state={}
                )
                result = self.hrm.reason(task)
                return AIResponse(
                    success=True,
                    result={
                        'intent': 'nix_operation',
                        'solution': result.solution,
                        'steps': result.steps,
                        'model': 'HRM-v1'
                    },
                    source="hrm",
                    confidence=result.confidence
                )
            except Exception as e:
                print(f"HRM processing failed: {e}, trying Ollama")
        
        # Use Ollama for general knowledge or if HRM unavailable
        if self.ollama and self.ollama.available:
            try:
                response = self.ollama.understand_query(query)
                return AIResponse(
                    success=True,
                    result=response,
                    source="ollama",
                    confidence=0.9
                )
            except Exception as e:
                print(f"Ollama failed: {e}, falling back")
        
        # Fallback to basic pattern matching
        return AIResponse(
            success=True,
            result={"query": query, "intent": "unknown"},
            source="basic",
            confidence=0.3
        )
    
    def generate_config(self, description: str) -> AIResponse:
        """Generate NixOS configuration from description"""
        if self.config_gen:
            try:
                config = self.config_gen.generate(description)
                return AIResponse(
                    success=True,
                    result=config,
                    source="ai_config_gen",
                    confidence=0.8
                )
            except Exception as e:
                print(f"Config generation failed: {e}")
        
        # Fallback to templates
        return AIResponse(
            success=False,
            result="AI config generation not available",
            source="none",
            confidence=0.0
        )
    
    def resolve_error(self, error: str) -> AIResponse:
        """Get AI help for error resolution"""
        if self.error_resolver:
            try:
                solution = self.error_resolver.resolve(error)
                return AIResponse(
                    success=True,
                    result=solution,
                    source="ai_error_resolver",
                    confidence=0.7
                )
            except Exception as e:
                print(f"Error resolution failed: {e}")
        
        # Fallback to basic error patterns
        return AIResponse(
            success=False,
            result="Try checking the package name or permissions",
            source="basic",
            confidence=0.2
        )
    
    def recommend_plugins(self, query: str) -> AIResponse:
        """
        Recommend plugins based on user query.

        Analyzes the query and suggests relevant plugins that could help.

        Args:
            query: User's natural language query

        Returns:
            AIResponse with plugin recommendations
        """
        if not self.plugin_manager:
            return AIResponse(
                success=False,
                result="Plugin system not available",
                source="none",
                confidence=0.0
            )

        # Get all discovered plugins
        manifests = self.plugin_manager._manifests.values()
        recommendations = []

        # Simple keyword matching for now
        # TODO: Use semantic similarity with embeddings in future
        query_lower = query.lower()

        # Keyword to plugin mapping
        plugin_keywords = {
            'docker': ['docker-operations'],
            'container': ['docker-operations'],
            'docker-compose': ['docker-operations'],
            'git': ['git-operations'],  # Future plugin
            'version control': ['git-operations'],  # Future plugin
            'systemd': ['systemd-manager'],  # Future plugin
            'service': ['systemd-manager'],  # Future plugin
            'home-manager': ['home-manager-integration'],  # Future plugin
            'dotfiles': ['home-manager-integration'],  # Future plugin
        }

        # Find matching plugins (deduplicated)
        seen_plugins = set()
        matched_keywords = []

        for keyword, plugin_names in plugin_keywords.items():
            if keyword in query_lower:
                matched_keywords.append(keyword)
                for plugin_name in plugin_names:
                    if plugin_name in self.plugin_manager._manifests and plugin_name not in seen_plugins:
                        manifest = self.plugin_manager._manifests[plugin_name]
                        seen_plugins.add(plugin_name)
                        recommendations.append({
                            'name': manifest.name,
                            'version': manifest.version,
                            'description': manifest.description,
                            'keywords': [kw for kw in matched_keywords if plugin_name in plugin_keywords.get(kw, [])],
                            'command': f"ask-nix plugins enable {manifest.name}"
                        })

        if recommendations:
            return AIResponse(
                success=True,
                result={
                    'recommendations': recommendations,
                    'count': len(recommendations)
                },
                source="plugin_recommender",
                confidence=0.8
            )
        else:
            return AIResponse(
                success=False,
                result="No plugin recommendations for this query",
                source="plugin_recommender",
                confidence=0.0
            )

    def answer_query(self, query: str, context: str = "") -> AIResponse:
        """
        Answer a general query with full context.
        This is different from understand_query - it provides actual answers,
        not just intent detection.
        """
        # Use Ollama for general queries if available
        if self.ollama and self.ollama.available:
            try:
                # Pass context to Ollama for better answers
                full_query = f"{context}\n\nUser Query: {query}" if context else query
                response = self.ollama.ask(full_query)
                return AIResponse(
                    success=True,
                    result=response,
                    source="ollama",
                    confidence=0.9
                )
            except Exception as e:
                print(f"Ollama answer failed: {e}")

        # Fallback: provide a helpful message
        return AIResponse(
            success=False,
            result=f"I'd like to answer that question, but I need Ollama to be running. "
                   f"Please start Ollama with: `systemctl start ollama` or run `ollama serve`\n\n"
                   f"Alternatively, for NixOS-specific questions, I can help without Ollama!",
            source="fallback",
            confidence=0.0
        )

    def is_ai_available(self) -> bool:
        """Check if any AI system is available"""
        return bool(self.ollama or self.config_gen or self.error_resolver)

# Global orchestrator instance
_ai_orchestrator = None

def get_ai_orchestrator() -> AIOrchestrator:
    """Get or create AI orchestrator singleton"""
    global _ai_orchestrator
    if _ai_orchestrator is None:
        _ai_orchestrator = AIOrchestrator()
    return _ai_orchestrator
