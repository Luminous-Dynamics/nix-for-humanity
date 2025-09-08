"""AI interface for testing and companion functionality.

This module provides interfaces for AI agents to interact with and test the system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TestStatus(Enum):
    """Status of a test result."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of an AI-driven test."""

    name: str
    status: TestStatus
    message: str | None = None
    details: dict[str, Any] | None = None


class AICompanionInterface:
    """Interface for AI companions to interact with the system."""

    def __init__(self):
        self.connected = False
        self.test_results: list[TestResult] = []

    def connect(self) -> bool:
        """Connect to the system."""
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from the system."""
        self.connected = False

    def execute_command(self, command: str) -> dict[str, Any]:
        """Execute a command through the AI interface."""
        if not self.connected:
            return {"success": False, "error": "Not connected"}

        # Stub implementation
        return {"success": True, "output": f"Executed: {command}", "data": {}}

    def run_test(self, test_name: str, test_func: callable) -> TestResult:
        """Run a test and return the result."""
        try:
            test_func()
            result = TestResult(
                name=test_name,
                status=TestStatus.PASSED,
                message="Test passed successfully",
            )
        except AssertionError as e:
            result = TestResult(
                name=test_name, status=TestStatus.FAILED, message=str(e)
            )
        except Exception as e:
            result = TestResult(name=test_name, status=TestStatus.ERROR, message=str(e))

        self.test_results.append(result)
        return result

    def get_test_results(self) -> list[TestResult]:
        """Get all test results."""
        return self.test_results

    def clear_test_results(self) -> None:
        """Clear test results."""
        self.test_results = []

    def get_system_state(self) -> dict[str, Any]:
        """Get current system state."""
        return {
            "connected": self.connected,
            "test_count": len(self.test_results),
            "status": "ready" if self.connected else "disconnected",
        }


# Export for compatibility
__all__ = ["TestStatus", "TestResult", "AICompanionInterface"]
