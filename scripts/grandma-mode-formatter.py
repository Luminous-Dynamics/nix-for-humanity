#!/usr/bin/env python3
"""
from typing import List
Grandma Mode Formatter - Makes NixOS accessible to everyone

Removes technical jargon, simplifies responses to 3 sentences max,
and ensures voice-friendly output.
"""

import re
from typing import Dict, List

class GrandmaModeFormatter:
    def __init__(self):
        # Technical term translations
        self.jargon_map = {
            'nixpkgs': 'software collection',
            'nix profile': 'your programs',
            'nix-env': 'program manager',
            'sudo': 'administrator permission',
            'declarative': 'permanent',
            'imperative': 'temporary',
            'configuration.nix': 'system settings',
            'home.packages': 'your personal programs',
            'nixos-rebuild': 'system update',
            'flake': 'package list',
            'derivation': 'package',
            'generation': 'backup point',
            'rollback': 'go back',
            'channel': 'software source',
            'unstable': 'newest',
            'stable': 'tested',
            'attribute': 'name',
            'overlay': 'customization',
            'expression': 'instruction',
            'evaluation': 'processing',
            'instantiate': 'prepare',
            'realize': 'install',
            'garbage collection': 'cleanup',
            'store path': 'location',
            '/nix/store': 'program storage',
            'hash': 'identifier',
            'binary cache': 'download source',
            'substituter': 'download server',
            'symlink': 'shortcut',
            'profile': 'your setup'
        }
        
        # Remove these patterns entirely
        self.remove_patterns = [
            r'```[^`]*```',  # Code blocks
            r'`[^`]+`',      # Inline code
            r'/nix/store/[a-z0-9]{32}-',  # Store paths
            r'[a-f0-9]{32,}',  # Hashes
            r'https?://\S+',   # URLs
            r'--[a-zA-Z-]+',   # Command flags
            r'\$\{[^}]+\}',    # Variables
            r'::',             # Double colons
            r'->',             # Arrows
            r'=>',             # Fat arrows
        ]
        
    def format_for_grandma(self, text: str) -> str:
        """
        Transform technical NixOS output into Grandma-friendly language
        """
        # Step 1: Remove code blocks and technical patterns
        cleaned = text
        for pattern in self.remove_patterns:
            cleaned = re.sub(pattern, '', cleaned)
            
        # Step 2: Replace technical jargon
        for jargon, simple in self.jargon_map.items():
            # Case-insensitive replacement
            cleaned = re.sub(
                rf'\b{re.escape(jargon)}\b', 
                simple, 
                cleaned, 
                flags=re.IGNORECASE
            )
            
        # Step 3: Remove emojis (can confuse screen readers)
        cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)
        
        # Step 4: Simplify sentences
        sentences = self._split_sentences(cleaned)
        
        # Step 5: Keep only first 3 sentences
        if len(sentences) > 3:
            sentences = sentences[:3]
            
        # Step 6: Ensure each sentence is simple
        simple_sentences = []
        for sentence in sentences:
            # Remove parenthetical explanations
            sentence = re.sub(r'\([^)]+\)', '', sentence)
            # Remove multiple spaces
            sentence = re.sub(r'\s+', ' ', sentence)
            # Trim
            sentence = sentence.strip()
            if sentence:
                simple_sentences.append(sentence)
                
        # Step 7: Join with proper spacing
        result = '. '.join(simple_sentences)
        if result and not result.endswith('.'):
            result += '.'
            
        # Step 8: Final cleanup
        result = re.sub(r'\.+', '.', result)  # Multiple periods
        result = re.sub(r'\s+', ' ', result)  # Multiple spaces
        
        return result.strip()
        
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences, handling common abbreviations"""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
        
    def format_command_response(self, intent: str, response: str) -> str:
        """Format responses for specific command types"""
        
        # Special handling for different intents
        if intent == 'install_package':
            return self._format_install_response(response)
        elif intent == 'update_system':
            return self._format_update_response(response)
        elif intent == 'remove_package':
            return self._format_remove_response(response)
        elif intent == 'search_package':
            return self._format_search_response(response)
        else:
            return self.format_for_grandma(response)
            
    def _format_install_response(self, response: str) -> str:
        """Special formatting for install commands"""
        # Extract package name if possible
        package_match = re.search(r'install[ing]?\s+(\w+)', response, re.IGNORECASE)
        if package_match:
            package = package_match.group(1)
            return f"I'll install {package} for you. This will add it to your computer. It will be ready to use soon."
        return "I'll install that program for you. It will be ready soon."
        
    def _format_update_response(self, response: str) -> str:
        """Special formatting for update commands"""
        return "I'll update your computer now. This keeps everything working well. Please wait a moment."
        
    def _format_remove_response(self, response: str) -> str:
        """Special formatting for remove commands"""
        package_match = re.search(r'remov[ing]?\s+(\w+)', response, re.IGNORECASE)
        if package_match:
            package = package_match.group(1)
            return f"I'll remove {package} from your computer. It will be gone. You can add it back later if needed."
        return "I'll remove that program. You can add it back later if you want."
        
    def _format_search_response(self, response: str) -> str:
        """Special formatting for search results"""
        # Count how many results
        lines = response.strip().split('\n')
        result_count = len([l for l in lines if l.strip()])
        
        if result_count == 0:
            return "I couldn't find that program. Try a different name."
        elif result_count == 1:
            return "I found one program matching your search. Would you like to install it?"
        else:
            return f"I found {result_count} programs. Which one would you like?"


def main():
    """Test the formatter"""
    formatter = GrandmaModeFormatter()
    
    # Test cases
    test_responses = [
        "Hi there! I'll help you install firefox! Here are your options:\n\n1. **Home Manager (User-level, No Sudo)** (no sudo needed)\n   User-specific installation without root access\n   ```\n   home.packages = with pkgs; [ firefox ];\n   ```\n\n2. **Nix Profile (User-level)** (no sudo needed)\n   Modern way to install for current user\n   ```\n   nix profile install nixpkgs#firefox\n   ```",
        
        "Update full system configuration\n\n⚠️ This operation requires sudo privileges.\n\nExample:\n```\nsudo nixos-rebuild switch\n```\n\n💡 Only needed for system-wide changes",
        
        "Error: Package 'firefx' not found in nixpkgs. Did you mean 'firefox'?\n\nSimilar packages:\n- firefox\n- firefox-esr\n- firefox-wayland\n\nTry: nix search nixpkgs firefox",
    ]
    
    print("🧓 Grandma Mode Formatter Test\n")
    print("=" * 50)
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n📝 Test {i} - Original:")
        print("-" * 40)
        print(response)
        print("\n👵 Grandma Mode:")
        print("-" * 40)
        formatted = formatter.format_for_grandma(response)
        print(formatted)
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()