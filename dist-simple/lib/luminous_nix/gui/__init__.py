"""🎨 AI-Driven Interface Generation for Luminous Nix

A complete production-ready system for generating interfaces from natural language.
"""

__version__ = "1.0.0"

# Core exports
from .cli_integration import UIGeneratorCLI
from .nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext
from .textual_ui_renderer import TextualUIRenderer

# Service exports
from .services import (
    InterfaceGenerationService,
    PatternAnalysisService,
    FeedbackService,
    OptimizationService,
    ABTestingService,
    PerformanceService,
)

# Production exports
from .production_deployment import ProductionDeployment
# from .api_server import create_app  # Not implemented yet

__all__ = [
    "UIGeneratorCLI",
    "NLInterfaceBuilderV2",
    "UserContext",
    "TextualUIRenderer",
    "InterfaceGenerationService",
    "PatternAnalysisService",
    "FeedbackService",
    "OptimizationService",
    "ABTestingService",
    "PerformanceService",
    "ProductionDeployment",
    # "create_app",  # Not implemented yet
]