#!/usr/bin/env python3
"""
⚙️ Configuration Management System for AI-Driven Interface Generation
Centralized configuration for all adjustable parameters
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import timedelta

from error_handler import safe_file_operation, get_logger


@dataclass
class OptimizationConfig:
    """Configuration for optimization engine"""
    
    # Thresholds
    min_confidence: float = 0.7
    cooldown_hours: int = 24
    min_data_points: int = 10
    measurement_period_hours: int = 24
    
    # Performance thresholds
    slow_generation_threshold_ms: int = 2000
    low_satisfaction_threshold: float = 3.0
    high_error_rate_threshold: float = 0.1
    high_abandonment_threshold: float = 0.3
    low_task_completion_threshold: float = 0.6
    low_accessibility_threshold: float = 0.7
    max_workflow_steps: int = 5
    
    # Auto-apply settings
    auto_apply: bool = True
    require_approval: bool = False


@dataclass
class PatternAnalysisConfig:
    """Configuration for pattern analysis"""
    
    # Analysis parameters
    min_pattern_frequency: int = 3
    confidence_threshold: float = 0.7
    analysis_window_days: int = 30
    
    # Trend detection
    trend_change_threshold_percent: float = 5.0
    min_data_points_for_trend: int = 3
    
    # Insight generation
    significant_change_threshold: float = 10.0
    high_optimization_score: float = 0.7


@dataclass
class FeedbackConfig:
    """Configuration for feedback collection"""
    
    # Trigger thresholds
    time_based_trigger_seconds: int = 30
    interaction_based_trigger: int = 10
    feedback_cooldown_seconds: int = 60
    
    # Collection settings
    max_storage_days: int = 90
    min_feedback_for_summary: int = 10
    
    # Sentiment thresholds
    positive_sentiment_threshold: float = 0.2
    negative_sentiment_threshold: float = -0.2


@dataclass
class ABTestingConfig:
    """Configuration for A/B testing"""
    
    # Test parameters
    minimum_sample_size: int = 50
    confidence_level: float = 0.95
    significant_improvement_threshold: float = 0.05
    
    # Test duration
    min_test_duration_hours: int = 24
    max_test_duration_days: int = 30
    
    # Auto-conclusion
    auto_conclude: bool = True
    auto_apply_winner: bool = False


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring"""
    
    # Monitoring intervals
    metric_collection_interval_seconds: int = 60
    summary_calculation_interval_minutes: int = 15
    
    # Performance thresholds
    slow_response_threshold_ms: int = 1000
    high_memory_threshold_mb: int = 500
    high_cpu_threshold_percent: float = 80.0
    
    # History settings
    max_metric_history_points: int = 1000
    metric_retention_days: int = 30


@dataclass
class InterfaceConfig:
    """Configuration for interface generation"""
    
    # Generation settings
    max_components_per_interface: int = 20
    default_complexity_level: str = "moderate"
    enable_animations: bool = True
    enable_accessibility_features: bool = True
    
    # Component DNA settings
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    evolution_generations: int = 10
    population_size: int = 20


@dataclass
class SystemConfig:
    """Main system configuration"""
    
    # Component configurations
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    pattern_analysis: PatternAnalysisConfig = field(default_factory=PatternAnalysisConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    ab_testing: ABTestingConfig = field(default_factory=ABTestingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    interface: InterfaceConfig = field(default_factory=InterfaceConfig)
    
    # System-wide settings
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Storage paths
    data_dir: str = str(Path.home() / ".local" / "share" / "luminous-nix")
    cache_dir: str = str(Path.home() / ".cache" / "luminous-nix")
    config_dir: str = str(Path.home() / ".config" / "luminous-nix")
    
    # Database settings
    db_path: str = str(Path.home() / ".local" / "share" / "luminous-nix" / "learning.db")
    enable_wal_mode: bool = True
    
    # Feature flags
    enable_voice: bool = True
    enable_consciousness_tracking: bool = True
    enable_sacred_pause: bool = True
    enable_auto_optimization: bool = True
    enable_pattern_learning: bool = True


class ConfigManager:
    """Manages system configuration with environment variable override"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[SystemConfig] = None
    
    def __new__(cls):
        """Singleton pattern for config manager"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager"""
        if self._config is None:
            self.logger = get_logger(__name__)
            self.config_file = Path.home() / ".config" / "luminous-nix" / "config.json"
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self._config = self._load_config()
    
    @property
    def config(self) -> SystemConfig:
        """Get current configuration"""
        return self._config
    
    @safe_file_operation(default_return=None)
    def _load_config(self) -> SystemConfig:
        """Load configuration from file and environment"""
        
        config_data = {}
        
        # Load from file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self.logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}")
        
        # Create config with defaults
        config = SystemConfig()
        
        # Override with file values
        self._update_config_from_dict(config, config_data)
        
        # Override with environment variables
        self._override_from_environment(config)
        
        return config
    
    def _update_config_from_dict(self, config: SystemConfig, data: Dict[str, Any]):
        """Update config object from dictionary"""
        
        for key, value in data.items():
            if hasattr(config, key):
                if isinstance(value, dict):
                    # Nested configuration
                    sub_config = getattr(config, key)
                    for sub_key, sub_value in value.items():
                        if hasattr(sub_config, sub_key):
                            setattr(sub_config, sub_key, sub_value)
                else:
                    setattr(config, key, value)
    
    def _override_from_environment(self, config: SystemConfig):
        """Override configuration from environment variables"""
        
        # Format: LUMINOUS_<SECTION>_<KEY>
        # Example: LUMINOUS_OPTIMIZATION_MIN_CONFIDENCE=0.8
        
        env_prefix = "LUMINOUS_"
        
        for key, value in os.environ.items():
            if not key.startswith(env_prefix):
                continue
            
            # Parse environment variable
            parts = key[len(env_prefix):].lower().split('_')
            
            if len(parts) < 2:
                continue
            
            section = parts[0]
            setting = '_'.join(parts[1:])
            
            # Apply to configuration
            try:
                if hasattr(config, section):
                    sub_config = getattr(config, section)
                    if hasattr(sub_config, setting):
                        # Convert value type
                        current_value = getattr(sub_config, setting)
                        if isinstance(current_value, bool):
                            new_value = value.lower() in ('true', '1', 'yes')
                        elif isinstance(current_value, int):
                            new_value = int(value)
                        elif isinstance(current_value, float):
                            new_value = float(value)
                        else:
                            new_value = value
                        
                        setattr(sub_config, setting, new_value)
                        self.logger.debug(f"Override {section}.{setting} = {new_value}")
                elif setting in ['debug_mode', 'log_level', 'data_dir', 'cache_dir', 'config_dir', 'db_path']:
                    # System-wide settings
                    if setting == 'debug_mode':
                        config.debug_mode = value.lower() in ('true', '1', 'yes')
                    else:
                        setattr(config, setting, value)
                    self.logger.debug(f"Override {setting} = {value}")
            except Exception as e:
                self.logger.warning(f"Failed to apply environment override {key}: {e}")
    
    @safe_file_operation(default_return=False)
    def save_config(self) -> bool:
        """Save current configuration to file"""
        
        try:
            # Convert to dictionary
            config_dict = self._config_to_dict(self._config)
            
            # Write to file
            with open(self.config_file, 'w') as f:
                json.dumps(config_dict, f, indent=2)
            
            self.logger.info(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """Convert config object to dictionary"""
        
        result = {}
        
        for key, value in asdict(config).items():
            if isinstance(value, dict):
                # Nested config - already converted by asdict
                result[key] = value
            else:
                result[key] = value
        
        return result
    
    def update_config(self, section: str, **kwargs):
        """Update configuration values"""
        
        if hasattr(self._config, section):
            sub_config = getattr(self._config, section)
            for key, value in kwargs.items():
                if hasattr(sub_config, key):
                    setattr(sub_config, key, value)
                    self.logger.info(f"Updated {section}.{key} = {value}")
        else:
            self.logger.warning(f"Configuration section '{section}' not found")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        
        self._config = SystemConfig()
        self.logger.info("Reset configuration to defaults")
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """Get configuration value by path (e.g., 'optimization.min_confidence')"""
        
        parts = path.split('.')
        current = self._config
        
        try:
            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                else:
                    return default
            return current
        except Exception:
            return default


# Global configuration instance
config = ConfigManager().config


def get_config() -> SystemConfig:
    """Get global configuration instance"""
    return ConfigManager().config


def update_config(section: str, **kwargs):
    """Update configuration section"""
    ConfigManager().update_config(section, **kwargs)


def save_config():
    """Save current configuration"""
    return ConfigManager().save_config()


def demo_configuration():
    """Demonstrate configuration management"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        ⚙️ CONFIGURATION MANAGEMENT DEMO                             ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Get configuration
    cfg = get_config()
    
    print("\n📋 Current Configuration:")
    print("-" * 60)
    print(f"   Optimization:")
    print(f"     • Min confidence: {cfg.optimization.min_confidence}")
    print(f"     • Cooldown hours: {cfg.optimization.cooldown_hours}")
    print(f"     • Auto-apply: {cfg.optimization.auto_apply}")
    
    print(f"\n   Pattern Analysis:")
    print(f"     • Min frequency: {cfg.pattern_analysis.min_pattern_frequency}")
    print(f"     • Confidence threshold: {cfg.pattern_analysis.confidence_threshold}")
    print(f"     • Analysis window: {cfg.pattern_analysis.analysis_window_days} days")
    
    print(f"\n   Feedback:")
    print(f"     • Time trigger: {cfg.feedback.time_based_trigger_seconds}s")
    print(f"     • Interaction trigger: {cfg.feedback.interaction_based_trigger}")
    
    print(f"\n   System:")
    print(f"     • Debug mode: {cfg.debug_mode}")
    print(f"     • Data directory: {cfg.data_dir}")
    print(f"     • Enable voice: {cfg.enable_voice}")
    
    # Test environment override
    print("\n🔧 Testing Environment Override:")
    print("-" * 60)
    os.environ['LUMINOUS_OPTIMIZATION_MIN_CONFIDENCE'] = '0.9'
    os.environ['LUMINOUS_DEBUG_MODE'] = 'true'
    
    # Reload config
    new_manager = ConfigManager()
    new_manager._config = new_manager._load_config()
    cfg = new_manager.config
    
    print(f"   After environment override:")
    print(f"     • Min confidence: {cfg.optimization.min_confidence}")
    print(f"     • Debug mode: {cfg.debug_mode}")
    
    # Test programmatic update
    print("\n✏️ Testing Programmatic Update:")
    print("-" * 60)
    update_config('pattern_analysis', min_pattern_frequency=5, confidence_threshold=0.8)
    
    cfg = get_config()
    print(f"   After update:")
    print(f"     • Min frequency: {cfg.pattern_analysis.min_pattern_frequency}")
    print(f"     • Confidence threshold: {cfg.pattern_analysis.confidence_threshold}")
    
    # Test path-based access
    print("\n🔍 Testing Path-Based Access:")
    print("-" * 60)
    manager = ConfigManager()
    value = manager.get_value('optimization.slow_generation_threshold_ms')
    print(f"   optimization.slow_generation_threshold_ms = {value}")
    
    print("""
    
═══════════════════════════════════════════════════════════════════════
✨ Configuration Management Features:

1. Centralized Configuration:
   • All parameters in one place
   • No more magic numbers
   • Type-safe dataclasses

2. Environment Override:
   • LUMINOUS_<SECTION>_<KEY> format
   • Production deployment flexibility
   • No code changes needed

3. File Persistence:
   • JSON configuration file
   • User preferences saved
   • Easy backup/restore

4. Hierarchical Structure:
   • Organized by component
   • Clear naming conventions
   • Easy to extend

5. Default Values:
   • Sensible defaults
   • Works out of the box
   • Progressive customization

Next Steps:
• Connect all components to use config
• Add configuration UI
• Implement hot-reload
• Add validation rules
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_configuration()