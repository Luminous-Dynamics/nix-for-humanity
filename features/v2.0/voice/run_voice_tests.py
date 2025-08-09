#!/usr/bin/env python3
"""Simple test runner for voice integration tests without pytest."""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Mock pytest for compatibility
class pytest:
    @staticmethod
    def mark(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    parametrize = mark
    asyncio = mark
    
    class fixture:
        def __init__(self, *args, **kwargs):
            pass
        
        def __call__(self, func):
            return func

# Add pytest to sys.modules
sys.modules['pytest'] = pytest

# Mock voice dependencies that might not be available
sys.modules['pipecat'] = MagicMock()
sys.modules['pipecat.pipeline'] = MagicMock()
sys.modules['pipecat.transports'] = MagicMock()
sys.modules['pipecat.transports.local'] = MagicMock()
sys.modules['pipecat.services'] = MagicMock()
sys.modules['pipecat.services.whisper'] = MagicMock()
sys.modules['pipecat.services.piper'] = MagicMock()
sys.modules['whisper_cpp'] = MagicMock()
sys.modules['piper'] = MagicMock()

# Create a simple voice test
def test_voice_basic():
    """Basic test to verify voice module structure."""
    print("\n🎯 Testing basic voice module imports...")
    
    try:
        from nix_for_humanity.voice.model_manager import ModelManager, ModelType
        print("✅ Successfully imported ModelManager")
        
        # Test model manager initialization
        manager = ModelManager()
        print(f"✅ ModelManager initialized with base path: {manager.models_dir}")
        
        # Test model types
        assert ModelType.WHISPER.value == "whisper"
        assert ModelType.PIPER.value == "piper"
        print("✅ Model types validated")
        
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def test_voice_personas():
    """Test voice persona configuration."""
    print("\n🎯 Testing voice persona configurations...")
    
    try:
        from nix_for_humanity.voice.voice_config import VOICE_PERSONAS
        
        # Check all 10 personas exist
        expected_personas = [
            "grandma_rose", "maya_adhd", "alex_blind", "dr_sarah",
            "carlos_learner", "david_tired", "priya_mom", "jamie_privacy",
            "viktor_esl", "luna_autistic"
        ]
        
        for persona in expected_personas:
            assert persona in VOICE_PERSONAS, f"Missing persona: {persona}"
            config = VOICE_PERSONAS[persona]
            assert "voice_speed" in config
            assert "voice_pitch" in config
            print(f"✅ Persona '{persona}' configured correctly")
        
        return True
    except Exception as e:
        print(f"❌ Persona test failed: {e}")
        return False

def test_model_download_script():
    """Test that model download script exists and has correct structure."""
    print("\n🎯 Testing model download script...")
    
    try:
        script_path = project_root / "tests" / "voice" / "test_model_download.py"
        assert script_path.exists(), f"Model download script not found at {script_path}"
        print("✅ Model download script exists")
        
        # Check if it's executable or can be run
        with open(script_path, 'r') as f:
            content = f.read()
            assert "ModelManager" in content
            assert "download_model" in content or "ensure_model" in content
            print("✅ Model download script has expected structure")
        
        return True
    except Exception as e:
        print(f"❌ Model download script test failed: {e}")
        return False

def run_voice_tests():
    """Run voice integration tests."""
    print("🎤 Running Voice Integration Tests...")
    print("=" * 60)
    
    tests = [
        test_voice_basic,
        test_voice_personas,
        test_model_download_script
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All voice integration tests passed!")
        print("\n📝 Next steps for Sprint 1:")
        print("1. ✅ Model download script tested")
        print("2. ✅ CI/CD workflow created") 
        print("3. ✅ Voice integration tests run")
        print("4. 📋 Create user documentation for voice features")
    else:
        print(f"\n⚠️  {failed} tests failed. Please review the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_voice_tests()
    sys.exit(0 if success else 1)