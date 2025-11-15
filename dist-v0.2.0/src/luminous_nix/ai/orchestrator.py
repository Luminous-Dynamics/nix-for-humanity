#!/usr/bin/env python3
"""
AI Orchestrator for Luminous Nix
Intelligently routes queries to HRM (fast reasoning) or Ollama (general knowledge)
"""

import time
import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

# Import our AI systems
from .hrm_reasoner import HRMNixOSReasoner, ReasoningTask, ReasoningResult
from .ollama_interface import OllamaInterface, OllamaConfig

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available AI models"""

    HRM = "hrm"
    OLLAMA = "ollama"
    PATTERN = "pattern"  # Fallback pattern matching


@dataclass
class OrchestrationResult:
    """Unified result from any AI model"""

    response: str
    model_used: ModelType
    confidence: float
    response_time_ms: float
    reasoning_steps: Optional[List[str]] = None
    fallback_used: bool = False
    metadata: Optional[Dict[str, Any]] = None


class IntentRouter:
    """Routes queries to appropriate AI model based on intent"""

    def __init__(self):
        # NixOS-specific patterns that HRM handles best
        self.nixos_patterns = {
            "dependency": [
                "conflict",
                "collision",
                "dependency",
                "package conflict",
                "version mismatch",
                "incompatible",
                "override",
            ],
            "configuration": [
                "configuration.nix",
                "setup",
                "configure",
                "enable service",
                "system config",
                "nixos config",
                "services.",
                "environment.",
            ],
            "error": [
                "error:",
                "failed",
                "attribute missing",
                "undefined",
                "not found",
                "broken",
                "issue",
                "problem",
            ],
            "optimization": [
                "optimize",
                "performance",
                "faster",
                "improve",
                "reduce size",
                "cleanup",
                "garbage collect",
            ],
        }

        # General patterns better suited for Ollama
        self.general_patterns = [
            "what is",
            "how does",
            "explain",
            "why",
            "when should",
            "best practice",
            "difference between",
            "tutorial",
            "guide",
            "documentation",
            "learn",
        ]

    def classify(self, query: str) -> ModelType:
        """Classify query to determine best model"""
        query_lower = query.lower()

        # Check for NixOS-specific patterns
        for category, patterns in self.nixos_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                logger.debug(f"Routing to HRM: {category} pattern detected")
                return ModelType.HRM

        # Check for general knowledge patterns
        if any(pattern in query_lower for pattern in self.general_patterns):
            logger.debug("Routing to Ollama: general knowledge query")
            return ModelType.OLLAMA

        # Default heuristic: short technical queries → HRM, longer → Ollama
        word_count = len(query.split())
        if word_count < 10 and any(
            tech in query_lower for tech in ["nix", "package", "install", "build"]
        ):
            return ModelType.HRM

        return ModelType.OLLAMA

    def get_confidence_threshold(self, model: ModelType) -> float:
        """Get minimum confidence threshold for model"""
        thresholds = {
            ModelType.HRM: 0.85,
            ModelType.OLLAMA: 0.60,
            ModelType.PATTERN: 0.40,
        }
        return thresholds.get(model, 0.50)


class AIOrchestrator:
    """
    Main orchestrator that manages all AI models
    Provides unified interface with intelligent routing
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator with all AI models"""
        self.config = config or {}

        # Initialize models
        self.hrm = None
        self.ollama = None
        self.router = IntentRouter()

        # Performance tracking
        self.metrics = {
            "hrm_queries": 0,
            "ollama_queries": 0,
            "pattern_fallbacks": 0,
            "total_response_time": 0.0,
        }

        # Initialize models lazily
        self._init_models()

    def _init_models(self):
        """Initialize AI models based on configuration"""
        # Initialize HRM if enabled
        if self.config.get("hrm_enabled", True):
            try:
                self.hrm = HRMNixOSReasoner()
                self.hrm.load_model()  # Would load actual model in production
                logger.info("✅ HRM model initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize HRM: {e}")
                self.hrm = None

        # Initialize Ollama if enabled
        if self.config.get("ollama_enabled", True):
            try:
                ollama_config = OllamaConfig(
                    model=self.config.get("ollama_model", "gemma:2b"),
                    temperature=self.config.get("temperature", 0.7),
                )
                self.ollama = OllamaInterface(ollama_config)
                logger.info("✅ Ollama interface initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama: {e}")
                self.ollama = None

    def process(
        self, query: str, force_model: Optional[ModelType] = None, timeout: float = 5.0
    ) -> OrchestrationResult:
        """
        Process query with appropriate AI model

        Args:
            query: User's natural language query
            force_model: Optional - force specific model
            timeout: Maximum time to wait for response

        Returns:
            OrchestrationResult with response and metadata
        """
        start_time = time.time()

        # Determine which model to use
        if force_model:
            model_to_use = force_model
        else:
            model_to_use = self.router.classify(query)

        # Route to appropriate model
        try:
            if model_to_use == ModelType.HRM and self.hrm:
                result = self._process_with_hrm(query, timeout)
            elif model_to_use == ModelType.OLLAMA and self.ollama:
                result = self._process_with_ollama(query, timeout)
            else:
                result = self._process_with_pattern_matching(query)
        except Exception as e:
            logger.error(f"Error processing with {model_to_use}: {e}")
            result = self._process_with_fallback(query)

        # Update metrics
        response_time = (time.time() - start_time) * 1000
        self.metrics["total_response_time"] += response_time

        # Add timing to result
        result.response_time_ms = response_time

        return result

    def _process_with_hrm(self, query: str, timeout: float) -> OrchestrationResult:
        """Process query with HRM for fast NixOS reasoning"""
        logger.debug(f"Processing with HRM: {query[:50]}...")

        # Determine task type from query
        task_type = self._classify_hrm_task(query)

        # Create reasoning task
        task = ReasoningTask(
            task_type=task_type,
            description=query,
            constraints=self._extract_constraints(query),
            current_state={},
            goal_state={},
        )

        # Get reasoning result
        start = time.time()
        hrm_result = self.hrm.reason(task)
        elapsed = (time.time() - start) * 1000

        self.metrics["hrm_queries"] += 1

        # Check confidence
        confidence_threshold = self.router.get_confidence_threshold(ModelType.HRM)
        if hrm_result.confidence < confidence_threshold and self.ollama:
            logger.debug(
                f"HRM confidence low ({hrm_result.confidence:.2f}), checking with Ollama"
            )
            return self._process_with_ollama(query, timeout, hrm_fallback=hrm_result)

        return OrchestrationResult(
            response=hrm_result.solution,
            model_used=ModelType.HRM,
            confidence=hrm_result.confidence,
            response_time_ms=elapsed,
            reasoning_steps=hrm_result.steps,
            fallback_used=False,
            metadata={"reasoning_depth": hrm_result.reasoning_depth},
        )

    def _process_with_ollama(
        self, query: str, timeout: float, hrm_fallback: Optional[ReasoningResult] = None
    ) -> OrchestrationResult:
        """Process query with Ollama for general knowledge"""
        logger.debug(f"Processing with Ollama: {query[:50]}...")

        start = time.time()

        # Add context if we have HRM fallback
        if hrm_fallback:
            enhanced_query = (
                f"{query}\n\n[Initial analysis: {hrm_fallback.solution[:200]}...]"
            )
        else:
            enhanced_query = query

        # Query Ollama
        ollama_response = self.ollama.query(enhanced_query, max_length=500)
        elapsed = (time.time() - start) * 1000

        self.metrics["ollama_queries"] += 1

        # Extract response and confidence
        if isinstance(ollama_response, dict):
            response_text = ollama_response.get("response", "")
            confidence = ollama_response.get("confidence", 0.7)
        else:
            response_text = str(ollama_response)
            confidence = 0.7

        return OrchestrationResult(
            response=response_text,
            model_used=ModelType.OLLAMA,
            confidence=confidence,
            response_time_ms=elapsed,
            reasoning_steps=None,
            fallback_used=(hrm_fallback is not None),
            metadata={"enhanced_with_hrm": hrm_fallback is not None},
        )

    def _process_with_pattern_matching(self, query: str) -> OrchestrationResult:
        """Fallback to simple pattern matching"""
        logger.debug("Using pattern matching fallback")

        self.metrics["pattern_fallbacks"] += 1

        # Simple pattern-based responses
        patterns = {
            "install": "Use: nix-env -iA nixpkgs.{package}",
            "search": "Use: nix search nixpkgs {term}",
            "update": "Use: nix-channel --update",
            "error": "Check: nix-channel --list and update channels",
            "config": "Edit: /etc/nixos/configuration.nix",
        }

        query_lower = query.lower()
        for pattern, response in patterns.items():
            if pattern in query_lower:
                return OrchestrationResult(
                    response=response,
                    model_used=ModelType.PATTERN,
                    confidence=0.5,
                    response_time_ms=0.1,
                    reasoning_steps=None,
                    fallback_used=True,
                )

        return OrchestrationResult(
            response="I can help with NixOS. Please be more specific about what you need.",
            model_used=ModelType.PATTERN,
            confidence=0.3,
            response_time_ms=0.1,
            reasoning_steps=None,
            fallback_used=True,
        )

    def _process_with_fallback(self, query: str) -> OrchestrationResult:
        """Ultimate fallback when all models fail"""
        logger.warning("All models failed, using ultimate fallback")

        return self._process_with_pattern_matching(query)

    def _classify_hrm_task(self, query: str) -> str:
        """Classify query into HRM task type"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["conflict", "collision", "dependency"]):
            return "dependency"
        elif any(word in query_lower for word in ["setup", "configure", "enable"]):
            return "config"
        elif any(word in query_lower for word in ["error", "failed", "issue"]):
            return "error"
        elif any(word in query_lower for word in ["optimize", "performance", "faster"]):
            return "optimization"
        else:
            return "config"  # Default to configuration

    def _extract_constraints(self, query: str) -> List[str]:
        """Extract constraints from query for HRM"""
        constraints = []

        query_lower = query.lower()

        # Security constraints
        if any(word in query_lower for word in ["secure", "safe", "hardened"]):
            constraints.append("security_required")

        # Performance constraints
        if any(word in query_lower for word in ["fast", "quick", "performance"]):
            constraints.append("optimize_performance")

        # Compatibility constraints
        if any(
            word in query_lower for word in ["compatible", "work with", "alongside"]
        ):
            constraints.append("ensure_compatibility")

        return constraints if constraints else ["standard_setup"]

    def process_batch(self, queries: List[str]) -> List[OrchestrationResult]:
        """Process multiple queries efficiently"""
        results = []

        # Group by model type for efficiency
        hrm_queries = []
        ollama_queries = []

        for query in queries:
            model = self.router.classify(query)
            if model == ModelType.HRM:
                hrm_queries.append(query)
            else:
                ollama_queries.append(query)

        # Process HRM queries (fast)
        for query in hrm_queries:
            results.append(self._process_with_hrm(query, timeout=1.0))

        # Process Ollama queries (slower)
        for query in ollama_queries:
            results.append(self._process_with_ollama(query, timeout=5.0))

        return results

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        total_queries = sum(
            [
                self.metrics["hrm_queries"],
                self.metrics["ollama_queries"],
                self.metrics["pattern_fallbacks"],
            ]
        )

        if total_queries == 0:
            avg_response_time = 0
        else:
            avg_response_time = self.metrics["total_response_time"] / total_queries

        return {
            "total_queries": total_queries,
            "hrm_queries": self.metrics["hrm_queries"],
            "ollama_queries": self.metrics["ollama_queries"],
            "pattern_fallbacks": self.metrics["pattern_fallbacks"],
            "average_response_time_ms": avg_response_time,
            "hrm_percentage": (self.metrics["hrm_queries"] / total_queries * 100)
            if total_queries > 0
            else 0,
        }

    def explain_routing(self, query: str) -> Dict[str, Any]:
        """Explain why a query would be routed to a specific model"""
        model = self.router.classify(query)

        explanation = {"query": query, "selected_model": model.value, "reasoning": []}

        query_lower = query.lower()

        # Check NixOS patterns
        for category, patterns in self.router.nixos_patterns.items():
            matches = [p for p in patterns if p in query_lower]
            if matches:
                explanation["reasoning"].append(
                    f"NixOS {category} patterns detected: {', '.join(matches)}"
                )

        # Check general patterns
        general_matches = [p for p in self.router.general_patterns if p in query_lower]
        if general_matches:
            explanation["reasoning"].append(
                f"General knowledge patterns detected: {', '.join(general_matches)}"
            )

        if not explanation["reasoning"]:
            explanation["reasoning"].append("Default routing based on query structure")

        return explanation


# Convenience functions
_orchestrator = None


def get_orchestrator(config: Optional[Dict[str, Any]] = None) -> AIOrchestrator:
    """Get or create singleton orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator(config)
    return _orchestrator


def ask(
    query: str, model: Optional[str] = None, verbose: bool = False
) -> Union[str, Dict[str, Any]]:
    """
    Simple API for asking questions

    Args:
        query: Natural language question
        model: Optional - force specific model ('hrm', 'ollama')
        verbose: Return full metadata

    Returns:
        Answer string, or dict with metadata if verbose=True
    """
    orchestrator = get_orchestrator()

    # Convert model string to enum
    force_model = None
    if model:
        force_model = ModelType[model.upper()]

    # Process query
    result = orchestrator.process(query, force_model=force_model)

    if verbose:
        return {
            "answer": result.response,
            "model_used": result.model_used.value,
            "confidence": result.confidence,
            "response_time_ms": result.response_time_ms,
            "reasoning_steps": result.reasoning_steps,
            "fallback_used": result.fallback_used,
            "metadata": result.metadata,
        }
    else:
        return result.response


if __name__ == "__main__":
    # Demo the orchestrator
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "how do I install firefox?"

    print(f"Query: {query}")
    print("-" * 50)

    # Get orchestrator
    orchestrator = get_orchestrator()

    # Explain routing
    explanation = orchestrator.explain_routing(query)
    print(f"Model selected: {explanation['selected_model']}")
    print(f"Reasoning: {explanation['reasoning'][0]}")
    print("-" * 50)

    # Process query
    result = orchestrator.process(query)

    print(f"Response ({result.response_time_ms:.1f}ms via {result.model_used.value}):")
    print(result.response)

    if result.reasoning_steps:
        print(f"\nReasoning steps: {len(result.reasoning_steps)}")
        for step in result.reasoning_steps[:3]:
            print(f"  - {step}")

    print("\nMetrics:", orchestrator.get_metrics())
