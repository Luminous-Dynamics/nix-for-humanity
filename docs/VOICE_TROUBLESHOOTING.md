# 🔧 Voice Interface Troubleshooting

*Common issues and solutions for the Nix for Humanity voice interface*

## Quick Diagnostics

Run this first to check your setup:
```bash
python setup_voice.py
```

This will:
- Check all dependencies
- Test your microphone
- Verify Whisper installation
- Test Piper TTS
- Create configuration

## Common Issues

### 1. "Voice interface not available" Error

**Symptom**: Pressing Ctrl+V shows error message

**Solution**:
```bash
# Install required packages
pip install openai-whisper sounddevice numpy

# Download Whisper model
python -c "import whisper; whisper.load_model('base')"

# Install Piper
pip install piper-tts
```

### 2. No Audio Input Detected

**Symptom**: Voice interface active but doesn't respond to speech

**Causes & Solutions**:

#### A. Wrong microphone selected
```python
# List available devices
import sounddevice as sd
print(sd.query_devices())

# Set specific device in config
# ~/.config/nix-humanity/voice.json
{
  "voice": {
    "audio": {
      "input_device": 2  # Your mic's device number
    }
  }
}
```

#### B. Microphone permissions (Linux)
```bash
# Check if user is in audio group
groups | grep audio

# If not, add yourself
sudo usermod -a -G audio $USER
# Log out and back in
```

#### C. PulseAudio/PipeWire issues
```bash
# Restart audio service
systemctl --user restart pulseaudio
# or
systemctl --user restart pipewire

# Test microphone
pactl info
```

### 3. Wake Word Not Recognized

**Symptom**: Saying "Hey Nix" doesn't activate

**Solutions**:

#### A. Increase wake word sensitivity
Edit `~/.config/nix-humanity/voice.json`:
```json
{
  "voice": {
    "wake_sensitivity": 0.6,  // Lower = more sensitive
    "wake_variants": ["hey nix", "okay nix", "hi nix"]
  }
}
```

#### B. Check background noise
- Move to quieter location
- Use headset with noise cancellation
- Adjust silence threshold:
```json
{
  "voice": {
    "audio": {
      "silence_threshold": 0.02  // Increase for noisy environments
    }
  }
}
```

#### C. Test with mock mode
```bash
# Run with mock voice to verify setup
NIX_VOICE_MOCK=true ./bin/nix-voice
```

### 4. Whisper Model Errors

**Symptom**: "Failed to load Whisper model"

**Solutions**:

#### A. Re-download model
```python
import whisper
# Force re-download
whisper.load_model("base", download_root="~/.cache/whisper")
```

#### B. Try smaller model
```python
# Use tiny model (39MB vs 150MB)
whisper.load_model("tiny")
```

#### C. Check disk space
```bash
df -h ~/.cache/whisper
# Need at least 500MB free
```

### 5. Piper TTS Not Working

**Symptom**: No voice output, synthesis errors

**Solutions**:

#### A. Manual voice download
```bash
mkdir -p ~/.local/share/piper/voices
cd ~/.local/share/piper/voices

# Download voice files
wget https://github.com/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx.json
```

#### B. Test Piper CLI
```bash
echo "Hello from Nix" | piper \
  --model ~/.local/share/piper/voices/en_US-amy-medium.onnx \
  --output_file test.wav

# Play the file
aplay test.wav
```

#### C. Use different voice
```bash
# List available voices
ls ~/.local/share/piper/voices/

# Update config to use available voice
```

### 6. Performance Issues

**Symptom**: Slow response, high CPU usage

**Solutions**:

#### A. Use smaller models
```json
{
  "voice": {
    "whisper": {
      "model": "tiny"  // Fastest
    }
  }
}
```

#### B. Enable GPU acceleration (if available)
```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Set device in config
{
  "voice": {
    "whisper": {
      "device": "cuda"
    }
  }
}
```

#### C. Increase chunk duration
```json
{
  "voice": {
    "audio": {
      "chunk_duration": 0.2  // Larger chunks, less processing
    }
  }
}
```

### 7. Voice Not Integrated with TUI

**Symptom**: Voice works standalone but not in TUI

**Solution**:
```bash
# Make sure you're using the unified TUI
./bin/nix-tui

# Press Ctrl+V to enable voice
# Look for voice widget in enhanced mode (Ctrl+E)
```

### 8. Transcription Errors

**Symptom**: Speech recognized incorrectly

**Solutions**:

#### A. Provide context hints
```json
{
  "voice": {
    "whisper": {
      "initial_prompt": "NixOS commands like install, update, remove, search"
    }
  }
}
```

#### B. Speak more clearly
- Pause briefly after wake word
- Speak at moderate pace
- Complete sentences work better
- Avoid background conversations

#### C. Use larger model
```json
{
  "voice": {
    "whisper": {
      "model": "small"  // Better accuracy
    }
  }
}
```

## Debug Mode

Enable detailed logging:
```bash
# Set environment variable
export NIX_VOICE_DEBUG=true

# Run voice interface
./bin/nix-voice
```

This shows:
- Audio levels
- Wake word detection attempts
- Transcription results
- State changes

## Testing Components Individually

### Test Microphone
```python
import sounddevice as sd
import numpy as np

duration = 5  # seconds
print("Recording...")
recording = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
sd.wait()
print(f"Average volume: {np.abs(recording).mean()}")
```

### Test Whisper
```python
import whisper
model = whisper.load_model("base")
# Should load without errors
```

### Test Piper
```bash
piper --version
# Should show version number
```

## Platform-Specific Issues

### NixOS
```nix
# Add to configuration.nix
environment.systemPackages = with pkgs; [
  python3Packages.sounddevice
  python3Packages.numpy
  ffmpeg  # Required by Whisper
];

# Audio permissions
users.users.youruser.extraGroups = [ "audio" ];
```

### macOS
- Grant microphone permissions in System Preferences
- May need to install PortAudio: `brew install portaudio`

### Windows
- Run as Administrator for first setup
- Windows Defender may block microphone access

## Getting Help

If issues persist:

1. **Collect debug info**:
```bash
python setup_voice.py > debug_info.txt 2>&1
```

2. **Check logs**:
```bash
tail -f ~/.local/share/nix-humanity/voice.log
```

3. **Report issue** with:
- OS and version
- Python version
- Debug output
- Steps to reproduce

## Quick Fixes Checklist

- [ ] Dependencies installed (`pip install openai-whisper sounddevice numpy`)
- [ ] Whisper model downloaded (`python -c "import whisper; whisper.load_model('base')"`)
- [ ] Piper voices downloaded (check `~/.local/share/piper/voices/`)
- [ ] Microphone working (`arecord -d 5 test.wav && aplay test.wav`)
- [ ] Audio permissions granted
- [ ] Configuration file exists (`~/.config/nix-humanity/voice.json`)
- [ ] No other apps using microphone
- [ ] Tried mock mode (`NIX_VOICE_MOCK=true ./bin/nix-voice`)

---

*Remember: Voice control is about making NixOS accessible. If voice isn't working, the CLI and TUI still provide full functionality!*