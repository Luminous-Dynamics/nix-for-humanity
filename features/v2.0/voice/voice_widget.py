#!/usr/bin/env python3
"""
Voice Visualization Widget for Nix for Humanity TUI

Shows real-time voice interface state with visual feedback.
"""

import time
from typing import Optional
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.columns import Columns
from rich.progress_bar import ProgressBar
from rich.console import Group

# Try to import voice interface
try:
    from nix_humanity.interfaces.voice_interface import VoiceState
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    # Define stub
    class VoiceState:
        IDLE = "idle"
        LISTENING = "listening"
        PROCESSING = "processing"
        SPEAKING = "speaking"
        ERROR = "error"


class VoiceVisualizationWidget(Static):
    """
    Enhanced voice visualization showing:
    - Current voice state
    - Audio waveform visualization
    - Transcription display
    - Wake word detection indicator
    """
    
    voice_state = reactive(VoiceState.IDLE)
    transcription = reactive("")
    is_active = reactive(False)
    audio_level = reactive(0.0)
    
    def __init__(self):
        super().__init__()
        self.frame = 0
        self.wake_word_detected = False
        self.last_transcription = ""
        self.error_message = ""
        
    def on_mount(self):
        """Start animation timer"""
        self.set_interval(0.1, self.animate)
        
    def animate(self):
        """Update animation frame"""
        self.frame += 1
        self.refresh()
        
    def set_voice_state(self, state: VoiceState):
        """Update voice state"""
        self.voice_state = state
        if state == VoiceState.ERROR:
            self.error_message = "Voice error - check microphone"
        else:
            self.error_message = ""
        self.refresh()
        
    def set_transcription(self, text: str):
        """Update transcription display"""
        self.transcription = text
        self.last_transcription = text
        self.refresh()
        
    def set_audio_level(self, level: float):
        """Update audio level (0.0 to 1.0)"""
        self.audio_level = max(0.0, min(1.0, level))
        self.refresh()
        
    def set_active(self, active: bool):
        """Set voice interface active state"""
        self.is_active = active
        if not active:
            self.voice_state = VoiceState.IDLE
            self.audio_level = 0.0
        self.refresh()
        
    def render(self):
        """Render the voice visualization"""
        if not self.is_active:
            return Panel(
                Align.center(
                    Text("🎤 Voice Inactive\nPress Ctrl+V to enable", 
                         style="dim", justify="center"),
                    vertical="middle"
                ),
                title="Voice Interface",
                border_style="dim"
            )
        
        # Create state indicator
        state_emoji = {
            VoiceState.IDLE: "😴",
            VoiceState.LISTENING: "👂",
            VoiceState.PROCESSING: "🤔",
            VoiceState.SPEAKING: "🗣️",
            VoiceState.ERROR: "❌"
        }
        
        emoji = state_emoji.get(self.voice_state, "❓")
        state_text = f"{emoji} {self.voice_state.value.capitalize()}"
        
        # Create audio visualization
        audio_viz = self._create_audio_visualization()
        
        # Create transcription display
        if self.voice_state == VoiceState.LISTENING:
            trans_text = "Listening..." if not self.transcription else f'"{self.transcription}"'
            trans_style = "yellow"
        elif self.voice_state == VoiceState.PROCESSING:
            trans_text = f'Processing: "{self.last_transcription}"'
            trans_style = "blue"
        elif self.voice_state == VoiceState.SPEAKING:
            trans_text = "Speaking response..."
            trans_style = "green"
        elif self.error_message:
            trans_text = self.error_message
            trans_style = "red"
        else:
            trans_text = 'Say "Hey Nix" to activate'
            trans_style = "dim"
        
        # Create wake word indicator
        if self.voice_state == VoiceState.IDLE:
            wake_indicator = self._create_wake_indicator()
        else:
            wake_indicator = ""
        
        # Combine all elements
        content = Group(
            Align.center(Text(state_text, style="bold cyan")),
            Text(""),
            audio_viz,
            Text(""),
            Align.center(Text(trans_text, style=trans_style)),
            Text(""),
            wake_indicator
        )
        
        # Return panel with appropriate styling
        border_style = {
            VoiceState.IDLE: "dim",
            VoiceState.LISTENING: "yellow",
            VoiceState.PROCESSING: "blue",
            VoiceState.SPEAKING: "green",
            VoiceState.ERROR: "red"
        }.get(self.voice_state, "white")
        
        return Panel(
            Align.center(content, vertical="middle"),
            title="🎤 Voice Interface",
            border_style=border_style,
            height=12
        )
    
    def _create_audio_visualization(self) -> Align:
        """Create audio level visualization"""
        if self.voice_state not in [VoiceState.LISTENING, VoiceState.SPEAKING]:
            # No audio viz when not active
            return Align.center(Text("─" * 30, style="dim"))
        
        # Create waveform based on audio level and animation frame
        width = 30
        center = width // 2
        
        # Generate waveform characters
        wave_chars = []
        for i in range(width):
            # Calculate wave height based on position and audio level
            distance_from_center = abs(i - center) / center
            base_height = 1.0 - distance_from_center
            
            # Add animation
            phase = (i + self.frame) * 0.3
            animated_height = base_height * (0.5 + 0.5 * abs(time.sin(phase)))
            
            # Scale by audio level
            height = animated_height * self.audio_level * 5
            
            # Choose character based on height
            if height < 0.2:
                char = "─"
            elif height < 0.5:
                char = "▁"
            elif height < 1.0:
                char = "▂"
            elif height < 1.5:
                char = "▃"
            elif height < 2.0:
                char = "▄"
            elif height < 2.5:
                char = "▅"
            elif height < 3.0:
                char = "▆"
            elif height < 3.5:
                char = "▇"
            else:
                char = "█"
            
            wave_chars.append(char)
        
        # Color based on state
        if self.voice_state == VoiceState.LISTENING:
            style = "yellow"
        elif self.voice_state == VoiceState.SPEAKING:
            style = "green"
        else:
            style = "cyan"
        
        return Align.center(Text("".join(wave_chars), style=style))
    
    def _create_wake_indicator(self) -> Align:
        """Create wake word detection indicator"""
        # Animated dots
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        dot = dots[self.frame % len(dots)]
        
        return Align.center(
            Text(f"{dot} Waiting for 'Hey Nix' {dot}", style="dim cyan")
        )


class SimpleVoiceWidget(Static):
    """Simple voice status widget for basic mode"""
    
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.state = VoiceState.IDLE
        
    def set_active(self, active: bool):
        """Toggle voice active state"""
        self.is_active = active
        self.refresh()
        
    def set_voice_state(self, state: VoiceState):
        """Update voice state"""
        self.state = state
        self.refresh()
        
    def render(self):
        """Render simple voice status"""
        if not self.is_active:
            return Text("🎤 Voice: OFF (Ctrl+V to enable)", style="dim")
        
        state_text = {
            VoiceState.IDLE: "Ready",
            VoiceState.LISTENING: "Listening...",
            VoiceState.PROCESSING: "Processing...",
            VoiceState.SPEAKING: "Speaking...",
            VoiceState.ERROR: "Error"
        }.get(self.state, "Unknown")
        
        state_style = {
            VoiceState.IDLE: "green",
            VoiceState.LISTENING: "yellow",
            VoiceState.PROCESSING: "blue",
            VoiceState.SPEAKING: "cyan",
            VoiceState.ERROR: "red"
        }.get(self.state, "white")
        
        return Text(f"🎤 Voice: {state_text}", style=state_style)


# Helper function for easy import
def create_voice_widget(enhanced: bool = False):
    """Create appropriate voice widget based on mode"""
    if enhanced and VOICE_AVAILABLE:
        return VoiceVisualizationWidget()
    else:
        return SimpleVoiceWidget()