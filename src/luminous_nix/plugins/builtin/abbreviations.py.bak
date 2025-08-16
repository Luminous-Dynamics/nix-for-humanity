"""
Abbreviations Plugin for Nix for Humanity.

Expands common abbreviations and shortcuts in queries.

Since: v1.0.0
"""

from ..base import BuiltinPlugin, PluginMetadata
from ..hooks import HookPriority, hook


class AbbreviationsPlugin(BuiltinPlugin):
    """
    Expands abbreviations in user queries.

    Examples:
        - "i firefox" -> "install firefox"
        - "rm vim" -> "remove vim"
        - "u system" -> "update system"

    Since: v1.0.0
    """

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="abbreviations",
            version="1.0.0",
            author="Nix for Humanity Team",
            description="Expands common command abbreviations",
            keywords=["shortcuts", "abbreviations", "productivity"],
            hooks=["pre_parse"],
        )

    def initialize(self) -> bool:
        """Initialize plugin with abbreviation mappings."""
        self.abbreviations = {
            # Single letter shortcuts
            "i": "install",
            "r": "remove",
            "s": "search",
            "u": "update",
            "g": "generate",
            "h": "help",
            "l": "list",
            # Common abbreviations
            "rm": "remove",
            "del": "remove",
            "find": "search",
            "show": "info",
            "cfg": "config",
            "gen": "generate",
            "rb": "rollback",
            "upd": "update",
            "pkg": "package",
            "svc": "service",
            "sys": "system",
            # Convenience expansions
            "plz": "please",
            "pls": "please",
            "thx": "thanks",
        }
        return True

    @hook("pre_parse", priority=HookPriority.HIGH)
    def expand_abbreviations(self, query: str) -> str:
        """
        Expand abbreviations in query before parsing.

        Args:
            query: User query

        Returns:
            Query with abbreviations expanded
        """
        words = query.split()
        expanded_words = []

        for word in words:
            # Check if word is an abbreviation
            if word.lower() in self.abbreviations:
                expanded_words.append(self.abbreviations[word.lower()])
            else:
                expanded_words.append(word)

        expanded = " ".join(expanded_words)

        # Log if we made changes
        if expanded != query:
            from ...core.logging_config import get_logger

            logger = get_logger(__name__)
            logger.debug(f"Expanded '{query}' to '{expanded}'")

        return expanded
