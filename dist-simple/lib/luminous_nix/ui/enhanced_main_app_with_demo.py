"""
from typing import Dict, List, Optional
🌟 Enhanced Nix for Humanity TUI with Demo Mode

Includes automated demo capability for creating videos and GIFs.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Static, Button, Label, ListView, ListItem
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from textual import events
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.console import RenderableType
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import random
import math
import time

from .enhanced_consciousness_orb import EnhancedConsciousnessOrb, AIState, EmotionalState
from .visual_state_controller import VisualStateController, ComplexityLevel
from .demo_mode import DemoScript, DemoRecorder, DemoStep
from ..core.engine import NixForHumanityBackend


class EnhancedNixForHumanityTUIWithDemo(App):
    """
    Enhanced TUI with built-in demo mode for creating promotional materials.
    
    Features:
    - All enhanced visualizations
    - Demo recording and playback
    - Automated showcase mode
    - Export demos as scripts
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
    
    #demo-banner {
        background: $warning;
        color: $text;
        padding: 1;
        text-align: center;
        display: none;
    }
    
    .demo-active #demo-banner {
        display: block;
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
        Binding("f5", "start_demo", "Demo Mode"),
        Binding("f6", "record_demo", "Record"),
        Binding("f7", "stop_demo", "Stop Demo"),
    ]
    
    # App state
    complexity_level = reactive(ComplexityLevel.BALANCED)
    zen_mode = reactive(False)
    debug_mode = reactive(False)
    voice_mode = reactive(False)
    demo_mode = reactive(False)
    recording_mode = reactive(False)
    
    def __init__(self, engine: Optional[NixForHumanityBackend] = None):
        super().__init__()
        self.engine = engine or NixForHumanityBackend()
        self.visual_controller = VisualStateController()
        self.command_history: List[Dict[str, Any]] = []
        self.current_query = ""
        
        # Demo systems
        self.demo_script = DemoScript(self)
        self.demo_recorder = DemoRecorder()
        self.demo_task: Optional[asyncio.Task] = None
        
        # Simulated states for demo
        self.network_connected = True
        self.network_latency = 20.0
        self.learning_progress = 0.1
        self.voice_amplitude = 0.0
        
    def compose(self) -> ComposeResult:
        """Create the enhanced UI layout with demo banner"""
        yield Header(show_clock=True)
        
        # Demo mode banner
        with Container(id="demo-banner"):
            yield Label("🎬 DEMO MODE ACTIVE - Press F7 to stop", id="demo-status")
        
        with Container(id="main-container"):
            # Left panel - Main interaction
            with Vertical(id="left-panel"):
                # Enhanced consciousness orb
                with Container(id="orb-container"):
                    self.orb = EnhancedConsciousnessOrb()
                    yield self.orb
                
                # Status display
                with Container(id="status-container"):
                    yield Label("🌐 Network: Connected", id="network-status", classes="status-label")
                    yield Label("🎤 Voice: Inactive", id="voice-status", classes="status-label")
                    yield Label("🧠 Learning: 10% Complete", id="learning-status", classes="status-label")
                    yield Label("🌊 Flow State: Building...", id="flow-status", classes="status-label")
                
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
                
                # Demo controls
                yield Label("🎬 Demo Controls", classes="status-label")
                yield Button("▶️ Run Demo", id="btn-demo", variant="success")
                yield Button("⏺️ Record Demo", id="btn-record", variant="warning")
        
        # Input at bottom
        with Container(id="input-container"):
            self.input = Input(
                placeholder="Ask me anything about NixOS... (try 'install firefox' or 'help')",
                id="command-input"
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
        self.add_to_history({
            "type": "system",
            "message": "🌟 Welcome to Nix for Humanity! I'm here to help you with NixOS in natural language.",
            "timestamp": datetime.now()
        })
        
        # Check if we should auto-start demo
        import sys
        if "--demo" in sys.argv:
            await self.action_start_demo()
            
    async def action_start_demo(self) -> None:
        """Start the automated demo"""
        if self.demo_mode:
            return
            
        self.demo_mode = True
        self.add_class("demo-active")
        
        # Load showcase script
        self.demo_script.load_showcase_script()
        
        # Clear history for clean demo
        self.command_history.clear()
        self.history_view.clear()
        
        # Start demo playback
        self.demo_task = asyncio.create_task(
            self.demo_script.play(on_complete=self._demo_complete)
        )
        
        self.notify("🎬 Demo mode started!", severity="information")
        
    def action_record_demo(self) -> None:
        """Start recording user actions"""
        if self.recording_mode:
            return
            
        self.recording_mode = True
        self.demo_recorder.start_recording()
        
        # Update banner
        demo_banner = self.query_one("#demo-banner")
        demo_status = self.query_one("#demo-status", Label)
        demo_status.update("⏺️ RECORDING DEMO - Press F7 to stop")
        demo_banner.styles.background = "red"
        self.add_class("demo-active")
        
        self.notify("⏺️ Recording started!", severity="warning")
        
    def action_stop_demo(self) -> None:
        """Stop demo or recording"""
        if self.demo_mode:
            self.demo_mode = False
            if self.demo_task:
                self.demo_task.cancel()
            self.demo_script.stop()
            self.notify("🛑 Demo stopped", severity="information")
            
        if self.recording_mode:
            self.recording_mode = False
            recorded_steps = self.demo_recorder.stop_recording()
            
            # Save the recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"demo_recording_{timestamp}.py"
            self.demo_recorder.export_script(filename)
            
            self.notify(f"💾 Recording saved to {filename}", severity="success")
            
        self.remove_class("demo-active")
        
    def _demo_complete(self) -> None:
        """Called when demo playback completes"""
        self.demo_mode = False
        self.remove_class("demo-active")
        self.notify("✅ Demo complete!", severity="success")
        
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission with demo recording"""
        query = event.value.strip()
        if not query:
            return
            
        # Record action if recording
        if self.recording_mode:
            self.demo_recorder.record_action("type", query, "User command")
            self.demo_recorder.record_action("key", "enter", "Submit command")
            
        # Clear input
        self.input.value = ""
        self.current_query = query
        
        # Rest of the processing...
        await self._process_command(query)
        
    async def _process_command(self, query: str) -> None:
        """Process command (extracted for demo compatibility)"""
        # Add to history
        self.add_to_history({
            "type": "user",
            "message": query,
            "timestamp": datetime.now()
        })
        
        # Update orb state
        self.orb.set_state(AIState.LISTENING, EmotionalState.ATTENTIVE)
        await asyncio.sleep(0.5)
        
        self.orb.set_state(AIState.THINKING, EmotionalState.THINKING)
        
        # Process with backend
        try:
            # For demo mode, use faster response times
            if self.demo_mode:
                await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            response = await self.process_query(query)
            
            # Update orb based on response
            if response.get("success"):
                self.orb.set_state(AIState.IDLE, EmotionalState.HAPPY)
            else:
                self.orb.set_state(AIState.ERROR, EmotionalState.CONCERNED)
                
            # Add response to history
            self.add_to_history({
                "type": "assistant",
                "message": response.get("message", "I processed your request."),
                "success": response.get("success", True),
                "timestamp": datetime.now()
            })
            
            # Special states
            if "learn" in query.lower() or "teach" in query.lower():
                self.orb.set_state(AIState.LEARNING, EmotionalState.LEARNING)
            elif "voice" in query.lower() and "on" in query.lower():
                self.voice_mode = True
                
        except Exception as e:
            self.orb.set_state(AIState.ERROR, EmotionalState.CONFUSED)
            self.add_to_history({
                "type": "error",
                "message": f"Error: {str(e)}",
                "timestamp": datetime.now()
            })
            
    async def on_key(self, event: events.Key) -> None:
        """Record key presses when in recording mode"""
        if self.recording_mode and event.key not in ["f6", "f7"]:
            self.demo_recorder.record_action("key", str(event.key), "Key press")
        await super().on_key(event)
        
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses including demo controls"""
        button_id = event.button.id
        
        if button_id == "btn-demo":
            await self.action_start_demo()
        elif button_id == "btn-record":
            self.action_record_demo()
        else:
            # Record button press if recording
            if self.recording_mode:
                self.demo_recorder.record_action("button", button_id, f"Click {event.button.label}")
                
            # Handle other buttons
            await super().on_button_pressed(event)
            
    # Include all other methods from enhanced_main_app.py
    # (update_voice_visualization, update_network_status, etc.)
    # Not repeating them here for brevity, but they would be included
    
    async def update_voice_visualization(self) -> None:
        """Update voice activity visualization"""
        if self.voice_mode:
            # For demo mode, create more interesting patterns
            if self.demo_mode:
                self.voice_amplitude = abs(math.sin(time.time() * 3) * 0.8)
            else:
                self.voice_amplitude = abs(random.gauss(0.5, 0.3))
                
            self.orb.set_voice_activity(True, self.voice_amplitude)
            
            voice_label = self.query_one("#voice-status", Label)
            voice_label.update(f"🎤 Voice: Active ({self.voice_amplitude:.0%} amplitude)")
        else:
            self.orb.set_voice_activity(False)
            voice_label = self.query_one("#voice-status", Label)
            voice_label.update("🎤 Voice: Inactive")
            
    # ... rest of the methods from enhanced_main_app.py ...


if __name__ == "__main__":
    import sys
    app = EnhancedNixForHumanityTUIWithDemo()
    app.run()