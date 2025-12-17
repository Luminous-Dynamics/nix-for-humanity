"""
Sophia Phase 4: Multi-Agent Orchestration

This module implements collective intelligence through multiple
specialized Sophia agents coordinated by Meta-Sophia.
"""

from .agent_protocol import (
    AgentMessage,
    MessageType,
    AgentProfile,
    OrchestrationContext,
    ConsensusResponse,
    SubTask,
    AgentResponse,
)

from .meta_sophia import MetaSophia
from .task_router import TaskRouter
from .agent_registry import AgentRegistry
from .knowledge_broker import KnowledgeBroker, KnowledgeEntry, LearningEvent
from .emergence_monitor import EmergenceMonitor, Pattern, EmergentInsight, CollaborationEvent

__all__ = [
    # Protocol types
    "AgentMessage",
    "MessageType",
    "AgentProfile",
    "OrchestrationContext",
    "ConsensusResponse",
    "SubTask",
    "AgentResponse",

    # Core orchestration
    "MetaSophia",
    "TaskRouter",
    "AgentRegistry",

    # Knowledge & Emergence (Phase 4C)
    "KnowledgeBroker",
    "KnowledgeEntry",
    "LearningEvent",
    "EmergenceMonitor",
    "Pattern",
    "EmergentInsight",
    "CollaborationEvent",
]
