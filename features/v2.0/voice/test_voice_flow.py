#!/usr/bin/env python3
"""
Test Voice Flow End-to-End
==========================

Tests the complete voice flow from recording to response.
"""

import sys
import os
import asyncio
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'scripts'))

from voice_interface import VoiceInterface
from voice_nlp_integration import VoiceNLPBridge, UserProfile
from voice_demo_simple import SimpleVoiceDemo

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_components():
    """Test basic components are working"""
    print("🧪 Testing Voice Components")
    print("=" * 50)
    
    # Test 1: Voice Interface
    print("\n1. Testing Voice Interface...")
    voice = VoiceInterface()
    ok, message = voice.check_dependencies()
    if ok:
        print("✅ Voice interface ready")
    else:
        print(f"❌ Missing dependencies:\n{message}")
        return False
    
    # Test 2: NLP Bridge
    print("\n2. Testing NLP Bridge...")
    try:
        bridge = VoiceNLPBridge(UserProfile(name="Test User", technical_level="beginner"))
        print("✅ NLP Bridge initialized")
    except Exception as e:
        print(f"❌ NLP Bridge error: {e}")
        return False
    
    # Test 3: Knowledge Engine
    print("\n3. Testing Knowledge Engine...")
    try:
        from nix_knowledge_engine import NixOSKnowledgeEngine
        engine = NixOSKnowledgeEngine()
        
        # Test intent extraction
        intent = engine.extract_intent("install firefox")
        if intent['action'] == 'install_package':
            print("✅ Intent extraction working")
        else:
            print(f"❌ Intent extraction failed: {intent}")
            return False
    except Exception as e:
        print(f"❌ Knowledge engine error: {e}")
        return False
    
    return True


async def test_voice_processing():
    """Test voice processing pipeline"""
    print("\n🎤 Testing Voice Processing Pipeline")
    print("=" * 50)
    
    bridge = VoiceNLPBridge(UserProfile(name="Grandma Rose", technical_level="beginner"))
    
    # Test commands
    test_cases = [
        ("I need to check my email", "install_package"),
        ("My wife eye isn't working", "fix_wifi"),  # Test typo correction
        ("Update my computer", "update_system"),
    ]
    
    for voice_input, expected_action in test_cases:
        print(f"\n📝 Testing: '{voice_input}'")
        
        result = await bridge.process_voice_command(voice_input)
        command = result['command']
        
        print(f"   Processed: '{result['processed_text']}'")
        print(f"   Intent: {command.intent['action']}")
        print(f"   Needs confirmation: {result['needs_confirmation']}")
        
        if command.intent['action'] == expected_action:
            print("   ✅ Correct intent detected")
        else:
            print(f"   ❌ Wrong intent: expected {expected_action}")
        
        # Show response preview
        print(f"   Response preview: {command.response[:100]}...")


def test_simple_demo():
    """Test the simple demo mode"""
    print("\n🎭 Testing Simple Demo Mode")
    print("=" * 50)
    
    demo = SimpleVoiceDemo()
    
    # Test command processing
    test_inputs = [
        "open the internet",
        "I want to video call my grandkids",
        "update computer"
    ]
    
    for input_text in test_inputs:
        print(f"\n📝 Processing: '{input_text}'")
        result = demo.process_command(input_text)
        
        if result['success']:
            print("   ✅ Successfully processed")
            print(f"   Intent: {result['intent']['action']}")
            print(f"   Response preview: {result['response'][:100]}...")
        else:
            print("   ❌ Processing failed")


def test_tts():
    """Test text-to-speech"""
    print("\n🔊 Testing Text-to-Speech")
    print("=" * 50)
    
    voice = VoiceInterface()
    
    test_phrases = [
        "Hello! I'm your computer helper.",
        "I'll help you install Firefox right away.",
        "Your computer is now up to date and secure."
    ]
    
    for phrase in test_phrases:
        print(f"\nTesting TTS: '{phrase}'")
        voice.speak(phrase)
        input("Press Enter to continue...")


def main():
    """Run all tests"""
    print("""
    🧪 Nix for Humanity Voice Interface Test Suite
    =============================================
    
    This will test all components of the voice system.
    """)
    
    # Test basic components
    if not test_basic_components():
        print("\n❌ Basic component tests failed. Please install dependencies.")
        return
    
    # Test voice processing
    asyncio.run(test_voice_processing())
    
    # Test simple demo
    test_simple_demo()
    
    # Optional: Test TTS (requires audio)
    response = input("\n🔊 Test text-to-speech? (requires speakers) [y/N]: ")
    if response.lower() == 'y':
        test_tts()
    
    print("\n✅ All tests completed!")
    print("\n📝 Next steps:")
    print("1. Run the WebSocket server: python voice_websocket_server.py")
    print("2. Open the web interface: frontend/voice-ui/index.html")
    print("3. Or run the simple demo: python voice_demo_simple.py")


if __name__ == "__main__":
    main()