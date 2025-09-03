#!/usr/bin/env python3
"""
🎮 Dynamic Interface Demonstration
Interactive demo where users can create interfaces through natural language
"""

import asyncio
from datetime import datetime

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Static

from .nl_interface_builder import NLInterfaceBuilder, UserContext
from .synthesis_bridge import DynamicModificationEngine, SynthesisBridge


class DynamicInterfaceDemo(App):
    """Interactive demonstration of dynamic interface generation"""

    CSS = """
    #input-area {
        height: 3;
        margin: 1;
        border: solid $primary;
    }
    
    #generated-area {
        min-height: 20;
        margin: 1;
        border: dashed $secondary;
    }
    
    #info-panel {
        dock: right;
        width: 40;
        margin: 1;
        border: solid $accent;
    }
    
    .example-button {
        margin: 0 1;
    }
    
    #feedback-area {
        height: 5;
        margin: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+r", "reset", "Reset"),
        Binding("ctrl+h", "help", "Help"),
        Binding("ctrl+e", "examples", "Examples"),
    ]

    def __init__(self):
        super().__init__()
        self.builder = NLInterfaceBuilder()
        self.bridge = SynthesisBridge()
        self.modifier = DynamicModificationEngine(self.bridge)
        self.current_interface = None
        self.history = []

        # User context
        self.user_context = UserContext(
            user_id="demo_user", expertise_level="intermediate", device_type="desktop"
        )

    def compose(self) -> ComposeResult:
        """Create the demo interface"""

        yield Header()

        with Container():
            # Main area
            with Vertical(id="main-area"):
                # Title
                yield Static(
                    Panel(
                        Align.center(
                            Text("✨ Dynamic Interface Generator ✨", style="bold cyan"),
                            vertical="middle",
                        ),
                        title="AI-Powered Interface Creation",
                        border_style="cyan",
                    )
                )

                # Input area
                with Horizontal(id="input-section"):
                    yield Label("Request: ")
                    yield Input(
                        placeholder="Describe the interface you want (e.g., 'Create a dashboard for monitoring tasks')",
                        id="request-input",
                    )
                    yield Button("Generate", variant="primary", id="generate-btn")

                # Example buttons
                with Horizontal(id="examples-section"):
                    yield Button(
                        "Dashboard", classes="example-button", id="ex-dashboard"
                    )
                    yield Button("Form", classes="example-button", id="ex-form")
                    yield Button("List", classes="example-button", id="ex-list")
                    yield Button("Zen Editor", classes="example-button", id="ex-zen")

                # Generated interface area
                yield Static(
                    Panel(
                        Text("Generated interface will appear here...", style="dim"),
                        title="Generated Interface",
                        border_style="green",
                    ),
                    id="generated-area",
                )

                # Feedback area
                with Horizontal(id="feedback-section"):
                    yield Label("Feedback: ")
                    yield Button("👍 Good", id="feedback-good")
                    yield Button("😐 OK", id="feedback-ok")
                    yield Button("👎 Needs Work", id="feedback-bad")
                    yield Button("🔄 Evolve", id="evolve-btn")

            # Info panel
            with ScrollableContainer(id="info-panel"):
                yield Static(
                    Panel(
                        self._get_info_content(),
                        title="Information",
                        border_style="blue",
                    ),
                    id="info-content",
                )

        yield Footer()

    def _get_info_content(self) -> Text:
        """Get content for info panel"""

        text = Text()
        text.append("Current Interface\n", style="bold")

        if self.current_interface:
            text.append(f"Components: {len(self.current_interface.components)}\n")
            text.append(
                f"Layout: {self.current_interface.layout.get('type', 'unknown')}\n"
            )
            text.append(
                f"Theme: {self.current_interface.theme.get('mode', 'default')}\n\n"
            )

            text.append("Components:\n", style="bold")
            for comp in self.current_interface.components:
                text.append(f"  • {comp.name}\n", style="cyan")
                text.append(f"    Purpose: {comp.dna.purpose}\n", style="dim")
        else:
            text.append("No interface generated yet\n", style="dim")

        text.append("\n")
        text.append("History\n", style="bold")
        text.append(f"Requests made: {len(self.history)}\n", style="dim")

        return text

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""

        if event.button.id == "generate-btn":
            await self._generate_interface()

        elif event.button.id == "evolve-btn":
            await self._evolve_interface()

        elif event.button.id.startswith("ex-"):
            # Example buttons
            examples = {
                "ex-dashboard": "Create a dashboard for monitoring server metrics with dark theme",
                "ex-form": "Build a simple form to collect user feedback",
                "ex-list": "Show me a list of tasks in a fun, playful way",
                "ex-zen": "Create a zen writing environment with no distractions",
            }

            if event.button.id in examples:
                input_widget = self.query_one("#request-input", Input)
                input_widget.value = examples[event.button.id]
                await self._generate_interface()

        elif event.button.id.startswith("feedback-"):
            await self._handle_feedback(event.button.id)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        await self._generate_interface()

    async def _generate_interface(self) -> None:
        """Generate interface from input"""

        input_widget = self.query_one("#request-input", Input)
        request = input_widget.value.strip()

        if not request:
            return

        # Update status
        generated_area = self.query_one("#generated-area", Static)
        generated_area.update(
            Panel(
                Text("🔄 Generating interface...", style="yellow"),
                title="Generating",
                border_style="yellow",
            )
        )

        # Generate interface
        try:
            interface = self.builder.build_interface(request, self.user_context)
            self.current_interface = interface

            # Render to widgets
            container = self.bridge.render_interface(interface)

            # Display results
            if container:
                # Mount the generated widgets
                generated_area.update(container)
            else:
                # Show specification if widgets not available
                result_text = Text()
                result_text.append("✅ Interface Generated!\n\n", style="bold green")
                result_text.append(f"Components: {len(interface.components)}\n")
                result_text.append(
                    f"Layout: {interface.layout.get('type', 'unknown')}\n"
                )
                result_text.append(
                    f"Theme: {interface.theme.get('mode', 'default')}\n\n"
                )

                for i, comp in enumerate(interface.components):
                    result_text.append(f"Component {i+1}: {comp.name}\n", style="cyan")
                    result_text.append(f"  Purpose: {comp.dna.purpose}\n")
                    result_text.append(f"  Visual: {comp.dna.visual_traits}\n")
                    result_text.append(f"  Behavior: {comp.dna.behaviors}\n\n")

                generated_area.update(
                    Panel(
                        result_text, title="Generated Interface", border_style="green"
                    )
                )

            # Update info panel
            self._update_info_panel()

            # Add to history
            self.history.append(
                {
                    "request": request,
                    "interface": interface,
                    "timestamp": datetime.now(),
                }
            )

        except Exception as e:
            generated_area.update(
                Panel(
                    Text(f"❌ Error: {str(e)}", style="red"),
                    title="Error",
                    border_style="red",
                )
            )

    async def _evolve_interface(self) -> None:
        """Evolve the current interface"""

        if not self.current_interface or not self.current_interface.components:
            return

        generated_area = self.query_one("#generated-area", Static)
        generated_area.update(
            Panel(
                Text("🧬 Evolving interface...", style="magenta"),
                title="Evolving",
                border_style="magenta",
            )
        )

        # Simulate evolution
        await asyncio.sleep(1)

        # For demo, just modify the first component
        component = self.current_interface.components[0]

        # Evolve it
        evolved = self.builder.synthesizer.evolve_component(
            component.id, {"satisfaction": 0.6}  # Simulate medium satisfaction
        )

        # Update display
        result_text = Text()
        result_text.append("🧬 Interface Evolved!\n\n", style="bold magenta")
        result_text.append("Changes:\n", style="bold")
        result_text.append("  • Visual traits mutated\n")
        result_text.append("  • Behaviors adapted\n")
        result_text.append("  • Learning applied\n\n")
        result_text.append(f"New DNA:\n{evolved.dna.to_json()}\n", style="dim")

        generated_area.update(
            Panel(result_text, title="Evolved Interface", border_style="magenta")
        )

    async def _handle_feedback(self, feedback_id: str) -> None:
        """Handle user feedback"""

        if not self.current_interface:
            return

        feedback_map = {
            "feedback-good": {"satisfaction": 0.9, "label": "👍 Good"},
            "feedback-ok": {"satisfaction": 0.6, "label": "😐 OK"},
            "feedback-bad": {"satisfaction": 0.3, "label": "👎 Needs Work"},
        }

        if feedback_id in feedback_map:
            feedback = feedback_map[feedback_id]

            # Store feedback (would be used for learning)
            self.history[-1]["feedback"] = feedback

            # Show confirmation
            info_panel = self.query_one("#info-content", Static)
            text = self._get_info_content()
            text.append(f"\n✅ Feedback recorded: {feedback['label']}", style="green")

            info_panel.update(Panel(text, title="Information", border_style="blue"))

    def _update_info_panel(self) -> None:
        """Update the info panel"""

        info_panel = self.query_one("#info-content", Static)
        info_panel.update(
            Panel(self._get_info_content(), title="Information", border_style="blue")
        )

    def action_reset(self) -> None:
        """Reset the interface"""

        self.current_interface = None
        self.history.clear()

        generated_area = self.query_one("#generated-area", Static)
        generated_area.update(
            Panel(
                Text("Generated interface will appear here...", style="dim"),
                title="Generated Interface",
                border_style="green",
            )
        )

        self._update_info_panel()

    def action_help(self) -> None:
        """Show help"""

        help_text = Text()
        help_text.append("How to Use:\n", style="bold")
        help_text.append(
            "1. Type a natural language description of the interface you want\n"
        )
        help_text.append("2. Press Enter or click Generate\n")
        help_text.append("3. View the generated interface\n")
        help_text.append("4. Provide feedback to help the system learn\n")
        help_text.append("5. Click Evolve to see the interface adapt\n\n")

        help_text.append("Example Requests:\n", style="bold")
        help_text.append("• Create a dashboard for monitoring tasks\n", style="cyan")
        help_text.append("• Build a simple form with dark theme\n", style="cyan")
        help_text.append("• Show me a zen writing environment\n", style="cyan")
        help_text.append("• Make a fun, colorful list of items\n", style="cyan")

        generated_area = self.query_one("#generated-area", Static)
        generated_area.update(Panel(help_text, title="Help", border_style="yellow"))


def run_demo():
    """Run the demonstration"""
    app = DynamicInterfaceDemo()
    app.run()


if __name__ == "__main__":
    run_demo()
