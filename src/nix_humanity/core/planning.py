"""Planning and execution management for nix_humanity.

Provides plan creation and execution result tracking with consciousness awareness.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ExecutionResult:
    """Result of executing a plan or command."""
    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    consciousness_preserved: bool = True
    
    @property
    def is_success(self) -> bool:
        """Alias for success for compatibility."""
        return self.success


@dataclass
class Step:
    """A single step in an execution plan."""
    command: str
    description: str
    dry_run: bool = True
    critical: bool = False
    result: Optional[ExecutionResult] = None


@dataclass
class Plan:
    """Execution plan with consciousness-first principles."""
    goal: str
    steps: List[Step] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    consciousness_level: float = 0.5
    
    def add_step(self, command: str, description: str, critical: bool = False) -> None:
        """Add a step to the plan."""
        self.steps.append(Step(
            command=command,
            description=description,
            critical=critical
        ))
    
    @property
    def is_complete(self) -> bool:
        """Check if all steps have been executed."""
        return all(step.result is not None for step in self.steps)
    
    @property
    def is_successful(self) -> bool:
        """Check if all critical steps succeeded."""
        for step in self.steps:
            if step.critical and step.result:
                if not step.result.success:
                    return False
        return True