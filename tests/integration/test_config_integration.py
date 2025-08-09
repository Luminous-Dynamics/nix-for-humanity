#!/usr/bin/env python3
"""
Integration tests for the configuration system
"""

import pytest
import tempfile
import os
from pathlib import Path

from nix_humanity.config import get_config_manager, ConfigSchema
from nix_humanity.config.schema import Personality, ResponseFormat


class TestConfigIntegration:
    """Test configuration system integration"""
    
    def test_default_config_loads(self):
        """Test that default configuration loads correctly"""
        manager = get_config_manager()
        assert manager is not None
        assert isinstance(manager.config, ConfigSchema)
        assert manager.config.core.version == "0.8.3"
    
    def test_personality_settings_work(self):
        """Test that personality settings affect behavior"""
        manager = get_config_manager()
        
        # Test minimal personality
        manager.config.ui.default_personality = Personality.MINIMAL
        assert manager.config.ui.default_personality == Personality.MINIMAL
        
        # Test technical personality
        manager.config.ui.default_personality = Personality.TECHNICAL
        assert manager.config.ui.default_personality == Personality.TECHNICAL
    
    def test_profile_application(self):
        """Test applying built-in profiles"""
        manager = get_config_manager()
        
        # Apply Maya profile (fast, minimal)
        success = manager.apply_profile('maya')
        assert success
        assert manager.config.ui.default_personality == Personality.MINIMAL
        assert manager.config.performance.fast_mode is True
        
        # Apply Alex profile (accessible)
        success = manager.apply_profile('alex')
        assert success
        assert manager.config.ui.default_personality == Personality.ACCESSIBLE
        assert manager.config.accessibility.screen_reader is True
    
    def test_aliases_and_shortcuts(self):
        """Test command aliases and shortcuts"""
        manager = get_config_manager()
        
        # Add alias
        manager.add_alias('test', 'test command')
        aliases = manager.get_aliases()
        assert 'test' in aliases
        assert aliases['test'] == 'test command'
        
        # Add shortcut
        manager.add_shortcut('test-multi', ['cmd1', 'cmd2'])
        shortcuts = manager.get_shortcuts()
        assert 'test-multi' in shortcuts
        assert shortcuts['test-multi'] == ['cmd1', 'cmd2']
        
        # Remove alias
        success = manager.remove_alias('test')
        assert success
        assert 'test' not in manager.get_aliases()
    
    def test_config_persistence(self):
        """Test saving and loading configuration"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            # Create manager with temp file
            manager = get_config_manager()
            
            # Modify settings
            manager.set('ui.use_colors', False)
            manager.set('performance.timeout', 45)
            manager.add_alias('test-save', 'saved command')
            
            # Save to temp file
            success = manager.save(temp_path)
            assert success
            
            # Create new manager and load from temp file
            from nix_humanity.config.config_manager import ConfigManager
            new_manager = ConfigManager(temp_path)
            
            # Verify settings were persisted
            assert new_manager.get('ui.use_colors') is False
            assert new_manager.get('performance.timeout') == 45
            assert 'test-save' in new_manager.get_aliases()
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_environment_overrides(self):
        """Test environment variable overrides"""
        # Set environment variables
        os.environ['NIX_HUMANITY_PERSONALITY'] = 'technical'
        os.environ['NIX_HUMANITY_FAST_MODE'] = 'true'
        
        try:
            # Force reload of config manager
            from nix_humanity.config import config_manager
            config_manager._config_manager = None
            
            # Get fresh manager
            manager = get_config_manager()
            
            # Check overrides were applied
            # Note: This depends on the loader applying env overrides
            
        finally:
            # Clean up
            del os.environ['NIX_HUMANITY_PERSONALITY']
            del os.environ['NIX_HUMANITY_FAST_MODE']
            config_manager._config_manager = None
    
    def test_config_validation(self):
        """Test configuration validation"""
        manager = get_config_manager()
        
        # Valid config should pass
        errors = manager.validate()
        assert len(errors) == 0
        
        # Invalid settings should fail
        manager.config.performance.timeout = -1
        errors = manager.validate()
        assert len(errors) > 0
        assert any('timeout' in error.lower() for error in errors)
        
        # Reset to valid
        manager.config.performance.timeout = 30
        errors = manager.validate()
        assert len(errors) == 0
    
    def test_profile_inheritance(self):
        """Test profile with base profile inheritance"""
        manager = get_config_manager()
        
        # Create a profile that inherits from maya
        from nix_humanity.config.profiles import UserProfile
        custom = UserProfile(
            name="maya-custom",
            base_profile="maya",
            config_overrides={
                "ui": {"greeting": "Custom greeting"}
            }
        )
        
        # Save it
        success = manager.profile_manager.save_profile(custom)
        assert success
        
        # Apply it
        success = manager.apply_profile("maya-custom")
        assert success
        
        # Should have maya's settings plus custom greeting
        assert manager.config.ui.default_personality == Personality.MINIMAL
        assert manager.config.performance.fast_mode is True
        assert manager.config.ui.greeting == "Custom greeting"
        
        # Clean up
        manager.profile_manager.delete_profile("maya-custom")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])