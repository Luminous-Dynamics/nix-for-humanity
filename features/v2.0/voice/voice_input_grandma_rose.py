#!/usr/bin/env python3
"""
from typing import Dict, Optional
Voice Input Prototype for Grandma Rose
======================================

This is a local, privacy-first voice recognition system designed specifically
for elderly users like Grandma Rose. It uses OpenAI Whisper for speech-to-text
and pyttsx3 for text-to-speech, both running entirely offline.

Key Features:
- Large visual feedback
- Clear audio cues
- Simple commands first
- Low latency
- 100% local processing
"""

import os
import sys
import time
import threading
import queue
import json
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime

# Audio recording and processing
try:
    import pyaudio
    import wave
    import numpy as np
except ImportError:
    print("Please install required packages: pip install pyaudio wave numpy")
    sys.exit(1)

# Speech recognition
try:
    import whisper
except ImportError:
    print("Please install Whisper: pip install openai-whisper")
    sys.exit(1)

# Text-to-speech
try:
    import pyttsx3
except ImportError:
    print("Please install pyttsx3: pip install pyttsx3")
    sys.exit(1)

# Add parent directory to path for NLP integration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nix_knowledge_engine import NixOSKnowledgeEngine


@dataclass
class VoiceSettings:
    """Settings optimized for elderly users"""
    # Whisper settings
    whisper_model: str = "base"  # Balance between speed and accuracy
    language: str = "en"
    
    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    
    # Voice feedback settings
    tts_rate: int = 150  # Slower speech for clarity (default is 200)
    tts_volume: float = 0.9  # Louder volume
    tts_voice_index: int = 0  # Usually the clearest voice
    
    # UI settings
    font_size: int = 36  # Extra large text
    high_contrast: bool = True
    visual_feedback: bool = True
    audio_feedback: bool = True
    
    # Recognition settings
    silence_threshold: float = 500  # Amplitude threshold for silence
    silence_duration: float = 1.5  # Seconds of silence to stop recording
    max_recording_duration: float = 10.0  # Maximum recording length
    

class GrandmaRoseVoiceInterface:
    """Voice interface designed for elderly users with accessibility as primary concern"""
    
    def __init__(self, settings: VoiceSettings = None):
        self.settings = settings or VoiceSettings()
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # Initialize components
        print("🎙️ Initializing Grandma Rose Voice Interface...")
        
        # Load Whisper model
        print(f"Loading Whisper {self.settings.whisper_model} model (this may take a moment)...")
        self.whisper_model = whisper.load_model(self.settings.whisper_model)
        print("✅ Whisper loaded successfully")
        
        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self._configure_tts()
        
        # Initialize NixOS knowledge engine
        self.nix_engine = NixOSKnowledgeEngine()
        
        # Audio setup
        self.audio = pyaudio.PyAudio()
        
        # Command history for learning
        self.command_history = []
        
        print("✅ Voice interface ready!")
        
    def _configure_tts(self):
        """Configure text-to-speech for elderly users"""
        # Set speech rate (slower for clarity)
        self.tts_engine.setProperty('rate', self.settings.tts_rate)
        
        # Set volume (louder for hearing)
        self.tts_engine.setProperty('volume', self.settings.tts_volume)
        
        # Select clearest voice
        voices = self.tts_engine.getProperty('voices')
        if voices and len(voices) > self.settings.tts_voice_index:
            self.tts_engine.setProperty('voice', voices[self.settings.tts_voice_index].id)
    
    def speak(self, text: str, wait: bool = True):
        """Speak text with clear pronunciation"""
        if self.settings.audio_feedback:
            self.tts_engine.say(text)
            if wait:
                self.tts_engine.runAndWait()
            else:
                # Run in background
                threading.Thread(target=self.tts_engine.runAndWait).start()
    
    def show_visual_feedback(self, message: str, type: str = "info"):
        """Display large, clear visual feedback"""
        if self.settings.visual_feedback:
            # In a real implementation, this would update a GUI
            # For now, we'll use console with clear formatting
            border = "=" * 60
            
            if type == "listening":
                symbol = "🎤"
                color = "\033[92m"  # Green
            elif type == "processing":
                symbol = "⏳"
                color = "\033[93m"  # Yellow
            elif type == "success":
                symbol = "✅"
                color = "\033[92m"  # Green
            elif type == "error":
                symbol = "❌"
                color = "\033[91m"  # Red
            else:
                symbol = "ℹ️"
                color = "\033[94m"  # Blue
            
            print(f"\n{color}{border}")
            print(f"{symbol} {message.upper()}")
            print(f"{border}\033[0m\n")
    
    def record_audio(self, callback: Optional[Callable] = None) -> Optional[np.ndarray]:
        """Record audio with visual feedback and silence detection"""
        self.show_visual_feedback("LISTENING - PLEASE SPEAK", "listening")
        self.speak("I'm listening. What would you like to do?", wait=False)
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.settings.channels,
            rate=self.settings.sample_rate,
            input=True,
            frames_per_buffer=self.settings.chunk_size
        )
        
        frames = []
        silent_chunks = 0
        start_time = time.time()
        
        try:
            while True:
                # Check for timeout
                if time.time() - start_time > self.settings.max_recording_duration:
                    self.show_visual_feedback("RECORDING STOPPED - TIME LIMIT", "info")
                    break
                
                # Read audio chunk
                data = stream.read(self.settings.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Convert to numpy for amplitude check
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitude = np.abs(audio_data).mean()
                
                # Visual amplitude feedback
                if callback:
                    callback(amplitude)
                
                # Check for silence
                if amplitude < self.settings.silence_threshold:
                    silent_chunks += 1
                    if silent_chunks > (self.settings.silence_duration * 
                                      self.settings.sample_rate / self.settings.chunk_size):
                        self.show_visual_feedback("PROCESSING YOUR REQUEST", "processing")
                        break
                else:
                    silent_chunks = 0
                    
        except KeyboardInterrupt:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        finally:
            stream.stop_stream()
            stream.close()
        
        # Convert frames to numpy array
        if frames:
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            return audio_data.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
        return None
    
    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Whisper"""
        try:
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                audio_data,
                language=self.settings.language,
                task="transcribe"
            )
            
            text = result["text"].strip()
            
            if text:
                self.show_visual_feedback(f"I HEARD: {text}", "success")
                return text
            else:
                self.show_visual_feedback("I DIDN'T CATCH THAT", "error")
                self.speak("I'm sorry, I didn't catch that. Could you please repeat?")
                return ""
                
        except Exception as e:
            self.show_visual_feedback("ERROR UNDERSTANDING SPEECH", "error")
            self.speak("I'm having trouble understanding. Let me try again.")
            print(f"Transcription error: {e}")
            return ""
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """Process natural language command through NixOS engine"""
        # Extract intent
        intent = self.nix_engine.extract_intent(text)
        
        # Get solution
        solution = self.nix_engine.get_solution(intent)
        
        # Format response
        response = self.nix_engine.format_response(intent, solution)
        
        # Make response more grandma-friendly
        if "I'll help you install" in response:
            # Simplify technical instructions
            friendly_response = self._make_grandma_friendly(response, intent)
            return {
                "original": text,
                "intent": intent,
                "response": friendly_response,
                "success": solution.get('found', False)
            }
        
        return {
            "original": text,
            "intent": intent,
            "response": response,
            "success": solution.get('found', False)
        }
    
    def _make_grandma_friendly(self, response: str, intent: Dict) -> str:
        """Convert technical response to grandma-friendly language"""
        if intent.get('action') == 'install_package':
            package = intent.get('package', 'that program')
            
            friendly = f"I'll help you get {package} on your computer!\n\n"
            friendly += "Here's the easiest way:\n\n"
            friendly += f"1. I'll add {package} to your computer for you\n"
            friendly += "2. It will be ready to use in just a moment\n"
            friendly += "3. You'll find it in your applications menu\n\n"
            friendly += "Would you like me to do this for you now?"
            
            return friendly
            
        elif intent.get('action') == 'update_system':
            return ("I'll update your computer to make sure everything is safe and working well.\n\n"
                   "This might take a few minutes. I'll let you know when it's done.\n\n"
                   "Would you like me to start the update now?")
                   
        elif intent.get('action') == 'fix_wifi':
            return ("Let me help you fix your internet connection.\n\n"
                   "I'll check a few things:\n"
                   "1. First, I'll make sure your WiFi is turned on\n"
                   "2. Then I'll look for available networks\n"
                   "3. Finally, I'll help you connect\n\n"
                   "Let's start by checking your WiFi settings.")
        
        return response
    
    def voice_conversation_loop(self):
        """Main conversation loop with voice input/output"""
        self.show_visual_feedback("VOICE ASSISTANT READY", "success")
        self.speak("Hello! I'm here to help you with your computer. Just tell me what you need.")
        
        try:
            while True:
                # Wait for wake word or button press
                print("\n👂 Say 'Hello Computer' or press ENTER to start...")
                input()  # For prototype, use ENTER instead of wake word
                
                # Record audio
                audio_data = self.record_audio()
                
                if audio_data is not None and len(audio_data) > 0:
                    # Transcribe
                    text = self.transcribe_audio(audio_data)
                    
                    if text:
                        # Process command
                        result = self.process_command(text)
                        
                        # Speak response
                        self.speak(result['response'])
                        
                        # Log for learning
                        self.command_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "input": text,
                            "intent": result['intent'],
                            "success": result['success']
                        })
                        
                        # Check for exit commands
                        if any(word in text.lower() for word in ['goodbye', 'exit', 'quit', 'stop']):
                            self.speak("Goodbye! Call me anytime you need help.")
                            break
                
        except KeyboardInterrupt:
            self.speak("Goodbye!")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.audio.terminate()
        
        # Save command history for learning
        history_file = Path("grandma_rose_commands.json")
        with open(history_file, 'w') as f:
            json.dump(self.command_history, f, indent=2)
        print(f"Command history saved to {history_file}")


def main():
    """Run the Grandma Rose voice interface"""
    print("""
    👵 Grandma Rose Voice Interface
    ===============================
    
    This is a voice-controlled NixOS assistant designed
    specifically for elderly users with accessibility needs.
    
    Features:
    - Simple voice commands
    - Clear audio feedback
    - Large visual indicators
    - Offline operation
    - Privacy-first design
    
    Starting up...
    """)
    
    # Create and run interface
    interface = GrandmaRoseVoiceInterface()
    interface.voice_conversation_loop()


if __name__ == "__main__":
    main()