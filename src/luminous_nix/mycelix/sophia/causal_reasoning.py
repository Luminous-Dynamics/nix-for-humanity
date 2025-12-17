"""
Causal Reasoning Engine - Revolutionary Causality Understanding

Makes Sophia understand WHY things happen, not just WHAT happens:
- Root cause analysis for errors
- Counterfactual thinking ("what if we had...")
- Causal chain detection
- Intervention recommendations
- Dependency graph understanding

This is paradigm-shifting because most AI just correlates - Sophia understands causality.

Example:
"Our build failed" → Why? → "Missing dependency"
→ Why? → "Package not installed"
→ Why? → "We forgot to add it to requirements"
→ Root cause: Missing package specification
→ Intervention: Add package to requirements.txt
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Tuple, Set
import re

from ..context import Context, CommandActivity, FileActivity


class CauseType(Enum):
    """Type of cause"""
    ROOT_CAUSE = "root_cause"              # Fundamental underlying cause
    IMMEDIATE_CAUSE = "immediate_cause"    # Direct trigger
    CONTRIBUTING_FACTOR = "contributing"   # Contributing factor
    CORRELATION = "correlation"            # Correlated but not causal


class InterventionType(Enum):
    """Type of intervention"""
    PREVENTIVE = "preventive"      # Prevent the issue
    CORRECTIVE = "corrective"      # Fix the current issue
    MITIGATING = "mitigating"      # Reduce impact
    MONITORING = "monitoring"      # Watch for recurrence


@dataclass
class CausalLink:
    """A causal link in the chain"""
    cause: str
    effect: str
    cause_type: CauseType
    confidence: float  # 0.0-1.0
    evidence: List[str]

    # Temporal relationship
    time_lag: Optional[timedelta] = None  # How long between cause and effect


@dataclass
class CausalChain:
    """A complete causal chain from root cause to effect"""
    root_cause: str
    final_effect: str
    links: List[CausalLink]
    confidence: float  # Overall chain confidence

    def __str__(self) -> str:
        """String representation showing the chain"""
        parts = [self.root_cause]
        for link in self.links:
            parts.append(f" → {link.effect}")
        return "".join(parts)


@dataclass
class Counterfactual:
    """A counterfactual 'what if' scenario"""
    scenario: str  # "What if we had tested first?"
    likely_outcome: str  # "The bug would have been caught"
    confidence: float
    evidence: List[str]

    # Comparison with actual outcome
    actual_outcome: str
    improvement: bool  # Would this have been better?


@dataclass
class Intervention:
    """A recommended intervention"""
    intervention_type: InterventionType
    action: str  # What to do
    target_cause: str  # What cause this addresses
    expected_impact: str  # What we expect to happen
    confidence: float

    # Implementation details
    complexity: str  # "simple", "moderate", "complex"
    time_estimate: str  # "5 minutes", "1 hour", etc.


@dataclass
class CausalAnalysis:
    """Complete causal analysis of a situation"""
    situation: str  # What happened
    timestamp: datetime

    # Causal understanding
    causal_chains: List[CausalChain]
    contributing_factors: List[str]

    # Reasoning
    counterfactuals: List[Counterfactual]
    interventions: List[Intervention]

    # Meta
    confidence: float
    analysis_notes: List[str]


class CausalReasoningEngine:
    """
    Revolutionary Causal Reasoning Engine

    Enables Sophia to understand WHY things happen through:
    - Root cause analysis
    - Causal chain detection
    - Counterfactual thinking
    - Intervention recommendations

    This transforms Sophia from correlational to causal understanding.
    """

    def __init__(self):
        # History of causal analyses
        self.analysis_history: List[CausalAnalysis] = []

        # Learned causal patterns
        self.learned_causal_patterns: Dict[str, List[CausalChain]] = {}

        # Known dependency relationships
        self.dependency_graph: Dict[str, Set[str]] = {}

    def analyze_error(
        self,
        error: str,
        context: Optional[Context] = None,
        recent_commands: Optional[List[CommandActivity]] = None
    ) -> CausalAnalysis:
        """
        Analyze an error to understand its root cause

        Args:
            error: The error message or description
            context: Current session context
            recent_commands: Recent command history

        Returns:
            CausalAnalysis with root causes and interventions
        """
        now = datetime.now()

        # Get recent commands if not provided
        if recent_commands is None and context:
            recent_commands = context.recent_commands[-10:] if context.recent_commands else []

        # Build causal chains
        causal_chains = self._build_causal_chains(error, recent_commands, context)

        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(error, recent_commands, context)

        # Generate counterfactuals
        counterfactuals = self._generate_counterfactuals(error, recent_commands, causal_chains)

        # Recommend interventions
        interventions = self._recommend_interventions(causal_chains, contributing_factors)

        # Calculate overall confidence
        confidence = (
            sum(chain.confidence for chain in causal_chains) / len(causal_chains)
            if causal_chains else 0.5
        )

        # Analysis notes
        notes = []
        if len(causal_chains) > 1:
            notes.append("Multiple causal pathways detected - issue has several root causes")
        if confidence < 0.6:
            notes.append("Low confidence - may need more context to identify root cause")

        analysis = CausalAnalysis(
            situation=error,
            timestamp=now,
            causal_chains=causal_chains,
            contributing_factors=contributing_factors,
            counterfactuals=counterfactuals,
            interventions=interventions,
            confidence=confidence,
            analysis_notes=notes
        )

        self.analysis_history.append(analysis)

        # Learn from this analysis
        self._learn_causal_pattern(error, causal_chains)

        return analysis

    def _build_causal_chains(
        self,
        error: str,
        recent_commands: Optional[List[CommandActivity]],
        context: Optional[Context]
    ) -> List[CausalChain]:
        """Build causal chains from root causes to the error"""
        chains = []

        # Pattern 1: Missing dependency
        if any(word in error.lower() for word in ['not found', 'no module', 'cannot find', 'missing']):
            chain = self._analyze_missing_dependency_error(error, recent_commands)
            if chain:
                chains.append(chain)

        # Pattern 2: Build failure
        if any(word in error.lower() for word in ['failed', 'error', 'compilation']):
            chain = self._analyze_build_failure(error, recent_commands, context)
            if chain:
                chains.append(chain)

        # Pattern 3: Permission error
        if 'permission' in error.lower() or 'denied' in error.lower():
            chain = self._analyze_permission_error(error, recent_commands)
            if chain:
                chains.append(chain)

        # Pattern 4: Configuration error
        if any(word in error.lower() for word in ['config', 'configuration', 'invalid']):
            chain = self._analyze_config_error(error, context)
            if chain:
                chains.append(chain)

        # If no specific patterns matched, create generic chain
        if not chains:
            chains.append(self._create_generic_chain(error))

        return chains

    def _analyze_missing_dependency_error(
        self,
        error: str,
        recent_commands: Optional[List[CommandActivity]]
    ) -> Optional[CausalChain]:
        """Analyze missing dependency errors"""

        # Try to extract what's missing
        missing_item = self._extract_missing_item(error)
        if not missing_item:
            missing_item = "dependency"

        # Build causal chain
        links = [
            CausalLink(
                cause=f"{missing_item} not in environment",
                effect=f"System cannot find {missing_item}",
                cause_type=CauseType.IMMEDIATE_CAUSE,
                confidence=0.9,
                evidence=[error]
            ),
            CausalLink(
                cause=f"{missing_item} not installed",
                effect=f"{missing_item} not in environment",
                cause_type=CauseType.ROOT_CAUSE,
                confidence=0.85,
                evidence=["Dependency not in installed packages"]
            )
        ]

        # Check if they tried to use it without installing
        if recent_commands:
            install_attempted = any(
                'install' in cmd.command.lower() and missing_item.lower() in cmd.command.lower()
                for cmd in recent_commands
            )
            if not install_attempted:
                links.insert(0, CausalLink(
                    cause="Forgot to install dependency",
                    effect=f"{missing_item} not installed",
                    cause_type=CauseType.ROOT_CAUSE,
                    confidence=0.8,
                    evidence=["No install command found in recent history"]
                ))

        return CausalChain(
            root_cause=links[0].cause,
            final_effect=error,
            links=links,
            confidence=0.85
        )

    def _analyze_build_failure(
        self,
        error: str,
        recent_commands: Optional[List[CommandActivity]],
        context: Optional[Context]
    ) -> Optional[CausalChain]:
        """Analyze build failure errors"""

        links = []

        # Check for syntax errors
        if 'syntax' in error.lower():
            links.append(CausalLink(
                cause="Syntax error in code",
                effect="Build fails",
                cause_type=CauseType.IMMEDIATE_CAUSE,
                confidence=0.95,
                evidence=[error]
            ))

        # Check if they built without testing
        if recent_commands:
            last_test = None
            last_edit_time = None

            for cmd in reversed(recent_commands):
                if 'test' in cmd.command.lower() and not last_test:
                    last_test = cmd.timestamp
                if 'build' in cmd.command.lower():
                    break

            if context and context.active_files:
                last_edit_time = max(f.last_modified for f in context.active_files)

            if last_edit_time and (not last_test or last_edit_time > last_test):
                links.append(CausalLink(
                    cause="Built without testing after changes",
                    effect="Build failure not caught early",
                    cause_type=CauseType.CONTRIBUTING_FACTOR,
                    confidence=0.7,
                    evidence=["No test command between edit and build"]
                ))

        # Generic build failure link
        if not links:
            links.append(CausalLink(
                cause="Code has errors",
                effect="Build fails",
                cause_type=CauseType.IMMEDIATE_CAUSE,
                confidence=0.8,
                evidence=[error]
            ))

        return CausalChain(
            root_cause=links[0].cause,
            final_effect=error,
            links=links,
            confidence=0.75
        ) if links else None

    def _analyze_permission_error(
        self,
        error: str,
        recent_commands: Optional[List[CommandActivity]]
    ) -> Optional[CausalChain]:
        """Analyze permission errors"""

        links = [
            CausalLink(
                cause="Insufficient permissions",
                effect="Permission denied",
                cause_type=CauseType.IMMEDIATE_CAUSE,
                confidence=0.95,
                evidence=[error]
            )
        ]

        # Check if they ran without sudo
        if recent_commands:
            last_cmd = recent_commands[-1].command if recent_commands else ""
            if 'sudo' not in last_cmd.lower():
                links.insert(0, CausalLink(
                    cause="Command run without sudo",
                    effect="Insufficient permissions",
                    cause_type=CauseType.ROOT_CAUSE,
                    confidence=0.85,
                    evidence=["Command doesn't include 'sudo'"]
                ))

        return CausalChain(
            root_cause=links[0].cause,
            final_effect=error,
            links=links,
            confidence=0.9
        )

    def _analyze_config_error(
        self,
        error: str,
        context: Optional[Context]
    ) -> Optional[CausalChain]:
        """Analyze configuration errors"""

        links = [
            CausalLink(
                cause="Invalid configuration",
                effect="Configuration error",
                cause_type=CauseType.IMMEDIATE_CAUSE,
                confidence=0.85,
                evidence=[error]
            ),
            CausalLink(
                cause="Configuration not validated before use",
                effect="Invalid configuration",
                cause_type=CauseType.ROOT_CAUSE,
                confidence=0.7,
                evidence=["Error at runtime, not at config time"]
            )
        ]

        return CausalChain(
            root_cause=links[0].cause,
            final_effect=error,
            links=links,
            confidence=0.75
        )

    def _create_generic_chain(self, error: str) -> CausalChain:
        """Create a generic causal chain when no specific pattern matches"""
        link = CausalLink(
            cause="Unknown root cause",
            effect=error,
            cause_type=CauseType.IMMEDIATE_CAUSE,
            confidence=0.5,
            evidence=[error]
        )

        return CausalChain(
            root_cause="Unknown root cause",
            final_effect=error,
            links=[link],
            confidence=0.5
        )

    def _extract_missing_item(self, error: str) -> Optional[str]:
        """Extract what item is missing from error message"""
        # Try to find quoted items
        matches = re.findall(r"['\"]([^'\"]+)['\"]", error)
        if matches:
            return matches[0]

        # Try to find items after "module" or "package"
        for keyword in ['module', 'package', 'library', 'dependency']:
            pattern = f"{keyword}\\s+([\\w\\-\\.]+)"
            matches = re.findall(pattern, error, re.IGNORECASE)
            if matches:
                return matches[0]

        return None

    def _identify_contributing_factors(
        self,
        error: str,
        recent_commands: Optional[List[CommandActivity]],
        context: Optional[Context]
    ) -> List[str]:
        """Identify contributing factors to the error"""
        factors = []

        # Check for error patterns
        if recent_commands:
            failed_commands = [cmd for cmd in recent_commands if not cmd.success]
            if len(failed_commands) > 2:
                factors.append("Multiple recent failures indicate systemic issue")

        # Check for time factors
        if context:
            from ..context import get_context_engine
            ctx_engine = get_context_engine()
            current_context = ctx_engine.get_current_context()

            if current_context.session_start:
                session_duration = (datetime.now() - current_context.session_start).total_seconds() / 60
                if session_duration > 120:
                    factors.append("Long session (120+ min) may contribute to errors")

        return factors

    def _generate_counterfactuals(
        self,
        error: str,
        recent_commands: Optional[List[CommandActivity]],
        causal_chains: List[CausalChain]
    ) -> List[Counterfactual]:
        """Generate counterfactual 'what if' scenarios"""
        counterfactuals = []

        # Counterfactual: What if we had tested first?
        if recent_commands:
            has_test = any('test' in cmd.command.lower() for cmd in recent_commands[-3:])
            if not has_test:
                counterfactuals.append(Counterfactual(
                    scenario="What if we had tested before building?",
                    likely_outcome="The error would have been caught earlier with clearer context",
                    confidence=0.75,
                    evidence=["Testing provides earlier, clearer error messages"],
                    actual_outcome=error,
                    improvement=True
                ))

        # Counterfactual: What if we had checked dependencies?
        if any('not found' in error.lower() or 'missing' in error.lower() for _ in [1]):
            counterfactuals.append(Counterfactual(
                scenario="What if we had verified dependencies first?",
                likely_outcome="We would have installed the missing dependency proactively",
                confidence=0.8,
                evidence=["Dependency errors are preventable with pre-checks"],
                actual_outcome=error,
                improvement=True
            ))

        return counterfactuals

    def _recommend_interventions(
        self,
        causal_chains: List[CausalChain],
        contributing_factors: List[str]
    ) -> List[Intervention]:
        """Recommend interventions based on causal analysis"""
        interventions = []

        for chain in causal_chains:
            # Get the root cause from the chain
            root_cause = chain.root_cause

            # Recommend intervention based on root cause
            if 'not installed' in root_cause.lower():
                interventions.append(Intervention(
                    intervention_type=InterventionType.CORRECTIVE,
                    action="Install the missing dependency",
                    target_cause=root_cause,
                    expected_impact="Error will be resolved",
                    confidence=0.9,
                    complexity="simple",
                    time_estimate="1-2 minutes"
                ))

                # Also add preventive
                interventions.append(Intervention(
                    intervention_type=InterventionType.PREVENTIVE,
                    action="Add dependency to requirements file",
                    target_cause=root_cause,
                    expected_impact="Prevents recurrence in fresh environments",
                    confidence=0.85,
                    complexity="simple",
                    time_estimate="1 minute"
                ))

            elif 'permission' in root_cause.lower():
                interventions.append(Intervention(
                    intervention_type=InterventionType.CORRECTIVE,
                    action="Run command with sudo or fix file permissions",
                    target_cause=root_cause,
                    expected_impact="Command will have necessary permissions",
                    confidence=0.9,
                    complexity="simple",
                    time_estimate="1 minute"
                ))

            elif 'test' in root_cause.lower():
                interventions.append(Intervention(
                    intervention_type=InterventionType.PREVENTIVE,
                    action="Test before building",
                    target_cause=root_cause,
                    expected_impact="Errors caught earlier with better context",
                    confidence=0.8,
                    complexity="simple",
                    time_estimate="2-5 minutes"
                ))

        return interventions

    def _learn_causal_pattern(self, situation: str, chains: List[CausalChain]):
        """Learn causal patterns for future reference"""
        # Simplified pattern key
        pattern_key = situation[:50].lower()

        if pattern_key not in self.learned_causal_patterns:
            self.learned_causal_patterns[pattern_key] = []

        self.learned_causal_patterns[pattern_key].extend(chains)

    def get_causal_explanation(self, analysis: CausalAnalysis) -> str:
        """Get a human-readable causal explanation"""
        parts = []

        parts.append(f"📊 Causal Analysis: {analysis.situation}\n")

        # Show causal chains
        if analysis.causal_chains:
            parts.append("\n🔗 Causal Chain:")
            for i, chain in enumerate(analysis.causal_chains, 1):
                parts.append(f"\n{i}. {chain.root_cause}")
                for link in chain.links:
                    parts.append(f"   → {link.effect}")

        # Show counterfactuals
        if analysis.counterfactuals:
            parts.append("\n\n💭 What If:")
            for cf in analysis.counterfactuals:
                parts.append(f"\n• {cf.scenario}")
                parts.append(f"  Likely: {cf.likely_outcome}")

        # Show interventions
        if analysis.interventions:
            parts.append("\n\n✨ Our Path Forward:")
            for i, intervention in enumerate(analysis.interventions[:3], 1):
                parts.append(f"\n{i}. {intervention.action} ({intervention.complexity}, ~{intervention.time_estimate})")
                parts.append(f"   Impact: {intervention.expected_impact}")

        return "".join(parts)


# Global singleton
_causal_reasoning_engine: Optional[CausalReasoningEngine] = None


def get_causal_reasoning_engine() -> CausalReasoningEngine:
    """Get the global causal reasoning engine singleton"""
    global _causal_reasoning_engine
    if _causal_reasoning_engine is None:
        _causal_reasoning_engine = CausalReasoningEngine()
    return _causal_reasoning_engine
