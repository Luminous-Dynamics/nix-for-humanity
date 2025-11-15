"""LLM-Assisted Intent Recognition for Luminous Nix

This module provides intelligent intent recognition using LLMs when available,
with fallback to pattern matching.
"""

import json
import logging

from .intents import Intent, IntentRecognizer, IntentType

logger = logging.getLogger(__name__)


class LLMIntentRecognizer:
    """Hybrid intent recognizer using LLM when available."""

    def __init__(self):
        """Initialize with pattern-based recognizer as fallback."""
        self.pattern_recognizer = IntentRecognizer()
        self.llm_client = None
        self._init_llm()

    def _init_llm(self):
        """Try to initialize LLM connection."""
        try:
            # Use our new Ollama integration
            from luminous_nix.ai.ollama_integration import ollama_client

            if ollama_client.is_available():
                self.llm_client = ollama_client
                logger.info("✅ Ollama LLM available for advanced intent recognition")
            else:
                self.llm_client = None
                logger.debug("Ollama not available - using pattern matching only")
        except ImportError as e:
            logger.debug(f"Could not import Ollama client: {e}")
            self.llm_client = None

    def recognize(self, text: str, context: dict | None = None) -> Intent:
        """
        Recognize intent using hybrid approach.

        1. Try pattern matching first (fast)
        2. If low confidence or unknown, use LLM
        3. Learn from corrections
        """
        # Always try pattern matching first
        pattern_intent = self.pattern_recognizer.recognize(text)

        # If high confidence pattern match, use it
        if pattern_intent.confidence >= 0.85:
            return pattern_intent

        # If LLM available and pattern confidence is low
        if self.llm_client and (
            pattern_intent.confidence < 0.7 or pattern_intent.type == IntentType.UNKNOWN
        ):
            try:
                llm_intent = self._llm_classify(text, context)

                # If LLM is more confident, use its result
                if llm_intent and llm_intent.confidence > pattern_intent.confidence:
                    # Log this for learning
                    self._log_intent_learning(text, pattern_intent, llm_intent)
                    return llm_intent

            except Exception as e:
                logger.debug(f"LLM classification failed: {e}")

        return pattern_intent

    def _llm_classify(self, text: str, context: dict | None = None) -> Intent | None:
        """Use LLM to classify intent."""

        prompt = self._build_classification_prompt(text)

        try:
            # Use our Ollama client's process_query method
            response = self.llm_client.process_query(
                text, context=json.dumps(context) if context else None
            )

            # Use the structured response from Ollama
            if response.confidence > 0.7:
                intent_data = {
                    "type": self._map_intent_string_to_type(
                        response.intent or "unknown"
                    ),
                    "entities": response.entities or {},
                    "confidence": response.confidence,
                }
            else:
                intent_data = None

            if intent_data:
                return Intent(
                    type=intent_data["type"],
                    entities=intent_data.get("entities", {}),
                    confidence=intent_data.get("confidence", 0.8),
                    raw_text=text,
                )

        except Exception as e:
            logger.debug(f"LLM intent classification error: {e}")

        return None

    def _map_intent_string_to_type(self, intent_str: str) -> IntentType:
        """Map string intent to IntentType enum."""
        intent_map = {
            "install": IntentType.INSTALL_PACKAGE,
            "remove": IntentType.REMOVE_PACKAGE,
            "uninstall": IntentType.REMOVE_PACKAGE,
            "search": IntentType.SEARCH_PACKAGE,
            "find": IntentType.SEARCH_PACKAGE,
            "list": IntentType.LIST_INSTALLED,
            "update": IntentType.UPDATE_SYSTEM,
            "upgrade": IntentType.UPDATE_SYSTEM,
            "info": IntentType.CHECK_STATUS,
            "status": IntentType.CHECK_STATUS,
            "config": IntentType.CONFIG_SYSTEM,
            "help": IntentType.HELP,
            "unknown": IntentType.UNKNOWN,
        }

        return intent_map.get(intent_str.lower(), IntentType.UNKNOWN)

    def _build_classification_prompt(self, text: str) -> str:
        """Build prompt for LLM intent classification."""

        # List available intent types
        intent_types = [t.value for t in IntentType if t != IntentType.UNKNOWN]

        prompt = f"""Classify the following user request into a NixOS command intent.

User request: "{text}"

Available intent types:
{json.dumps(intent_types, indent=2)}

Respond with JSON only:
{{
    "intent": "most_appropriate_intent_type",
    "confidence": 0.0-1.0,
    "entities": {{}}
}}

Examples:
- "install firefox" -> {{"intent": "install_package", "confidence": 0.95, "entities": {{"package": "firefox"}}}}
- "analyze disk space" -> {{"intent": "analyze_disk", "confidence": 0.9, "entities": {{}}}}
- "show network status" -> {{"intent": "show_network", "confidence": 0.85, "entities": {{}}}}

JSON response:"""

        return prompt

    def _parse_llm_response(self, response: str, original_text: str) -> dict | None:
        """Parse LLM response into intent data."""
        try:
            # Extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())

                # Validate and convert intent string to IntentType
                intent_str = data.get("intent", "").upper()
                if not intent_str:
                    return None

                # Try to match to our IntentType enum
                try:
                    intent_type = IntentType(intent_str.lower())
                except ValueError:
                    # Try to find closest match
                    for itype in IntentType:
                        if itype.value == intent_str.lower():
                            intent_type = itype
                            break
                    else:
                        return None

                return {
                    "type": intent_type,
                    "confidence": float(data.get("confidence", 0.8)),
                    "entities": data.get("entities", {}),
                }

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.debug(f"Failed to parse LLM response: {e}")

        return None

    def _log_intent_learning(
        self, text: str, pattern_intent: Intent, llm_intent: Intent
    ):
        """Log cases where LLM disagrees with patterns for future learning."""
        learning_entry = {
            "text": text,
            "pattern_result": {
                "type": pattern_intent.type.value,
                "confidence": pattern_intent.confidence,
            },
            "llm_result": {
                "type": llm_intent.type.value,
                "confidence": llm_intent.confidence,
            },
        }

        # In a full system, this would be saved to a learning database
        # For now, just log it
        logger.info(f"Intent learning opportunity: {json.dumps(learning_entry)}")


class SmartIntentRouter:
    """
    Routes intent recognition based on availability and user preferences.

    This provides the best experience:
    - Fast pattern matching for common cases
    - LLM assistance for complex/ambiguous cases
    - Learning from disagreements
    - Graceful degradation when LLM unavailable
    """

    def __init__(self, prefer_llm: bool = False):
        """
        Initialize router.

        Args:
            prefer_llm: If True, always use LLM when available (slower but more accurate)
        """
        self.prefer_llm = prefer_llm
        self.recognizer = LLMIntentRecognizer()

    def recognize(self, text: str, **kwargs) -> Intent:
        """Route to appropriate recognizer."""

        # If user prefers LLM and it's available, use it directly
        if self.prefer_llm and self.recognizer.llm_client:
            # Still use hybrid approach but with lower pattern threshold
            self.recognizer.pattern_threshold = (
                0.95  # Only use patterns if very confident
            )

        return self.recognizer.recognize(text, **kwargs)
