"""
🗣️ Natural Language Interface Builder
Transforms human desires into functional interfaces through semantic understanding
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from .component_synthesis_engine import (
        ComponentDNA,
        ComponentRequirements,
        ComponentSynthesizer,
        SynthesizedComponent,
    )
except ImportError:
    from component_synthesis_engine import (
        ComponentRequirements,
        ComponentSynthesizer,
        SynthesizedComponent,
    )


class IntentAction(Enum):
    """Primary actions users can request"""

    CREATE = "create"
    SHOW = "show"
    MODIFY = "modify"
    REMOVE = "remove"
    ORGANIZE = "organize"
    CUSTOMIZE = "customize"


class InterfaceType(Enum):
    """Types of interfaces that can be created"""

    DASHBOARD = "dashboard"
    FORM = "form"
    LIST = "list"
    EDITOR = "editor"
    VIEWER = "viewer"
    MONITOR = "monitor"
    WORKSPACE = "workspace"
    WIDGET = "widget"


@dataclass
class ParsedIntent:
    """Parsed user intent from natural language"""

    action: IntentAction
    interface_type: InterfaceType | None
    target: str | None  # What to show/create/modify
    purpose: str | None  # Why they want it
    modifiers: list[str] = field(default_factory=list)  # How they want it
    constraints: list[str] = field(default_factory=list)  # Limitations
    style_preferences: list[str] = field(default_factory=list)  # Aesthetic desires
    data_context: str | None = None  # What data to work with


@dataclass
class UserContext:
    """User's current context and preferences"""

    user_id: str
    expertise_level: str = "intermediate"  # beginner, intermediate, expert
    current_task: str | None = None
    device_type: str = "desktop"
    preferences: dict[str, Any] = field(default_factory=dict)
    interaction_history: list[str] = field(default_factory=list)
    time_context: str = "day"  # morning, day, evening, night
    cognitive_load: float = 0.5  # 0-1 scale


@dataclass
class InterfaceSpecification:
    """Complete specification for an interface"""

    components: list[SynthesizedComponent]
    layout: dict[str, Any]
    theme: dict[str, Any]
    interactions: dict[str, Any]
    data_bindings: dict[str, Any]
    metadata: dict[str, Any]


class NaturalLanguageParser:
    """Parse natural language into structured intent"""

    def __init__(self):
        # Action keywords
        self.action_patterns = {
            IntentAction.CREATE: r"\b(create|make|build|generate|design)\b",
            IntentAction.SHOW: r"\b(show|display|present|view|see)\b",
            IntentAction.MODIFY: r"\b(change|modify|update|edit|adjust)\b",
            IntentAction.REMOVE: r"\b(remove|delete|hide|close)\b",
            IntentAction.ORGANIZE: r"\b(organize|arrange|layout|structure)\b",
            IntentAction.CUSTOMIZE: r"\b(customize|personalize|theme|style)\b",
        }

        # Interface type keywords
        self.interface_patterns = {
            InterfaceType.DASHBOARD: r"\b(dashboard|overview|summary|status)\b",
            InterfaceType.FORM: r"\b(form|input|entry|submission)\b",
            InterfaceType.LIST: r"\b(list|items|collection|catalog)\b",
            InterfaceType.EDITOR: r"\b(editor|writing|document|text)\b",
            InterfaceType.VIEWER: r"\b(viewer|reader|display|preview)\b",
            InterfaceType.MONITOR: r"\b(monitor|tracking|metrics|analytics)\b",
            InterfaceType.WORKSPACE: r"\b(workspace|environment|studio)\b",
            InterfaceType.WIDGET: r"\b(widget|component|element|module)\b",
        }

        # Style modifiers
        self.style_keywords = {
            "minimal": ["simple", "clean", "minimal", "basic", "plain"],
            "rich": ["rich", "detailed", "comprehensive", "full"],
            "playful": ["fun", "playful", "colorful", "animated", "lively"],
            "serious": ["serious", "professional", "formal", "business"],
            "dark": ["dark", "night", "black"],
            "light": ["light", "bright", "white"],
            "zen": ["zen", "calm", "peaceful", "serene", "focused"],
        }

    def parse(self, text: str, context: UserContext | None = None) -> ParsedIntent:
        """Parse natural language into structured intent"""

        text_lower = text.lower()

        # Extract action
        action = self._extract_action(text_lower)

        # Extract interface type
        interface_type = self._extract_interface_type(text_lower)

        # Extract target
        target = self._extract_target(text_lower)

        # Extract purpose
        purpose = self._extract_purpose(text_lower)

        # Extract modifiers
        modifiers = self._extract_modifiers(text_lower)

        # Extract style preferences
        style_preferences = self._extract_styles(text_lower)

        # Extract constraints
        constraints = self._extract_constraints(text_lower)

        # Extract data context
        data_context = self._extract_data_context(text_lower)

        return ParsedIntent(
            action=action,
            interface_type=interface_type,
            target=target,
            purpose=purpose,
            modifiers=modifiers,
            constraints=constraints,
            style_preferences=style_preferences,
            data_context=data_context,
        )

    def _extract_action(self, text: str) -> IntentAction:
        """Extract the primary action"""
        for action, pattern in self.action_patterns.items():
            if re.search(pattern, text):
                return action
        return IntentAction.CREATE  # Default action

    def _extract_interface_type(self, text: str) -> InterfaceType | None:
        """Extract the type of interface requested"""
        for interface_type, pattern in self.interface_patterns.items():
            if re.search(pattern, text):
                return interface_type
        return None

    def _extract_target(self, text: str) -> str | None:
        """Extract what the user wants to work with"""
        # Look for "for X", "with Y", "showing Z"
        patterns = [
            r"for\s+(\w+(?:\s+\w+)*)",
            r"with\s+(\w+(?:\s+\w+)*)",
            r"showing\s+(\w+(?:\s+\w+)*)",
            r"to\s+(?:monitor|track|display)\s+(\w+(?:\s+\w+)*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _extract_purpose(self, text: str) -> str | None:
        """Extract the purpose or goal"""
        purpose_patterns = [
            r"to\s+(\w+(?:\s+\w+)*)",
            r"for\s+(\w+ing(?:\s+\w+)*)",
            r"that\s+(\w+s?\s+\w+(?:\s+\w+)*)",
        ]

        for pattern in purpose_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _extract_modifiers(self, text: str) -> list[str]:
        """Extract descriptive modifiers"""
        modifiers = []

        modifier_words = [
            "simple",
            "complex",
            "fast",
            "slow",
            "easy",
            "difficult",
            "large",
            "small",
            "responsive",
            "static",
            "dynamic",
            "real-time",
            "cached",
            "live",
            "interactive",
        ]

        for word in modifier_words:
            if word in text:
                modifiers.append(word)

        return modifiers

    def _extract_styles(self, text: str) -> list[str]:
        """Extract style preferences"""
        styles = []

        for style_category, keywords in self.style_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    styles.append(style_category)
                    break

        return list(set(styles))  # Remove duplicates

    def _extract_constraints(self, text: str) -> list[str]:
        """Extract any constraints or limitations"""
        constraints = []

        if "without" in text or "no " in text or "don't" in text:
            # Extract what should be excluded
            exclusion_patterns = [
                r"without\s+(\w+(?:\s+\w+)*)",
                r"no\s+(\w+(?:\s+\w+)*)",
                r"don't\s+(?:want|need|include)\s+(\w+(?:\s+\w+)*)",
            ]

            for pattern in exclusion_patterns:
                match = re.search(pattern, text)
                if match:
                    constraints.append(f"exclude_{match.group(1).replace(' ', '_')}")

        if "only" in text or "just" in text:
            # Extract what should be limited to
            limitation_patterns = [
                r"only\s+(\w+(?:\s+\w+)*)",
                r"just\s+(\w+(?:\s+\w+)*)",
            ]

            for pattern in limitation_patterns:
                match = re.search(pattern, text)
                if match:
                    constraints.append(f"only_{match.group(1).replace(' ', '_')}")

        return constraints

    def _extract_data_context(self, text: str) -> str | None:
        """Extract data context if mentioned"""
        data_keywords = [
            "data",
            "metrics",
            "statistics",
            "numbers",
            "information",
            "content",
            "text",
            "images",
            "files",
            "documents",
        ]

        for keyword in data_keywords:
            if keyword in text:
                # Try to find what kind of data
                pattern = rf"(\w+\s+)?{keyword}"
                match = re.search(pattern, text)
                if match:
                    return match.group(0)

        return None


class InterfaceComposer:
    """Compose interfaces from parsed intent and components"""

    def __init__(self):
        self.layout_templates = {
            InterfaceType.DASHBOARD: self._dashboard_layout,
            InterfaceType.FORM: self._form_layout,
            InterfaceType.LIST: self._list_layout,
            InterfaceType.EDITOR: self._editor_layout,
            InterfaceType.VIEWER: self._viewer_layout,
            InterfaceType.MONITOR: self._monitor_layout,
            InterfaceType.WORKSPACE: self._workspace_layout,
            InterfaceType.WIDGET: self._widget_layout,
        }

    def compose(
        self,
        components: list[SynthesizedComponent],
        intent: ParsedIntent,
        context: UserContext,
    ) -> InterfaceSpecification:
        """Compose a complete interface from components and intent"""

        # Select layout template
        layout = self._select_layout(intent, context)

        # Generate theme
        theme = self._generate_theme(intent, context)

        # Define interactions
        interactions = self._define_interactions(intent, components)

        # Create data bindings
        data_bindings = self._create_data_bindings(intent, components)

        return InterfaceSpecification(
            components=components,
            layout=layout,
            theme=theme,
            interactions=interactions,
            data_bindings=data_bindings,
            metadata={
                "created_at": datetime.now().isoformat(),
                "intent": intent.__dict__,
                "context": context.__dict__ if context else {},
            },
        )

    def _select_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Select and configure layout based on intent"""

        if intent.interface_type and intent.interface_type in self.layout_templates:
            return self.layout_templates[intent.interface_type](intent, context)

        # Default layout
        return self._default_layout(intent, context)

    def _dashboard_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Dashboard layout configuration"""
        return {
            "type": "grid",
            "columns": 3 if context.device_type == "desktop" else 1,
            "rows": "auto",
            "gap": "16px",
            "areas": [
                {"name": "header", "span": 3},
                {"name": "main", "span": 2},
                {"name": "sidebar", "span": 1},
            ],
        }

    def _form_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Form layout configuration"""
        return {
            "type": "vertical",
            "spacing": "normal",
            "sections": [{"name": "fields", "flex": 1}, {"name": "actions", "flex": 0}],
        }

    def _list_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """List layout configuration"""
        return {
            "type": "vertical",
            "scrollable": True,
            "virtualized": len(intent.modifiers) > 0 and "large" in intent.modifiers,
        }

    def _editor_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Editor layout configuration"""
        return {
            "type": "split",
            "orientation": "vertical",
            "panels": [
                {"name": "toolbar", "size": "48px"},
                {"name": "content", "size": "1fr"},
                {"name": "status", "size": "24px"},
            ],
        }

    def _viewer_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Viewer layout configuration"""
        return {"type": "centered", "maxWidth": "800px", "padding": "24px"}

    def _monitor_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Monitor layout configuration"""
        return {
            "type": "grid",
            "columns": 2,
            "rows": 2,
            "autoRefresh": True,
            "refreshInterval": 5000,
        }

    def _workspace_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Workspace layout configuration"""
        return {
            "type": "dockable",
            "panels": ["left", "center", "right", "bottom"],
            "resizable": True,
        }

    def _widget_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Widget layout configuration"""
        return {"type": "compact", "standalone": True, "draggable": True}

    def _default_layout(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Default layout when type is not specified"""
        return {
            "type": "flex",
            "direction": "column",
            "alignItems": "stretch",
            "justifyContent": "flex-start",
        }

    def _generate_theme(
        self, intent: ParsedIntent, context: UserContext
    ) -> dict[str, Any]:
        """Generate theme based on preferences"""

        theme = {
            "mode": "light",
            "primary": "#007bff",
            "secondary": "#6c757d",
            "background": "#ffffff",
            "text": "#212529",
            "border": "#dee2e6",
            "borderRadius": "8px",
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
            },
            "typography": {
                "fontFamily": "system-ui, -apple-system, sans-serif",
                "fontSize": {
                    "base": "16px",
                    "small": "14px",
                    "large": "18px",
                    "title": "24px",
                },
            },
        }

        # Apply style preferences
        if "dark" in intent.style_preferences:
            theme["mode"] = "dark"
            theme["background"] = "#1a1a1a"
            theme["text"] = "#ffffff"
            theme["border"] = "#333333"

        if "minimal" in intent.style_preferences:
            theme["borderRadius"] = "0"
            theme["primary"] = "#000000"

        if "playful" in intent.style_preferences:
            theme["primary"] = "#ff6b6b"
            theme["borderRadius"] = "16px"

        return theme

    def _define_interactions(
        self, intent: ParsedIntent, components: list[SynthesizedComponent]
    ) -> dict[str, Any]:
        """Define interactions between components"""

        interactions = {"navigation": {}, "dataFlow": {}, "events": {}}

        # Set up navigation if multiple components
        if len(components) > 1:
            interactions["navigation"] = {
                "type": "sequential"
                if "form" in str(intent.interface_type)
                else "free",
                "keyboard": True,
                "touch": context.device_type in ["mobile", "tablet"]
                if hasattr(self, "context")
                else False,
            }

        # Define data flow
        if intent.data_context:
            interactions["dataFlow"] = {
                "source": intent.data_context,
                "updateStrategy": "realtime"
                if "real-time" in intent.modifiers
                else "onDemand",
            }

        return interactions

    def _create_data_bindings(
        self, intent: ParsedIntent, components: list[SynthesizedComponent]
    ) -> dict[str, Any]:
        """Create data bindings for components"""

        bindings = {}

        for component in components:
            if component.dna.data_bindings.get("sources"):
                bindings[component.id] = {
                    "source": component.dna.data_bindings["sources"][0]
                    if component.dna.data_bindings["sources"]
                    else "default",
                    "transform": component.dna.data_bindings.get("transformations", []),
                    "updateFrequency": component.dna.data_bindings.get(
                        "update_frequency", 1000
                    ),
                }

        return bindings


class NLInterfaceBuilder:
    """Main interface builder that orchestrates the entire process"""

    def __init__(self):
        self.parser = NaturalLanguageParser()
        self.synthesizer = ComponentSynthesizer()
        self.composer = InterfaceComposer()
        self.learning_history = []

    def build_interface(
        self, request: str, context: UserContext | None = None
    ) -> InterfaceSpecification:
        """Build a complete interface from natural language request"""

        # Parse the request
        intent = self.parser.parse(request, context)

        # Generate component requirements
        requirements_list = self._generate_requirements(intent, context)

        # Synthesize components
        components = []
        for req in requirements_list:
            component = self.synthesizer.synthesize(req)
            components.append(component)

        # Compose interface
        interface = self.composer.compose(
            components, intent, context or self._default_context()
        )

        # Learn from this interaction
        self._learn_pattern(request, intent, interface)

        return interface

    def _generate_requirements(
        self, intent: ParsedIntent, context: UserContext | None
    ) -> list[ComponentRequirements]:
        """Generate component requirements from intent"""

        requirements_list = []

        # Determine number and types of components needed
        if intent.interface_type == InterfaceType.DASHBOARD:
            # Dashboard needs multiple components
            requirements_list.extend(
                [
                    ComponentRequirements(
                        functionality="display metrics",
                        data_type="chart",
                        visual_style=intent.style_preferences[0]
                        if intent.style_preferences
                        else "auto",
                    ),
                    ComponentRequirements(
                        functionality="show summary",
                        data_type="text",
                        visual_style=intent.style_preferences[0]
                        if intent.style_preferences
                        else "auto",
                    ),
                    ComponentRequirements(
                        functionality="display status",
                        data_type="indicator",
                        visual_style=intent.style_preferences[0]
                        if intent.style_preferences
                        else "auto",
                    ),
                ]
            )

        elif intent.interface_type == InterfaceType.FORM:
            requirements_list.append(
                ComponentRequirements(
                    functionality="collect input",
                    interactions=["input", "submit"],
                    visual_style=intent.style_preferences[0]
                    if intent.style_preferences
                    else "auto",
                )
            )

        elif intent.interface_type == InterfaceType.LIST:
            requirements_list.append(
                ComponentRequirements(
                    functionality="display items",
                    data_type="list",
                    interactions=["click", "hover"],
                    visual_style=intent.style_preferences[0]
                    if intent.style_preferences
                    else "auto",
                )
            )

        else:
            # Default single component
            requirements_list.append(
                ComponentRequirements(
                    functionality=intent.target or "general display",
                    visual_style=intent.style_preferences[0]
                    if intent.style_preferences
                    else "auto",
                    user_expertise=context.expertise_level
                    if context
                    else "intermediate",
                )
            )

        return requirements_list

    def _default_context(self) -> UserContext:
        """Create default user context"""
        return UserContext(
            user_id="default", expertise_level="intermediate", device_type="desktop"
        )

    def _learn_pattern(
        self, request: str, intent: ParsedIntent, interface: InterfaceSpecification
    ):
        """Learn from this interaction for future improvements"""

        self.learning_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "request": request,
                "intent": intent.__dict__,
                "interface_id": id(interface),
                "component_count": len(interface.components),
            }
        )

        # TODO: Implement actual learning logic
        # - Track successful patterns
        # - Learn user preferences
        # - Optimize component selection


# Example usage
if __name__ == "__main__":
    builder = NLInterfaceBuilder()

    # Example requests
    requests = [
        "Create a dashboard for monitoring my server with a dark theme",
        "I need a simple form to collect user feedback",
        "Show me a list of tasks in a fun, playful way",
        "Build a zen writing environment with no distractions",
        "Make a real-time monitor for system metrics",
    ]

    for request in requests:
        print(f"\n{'='*60}")
        print(f"Request: {request}")
        print(f"{'='*60}")

        # Create context
        context = UserContext(
            user_id="demo_user", expertise_level="intermediate", device_type="desktop"
        )

        # Build interface
        interface = builder.build_interface(request, context)

        # Display results
        print(f"Generated {len(interface.components)} components")
        print(f"Layout type: {interface.layout.get('type')}")
        print(f"Theme mode: {interface.theme.get('mode')}")

        for i, component in enumerate(interface.components):
            print(f"\nComponent {i+1}: {component.name}")
            print(f"  Purpose: {component.dna.purpose}")
            print(f"  Style: {component.dna.visual_traits}")
