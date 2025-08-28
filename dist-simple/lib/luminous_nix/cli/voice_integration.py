#!/usr/bin/env python3
"""
🎙️ Voice Integration for CLI
Integrates adaptive voice into CLI responses
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio

from luminous_nix.voice.unified_voice import UnifiedVoiceSystem
from luminous_nix.consciousness.adaptive_persona import (
    PersonaLearningEngine,
    DynamicPersona,
    EmotionalState,
    Interaction
)

logger = logging.getLogger(__name__)


class VoiceEnabledCLI:
    """
    CLI with integrated adaptive voice responses
    Voice changes tone based on user's emotional state
    """
    
    def __init__(self, 
                 enable_voice: bool = True,
                 tts_engine: str = "espeak-ng",
                 auto_speak: bool = False):
        """
        Initialize voice-enabled CLI
        
        Args:
            enable_voice: Whether to enable voice output
            tts_engine: Which TTS engine to use
            auto_speak: Whether to automatically speak all responses
        """
        self.enable_voice = enable_voice
        self.auto_speak = auto_speak
        
        if enable_voice:
            self.voice_system = UnifiedVoiceSystem(tts_engine=tts_engine)
            self.persona_system = PersonaLearningEngine()
        else:
            self.voice_system = None
            self.persona_system = None
        
        self.current_persona = None
        self.voice_queue = asyncio.Queue() if enable_voice else None
    
    def respond(self, 
                text: str, 
                user_id: str = "default",
                speak: Optional[bool] = None) -> str:
        """
        Respond to user with adaptive voice
        
        Args:
            text: Response text
            user_id: User identifier
            speak: Override auto_speak setting
            
        Returns:
            The response text (possibly modified for voice)
        """
        if not self.enable_voice:
            return text
        
        # Get or create persona
        if self.current_persona is None or self.current_persona.user_id != user_id:
            self.current_persona = self.persona_system.get_or_create_persona(user_id)
        
        # Adapt voice to persona
        voice_profile = self.voice_system.adapt_to_persona(self.current_persona)
        
        # Adapt text content based on emotional state
        adapted_text = self._adapt_response_text(text, self.current_persona)
        
        # Speak if requested
        should_speak = speak if speak is not None else self.auto_speak
        if should_speak:
            self.voice_system.speak_with_emotion(
                adapted_text,
                self.current_persona,
                play_audio=True
            )
        
        return adapted_text
    
    def _adapt_response_text(self, text: str, persona: DynamicPersona) -> str:
        """
        Adapt response text based on persona state
        More than just voice - changes what we say
        """
        # Add appropriate formatting for different states
        if persona.current_mood == EmotionalState.FRUSTRATED:
            # Be extra helpful
            if "error" in text.lower():
                text = f"I see there's an issue. {text} Don't worry, we'll figure this out together."
            elif "failed" in text.lower():
                text = f"Something didn't work as expected. {text} Let's try a different approach."
        
        elif persona.current_mood == EmotionalState.CONFUSED:
            # Add more explanation
            if ":" in text and not text.startswith("Let me"):
                text = f"Let me break this down for you. {text}"
            
        elif persona.current_mood == EmotionalState.LEARNING:
            # Add educational context
            if any(cmd in text.lower() for cmd in ["install", "configure", "build"]):
                text = f"Here's what's happening: {text}"
        
        elif persona.current_mood == EmotionalState.SATISFIED:
            # Celebrate success
            if any(word in text.lower() for word in ["complete", "success", "installed"]):
                text = f"🎉 {text} Well done!"
        
        elif persona.current_mood == EmotionalState.RUSHED:
            # Be concise
            # Remove unnecessary words
            text = text.replace("Let me explain", "").strip()
            text = text.replace("Here's what's happening:", "").strip()
        
        # Adjust verbosity based on preference
        if persona.preferred_verbosity < 0.3:
            # Ultra-concise
            text = self._make_concise(text)
        elif persona.preferred_verbosity > 0.7:
            # Add detail
            text = self._add_detail(text)
        
        return text
    
    def _make_concise(self, text: str) -> str:
        """Make text more concise for impatient users"""
        # Remove filler phrases
        concise_text = text
        filler_phrases = [
            "Let me explain ",
            "Here's what's happening: ",
            "I'll help you ",
            "We need to ",
            "You can ",
            "This will "
        ]
        
        for phrase in filler_phrases:
            concise_text = concise_text.replace(phrase, "")
        
        # Shorten common phrases
        replacements = {
            "installation": "install",
            "configuration": "config",
            "successfully": "✓",
            "completed": "done",
            "processing": "...",
        }
        
        for long_form, short_form in replacements.items():
            concise_text = concise_text.replace(long_form, short_form)
        
        return concise_text.strip()
    
    def _add_detail(self, text: str) -> str:
        """Add more detail for users who prefer verbosity"""
        detailed_text = text
        
        # Add explanations for commands
        if "nix-env -iA" in text:
            detailed_text += " (This installs the package system-wide)"
        elif "nix-shell" in text:
            detailed_text += " (This creates a temporary development environment)"
        elif "nixos-rebuild" in text:
            detailed_text += " (This rebuilds your entire system configuration)"
        
        return detailed_text
    
    def update_emotional_state(self, 
                              user_id: str,
                              interaction_type: str,
                              success: bool):
        """
        Update user's emotional state based on interaction
        
        Args:
            user_id: User identifier
            interaction_type: Type of interaction (command, error, etc)
            success: Whether interaction was successful
        """
        if not self.enable_voice:
            return
        
        # Get persona
        if self.current_persona is None or self.current_persona.user_id != user_id:
            self.current_persona = self.persona_system.get_or_create_persona(user_id)
        
        # Update based on interaction
        from datetime import datetime
        if interaction_type == "error":
            interaction = Interaction(
                timestamp=datetime.now(),
                command="error",
                success=False,
                response_time_ms=0,
                error_message="User experienced an error"
            )
            self.persona_system.learn_from_interaction(user_id, interaction)
        elif interaction_type == "command":
            interaction = Interaction(
                timestamp=datetime.now(),
                command="command",
                success=success,
                response_time_ms=0
            )
            self.persona_system.learn_from_interaction(user_id, interaction)
    
    def speak_notification(self, 
                          message: str,
                          urgency: str = "normal",
                          user_id: str = "default"):
        """
        Speak a notification with appropriate tone
        
        Args:
            message: Notification message
            urgency: low, normal, high
            user_id: User identifier
        """
        if not self.enable_voice:
            return
        
        # Get persona
        if self.current_persona is None or self.current_persona.user_id != user_id:
            self.current_persona = self.persona_system.get_or_create_persona(user_id)
        
        # Adjust persona mood for urgency
        original_mood = self.current_persona.current_mood
        
        if urgency == "high":
            self.current_persona.current_mood = EmotionalState.RUSHED
        elif urgency == "low":
            self.current_persona.current_mood = EmotionalState.SATISFIED
        
        # Speak notification
        self.voice_system.speak_with_emotion(
            message,
            self.current_persona,
            play_audio=True
        )
        
        # Restore original mood
        self.current_persona.current_mood = original_mood
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Get current voice system status"""
        if not self.enable_voice:
            return {"enabled": False}
        
        status = {
            "enabled": True,
            "auto_speak": self.auto_speak,
            "voice_analytics": self.voice_system.get_voice_analytics()
        }
        
        if self.current_persona:
            status["current_user"] = self.current_persona.user_id
            status["emotional_state"] = self.current_persona.current_mood.value
            status["frustration_level"] = self.current_persona.frustration_level
            status["confidence_level"] = self.current_persona.confidence_level
        
        return status


# Example integration with main CLI
def integrate_voice_with_cli(cli_instance, enable_voice: bool = True):
    """
    Integrate voice system with existing CLI
    
    Args:
        cli_instance: Existing CLI instance
        enable_voice: Whether to enable voice
    """
    voice_cli = VoiceEnabledCLI(enable_voice=enable_voice)
    
    # Wrap existing response methods
    original_respond = cli_instance.respond if hasattr(cli_instance, 'respond') else None
    
    def voice_respond(text: str, **kwargs):
        # Get user context if available
        user_id = kwargs.get('user_id', 'default')
        
        # Process through voice system
        adapted_text = voice_cli.respond(text, user_id)
        
        # Call original if exists
        if original_respond:
            return original_respond(adapted_text, **kwargs)
        return adapted_text
    
    # Replace method
    cli_instance.respond = voice_respond
    cli_instance.voice_system = voice_cli
    
    return cli_instance


# Standalone test
if __name__ == "__main__":
    # Test voice CLI
    voice_cli = VoiceEnabledCLI(enable_voice=True, auto_speak=False)
    
    # Simulate different user states
    print("Testing voice adaptation for different emotional states...")
    
    # Frustrated user
    voice_cli.current_persona = DynamicPersona(
        user_id="test_frustrated",
        current_mood=EmotionalState.FRUSTRATED,
        frustration_level=0.8
    )
    response = voice_cli.respond("Error: Package not found")
    print(f"Frustrated: {response}")
    
    # Satisfied user
    voice_cli.current_persona = DynamicPersona(
        user_id="test_satisfied",
        current_mood=EmotionalState.SATISFIED,
        confidence_level=0.9
    )
    response = voice_cli.respond("Installation complete")
    print(f"Satisfied: {response}")
    
    # Rushed user
    voice_cli.current_persona = DynamicPersona(
        user_id="test_rushed",
        current_mood=EmotionalState.RUSHED,
        preferred_verbosity=0.2
    )
    response = voice_cli.respond("Let me explain the installation process")
    print(f"Rushed: {response}")
    
    print("\nVoice status:", voice_cli.get_voice_status())