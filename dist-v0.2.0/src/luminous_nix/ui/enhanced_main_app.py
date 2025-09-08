"""
from typing import List, Dict, Optional
🌟 Enhanced Luminous Nix TUI Application

Features:
- Enhanced consciousness orb with voice, network, and learning visualizations
- Real-time status monitoring
- configurable interface complexity
- Beautiful animations and transitions
"""

import asyncio
import random
from datetime import datetime
from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from ..core.engine import LuminousNixBackend
from .enhanced_consciousness_orb import (
    AIState,
    EmotionalState,
    EnhancedConsciousnessOrb,
)
from .visual_state_controller import ComplexityLevel, VisualStateController


class StatusUpdate(Message):
    """Message for status updates"""

    def __init__(self, status: dict[str, Any]) -> None:
        super().__init__()
        self.status = status


class EnhancedLuminousNixTUI(App):
    """
    The enhanced beautiful, consciousness-first TUI for Luminous Nix.

    Features:
    - Living consciousness orb with advanced visualizations
    - Voice activity monitoring
    - Network status display
    - Learning progress tracking
    - Adaptive complexity based on user flow
    - Natural language input
    - Real-time command execution
    - Sacred pause awareness
    """

    CSS = """
    #main-container {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 2fr 1fr;
        grid-rows: 1fr;
    }
    
    #left-panel {
        border: solid $primary;
        padding: 1;
        margin: 1;
    }
    
    #right-panel {
        border: solid $secondary;
        padding: 1;
        margin: 1;
    }
    
    #orb-container {
        height: 20;
        border: none;
        align: center middle;
    }
    
    #status-container {
        height: 10;
        border: solid $accent;
        padding: 1;
    }
    
    #input-container {
        height: 3;
        dock: bottom;
        border: solid $primary;
        padding: 0 1;
    }
    
    #history-container {
        border: solid $secondary;
        padding: 1;
        overflow-y: scroll;
    }
    
    Input {
        dock: bottom;
    }
    
    .status-label {
        color: $text-muted;
        text-style: italic;
    }
    
    .command-success {
        color: $success;
    }
    
    .command-error {
        color: $error;
    }
    
    .thinking {
        color: $warning;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+z", "toggle_zen", "Zen Mode"),
        Binding("ctrl+d", "toggle_debug", "Debug Info"),
        Binding("ctrl+v", "toggle_voice", "Voice Mode"),
        Binding("ctrl+l", "clear_history", "Clear"),
        Binding("f1", "help", "Help"),
    ]

    # App state
    complexity_level = reactive(ComplexityLevel.BALANCED)
    zen_mode = reactive(False)
    debug_mode = reactive(False)
    voice_mode = reactive(False)

    def __init__(self, engine: LuminousNixBackend | None = None):
        super().__init__()
        self.engine = engine or LuminousNixBackend()
        self.visual_controller = VisualStateController()
        self.command_history: list[dict[str, Any]] = []
        self.current_query = ""

        # Simulated states for demo
        self.network_connected = True
        self.network_latency = 20.0
        self.learning_progress = 0.1
        self.voice_amplitude = 0.0

    def compose(self) -> ComposeResult:
        """Create the enhanced UI layout"""
        yield Header(show_clock=True)

        with Container(id="main-container"):
            # Left panel - Main interaction
            with Vertical(id="left-panel"):
                # Enhanced consciousness orb
                with Container(id="orb-container"):
                    self.orb = EnhancedConsciousnessOrb()
                    yield self.orb

                # Status display
                with Container(id="status-container"):
                    yield Label(
                        "🌐 Network: Connected",
                        id="network-status",
                        classes="status-label",
                    )
                    yield Label(
                        "🎤 Voice: Inactive", id="voice-status", classes="status-label"
                    )
                    yield Label(
                        "🧠 Learning: 10% Complete",
                        id="learning-status",
                        classes="status-label",
                    )
                    yield Label(
                        "🌊 Flow State: Building...",
                        id="flow-status",
                        classes="status-label",
                    )

                # Command history
                with VerticalScroll(id="history-container"):
                    self.history_view = ListView(id="command-history")
                    yield self.history_view

            # Right panel - Advanced features
            with Vertical(id="right-panel"):
                yield Label("✨ Sacred Metrics", classes="status-label")
                yield Static(id="metrics-display")

                yield Label("🔮 AI Insights", classes="status-label")
                yield Static(id="insights-display")

                yield Label("📊 System Status", classes="status-label")
                yield Static(id="system-display")

                # Quick actions
                yield Label("⚡ Quick Actions", classes="status-label")
                yield Button("🔄 Update System", id="btn-update", variant="primary")
                yield Button("🧹 Clean Cache", id="btn-clean", variant="secondary")
                yield Button("📦 List Packages", id="btn-list", variant="default")

        # Input at bottom
        with Container(id="input-container"):
            self.input = Input(
                placeholder="Ask me anything about NixOS... (try 'install firefox' or 'help')",
                id="command-input",
            )
            yield self.input

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize when app starts"""
        # Focus on input
        self.input.focus()

        # Start consciousness orb
        self.orb.set_state(AIState.IDLE, EmotionalState.NEUTRAL)

        # Start monitoring timers
        self.set_interval(0.1, self.update_voice_visualization)
        self.set_interval(1.0, self.update_network_status)
        self.set_interval(2.0, self.update_learning_progress)
        self.set_interval(5.0, self.update_sacred_metrics)

        # Welcome message
        self.add_to_history(
            {
                "type": "system",
                "message": "🌟 Welcome to Luminous Nix! I'm here to help you with NixOS in natural language.",
                "timestamp": datetime.now(),
            }
        )

    async def update_voice_visualization(self) -> None:
        """Update voice activity visualization"""
        if self.voice_mode:
            # Simulate voice activity
            self.voice_amplitude = abs(random.gauss(0.5, 0.3))
            self.orb.set_voice_activity(True, self.voice_amplitude)

            voice_label = self.query_one("#voice-status", Label)
            voice_label.update(
                f"🎤 Voice: Active ({self.voice_amplitude:.0%} amplitude)"
            )
        else:
            self.orb.set_voice_activity(False)
            voice_label = self.query_one("#voice-status", Label)
            voice_label.update("🎤 Voice: Inactive")

    async def update_network_status(self) -> None:
        """Update network connectivity status"""
        # Simulate network fluctuations
        if random.random() < 0.95:  # 95% uptime
            self.network_connected = True
            self.network_latency = random.uniform(10, 50)
            strength = 0.9 + random.uniform(-0.1, 0.1)
        else:
            self.network_connected = False
            self.network_latency = 999
            strength = 0.0

        self.orb.set_network_status(
            self.network_connected, self.network_latency, strength
        )

        network_label = self.query_one("#network-status", Label)
        if self.network_connected:
            network_label.update(f"🌐 Network: Connected ({self.network_latency:.0f}ms)")
            network_label.styles.color = "green"
        else:
            network_label.update("🌐 Network: Disconnected")
            network_label.styles.color = "red"

    async def update_learning_progress(self) -> None:
        """Update learning system progress"""
        # Simulate learning progress
        if len(self.command_history) > 0:
            self.learning_progress = min(1.0, self.learning_progress + 0.02)
            growth = 0.1 if self.orb.ai_state == AIState.LEARNING else 0.01
        else:
            growth = 0.0

        self.orb.set_learning_progress(self.learning_progress, growth)

        learning_label = self.query_one("#learning-status", Label)
        learning_label.update(f"🧠 Learning: {self.learning_progress:.0%} Complete")

    async def update_sacred_metrics(self) -> None:
        """Update sacred metrics display"""
        metrics = self.query_one("#metrics-display", Static)

        # Calculate flow score based on interaction patterns
        flow_score = min(1.0, len(self.command_history) * 0.1) * self.orb.coherence

        metrics_text = Text()
        metrics_text.append("Flow Score: ", style="bold")
        metrics_text.append(
            f"{flow_score:.0%}\n", style="green" if flow_score > 0.7 else "yellow"
        )

        metrics_text.append("Coherence: ", style="bold")
        metrics_text.append(f"{self.orb.coherence:.0%}\n", style="cyan")

        metrics_text.append("Attention: ", style="bold")
        metrics_text.append(f"{self.orb.attention_level:.0%}\n", style="magenta")

        metrics.update(metrics_text)

        # Update flow status
        flow_label = self.query_one("#flow-status", Label)
        if flow_score > 0.8:
            flow_label.update("🌊 Flow State: Active!")
            flow_label.styles.color = "green"
            if self.orb.ai_state != AIState.FLOW:
                self.orb.enter_flow_state()
        else:
            flow_label.update(f"🌊 Flow State: Building... ({flow_score:.0%})")
            flow_label.styles.color = "yellow"

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission"""
        query = event.value.strip()
        if not query:
            return

        # Clear input
        self.input.value = ""
        self.current_query = query

        # Add to history
        self.add_to_history(
            {"type": "user", "message": query, "timestamp": datetime.now()}
        )

        # Update orb state
        self.orb.set_state(AIState.LISTENING, EmotionalState.ATTENTIVE)
        await asyncio.sleep(0.5)  # Brief listening pause

        self.orb.set_state(AIState.THINKING, EmotionalState.THINKING)

        # Process with backend
        try:
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.5, 2.0))

            response = await self.process_query(query)

            # Update orb based on response
            if response.get("success"):
                self.orb.set_state(AIState.IDLE, EmotionalState.HAPPY)
            else:
                self.orb.set_state(AIState.ERROR, EmotionalState.CONCERNED)

            # Add response to history
            self.add_to_history(
                {
                    "type": "assistant",
                    "message": response.get("message", "I processed your request."),
                    "success": response.get("success", True),
                    "timestamp": datetime.now(),
                }
            )

            # If learning something new
            if "learn" in query.lower() or "teach" in query.lower():
                self.orb.set_state(AIState.LEARNING, EmotionalState.LEARNING)

        except Exception as e:
            self.orb.set_state(AIState.ERROR, EmotionalState.CONFUSED)
            self.add_to_history(
                {
                    "type": "error",
                    "message": f"Error: {str(e)}",
                    "timestamp": datetime.now(),
                }
            )

    async def process_query(self, query: str) -> dict[str, Any]:
        """Process query with enhanced responses"""
        # Simple demo responses
        query_lower = query.lower()

        if "install" in query_lower:
            package = query.split()[-1] if len(query.split()) > 1 else "package"
            return {
                "success": True,
                "message": f"✅ Installing {package}... This would run: nix profile install nixpkgs#{package}",
                "command": f"nix profile install nixpkgs#{package}",
            }
        if "help" in query_lower:
            return {
                "success": True,
                "message": """🌟 I can help you with:
• Installing packages: "install firefox"
• System updates: "update system"
• Package search: "search editor"
• Network issues: "fix wifi"
• Learning together: "teach me about generations"

Try the buttons on the right for quick actions!""",
            }
        if "search" in query_lower:
            term = query.split()[-1] if len(query.split()) > 1 else "packages"
            return {
                "success": True,
                "message": f"🔍 Searching for '{term}'... Found: firefox, firefox-esr, firefox-bin",
            }
        if "update" in query_lower:
            return {
                "success": True,
                "message": "🔄 Updating system... This would run: sudo nixos-rebuild switch",
            }
        if "voice" in query_lower:
            self.voice_mode = True
            return {
                "success": True,
                "message": "🎤 Voice mode activated! I'm listening...",
            }
        return {
            "success": True,
            "message": f"🤔 I understood '{query}'. In a full implementation, I would process this naturally!",
        }

    def add_to_history(self, entry: dict[str, Any]) -> None:
        """Add entry to command history"""
        self.command_history.append(entry)

        # Create list item
        timestamp = entry["timestamp"].strftime("%H:%M:%S")

        if entry["type"] == "user":
            item_text = f"[{timestamp}] You: {entry['message']}"
            style = "bold cyan"
        elif entry["type"] == "assistant":
            icon = "✅" if entry.get("success") else "❌"
            item_text = f"[{timestamp}] {icon} Nix: {entry['message']}"
            style = "green" if entry.get("success") else "red"
        elif entry["type"] == "system":
            item_text = f"[{timestamp}] 🌟 {entry['message']}"
            style = "yellow"
        else:
            item_text = f"[{timestamp}] ⚠️ {entry['message']}"
            style = "red"

        # Add to list view
        list_item = ListItem(Text(item_text, style=style))
        self.history_view.append(list_item)

        # Auto-scroll to bottom
        self.history_view.scroll_end(animate=True)

    def action_toggle_zen(self) -> None:
        """Toggle zen mode"""
        self.zen_mode = not self.zen_mode
        if self.zen_mode:
            self.complexity_level = ComplexityLevel.MINIMAL
            self.query_one("#right-panel").display = False
            self.notify("Zen mode: Enabled 🧘", severity="information")
        else:
            self.complexity_level = ComplexityLevel.BALANCED
            self.query_one("#right-panel").display = True
            self.notify("Zen mode: Disabled", severity="information")

    def action_toggle_debug(self) -> None:
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        self.notify(
            f"Debug mode: {'Enabled' if self.debug_mode else 'Disabled'}",
            severity="information",
        )

    def action_toggle_voice(self) -> None:
        """Toggle voice mode"""
        self.voice_mode = not self.voice_mode
        self.notify(
            f"Voice mode: {'Enabled 🎤' if self.voice_mode else 'Disabled'}",
            severity="information",
        )

    def action_clear_history(self) -> None:
        """Clear command history"""
        self.command_history.clear()
        self.history_view.clear()
        self.add_to_history(
            {
                "type": "system",
                "message": "History cleared. Fresh start! 🌱",
                "timestamp": datetime.now(),
            }
        )

    def action_help(self) -> None:
        """Show help"""
        help_text = """🌟 Luminous Nix - Keyboard Shortcuts:

Ctrl+Z - Toggle Zen Mode (minimal UI)
Ctrl+D - Toggle Debug Info
Ctrl+V - Toggle Voice Mode
Ctrl+L - Clear History
F1     - Show this help
Ctrl+C - Quit

Just type naturally and press Enter!"""
        self.add_to_history(
            {"type": "system", "message": help_text, "timestamp": datetime.now()}
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "btn-update":
            await self.on_input_submitted(Input.Submitted(self.input, "update system"))
        elif button_id == "btn-clean":
            await self.on_input_submitted(Input.Submitted(self.input, "clean cache"))
        elif button_id == "btn-list":
            await self.on_input_submitted(
                Input.Submitted(self.input, "list installed packages")
            )


if __name__ == "__main__":
    app = EnhancedLuminousNixTUI()
    app.run()
