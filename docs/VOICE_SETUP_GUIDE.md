# 🎤 Voice Interface Setup Guide - Nix for Humanity

*Enable natural voice interaction with NixOS using Whisper and Piper*

## Overview

The Nix for Humanity voice interface provides:
- **Wake word detection**: "Hey Nix" to activate
- **Speech-to-text**: Whisper for accurate transcription
- **Text-to-speech**: Piper for natural voice responses
- **Continuous listening**: Hands-free operation

## Prerequisites

### System Requirements
- NixOS system (or Linux with Nix)
- Microphone (USB or built-in)
- Speakers or headphones
- ~2GB disk space for models
- Python 3.11+

### Audio Setup
Ensure your audio devices are working:
```bash
# Test microphone
arecord -d 5 test.wav
aplay test.wav

# List audio devices
arecord -l
aplay -l
```

## Installation

### Method 1: NixOS Module (Recommended - The Nix Way!)

Add to your NixOS configuration:
```nix
# configuration.nix or flake.nix
{
  imports = [
    # Import the voice module
    (fetchGit {
      url = "https://github.com/Luminous-Dynamics/nix-for-humanity";
      ref = "main";
    } + "/modules/voice.nix")
  ];
  
  # Enable and configure voice interface
  services.nixForHumanity.voice = {
    enable = true;
    whisperModel = "base";        # or "tiny", "small", "medium", "large"
    piperVoice = "en_US-amy-medium";
    device = "cpu";               # or "cuda" for GPU acceleration
    autoDownloadModels = true;    # Downloads models on first run
  };
  
  # Optional: customize settings
  services.nixForHumanity.voice = {
    wakeWord = "hey nix";         # Custom wake word
    language = "en";              # Speech recognition language
    speechRate = 1.0;             # TTS speed (0.5-2.0)
    sampleRate = 16000;           # Audio quality
  };
}
```

Then rebuild:
```bash
sudo nixos-rebuild switch
```

The service will automatically:
- Install all dependencies (Whisper, Piper, audio libraries)
- Download voice models on first run
- Set up systemd service
- Configure audio permissions

### Method 2: Nix Development Shell (For Development)

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Enter the Nix shell with all voice dependencies
nix develop

# Voice dependencies are automatically available!
# No pip install needed - everything is provided by Nix
```

The shell includes:
- OpenAI Whisper with PyTorch
- Piper TTS
- All audio libraries (sounddevice, portaudio)
- FFmpeg and Sox for audio processing

### Method 3: Standalone Nix Shell (Quick Testing)

Create a `shell.nix` file:
```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    (python311.withPackages (ps: with ps; [
      openai-whisper
      sounddevice
      numpy
      torch
      torchaudio
    ]))
    piper-tts
    portaudio
    ffmpeg
    sox
  ];
  
  shellHook = ''
    echo "🎤 Voice interface dependencies loaded!"
    echo "Run: python setup_voice.py"
  '';
}
```

Then:
```bash
nix-shell
python setup_voice.py
```

### Method 4: Home Manager Module

For user-specific installation:
```nix
# home.nix
{
  imports = [
    (fetchGit {
      url = "https://github.com/Luminous-Dynamics/nix-for-humanity";
      ref = "main";
    } + "/modules/home-manager/voice.nix")
  ];
  
  programs.nixForHumanity.voice = {
    enable = true;
    whisperModel = "base";
    piperVoice = "en_US-amy-medium";
  };
}
```

## Why the Nix Way is Better

1. **Reproducible**: Same environment on every machine
2. **No Dependency Conflicts**: Nix handles all versions
3. **Atomic Updates**: Roll back if something breaks
4. **No Global Pollution**: Everything is isolated
5. **Declarative**: Your config describes the entire setup

## Post-Installation Setup

### 1. Enable the Service (NixOS module)
```bash
# Start the voice service
sudo systemctl start nix-humanity-voice

# Enable at boot
sudo systemctl enable nix-humanity-voice

# Check status
sudo systemctl status nix-humanity-voice
```

### 2. Test Audio (All methods)
```bash
# Run the convenience script (if using NixOS module)
/etc/nix-humanity/enable-voice.sh

# Or test manually
arecord -d 3 test.wav && aplay test.wav
```

### 3. Download Models

If not using `autoDownloadModels`, manually download:
```bash
# In nix shell
python -c "import whisper; whisper.load_model('base')"

# Download Piper voices
mkdir -p ~/.local/share/piper/voices
cd ~/.local/share/piper/voices
wget https://github.com/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx.json
```

2. **Download Whisper model**:
```bash
# Download base model (~150MB)
python -c "import whisper; whisper.load_model('base')"

# For better accuracy (but slower):
# python -c "import whisper; whisper.load_model('small')"  # ~500MB
# python -c "import whisper; whisper.load_model('medium')" # ~1.5GB
```

3. **Download Piper voice**:
```bash
# Create voices directory
mkdir -p ~/.local/share/piper/voices

# Download Amy voice (natural US English)
cd ~/.local/share/piper/voices
wget https://github.com/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.0.0/en_US-amy-medium.onnx.json
```

## Configuration

### Voice Settings

Create or edit `~/.config/nix-humanity/voice.yaml`:
```yaml
voice:
  # Wake word configuration
  wake_word: "hey nix"  # Can be customized
  
  # Whisper settings
  whisper:
    model: "base"  # tiny, base, small, medium, large
    language: "en"
    
  # Piper settings  
  piper:
    voice: "en_US-amy-medium"
    speed: 1.0  # Speech rate (0.5-2.0)
    
  # Audio settings
  audio:
    sample_rate: 16000
    chunk_duration: 0.1  # 100ms chunks
    silence_threshold: 0.01
    silence_duration: 1.5  # Stop after 1.5s silence
```

### Available Voices

Piper supports many voices:
- **US English**: amy, danny, joe, kathleen, ryan
- **UK English**: alan, alba, jenny, northern_english_male
- **Other accents**: Various regional options

Download additional voices from:
https://github.com/rhasspy/piper/releases

## Usage

### Starting Voice Interface

1. **Standalone mode**:
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
./bin/nix-voice
```

2. **With TUI (enhanced mode)**:
```bash
./bin/nix-tui
# Press Ctrl+V to toggle voice
```

3. **Programmatically**:
```python
from nix_humanity.interfaces.voice_interface import VoiceAssistant

assistant = VoiceAssistant()
assistant.start()
# Say "Hey Nix" to activate
```

### Voice Commands

Once activated with "Hey Nix":
- "Install Firefox"
- "Update my system"
- "Search for text editors"
- "How much disk space do I have?"
- "What's my IP address?"
- "Show system information"

### Visual Feedback

The TUI shows voice state:
- 🎤 **Idle**: Waiting for wake word
- 👂 **Listening**: Recording your command
- 🤔 **Processing**: Understanding your request
- 🗣️ **Speaking**: Responding to you
- ❌ **Error**: Something went wrong

## Troubleshooting

### No Audio Input Detected

1. Check microphone permissions:
```bash
# Ensure user is in audio group
groups | grep audio
sudo usermod -a -G audio $USER
```

2. Test with Python:
```python
import sounddevice as sd
print(sd.query_devices())
```

3. Set default device:
```python
# In voice.yaml
audio:
  input_device: 2  # Device index from query_devices()
```

### Wake Word Not Detected

1. **Increase sensitivity**:
```yaml
voice:
  wake_sensitivity: 0.7  # Lower = more sensitive (0.5-0.9)
```

2. **Check background noise**:
```bash
# Monitor audio levels
python -m nix_humanity.tools.audio_monitor
```

3. **Use push-to-talk**:
```yaml
voice:
  push_to_talk: true
  ptt_key: "space"  # Hold space to talk
```

### Speech Recognition Errors

1. **Try different Whisper model**:
```yaml
whisper:
  model: "small"  # More accurate than base
```

2. **Adjust for accent**:
```yaml
whisper:
  language: "en"
  task: "transcribe"
  initial_prompt: "NixOS commands"  # Helps with technical terms
```

### Voice Synthesis Issues

1. **Check Piper installation**:
```bash
piper --version
```

2. **Test voice directly**:
```bash
echo "Hello from Nix" | piper \
  --model ~/.local/share/piper/voices/en_US-amy-medium.onnx \
  --output_file test.wav
aplay test.wav
```

### Performance Issues

1. **Use smaller models**:
```yaml
whisper:
  model: "tiny"  # Fastest, lower accuracy
```

2. **Enable GPU acceleration** (if available):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. **Optimize audio buffer**:
```yaml
audio:
  chunk_duration: 0.2  # Larger chunks, less CPU
```

## Advanced Configuration

### Custom Wake Words

```yaml
voice:
  wake_words:
    - "hey nix"
    - "okay nix"
    - "nixos"
  wake_engine: "pocketsphinx"  # or "precise", "snowboy"
```

### Multiple Languages

```yaml
whisper:
  multilingual: true
  languages: ["en", "es", "de", "fr"]
  detect_language: true
```

### Voice Profiles

```yaml
profiles:
  quiet:
    piper:
      speed: 0.9
      volume: 0.7
  energetic:
    piper:
      speed: 1.2
      pitch: 1.1
```

### Privacy Settings

```yaml
privacy:
  save_recordings: false
  anonymize_logs: true
  local_only: true  # Never send audio to cloud
```

## Integration with TUI

The voice interface integrates seamlessly with the TUI:

1. **Voice indicator**: Shows current state in status bar
2. **Transcript display**: Shows what was heard
3. **Response visualization**: Animated speech output
4. **Keyboard override**: Press any key to interrupt

## Tips for Best Experience

### Microphone Placement
- 6-12 inches from mouth
- Away from fans/vents
- Stable position (not handheld)

### Speaking Style
- Natural pace
- Clear pronunciation
- Pause briefly after wake word
- Complete sentences work best

### Environment
- Quiet room preferred
- Consistent background noise OK
- Avoid echo-prone spaces

### Commands
- Start with verb: "Install", "Search", "Update"
- Be specific: "Install Firefox" not "Get browser"
- Ask questions: "What's installed?"

## Example Configurations

### Accessibility-Focused
```yaml
voice:
  # Easier wake word
  wake_word: "computer"
  
  # More forgiving settings
  silence_duration: 2.5
  wake_sensitivity: 0.6
  
  # Clearer voice
  piper:
    voice: "en_US-kathleen-medium"
    speed: 0.85
```

### Developer-Focused
```yaml
voice:
  # Quick activation
  wake_word: "nix"
  push_to_talk: true
  ptt_key: "ctrl"
  
  # Fast response
  whisper:
    model: "tiny"
  
  # Minimal voice
  piper:
    voice: "en_US-joe-medium"
    speed: 1.1
```

### Family Computer
```yaml
voice:
  # Multiple wake words
  wake_words: ["hey computer", "okay nix", "help please"]
  
  # Accurate recognition
  whisper:
    model: "small"
    
  # Friendly voice
  piper:
    voice: "en_US-amy-medium"
    personality: "friendly"
```

## Extending Voice Interface

### Custom Commands

Add to `~/.config/nix-humanity/voice_commands.py`:
```python
def handle_custom_command(text):
    if "good morning" in text.lower():
        return "Good morning! Here's your system status..."
    elif "bedtime" in text.lower():
        return "Setting up night mode. Sleep well!"
```

### Voice Shortcuts

```yaml
shortcuts:
  "update everything": "update system && update packages"
  "clean up": "collect garbage && optimize store"
  "daily routine": "update system && show status"
```

## Resources

- [Whisper Documentation](https://github.com/openai/whisper)
- [Piper TTS Guide](https://github.com/rhasspy/piper)
- [Audio Troubleshooting](https://wiki.nixos.org/wiki/Audio)
- [Nix for Humanity Discussions](https://github.com/Luminous-Dynamics/nix-for-humanity/discussions)

---

*Voice control makes NixOS accessible to everyone. Speak naturally, and let Nix for Humanity handle the complexity.*