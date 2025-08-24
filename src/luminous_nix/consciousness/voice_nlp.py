#!/usr/bin/env python3
"""
🎙️ Voice-Ready Natural Language Processing
Optimized for spoken commands with context understanding
Handles interruptions, corrections, and conversational flow
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import difflib


class IntentType(Enum):
    """Voice-optimized intent categories"""
    INSTALL = "install"
    SEARCH = "search"
    CONFIGURE = "configure"
    ROLLBACK = "rollback"
    INFO = "info"
    HELP = "help"
    CORRECTION = "correction"
    CONFIRMATION = "confirmation"
    INTERRUPTION = "interruption"
    CLARIFICATION = "clarification"
    GENERAL = "general"


@dataclass
class VoiceIntent:
    """Parsed voice intent with confidence"""
    type: IntentType
    primary_entity: Optional[str]
    secondary_entities: List[str]
    confidence: float
    original_text: str
    normalized_text: str
    context_needed: bool
    suggested_clarification: Optional[str]


class VoiceNLP:
    """
    Natural language processor optimized for voice input
    Handles spoken patterns, corrections, and conversational flow
    """
    
    def __init__(self):
        # Voice-specific patterns
        self.filler_words = {
            "um", "uh", "ah", "er", "hmm", "like", "you know", "i mean",
            "basically", "actually", "literally", "right", "okay", "so"
        }
        
        # Common voice corrections
        self.correction_patterns = [
            r"no (?:wait|sorry|actually) (.+)",
            r"i meant (.+)",
            r"scratch that (.+)",
            r"let me (?:try|say) (?:that )?again (.+)",
            r"(?:no|not) (.+) i mean (.+)",
            r"(.+) no wait (.+)"
        ]
        
        # Confirmation patterns
        self.confirmation_patterns = [
            r"^(?:yes|yeah|yep|sure|okay|alright|confirm|do it|go ahead|proceed)$",
            r"^(?:that'?s )?(?:right|correct|it|the one)$",
            r"^(?:sounds good|perfect|great|fine)$"
        ]
        
        # Interruption patterns
        self.interruption_patterns = [
            r"^(?:wait|stop|hold on|pause|cancel|never ?mind)$",
            r"^(?:actually|no|not that)$"
        ]
        
        # Natural language patterns for intents
        self.intent_patterns = {
            IntentType.INSTALL: [
                r"(?:can you |please )?install (.+)",
                r"i (?:need|want) (.+) installed",
                r"(?:set up|setup|add|get me) (.+)",
                r"put (.+) on (?:my |this )?(?:system|computer|machine)",
                r"i'?d like to have (.+)",
                r"(?:download and )?install (.+) for me",
                r"get (.+) working"
            ],
            IntentType.SEARCH: [
                r"(?:search for|find|look for|find me) (.+)",
                r"what (?:packages|programs|software|apps) (?:are there )?for (.+)",
                r"i'?m looking for (?:something for |something like )?(.+)",
                r"(?:is there|do you have) (?:a |an )?(.+)",
                r"show me (?:options for |alternatives to )?(.+)",
                r"what can i use for (.+)",
                r"i need (?:something|a (?:program|tool|app)) (?:for|to do) (.+)"
            ],
            IntentType.CONFIGURE: [
                r"(?:configure|set up|setup|enable) (.+)",
                r"(?:turn on|activate|start) (.+)",
                r"make (.+) (?:work|run|start) (?:automatically|at boot)",
                r"i want (.+) to (?:run|start|work)",
                r"help me (?:configure|set up) (.+)",
                r"change (?:the )?(.+) (?:settings|configuration)"
            ],
            IntentType.ROLLBACK: [
                r"(?:go back|roll back|undo|revert)",
                r"(?:that|this) (?:broke|doesn'?t work|failed)",
                r"(?:restore|get back to) (?:the )?previous (?:version|state|configuration)",
                r"undo (?:the )?(?:last|recent) (?:change|update|install)",
                r"(?:something'?s|it'?s) broken"
            ],
            IntentType.INFO: [
                r"(?:what is|what'?s|explain|tell me about) (.+)",
                r"(?:how do i|how can i|how to) (.+)",
                r"(?:help me understand|teach me about) (.+)",
                r"(?:why|when|where) (?:do i |should i )?(.+)"
            ],
            IntentType.HELP: [
                r"^help$",
                r"i (?:need help|don'?t understand|'?m confused|'?m lost)",
                r"what (?:can you do|are you capable of)",
                r"(?:show me |list )(?:your )?(?:commands|options|features)"
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'package': r"(?:package|program|software|app|tool|application) (?:called |named )?([a-zA-Z0-9_-]+)",
            'service': r"(?:service|daemon|server) (?:called |named )?([a-zA-Z0-9_-]+)",
            'file': r"(?:file|config|configuration) (?:at |in )?([/a-zA-Z0-9._-]+)",
            'version': r"(?:version|release) ([0-9.]+)",
        }
        
        # Context tracking
        self.last_intent = None
        self.last_entity = None
        self.conversation_context = []
        
    def process_voice_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> VoiceIntent:
        """
        Process voice input and extract intent
        Handles natural speech patterns and corrections
        """
        
        # Normalize the input
        normalized = self._normalize_voice_text(text)
        
        # Check for corrections first
        correction = self._detect_correction(normalized)
        if correction:
            # Process the corrected text
            normalized = correction
            intent_type = IntentType.CORRECTION
        else:
            # Check for confirmations and interruptions
            if self._is_confirmation(normalized):
                return self._create_confirmation_intent(text, normalized)
            
            if self._is_interruption(normalized):
                return self._create_interruption_intent(text, normalized)
            
            # Extract main intent
            intent_type = self._extract_intent(normalized)
        
        # Extract entities
        primary_entity, secondary_entities = self._extract_entities(normalized, intent_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(normalized, intent_type, primary_entity)
        
        # Check if context is needed
        context_needed = self._needs_context(intent_type, primary_entity)
        
        # Generate clarification if needed
        clarification = self._generate_clarification(intent_type, primary_entity, confidence)
        
        # Create intent object
        intent = VoiceIntent(
            type=intent_type,
            primary_entity=primary_entity,
            secondary_entities=secondary_entities,
            confidence=confidence,
            original_text=text,
            normalized_text=normalized,
            context_needed=context_needed,
            suggested_clarification=clarification
        )
        
        # Update context
        self._update_context(intent)
        
        return intent
    
    def _normalize_voice_text(self, text: str) -> str:
        """Normalize voice input text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove filler words
        words = text.split()
        filtered = []
        for word in words:
            if word not in self.filler_words:
                filtered.append(word)
        
        # Rejoin
        text = ' '.join(filtered)
        
        # Fix common voice transcription errors
        replacements = {
            "nick's": "nix",
            "next": "nix",
            "necks": "nix",
            "fire fox": "firefox",
            "v s code": "vscode",
            "v code": "vscode",
            "pie thon": "python",
            "python three": "python3",
            "get": "git",  # context-dependent
            "docker rise": "dockerize",
            "pseudo": "sudo",
            "sue do": "sudo",
            "vim": "vim",  # sometimes heard as "them"
            "neo vim": "neovim",
            "knee oh vim": "neovim",
        }
        
        for wrong, right in replacements.items():
            text = text.replace(wrong, right)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _detect_correction(self, text: str) -> Optional[str]:
        """Detect if this is a correction and extract corrected text"""
        for pattern in self.correction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Return the corrected portion
                if len(match.groups()) == 2:
                    # "not X, I mean Y" pattern
                    return match.group(2)
                else:
                    return match.group(1)
        return None
    
    def _is_confirmation(self, text: str) -> bool:
        """Check if this is a confirmation"""
        for pattern in self.confirmation_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_interruption(self, text: str) -> bool:
        """Check if this is an interruption"""
        for pattern in self.interruption_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_intent(self, text: str) -> IntentType:
        """Extract the primary intent from normalized text"""
        best_match = IntentType.GENERAL
        best_score = 0
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate match score based on position and length
                    score = len(match.group(0)) / len(text)
                    if match.start() == 0:
                        score *= 1.5  # Boost for start of sentence
                    
                    if score > best_score:
                        best_score = score
                        best_match = intent_type
        
        # Use context if intent is unclear
        if best_score < 0.3 and self.last_intent:
            # Likely a continuation of previous intent
            return self.last_intent
        
        return best_match
    
    def _extract_entities(self, text: str, intent_type: IntentType) -> Tuple[Optional[str], List[str]]:
        """Extract entities from the text"""
        primary = None
        secondary = []
        
        # Intent-specific extraction
        if intent_type in [IntentType.INSTALL, IntentType.SEARCH, IntentType.CONFIGURE]:
            # Extract package/service name
            for pattern in self.intent_patterns[intent_type]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match and match.groups():
                    primary = match.group(1).strip()
                    break
            
            # Clean up the primary entity
            if primary:
                primary = self._clean_entity(primary)
        
        # Extract additional entities
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match != primary:
                    secondary.append(match)
        
        # Use last entity if none found
        if not primary and self.last_entity and intent_type != IntentType.GENERAL:
            primary = self.last_entity
        
        return primary, secondary
    
    def _clean_entity(self, entity: str) -> str:
        """Clean up extracted entity"""
        # Remove articles and common prefixes
        prefixes = ["a", "an", "the", "some", "any", "that", "this"]
        words = entity.split()
        
        while words and words[0] in prefixes:
            words.pop(0)
        
        # Remove common suffixes
        suffixes = ["please", "thanks", "now", "first", "next"]
        while words and words[-1] in suffixes:
            words.pop()
        
        return ' '.join(words)
    
    def _calculate_confidence(self, text: str, intent_type: IntentType, entity: Optional[str]) -> float:
        """Calculate confidence in the extracted intent"""
        confidence = 0.5  # Base confidence
        
        # Boost for clear intent match
        if intent_type != IntentType.GENERAL:
            confidence += 0.2
        
        # Boost for entity extraction
        if entity:
            confidence += 0.2
        
        # Reduce for very short input
        if len(text.split()) < 3:
            confidence -= 0.1
        
        # Reduce for unclear patterns
        if "maybe" in text or "might" in text or "possibly" in text:
            confidence -= 0.15
        
        # Boost for polite/clear requests
        if "please" in text or "could you" in text:
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def _needs_context(self, intent_type: IntentType, entity: Optional[str]) -> bool:
        """Determine if more context is needed"""
        if intent_type == IntentType.GENERAL:
            return True
        
        if intent_type in [IntentType.INSTALL, IntentType.SEARCH] and not entity:
            return True
        
        if intent_type == IntentType.CORRECTION and not self.last_intent:
            return True
        
        return False
    
    def _generate_clarification(
        self,
        intent_type: IntentType,
        entity: Optional[str],
        confidence: float
    ) -> Optional[str]:
        """Generate a clarification question if needed"""
        if confidence > 0.7:
            return None
        
        if intent_type == IntentType.GENERAL:
            return "What would you like me to help you with?"
        
        if intent_type == IntentType.INSTALL and not entity:
            return "What package would you like to install?"
        
        if intent_type == IntentType.SEARCH and not entity:
            return "What are you looking for?"
        
        if confidence < 0.5:
            return f"Did you want me to {intent_type.value} {entity or 'something'}?"
        
        return None
    
    def _update_context(self, intent: VoiceIntent):
        """Update conversation context"""
        self.last_intent = intent.type
        if intent.primary_entity:
            self.last_entity = intent.primary_entity
        
        # Keep last 5 intents for context
        self.conversation_context.append(intent)
        if len(self.conversation_context) > 5:
            self.conversation_context.pop(0)
    
    def _create_confirmation_intent(self, original: str, normalized: str) -> VoiceIntent:
        """Create a confirmation intent"""
        return VoiceIntent(
            type=IntentType.CONFIRMATION,
            primary_entity=self.last_entity,
            secondary_entities=[],
            confidence=0.95,
            original_text=original,
            normalized_text=normalized,
            context_needed=False,
            suggested_clarification=None
        )
    
    def _create_interruption_intent(self, original: str, normalized: str) -> VoiceIntent:
        """Create an interruption intent"""
        return VoiceIntent(
            type=IntentType.INTERRUPTION,
            primary_entity=None,
            secondary_entities=[],
            confidence=0.95,
            original_text=original,
            normalized_text=normalized,
            context_needed=False,
            suggested_clarification=None
        )
    
    def suggest_voice_response(self, intent: VoiceIntent) -> str:
        """Generate a voice-friendly response suggestion"""
        if intent.confidence < 0.5 and intent.suggested_clarification:
            return intent.suggested_clarification
        
        responses = {
            IntentType.INSTALL: f"I'll install {intent.primary_entity} for you",
            IntentType.SEARCH: f"Let me search for {intent.primary_entity}",
            IntentType.CONFIGURE: f"I'll help you configure {intent.primary_entity}",
            IntentType.ROLLBACK: "I'll roll back to the previous configuration",
            IntentType.INFO: f"Here's information about {intent.primary_entity}",
            IntentType.HELP: "Here's what I can help you with",
            IntentType.CONFIRMATION: "Confirmed, proceeding",
            IntentType.INTERRUPTION: "Stopped, what would you like instead?",
            IntentType.CORRECTION: f"Got it, you meant {intent.primary_entity}",
            IntentType.GENERAL: "How can I help you?"
        }
        
        return responses.get(intent.type, "I'll help you with that")
    
    def get_voice_shortcuts(self) -> Dict[str, str]:
        """Get common voice command shortcuts"""
        return {
            "install firefox": "Install the Firefox web browser",
            "find text editor": "Search for text editing software",
            "rollback": "Undo the last system change",
            "what's installed": "List installed packages",
            "update system": "Update all packages",
            "help": "Show available commands",
            "configure wifi": "Set up wireless networking",
            "enable bluetooth": "Turn on Bluetooth support",
            "install python": "Install Python programming language",
            "search music player": "Find music playback software"
        }


# Global NLP instance
_VOICE_NLP: Optional[VoiceNLP] = None

def get_voice_nlp() -> VoiceNLP:
    """Get or create voice NLP processor"""
    global _VOICE_NLP
    if _VOICE_NLP is None:
        _VOICE_NLP = VoiceNLP()
    return _VOICE_NLP


if __name__ == "__main__":
    # Test voice NLP
    nlp = get_voice_nlp()
    
    print("🎙️ Testing Voice NLP\n")
    print("=" * 60)
    
    # Test various voice inputs
    test_inputs = [
        "um can you install firefox please",
        "i need uh something for editing text",
        "no wait i meant neovim not vim",
        "search for like a music player or something",
        "actually never mind",
        "yes do it",
        "what's nix flakes",
        "help me set up docker",
        "roll back that didn't work",
        "i want python three installed on my system"
    ]
    
    for text in test_inputs:
        print(f"\nInput: '{text}'")
        intent = nlp.process_voice_input(text)
        
        print(f"Intent: {intent.type.value}")
        print(f"Entity: {intent.primary_entity}")
        print(f"Confidence: {intent.confidence:.0%}")
        print(f"Normalized: {intent.normalized_text}")
        
        if intent.suggested_clarification:
            print(f"Clarify: {intent.suggested_clarification}")
        
        response = nlp.suggest_voice_response(intent)
        print(f"Response: {response}")
        print("-" * 40)