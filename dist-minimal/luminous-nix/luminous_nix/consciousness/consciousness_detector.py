"""Consciousness detector for awareness metrics.

Detects and measures consciousness-related metrics.
"""

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ConsciousnessMetrics:
    """Metrics for consciousness state."""

    awareness_level: float = 0.5
    coherence: float = 0.5
    presence: float = 0.5
    flow_state: float = 0.0


class ConsciousnessBarometer:
    """Measures consciousness state."""

    def __init__(self):
        self.metrics = ConsciousnessMetrics()
        self.last_update = time.time()

    def measure(self) -> ConsciousnessMetrics:
        """Get current consciousness metrics."""
        return self.metrics

    def update(self, signals: dict[str, Any]) -> None:
        """Update metrics based on signals."""
        self.last_update = time.time()

        # Simple heuristics for demo
        if "focus" in signals:
            self.metrics.coherence = signals["focus"]
        if "activity" in signals:
            self.metrics.awareness_level = signals["activity"]

    def get_state(self) -> str:
        """Get descriptive state."""
        avg = (
            self.metrics.awareness_level
            + self.metrics.coherence
            + self.metrics.presence
        ) / 3

        if avg > 0.7:
            return "highly_conscious"
        if avg > 0.4:
            return "aware"
        return "distracted"

    def is_in_flow(self) -> bool:
        """Check if in flow state."""
        return self.metrics.flow_state > 0.6


# Export for compatibility
__all__ = ["ConsciousnessMetrics", "ConsciousnessBarometer"]
