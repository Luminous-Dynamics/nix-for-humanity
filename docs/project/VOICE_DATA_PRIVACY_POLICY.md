# 🔒 Voice Data Privacy Policy - Nix for Humanity

## Our Commitment

Your voice is yours. Your words are yours. Your privacy is sacred.

Nix for Humanity processes all voice data locally on your computer. We never record, store, or transmit your voice to any external service unless you explicitly enable cloud features.

## Key Privacy Principles

### 1. Local Processing by Default
- ✅ Voice recognition happens on YOUR computer
- ✅ Uses Whisper.cpp running locally
- ✅ No internet connection required
- ✅ Works completely offline

### 2. No Voice Recording
- ✅ Voice is converted to text immediately
- ✅ Audio data is discarded after processing
- ✅ No voice files saved anywhere
- ✅ No voice fingerprinting or profiling

### 3. Text Privacy
- ✅ Converted text stays on your computer
- ✅ Command history stored locally only
- ✅ You control all data retention
- ✅ Easy to delete all history

## What Happens to Your Voice

```
Your Voice → Microphone → Whisper.cpp → Text → Discarded
                                           ↓
                                    Natural Language Processing
                                           ↓
                                      System Action
```

### Step by Step:
1. **You speak** into your microphone
2. **Whisper.cpp converts** speech to text locally
3. **Audio is immediately deleted** from memory
4. **Text is processed** to understand intent
5. **Action is performed** on your system
6. **Text may be logged** locally for history (optional)

## Data We DO NOT Collect

- ❌ Voice recordings
- ❌ Voice characteristics
- ❌ Speech patterns
- ❌ Accent information
- ❌ Background audio
- ❌ Ambient sounds
- ❌ Other speakers
- ❌ Any audio data

## Data We Process Locally

- ✅ Converted text from speech
- ✅ Recognized commands
- ✅ System responses
- ✅ Error messages
- ✅ Usage patterns (local only)

## Optional Cloud Features

If you explicitly enable cloud AI assistance:

### What Changes:
- Text of commands may be sent to AI service
- Voice audio is NEVER sent
- Only sanitized text is transmitted
- Personal information is stripped

### Privacy Safeguards:
- Opt-in only (disabled by default)
- Clear consent required
- See exactly what's sent
- Delete cloud history anytime
- Use privacy-focused AI services only

### Recommended Cloud Services:
1. **Anthropic Claude** - No training on user data
2. **Local Ollama** - Self-hosted models
3. **Privacy-focused alternatives**

## Your Rights

### You Can Always:
- ✅ Disable voice input completely
- ✅ Use text-only interaction
- ✅ Delete all command history
- ✅ See all stored data
- ✅ Export your data
- ✅ Remove the software entirely

### Access Your Data:
```bash
# View command history
cat ~/.config/nix-for-humanity/history.json

# Delete all history
rm ~/.config/nix-for-humanity/history.json

# Disable voice completely
echo "voice_enabled: false" > ~/.config/nix-for-humanity/config.yaml
```

## Security Measures

### Voice Input Security:
- Microphone access requires explicit permission
- Visual indicator when microphone is active
- One-click to stop listening
- Automatic timeout after silence
- No background listening

### Data Protection:
- All local data encrypted at rest
- Memory cleared after processing
- No temporary audio files
- Secure inter-process communication
- Regular security audits

## Children's Privacy

- No special processing for children's voices
- No age detection or profiling
- Same privacy protections for all users
- Parental controls available

## Accessibility Privacy

For users with speech differences:
- No storage of speech patterns
- No adaptation data saved
- No medical information inferred
- Equal privacy for all users

## Updates to This Policy

- Policy updates announced in release notes
- Major changes require user consent
- Previous versions available in git history
- User notification for any changes

## Contact

Privacy questions or concerns:
- Email: privacy@luminousdynamics.org
- GitHub: https://github.com/Luminous-Dynamics/nix-for-humanity/issues
- Documentation: See SECURITY.md

## Summary

**Your voice stays yours. Always.**

- 🏠 Everything happens locally
- 🎤 No voice recording ever
- 📝 Only text is processed
- 🗑️ Audio immediately deleted
- 🔐 You control all data
- ☁️ Cloud is optional and transparent

## Technical Implementation

```rust
// Voice processing pipeline
impl VoiceProcessor {
    fn process_audio(&mut self, audio: AudioBuffer) -> Result<String> {
        // Convert to text
        let text = self.whisper.transcribe(&audio)?;
        
        // CRITICAL: Clear audio from memory immediately
        audio.secure_clear();
        drop(audio);
        
        // Return only text
        Ok(text)
    }
    
    // No methods for:
    // - save_audio()
    // - store_voice()
    // - upload_recording()
    // These don't exist by design
}
```

---

*Last updated: 2025-07-23*

*"Privacy is not optional. It's fundamental."*