#!/usr/bin/env python3
"""
from typing import List, Optional
Fix the IntentEngine structure that got corrupted during the previous fix.
"""

import os
from pathlib import Path

def fix_intent_engine():
    """Fix the broken IntentEngine structure"""
    
    intent_engine_content = '''# Intent Recognition Engine
"""
Extracts user intent from natural language input
"""

import re
from typing import Optional, List, Tuple
from .types import Intent, IntentType


class IntentEngine:
    """Recognizes user intent from natural language"""
    
    def __init__(self):
        # Pattern definitions (extracted from ask-nix)
        # Order matters - more specific patterns first
        self.patterns = {
            IntentType.REMOVE: [
                (r'^(remove|uninstall|delete)\s+(.+)$', 2),
                (r'^get\s+rid\s+of\s+(.+)$', 1),
                (r'^(.+)\s+(is\s+gone|needs\s+to\s+be\s+gone)$', 1),
            ],
            IntentType.INFO: [
                (r'^(what|show)\s+(is|me)\s+installed$', 0),
                (r'^what\s+is\s+installed$', 0),
                (r'^show\s+me\s+installed$', 0),
                (r'^show\s+installed$', 0),  # Fix: "show installed"
                (r'^list\s+packages$', 0),
                (r'^system\s+info$', 0),
            ],
            IntentType.UPDATE: [
                # System-specific update patterns (checked first to avoid conflicts)
                (r'^(update|upgrade)\s+(system|everything|all|all\s+packages)$', 0),
                (r'^(update|upgrade)\s+my\s+system$', 0),
                (r'^(update|upgrade)\s+the\s+(whole\s+)?system$', 0),
                (r'^(update|upgrade)\s+my\s+nixos$', 0),
                (r'^(update|upgrade)\s+everything\s+on\s+my\s+system$', 0),
                (r'^(system\s+)?(update|upgrade)(\s+please)?$', 0),
                (r'^system\s+(update|upgrade)(\s+please)?$', 0),
                (r'^make\s+everything\s+current$', 0),
                (r'^make\s+my\s+system\s+current$', 0),
                # Standalone update/upgrade (no specific target)
                (r'^(update|upgrade)\s*$', 0),
            ],
            IntentType.INSTALL: [
                # Direct install commands
                (r'^(install|add|download)\s+(.+)$', 2),
                (r'^get\s+me\s+(.+)$', 1),
                (r'^get\s+(?!rid\s+of)(.+)$', 1),  # Get but not "get rid of"
                # Update specific packages (install newer version) - comes after system updates
                (r'^(update|upgrade)\s+([a-zA-Z][a-zA-Z0-9_-]*(?:\s+[a-zA-Z][a-zA-Z0-9_-]*)?)(?:\s+(?:package|software))?$', 2),  # "update firefox" or "upgrade vim"
                # Polite/conversational requests
                (r'^(please\s+)?(install|add|get)\s+(.+?)(\s+please)?$', 3),
                (r'^(can\s+you\s+)?(please\s+)?(install|add|get)\s+(.+?)(\s+(for\s+me|please))?$', 4),
                (r'^(would\s+you\s+mind\s+)?(adding|installing)\s+(.+)$', 3),
                (r'^(could\s+i\s+get|can\s+i\s+have)\s+(.+?)(\s+please)?$', 2),
                # Need/want expressions
                (r'^i\s+(need|want|require)\s+(.+)$', 2),
                (r'^i\s+really\s+(need|want)\s+(.+?)(\s+that\s+works)?$', 2),
                (r'^(need|want)\s+(.+)$', 2),
                # Simple expressions - but exclude system upgrade/update
                (r'^(?!.*(system|upgrade|update))(.+)\s+please$', 2),  # "firefox please" but not "system upgrade please"
            ],
            IntentType.SEARCH: [
                (r'^(search|find|look\s+for)\s+(.+)$', 2),
                (r'^what\s+is\s+(?!installed)(.+)$', 1),  # "what is" but not "what is installed"
                (r'^is\s+there\s+(.+)$', 1),
                (r'^show\s+me\s+(?!installed)(.+)$', 1),  # "show me" but not "show me installed"
            ],
            IntentType.ROLLBACK: [
                (r'^(rollback|revert|undo)(\s+.*)?$', 0),
                (r'^go\s+back(\s+.*)?$', 0),
                (r'^previous\s+generation$', 0),
            ],
            IntentType.HELP: [
                (r'^help(\s+.*)?$', 0),
                (r'^what\s+can\s+(you\s+do|this\s+system\s+do)$', 0),
                (r'^how\s+do\s+i(\s+.*)?$', 0),
                (r'^i\s+need\s+(assistance|help)$', 0),
                (r'^(explain|tutorial)\s+(.+)$', 0),
            ],
        }
        
        # Common package aliases - order matters for multi-word matches
        self.package_aliases = {
            # Browsers
            'browser': 'firefox',
            'web browser': 'firefox',
            'firefox browser': 'firefox',
            'firefox web browser': 'firefox',
            'chrome': 'google-chrome',
            
            # Editors
            'editor': 'vim',
            'text editor': 'vim',
            'vim editor': 'vim',
            'code editor': 'vscode',
            'vscode': 'vscode',
            'code': 'vscode',
            'vi': 'vim',
            'vim': 'vim',
            
            # Programming languages and runtimes
            'python': 'python3',
            'python package': 'python3',
            'python programming language': 'python3',
            'programming language python': 'python3',
            'node': 'nodejs',
            'nodejs': 'nodejs',
            'nodejs javascript runtime': 'nodejs',
            'javascript runtime': 'nodejs',
            
            # Containers
            'docker': 'docker',
            'docker container system': 'docker',
            'container system': 'docker',
            
            # Common software
            'firefox': 'firefox',
        }
        
        # Test compatibility properties
        self.install_patterns = [pattern[0] for pattern in self.patterns.get(IntentType.INSTALL, [])]
        self.update_patterns = [pattern[0] for pattern in self.patterns.get(IntentType.UPDATE, [])]
        self.search_patterns = [pattern[0] for pattern in self.patterns.get(IntentType.SEARCH, [])]
        self._embeddings_loaded = False
        
    def _normalize(self, text: str) -> str:
        """Normalize text for processing"""
        # Remove extra whitespace and punctuation
        text = re.sub(r'[^\\w\\s]', '', text)
        text = re.sub(r'\\s+', ' ', text)
        return text.strip().lower()
    
    def extract_entities(self, text: str, intent_type: IntentType) -> dict:
        """Extract entities for given intent type"""
        entities = {}
        
        if intent_type == IntentType.INSTALL:
            package = self.extract_package_name(text)
            if package:
                entities['package'] = package
                
        elif intent_type == IntentType.SEARCH:
            # Extract search query
            words = text.lower().split()
            # Remove command words
            command_words = {'search', 'find', 'look', 'for'}
            query_words = [w for w in words if w not in command_words]
            if query_words:
                entities['query'] = ' '.join(query_words)
                
        elif intent_type == IntentType.CONFIG:
            # Extract config target
            words = text.lower().split()
            config_words = {'configure', 'config', 'set', 'up', 'enable', 'help', 'me'}
            target_words = [w for w in words if w not in config_words]
            if target_words:
                entities['config'] = target_words[0]
                
        elif intent_type == IntentType.INFO:
            # Extract info topic
            words = text.lower().split()
            info_words = {'what', 'is', 'explain', 'tell', 'me', 'about', 'how', 'does', 'work'}
            topic_words = [w for w in words if w not in info_words]
            if topic_words:
                entities['topic'] = ' '.join(topic_words)
        
        return entities
        
    def recognize(self, text: str) -> Intent:
        """Extract intent from user input"""
        # Normalize input
        text = text.strip().lower()
        
        # Try each intent type
        for intent_type, patterns in self.patterns.items():
            for pattern, target_group in patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    # Extract target if pattern has one
                    target = None
                    if target_group > 0 and len(match.groups()) >= target_group:
                        raw_target = match.group(target_group).strip()
                        # Use extract_package_name for better processing
                        target = self.extract_package_name(raw_target)
                        # If extraction fails, try direct alias lookup
                        if not target:
                            target = self.package_aliases.get(raw_target, raw_target)
                    
                    return Intent(
                        type=intent_type,
                        entities={'target': target, 'package': target},
                        target=target or '',
                        confidence=0.95,
                        raw_input=text
                    )
        
        # No pattern matched
        return Intent(
            type=IntentType.UNKNOWN,
            entities={},
            target='',
            confidence=0.0,
            raw_input=text
        )
    
    def extract_package_name(self, text: str) -> Optional[str]:
        """Extract package name from various phrasings"""
        # Remove common words
        noise_words = {
            'the', 'a', 'an', 'that', 'this', 'please', 'now',
            'for', 'me', 'i', 'need', 'want', 'install', 'get',
            'add', 'download', 'remove', 'uninstall', 'delete'
        }
        
        words = text.lower().split()
        filtered = [w for w in words if w not in noise_words]
        
        if filtered:
            # Try exact match first
            potential_package = ' '.join(filtered)
            if potential_package in self.package_aliases:
                return self.package_aliases[potential_package]
            
            # Try individual words for single word matches
            if len(filtered) == 1:
                return self.package_aliases.get(filtered[0], filtered[0])
            
            # For multi-word, try to find known packages by reducing from end
            for i in range(len(filtered), 0, -1):
                candidate = ' '.join(filtered[:i])
                if candidate in self.package_aliases:
                    return self.package_aliases[candidate]
                    
            # Handle special cases like "python package" -> "python"
            if len(filtered) >= 2:
                first_word = filtered[0]
                if first_word in self.package_aliases:
                    return self.package_aliases[first_word]
                elif first_word in ['python', 'node', 'vim', 'docker', 'firefox']:
                    return self.package_aliases.get(first_word, first_word)
            
            # Return the cleaned up text
            return potential_package
        
        return None
    
    def suggest_alternatives(self, text: str) -> List[str]:
        """Suggest alternative interpretations"""
        suggestions = []
        
        # Check for common misspellings
        if 'fierfix' in text or 'firfox' in text:
            suggestions.append("Did you mean 'firefox'?")
        
        if 'pyton' in text or 'pythn' in text:
            suggestions.append("Did you mean 'python'?")
            
        # Check for ambiguous requests
        if any(word in text for word in ['editor', 'ide']):
            suggestions.extend([
                "Popular editors: vim, neovim, emacs, vscode",
                "Try 'search editor' to see all options"
            ])
            
        return suggestions


# Compatibility alias for tests
IntentRecognizer = IntentEngine
'''
    
    intent_engine_file = Path("src/nix_for_humanity/core/intent_engine.py")
    intent_engine_file.write_text(intent_engine_content)
    print("✅ Fixed IntentEngine structure")

def main():
    """Run the fix"""
    print("🔧 Fixing IntentEngine structure...")
    
    # Change to project directory
    os.chdir("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
    
    try:
        fix_intent_engine()
        print("\n✅ IntentEngine structure fixed!")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()