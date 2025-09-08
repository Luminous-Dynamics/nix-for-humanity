"""
User Preferences - Simple, honest configuration system

This replaces the misleading "configurable user preferences" with what we actually have:
simple user preferences that can be configured.
"""

from dataclasses import dataclass
from typing import Optional
import json
from pathlib import Path


@dataclass
class UserPreferences:
    """Simple user preferences - no AI, no adaptation, just settings"""
    
    # Display preferences
    verbose: bool = False  # Show detailed output
    show_tips: bool = True  # Show helpful tips
    use_colors: bool = True  # Use colored output
    
    # Interaction preferences
    mindful_mode: bool = False  # Add pauses for reflection
    confirm_actions: bool = True  # Ask before executing
    
    # Output style (simple choice, not "personality")
    output_style: str = "friendly"  # Options: minimal, friendly, detailed
    
    # Performance preferences
    enable_cache: bool = True  # Use caching for speed
    timeout_seconds: int = 30  # Command timeout
    
    def save(self, path: Optional[Path] = None):
        """Save preferences to file"""
        if path is None:
            path = Path.home() / ".config" / "luminous-nix" / "preferences.json"
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
    
    @classmethod
    def load(cls, path: Optional[Path] = None) -> 'UserPreferences':
        """Load preferences from file"""
        if path is None:
            path = Path.home() / ".config" / "luminous-nix" / "preferences.json"
        
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                return cls(**data)
        
        return cls()  # Return defaults if no file exists
    
    def get_response_style(self) -> dict:
        """Get response templates based on output style"""
        styles = {
            "minimal": {
                "success": "Done.",
                "error": "Error: {error}",
                "confirm": "Continue?",
                "working": "..."
            },
            "friendly": {
                "success": "All done!",
                "error": "Oh no, something went wrong: {error}",
                "confirm": "Shall I proceed?",
                "working": "Working on it..."
            },
            "detailed": {
                "success": "Task completed successfully. Here's what happened:",
                "error": "An error occurred. Details: {error}",
                "confirm": "Please confirm you want to proceed with this action.",
                "working": "Processing your request. This may take a moment..."
            }
        }
        
        return styles.get(self.output_style, styles["friendly"])


# Global preferences instance
_preferences = None


def get_preferences() -> UserPreferences:
    """Get or create the global preferences"""
    global _preferences
    if _preferences is None:
        _preferences = UserPreferences.load()
    return _preferences


def set_preference(key: str, value):
    """Set a single preference"""
    prefs = get_preferences()
    if hasattr(prefs, key):
        setattr(prefs, key, value)
        prefs.save()
        return True
    return False


def reset_preferences():
    """Reset to default preferences"""
    global _preferences
    _preferences = UserPreferences()
    _preferences.save()
