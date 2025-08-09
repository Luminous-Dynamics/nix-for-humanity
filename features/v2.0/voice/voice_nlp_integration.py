#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Voice-NLP Integration for Nix for Humanity
==========================================

This module integrates the Grandma Rose voice interface with the existing
NLP engine and command execution system, providing a complete voice-controlled
NixOS management experience.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from nix_knowledge_engine import NixOSKnowledgeEngine
from command_executor import CommandExecutor
from natural_language_executor import NaturalLanguageExecutor


@dataclass
class VoiceCommand:
    """Represents a voice command with metadata"""
    text: str
    timestamp: datetime
    confidence: float = 1.0
    intent: Optional[Dict] = None
    response: Optional[str] = None
    executed: bool = False
    execution_result: Optional[Dict] = None
    user_feedback: Optional[str] = None


@dataclass
class UserProfile:
    """User profile for personalization"""
    name: str = "User"
    preferred_speed: int = 150  # TTS words per minute
    preferred_volume: float = 0.9
    technical_level: str = "beginner"  # beginner, intermediate, advanced
    common_tasks: List[str] = field(default_factory=list)
    voice_patterns: Dict[str, Any] = field(default_factory=dict)


class VoiceNLPBridge:
    """Bridges voice input with NLP processing and command execution"""
    
    def __init__(self, user_profile: Optional[UserProfile] = None):
        self.profile = user_profile or UserProfile(name="Grandma Rose", technical_level="beginner")
        self.nix_engine = NixOSKnowledgeEngine()
        self.command_executor = CommandExecutor()
        self.nl_executor = NaturalLanguageExecutor()
        
        # Command history for learning
        self.history: List[VoiceCommand] = []
        self.load_history()
        
        # Common mishearings and corrections
        self.voice_corrections = {
            "fire fox": "firefox",
            "goggle chrome": "google chrome",
            "wife eye": "wifi",
            "why fi": "wifi",
            "my computer": "system",
            "the computer": "system"
        }
        
        # Confirmation phrases
        self.confirmation_phrases = {
            "positive": ["yes", "yeah", "sure", "okay", "ok", "please", "go ahead", "do it", "sounds good"],
            "negative": ["no", "nope", "cancel", "stop", "nevermind", "forget it", "not now", "don't"]
        }
    
    def preprocess_voice_text(self, text: str) -> str:
        """Preprocess voice transcription to fix common issues"""
        processed = text.lower().strip()
        
        # Fix common mishearings
        for wrong, correct in self.voice_corrections.items():
            processed = processed.replace(wrong, correct)
        
        # Remove filler words common in speech
        filler_words = ["um", "uh", "hmm", "well", "like", "you know"]
        words = processed.split()
        words = [w for w in words if w not in filler_words]
        processed = " ".join(words)
        
        # Handle punctuation issues from speech
        processed = processed.replace(" ?", "?").replace(" .", ".")
        
        return processed
    
    async def process_voice_command(self, voice_text: str, confidence: float = 1.0) -> Dict[str, Any]:
        """Process a voice command through the full pipeline"""
        
        # Create command object
        command = VoiceCommand(
            text=voice_text,
            timestamp=datetime.now(),
            confidence=confidence
        )
        
        # Preprocess voice text
        processed_text = self.preprocess_voice_text(voice_text)
        logger.info(f"Processing voice command: '{voice_text}' -> '{processed_text}'")
        
        # Extract intent
        command.intent = self.nix_engine.extract_intent(processed_text)
        
        # Check if this needs confirmation based on user level
        needs_confirmation = self._needs_confirmation(command.intent)
        
        # Get solution and format response
        solution = self.nix_engine.get_solution(command.intent)
        base_response = self.nix_engine.format_response(command.intent, solution)
        
        # Adapt response for voice and user level
        command.response = self._adapt_response_for_voice(base_response, command.intent)
        
        # Add to history
        self.history.append(command)
        
        return {
            "command": command,
            "needs_confirmation": needs_confirmation,
            "can_execute": solution.get('found', False),
            "processed_text": processed_text
        }
    
    def _needs_confirmation(self, intent: Dict) -> bool:
        """Determine if a command needs confirmation based on user profile"""
        # Always confirm for beginners
        if self.profile.technical_level == "beginner":
            return True
        
        # System-changing operations always need confirmation
        dangerous_actions = ['update_system', 'rollback_system', 'remove_package']
        if intent.get('action') in dangerous_actions:
            return True
        
        # Check user's common tasks - don't confirm if it's routine
        action = intent.get('action')
        if action in self.profile.common_tasks:
            return False
        
        return self.profile.technical_level == "intermediate"
    
    def _adapt_response_for_voice(self, response: str, intent: Dict) -> str:
        """Adapt response for voice output based on user profile"""
        
        if self.profile.technical_level == "beginner":
            # Simplify technical terms
            replacements = {
                "environment.systemPackages": "your computer's program list",
                "configuration.nix": "your computer's settings file",
                "nixos-rebuild switch": "updating your computer",
                "declarative": "permanent",
                "imperative": "temporary",
                "generation": "backup point",
                "rollback": "go back to previous version"
            }
            
            for tech, simple in replacements.items():
                response = response.replace(tech, simple)
            
            # Add reassuring language
            if intent.get('action') == 'install_package':
                response += "\n\nDon't worry, this is completely safe and reversible!"
            elif intent.get('action') == 'update_system':
                response += "\n\nI'll make sure everything stays working properly."
        
        # Make response more conversational
        response = response.replace("```", "").replace("`", "")  # Remove code formatting
        
        return response
    
    async def execute_confirmed_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute a confirmed voice command"""
        
        try:
            # Use the natural language executor for better integration
            result = await self.nl_executor.execute_intent(command.intent)
            
            command.executed = True
            command.execution_result = result
            
            # Learn from successful execution
            if result.get('success'):
                self.profile.common_tasks.append(command.intent.get('action'))
                self.save_profile()
            
            return {
                "success": result.get('success', False),
                "output": result.get('output', ''),
                "message": self._create_voice_result_message(result, command.intent)
            }
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I'm sorry, I encountered an error. Let me try a different approach."
            }
    
    def _create_voice_result_message(self, result: Dict, intent: Dict) -> str:
        """Create a voice-friendly result message"""
        
        if result.get('success'):
            if intent.get('action') == 'install_package':
                package = intent.get('package', 'the program')
                return f"Great! I've successfully installed {package}. You can now find it in your applications menu."
            elif intent.get('action') == 'update_system':
                return "Perfect! Your computer is now up to date and more secure."
            elif intent.get('action') == 'fix_wifi':
                return "Good news! I've reset your network settings. Your WiFi should be working now."
            else:
                return "All done! Everything completed successfully."
        else:
            # Friendly error messages
            error = result.get('error', '')
            if 'not found' in error.lower():
                return "I couldn't find that program. Could you tell me more about what you want to do?"
            elif 'permission' in error.lower():
                return "I need your password to make that change. This is normal for system updates."
            else:
                return "I ran into a small problem. Let me try a different approach, or we can ask for help."
    
    def process_confirmation(self, response: str) -> bool:
        """Process a confirmation response"""
        response_lower = response.lower().strip()
        
        # Check against known phrases
        for phrase in self.confirmation_phrases['positive']:
            if phrase in response_lower:
                return True
                
        for phrase in self.confirmation_phrases['negative']:
            if phrase in response_lower:
                return False
        
        # Default unclear responses based on user level
        if self.profile.technical_level == "beginner":
            # For beginners, unclear means no (safer)
            return False
        else:
            # For others, could check for more context
            return "ok" in response_lower or "alright" in response_lower
    
    def get_voice_suggestions(self, context: str) -> List[str]:
        """Get voice-appropriate command suggestions"""
        
        suggestions = []
        
        if context == "initial":
            if self.profile.technical_level == "beginner":
                suggestions = [
                    "Install Firefox for web browsing",
                    "Check if my computer needs updates",
                    "Help me with my WiFi",
                    "Show me my photos",
                    "Set up video calling"
                ]
            else:
                suggestions = [
                    "Install a new program",
                    "Update my system",
                    "Search for available packages",
                    "Check system status",
                    "Configure development environment"
                ]
        
        elif context == "after_error":
            suggestions = [
                "Try a different approach",
                "Tell me more about what you want to do",
                "Show me similar programs",
                "Check what's already installed"
            ]
        
        return suggestions
    
    def load_history(self):
        """Load command history from disk"""
        history_file = Path("voice_command_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    # Convert to VoiceCommand objects
                    self.history = [VoiceCommand(**cmd) for cmd in data]
            except Exception as e:
                logger.error(f"Error loading history: {e}")
    
    def save_history(self):
        """Save command history to disk"""
        history_file = Path("voice_command_history.json")
        try:
            # Convert to serializable format
            data = []
            for cmd in self.history[-100:]:  # Keep last 100 commands
                cmd_dict = {
                    'text': cmd.text,
                    'timestamp': cmd.timestamp.isoformat(),
                    'confidence': cmd.confidence,
                    'intent': cmd.intent,
                    'response': cmd.response,
                    'executed': cmd.executed,
                    'execution_result': cmd.execution_result
                }
                data.append(cmd_dict)
            
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def save_profile(self):
        """Save user profile"""
        profile_file = Path(f"profile_{self.profile.name.lower().replace(' ', '_')}.json")
        try:
            with open(profile_file, 'w') as f:
                json.dump({
                    'name': self.profile.name,
                    'preferred_speed': self.profile.preferred_speed,
                    'preferred_volume': self.profile.preferred_volume,
                    'technical_level': self.profile.technical_level,
                    'common_tasks': list(set(self.profile.common_tasks[-20:])),  # Keep last 20 unique
                    'voice_patterns': self.profile.voice_patterns
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving profile: {e}")


async def demo_voice_pipeline():
    """Demo the voice-NLP integration"""
    
    # Create Grandma Rose profile
    grandma_profile = UserProfile(
        name="Grandma Rose",
        technical_level="beginner",
        preferred_speed=140,  # Slower speech
        preferred_volume=0.95  # Louder
    )
    
    # Create bridge
    bridge = VoiceNLPBridge(grandma_profile)
    
    # Test commands
    test_commands = [
        "I need to check my email",
        "Install fire fox please",  # Test correction
        "My wife eye isn't working",  # Test correction
        "Update my computer"
    ]
    
    print("🎤 Voice-NLP Integration Demo")
    print("============================\n")
    
    for voice_input in test_commands:
        print(f"🎤 Voice input: '{voice_input}'")
        
        # Process command
        result = await bridge.process_voice_command(voice_input)
        command = result['command']
        
        print(f"🧠 Understood: '{result['processed_text']}'")
        print(f"🎯 Intent: {command.intent}")
        print(f"💬 Response: {command.response}")
        
        if result['needs_confirmation']:
            print("❓ Needs confirmation")
            
            # Simulate confirmation
            if "update" in voice_input.lower():
                print("👵 User says: 'Yes, please update'")
                confirmed = bridge.process_confirmation("yes please")
                
                if confirmed:
                    exec_result = await bridge.execute_confirmed_command(command)
                    print(f"✅ Result: {exec_result['message']}")
        
        print("-" * 50)
    
    # Save history
    bridge.save_history()
    print("\n📝 Command history saved")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_voice_pipeline())