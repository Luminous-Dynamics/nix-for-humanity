"""Production-ready secure intent recognition wrapper.

This module provides the main interface for secure intent recognition
with all security features enabled by default.
"""

import logging
from typing import Any

from .config_enhanced_intent import IntentRecognitionConfig
from .intent_factory import IntentRecognizerProxy
from .intent_improvement import IntentLearningDatabase
from .intent_security import SecureIntentRecognizer
from .intents import Intent, IntentRecognizer, IntentType

logger = logging.getLogger(__name__)


class ProductionIntentRecognizer:
    """Production-ready intent recognizer with full security."""

    def __init__(
        self,
        enable_llm: bool = True,
        enable_learning: bool = True,
        enable_security: bool = True,
        security_level: str = "high",
        llm_client: Any | None = None,
    ):
        """Initialize production recognizer.

        Args:
            enable_llm: Whether to enable LLM assistance
            enable_learning: Whether to enable learning from corrections
            enable_security: Whether to enable security features
            security_level: Security level ("low", "medium", "high")
            llm_client: Optional LLM client for coherence checking
        """
        # Create base recognizer (with hybrid capabilities if available)
        if enable_llm:
            config = IntentRecognitionConfig(enable_llm=True, mode="balanced")
            self.base_recognizer = IntentRecognizerProxy(config)
        else:
            self.base_recognizer = IntentRecognizer()

        # Wrap with security if enabled
        if enable_security:
            self.recognizer = SecureIntentRecognizer(
                self.base_recognizer, llm_client=llm_client
            )
            self.security_enabled = True
        else:
            self.recognizer = self.base_recognizer
            self.security_enabled = False

        # Initialize learning database if enabled
        if enable_learning:
            self.learning_db = IntentLearningDatabase()
        else:
            self.learning_db = None

        self.security_level = security_level
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "blocked": 0,
            "errors": 0,
            "threats_detected": {},
        }

    def recognize(
        self, text: str, user_id: str | None = None, context: dict | None = None
    ) -> dict[str, Any]:
        """Recognize intent with full security and learning.

        Args:
            text: User input text
            user_id: Optional user identifier for rate limiting
            context: Optional context dictionary

        Returns:
            Dictionary with intent and metadata
        """
        self.stats["total_requests"] += 1

        try:
            # Use secure recognizer if enabled
            if self.security_enabled:
                result = self.recognizer.recognize(text, user_id)

                # Track security events
                if result.get("error"):
                    self.stats["blocked"] += 1
                    threat = result.get("error", "unknown")
                    self.stats["threats_detected"][threat] = (
                        self.stats["threats_detected"].get(threat, 0) + 1
                    )

                    # Log high-severity threats
                    if threat in ["MALICIOUS_INPUT", "ADVERSARIAL_INPUT"]:
                        logger.warning(
                            f"High-severity threat detected: {threat} from user {user_id}"
                        )

                    return self._format_error_response(result)

                # Extract intent from secure result
                intent = result.get("intent")
                security_info = result.get("security", {})
                llm_assessment = result.get("llm_assessment")

            else:
                # Direct recognition without security
                intent = self.recognizer.recognize(text)
                security_info = {}
                llm_assessment = None

            if not intent:
                self.stats["errors"] += 1
                return {
                    "success": False,
                    "error": "RECOGNITION_FAILED",
                    "message": "Could not recognize intent",
                }

            # Apply security level adjustments
            intent = self._apply_security_level(intent, security_info)

            # Record for learning if enabled
            if self.learning_db and intent.type != IntentType.UNKNOWN:
                self.learning_db.log_query(
                    text,
                    intent.type.value,
                    intent.confidence,
                    0.1,  # Placeholder latency
                )

            self.stats["successful"] += 1

            # Format successful response
            return self._format_success_response(intent, security_info, llm_assessment)

        except Exception as e:
            logger.error(f"Intent recognition error: {e}")
            self.stats["errors"] += 1
            return {"success": False, "error": "INTERNAL_ERROR", "message": str(e)}

    def _apply_security_level(self, intent: Intent, security_info: dict) -> Intent:
        """Apply security level adjustments to intent.

        Args:
            intent: Recognized intent
            security_info: Security assessment info

        Returns:
            Adjusted intent
        """
        if not security_info:
            return intent

        # Adjust confidence based on security level
        if self.security_level == "high":
            # Reduce confidence for any warnings
            if security_info.get("warnings"):
                intent.confidence *= 0.8

            # Reduce confidence for low coherence
            coherence = security_info.get("coherence", 1.0)
            if coherence < 0.7:
                intent.confidence *= coherence

            # Mark as unknown if too suspicious
            threat_level = security_info.get("threat_level")
            if threat_level in ["suspicious", "nonsense"]:
                if intent.confidence < 0.5:
                    intent.type = IntentType.UNKNOWN
                    intent.confidence = 0.1

        elif self.security_level == "medium":
            # Moderate adjustments
            coherence = security_info.get("coherence", 1.0)
            if coherence < 0.5:
                intent.confidence *= 0.7

        # Low security level: minimal adjustments

        return intent

    def _format_success_response(
        self, intent: Intent, security_info: dict, llm_assessment: dict | None
    ) -> dict[str, Any]:
        """Format successful recognition response.

        Args:
            intent: Recognized intent
            security_info: Security assessment
            llm_assessment: Optional LLM assessment

        Returns:
            Formatted response dictionary
        """
        response = {
            "success": True,
            "intent": {
                "type": intent.type.value,
                "confidence": intent.confidence,
                "entities": intent.entities,
            },
        }

        # Add security information if available
        if security_info:
            response["security"] = {
                "threat_level": security_info.get("threat_level", "unknown"),
                "coherence": security_info.get("coherence", 1.0),
                "sanitized": security_info.get("sanitized", False),
            }

            # Add warnings if present
            if security_info.get("warnings"):
                response["warnings"] = security_info["warnings"]

        # Add LLM assessment if available
        if llm_assessment and llm_assessment.get("available"):
            response["ai_assessment"] = {
                "coherence": llm_assessment.get("coherence_score"),
                "confidence": llm_assessment.get("confidence_score"),
                "intent_clarity": llm_assessment.get("intent_clarity"),
                "adversarial": llm_assessment.get("is_adversarial", False),
            }

        return response

    def _format_error_response(self, error_result: dict) -> dict[str, Any]:
        """Format error response.

        Args:
            error_result: Error result from secure recognizer

        Returns:
            Formatted error response
        """
        error_type = error_result.get("error", "UNKNOWN_ERROR")

        # User-friendly error messages
        error_messages = {
            "RATE_LIMITED": "Too many requests. Please wait a moment.",
            "MALICIOUS_INPUT": "Input appears unsafe and was blocked.",
            "ADVERSARIAL_INPUT": "Input appears to be testing the system.",
            "RECOGNITION_ERROR": "Could not process your request.",
            "INTERNAL_ERROR": "An internal error occurred.",
        }

        return {
            "success": False,
            "error": error_type,
            "message": error_messages.get(error_type, "Request could not be processed"),
            "details": error_result.get("reason")
            if self.security_level != "high"
            else None,
        }

    def learn_correction(
        self,
        original_text: str,
        correct_intent: IntentType,
        user_id: str | None = None,
    ) -> bool:
        """Learn from a correction.

        Args:
            original_text: Original input text
            correct_intent: The correct intent type
            user_id: Optional user identifier

        Returns:
            True if learning was recorded
        """
        if not self.learning_db:
            return False

        try:
            # Record correction in learning database
            from .intent_improvement import IntentFeedback

            # Get original recognition
            result = self.recognize(original_text, user_id)
            original_intent = result.get("intent", {}).get("type", "unknown")

            feedback = IntentFeedback(
                query=original_text,
                recognized_intent=original_intent,
                correct_intent=correct_intent.value,
                confidence=result.get("intent", {}).get("confidence", 0),
                timestamp=time.time(),
            )

            self.learning_db.add_feedback(feedback)

            # If using hybrid recognizer, teach it
            if hasattr(self.base_recognizer, "teach"):
                self.base_recognizer.teach(original_text, correct_intent)

            return True

        except Exception as e:
            logger.error(f"Failed to record learning: {e}")
            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get recognition statistics.

        Returns:
            Statistics dictionary
        """
        stats = self.stats.copy()

        # Calculate rates
        if stats["total_requests"] > 0:
            stats["success_rate"] = stats["successful"] / stats["total_requests"]
            stats["block_rate"] = stats["blocked"] / stats["total_requests"]
            stats["error_rate"] = stats["errors"] / stats["total_requests"]
        else:
            stats["success_rate"] = 0
            stats["block_rate"] = 0
            stats["error_rate"] = 0

        return stats

    def reset_statistics(self):
        """Reset statistics counters."""
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "blocked": 0,
            "errors": 0,
            "threats_detected": {},
        }


# Convenience function for creating production recognizer
def create_production_recognizer(
    security_level: str = "high", enable_ai: bool = True
) -> ProductionIntentRecognizer:
    """Create a production-ready recognizer with recommended settings.

    Args:
        security_level: Security level ("low", "medium", "high")
        enable_ai: Whether to enable AI features

    Returns:
        Configured ProductionIntentRecognizer
    """
    return ProductionIntentRecognizer(
        enable_llm=enable_ai,
        enable_learning=True,
        enable_security=True,
        security_level=security_level,
    )


# Export classes
__all__ = ["ProductionIntentRecognizer", "create_production_recognizer"]
