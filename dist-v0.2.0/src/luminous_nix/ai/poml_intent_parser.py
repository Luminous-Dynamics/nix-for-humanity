"""
POML-based Intent Parser for Natural Language Understanding
Uses Microsoft POML v2 specification for structured prompt engineering
"""

import json
import logging
from pathlib import Path
from typing import Any

from luminous_nix.agents.poml_bridge_v2 import POMLProcessor


class POMLIntentParser:
    """Parse user intent using POML-structured prompts"""
    
    def __init__(self):
        """Initialize the POML intent parser"""
        self.logger = logging.getLogger(__name__)
        
        # Load the intent recognition POML template
        poml_path = Path(__file__).parent.parent / "agents" / "intent_recognition.poml"
        self.poml_processor = POMLProcessor(poml_path)
        
        # Fallback mappings for when AI is unavailable
        self.description_to_package = {
            "web browser": "firefox",
            "browser": "firefox",
            "text editor": "vim",
            "editor": "vim",
            "terminal": "alacritty",
            "video player": "vlc",
            "music player": "spotify",
            "pdf reader": "zathura",
            "pdf viewer": "zathura",
            "image editor": "gimp",
            "photo editor": "gimp",
            "file manager": "ranger",
            "password manager": "bitwarden",
            "ide": "vscode",
            "email client": "thunderbird",
            "email": "thunderbird",
            "chat": "discord",
            "messenger": "telegram-desktop",
        }
    
    def parse_with_ai(self, query: str, ollama_client) -> dict[str, Any]:
        """
        Parse intent using AI with POML-structured prompt
        
        Args:
            query: Natural language query from user
            ollama_client: Ollama client for AI processing
            
        Returns:
            Parsed intent with package, confidence, etc.
        """
        try:
            # Generate structured prompt using POML
            context = {"user_query": query}
            structured_prompt = self.poml_processor.process(context)
            
            # Ask AI with structured prompt
            response = ollama_client.ask(structured_prompt, model=ollama_client.models.get("quick"))
            
            if response:
                # Try to parse JSON response
                import re
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    # Ensure we have all expected fields
                    if all(k in result for k in ["intent", "package", "confidence"]):
                        self.logger.debug(f"AI parsed intent: {result}")
                        return result
        except Exception as e:
            self.logger.warning(f"AI parsing failed: {e}")
        
        # Fallback to rule-based parsing
        return self.parse_without_ai(query)
    
    def parse_without_ai(self, query: str) -> dict[str, Any]:
        """
        Parse intent using rule-based approach (no AI required)
        
        Args:
            query: Natural language query from user
            
        Returns:
            Parsed intent with package, confidence, etc.
        """
        query_lower = query.lower()
        
        # Detect intent
        intent = "unknown"
        if "install" in query_lower:
            intent = "install"
        elif "search" in query_lower or "find" in query_lower or "look for" in query_lower:
            intent = "search"
        elif "remove" in query_lower or "uninstall" in query_lower:
            intent = "remove"
        elif "update" in query_lower or "upgrade" in query_lower:
            intent = "update"
        
        # Extract package based on descriptions
        package = None
        description = None
        
        # Check for known descriptions
        for desc, pkg in self.description_to_package.items():
            if desc in query_lower:
                package = pkg
                description = desc
                break
        
        # If no description matched, try to extract from query
        if not package and intent != "unknown":
            words = query_lower.split()
            
            # Find the intent word and get what comes after
            intent_words = ["install", "search", "find", "remove", "uninstall"]
            for word in intent_words:
                if word in words:
                    idx = words.index(word)
                    remaining = words[idx + 1:]
                    
                    # Filter out common filler words
                    ignore = {"a", "an", "the", "for", "to", "me", "how", "do", "i", "some", "any"}
                    filtered = [w for w in remaining if w not in ignore]
                    
                    # Check if it's a compound term
                    if len(filtered) >= 2:
                        two_word = " ".join(filtered[:2])
                        if two_word in self.description_to_package:
                            package = self.description_to_package[two_word]
                            description = two_word
                            break
                    
                    # Otherwise use first meaningful word
                    if filtered and not package:
                        package = filtered[0]
                        description = filtered[0]
                        break
        
        # Calculate confidence
        confidence = 0.3  # Default low confidence
        if intent != "unknown":
            confidence = 0.6
            if package in self.description_to_package.values():
                confidence = 0.8  # Higher confidence for known packages
        
        return {
            "intent": intent,
            "package": package or "",
            "description": description or package or "",
            "confidence": confidence,
            "reasoning": f"Rule-based parsing: detected '{intent}' with '{description or package}'"
        }
    
    def parse(self, query: str, ollama_client=None) -> dict[str, Any]:
        """
        Parse user intent, using AI if available, otherwise rules
        
        Args:
            query: Natural language query from user
            ollama_client: Optional Ollama client for AI parsing
            
        Returns:
            Parsed intent dictionary
        """
        # Try AI first if available
        if ollama_client and hasattr(ollama_client, 'is_available') and ollama_client.is_available():
            result = self.parse_with_ai(query, ollama_client)
            # Only use AI result if confidence is high enough
            if result.get("confidence", 0) > 0.7:
                return result
        
        # Fallback to rule-based
        return self.parse_without_ai(query)