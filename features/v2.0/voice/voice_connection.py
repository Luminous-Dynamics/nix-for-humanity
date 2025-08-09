"""
from typing import Optional
🎤 Voice Connection for Unified Enhanced TUI

Connects the voice interface components to the TUI:
- Wake word detection ("Hey Nix")
- Speech-to-text with Whisper
- Text-to-speech with Piper
- Real-time visualization in TUI
"""

import asyncio
import numpy as np
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import time
import logging
from enum import Enum

# Voice components
from .wake_word_detector import WakeWordDetector
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech

logger = logging.getLogger(__name__)


class VoiceState(Enum):
    """Voice system states"""
    IDLE = "idle"
    LISTENING_FOR_WAKE = "listening_for_wake"
    WAKE_DETECTED = "wake_detected"
    RECORDING = "recording"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class VoiceMetrics:
    """Real-time voice metrics for visualization"""
    amplitude: float = 0.0  # 0.0 to 1.0
    frequency: float = 440.0  # Dominant frequency in Hz
    is_speaking: bool = False
    noise_level: float = 0.0
    clarity: float = 1.0  # Voice clarity score


class VoiceConnection:
    """
    Manages voice interface connection to TUI
    
    Provides:
    - Wake word activation
    - Speech recognition
    - Voice synthesis
    - Real-time metrics for visualization
    """
    
    def __init__(self, 
                 on_text_received: Optional[Callable[[str], None]] = None,
                 on_metrics_update: Optional[Callable[[VoiceMetrics], None]] = None):
        """
        Initialize voice connection
        
        Args:
            on_text_received: Callback when speech is recognized
            on_metrics_update: Callback for real-time voice metrics
        """
        self.on_text_received = on_text_received
        self.on_metrics_update = on_metrics_update
        
        # Voice components
        self.wake_detector = WakeWordDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        
        # State management
        self.state = VoiceState.IDLE
        self.is_active = False
        self.metrics = VoiceMetrics()
        
        # Audio processing
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_buffer = []
        
        # Timing
        self.last_wake_time = 0
        self.wake_timeout = 30.0  # Seconds before returning to wake word mode
        
    async def start(self) -> None:
        """Start voice connection"""
        logger.info("Starting voice connection...")
        self.is_active = True
        
        # Start components
        await self.wake_detector.start()
        await self.stt.start()
        
        # Start processing loops
        asyncio.create_task(self._audio_processing_loop())
        asyncio.create_task(self._metrics_update_loop())
        
        self.state = VoiceState.LISTENING_FOR_WAKE
        logger.info("Voice connection ready - say 'Hey Nix' to activate")
        
    async def stop(self) -> None:
        """Stop voice connection"""
        logger.info("Stopping voice connection...")
        self.is_active = False
        
        await self.wake_detector.stop()
        await self.stt.stop()
        
        self.state = VoiceState.IDLE
        
    async def speak(self, text: str) -> None:
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
        """
        if not self.is_active:
            return
            
        logger.info(f"Speaking: {text}")
        self.state = VoiceState.SPEAKING
        
        # Update metrics for speaking
        self.metrics.is_speaking = True
        self._update_metrics()
        
        try:
            # Generate and play speech
            await self.tts.speak(text)
            
            # Simulate speaking animation
            words = text.split()
            for i, word in enumerate(words):
                # Update amplitude based on word position
                self.metrics.amplitude = 0.3 + (0.4 * abs(np.sin(i * 0.5)))
                self.metrics.frequency = 200 + (100 * np.sin(i * 0.3))
                self._update_metrics()
                
                # Wait based on word length
                await asyncio.sleep(len(word) * 0.08)
                
        finally:
            self.metrics.is_speaking = False
            self.metrics.amplitude = 0.0
            self._update_metrics()
            
            # Return to listening
            self.state = VoiceState.LISTENING_FOR_WAKE
            
    async def _audio_processing_loop(self) -> None:
        """Main audio processing loop"""
        while self.is_active:
            try:
                if self.state == VoiceState.LISTENING_FOR_WAKE:
                    await self._process_wake_word()
                    
                elif self.state == VoiceState.WAKE_DETECTED:
                    await self._process_command()
                    
                elif self.state == VoiceState.RECORDING:
                    await self._process_recording()
                    
                await asyncio.sleep(0.01)  # Small delay
                
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
                self.state = VoiceState.ERROR
                await asyncio.sleep(1.0)
                self.state = VoiceState.LISTENING_FOR_WAKE
                
    async def _process_wake_word(self) -> None:
        """Process audio for wake word detection"""
        # Simulate audio capture (in real implementation, use microphone)
        audio_chunk = self._simulate_audio_chunk()
        
        # Update metrics with ambient noise
        self.metrics.amplitude = np.abs(audio_chunk).mean() * 0.1
        self.metrics.frequency = 100 + (np.random.random() * 50)
        self.metrics.noise_level = 0.1
        
        # Check for wake word
        if self.wake_detector.detect(audio_chunk):
            logger.info("Wake word detected!")
            self.state = VoiceState.WAKE_DETECTED
            self.last_wake_time = time.time()
            
            # Visual feedback
            self.metrics.amplitude = 0.8
            self._update_metrics()
            
            # Play acknowledgment
            await self.speak("Yes?")
            
    async def _process_command(self) -> None:
        """Process voice command after wake word"""
        # Check timeout
        if time.time() - self.last_wake_time > self.wake_timeout:
            logger.info("Wake word timeout, returning to listening")
            self.state = VoiceState.LISTENING_FOR_WAKE
            return
            
        # Start recording
        self.state = VoiceState.RECORDING
        self.audio_buffer = []
        
    async def _process_recording(self) -> None:
        """Process recording of user command"""
        # Simulate recording (in real implementation, use microphone)
        audio_chunk = self._simulate_audio_chunk(speaking=True)
        self.audio_buffer.append(audio_chunk)
        
        # Update metrics for speaking
        self.metrics.amplitude = np.abs(audio_chunk).mean()
        self.metrics.frequency = 200 + (np.random.random() * 300)
        self.metrics.clarity = 0.9
        
        # Simulate end of speech detection
        if len(self.audio_buffer) > 50:  # About 3 seconds
            self.state = VoiceState.PROCESSING
            
            # Process speech
            audio_data = np.concatenate(self.audio_buffer)
            
            # Simulate STT (in real implementation, use Whisper)
            # For demo, use predefined commands
            demo_commands = [
                "install firefox",
                "update my system",
                "list all generations",
                "show disk usage",
                "what's my network status"
            ]
            
            recognized_text = np.random.choice(demo_commands)
            logger.info(f"Recognized: {recognized_text}")
            
            # Send to TUI
            if self.on_text_received:
                self.on_text_received(recognized_text)
                
            # Reset for next command
            self.audio_buffer = []
            self.state = VoiceState.LISTENING_FOR_WAKE
            
    async def _metrics_update_loop(self) -> None:
        """Update metrics at regular intervals"""
        while self.is_active:
            self._update_metrics()
            await asyncio.sleep(0.05)  # 20 Hz update rate
            
    def _update_metrics(self) -> None:
        """Send metrics update to TUI"""
        if self.on_metrics_update:
            self.on_metrics_update(self.metrics)
            
    def _simulate_audio_chunk(self, speaking: bool = False) -> np.ndarray:
        """Simulate audio chunk for demo"""
        if speaking:
            # Simulate speech waveform
            t = np.linspace(0, self.chunk_size / self.sample_rate, self.chunk_size)
            # Mix of frequencies for speech
            signal = (
                0.3 * np.sin(2 * np.pi * 200 * t) +  # Fundamental
                0.2 * np.sin(2 * np.pi * 400 * t) +  # Harmonic
                0.1 * np.sin(2 * np.pi * 800 * t) +  # Harmonic
                0.05 * np.random.randn(self.chunk_size)  # Noise
            )
            # Add envelope
            envelope = np.sin(np.pi * t / t[-1]) ** 0.5
            return signal * envelope
        else:
            # Ambient noise
            return 0.01 * np.random.randn(self.chunk_size)
            
    def get_voice_waveform(self, width: int = 40) -> str:
        """
        Get ASCII waveform for TUI display
        
        Args:
            width: Width of waveform in characters
            
        Returns:
            ASCII waveform string
        """
        if self.metrics.amplitude < 0.01:
            return "─" * width
            
        # Generate waveform based on amplitude and frequency
        waveform = []
        for i in range(width):
            # Create wave pattern
            phase = (i / width) * 2 * np.pi * (self.metrics.frequency / 100)
            height = int(self.metrics.amplitude * 3 * abs(np.sin(phase)))
            
            # Choose character based on height
            if height == 0:
                waveform.append("─")
            elif height == 1:
                waveform.append("╌")
            elif height == 2:
                waveform.append("═")
            else:
                waveform.append("▀")
                
        return "".join(waveform)


class VoiceIntegration:
    """
    Integration layer between voice connection and TUI
    """
    
    def __init__(self, tui_app):
        """
        Initialize voice integration
        
        Args:
            tui_app: The UnifiedEnhancedTUI instance
        """
        self.tui = tui_app
        self.voice_conn = VoiceConnection(
            on_text_received=self._handle_voice_command,
            on_metrics_update=self._update_voice_metrics
        )
        
    async def start(self) -> None:
        """Start voice integration"""
        await self.voice_conn.start()
        
    async def stop(self) -> None:
        """Stop voice integration"""
        await self.voice_conn.stop()
        
    def _handle_voice_command(self, text: str) -> None:
        """Handle recognized voice command"""
        # Send to TUI as if typed
        self.tui.input.value = text
        asyncio.create_task(
            self.tui.on_input_submitted(
                type('Event', (), {'value': text})()
            )
        )
        
    def _update_voice_metrics(self, metrics: VoiceMetrics) -> None:
        """Update TUI with voice metrics"""
        # Update orb visualization
        self.tui.voice_amplitude = metrics.amplitude
        self.tui.orb.set_voice_activity(
            metrics.amplitude > 0.1,
            metrics.amplitude,
            metrics.frequency
        )
        
        # Update voice status label
        if self.tui.voice_mode:
            if metrics.is_speaking:
                status = f"🎤 Voice: Speaking ({metrics.amplitude:.0%})"
            elif metrics.amplitude > 0.1:
                status = f"🎤 Voice: Listening ({metrics.clarity:.0%} clarity)"
            else:
                status = "🎤 Voice: Ready (say 'Hey Nix')"
                
            try:
                voice_label = self.tui.query_one("#voice-status")
                voice_label.update(status)
            except Exception:
                pass  # Label might not exist yet


# Demo mode for testing
async def demo_voice_connection():
    """Demo the voice connection"""
    
    def on_text(text: str):
        print(f"📝 Recognized: {text}")
        
    def on_metrics(metrics: VoiceMetrics):
        waveform = VoiceConnection().get_voice_waveform()
        print(f"\r🎤 {waveform} | Amp: {metrics.amplitude:.2f} | Freq: {metrics.frequency:.0f}Hz", end="")
        
    voice = VoiceConnection(on_text, on_metrics)
    
    print("🎤 Voice Connection Demo")
    print("Say 'Hey Nix' to activate...")
    
    await voice.start()
    
    try:
        # Run for 30 seconds
        await asyncio.sleep(30)
    finally:
        await voice.stop()
        print("\n✅ Demo complete")


if __name__ == "__main__":
    asyncio.run(demo_voice_connection())