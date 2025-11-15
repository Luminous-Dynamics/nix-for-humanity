#!/usr/bin/env python3
"""
Conversation Memory Manager for Luminous Nix
Maintains context across queries for better AI responses
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class ConversationTurn:
    """Single turn in a conversation"""

    timestamp: float
    query: str
    response: str
    intent: Optional[str] = None
    model_used: Optional[str] = None
    success: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationTurn":
        """Create from dictionary"""
        return cls(**data)


class ConversationMemory:
    """
    Manages conversation history and context
    Provides relevant context to AI for better responses
    """

    def __init__(self, max_history: int = 100, storage_path: Optional[Path] = None):
        """
        Initialize conversation memory

        Args:
            max_history: Maximum turns to keep in memory
            storage_path: Path to persist conversations
        """
        self.max_history = max_history
        self.storage_path = (
            storage_path or Path.home() / ".cache" / "luminous-nix" / "conversations"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Current session
        self.session_id = self._generate_session_id()
        self.history: List[ConversationTurn] = []
        self.context: Dict[str, Any] = {}

        # User patterns and preferences
        self.user_patterns = {
            "common_packages": {},  # Track frequently installed packages
            "common_tasks": {},  # Track common task types
            "preferences": {},  # User preferences (verbosity, etc)
            "corrections": [],  # Learn from corrections
        }

        # Load previous session if exists
        self._load_last_session()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]

    def add_turn(
        self,
        query: str,
        response: str,
        intent: Optional[str] = None,
        model_used: Optional[str] = None,
        success: bool = True,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Add a conversation turn to memory

        Args:
            query: User's query
            response: System's response
            intent: Detected intent type
            model_used: Which AI model was used
            success: Whether the operation succeeded
            metadata: Additional metadata
        """
        turn = ConversationTurn(
            timestamp=time.time(),
            query=query,
            response=response,
            intent=intent,
            model_used=model_used,
            success=success,
            metadata=metadata or {},
        )

        self.history.append(turn)

        # Maintain max history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        # Update patterns
        self._update_patterns(turn)

        # Extract context
        self._extract_context(turn)

        # Auto-save periodically
        if len(self.history) % 10 == 0:
            self.save_session()

    def _update_patterns(self, turn: ConversationTurn) -> None:
        """Update user patterns from conversation turn"""
        # Track package installations
        if turn.intent == "install" and turn.success:
            package = self._extract_package_name(turn.query)
            if package:
                self.user_patterns["common_packages"][package] = (
                    self.user_patterns["common_packages"].get(package, 0) + 1
                )

        # Track task types
        if turn.intent:
            self.user_patterns["common_tasks"][turn.intent] = (
                self.user_patterns["common_tasks"].get(turn.intent, 0) + 1
            )

    def _extract_context(self, turn: ConversationTurn) -> None:
        """Extract reusable context from turn"""
        # Remember recent packages
        if "package" in turn.query.lower():
            package = self._extract_package_name(turn.query)
            if package:
                self.context["last_package"] = package
                self.context["last_package_time"] = turn.timestamp

        # Remember configuration context
        if "configuration" in turn.query.lower() or "config" in turn.query.lower():
            self.context["discussing_config"] = True
            self.context["config_start_time"] = turn.timestamp

        # Remember error context
        if "error" in turn.query.lower() or "failed" in turn.query.lower():
            self.context["debugging"] = True
            self.context["error_context"] = turn.query

    def get_relevant_context(self, query: str, max_turns: int = 5) -> Dict[str, Any]:
        """
        Get relevant context for a new query

        Args:
            query: The new query
            max_turns: Maximum historical turns to include

        Returns:
            Dictionary with relevant context
        """
        context = {
            "session_id": self.session_id,
            "turn_number": len(self.history) + 1,
            "recent_history": [],
            "relevant_history": [],
            "user_patterns": self.user_patterns,
            "current_context": self.context.copy(),
        }

        # Add recent history
        if self.history:
            context["recent_history"] = [
                {
                    "query": turn.query,
                    "response": turn.response[:200],  # Truncate long responses
                    "intent": turn.intent,
                    "time_ago": time.time() - turn.timestamp,
                }
                for turn in self.history[-max_turns:]
            ]

        # Find relevant historical context
        query_lower = query.lower()
        keywords = set(query_lower.split())

        for turn in reversed(self.history[:-max_turns]):
            turn_keywords = set(turn.query.lower().split())
            overlap = len(keywords & turn_keywords)

            if overlap >= 2:  # At least 2 words in common
                context["relevant_history"].append(
                    {
                        "query": turn.query,
                        "response": turn.response[:200],
                        "relevance_score": overlap,
                        "time_ago": time.time() - turn.timestamp,
                    }
                )

                if len(context["relevant_history"]) >= 3:
                    break

        # Add commonly used packages if discussing installation
        if any(word in query_lower for word in ["install", "package", "setup"]):
            top_packages = sorted(
                self.user_patterns["common_packages"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5]
            context["frequently_used_packages"] = [pkg for pkg, _ in top_packages]

        return context

    def add_correction(self, original_query: str, corrected_intent: str) -> None:
        """Learn from user corrections"""
        self.user_patterns["corrections"].append(
            {
                "original": original_query,
                "corrected": corrected_intent,
                "timestamp": time.time(),
            }
        )

        # Keep only recent corrections
        if len(self.user_patterns["corrections"]) > 50:
            self.user_patterns["corrections"] = self.user_patterns["corrections"][-50:]

    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation"""
        if not self.history:
            return "No conversation history yet."

        summary_parts = [f"Session {self.session_id} - {len(self.history)} turns"]

        # Summarize intents
        intent_counts = {}
        for turn in self.history:
            if turn.intent:
                intent_counts[turn.intent] = intent_counts.get(turn.intent, 0) + 1

        if intent_counts:
            summary_parts.append(
                "Topics: "
                + ", ".join(
                    f"{intent} ({count})" for intent, count in intent_counts.items()
                )
            )

        # Recent activity
        if self.history:
            last_turn = self.history[-1]
            time_ago = time.time() - last_turn.timestamp
            if time_ago < 60:
                summary_parts.append(f"Active now")
            else:
                summary_parts.append(f"Last active {int(time_ago/60)} minutes ago")

        return " | ".join(summary_parts)

    def save_session(self) -> None:
        """Save current session to disk"""
        session_file = self.storage_path / f"session_{self.session_id}.json"

        data = {
            "session_id": self.session_id,
            "history": [turn.to_dict() for turn in self.history],
            "context": self.context,
            "user_patterns": self.user_patterns,
            "timestamp": time.time(),
        }

        with open(session_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_last_session(self) -> None:
        """Load the most recent session if available"""
        sessions = list(self.storage_path.glob("session_*.json"))
        if not sessions:
            return

        # Get most recent session
        latest = max(sessions, key=lambda p: p.stat().st_mtime)

        try:
            with open(latest) as f:
                data = json.load(f)

            # Only load if recent (within 24 hours)
            if time.time() - data.get("timestamp", 0) < 86400:
                # Load user patterns (always useful)
                self.user_patterns = data.get("user_patterns", self.user_patterns)

                # Optionally load recent history
                if time.time() - data.get("timestamp", 0) < 3600:  # Within 1 hour
                    history_data = data.get("history", [])[-10:]  # Last 10 turns
                    self.history = [
                        ConversationTurn.from_dict(turn) for turn in history_data
                    ]
                    self.context = data.get("context", {})
        except Exception as e:
            # Don't fail if session loading fails
            pass

    def _extract_package_name(self, query: str) -> Optional[str]:
        """Extract package name from query"""
        # Simple extraction - can be improved
        tokens = query.lower().split()

        # Look for package name after keywords
        keywords = ["install", "remove", "update", "search"]
        for i, token in enumerate(tokens):
            if token in keywords and i + 1 < len(tokens):
                return tokens[i + 1].strip(".,!?")

        return None

    def clear_session(self) -> None:
        """Clear current session"""
        self.history.clear()
        self.context.clear()
        self.session_id = self._generate_session_id()

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            "total_turns": len(self.history),
            "session_id": self.session_id,
            "success_rate": sum(1 for t in self.history if t.success)
            / len(self.history)
            if self.history
            else 0,
            "top_packages": sorted(
                self.user_patterns["common_packages"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10],
            "top_tasks": sorted(
                self.user_patterns["common_tasks"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10],
            "corrections_made": len(self.user_patterns["corrections"]),
        }


class ContextEnhancer:
    """
    Enhances queries with conversation context
    Makes AI responses more relevant and personalized
    """

    def __init__(self, memory: ConversationMemory):
        self.memory = memory

    def enhance_query(self, query: str) -> str:
        """
        Enhance query with relevant context

        Args:
            query: Original user query

        Returns:
            Enhanced query with context
        """
        context = self.memory.get_relevant_context(query)

        # Don't enhance if no relevant context
        if not context["recent_history"] and not context["relevant_history"]:
            return query

        enhanced_parts = [query]

        # Add recent context if continuing conversation
        if context["recent_history"] and len(context["recent_history"]) > 0:
            last_turn = context["recent_history"][-1]
            if last_turn["time_ago"] < 300:  # Within 5 minutes
                enhanced_parts.append(
                    f"\n[Continuing from: {last_turn['query'][:50]}...]"
                )

        # Add relevant historical context
        if context["relevant_history"]:
            relevant = context["relevant_history"][0]
            enhanced_parts.append(
                f"\n[Previously discussed: {relevant['query'][:50]}...]"
            )

        # Add user preferences
        if context["frequently_used_packages"]:
            enhanced_parts.append(
                f"\n[User frequently uses: {', '.join(context['frequently_used_packages'][:3])}]"
            )

        return "\n".join(enhanced_parts)

    def personalize_response(self, response: str, query: str) -> str:
        """
        Personalize response based on user patterns

        Args:
            response: Original AI response
            query: User's query

        Returns:
            Personalized response
        """
        context = self.memory.get_relevant_context(query)

        # Add personal touches based on patterns
        if context["user_patterns"]["common_tasks"]:
            top_task = max(
                context["user_patterns"]["common_tasks"].items(), key=lambda x: x[1]
            )[0]

            # Add helpful suggestions based on common tasks
            if top_task == "install" and "install" in query.lower():
                packages = context.get("frequently_used_packages", [])
                if packages:
                    response += f"\n\n💡 Based on your history, you might also want: {', '.join(packages[:3])}"

        return response


# Example usage and integration
if __name__ == "__main__":
    # Demo the conversation memory
    memory = ConversationMemory()
    enhancer = ContextEnhancer(memory)

    # Simulate conversation
    queries = [
        "install firefox",
        "how do I configure nginx?",
        "install postgresql",
        "what was that nginx config again?",
        "install firefox",  # Repeated - should be recognized
    ]

    for query in queries:
        print(f"\n📝 Query: {query}")

        # Get context
        context = memory.get_relevant_context(query)

        # Enhance query
        enhanced = enhancer.enhance_query(query)
        if enhanced != query:
            print(f"✨ Enhanced with context")

        # Simulate response
        response = f"Here's how to {query}..."

        # Add to memory
        memory.add_turn(
            query=query,
            response=response,
            intent="install" if "install" in query else "config",
            model_used="pattern",
            success=True,
        )

        # Show relevant context
        if context["recent_history"]:
            print(f"📚 Recent context: {len(context['recent_history'])} turns")
        if context["relevant_history"]:
            print(
                f"🔍 Found relevant history: {context['relevant_history'][0]['query'][:30]}..."
            )

    # Show stats
    print("\n📊 Session Statistics:")
    stats = memory.get_stats()
    print(f"  Total turns: {stats['total_turns']}")
    print(f"  Top packages: {stats['top_packages']}")
    print(f"  Top tasks: {stats['top_tasks']}")

    # Save session
    memory.save_session()
    print(f"\n💾 Session saved as {memory.session_id}")
