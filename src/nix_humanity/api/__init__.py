"""
from typing import List, Dict
Request/Response schema for the unified backend

These types are re-exported from the core types module for backward compatibility.
All new code should import from nix_humanity.core.types directly.
"""

# Define types locally for now (until we find the actual location)
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class IntentType(Enum):
    """Intent types (simplified for now)"""
    INSTALL_PACKAGE = "install_package"
    UPDATE_SYSTEM = "update_system"
    SEARCH_PACKAGE = "search_package"
    HELP = "help"
    UNKNOWN = "unknown"

@dataclass
class Context:
    """Context for request processing"""
    personality: str = "friendly"
    execute: bool = False
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_preferences is None:
            self.user_preferences = {}

@dataclass
class Request:
    """Incoming request from user"""
    query: str
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class Intent:
    """Recognized intent from user query"""
    type: IntentType
    entities: Dict[str, Any]
    confidence: float
    raw_text: str

@dataclass
class ExecutionResult:
    """Result of command execution"""
    success: bool
    output: str = ""
    error: str = ""
    command: str = ""

@dataclass
class Command:
    """Command to be executed"""
    command: str
    description: str = ""
    explanation: str = ""
    preview: bool = True

@dataclass
class Response:
    """Response to user request"""
    success: bool
    text: str
    commands: List[Dict[str, Any]] = None
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.commands is None:
            self.commands = []
        if self.data is None:
            self.data = {}

@dataclass
class Package:
    """Package information"""
    name: str
    version: str = ""
    description: str = ""

@dataclass
class FeedbackItem:
    """User feedback item"""
    query: str
    response: str
    helpful: bool
    timestamp: str = ""

@dataclass
class Plan:
    """Execution plan"""
    steps: List[str]
    explanation: str = ""

# Legacy alias for backward compatibility
Result = ExecutionResult

__all__ = [
    "Request",
    "Response",
    "Context",
    "Intent",
    "IntentType",
    "ExecutionResult",
    "Result",  # Legacy alias
    "Plan",
    "Command",
    "Package",
    "FeedbackItem"
]