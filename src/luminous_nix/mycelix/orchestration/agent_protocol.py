"""
Agent Communication Protocol

Defines standardized message formats and data structures for
inter-agent communication in the Sophia orchestration network.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid


class MessageType(Enum):
    """Types of messages agents can exchange"""

    QUERY = "query"  # Asking another agent
    RESPONSE = "response"  # Responding to query
    INSIGHT = "insight"  # Sharing learned knowledge
    ALERT = "alert"  # Urgent information
    VOTE = "vote"  # Consensus building
    HEARTBEAT = "heartbeat"  # Agent status check


@dataclass
class AgentMessage:
    """Standard message format for agent communication"""

    sender: str  # Agent ID
    recipient: str  # Agent ID or "broadcast"
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    confidence: float = 1.0  # Sender's confidence in content

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary"""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Deserialize message from dictionary"""
        return cls(
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            timestamp=data["timestamp"],
            correlation_id=data["correlation_id"],
            confidence=data.get("confidence", 1.0),
        )


@dataclass
class AgentProfile:
    """Profile defining a Sophia agent's specialization"""

    agent_id: str
    name: str
    specialization: str
    expertise_domains: List[str]
    capabilities: List[str]

    # Performance metrics
    success_rate: float = 0.0
    average_confidence: float = 0.0
    response_time_avg: float = 0.0

    # Load balancing
    current_load: int = 0
    max_concurrent_tasks: int = 10

    # Learning
    total_queries_processed: int = 0
    positive_feedback_count: int = 0
    negative_feedback_count: int = 0

    def update_metrics(self, success: bool, confidence: float, response_time: float):
        """Update agent performance metrics"""
        self.total_queries_processed += 1

        # Update success rate (exponential moving average)
        alpha = 0.1
        self.success_rate = (
            alpha * (1.0 if success else 0.0) + (1 - alpha) * self.success_rate
        )

        # Update average confidence
        self.average_confidence = (
            alpha * confidence + (1 - alpha) * self.average_confidence
        )

        # Update average response time
        self.response_time_avg = (
            alpha * response_time + (1 - alpha) * self.response_time_avg
        )


@dataclass
class SubTask:
    """Decomposed sub-task for agent processing"""

    task_id: str
    query: str
    context: Dict[str, Any]
    priority: int = 5  # 1-10, higher = more urgent
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    assigned_agent: Optional[str] = None
    created_at: float = field(default_factory=time.time)


@dataclass
class AgentResponse:
    """Response from a Sophia agent"""

    agent_id: str
    task_id: str
    content: str
    insights: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)

    # Metadata
    confidence: float = 1.0
    processing_time: float = 0.0
    timestamp: float = field(default_factory=time.time)

    # Context
    reasoning: Optional[str] = None
    alternatives_considered: List[str] = field(default_factory=list)


@dataclass
class ConsensusResponse:
    """Synthesized response from multiple agents"""

    content: str
    insights: List[str]
    suggestions: List[str]
    actions: List[str]

    # Consensus metadata
    contributing_agents: List[str]
    confidence: float
    agreement_level: float  # 0.0-1.0

    # Conflicts resolved
    disagreements: List[str] = field(default_factory=list)
    resolution_method: str = "bayesian_merge"

    # Emergent insights
    novel_insights: List[str] = field(default_factory=list)
    emergent_patterns: List[str] = field(default_factory=list)

    # Timing
    total_processing_time: float = 0.0
    consensus_building_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize consensus response"""
        return {
            "content": self.content,
            "insights": self.insights,
            "suggestions": self.suggestions,
            "actions": self.actions,
            "contributing_agents": self.contributing_agents,
            "confidence": self.confidence,
            "agreement_level": self.agreement_level,
            "disagreements": self.disagreements,
            "resolution_method": self.resolution_method,
            "novel_insights": self.novel_insights,
            "emergent_patterns": self.emergent_patterns,
            "total_processing_time": self.total_processing_time,
            "consensus_building_time": self.consensus_building_time,
        }


@dataclass
class OrchestrationContext:
    """Context for orchestrated task execution"""

    query: str
    user_id: str
    session_id: str

    # Task decomposition
    sub_tasks: List[SubTask] = field(default_factory=list)
    assigned_agents: Dict[str, str] = field(
        default_factory=dict
    )  # task_id -> agent_id

    # Execution tracking
    start_time: float = field(default_factory=time.time)
    agent_responses: List[AgentResponse] = field(default_factory=list)
    consensus: Optional[ConsensusResponse] = None

    # Meta information
    complexity_score: float = 0.0
    requires_consensus: bool = False
    confidence_threshold: float = 0.85

    def add_response(self, response: AgentResponse):
        """Add agent response to context"""
        self.agent_responses.append(response)

    def all_tasks_completed(self) -> bool:
        """Check if all sub-tasks have responses"""
        return len(self.agent_responses) == len(self.sub_tasks)

    def get_elapsed_time(self) -> float:
        """Get elapsed time since orchestration started"""
        return time.time() - self.start_time


# Utility functions


def create_query_message(
    sender: str, recipient: str, query: str, context: Dict[str, Any]
) -> AgentMessage:
    """Create a standard query message"""
    return AgentMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.QUERY,
        content={"query": query, "context": context},
    )


def create_response_message(
    sender: str,
    recipient: str,
    response: AgentResponse,
    correlation_id: str,
) -> AgentMessage:
    """Create a standard response message"""
    return AgentMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.RESPONSE,
        content={
            "response": {
                "content": response.content,
                "insights": response.insights,
                "suggestions": response.suggestions,
                "actions": response.actions,
                "confidence": response.confidence,
                "reasoning": response.reasoning,
            }
        },
        correlation_id=correlation_id,
        confidence=response.confidence,
    )


def create_insight_message(
    sender: str, insight: str, context: Dict[str, Any]
) -> AgentMessage:
    """Create a broadcast insight message"""
    return AgentMessage(
        sender=sender,
        recipient="broadcast",
        message_type=MessageType.INSIGHT,
        content={"insight": insight, "context": context},
    )
