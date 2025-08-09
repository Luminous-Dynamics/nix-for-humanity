#!/usr/bin/env python3
"""
from typing import Dict
Voice Interface Setup Script for Nix for Humanity

This script helps users set up and test the voice interface with real
Whisper and Piper models.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

def check_dependencies() -> Dict[str, bool]:
    """Check which dependencies are installed"""
    deps = {
        'whisper': False,
        'piper': False,
        'sounddevice': AUDIO_AVAILABLE,
        'numpy': False,
        'torch': False
    }
    
    try:
        import whisper
        deps['whisper'] = True
    except ImportError:
        # TODO: Add proper error handling
        pass  # Silent for now, should log error
    
    try:
        import piper
        deps['piper'] = True
    except ImportError:
        # TODO: Add proper error handling
        pass  # Silent for now, should log error
    
    try:
        import numpy
        deps['numpy'] = True
    except ImportError:
        # TODO: Add proper error handling
        pass  # Silent for now, should log error
    
    try:
        import torch
        deps['torch'] = True
    except ImportError:
        # TODO: Add proper error handling
        pass  # Silent for now, should log error
    
    return deps

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing voice dependencies...")
    
    packages = [
        "openai-whisper",
        "sounddevice",
        "numpy",
        "pyaudio"
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def download_whisper_model(model_size: str = "base"):
    """Download Whisper model"""
    print(f"\n📥 Downloading Whisper {model_size} model...")
    
    try:
        import whisper
        print("Loading model (this may take a while on first run)...")
        model = whisper.load_model(model_size)
        print(f"✅ Whisper {model_size} model ready!")
        return model
    except Exception as e:
        print(f"❌ Failed to download Whisper model: {e}")
        return None

def setup_piper_voice(voice_name: str = "en_US-amy-medium"):
    """Set up Piper TTS voice"""
    print(f"\n🗣️ Setting up Piper voice: {voice_name}")
    
    # Create voices directory
    voices_dir = Path.home() / ".local" / "share" / "piper" / "voices"
    voices_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if voice already exists
    voice_file = voices_dir / f"{voice_name}.onnx"
    config_file = voices_dir / f"{voice_name}.onnx.json"
    
    if voice_file.exists() and config_file.exists():
        print(f"✅ Voice {voice_name} already installed")
        return True
    
    # Download voice files
    base_url = "https://github.com/rhasspy/piper/releases/download/v1.0.0"
    
    for file_name, file_path in [(f"{voice_name}.onnx", voice_file), 
                                  (f"{voice_name}.onnx.json", config_file)]:
        print(f"📥 Downloading {file_name}...")
        try:
            import urllib.request
            url = f"{base_url}/{file_name}"
            urllib.request.urlretrieve(url, file_path)
            print(f"✅ Downloaded {file_name}")
        except Exception as e:
            print(f"❌ Failed to download {file_name}: {e}")
            return False
    
    return True

def test_microphone():
    """Test microphone input"""
    if not AUDIO_AVAILABLE:
        print("❌ Audio libraries not available. Please install sounddevice.")
        return False
    
    print("\n🎤 Testing microphone...")
    print("Available audio devices:")
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  [{i}] {device['name']} (inputs: {device['max_input_channels']})")
    
    # Test recording
    print("\n🔴 Recording 3 seconds of audio...")
    try:
        duration = 3
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='float32')
        sd.wait()
        
        # Calculate volume
        volume = np.abs(recording).mean()
        print(f"✅ Recording complete. Average volume: {volume:.4f}")
        
        if volume < 0.001:
            print("⚠️ Very low volume detected. Check your microphone.")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_whisper_transcription():
    """Test Whisper speech recognition"""
    print("\n🧪 Testing Whisper transcription...")
    
    try:
        import whisper
        model = whisper.load_model("base")
        
        # Create test audio
        print("🎤 Say something in the next 5 seconds...")
        duration = 5
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          dtype='float32')
        sd.wait()
        
        print("🤔 Transcribing...")
        result = model.transcribe(recording.flatten(), language="en")
        text = result.get("text", "").strip()
        
        if text:
            print(f"✅ Transcription: '{text}'")
            return True
        else:
            print("❌ No speech detected")
            return False
            
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

def test_piper_synthesis():
    """Test Piper text-to-speech"""
    print("\n🧪 Testing Piper TTS...")
    
    voice_name = "en_US-amy-medium"
    voices_dir = Path.home() / ".local" / "share" / "piper" / "voices"
    voice_file = voices_dir / f"{voice_name}.onnx"
    
    if not voice_file.exists():
        print(f"❌ Voice file not found: {voice_file}")
        return False
    
    try:
        # Use piper CLI for testing
        test_text = "Hello from Nix for Humanity. Voice interface is working!"
        
        print(f"🗣️ Synthesizing: '{test_text}'")
        
        # Create temporary wav file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Run piper
        cmd = [
            "piper",
            "--model", str(voice_file),
            "--output_file", tmp_path
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=test_text)
        
        if process.returncode == 0:
            print("✅ Speech synthesis successful!")
            
            # Try to play the audio
            if AUDIO_AVAILABLE:
                import wave
                with wave.open(tmp_path, 'rb') as wf:
                    data = wf.readframes(wf.getnframes())
                    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    sd.play(audio, samplerate=wf.getframerate())
                    sd.wait()
                    print("✅ Audio playback complete!")
            
            # Clean up
            os.unlink(tmp_path)
            return True
        else:
            print(f"❌ Piper failed: {stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Piper command not found. Install with: pip install piper-tts")
        return False
    except Exception as e:
        print(f"❌ Piper test failed: {e}")
        return False

def create_config():
    """Create voice configuration file"""
    print("\n📝 Creating voice configuration...")
    
    config_dir = Path.home() / ".config" / "nix-humanity"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "voice": {
            "wake_word": "hey nix",
            "whisper": {
                "model": "base",
                "language": "en"
            },
            "piper": {
                "voice": "en_US-amy-medium",
                "speed": 1.0
            },
            "audio": {
                "sample_rate": 16000,
                "chunk_duration": 0.1,
                "silence_threshold": 0.01,
                "silence_duration": 1.5
            }
        }
    }
    
    config_file = config_dir / "voice.yaml"
    
    # Use JSON for simplicity (YAML requires additional dependency)
    config_json = config_dir / "voice.json"
    with open(config_json, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to: {config_json}")
    return True

def run_voice_demo():
    """Run a simple voice interface demo"""
    print("\n🎭 Running voice interface demo...")
    
    try:
        # Import our voice interface
        from nix_humanity.interfaces.voice_interface import VoiceAssistant
        
        print("🚀 Starting voice assistant...")
        print("Say 'Hey Nix' followed by your command")
        print("Press Ctrl+C to stop")
        
        assistant = VoiceAssistant()
        assistant.start()
        
        # Keep running until interrupted
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping voice assistant...")
            assistant.stop()
            
    except ImportError as e:
        print(f"❌ Could not import voice interface: {e}")
        print("Make sure you're in the project directory")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def main():
    """Main setup flow"""
    print("🎤 Nix for Humanity Voice Interface Setup")
    print("=" * 50)
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    deps = check_dependencies()
    
    for dep, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"  {status} {dep}")
    
    # Install missing dependencies
    if not all(deps.values()):
        response = input("\n📦 Install missing dependencies? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
            deps = check_dependencies()
    
    # Set up Whisper
    if deps['whisper']:
        model_size = input("\n🎯 Whisper model size (tiny/base/small/medium) [base]: ") or "base"
        download_whisper_model(model_size)
    
    # Set up Piper
    voice_name = input("\n🗣️ Piper voice name [en_US-amy-medium]: ") or "en_US-amy-medium"
    setup_piper_voice(voice_name)
    
    # Test components
    print("\n🧪 Running component tests...")
    
    if test_microphone():
        print("✅ Microphone working")
    
    if deps['whisper'] and AUDIO_AVAILABLE:
        if test_whisper_transcription():
            print("✅ Whisper working")
    
    if test_piper_synthesis():
        print("✅ Piper working")
    
    # Create config
    create_config()
    
    # Offer to run demo
    response = input("\n🎭 Run voice interface demo? (y/n): ")
    if response.lower() == 'y':
        run_voice_demo()
    
    print("\n✅ Voice setup complete!")
    print("\nTo use voice with the TUI:")
    print("  ./bin/nix-tui  # Then press Ctrl+V to toggle voice")
    print("\nTo run standalone voice interface:")
    print("  ./bin/nix-voice")

if __name__ == "__main__":
    main()