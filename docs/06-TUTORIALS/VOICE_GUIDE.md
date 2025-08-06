# 🎤 Voice Interface Guide

*Natural conversation with NixOS through speech*

## Overview

The voice interface enables hands-free interaction with Nix for Humanity, perfect for accessibility needs, multitasking, or simply preferring to speak rather than type.

## Getting Started

### Enable Voice Mode

```bash
# In the TUI
Press Ctrl+V to toggle voice mode

# From CLI
ask-nix --voice

# Set as default
export NIX_HUMANITY_VOICE=enabled
```

### First-Time Setup

When you first enable voice:
1. Permission prompt for microphone access
2. Quick audio test to ensure quality
3. Optional voice calibration for better recognition

## How It Works

### Wake Word: "Hey Nix"

```
You: "Hey Nix"
System: *gentle chime* "I'm listening..."
You: "Install Firefox"
System: "I'll help you install Firefox. Should I proceed?"
You: "Yes"
System: "Installing Firefox now..."
```

### Continuous Mode

For extended conversations:
```
You: "Hey Nix, let's talk"
System: "I'm in conversation mode. Say 'goodbye' when done."
You: "What browsers are available?"
System: "I found Firefox, Chrome, Brave, and Vivaldi..."
You: "Tell me about Brave"
System: "Brave is a privacy-focused browser..."
```

## Voice Commands

### Natural Language Examples

**Software Installation**
- "Install a web browser"
- "I need something to edit photos"
- "Get me that Firefox thing"

**System Management**
- "Update my computer"
- "Check for updates"
- "How much space do I have?"

**Help & Information**
- "What can you do?"
- "Help me with WiFi"
- "Explain what a generation is"

### Voice Shortcuts

Some phrases trigger immediate actions:
- "Stop" - Cancels current operation
- "Repeat" - Says the last response again
- "Slower" - Speaks more slowly
- "Louder" - Increases volume

## Accessibility Features

### For Vision Impairment

**Screen Reader Integration**
- Full compatibility with Orca, NVDA, JAWS
- Announces all actions before executing
- Describes visual elements verbally

**Audio Cues**
- Different tones for different events
- Success: Rising chime
- Error: Gentle descending tone
- Waiting: Soft pulse

### For Hearing Impairment

**Visual Feedback**
- Live transcription of speech
- Visual indicators for system state
- Vibration patterns (if available)

**Adjustable Speech**
```bash
# Slow down speech
ask-nix --voice --speech-rate 0.8

# Use different voice
ask-nix --voice --speech-voice clara

# Enable captions
ask-nix --voice --show-captions
```

### For Motor Impairment

**Hands-Free Operation**
- No keyboard/mouse required
- Voice-only navigation
- Confirmation by voice

**Adjustable Timing**
```bash
# Longer pause before timeout
ask-nix --voice --listen-timeout 10

# Keep microphone open longer
ask-nix --voice --continuous
```

## Voice Personalities

The voice interface adapts its speaking style:

### Grandma Rose Mode
```
You: "Hey Nix, talk like you're explaining to grandma"
System: "Of course, dear! I'll speak slowly and clearly, and I'll explain everything simply."
```

### Professional Mode
```
You: "Use professional voice"
System: "Acknowledged. Switching to professional communication style."
```

### Conversational Mode
```
You: "Just talk normally"
System: "Sure thing! I'll keep it casual and friendly."
```

## Privacy & Voice

### Local Processing
- All speech recognition happens on your computer
- No audio ever sent to the cloud
- Uses Whisper AI model locally

### Privacy Controls
```bash
# Disable voice history
ask-nix --voice --no-history

# Clear voice data
ask-nix --clear-voice-data

# Voice privacy report
ask-nix --voice-privacy-report
```

## Troubleshooting

### Microphone Not Detected
```bash
# Check audio devices
ask-nix --check-audio

# Select specific microphone
ask-nix --voice --mic "Blue Yeti"

# Test microphone
ask-nix --test-mic
```

### Recognition Issues

**Background Noise**
- Use push-to-talk: Hold Space while speaking
- Enable noise cancellation: `--noise-cancel`
- Move to quieter location

**Accent/Dialect**
```bash
# Train on your voice
ask-nix --voice-training

# Select language variant
ask-nix --voice --language en-GB
ask-nix --voice --language es-MX
```

### Response Issues

**Can't Hear Responses**
```bash
# Check volume
ask-nix --check-speakers

# Test text-to-speech
ask-nix --test-speech "Hello, can you hear me?"

# Use different voice engine
ask-nix --voice --tts piper
```

## Advanced Features

### Voice Macros

Create custom voice commands:
```bash
# Define a macro
ask-nix --define-macro "morning routine" \
  "update system, check disk space, show weather"

# Use it
You: "Hey Nix, morning routine"
System: "Running your morning routine..."
```

### Multi-Language Support

```bash
# Set primary language
ask-nix --voice --language es

# Multi-language mode
ask-nix --voice --languages en,es,fr

# Auto-detect language
ask-nix --voice --auto-language
```

### Voice Profiles

Different profiles for different users:
```bash
# Create profile
ask-nix --create-voice-profile "Mom"

# Switch profiles
ask-nix --voice --profile "Mom"

# Each profile remembers:
# - Speech patterns
# - Preferred voice
# - Common commands
```

## Integration with Other Modes

### Voice + TUI
- Voice commands work in the TUI
- See transcription in real-time
- Switch between voice and typing seamlessly

### Voice + CLI
```bash
# Pipe voice to commands
ask-nix --voice --stream | grep "install"

# Voice input for scripts
PACKAGE=$(ask-nix --voice --single "What package do you want?")
```

## Best Practices

### Clear Communication
1. Speak naturally but clearly
2. Pause briefly after wake word
3. One command at a time
4. Use simple language

### Confirmation Strategy
- Always confirm destructive actions
- Visual + audio confirmation
- Allow "undo" when possible

### Error Recovery
```
You: "Install Firefax" (misspoken)
System: "Did you mean Firefox?"
You: "Yes"
System: "Installing Firefox..."
```

## Performance Optimization

### Reduce Latency
```bash
# Preload voice models
ask-nix --preload-voice

# Use smaller model for speed
ask-nix --voice --model whisper-tiny

# Enable GPU acceleration
ask-nix --voice --gpu
```

### Battery Optimization
```bash
# Power-saving mode
ask-nix --voice --power-save

# Reduce wake word sensitivity
ask-nix --voice --wake-sensitivity low
```

## Coming Soon

### Planned Features
- [ ] Custom wake words
- [ ] Voice authentication
- [ ] Emotional tone detection
- [ ] Multilingual conversations
- [ ] Voice shortcuts editor
- [ ] Offline voice packs

### Future Integrations
- Smart home control
- Calendar integration
- Reminder system
- Music control
- System automation

## FAQ

**Q: Does voice work offline?**
A: Yes! All processing is local. No internet required.

**Q: Can I change the voice?**
A: Yes, multiple voices available. Use `--list-voices`.

**Q: Is it always listening?**
A: No, only after wake word or in continuous mode.

**Q: Can others use voice on my system?**
A: Yes, with permission. Each user can have a profile.

**Q: How accurate is recognition?**
A: 95%+ for common commands, improves with use.

---

*"Technology should adapt to how humans naturally communicate - through speech, gesture, and intuition."*