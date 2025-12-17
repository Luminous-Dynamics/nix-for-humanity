"""
MetricsPlugin - Performance Metrics Collection

Demonstrates StepHandler extension point for collecting performance
metrics during execution.

Features:
- Step execution count tracking
- Success/failure rates
- Average execution time
- Export to JSON
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json
import time

from luminous_nix.core.plugin_registry import Plugin
from luminous_nix.core.extension_points import StepHandler
from luminous_nix.core.execution_plan import ExecutionStep


class MetricsStepHandler(StepHandler):
    """
    StepHandler that collects performance metrics.

    Wraps step execution to collect timing and success/failure data.
    """

    def __init__(self, plugin: 'MetricsPlugin'):
        """
        Initialize metrics step handler.

        Args:
            plugin: Parent MetricsPlugin instance
        """
        self.plugin = plugin

    def can_handle(self, step_type: str) -> bool:
        """
        Can handle any step type for metrics.

        Args:
            step_type: Type of step

        Returns:
            Always True (collects metrics for all steps)
        """
        return True

    def execute(self, step: ExecutionStep, context: Dict[str, Any]) -> Any:
        """
        Execute step while collecting metrics.

        Args:
            step: ExecutionStep to execute
            context: Execution context

        Returns:
            Result from actual step execution
        """
        start_time = time.time()

        try:
            # Execute actual step
            result = step.handler(step.parameters)

            # Record success metrics
            duration_ms = (time.time() - start_time) * 1000
            self.plugin._record_success(step.id, duration_ms)

            return result

        except Exception as e:
            # Record failure metrics
            duration_ms = (time.time() - start_time) * 1000
            self.plugin._record_failure(step.id, duration_ms, e)

            # Re-raise the error
            raise


class MetricsPlugin(Plugin):
    """
    Example plugin demonstrating performance metrics collection.

    Tracks execution count, success rate, and timing for all steps.

    Example:
        >>> plugin = MetricsPlugin()
        >>> registry.register(plugin)
        >>> registry.enable_plugin("metrics-plugin")
        >>> # Execute some steps...
        >>> metrics = plugin.get_metrics()
        >>> print(f"Success rate: {metrics['success_rate']}%")
    """

    def __init__(self):
        """Initialize metrics plugin"""
        super().__init__()

        self.metrics: Dict[str, Any] = {
            'total_steps': 0,
            'successful_steps': 0,
            'failed_steps': 0,
            'total_duration_ms': 0.0,
            'step_details': []
        }

        self.step_handler: Optional[MetricsStepHandler] = None

    @property
    def name(self) -> str:
        """Plugin name"""
        return "metrics-plugin"

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
        return "Collects performance metrics for step execution"

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        pass

    def on_enable(self) -> None:
        """
        Called when plugin is enabled.

        Creates and registers the metrics step handler.
        """
        self.step_handler = MetricsStepHandler(self)
        self.metrics['start_time'] = datetime.now().isoformat()

    def on_disable(self) -> None:
        """
        Called when plugin is disabled.

        Finalizes metrics collection.
        """
        self.metrics['end_time'] = datetime.now().isoformat()
        self.step_handler = None

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        pass

    def _record_success(self, step_id: str, duration_ms: float) -> None:
        """
        Record successful step execution.

        Args:
            step_id: ID of step
            duration_ms: Execution duration in milliseconds
        """
        self.metrics['total_steps'] += 1
        self.metrics['successful_steps'] += 1
        self.metrics['total_duration_ms'] += duration_ms

        self.metrics['step_details'].append({
            'step_id': step_id,
            'status': 'success',
            'duration_ms': round(duration_ms, 2),
            'timestamp': datetime.now().isoformat()
        })

    def _record_failure(self, step_id: str, duration_ms: float, error: Exception) -> None:
        """
        Record failed step execution.

        Args:
            step_id: ID of step
            duration_ms: Execution duration in milliseconds
            error: Exception that occurred
        """
        self.metrics['total_steps'] += 1
        self.metrics['failed_steps'] += 1
        self.metrics['total_duration_ms'] += duration_ms

        self.metrics['step_details'].append({
            'step_id': step_id,
            'status': 'failure',
            'duration_ms': round(duration_ms, 2),
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat()
        })

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get collected metrics.

        Returns:
            Dictionary of metrics including:
            - total_steps: Total number of steps executed
            - successful_steps: Number of successful steps
            - failed_steps: Number of failed steps
            - success_rate: Percentage of successful steps
            - average_duration_ms: Average step duration
            - step_details: List of individual step metrics
        """
        metrics = dict(self.metrics)

        # Calculate derived metrics
        if metrics['total_steps'] > 0:
            metrics['success_rate'] = round(
                (metrics['successful_steps'] / metrics['total_steps']) * 100,
                2
            )
            metrics['failure_rate'] = round(
                (metrics['failed_steps'] / metrics['total_steps']) * 100,
                2
            )
            metrics['average_duration_ms'] = round(
                metrics['total_duration_ms'] / metrics['total_steps'],
                2
            )
        else:
            metrics['success_rate'] = 0.0
            metrics['failure_rate'] = 0.0
            metrics['average_duration_ms'] = 0.0

        return metrics

    def export_metrics(self, file_path: str) -> None:
        """
        Export metrics to JSON file.

        Args:
            file_path: Path to output file
        """
        metrics = self.get_metrics()

        with open(file_path, 'w') as f:
            json.dump(metrics, f, indent=2)

    def reset_metrics(self) -> None:
        """Reset all metrics to initial state"""
        self.metrics = {
            'total_steps': 0,
            'successful_steps': 0,
            'failed_steps': 0,
            'total_duration_ms': 0.0,
            'step_details': []
        }

    def get_summary(self) -> str:
        """
        Get human-readable metrics summary.

        Returns:
            Formatted string with key metrics
        """
        metrics = self.get_metrics()

        return f"""
Metrics Summary
===============
Total Steps:      {metrics['total_steps']}
Successful:       {metrics['successful_steps']} ({metrics['success_rate']}%)
Failed:           {metrics['failed_steps']} ({metrics['failure_rate']}%)
Avg Duration:     {metrics['average_duration_ms']} ms
Total Duration:   {metrics['total_duration_ms']:.2f} ms
        """.strip()


if __name__ == "__main__":
    # Example usage
    print("MetricsPlugin Example")
    print("-" * 50)

    # Create plugin
    plugin = MetricsPlugin()

    # Simulate plugin lifecycle
    plugin.on_load()
    plugin.on_enable()

    # Simulate some step executions
    plugin._record_success("step1", 100.5)
    plugin._record_success("step2", 50.2)
    plugin._record_failure("step3", 75.8, Exception("Test error"))
    plugin._record_success("step4", 200.1)

    # Get metrics
    print("\n" + plugin.get_summary())

    # Export to file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        plugin.export_metrics(f.name)
        print(f"\nMetrics exported to: {f.name}")

    # Disable plugin
    plugin.on_disable()
