"""
🎨 Voice-TUI Integration for Luminous Nix
Adds voice capabilities to the beautiful Textual UI
"""

import asyncio
import logging
from typing import Optional, Callable
from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Label, ProgressBar
from textual.reactive import reactive
from textual import events
from textual.message import Message

from .sacred_voice_interface import SacredVoiceInterface, VoiceConfig, FlowState
from .voice_nlp_bridge import VoiceNLPBridge
from ..core.backend import LuminousNixBackend

logger = logging.getLogger(__name__)


class VoiceStatusWidget(Static):
    """Widget showing voice interface status"""
    
    flow_state = reactive(FlowState.IDLE)
    is_listening = reactive(False)
    last_command = reactive("")
    volume_level = reactive(0.0)
    
    def compose(self) -> ComposeResult:
        """Create voice status display"""
        yield Container(
            Label("🎤 Voice", id="voice-label"),
            Static("", id="flow-state"),
            ProgressBar(total=100, id="volume-bar"),
            Static("", id="last-command"),
            id="voice-status"
        )
    
    def on_mount(self) -> None:
        """Initialize widget"""
        self.update_display()
    
    def watch_flow_state(self) -> None:
        """React to flow state changes"""
        self.update_display()
    
    def watch_is_listening(self) -> None:
        """React to listening state changes"""
        self.update_display()
    
    def update_display(self) -> None:
        """Update the status display"""
        state_widget = self.query_one("#flow-state", Static)
        
        # Flow state indicators
        state_displays = {
            FlowState.IDLE: "⚪ Ready",
            FlowState.LISTENING: "🔴 Listening...",
            FlowState.THINKING: "🤔 Processing...",
            FlowState.SPEAKING: "🗣️ Speaking...",
            FlowState.DEEP_FOCUS: "🧘 Focus Mode",
            FlowState.SACRED_PAUSE: "🕉️ Sacred Pause"
        }
        
        state_widget.update(state_displays.get(self.flow_state, "Unknown"))
        
        # Update volume bar if listening
        if self.is_listening:
            volume_bar = self.query_one("#volume-bar", ProgressBar)
            volume_bar.update(progress=int(self.volume_level * 100))
        
        # Show last command
        if self.last_command:
            cmd_widget = self.query_one("#last-command", Static)
            cmd_widget.update(f"Last: {self.last_command[:30]}...")


class VoiceControlPanel(Container):
    """Panel with voice controls"""
    
    def compose(self) -> ComposeResult:
        """Create control panel"""
        yield Container(
            Label("Voice Controls", classes="panel-title"),
            Horizontal(
                Button("🎤 Start", id="voice-start", variant="success"),
                Button("⏸️ Pause", id="voice-pause", variant="warning"),
                Button("🛑 Stop", id="voice-stop", variant="error"),
                classes="button-row"
            ),
            Horizontal(
                Button("🔊", id="volume-up"),
                Button("🔉", id="volume-down"),
                Button("⚡", id="speed-up"),
                Button("🐌", id="speed-down"),
                classes="button-row"
            ),
            Horizontal(
                Button("🧘 Focus", id="focus-mode"),
                Button("💬 Normal", id="normal-mode"),
                Button("🕉️ Breath", id="sacred-breath"),
                classes="button-row"
            ),
            id="voice-controls"
        )


class VoiceHistoryWidget(Container):
    """Widget showing voice interaction history"""
    
    def __init__(self, max_history: int = 10):
        super().__init__()
        self.history = []
        self.max_history = max_history
    
    def compose(self) -> ComposeResult:
        """Create history display"""
        yield Container(
            Label("Voice History", classes="panel-title"),
            Container(id="history-list"),
            id="voice-history"
        )
    
    def add_interaction(self, command: str, response: str, success: bool = True):
        """Add an interaction to history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.history.append({
            'time': timestamp,
            'command': command,
            'response': response,
            'success': success
        })
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        self.update_display()
    
    def update_display(self):
        """Update the history display"""
        history_list = self.query_one("#history-list", Container)
        history_list.remove_children()
        
        for item in reversed(self.history):  # Show newest first
            status = "✓" if item['success'] else "✗"
            entry = Static(
                f"[{item['time']}] {status} {item['command'][:30]}...",
                classes="history-entry"
            )
            history_list.mount(entry)


class VoiceTUIIntegration:
    """
    Integration layer for adding voice to TUI
    
    Features:
    - Voice status widget
    - Control panel for voice settings
    - History of voice interactions
    - Real-time volume visualization
    - Flow state indicators
    """
    
    def __init__(self, app, backend: Optional[LuminousNixBackend] = None):
        self.app = app
        self.backend = backend or LuminousNixBackend()
        self.bridge = None
        self.voice_thread = None
        
        # Widgets
        self.status_widget = None
        self.control_panel = None
        self.history_widget = None
        
        # Configuration
        self.config = VoiceConfig(
            voice_personality="gentle",
            use_acknowledgments=True,
            focus_protection=True
        )
    
    def create_widgets(self) -> tuple:
        """Create voice UI widgets"""
        self.status_widget = VoiceStatusWidget()
        self.control_panel = VoiceControlPanel()
        self.history_widget = VoiceHistoryWidget()
        
        return (self.status_widget, self.control_panel, self.history_widget)
    
    def setup_voice_bridge(self):
        """Initialize voice bridge"""
        self.bridge = VoiceNLPBridge(self.backend, self.config)
        
        # Set up callbacks
        self.bridge.voice.on_state_change = self.handle_state_change
        self.bridge.voice.on_command = self.process_command_with_ui
    
    def handle_state_change(self, state: FlowState):
        """Handle voice state changes"""
        if self.status_widget:
            self.status_widget.flow_state = state
            
            # Update listening indicator
            self.status_widget.is_listening = (state == FlowState.LISTENING)
    
    def process_command_with_ui(self, text: str) -> str:
        """Process command and update UI"""
        try:
            # Update status
            if self.status_widget:
                self.status_widget.last_command = text
            
            # Process through bridge
            response = self.bridge.process_voice_command(text)
            
            # Add to history
            if self.history_widget:
                self.history_widget.add_interaction(
                    text, response, 
                    success=self.bridge.context.error_count == 0
                )
            
            # Update main app if needed
            if hasattr(self.app, 'handle_voice_command'):
                self.app.handle_voice_command(text, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return f"Error: {str(e)}"
    
    def start_voice(self):
        """Start voice interface"""
        if not self.bridge:
            self.setup_voice_bridge()
        
        self.bridge.start()
        logger.info("Voice interface started in TUI")
    
    def stop_voice(self):
        """Stop voice interface"""
        if self.bridge:
            self.bridge.stop()
        logger.info("Voice interface stopped in TUI")
    
    def pause_voice(self):
        """Pause voice interface"""
        if self.bridge:
            self.bridge.voice.enter_deep_focus()
    
    def resume_voice(self):
        """Resume voice interface"""
        if self.bridge:
            self.bridge.voice.exit_deep_focus()
    
    def adjust_volume(self, delta: float):
        """Adjust voice volume"""
        if self.bridge:
            new_volume = self.bridge.voice.config.voice_volume + delta
            new_volume = max(0.1, min(1.0, new_volume))
            self.bridge.voice.config.voice_volume = new_volume
            
            if self.bridge.voice.speaker:
                self.bridge.voice.speaker.setProperty('volume', new_volume)
    
    def adjust_speed(self, delta: int):
        """Adjust speech rate"""
        if self.bridge:
            new_rate = self.bridge.voice.config.voice_rate + delta
            new_rate = max(100, min(300, new_rate))
            self.bridge.voice.config.voice_rate = new_rate
            
            if self.bridge.voice.speaker:
                self.bridge.voice.speaker.setProperty('rate', new_rate)
    
    def take_sacred_breath(self):
        """Trigger sacred breath"""
        if self.bridge:
            self.bridge.voice.take_sacred_breath()
    
    def bind_controls(self):
        """Bind control panel buttons to actions"""
        if not self.control_panel:
            return
        
        # Bind buttons to methods
        controls = {
            "#voice-start": self.start_voice,
            "#voice-pause": self.pause_voice,
            "#voice-stop": self.stop_voice,
            "#volume-up": lambda: self.adjust_volume(0.1),
            "#volume-down": lambda: self.adjust_volume(-0.1),
            "#speed-up": lambda: self.adjust_speed(25),
            "#speed-down": lambda: self.adjust_speed(-25),
            "#focus-mode": self.pause_voice,
            "#normal-mode": self.resume_voice,
            "#sacred-breath": self.take_sacred_breath,
        }
        
        for selector, handler in controls.items():
            button = self.control_panel.query_one(selector)
            if button:
                button.action = handler


def integrate_voice_with_tui(app):
    """
    Add voice capabilities to existing TUI app
    
    Usage:
        from luminous_nix.ui.main_app import LuminousNixTUI
        from luminous_nix.voice.voice_tui_integration import integrate_voice_with_tui
        
        app = LuminousNixTUI()
        voice = integrate_voice_with_tui(app)
        
        # In app.compose():
        status, controls, history = voice.create_widgets()
        yield status
        yield controls  
        yield history
        
        # In app.on_mount():
        voice.bind_controls()
    """
    return VoiceTUIIntegration(app)


# Styling for voice widgets
VOICE_TUI_CSS = """
#voice-status {
    height: 5;
    border: solid $primary;
    padding: 1;
}

#voice-controls {
    border: solid $secondary;
    padding: 1;
}

#voice-history {
    border: solid $accent;
    padding: 1;
    max-height: 15;
}

.button-row {
    height: 3;
    align: center middle;
}

.history-entry {
    margin: 0 1;
}

.panel-title {
    text-style: bold;
    color: $primary;
}

#volume-bar {
    width: 100%;
    height: 1;
}
"""