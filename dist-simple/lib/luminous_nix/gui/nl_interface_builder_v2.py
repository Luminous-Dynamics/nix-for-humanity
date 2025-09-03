"""
🗣️ Natural Language Interface Builder V2
Enhanced with Hybrid NLP+LLM for superior understanding
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from component_synthesis_engine import (
    ComponentRequirements,
    ComponentSynthesizer,
    SynthesizedComponent,
)
from hybrid_nlp_llm import EnhancedIntent, HybridNLPLLM

try:
    from .nl_interface_builder import InterfaceSpecification, UserContext
except ImportError:
    from nl_interface_builder import InterfaceSpecification, UserContext


class GeneratedInterface:
    """Simple stub for generated interface results"""
    def __init__(self, spec: InterfaceSpecification):
        self.specification = spec
        self.components = []
        self.layout = {}


class NLInterfaceBuilderV2:
    """Enhanced interface builder with hybrid NLP+LLM understanding"""

    def __init__(
        self,
        use_llm: bool = True,
        enable_learning: bool = True,
        enable_context: bool = True,
    ):
        # Initialize hybrid parser
        self.hybrid_parser = HybridNLPLLM(
            use_llm=use_llm, llm_threshold=0.6, cache_enabled=True
        )

        # Component synthesizer
        self.synthesizer = ComponentSynthesizer()

        # Conversation context
        self.enable_context = enable_context
        self.conversation_history = []
        self.user_contexts = {}  # Per-user context storage

        # Learning system
        self.enable_learning = enable_learning
        self.successful_patterns = []

    def build_interface(
        self, request: str, context: UserContext | None = None
    ) -> InterfaceSpecification:
        """Build interface with enhanced understanding"""

        # Prepare context for parser
        parser_context = self._prepare_parser_context(request, context)

        # Parse with hybrid system
        intent = self.hybrid_parser.parse(request, parser_context)

        # Handle ambiguities and get clarification if needed
        if intent.ambiguities and self.enable_context:
            intent = self._handle_ambiguities(intent, request, context)

        # Generate components based on enhanced intent
        components = self._generate_components_from_intent(intent, context)

        # Create interface specification
        interface = self._compose_interface(components, intent, context)

        # Update conversation history
        if self.enable_context:
            self._update_conversation_history(request, intent, interface)

        # Learn from this interaction
        if self.enable_learning:
            self._record_pattern(request, intent, interface)

        return interface

    def _prepare_parser_context(
        self, request: str, user_context: UserContext | None
    ) -> dict:
        """Prepare context for the parser"""

        context = {}

        if user_context:
            context["expertise_level"] = user_context.expertise_level
            context["device_type"] = user_context.device_type
            context["preferences"] = user_context.preferences

            # Add user-specific history
            if user_context.user_id in self.user_contexts:
                user_history = self.user_contexts[user_context.user_id]
                context["history"] = user_history.get("recent_requests", [])[-5:]
                context["preferred_styles"] = user_history.get("preferred_styles", {})
                context["common_patterns"] = user_history.get("common_patterns", [])

        # Add recent conversation history
        if self.conversation_history:
            context["recent_conversation"] = [
                h["request"] for h in self.conversation_history[-3:]
            ]

        return context

    def _handle_ambiguities(
        self, intent: EnhancedIntent, request: str, context: UserContext | None
    ) -> EnhancedIntent:
        """Handle ambiguous intents"""

        # For now, make intelligent assumptions
        # In production, this could prompt for clarification

        if "Vague terminology" in intent.ambiguities:
            # Use context to make assumptions
            if context and context.expertise_level == "beginner":
                # Assume simple interface
                intent.interface_type = "simple"
                intent.components_needed = [
                    {
                        "type": "display",
                        "properties": {"simple": True},
                        "priority": "high",
                    }
                ]
            elif context and context.expertise_level == "expert":
                # Assume complex interface
                intent.interface_type = "advanced"
                intent.components_needed.append(
                    {
                        "type": "advanced_controls",
                        "properties": {},
                        "priority": "medium",
                    }
                )

        if "Very short request" in intent.ambiguities:
            # Look at conversation history for context
            if self.conversation_history:
                # Assume continuation of previous topic
                last_intent = self.conversation_history[-1].get("intent")
                if last_intent:
                    intent.interface_type = last_intent.interface_type

        return intent

    def _generate_components_from_intent(
        self, intent: EnhancedIntent, context: UserContext | None
    ) -> list[SynthesizedComponent]:
        """Generate components from enhanced intent"""

        components = []

        # Create component requirements from intent
        for comp_spec in intent.components_needed:
            requirements = ComponentRequirements(
                functionality=comp_spec["type"],
                data_type=comp_spec.get("data_type"),
                interactions=intent.interactions,
                performance=comp_spec.get("priority", "normal"),
                visual_style=self._determine_visual_style(intent, context),
                color_scheme=self._determine_color_scheme(intent, context),
                animation_level=intent.style_preferences.get("animation", "auto"),
                user_expertise=context.expertise_level if context else "intermediate",
                device_type=context.device_type if context else "desktop",
                use_case=intent.target or "general",
            )

            # Synthesize component
            component = self.synthesizer.synthesize(requirements)

            # Apply specific properties from intent
            if "properties" in comp_spec:
                for key, value in comp_spec["properties"].items():
                    if hasattr(component, key):
                        setattr(component, key, value)

            components.append(component)

        # If no components specified, create default based on interface type
        if not components:
            components = self._create_default_components(intent, context)

        return components

    def _determine_visual_style(
        self, intent: EnhancedIntent, context: UserContext | None
    ) -> str:
        """Determine visual style from intent and context"""

        # Check explicit style preferences
        if "minimal" in intent.style_preferences:
            return "minimal"
        if "playful" in intent.style_preferences:
            return "playful"
        if "professional" in intent.style_preferences:
            return "serious"

        # Check user preferences
        if context and context.preferences:
            if "style" in context.preferences:
                return context.preferences["style"]

        # Default based on interface type
        style_map = {
            "dashboard": "modern",
            "form": "clean",
            "editor": "minimal",
            "chart": "data-focused",
        }

        return style_map.get(intent.interface_type, "auto")

    def _determine_color_scheme(
        self, intent: EnhancedIntent, context: UserContext | None
    ) -> str:
        """Determine color scheme"""

        # Check explicit mentions
        if "dark" in intent.style_preferences:
            return "dark"
        if "light" in intent.style_preferences:
            return "light"

        # Check user preferences
        if context and context.preferences:
            if "theme" in context.preferences:
                return context.preferences["theme"]

        # Time-based default
        if context and hasattr(context, "time_context"):
            if context.time_context in ["evening", "night"]:
                return "dark"

        return "auto"

    def _create_default_components(
        self, intent: EnhancedIntent, context: UserContext | None
    ) -> list[SynthesizedComponent]:
        """Create default components for interface type"""

        defaults = {
            "dashboard": ["metrics_display", "chart", "status_panel"],
            "form": ["input_group", "submit_button"],
            "editor": ["text_area", "toolbar"],
            "list": ["item_list", "filter_bar"],
            "chart": ["chart_display", "legend"],
        }

        component_types = defaults.get(intent.interface_type, ["display"])

        components = []
        for comp_type in component_types:
            requirements = ComponentRequirements(
                functionality=comp_type,
                user_expertise=context.expertise_level if context else "intermediate",
            )
            components.append(self.synthesizer.synthesize(requirements))

        return components

    def _compose_interface(
        self,
        components: list[SynthesizedComponent],
        intent: EnhancedIntent,
        context: UserContext | None,
    ) -> InterfaceSpecification:
        """Compose final interface specification"""

        # Determine layout
        layout = {
            "type": intent.layout_suggestion,
            "responsive": intent.style_preferences.get("responsive", True),
            "spacing": self._determine_spacing(intent, context),
        }

        # Determine theme
        theme = {
            "mode": self._determine_color_scheme(intent, context),
            "style": self._determine_visual_style(intent, context),
            "animations": intent.style_preferences.get("animations", True),
            "accessibility": context.preferences.get("accessibility", "standard")
            if context
            else "standard",
        }

        # Set up interactions
        interactions = {
            "primary": intent.interactions[0] if intent.interactions else "click",
            "supported": intent.interactions,
            "gestures": self._determine_gestures(context),
        }

        # Data bindings
        data_bindings = {
            "sources": intent.data_requirements,
            "update_strategy": "realtime"
            if "realtime" in intent.style_preferences
            else "on_demand",
            "cache": True,
        }

        # Metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "confidence": intent.confidence.overall,
            "parse_source": intent.confidence.source,
            "parse_time": getattr(intent, "parse_time", None),
            "user_context": context.__dict__ if context else None,
        }

        return InterfaceSpecification(
            components=components,
            layout=layout,
            theme=theme,
            interactions=interactions,
            data_bindings=data_bindings,
            metadata=metadata,
        )

    def _determine_spacing(
        self, intent: EnhancedIntent, context: UserContext | None
    ) -> str:
        """Determine spacing preference"""

        if context and context.expertise_level == "beginner":
            return "comfortable"  # More space
        if context and context.expertise_level == "expert":
            return "compact"  # Dense information

        return "normal"

    def _determine_gestures(self, context: UserContext | None) -> list[str]:
        """Determine supported gestures"""

        if not context:
            return []

        if context.device_type in ["mobile", "tablet"]:
            return ["swipe", "pinch", "tap", "long_press"]
        return ["drag", "scroll", "hover"]

    def _update_conversation_history(
        self, request: str, intent: EnhancedIntent, interface: InterfaceSpecification
    ):
        """Update conversation history"""

        self.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "request": request,
                "intent": intent,
                "interface_id": id(interface),
                "success": True,
            }
        )

        # Limit history size
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-50:]

    def _record_pattern(
        self, request: str, intent: EnhancedIntent, interface: InterfaceSpecification
    ):
        """Record successful patterns for learning"""

        pattern = {
            "request_pattern": self._extract_pattern(request),
            "intent_type": intent.interface_type,
            "components": [c.dna.purpose for c in interface.components],
            "confidence": intent.confidence.overall,
            "timestamp": datetime.now().isoformat(),
        }

        self.successful_patterns.append(pattern)

    def _extract_pattern(self, request: str) -> str:
        """Extract reusable pattern from request"""

        # Simplified pattern extraction
        # In production, use more sophisticated NLP

        words = request.lower().split()

        # Replace specific values with placeholders
        pattern_words = []
        for word in words:
            if word.isdigit():
                pattern_words.append("<NUMBER>")
            elif word in ["my", "the", "a", "an"]:
                pattern_words.append(word)
            else:
                pattern_words.append(word)

        return " ".join(pattern_words)

    def refine_interface(
        self,
        interface: InterfaceSpecification,
        refinement: str,
        context: UserContext | None = None,
    ) -> InterfaceSpecification:
        """Refine an existing interface based on feedback"""

        # Parse refinement request
        parser_context = self._prepare_parser_context(refinement, context)
        parser_context["existing_interface"] = {
            "components": len(interface.components),
            "layout": interface.layout.get("type"),
            "theme": interface.theme.get("mode"),
        }

        refinement_intent = self.hybrid_parser.parse(refinement, parser_context)

        # Apply refinements
        if refinement_intent.action == "modify":
            # Modify existing components
            for component in interface.components:
                if refinement_intent.style_preferences:
                    # Apply style changes
                    component.styles.update(refinement_intent.style_preferences)

        elif refinement_intent.action == "add":
            # Add new components
            new_components = self._generate_components_from_intent(
                refinement_intent, context
            )
            interface.components.extend(new_components)

        elif refinement_intent.action == "remove":
            # Remove components (simplified)
            if refinement_intent.target:
                interface.components = [
                    c
                    for c in interface.components
                    if refinement_intent.target not in c.dna.purpose.lower()
                ]

        return interface

    def get_statistics(self) -> dict:
        """Get usage and performance statistics"""

        stats = self.hybrid_parser.get_stats()

        stats.update(
            {
                "total_interfaces_generated": len(self.conversation_history),
                "patterns_learned": len(self.successful_patterns),
                "active_users": len(self.user_contexts),
            }
        )

        if self.conversation_history:
            # Calculate average confidence
            avg_confidence = sum(
                h["intent"].confidence.overall
                for h in self.conversation_history
                if "intent" in h
            ) / len(self.conversation_history)

            stats["average_confidence"] = avg_confidence

        return stats


# Testing the enhanced builder
if __name__ == "__main__":
    print("🚀 TESTING NL INTERFACE BUILDER V2")
    print("=" * 60)

    # Initialize enhanced builder
    builder = NLInterfaceBuilderV2(use_llm=True)

    # Test cases showing progression
    test_cases = [
        # Simple request
        ("Create a button", "beginner"),
        # With context
        ("Add a submit button to the form", "intermediate"),
        # Complex request
        (
            "Build a real-time dashboard showing server metrics with CPU, memory, and disk usage charts, dark theme, and automatic refresh every 5 seconds",
            "expert",
        ),
        # Ambiguous request
        ("Make it better", "intermediate"),
        # Conversational
        (
            "Actually, can you make the charts bigger and add some animations?",
            "intermediate",
        ),
    ]

    for request, expertise in test_cases:
        print(f"\n📝 Request: {request[:50]}...")
        print(f"   User Level: {expertise}")

        context = UserContext(
            user_id=f"test_{expertise}",
            expertise_level=expertise,
            device_type="desktop",
            preferences={"theme": "dark"} if expertise == "expert" else {},
        )

        interface = builder.build_interface(request, context)

        print(f"   Components: {len(interface.components)}")
        print(f"   Layout: {interface.layout.get('type')}")
        print(f"   Theme: {interface.theme.get('mode')}")
        print(f"   Confidence: {interface.metadata.get('confidence', 0):.2f}")
        print(f"   Parse Source: {interface.metadata.get('parse_source', 'unknown')}")

        if interface.metadata.get("parse_time"):
            print(f"   Parse Time: {interface.metadata['parse_time']:.2f}ms")

    # Show statistics
    print("\n" + "=" * 60)
    print("📊 BUILDER STATISTICS")
    print("=" * 60)

    stats = builder.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
