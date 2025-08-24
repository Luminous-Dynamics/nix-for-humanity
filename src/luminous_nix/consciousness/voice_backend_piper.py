#!/usr/bin/env python3
"""
🎙️ Piper TTS Voice Backend - Fast, Local, Neural Voice

Simple implementation using Piper TTS for voice synthesis.
"""

import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PiperVoiceConfig:
    """Configuration for Piper TTS voices."""
    model: str = "en_US-amy-medium"
    speaker: Optional[int] = None
    noise_scale: float = 0.667
    length_scale: float = 1.0
    noise_w: float = 0.8

class PiperVoiceBackend:
    """
    Voice backend using Piper TTS for local neural voice synthesis.
    
    Piper provides:
    - Fast, local TTS (no internet required)
    - High quality neural voices
    - Multiple voice options
    - Works great on NixOS
    """
    
    # Map personas to Piper voices
    PERSONA_VOICES = {
        'grandma_rose': 'en_US-amy-medium',       # Warm, friendly
        'maya_lightning': 'en_US-arctic-medium',   # Fast, energetic
        'alex_screenreader': 'en_US-ryan-medium',  # Clear, neutral
        'dr_sarah_precise': 'en_US-libritts-high', # Professional
        'jordan_conversational': 'en_US-danny-low', # Casual
        'dev_taylor': 'en_US-lessac-medium',       # Technical
        'kai_multilingual': 'en_US-kusal-medium',  # International
        'robin_patient': 'en_US-amy-low',          # Gentle, slow
        'sam_efficient': 'en_US-arctic-high',      # Quick, clear
        'power_user_kim': 'en_US-ryan-high'        # Confident
    }
    
    def __init__(self, persona: str = 'jordan_conversational'):
        """Initialize with a specific persona voice."""
        self.persona = persona
        self.voice_model = self.PERSONA_VOICES.get(persona, 'en_US-amy-medium')
        self.piper_available = self._check_piper()
        
    def _check_piper(self) -> bool:
        """Check if Piper is available."""
        try:
            result = subprocess.run(
                ['piper', '--version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("Piper TTS not available. Install with: nix-env -iA nixpkgs.piper-tts")
            return False
    
    def speak(self, text: str, speed: float = 1.0, pitch: float = 1.0) -> bool:
        """
        Synthesize and play speech.
        
        Args:
            text: Text to speak
            speed: Speech rate (0.5 = slow, 1.0 = normal, 2.0 = fast)
            pitch: Voice pitch (not supported by Piper, ignored)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.piper_available:
            # Fallback to text output
            print(f"🗣️ [{self.persona}]: {text}")
            return False
            
        try:
            # Adjust length_scale for speed (inverse relationship)
            length_scale = 1.0 / speed
            
            # Generate audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
                # Run Piper TTS
                result = subprocess.run(
                    [
                        'piper',
                        '--model', self.voice_model,
                        '--output_file', audio_file.name,
                        '--length_scale', str(length_scale)
                    ],
                    input=text,
                    text=True,
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    logger.error(f"Piper TTS failed: {result.stderr}")
                    return False
                
                # Play the audio
                return self._play_audio(audio_file.name)
                
        except subprocess.TimeoutExpired:
            logger.error("Piper TTS timed out")
            return False
        except Exception as e:
            logger.error(f"Voice synthesis failed: {e}")
            return False
    
    def _play_audio(self, audio_file: str) -> bool:
        """Play audio file using available player."""
        players = [
            ['paplay', audio_file],      # PulseAudio
            ['aplay', audio_file],        # ALSA
            ['pw-play', audio_file],      # PipeWire
            ['ffplay', '-nodisp', '-autoexit', audio_file],  # FFmpeg
        ]
        
        for player_cmd in players:
            try:
                result = subprocess.run(
                    player_cmd,
                    capture_output=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
                
        logger.warning("No audio player available")
        return False
    
    def set_persona(self, persona: str):
        """Change the voice persona."""
        self.persona = persona
        self.voice_model = self.PERSONA_VOICES.get(persona, 'en_US-amy-medium')
    
    def download_voice(self, model: str) -> bool:
        """Download a Piper voice model if not available."""
        try:
            result = subprocess.run(
                ['piper', '--download-voice', model],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False


class TextFallbackVoice:
    """Simple text-based fallback when no TTS is available."""
    
    def __init__(self, persona: str = 'assistant'):
        self.persona = persona
        self.emoji_map = {
            'grandma_rose': '👵',
            'maya_lightning': '⚡',
            'alex_screenreader': '🔊',
            'dr_sarah_precise': '👩‍⚕️',
            'jordan_conversational': '💬',
            'dev_taylor': '👨‍💻',
            'kai_multilingual': '🌍',
            'robin_patient': '🕊️',
            'sam_efficient': '⚙️',
            'power_user_kim': '🚀',
            'assistant': '🤖'
        }
    
    def speak(self, text: str, **kwargs) -> bool:
        """Display text with persona emoji."""
        emoji = self.emoji_map.get(self.persona, '🗣️')
        print(f"{emoji} [{self.persona}]: {text}")
        return True
    
    def set_persona(self, persona: str):
        """Change the persona."""
        self.persona = persona


def get_voice_backend(persona: str = 'jordan_conversational') -> Any:
    """
    Get the best available voice backend.
    
    Returns:
        PiperVoiceBackend if available, TextFallbackVoice otherwise
    """
    backend = PiperVoiceBackend(persona)
    if backend.piper_available:
        logger.info(f"Using Piper TTS with {backend.voice_model}")
        return backend
    else:
        logger.info("Using text fallback (install Piper for voice)")
        return TextFallbackVoice(persona)


# Quick test
if __name__ == "__main__":
    import sys
    
    # Test with different personas
    personas = ['grandma_rose', 'maya_lightning', 'dev_taylor']
    test_text = "Hello! I'm helping you install Firefox on NixOS."
    
    for persona in personas:
        print(f"\n=== Testing {persona} ===")
        voice = get_voice_backend(persona)
        voice.speak(test_text)
        
    # Test speed variations
    print("\n=== Testing speed variations ===")
    voice = get_voice_backend('jordan_conversational')
    voice.speak("This is normal speed.", speed=1.0)
    voice.speak("This is slow speech.", speed=0.7)
    voice.speak("This is fast speech!", speed=1.5)