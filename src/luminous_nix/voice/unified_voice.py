"""
🎤 Unified Voice System - Consolidated voice functionality for Luminous Nix

This module consolidates all voice-related functionality into a single system:
- Voice command processing
- Adaptive voice synthesis
- Voice interfaces and backends
- Integration with consciousness systems
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class VoiceCapability(Enum):
    """Voice system capabilities"""
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    COMMAND_PROCESSING = "command_processing"
    ADAPTIVE_SYNTHESIS = "adaptive_synthesis"
    EMOTIONAL_MODULATION = "emotional_modulation"


@dataclass
class VoiceConfig:
    """Unified voice configuration"""
    enabled: bool = False
    backend: str = "piper"  # piper, espeak, cloud
    input_device: Optional[str] = None
    output_device: Optional[str] = None
    language: str = "en"
    voice_model: str = "default"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 0.8
    wake_word: Optional[str] = None
    continuous_listening: bool = False
    adaptive_mode: bool = True


class UnifiedVoiceSystem:
    """
    Unified voice system that consolidates all voice functionality.
    
    This replaces:
    - voice_commands.py (command processing)
    - adaptive_voice.py (emotional adaptation)
    - voice_engine.py (TTS/STT engines)
    - conscious_voice.py (consciousness integration)
    - simple_voice.py (basic voice)
    - voice_backend_piper.py (Piper backend)
    - voice_nlp.py (NLP processing)
    - voice_integration.py (CLI integration)
    
    Features:
    - Unified API for all voice operations
    - Adaptive voice based on user state
    - Command processing with NLP
    - Multiple backend support
    - Consciousness integration
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        """Initialize unified voice system"""
        self.config = config or VoiceConfig()
        self.capabilities: List[VoiceCapability] = []
        self._backends: Dict[str, Any] = {}
        self._command_handlers: Dict[str, Callable] = {}
        self._emotional_state = "neutral"
        self._voice_profile = None
        
        # LLM control integration
        self.llm_control = None  # Will be injected
        self.adaptation_enabled = True  # LLM can control this
        
        if self.config.enabled:
            self._initialize_backends()
            logger.info("🎤 Unified Voice System initialized")
    
    def _initialize_backends(self):
        """Initialize voice backends based on configuration"""
        try:
            if self.config.backend == "piper":
                # PiperBackend now integrated into UnifiedVoiceSystem
                try:
                    from luminous_nix.consciousness.voice_backend_piper import PiperBackend
                    self._backends['tts'] = PiperBackend()
                except ImportError:
                    # Fallback to espeak if PiperBackend not available
                    self._backends['tts'] = self._create_espeak_backend()
                self.capabilities.append(VoiceCapability.TEXT_TO_SPEECH)
            elif self.config.backend == "espeak":
                # Simple fallback
                self._backends['tts'] = self._create_espeak_backend()
                self.capabilities.append(VoiceCapability.TEXT_TO_SPEECH)
            
            # Always enable command processing
            self.capabilities.append(VoiceCapability.COMMAND_PROCESSING)
            
            if self.config.adaptive_mode:
                self.capabilities.append(VoiceCapability.ADAPTIVE_SYNTHESIS)
                self.capabilities.append(VoiceCapability.EMOTIONAL_MODULATION)
                
        except ImportError as e:
            logger.warning(f"Voice backend initialization failed: {e}")
            self.config.enabled = False
    
    def _create_espeak_backend(self):
        """Create simple espeak backend"""
        class EspeakBackend:
            def speak(self, text: str, **kwargs):
                import subprocess
                try:
                    subprocess.run(['espeak', text], check=True)
                except Exception as e:
                    logger.error(f"Espeak failed: {e}")
        return EspeakBackend()
    
    # === Voice Command Processing ===
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process voice command (from voice_commands.py)
        
        Args:
            text: Raw voice command text
            
        Returns:
            Processed command with intent and entities
        """
        # Simple intent extraction
        intent = self._extract_intent(text)
        entities = self._extract_entities(text)
        
        return {
            'text': text,
            'intent': intent,
            'entities': entities,
            'confidence': 0.9,
            'requires_confirmation': self._needs_confirmation(intent)
        }
    
    def _extract_intent(self, text: str) -> str:
        """Extract intent from command text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['install', 'add', 'get']):
            return 'installation'
        elif any(word in text_lower for word in ['search', 'find', 'look for']):
            return 'search'
        elif any(word in text_lower for word in ['help', 'how', 'what']):
            return 'help'
        elif any(word in text_lower for word in ['configure', 'config', 'setup']):
            return 'configuration'
        else:
            return 'general'
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from command text"""
        entities = {}
        
        # Simple package name extraction
        if 'install' in text.lower():
            words = text.split()
            if 'install' in words:
                idx = words.index('install')
                if idx + 1 < len(words):
                    entities['package'] = words[idx + 1]
        
        return entities
    
    def _needs_confirmation(self, intent: str) -> bool:
        """Check if command needs confirmation"""
        return intent in ['installation', 'configuration']
    
    # === Adaptive Voice Synthesis ===
    
    def adapt_voice(self, emotional_state: str, text: str) -> str:
        """
        Adapt voice based on emotional state (from adaptive_voice.py)
        
        Args:
            emotional_state: Current emotional state
            text: Text to speak
            
        Returns:
            Modulated text or settings
        """
        self._emotional_state = emotional_state
        
        # Adjust voice parameters based on emotion
        if emotional_state == "frustrated":
            self.config.speed = 0.9
            self.config.pitch = 0.95
            text = f"I understand this is frustrating. {text}"
        elif emotional_state == "curious":
            self.config.speed = 1.1
            self.config.pitch = 1.05
            text = f"That's interesting! {text}"
        elif emotional_state == "confident":
            self.config.speed = 1.0
            self.config.pitch = 1.0
        
        return text
    
    # === Text-to-Speech ===
    
    def speak(self, text: str, adaptive: bool = True) -> bool:
        """
        Speak text using configured backend
        
        Args:
            text: Text to speak
            adaptive: Apply adaptive modulation
            
        Returns:
            Success status
        """
        if not self.config.enabled:
            logger.debug(f"Voice disabled, would say: {text}")
            return False
        
        try:
            if adaptive and self.config.adaptive_mode:
                text = self.adapt_voice(self._emotional_state, text)
            
            if 'tts' in self._backends:
                self._backends['tts'].speak(
                    text,
                    speed=self.config.speed,
                    pitch=self.config.pitch,
                    volume=self.config.volume
                )
                return True
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
        
        return False
    
    # === Speech-to-Text (Placeholder) ===
    
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen for voice input (placeholder for future STT)
        
        Args:
            timeout: Listening timeout in seconds
            
        Returns:
            Recognized text or None
        """
        if not self.config.enabled:
            return None
        
        # Placeholder - would integrate whisper or other STT
        logger.info("Listening for voice input...")
        return None
    
    # === Integration Helpers ===
    
    def register_command_handler(self, command: str, handler: Callable):
        """Register a command handler"""
        self._command_handlers[command] = handler
    
    def has_capability(self, capability: VoiceCapability) -> bool:
        """Check if system has a capability"""
        return capability in self.capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice system status"""
        return {
            'enabled': self.config.enabled,
            'backend': self.config.backend,
            'capabilities': [c.value for c in self.capabilities],
            'emotional_state': self._emotional_state,
            'adaptive_mode': self.config.adaptive_mode
        }
    
    # === Consciousness Integration ===
    
    def integrate_with_consciousness(self, consciousness_state: Dict[str, Any]):
        """
        Integrate with consciousness system (from conscious_voice.py)
        
        Args:
            consciousness_state: Current consciousness state
        """
        # Adapt based on consciousness level
        awareness_level = consciousness_state.get('awareness_level', 0)
        
        if awareness_level > 0.7:
            self._emotional_state = "enlightened"
            self.config.speed = 0.95  # Slower, more thoughtful
        elif awareness_level > 0.4:
            self._emotional_state = "focused"
            self.config.speed = 1.0
        else:
            self._emotional_state = "scattered"
            self.config.speed = 1.1  # Faster to maintain attention
    
    # === CLI Integration ===
    
    # === LLM Control Methods ===
    
    def set_llm_control(self, llm_control):
        """Connect LLM control layer for AI-driven voice adaptation"""
        self.llm_control = llm_control
        logger.info("🤖 LLM control connected to voice system")
    
    async def request_llm_voice_adaptation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Request LLM guidance for voice adaptation"""
        if not self.llm_control or not self.adaptation_enabled:
            return {"adapted": False}
        
        # Ask LLM for voice adaptation
        from luminous_nix.consciousness.llm_control_layer import SystemCapability
        decision = await self.llm_control.request_llm_decision(
            context=context,
            capability=SystemCapability.VOICE_ADAPTATION
        )
        
        # Apply LLM decision
        if 'tone' in decision.parameters:
            self._emotional_state = decision.parameters['tone']
        if 'speed' in decision.parameters:
            self.config.speed = decision.parameters['speed']
        if 'pitch' in decision.parameters:
            self.config.pitch = decision.parameters['pitch']
        if 'volume' in decision.parameters:
            self.config.volume = decision.parameters['volume']
        
        return {
            "adapted": True,
            "parameters": decision.parameters,
            "reasoning": decision.reasoning
        }
    
    def set_adaptation_enabled(self, enabled: bool):
        """Enable/disable LLM-driven adaptation"""
        self.adaptation_enabled = enabled
        logger.info(f"🎵 Voice adaptation {'enabled' if enabled else 'disabled'}")
    
    def cli_voice_command(self, command: str) -> Dict[str, Any]:
        """
        Process CLI voice command (from voice_integration.py)
        
        Args:
            command: Voice command from CLI
            
        Returns:
            Command result
        """
        # Process the command
        processed = self.process_command(command)
        
        # Execute if handler registered
        if processed['intent'] in self._command_handlers:
            handler = self._command_handlers[processed['intent']]
            result = handler(processed)
            
            # Speak result if enabled
            if self.config.enabled and 'message' in result:
                self.speak(result['message'])
            
            return result
        
        return {
            'status': 'unhandled',
            'intent': processed['intent'],
            'message': f"No handler for {processed['intent']}"
        }


# === Singleton Instance ===

_voice_system: Optional[UnifiedVoiceSystem] = None


def get_voice_system(config: Optional[VoiceConfig] = None) -> UnifiedVoiceSystem:
    """Get or create singleton voice system instance"""
    global _voice_system
    if _voice_system is None:
        _voice_system = UnifiedVoiceSystem(config)
    return _voice_system


# === Convenience Functions ===

def speak(text: str) -> bool:
    """Convenience function to speak text"""
    system = get_voice_system()
    return system.speak(text)


def process_voice_command(command: str) -> Dict[str, Any]:
    """Convenience function to process voice command"""
    system = get_voice_system()
    return system.process_command(command)


def enable_voice(backend: str = "piper"):
    """Enable voice system with specified backend"""
    config = VoiceConfig(enabled=True, backend=backend)
    return get_voice_system(config)


def disable_voice():
    """Disable voice system"""
    system = get_voice_system()
    system.config.enabled = False
    return system