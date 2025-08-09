#!/usr/bin/env python3
"""
from typing import Tuple, Optional
Voice Interface for Nix for Humanity

A privacy-first, local voice interface designed with Grandma Rose in mind.
Uses Whisper for speech-to-text and Piper for text-to-speech.
"""

import os
import sys
import json
import wave
import pyaudio
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Tuple
import subprocess
import tempfile
import time
import threading

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from nixos_python_backend import NixOSPythonBackend
from nix_knowledge_engine import NixOSKnowledgeEngine
from adaptive_response_formatter import AdaptiveResponseFormatter

class VoiceInterface:
    """
    Voice interface for natural NixOS interaction.
    Designed for accessibility and ease of use.
    """
    
    def __init__(self):
        # Audio settings
        self.sample_rate = 16000  # 16kHz for Whisper
        self.channels = 1  # Mono
        self.chunk_size = 1024
        self.silence_threshold = 500  # Adjust based on environment
        self.silence_duration = 1.5  # Seconds of silence to stop recording
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        
        # Components
        self.backend = NixOSPythonBackend()
        self.knowledge = NixOSKnowledgeEngine()
        self.formatter = AdaptiveResponseFormatter()
        
        # Paths
        self.whisper_model = self._find_whisper_model()
        self.piper_model = self._find_piper_model()
        
        # State
        self.is_recording = False
        self.is_processing = False
        
    def _find_whisper_model(self) -> Optional[str]:
        """Find Whisper model in system"""
        # Check common locations
        paths = [
            "/run/current-system/sw/share/whisper/models/ggml-base.en.bin",
            Path.home() / ".local/share/whisper/models/ggml-base.en.bin",
            "/nix/store/*/share/whisper/models/ggml-base.en.bin"
        ]
        
        for path in paths:
            if isinstance(path, str) and os.path.exists(path):
                return path
            elif isinstance(path, Path) and path.exists():
                return str(path)
        
        # Try to find with glob
        import glob
        models = glob.glob("/nix/store/*/share/whisper/models/ggml-base.en.bin")
        if models:
            return models[0]
            
        return None
    
    def _find_piper_model(self) -> Optional[str]:
        """Find Piper voice model"""
        # Look for Amy voice (clear, friendly)
        paths = [
            "/run/current-system/sw/share/piper/voices/en_US-amy-medium.onnx",
            Path.home() / ".local/share/piper/voices/en_US-amy-medium.onnx",
        ]
        
        for path in paths:
            if isinstance(path, str) and os.path.exists(path):
                return path
            elif isinstance(path, Path) and path.exists():
                return str(path)
                
        return None
    
    def check_dependencies(self) -> Tuple[bool, str]:
        """Check if voice dependencies are available"""
        issues = []
        
        # Check Whisper
        if not self.whisper_model:
            issues.append("Whisper model not found. Install with: nix-env -iA nixpkgs.whisper-cpp")
        else:
            # Check whisper binary
            try:
                subprocess.run(["whisper-cpp", "--help"], 
                             capture_output=True, check=True)
            except Exception:
                issues.append("whisper-cpp not found. Install with: nix-env -iA nixpkgs.whisper-cpp")
        
        # Check Piper
        if not self.piper_model:
            issues.append("Piper voice not found. Install with: nix-env -iA nixpkgs.piper-tts")
        else:
            # Check piper binary
            try:
                subprocess.run(["piper", "--help"], 
                             capture_output=True, check=True)
            except Exception:
                issues.append("piper not found. Install with: nix-env -iA nixpkgs.piper-tts")
        
        # Check audio
        try:
            self.audio.get_default_input_device_info()
        except Exception:
            issues.append("No microphone detected. Please connect a microphone.")
        
        if issues:
            return False, "\n".join(issues)
        return True, "All dependencies satisfied"
    
    def record_audio(self, callback: Optional[Callable[[float], None]] = None) -> bytes:
        """
        Record audio from microphone until silence detected.
        
        Args:
            callback: Optional callback for volume level (0.0-1.0)
            
        Returns:
            Raw audio data
        """
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        frames = []
        silent_chunks = 0
        chunks_for_silence = int(self.silence_duration * self.sample_rate / self.chunk_size)
        
        print("🎤 Listening... (speak now, I'll stop when you're done)")
        
        self.is_recording = True
        while self.is_recording:
            try:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Calculate volume
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_data).mean()
                
                # Callback for UI
                if callback:
                    normalized_volume = min(1.0, volume / 10000)
                    callback(normalized_volume)
                
                # Check for silence
                if volume < self.silence_threshold:
                    silent_chunks += 1
                    if silent_chunks > chunks_for_silence and len(frames) > 10:
                        print("✓ Got it! Processing...")
                        break
                else:
                    silent_chunks = 0
                    
            except KeyboardInterrupt:
                break
        
        stream.stop_stream()
        stream.close()
        
        self.is_recording = False
        return b''.join(frames)
    
    def save_audio(self, audio_data: bytes, filename: str):
        """Save audio data to WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
    
    def transcribe_audio(self, audio_file: str) -> Optional[str]:
        """Transcribe audio using Whisper"""
        try:
            result = subprocess.run([
                "whisper-cpp",
                "--model", self.whisper_model,
                "--language", "en",
                "--no-timestamps",
                "--output-txt",
                audio_file
            ], capture_output=True, text=True)
            
            # Read transcription
            txt_file = audio_file + ".txt"
            if os.path.exists(txt_file):
                with open(txt_file, 'r') as f:
                    text = f.read().strip()
                os.remove(txt_file)
                return text
                
        except Exception as e:
            print(f"Transcription error: {e}")
            
        return None
    
    def synthesize_speech(self, text: str, output_file: str) -> bool:
        """Convert text to speech using Piper"""
        try:
            # Ensure text is clean for speech
            text = text.replace("```", "").replace("**", "").replace("*", "")
            
            result = subprocess.run([
                "piper",
                "--model", self.piper_model,
                "--output_file", output_file
            ], input=text, text=True, capture_output=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"TTS error: {e}")
            return False
    
    def play_audio(self, filename: str):
        """Play audio file"""
        try:
            # Use paplay (PulseAudio) or aplay (ALSA)
            for player in ["paplay", "aplay"]:
                try:
                    subprocess.run([player, filename], check=True)
                    return
                except Exception:
                    continue
                    
            print(f"Could not play audio: {filename}")
            
        except Exception as e:
            print(f"Playback error: {e}")
    
    def process_voice_command(self, volume_callback: Optional[Callable[[float], None]] = None):
        """
        Complete voice interaction flow.
        Record -> Transcribe -> Process -> Speak
        """
        self.is_processing = True
        
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_file = os.path.join(temp_dir, "recording.wav")
            response_file = os.path.join(temp_dir, "response.wav")
            
            try:
                # 1. Record audio
                audio_data = self.record_audio(volume_callback)
                if not audio_data:
                    return
                
                # 2. Save audio
                self.save_audio(audio_data, audio_file)
                
                # 3. Transcribe
                print("🤔 Understanding...")
                text = self.transcribe_audio(audio_file)
                if not text:
                    self.speak("I didn't catch that. Could you try again?")
                    return
                
                print(f"📝 Heard: \"{text}\"")
                
                # 4. Process with NLP
                response = self.process_command(text)
                
                # 5. Speak response
                self.speak(response)
                
            finally:
                self.is_processing = False
    
    def process_command(self, text: str) -> str:
        """Process voice command through NLP pipeline"""
        # Extract intent
        intent = self.knowledge.extract_intent(text)
        
        # Get solution
        solution = self.knowledge.get_solution(intent)
        response = self.knowledge.format_response(intent, solution)
        
        # Apply voice-optimized formatting
        # Force simple mode for voice
        voice_query = text + " explain simply for voice"
        adapted, _ = self.formatter.adapt_response(
            voice_query, 
            response, 
            intent['action']
        )
        
        # Further simplify for speech
        adapted = self._simplify_for_speech(adapted)
        
        return adapted
    
    def _simplify_for_speech(self, text: str) -> str:
        """Simplify text for speech output"""
        # Remove markdown
        text = text.replace("**", "").replace("*", "")
        text = text.replace("```", "").replace("`", "")
        
        # Remove bullet points
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                line = line[2:]
            if line.startswith('• '):
                line = line[2:]
            if line:
                cleaned.append(line)
        
        # Join with pauses
        text = ". ".join(cleaned)
        
        # Shorten if too long
        sentences = text.split('. ')
        if len(sentences) > 3:
            text = '. '.join(sentences[:3]) + "."
            text += " Would you like to hear more?"
        
        return text
    
    def speak(self, text: str):
        """Speak text using TTS"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            if self.synthesize_speech(text, tmp.name):
                print(f"🔊 Speaking: {text}")
                self.play_audio(tmp.name)
            else:
                print(f"Could not speak: {text}")
            
            # Clean up
            try:
                os.unlink(tmp.name)
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
    
    def interactive_session(self):
        """Run interactive voice session"""
        print("""
🎙️  Nix for Humanity Voice Interface
====================================

Press SPACE to start speaking, release when done.
Say "exit" or press Ctrl+C to quit.

Ready when you are!
        """)
        
        try:
            while True:
                input("Press Enter to start recording...")
                self.process_voice_command()
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")


def main():
    """Test voice interface"""
    voice = VoiceInterface()
    
    # Check dependencies
    ok, message = voice.check_dependencies()
    if not ok:
        print("❌ Missing dependencies:")
        print(message)
        print("\nPlease install the required packages and try again.")
        return
    
    print("✅ All dependencies found!")
    
    # Run test
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("\n🧪 Testing voice synthesis...")
        voice.speak("Hello! I'm Nix for Humanity. I can help you install software.")
        print("\n🧪 Testing voice recognition...")
        voice.process_voice_command()
    else:
        # Interactive mode
        voice.interactive_session()


if __name__ == "__main__":
    main()