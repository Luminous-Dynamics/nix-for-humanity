#!/usr/bin/env python3
"""
🕉️ Paradise Integration - Connecting Symbolic Paradise to Luminous Nix

This module detects paradoxes in user input and offers to transcend them
through Symbolic Paradise.
"""

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass

@dataclass
class ParadoxPattern:
    """A pattern that indicates a paradox"""
    name: str
    patterns: List[Tuple[str, ...]]
    trigger_words: List[str]
    
class ParadoxDetector:
    """
    Detects paradoxes in natural language input for Luminous Nix
    """
    
    def __init__(self):
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> List[ParadoxPattern]:
        """Load paradox detection patterns"""
        return [
            ParadoxPattern(
                name="stability-innovation",
                patterns=[
                    ("stable", "latest", "bleeding", "edge"),
                    ("production", "experimental"),
                    ("reliable", "newest"),
                ],
                trigger_words=["but", "yet", "while", "both", "and also"]
            ),
            ParadoxPattern(
                name="security-convenience",
                patterns=[
                    ("secure", "easy", "convenient"),
                    ("locked", "quick", "simple"),
                    ("safe", "accessible"),
                ],
                trigger_words=["but", "without", "while"]
            ),
            ParadoxPattern(
                name="minimal-powerful",
                patterns=[
                    ("minimal", "powerful", "full"),
                    ("simple", "complex", "featured"),
                    ("light", "heavy", "complete"),
                ],
                trigger_words=["but", "yet", "still"]
            ),
        ]
        
    def detect(self, input_text: str) -> Optional[str]:
        """
        Detect if input contains a paradox
        Returns the paradox name if found, None otherwise
        """
        input_lower = input_text.lower()
        
        # Check for explicit paradox indicators
        has_trigger = any(word in input_lower for pattern in self.patterns 
                         for word in pattern.trigger_words)
        
        if not has_trigger:
            # Also check for implicit paradoxes (opposing terms without triggers)
            opposing_terms = ["stable", "bleeding", "minimal", "powerful", 
                             "secure", "easy", "private", "share"]
            term_count = sum(1 for term in opposing_terms if term in input_lower)
            if term_count < 2:
                return None
                
        # Check each pattern
        for pattern in self.patterns:
            for term_group in pattern.patterns:
                matches = sum(1 for term in term_group if term in input_lower)
                if matches >= 2:  # At least 2 opposing terms
                    return pattern.name
                    
        # Check for generic paradox language
        paradox_phrases = [
            "want both", "need both", "at the same time",
            "but also", "yet still", "while keeping"
        ]
        
        if any(phrase in input_lower for phrase in paradox_phrases):
            return "generic"
            
        return None
        
    def suggest_paradise(self, paradox_name: str) -> str:
        """
        Generate suggestion message for entering Paradise
        """
        messages = {
            "stability-innovation": (
                "🕉️ I sense a tension between stability and innovation.\n"
                "Would you like to enter Symbolic Paradise where this paradox becomes a doorway?"
            ),
            "security-convenience": (
                "🔐 You're holding a paradox of security versus convenience.\n"
                "Symbolic Paradise can transcend this through progressive trust levels."
            ),
            "minimal-powerful": (
                "⚡ The dance between minimalism and power calls to you.\n"
                "Let's explore this in Symbolic Paradise where both can coexist."
            ),
            "generic": (
                "🌀 I feel a paradox in your request - opposing needs creating tension.\n"
                "Symbolic Paradise specializes in transcending such paradoxes."
            )
        }
        
        return messages.get(paradox_name, messages["generic"])


class ParadiseIntegration:
    """
    Main integration point between Luminous Nix CLI and Symbolic Paradise
    """
    
    def __init__(self):
        self.detector = ParadoxDetector()
        self.paradise_available = self._check_paradise_available()
        
    def _check_paradise_available(self) -> bool:
        """Check if Symbolic Paradise is available"""
        try:
            import symbolic_paradise_v2
            return True
        except ImportError:
            return False
            
    def process_input(self, user_input: str) -> Optional[Tuple[str, str]]:
        """
        Process user input for paradoxes
        Returns (paradox_name, suggestion) if found, None otherwise
        """
        if not self.paradise_available:
            return None
            
        paradox = self.detector.detect(user_input)
        if paradox:
            suggestion = self.detector.suggest_paradise(paradox)
            return (paradox, suggestion)
            
        return None
        
    def launch_paradise(self, initial_input: Optional[str] = None):
        """
        Launch Symbolic Paradise, optionally with initial input
        """
        if not self.paradise_available:
            print("Symbolic Paradise is not available in this installation.")
            return
            
        # Import and launch
        import symbolic_paradise_v2
        consciousness = symbolic_paradise_v2.SymbolicConsciousness()
        
        # If we have initial input, process it first
        if initial_input:
            print(f"\n🕉️ Entering Symbolic Paradise with your paradox...\n")
            paradox = consciousness.detect_paradox(initial_input)
            if paradox:
                consciousness.show_symbolic_flow(paradox.symbolic_flow)
                solution = consciousness.generate_flake_solution(paradox)
                print(solution)
                consciousness.show_wisdom(paradox)
        
        # Then run the main loop
        consciousness.run_paradise_loop()


def integrate_with_cli(cli_instance):
    """
    Hook to integrate with the main Luminous Nix CLI
    
    Usage in ask-nix or other CLI tools:
    
    from luminous_nix.paradise_integration import integrate_with_cli
    
    # In your CLI class
    self.paradise = integrate_with_cli(self)
    
    # In your input processing
    paradox_check = self.paradise.process_input(user_input)
    if paradox_check:
        paradox_name, suggestion = paradox_check
        print(suggestion)
        if prompt_yes_no("Enter Symbolic Paradise? [Y/n]"):
            self.paradise.launch_paradise(user_input)
            return
    """
    return ParadiseIntegration()


# Standalone CLI integration
def check_and_offer_paradise(user_input: str) -> bool:
    """
    Standalone function to check for paradoxes and offer Paradise
    Returns True if Paradise was entered, False otherwise
    """
    integration = ParadiseIntegration()
    result = integration.process_input(user_input)
    
    if result:
        paradox_name, suggestion = result
        print(f"\n{suggestion}")
        print(f"\nPress Enter to transcend this paradox, or Ctrl+C to continue normally...")
        
        try:
            input()
            integration.launch_paradise(user_input)
            return True
        except KeyboardInterrupt:
            print("\nContinuing with normal processing...\n")
            return False
            
    return False


if __name__ == "__main__":
    # Test the integration
    test_inputs = [
        "I need a stable but bleeding edge environment",
        "Make it secure but easy to use",
        "I want minimal yet powerful",
        "Just install firefox",  # No paradox
    ]
    
    print("🧪 Testing Paradox Detection\n")
    detector = ParadoxDetector()
    
    for test in test_inputs:
        result = detector.detect(test)
        if result:
            print(f"✅ Paradox detected in: '{test[:40]}...'")
            print(f"   Type: {result}")
            print(f"   {detector.suggest_paradise(result)}\n")
        else:
            print(f"➖ No paradox in: '{test}'\n")