"""
NotificationPlugin - Error Notifications

Demonstrates RecoveryStrategy extension point for sending notifications
when errors occur during execution.

Features:
- Error notification on classified errors
- Severity-based filtering
- Desktop notification support (optional)
- Notification history tracking
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import subprocess

from luminous_nix.core.plugin_registry import Plugin
from luminous_nix.core.extension_points import RecoveryStrategy
from luminous_nix.core.error_recovery import ClassifiedError, ErrorSeverity


# Severity ordering from most to least severe
SEVERITY_ORDER = {
    ErrorSeverity.FATAL: 5,
    ErrorSeverity.CRITICAL: 4,
    ErrorSeverity.HIGH: 3,
    ErrorSeverity.MEDIUM: 2,
    ErrorSeverity.LOW: 1
}


class NotificationRecoveryStrategy(RecoveryStrategy):
    """
    RecoveryStrategy that sends notifications on errors.

    Does not actually recover but sends notifications to alert users.
    """

    def __init__(self, plugin: 'NotificationPlugin'):
        """
        Initialize notification recovery strategy.

        Args:
            plugin: Parent NotificationPlugin instance
        """
        self.plugin = plugin

    def can_recover(self, error: ClassifiedError) -> bool:
        """
        Check if notification should be sent for this error.

        Args:
            error: Classified error

        Returns:
            True if error meets notification criteria
        """
        # Check if error severity meets minimum threshold using severity ordering
        error_level = SEVERITY_ORDER.get(error.severity, 0)
        min_level = SEVERITY_ORDER.get(self.plugin.min_severity, 0)

        if error_level >= min_level:
            # Send notification only if severity is high enough
            self.plugin._send_notification(error)

        # This strategy doesn't actually recover
        return False

    def recover(self, error: ClassifiedError, context: Dict[str, Any]) -> bool:
        """
        Attempt recovery (notification only, no actual recovery).

        Args:
            error: Classified error
            context: Recovery context

        Returns:
            False (notification only, doesn't recover)
        """
        # Already sent notification in can_recover
        return False


class NotificationPlugin(Plugin):
    """
    Example plugin demonstrating error notifications.

    Sends notifications when errors occur during execution.

    Example:
        >>> plugin = NotificationPlugin(min_severity=ErrorSeverity.HIGH)
        >>> registry.register(plugin)
        >>> registry.enable_plugin("notification-plugin")
        >>> # Now errors will trigger notifications
    """

    def __init__(
        self,
        enable_desktop_notifications: bool = True,
        min_severity: ErrorSeverity = ErrorSeverity.HIGH
    ):
        """
        Initialize notification plugin.

        Args:
            enable_desktop_notifications: Whether to show desktop notifications
            min_severity: Minimum error severity to notify on
        """
        super().__init__()
        self.enable_desktop_notifications = enable_desktop_notifications
        self.min_severity = min_severity

        self.notifications: List[Dict[str, Any]] = []
        self.recovery_strategy: Optional[NotificationRecoveryStrategy] = None

    @property
    def name(self) -> str:
        """Plugin name"""
        return "notification-plugin"

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
        return "Sends notifications when errors occur"

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        pass

    def on_enable(self) -> None:
        """
        Called when plugin is enabled.

        Creates and registers the notification recovery strategy.
        """
        self.recovery_strategy = NotificationRecoveryStrategy(self)

    def on_disable(self) -> None:
        """
        Called when plugin is disabled.
        """
        self.recovery_strategy = None

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        pass

    def _send_notification(self, error: ClassifiedError) -> None:
        """
        Send notification for error.

        Args:
            error: Classified error
        """
        # Create notification record
        notification = {
            'timestamp': datetime.now().isoformat(),
            'message': error.message,
            'severity': error.severity.name,
            'category': error.category.name,
            'operation_id': error.operation_id
        }

        self.notifications.append(notification)

        # Send desktop notification if enabled
        if self.enable_desktop_notifications:
            self._send_desktop_notification(
                title=f"{error.severity.name}: {error.category.name}",
                message=error.message
            )

    def _send_desktop_notification(self, title: str, message: str) -> None:
        """
        Send desktop notification.

        Args:
            title: Notification title
            message: Notification message
        """
        try:
            # Use notify-send on Linux
            subprocess.run(
                ['notify-send', title, message],
                check=False,
                capture_output=True,
                timeout=5
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # notify-send not available or timed out
            pass

    def get_notifications(self) -> List[Dict[str, Any]]:
        """
        Get all notifications sent.

        Returns:
            List of notification records
        """
        return list(self.notifications)

    def clear_notifications(self) -> None:
        """Clear notification history"""
        self.notifications.clear()

    def get_summary(self) -> str:
        """
        Get human-readable summary of notifications.

        Returns:
            Formatted string with notification statistics
        """
        total = len(self.notifications)

        if total == 0:
            return "No notifications sent"

        # Count by severity
        by_severity = {}
        for notif in self.notifications:
            severity = notif['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1

        summary = f"Total Notifications: {total}\n"
        summary += "By Severity:\n"
        for severity, count in sorted(by_severity.items()):
            summary += f"  {severity}: {count}\n"

        return summary.strip()


if __name__ == "__main__":
    # Example usage
    print("NotificationPlugin Example")
    print("-" * 50)

    # Create plugin (disable desktop notifications for example)
    plugin = NotificationPlugin(
        enable_desktop_notifications=False,
        min_severity=ErrorSeverity.HIGH
    )

    # Simulate plugin lifecycle
    plugin.on_load()
    plugin.on_enable()

    # Simulate some errors
    from luminous_nix.core.error_recovery import ErrorCategory, RecoverabilityLevel

    error1 = ClassifiedError(
        message="Network connection failed",
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.HIGH,
        recoverability=RecoverabilityLevel.RETRY_RECOVERABLE,
        operation_id="op1",
        timestamp=datetime.now(),
        context={}
    )

    error2 = ClassifiedError(
        message="System failure",
        category=ErrorCategory.SYSTEM,
        severity=ErrorSeverity.FATAL,
        recoverability=RecoverabilityLevel.NOT_RECOVERABLE,
        operation_id="op2",
        timestamp=datetime.now(),
        context={}
    )

    # Trigger notifications
    plugin.recovery_strategy.can_recover(error1)
    plugin.recovery_strategy.can_recover(error2)

    # Get summary
    print("\n" + plugin.get_summary())

    # Disable plugin
    plugin.on_disable()
