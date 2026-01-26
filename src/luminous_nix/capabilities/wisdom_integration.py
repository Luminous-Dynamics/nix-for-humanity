"""
WisdomEngine Integration for Luminous Nix CLI

This module bridges the CLI to the WisdomEngine, enabling:
1. READ PATH: Inject pattern recommendations into AI context
2. WRITE PATH: Record command outcomes to improve future recommendations

The Data Flywheel:
    User asks question
    → Wisdom Engine guides response
    → User runs command
    → Result flows back to Wisdom Engine
    → Smarter Engine
    → Repeat
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Add wisdom module to path for direct import (avoids mycelix parent import issues)
_wisdom_path = Path(__file__).parent.parent / "mycelix" / "wisdom"
if str(_wisdom_path) not in sys.path:
    sys.path.insert(0, str(_wisdom_path))

try:
    from wisdom_bridge import WisdomBridge, PatternRecommendation, PatternOutcome
    from nixos_patterns import NixOSPatterns, NIXOS_DOMAINS
    WISDOM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"WisdomEngine not available: {e}")
    WISDOM_AVAILABLE = False


@dataclass
class WisdomContext:
    """Context from the Wisdom Engine for a query"""
    query: str
    domain: str
    recommendations: List[PatternRecommendation]
    injection_text: str
    suggested_patterns: List[str]


class WisdomIntegration:
    """
    Middleware connecting the CLI to the WisdomEngine.

    Handles:
    1. User Query → Contextual Recommendations (Read Path)
    2. Execution Result → Wisdom Reinforcement (Write Path)
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.engine: Optional[WisdomBridge] = None
        self.initialized = False
        self.current_context: Optional[WisdomContext] = None

        if not WISDOM_AVAILABLE:
            if verbose:
                logger.info("WisdomEngine not available - running without pattern intelligence")
            return

        try:
            # Initialize engine
            storage_path = Path.home() / ".luminous-nix" / "wisdom"
            self.engine = WisdomBridge(storage_path)

            # Check if we need to bootstrap with NixOS patterns
            stats = self.engine.get_stats()
            if stats["total_patterns"] == 0:
                if verbose:
                    print("🌱 Initializing WisdomEngine with NixOS pattern catalog...")
                count = NixOSPatterns.initialize_engine(self.engine)
                NixOSPatterns.seed_with_community_wisdom(self.engine)
                if verbose:
                    print(f"   Loaded {count} patterns with community wisdom")

            self.initialized = True

            if verbose:
                print(f"🧠 WisdomEngine active: {stats['total_patterns']} patterns, "
                      f"{stats['total_uses']} recorded outcomes")

        except Exception as e:
            logger.error(f"Failed to initialize WisdomEngine: {e}")
            self.engine = None

    def detect_domain(self, query: str) -> str:
        """Detect the NixOS domain from the query text"""
        query_lower = query.lower()

        # Hardware detection
        if any(kw in query_lower for kw in ["nvidia", "cuda", "geforce", "rtx", "gtx"]):
            return NIXOS_DOMAINS.HARDWARE_NVIDIA
        if any(kw in query_lower for kw in ["amd", "radeon", "rocm", "rx "]):
            return NIXOS_DOMAINS.HARDWARE_AMD
        if any(kw in query_lower for kw in ["driver", "gpu", "graphics", "hardware"]):
            return NIXOS_DOMAINS.HARDWARE

        # Development detection
        if any(kw in query_lower for kw in ["devshell", "dev shell", "development", "python",
                                             "rust", "node", "project", "environment"]):
            return NIXOS_DOMAINS.DEVELOPMENT

        # Secrets detection
        if any(kw in query_lower for kw in ["secret", "password", "credential", "agenix",
                                             "sops", "encrypt", "key"]):
            return NIXOS_DOMAINS.SECRETS

        # Flakes detection
        if any(kw in query_lower for kw in ["flake", "flake.nix", "nix develop", "inputs"]):
            return NIXOS_DOMAINS.FLAKES

        # Package management detection
        if any(kw in query_lower for kw in ["install", "package", "nix-env", "channel"]):
            return NIXOS_DOMAINS.PACKAGE_MANAGEMENT

        # Default to system management
        return NIXOS_DOMAINS.SYSTEM_MANAGEMENT

    def get_context_injection(self, query: str) -> str:
        """
        Get wisdom context to inject into the AI prompt.

        Returns a formatted string with pattern recommendations
        that helps the AI give better answers.
        """
        if not self.initialized or not self.engine:
            return ""

        try:
            # Detect domain from query
            domain = self.detect_domain(query)

            # Get recommendations
            recommendations = self.engine.recommend_patterns(
                domain=domain,
                context=query,
                limit=3
            )

            if not recommendations:
                return ""

            # Store for later outcome recording
            self.current_context = WisdomContext(
                query=query,
                domain=domain,
                recommendations=recommendations,
                injection_text="",
                suggested_patterns=[r.pattern_id for r in recommendations]
            )

            # Format for AI context
            injection = "\n[WISDOM ENGINE - Learned Patterns]\n"
            injection += "These patterns have proven success in similar situations:\n\n"

            for rec in recommendations:
                # Get pattern details
                pattern = self.engine.get_pattern(rec.pattern_id)
                if not pattern:
                    continue

                # Trust indicator
                trust_icon = {
                    "CRYPTOGRAPHIC": "🔒",
                    "AUDITED": "✅",
                    "TESTIMONIAL": "📝"
                }.get(pattern.trust_level, "📝")

                injection += f"{trust_icon} **{rec.pattern_name}** "
                injection += f"(score: {rec.score:.0%}, confidence: {rec.confidence:.0%})\n"

                # Description
                injection += f"   {pattern.description}\n"

                # Reasons
                if rec.reasons:
                    for reason in rec.reasons[:2]:
                        injection += f"   + {reason}\n"

                # Warnings
                if rec.warnings:
                    for warning in rec.warnings:
                        injection += f"   ⚠️ {warning}\n"

                # Check for succession
                successor_id = self.engine.get_successor(rec.pattern_id)
                if successor_id:
                    successor = self.engine.get_pattern(successor_id)
                    if successor:
                        injection += f"   → Prefer: {successor.name}\n"

                injection += "\n"

            injection += "[END WISDOM CONTEXT]\n"

            self.current_context.injection_text = injection

            return injection

        except Exception as e:
            logger.error(f"Error getting wisdom context: {e}")
            return ""

    def record_outcome(
        self,
        command: str,
        exit_code: int,
        error_message: Optional[str] = None
    ):
        """
        Record the outcome of a command execution.

        This is the WRITE PATH of the data flywheel.
        """
        if not self.initialized or not self.engine:
            return

        if not self.current_context:
            # No context - try to attribute based on command
            return

        try:
            success = (exit_code == 0)
            outcome = PatternOutcome.SUCCESS if success else PatternOutcome.FAILURE

            # Attribute to the top recommended pattern
            if self.current_context.suggested_patterns:
                top_pattern_id = self.current_context.suggested_patterns[0]
                pattern = self.engine.get_pattern(top_pattern_id)

                if pattern:
                    if success:
                        self.engine.record_success(
                            top_pattern_id,
                            context=self.current_context.query[:50]
                        )
                        if self.verbose:
                            print(f"   🧠 Recorded success for '{pattern.name}'")
                    else:
                        self.engine.record_failure(
                            top_pattern_id,
                            context=self.current_context.query[:50]
                        )
                        if self.verbose:
                            print(f"   🧠 Recorded failure for '{pattern.name}'")

            # Clear context after recording
            self.current_context = None

        except Exception as e:
            logger.error(f"Error recording outcome: {e}")

    def get_stats_summary(self) -> str:
        """Get a human-readable summary of wisdom engine stats"""
        if not self.initialized or not self.engine:
            return "WisdomEngine not available"

        stats = self.engine.get_stats()

        return (
            f"Patterns: {stats['total_patterns']} "
            f"({stats['active_patterns']} active, {stats['deprecated_patterns']} deprecated) | "
            f"Uses: {stats['total_uses']} | "
            f"Success rate: {stats['overall_success_rate']:.1%}"
        )

    def explain_pattern(self, pattern_id: str) -> Optional[str]:
        """Get detailed explanation for a pattern"""
        if not self.initialized or not self.engine:
            return None

        pattern = self.engine.get_pattern(pattern_id)
        if not pattern:
            return None

        lines = [
            f"Pattern: {pattern.name}",
            f"Description: {pattern.description}",
            f"Domain: {pattern.domain}",
            f"Trust Level: {pattern.trust_level}",
            f"Success Rate: {pattern.success_rate:.1%} ({pattern.total_uses} uses)",
            f"State: {pattern.state}",
        ]

        successor_id = self.engine.get_successor(pattern_id)
        if successor_id:
            successor = self.engine.get_pattern(successor_id)
            if successor:
                lines.append(f"Successor: {successor.name}")

        return "\n".join(lines)


# Singleton instance
_integration: Optional[WisdomIntegration] = None


def get_wisdom_integration(verbose: bool = False) -> WisdomIntegration:
    """Get or create the singleton WisdomIntegration instance"""
    global _integration

    if _integration is None:
        _integration = WisdomIntegration(verbose=verbose)

    return _integration


def reset_wisdom_integration():
    """Reset the singleton (for testing)"""
    global _integration
    _integration = None
