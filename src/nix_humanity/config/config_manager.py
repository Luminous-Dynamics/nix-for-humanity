"""
from typing import Dict, List, Optional
Main Configuration Manager

Provides the central interface for configuration management in Nix for Humanity.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading

from .schema import ConfigSchema
from .loader import ConfigLoader
from .profiles import ProfileManager, UserProfile


class ConfigManager:
    """Central configuration management for Nix for Humanity"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # Initialize components
        self.loader = ConfigLoader()
        self.profile_manager = ProfileManager()
        
        # Load configuration
        self.config_path = config_path
        self.config = self._load_initial_config()
        
        # Track if config has been modified
        self._modified = False
        
    def _load_initial_config(self) -> ConfigSchema:
        """Load initial configuration"""
        # Check for legacy config migration
        if self.loader.migrate_legacy_config():
            self.logger.info("Migrated legacy configuration")
            
        # Load config
        config = self.loader.load_config(self.config_path)
        
        # Apply profile if specified via environment
        profile_name = os.getenv("NIX_HUMANITY_PROFILE")
        if profile_name:
            config = self.profile_manager.apply_profile(config, profile_name)
            
        return config
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated path"""
        with self._lock:
            parts = path.split('.')
            value = self.config
            
            try:
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    elif isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return default
                        
                return value
                
            except (AttributeError, KeyError, TypeError):
                return default
    
    def set(self, path: str, value: Any) -> bool:
        """Set a configuration value by dot-separated path"""
        with self._lock:
            parts = path.split('.')
            
            if not parts:
                return False
                
            # Navigate to the parent object
            target = self.config
            for part in parts[:-1]:
                if hasattr(target, part):
                    target = getattr(target, part)
                else:
                    self.logger.error(f"Invalid configuration path: {path}")
                    return False
                    
            # Set the value
            final_key = parts[-1]
            if hasattr(target, final_key):
                setattr(target, final_key, value)
                self._modified = True
                return True
            else:
                self.logger.error(f"Invalid configuration key: {final_key}")
                return False
    
    def reload(self) -> bool:
        """Reload configuration from disk"""
        try:
            with self._lock:
                self.config = self._load_initial_config()
                self._modified = False
                self.logger.info("Configuration reloaded")
                return True
        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")
            return False
    
    def save(self, path: Optional[str] = None) -> bool:
        """Save current configuration to disk"""
        with self._lock:
            save_path = path or self.config_path
            
            if not save_path:
                # Use default user config location
                save_path = os.path.expanduser("~/.config/nix-for-humanity/config.yaml")
                
            try:
                # Update timestamp
                self.config.last_modified = datetime.now().isoformat()
                
                # Save
                success = self.loader.save_config(self.config, save_path)
                if success:
                    self._modified = False
                    
                return success
                
            except Exception as e:
                self.logger.error(f"Error saving configuration: {e}")
                return False
    
    def apply_profile(self, profile_name: str) -> bool:
        """Apply a user profile to current configuration"""
        try:
            with self._lock:
                new_config = self.profile_manager.apply_profile(self.config, profile_name)
                self.config = new_config
                self._modified = True
                self.logger.info(f"Applied profile: {profile_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error applying profile: {e}")
            return False
    
    def save_as_profile(self, name: str, description: str = "") -> bool:
        """Save current configuration as a new profile"""
        try:
            profile = self.profile_manager.create_profile_from_config(
                name, self.config, description
            )
            return self.profile_manager.save_profile(profile)
            
        except Exception as e:
            self.logger.error(f"Error saving profile: {e}")
            return False
    
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        return self.profile_manager.list_profiles()
    
    def get_profile(self, name: str) -> Optional[UserProfile]:
        """Get a specific profile"""
        return self.profile_manager.get_profile(name)
    
    def validate(self) -> List[str]:
        """Validate current configuration"""
        with self._lock:
            return self.config.validate()
    
    def is_modified(self) -> bool:
        """Check if configuration has been modified"""
        return self._modified
    
    def reset(self) -> bool:
        """Reset configuration to defaults"""
        try:
            with self._lock:
                self.config = ConfigSchema()
                self._modified = True
                self.logger.info("Configuration reset to defaults")
                return True
                
        except Exception as e:
            self.logger.error(f"Error resetting configuration: {e}")
            return False
    
    def export(self, format: str = "yaml") -> Optional[str]:
        """Export configuration as string"""
        try:
            import yaml
            import json
            import toml
            
            data = self.config.to_dict()
            
            if format == "yaml":
                return yaml.dump(data, default_flow_style=False, sort_keys=False)
            elif format == "json":
                return json.dumps(data, indent=2)
            elif format == "toml":
                return toml.dumps(data)
            else:
                self.logger.error(f"Unknown export format: {format}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return None
    
    def import_config(self, data: str, format: str = "yaml") -> bool:
        """Import configuration from string"""
        try:
            import yaml
            import json
            import toml
            
            # Parse based on format
            if format == "yaml":
                parsed = yaml.safe_load(data)
            elif format == "json":
                parsed = json.loads(data)
            elif format == "toml":
                parsed = toml.loads(data)
            else:
                self.logger.error(f"Unknown import format: {format}")
                return False
                
            # Create new config
            with self._lock:
                self.config = ConfigSchema.from_dict(parsed)
                self._modified = True
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False
    
    def get_aliases(self) -> Dict[str, str]:
        """Get command aliases"""
        return self.config.aliases.aliases
    
    def get_shortcuts(self) -> Dict[str, List[str]]:
        """Get command shortcuts"""
        return self.config.aliases.shortcuts
    
    def add_alias(self, alias: str, command: str) -> bool:
        """Add a command alias"""
        with self._lock:
            self.config.aliases.aliases[alias] = command
            self._modified = True
            return True
    
    def add_shortcut(self, name: str, commands: List[str]) -> bool:
        """Add a command shortcut"""
        with self._lock:
            self.config.aliases.shortcuts[name] = commands
            self._modified = True
            return True
    
    def remove_alias(self, alias: str) -> bool:
        """Remove a command alias"""
        with self._lock:
            if alias in self.config.aliases.aliases:
                del self.config.aliases.aliases[alias]
                self._modified = True
                return True
            return False
    
    def remove_shortcut(self, name: str) -> bool:
        """Remove a command shortcut"""
        with self._lock:
            if name in self.config.aliases.shortcuts:
                del self.config.aliases.shortcuts[name]
                self._modified = True
                return True
            return False


# Global configuration instance
_config_manager: Optional[ConfigManager] = None
_config_lock = threading.Lock()


def get_config() -> ConfigSchema:
    """Get the global configuration"""
    global _config_manager
    
    with _config_lock:
        if _config_manager is None:
            _config_manager = ConfigManager()
            
        return _config_manager.config


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager"""
    global _config_manager
    
    with _config_lock:
        if _config_manager is None:
            _config_manager = ConfigManager()
            
        return _config_manager


def update_config(**kwargs) -> ConfigSchema:
    """Update global configuration with new values"""
    manager = get_config_manager()
    
    for key, value in kwargs.items():
        manager.set(key, value)
        
    return manager.config