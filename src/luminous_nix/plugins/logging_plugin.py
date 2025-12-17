"""
LoggingPlugin - Step Execution Logging

Demonstrates StepHandler extension point for capturing and logging
all step executions during plan execution.

Features:
- Captures all step executions
- Configurable log levels
- File and console output
- Structured log format
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum
import json
import time

from luminous_nix.core.plugin_registry import Plugin
from luminous_nix.core.extension_points import StepHandler
from luminous_nix.core.execution_plan import ExecutionStep


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5


class LoggingStepHandler(StepHandler):
    """
    StepHandler that logs all step executions.

    Wraps actual step execution with logging before and after.
    """

    def __init__(self, plugin: 'LoggingPlugin'):
        """
        Initialize logging step handler.

        Args:
            plugin: Parent LoggingPlugin instance
        """
        self.plugin = plugin

    def can_handle(self, step_type: str) -> bool:
        """
        Can handle any step type for logging.

        Args:
            step_type: Type of step

        Returns:
            Always True (logs all steps)
        """
        return True

    def execute(self, step: ExecutionStep, context: Dict[str, Any]) -> Any:
        """
        Execute step while logging execution details.

        Args:
            step: ExecutionStep to execute
            context: Execution context

        Returns:
            Result from actual step execution
        """
        start_time = time.time()

        # Log step start
        self.plugin._add_log({
            'event': 'step_start',
            'step_id': step.id,
            'step_name': step.name,
            'timestamp': datetime.now().isoformat(),
            'parameters': step.parameters
        })

        try:
            # Execute actual step
            result = step.handler(step.parameters)

            # Log successful completion
            duration_ms = (time.time() - start_time) * 1000
            self.plugin._add_log({
                'event': 'step_complete',
                'step_id': step.id,
                'step_name': step.name,
                'timestamp': datetime.now().isoformat(),
                'duration_ms': round(duration_ms, 2),
                'status': 'success'
            })

            return result

        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            self.plugin._add_log({
                'event': 'step_error',
                'step_id': step.id,
                'step_name': step.name,
                'timestamp': datetime.now().isoformat(),
                'duration_ms': round(duration_ms, 2),
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            })

            # Re-raise the error
            raise


class LoggingPlugin(Plugin):
    """
    Example plugin demonstrating step execution logging.

    Captures and logs all step executions with configurable output
    to file and/or console.

    Example:
        >>> plugin = LoggingPlugin(log_file="execution.log")
        >>> registry.register(plugin)
        >>> registry.enable_plugin("logging-plugin")
        >>> # Now all step executions will be logged
    """

    def __init__(
        self,
        log_level: LogLevel = LogLevel.INFO,
        log_file: Optional[str] = None,
        console_output: bool = True
    ):
        """
        Initialize logging plugin.

        Args:
            log_level: Minimum log level to capture
            log_file: Optional file path for log output
            console_output: Whether to print logs to console
        """
        super().__init__()
        self.log_level = log_level
        self.log_file = Path(log_file) if log_file else None
        self.console_output = console_output

        self.logs: List[Dict[str, Any]] = []
        self.step_handler: Optional[LoggingStepHandler] = None

    @property
    def name(self) -> str:
        """Plugin name"""
        return "logging-plugin"

    @property
    def version(self) -> str:
        """Plugin version"""
        return "1.0.0"

    @property
    def author(self) -> str:
        """Plugin author"""
        return "Luminous Dynamics"

    @property
    def description(self) -> str:
        """Plugin description"""
        return "Logs all step executions with configurable output"

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        pass

    def on_enable(self) -> None:
        """
        Called when plugin is enabled.

        Creates and registers the logging step handler.
        """
        self.step_handler = LoggingStepHandler(self)
        self.log_info("plugin", "LoggingPlugin enabled")

    def on_disable(self) -> None:
        """
        Called when plugin is disabled.

        Flushes any pending logs.
        """
        self.flush_logs()
        self.step_handler = None
        self.log_info("plugin", "LoggingPlugin disabled")

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        self.flush_logs()

    def _add_log(self, log_entry: Dict[str, Any]) -> None:
        """
        Add log entry to storage.

        Args:
            log_entry: Log entry dictionary
        """
        self.logs.append(log_entry)

        # Console output if enabled
        if self.console_output:
            print(f"[{log_entry.get('timestamp', 'N/A')}] {log_entry}")

        # File output if configured
        if self.log_file:
            self._write_to_file(log_entry)

    def _write_to_file(self, log_entry: Dict[str, Any]) -> None:
        """
        Write log entry to file.

        Args:
            log_entry: Log entry dictionary
        """
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def log_info(self, category: str, message: str) -> None:
        """
        Log INFO level message.

        Args:
            category: Log category
            message: Log message
        """
        if self.log_level.value <= LogLevel.INFO.value:
            self._add_log({
                'level': 'INFO',
                'category': category,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })

    def log_warning(self, category: str, message: str) -> None:
        """
        Log WARNING level message.

        Args:
            category: Log category
            message: Log message
        """
        if self.log_level.value <= LogLevel.WARNING.value:
            self._add_log({
                'level': 'WARNING',
                'category': category,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })

    def log_error(self, category: str, message: str, error: Optional[Exception] = None) -> None:
        """
        Log ERROR level message.

        Args:
            category: Log category
            message: Log message
            error: Optional exception
        """
        if self.log_level.value <= LogLevel.ERROR.value:
            entry = {
                'level': 'ERROR',
                'category': category,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            if error:
                entry['error'] = str(error)
                entry['error_type'] = type(error).__name__
            self._add_log(entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Get all logged entries.

        Returns:
            List of log entries
        """
        return list(self.logs)

    def flush_logs(self) -> None:
        """Flush any buffered logs to file"""
        # All logs already written immediately
        pass

    def clear_logs(self) -> None:
        """Clear in-memory logs"""
        self.logs.clear()


if __name__ == "__main__":
    # Example usage
    print("LoggingPlugin Example")
    print("-" * 50)

    # Create plugin
    plugin = LoggingPlugin(
        log_level=LogLevel.INFO,
        console_output=True
    )

    # Simulate plugin lifecycle
    plugin.on_load()
    plugin.on_enable()

    # Log some messages
    plugin.log_info("test", "This is an info message")
    plugin.log_warning("test", "This is a warning")
    plugin.log_error("test", "This is an error", Exception("Test error"))

    # Get logs
    logs = plugin.get_logs()
    print(f"\nCaptured {len(logs)} log entries")

    # Disable plugin
    plugin.on_disable()
