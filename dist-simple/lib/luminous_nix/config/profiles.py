"""
from typing import List, Dict, Optional
User Profile Management

Manages user profiles and persona-specific configurations.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

from .schema import ConfigSchema, Personality, ResponseFormat
from .loader import ConfigLoader


@dataclass
class UserProfile:
    """Represents a user profile with specific configuration overrides"""
    name: str
    description: str = ""
    base_profile: Optional[str] = None  # Inherit from another profile
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: Optional[str] = None
    last_used: Optional[str] = None
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "base_profile": self.base_profile,
            "config_overrides": self.config_overrides,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "usage_count": self.usage_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            base_profile=data.get("base_profile"),
            config_overrides=data.get("config_overrides", {}),
            created_at=data.get("created_at"),
            last_used=data.get("last_used"),
            usage_count=data.get("usage_count", 0),
        )


class ProfileManager:
    """Manages user profiles and persona configurations"""
    
    # Built-in personas
    BUILT_IN_PROFILES = {
        "grandma-rose": UserProfile(
            name="grandma-rose",
            description="Voice-first, patient, encouraging interface for Grandma Rose (75)",
            config_overrides={
                "ui": {
                    "default_personality": "encouraging",
                    "simple_language": True,
                    "patience_mode": True,
                    "greeting": "Hello dear! How can I help you today?",
                    "farewell": "Take care, dear!",
                },
                "accessibility": {
                    "large_text": True,
                    "simple_language": True,
                    "extra_confirmations": True,
                    "patient_mode": True,
                },
                "voice": {
                    "enabled": True,
                    "voice_feedback": True,
                    "speed": 0.9,
                },
                "performance": {
                    "fast_mode": False,  # Accuracy over speed
                },
            }
        ),
        
        "maya": UserProfile(
            name="maya",
            description="Lightning-fast, minimal interface for Maya (16, ADHD)",
            config_overrides={
                "ui": {
                    "default_personality": "minimal",
                    "response_format": "plain",
                    "show_commands": False,
                    "progress_indicators": False,
                    "greeting": "Ready.",
                    "farewell": "Done.",
                },
                "performance": {
                    "fast_mode": True,
                    "timeout": 10,
                },
                "nlp": {
                    "confidence_threshold": 0.6,  # Lower threshold for speed
                },
            }
        ),
        
        "alex": UserProfile(
            name="alex",
            description="Screen-reader optimized interface for Alex (28, blind developer)",
            config_overrides={
                "ui": {
                    "default_personality": "accessible",
                    "response_format": "structured",
                    "use_colors": False,
                },
                "accessibility": {
                    "screen_reader": True,
                    "structured_output": True,
                    "keyboard_only": True,
                    "consistent_terminology": True,
                },
                "voice": {
                    "enabled": True,
                    "voice_feedback": True,
                },
                "development": {
                    "show_all_details": True,
                },
            }
        ),
        
        "dr-sarah": UserProfile(
            name="dr-sarah",
            description="Precise, technical interface for Dr. Sarah (35, researcher)",
            config_overrides={
                "ui": {
                    "default_personality": "technical",
                    "response_format": "structured",
                    "show_commands": True,
                },
                "development": {
                    "debug_mode": True,
                    "api_logging": True,
                },
                "performance": {
                    "fast_mode": False,  # Accuracy over speed
                },
            }
        ),
        
        "carlos": UserProfile(
            name="carlos",
            description="Learning-focused interface for Carlos (52, career switcher)",
            config_overrides={
                "ui": {
                    "default_personality": "encouraging",
                    "show_commands": True,
                    "confirm_actions": True,
                },
                "learning": {
                    "enabled": True,
                    "personal_preferences": True,
                    "error_recovery": True,
                },
                "nlp": {
                    "context_memory": 20,
                    "learning_enabled": True,
                },
            }
        ),
        
        "viktor": UserProfile(
            name="viktor",
            description="Simple, clear interface for Viktor (67, English second language)",
            config_overrides={
                "ui": {
                    "default_personality": "friendly",
                    "simple_language": True,
                    "error_prefix": "Sorry, there was a problem:",
                    "success_prefix": "Success!",
                },
                "accessibility": {
                    "simple_language": True,
                    "consistent_terminology": True,
                },
                "nlp": {
                    "typo_correction": True,
                    "fuzzy_match_threshold": 0.7,
                },
            }
        ),
        
        "david": UserProfile(
            name="david",
            description="Efficient interface for David (42, tired sys admin)",
            config_overrides={
                "ui": {
                    "default_personality": "minimal",
                    "response_format": "plain",
                    "confirm_actions": False,  # Trust the user
                },
                "performance": {
                    "fast_mode": True,
                    "cache_responses": True,
                    "prefetch_common": True,
                },
                "aliases": {
                    "aliases": {
                        "u": "update",
                        "i": "install",
                        "s": "search",
                        "gc": "collect garbage",
                    },
                },
            }
        ),
        
        "priya": UserProfile(
            name="priya",
            description="Quick, efficient interface for Priya (34, developer)",
            config_overrides={
                "ui": {
                    "default_personality": "technical",
                    "response_format": "structured",
                    "show_commands": True,
                },
                "performance": {
                    "fast_mode": True,
                    "parallel_processing": True,
                },
                "development": {
                    "api_logging": True,
                },
            }
        ),
        
        "luna": UserProfile(
            name="luna",
            description="Structured, predictable interface for Luna (14, autistic)",
            config_overrides={
                "ui": {
                    "default_personality": "friendly",
                    "response_format": "structured",
                    "confirm_actions": True,
                },
                "accessibility": {
                    "consistent_terminology": True,
                    "structured_output": True,
                    "reduce_motion": True,
                },
                "performance": {
                    "fast_mode": False,  # Consistency over speed
                },
            }
        ),
        
        "jamie": UserProfile(
            name="jamie",
            description="Privacy-focused interface for Jamie (19, privacy advocate)",
            config_overrides={
                "privacy": {
                    "data_collection": "none",
                    "share_anonymous_stats": False,
                    "local_only": True,
                    "encrypt_data": True,
                    "auto_cleanup": True,
                    "log_retention_days": 7,
                },
                "learning": {
                    "privacy_mode": "strict",
                    "retention_days": 30,
                },
                "ui": {
                    "default_personality": "technical",
                },
            }
        ),
    }
    
    def __init__(self, profiles_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        if profiles_dir:
            self.profiles_dir = Path(profiles_dir)
        else:
            self.profiles_dir = Path.home() / ".config" / "nix-for-humanity" / "profiles"
            
        # Ensure profiles directory exists
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Load custom profiles
        self.custom_profiles = self._load_custom_profiles()
        
    def get_profile(self, name: str) -> Optional[UserProfile]:
        """Get a profile by name"""
        # Check built-in profiles first
        if name in self.BUILT_IN_PROFILES:
            return self.BUILT_IN_PROFILES[name]
            
        # Check custom profiles
        if name in self.custom_profiles:
            return self.custom_profiles[name]
            
        return None
    
    def list_profiles(self) -> List[str]:
        """List all available profile names"""
        built_in = list(self.BUILT_IN_PROFILES.keys())
        custom = list(self.custom_profiles.keys())
        return sorted(built_in + custom)
    
    def save_profile(self, profile: UserProfile) -> bool:
        """Save a custom profile"""
        try:
            # Don't overwrite built-in profiles
            if profile.name in self.BUILT_IN_PROFILES:
                self.logger.error(f"Cannot overwrite built-in profile: {profile.name}")
                return False
                
            # Save to file
            profile_path = self.profiles_dir / f"{profile.name}.json"
            with open(profile_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
                
            # Update cache
            self.custom_profiles[profile.name] = profile
            
            self.logger.info(f"Saved profile: {profile.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving profile: {e}")
            return False
    
    def delete_profile(self, name: str) -> bool:
        """Delete a custom profile"""
        try:
            # Can't delete built-in profiles
            if name in self.BUILT_IN_PROFILES:
                self.logger.error(f"Cannot delete built-in profile: {name}")
                return False
                
            # Delete file
            profile_path = self.profiles_dir / f"{name}.json"
            if profile_path.exists():
                profile_path.unlink()
                
            # Remove from cache
            if name in self.custom_profiles:
                del self.custom_profiles[name]
                
            self.logger.info(f"Deleted profile: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting profile: {e}")
            return False
    
    def apply_profile(self, base_config: ConfigSchema, profile_name: str) -> ConfigSchema:
        """Apply a profile to a base configuration"""
        profile = self.get_profile(profile_name)
        if not profile:
            self.logger.warning(f"Profile not found: {profile_name}")
            return base_config
            
        # Apply profile hierarchy if there's a base profile
        if profile.base_profile:
            base_config = self.apply_profile(base_config, profile.base_profile)
            
        # Apply overrides
        config_dict = base_config.to_dict()
        config_dict = self._apply_overrides(config_dict, profile.config_overrides)
        
        # Create new config with profile applied
        new_config = ConfigSchema.from_dict(config_dict)
        new_config.profile_name = profile_name
        
        # Update profile usage
        from datetime import datetime
        profile.last_used = datetime.now().isoformat()
        profile.usage_count += 1
        
        # Save updated profile if it's custom
        if profile_name not in self.BUILT_IN_PROFILES:
            self.save_profile(profile)
            
        return new_config
    
    def create_profile_from_config(self, name: str, config: ConfigSchema, 
                                  description: str = "") -> UserProfile:
        """Create a new profile from current configuration"""
        # Get the differences from default
        default_config = ConfigSchema()
        overrides = self._get_config_diff(default_config.to_dict(), config.to_dict())
        
        from datetime import datetime
        profile = UserProfile(
            name=name,
            description=description,
            config_overrides=overrides,
            created_at=datetime.now().isoformat(),
        )
        
        return profile
    
    def _load_custom_profiles(self) -> Dict[str, UserProfile]:
        """Load custom profiles from disk"""
        profiles = {}
        
        try:
            for profile_file in self.profiles_dir.glob("*.json"):
                try:
                    with open(profile_file, 'r') as f:
                        data = json.load(f)
                        profile = UserProfile.from_dict(data)
                        profiles[profile.name] = profile
                except Exception as e:
                    self.logger.error(f"Error loading profile {profile_file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error loading custom profiles: {e}")
            
        return profiles
    
    def _apply_overrides(self, base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Apply configuration overrides"""
        result = base.copy()
        
        for key, value in overrides.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                result[key] = self._apply_overrides(result[key], value)
            else:
                # Override value
                result[key] = value
                
        return result
    
    def _get_config_diff(self, base: Dict[str, Any], modified: Dict[str, Any]) -> Dict[str, Any]:
        """Get differences between two configurations"""
        diff = {}
        
        for key, value in modified.items():
            if key not in base:
                diff[key] = value
            elif isinstance(value, dict) and isinstance(base.get(key), dict):
                # Recursive diff for nested dicts
                nested_diff = self._get_config_diff(base[key], value)
                if nested_diff:
                    diff[key] = nested_diff
            elif value != base.get(key):
                diff[key] = value
                
        return diff