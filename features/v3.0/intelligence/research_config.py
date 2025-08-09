"""
Configuration for research-based symbiotic intelligence components

This configuration enables/disables and configures the advanced research
components including SKG, Trust Engine, Consciousness Metrics, etc.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ResearchConfig:
    """Configuration for research-based components"""
    
    # Symbiotic Knowledge Graph
    skg_enabled: bool = True
    skg_db_path: str = "./data/nix_humanity_skg.db"
    
    # Trust Modeling
    trust_modeling_enabled: bool = True
    trust_initial_level: str = "acquaintance"
    vulnerability_frequency: float = 0.1  # 10% of interactions
    
    # Consciousness Metrics
    consciousness_metrics_enabled: bool = True
    wellbeing_tracking: bool = True
    flow_state_detection: bool = True
    attention_tracking: bool = True
    
    # Activity Monitoring (Privacy-First)
    activity_monitoring_enabled: bool = False  # Opt-in only
    activity_privacy_mode: str = "aggregate"  # strict, aggregate, full
    activity_excluded_apps: list = None
    
    # Sacred Development
    sacred_patterns_enabled: bool = True
    kairos_time_enabled: bool = True
    consciousness_guard_enabled: bool = True
    
    # Integration Settings
    enhanced_responses_enabled: bool = True
    trust_building_responses: bool = True
    consciousness_aware_responses: bool = True
    
    # Learning Settings
    episodic_memory_enabled: bool = True
    phenomenological_tracking: bool = True
    metacognitive_reflection: bool = True
    
    # Performance Settings
    lazy_load_research_components: bool = True
    research_component_timeout: float = 5.0  # seconds
    
    def __post_init__(self):
        """Initialize with environment overrides"""
        # Override from environment variables
        if os.getenv('NIX_HUMANITY_DISABLE_RESEARCH'):
            self.skg_enabled = False
            self.trust_modeling_enabled = False
            self.consciousness_metrics_enabled = False
            
        if os.getenv('NIX_HUMANITY_SKG_PATH'):
            self.skg_db_path = os.getenv('NIX_HUMANITY_SKG_PATH')
            
        if os.getenv('NIX_HUMANITY_ACTIVITY_TRACKING'):
            self.activity_monitoring_enabled = os.getenv(
                'NIX_HUMANITY_ACTIVITY_TRACKING', 'false'
            ).lower() == 'true'
            
        if os.getenv('NIX_HUMANITY_PRIVACY_MODE'):
            self.activity_privacy_mode = os.getenv('NIX_HUMANITY_PRIVACY_MODE')
            
        # Default excluded apps if not provided
        if self.activity_excluded_apps is None:
            self.activity_excluded_apps = [
                '1password', 'bitwarden', 'keepassxc',
                'banking', 'medical', 'private'
            ]
    
    @classmethod
    def from_env(cls) -> 'ResearchConfig':
        """Create config from environment variables"""
        return cls()
    
    def is_research_enabled(self) -> bool:
        """Check if any research component is enabled"""
        return any([
            self.skg_enabled,
            self.trust_modeling_enabled,
            self.consciousness_metrics_enabled,
            self.activity_monitoring_enabled,
            self.sacred_patterns_enabled
        ])
    
    def get_enabled_components(self) -> list[str]:
        """Get list of enabled research components"""
        enabled = []
        
        if self.skg_enabled:
            enabled.append("Symbiotic Knowledge Graph")
        if self.trust_modeling_enabled:
            enabled.append("Trust Modeling Engine")
        if self.consciousness_metrics_enabled:
            enabled.append("Consciousness Metrics")
        if self.activity_monitoring_enabled:
            enabled.append("Activity Monitoring")
        if self.sacred_patterns_enabled:
            enabled.append("Sacred Development Patterns")
            
        return enabled
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'skg': {
                'enabled': self.skg_enabled,
                'db_path': self.skg_db_path
            },
            'trust': {
                'enabled': self.trust_modeling_enabled,
                'initial_level': self.trust_initial_level,
                'vulnerability_frequency': self.vulnerability_frequency
            },
            'consciousness': {
                'enabled': self.consciousness_metrics_enabled,
                'wellbeing': self.wellbeing_tracking,
                'flow_state': self.flow_state_detection,
                'attention': self.attention_tracking
            },
            'activity': {
                'enabled': self.activity_monitoring_enabled,
                'privacy_mode': self.activity_privacy_mode,
                'excluded_apps': self.activity_excluded_apps
            },
            'sacred': {
                'patterns': self.sacred_patterns_enabled,
                'kairos_time': self.kairos_time_enabled,
                'consciousness_guard': self.consciousness_guard_enabled
            },
            'integration': {
                'enhanced_responses': self.enhanced_responses_enabled,
                'trust_building': self.trust_building_responses,
                'consciousness_aware': self.consciousness_aware_responses
            }
        }


# Global config instance
research_config = ResearchConfig.from_env()


def get_research_config() -> ResearchConfig:
    """Get the global research configuration"""
    return research_config


def update_research_config(**kwargs) -> ResearchConfig:
    """Update research configuration with new values"""
    global research_config
    
    for key, value in kwargs.items():
        if hasattr(research_config, key):
            setattr(research_config, key, value)
            
    return research_config