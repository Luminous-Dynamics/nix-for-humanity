#!/usr/bin/env python3
"""
🎤 Voice Command System - Natural language voice control for NixOS

This module implements comprehensive voice command processing with:
- Natural language understanding
- Command shortcuts
- Context-aware responses
- Accessibility features
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CommandCategory(Enum):
    """Categories of voice commands"""
    INSTALLATION = "installation"
    SEARCH = "search"
    SYSTEM = "system"
    HELP = "help"
    CONFIGURATION = "configuration"
    NAVIGATION = "navigation"
    ACCESSIBILITY = "accessibility"
    META = "meta"  # Commands about the system itself


@dataclass
class VoiceCommand:
    """Structured voice command"""
    text: str
    category: CommandCategory
    intent: str
    entities: Dict[str, Any]
    confidence: float = 1.0
    requires_confirmation: bool = False
    
    def __getitem__(self, key: str):
        """Allow dictionary-style access for compatibility"""
        if key == 'category':
            return self.category.value
        elif key == 'intent':
            return self.intent
        elif key == 'text':
            return self.text
        elif key == 'entities':
            return self.entities
        elif key == 'confidence':
            return self.confidence
        elif key == 'requires_confirmation':
            return self.requires_confirmation
        else:
            raise KeyError(f"Unknown key: {key}")


class VoiceCommandProcessor:
    """
    Process natural language voice commands into structured intents.
    
    This enables users to speak naturally and have their intent understood.
    """
    
    def __init__(self):
        """Initialize voice command processor"""
        # Command patterns mapped to intents
        self.command_patterns = self._build_command_patterns()
        
        # Shortcuts for common commands
        self.shortcuts = self._build_shortcuts()
        
        # Accessibility commands
        self.accessibility_commands = self._build_accessibility_commands()
        
        logger.info("🎯 Voice command processor initialized")
    
    def _build_command_patterns(self) -> List[Tuple[re.Pattern, CommandCategory, str, bool]]:
        """Build regex patterns for command recognition"""
        patterns = []
        
        # Installation commands
        patterns.extend([
            (re.compile(r"install\s+(.+)", re.I), CommandCategory.INSTALLATION, "install", False),
            (re.compile(r"get\s+me\s+(.+)", re.I), CommandCategory.INSTALLATION, "install", False),
            (re.compile(r"i\s+need\s+(.+)", re.I), CommandCategory.INSTALLATION, "install", False),
            (re.compile(r"set\s+up\s+(.+)", re.I), CommandCategory.INSTALLATION, "install", False),
        ])
        
        # Search commands
        patterns.extend([
            (re.compile(r"search\s+for\s+(.+)", re.I), CommandCategory.SEARCH, "search", False),
            (re.compile(r"find\s+(.+)", re.I), CommandCategory.SEARCH, "search", False),
            (re.compile(r"look\s+for\s+(.+)", re.I), CommandCategory.SEARCH, "search", False),
            (re.compile(r"what\s+(.+)\s+are\s+available", re.I), CommandCategory.SEARCH, "search", False),
        ])
        
        # System commands
        patterns.extend([
            (re.compile(r"update\s+(?:my\s+)?(?:system|computer)", re.I), CommandCategory.SYSTEM, "update", True),
            (re.compile(r"check\s+for\s+updates", re.I), CommandCategory.SYSTEM, "check_updates", False),
            (re.compile(r"restart\s+(?:my\s+)?(?:system|computer)", re.I), CommandCategory.SYSTEM, "restart", True),
            (re.compile(r"shut\s*down", re.I), CommandCategory.SYSTEM, "shutdown", True),
            (re.compile(r"how\s+much\s+(?:disk\s+)?space", re.I), CommandCategory.SYSTEM, "disk_space", False),
            (re.compile(r"system\s+health", re.I), CommandCategory.SYSTEM, "health_check", False),
        ])
        
        # Configuration commands
        patterns.extend([
            (re.compile(r"configure\s+(.+)", re.I), CommandCategory.CONFIGURATION, "configure", False),
            (re.compile(r"set\s+up\s+(.+)\s+config", re.I), CommandCategory.CONFIGURATION, "configure", False),
            (re.compile(r"change\s+(.+)\s+settings", re.I), CommandCategory.CONFIGURATION, "configure", False),
            (re.compile(r"enable\s+(.+)", re.I), CommandCategory.CONFIGURATION, "enable", False),
            (re.compile(r"disable\s+(.+)", re.I), CommandCategory.CONFIGURATION, "disable", False),
        ])
        
        # Help commands
        patterns.extend([
            (re.compile(r"help", re.I), CommandCategory.HELP, "help", False),
            (re.compile(r"what\s+can\s+you\s+do", re.I), CommandCategory.HELP, "capabilities", False),
            (re.compile(r"explain\s+(.+)", re.I), CommandCategory.HELP, "explain", False),
            (re.compile(r"how\s+(?:do\s+i|to)\s+(.+)", re.I), CommandCategory.HELP, "howto", False),
        ])
        
        # Meta commands
        patterns.extend([
            (re.compile(r"stop", re.I), CommandCategory.META, "stop", False),
            (re.compile(r"cancel", re.I), CommandCategory.META, "cancel", False),
            (re.compile(r"repeat", re.I), CommandCategory.META, "repeat", False),
            (re.compile(r"louder", re.I), CommandCategory.META, "volume_up", False),
            (re.compile(r"quieter|softer", re.I), CommandCategory.META, "volume_down", False),
            (re.compile(r"slower", re.I), CommandCategory.META, "speed_down", False),
            (re.compile(r"faster", re.I), CommandCategory.META, "speed_up", False),
        ])
        
        return patterns
    
    def _build_shortcuts(self) -> Dict[str, VoiceCommand]:
        """Build shortcut commands for quick access"""
        return {
            "firefox": VoiceCommand(
                text="firefox",
                category=CommandCategory.INSTALLATION,
                intent="install",
                entities={"package": "firefox"}
            ),
            "browser": VoiceCommand(
                text="browser",
                category=CommandCategory.SEARCH,
                intent="search",
                entities={"query": "web browser"}
            ),
            "editor": VoiceCommand(
                text="editor",
                category=CommandCategory.SEARCH,
                intent="search",
                entities={"query": "text editor"}
            ),
            "update": VoiceCommand(
                text="update",
                category=CommandCategory.SYSTEM,
                intent="update",
                entities={},
                requires_confirmation=True
            ),
            "help": VoiceCommand(
                text="help",
                category=CommandCategory.HELP,
                intent="help",
                entities={}
            ),
        }
    
    def _build_accessibility_commands(self) -> Dict[str, VoiceCommand]:
        """Build accessibility-specific commands"""
        return {
            "speak slower": VoiceCommand(
                text="speak slower",
                category=CommandCategory.ACCESSIBILITY,
                intent="adjust_speech_rate",
                entities={"direction": "slower"}
            ),
            "speak faster": VoiceCommand(
                text="speak faster",
                category=CommandCategory.ACCESSIBILITY,
                intent="adjust_speech_rate",
                entities={"direction": "faster"}
            ),
            "louder please": VoiceCommand(
                text="louder please",
                category=CommandCategory.ACCESSIBILITY,
                intent="adjust_volume",
                entities={"direction": "up"}
            ),
            "enable captions": VoiceCommand(
                text="enable captions",
                category=CommandCategory.ACCESSIBILITY,
                intent="toggle_captions",
                entities={"state": "on"}
            ),
            "high contrast": VoiceCommand(
                text="high contrast",
                category=CommandCategory.ACCESSIBILITY,
                intent="toggle_contrast",
                entities={"state": "high"}
            ),
            "screen reader mode": VoiceCommand(
                text="screen reader mode",
                category=CommandCategory.ACCESSIBILITY,
                intent="toggle_screen_reader",
                entities={"state": "on"}
            ),
        }
    
    def process(self, text: str) -> Optional[VoiceCommand]:
        """
        Process voice input into structured command.
        
        Args:
            text: Raw voice input text
            
        Returns:
            Structured VoiceCommand or None if not understood
        """
        if not text:
            return None
        
        text = text.strip().lower()
        
        # Check shortcuts first
        if text in self.shortcuts:
            logger.debug(f"Matched shortcut: {text}")
            return self.shortcuts[text]
        
        # Check accessibility commands
        for key, command in self.accessibility_commands.items():
            if key in text:
                logger.debug(f"Matched accessibility command: {key}")
                return command
        
        # Check command patterns
        for pattern, category, intent, requires_confirmation in self.command_patterns:
            match = pattern.search(text)
            if match:
                entities = {}
                
                # Extract matched groups as entities
                if match.groups():
                    if intent in ["install", "search", "configure", "explain", "howto"]:
                        entities["target"] = match.group(1)
                
                command = VoiceCommand(
                    text=text,
                    category=category,
                    intent=intent,
                    entities=entities,
                    requires_confirmation=requires_confirmation
                )
                
                logger.debug(f"Matched pattern: category={category}, intent={intent}")
                return command
        
        # If no pattern matched, try to infer intent
        return self._infer_intent(text)
    
    def _infer_intent(self, text: str) -> Optional[VoiceCommand]:
        """Try to infer intent from unmatched text"""
        # Simple keyword-based inference
        if any(word in text for word in ["install", "get", "download"]):
            # Extract package name (last significant word)
            words = text.split()
            target = words[-1] if words else text
            return VoiceCommand(
                text=text,
                category=CommandCategory.INSTALLATION,
                intent="install",
                entities={"target": target},
                confidence=0.7
            )
        
        if any(word in text for word in ["find", "search", "look"]):
            return VoiceCommand(
                text=text,
                category=CommandCategory.SEARCH,
                intent="search",
                entities={"query": text},
                confidence=0.7
            )
        
        if any(word in text for word in ["help", "how", "what", "explain"]):
            return VoiceCommand(
                text=text,
                category=CommandCategory.HELP,
                intent="help",
                entities={"query": text},
                confidence=0.7
            )
        
        # Unknown command
        logger.debug(f"Could not process command: {text}")
        return None
    
    def get_confirmation_prompt(self, command: VoiceCommand) -> str:
        """Get confirmation prompt for a command"""
        prompts = {
            "update": "This will update your system. Should I proceed?",
            "restart": "This will restart your computer. Are you sure?",
            "shutdown": "This will shut down your computer. Are you sure?",
        }
        
        return prompts.get(
            command.intent,
            f"This will {command.intent}. Should I proceed?"
        )
    
    def format_response(self, command: VoiceCommand, result: Any) -> str:
        """Format command result for voice output"""
        if command.category == CommandCategory.INSTALLATION:
            if command.intent == "install":
                package = command.entities.get("target", "the package")
                return f"I'll help you install {package}."
        
        elif command.category == CommandCategory.SEARCH:
            if command.intent == "search":
                return f"I found several options for you."
        
        elif command.category == CommandCategory.SYSTEM:
            if command.intent == "update":
                return "System update completed successfully."
            elif command.intent == "disk_space":
                return f"You have {result} of free disk space."
        
        elif command.category == CommandCategory.HELP:
            return "Here's what I can help you with."
        
        return "Command completed."


class VoiceShortcuts:
    """
    Manage user-defined voice shortcuts and macros.
    """
    
    def __init__(self):
        """Initialize voice shortcuts system"""
        self.shortcuts = {}
        self.macros = {}
        
    def add_shortcut(self, trigger: str, command: str):
        """Add a voice shortcut"""
        self.shortcuts[trigger.lower()] = command
        logger.info(f"Added shortcut: '{trigger}' -> '{command}'")
    
    def add_macro(self, name: str, commands: List[str]):
        """Add a voice macro (sequence of commands)"""
        self.macros[name.lower()] = commands
        logger.info(f"Added macro: '{name}' with {len(commands)} commands")
    
    def get_command(self, trigger: str) -> Optional[str]:
        """Get command for a trigger"""
        return self.shortcuts.get(trigger.lower())
    
    def get_macro(self, name: str) -> Optional[List[str]]:
        """Get macro commands"""
        return self.macros.get(name.lower())
    
    def execute_macro(self, name: str, executor: Callable) -> List[Any]:
        """Execute a macro with given executor function"""
        commands = self.get_macro(name)
        if not commands:
            return []
        
        results = []
        for command in commands:
            logger.debug(f"Executing macro command: {command}")
            result = executor(command)
            results.append(result)
        
        return results


# Example voice command flows
VOICE_FLOWS = {
    "morning_routine": [
        "check for updates",
        "show system health",
        "check disk space"
    ],
    "dev_setup": [
        "install visual studio code",
        "install git",
        "install docker",
        "configure development environment"
    ],
    "accessibility_setup": [
        "enable screen reader mode",
        "speak slower",
        "enable high contrast",
        "enable captions"
    ]
}


def demonstrate_voice_commands():
    """Demonstrate voice command processing"""
    processor = VoiceCommandProcessor()
    shortcuts = VoiceShortcuts()
    
    # Add some shortcuts
    shortcuts.add_shortcut("morning", "morning_routine")
    shortcuts.add_macro("morning_routine", VOICE_FLOWS["morning_routine"])
    
    print("🎤 Voice Command Processing Demo")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        "install firefox",
        "search for text editor",
        "how much disk space do I have",
        "update my system",
        "help me with wifi",
        "speak slower",
        "morning routine",
        "shutdown"
    ]
    
    for text in test_commands:
        print(f"\nVoice: '{text}'")
        command = processor.process(text)
        
        if command:
            print(f"  Category: {command.category.value}")
            print(f"  Intent: {command.intent}")
            print(f"  Entities: {command.entities}")
            
            if command.requires_confirmation:
                prompt = processor.get_confirmation_prompt(command)
                print(f"  ⚠️  Confirmation needed: {prompt}")
            
            response = processor.format_response(command, "example result")
            print(f"  Response: {response}")
        else:
            print("  ❌ Command not understood")
    
    print("\n" + "=" * 50)
    print("Voice command processing demo complete!")


if __name__ == "__main__":
    demonstrate_voice_commands()