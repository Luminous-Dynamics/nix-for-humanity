#!/usr/bin/env python3
"""
Test script to verify Error Intelligence and Configuration Management integrations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from luminous_nix.core.engine import NixForHumanityBackend
from luminous_nix.api.schema import Request
import json

def test_error_intelligence():
    """Test that Error Intelligence is working"""
    print("\n🧪 Testing Error Intelligence Integration...")
    
    engine = NixForHumanityBackend()
    
    # Test with a query that will likely cause an error
    request = Request(
        query="install nonexistent-package-xyz123",
        context={}
    )
    
    try:
        # This should trigger an error
        response = engine.process_request(request)
        
        if response.error:
            print("✅ Error caught and processed")
            print(f"   Error type: {response.error_details.get('type', 'unknown')}")
            
            # Check if we have intelligent suggestions
            if response.suggestions:
                print(f"✅ Error Intelligence provided {len(response.suggestions)} suggestions:")
                for i, suggestion in enumerate(response.suggestions[:3], 1):
                    print(f"   {i}. {suggestion}")
            else:
                print("⚠️  No intelligent suggestions provided")
                
            # Check for educational error message
            if response.error_details.get('explanation'):
                print("✅ Educational explanation provided")
            
            # Check for auto-fix availability
            if response.error_details.get('auto_fixable'):
                print("✅ Auto-fix available:", response.error_details.get('fix_command'))
        else:
            print("⚠️  Expected an error but got success")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

def test_config_management():
    """Test that Configuration Management is working"""
    print("\n🧪 Testing Configuration Management Integration...")
    
    engine = NixForHumanityBackend()
    
    # Test setting a configuration value
    print("   Testing setting configuration...")
    success = engine.update_setting('interface.verbosity', 'verbose')
    if success:
        print("✅ Configuration setting updated")
    else:
        print("❌ Failed to update configuration")
    
    # Test getting all settings
    print("   Testing getting all settings...")
    settings = engine.get_all_settings()
    if settings:
        print(f"✅ Retrieved {len(settings)} configuration sections")
        
        # Check if our setting was saved
        if 'interface' in settings:
            print("✅ Interface settings available")
            verbosity = settings.get('interface', {}).get('verbosity')
            if verbosity == 'verbose':
                print("✅ Setting persisted correctly")
            else:
                print(f"⚠️  Setting value unexpected: {verbosity}")
    else:
        print("❌ No settings retrieved")
    
    # Test configuration persistence
    print("   Testing configuration persistence...")
    if hasattr(engine, 'config_manager'):
        if engine.config_manager.is_modified():
            print("✅ Configuration marked as modified")
            
        # Try to save
        config_path = os.path.expanduser("~/.config/nix-for-humanity/test-config.yaml")
        if engine.config_manager.save(config_path):
            print(f"✅ Configuration saved to {config_path}")
            
            # Check if file exists
            if os.path.exists(config_path):
                print("✅ Configuration file created")
                # Clean up test file
                os.remove(config_path)
        else:
            print("⚠️  Could not save configuration")
    else:
        print("❌ Config manager not found on engine")

def test_user_preferences():
    """Test that user preferences are loaded and applied"""
    print("\n🧪 Testing User Preferences Loading...")
    
    engine = NixForHumanityBackend()
    
    # Check if preferences were loaded
    if hasattr(engine, '_load_user_preferences'):
        print("✅ User preferences loader exists")
        
        # Set a preference and check if it's applied
        engine.update_setting('backend.use_native_api', True)
        
        # Get settings to verify
        settings = engine.get_all_settings()
        if settings.get('backend', {}).get('use_native_api'):
            print("✅ Native API preference applied")
        else:
            print("⚠️  Native API preference not reflected")
    else:
        print("❌ User preferences loader not found")

def main():
    print("=" * 60)
    print("🔬 Integration Test Suite")
    print("=" * 60)
    
    # Test Error Intelligence
    test_error_intelligence()
    
    # Test Configuration Management
    test_config_management()
    
    # Test User Preferences
    test_user_preferences()
    
    print("\n" + "=" * 60)
    print("✨ Integration tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()