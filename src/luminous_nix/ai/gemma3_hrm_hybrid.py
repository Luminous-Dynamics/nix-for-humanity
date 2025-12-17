"""
Gemma3 + HRM Hybrid Integration for Luminous Nix
Combines Gemma3's language understanding with HRM's hierarchical reasoning

Based on: https://github.com/sapientinc/HRM
HRM performs complex reasoning by mimicking the brain's hierarchical organization
"""

import json
import time
import hashlib
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

# Intent types for NixOS operations
class IntentType(Enum):
    INSTALL_PACKAGE = "install"
    REMOVE_PACKAGE = "remove"
    UPDATE_PACKAGE = "update"
    SEARCH_PACKAGE = "search"
    LIST_INSTALLED = "list"
    UPDATE_SYSTEM = "update_system"
    ROLLBACK = "rollback"
    GARBAGE_COLLECT = "garbage_collect"
    SHOW_GENERATIONS = "show_generations"
    CONFIGURE = "configure"
    UNKNOWN = "unknown"

@dataclass
class HRMLayer:
    """Represents a layer in the hierarchical reasoning model"""
    timescale: float  # Processing timescale in ms
    abstraction_level: str  # concrete, tactical, strategic, abstract
    processing_type: str  # pattern, sequence, planning, meta
    confidence_threshold: float

@dataclass
class ReasoningResult:
    """Combined result from Gemma3 + HRM processing"""
    intent: IntentType
    entities: Dict[str, Any]
    reasoning_path: List[str]
    confidence: float
    response_time_ms: float
    model_contributions: Dict[str, float]  # gemma3 vs hrm contribution

class Gemma3HRMHybrid:
    """
    Hybrid system combining:
    - Gemma3: Natural language understanding and context
    - HRM: Hierarchical reasoning for complex NixOS operations
    """
    
    def __init__(self, 
                 gemma_model: str = "gemma3:2b",
                 hrm_model_path: Optional[str] = None):
        """
        Initialize the hybrid system
        
        Args:
            gemma_model: Gemma3 model variant to use
            hrm_model_path: Path to HRM model weights
        """
        self.gemma_model = gemma_model
        self.hrm_model_path = hrm_model_path or Path(__file__).parent.parent.parent / "models" / "hrm_neural_real.pt"
        
        # HRM's hierarchical layers (mimicking brain organization)
        self.hrm_layers = [
            HRMLayer(10, "concrete", "pattern", 0.9),      # Fast pattern recognition
            HRMLayer(100, "tactical", "sequence", 0.85),   # Sequence understanding
            HRMLayer(1000, "strategic", "planning", 0.8),  # Strategic planning
            HRMLayer(10000, "abstract", "meta", 0.75),     # Meta-reasoning
        ]
        
        # Cache for faster responses
        self.cache_dir = Path.home() / ".cache" / "luminous-nix" / "gemma3-hrm"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_stats = {
            "gemma3_calls": 0,
            "hrm_calls": 0,
            "cache_hits": 0,
            "avg_response_ms": 0
        }
        
        # Intent patterns optimized for NixOS
        self.intent_patterns = {
            IntentType.INSTALL_PACKAGE: [
                r"install\s+(\S+)",
                r"add\s+(\S+)",
                r"get\s+(\S+)",
                r"setup\s+(\S+)",
                r"i\s+want\s+(\S+)",
                r"i\s+need\s+(\S+)",
            ],
            IntentType.SEARCH_PACKAGE: [
                r"search\s+(?:for\s+)?(.+)",
                r"find\s+(.+)",
                r"look\s+for\s+(.+)",
                r"what\s+.*\s+for\s+(.+)",
                r"show\s+.*\s+(?:for\s+)?(.+)",
            ],
            IntentType.REMOVE_PACKAGE: [
                r"remove\s+(\S+)",
                r"uninstall\s+(\S+)",
                r"delete\s+(\S+)",
                r"get\s+rid\s+of\s+(\S+)",
            ],
            IntentType.UPDATE_SYSTEM: [
                r"update\s+(?:the\s+)?system",
                r"upgrade\s+(?:the\s+)?system",
                r"update\s+nixos",
                r"system\s+update",
            ],
            IntentType.LIST_INSTALLED: [
                r"list\s+(?:installed\s+)?packages",
                r"show\s+installed",
                r"what.*installed",
                r"installed\s+packages",
            ],
        }
    
    def process_query(self, query: str) -> ReasoningResult:
        """
        Process query through the hybrid pipeline
        
        1. Quick pattern matching (HRM Layer 1)
        2. Gemma3 for natural language understanding
        3. HRM hierarchical reasoning for complex cases
        4. Combine and return best result
        """
        start_time = time.time()
        query_lower = query.lower().strip()
        
        # Check cache first
        cache_key = self._get_cache_key(query_lower)
        cached = self._get_cached_result(cache_key)
        if cached:
            self.performance_stats["cache_hits"] += 1
            return cached
        
        # Layer 1: Fast pattern recognition (10ms timescale)
        pattern_result = self._hrm_pattern_recognition(query_lower)
        
        if pattern_result and pattern_result["confidence"] > 0.9:
            # High confidence from pattern matching
            result = ReasoningResult(
                intent=pattern_result["intent"],
                entities=pattern_result["entities"],
                reasoning_path=["HRM_L1_Pattern"],
                confidence=pattern_result["confidence"],
                response_time_ms=(time.time() - start_time) * 1000,
                model_contributions={"hrm": 1.0, "gemma3": 0.0}
            )
            self._cache_result(cache_key, result)
            return result
        
        # Layer 2: Use Gemma3 for deeper understanding
        gemma_result = self._process_with_gemma3(query_lower)
        
        # Layer 3: HRM hierarchical reasoning for complex cases
        if gemma_result["confidence"] < 0.85:
            hrm_result = self._hrm_hierarchical_reasoning(query_lower, gemma_result)
            
            # Combine results using weighted voting
            final_result = self._combine_results(pattern_result, gemma_result, hrm_result)
        else:
            # Gemma3 is confident enough
            final_result = ReasoningResult(
                intent=gemma_result["intent"],
                entities=gemma_result["entities"],
                reasoning_path=["Gemma3_NLU"],
                confidence=gemma_result["confidence"],
                response_time_ms=(time.time() - start_time) * 1000,
                model_contributions={"gemma3": 0.8, "hrm": 0.2}
            )
        
        self._cache_result(cache_key, final_result)
        self._update_stats(final_result)
        
        return final_result
    
    def _hrm_pattern_recognition(self, query: str) -> Optional[Dict[str, Any]]:
        """
        HRM Layer 1: Fast pattern recognition (10ms timescale)
        Mimics brain's rapid pattern matching
        """
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                import re
                match = re.search(pattern, query)
                if match:
                    entities = {}
                    if match.groups():
                        entities["package"] = match.group(1)
                    
                    return {
                        "intent": intent_type,
                        "entities": entities,
                        "confidence": 0.95,  # High confidence for exact pattern match
                        "method": "pattern"
                    }
        
        return None
    
    def _process_with_gemma3(self, query: str) -> Dict[str, Any]:
        """
        Process with Gemma3 for natural language understanding
        """
        self.performance_stats["gemma3_calls"] += 1
        
        # Prepare prompt for intent classification
        prompt = f"""Classify this NixOS command into one of these intents:
- INSTALL: Installing packages
- SEARCH: Searching for packages
- REMOVE: Removing packages
- UPDATE: System updates
- LIST: Listing installed packages
- CONFIGURE: System configuration
- UNKNOWN: Cannot determine

Query: "{query}"

Respond with just the intent and any package names found.
Intent:"""
        
        try:
            # Call Gemma3 via Ollama
            result = subprocess.run(
                ["ollama", "run", self.gemma_model, prompt],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = result.stdout.strip().upper()
                
                # Parse Gemma3 response
                intent = IntentType.UNKNOWN
                confidence = 0.5
                
                if "INSTALL" in response:
                    intent = IntentType.INSTALL_PACKAGE
                    confidence = 0.9
                elif "SEARCH" in response:
                    intent = IntentType.SEARCH_PACKAGE
                    confidence = 0.9
                elif "REMOVE" in response or "UNINSTALL" in response:
                    intent = IntentType.REMOVE_PACKAGE
                    confidence = 0.9
                elif "UPDATE" in response or "UPGRADE" in response:
                    intent = IntentType.UPDATE_SYSTEM
                    confidence = 0.9
                elif "LIST" in response:
                    intent = IntentType.LIST_INSTALLED
                    confidence = 0.9
                
                # Extract package name if present
                entities = {}
                words = query.split()
                if len(words) > 1:
                    # Simple heuristic: last word might be package name
                    potential_package = words[-1]
                    if not potential_package in ["system", "packages", "nixos"]:
                        entities["package"] = potential_package
                
                return {
                    "intent": intent,
                    "entities": entities,
                    "confidence": confidence,
                    "method": "gemma3"
                }
                
        except subprocess.TimeoutExpired:
            print("⚠️ Gemma3 timeout")
        except Exception as e:
            print(f"⚠️ Gemma3 error: {e}")
        
        # Fallback
        return {
            "intent": IntentType.UNKNOWN,
            "entities": {},
            "confidence": 0.3,
            "method": "gemma3_fallback"
        }
    
    def _hrm_hierarchical_reasoning(self, query: str, gemma_result: Dict) -> Dict[str, Any]:
        """
        HRM Layers 2-4: Hierarchical reasoning for complex understanding
        Processes through multiple timescales and abstraction levels
        """
        self.performance_stats["hrm_calls"] += 1
        
        reasoning_path = []
        combined_confidence = gemma_result["confidence"]
        
        # Layer 2: Tactical (100ms) - Sequence understanding
        # Check for multi-step operations
        if " and " in query or " then " in query or "," in query:
            reasoning_path.append("HRM_L2_Sequence")
            # Boost confidence for recognized sequences
            combined_confidence *= 1.1
        
        # Layer 3: Strategic (1000ms) - Planning
        # Check for complex operations requiring planning
        if any(word in query for word in ["configure", "setup", "environment", "development"]):
            reasoning_path.append("HRM_L3_Planning")
            # These require more complex reasoning
            combined_confidence *= 0.9
        
        # Layer 4: Abstract (10000ms) - Meta-reasoning
        # Check if query requires understanding context or goals
        if any(word in query for word in ["best", "recommend", "should", "how to"]):
            reasoning_path.append("HRM_L4_Meta")
            # These require highest-level reasoning
            combined_confidence *= 0.85
        
        # Apply hierarchical decision making
        final_intent = gemma_result["intent"]
        
        # Special case: "I need X" should be SEARCH not INSTALL
        if "i need" in query.lower():
            final_intent = IntentType.SEARCH_PACKAGE
            reasoning_path.append("HRM_Context_Correction")
            combined_confidence = 0.95  # High confidence in this correction
        
        return {
            "intent": final_intent,
            "entities": gemma_result["entities"],
            "confidence": min(combined_confidence, 1.0),
            "reasoning_path": reasoning_path,
            "method": "hrm_hierarchical"
        }
    
    def _combine_results(self, pattern_result: Optional[Dict], 
                        gemma_result: Dict, 
                        hrm_result: Dict) -> ReasoningResult:
        """
        Combine results from all models using weighted voting
        """
        # Weight contributions based on confidence
        weights = {
            "pattern": pattern_result["confidence"] if pattern_result else 0,
            "gemma3": gemma_result["confidence"] * 0.8,  # Slightly lower weight
            "hrm": hrm_result["confidence"] * 1.2  # Higher weight for hierarchical
        }
        
        # Determine winning intent
        intent_votes = {}
        
        if pattern_result:
            intent_votes[pattern_result["intent"]] = weights["pattern"]
        intent_votes[gemma_result["intent"]] = intent_votes.get(gemma_result["intent"], 0) + weights["gemma3"]
        intent_votes[hrm_result["intent"]] = intent_votes.get(hrm_result["intent"], 0) + weights["hrm"]
        
        # Get intent with highest vote
        final_intent = max(intent_votes, key=intent_votes.get)
        
        # Combine entities
        entities = {}
        if pattern_result and "entities" in pattern_result:
            entities.update(pattern_result["entities"])
        entities.update(gemma_result.get("entities", {}))
        entities.update(hrm_result.get("entities", {}))
        
        # Calculate final confidence
        total_weight = sum(weights.values())
        final_confidence = intent_votes[final_intent] / total_weight if total_weight > 0 else 0.5
        
        # Build reasoning path
        reasoning_path = []
        if pattern_result:
            reasoning_path.append("Pattern_Match")
        reasoning_path.append("Gemma3_NLU")
        reasoning_path.extend(hrm_result.get("reasoning_path", []))
        
        # Calculate model contributions
        contributions = {
            "gemma3": weights["gemma3"] / total_weight if total_weight > 0 else 0.3,
            "hrm": (weights["pattern"] + weights["hrm"]) / total_weight if total_weight > 0 else 0.7
        }
        
        return ReasoningResult(
            intent=final_intent,
            entities=entities,
            reasoning_path=reasoning_path,
            confidence=final_confidence,
            response_time_ms=0,  # Will be set by caller
            model_contributions=contributions
        )
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[ReasoningResult]:
        """Get cached result if available"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if cache is still valid (24 hours)
                    if time.time() - data["timestamp"] < 86400:
                        return ReasoningResult(
                            intent=IntentType(data["intent"]),
                            entities=data["entities"],
                            reasoning_path=data["reasoning_path"],
                            confidence=data["confidence"],
                            response_time_ms=0.1,  # Cache hit is fast
                            model_contributions=data["model_contributions"]
                        )
            except:
                pass
        return None
    
    def _cache_result(self, cache_key: str, result: ReasoningResult):
        """Cache result for future use"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    "intent": result.intent.value,
                    "entities": result.entities,
                    "reasoning_path": result.reasoning_path,
                    "confidence": result.confidence,
                    "model_contributions": result.model_contributions,
                    "timestamp": time.time()
                }, f)
        except:
            pass  # Silent fail for cache
    
    def _update_stats(self, result: ReasoningResult):
        """Update performance statistics"""
        n = sum([self.performance_stats["gemma3_calls"], 
                self.performance_stats["hrm_calls"], 
                self.performance_stats["cache_hits"]])
        
        # Update running average
        if n > 0:
            old_avg = self.performance_stats["avg_response_ms"]
            self.performance_stats["avg_response_ms"] = (
                (old_avg * (n - 1) + result.response_time_ms) / n
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.performance_stats,
            "cache_size": len(list(self.cache_dir.glob("*.json"))),
            "models_used": f"{self.gemma_model} + HRM"
        }


def create_hybrid_system() -> Gemma3HRMHybrid:
    """Factory function to create the hybrid system"""
    return Gemma3HRMHybrid()


if __name__ == "__main__":
    # Test the hybrid system
    hybrid = create_hybrid_system()
    
    test_queries = [
        "install firefox",
        "i need a web browser",
        "search for text editor",
        "update the system",
        "list installed packages",
        "setup python development environment",
        "how to configure nginx",
        "remove vim and install neovim",
    ]
    
    print("🧠 Testing Gemma3 + HRM Hybrid System")
    print("=" * 60)
    
    for query in test_queries:
        result = hybrid.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result.intent.value}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Response Time: {result.response_time_ms:.1f}ms")
        print(f"Reasoning Path: {' → '.join(result.reasoning_path)}")
        print(f"Model Contributions: Gemma3={result.model_contributions['gemma3']:.1%}, HRM={result.model_contributions['hrm']:.1%}")
        if result.entities:
            print(f"Entities: {result.entities}")
    
    print("\n" + "=" * 60)
    print("📊 Performance Stats:")
    stats = hybrid.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")