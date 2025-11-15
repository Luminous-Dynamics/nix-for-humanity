"""
Ollama LLM integration for advanced natural language understanding.

This module provides AI-powered query understanding and package discovery
using local Ollama models.
"""

import json
import subprocess
import hashlib
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OllamaResponse:
    """Response from Ollama model"""

    text: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    model_used: str = ""


class OllamaClient:
    """
    Client for interacting with Ollama for enhanced NLP.

    Features:
    - Package discovery from natural descriptions
    - Complex query understanding
    - Intent clarification
    - Configuration generation assistance
    """

    def __init__(self, model: str = "gemma3:270m", timeout: int = 60):
        """
        Initialize Ollama client.

        Args:
            model: The Ollama model to use (default: gemma3:270m - ultra-fast 291MB model)
            timeout: Timeout for Ollama requests in seconds (default: 60s)
        """
        self.model = model
        self.timeout = timeout
        self.available = self._check_ollama_available()

        # Response cache for faster repeated queries
        self.cache_dir = Path.home() / ".cache" / "luminous-nix" / "llm"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "ollama_cache.json"
        self.cache = self._load_cache()
        self.cache_ttl = 3600 * 24  # 24 hours

        # Fallback models - optimized based on comprehensive testing
        self.fallback_models = [
            "gemma3:270m",  # 291MB - ULTRA-FAST: 0.3-1.2s responses!
            "gemma3:1b",  # 815MB - FAST: 2-7s, good quality
            "qwen2.5:0.5b",  # 394MB - ALTERNATIVE: If gemma unavailable
            "gemma3:4b",  # 3.3GB - COMPLEX: Better understanding
            "qwen2.5:3b",  # 1.9GB - BACKUP: Balanced alternative
            "mistral:7b",  # 4.1GB - LAST RESORT: Original default
        ]

        # Use Gemma 3 for complex queries
        self.complex_model = (
            "gemma3:4b" if self._model_available("gemma3:4b") else self.model
        )

    def _model_available(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return model_name.split(":")[0] in result.stdout.lower()
        except:
            pass
        return False

    def _check_ollama_available(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Check which models are available
                available_models = result.stdout.lower()
                for model in (
                    self.fallback_models
                    if hasattr(self, "fallback_models")
                    else [self.model]
                ):
                    model_name = model.split(":")[0]
                    if model_name in available_models:
                        self.model = model  # Use first available model
                        break
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _load_cache(self) -> Dict[str, Any]:
        """Load response cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    cache = json.load(f)
                # Clean expired entries
                current_time = time.time()
                cache = {
                    k: v
                    for k, v in cache.items()
                    if current_time - v.get("timestamp", 0) < self.cache_ttl
                }
                return cache
            except:
                pass
        return {}

    def _save_cache(self):
        """Save response cache to disk"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass  # Ignore cache save errors

    def _get_cache_key(self, query: str, context: Optional[str]) -> str:
        """Generate cache key for query"""
        key_str = f"{query}:{context or ''}:{self.model}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _is_complex_query(self, query: str) -> bool:
        """Detect if a query is complex and needs better model"""
        complex_indicators = [
            "configure",
            "config",
            "setup",
            "development",
            "environment",
            "how do i",
            "how to",
            "why",
            "explain",
            "understand",
            "multiple",
            "several",
            "various",
            "complex",
            "advanced",
            "troubleshoot",
            "debug",
            "error",
            "problem",
            "issue",
            "best practice",
            "recommend",
            "compare",
            "difference",
            "nix expression",
            "flake",
            "overlay",
            "derivation",
        ]
        query_lower = query.lower()
        # Complex if: long query, multiple sentences, or contains complex indicators
        is_long = len(query) > 50
        has_multiple_sentences = len(query.split(".")) > 1
        has_complex_words = any(
            indicator in query_lower for indicator in complex_indicators
        )

        return is_long or has_multiple_sentences or has_complex_words

    def is_available(self) -> bool:
        """Check if Ollama is available for use"""
        return self.available

    def process_query(
        self, query: str, context: Optional[str] = None
    ) -> OllamaResponse:
        """
        Process a natural language query with Ollama.

        Args:
            query: The user's natural language query
            context: Optional context about the current task

        Returns:
            OllamaResponse with parsed intent and entities
        """
        if not self.available:
            return OllamaResponse(text="Ollama not available", confidence=0.0)

        # Check cache first
        cache_key = self._get_cache_key(query, context)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            return OllamaResponse(
                text=cached["text"],
                intent=cached.get("intent"),
                entities=cached.get("entities"),
                confidence=cached.get("confidence", 0.8),
                model_used=cached.get("model_used", self.model),
            )

        # Detect if query is complex (needs better understanding)
        is_complex = self._is_complex_query(query)

        # Build the prompt for NixOS package management
        prompt = self._build_prompt(query, context)

        # Choose model based on query complexity
        if is_complex and hasattr(self, "complex_model"):
            primary_model = self.complex_model
        else:
            primary_model = self.model

        # Try with progressively longer timeouts and different models
        timeouts = [10, 30, self.timeout]  # Quick, medium, full timeout
        models_to_try = [primary_model] + [
            m for m in self.fallback_models if m != primary_model
        ]

        for timeout_val in timeouts:
            for model in models_to_try[:2]:  # Try at most 2 models per timeout
                try:
                    # Run Ollama with the prompt
                    result = subprocess.run(
                        ["ollama", "run", model, prompt],
                        capture_output=True,
                        text=True,
                        timeout=timeout_val,
                    )

                    if result.returncode == 0:
                        response_text = result.stdout.strip()

                        # Try to parse structured response
                        parsed = self._parse_response(response_text, query)

                        response = OllamaResponse(
                            text=response_text,
                            intent=parsed.get("intent"),
                            entities=parsed.get("entities"),
                            confidence=parsed.get("confidence", 0.8),
                            model_used=model,
                        )

                        # Cache successful response
                        self.cache[cache_key] = {
                            "text": response_text,
                            "intent": response.intent,
                            "entities": response.entities,
                            "confidence": response.confidence,
                            "model_used": model,
                            "timestamp": time.time(),
                        }
                        self._save_cache()

                        return response

                except subprocess.TimeoutExpired:
                    if timeout_val == timeouts[-1] and model == models_to_try[-1]:
                        # Final attempt failed
                        return OllamaResponse(
                            text="Ollama request timed out after multiple attempts",
                            confidence=0.0,
                        )
                    continue  # Try next timeout/model
                except Exception:
                    continue  # Try next model

        # All attempts failed - return graceful fallback
        return OllamaResponse(
            text="Unable to enhance with AI at this time", confidence=0.0
        )

    def _build_prompt(self, query: str, context: Optional[str]) -> str:
        """Build an effective prompt for NixOS operations"""

        prompt = f"""You are a NixOS package management assistant. Parse the user's request and identify:
1. The intent (install, remove, search, update, config, etc.)
2. The package or packages mentioned
3. Any special requirements

User query: "{query}"

{f"Context: {context}" if context else ""}

Respond in this JSON format:
{{
    "intent": "install|remove|search|update|config|info|help",
    "packages": ["package1", "package2"],
    "requirements": ["requirement1", "requirement2"],
    "natural_response": "A helpful explanation"
}}

If the query is complex or unclear, provide your best interpretation and explain in natural_response.
"""
        return prompt

    def _parse_response(
        self, response_text: str, original_query: str
    ) -> Dict[str, Any]:
        """Parse the Ollama response into structured data"""

        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                return {
                    "intent": data.get("intent", "unknown"),
                    "entities": {
                        "packages": data.get("packages", []),
                        "requirements": data.get("requirements", []),
                        "original_query": original_query,
                    },
                    "confidence": 0.9 if data.get("intent") else 0.5,
                    "natural_response": data.get("natural_response", response_text),
                }
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback: Try to extract intent from text
        intent = "unknown"
        entities = {"original_query": original_query}

        lower_text = response_text.lower()
        if "install" in lower_text:
            intent = "install"
        elif "remove" in lower_text or "uninstall" in lower_text:
            intent = "remove"
        elif "search" in lower_text or "find" in lower_text:
            intent = "search"
        elif "update" in lower_text or "upgrade" in lower_text:
            intent = "update"

        return {
            "intent": intent,
            "entities": entities,
            "confidence": 0.6,
            "natural_response": response_text,
        }

    def suggest_packages(self, description: str) -> List[str]:
        """
        Suggest packages based on a natural language description.

        Args:
            description: Natural language description of what the user needs

        Returns:
            List of suggested package names
        """
        if not self.available:
            return []

        prompt = f"""Based on this description, suggest NixOS packages that would be helpful:
"{description}"

List the actual NixOS package names (not descriptions), one per line.
Limit to the 5 most relevant packages.
"""

        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                # Parse package names from response
                lines = result.stdout.strip().split("\n")
                packages = []

                for line in lines:
                    # Clean up the line
                    line = line.strip()
                    # Remove common prefixes like "- " or "* "
                    line = re.sub(r"^[-*\s]+", "", line)
                    # Remove inline comments
                    line = re.sub(r"\s+#.*$", "", line)
                    line = re.sub(r"\s+//.*$", "", line)

                    if line and not line.startswith("#"):
                        # Extract just the package name (first word)
                        parts = line.split()
                        if parts:
                            packages.append(parts[0])

                return packages[:5]  # Limit to 5 suggestions

        except:
            pass

        return []

    def generate_config(self, requirements: str) -> Optional[str]:
        """
        Generate NixOS configuration based on requirements.

        Args:
            requirements: Natural language requirements

        Returns:
            Generated configuration text or None
        """
        if not self.available:
            return None

        prompt = f"""Generate a NixOS configuration snippet for these requirements:
{requirements}

Provide valid Nix configuration code that can be added to configuration.nix.
Include comments explaining each section.
"""

        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout.strip()

        except:
            pass

        return None


# Global instance for easy access - using ULTRA-FAST gemma3:270m (0.3-1.2s!)
ollama_client = OllamaClient(model="gemma3:270m", timeout=60)


def is_ollama_available() -> bool:
    """Check if Ollama is available"""
    return ollama_client.is_available()


def enhance_query(query: str) -> Dict[str, Any]:
    """
    Enhance a query with AI understanding.

    Returns dict with:
    - enhanced: bool (whether enhancement was successful)
    - intent: str
    - entities: dict
    - suggestions: list
    """
    if not ollama_client.is_available():
        return {"enhanced": False, "reason": "Ollama not available"}

    response = ollama_client.process_query(query)

    if response.confidence > 0.7:
        return {
            "enhanced": True,
            "intent": response.intent,
            "entities": response.entities,
            "suggestions": [],
            "confidence": response.confidence,
            "natural_response": response.text,
        }
    else:
        return {
            "enhanced": False,
            "reason": "Low confidence in understanding",
            "raw_response": response.text,
        }
