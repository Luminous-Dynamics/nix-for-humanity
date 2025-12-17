"""
Test-Driven Development: Example Plugins

Tests for example plugins demonstrating extension point usage.
These plugins showcase real-world patterns for extending Luminous Nix.

Based on: Week 7 Example Plugins
"""

import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


# === Test LoggingPlugin (StepHandler demonstration) ===

def test_logging_plugin_basic():
    """Test LoggingPlugin captures step executions"""
    from luminous_nix.plugins.logging_plugin import LoggingPlugin
    from luminous_nix.core.plugin_registry import PluginRegistry

    plugin = LoggingPlugin()

    # Verify plugin properties
    assert plugin.name == "logging-plugin"
    assert plugin.version.startswith("1.")

    # Register and enable
    registry = PluginRegistry()
    registry.register(plugin)
    registry.enable_plugin("logging-plugin")

    # Verify step handler was created
    assert plugin.step_handler is not None


def test_logging_plugin_captures_steps():
    """Test that LoggingPlugin actually logs step executions"""
    from luminous_nix.plugins.logging_plugin import LoggingPlugin
    from luminous_nix.core.execution_plan import ExecutionStep
    from luminous_nix.core.plugin_registry import PluginRegistry

    plugin = LoggingPlugin()
    registry = PluginRegistry()
    registry.register(plugin)
    registry.enable_plugin("logging-plugin")

    # Create a test step
    step = ExecutionStep(
        id="test_step",
        name="Test Step",
        handler=lambda p: "result",
        parameters={"param": "value"},
        depends_on=set(),
        provides={'output'},
        requires=set()
    )

    # Execute through logging handler
    context = {"test": "data"}
    result = plugin.step_handler.execute(step, context)

    # Verify logging occurred
    assert len(plugin.get_logs()) > 0
    last_log = plugin.get_logs()[-1]
    assert last_log['step_id'] == "test_step"
    assert last_log['step_name'] == "Test Step"
    assert 'timestamp' in last_log
    assert 'duration_ms' in last_log


def test_logging_plugin_log_levels():
    """Test LoggingPlugin respects log levels"""
    from luminous_nix.plugins.logging_plugin import LoggingPlugin, LogLevel

    plugin = LoggingPlugin(log_level=LogLevel.ERROR)

    # Should not log INFO level
    plugin.log_info("test", "This should not appear")
    assert len(plugin.get_logs()) == 0

    # Should log ERROR level
    plugin.log_error("test", "This should appear", Exception("test error"))
    assert len(plugin.get_logs()) == 1


def test_logging_plugin_file_output():
    """Test LoggingPlugin can write to file"""
    from luminous_nix.plugins.logging_plugin import LoggingPlugin

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        plugin = LoggingPlugin(log_file=str(log_file))
        plugin.log_info("test", "Test message")
        plugin.flush_logs()

        # Verify file was written
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content


# === Test MetricsPlugin (Performance monitoring) ===

def test_metrics_plugin_basic():
    """Test MetricsPlugin tracks basic metrics"""
    from luminous_nix.plugins.metrics_plugin import MetricsPlugin
    from luminous_nix.core.plugin_registry import PluginRegistry

    plugin = MetricsPlugin()

    # Verify plugin properties
    assert plugin.name == "metrics-plugin"
    assert plugin.version.startswith("1.")

    # Register and enable
    registry = PluginRegistry()
    registry.register(plugin)
    registry.enable_plugin("metrics-plugin")

    # Verify metrics collector was initialized
    assert plugin.metrics is not None


def test_metrics_plugin_step_metrics():
    """Test MetricsPlugin collects step execution metrics"""
    from luminous_nix.plugins.metrics_plugin import MetricsPlugin
    from luminous_nix.core.execution_plan import ExecutionStep
    from luminous_nix.core.plugin_registry import PluginRegistry

    plugin = MetricsPlugin()
    registry = PluginRegistry()
    registry.register(plugin)
    registry.enable_plugin("metrics-plugin")

    # Create and execute test step
    step = ExecutionStep(
        id="metric_step",
        name="Metric Test",
        handler=lambda p: "success",
        parameters={},
        depends_on=set(),
        provides={'result'},
        requires=set()
    )

    # Execute through metrics handler
    plugin.step_handler.execute(step, {})

    # Verify metrics were collected
    metrics = plugin.get_metrics()
    assert metrics['total_steps'] == 1
    assert metrics['successful_steps'] == 1
    assert 'average_duration_ms' in metrics


def test_metrics_plugin_error_tracking():
    """Test MetricsPlugin tracks errors"""
    from luminous_nix.plugins.metrics_plugin import MetricsPlugin
    from luminous_nix.core.execution_plan import ExecutionStep

    plugin = MetricsPlugin()
    plugin.on_enable()

    # Create step that will fail
    def failing_handler(p):
        raise RuntimeError("Test error")

    step = ExecutionStep(
        id="failing_step",
        name="Failing Step",
        handler=failing_handler,
        parameters={},
        depends_on=set(),
        provides=set(),
        requires=set()
    )

    # Execute and expect failure
    try:
        plugin.step_handler.execute(step, {})
    except RuntimeError:
        pass  # Expected

    # Verify error was tracked
    metrics = plugin.get_metrics()
    assert metrics['total_steps'] == 1
    assert metrics['failed_steps'] == 1
    assert metrics['successful_steps'] == 0


def test_metrics_plugin_export():
    """Test MetricsPlugin can export metrics to JSON"""
    from luminous_nix.plugins.metrics_plugin import MetricsPlugin
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        export_file = Path(tmpdir) / "metrics.json"

        plugin = MetricsPlugin()
        plugin.on_enable()

        # Simulate some activity
        plugin.metrics['total_steps'] = 10
        plugin.metrics['successful_steps'] = 8
        plugin.metrics['failed_steps'] = 2

        # Export
        plugin.export_metrics(str(export_file))

        # Verify export
        assert export_file.exists()
        data = json.loads(export_file.read_text())
        assert data['total_steps'] == 10
        assert data['successful_steps'] == 8


# === Test NotificationPlugin (RecoveryStrategy demonstration) ===

def test_notification_plugin_basic():
    """Test NotificationPlugin initializes correctly"""
    from luminous_nix.plugins.notification_plugin import NotificationPlugin
    from luminous_nix.core.plugin_registry import PluginRegistry

    plugin = NotificationPlugin()

    # Verify plugin properties
    assert plugin.name == "notification-plugin"
    assert plugin.version.startswith("1.")

    # Register and enable
    registry = PluginRegistry()
    registry.register(plugin)
    registry.enable_plugin("notification-plugin")

    # Verify recovery strategy was created
    assert plugin.recovery_strategy is not None


def test_notification_plugin_error_notifications():
    """Test NotificationPlugin sends notifications on errors"""
    from luminous_nix.plugins.notification_plugin import NotificationPlugin
    from luminous_nix.core.error_recovery import ClassifiedError, ErrorCategory, ErrorSeverity, RecoverabilityLevel

    plugin = NotificationPlugin(enable_desktop_notifications=False)  # Disable actual notifications
    plugin.on_enable()

    # Create a test error
    error = ClassifiedError(
        message="Test error occurred",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
        operation_id="test_op",
        timestamp=datetime.now(),
        context={"details": "test"}
    )

    # Trigger notification
    plugin.recovery_strategy.can_recover(error)

    # Verify notification was queued
    notifications = plugin.get_notifications()
    assert len(notifications) > 0
    assert "Test error occurred" in notifications[0]['message']


def test_notification_plugin_filtering():
    """Test NotificationPlugin can filter by severity"""
    from luminous_nix.plugins.notification_plugin import NotificationPlugin
    from luminous_nix.core.error_recovery import ClassifiedError, ErrorCategory, ErrorSeverity, RecoverabilityLevel

    plugin = NotificationPlugin(
        enable_desktop_notifications=False,
        min_severity=ErrorSeverity.FATAL  # Only notify on FATAL
    )
    plugin.on_enable()

    # Create HIGH severity error (should be filtered)
    high_error = ClassifiedError(
        message="High severity error",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
        operation_id="test_op",
        timestamp=datetime.now(),
        context={}
    )

    plugin.recovery_strategy.can_recover(high_error)

    # Should not create notification
    assert len(plugin.get_notifications()) == 0

    # Create FATAL error (should notify)
    fatal_error = ClassifiedError(
        message="Fatal error",
        category=ErrorCategory.CONFIGURATION,
        severity=ErrorSeverity.FATAL,
        recoverability=RecoverabilityLevel.NOT_RECOVERABLE,
        operation_id="test_op",
        timestamp=datetime.now(),
        context={}
    )

    plugin.recovery_strategy.can_recover(fatal_error)

    # Should create notification
    assert len(plugin.get_notifications()) == 1


# === Test CustomStepPlugin (Domain-specific steps) ===

def test_custom_step_plugin_basic():
    """Test CustomStepPlugin provides custom step types"""
    from luminous_nix.plugins.custom_step_plugin import CustomStepPlugin
    from luminous_nix.core.plugin_registry import PluginRegistry

    plugin = CustomStepPlugin()

    # Verify plugin properties
    assert plugin.name == "custom-step-plugin"
    assert plugin.version.startswith("1.")

    # Register and enable
    registry = PluginRegistry()
    registry.register(plugin)
    registry.enable_plugin("custom-step-plugin")

    # Verify custom handlers were registered
    assert plugin.http_handler is not None
    assert plugin.file_handler is not None


def test_custom_step_plugin_http_step():
    """Test CustomStepPlugin handles HTTP request steps"""
    from luminous_nix.plugins.custom_step_plugin import CustomStepPlugin
    from luminous_nix.core.execution_plan import ExecutionStep

    plugin = CustomStepPlugin()
    plugin.on_enable()

    # Create HTTP request step
    step = ExecutionStep(
        id="http_step",
        name="HTTP Request",
        handler=lambda p: None,  # Will be overridden
        parameters={
            "type": "http_request",
            "url": "https://httpbin.org/get",
            "method": "GET"
        },
        depends_on=set(),
        provides={'response'},
        requires=set()
    )

    # Execute
    result = plugin.http_handler.execute(step, {})

    # Verify result
    assert result is not None
    assert 'status_code' in result
    assert 'body' in result or 'error' in result


def test_custom_step_plugin_file_operation():
    """Test CustomStepPlugin handles file operation steps"""
    from luminous_nix.plugins.custom_step_plugin import CustomStepPlugin
    from luminous_nix.core.execution_plan import ExecutionStep

    plugin = CustomStepPlugin()
    plugin.on_enable()

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"

        # Create file write step
        step = ExecutionStep(
            id="file_step",
            name="File Write",
            handler=lambda p: None,
            parameters={
                "type": "file_operation",
                "operation": "write",
                "path": str(test_file),
                "content": "test content"
            },
            depends_on=set(),
            provides={'file_path'},
            requires=set()
        )

        # Execute
        result = plugin.file_handler.execute(step, {})

        # Verify file was created
        assert test_file.exists()
        assert test_file.read_text() == "test content"
        assert result['success'] is True


def test_custom_step_plugin_can_handle():
    """Test CustomStepPlugin correctly identifies step types"""
    from luminous_nix.plugins.custom_step_plugin import CustomStepPlugin

    plugin = CustomStepPlugin()
    plugin.on_enable()

    # HTTP handler
    assert plugin.http_handler.can_handle("http_request")
    assert plugin.http_handler.can_handle("http_get")
    assert plugin.http_handler.can_handle("http_post")
    assert not plugin.http_handler.can_handle("file_operation")

    # File handler
    assert plugin.file_handler.can_handle("file_operation")
    assert plugin.file_handler.can_handle("file_read")
    assert plugin.file_handler.can_handle("file_write")
    assert not plugin.file_handler.can_handle("http_request")


# === Test Plugin Integration ===

def test_multiple_plugins_together():
    """Test that multiple example plugins work together"""
    from luminous_nix.plugins.logging_plugin import LoggingPlugin
    from luminous_nix.plugins.metrics_plugin import MetricsPlugin
    from luminous_nix.core.plugin_registry import PluginRegistry
    from luminous_nix.core.execution_plan import ExecutionStep

    # Create registry with multiple plugins
    registry = PluginRegistry()

    logging_plugin = LoggingPlugin()
    metrics_plugin = MetricsPlugin()

    registry.register(logging_plugin)
    registry.register(metrics_plugin)

    registry.enable_plugin("logging-plugin")
    registry.enable_plugin("metrics-plugin")

    # Create test step
    step = ExecutionStep(
        id="combined_step",
        name="Combined Test",
        handler=lambda p: "success",
        parameters={},
        depends_on=set(),
        provides={'result'},
        requires=set()
    )

    # Execute through both plugins
    context = {}

    # Logging plugin records it
    logging_plugin.step_handler.execute(step, context)

    # Metrics plugin tracks it
    metrics_plugin.step_handler.execute(step, context)

    # Verify both plugins captured the execution
    assert len(logging_plugin.get_logs()) > 0
    assert metrics_plugin.get_metrics()['total_steps'] > 0


def test_plugin_cleanup_on_disable():
    """Test that plugins clean up resources on disable"""
    from luminous_nix.plugins.logging_plugin import LoggingPlugin
    from luminous_nix.plugins.metrics_plugin import MetricsPlugin
    from luminous_nix.core.plugin_registry import PluginRegistry

    registry = PluginRegistry()

    logging_plugin = LoggingPlugin()
    metrics_plugin = MetricsPlugin()

    registry.register(logging_plugin)
    registry.register(metrics_plugin)

    registry.enable_plugin("logging-plugin")
    registry.enable_plugin("metrics-plugin")

    # Verify plugins are active
    assert logging_plugin.step_handler is not None
    assert metrics_plugin.step_handler is not None

    # Disable plugins
    registry.disable_plugin("logging-plugin")
    registry.disable_plugin("metrics-plugin")

    # Plugins should still exist but be inactive
    # (Specific cleanup behavior depends on implementation)
    assert registry.get_plugin("logging-plugin") is not None
    assert not registry.is_enabled("logging-plugin")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
