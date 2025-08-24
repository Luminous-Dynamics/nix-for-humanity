"""
Advanced Intent Recognition Pipeline for Natural Language Understanding
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

class Intent(Enum):
    """All possible intents the system can recognize"""
    # Package Management
    INSTALL = "install"
    REMOVE = "remove"
    UPDATE = "update"
    SEARCH = "search"
    LIST = "list"
    
    # System Management
    ROLLBACK = "rollback"
    REBUILD = "rebuild"
    GARBAGE_COLLECT = "garbage_collect"
    REPAIR = "repair"
    
    # Configuration
    CONFIGURE = "configure"
    EDIT_CONFIG = "edit_config"
    SHOW_CONFIG = "show_config"
    
    # Information
    HELP = "help"
    EXPLAIN = "explain"
    STATUS = "status"
    VERSION = "version"
    
    # Development
    CREATE_SHELL = "create_shell"
    BUILD = "build"
    TEST = "test"
    
    # Flakes
    FLAKE_INIT = "flake_init"
    FLAKE_UPDATE = "flake_update"
    FLAKE_CHECK = "flake_check"
    
    # Home Manager
    HOME_INSTALL = "home_install"
    HOME_CONFIG = "home_config"
    
    # Troubleshooting
    DIAGNOSE = "diagnose"
    FIX = "fix"
    CHECK_HEALTH = "check_health"
    
    # Complex
    MULTIPLE = "multiple"
    CONDITIONAL = "conditional"
    UNKNOWN = "unknown"

@dataclass
class Entity:
    """An entity extracted from the query"""
    type: str  # package, config_file, channel, etc.
    value: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntentResult:
    """Result of intent recognition"""
    primary_intent: Intent
    confidence: float
    entities: List[Entity]
    original_query: str
    normalized_query: str
    secondary_intents: List[Intent] = field(default_factory=list)
    context_required: bool = False
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntentRecognitionPipeline:
    """
    Multi-stage intent recognition pipeline
    
    Stages:
    1. Preprocessing - Clean and normalize
    2. Pattern Matching - Rule-based detection
    3. Entity Extraction - Find packages, files, etc.
    4. Context Enhancement - Use conversation history
    5. Confidence Scoring - Rate the recognition
    6. Fallback Strategies - Handle ambiguous cases
    """
    
    def __init__(self, patterns_file: Optional[Path] = None):
        """Initialize the intent recognition pipeline"""
        self.patterns_file = patterns_file
        self.intent_patterns = self._load_patterns()
        self.entity_patterns = self._load_entity_patterns()
        self.compound_patterns = self._load_compound_patterns()
        
        # Learning data
        self.successful_matches = []
        self.failed_matches = []
        
    def _load_patterns(self) -> Dict[Intent, List[Tuple[str, float]]]:
        """Load intent patterns with confidence scores"""
        return {
            Intent.INSTALL: [
                (r'\b(install|add|get|setup|deploy)\b', 0.9),
                (r'\bi (want|need|would like)( to)? (install|add|get)\b', 0.95),
                (r'\b(can you|could you|please) install\b', 0.95),
                (r'\bput .*( on| in) (my )?(system|machine|computer)\b', 0.7),
                (r'\badd .* to (my )?(system|nixos)\b', 0.8),
            ],
            Intent.REMOVE: [
                (r'\b(remove|uninstall|delete|purge|erase)\b', 0.9),
                (r'\bget rid of\b', 0.85),
                (r'\b(don\'t|do not) (want|need)\b.*anymore', 0.7),
                (r'\btake .* off (my )?(system|machine)\b', 0.75),
            ],
            Intent.UPDATE: [
                (r'\b(update|upgrade|refresh)\b', 0.9),
                (r'\b(bring|get) .* up to date\b', 0.85),
                (r'\blatest version\b', 0.7),
                (r'\bnew(er|est) version\b', 0.75),
            ],
            Intent.SEARCH: [
                (r'\b(search|find|look for|locate|discover)\b', 0.9),
                (r'\bwhat .* (is|are) available\b', 0.85),
                (r'\b(show|list) .* packages\b', 0.8),
                (r'\bis there (a|an)\b', 0.7),
                (r'\bdo you have\b', 0.7),
                (r'\bi need (a|an|some)\b', 0.85),  # "I need a text editor"
                (r'\bi want (a|an|some)\b', 0.8),   # "I want a browser"
                (r'\blooking for (a|an|some)\b', 0.9),  # "Looking for a terminal"
                (r'\bgive me (a|an|some)\b', 0.75),  # "Give me a music player"
            ],
            Intent.LIST: [
                (r'\b(list|show|display|what\'s) installed\b', 0.95),
                (r'\bwhat (do )?i have installed\b', 0.95),
                (r'\bshow (me )?my packages\b', 0.9),
                (r'\bwhat packages\b', 0.8),
            ],
            Intent.ROLLBACK: [
                (r'\b(rollback|revert|undo|go back)\b', 0.9),
                (r'\bprevious (version|generation|state)\b', 0.85),
                (r'\b(that|this) (was|is) a mistake\b', 0.7),
                (r'\bput it back\b', 0.75),
            ],
            Intent.HELP: [
                (r'\b(help|how do i|how to|what can)\b', 0.85),
                (r'\b(explain|tell me about|what is)\b', 0.8),
                (r'\bi don\'t (understand|know)\b', 0.75),
                (r'\bshow me how\b', 0.85),
            ],
            Intent.CONFIGURE: [
                (r'\b(configure|config|set up|customize)\b', 0.9),
                (r'\bchange .* setting\b', 0.85),
                (r'\benable|disable\b', 0.8),
                (r'\bturn (on|off)\b', 0.75),
            ],
            Intent.BUILD: [
                (r'\b(build|compile|make)\b', 0.9),
                (r'\bcreate .* (package|derivation)\b', 0.85),
                (r'\bnix-build\b', 1.0),
            ],
            Intent.CREATE_SHELL: [
                (r'\b(shell|environment|env|devshell|dev shell)\b', 0.85),
                (r'\bnix-shell\b', 1.0),
                (r'\bdevelopment environment\b', 0.9),
                (r'\bdev environment for\b', 0.95),
            ],
            Intent.DIAGNOSE: [
                (r'\b(diagnose|debug|troubleshoot|what\'s wrong)\b', 0.9),
                (r'\b(not|isn\'t|won\'t|doesn\'t) work(ing)?\b', 0.85),
                (r'\b(error|problem|issue|broken)\b', 0.8),
                (r'\bwhy (is|does)\b', 0.7),
                (r'\bsomething(\'s| is) wrong\b', 0.95),  # "Something's wrong with my system"
                (r'\bcheck (my )?(system|health|status)\b', 0.9),
                (r'\bhaving (problems|issues|trouble)\b', 0.85),
                (r'\bsystem (is )?(slow|broken|acting weird)\b', 0.85),
            ],
            Intent.GARBAGE_COLLECT: [
                (r'\b(garbage collect|gc|clean up|free space)\b', 0.95),
                (r'\bremove (old|unused) (packages|generations)\b', 0.9),
                (r'\bclear cache\b', 0.85),
                (r'\bsave (disk )?space\b', 0.8),
            ],
            Intent.FLAKE_INIT: [
                (r'\b(init|create|new) flake\b', 0.95),
                (r'\bflake init\b', 1.0),
                (r'\bstart .* flake\b', 0.9),
            ],
            Intent.FLAKE_UPDATE: [
                (r'\bupdate flake\b', 0.95),
                (r'\bflake update\b', 1.0),
                (r'\bupdate .* inputs\b', 0.9),
            ],
            Intent.HOME_INSTALL: [
                (r'\bhome(-| )manager\b.*install', 0.95),
                (r'\binstall.*home(-| )manager\b', 0.95),
                (r'\buser (package|config)\b', 0.7),
            ],
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load patterns for entity extraction"""
        return {
            'package': [
                (r'(?:install|remove|update|search for|search|find|get|add|delete) (\S+)', 'direct'),
                (r'package (?:called |named )?(\S+)', 'explicit'),
                (r'(\S+) package', 'trailing'),
                (r'(?:search|find|look for) (\S+)', 'search'),
                # Natural language patterns
                (r'(?:i need|i want|looking for|give me) (?:a |an |some )?(\w+[\w-]*)', 'natural'),
                (r'(?:a |an |some )?(\w+) (?:editor|browser|player|manager|tool|program|app|server)', 'category'),
                (r'(?:text |code |music |video |image |file )?(\w+)', 'type_hint'),
            ],
            'config_file': [
                (r'(/etc/nixos/\S+)', 'path'),
                (r'(configuration\.nix)', 'filename'),
                (r'(\S+\.nix)', 'nix_file'),
            ],
            'channel': [
                (r'(nixos-\d+\.\d+)', 'version'),
                (r'(nixos-unstable)', 'unstable'),
                (r'channel (\S+)', 'explicit'),
            ],
            'generation': [
                (r'generation (\d+)', 'number'),
                (r'(\d+) generations? ago', 'relative'),
            ],
        }
    
    def _load_compound_patterns(self) -> List[Tuple[str, List[Intent]]]:
        """Load patterns for compound/multiple intents"""
        return [
            (r'install .* and .* and', [Intent.INSTALL, Intent.MULTIPLE]),
            (r'first .* then', [Intent.MULTIPLE, Intent.CONDITIONAL]),
            (r'update .* and install', [Intent.UPDATE, Intent.INSTALL]),
            (r'remove .* and .* clean', [Intent.REMOVE, Intent.GARBAGE_COLLECT]),
        ]
    
    def recognize(self, query: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """
        Main recognition pipeline
        
        Args:
            query: The user's natural language query
            context: Optional context from conversation state
            
        Returns:
            IntentResult with recognized intent and entities
        """
        # Stage 1: Preprocessing
        normalized = self._preprocess(query)
        
        # Stage 2: Pattern Matching
        intent_scores = self._match_patterns(normalized)
        
        # Stage 3: Entity Extraction
        entities = self._extract_entities(query, normalized)
        
        # Stage 4: Context Enhancement
        if context:
            intent_scores = self._enhance_with_context(intent_scores, context)
        
        # Stage 5: Compound Detection
        compound_intents = self._detect_compound(normalized)
        
        # Stage 6: Confidence Scoring
        primary_intent, confidence = self._select_primary_intent(intent_scores)
        
        # Stage 7: Generate Suggestions
        suggestions = self._generate_suggestions(primary_intent, entities, confidence)
        
        # Create result
        result = IntentResult(
            primary_intent=primary_intent,
            confidence=confidence,
            entities=entities,
            original_query=query,
            normalized_query=normalized,
            secondary_intents=compound_intents,
            context_required=confidence < 0.6,
            suggestions=suggestions,
            metadata={
                'intent_scores': {k.value: v for k, v in intent_scores.items()},
                'preprocessing': {'original_length': len(query), 'normalized_length': len(normalized)}
            }
        )
        
        # Learn from this recognition (would be persisted in production)
        if confidence > 0.8:
            self.successful_matches.append((query, primary_intent))
        elif confidence < 0.5:
            self.failed_matches.append((query, primary_intent))
        
        return result
    
    def _preprocess(self, query: str) -> str:
        """Clean and normalize the query"""
        # Convert to lowercase
        normalized = query.lower()
        
        # Expand contractions
        contractions = {
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "couldn't": "could not",
            "shouldn't": "should not",
            "wouldn't": "would not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "haven't": "have not",
            "hasn't": "has not",
            "hadn't": "had not",
            "i'm": "i am",
            "you're": "you are",
            "he's": "he is",
            "she's": "she is",
            "it's": "it is",
            "we're": "we are",
            "they're": "they are",
            "i've": "i have",
            "you've": "you have",
            "we've": "we have",
            "they've": "they have",
            "i'd": "i would",
            "you'd": "you would",
            "he'd": "he would",
            "she'd": "she would",
            "we'd": "we would",
            "they'd": "they would",
            "i'll": "i will",
            "you'll": "you will",
            "he'll": "he will",
            "she'll": "she will",
            "we'll": "we will",
            "they'll": "they will",
            "what's": "what is",
            "that's": "that is",
            "there's": "there is",
            "here's": "here is",
        }
        
        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _match_patterns(self, normalized: str) -> Dict[Intent, float]:
        """Match query against intent patterns"""
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            max_score = 0.0
            for pattern, base_score in patterns:
                if re.search(pattern, normalized, re.IGNORECASE):
                    # Adjust score based on pattern position
                    match = re.search(pattern, normalized, re.IGNORECASE)
                    position_factor = 1.0 - (match.start() / max(len(normalized), 1)) * 0.1
                    adjusted_score = base_score * position_factor
                    max_score = max(max_score, adjusted_score)
            
            if max_score > 0:
                scores[intent] = max_score
        
        # If no patterns matched, set unknown
        if not scores:
            scores[Intent.UNKNOWN] = 0.5
        
        return scores
    
    def _extract_entities(self, original: str, normalized: str) -> List[Entity]:
        """Extract entities from the query"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern, pattern_type in patterns:
                matches = re.finditer(pattern, original, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    # Skip common words
                    if value.lower() in {'the', 'a', 'an', 'it', 'that', 'this', 'my'}:
                        continue
                    
                    # Calculate confidence based on pattern type
                    confidence = 1.0 if pattern_type in ['direct', 'explicit', 'path'] else 0.8
                    
                    entity = Entity(
                        type=entity_type,
                        value=value,
                        confidence=confidence,
                        metadata={'pattern_type': pattern_type, 'position': match.start()}
                    )
                    entities.append(entity)
        
        # Deduplicate entities
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity.type, entity.value.lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _enhance_with_context(self, scores: Dict[Intent, float], context: Dict[str, Any]) -> Dict[Intent, float]:
        """Enhance intent scores using conversation context"""
        enhanced = scores.copy()
        
        # Boost intents related to recent conversation
        if 'recent_history' in context:
            for turn in context.get('recent_history', [])[-3:]:
                if 'intent' in turn:
                    recent_intent = Intent(turn['intent']) if isinstance(turn['intent'], str) else turn['intent']
                    # Boost related intents
                    if recent_intent == Intent.SEARCH and Intent.INSTALL in enhanced:
                        enhanced[Intent.INSTALL] *= 1.2
                    elif recent_intent == Intent.INSTALL and Intent.CONFIGURE in enhanced:
                        enhanced[Intent.CONFIGURE] *= 1.2
                    elif recent_intent == Intent.DIAGNOSE and Intent.FIX in enhanced:
                        enhanced[Intent.FIX] *= 1.3
        
        # Boost based on user skill level
        skill_level = context.get('user_skill', 'beginner')
        if skill_level == 'expert':
            # Experts more likely to use advanced commands
            for intent in [Intent.BUILD, Intent.FLAKE_INIT, Intent.CONFIGURE]:
                if intent in enhanced:
                    enhanced[intent] *= 1.1
        elif skill_level == 'beginner':
            # Beginners more likely to need help
            if Intent.HELP in enhanced:
                enhanced[Intent.HELP] *= 1.2
        
        # Check for follow-up patterns
        if context.get('is_followup'):
            # Boost intents that commonly follow the last one
            if 'working_memory' in context:
                last_command = context['working_memory'].get('last_command')
                if last_command == 'search' and Intent.INSTALL in enhanced:
                    enhanced[Intent.INSTALL] *= 1.5
                elif last_command == 'install' and Intent.CONFIGURE in enhanced:
                    enhanced[Intent.CONFIGURE] *= 1.3
        
        return enhanced
    
    def _detect_compound(self, normalized: str) -> List[Intent]:
        """Detect compound/multiple intents"""
        compound_intents = []
        
        for pattern, intents in self.compound_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                compound_intents.extend(intents)
        
        return list(set(compound_intents))  # Deduplicate
    
    def _select_primary_intent(self, scores: Dict[Intent, float]) -> Tuple[Intent, float]:
        """Select the primary intent from scores"""
        if not scores:
            return Intent.UNKNOWN, 0.0
        
        # Get highest scoring intent
        primary = max(scores.items(), key=lambda x: x[1])
        
        # Check if there are close competitors
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) > 1:
            # If second best is very close, reduce confidence
            if sorted_scores[1][1] / sorted_scores[0][1] > 0.8:
                return primary[0], primary[1] * 0.8
        
        return primary[0], primary[1]
    
    def _generate_suggestions(self, intent: Intent, entities: List[Entity], confidence: float) -> List[str]:
        """Generate suggestions based on recognition results"""
        suggestions = []
        
        if confidence < 0.6:
            suggestions.append("I'm not entirely sure what you want. Could you be more specific?")
            
            # Suggest possible interpretations
            if intent == Intent.UNKNOWN:
                suggestions.append("Did you mean to: install, search, update, or get help?")
            else:
                suggestions.append(f"Did you mean to {intent.value.replace('_', ' ')}?")
        
        # Check for missing entities
        if intent in [Intent.INSTALL, Intent.REMOVE, Intent.SEARCH] and not entities:
            suggestions.append(f"What would you like to {intent.value}?")
        
        # Suggest related commands
        if intent == Intent.SEARCH and entities:
            suggestions.append(f"After searching, you can install with: install {entities[0].value}")
        elif intent == Intent.INSTALL and entities:
            suggestions.append(f"After installing, you might want to: configure {entities[0].value}")
        
        return suggestions
    
    def learn_from_feedback(self, query: str, correct_intent: Intent, was_successful: bool):
        """Learn from user feedback to improve recognition"""
        if was_successful:
            self.successful_matches.append((query, correct_intent))
            # In production, we'd update pattern weights here
        else:
            self.failed_matches.append((query, correct_intent))
            # In production, we'd add new patterns or adjust weights
    
    def get_recognition_stats(self) -> Dict[str, Any]:
        """Get statistics about recognition performance"""
        return {
            'successful_recognitions': len(self.successful_matches),
            'failed_recognitions': len(self.failed_matches),
            'success_rate': len(self.successful_matches) / max(len(self.successful_matches) + len(self.failed_matches), 1),
            'total_patterns': sum(len(patterns) for patterns in self.intent_patterns.values()),
            'intent_coverage': len(self.intent_patterns)
        }