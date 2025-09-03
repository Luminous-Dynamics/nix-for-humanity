"""Signal collector for consciousness detection.

Collects and processes signals for consciousness-aware features.
"""

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class Signal:
    """Represents a collected signal."""

    timestamp: float
    type: str
    value: Any
    source: str


class RealTimeSignalCollector:
    """Collects signals in real-time."""

    def __init__(self):
        self.signals: list[Signal] = []
        self.active = False

    def start(self) -> None:
        """Start signal collection."""
        self.active = True

    def stop(self) -> None:
        """Stop signal collection."""
        self.active = False

    def collect(self, signal_type: str, value: Any, source: str = "unknown") -> None:
        """Collect a signal."""
        if self.active:
            signal = Signal(
                timestamp=time.time(), type=signal_type, value=value, source=source
            )
            self.signals.append(signal)

    def get_recent(self, count: int = 10) -> list[Signal]:
        """Get recent signals."""
        return self.signals[-count:] if self.signals else []


class IntegrationBridge:
    """Bridge for integrating with other systems."""

    def __init__(self):
        self.connected = False

    def connect(self) -> bool:
        """Connect to integration target."""
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from integration target."""
        self.connected = False

    def send(self, data: dict[str, Any]) -> bool:
        """Send data through bridge."""
        return self.connected


# Export for compatibility
__all__ = ["Signal", "RealTimeSignalCollector", "IntegrationBridge"]
