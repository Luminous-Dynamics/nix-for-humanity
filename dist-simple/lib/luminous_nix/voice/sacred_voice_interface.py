"""
🎤 Sacred Voice Interface for Luminous Nix
Consciousness-first voice interaction with sacred pauses and flow protection
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Any
import threading
import queue

# Audio processing
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    sr = None
    pyttsx3 = None

# Advanced voice (optional)
try:
    import whisper
    import numpy as np
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

logger = logging.getLogger(__name__)


class FlowState(Enum):
    """User's current flow state"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    DEEP_FOCUS = "deep_focus"
    SACRED_PAUSE = "sacred_pause"


class InterruptionLevel(Enum):
    """Interruption urgency levels"""
    NONE = 0  # No interruption allowed
    GENTLE = 1  # Wait for natural pause
    NORMAL = 2  # Standard interruption
    URGENT = 3  # Important but not critical
    CRITICAL = 4  # Must interrupt immediately


@dataclass
class VoiceConfig:
    """Voice interface configuration"""
    # Recognition settings
    energy_threshold: int = 300
    pause_threshold: float = 0.8
    phrase_time_limit: float = 10.0
    
    # Speech settings
    voice_rate: int = 150
    voice_volume: float = 0.9
    voice_id: str = "default"
    
    # Sacred pause settings
    pause_before_speech: float = 0.5
    pause_after_listening: float = 0.3
    deep_breath_duration: float = 2.0
    
    # Flow protection
    focus_protection: bool = True
    min_focus_duration: float = 300  # 5 minutes
    interruption_cooldown: float = 60  # 1 minute
    
    # Personality
    voice_personality: str = "gentle"  # gentle, energetic, professional
    use_acknowledgments: bool = True
    use_thinking_sounds: bool = True


class SacredVoiceInterface:
    """
    Main voice interface with consciousness-first design
    
    Features:
    - Natural speech recognition with Whisper/SpeechRecognition
    - Expressive speech synthesis with Piper/pyttsx3
    - Sacred pauses for mindful interaction
    - Flow state protection
    - Seamless integration with CLI/TUI/GUI
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.flow_state = FlowState.IDLE
        self.last_interaction = time.time()
        self.focus_start_time = None
        
        # Voice components
        self.recognizer = None
        self.microphone = None
        self.speaker = None
        self.whisper_model = None
        
        # Command queue for async processing
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Callbacks
        self.on_command: Optional[Callable[[str], Any]] = None
        self.on_state_change: Optional[Callable[[FlowState], None]] = None
        
        # Initialize if available
        if VOICE_AVAILABLE:
            self._initialize_voice()
    
    def _initialize_voice(self):
        """Initialize voice components"""
        try:
            # Speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.config.energy_threshold
            self.recognizer.pause_threshold = self.config.pause_threshold
            self.microphone = sr.Microphone()
            
            # Text to speech
            self.speaker = pyttsx3.init()
            self.speaker.setProperty('rate', self.config.voice_rate)
            self.speaker.setProperty('volume', self.config.voice_volume)
            
            # Set voice personality
            voices = self.speaker.getProperty('voices')
            if voices and self.config.voice_id != "default":
                for voice in voices:
                    if self.config.voice_id in voice.id.lower():
                        self.speaker.setProperty('voice', voice.id)
                        break
            
            # Load Whisper if available
            if WHISPER_AVAILABLE:
                logger.info("Loading Whisper model for advanced recognition...")
                self.whisper_model = whisper.load_model("base")
            
            logger.info("Voice interface initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice: {e}")
            raise
    
    def _set_flow_state(self, state: FlowState):
        """Update flow state with callback"""
        self.flow_state = state
        if self.on_state_change:
            self.on_state_change(state)
        logger.debug(f"Flow state: {state.value}")
    
    def _sacred_pause(self, duration: Optional[float] = None):
        """
        Sacred pause for mindful interaction
        
        A moment of digital silence to:
        - Allow processing of what was said
        - Prepare for what comes next
        - Respect natural conversation rhythms
        """
        pause_time = duration or self.config.pause_after_listening
        self._set_flow_state(FlowState.SACRED_PAUSE)
        time.sleep(pause_time)
    
    def _can_interrupt(self, level: InterruptionLevel) -> bool:
        """
        Check if we can interrupt based on flow state protection
        
        Implements the Calculus of Interruption:
        - Respects deep focus states
        - Considers interruption urgency
        - Enforces cooldown periods
        """
        if not self.config.focus_protection:
            return True
        
        if self.flow_state == FlowState.DEEP_FOCUS:
            # In deep focus, only critical interruptions allowed
            if level.value < InterruptionLevel.CRITICAL.value:
                focus_duration = time.time() - self.focus_start_time
                if focus_duration < self.config.min_focus_duration:
                    return False
        
        # Check interruption cooldown
        time_since_last = time.time() - self.last_interaction
        if time_since_last < self.config.interruption_cooldown:
            if level.value < InterruptionLevel.URGENT.value:
                return False
        
        return True
    
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen for voice input with sacred awareness
        
        Returns:
            Recognized text or None if nothing detected
        """
        if not VOICE_AVAILABLE or not self.recognizer:
            logger.warning("Voice recognition not available")
            return None
        
        try:
            self._set_flow_state(FlowState.LISTENING)
            
            # Gentle acknowledgment
            if self.config.use_acknowledgments:
                self._play_listening_sound()
            
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen with timeout
                logger.debug("Listening for voice input...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.config.phrase_time_limit
                )
            
            # Sacred pause after listening
            self._sacred_pause()
            
            # Recognition
            self._set_flow_state(FlowState.THINKING)
            
            if self.config.use_thinking_sounds:
                self._play_thinking_sound()
            
            # Try Whisper first if available
            if WHISPER_AVAILABLE and self.whisper_model:
                try:
                    # Convert to numpy array for Whisper
                    audio_data = np.frombuffer(audio.frame_data, np.int16).astype(np.float32) / 32768.0
                    result = self.whisper_model.transcribe(audio_data)
                    text = result["text"].strip()
                except Exception as e:
                    logger.debug(f"Whisper failed, falling back: {e}")
                    text = self.recognizer.recognize_google(audio)
            else:
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
            
            logger.info(f"Recognized: {text}")
            self.last_interaction = time.time()
            return text
            
        except sr.WaitTimeoutError:
            logger.debug("No speech detected (timeout)")
            return None
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            return None
        finally:
            self._set_flow_state(FlowState.IDLE)
    
    def speak(self, text: str, interruption_level: InterruptionLevel = InterruptionLevel.NORMAL):
        """
        Speak text with consciousness-first awareness
        
        Args:
            text: Text to speak
            interruption_level: How urgent this speech is
        """
        if not VOICE_AVAILABLE or not self.speaker:
            logger.warning("Voice synthesis not available")
            print(f"🗣️ {text}")  # Fallback to text
            return
        
        # Check interruption permission
        if not self._can_interrupt(interruption_level):
            logger.debug(f"Speech queued (flow protection): {text[:50]}...")
            self.response_queue.put(text)
            return
        
        try:
            self._set_flow_state(FlowState.SPEAKING)
            
            # Sacred pause before speaking
            if self.config.pause_before_speech > 0:
                time.sleep(self.config.pause_before_speech)
            
            # Apply personality adjustments
            text = self._apply_voice_personality(text)
            
            # Speak
            self.speaker.say(text)
            self.speaker.runAndWait()
            
            self.last_interaction = time.time()
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            print(f"🗣️ {text}")  # Fallback to text
        finally:
            self._set_flow_state(FlowState.IDLE)
    
    def _apply_voice_personality(self, text: str) -> str:
        """Apply voice personality adjustments"""
        if self.config.voice_personality == "gentle":
            # Add gentle pauses
            text = text.replace(".", "...")
            text = text.replace("!", ".")
        elif self.config.voice_personality == "energetic":
            # Add emphasis
            text = text.replace(".", "!")
        # Professional stays as-is
        return text
    
    def _play_listening_sound(self):
        """Play a gentle sound to indicate listening"""
        # Could play a soft chime or beep
        # For now, just a visual indicator
        print("👂 ...")
    
    def _play_thinking_sound(self):
        """Play a subtle sound while thinking"""
        # Could play soft ambient sound
        # For now, just a visual indicator
        print("🤔 ...")
    
    def start_conversation_loop(self):
        """
        Start the main conversation loop
        
        Runs in background thread, processing voice commands continuously
        """
        def _loop():
            logger.info("Starting voice conversation loop")
            while True:
                try:
                    # Listen for command
                    text = self.listen(timeout=10)
                    
                    if text:
                        # Process command if callback is set
                        if self.on_command:
                            response = self.on_command(text)
                            if response:
                                self.speak(response)
                    
                    # Check for queued responses (from flow protection)
                    try:
                        response = self.response_queue.get_nowait()
                        if self._can_interrupt(InterruptionLevel.NORMAL):
                            self.speak(response)
                        else:
                            self.response_queue.put(response)  # Re-queue
                    except queue.Empty:
                        pass
                    
                    # Brief pause between iterations
                    time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Conversation loop error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        return thread
    
    def enter_deep_focus(self):
        """Enter deep focus mode - minimize interruptions"""
        self._set_flow_state(FlowState.DEEP_FOCUS)
        self.focus_start_time = time.time()
        logger.info("Entering deep focus mode")
    
    def exit_deep_focus(self):
        """Exit deep focus mode"""
        self._set_flow_state(FlowState.IDLE)
        self.focus_start_time = None
        logger.info("Exiting deep focus mode")
    
    def take_sacred_breath(self):
        """
        Take a sacred digital breath
        
        A moment of complete pause for:
        - Resetting attention
        - Clearing command queue
        - Preparing for fresh interaction
        """
        self._set_flow_state(FlowState.SACRED_PAUSE)
        time.sleep(self.config.deep_breath_duration)
        
        # Clear queues
        while not self.command_queue.empty():
            self.command_queue.get()
        while not self.response_queue.empty():
            self.response_queue.get()
        
        self._set_flow_state(FlowState.IDLE)
        logger.info("Sacred breath complete - ready for fresh interaction")


def create_voice_interface(config: Optional[VoiceConfig] = None) -> SacredVoiceInterface:
    """
    Factory function to create voice interface
    
    Returns:
        Configured voice interface ready for use
    """
    return SacredVoiceInterface(config or VoiceConfig())


# Example usage
if __name__ == "__main__":
    # Create voice interface
    voice = create_voice_interface(VoiceConfig(
        voice_personality="gentle",
        use_acknowledgments=True,
        focus_protection=True
    ))
    
    # Set command processor
    def process_command(text: str) -> str:
        """Process voice command through Luminous Nix"""
        # Here we'd integrate with the actual CLI
        return f"Processing: {text}"
    
    voice.on_command = process_command
    
    # Start conversation
    print("🎤 Sacred Voice Interface Ready")
    print("Say 'Hello Luminous' to begin...")
    
    try:
        voice.start_conversation_loop().join()
    except KeyboardInterrupt:
        print("\n🙏 Sacred conversation complete")