#!/usr/bin/env python3
"""
🎙️ Simple Voice Solution - Works Immediately

Progressive enhancement approach:
1. Text output (always works)
2. System TTS if available (espeak/say)
3. Piper TTS if configured
"""

import subprocess
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VoiceParameters:
    """Voice parameters for any backend."""
    rate: int = 150          # Words per minute
    pitch: int = 50          # 0-100 scale
    volume: float = 0.9      # 0.0-1.0 scale
    voice_id: str = 'default'
    emotion: str = 'neutral'
    pause_duration: float = 0.5
    
    # Compatibility properties for tests
    @property
    def speed_factor(self) -> float:
        """Speed as a factor (1.0 = normal)."""
        return self.rate / 150.0
    
    @property
    def pitch_factor(self) -> float:
        """Pitch as a factor (1.0 = normal)."""
        return self.pitch / 50.0
    
    @property
    def warmth(self) -> float:
        """Emotional warmth (0.0-1.0)."""
        emotion_warmth = {
            'warm': 0.9,
            'friendly': 0.8,
            'neutral': 0.5,
            'professional': 0.3,
            'cold': 0.1
        }
        return emotion_warmth.get(self.emotion, 0.5)
    
    @property
    def formality(self) -> float:
        """Speech formality (0.0-1.0)."""
        emotion_formality = {
            'professional': 0.9,
            'academic': 0.8,
            'neutral': 0.5,
            'friendly': 0.3,
            'casual': 0.1
        }
        return emotion_formality.get(self.emotion, 0.5)


class SimpleVoiceInterface:
    """
    Simple voice interface that works everywhere.
    
    Uses progressive enhancement:
    1. Always shows text
    2. Tries espeak if available (Linux/NixOS)
    3. Tries say if available (macOS)
    4. Falls back to pure text
    """
    
    def __init__(self):
        """Initialize and detect available TTS."""
        self.tts_backend = self._detect_tts()
        self.show_text = True  # Always show text for debugging
        
    def _detect_tts(self) -> Optional[str]:
        """Detect available TTS system."""
        # Try espeak (Linux/NixOS)
        try:
            result = subprocess.run(
                ['espeak', '--version'],
                capture_output=True,
                timeout=1
            )
            if result.returncode == 0:
                logger.info("Using espeak for TTS")
                return 'espeak'
        except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
            pass
        
        # Try espeak-ng (newer version)
        try:
            result = subprocess.run(
                ['espeak-ng', '--version'],
                capture_output=True,
                timeout=1
            )
            if result.returncode == 0:
                logger.info("Using espeak-ng for TTS")
                return 'espeak-ng'
        except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
            pass
        
        # Try say (macOS)
        try:
            result = subprocess.run(
                ['say', '-v', '?'],
                capture_output=True,
                timeout=1
            )
            if result.returncode == 0:
                logger.info("Using macOS 'say' for TTS")
                return 'say'
        except (subprocess.SubprocessError, FileNotFoundError, PermissionError):
            pass
        
        logger.info("No TTS backend found, using text-only mode")
        return None
    
    def speak(self, text: str, params: Optional[VoiceParameters] = None) -> bool:
        """
        Speak text using best available method.
        
        Args:
            text: Text to speak
            params: Voice parameters (optional)
            
        Returns:
            True if speech was attempted, False if text-only
        """
        if params is None:
            params = VoiceParameters()
        
        # Always show text
        if self.show_text:
            emoji = self._get_emotion_emoji(params.emotion)
            print(f"{emoji} {text}")
        
        # Try TTS if available
        if self.tts_backend == 'espeak' or self.tts_backend == 'espeak-ng':
            return self._speak_espeak(text, params)
        elif self.tts_backend == 'say':
            return self._speak_say(text, params)
        else:
            return False  # Text-only mode
    
    def _speak_espeak(self, text: str, params: VoiceParameters) -> bool:
        """Speak using espeak/espeak-ng."""
        try:
            # Convert parameters to espeak format
            speed = int(params.rate * 1.2)  # espeak uses different scale
            pitch = params.pitch
            
            cmd = [
                self.tts_backend,
                '-s', str(speed),
                '-p', str(pitch),
                text
            ]
            
            # Run in background to not block
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
            
        except Exception as e:
            logger.error(f"espeak failed: {e}")
            return False
    
    def _speak_say(self, text: str, params: VoiceParameters) -> bool:
        """Speak using macOS say command."""
        try:
            # Convert rate to macOS format
            rate = params.rate
            
            cmd = ['say', '-r', str(rate), text]
            
            # Run in background
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
            
        except Exception as e:
            logger.error(f"say failed: {e}")
            return False
    
    def _get_emotion_emoji(self, emotion: str) -> str:
        """Get emoji for emotion."""
        emoji_map = {
            'warm': '💖',
            'friendly': '😊',
            'neutral': '🗣️',
            'professional': '💼',
            'excited': '🎉',
            'calm': '😌',
            'encouraging': '💪',
            'curious': '🤔'
        }
        return emoji_map.get(emotion, '🗣️')
    
    def listen(self) -> Optional[str]:
        """
        Listen for voice input (fallback to text).
        
        For now, always uses text input.
        Future: Add speech recognition.
        """
        try:
            return input("🎤 You: ")
        except (EOFError, KeyboardInterrupt):
            return None


# Persona configurations
PERSONA_CONFIGS = {
    'grandma_rose': VoiceParameters(
        rate=120,  # Slower
        pitch=60,  # Slightly higher
        emotion='warm',
        pause_duration=1.0
    ),
    'maya_lightning': VoiceParameters(
        rate=200,  # Fast
        pitch=55,
        emotion='excited',
        pause_duration=0.2
    ),
    'alex_screenreader': VoiceParameters(
        rate=150,  # Normal
        pitch=50,  # Neutral
        emotion='neutral',
        pause_duration=0.5
    ),
    'dr_sarah_precise': VoiceParameters(
        rate=140,
        pitch=45,
        emotion='professional',
        pause_duration=0.7
    ),
    'jordan_conversational': VoiceParameters(
        rate=160,
        pitch=50,
        emotion='friendly',
        pause_duration=0.4
    ),
    'dev_taylor': VoiceParameters(
        rate=170,
        pitch=48,
        emotion='neutral',
        pause_duration=0.3
    ),
    'kai_multilingual': VoiceParameters(
        rate=145,
        pitch=52,
        emotion='friendly',
        pause_duration=0.6
    ),
    'robin_patient': VoiceParameters(
        rate=110,  # Very slow
        pitch=55,
        emotion='calm',
        pause_duration=1.2
    ),
    'sam_efficient': VoiceParameters(
        rate=180,  # Fast
        pitch=50,
        emotion='professional',
        pause_duration=0.2
    ),
    'power_user_kim': VoiceParameters(
        rate=190,
        pitch=48,
        emotion='neutral',
        pause_duration=0.1
    )
}


def get_persona_voice(persona: str) -> VoiceParameters:
    """Get voice parameters for a persona."""
    return PERSONA_CONFIGS.get(persona, VoiceParameters())


# Quick test
if __name__ == "__main__":
    print("=== Testing Simple Voice Interface ===\n")
    
    voice = SimpleVoiceInterface()
    
    # Test basic speech
    print("1. Basic speech:")
    voice.speak("Hello! I'm Luminous Nix, your NixOS assistant.")
    
    # Test with personas
    print("\n2. Testing personas:")
    for persona_name in ['grandma_rose', 'maya_lightning', 'dev_taylor']:
        params = get_persona_voice(persona_name)
        print(f"\n{persona_name}:")
        voice.speak(
            f"Hi! I'm speaking as {persona_name.replace('_', ' ').title()}.",
            params
        )
    
    # Test emotion variations
    print("\n3. Testing emotions:")
    emotions = ['warm', 'professional', 'excited', 'calm']
    for emotion in emotions:
        params = VoiceParameters(emotion=emotion)
        voice.speak(f"This is {emotion} speech.", params)
    
    print("\n✅ Voice test complete!")
    print(f"TTS Backend: {voice.tts_backend or 'Text-only'}")