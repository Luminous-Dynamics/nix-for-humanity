"""
Nix for Humanity Configuration System

Provides comprehensive configuration management with support for:
- Multiple configuration sources (system, user, project, environment)
- Configuration file formats (YAML, JSON, TOML)
- Type-safe configuration schema
- Configuration validation
- Hierarchical configuration merging
- User profiles and personas
"""

from .config_manager import ConfigManager, get_config, update_config
from .loader import ConfigLoader
from .profiles import ProfileManager, UserProfile
from .schema import ConfigSchema, NLPConfig, PerformanceConfig, UIConfig

# Create a singleton config manager
_config_manager = None


def get_config_manager():
    """Get the singleton config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


__all__ = [
    "ConfigManager",
    "get_config",
    "update_config",
    "get_config_manager",
    "ConfigSchema",
    "UIConfig",
    "NLPConfig",
    "PerformanceConfig",
    "ConfigLoader",
    "ProfileManager",
    "UserProfile",
]
