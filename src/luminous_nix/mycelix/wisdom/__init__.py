"""
WisdomEngine Integration for Luminous Nix

Provides pattern intelligence powered by the Mycelix WisdomEngine:
- Pattern Learning: Track what works, what fails
- Pattern Succession: Flakes > Channels (learned over time)
- Context-Aware Recommendations: NVIDIA context → NVIDIA patterns
- Trust Weighting: Cryptographically verified > Testimonial

This module bridges the Rust WisdomEngine (mycelix-core-types) to Python.

Initial implementation: Pure Python with JSON persistence
Future: PyO3 native bindings for full performance

Usage:
    from luminous_nix.mycelix.wisdom import get_wisdom_engine

    engine = get_wisdom_engine()
    engine.record_success("flakes", context="development")

    recommendations = engine.recommend_patterns(
        domain="development_environments",
        context="python project"
    )
"""

from .wisdom_bridge import (
    WisdomBridge,
    get_wisdom_engine,
    PatternOutcome,
    PatternRecommendation,
    TrustLevel,
)

from .nixos_patterns import (
    NixOSPatterns,
    NIXOS_DOMAINS,
    NIXOS_PATTERN_CATALOG,
    get_nixos_pattern_catalog,
)

__version__ = "0.1.0-alpha"
__all__ = [
    # Core bridge
    "WisdomBridge",
    "get_wisdom_engine",
    "PatternOutcome",
    "PatternRecommendation",
    "TrustLevel",
    # NixOS patterns
    "NixOSPatterns",
    "NIXOS_DOMAINS",
    "NIXOS_PATTERN_CATALOG",
    "get_nixos_pattern_catalog",
]
