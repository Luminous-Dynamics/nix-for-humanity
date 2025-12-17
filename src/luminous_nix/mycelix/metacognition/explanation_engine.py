"""
Explanation Engine - Full Reasoning Transparency

Revolutionary feature: The AI can explain WHY it made every decision.

This is not a post-hoc rationalization. This is genuine step-by-step
reasoning captured during the actual decision-making process.

Users can ask:
- "Why did you suggest that?"
- "How did you arrive at this answer?"
- "What were you thinking?"

And get REAL answers showing the actual reasoning process.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReasoningType(Enum):
    """Types of reasoning steps"""
    ANALYSIS = "analysis"  # Analyzed the query
    DECOMPOSITION = "decomposition"  # Broke down the task
    AGENT_SELECTION = "agent_selection"  # Chose specific agents
    KNOWLEDGE_LOOKUP = "knowledge_lookup"  # Consulted knowledge base
    INFERENCE = "inference"  # Drew a conclusion
    SYNTHESIS = "synthesis"  # Combined multiple perspectives
    VALIDATION = "validation"  # Checked the result
    UNCERTAINTY = "uncertainty"  # Acknowledged uncertainty


@dataclass
class ReasoningStep:
    """A single step in the reasoning process"""
    step_number: int
    reasoning_type: ReasoningType
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    alternatives_considered: List[str] = field(default_factory=list)
    why_chosen: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Explanation:
    """Complete explanation of a response"""
    query: str
    final_response: str
    reasoning_chain: List[ReasoningStep]
    key_decisions: List[str]
    uncertainties: List[str]
    alternatives_considered: Dict[str, str]  # alternative -> why_not_chosen
    confidence_breakdown: Dict[str, float]
    generated_at: datetime = field(default_factory=datetime.now)

    def to_natural_language(self, detail_level: str = "medium") -> str:
        """
        Convert explanation to natural language

        Args:
            detail_level: "brief", "medium", or "full"

        Returns:
            Human-readable explanation
        """
        lines = []

        # Header
        lines.append(f"# How I Answered: \"{self.query}\"")
        lines.append("")

        if detail_level == "brief":
            # Just key decisions
            lines.append("## Key Decisions:")
            for decision in self.key_decisions:
                lines.append(f"- {decision}")

            if self.uncertainties:
                lines.append("")
                lines.append("## Uncertainties:")
                for uncertainty in self.uncertainties:
                    lines.append(f"- {uncertainty}")

        elif detail_level in ["medium", "full"]:
            # Reasoning chain
            lines.append("## Reasoning Process:")
            lines.append("")

            for step in self.reasoning_chain:
                emoji = self._get_step_emoji(step.reasoning_type)
                lines.append(f"{step.step_number}. {emoji} **{step.reasoning_type.value.title()}**")
                lines.append(f"   {step.description}")

                if detail_level == "full" and step.alternatives_considered:
                    lines.append(f"   *Alternatives: {', '.join(step.alternatives_considered)}*")
                    if step.why_chosen:
                        lines.append(f"   *Chose this because: {step.why_chosen}*")

                lines.append("")

            # Key decisions
            if self.key_decisions:
                lines.append("## Key Decisions:")
                for decision in self.key_decisions:
                    lines.append(f"- {decision}")
                lines.append("")

            # Uncertainties
            if self.uncertainties:
                lines.append("## What I'm Uncertain About:")
                for uncertainty in self.uncertainties:
                    lines.append(f"- {uncertainty}")
                lines.append("")

            # Alternatives considered
            if self.alternatives_considered and detail_level == "full":
                lines.append("## Alternatives I Considered:")
                for alt, why_not in self.alternatives_considered.items():
                    lines.append(f"- **{alt}**: {why_not}")
                lines.append("")

            # Confidence breakdown
            if self.confidence_breakdown:
                lines.append("## Confidence Breakdown:")
                for aspect, conf in self.confidence_breakdown.items():
                    bar = "█" * int(conf * 10) + "░" * (10 - int(conf * 10))
                    lines.append(f"- {aspect}: {bar} {conf:.0%}")

        return "\n".join(lines)

    def _get_step_emoji(self, reasoning_type: ReasoningType) -> str:
        """Get emoji for reasoning type"""
        emoji_map = {
            ReasoningType.ANALYSIS: "🔍",
            ReasoningType.DECOMPOSITION: "📊",
            ReasoningType.AGENT_SELECTION: "🤝",
            ReasoningType.KNOWLEDGE_LOOKUP: "📚",
            ReasoningType.INFERENCE: "💡",
            ReasoningType.SYNTHESIS: "🔄",
            ReasoningType.VALIDATION: "✅",
            ReasoningType.UNCERTAINTY: "❓",
        }
        return emoji_map.get(reasoning_type, "•")


class ExplanationEngine:
    """
    Generates explanations of AI reasoning

    Philosophy:
    - Transparency builds trust
    - Users deserve to understand AI decisions
    - Explanation is a first-class feature, not an afterthought
    """

    def __init__(self):
        """Initialize explanation engine"""
        # Track explanations for learning
        self.explanation_history: List[Explanation] = []

        # Track which explanations users found helpful
        self.helpful_count = 0
        self.total_explanations = 0

    def start_explanation(self, query: str) -> "ExplanationBuilder":
        """
        Start building an explanation

        Returns:
            ExplanationBuilder for recording reasoning steps
        """
        return ExplanationBuilder(query, self)

    def get_recent_explanations(self, n: int = 10) -> List[Explanation]:
        """Get recent explanations"""
        return self.explanation_history[-n:]

    def record_feedback(self, was_helpful: bool):
        """Record whether explanation was helpful"""
        self.total_explanations += 1
        if was_helpful:
            self.helpful_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get explanation statistics"""
        return {
            "total_explanations": self.total_explanations,
            "helpful_explanations": self.helpful_count,
            "helpfulness_rate": (
                self.helpful_count / self.total_explanations
                if self.total_explanations > 0
                else 0.0
            ),
            "recent_explanations": len(self.explanation_history),
        }


class ExplanationBuilder:
    """
    Builder for constructing explanations step-by-step

    Usage:
        builder = engine.start_explanation("install firefox")
        builder.add_step(ReasoningType.ANALYSIS, "Identified 'install' intent", ...)
        builder.add_step(ReasoningType.AGENT_SELECTION, "Selected SophiaNixOS", ...)
        explanation = builder.build()
    """

    def __init__(self, query: str, engine: ExplanationEngine):
        """Initialize explanation builder"""
        self.query = query
        self.engine = engine
        self.steps: List[ReasoningStep] = []
        self.key_decisions: List[str] = []
        self.uncertainties: List[str] = []
        self.alternatives: Dict[str, str] = {}
        self.confidence_breakdown: Dict[str, float] = {}
        self.final_response: Optional[str] = None

    def add_step(
        self,
        reasoning_type: ReasoningType,
        description: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        alternatives: Optional[List[str]] = None,
        why_chosen: Optional[str] = None,
    ) -> "ExplanationBuilder":
        """
        Add a reasoning step

        Args:
            reasoning_type: Type of reasoning
            description: Human-readable description
            input_data: What went into this step
            output_data: What came out of this step
            confidence: How confident in this step (0-1)
            alternatives: Alternative approaches considered
            why_chosen: Why this approach was chosen

        Returns:
            Self for chaining
        """
        step = ReasoningStep(
            step_number=len(self.steps) + 1,
            reasoning_type=reasoning_type,
            description=description,
            input_data=input_data or {},
            output_data=output_data or {},
            confidence=confidence,
            alternatives_considered=alternatives or [],
            why_chosen=why_chosen,
        )

        self.steps.append(step)
        return self

    def add_key_decision(self, decision: str) -> "ExplanationBuilder":
        """Add a key decision point"""
        self.key_decisions.append(decision)
        return self

    def add_uncertainty(self, uncertainty: str) -> "ExplanationBuilder":
        """Add an uncertainty acknowledgment"""
        self.uncertainties.append(uncertainty)
        return self

    def add_alternative(
        self,
        alternative: str,
        why_not_chosen: str
    ) -> "ExplanationBuilder":
        """Add an alternative that was considered but not chosen"""
        self.alternatives[alternative] = why_not_chosen
        return self

    def set_confidence_breakdown(
        self,
        breakdown: Dict[str, float]
    ) -> "ExplanationBuilder":
        """Set confidence breakdown by aspect"""
        self.confidence_breakdown = breakdown
        return self

    def set_final_response(self, response: str) -> "ExplanationBuilder":
        """Set the final response"""
        self.final_response = response
        return self

    def build(self) -> Explanation:
        """
        Build the complete explanation

        Returns:
            Complete Explanation object
        """
        explanation = Explanation(
            query=self.query,
            final_response=self.final_response or "",
            reasoning_chain=self.steps,
            key_decisions=self.key_decisions,
            uncertainties=self.uncertainties,
            alternatives_considered=self.alternatives,
            confidence_breakdown=self.confidence_breakdown,
        )

        # Store in engine history
        self.engine.explanation_history.append(explanation)

        # Limit history size
        if len(self.engine.explanation_history) > 100:
            self.engine.explanation_history = self.engine.explanation_history[-100:]

        return explanation


# Utility functions for common explanation patterns

def explain_agent_selection(
    selected_agents: List[str],
    all_agents: List[str],
    selection_criteria: str
) -> ReasoningStep:
    """Create explanation for agent selection"""
    return ReasoningStep(
        step_number=0,  # Will be renumbered
        reasoning_type=ReasoningType.AGENT_SELECTION,
        description=f"Selected {len(selected_agents)} agent(s) for this query",
        input_data={
            "available_agents": all_agents,
            "criteria": selection_criteria,
        },
        output_data={
            "selected": selected_agents,
        },
        confidence=1.0,
        alternatives_considered=[
            agent for agent in all_agents if agent not in selected_agents
        ],
        why_chosen=selection_criteria,
    )


def explain_consensus(
    agent_responses: List[Dict[str, Any]],
    final_confidence: float,
    agreement_level: float
) -> ReasoningStep:
    """Create explanation for consensus building"""
    agent_confidences = [r.get("confidence", 0.5) for r in agent_responses]

    return ReasoningStep(
        step_number=0,
        reasoning_type=ReasoningType.SYNTHESIS,
        description=f"Synthesized {len(agent_responses)} agent responses",
        input_data={
            "num_agents": len(agent_responses),
            "agent_confidences": agent_confidences,
        },
        output_data={
            "final_confidence": final_confidence,
            "agreement_level": agreement_level,
        },
        confidence=final_confidence,
    )
