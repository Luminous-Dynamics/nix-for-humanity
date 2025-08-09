# 🎤 Grandma Rose Voice Interface

*Making NixOS accessible through natural conversation*

## Overview

The Grandma Rose Voice Interface is a compassionate, accessibility-first voice system designed to make NixOS usable by everyone - especially those who find traditional command-line interfaces challenging.

## Features

### For Users
- 🎤 **Natural Speech**: Just press and talk - no commands to memorize
- 🔊 **Clear Responses**: Friendly voice feedback in simple language
- 🎯 **Smart Understanding**: Handles common phrases like "check my email"
- ♿ **Fully Accessible**: Large buttons, clear visuals, keyboard shortcuts
- 🏠 **Privacy First**: Everything runs locally on your computer

### Technical Features
- **Whisper.cpp**: Fast, accurate speech recognition
- **Piper TTS**: Natural-sounding voice responses
- **WebSocket Bridge**: Real-time communication
- **Adaptive Responses**: Adjusts complexity based on user
- **Python Backend**: Direct NixOS integration

## Quick Start

### 1. Simple Demo (No Audio Required)
```bash
./start-voice-interface.sh demo
```
This runs a text-based simulation perfect for testing.

### 2. Full Voice Interface
```bash
./start-voice-interface.sh
```
Opens the web interface with full voice capabilities.

### 3. Run Tests
```bash
./start-voice-interface.sh test
```
Verifies all components are working correctly.

## Installation

### Prerequisites
The voice interface requires these packages (included in flake.nix):
- `whisper-cpp` - Speech recognition
- `piper-tts` - Text-to-speech
- `portaudio` - Audio I/O
- `python3` with `pyaudio`, `numpy`

### Setup
1. Enter the development environment:
   ```bash
   cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
   nix develop
   ```

2. Install Python dependencies:
   ```bash
   pip install -r backend/python/voice_requirements.txt
   ```

3. Start the interface:
   ```bash
   ./start-voice-interface.sh
   ```

## How It Works

### User Flow
1. **Press the Button**: Click or press Space to start
2. **Speak Naturally**: "I need to check my email"
3. **See Response**: Clear instructions appear
4. **Hear Feedback**: Friendly voice guides you

### Architecture
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Browser   │────▶│ WebSocket Server │────▶│ Voice Interface │
│  (Frontend UI)  │◀────│   (Bridge)       │◀────│   (Backend)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │  NLP Pipeline   │
                                                  │ & NixOS Backend │
                                                  └─────────────────┘
```

## Common Voice Commands

### Email & Internet
- "I need to check my email" → Installs Firefox
- "Open the internet" → Installs web browser
- "I can't get online" → Troubleshoots network

### Video Calling
- "I want to video call my grandkids" → Installs Zoom
- "Set up video calls" → Helps with webcam setup
- "Help me with Skype" → Installs and configures Skype

### System Maintenance
- "Update my computer" → Safely updates NixOS
- "Is my computer safe?" → Checks security status
- "My WiFi isn't working" → Network troubleshooting

## Customization

### Voice Settings
Access settings with the gear icon (⚙️):
- **Speech Speed**: 50-200 words per minute
- **Volume**: 0-100% output level

### Adding Commands
Edit `voice_nlp_integration.py` to add translations:
```python
grandma_translations = {
    "your phrase": "nixos command",
    # Add more...
}
```

## Troubleshooting

### No Microphone Detected
1. Check microphone is connected
2. Run `arecord -l` to list devices
3. Ensure PulseAudio is running

### Voice Not Working
1. Test with demo mode first: `./start-voice-interface.sh demo`
2. Check WebSocket connection in browser console
3. Verify Python dependencies installed

### Can't Hear Responses
1. Check system volume
2. Test speakers with: `speaker-test`
3. Try Web Speech API fallback in browser

## Development

### Running Individual Components
```bash
# Voice processing only
python3 backend/python/voice_interface.py --test

# WebSocket server only
python3 backend/python/voice_websocket_server.py

# NLP testing
python3 backend/python/voice_nlp_integration.py
```

### Adding New Features
1. **Voice Corrections**: Edit `voice_corrections` dict
2. **Response Styles**: Modify `_adapt_response_for_voice()`
3. **New Intents**: Update knowledge engine patterns

## Privacy & Ethics

- **100% Local**: No cloud services, no data collection
- **Transparent**: All processing explained to user
- **Respectful**: Age-appropriate, dignified interactions
- **Empowering**: Teaches while helping

## Credits

Built with love for Grandma Rose and everyone who deserves accessible technology.

Part of the Luminous-Dynamics Sacred Trinity development model:
- **Human**: Vision and empathy
- **Claude**: Architecture and implementation  
- **Local LLM**: NixOS expertise

---

*"Technology should adapt to humans, not the other way around."*