#!/usr/bin/env python3
"""
Test Complete Voice Pipeline
============================

End-to-end test of the voice interface for Grandma Rose.
Tests all components working together.
"""

import asyncio
import websockets
import json
import base64
import wave
import numpy as np
import tempfile
import os


def create_test_audio():
    """Create a test audio file (silent)"""
    # Create a simple WAV file with silence
    duration = 2  # seconds
    sample_rate = 16000
    num_samples = duration * sample_rate
    
    # Generate silence (zeros)
    audio_data = np.zeros(num_samples, dtype=np.int16)
    
    # Save to temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        with wave.open(tmp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return tmp_file.name


async def test_websocket_connection():
    """Test WebSocket connection and communication"""
    print("\n🧪 Testing WebSocket Connection")
    print("=" * 50)
    
    try:
        # Connect to WebSocket server
        uri = "ws://localhost:8765"
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Test 1: Welcome message
            welcome = await websocket.recv()
            data = json.loads(welcome)
            print(f"✅ Received welcome: {data['message']}")
            
            # Test 2: Text command
            print("\n📝 Testing text command...")
            await websocket.send(json.dumps({
                "type": "text",
                "text": "I need to check my email"
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            if data['type'] == 'response':
                print(f"✅ Got response: {data['response'][:100]}...")
                print(f"   Intent: {data.get('intent', 'unknown')}")
            
            # Test 3: Settings update
            print("\n⚙️  Testing settings update...")
            await websocket.send(json.dumps({
                "type": "settings",
                "settings": {
                    "voiceSpeed": 0.8,
                    "voiceVolume": 0.9
                }
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            if data['type'] == 'settings_updated':
                print("✅ Settings updated successfully")
            
            # Test 4: Audio processing (mock)
            print("\n🎤 Testing audio processing...")
            
            # Create test audio
            audio_path = create_test_audio()
            
            # Read and encode audio
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Send audio
            await websocket.send(json.dumps({
                "type": "audio",
                "audio": audio_base64
            }))
            
            # Wait for responses
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                if data['type'] == 'status':
                    print(f"   Status: {data['message']}")
                elif data['type'] == 'transcript':
                    print(f"   Transcript: {data['text']}")
                elif data['type'] == 'response':
                    print(f"✅ Got audio response")
                    print(f"   Response: {data['response'][:100]}...")
                    break
                elif data['type'] == 'error':
                    print(f"❌ Error: {data['message']}")
                    break
            
            # Clean up
            os.unlink(audio_path)
            
            print("\n✅ All WebSocket tests passed!")
            
    except websockets.exceptions.ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("   Make sure the server is running:")
        print("   python backend/python/run_voice_server.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_voice_commands():
    """Test various voice commands"""
    print("\n🗣️  Testing Voice Commands")
    print("=" * 50)
    
    test_commands = [
        ("I need to check my email", "install_package"),
        ("My WiFi isn't working", "fix_wifi"),
        ("Update my computer", "update_system"),
        ("I want to video call my grandkids", "install_package"),
        ("Is my computer safe?", "check_security"),
    ]
    
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            # Skip welcome message
            await websocket.recv()
            
            for command, expected_intent in test_commands:
                print(f"\n📝 Testing: '{command}'")
                
                # Send command
                await websocket.send(json.dumps({
                    "type": "text",
                    "text": command
                }))
                
                # Get response
                response = await websocket.recv()
                data = json.loads(response)
                
                if data['type'] == 'response':
                    intent = data.get('intent', 'unknown')
                    print(f"   Intent: {intent}")
                    print(f"   Response: {data['response'][:80]}...")
                    
                    if intent == expected_intent:
                        print("   ✅ Correct intent detected")
                    else:
                        print(f"   ⚠️  Expected '{expected_intent}', got '{intent}'")
                
                # Small delay between tests
                await asyncio.sleep(0.5)
                
    except Exception as e:
        print(f"❌ Command test failed: {e}")


def test_frontend_compatibility():
    """Test that frontend files are accessible"""
    print("\n🌐 Testing Frontend Compatibility")
    print("=" * 50)
    
    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'frontend', 'voice-ui'
    )
    
    required_files = [
        'index.html',
        'styles.css',
        'voice-interface.js'
    ]
    
    all_found = True
    for file in required_files:
        file_path = os.path.join(frontend_path, file)
        if os.path.exists(file_path):
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            all_found = False
    
    if all_found:
        print("\n✅ All frontend files present!")
        print(f"   Open file://{os.path.join(frontend_path, 'index.html')} to test")
    else:
        print("\n❌ Some frontend files are missing")


async def main():
    """Run all tests"""
    print("""
🎤 Nix for Humanity Voice Pipeline Test
======================================

This test verifies the complete voice interface pipeline.
""")
    
    # Test frontend files
    test_frontend_compatibility()
    
    # Test WebSocket connection
    await test_websocket_connection()
    
    # Test voice commands
    await test_voice_commands()
    
    print("\n" + "=" * 50)
    print("🎉 Voice pipeline testing complete!")
    print("\nNext steps:")
    print("1. Start the server: python backend/python/run_voice_server.py")
    print("2. Open frontend/voice-ui/index.html in a browser")
    print("3. Click the microphone button and speak!")


if __name__ == "__main__":
    asyncio.run(main())