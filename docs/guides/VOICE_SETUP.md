# 🎤 Voice Setup Guide - Nix for Humanity

## Overview

Voice input is one of two equal ways to interact with Nix for Humanity (the other being text). This guide helps you set up voice recognition for natural language commands.

**Remember**: Voice is completely optional. Everything works perfectly with text input alone.

## 🚀 Quick Setup

### 1. Check Your Microphone

```bash
# Test if NixOS detects your microphone
arecord -l

# Test recording (speak for 5 seconds)
arecord -d 5 test.wav
aplay test.wav  # Should hear your recording
```

### 2. Grant Microphone Permission

When you first use voice:
1. Click the microphone button
2. Your browser/system will ask for permission
3. Click "Allow" to enable voice input
4. You'll see a visual indicator when listening

### 3. Test Voice Input

Say or type: "Hey Nix, can you hear me?"

Expected response: "Yes, I can hear you clearly!"

## 🎯 Optimizing Voice Recognition

### Microphone Placement
- **Ideal**: 6-12 inches from mouth
- **Angle**: Pointed toward you, not up/down
- **Position**: Avoid being directly in front (breathing sounds)

### Environment Setup
- **Quiet room**: Reduces recognition errors
- **Consistent background**: AC/fan noise is OK if constant
- **Avoid**: Echo-prone rooms, multiple speakers

### Speaking Tips
- **Natural pace**: Don't speak too fast or slow
- **Clear articulation**: But don't over-pronounce
- **Natural language**: "install firefox" not "INSTALL. FIREFOX."
- **Continuous phrases**: Better than word-by-word

## 🔧 Advanced Configuration

### Selecting Audio Device

If you have multiple microphones:

```bash
# List all audio inputs
pactl list sources short

# Set default input
pactl set-default-source <device_name>
```

### Adjusting Microphone Sensitivity

```bash
# Open audio mixer
alsamixer

# Or use GUI
pavucontrol
```

Tips:
- Set input level to ~70%
- Enable noise reduction if available
- Disable AGC (Automatic Gain Control) if it causes issues

### Voice Activation Threshold

In settings, adjust:
- **Sensitivity**: Lower = more sensitive
- **Silence threshold**: How long before stopping
- **Wake words**: "Hey Nix" or custom phrase

## 🌍 Language and Accent Support

### Supported Languages
Currently: English (US, UK, AU, IN)
Coming soon: Spanish, French, German, Mandarin

### Accent Adaptation
The system learns your accent over time:
1. Use it regularly for a week
2. Corrections help it learn
3. Personal model improves accuracy

### If Recognition Struggles
- Speak slightly slower
- Emphasize problem words
- Use text for specific terms
- Train custom vocabulary

## 🔒 Privacy & Security

### Local Processing
- **Whisper.cpp** runs entirely on your computer
- **No cloud services** unless explicitly enabled
- **No recordings saved** without permission
- **Processing stops** when mic is off

### What We Process
```
Your voice → Local Whisper.cpp → Text → NLP Engine → Action
     ↓
 (Discarded)
```

### Privacy Controls
- Microphone LED/indicator when active
- Click to stop listening anytime
- Keyboard shortcut to toggle (Ctrl+Shift+M)
- Complete voice disable option

## 🚑 Troubleshooting

### "No microphone detected"

1. Check physical connection
2. Verify in system settings:
   ```bash
   # Check if detected
   arecord -l
   
   # Check PulseAudio
   pactl info
   ```

3. Install missing drivers:
   ```nix
   # In configuration.nix
   hardware.pulseaudio.enable = true;
   # or
   services.pipewire.enable = true;
   ```

### "Poor recognition accuracy"

1. **Check microphone quality**:
   ```bash
   # Record sample
   arecord -f cd -d 10 test.wav
   # Check for clarity, volume, noise
   ```

2. **Adjust input level**:
   - Too low = missed words
   - Too high = distortion
   - Aim for -12dB peaks

3. **Reduce background noise**:
   - Close windows
   - Turn off fans temporarily
   - Use directional microphone

### "Voice not responding"

1. Check browser permissions
2. Verify service is running:
   ```bash
   systemctl status nix-for-humanity-voice
   ```
3. Try text input to verify system works
4. Restart voice service

### "Works in text but not voice"

This indicates voice recognition issue, not NLP:
1. Test microphone with other apps
2. Check Whisper.cpp logs
3. Try simpler commands first
4. Verify language settings

## 🎯 Best Practices

### DO:
- ✅ Speak naturally
- ✅ Use complete phrases
- ✅ Pause between commands
- ✅ Keep microphone consistent

### DON'T:
- ❌ Shout or whisper
- ❌ Talk over system responses
- ❌ Use computer-speak
- ❌ Move mic while talking

## 📊 Performance Expectations

With proper setup:
- **Recognition delay**: 200-500ms
- **Accuracy**: 95%+ for common commands
- **Accent learning**: Improves over 1-2 weeks
- **CPU usage**: 5-15% while listening

## 🆘 Getting Help

If voice issues persist:

1. **Use text input** - Everything works without voice
2. **Check documentation** - This guide + troubleshooting
3. **Community support** - Discord #voice-help channel
4. **Report issues** - GitHub with mic model, OS version

Remember: Voice is just one option. The goal is natural language understanding, whether typed or spoken.

---

*"The best voice interface is one that understands you, not one you have to understand."*