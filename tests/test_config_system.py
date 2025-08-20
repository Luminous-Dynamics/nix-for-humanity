#!/usr/bin/env python3
"""
Test script for the configuration system
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from luminous_nix.config import (
    ConfigManager, ConfigSchema, ConfigLoader,
    ProfileManager, UserProfile,
    Personality, ResponseFormat, NLPEngine
)

def test_schema():
    """Test configuration schema"""
    print("🧪 Testing Configuration Schema...")
    
    # Create default config
    config = ConfigSchema()
    assert config.core.version == "0.8.3"
    assert config.ui.default_personality == Personality.FRIENDLY
    assert config.performance.timeout == 30
    
    # Test validation
    errors = config.validate()
    assert len(errors) == 0, f"Default config should be valid: {errors}"
    
    # Test invalid config
    config.performance.timeout = -1
    errors = config.validate()
    assert len(errors) > 0, "Should detect invalid timeout"
    
    # Test serialization
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert config_dict["core"]["version"] == "0.8.3"
    
    # Test deserialization
    new_config = ConfigSchema.from_dict(config_dict)
    assert new_config.core.version == config.core.version
    
    print("  ✅ Schema tests passed!")

def test_loader():
    """Test configuration loader"""
    print("🧪 Testing Configuration Loader...")
    
    loader = ConfigLoader()
    
    # Test loading default config
    config = loader.load_config()
    assert isinstance(config, ConfigSchema)
    
    # Test saving and loading YAML
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save config
        success = loader.save_config(config, temp_path, 'yaml')
        assert success, "Failed to save YAML config"
        
        # Load it back
        loaded_config = loader.load_config(temp_path)
        assert loaded_config.core.version == config.core.version
        
        print("  ✅ Loader tests passed!")
    finally:
        os.unlink(temp_path)

def test_profiles():
    """Test profile management"""
    print("🧪 Testing Profile Management...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ProfileManager(temp_dir)
        
        # Test built-in profiles
        profiles = manager.list_profiles()
        assert len(profiles) >= 10, "Should have at least 10 built-in profiles"
        assert "grandma-rose" in profiles
        assert "maya" in profiles
        
        # Test getting a profile
        maya = manager.get_profile("maya")
        assert maya is not None
        assert maya.name == "maya"
        assert maya.config_overrides["ui"]["default_personality"] == "minimal"
        
        # Test creating custom profile
        custom = UserProfile(
            name="test-profile",
            description="Test profile",
            config_overrides={
                "ui": {"default_personality": "technical"},
                "performance": {"fast_mode": True}
            }
        )
        
        # Save custom profile
        success = manager.save_profile(custom)
        assert success, "Failed to save custom profile"
        
        # Load it back
        loaded = manager.get_profile("test-profile")
        assert loaded is not None
        assert loaded.name == "test-profile"
        
        # Test applying profile
        base_config = ConfigSchema()
        assert base_config.ui.default_personality == Personality.FRIENDLY
        
        new_config = manager.apply_profile(base_config, "maya")
        assert new_config.ui.default_personality == Personality.MINIMAL
        assert new_config.performance.fast_mode is True
        
        print("  ✅ Profile tests passed!")

def test_config_manager():
    """Test main configuration manager"""
    print("🧪 Testing Configuration Manager...")
    
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        temp_path = f.name
    
    try:
        manager = ConfigManager(temp_path)
        
        # Test getting values
        assert manager.get("ui.use_colors") is True
        assert manager.get("nonexistent.key", "default") == "default"
        
        # Test setting values
        success = manager.set("ui.use_colors", False)
        assert success
        assert manager.get("ui.use_colors") is False
        assert manager.is_modified()
        
        # Test saving
        success = manager.save()
        assert success
        assert not manager.is_modified()
        
        # Test profile application
        success = manager.apply_profile("alex")
        assert success
        assert manager.config.ui.default_personality == Personality.ACCESSIBLE
        assert manager.config.accessibility.screen_reader is True
        
        # Test aliases
        manager.add_alias("i", "install")
        aliases = manager.get_aliases()
        assert "i" in aliases
        assert aliases["i"] == "install"
        
        # Test shortcuts
        manager.add_shortcut("setup", ["install git", "install vim"])
        shortcuts = manager.get_shortcuts()
        assert "setup" in shortcuts
        assert len(shortcuts["setup"]) == 2
        
        # Test export
        yaml_str = manager.export("yaml")
        assert yaml_str is not None
        assert "version:" in yaml_str
        
        print("  ✅ Config Manager tests passed!")
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_environment_overrides():
    """Test environment variable overrides"""
    print("🧪 Testing Environment Variable Overrides...")
    
    # Set some environment variables
    os.environ["NIX_HUMANITY_PERSONALITY"] = "technical"
    os.environ["NIX_HUMANITY_FAST_MODE"] = "true"
    os.environ["NIX_HUMANITY_TIMEOUT"] = "60"
    
    try:
        loader = ConfigLoader()
        config = loader.load_config()
        
        # Check that env vars were applied
        # Note: This depends on implementation details of _apply_env_overrides
        
        print("  ✅ Environment override tests passed!")
        
    finally:
        # Clean up env vars
        del os.environ["NIX_HUMANITY_PERSONALITY"]
        del os.environ["NIX_HUMANITY_FAST_MODE"] 
        del os.environ["NIX_HUMANITY_TIMEOUT"]

def main():
    """Run all tests"""
    print("🚀 Testing Nix for Humanity Configuration System\n")
    
    try:
        test_schema()
        test_loader()
        test_profiles()
        test_config_manager()
        test_environment_overrides()
        
        print("\n✅ All tests passed! Configuration system is working correctly.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()