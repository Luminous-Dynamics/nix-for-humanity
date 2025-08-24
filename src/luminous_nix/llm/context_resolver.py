#!/usr/bin/env python3
"""
🔄 Context Resolver - Handles Referential Commands in Conversations
Resolves "install that", "the first one", "try again" etc.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum


class ReferenceType(Enum):
    """Types of references in natural language"""
    ORDINAL = "ordinal"          # first, second, third, last
    DEMONSTRATIVE = "demonstrative"  # that, this, those, these
    PRONOUN = "pronoun"          # it, them
    RELATIVE = "relative"        # previous, above, before
    TEMPORAL = "temporal"        # again, retry, repeat


class ContextResolver:
    """
    Resolves contextual references in natural language
    Makes conversation feel natural by understanding what "that" refers to
    """
    
    def __init__(self):
        """Initialize the context resolver"""
        self.reference_patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[ReferenceType, List[re.Pattern]]:
        """Compile regex patterns for different reference types"""
        return {
            ReferenceType.ORDINAL: [
                re.compile(r'\b(first|1st)\b', re.I),
                re.compile(r'\b(second|2nd)\b', re.I),
                re.compile(r'\b(third|3rd)\b', re.I),
                re.compile(r'\b(fourth|4th)\b', re.I),
                re.compile(r'\b(fifth|5th)\b', re.I),
                re.compile(r'\b(last|final)\b', re.I),
            ],
            ReferenceType.DEMONSTRATIVE: [
                re.compile(r'\b(that|this)\s+(one|package|option|choice)\b', re.I),
                re.compile(r'\b(those|these)\s+(ones|packages|options)\b', re.I),
                re.compile(r'\bjust\s+(that|this)\b', re.I),
            ],
            ReferenceType.PRONOUN: [
                re.compile(r'\bit\b(?!\s+is|\s+was)', re.I),  # "it" but not "it is"
                re.compile(r'\bthem\b', re.I),
                re.compile(r'\ball\s+of\s+them\b', re.I),
            ],
            ReferenceType.RELATIVE: [
                re.compile(r'\b(previous|above|earlier)\s+(one|package|option)?\b', re.I),
                re.compile(r'\bwhat\s+you\s+(just\s+)?showed\b', re.I),
                re.compile(r'\bfrom\s+before\b', re.I),
            ],
            ReferenceType.TEMPORAL: [
                re.compile(r'\b(try|do)\s+(that\s+)?again\b', re.I),
                re.compile(r'\bretry\b', re.I),
                re.compile(r'\brepeat\s+(that|the\s+last)?\b', re.I),
            ]
        }
    
    def detect_reference(self, message: str) -> Optional[Tuple[ReferenceType, str]]:
        """
        Detect if message contains a reference
        
        Returns:
            Tuple of (reference_type, matched_text) or None
        """
        for ref_type, patterns in self.reference_patterns.items():
            for pattern in patterns:
                match = pattern.search(message)
                if match:
                    return (ref_type, match.group(0))
        
        return None
    
    def resolve(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve references in the message using context
        
        Args:
            message: User message potentially containing references
            context: Conversation context with history
            
        Returns:
            Resolved intent with concrete values
        """
        # Detect reference type
        reference = self.detect_reference(message)
        if not reference:
            # No reference detected, return as-is
            return self._extract_direct_intent(message)
        
        ref_type, ref_text = reference
        
        # Resolve based on reference type
        if ref_type == ReferenceType.ORDINAL:
            return self._resolve_ordinal(message, ref_text, context)
        elif ref_type == ReferenceType.DEMONSTRATIVE:
            return self._resolve_demonstrative(message, ref_text, context)
        elif ref_type == ReferenceType.PRONOUN:
            return self._resolve_pronoun(message, context)
        elif ref_type == ReferenceType.RELATIVE:
            return self._resolve_relative(message, context)
        elif ref_type == ReferenceType.TEMPORAL:
            return self._resolve_temporal(message, context)
        
        return self._extract_direct_intent(message)
    
    def _resolve_ordinal(
        self,
        message: str,
        ref_text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve ordinal references (first, second, last)
        
        Example: "install the first one"
        """
        # Get recent search results or list
        last_list = self._get_last_list(context)
        if not last_list:
            return {
                "action": "clarify",
                "error": "No previous list to reference",
                "original_message": message
            }
        
        # Map ordinal to index
        index = self._ordinal_to_index(ref_text, len(last_list))
        if index is None or index >= len(last_list):
            return {
                "action": "clarify",
                "error": f"Cannot find {ref_text} in the list",
                "original_message": message
            }
        
        # Determine action from message
        action = self._detect_action(message)
        item = last_list[index]
        
        if action == "install":
            return {
                "action": "install",
                "package": item.get("name", item),
                "resolved_from": f"{ref_text} of {len(last_list)} options"
            }
        elif action == "explain":
            return {
                "action": "explain",
                "concept": item.get("name", item),
                "resolved_from": ref_text
            }
        else:
            return {
                "action": action,
                "target": item,
                "resolved_from": ref_text
            }
    
    def _resolve_demonstrative(
        self,
        message: str,
        ref_text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve demonstrative references (that, this, those)
        
        Example: "install that package"
        """
        # Get most recent relevant item
        last_item = self._get_last_mentioned_item(context)
        if not last_item:
            return {
                "action": "clarify",
                "error": "Not sure what 'that' refers to",
                "original_message": message
            }
        
        action = self._detect_action(message)
        
        if "those" in ref_text or "these" in ref_text:
            # Plural reference - get all recent items
            items = self._get_last_list(context)
            return {
                "action": action,
                "targets": items,
                "resolved_from": "recent list",
                "multiple": True
            }
        else:
            # Singular reference
            return {
                "action": action,
                "target": last_item,
                "resolved_from": "last mentioned item"
            }
    
    def _resolve_pronoun(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve pronoun references (it, them)
        
        Example: "install it"
        """
        if "them" in message.lower() or "all of them" in message.lower():
            # Plural pronoun
            items = self._get_last_list(context)
            if not items:
                return {
                    "action": "clarify",
                    "error": "No items to reference",
                    "original_message": message
                }
            
            return {
                "action": self._detect_action(message),
                "targets": items,
                "multiple": True,
                "resolved_from": "pronoun reference to list"
            }
        else:
            # Singular pronoun "it"
            last_item = self._get_last_mentioned_item(context)
            if not last_item:
                return {
                    "action": "clarify",
                    "error": "Not sure what 'it' refers to",
                    "original_message": message
                }
            
            return {
                "action": self._detect_action(message),
                "target": last_item,
                "resolved_from": "pronoun reference"
            }
    
    def _resolve_relative(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve relative references (previous, above, earlier)
        
        Example: "use the previous option"
        """
        # Get second-to-last item or action
        history = context.get("history", [])
        if len(history) < 2:
            return {
                "action": "clarify",
                "error": "No previous item to reference",
                "original_message": message
            }
        
        # Look back through history
        for entry in reversed(history[:-1]):  # Skip most recent
            if "package" in entry or "result" in entry:
                target = entry.get("package") or entry.get("result")
                return {
                    "action": self._detect_action(message),
                    "target": target,
                    "resolved_from": "previous interaction"
                }
        
        return {
            "action": "clarify",
            "error": "Could not find previous reference",
            "original_message": message
        }
    
    def _resolve_temporal(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve temporal references (again, retry, repeat)
        
        Example: "try that again"
        """
        # Get last action from history
        last_action = self._get_last_action(context)
        if not last_action:
            return {
                "action": "clarify",
                "error": "No previous action to repeat",
                "original_message": message
            }
        
        # Check if it was an error that needs retry
        if last_action.get("success") == False:
            # Retry with modifications
            return {
                "action": last_action.get("action"),
                "retry": True,
                "previous_error": last_action.get("error"),
                "modifications": self._suggest_modifications(last_action),
                **last_action.get("parameters", {})
            }
        else:
            # Repeat successful action
            return {
                "action": last_action.get("action"),
                "repeat": True,
                **last_action.get("parameters", {})
            }
    
    def _extract_direct_intent(self, message: str) -> Dict[str, Any]:
        """Extract intent when no reference is found"""
        action = self._detect_action(message)
        
        # Extract target from message
        target = None
        words = message.split()
        
        # Look for package/concept name after action word
        action_words = ["install", "remove", "search", "explain", "show"]
        for i, word in enumerate(words):
            if word.lower() in action_words and i + 1 < len(words):
                target = " ".join(words[i+1:])
                break
        
        return {
            "action": action,
            "target": target,
            "direct": True
        }
    
    def _detect_action(self, message: str) -> str:
        """Detect the intended action from the message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["install", "add", "get"]):
            return "install"
        elif any(word in message_lower for word in ["remove", "uninstall", "delete"]):
            return "remove"
        elif any(word in message_lower for word in ["search", "find", "look"]):
            return "search"
        elif any(word in message_lower for word in ["explain", "what is", "describe"]):
            return "explain"
        elif any(word in message_lower for word in ["list", "show", "display"]):
            return "list"
        elif any(word in message_lower for word in ["update", "upgrade"]):
            return "update"
        else:
            return "unknown"
    
    def _get_last_list(self, context: Dict[str, Any]) -> List[Any]:
        """Get the most recent list from context"""
        # Check for search results
        if "last_search_results" in context:
            return context["last_search_results"]
        
        # Check history for lists
        history = context.get("history", [])
        for entry in reversed(history):
            if "packages" in entry:
                return entry["packages"]
            elif "results" in entry:
                return entry["results"]
            elif "list" in entry:
                return entry["list"]
        
        return []
    
    def _get_last_mentioned_item(self, context: Dict[str, Any]) -> Optional[Any]:
        """Get the most recently mentioned single item"""
        # Check for last selected item
        if "last_selected" in context:
            return context["last_selected"]
        
        # Check history
        history = context.get("history", [])
        for entry in reversed(history):
            if "package" in entry:
                return entry["package"]
            elif "target" in entry:
                return entry["target"]
            elif "item" in entry:
                return entry["item"]
        
        # Check last list and return first item
        last_list = self._get_last_list(context)
        if last_list:
            return last_list[0]
        
        return None
    
    def _get_last_action(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the last action performed"""
        history = context.get("history", [])
        if history:
            return history[-1]
        return None
    
    def _ordinal_to_index(self, ordinal_text: str, list_length: int) -> Optional[int]:
        """Convert ordinal text to list index"""
        ordinal_map = {
            "first": 0, "1st": 0,
            "second": 1, "2nd": 1,
            "third": 2, "3rd": 2,
            "fourth": 3, "4th": 3,
            "fifth": 4, "5th": 4,
            "last": list_length - 1,
            "final": list_length - 1
        }
        
        for key, index in ordinal_map.items():
            if key in ordinal_text.lower():
                return index
        
        return None
    
    def _suggest_modifications(self, failed_action: Dict[str, Any]) -> List[str]:
        """Suggest modifications for a failed action"""
        suggestions = []
        
        error = failed_action.get("error", "").lower()
        
        if "permission" in error:
            suggestions.append("Try with sudo or --user flag")
        elif "not found" in error:
            suggestions.append("Check package name spelling")
            suggestions.append("Search for similar packages first")
        elif "space" in error:
            suggestions.append("Free up disk space with garbage collection")
        elif "network" in error:
            suggestions.append("Check network connection")
            suggestions.append("Update channels first")
        
        return suggestions


def demo_context_resolution():
    """Demonstrate context resolution capabilities"""
    print("🔄 Context Resolution Demonstration")
    print("=" * 60)
    
    resolver = ContextResolver()
    
    # Sample context with search results
    context = {
        "last_search_results": [
            {"name": "firefox", "description": "Web browser"},
            {"name": "chromium", "description": "Open source browser"},
            {"name": "brave", "description": "Privacy-focused browser"}
        ],
        "history": [
            {
                "action": "search",
                "query": "web browser",
                "packages": [
                    {"name": "firefox"},
                    {"name": "chromium"},
                    {"name": "brave"}
                ],
                "success": True
            }
        ]
    }
    
    # Test various references
    test_cases = [
        "install the first one",
        "get the second option",
        "install that",
        "remove it",
        "explain the last one",
        "install all of them",
        "try again",
        "use the previous one"
    ]
    
    for message in test_cases:
        print(f"\n📝 Message: '{message}'")
        
        # Detect reference
        reference = resolver.detect_reference(message)
        if reference:
            ref_type, ref_text = reference
            print(f"   🔍 Detected: {ref_type.value} reference - '{ref_text}'")
        
        # Resolve
        result = resolver.resolve(message, context)
        
        if result.get("action") == "clarify":
            print(f"   ❓ Needs clarification: {result.get('error')}")
        else:
            print(f"   ✅ Resolved to: {result.get('action')}")
            if "target" in result:
                target = result["target"]
                if isinstance(target, dict):
                    print(f"      Target: {target.get('name', target)}")
                else:
                    print(f"      Target: {target}")
            elif "package" in result:
                print(f"      Package: {result['package']}")
            if "resolved_from" in result:
                print(f"      Source: {result['resolved_from']}")
    
    print("\n" + "=" * 60)
    print("✨ Context resolution enables natural conversation!")


if __name__ == "__main__":
    demo_context_resolution()