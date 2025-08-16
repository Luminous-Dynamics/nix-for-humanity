"""
Hook System for Plugin Architecture.

Provides a flexible hook system that allows plugins to intercept
and modify behavior at various points in the application lifecycle.

Since: v1.0.0
"""

import asyncio
from collections import defaultdict
from collections.abc import Callable
from enum import IntEnum
from typing import Any

from ..core.logging_config import get_logger

logger = get_logger(__name__)


class HookPriority(IntEnum):
    """
    Standard hook priorities.

    Lower values execute first.

    Since: v1.0.0
    """

    FIRST = 0
    VERY_HIGH = 10
    HIGH = 25
    NORMAL = 50
    LOW = 75
    VERY_LOW = 90
    LAST = 100


class Hook:
    """
    Represents a single hook registration.

    Since: v1.0.0
    """

    def __init__(
        self,
        name: str,
        callback: Callable,
        plugin_name: str,
        priority: int = HookPriority.NORMAL,
    ):
        """
        Initialize hook.

        Args:
            name: Hook point name
            callback: Function to call
            plugin_name: Plugin that registered this hook
            priority: Execution priority
        """
        self.name = name
        self.callback = callback
        self.plugin_name = plugin_name
        self.priority = priority
        self.is_async = asyncio.iscoroutinefunction(callback)

    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the hook.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Hook result
        """
        try:
            if self.is_async:
                return await self.callback(*args, **kwargs)
            return self.callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Hook error in {self.plugin_name}.{self.name}: {e}")
            raise


class HookManager:
    """
    Manages hook registration and execution.

    Provides a central registry for hooks and handles their
    execution in priority order with error isolation.

    Since: v1.0.0
    """

    # Standard hook points
    HOOKS = {
        # Query processing
        "pre_parse": "Before parsing user query",
        "post_parse": "After parsing query into intent",
        "pre_execute": "Before executing command",
        "post_execute": "After command execution",
        # Error handling
        "on_error": "When an error occurs",
        "on_recovery": "During error recovery",
        # Learning
        "on_learn": "When pattern detected",
        "on_feedback": "When user provides feedback",
        # Configuration
        "on_config_change": "When configuration changes",
        "on_plugin_load": "When a plugin is loaded",
        "on_plugin_unload": "When a plugin is unloaded",
        # UI Events
        "on_progress": "Progress update",
        "on_complete": "Operation complete",
        "on_cancel": "Operation cancelled",
    }

    def __init__(self):
        """Initialize hook manager."""
        self.hooks: dict[str, list[Hook]] = defaultdict(list)
        self.hook_results: dict[str, list[Any]] = defaultdict(list)

    def register_hook(
        self,
        hook_name: str,
        callback: Callable,
        plugin_name: str = "core",
        priority: int = HookPriority.NORMAL,
    ) -> None:
        """
        Register a hook.

        Args:
            hook_name: Name of the hook point
            callback: Function to call
            plugin_name: Plugin registering the hook
            priority: Execution priority
        """
        hook = Hook(hook_name, callback, plugin_name, priority)

        # Insert in priority order
        hooks = self.hooks[hook_name]
        insert_pos = len(hooks)

        for i, existing in enumerate(hooks):
            if existing.priority > priority:
                insert_pos = i
                break

        hooks.insert(insert_pos, hook)
        logger.debug(
            f"Registered hook {hook_name} from {plugin_name} " f"at priority {priority}"
        )

    def unregister_hook(self, hook_name: str, callback: Callable) -> bool:
        """
        Unregister a specific hook.

        Args:
            hook_name: Hook point name
            callback: Callback to remove

        Returns:
            True if found and removed
        """
        if hook_name not in self.hooks:
            return False

        hooks = self.hooks[hook_name]
        for i, hook in enumerate(hooks):
            if hook.callback == callback:
                del hooks[i]
                logger.debug(f"Unregistered hook {hook_name}")
                return True

        return False

    def unregister_plugin_hooks(self, plugin_name: str) -> int:
        """
        Unregister all hooks from a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Number of hooks removed
        """
        removed = 0

        for hook_name in list(self.hooks.keys()):
            hooks = self.hooks[hook_name]
            original_len = len(hooks)

            # Remove all hooks from this plugin
            self.hooks[hook_name] = [h for h in hooks if h.plugin_name != plugin_name]

            removed += original_len - len(self.hooks[hook_name])

            # Clean up empty hook lists
            if not self.hooks[hook_name]:
                del self.hooks[hook_name]

        if removed:
            logger.debug(f"Unregistered {removed} hooks from {plugin_name}")

        return removed

    async def execute_hook(
        self, hook_name: str, *args, stop_on_result: bool = False, **kwargs
    ) -> list[Any]:
        """
        Execute all hooks for a hook point.

        Args:
            hook_name: Hook point name
            *args: Positional arguments for hooks
            stop_on_result: Stop if a hook returns non-None
            **kwargs: Keyword arguments for hooks

        Returns:
            List of results from all executed hooks
        """
        if hook_name not in self.hooks:
            return []

        results = []
        hooks = self.hooks[hook_name]

        logger.debug(f"Executing {len(hooks)} hooks for {hook_name}")

        for hook in hooks:
            try:
                result = await hook.execute(*args, **kwargs)
                results.append(result)

                # Some hooks can stop the chain
                if stop_on_result and result is not None:
                    logger.debug(f"Hook {hook.plugin_name} stopped chain with result")
                    break

            except Exception as e:
                logger.error(
                    f"Error executing hook {hook_name} from " f"{hook.plugin_name}: {e}"
                )
                # Continue with other hooks despite error
                results.append(None)

        # Store results for debugging
        self.hook_results[hook_name] = results

        return results

    def get_hook_info(self, hook_name: str) -> list[dict[str, Any]]:
        """
        Get information about registered hooks.

        Args:
            hook_name: Hook point name

        Returns:
            List of hook information dictionaries
        """
        if hook_name not in self.hooks:
            return []

        return [
            {
                "plugin": hook.plugin_name,
                "priority": hook.priority,
                "is_async": hook.is_async,
                "function": hook.callback.__name__,
            }
            for hook in self.hooks[hook_name]
        ]

    def list_hook_points(self) -> dict[str, str]:
        """
        List all available hook points.

        Returns:
            Dictionary of hook names to descriptions
        """
        return self.HOOKS.copy()

    def list_active_hooks(self) -> dict[str, int]:
        """
        List active hook points with registration counts.

        Returns:
            Dictionary of hook names to registration counts
        """
        return {name: len(hooks) for name, hooks in self.hooks.items()}


def hook(name: str, priority: int = HookPriority.NORMAL) -> Callable:
    """
    Decorator for marking methods as hooks.

    Usage:
        @hook("pre_execute", priority=HookPriority.HIGH)
        def my_hook(self, query: str) -> str:
            return query.lower()

    Args:
        name: Hook point name
        priority: Execution priority

    Returns:
        Decorated function

    Since: v1.0.0
    """

    def decorator(func: Callable) -> Callable:
        func._hook_name = name
        func._hook_priority = priority
        return func

    return decorator
