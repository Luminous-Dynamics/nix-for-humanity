"""
Voice Engine Integration for Luminous Nix
Combines Whisper (speech-to-text) and Piper (text-to-speech) for full voice interaction
"""

import subprocess
import tempfile
import wave
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class VoiceConfig:
    """Configuration for voice engine"""
    whisper_model: str = "base"  # tiny, base, small, medium, large
    piper_voice: str = "en_US-amy-medium"  # Piper voice model
    sample_rate: int = 16000
    channels: int = 1
    espeak_fallback: bool = True  # Use espeak-ng if piper unavailable
    
class VoiceEngine:
    """Unified voice engine for speech recognition and synthesis"""
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Check if voice tools are available"""
        self.has_whisper = self._command_exists("whisper")
        self.has_piper = self._command_exists("piper")
        self.has_espeak = self._command_exists("espeak-ng")
        
        if not self.has_whisper:
            logger.warning("Whisper not found. Install with: pip install openai-whisper")
        if not self.has_piper:
            logger.warning("Piper not found. Using espeak-ng fallback")
        if not self.has_espeak and not self.has_piper:
            logger.error("No TTS engine found! Install espeak-ng or piper")
            
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
            
    async def transcribe(self, audio_path: Path) -> Optional[str]:
        """Transcribe audio file to text using Whisper"""
        if not self.has_whisper:
            logger.error("Whisper not available for transcription")
            return None
            
        try:
            # Run whisper transcription
            result = await asyncio.create_subprocess_exec(
                "whisper",
                str(audio_path),
                "--model", self.config.whisper_model,
                "--output_format", "json",
                "--output_dir", "/tmp",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"Whisper failed: {stderr.decode()}")
                return None
                
            # Read the JSON output
            json_path = Path("/tmp") / f"{audio_path.stem}.json"
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                    return data.get("text", "").strip()
                    
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
            
    async def speak(self, text: str, output_path: Optional[Path] = None) -> bool:
        """Convert text to speech using Piper or espeak-ng"""
        if self.has_piper:
            return await self._speak_piper(text, output_path)
        elif self.has_espeak and self.config.espeak_fallback:
            return await self._speak_espeak(text, output_path)
        else:
            logger.error("No TTS engine available")
            return False
            
    async def _speak_piper(self, text: str, output_path: Optional[Path] = None) -> bool:
        """Use Piper for high-quality neural TTS"""
        try:
            output = output_path or Path(tempfile.mktemp(suffix=".wav"))
            
            # Piper command
            process = await asyncio.create_subprocess_exec(
                "piper",
                "--model", self.config.piper_voice,
                "--output_file", str(output),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=text.encode())
            
            if process.returncode != 0:
                logger.error(f"Piper failed: {stderr.decode()}")
                return False
                
            # Play the audio if no output path specified
            if not output_path:
                await self._play_audio(output)
                output.unlink()  # Clean up temp file
                
            return True
            
        except Exception as e:
            logger.error(f"Piper TTS error: {e}")
            return False
            
    async def _speak_espeak(self, text: str, output_path: Optional[Path] = None) -> bool:
        """Use espeak-ng as fallback TTS"""
        try:
            args = ["espeak-ng"]
            
            if output_path:
                args.extend(["-w", str(output_path)])
                
            args.append(text)
            
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"espeak-ng failed: {stderr.decode()}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"espeak-ng TTS error: {e}")
            return False
            
    async def _play_audio(self, audio_path: Path):
        """Play audio file using available player"""
        players = ["aplay", "paplay", "ffplay"]
        
        for player in players:
            if self._command_exists(player):
                try:
                    process = await asyncio.create_subprocess_exec(
                        player,
                        str(audio_path),
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL
                    )
                    await process.communicate()
                    return
                except:
                    continue
                    
        logger.warning("No audio player found")
        
    async def interactive_session(self):
        """Run an interactive voice session"""
        print("🎤 Voice interaction ready! Press Ctrl+C to exit")
        print("Say 'Hey Nix' to activate...")
        
        # This would integrate with actual microphone input
        # For now, it's a placeholder for the full implementation
        pass


class VoicePersonaAdapter:
    """Adapt voice settings based on user persona"""
    
    PERSONA_VOICES = {
        "grandma_rose": {
            "speed": 0.9,  # Slower speech
            "pitch": 1.1,  # Slightly higher pitch
            "voice": "en_US-amy-medium",  # Friendly female voice
        },
        "maya_lightning": {
            "speed": 1.3,  # Faster speech
            "pitch": 1.0,
            "voice": "en_US-danny-low",  # Energetic voice
        },
        "dr_sarah_precise": {
            "speed": 1.0,
            "pitch": 0.95,
            "voice": "en_US-kathleen-low",  # Professional voice
        },
        "default": {
            "speed": 1.0,
            "pitch": 1.0,
            "voice": "en_US-amy-medium",
        }
    }
    
    @classmethod
    def get_voice_config(cls, persona: str) -> Dict[str, Any]:
        """Get voice configuration for a specific persona"""
        return cls.PERSONA_VOICES.get(persona, cls.PERSONA_VOICES["default"])
        
    @classmethod
    def adapt_text_for_persona(cls, text: str, persona: str) -> str:
        """Adapt text style for persona before TTS"""
        if persona == "grandma_rose":
            # Add gentle pauses and warmth
            text = text.replace(".", "... ")
            text = text.replace("!", "! ")
            
        elif persona == "maya_lightning":
            # Make it snappier
            text = text.replace("...", "!")
            
        return text


# Integration with Luminous Nix consciousness
async def voice_conscious_interaction(consciousness, voice_engine: VoiceEngine):
    """Voice-enabled conscious interaction"""
    
    # Example of voice-driven workflow
    print("🎙️ Listening for your command...")
    
    # In real implementation, this would capture from microphone
    # For now, we'll simulate with a test audio file
    test_audio = Path("/tmp/test_command.wav")
    
    if test_audio.exists():
        # Transcribe user's voice
        user_text = await voice_engine.transcribe(test_audio)
        
        if user_text:
            print(f"📝 You said: {user_text}")
            
            # Process through consciousness
            result = consciousness.process_intent(
                intent=user_text,
                context={"interface": "voice"},
                persona="grandma_rose"  # Could be detected from voice
            )
            
            # Speak the response
            response_text = result.get("response", "I understand.")
            print(f"🗣️ Nix says: {response_text}")
            
            await voice_engine.speak(response_text)
            
    else:
        # Fallback to text interaction
        print("No audio input detected, falling back to text mode")