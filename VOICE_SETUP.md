# 🎙️ Voice Interface Setup Guide

## Overview

Luminous Nix includes optional voice interface capabilities for natural speech interaction. This allows you to speak commands and hear responses, making NixOS truly accessible to everyone.

## Prerequisites

The voice interface requires several Python packages that are not included by default to keep the base installation lightweight.

## Installation

### Quick Install

```bash
# Install all voice dependencies
pip install --user SpeechRecognition pyttsx3 pyaudio

# For better speech recognition (optional)
pip install --user google-cloud-speech
```

### Detailed Installation

#### 1. Speech Recognition
```bash
pip install --user SpeechRecognition
```
This provides speech-to-text capabilities using various engines.

#### 2. Text-to-Speech
```bash
pip install --user pyttsx3
```
This enables the system to speak responses back to you.

#### 3. Audio Input
```bash
pip install --user pyaudio
```
Required for microphone access. On some systems, you may need:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyaudio

# Fedora
sudo dnf install python3-pyaudio

# NixOS
nix-env -iA nixos.python3Packages.pyaudio
# Or with nix profile (recommended)
nix profile install nixpkgs#python3Packages.pyaudio
```

### Troubleshooting Audio Dependencies

If you encounter issues with PyAudio installation:

#### On Linux:
```bash
# Install system dependencies first
sudo apt-get install portaudio19-dev python3-dev
# Then install pyaudio
pip install --user pyaudio
```

#### On macOS:
```bash
# Using Homebrew
brew install portaudio
pip install --user pyaudio
```

#### On NixOS:
```bash
# Use nix-shell for development
nix-shell -p portaudio python3Packages.pyaudio
```

## Usage

Once dependencies are installed, you can use voice features:

### Basic Voice Commands
```bash
# Enable voice input
ask-nix --voice

# Speak responses
ask-nix --speak "install firefox"

# Continuous listening mode
ask-nix --listen

# All voice features
ask-nix --voice --speak --listen
```

### Example Session
```bash
$ ask-nix --voice
🎤 Listening... (Say your command)
You: "Install Firefox"
Nix: "Installing Firefox..." (spoken aloud if --speak is enabled)
```

## Configuration

### Microphone Selection
The system will use your default microphone. To change it:
1. Set your system's default audio input device
2. Or modify the voice settings in your configuration

### Speech Engine
By default, the system uses:
- **Recognition**: Google Speech Recognition (requires internet)
- **Synthesis**: System default TTS engine

### Language Settings
Currently supports English. Future versions will add multilingual support.

## Privacy Considerations

- **Local Mode**: If you prefer completely offline operation, you can use PocketSphinx:
  ```bash
  pip install --user pocketsphinx
  ```
  Note: Offline recognition is less accurate than cloud-based services.

- **Cloud Services**: Default Google Speech Recognition sends audio to Google servers. For privacy-conscious users, we recommend using offline alternatives.

## Common Issues

### "Voice support not available"
This means the required packages are not installed. Run the installation commands above.

### "No microphone found"
1. Check your microphone is connected
2. Verify system audio permissions
3. Test with: `python -m speech_recognition`

### "PyAudio installation failed"
You need system-level audio libraries. See the Troubleshooting section above.

### Poor recognition accuracy
1. Speak clearly and at normal pace
2. Reduce background noise
3. Check microphone quality
4. Consider using a headset

## Future Enhancements

Planned improvements for voice interface:
- Multiple language support
- Custom wake words
- Voice profiles for different users
- Integration with local LLMs for processing
- Noise cancellation
- Speaker identification

## Testing Voice Setup

After installation, test your setup:

```bash
# Test speech recognition
python -c "import speech_recognition as sr; print('✅ Speech recognition available')"

# Test text-to-speech
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Hello from Luminous Nix'); engine.runAndWait()"

# Test full voice interface
ask-nix --voice --speak "test voice"
```

## Personas and Voice

Different personas have different voice characteristics:
- **Grandma Rose**: Slower, clearer speech
- **Maya (ADHD)**: Faster responses, minimal verbosity
- **Alex (Blind)**: Detailed audio descriptions
- **Dr. Sarah**: Technical terminology pronunciation

Select a persona with voice:
```bash
ask-nix --voice --persona grandma
```

---

## Summary

Voice interface is an optional but powerful feature that makes NixOS accessible to everyone. While it requires additional dependencies, the setup is straightforward and the benefits are significant for users who prefer or need voice interaction.

For any issues, please refer to our [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) or open an issue on GitHub.