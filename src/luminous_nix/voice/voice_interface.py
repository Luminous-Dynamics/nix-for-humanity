#!/usr/bin/env python3
"""
Simple Voice Interface for Luminous Nix
Integrates TTS and STT for natural conversation
"""

import os
import sys
from typing import Optional, Tuple
from pathlib import Path

# Check for voice support
VOICE_AVAILABLE = True
try:
    import speech_recognition as sr
    import pyttsx3
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    VOICE_AVAILABLE = False

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    VOICE_AVAILABLE = False

class VoiceInterface:
    """Handles voice input and output for Luminous Nix"""
    
    def __init__(self, verbose: bool = False):
        """Initialize voice interface"""
        self.verbose = verbose
        self.recognizer = None
        self.tts_engine = None
        self.microphone = None
        
        if VOICE_AVAILABLE:
            self._initialize_voice()
    
    def _initialize_voice(self):
        """Initialize voice components"""
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Initialize TTS
            try:
                self.tts_engine = pyttsx3.init()
                # Configure voice
                self.tts_engine.setProperty('rate', 175)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                
                # Try to use a better voice if available
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ TTS initialization failed: {e}")
                self.tts_engine = None
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen for voice input
        
        Returns:
            Recognized text or None if failed
        """
        if not VOICE_AVAILABLE or not self.recognizer:
            return None
        
        try:
            with self.microphone as source:
                if self.verbose:
                    print("🎤 Listening...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for input
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                if self.verbose:
                    print("🔄 Processing speech...")
                
                # Try multiple recognition engines
                text = None
                
                # Try Google first (no API key needed)
                try:
                    text = self.recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    if self.verbose:
                        print(f"⚠️ Google Speech Recognition error: {e}")
                
                # Try Sphinx offline if Google fails
                if not text:
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                    except Exception:
                        pass
                
                return text
                
        except sr.WaitTimeoutError:
            if self.verbose:
                print("⏱️ No speech detected (timeout)")
            return None
        except Exception as e:
            if self.verbose:
                print(f"❌ Voice recognition error: {e}")
            return None
    
    def speak(self, text: str) -> bool:
        """
        Speak text aloud
        
        Returns:
            True if successful
        """
        if not self.tts_engine:
            return False
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            if self.verbose:
                print(f"❌ Speech synthesis error: {e}")
            return False
    
    def conversation_loop(self, process_command_func):
        """
        Run continuous conversation loop
        
        Args:
            process_command_func: Function to process recognized commands
        """
        if not VOICE_AVAILABLE:
            print("❌ Voice support not available. Install required packages:")
            print("  pip install SpeechRecognition pyttsx3 pyaudio")
            return
        
        print("🎙️ Voice Mode Active!")
        print("Say 'exit', 'quit', or 'goodbye' to stop")
        print("-" * 40)
        
        self.speak("Hello! I'm Nix. How can I help you?")
        
        while True:
            # Listen for command
            text = self.listen()
            
            if text:
                print(f"🗣️ You said: {text}")
                
                # Check for exit commands
                if any(word in text.lower() for word in ['exit', 'quit', 'goodbye', 'stop']):
                    self.speak("Goodbye!")
                    print("👋 Voice mode ended")
                    break
                
                # Process the command
                response = process_command_func(text)
                
                # Speak the response
                if response:
                    # Clean response for speech (remove emojis and special chars)
                    clean_response = ''.join(
                        char for char in response 
                        if char.isalnum() or char.isspace() or char in '.,!?'
                    )
                    self.speak(clean_response)
            else:
                print("🔇 No speech detected, try again...")

def test_voice():
    """Test voice functionality"""
    voice = VoiceInterface(verbose=True)
    
    print("Testing TTS...")
    voice.speak("Hello! This is a test of the text to speech system.")
    
    print("\nTesting STT (say something)...")
    text = voice.listen(timeout=5)
    if text:
        print(f"Recognized: {text}")
        voice.speak(f"You said: {text}")
    else:
        print("No speech recognized")

if __name__ == "__main__":
    test_voice()