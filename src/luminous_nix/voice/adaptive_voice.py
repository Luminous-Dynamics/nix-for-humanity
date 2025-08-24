#!/usr/bin/env python3
"""
🎵 Adaptive Voice System - Voice that changes with emotional context
The system speaks differently based on detected user mood and state
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import logging
from pathlib import Path
import json
import subprocess
import tempfile
from datetime import datetime

from luminous_nix.consciousness.adaptive_persona import EmotionalState, DynamicPersona

logger = logging.getLogger(__name__)


class VoiceTone(Enum):
    """Different voice tones for different emotional contexts"""
    CALM = "calm"              # Slow, steady, peaceful
    ENCOURAGING = "encouraging" # Warm, supportive, uplifting  
    EFFICIENT = "efficient"    # Quick, clear, direct
    PATIENT = "patient"        # Slow, careful, understanding
    CELEBRATORY = "celebratory" # Bright, energetic, happy
    GENTLE = "gentle"          # Soft, caring, nurturing
    FOCUSED = "focused"        # Clear, minimal, concentrated


@dataclass
class VoiceProfile:
    """Voice parameters for speech synthesis"""
    tone: VoiceTone
    speed: float           # 0.5 (slow) to 2.0 (fast)
    pitch: float           # 0.5 (low) to 2.0 (high)
    volume: float          # 0.0 (quiet) to 1.0 (loud)
    pause_length: float    # Seconds between sentences
    emphasis_level: float  # 0.0 (flat) to 1.0 (expressive)
    warmth: float         # 0.0 (neutral) to 1.0 (warm)


# Predefined voice profiles for different emotional states
VOICE_PROFILES = {
    EmotionalState.CURIOUS: VoiceProfile(
        tone=VoiceTone.ENCOURAGING,
        speed=1.0,
        pitch=1.1,
        volume=0.8,
        pause_length=0.5,
        emphasis_level=0.7,
        warmth=0.8
    ),
    EmotionalState.FOCUSED: VoiceProfile(
        tone=VoiceTone.EFFICIENT,
        speed=1.1,
        pitch=1.0,
        volume=0.7,
        pause_length=0.3,
        emphasis_level=0.4,
        warmth=0.3
    ),
    EmotionalState.FRUSTRATED: VoiceProfile(
        tone=VoiceTone.PATIENT,
        speed=0.85,
        pitch=0.95,
        volume=0.6,
        pause_length=0.8,
        emphasis_level=0.3,
        warmth=0.9
    ),
    EmotionalState.CONFUSED: VoiceProfile(
        tone=VoiceTone.GENTLE,
        speed=0.8,
        pitch=1.0,
        volume=0.7,
        pause_length=1.0,
        emphasis_level=0.5,
        warmth=1.0
    ),
    EmotionalState.SATISFIED: VoiceProfile(
        tone=VoiceTone.CELEBRATORY,
        speed=1.05,
        pitch=1.15,
        volume=0.8,
        pause_length=0.4,
        emphasis_level=0.8,
        warmth=0.9
    ),
    EmotionalState.LEARNING: VoiceProfile(
        tone=VoiceTone.ENCOURAGING,
        speed=0.95,
        pitch=1.05,
        volume=0.75,
        pause_length=0.6,
        emphasis_level=0.6,
        warmth=0.7
    ),
    EmotionalState.RUSHED: VoiceProfile(
        tone=VoiceTone.FOCUSED,
        speed=1.3,
        pitch=1.0,
        volume=0.8,
        pause_length=0.2,
        emphasis_level=0.2,
        warmth=0.2
    )
}


class AdaptiveVoiceSystem:
    """
    Voice system that adapts tone, speed, and style based on user's emotional state
    Creates more natural and empathetic interactions
    """
    
    def __init__(self, tts_engine: str = "espeak-ng"):
        """
        Initialize adaptive voice system
        
        Args:
            tts_engine: Text-to-speech engine to use
        """
        self.tts_engine = tts_engine
        self.current_profile = VOICE_PROFILES[EmotionalState.FOCUSED]
        self.voice_cache = {}  # Cache generated audio
        
        # Check available TTS engines
        self._detect_tts_engines()
        
    def _detect_tts_engines(self):
        """Detect available TTS engines on the system"""
        self.available_engines = {}
        
        # Check for espeak-ng
        try:
            subprocess.run(['espeak-ng', '--version'], 
                         capture_output=True, check=True)
            self.available_engines['espeak-ng'] = True
            logger.info("Found espeak-ng TTS engine")
        except:
            self.available_engines['espeak-ng'] = False
        
        # Check for piper
        try:
            subprocess.run(['piper', '--version'], 
                         capture_output=True, check=True)
            self.available_engines['piper'] = True
            logger.info("Found piper TTS engine")
        except:
            self.available_engines['piper'] = False
        
        # Check for festival
        try:
            subprocess.run(['festival', '--version'], 
                         capture_output=True, check=True)
            self.available_engines['festival'] = True
            logger.info("Found festival TTS engine")
        except:
            self.available_engines['festival'] = False
    
    def adapt_to_persona(self, persona: DynamicPersona) -> VoiceProfile:
        """
        Adapt voice profile based on user's persona and current state
        
        Args:
            persona: User's dynamic persona with emotional state
            
        Returns:
            Adapted voice profile
        """
        # Start with base profile for emotional state
        base_profile = VOICE_PROFILES.get(
            persona.current_mood, 
            VOICE_PROFILES[EmotionalState.FOCUSED]
        )
        
        # Create adapted profile
        adapted = VoiceProfile(
            tone=base_profile.tone,
            speed=base_profile.speed,
            pitch=base_profile.pitch,
            volume=base_profile.volume,
            pause_length=base_profile.pause_length,
            emphasis_level=base_profile.emphasis_level,
            warmth=base_profile.warmth
        )
        
        # Adjust based on persona characteristics
        
        # Technical proficiency affects speed and detail
        if persona.technical_proficiency > 0.7:
            adapted.speed *= 1.1  # Faster for experts
            adapted.pause_length *= 0.8
        elif persona.technical_proficiency < 0.3:
            adapted.speed *= 0.9  # Slower for beginners
            adapted.pause_length *= 1.2
        
        # Patience level affects pacing
        if persona.patience_level < 0.3:
            adapted.speed *= 1.15  # Speed up for impatient users
            adapted.pause_length *= 0.7
        elif persona.patience_level > 0.7:
            adapted.speed *= 0.95  # Can take time with patient users
        
        # Frustration requires extra care
        if persona.frustration_level > 0.5:
            adapted.warmth = min(1.0, adapted.warmth + 0.2)
            adapted.speed *= 0.9
            adapted.volume *= 0.9  # Softer voice
            adapted.tone = VoiceTone.GENTLE
        
        # Confidence affects emphasis
        if persona.confidence_level > 0.7:
            adapted.emphasis_level *= 0.8  # Less dramatic
        elif persona.confidence_level < 0.3:
            adapted.emphasis_level *= 1.2  # More encouraging
        
        # Time of day affects energy
        hour = datetime.now().hour
        if hour < 6 or hour > 22:  # Late night/early morning
            adapted.volume *= 0.8
            adapted.speed *= 0.9
            adapted.tone = VoiceTone.CALM
        elif hasattr(persona, 'peak_hours') and hour in persona.peak_hours:  # Peak productivity
            adapted.speed *= 1.05
            adapted.emphasis_level *= 1.1
        
        self.current_profile = adapted
        return adapted
    
    def generate_speech(self, 
                       text: str, 
                       profile: Optional[VoiceProfile] = None,
                       output_file: Optional[Path] = None) -> Optional[Path]:
        """
        Generate speech with adaptive voice parameters
        
        Args:
            text: Text to speak
            profile: Voice profile to use (or current profile)
            output_file: Where to save audio (or temp file)
            
        Returns:
            Path to generated audio file
        """
        if profile is None:
            profile = self.current_profile
        
        # Check cache
        cache_key = f"{text}_{profile.tone.value}_{profile.speed}_{profile.pitch}"
        if cache_key in self.voice_cache:
            logger.debug(f"Using cached audio for: {text[:30]}...")
            return self.voice_cache[cache_key]
        
        # Prepare output file
        if output_file is None:
            output_file = Path(tempfile.mktemp(suffix='.wav'))
        
        # Generate based on available engine
        if self.tts_engine == 'espeak-ng' and self.available_engines.get('espeak-ng'):
            self._generate_espeak(text, profile, output_file)
        elif self.tts_engine == 'piper' and self.available_engines.get('piper'):
            self._generate_piper(text, profile, output_file)
        elif self.tts_engine == 'festival' and self.available_engines.get('festival'):
            self._generate_festival(text, profile, output_file)
        else:
            logger.warning(f"TTS engine {self.tts_engine} not available")
            return None
        
        # Cache the result
        self.voice_cache[cache_key] = output_file
        
        return output_file
    
    def _generate_espeak(self, text: str, profile: VoiceProfile, output_file: Path):
        """Generate speech using espeak-ng"""
        # Convert profile to espeak parameters
        speed_wpm = int(120 + (profile.speed - 1.0) * 80)  # 40-200 wpm
        pitch = int(50 + (profile.pitch - 1.0) * 50)  # 0-99
        amplitude = int(profile.volume * 200)  # 0-200
        
        # Add voice variant based on tone
        voice_variant = {
            VoiceTone.CALM: "+f3",
            VoiceTone.ENCOURAGING: "+f4",
            VoiceTone.EFFICIENT: "+m3",
            VoiceTone.PATIENT: "+f2",
            VoiceTone.CELEBRATORY: "+f5",
            VoiceTone.GENTLE: "+f1",
            VoiceTone.FOCUSED: "+m4"
        }.get(profile.tone, "+f3")
        
        cmd = [
            'espeak-ng',
            '-s', str(speed_wpm),
            '-p', str(pitch),
            '-a', str(amplitude),
            '-v', f'en{voice_variant}',
            '-w', str(output_file),
            text
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.debug(f"Generated speech with espeak-ng: {output_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate speech: {e}")
    
    def _generate_piper(self, text: str, profile: VoiceProfile, output_file: Path):
        """Generate speech using piper (neural TTS)"""
        # Piper uses different models for different voices
        model = {
            VoiceTone.CALM: "en_US-amy-low",
            VoiceTone.ENCOURAGING: "en_US-kusal-medium",
            VoiceTone.EFFICIENT: "en_US-ryan-high",
            VoiceTone.PATIENT: "en_US-amy-medium",
            VoiceTone.CELEBRATORY: "en_US-kusal-high",
            VoiceTone.GENTLE: "en_US-amy-low",
            VoiceTone.FOCUSED: "en_US-ryan-medium"
        }.get(profile.tone, "en_US-amy-medium")
        
        # Piper doesn't support all parameters, but we can adjust the text
        adjusted_text = self._add_ssml_hints(text, profile)
        
        cmd = [
            'piper',
            '--model', model,
            '--output_file', str(output_file)
        ]
        
        try:
            result = subprocess.run(cmd, input=adjusted_text, 
                                  text=True, capture_output=True, check=True)
            logger.debug(f"Generated speech with piper: {output_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate speech with piper: {e}")
    
    def _generate_festival(self, text: str, profile: VoiceProfile, output_file: Path):
        """Generate speech using festival"""
        # Festival script for voice synthesis
        script = f"""
(Parameter.set 'Duration_Stretch {1.0 / profile.speed})
(Parameter.set 'Int_Target_Method Int_Targets_Linear)
(Parameter.set 'Int_Target_F0_Mean {100 * profile.pitch})
(Parameter.set 'Int_Target_F0_Std {15 * profile.emphasis_level})

(set! utt1 (Utterance Text "{text}"))
(utt.synth utt1)
(utt.save.wave utt1 "{output_file}")
"""
        
        try:
            subprocess.run(['festival', '-b'], input=script, 
                         text=True, capture_output=True, check=True)
            logger.debug(f"Generated speech with festival: {output_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate speech with festival: {e}")
    
    def _add_ssml_hints(self, text: str, profile: VoiceProfile) -> str:
        """
        Add SSML-like hints to text for better prosody
        (Poor man's SSML for engines that don't support it)
        """
        # Add pauses
        if profile.pause_length > 0.5:
            text = text.replace('. ', '... ')
            text = text.replace('? ', '?.. ')
        
        # Add emphasis
        if profile.emphasis_level > 0.7:
            # Emphasize important words
            important_words = ['important', 'critical', 'essential', 'must', 'need']
            for word in important_words:
                text = text.replace(word, f"**{word}**")
        
        return text
    
    def speak_with_emotion(self, 
                          text: str, 
                          persona: DynamicPersona,
                          play_audio: bool = True) -> Optional[Path]:
        """
        Main method: Speak text with appropriate emotional tone
        
        Args:
            text: What to say
            persona: User's persona with emotional state
            play_audio: Whether to play immediately
            
        Returns:
            Path to audio file if generated
        """
        # Adapt voice to persona
        profile = self.adapt_to_persona(persona)
        
        # Modify text based on emotional state
        text = self._adapt_text_content(text, persona)
        
        # Generate speech
        audio_file = self.generate_speech(text, profile)
        
        if audio_file and play_audio:
            self._play_audio(audio_file)
        
        return audio_file
    
    def _adapt_text_content(self, text: str, persona: DynamicPersona) -> str:
        """
        Adapt the actual content based on emotional state
        Not just how it's said, but what is said
        """
        # Add emotional prefixes based on state
        if persona.current_mood == EmotionalState.FRUSTRATED:
            if not text.startswith(("I understand", "Let me", "Don't worry")):
                text = "I understand this can be frustrating. " + text
        
        elif persona.current_mood == EmotionalState.CONFUSED:
            if not text.startswith(("Let me", "Here's")):
                text = "Let me explain this step by step. " + text
        
        elif persona.current_mood == EmotionalState.SATISFIED:
            if not text.startswith(("Great", "Excellent", "Perfect")):
                text = "Great job! " + text
        
        elif persona.current_mood == EmotionalState.LEARNING:
            if not text.startswith(("Here's", "Let's explore")):
                text = "Here's something interesting. " + text
        
        # Add appropriate endings
        if persona.frustration_level > 0.7:
            if not text.endswith(("help", "?", "!")):
                text += " Let me know if you need more help."
        
        elif persona.confidence_level > 0.8:
            if not text.endswith(("!", ".")):
                text += " You're doing great!"
        
        return text
    
    def _play_audio(self, audio_file: Path):
        """Play audio file using available player"""
        players = ['aplay', 'paplay', 'play', 'afplay']  # Linux/macOS options
        
        for player in players:
            try:
                subprocess.run([player, str(audio_file)], 
                             capture_output=True, check=True)
                logger.debug(f"Played audio with {player}")
                return
            except:
                continue
        
        logger.warning("No audio player found to play speech")
    
    def get_voice_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about voice adaptation patterns
        Useful for understanding how the system is adapting
        """
        return {
            'current_tone': self.current_profile.tone.value,
            'current_speed': self.current_profile.speed,
            'current_warmth': self.current_profile.warmth,
            'available_engines': self.available_engines,
            'active_engine': self.tts_engine,
            'cache_size': len(self.voice_cache),
            'profiles_available': len(VOICE_PROFILES)
        }