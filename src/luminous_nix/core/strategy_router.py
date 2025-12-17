"""
Strategy Router - Intelligent routing of intents to execution strategies

This is the key piece that transforms Luminous Nix from a simple command executor
into an expert system that can "handle anything a NixOS expert can do."

Architecture Layer: 3 (Strategy Selection)
Connects: Intent Recognition (Layer 1-2) → Execution (Layer 4)
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Available execution strategies"""
    # Package management strategies
    USER_ENV = "user_environment"  # nix-env for user packages
    SYSTEM_WIDE = "system_wide"  # configuration.nix system packages
    FLAKE_BASED = "flake_based"  # flake.nix with lock file
    TEMPORARY = "temporary"  # nix-shell for one-off use

    # Configuration strategies
    DECLARATIVE = "declarative"  # Edit configuration.nix
    IMPERATIVE = "imperative"  # Direct nix commands
    MODULAR = "modular"  # Create/use modules

    # Multi-step strategies
    TEMPLATE_BASED = "template"  # Use predefined template
    COMPOSED = "composed"  # Dynamically compose operations
    ADAPTIVE = "adaptive"  # Try multiple approaches

    # Expert strategies
    ANALYSIS_THEN_ACTION = "analyze_first"  # Analyze before acting
    PARALLEL_EXECUTION = "parallel"  # Execute steps in parallel
    INCREMENTAL = "incremental"  # Step-by-step with verification


@dataclass
class SystemCapabilities:
    """What the target system can do"""
    has_flakes: bool = False
    has_binary_cache: bool = True
    has_nix_command: bool = False
    nixos_version: str = "24.11"
    is_nixos: bool = True
    disk_space_gb: float = 0.0
    network_available: bool = True

    # Advanced capabilities
    can_use_substituters: bool = True
    can_parallel_build: bool = True
    max_jobs: int = 4


@dataclass
class UserProfile:
    """User preferences and skill level"""
    skill_level: str = "intermediate"  # beginner, intermediate, expert
    prefers_system_packages: bool = True
    prefers_flakes: bool = False
    risk_tolerance: str = "moderate"  # cautious, moderate, aggressive
    optimization_preference: str = "balanced"  # speed, reliability, minimal

    # Learning from history
    successful_strategies: Dict[str, int] = None  # strategy -> success count
    failed_strategies: Dict[str, int] = None  # strategy -> failure count

    def __post_init__(self):
        if self.successful_strategies is None:
            self.successful_strategies = {}
        if self.failed_strategies is None:
            self.failed_strategies = {}


@dataclass
class ExecutionContext:
    """Full context for strategy selection"""
    system: SystemCapabilities
    user: UserProfile
    intent_type: str
    intent_tags: List[str]
    complexity: str  # simple, moderate, complex, expert
    time_pressure: str = "normal"  # urgent, normal, relaxed

    def __post_init__(self):
        if self.intent_tags is None:
            self.intent_tags = []


@dataclass
class SelectedStrategy:
    """The chosen strategy with rationale"""
    strategy: StrategyType
    confidence: float  # 0.0-1.0
    rationale: List[str]  # Why this strategy was chosen
    alternatives: List[StrategyType]  # Fallback options if primary fails
    estimated_time: float  # Seconds
    risk_level: str  # low, medium, high


class StrategyRouter:
    """
    Intelligently route intents to the best execution strategy.

    This is what makes "install firefox" actually expert-level:
    - Considers system capabilities (flakes? cache?)
    - Considers user preferences (system-wide? user env?)
    - Considers context (network available? disk space?)
    - Learns from history (what worked before?)
    - Provides fallbacks (primary fails? try alternative)
    """

    def __init__(self,
                 system_profiler=None,
                 user_profiler=None):
        """
        Initialize strategy router

        Args:
            system_profiler: Analyzes system capabilities
            user_profiler: Tracks user preferences
        """
        self.system_profiler = system_profiler
        self.user_profiler = user_profiler

        # Strategy ranking weights (learned over time)
        self.strategy_weights = {
            StrategyType.FLAKE_BASED: 1.0,  # Preferred when available
            StrategyType.SYSTEM_WIDE: 0.9,  # Reliable, reproducible
            StrategyType.USER_ENV: 0.7,  # Quick but less reproducible
            StrategyType.TEMPORARY: 0.5,  # One-off use only
        }

    def select_strategy(self,
                       intent_type: str,
                       context: ExecutionContext) -> SelectedStrategy:
        """
        Select the best execution strategy for this intent and context

        This is the core intelligence that transforms simple operations
        into expert-level decision making.

        Args:
            intent_type: Type of operation (install, configure, etc.)
            context: Full execution context

        Returns:
            SelectedStrategy with primary + alternatives
        """
        logger.info(f"Selecting strategy for {intent_type} with context: {context}")

        # Route to appropriate selector
        if intent_type in ["install", "remove", "update"]:
            return self._select_package_strategy(intent_type, context)
        elif intent_type in ["configure", "enable_service", "setup"]:
            return self._select_config_strategy(intent_type, context)
        elif intent_type in ["migrate", "refactor", "optimize"]:
            return self._select_expert_strategy(intent_type, context)
        else:
            return self._select_generic_strategy(intent_type, context)

    def _select_package_strategy(self,
                                 intent_type: str,
                                 context: ExecutionContext) -> SelectedStrategy:
        """
        Select strategy for package operations

        This shows how "install firefox" becomes intelligent:
        """
        rationale = []
        candidates = []

        # Check flakes preference and availability
        if context.system.has_flakes and context.user.prefers_flakes:
            candidates.append((StrategyType.FLAKE_BASED, 0.95))
            rationale.append("Flakes enabled and user prefers them")
        elif context.system.has_flakes and context.user.skill_level == "expert":
            candidates.append((StrategyType.FLAKE_BASED, 0.85))
            rationale.append("Flakes available and user is expert")

        # Check system-wide preference
        if context.user.prefers_system_packages:
            candidates.append((StrategyType.SYSTEM_WIDE, 0.90))
            rationale.append("User prefers system-wide packages")
        elif context.system.is_nixos:
            candidates.append((StrategyType.SYSTEM_WIDE, 0.80))
            rationale.append("NixOS system supports declarative config")

        # User environment is always available
        candidates.append((StrategyType.USER_ENV, 0.70))
        rationale.append("User environment available as fallback")

        # Temporary for one-off testing
        if "test" in context.intent_tags or "temporary" in context.intent_tags:
            candidates.append((StrategyType.TEMPORARY, 0.85))
            rationale.append("Temporary use requested")

        # Consider success history
        if context.user.successful_strategies:
            for strategy, confidence in candidates:
                success_count = context.user.successful_strategies.get(strategy.value, 0)
                failure_count = context.user.failed_strategies.get(strategy.value, 0)
                if success_count > 0:
                    success_rate = success_count / (success_count + failure_count + 1)
                    adjusted_confidence = confidence * (0.7 + 0.3 * success_rate)
                    candidates = [(s, adjusted_confidence if s == strategy else c)
                                 for s, c in candidates]
                    rationale.append(f"{strategy.value} has {success_rate:.0%} success rate")

        # Sort by confidence
        candidates.sort(key=lambda x: x[1], reverse=True)

        if not candidates:
            # Fallback: user environment
            return SelectedStrategy(
                strategy=StrategyType.USER_ENV,
                confidence=0.5,
                rationale=["Default fallback to user environment"],
                alternatives=[StrategyType.SYSTEM_WIDE],
                estimated_time=30.0,
                risk_level="low"
            )

        # Select primary and alternatives
        primary = candidates[0]
        alternatives = [s for s, _ in candidates[1:3]]

        return SelectedStrategy(
            strategy=primary[0],
            confidence=primary[1],
            rationale=rationale,
            alternatives=alternatives,
            estimated_time=self._estimate_time(primary[0], context),
            risk_level=self._assess_risk(primary[0], context)
        )

    def _select_config_strategy(self,
                               intent_type: str,
                               context: ExecutionContext) -> SelectedStrategy:
        """Select strategy for configuration operations"""

        rationale = []

        # For NixOS, declarative is preferred
        if context.system.is_nixos:
            rationale.append("NixOS system: using declarative configuration")

            # Check if modular approach is better
            if context.complexity in ["complex", "expert"]:
                rationale.append("Complex operation: using modular approach")
                return SelectedStrategy(
                    strategy=StrategyType.MODULAR,
                    confidence=0.9,
                    rationale=rationale,
                    alternatives=[StrategyType.DECLARATIVE, StrategyType.COMPOSED],
                    estimated_time=120.0,
                    risk_level="medium"
                )

            return SelectedStrategy(
                strategy=StrategyType.DECLARATIVE,
                confidence=0.85,
                rationale=rationale,
                alternatives=[StrategyType.IMPERATIVE],
                estimated_time=60.0,
                risk_level="low"
            )

        # Non-NixOS: imperative commands
        rationale.append("Non-NixOS system: using imperative commands")
        return SelectedStrategy(
            strategy=StrategyType.IMPERATIVE,
            confidence=0.75,
            rationale=rationale,
            alternatives=[StrategyType.TEMPLATE_BASED],
            estimated_time=45.0,
            risk_level="medium"
        )

    def _select_expert_strategy(self,
                                intent_type: str,
                                context: ExecutionContext) -> SelectedStrategy:
        """
        Select strategy for expert-level operations

        Examples: migrate to flakes, optimize performance, refactor config
        """

        rationale = [f"Expert operation: {intent_type}"]

        # Expert operations need analysis first
        if context.user.skill_level != "expert" and context.user.risk_tolerance != "aggressive":
            rationale.append("Non-expert user: analyzing before action")
            return SelectedStrategy(
                strategy=StrategyType.ANALYSIS_THEN_ACTION,
                confidence=0.95,
                rationale=rationale,
                alternatives=[StrategyType.INCREMENTAL, StrategyType.ADAPTIVE],
                estimated_time=300.0,
                risk_level="high"
            )

        # Expert users can use adaptive strategy
        if context.user.skill_level == "expert":
            rationale.append("Expert user: using adaptive strategy")
            return SelectedStrategy(
                strategy=StrategyType.ADAPTIVE,
                confidence=0.90,
                rationale=rationale,
                alternatives=[StrategyType.INCREMENTAL, StrategyType.ANALYSIS_THEN_ACTION],
                estimated_time=180.0,
                risk_level="medium"
            )

        # Default: incremental with verification
        rationale.append("Using incremental strategy with verification")
        return SelectedStrategy(
            strategy=StrategyType.INCREMENTAL,
            confidence=0.85,
            rationale=rationale,
            alternatives=[StrategyType.ADAPTIVE, StrategyType.TEMPLATE_BASED],
            estimated_time=240.0,
            risk_level="medium"
        )

    def _select_generic_strategy(self,
                                intent_type: str,
                                context: ExecutionContext) -> SelectedStrategy:
        """Fallback for unknown intent types"""

        return SelectedStrategy(
            strategy=StrategyType.ADAPTIVE,
            confidence=0.6,
            rationale=["Unknown intent type, using adaptive strategy"],
            alternatives=[StrategyType.TEMPLATE_BASED, StrategyType.IMPERATIVE],
            estimated_time=90.0,
            risk_level="medium"
        )

    def _estimate_time(self, strategy: StrategyType, context: ExecutionContext) -> float:
        """Estimate execution time in seconds"""

        # Base times by strategy
        base_times = {
            StrategyType.USER_ENV: 30.0,
            StrategyType.SYSTEM_WIDE: 120.0,  # Needs rebuild
            StrategyType.FLAKE_BASED: 60.0,
            StrategyType.TEMPORARY: 15.0,
            StrategyType.DECLARATIVE: 90.0,
            StrategyType.IMPERATIVE: 30.0,
            StrategyType.MODULAR: 180.0,
            StrategyType.TEMPLATE_BASED: 120.0,
            StrategyType.COMPOSED: 180.0,
            StrategyType.ADAPTIVE: 90.0,
            StrategyType.ANALYSIS_THEN_ACTION: 300.0,
            StrategyType.PARALLEL_EXECUTION: 60.0,
            StrategyType.INCREMENTAL: 240.0,
        }

        base = base_times.get(strategy, 60.0)

        # Adjust for network
        if not context.system.network_available:
            base *= 3.0  # Much slower without cache

        # Adjust for complexity
        if context.complexity == "expert":
            base *= 2.0
        elif context.complexity == "complex":
            base *= 1.5

        return base

    def _assess_risk(self, strategy: StrategyType, context: ExecutionContext) -> str:
        """Assess risk level of strategy"""

        # Declarative strategies are lower risk
        if strategy in [StrategyType.DECLARATIVE, StrategyType.MODULAR, StrategyType.ANALYSIS_THEN_ACTION]:
            return "low"

        # Expert strategies are higher risk
        if strategy in [StrategyType.ADAPTIVE, StrategyType.COMPOSED]:
            if context.user.skill_level == "beginner":
                return "high"
            else:
                return "medium"

        # User environment is generally safe
        if strategy == StrategyType.USER_ENV:
            return "low"

        # System-wide changes are medium risk
        if strategy == StrategyType.SYSTEM_WIDE:
            return "medium"

        return "medium"

    def learn_from_outcome(self,
                          strategy: StrategyType,
                          success: bool,
                          user_profile: UserProfile):
        """
        Learn from execution outcome to improve future selections

        This is key to the system getting smarter over time.
        """
        if success:
            user_profile.successful_strategies[strategy.value] = \
                user_profile.successful_strategies.get(strategy.value, 0) + 1
            logger.info(f"Strategy {strategy.value} succeeded, updated profile")
        else:
            user_profile.failed_strategies[strategy.value] = \
                user_profile.failed_strategies.get(strategy.value, 0) + 1
            logger.info(f"Strategy {strategy.value} failed, updated profile")

    def explain_selection(self, selected: SelectedStrategy) -> str:
        """
        Generate human-readable explanation of strategy selection

        Transparency is crucial for user trust.
        """
        explanation = [
            f"Selected strategy: {selected.strategy.value}",
            f"Confidence: {selected.confidence:.0%}",
            "",
            "Reasoning:"
        ]

        for reason in selected.rationale:
            explanation.append(f"  • {reason}")

        if selected.alternatives:
            explanation.append("")
            explanation.append("Fallback options if primary fails:")
            for alt in selected.alternatives:
                explanation.append(f"  • {alt.value}")

        explanation.extend([
            "",
            f"Estimated time: {selected.estimated_time:.0f}s",
            f"Risk level: {selected.risk_level}"
        ])

        return "\n".join(explanation)


# Convenience function for quick usage
def select_best_strategy(intent_type: str,
                        system: SystemCapabilities,
                        user: UserProfile,
                        complexity: str = "simple",
                        intent_tags: List[str] = None) -> SelectedStrategy:
    """
    Quick helper to select strategy without full context setup
    """
    context = ExecutionContext(
        system=system,
        user=user,
        intent_type=intent_type,
        intent_tags=intent_tags or [],
        complexity=complexity
    )

    router = StrategyRouter()
    return router.select_strategy(intent_type, context)


if __name__ == "__main__":
    # Demo: Show how "install firefox" becomes intelligent

    print("=== Demo: Intelligent Strategy Selection ===\n")

    # Scenario 1: Beginner user on flakes-enabled system
    print("Scenario 1: Beginner user, flakes available")
    print("-" * 50)

    system1 = SystemCapabilities(
        has_flakes=True,
        has_binary_cache=True,
        is_nixos=True,
        disk_space_gb=100.0
    )

    user1 = UserProfile(
        skill_level="beginner",
        prefers_system_packages=True,
        risk_tolerance="cautious"
    )

    context1 = ExecutionContext(
        system=system1,
        user=user1,
        intent_type="install",
        intent_tags=["package"],
        complexity="simple"
    )

    router = StrategyRouter()
    strategy1 = router.select_strategy("install", context1)

    print(router.explain_selection(strategy1))

    print("\n" + "="*50 + "\n")

    # Scenario 2: Expert user wanting to migrate to flakes
    print("Scenario 2: Expert user, migrate to flakes")
    print("-" * 50)

    system2 = SystemCapabilities(
        has_flakes=False,  # Not yet enabled
        is_nixos=True
    )

    user2 = UserProfile(
        skill_level="expert",
        risk_tolerance="aggressive",
        prefers_flakes=True
    )

    context2 = ExecutionContext(
        system=system2,
        user=user2,
        intent_type="migrate",
        intent_tags=["flakes", "refactor"],
        complexity="expert"
    )

    strategy2 = router.select_strategy("migrate", context2)

    print(router.explain_selection(strategy2))
