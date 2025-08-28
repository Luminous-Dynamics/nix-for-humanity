"""
🧬 Component Synthesis Engine
Generates new UI components dynamically from requirements
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# Component DNA - The genetic blueprint of a component
@dataclass
class ComponentDNA:
    """Genetic information that defines a component's characteristics"""

    # Identity
    purpose: str
    capabilities: list[str] = field(default_factory=list)

    # Visual characteristics
    visual_traits: dict[str, str] = field(
        default_factory=lambda: {
            "size": "normal",  # compact, normal, expansive
            "density": "balanced",  # sparse, balanced, dense
            "emphasis": "moderate",  # subtle, moderate, bold
            "style": "modern",  # minimal, modern, playful, serious
        }
    )

    # Behavioral patterns
    behaviors: dict[str, str] = field(
        default_factory=lambda: {
            "interactivity": "reactive",  # static, reactive, proactive
            "feedback": "informative",  # minimal, informative, rich
            "animation": "subtle",  # none, subtle, expressive
            "intelligence": "passive",  # passive, suggestive, predictive
        }
    )

    # Data connections
    data_bindings: dict[str, Any] = field(
        default_factory=lambda: {
            "sources": [],
            "transformations": [],
            "update_frequency": 1000,  # milliseconds
        }
    )

    # Evolution capabilities
    evolution: dict[str, Any] = field(
        default_factory=lambda: {
            "mutability": "adaptive",  # static, adaptive, evolutionary
            "learning_speed": 0.1,
            "generation_lifespan": 7,  # days before re-evaluation
        }
    )

    def to_json(self) -> str:
        """Serialize DNA to JSON"""
        return json.dumps(
            {
                "purpose": self.purpose,
                "capabilities": self.capabilities,
                "visual_traits": self.visual_traits,
                "behaviors": self.behaviors,
                "data_bindings": self.data_bindings,
                "evolution": self.evolution,
            }
        )

    def mutate(self, mutation_rate: float = 0.1) -> "ComponentDNA":
        """Create a mutated version of this DNA"""
        import random

        mutated = ComponentDNA(
            purpose=self.purpose,
            capabilities=self.capabilities.copy(),
            visual_traits=self.visual_traits.copy(),
            behaviors=self.behaviors.copy(),
            data_bindings=self.data_bindings.copy(),
            evolution=self.evolution.copy(),
        )

        # Randomly mutate some traits
        if random.random() < mutation_rate:
            trait_type = random.choice(["visual_traits", "behaviors"])
            traits = getattr(mutated, trait_type)
            if traits:
                key = random.choice(list(traits.keys()))
                # Mutate to a related value (simplified for now)
                traits[key] = self._mutate_value(traits[key])

        return mutated

    def _mutate_value(self, value: str) -> str:
        """Mutate a value to a related one"""
        mutations = {
            "normal": ["compact", "expansive"],
            "balanced": ["sparse", "dense"],
            "moderate": ["subtle", "bold"],
            "reactive": ["static", "proactive"],
            "informative": ["minimal", "rich"],
            "subtle": ["none", "expressive"],
        }

        if value in mutations:
            import random

            return random.choice(mutations[value])
        return value


@dataclass
class ComponentRequirements:
    """Requirements for synthesizing a new component"""

    # Functional requirements
    functionality: str  # What the component should do
    data_type: str | None = None  # Type of data to display/handle
    interactions: list[str] = field(default_factory=list)  # Required interactions

    # Non-functional requirements
    performance: str = "normal"  # low, normal, high
    accessibility: str = "standard"  # basic, standard, comprehensive
    responsiveness: str = "adaptive"  # fixed, fluid, adaptive

    # Aesthetic preferences
    visual_style: str = "auto"  # auto, minimal, rich, playful
    color_scheme: str = "auto"  # auto, light, dark, high-contrast
    animation_level: str = "auto"  # auto, none, subtle, rich

    # Context
    user_expertise: str = "intermediate"  # beginner, intermediate, expert
    device_type: str = "desktop"  # mobile, tablet, desktop, universal
    use_case: str = "general"  # general, focused, monitoring, creative


@dataclass
class SynthesizedComponent:
    """A dynamically synthesized component"""

    id: str
    name: str
    dna: ComponentDNA
    structure: dict[str, Any]  # Component structure (HTML/JSX equivalent)
    styles: dict[str, Any]  # CSS styles
    behaviors: dict[str, Any]  # Event handlers and interactions
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_react_component(self) -> str:
        """Generate React component code"""
        return f"""
import React from 'react';

const {self.name} = (props) => {{
    return (
        <div className="{self.id}" style={{{json.dumps(self.styles)}}}>
            {json.dumps(self.structure, indent=2)}
        </div>
    );
}};

export default {self.name};
"""

    def to_web_component(self) -> str:
        """Generate Web Component code"""
        return f"""
class {self.name} extends HTMLElement {{
    constructor() {{
        super();
        this.attachShadow({{ mode: 'open' }});
        this.render();
    }}
    
    render() {{
        this.shadowRoot.innerHTML = `
            <style>
                {self._styles_to_css()}
            </style>
            {self._structure_to_html()}
        `;
    }}
}}

customElements.define('{self.id}', {self.name});
"""

    def _styles_to_css(self) -> str:
        """Convert styles dict to CSS"""
        css = []
        for selector, rules in self.styles.items():
            rule_strings = [f"{prop}: {value}" for prop, value in rules.items()]
            css.append(f"{selector} {{ {'; '.join(rule_strings)} }}")
        return "\n".join(css)

    def _structure_to_html(self) -> str:
        """Convert structure to HTML"""
        # Simplified HTML generation
        return f"<div>{json.dumps(self.structure)}</div>"


class ComponentSynthesizer:
    """Main synthesis engine for creating components"""

    def __init__(self):
        self.component_library = {}  # Store of synthesized components
        self.dna_pool = []  # Pool of successful DNA patterns
        self.synthesis_history = []  # Track what we've created

    def synthesize(self, requirements: ComponentRequirements) -> SynthesizedComponent:
        """Synthesize a new component from requirements"""

        # Step 1: Generate component DNA
        dna = self._generate_dna(requirements)

        # Step 2: Select base primitives
        primitives = self._select_primitives(dna, requirements)

        # Step 3: Compose structure
        structure = self._compose_structure(primitives, dna)

        # Step 4: Generate styles
        styles = self._generate_styles(dna, requirements)

        # Step 5: Attach behaviors
        behaviors = self._attach_behaviors(dna, requirements)

        # Step 6: Create component
        component = SynthesizedComponent(
            id=self._generate_id(requirements),
            name=self._generate_name(requirements),
            dna=dna,
            structure=structure,
            styles=styles,
            behaviors=behaviors,
            metadata={
                "created_at": datetime.now().isoformat(),
                "requirements": requirements.__dict__,
                "version": "1.0.0",
            },
        )

        # Store in library
        self.component_library[component.id] = component
        self.synthesis_history.append(component.id)

        # Add successful DNA to pool for future use
        self.dna_pool.append(dna)

        return component

    def _generate_dna(self, requirements: ComponentRequirements) -> ComponentDNA:
        """Generate DNA from requirements"""

        # Map requirements to DNA traits
        visual_traits = {
            "size": "compact" if requirements.device_type == "mobile" else "normal",
            "density": "sparse"
            if requirements.user_expertise == "beginner"
            else "balanced",
            "emphasis": "bold"
            if requirements.visual_style == "playful"
            else "moderate",
            "style": requirements.visual_style
            if requirements.visual_style != "auto"
            else "modern",
        }

        behaviors = {
            "interactivity": "proactive"
            if requirements.user_expertise == "beginner"
            else "reactive",
            "feedback": "rich"
            if requirements.accessibility == "comprehensive"
            else "informative",
            "animation": requirements.animation_level
            if requirements.animation_level != "auto"
            else "subtle",
            "intelligence": "predictive"
            if requirements.use_case == "monitoring"
            else "passive",
        }

        return ComponentDNA(
            purpose=requirements.functionality,
            capabilities=requirements.interactions,
            visual_traits=visual_traits,
            behaviors=behaviors,
        )

    def _select_primitives(
        self, dna: ComponentDNA, requirements: ComponentRequirements
    ) -> list[str]:
        """Select primitive components to combine"""

        primitives = []

        # Select based on functionality
        if "display" in requirements.functionality.lower():
            primitives.append("container")
            primitives.append("text")

        if "input" in requirements.functionality.lower():
            primitives.append("input")
            primitives.append("label")

        if "button" in requirements.interactions:
            primitives.append("button")

        if "list" in requirements.functionality.lower():
            primitives.append("list")
            primitives.append("list-item")

        if requirements.data_type:
            if "chart" in requirements.data_type.lower():
                primitives.append("chart")
            elif "table" in requirements.data_type.lower():
                primitives.append("table")

        # Always include a container
        if "container" not in primitives:
            primitives.append("container")

        return primitives

    def _compose_structure(
        self, primitives: list[str], dna: ComponentDNA
    ) -> dict[str, Any]:
        """Compose component structure from primitives"""

        structure = {
            "type": "div",
            "props": {
                "className": f"synthesized-{dna.purpose.replace(' ', '-').lower()}",
                "role": self._determine_aria_role(dna),
            },
            "children": [],
        }

        # Build structure based on primitives
        for primitive in primitives:
            if primitive == "container":
                continue  # Already the root
            if primitive == "text":
                structure["children"].append(
                    {
                        "type": "span",
                        "props": {"className": "text-content"},
                        "children": "{{content}}",
                    }
                )
            elif primitive == "input":
                structure["children"].append(
                    {
                        "type": "input",
                        "props": {
                            "type": "text",
                            "className": "synthesized-input",
                            "placeholder": "Enter value...",
                        },
                    }
                )
            elif primitive == "button":
                structure["children"].append(
                    {
                        "type": "button",
                        "props": {
                            "className": "synthesized-button",
                            "onClick": "{{handleClick}}",
                        },
                        "children": "Action",
                    }
                )
            elif primitive == "list":
                structure["children"].append(
                    {
                        "type": "ul",
                        "props": {"className": "synthesized-list"},
                        "children": "{{listItems}}",
                    }
                )

        return structure

    def _generate_styles(
        self, dna: ComponentDNA, requirements: ComponentRequirements
    ) -> dict[str, Any]:
        """Generate styles based on DNA and requirements"""

        # Base styles
        styles = {
            ".synthesized-"
            + dna.purpose.replace(" ", "-").lower(): {
                "display": "flex",
                "flexDirection": "column",
                "padding": self._get_spacing(dna.visual_traits["density"]),
                "gap": self._get_gap(dna.visual_traits["density"]),
                "borderRadius": "8px"
                if dna.visual_traits["style"] == "modern"
                else "0",
                "transition": "all 0.3s ease"
                if dna.behaviors["animation"] != "none"
                else "none",
            }
        }

        # Color scheme
        if requirements.color_scheme == "dark":
            styles[".synthesized-" + dna.purpose.replace(" ", "-").lower()].update(
                {"backgroundColor": "#1a1a1a", "color": "#ffffff"}
            )
        elif requirements.color_scheme == "light":
            styles[".synthesized-" + dna.purpose.replace(" ", "-").lower()].update(
                {"backgroundColor": "#ffffff", "color": "#000000"}
            )

        # Responsive styles
        if requirements.responsiveness == "adaptive":
            styles["@media (max-width: 768px)"] = {
                ".synthesized-"
                + dna.purpose.replace(" ", "-").lower(): {
                    "padding": "8px",
                    "fontSize": "14px",
                }
            }

        return styles

    def _attach_behaviors(
        self, dna: ComponentDNA, requirements: ComponentRequirements
    ) -> dict[str, Any]:
        """Attach behaviors and interactions"""

        behaviors = {}

        # Add interactions based on requirements
        for interaction in requirements.interactions:
            if interaction == "click":
                behaviors["onClick"] = "handleClick"
            elif interaction == "hover":
                behaviors["onHover"] = "handleHover"
            elif interaction == "input":
                behaviors["onChange"] = "handleChange"

        # Add intelligence behaviors
        if dna.behaviors["intelligence"] == "predictive":
            behaviors["predictNext"] = True
            behaviors["prefetch"] = True
        elif dna.behaviors["intelligence"] == "suggestive":
            behaviors["showSuggestions"] = True

        # Add animation behaviors
        if dna.behaviors["animation"] != "none":
            behaviors["animate"] = True
            behaviors["animationLevel"] = dna.behaviors["animation"]

        return behaviors

    def _generate_id(self, requirements: ComponentRequirements) -> str:
        """Generate unique component ID"""
        hash_input = f"{requirements.functionality}{datetime.now().isoformat()}"
        return f"comp_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"

    def _generate_name(self, requirements: ComponentRequirements) -> str:
        """Generate component name"""
        words = requirements.functionality.split()
        return "".join(word.capitalize() for word in words) + "Component"

    def _determine_aria_role(self, dna: ComponentDNA) -> str:
        """Determine appropriate ARIA role"""
        purpose_lower = dna.purpose.lower()

        if "button" in purpose_lower:
            return "button"
        if "navigation" in purpose_lower:
            return "navigation"
        if "list" in purpose_lower:
            return "list"
        if "form" in purpose_lower or "input" in purpose_lower:
            return "form"
        return "region"

    def _get_spacing(self, density: str) -> str:
        """Get spacing based on density"""
        spacing_map = {"sparse": "24px", "balanced": "16px", "dense": "8px"}
        return spacing_map.get(density, "16px")

    def _get_gap(self, density: str) -> str:
        """Get gap based on density"""
        gap_map = {"sparse": "16px", "balanced": "12px", "dense": "4px"}
        return gap_map.get(density, "12px")

    def evolve_component(
        self, component_id: str, feedback: dict[str, Any]
    ) -> SynthesizedComponent:
        """Evolve an existing component based on feedback"""

        if component_id not in self.component_library:
            raise ValueError(f"Component {component_id} not found")

        component = self.component_library[component_id]

        # Mutate DNA based on feedback
        mutation_rate = 0.1 if feedback.get("satisfaction", 0.5) < 0.7 else 0.05
        new_dna = component.dna.mutate(mutation_rate)

        # Re-synthesize with new DNA
        evolved = SynthesizedComponent(
            id=component_id + "_evolved",
            name=component.name + "Evolved",
            dna=new_dna,
            structure=component.structure,  # Keep structure for now
            styles=self._generate_styles(
                new_dna, ComponentRequirements(functionality=new_dna.purpose)
            ),
            behaviors=component.behaviors,
            metadata={
                **component.metadata,
                "evolved_from": component_id,
                "evolution_date": datetime.now().isoformat(),
            },
        )

        self.component_library[evolved.id] = evolved
        return evolved


# Example usage and testing
if __name__ == "__main__":
    # Create synthesizer
    synthesizer = ComponentSynthesizer()

    # Define requirements for a dashboard widget
    requirements = ComponentRequirements(
        functionality="display real-time metrics",
        data_type="chart",
        interactions=["hover", "click"],
        performance="high",
        visual_style="modern",
        color_scheme="dark",
        animation_level="subtle",
        user_expertise="intermediate",
        device_type="desktop",
        use_case="monitoring",
    )

    # Synthesize component
    component = synthesizer.synthesize(requirements)

    print(f"Synthesized: {component.name}")
    print(f"DNA: {component.dna.to_json()}")
    print(f"\nReact Component:\n{component.to_react_component()}")

    # Evolve based on feedback
    evolved = synthesizer.evolve_component(
        component.id, {"satisfaction": 0.6, "issues": ["too_complex"]}
    )
    print(f"\nEvolved to: {evolved.name}")
