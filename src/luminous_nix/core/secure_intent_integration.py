"""Integration module for secure intent recognition in the CLI.

This module connects the production-ready secure intent recognizer
with the CLI infrastructure.
"""

import logging
import os
from pathlib import Path
from typing import Any

from .intent_pipeline import Entity, IntentRecognitionResult
from .intent_secure_wrapper import (
    ProductionIntentRecognizer,
)
from .intents import IntentType

logger = logging.getLogger(__name__)


class SecureIntentPipeline:
    """Secure intent pipeline that integrates with the CLI's existing infrastructure."""

    def __init__(
        self,
        security_level: str = "medium",  # Default to medium for balance
        enable_ai: bool = True,
        enable_learning: bool = True,
        cache_dir: Path | None = None,
    ):
        """Initialize secure intent pipeline.

        Args:
            security_level: Security level ("low", "medium", "high")
            enable_ai: Whether to enable AI assistance
            enable_learning: Whether to enable learning from corrections
            cache_dir: Directory for learning database
        """
        # Get security level from environment if set
        env_security = os.environ.get("LUMINOUS_SECURITY_LEVEL", "").lower()
        if env_security in ["low", "medium", "high"]:
            security_level = env_security

        # Check if AI should be disabled (for testing/offline mode)
        env_ai = os.environ.get("LUMINOUS_AI_ENABLED", "").lower() == "true"
        enable_ai = enable_ai and env_ai

        # Create production recognizer
        self.recognizer = ProductionIntentRecognizer(
            enable_llm=enable_ai,
            enable_learning=enable_learning,
            enable_security=True,
            security_level=security_level,
        )

        self.security_level = security_level
        self.stats = {
            "queries_processed": 0,
            "successful": 0,
            "blocked": 0,
            "learned": 0,
        }

        logger.info(
            f"Secure intent pipeline initialized with {security_level} security"
        )

    def recognize(
        self, query: str, context: dict | None = None
    ) -> IntentRecognitionResult:
        """Recognize intent with full security.

        Args:
            query: User input query
            context: Optional conversation context

        Returns:
            IntentRecognitionResult compatible with CLI expectations
        """
        # Get user ID from context or environment
        user_id = None
        if context:
            user_id = context.get("user_id")
        if not user_id:
            user_id = os.environ.get("USER", "unknown")

        # Use secure recognizer
        result = self.recognizer.recognize(query, user_id=user_id, context=context)

        self.stats["queries_processed"] += 1

        # Handle blocked/error cases
        if not result.get("success"):
            self.stats["blocked"] += 1

            # Log security events
            error_type = result.get("error")
            if error_type in ["MALICIOUS_INPUT", "ADVERSARIAL_INPUT"]:
                logger.warning(
                    f"Security threat blocked: {error_type} from user {user_id}"
                )

            # Return low-confidence unknown intent for blocked inputs
            return IntentRecognitionResult(
                primary_intent=IntentType.UNKNOWN,
                confidence=0.0,
                entities=[],
                original_query=query,  # Add required field
                normalized_query=query,  # Add required field
                suggestions=[
                    result.get("message", "Input blocked for security reasons")
                ],
                metadata={
                    "security_block": True,
                    "block_reason": error_type,
                    "threat_level": result.get("security", {}).get("threat_level"),
                },
            )

        # Extract successful intent
        intent_data = result.get("intent", {})
        intent_type = IntentType(intent_data.get("type", "unknown"))
        confidence = intent_data.get("confidence", 0.0)

        # Convert entities to Entity objects for CLI compatibility
        entities = []
        for entity_type, entity_value in intent_data.get("entities", {}).items():
            entities.append(
                Entity(type=entity_type, value=entity_value, confidence=confidence)
            )

        # Build suggestions based on security info
        suggestions = []
        security_info = result.get("security", {})
        warnings = result.get("warnings", [])

        if warnings:
            suggestions.extend(warnings)

        # Add coherence warning if low
        coherence = security_info.get("coherence", 1.0)
        if coherence < 0.5:
            suggestions.append(f"Input seems unclear (coherence: {coherence:.1%})")

        # Add AI assessment if available
        ai_assessment = result.get("ai_assessment")
        if ai_assessment and ai_assessment.get("adversarial"):
            suggestions.append("⚠️ This input appears adversarial")

        self.stats["successful"] += 1

        # Create result compatible with CLI
        return IntentRecognitionResult(
            primary_intent=intent_type,
            confidence=confidence,
            entities=entities,
            original_query=query,  # Add required field
            normalized_query=security_info.get(
                "sanitized_query", query
            ),  # Add required field
            suggestions=suggestions,
            metadata={
                "security": security_info,
                "ai_assessment": ai_assessment,
                "sanitized": security_info.get("sanitized", False),
            },
        )

    def learn_correction(
        self,
        original_query: str,
        correct_intent: IntentType,
        user_id: str | None = None,
    ) -> bool:
        """Learn from user correction.

        Args:
            original_query: Original user query
            correct_intent: The correct intent type
            user_id: Optional user identifier

        Returns:
            True if learning was recorded
        """
        success = self.recognizer.learn_correction(
            original_query, correct_intent, user_id
        )

        if success:
            self.stats["learned"] += 1
            logger.info(
                f"Learned correction: '{original_query}' -> {correct_intent.value}"
            )

        return success

    def get_statistics(self) -> dict[str, Any]:
        """Get pipeline statistics.

        Returns:
            Statistics dictionary
        """
        # Get recognizer stats
        recognizer_stats = self.recognizer.get_statistics()

        # Combine with pipeline stats
        combined = {
            **self.stats,
            **recognizer_stats,
            "security_level": self.security_level,
        }

        return combined

    def reset_statistics(self):
        """Reset all statistics."""
        self.stats = {
            "queries_processed": 0,
            "successful": 0,
            "blocked": 0,
            "learned": 0,
        }
        self.recognizer.reset_statistics()


# Convenience function to create secure pipeline for CLI
def create_secure_pipeline_for_cli(
    verbose: bool = False, security_level: str | None = None
) -> SecureIntentPipeline:
    """Create a secure intent pipeline configured for CLI usage.

    Args:
        verbose: Whether to enable verbose logging
        security_level: Override security level (defaults to environment or "medium")

    Returns:
        Configured SecureIntentPipeline
    """
    # Set logging level based on verbosity
    if verbose:
        logging.basicConfig(level=logging.INFO)

    # Determine security level
    if not security_level:
        # Check environment variable
        security_level = os.environ.get("LUMINOUS_SECURITY_LEVEL", "medium")

    # Check if we're in production mode
    is_production = os.environ.get("LUMINOUS_PRODUCTION", "").lower() == "true"
    if is_production and security_level != "high":
        logger.warning("Production mode detected, forcing high security level")
        security_level = "high"

    # Create and return pipeline
    return SecureIntentPipeline(
        security_level=security_level,
        enable_ai=os.environ.get("LUMINOUS_AI_ENABLED", "").lower() == "true",
        enable_learning=os.environ.get("LUMINOUS_NO_LEARNING", "").lower() != "true",
    )


# Export classes
__all__ = ["SecureIntentPipeline", "create_secure_pipeline_for_cli"]
