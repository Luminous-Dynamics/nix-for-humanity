#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Enhanced Voice Interface for Nix for Humanity

Improved implementation with better error handling, configuration,
and real Whisper/Piper integration.
"""

import asyncio
import queue
import threading
import time
import json
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import numpy as np
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("Audio libraries not available. Install sounddevice and numpy.")

# Import our backend
from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.api.schema import Request, Context
from nix_humanity.core.educational_errors import make_error_educational
from nix_humanity.core.progress_indicator import AsyncProgressIndicator, ProgressStyle


class VoiceState(Enum):
    """Voice interface states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"
    INITIALIZING = "initializing"


@dataclass
class VoiceConfig:
    """Enhanced voice interface configuration"""
    # Wake word settings
    wake_word: str = "hey nix"
    wake_variants: List[str] = field(default_factory=lambda: ["hey nix", "okay nix", "nixos"])
    wake_sensitivity: float = 0.8
    
    # Audio settings
    language: str = "en"
    sample_rate: int = 16000
    chunk_duration: float = 0.1  # 100ms chunks
    silence_threshold: float = 0.01
    silence_duration: float = 1.5  # Stop after 1.5s silence
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    
    # Model settings
    whisper_model: str = "base"
    whisper_device: str = "cpu"  # or "cuda"
    voice_model: str = "en_US-amy-medium"
    voice_speed: float = 1.0
    
    # Behavior settings
    auto_punctuate: bool = True
    echo_commands: bool = True
    confirm_dangerous: bool = True
    mock_mode: bool = False
    
    @classmethod
    def from_file(cls, path: Path) -> 'VoiceConfig':
        """Load configuration from JSON file"""
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                return cls(**data.get('voice', {}))
        return cls()


class AudioProcessor:
    """Handles audio recording and playback"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
    def start_recording(self):
        """Start continuous audio recording"""
        if not AUDIO_AVAILABLE:
            raise RuntimeError("Audio libraries not available")
        
        self.is_recording = True
        chunk_size = int(self.config.sample_rate * self.config.chunk_duration)
        
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio error: {status}")
            if self.is_recording:
                self.audio_queue.put(indata.copy())
        
        self.stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=1,
            callback=audio_callback,
            blocksize=chunk_size,
            device=self.config.input_device
        )
        self.stream.start()
        
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
    
    def get_audio_chunk(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """Get next audio chunk from queue"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def play_audio(self, audio_data: np.ndarray, sample_rate: Optional[int] = None):
        """Play audio data"""
        if not AUDIO_AVAILABLE:
            return
        
        sample_rate = sample_rate or self.config.sample_rate
        sd.play(audio_data, samplerate=sample_rate, device=self.config.output_device)
        sd.wait()


class WhisperTranscriber:
    """Handles speech-to-text with Whisper"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            import whisper
            logger.info(f"Loading Whisper {self.config.whisper_model} model...")
            self.model = whisper.load_model(
                self.config.whisper_model,
                device=self.config.whisper_device
            )
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def transcribe(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcribe audio to text"""
        if self.model is None:
            # Mock mode for testing
            return self._mock_transcribe(audio_data)
        
        try:
            # Ensure audio is float32 and normalized
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Whisper expects audio between -1 and 1
            if np.abs(audio_data).max() > 1.0:
                audio_data = audio_data / np.abs(audio_data).max()
            
            result = self.model.transcribe(
                audio_data,
                language=self.config.language,
                task="transcribe",
                initial_prompt="NixOS commands and questions"
            )
            
            text = result.get("text", "").strip()
            
            # Auto-punctuate if needed
            if self.config.auto_punctuate and text and not text[-1] in '.?!':
                text += '.'
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def _mock_transcribe(self, audio_data: np.ndarray) -> str:
        """Mock transcription for testing"""
        # Simulate different commands based on audio length
        duration = len(audio_data) / self.config.sample_rate
        if duration < 1:
            return "help"
        elif duration < 2:
            return "install firefox"
        elif duration < 3:
            return "update my system"
        else:
            return "search for text editors"


class PiperSynthesizer:
    """Handles text-to-speech with Piper"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.voice = None
        self._load_voice()
    
    def _load_voice(self):
        """Load Piper voice model"""
        try:
            # Try to use piper Python API if available
            import piper
            voices_dir = Path.home() / ".local" / "share" / "piper" / "voices"
            voice_path = voices_dir / f"{self.config.voice_model}.onnx"
            
            if voice_path.exists():
                self.voice = piper.PiperVoice.load(str(voice_path))
                logger.info(f"Piper voice {self.config.voice_model} loaded")
            else:
                logger.warning(f"Voice model not found: {voice_path}")
                self.voice = None
                
        except ImportError:
            logger.info("Piper Python API not available, will use CLI")
            self.voice = None
        except Exception as e:
            logger.error(f"Failed to load Piper voice: {e}")
            self.voice = None
    
    def synthesize(self, text: str) -> Optional[np.ndarray]:
        """Synthesize speech from text"""
        if not text:
            return None
        
        # Try Python API first
        if self.voice is not None:
            return self._synthesize_api(text)
        
        # Fall back to CLI
        return self._synthesize_cli(text)
    
    def _synthesize_api(self, text: str) -> Optional[np.ndarray]:
        """Synthesize using Python API"""
        try:
            audio_data = self.voice.synthesize(
                text,
                speed=self.config.voice_speed
            )
            return audio_data
        except Exception as e:
            logger.error(f"Synthesis API error: {e}")
            return None
    
    def _synthesize_cli(self, text: str) -> Optional[np.ndarray]:
        """Synthesize using Piper CLI"""
        import subprocess
        import tempfile
        import wave
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Run piper
            voices_dir = Path.home() / ".local" / "share" / "piper" / "voices"
            model_path = voices_dir / f"{self.config.voice_model}.onnx"
            
            if not model_path.exists():
                logger.warning(f"Voice model not found: {model_path}")
                return self._mock_synthesize(text)
            
            cmd = [
                "piper",
                "--model", str(model_path),
                "--output_file", tmp_path,
                "--length_scale", str(1.0 / self.config.voice_speed)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode == 0:
                # Read the generated audio
                with wave.open(tmp_path, 'rb') as wf:
                    frames = wf.readframes(wf.getnframes())
                    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Clean up
                Path(tmp_path).unlink()
                return audio
            else:
                logger.error(f"Piper CLI error: {stderr}")
                return None
                
        except FileNotFoundError:
            logger.warning("Piper CLI not found. Install with: pip install piper-tts")
            return self._mock_synthesize(text)
        except Exception as e:
            logger.error(f"Synthesis CLI error: {e}")
            return None
    
    def _mock_synthesize(self, text: str) -> np.ndarray:
        """Mock synthesis for testing"""
        # Generate simple sine wave "speech"
        duration = len(text) * 0.05  # Rough estimate
        samples = int(duration * self.config.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Mix of frequencies to sound "speech-like"
        audio = np.zeros(samples)
        for freq in [200, 400, 600]:
            audio += 0.1 * np.sin(2 * np.pi * freq * t)
        
        # Add envelope
        envelope = np.exp(-t / duration)
        audio *= envelope
        
        return audio.astype(np.float32)


class EnhancedVoiceInterface:
    """
    Enhanced voice interface with better real-world integration.
    """
    
    def __init__(
        self,
        backend: Optional[NixForHumanityBackend] = None,
        config: Optional[VoiceConfig] = None,
        state_callback: Optional[Callable[[VoiceState], None]] = None
    ):
        # Load config from file if not provided
        if config is None:
            config_path = Path.home() / ".config" / "nix-humanity" / "voice.json"
            config = VoiceConfig.from_file(config_path)
        
        self.backend = backend or NixForHumanityBackend()
        self.config = config
        self.state_callback = state_callback
        
        # Components
        self.audio = AudioProcessor(config)
        self.transcriber = WhisperTranscriber(config)
        self.synthesizer = PiperSynthesizer(config)
        
        # State
        self.current_state = VoiceState.INITIALIZING
        self.is_running = False
        self.audio_buffer = []
        self.silence_frames = 0
        self.last_command_time = 0
        
        # Threads
        self.processing_thread = None
        
        # Voice responses
        self.responses = self._init_responses()
    
    def _init_responses(self) -> Dict[str, str]:
        """Initialize voice response templates"""
        return {
            "greeting": "Hello! I'm ready to help you with NixOS. Just say 'Hey Nix' followed by your command.",
            "listening": "I'm listening...",
            "thinking": "Let me process that...",
            "wake_detected": "Yes?",
            "not_understood": "I didn't quite catch that. Could you please repeat?",
            "error": "I encountered an error: {}",
            "goodbye": "Goodbye! Say 'Hey Nix' anytime you need help.",
            "timeout": "I didn't hear anything. Say 'Hey Nix' when you're ready.",
            "dangerous_confirm": "This looks like a dangerous operation. Are you sure?",
            "help": """I can help you with:
- Installing software: 'Install Firefox'
- System updates: 'Update my system'
- Package search: 'Search for editors'
- System info: 'How much disk space?'
Just speak naturally after saying 'Hey Nix'!"""
        }
    
    def start(self):
        """Start the enhanced voice interface"""
        logger.info("Starting enhanced voice interface...")
        self._set_state(VoiceState.INITIALIZING)
        
        try:
            # Start audio recording
            if not self.config.mock_mode:
                self.audio.start_recording()
            
            # Start processing thread
            self.is_running = True
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True
            )
            self.processing_thread.start()
            
            # Ready announcement
            self._set_state(VoiceState.IDLE)
            self._speak(self.responses["greeting"])
            
            logger.info("Voice interface ready")
            
        except Exception as e:
            logger.error(f"Failed to start voice interface: {e}")
            self._set_state(VoiceState.ERROR)
            raise
    
    def stop(self):
        """Stop the voice interface"""
        logger.info("Stopping voice interface...")
        
        self.is_running = False
        self._speak(self.responses["goodbye"])
        
        # Stop audio
        if not self.config.mock_mode:
            self.audio.stop_recording()
        
        # Wait for thread
        if self.processing_thread:
            self.processing_thread.join(timeout=2)
        
        logger.info("Voice interface stopped")
    
    def _set_state(self, state: VoiceState):
        """Update current state and notify callback"""
        self.current_state = state
        logger.debug(f"State changed to: {state.value}")
        
        if self.state_callback:
            try:
                self.state_callback(state)
            except Exception as e:
                logger.error(f"State callback error: {e}")
    
    def _processing_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                if self.config.mock_mode:
                    # Mock mode - simulate wake word every 10 seconds
                    time.sleep(10)
                    if self.is_running:
                        self._handle_wake_word()
                        time.sleep(2)
                        self._process_mock_command()
                else:
                    # Real audio processing
                    chunk = self.audio.get_audio_chunk(timeout=0.1)
                    if chunk is not None:
                        self._process_audio_chunk(chunk)
                        
            except Exception as e:
                logger.error(f"Processing error: {e}")
                time.sleep(0.1)
    
    def _process_audio_chunk(self, chunk: np.ndarray):
        """Process a single audio chunk"""
        # Add to buffer
        self.audio_buffer.append(chunk)
        
        # Keep buffer size reasonable (10 seconds max)
        max_chunks = int(10 / self.config.chunk_duration)
        if len(self.audio_buffer) > max_chunks:
            self.audio_buffer.pop(0)
        
        # Check for silence
        volume = np.abs(chunk).mean()
        if volume < self.config.silence_threshold:
            self.silence_frames += 1
        else:
            self.silence_frames = 0
        
        # Process based on state
        if self.current_state == VoiceState.IDLE:
            # Check for wake word periodically
            if len(self.audio_buffer) >= 20:  # 2 seconds of audio
                if self._detect_wake_word():
                    self._handle_wake_word()
        
        elif self.current_state == VoiceState.LISTENING:
            # Check if user finished speaking
            silence_duration = self.silence_frames * self.config.chunk_duration
            if silence_duration >= self.config.silence_duration:
                self._process_command()
    
    def _detect_wake_word(self) -> bool:
        """Detect wake word in audio buffer"""
        if not self.audio_buffer:
            return False
        
        # Get recent audio (last 2 seconds)
        recent_chunks = self.audio_buffer[-20:]
        audio_data = np.concatenate(recent_chunks)
        
        # Transcribe
        text = self.transcriber.transcribe(audio_data)
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for any wake variant
        for variant in self.config.wake_variants:
            if variant.lower() in text_lower:
                logger.info(f"Wake word detected: '{variant}' in '{text}'")
                return True
        
        return False
    
    def _handle_wake_word(self):
        """Handle wake word detection"""
        logger.info("Wake word activated")
        self._set_state(VoiceState.LISTENING)
        
        # Clear buffer for command
        self.audio_buffer.clear()
        self.silence_frames = 0
        
        # Audio feedback
        self._play_wake_sound()
        self._speak(self.responses["wake_detected"])
    
    def _process_command(self):
        """Process the voice command"""
        self._set_state(VoiceState.PROCESSING)
        
        if not self.audio_buffer:
            self._speak(self.responses["timeout"])
            self._set_state(VoiceState.IDLE)
            return
        
        # Transcribe command
        audio_data = np.concatenate(self.audio_buffer)
        command_text = self.transcriber.transcribe(audio_data)
        
        if not command_text:
            self._speak(self.responses["not_understood"])
            self._set_state(VoiceState.IDLE)
            return
        
        logger.info(f"Command: {command_text}")
        
        # Echo command if configured
        if self.config.echo_commands:
            self._speak(f"I heard: {command_text}")
        
        # Clear buffer
        self.audio_buffer.clear()
        
        # Execute command
        self._execute_command(command_text)
    
    def _process_mock_command(self):
        """Process a mock command for testing"""
        commands = [
            "install firefox",
            "update my system",
            "search for text editors",
            "how much disk space do I have?",
            "what's my IP address?"
        ]
        
        import random
        command = random.choice(commands)
        logger.info(f"Mock command: {command}")
        
        self._execute_command(command)
    
    def _execute_command(self, command_text: str):
        """Execute command through backend"""
        try:
            # Show processing
            self._speak(self.responses["thinking"])
            
            # Create request
            request = Request(
                query=command_text,
                context=Context(
                    personality="voice",
                    execute=False,  # Safety first
                    dry_run=True
                )
            )
            
            # Process through backend
            response = self.backend.process(request)
            
            if response.success:
                self._speak_response(response)
            else:
                error_msg = make_error_educational(
                    response.error or "Operation failed",
                    verbose=False
                )
                self._speak(error_msg)
                
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            self._speak(self.responses["error"].format(str(e)))
        
        finally:
            self._set_state(VoiceState.IDLE)
    
    def _speak_response(self, response):
        """Speak backend response"""
        # Extract intent for custom responses
        intent = response.data.get("intent", "") if response.data else ""
        
        # Customize response based on intent
        if intent == "install_package":
            packages = response.data.get("packages", [])
            if packages:
                pkg = packages[0]
                text = f"I can help you install {pkg}. "
                text += f"The command would be: nix-env -i A nixpkgs.{pkg}"
            else:
                text = response.text
        
        elif intent == "search_package":
            results = response.data.get("results", [])
            if results:
                text = f"I found {len(results)} packages. "
                text += "The top results are: "
                text += ", ".join(results[:3])
            else:
                text = "No packages found matching your search."
        
        elif intent == "update_system":
            text = "I can help update your system. "
            text += "This will download the latest packages and rebuild your configuration. "
            text += "The command would be: sudo nixos-rebuild switch"
        
        elif intent == "help":
            text = self.responses["help"]
        
        else:
            # Use response text, but limit length for voice
            text = response.text
            if len(text) > 200:
                text = text[:200] + "... There's more information available."
        
        self._speak(text)
    
    def _speak(self, text: str):
        """Synthesize and play speech"""
        if not text:
            return
        
        self._set_state(VoiceState.SPEAKING)
        logger.info(f"Speaking: {text}")
        
        try:
            # Synthesize
            audio_data = self.synthesizer.synthesize(text)
            
            if audio_data is not None and not self.config.mock_mode:
                # Play audio
                self.audio.play_audio(audio_data)
            else:
                # Mock mode - just print
                print(f"🗣️ {text}")
                time.sleep(len(text) * 0.05)  # Simulate speaking time
                
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
        
        finally:
            if self.current_state == VoiceState.SPEAKING:
                self._set_state(VoiceState.IDLE)
    
    def _play_wake_sound(self):
        """Play wake detection sound"""
        if self.config.mock_mode:
            print("🔔 *ding*")
            return
        
        # Generate a pleasant ding sound
        duration = 0.1
        sample_rate = self.config.sample_rate
        t = np.linspace(0, duration, int(duration * sample_rate))
        
        # Two-tone ding
        freq1, freq2 = 800, 1200
        audio = 0.3 * np.sin(2 * np.pi * freq1 * t)
        audio += 0.2 * np.sin(2 * np.pi * freq2 * t)
        
        # Apply envelope
        envelope = np.exp(-t / (duration * 0.3))
        audio *= envelope
        
        self.audio.play_audio(audio.astype(np.float32))


class VoiceAssistant:
    """
    High-level voice assistant with enhanced features.
    """
    
    def __init__(
        self, 
        backend: Optional[NixForHumanityBackend] = None,
        config: Optional[VoiceConfig] = None
    ):
        self.backend = backend or NixForHumanityBackend()
        self.config = config
        self.interface = None
        self.state_history = []
    
    def start(self):
        """Start the voice assistant"""
        # Create interface with state tracking
        self.interface = EnhancedVoiceInterface(
            backend=self.backend,
            config=self.config,
            state_callback=self._on_state_change
        )
        
        self.interface.start()
    
    def stop(self):
        """Stop the voice assistant"""
        if self.interface:
            self.interface.stop()
    
    def _on_state_change(self, state: VoiceState):
        """Track state changes"""
        self.state_history.append((time.time(), state))
        
        # Log state changes
        state_emoji = {
            VoiceState.IDLE: "😴",
            VoiceState.LISTENING: "👂",
            VoiceState.PROCESSING: "🤔",
            VoiceState.SPEAKING: "🗣️",
            VoiceState.ERROR: "❌",
            VoiceState.INITIALIZING: "🚀"
        }
        
        emoji = state_emoji.get(state, "❓")
        print(f"\r{emoji} {state.value.capitalize()}...", end="", flush=True)


# Make enhanced version the default
VoiceInterface = EnhancedVoiceInterface


if __name__ == "__main__":
    # Demo the enhanced voice interface
    print("🎤 Enhanced Voice Interface Demo")
    print("=" * 50)
    
    # Use mock mode for demo
    config = VoiceConfig(mock_mode=True)
    
    assistant = VoiceAssistant(config=config)
    assistant.start()
    
    print("\nVoice assistant started in MOCK mode")
    print("Simulating wake word detection every 10 seconds...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        assistant.stop()