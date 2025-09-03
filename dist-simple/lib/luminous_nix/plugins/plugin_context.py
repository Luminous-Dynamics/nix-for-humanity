"""Plugin context module for managing plugin execution environments.

This module provides context management for plugin execution.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PluginContext:
    """Context for plugin execution."""

    name: str
    version: str
    data: dict[str, Any]
    config: dict[str, Any] | None = None

    def get_context(self) -> dict[str, Any]:
        """Get the plugin context."""
        context = {
            "name": self.name,
            "version": self.version,
            "data": self.data,
        }
        if self.config:
            context["config"] = self.config
        return context


def create_context(name: str, version: str = "1.0.0", **kwargs) -> PluginContext:
    """Create a new plugin context."""
    return PluginContext(
        name=name,
        version=version,
        data=kwargs.get("data", {}),
        config=kwargs.get("config"),
    )


# Export for compatibility
__all__ = ["PluginContext", "create_context"]
