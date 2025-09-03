"""
🌉 Voice-NLP Bridge for Luminous Nix
Seamlessly connects voice input to the existing NLP pipeline
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from ..core.intents import Intent, IntentType
from ..core.backend import LuminousNixBackend
from ..core.responses import Response, ResponseType
from ..consciousness.adaptive_persona import AdaptivePersona
from .sacred_voice_interface import SacredVoiceInterface, VoiceConfig, FlowState

logger = logging.getLogger(__name__)


@dataclass
class VoiceContext:
    """Context for voice interactions"""
    persona: str = "gentle"
    last_command: Optional[str] = None
    last_response: Optional[str] = None
    interaction_count: int = 0
    error_count: int = 0
    success_rate: float = 1.0
    preferred_verbosity: str = "normal"  # minimal, normal, detailed
    voice_shortcuts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.voice_shortcuts is None:
            self.voice_shortcuts = self._default_shortcuts()
    
    def _default_shortcuts(self) -> Dict[str, str]:
        """Default voice command shortcuts"""
        return {
            # Common commands
            "install firefox": "install firefox-esr",
            "install chrome": "install google-chrome",
            "what's installed": "list installed packages",
            "show packages": "list installed packages",
            
            # System commands
            "update system": "nixos-rebuild switch",
            "check updates": "check for system updates",
            "system status": "show system health",
            
            # Voice-specific
            "speak louder": "increase volume",
            "speak softer": "decrease volume",
            "speak faster": "increase speech rate",
            "speak slower": "decrease speech rate",
            "stop talking": "cancel speech",
            
            # Sacred commands
            "take a breath": "sacred pause",
            "focus mode": "enter deep focus",
            "normal mode": "exit deep focus",
        }


class VoiceNLPBridge:
    """
    Bridges voice interface with NLP pipeline
    
    Features:
    - Automatic persona detection from voice patterns
    - Command preprocessing and expansion
    - Response formatting for speech
    - Error recovery with voice-friendly messages
    - Learning from voice interactions
    """
    
    def __init__(self, 
                 backend: Optional[LuminousNixBackend] = None,
                 voice_config: Optional[VoiceConfig] = None):
        self.backend = backend or LuminousNixBackend()
        self.voice = SacredVoiceInterface(voice_config)
        self.context = VoiceContext()
        self.persona = AdaptivePersona()
        
        # Wire up callbacks
        self.voice.on_command = self.process_voice_command
        self.voice.on_state_change = self.handle_state_change
        
        # Statistics
        self.stats = {
            "commands_processed": 0,
            "commands_successful": 0,
            "commands_failed": 0,
            "average_response_time": 0,
            "voice_recognition_accuracy": 0.95,  # Estimated
        }
    
    def process_voice_command(self, text: str) -> str:
        """
        Process voice command through NLP pipeline
        
        Args:
            text: Recognized voice input
            
        Returns:
            Speech-formatted response
        """
        try:
            logger.info(f"Processing voice command: {text}")
            self.context.interaction_count += 1
            self.context.last_command = text
            
            # Preprocess for voice
            processed_text = self._preprocess_voice_input(text)
            
            # Check for voice control commands
            if self._is_voice_control(processed_text):
                return self._handle_voice_control(processed_text)
            
            # Create intent from voice input
            intent = self._voice_to_intent(processed_text)
            
            # Process through backend
            response = self.backend.process(intent)
            
            # Format for speech
            speech_response = self._format_for_speech(response)
            
            # Update context and stats
            self.context.last_response = speech_response
            if response.success:
                self.stats["commands_successful"] += 1
            else:
                self.stats["commands_failed"] += 1
                self.context.error_count += 1
            
            self.stats["commands_processed"] += 1
            self._update_success_rate()
            
            return speech_response
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            self.context.error_count += 1
            return self._format_error_for_speech(e)
    
    def _preprocess_voice_input(self, text: str) -> str:
        """
        Preprocess voice input for better understanding
        
        Handles:
        - Common speech recognition errors
        - Shortcuts and expansions
        - Natural language variations
        """
        processed = text.lower().strip()
        
        # Fix common recognition errors
        replacements = {
            "nixos": "nixos",
            "nix o s": "nixos",
            "nicks os": "nixos",
            "fire fox": "firefox",
            "v s code": "vscode",
            "v s codium": "vscodium",
        }
        
        for wrong, right in replacements.items():
            processed = processed.replace(wrong, right)
        
        # Apply shortcuts
        for shortcut, expansion in self.context.voice_shortcuts.items():
            if processed == shortcut:
                processed = expansion
                logger.debug(f"Expanded shortcut: {shortcut} -> {expansion}")
                break
        
        # Add implicit commands
        if not any(processed.startswith(cmd) for cmd in ["install", "remove", "search", "list", "show"]):
            # Try to infer command
            if "package" in processed or "software" in processed:
                if "find" in processed or "looking for" in processed:
                    processed = f"search {processed}"
                elif "get" in processed or "want" in processed:
                    processed = f"install {processed}"
        
        return processed
    
    def _voice_to_intent(self, text: str) -> Intent:
        """Convert voice input to Intent"""
        # Detect intent type from voice
        intent_type = self._detect_voice_intent_type(text)
        
        # Extract package/query
        query = self._extract_query(text, intent_type)
        
        # Build metadata
        metadata = {
            "source": "voice",
            "persona": self.context.persona,
            "verbosity": self.context.preferred_verbosity,
            "interaction_count": self.context.interaction_count,
        }
        
        return Intent(
            type=intent_type,
            query=query,
            metadata=metadata
        )
    
    def _detect_voice_intent_type(self, text: str) -> IntentType:
        """Detect intent type from voice input"""
        text_lower = text.lower()
        
        # Installation patterns
        if any(word in text_lower for word in ["install", "get", "add", "download"]):
            return IntentType.INSTALL
        
        # Removal patterns
        if any(word in text_lower for word in ["remove", "uninstall", "delete"]):
            return IntentType.REMOVE
        
        # Search patterns
        if any(word in text_lower for word in ["search", "find", "look for", "what is"]):
            return IntentType.SEARCH
        
        # List patterns
        if any(word in text_lower for word in ["list", "show", "what's installed"]):
            return IntentType.LIST
        
        # Configuration patterns
        if any(word in text_lower for word in ["configure", "settings", "config"]):
            return IntentType.CONFIGURE
        
        # Help patterns
        if any(word in text_lower for word in ["help", "how do", "what can"]):
            return IntentType.HELP
        
        # Default to query
        return IntentType.UNKNOWN
    
    def _extract_query(self, text: str, intent_type: IntentType) -> str:
        """Extract the query from voice command"""
        # Remove intent words
        command_words = {
            IntentType.INSTALL: ["install", "get", "add", "download"],
            IntentType.REMOVE: ["remove", "uninstall", "delete"],
            IntentType.SEARCH: ["search", "find", "look for", "search for"],
            IntentType.LIST: ["list", "show", "display"],
        }
        
        query = text.lower()
        if intent_type in command_words:
            for word in command_words[intent_type]:
                query = query.replace(word, "").strip()
        
        # Clean up common filler words
        filler_words = ["please", "can you", "i want", "i need", "to", "the", "a", "an"]
        for filler in filler_words:
            query = query.replace(f" {filler} ", " ").strip()
            if query.startswith(filler + " "):
                query = query[len(filler):].strip()
        
        return query
    
    def _format_for_speech(self, response: Response) -> str:
        """
        Format response for natural speech
        
        Makes responses more conversational and speech-friendly
        """
        if not response.message:
            return "Command processed successfully."
        
        message = response.message
        
        # Apply verbosity settings
        if self.context.preferred_verbosity == "minimal":
            # Just the essentials
            if response.success:
                if "installed" in message.lower():
                    return "Done. Package installed."
                elif "removed" in message.lower():
                    return "Done. Package removed."
                elif "found" in message.lower():
                    # Just list first few results
                    lines = message.split('\n')
                    if len(lines) > 3:
                        return f"Found {len(lines)-1} packages. First one is {lines[1].split()[0] if len(lines) > 1 else 'unknown'}."
                return "Done."
            else:
                return f"Failed. {message.split('.')[0]}."
        
        elif self.context.preferred_verbosity == "detailed":
            # Add extra context
            if response.success:
                message = f"Successfully completed. {message}"
            else:
                message = f"I encountered an issue. {message}"
        
        # Make more conversational
        replacements = {
            "Package": "The package",
            "Error:": "I'm sorry, but",
            "Failed to": "I couldn't",
            "nixos-rebuild": "system rebuild",
            "...": ", ",  # Replace ellipsis with pause
        }
        
        for old, new in replacements.items():
            message = message.replace(old, new)
        
        # Limit length for speech
        if len(message) > 200:
            message = message[:197] + "..."
        
        return message
    
    def _format_error_for_speech(self, error: Exception) -> str:
        """Format error messages for speech"""
        error_str = str(error)
        
        # Simplify technical errors
        if "permission denied" in error_str.lower():
            return "I need administrator permissions for that. Try saying 'sudo' before your command."
        elif "not found" in error_str.lower():
            return "I couldn't find that package. Try a different name or search first."
        elif "network" in error_str.lower():
            return "There seems to be a network issue. Please check your connection."
        else:
            return f"I encountered an error. {error_str[:100]}"
    
    def _is_voice_control(self, text: str) -> bool:
        """Check if command is for voice control"""
        voice_controls = [
            "speak louder", "speak softer", 
            "speak faster", "speak slower",
            "stop talking", "cancel",
            "take a breath", "sacred pause",
            "focus mode", "normal mode",
            "verbose", "minimal", "detailed",
        ]
        return any(control in text.lower() for control in voice_controls)
    
    def _handle_voice_control(self, text: str) -> str:
        """Handle voice control commands"""
        text_lower = text.lower()
        
        # Volume control
        if "louder" in text_lower:
            self.voice.config.voice_volume = min(1.0, self.voice.config.voice_volume + 0.1)
            self.voice.speaker.setProperty('volume', self.voice.config.voice_volume)
            return "Volume increased."
        elif "softer" in text_lower or "quieter" in text_lower:
            self.voice.config.voice_volume = max(0.1, self.voice.config.voice_volume - 0.1)
            self.voice.speaker.setProperty('volume', self.voice.config.voice_volume)
            return "Volume decreased."
        
        # Speed control
        elif "faster" in text_lower:
            self.voice.config.voice_rate = min(300, self.voice.config.voice_rate + 25)
            self.voice.speaker.setProperty('rate', self.voice.config.voice_rate)
            return "Speaking faster now."
        elif "slower" in text_lower:
            self.voice.config.voice_rate = max(100, self.voice.config.voice_rate - 25)
            self.voice.speaker.setProperty('rate', self.voice.config.voice_rate)
            return "Speaking slower now."
        
        # Sacred commands
        elif "breath" in text_lower or "sacred pause" in text_lower:
            self.voice.take_sacred_breath()
            return "Taking a sacred breath..."
        elif "focus mode" in text_lower:
            self.voice.enter_deep_focus()
            return "Entering deep focus mode. I'll be quieter now."
        elif "normal mode" in text_lower:
            self.voice.exit_deep_focus()
            return "Exiting focus mode. Ready for conversation."
        
        # Verbosity control
        elif "verbose" in text_lower or "detailed" in text_lower:
            self.context.preferred_verbosity = "detailed"
            return "I'll be more detailed now."
        elif "minimal" in text_lower or "brief" in text_lower:
            self.context.preferred_verbosity = "minimal"
            return "I'll be brief."
        elif "normal" in text_lower:
            self.context.preferred_verbosity = "normal"
            return "Back to normal verbosity."
        
        return "Voice command not recognized."
    
    def handle_state_change(self, state: FlowState):
        """Handle voice state changes"""
        logger.debug(f"Voice state changed to: {state.value}")
        
        # Could emit events or update UI here
        if state == FlowState.DEEP_FOCUS:
            # Notify other systems to be quieter
            pass
        elif state == FlowState.LISTENING:
            # Could show visual indicator
            pass
    
    def _update_success_rate(self):
        """Update success rate metric"""
        total = self.stats["commands_processed"]
        if total > 0:
            self.context.success_rate = self.stats["commands_successful"] / total
    
    def start(self):
        """Start the voice interface"""
        logger.info("Starting Voice-NLP Bridge")
        
        # Start voice conversation loop
        self.voice.start_conversation_loop()
        
        # Initial greeting
        self.voice.speak(
            "Hello! I'm ready to help you with NixOS. "
            "Just speak naturally, like 'install firefox' or 'search for editors'.",
            interruption_level=InterruptionLevel.NORMAL
        )
    
    def stop(self):
        """Stop the voice interface"""
        logger.info("Stopping Voice-NLP Bridge")
        self.voice.speak("Goodbye!", interruption_level=InterruptionLevel.URGENT)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get voice interaction statistics"""
        return {
            **self.stats,
            "context": {
                "interaction_count": self.context.interaction_count,
                "error_count": self.context.error_count,
                "success_rate": self.context.success_rate,
                "current_verbosity": self.context.preferred_verbosity,
                "current_persona": self.context.persona,
            },
            "voice_config": {
                "volume": self.voice.config.voice_volume,
                "rate": self.voice.config.voice_rate,
                "personality": self.voice.config.voice_personality,
                "flow_protection": self.voice.config.focus_protection,
            }
        }


# Make available at module level
def create_voice_bridge(backend: Optional[LuminousNixBackend] = None,
                        voice_config: Optional[VoiceConfig] = None) -> VoiceNLPBridge:
    """Create a configured voice-NLP bridge"""
    return VoiceNLPBridge(backend, voice_config)