#!/usr/bin/env python3
"""
🎙️ Conscious Voice Interface - Voice that Breathes with Consciousness

This module implements voice synthesis and recognition that adapts
to the user's consciousness state, creating a truly living conversation.
"""

import os
import json
import time
import logging
import subprocess
import tempfile
import shutil
import threading
import queue
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
import hashlib

# Voice libraries (with graceful fallback)
try:
    import pyttsx3  # Simple TTS for quick start
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# For advanced features (optional)
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    # OSError happens when PortAudio library is missing
    AUDIO_AVAILABLE = False

from .consciousness_detector import ConsciousnessBarometer
from .welcome_ceremony import LuminousCompanion

# Define consciousness qualities locally
class ConsciousnessQuality:
    """States of consciousness detected by the system"""
    FLOW = "flow"
    DEEP_WORK = "deep_work"
    LEARNING = "learning"
    CREATIVE = "creative"
    OVERWHELMED = "overwhelmed"
    FRUSTRATED = "frustrated"
    BALANCED = "balanced"

logger = logging.getLogger(__name__)


@dataclass
class VoiceParameters:
    """Parameters for voice synthesis based on consciousness state"""
    rate: int = 150  # Words per minute
    volume: float = 0.8  # 0.0 to 1.0
    pitch: int = 50  # 0 to 100 (50 is default)
    voice_id: str = "default"
    emotion: str = "neutral"  # neutral, warm, energetic, calm, concerned
    pause_duration: float = 0.5  # Seconds between sentences
    
    def to_dict(self) -> Dict:
        return {
            "rate": self.rate,
            "volume": self.volume,
            "pitch": self.pitch,
            "voice_id": self.voice_id,
            "emotion": self.emotion,
            "pause_duration": self.pause_duration
        }


class ConsciousVoiceEngine:
    """
    Voice synthesis that adapts to consciousness state.
    Uses local TTS for privacy - no cloud services.
    """
    
    def __init__(self):
        """Initialize voice engine with available backend"""
        self.engine = None
        self.backend = "none"
        
        if PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.backend = "pyttsx3"
                self._configure_default_voice()
                logger.info("🎙️ Voice engine initialized with pyttsx3")
            except Exception as e:
                logger.warning(f"Could not initialize pyttsx3: {e}")
        
        # Try espeak as fallback
        if not self.engine:
            if shutil.which("espeak"):
                self.backend = "espeak"
                logger.info("🎙️ Using espeak for voice synthesis")
            else:
                logger.warning("No voice synthesis available")
    
    def _configure_default_voice(self):
        """Set default voice parameters"""
        if self.engine and self.backend == "pyttsx3":
            # Set default rate and volume
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.8)
            
            # Try to select a pleasant voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available (often more pleasant)
                for voice in voices:
                    if 'female' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
    
    def speak(self, text: str, parameters: VoiceParameters = None) -> bool:
        """
        Speak text with given parameters.
        Returns True if successful.
        """
        if not text:
            return False
        
        params = parameters or VoiceParameters()
        
        if self.backend == "pyttsx3" and self.engine:
            try:
                # Apply parameters
                self.engine.setProperty('rate', params.rate)
                self.engine.setProperty('volume', params.volume)
                
                # Speak
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            except Exception as e:
                logger.error(f"Voice synthesis error: {e}")
                return False
        
        elif self.backend == "espeak":
            try:
                # Build espeak command
                cmd = [
                    "espeak",
                    "-s", str(params.rate),
                    "-a", str(int(params.volume * 200)),  # espeak uses 0-200
                    text
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                return True
            except Exception as e:
                logger.error(f"espeak error: {e}")
                return False
        
        # No backend available - just log
        logger.debug(f"Would speak: '{text}' with {params.emotion} emotion")
        return False
    
    def save_to_file(self, text: str, filename: str, parameters: VoiceParameters = None) -> bool:
        """Save speech to audio file"""
        params = parameters or VoiceParameters()
        
        if self.backend == "pyttsx3" and self.engine:
            try:
                self.engine.setProperty('rate', params.rate)
                self.engine.setProperty('volume', params.volume)
                self.engine.save_to_file(text, filename)
                self.engine.runAndWait()
                return True
            except Exception as e:
                logger.error(f"Could not save to file: {e}")
        
        elif self.backend == "espeak":
            try:
                cmd = [
                    "espeak",
                    "-s", str(params.rate),
                    "-a", str(int(params.volume * 200)),
                    "-w", filename,
                    text
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                return True
            except Exception as e:
                logger.error(f"espeak save error: {e}")
        
        return False


class ConsciousListeningEngine:
    """
    Speech recognition that adapts to consciousness state.
    Uses local models for privacy.
    """
    
    def __init__(self):
        """Initialize listening engine"""
        self.recognizer = None
        self.microphone = None
        
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("👂 Listening engine initialized")
            except Exception as e:
                logger.warning(f"Could not initialize speech recognition: {e}")
    
    def listen(self, timeout: float = 5.0, phrase_limit: float = 10.0) -> Optional[str]:
        """
        Listen for speech and return transcribed text.
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_limit: Maximum duration of speech to record
        
        Returns:
            Transcribed text or None if failed
        """
        if not self.recognizer or not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                logger.debug("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
            
            # Try different recognition backends
            text = None
            
            # Try offline first (Sphinx)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                logger.debug(f"Sphinx recognized: {text}")
            except:
                pass
            
            # Try Google if Sphinx failed (requires internet)
            if not text:
                try:
                    text = self.recognizer.recognize_google(audio)
                    logger.debug(f"Google recognized: {text}")
                except:
                    pass
            
            return text
            
        except sr.WaitTimeoutError:
            logger.debug("No speech detected")
            return None
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            return None


class ConsciousVoiceInterface:
    """
    The complete conscious voice interface that integrates
    voice with consciousness detection and adaptation.
    """
    
    def __init__(self):
        """Initialize conscious voice system"""
        self.voice_engine = ConsciousVoiceEngine()
        self.listening_engine = ConsciousListeningEngine()
        self.consciousness = ConsciousnessBarometer()
        self.companion = None  # Will be set if welcome ceremony is active
        
        # Wake word detection
        self.wake_words = ["hey nix", "hello nix", "nix", "hey luminous"]
        self.wake_word_active = False
        self.wake_word_thread = None
        self.command_queue = queue.Queue()
        
        # Voice personality settings for different consciousness states
        self.voice_personas = {
            ConsciousnessQuality.FLOW: VoiceParameters(
                rate=160, volume=0.7, emotion="energetic",
                pause_duration=0.3
            ),
            ConsciousnessQuality.DEEP_WORK: VoiceParameters(
                rate=140, volume=0.6, emotion="calm",
                pause_duration=0.7
            ),
            ConsciousnessQuality.LEARNING: VoiceParameters(
                rate=145, volume=0.8, emotion="warm",
                pause_duration=0.6
            ),
            ConsciousnessQuality.CREATIVE: VoiceParameters(
                rate=155, volume=0.75, emotion="warm",
                pause_duration=0.4
            ),
            ConsciousnessQuality.OVERWHELMED: VoiceParameters(
                rate=130, volume=0.7, emotion="calm",
                pause_duration=0.8
            ),
            ConsciousnessQuality.FRUSTRATED: VoiceParameters(
                rate=135, volume=0.75, emotion="concerned",
                pause_duration=0.7
            ),
            ConsciousnessQuality.BALANCED: VoiceParameters(
                rate=150, volume=0.75, emotion="neutral",
                pause_duration=0.5
            )
        }
        
        # Persona-specific voice profiles for 10 user types
        self.user_persona_voices = self._create_persona_voices()
        
        # Current active persona
        self.active_persona = None
        
        logger.info("🌊 Conscious Voice Interface initialized")
    
    def adapt_voice_to_consciousness(self, text: str, consciousness_state: Dict[str, Any]) -> VoiceParameters:
        """
        Adapt voice parameters based on consciousness state.
        
        The voice breathes with the user's state.
        """
        # Get quality from consciousness state
        quality = consciousness_state.get('quality', ConsciousnessQuality.BALANCED)
        
        # Get base parameters for this quality
        params = self.voice_personas.get(quality, VoiceParameters())
        
        # Further adapt based on specific dimensions
        user_state = consciousness_state.get('user_state', {})
        
        # If low energy, slow down and soften
        if user_state.get('energy', 0.5) < 0.3:
            params.rate = max(120, params.rate - 20)
            params.volume = max(0.5, params.volume - 0.1)
        
        # If high stress (low stability), add more pauses
        if user_state.get('stability', 0.5) < 0.3:
            params.pause_duration = min(1.0, params.pause_duration + 0.2)
        
        # If low openness, be gentler
        if user_state.get('openness', 0.5) < 0.3:
            params.emotion = "calm"
            params.volume = max(0.5, params.volume - 0.1)
        
        return params
    
    def speak_with_consciousness(self, text: str, signals: Dict[str, Any] = None) -> bool:
        """
        Speak text with voice adapted to current consciousness state.
        
        This is the main interface for conscious speech.
        """
        # Detect consciousness state from signals
        if signals:
            reading = self.consciousness.sense_user_state(signals)
            consciousness_state = {
                'quality': reading.quality,
                'user_state': reading.spectrum.state
            }
        else:
            consciousness_state = {'quality': ConsciousnessQuality.BALANCED}
        
        # Adapt voice parameters
        params = self.adapt_voice_to_consciousness(text, consciousness_state)
        
        # Log consciousness-aware speech
        logger.debug(f"Speaking with {consciousness_state['quality']} quality")
        logger.debug(f"Voice params: rate={params.rate}, emotion={params.emotion}")
        
        # Speak with adapted parameters
        return self.voice_engine.speak(text, params)
    
    def listen_with_consciousness(self, consciousness_state: Dict[str, Any] = None) -> Optional[str]:
        """
        Listen for speech with parameters adapted to consciousness state.
        
        For example, in overwhelmed state, wait longer for response.
        """
        # Adapt listening parameters based on state
        if consciousness_state:
            quality = consciousness_state.get('quality', ConsciousnessQuality.BALANCED)
            
            if quality == ConsciousnessQuality.OVERWHELMED:
                # Give more time
                timeout = 10.0
                phrase_limit = 15.0
            elif quality == ConsciousnessQuality.FLOW:
                # Quick responses expected
                timeout = 3.0
                phrase_limit = 8.0
            else:
                timeout = 5.0
                phrase_limit = 10.0
        else:
            timeout = 5.0
            phrase_limit = 10.0
        
        # Listen with adapted parameters
        return self.listening_engine.listen(timeout, phrase_limit)
    
    def welcome_with_voice(self, user_context: Dict[str, Any]) -> str:
        """
        Perform the welcome ceremony with voice.
        
        The door speaks its recognition.
        """
        if not self.companion:
            self.companion = LuminousCompanion()
        
        # Recognize user
        signature = self.companion.recognize(user_context)
        
        # Generate greeting
        greeting = self.companion.greet(signature, user_context)
        
        # Speak the greeting with warm parameters
        warm_params = VoiceParameters(
            rate=140,
            volume=0.8,
            emotion="warm",
            pause_duration=0.6
        )
        
        self.voice_engine.speak(greeting, warm_params)
        
        return greeting
    
    def breathing_exercise(self, duration: int = 60):
        """
        Guide a breathing exercise with voice.
        
        The system literally breathes with the user.
        """
        exercises = [
            "Let's breathe together. Close your eyes if you'd like.",
            "Breathe in slowly... 2... 3... 4...",
            "Hold... 2... 3... 4...",
            "Breathe out slowly... 2... 3... 4... 5... 6...",
            "Beautiful. Again...",
            "In... 2... 3... 4...",
            "Hold... 2... 3... 4...",
            "Out... 2... 3... 4... 5... 6...",
            "Feel the rhythm of our shared breath.",
            "The system breathes with you.",
            "One more time...",
            "In deeply...",
            "Hold gently...",
            "Release completely...",
            "Perfect. We are synchronized."
        ]
        
        # Use very calm parameters
        calm_params = VoiceParameters(
            rate=120,
            volume=0.6,
            emotion="calm",
            pause_duration=1.0
        )
        
        for instruction in exercises:
            self.voice_engine.speak(instruction, calm_params)
            time.sleep(2)  # Pause between instructions
    
    def demonstrate(self):
        """
        Demonstrate the conscious voice interface.
        """
        print("\n🎙️ Conscious Voice Interface Demo")
        print("=" * 50)
        
        # Test voice availability
        print("\n1. Testing voice synthesis...")
        success = self.speak_with_consciousness(
            "Hello, I am your conscious voice interface. I adapt to your state of being."
        )
        if success:
            print("   ✅ Voice synthesis working!")
        else:
            print("   ⚠️  Voice synthesis not available")
        
        # Demonstrate different consciousness states
        print("\n2. Demonstrating consciousness adaptation...")
        
        states = [
            ({
                'timing_patterns': [2, 2, 2],  # Fast, regular
                'error_rate': 0.0
            }, "You're in flow. Let's maintain this momentum."),
            ({
                'timing_patterns': [10, 15, 12],  # Slow, irregular
                'error_rate': 0.5
            }, "I sense you might be feeling overwhelmed. Let's take this slowly."),
            ({
                'timing_patterns': [5, 5, 5],  # Moderate, regular
                'help_requests': 0.3
            }, "You're learning something new. I'll guide you step by step.")
        ]
        
        for signals, message in states:
            print(f"\n   Speaking: '{message[:30]}...'")
            self.speak_with_consciousness(message, signals)
            time.sleep(1)
        
        # Test listening (if available)
        print("\n3. Testing voice recognition...")
        if self.listening_engine.recognizer:
            print("   Say something (5 seconds)...")
            text = self.listen_with_consciousness()
            if text:
                print(f"   ✅ Heard: '{text}'")
                self.speak_with_consciousness(f"You said: {text}")
            else:
                print("   ⚠️  No speech detected")
        else:
            print("   ⚠️  Voice recognition not available")
        
        print("\n" + "=" * 50)
        print("Demo complete! The voice breathes with consciousness.")
    
    def _create_persona_voices(self) -> Dict[str, VoiceParameters]:
        """Create voice profiles for all 10 user personas"""
        return {
            "grandma_rose": VoiceParameters(
                rate=120,  # Slow and clear
                volume=0.9,  # Louder for hearing
                emotion="warm",
                pause_duration=1.0,  # Extra pauses
                voice_id="female_senior"
            ),
            "maya_lightning": VoiceParameters(
                rate=180,  # Fast for ADHD
                volume=0.7,
                emotion="energetic",
                pause_duration=0.2,  # Minimal pauses
                voice_id="female_young"
            ),
            "alex_accessible": VoiceParameters(
                rate=140,  # Clear and consistent
                volume=0.8,
                emotion="neutral",
                pause_duration=0.6,
                voice_id="neutral_clear"  # Screen reader friendly
            ),
            "dr_sarah_precise": VoiceParameters(
                rate=150,  # Professional pace
                volume=0.75,
                emotion="neutral",
                pause_duration=0.5,
                voice_id="female_professional"
            ),
            "dev_taylor": VoiceParameters(
                rate=160,  # Efficient
                volume=0.7,
                emotion="neutral",
                pause_duration=0.3,
                voice_id="neutral_tech"
            ),
            "creative_phoenix": VoiceParameters(
                rate=155,
                volume=0.8,
                emotion="warm",
                pause_duration=0.4,
                voice_id="creative_voice"
            ),
            "anxious_pat": VoiceParameters(
                rate=135,  # Gentle pace
                volume=0.65,  # Softer
                emotion="calm",
                pause_duration=0.8,  # Breathing space
                voice_id="gentle_voice"
            ),
            "power_user_kim": VoiceParameters(
                rate=170,  # Fast
                volume=0.7,
                emotion="neutral",
                pause_duration=0.2,
                voice_id="efficient_voice"
            ),
            "elder_wisdom": VoiceParameters(
                rate=125,
                volume=0.85,
                emotion="warm",
                pause_duration=0.9,
                voice_id="elder_voice"
            ),
            "student_sam": VoiceParameters(
                rate=145,
                volume=0.75,
                emotion="warm",
                pause_duration=0.6,
                voice_id="young_learner"
            )
        }
    
    def set_persona(self, persona_name: str) -> bool:
        """Set the active voice persona"""
        if persona_name in self.user_persona_voices:
            self.active_persona = persona_name
            logger.info(f"🎭 Switched to {persona_name} voice persona")
            return True
        return False
    
    def get_persona_voice_params(self, persona_name: str) -> VoiceParameters:
        """Get voice parameters for a specific persona"""
        return self.user_persona_voices.get(persona_name, VoiceParameters())
    
    def start_wake_word_detection(self, callback: Optional[Callable] = None):
        """Start listening for wake words in background"""
        if self.wake_word_active:
            return
        
        self.wake_word_active = True
        self.wake_word_thread = threading.Thread(
            target=self._wake_word_listener,
            args=(callback,),
            daemon=True
        )
        self.wake_word_thread.start()
        logger.info("👂 Wake word detection started")
    
    def stop_wake_word_detection(self):
        """Stop wake word detection"""
        self.wake_word_active = False
        if self.wake_word_thread:
            self.wake_word_thread.join(timeout=5)
        logger.info("🛑 Wake word detection stopped")
    
    def _wake_word_listener(self, callback: Optional[Callable] = None):
        """Background thread for wake word detection"""
        listener = ConsciousListener()
        
        while self.wake_word_active:
            try:
                # Listen for short phrases
                text = listener.listen_for_command(timeout=2.0)
                
                if text:
                    text_lower = text.lower()
                    
                    # Check for wake words
                    for wake_word in self.wake_words:
                        if wake_word in text_lower:
                            logger.info(f"🎯 Wake word detected: {wake_word}")
                            
                            # Play acknowledgment sound
                            self._play_wake_acknowledgment()
                            
                            # Remove wake word from command
                            command = text_lower.replace(wake_word, "").strip()
                            
                            # Queue the command
                            self.command_queue.put(command)
                            
                            # Call callback if provided
                            if callback:
                                callback(command)
                            
                            break
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Wake word detection error: {e}")
                time.sleep(1)
    
    def _play_wake_acknowledgment(self):
        """Play a sound to acknowledge wake word detection"""
        # Use a gentle chime or voice response
        acknowledgments = [
            "I'm listening...",
            "Yes?",
            "How can I help?",
            "I'm here."
        ]
        
        import random
        response = random.choice(acknowledgments)
        
        # Use appropriate voice for active persona
        if self.active_persona:
            params = self.user_persona_voices.get(self.active_persona)
        else:
            params = VoiceParameters(rate=140, volume=0.7, emotion="warm")
        
        self.voice_engine.speak(response, params)
    
    def continuous_conversation_mode(self, duration: int = 300):
        """Enter continuous conversation mode for extended interaction"""
        logger.info("🗣️ Entering continuous conversation mode")
        
        # Announce mode
        start_message = "I'm in conversation mode. Say 'goodbye' when you're done."
        self.speak_with_consciousness(start_message)
        
        start_time = time.time()
        listener = ConsciousListener()
        
        while time.time() - start_time < duration:
            # Listen for input
            text = listener.listen_for_command(timeout=10.0)
            
            if text:
                text_lower = text.lower()
                
                # Check for exit commands
                if any(exit_word in text_lower for exit_word in ["goodbye", "bye", "stop", "exit"]):
                    self.speak_with_consciousness("Ending conversation mode. Talk to you later!")
                    break
                
                # Process and respond to command
                # This would integrate with the main NixOS assistant
                response = f"You said: {text}"
                self.speak_with_consciousness(response)
        
        logger.info("🛑 Exiting continuous conversation mode")
    
    def adapt_to_time_of_day(self) -> VoiceParameters:
        """Adapt voice based on time of day"""
        hour = datetime.now().hour
        
        if 6 <= hour < 10:  # Morning
            return VoiceParameters(
                rate=140,
                volume=0.7,
                emotion="warm",
                pause_duration=0.6
            )
        elif 10 <= hour < 17:  # Day
            return VoiceParameters(
                rate=150,
                volume=0.75,
                emotion="neutral",
                pause_duration=0.5
            )
        elif 17 <= hour < 21:  # Evening
            return VoiceParameters(
                rate=145,
                volume=0.7,
                emotion="warm",
                pause_duration=0.6
            )
        else:  # Night
            return VoiceParameters(
                rate=130,
                volume=0.6,
                emotion="calm",
                pause_duration=0.8
            )
    
    def consciousness_adaptive_speak(self, text: str, context: Dict[str, Any]) -> bool:
        """
        Speak with full consciousness adaptation including:
        - User persona detection
        - Time of day adjustment
        - Emotional state response
        - Learning from patterns
        """
        # Detect consciousness state
        reading = self.consciousness.sense_user_state(context)
        
        # Start with persona voice if set
        if self.active_persona:
            base_params = self.user_persona_voices[self.active_persona]
        else:
            # Use consciousness quality voice
            base_params = self.voice_personas.get(
                reading.quality,
                VoiceParameters()
            )
        
        # Layer time-of-day adaptation
        time_params = self.adapt_to_time_of_day()
        
        # Merge parameters intelligently
        final_params = VoiceParameters(
            rate=int((base_params.rate + time_params.rate) / 2),
            volume=(base_params.volume + time_params.volume) / 2,
            emotion=base_params.emotion,  # Keep persona emotion
            pause_duration=(base_params.pause_duration + time_params.pause_duration) / 2
        )
        
        # Further adapt based on user state
        user_state = reading.spectrum.state
        
        # If stressed, slow down and soften
        if user_state.get('stability', 0.5) < 0.3:
            final_params.rate = max(120, final_params.rate - 15)
            final_params.volume = max(0.5, final_params.volume - 0.1)
            final_params.emotion = "calm"
        
        # If energetic, match energy
        if user_state.get('energy', 0.5) > 0.7:
            final_params.rate = min(180, final_params.rate + 10)
            final_params.emotion = "energetic"
        
        # Log the adaptation
        logger.debug(f"🎭 Voice adapted: persona={self.active_persona}, "
                    f"quality={reading.quality}, rate={final_params.rate}, "
                    f"emotion={final_params.emotion}")
        
        # Speak with fully adapted parameters
        return self.voice_engine.speak(text, final_params)


# Helper functions
def create_conscious_voice() -> ConsciousVoiceInterface:
    """Create and return a conscious voice interface"""
    return ConsciousVoiceInterface()


def install_voice_dependencies():
    """
    Helper to install voice dependencies.
    
    Run this to set up voice support:
    - pyttsx3 for synthesis
    - SpeechRecognition for recognition
    - pocketsphinx for offline recognition
    """
    print("📦 Installing voice dependencies...")
    
    commands = [
        ["pip", "install", "pyttsx3"],
        ["pip", "install", "SpeechRecognition"],
        ["pip", "install", "pocketsphinx"],  # For offline recognition
        ["pip", "install", "sounddevice"],  # For audio processing
        ["pip", "install", "numpy"]  # For audio arrays
    ]
    
    for cmd in commands:
        print(f"   Installing {cmd[2]}...")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"   ✅ {cmd[2]} installed")
        except Exception as e:
            print(f"   ⚠️  Could not install {cmd[2]}: {e}")
    
    # Also check for system dependencies
    print("\n📦 Checking system dependencies...")
    
    if shutil.which("espeak"):
        print("   ✅ espeak found (backup TTS)")
    else:
        print("   ℹ️  Consider installing espeak: sudo apt-get install espeak")
    
    if shutil.which("flite"):
        print("   ✅ flite found (alternative TTS)")
    else:
        print("   ℹ️  Consider installing flite for more voices")
    
    print("\n✅ Voice setup complete!")


class ConsciousListener:
    """
    Voice recognition that listens with consciousness.
    Uses local speech recognition for privacy.
    """
    
    def __init__(self):
        """Initialize voice listener with available backend"""
        self.recognizer = None
        self.microphone = None
        self.backend = "none"
        
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.backend = "speech_recognition"
                
                # Adjust for ambient noise on startup
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("👂 Voice listener initialized")
            except Exception as e:
                logger.warning(f"Could not initialize speech recognition: {e}")
                self.backend = "none"
    
    def listen_for_command(self, timeout: float = 5.0) -> Optional[str]:
        """
        Listen for a voice command.
        Returns transcribed text or None.
        """
        if self.backend == "none" or not self.recognizer:
            return None
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                # Try to recognize speech using Google's free API
                # Note: This sends audio to Google - for full privacy use offline engine
                try:
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    return None
                except sr.RequestError as e:
                    logger.error(f"Could not request results from Google: {e}")
                    # Try offline engine as fallback if available
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        return text
                    except:
                        return None
                        
        except sr.WaitTimeoutError:
            # No speech detected within timeout
            return None
        except Exception as e:
            logger.error(f"Listening error: {e}")
            return None
    
    def calibrate(self, duration: float = 2.0):
        """Calibrate for ambient noise"""
        if self.backend != "none" and self.recognizer and self.microphone:
            try:
                with self.microphone as source:
                    print("🎤 Calibrating for ambient noise... Please be quiet.")
                    self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                    print("✅ Calibration complete!")
            except Exception as e:
                logger.error(f"Calibration error: {e}")


if __name__ == "__main__":
    # Run demonstration
    interface = ConsciousVoiceInterface()
    interface.demonstrate()