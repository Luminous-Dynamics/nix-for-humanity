"""
Natural Language Processing module for Luminous Nix.
Provides intent recognition and entity extraction.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    """Types of intents we can recognize"""
    INSTALL = "install"
    UNINSTALL = "uninstall"
    SEARCH = "search"
    LIST = "list"
    UPDATE = "update"
    CLEANUP = "cleanup"
    CONFIGURE = "configure"
    HELP = "help"
    FLAKE = "flake"  # New: Flake management
    DEVELOP = "develop"  # New: Development environments
    HOME = "home"  # New: Home Manager integration
    CONFIG_PARSE = "config_parse"  # Parse and analyze configuration.nix files
    UNKNOWN = "unknown"

@dataclass
class Intent:
    """Represents a recognized intent with entities"""
    type: IntentType
    confidence: float
    entities: Dict[str, Any]
    raw_query: str

class SimpleIntentRecognizer:
    """
    Simple pattern-based intent recognizer.
    Building with integrity - no shortcuts, just honest pattern matching.
    """
    
    def __init__(self):
        """Initialize with intent patterns"""
        self.patterns = {
            IntentType.INSTALL: [
                "install", "add", "get", "download", "setup"
            ],
            IntentType.UNINSTALL: [
                "remove", "uninstall", "delete", "purge"
            ],
            IntentType.SEARCH: [
                "search", "find", "look for", "query", "what is"
            ],
            IntentType.LIST: [
                "list", "show", "display", "what's installed"
            ],
            IntentType.UPDATE: [
                "update", "upgrade", "rebuild", "switch"
            ],
            IntentType.CLEANUP: [
                "clean", "garbage", "collect", "free space", "cleanup"
            ],
            IntentType.CONFIGURE: [
                "configure", "config", "set", "enable", "disable"
            ],
            IntentType.HELP: [
                "help", "how to", "what does", "explain"
            ],
            IntentType.FLAKE: [
                "flake", "flake.nix", "create flake", "make flake", "generate flake"
            ],
            IntentType.DEVELOP: [
                "develop", "dev environment", "development", "dev shell", "shell"
            ],
            IntentType.HOME: [
                "home", "dotfiles", "home manager", "user config", "personal config",
                "vim config", "tmux config", "shell config", "my config"
            ],
            IntentType.CONFIG_PARSE: [
                "parse config", "check config", "analyze config", "configuration.nix",
                "validate config", "review config", "config file", "nixos config"
            ]
        }
    
    def recognize(self, query: str) -> Intent:
        """
        Recognize intent from natural language query.
        
        Args:
            query: User's natural language input
            
        Returns:
            Intent object with type, confidence, and entities
        """
        query_lower = query.lower()
        
        # Check patterns with priority for longer/more specific matches
        best_match = None
        best_score = 0
        
        for intent_type, keywords in self.patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Score based on keyword length and position
                    score = len(keyword)
                    if query_lower.startswith(keyword):
                        score += 10  # Bonus for start of query
                    
                    if score > best_score:
                        best_score = score
                        best_match = (intent_type, keyword)
        
        if best_match:
            intent_type, keyword = best_match
            entities = self._extract_entities(query_lower, keyword)
            
            return Intent(
                type=intent_type,
                confidence=0.8,  # Simple pattern match confidence
                entities=entities,
                raw_query=query
            )
        
        # No pattern matched
        return Intent(
            type=IntentType.UNKNOWN,
            confidence=0.0,
            entities={},
            raw_query=query
        )
    
    def _extract_entities(self, query: str, keyword: str) -> Dict[str, Any]:
        """
        Extract entities from query.
        
        This is a simple implementation that extracts package names.
        A full implementation would use NER or more sophisticated parsing.
        """
        entities = {}
        
        # Remove the keyword and extract what remains
        remaining = query.replace(keyword, "").strip()
        
        # Clean up common words
        for word in ["the", "a", "an", "my", "for", "please"]:
            remaining = remaining.replace(word, "").strip()
        
        if remaining:
            # Assume the remaining text is the package/target
            entities['target'] = remaining
        
        return entities

# Export main components
__all__ = ['SimpleIntentRecognizer', 'Intent', 'IntentType']