"""
🌉 Synthesis Bridge - Connects Component Synthesis to Real UI
Translates synthesized components into actual Textual/Tauri widgets
"""

import asyncio
from collections.abc import Callable
from datetime import datetime
from typing import Any

# Textual imports for TUI
try:
    from rich.panel import Panel
    from rich.text import Text
    from textual.app import App
    from textual.containers import (
        Container,
        Grid,
        Horizontal,
        ScrollableContainer,
        Vertical,
    )
    from textual.reactive import reactive
    from textual.widgets import Button, DataTable, Input, Label, Static, TextArea, Tree

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    print("Warning: Textual not available, TUI features disabled")

try:
    from .component_synthesis_engine import ComponentDNA, SynthesizedComponent
    from .nl_interface_builder import InterfaceSpecification
except ImportError:
    from component_synthesis_engine import SynthesizedComponent
    from nl_interface_builder import InterfaceSpecification


class ComponentRegistry:
    """Registry of component translators"""

    def __init__(self):
        self.translators = {}
        self.widget_cache = {}
        self._register_default_translators()

    def register(self, component_type: str, translator: Callable):
        """Register a translator for a component type"""
        self.translators[component_type] = translator

    def translate(self, component: SynthesizedComponent) -> Any:
        """Translate a synthesized component to a real widget"""

        # Check cache
        if component.id in self.widget_cache:
            return self.widget_cache[component.id]

        # Find appropriate translator
        translator = self._find_translator(component)
        if translator:
            widget = translator(component)
            self.widget_cache[component.id] = widget
            return widget

        # Fallback to generic translation
        return self._generic_translator(component)

    def _find_translator(self, component: SynthesizedComponent) -> Callable | None:
        """Find the best translator for a component"""

        # Try exact match on purpose
        purpose = component.dna.purpose.lower()
        for key in self.translators:
            if key in purpose:
                return self.translators[key]

        return None

    def _register_default_translators(self):
        """Register default component translators"""

        if TEXTUAL_AVAILABLE:
            self.register("display", self._translate_display)
            self.register("input", self._translate_input)
            self.register("button", self._translate_button)
            self.register("list", self._translate_list)
            self.register("chart", self._translate_chart)
            self.register("form", self._translate_form)
            self.register("metrics", self._translate_metrics)

    def _generic_translator(self, component: SynthesizedComponent) -> Any:
        """Generic translator for unknown component types"""
        if not TEXTUAL_AVAILABLE:
            return None

        # Create a generic container with the component's content
        content = Panel(
            Text(f"{component.name}\n{component.dna.purpose}"),
            title=component.name,
            border_style="blue",
        )

        return Static(content, id=component.id)

    def _translate_display(self, component: SynthesizedComponent) -> Any:
        """Translate display components"""
        if not TEXTUAL_AVAILABLE:
            return None

        style = self._extract_textual_style(component)

        return Static(
            Panel(Text("Display Content", justify="center"), title=component.name),
            id=component.id,
            classes=style.get("classes", ""),
        )

    def _translate_input(self, component: SynthesizedComponent) -> Any:
        """Translate input components"""
        if not TEXTUAL_AVAILABLE:
            return None

        placeholder = "Enter value..."
        if component.structure and isinstance(component.structure, dict):
            props = component.structure.get("props", {})
            placeholder = props.get("placeholder", placeholder)

        return Input(placeholder=placeholder, id=component.id)

    def _translate_button(self, component: SynthesizedComponent) -> Any:
        """Translate button components"""
        if not TEXTUAL_AVAILABLE:
            return None

        label = "Action"
        if component.structure and isinstance(component.structure, dict):
            children = component.structure.get("children", "Action")
            if isinstance(children, str):
                label = children

        return Button(
            label=label,
            id=component.id,
            variant="primary"
            if component.dna.visual_traits.get("emphasis") == "bold"
            else "default",
        )

    def _translate_list(self, component: SynthesizedComponent) -> Any:
        """Translate list components"""
        if not TEXTUAL_AVAILABLE:
            return None

        # Create a tree widget for lists
        tree = Tree("Items", id=component.id)

        # Add sample items (would be populated from data)
        for i in range(5):
            tree.root.add_leaf(f"Item {i+1}")

        return tree

    def _translate_chart(self, component: SynthesizedComponent) -> Any:
        """Translate chart components"""
        if not TEXTUAL_AVAILABLE:
            return None

        # For now, create a placeholder for charts
        # In real implementation, would use plotext or similar
        return Static(
            Panel(
                Text(
                    "📊 Chart Visualization\n[Data would appear here]", justify="center"
                ),
                title="Metrics Chart",
            ),
            id=component.id,
        )

    def _translate_form(self, component: SynthesizedComponent) -> Any:
        """Translate form components"""
        if not TEXTUAL_AVAILABLE:
            return None

        # Create a vertical container with form fields
        container = Vertical(id=component.id)

        # Add typical form fields
        container.mount(Label("Form Field 1:"))
        container.mount(Input(placeholder="Enter value"))
        container.mount(Label("Form Field 2:"))
        container.mount(Input(placeholder="Enter value"))
        container.mount(Button("Submit", variant="primary"))

        return container

    def _translate_metrics(self, component: SynthesizedComponent) -> Any:
        """Translate metrics components"""
        if not TEXTUAL_AVAILABLE:
            return None

        # Create a data table for metrics
        table = DataTable(id=component.id)
        table.add_columns("Metric", "Value", "Status")
        table.add_rows(
            [
                ["CPU Usage", "45%", "✅"],
                ["Memory", "2.3GB", "✅"],
                ["Disk", "67%", "⚠️"],
                ["Network", "1.2Mbps", "✅"],
            ]
        )

        return table

    def _extract_textual_style(self, component: SynthesizedComponent) -> dict[str, Any]:
        """Extract Textual-compatible styles from component"""

        textual_style = {}

        if component.styles:
            # Map CSS-like styles to Textual classes
            if "backgroundColor" in component.styles:
                bg = component.styles["backgroundColor"]
                if bg == "#1a1a1a":
                    textual_style["classes"] = "dark"
                elif bg == "#ffffff":
                    textual_style["classes"] = "light"

        return textual_style


class LayoutTranslator:
    """Translates layout specifications to Textual containers"""

    def translate(self, layout: dict[str, Any], widgets: list[Any]) -> Any:
        """Translate a layout specification to Textual container"""

        if not TEXTUAL_AVAILABLE:
            return None

        layout_type = layout.get("type", "vertical")

        if layout_type == "grid":
            return self._create_grid(layout, widgets)
        if layout_type == "horizontal":
            return self._create_horizontal(layout, widgets)
        if layout_type == "vertical":
            return self._create_vertical(layout, widgets)
        if layout_type == "split":
            return self._create_split(layout, widgets)
        # Default to vertical
        return self._create_vertical(layout, widgets)

    def _create_grid(self, layout: dict[str, Any], widgets: list[Any]) -> Any:
        """Create a grid container"""

        container = Grid(id="synthesized-grid")

        # Add widgets to grid
        for widget in widgets:
            if widget:
                container.mount(widget)

        return container

    def _create_horizontal(self, layout: dict[str, Any], widgets: list[Any]) -> Any:
        """Create a horizontal container"""

        container = Horizontal(id="synthesized-horizontal")

        for widget in widgets:
            if widget:
                container.mount(widget)

        return container

    def _create_vertical(self, layout: dict[str, Any], widgets: list[Any]) -> Any:
        """Create a vertical container"""

        container = Vertical(id="synthesized-vertical")

        for widget in widgets:
            if widget:
                container.mount(widget)

        return container

    def _create_split(self, layout: dict[str, Any], widgets: list[Any]) -> Any:
        """Create a split panel container"""

        # For split layouts, create nested containers
        main_container = Vertical(id="synthesized-split")

        panels = layout.get("panels", [])
        widget_idx = 0

        for panel in panels:
            if widget_idx < len(widgets) and widgets[widget_idx]:
                panel_container = Container(id=f"panel-{panel.get('name', widget_idx)}")
                panel_container.mount(widgets[widget_idx])
                main_container.mount(panel_container)
                widget_idx += 1

        return main_container


class SynthesisBridge:
    """Main bridge between synthesis engine and UI system"""

    def __init__(self):
        self.registry = ComponentRegistry()
        self.layout_translator = LayoutTranslator()
        self.active_interfaces = {}
        self.widget_map = {}

    def render_interface(self, interface: InterfaceSpecification) -> Any:
        """Render a complete interface specification to UI widgets"""

        # Translate all components to widgets
        widgets = []
        for component in interface.components:
            widget = self.registry.translate(component)
            if widget:
                widgets.append(widget)
                self.widget_map[component.id] = widget

        # Apply layout
        container = self.layout_translator.translate(interface.layout, widgets)

        # Store active interface
        interface_id = id(interface)
        self.active_interfaces[interface_id] = {
            "interface": interface,
            "container": container,
            "widgets": widgets,
            "created_at": datetime.now(),
        }

        return container

    def update_component(self, component_id: str, changes: dict[str, Any]):
        """Update a live component"""

        if component_id not in self.widget_map:
            # If not in widget map, it means no actual widget was created (Textual not available)
            # Just return silently for testing purposes
            return

        widget = self.widget_map[component_id]

        # Apply changes based on type
        if "text" in changes and hasattr(widget, "update"):
            widget.update(changes["text"])

        if "style" in changes and hasattr(widget, "styles"):
            # Update widget styles
            for key, value in changes["style"].items():
                setattr(widget.styles, key, value)

        if "visible" in changes and hasattr(widget, "visible"):
            widget.visible = changes["visible"]

    def get_widget_state(self, component_id: str) -> dict[str, Any]:
        """Get current state of a widget"""

        if component_id not in self.widget_map:
            return {}

        widget = self.widget_map[component_id]

        state = {
            "id": component_id,
            "type": type(widget).__name__,
            "visible": getattr(widget, "visible", True),
        }

        # Extract widget-specific state
        if hasattr(widget, "value"):
            state["value"] = widget.value

        if hasattr(widget, "text"):
            state["text"] = str(widget.text)

        return state

    def apply_theme(self, interface_id: int, theme: dict[str, Any]):
        """Apply a theme to an interface"""

        if interface_id not in self.active_interfaces:
            return

        interface_data = self.active_interfaces[interface_id]

        # Apply theme to all widgets
        for widget in interface_data["widgets"]:
            if theme.get("mode") == "dark":
                if hasattr(widget, "styles"):
                    widget.styles.background = "rgb(26, 26, 26)"
                    widget.styles.color = "white"
            elif theme.get("mode") == "light":
                if hasattr(widget, "styles"):
                    widget.styles.background = "white"
                    widget.styles.color = "rgb(0, 0, 0)"

    async def animate_transition(
        self,
        from_interface: InterfaceSpecification,
        to_interface: InterfaceSpecification,
        duration: float = 0.5,
    ):
        """Animate transition between interfaces"""

        # Render new interface
        new_container = self.render_interface(to_interface)

        # TODO: Implement actual animation
        # For now, just swap instantly
        await asyncio.sleep(duration)

        return new_container


class DynamicModificationEngine:
    """Engine for real-time component modifications"""

    def __init__(self, bridge: SynthesisBridge):
        self.bridge = bridge
        self.modification_queue = []
        self.is_modifying = False

    async def modify_component(
        self, component_id: str, modifications: dict[str, Any], animated: bool = True
    ):
        """Modify a component in real-time"""

        # Queue modification
        self.modification_queue.append(
            {
                "component_id": component_id,
                "modifications": modifications,
                "animated": animated,
                "timestamp": datetime.now(),
            }
        )

        # Process queue if not already processing
        if not self.is_modifying:
            await self._process_modifications()

    async def _process_modifications(self):
        """Process queued modifications"""

        self.is_modifying = True

        while self.modification_queue:
            mod = self.modification_queue.pop(0)

            if mod["animated"]:
                # Animate the change
                await self._animate_modification(
                    mod["component_id"], mod["modifications"]
                )
            else:
                # Apply instantly
                self.bridge.update_component(mod["component_id"], mod["modifications"])

        self.is_modifying = False

    async def _animate_modification(
        self, component_id: str, modifications: dict[str, Any]
    ):
        """Animate a modification smoothly"""

        # Get current state
        current_state = self.bridge.get_widget_state(component_id)

        # Calculate interpolation steps
        steps = 10
        duration = 0.3  # seconds
        step_duration = duration / steps

        # Interpolate changes over time
        for i in range(steps):
            progress = (i + 1) / steps
            interpolated = self._interpolate(current_state, modifications, progress)

            self.bridge.update_component(component_id, interpolated)
            await asyncio.sleep(step_duration)

    def _interpolate(
        self, start: dict[str, Any], end: dict[str, Any], progress: float
    ) -> dict[str, Any]:
        """Interpolate between two states"""

        result = {}

        for key in end:
            if key in start and isinstance(start[key], (int, float)):
                # Numeric interpolation
                result[key] = start[key] + (end[key] - start[key]) * progress
            else:
                # Step change at midpoint
                result[key] = end[key] if progress > 0.5 else start.get(key)

        return result


# Example usage
if __name__ == "__main__":
    from .nl_interface_builder import NLInterfaceBuilder, UserContext

    # Create the synthesis bridge
    bridge = SynthesisBridge()

    # Build an interface from natural language
    builder = NLInterfaceBuilder()
    context = UserContext(user_id="demo", expertise_level="intermediate")

    interface = builder.build_interface(
        "Create a simple dashboard with metrics", context
    )

    # Render to actual UI widgets
    ui_container = bridge.render_interface(interface)

    print(f"Rendered interface with {len(interface.components)} components")
    print(f"Container type: {type(ui_container).__name__ if ui_container else 'None'}")

    # Example of dynamic modification
    if interface.components:
        component_id = interface.components[0].id

        # Create modification engine
        modifier = DynamicModificationEngine(bridge)

        # Schedule a modification
        import asyncio

        asyncio.run(
            modifier.modify_component(
                component_id,
                {"text": "Updated content!", "style": {"color": "green"}},
                animated=True,
            )
        )
