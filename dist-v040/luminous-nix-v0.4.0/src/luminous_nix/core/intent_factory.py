"""Factory for creating the appropriate intent recognizer.

This module provides a simple way to get the best available intent recognizer
based on system capabilities and user preferences.
"""

import logging

from .config_enhanced_intent import IntentRecognitionConfig
from .intents import IntentRecognizer

logger = logging.getLogger(__name__)


def create_intent_recognizer(config: IntentRecognitionConfig | None = None):
    """
    Create the best available intent recognizer.

    This function:
    1. Checks what's available (LLM, etc.)
    2. Respects user preferences
    3. Returns the most capable recognizer

    Args:
        config: Optional configuration, uses environment if not provided

    Returns:
        An intent recognizer (enhanced if possible, basic if not)
    """

    if config is None:
        config = IntentRecognitionConfig.from_env()

    # Try to create enhanced recognizer
    if config.enable_llm:
        try:
            from .intent_pipeline_enhanced import AdaptiveIntentRecognizer

            recognizer = AdaptiveIntentRecognizer()
            recognizer.set_mode(config.mode)

            # Check if LLM is actually available
            insights = recognizer.get_insights()
            if insights["capabilities"]["ai_available"]:
                logger.info(
                    f"🤖 Enhanced intent recognition enabled (mode: {config.mode})"
                )
            else:
                logger.info("📝 Pattern-based intent recognition (LLM not available)")

            return recognizer

        except ImportError as e:
            logger.debug(f"Enhanced intent recognition not available: {e}")

    # Fallback to basic pattern recognizer
    logger.info("📝 Using pattern-based intent recognition")
    return IntentRecognizer()


class IntentRecognizerProxy:
    """
    A proxy that wraps either basic or enhanced recognizer.

    This provides a consistent interface regardless of which
    recognizer is actually being used.
    """

    def __init__(self, config: IntentRecognitionConfig | None = None):
        """Initialize with the best available recognizer."""
        self.config = config or IntentRecognitionConfig.from_env()
        self._recognizer = None
        self._is_enhanced = False
        self._init_recognizer()

    def _init_recognizer(self):
        """Initialize the actual recognizer."""
        if self.config.enable_llm:
            try:
                from .intent_pipeline_enhanced import AdaptiveIntentRecognizer

                self._recognizer = AdaptiveIntentRecognizer()
                self._recognizer.set_mode(self.config.mode)
                self._is_enhanced = True
                return
            except (ImportError, Exception) as e:
                logger.debug(f"Could not initialize enhanced recognizer: {e}")

        # Fallback to basic
        from .intents import IntentRecognizer

        self._recognizer = IntentRecognizer()
        self._is_enhanced = False

    def recognize(self, text: str, **kwargs):
        """Recognize intent from text."""
        if self._is_enhanced:
            # Enhanced recognizer can handle explain flag
            return self._recognizer.recognize(
                text, explain=self.config.explain_recognition
            )
        # Basic recognizer
        return self._recognizer.recognize(text)

    def teach(self, text: str, correct_intent):
        """Teach the correct intent for a phrase (if supported)."""
        if self._is_enhanced and hasattr(self._recognizer, "teach"):
            return self._recognizer.teach(text, correct_intent)
        return "Learning not available with basic recognizer"

    def get_insights(self):
        """Get performance insights (if supported)."""
        if self._is_enhanced and hasattr(self._recognizer, "get_insights"):
            return self._recognizer.get_insights()
        return {"capabilities": {"ai_available": False, "mode": "pattern-only"}}

    @property
    def is_enhanced(self) -> bool:
        """Check if using enhanced recognizer."""
        return self._is_enhanced
