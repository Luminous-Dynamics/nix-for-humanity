"""
Feature Readiness Tracking System

This module provides a unified system for tracking and progressively activating
features as they move from vision to working state.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import functools

logger = logging.getLogger(__name__)


class ReadinessLevel(Enum):
    """Feature readiness levels with activation thresholds"""
    VISION = (0.0, 0.25, "🔴")      # 0-25% ready
    TESTING = (0.25, 0.50, "🟠")    # 25-50% ready
    INTEGRATING = (0.50, 0.75, "🟡") # 50-75% ready
    WORKING = (0.75, 1.0, "🟢")     # 75-100% ready
    
    def __init__(self, min_threshold: float, max_threshold: float, icon: str):
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.icon = icon
    
    @classmethod
    def from_readiness(cls, readiness: float) -> 'ReadinessLevel':
        """Get level from readiness percentage"""
        for level in cls:
            if level.min_threshold <= readiness < level.max_threshold:
                return level
        return cls.WORKING if readiness >= 1.0 else cls.VISION


@dataclass
class FeatureStatus:
    """Status tracking for individual features"""
    name: str
    readiness: float  # 0.0 to 1.0
    enabled: bool
    level: ReadinessLevel
    description: str
    integration_path: List[str]
    activation_criteria: List[Dict[str, Any]]
    last_updated: str
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['level'] = self.level.name
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureStatus':
        """Create from dictionary"""
        data['level'] = ReadinessLevel[data['level']]
        return cls(**data)


class FeatureReadinessTracker:
    """
    Central tracker for all feature readiness levels.
    Manages progressive activation and provides metrics.
    """
    
    DEFAULT_FEATURES = {
        'poml_consciousness': {
            'description': 'POML-based consciousness system',
            'readiness': 0.6,
            'integration_path': [
                'Connect templates to execution',
                'Implement memory persistence',
                'Full Ollama integration'
            ],
            'activation_criteria': [
                {'name': 'Templates load', 'completed': True},
                {'name': 'Executes commands', 'completed': False},
                {'name': 'Maintains context', 'completed': False}
            ]
        },
        'data_trinity': {
            'description': 'Three-database storage system',
            'readiness': 0.4,
            'integration_path': [
                'Migrate SimpleStore to DuckDB',
                'Add ChromaDB semantic layer',
                'Integrate Kùzu graphs'
            ],
            'activation_criteria': [
                {'name': 'DuckDB connected', 'completed': False},
                {'name': 'Data persists', 'completed': False},
                {'name': 'All three active', 'completed': False}
            ]
        },
        'tui_interface': {
            'description': 'Terminal user interface',
            'readiness': 0.7,
            'integration_path': [
                'Connect to backend',
                'Real-time updates',
                'Error display'
            ],
            'activation_criteria': [
                {'name': 'Interface renders', 'completed': True},
                {'name': 'Backend connected', 'completed': False},
                {'name': 'Updates real-time', 'completed': False}
            ]
        },
        'voice_interface': {
            'description': 'Voice interaction system',
            'readiness': 0.2,
            'integration_path': [
                'Basic STT with Whisper',
                'Simple TTS with Piper',
                'Voice command routing'
            ],
            'activation_criteria': [
                {'name': 'STT working', 'completed': False},
                {'name': 'TTS working', 'completed': False},
                {'name': 'Commands execute', 'completed': False}
            ]
        },
        'learning_system': {
            'description': 'Adaptive learning and preferences',
            'readiness': 0.45,
            'integration_path': [
                'Connect to persistence',
                'Pattern matching',
                'Adaptive responses'
            ],
            'activation_criteria': [
                {'name': 'Preferences saved', 'completed': True},
                {'name': 'Patterns recognized', 'completed': False},
                {'name': 'Adapts responses', 'completed': False}
            ]
        },
        'error_intelligence': {
            'description': 'Smart error handling and education',
            'readiness': 0.8,
            'integration_path': [
                'AST analysis',
                'Auto-fix execution',
                'Pattern learning'
            ],
            'activation_criteria': [
                {'name': 'Translates errors', 'completed': True},
                {'name': 'Suggests fixes', 'completed': True},
                {'name': 'Auto-fixes', 'completed': False}
            ]
        },
        'native_api': {
            'description': 'Native Python-Nix integration',
            'readiness': 0.5,
            'integration_path': [
                'Validate nixos-rebuild-ng',
                'Benchmark performance',
                'Full activation'
            ],
            'activation_criteria': [
                {'name': 'API accessible', 'completed': False},
                {'name': 'Performance validated', 'completed': False},
                {'name': 'Fully integrated', 'completed': False}
            ]
        },
        'plugin_ecosystem': {
            'description': 'Extensible plugin system',
            'readiness': 0.55,
            'integration_path': [
                'First working plugin',
                'API documentation',
                'Community template'
            ],
            'activation_criteria': [
                {'name': 'Plugin loads', 'completed': True},
                {'name': 'Plugin executes', 'completed': False},
                {'name': 'Community ready', 'completed': False}
            ]
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize tracker with optional config path"""
        self.config_path = config_path or Path.home() / '.config' / 'luminous-nix' / 'feature_readiness.json'
        self.features: Dict[str, FeatureStatus] = {}
        self.load_or_initialize()
        
    def load_or_initialize(self):
        """Load existing readiness data or initialize defaults"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for name, feature_data in data.items():
                        self.features[name] = FeatureStatus.from_dict(feature_data)
                logger.info(f"Loaded {len(self.features)} feature statuses")
            except Exception as e:
                logger.error(f"Failed to load readiness data: {e}")
                self.initialize_defaults()
        else:
            self.initialize_defaults()
    
    def initialize_defaults(self):
        """Initialize with default feature set"""
        for name, config in self.DEFAULT_FEATURES.items():
            self.features[name] = FeatureStatus(
                name=name,
                readiness=config['readiness'],
                enabled=config['readiness'] >= 0.75,
                level=ReadinessLevel.from_readiness(config['readiness']),
                description=config['description'],
                integration_path=config['integration_path'],
                activation_criteria=config['activation_criteria'],
                last_updated=datetime.now().isoformat(),
                metrics={}
            )
        self.save()
    
    def save(self):
        """Save current readiness data"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {name: feature.to_dict() for name, feature in self.features.items()}
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_readiness(self, feature_name: str, delta: float = 0.0, 
                        absolute: Optional[float] = None) -> bool:
        """
        Update feature readiness level.
        
        Args:
            feature_name: Name of the feature
            delta: Relative change in readiness
            absolute: Absolute readiness value (overrides delta)
            
        Returns:
            True if feature became enabled
        """
        if feature_name not in self.features:
            logger.warning(f"Unknown feature: {feature_name}")
            return False
        
        feature = self.features[feature_name]
        old_readiness = feature.readiness
        
        if absolute is not None:
            feature.readiness = max(0.0, min(1.0, absolute))
        else:
            feature.readiness = max(0.0, min(1.0, feature.readiness + delta))
        
        # Update level and enabled status
        feature.level = ReadinessLevel.from_readiness(feature.readiness)
        was_enabled = feature.enabled
        feature.enabled = feature.readiness >= 0.75
        feature.last_updated = datetime.now().isoformat()
        
        # Log significant changes
        if feature.enabled and not was_enabled:
            logger.info(f"🎉 Feature '{feature_name}' is now ENABLED at {feature.readiness:.1%} readiness!")
        elif abs(old_readiness - feature.readiness) > 0.1:
            logger.info(f"Feature '{feature_name}' readiness: {old_readiness:.1%} → {feature.readiness:.1%}")
        
        self.save()
        return feature.enabled and not was_enabled
    
    def complete_criterion(self, feature_name: str, criterion_name: str) -> bool:
        """Mark an activation criterion as complete"""
        if feature_name not in self.features:
            return False
        
        feature = self.features[feature_name]
        for criterion in feature.activation_criteria:
            if criterion['name'] == criterion_name:
                if not criterion['completed']:
                    criterion['completed'] = True
                    # Increase readiness based on criteria completion
                    completed = sum(1 for c in feature.activation_criteria if c['completed'])
                    total = len(feature.activation_criteria)
                    target_readiness = completed / total
                    self.update_readiness(feature_name, absolute=max(feature.readiness, target_readiness))
                    logger.info(f"✅ Completed '{criterion_name}' for {feature_name}")
                    return True
        return False
    
    def get_status(self, feature_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of specific feature or all features"""
        if feature_name:
            if feature_name in self.features:
                return self.features[feature_name].to_dict()
            return {}
        
        # Overall system status
        total_readiness = sum(f.readiness for f in self.features.values())
        avg_readiness = total_readiness / len(self.features) if self.features else 0
        
        return {
            'overall_readiness': avg_readiness,
            'overall_level': ReadinessLevel.from_readiness(avg_readiness).name,
            'features': {name: self._feature_summary(feature) 
                        for name, feature in self.features.items()},
            'working_count': sum(1 for f in self.features.values() if f.level == ReadinessLevel.WORKING),
            'enabled_count': sum(1 for f in self.features.values() if f.enabled),
            'total_features': len(self.features)
        }
    
    def _feature_summary(self, feature: FeatureStatus) -> Dict[str, Any]:
        """Create summary for a feature"""
        completed_criteria = sum(1 for c in feature.activation_criteria if c['completed'])
        total_criteria = len(feature.activation_criteria)
        
        return {
            'readiness': feature.readiness,
            'level': feature.level.name,
            'icon': feature.level.icon,
            'enabled': feature.enabled,
            'description': feature.description,
            'progress': f"{completed_criteria}/{total_criteria} criteria",
            'next_step': next((step for step in feature.integration_path), None)
        }
    
    def get_progress_bar(self, width: int = 20) -> str:
        """Generate ASCII progress bar for overall readiness"""
        avg_readiness = self.get_status()['overall_readiness']
        filled = int(avg_readiness * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {avg_readiness:.1%}"
    
    def get_report(self) -> str:
        """Generate human-readable status report"""
        status = self.get_status()
        lines = [
            "═" * 50,
            "LUMINOUS NIX FEATURE READINESS REPORT",
            "═" * 50,
            f"Overall System: {self.get_progress_bar()}",
            f"Level: {status['overall_level']} | Enabled: {status['enabled_count']}/{status['total_features']}",
            "",
            "Feature Status:",
            "-" * 50
        ]
        
        for name, summary in status['features'].items():
            lines.append(
                f"{summary['icon']} {name:20} {summary['readiness']:>5.1%} "
                f"{'[ENABLED]' if summary['enabled'] else '[DISABLED]':>10} "
                f"{summary['progress']:>15}"
            )
        
        lines.extend([
            "-" * 50,
            "",
            "Next Integration Steps:",
        ])
        
        for name, feature in self.features.items():
            if feature.readiness < 1.0:
                next_step = feature.integration_path[0] if feature.integration_path else "Complete"
                lines.append(f"  • {name}: {next_step}")
        
        return "\\n".join(lines)


# Feature flag decorator for progressive activation
def feature_flag(feature_name: str, fallback: Optional[Callable] = None):
    """
    Decorator for feature flag controlled functions.
    
    Args:
        feature_name: Name of the feature to check
        fallback: Optional fallback function if feature is disabled
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracker = FeatureReadinessTracker()
            feature = tracker.features.get(feature_name)
            
            if feature and feature.enabled:
                # Feature is enabled, execute normally
                return func(*args, **kwargs)
            elif fallback:
                # Use fallback function
                logger.debug(f"Feature '{feature_name}' disabled, using fallback")
                return fallback(*args, **kwargs)
            else:
                # Return None or raise based on context
                logger.warning(f"Feature '{feature_name}' is not enabled (readiness: {feature.readiness if feature else 0:.1%})")
                return None
        
        # Add metadata for introspection
        wrapper.feature_name = feature_name
        wrapper.is_feature_flagged = True
        
        return wrapper
    return decorator


# Global tracker instance
_tracker = None

def get_tracker() -> FeatureReadinessTracker:
    """Get or create global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = FeatureReadinessTracker()
    return _tracker


# Convenience functions
def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    tracker = get_tracker()
    feature = tracker.features.get(feature_name)
    return feature.enabled if feature else False


def get_feature_readiness(feature_name: str) -> float:
    """Get readiness level of a feature"""
    tracker = get_tracker()
    feature = tracker.features.get(feature_name)
    return feature.readiness if feature else 0.0


def update_feature_readiness(feature_name: str, delta: float = 0.0, 
                            absolute: Optional[float] = None) -> bool:
    """Update feature readiness"""
    tracker = get_tracker()
    return tracker.update_readiness(feature_name, delta, absolute)


def print_readiness_report():
    """Print current readiness report to console"""
    tracker = get_tracker()
    print(tracker.get_report())