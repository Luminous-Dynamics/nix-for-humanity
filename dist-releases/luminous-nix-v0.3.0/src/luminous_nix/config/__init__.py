"""
Luminous Nix Configuration System

Provides comprehensive configuration management with support for:
- Multiple configuration sources (system, user, project, environment)
- Configuration file formats (YAML, JSON, TOML)
- Type-safe configuration schema
- Configuration validation
- Hierarchical configuration merging
- User profiles and personas
"""

from .config_manager import ConfigManager, get_config, get_config_manager, update_config
from .loader import ConfigLoader
from .profiles import ProfileManager, UserProfile
from .schema import (
    ConfigSchema,
    NLPConfig,
    NLPEngine,
    PerformanceConfig,
    Personality,
    ResponseFormat,
    UIConfig,
)

__all__ = [
    "ConfigManager",
    "get_config",
    "get_config_manager",
    "update_config",
    "ConfigSchema",
    "UIConfig",
    "NLPConfig",
    "PerformanceConfig",
    "Personality",
    "ResponseFormat",
    "NLPEngine",
    "ConfigLoader",
    "ProfileManager",
    "UserProfile",
]
