#!/usr/bin/env python3
"""
from typing import Tuple, List
Adaptive Response Formatter - Dynamic response adaptation based on user needs

Instead of fixed personality styles, this system adapts response characteristics
along multiple dimensions based on natural language cues and user behavior.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class ResponseDimensions:
    """Response characteristics that can be adjusted independently"""
    complexity: float = 0.5      # 0.0 = simple, 1.0 = technical
    verbosity: float = 0.5       # 0.0 = minimal, 1.0 = detailed
    warmth: float = 0.5         # 0.0 = neutral, 1.0 = friendly
    examples: float = 0.5       # 0.0 = no examples, 1.0 = many examples
    pace: float = 0.5          # 0.0 = slow/patient, 1.0 = fast/efficient
    formality: float = 0.5     # 0.0 = casual, 1.0 = formal
    visual_structure: float = 0.5  # 0.0 = plain text, 1.0 = rich formatting

class UserState(Enum):
    """Detected user states that influence response adaptation"""
    LEARNING = "learning"
    CONFIDENT = "confident"
    FRUSTRATED = "frustrated"
    EXPLORING = "exploring"
    TIME_PRESSURED = "time_pressured"
    ACCESSIBILITY_FOCUSED = "accessibility_focused"
    FIRST_TIME = "first_time"
    EXPERT = "expert"

class AdaptiveResponseFormatter:
    def __init__(self):
        # Natural language cues that indicate user needs
        self.simplicity_cues = [
            "simple", "easy", "basic", "explain", "don't understand",
            "confused", "help", "new to", "what is", "how do"
        ]
        
        self.detail_cues = [
            "exactly", "specifically", "details", "more info", "explain more",
            "technical", "advanced", "precise", "comprehensive"
        ]
        
        self.urgency_cues = [
            "quick", "fast", "asap", "urgent", "now", "immediately",
            "hurry", "short", "brief", "summary"
        ]
        
        self.learning_cues = [
            "learn", "understand", "why", "how does", "explain",
            "teach", "show me", "example", "step by step"
        ]
        
        self.frustration_cues = [
            "not working", "broken", "error", "failed", "stuck",
            "frustrated", "annoying", "why isn't", "should work"
        ]
        
        self.accessibility_cues = [
            "screen reader", "voice", "speak", "hear", "accessible",
            "vision", "blind", "deaf", "disability"
        ]
        
        # Technical jargon mapping for simplification
        self.jargon_map = {
            'nixpkgs': 'software collection',
            'nix profile': 'your installed programs',
            'nix-env': 'program manager',
            'sudo': 'administrator permission',
            'declarative': 'permanent',
            'imperative': 'temporary',
            'configuration.nix': 'system settings file',
            'home.packages': 'your personal programs',
            'nixos-rebuild': 'system update',
            'flake': 'package list',
            'derivation': 'package',
            'generation': 'system backup',
            'rollback': 'go back to previous version',
            'channel': 'software source',
            'attribute': 'package name',
            'garbage collection': 'cleanup old files'
        }
    
    def detect_user_state(self, query: str, history: List[str] = None) -> List[UserState]:
        """Detect user's current state from their query and history"""
        query_lower = query.lower()
        states = []
        
        # Check for various states
        if any(cue in query_lower for cue in self.frustration_cues):
            states.append(UserState.FRUSTRATED)
            
        if any(cue in query_lower for cue in self.learning_cues):
            states.append(UserState.LEARNING)
            
        if any(cue in query_lower for cue in self.urgency_cues):
            states.append(UserState.TIME_PRESSURED)
            
        if any(cue in query_lower for cue in self.accessibility_cues):
            states.append(UserState.ACCESSIBILITY_FOCUSED)
            
        if any(cue in query_lower for cue in self.simplicity_cues):
            if UserState.LEARNING not in states:
                states.append(UserState.FIRST_TIME)
                
        # Check history for patterns
        if history:
            if len(history) == 0:
                states.append(UserState.FIRST_TIME)
            elif len(history) > 10:
                states.append(UserState.CONFIDENT)
                
        return states or [UserState.EXPLORING]
    
    def calculate_dimensions(self, query: str, states: List[UserState]) -> ResponseDimensions:
        """Calculate response dimensions based on query and user state"""
        dims = ResponseDimensions()
        query_lower = query.lower()
        
        # Adjust for detected states
        if UserState.FRUSTRATED in states:
            dims.complexity = 0.2
            dims.warmth = 0.8
            dims.examples = 0.9
            dims.pace = 0.3
            
        if UserState.LEARNING in states:
            dims.complexity = 0.3
            dims.verbosity = 0.7
            dims.examples = 0.8
            dims.pace = 0.4
            
        if UserState.TIME_PRESSURED in states:
            dims.verbosity = 0.2
            dims.examples = 0.3
            dims.pace = 0.9
            dims.visual_structure = 0.2
            
        if UserState.ACCESSIBILITY_FOCUSED in states:
            dims.complexity = 0.1
            dims.visual_structure = 0.0  # Plain text only
            dims.verbosity = 0.3  # Concise for screen readers
            
        if UserState.FIRST_TIME in states:
            dims.complexity = 0.2
            dims.warmth = 0.7
            dims.examples = 0.6
            
        if UserState.EXPERT in states:
            dims.complexity = 0.8
            dims.verbosity = 0.4
            dims.formality = 0.7
            dims.pace = 0.8
            
        # Adjust based on specific cues
        if any(cue in query_lower for cue in self.simplicity_cues):
            dims.complexity *= 0.5
            
        if any(cue in query_lower for cue in self.detail_cues):
            dims.verbosity = min(1.0, dims.verbosity * 1.5)
            dims.complexity = min(1.0, dims.complexity * 1.3)
            
        # Meta-instructions override
        if "explain simply" in query_lower:
            dims.complexity = 0.1
            dims.verbosity = 0.4
        elif "give me details" in query_lower:
            dims.verbosity = 0.9
            dims.complexity = 0.7
        elif "just the command" in query_lower:
            dims.verbosity = 0.1
            dims.examples = 0.0
            dims.warmth = 0.2
            
        return dims
    
    def format_response(self, response: str, dimensions: ResponseDimensions, 
                       intent: str = None) -> str:
        """Format response according to calculated dimensions"""
        
        # Step 1: Adjust complexity
        if dimensions.complexity < 0.5:
            response = self._simplify_language(response)
            
        # Step 2: Adjust verbosity
        if dimensions.verbosity < 0.3:
            response = self._make_concise(response)
        elif dimensions.verbosity > 0.7:
            response = self._add_context(response, intent)
            
        # Step 3: Adjust warmth
        if dimensions.warmth > 0.6:
            response = self._add_warmth(response)
            
        # Step 4: Handle examples
        if dimensions.examples < 0.3:
            response = self._remove_examples(response)
        elif dimensions.examples > 0.7:
            response = self._enhance_examples(response)
            
        # Step 5: Adjust visual structure
        if dimensions.visual_structure < 0.3:
            response = self._remove_formatting(response)
            
        # Step 6: Adjust pace
        if dimensions.pace < 0.4:
            response = self._add_reassurance(response)
            
        return response.strip()
    
    def _simplify_language(self, text: str) -> str:
        """Replace technical jargon with simple terms"""
        simplified = text
        
        # Replace jargon
        for jargon, simple in self.jargon_map.items():
            simplified = re.sub(
                rf'\b{re.escape(jargon)}\b', 
                simple, 
                simplified, 
                flags=re.IGNORECASE
            )
            
        # Remove code blocks for maximum simplicity
        simplified = re.sub(r'```[^`]*```', '', simplified)
        simplified = re.sub(r'`[^`]+`', '', simplified)
        
        # Remove complex punctuation
        simplified = re.sub(r'[()\\[\\]{}<>]', '', simplified)
        
        return simplified
    
    def _make_concise(self, text: str) -> str:
        """Reduce response to essential information"""
        lines = text.strip().split('\n')
        
        # Keep only essential lines
        essential = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip explanatory text
            if any(skip in line.lower() for skip in 
                   ['for example', 'note that', 'this means', 'in other words']):
                continue
            essential.append(line)
            
        # Limit to 3 lines for extreme conciseness
        return '\n'.join(essential[:3])
    
    def _add_context(self, text: str, intent: str) -> str:
        """Add helpful context for detailed responses"""
        context_additions = {
            'install_package': "\n\nNote: After installation, the package will be available immediately. You can verify with 'which <package-name>'.",
            'update_system': "\n\nThis will download and apply all available updates. The process may take several minutes depending on your internet speed.",
            'remove_package': "\n\nRemoved packages can be reinstalled anytime. Your configuration files are preserved.",
        }
        
        if intent in context_additions:
            text += context_additions[intent]
            
        return text
    
    def _add_warmth(self, text: str) -> str:
        """Add friendly touches to the response"""
        if not text.startswith(('Hi', 'Hello', 'Great')):
            text = "I'd be happy to help! " + text
            
        if not any(text.endswith(end) for end in ['!', '?', '😊', '👍']):
            text += " Let me know if you need anything else!"
            
        return text
    
    def _remove_examples(self, text: str) -> str:
        """Remove example sections"""
        # Remove example blocks
        text = re.sub(r'Example:.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL)
        text = re.sub(r'For example:.*?(?=\n|\Z)', '', text)
        return text
    
    def _enhance_examples(self, text: str) -> str:
        """Add or enhance examples"""
        if "install" in text.lower() and "example" not in text.lower():
            text += "\n\nExample: To install Firefox, use: nix profile install nixpkgs#firefox"
        return text
    
    def _remove_formatting(self, text: str) -> str:
        """Remove all formatting for accessibility"""
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'#{1,6}\s*', '', text)           # Headers
        text = re.sub(r'[-*+]\s', '', text)             # Bullet points
        text = re.sub(r'\d+\.\s', '', text)             # Numbered lists
        
        # Remove emojis
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        return text
    
    def _add_reassurance(self, text: str) -> str:
        """Add reassuring elements for stressed users"""
        reassurances = [
            "Take your time. ",
            "No rush - we'll get this working. ",
            "Don't worry, this is simpler than it seems. "
        ]
        
        import random
        if not any(r in text for r in ["Don't worry", "Take your time", "No rush"]):
            text = random.choice(reassurances) + text
            
        return text
    
    def adapt_response(self, query: str, response: str, intent: str = None,
                       history: List[str] = None) -> Tuple[str, ResponseDimensions]:
        """Main method: Adapt response based on all factors"""
        # Detect user state
        states = self.detect_user_state(query, history)
        
        # Calculate dimensions
        dimensions = self.calculate_dimensions(query, states)
        
        # Format response
        adapted = self.format_response(response, dimensions, intent)
        
        return adapted, dimensions


def main():
    """Test the adaptive formatter"""
    formatter = AdaptiveResponseFormatter()
    
    # Test cases showing different adaptations
    test_cases = [
        {
            "query": "How do I install Firefox? I'm new to this.",
            "response": "I'll help you install firefox! Here are your options:\n\n1. **Home Manager** - User-specific installation\n   ```\n   home.packages = with pkgs; [ firefox ];\n   ```\n\n2. **Nix Profile** - Modern user installation\n   ```\n   nix profile install nixpkgs#firefox\n   ```",
            "intent": "install_package"
        },
        {
            "query": "quickly tell me how to update",
            "response": "Update your system configuration and packages:\n\nExample:\n```\nsudo nixos-rebuild switch\n```\n\nThis will download all updates and apply them.",
            "intent": "update_system"
        },
        {
            "query": "My screen reader needs simple instructions for installing software",
            "response": "To install software on NixOS, you have several options:\n\n1. Edit your configuration.nix file\n2. Use nix-env for temporary installation\n3. Use home-manager for user packages",
            "intent": "install_package"
        },
        {
            "query": "Give me the technical details about garbage collection",
            "response": "Garbage collection removes unreferenced packages from /nix/store.\n\nRun: nix-collect-garbage -d",
            "intent": "cleanup"
        }
    ]
    
    print("🎯 Adaptive Response Formatter Test\n")
    print("=" * 70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}")
        print(f"Query: {test['query']}")
        print("-" * 70)
        print("Original Response:")
        print(test['response'])
        print("-" * 70)
        
        adapted, dims = formatter.adapt_response(
            test['query'], 
            test['response'], 
            test['intent']
        )
        
        print("Adapted Response:")
        print(adapted)
        print(f"\nDimensions: complexity={dims.complexity:.1f}, "
              f"verbosity={dims.verbosity:.1f}, warmth={dims.warmth:.1f}")
        print("=" * 70)


if __name__ == "__main__":
    main()