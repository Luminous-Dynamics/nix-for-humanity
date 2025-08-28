"""
from typing import Dict, Optional
Enhanced response generation with research-based symbiotic intelligence

This module integrates trust building, consciousness metrics, and sacred patterns
into response generation for genuine human-AI partnership.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..api.schema import Intent, Response
from .responses import ResponseGenerator

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels in the relationship"""

    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    COMPANION = "companion"
    PARTNER = "partner"
    SYMBIONT = "symbiont"


@dataclass
class ConsciousnessContext:
    """Context for consciousness-aware responses"""

    wellbeing_score: float
    attention_state: str
    flow_state: bool
    interruption_appropriate: bool
    trust_level: TrustLevel
    vulnerability_opportunity: bool


class SymbioticResponseEnhancer:
    """Enhances responses with research-based symbiotic intelligence"""

    def __init__(
        self,
        response_generator: ResponseGenerator | None = None,
        trust_engine=None,
        metrics_collector=None,
    ):
        """
        Initialize the response enhancer

        Args:
            response_generator: Base response generator
            trust_engine: Trust modeling engine
            metrics_collector: Consciousness metrics collector
        """
        self.response_generator = response_generator
        self.trust_engine = trust_engine
        self.metrics_collector = metrics_collector

    def enhance_response(
        self,
        base_response: Response,
        consciousness_context: ConsciousnessContext | None = None,
    ) -> Response:
        """
        Enhance a response with consciousness-first principles

        Args:
            base_response: The base response to enhance
            consciousness_context: Consciousness state information

        Returns:
            Enhanced response with trust building and consciousness awareness
        """
        enhanced = base_response

        # Apply consciousness-first enhancements
        if consciousness_context:
            # Adjust tone based on wellbeing
            if consciousness_context.wellbeing_score < 0.4:
                enhanced = self._add_wellbeing_support(enhanced)

            # Respect flow state
            if (
                consciousness_context.flow_state
                and not consciousness_context.interruption_appropriate
            ):
                enhanced = self._minimize_interruption(enhanced)

            # Build trust through vulnerability
            if consciousness_context.vulnerability_opportunity:
                enhanced = self._add_vulnerability_disclosure(
                    enhanced, consciousness_context.trust_level
                )

            # Adapt to attention state
            enhanced = self._adapt_to_attention(
                enhanced, consciousness_context.attention_state
            )

        return enhanced

    def _add_wellbeing_support(self, response: Response) -> Response:
        """Add supportive elements for low wellbeing"""
        # Prepend supportive message
        supportive_prefix = (
            "I notice you might be feeling overwhelmed. Let's take this step by step. "
        )
        response.explanation = supportive_prefix + response.explanation

        # Add self-care suggestion
        if not response.suggestions:
            response.suggestions = []
        response.suggestions.insert(
            0, "Consider taking a short break when this task is complete"
        )

        return response

    def _minimize_interruption(self, response: Response) -> Response:
        """Minimize interruption for flow state"""
        # Make response more concise
        if len(response.explanation) > 100:
            # Keep only essential information
            response.explanation = response.explanation[:100] + "..."

        # Remove non-critical suggestions
        if response.suggestions and len(response.suggestions) > 1:
            response.suggestions = response.suggestions[:1]

        # Mark as non-interrupting
        if not response.data:
            response.data = {}
        response.data["flow_respectful"] = True

        return response

    def _add_vulnerability_disclosure(
        self, response: Response, trust_level: TrustLevel
    ) -> Response:
        """Add appropriate vulnerability disclosure for trust building"""
        vulnerabilities = {
            TrustLevel.STRANGER: None,  # Too early
            TrustLevel.ACQUAINTANCE: "I'm still learning the best ways to help with NixOS. Your feedback helps me improve!",
            TrustLevel.COMPANION: "I sometimes struggle with complex package dependencies. I'll do my best to guide you through this.",
            TrustLevel.PARTNER: "I notice I'm not fully confident about this specific configuration. Let's figure it out together.",
            TrustLevel.SYMBIONT: "I sense uncertainty in my reasoning here. My confidence is about 70% - shall we verify this approach together?",
        }

        disclosure = vulnerabilities.get(trust_level)
        if disclosure:
            # Add to response data for special rendering
            if not response.data:
                response.data = {}
            response.data["vulnerability_disclosure"] = disclosure

            # Subtly include in explanation if appropriate
            if trust_level.value in ["companion", "partner", "symbiont"]:
                response.explanation += f"\n\n💭 {disclosure}"

        return response

    def _adapt_to_attention(self, response: Response, attention_state: str) -> Response:
        """Adapt response to user's attention state"""
        if attention_state == "scattered":
            # Use bullet points and clear structure
            if response.explanation and len(response.explanation) > 50:
                # Convert to bullet points
                points = response.explanation.split(". ")
                if len(points) > 1:
                    response.explanation = "Here's what we'll do:\n" + "\n".join(
                        f"• {p.strip()}" for p in points if p.strip()
                    )

        elif attention_state == "focused":
            # Can provide more detailed information
            if response.data and response.data.get("education"):
                # Include educational content in main explanation
                education = response.data["education"]
                if hasattr(education, "concept"):
                    response.explanation += f"\n\n📚 Quick insight: {education.concept}"

        elif attention_state == "fatigued":
            # Minimize cognitive load
            response.explanation = self._simplify_language(response.explanation)
            # Offer to handle complexity
            if not response.suggestions:
                response.suggestions = []
            response.suggestions.append(
                "I can handle the technical details for you - just say 'go ahead'"
            )

        return response

    def _simplify_language(self, text: str) -> str:
        """Simplify language for reduced cognitive load"""
        # Simple word replacements
        replacements = {
            "configure": "set up",
            "initialize": "start",
            "execute": "run",
            "implement": "add",
            "utilize": "use",
            "parameter": "setting",
            "repository": "source",
        }

        simplified = text
        for complex_word, simple_word in replacements.items():
            simplified = simplified.replace(complex_word, simple_word)

        return simplified

    def generate_trust_building_response(
        self, intent: Intent, context: dict[str, Any], trust_state: dict[str, Any]
    ) -> str:
        """
        Generate response that builds trust through CASA principles

        Args:
            intent: The recognized intent
            context: Request context
            trust_state: Current trust state from trust engine

        Returns:
            Trust-building response text
        """
        base_response = ""

        # Check for repair needed
        if trust_state.get("repair_needed"):
            base_response = self._generate_repair_response(
                trust_state["repair_type"], intent
            )

        # Check for vulnerability opportunity
        elif trust_state.get("vulnerability_opportunity"):
            base_response = self._generate_vulnerable_response(
                trust_state["vulnerability_type"], intent
            )

        # Normal response with trust elements
        else:
            base_response = self._generate_trustworthy_response(
                intent, trust_state.get("trust_level", TrustLevel.ACQUAINTANCE)
            )

        return base_response

    def _generate_repair_response(self, repair_type: str, intent: Intent) -> str:
        """Generate conversational repair response"""
        repairs = {
            "misunderstanding": "I think I misunderstood what you were asking for. Let me try again - ",
            "error": "I apologize for that error. Let me correct that and ",
            "confusion": "I see I wasn't clear. What I meant was ",
            "assumption": "I made an assumption there. Let me ask instead - ",
        }

        repair_prefix = repairs.get(repair_type, "Let me clarify - ")

        # Add intent-specific repair
        if intent.type.value == "install_package":
            return (
                repair_prefix
                + f"did you want to install {intent.entities.get('package')} for the current user or system-wide?"
            )
        return (
            repair_prefix
            + "could you tell me more about what you're trying to accomplish?"
        )

    def _generate_vulnerable_response(
        self, vulnerability_type: str, intent: Intent
    ) -> str:
        """Generate response with appropriate vulnerability"""
        if vulnerability_type == "uncertainty":
            return "I'll be honest - I'm about 80% confident this will work for your setup. Here's what I suggest: "
        if vulnerability_type == "limitation":
            return "This touches on something I'm still learning about. I'll share what I know, but please verify: "
        if vulnerability_type == "mistake_acknowledgment":
            return "You know what? I think I gave you outdated information earlier. The current best practice is: "
        return "Let me think about this carefully... "

    def _generate_trustworthy_response(
        self, intent: Intent, trust_level: TrustLevel
    ) -> str:
        """Generate response appropriate to trust level"""
        if trust_level == TrustLevel.STRANGER:
            # Formal, clear, establishing competence
            return f"I can help you {intent.type.value.replace('_', ' ')}. Here's the safe way to do this: "
        if trust_level == TrustLevel.ACQUAINTANCE:
            # Friendly, helpful, building rapport
            return f"Sure! Let's {intent.type.value.replace('_', ' ')} together. "
        if trust_level == TrustLevel.COMPANION:
            # Warm, supportive, collaborative
            return "Of course! I remember you prefer the declarative approach. Let's "
        if trust_level == TrustLevel.PARTNER:
            # Intuitive, predictive, deeply helpful
            return "I was actually thinking you might need this. Based on your workflow, here's what I recommend: "
        # SYMBIONT
        # Seamless, anticipated, extension of self
        return "Already preparing that for you. I noticed your pattern and here's the optimized approach: "
