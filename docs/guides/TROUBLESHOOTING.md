# 🔧 Troubleshooting Guide - Nix for Humanity

## Quick Diagnostics

Run this command to check your system:
```bash
nix-for-humanity diagnose
```

Or manually check:
```bash
# Service status
systemctl status nix-for-humanity

# Voice recognition test
nix-for-humanity test-voice

# NLP engine test
echo "install firefox" | nix-for-humanity test-nlp
```

## Common Issues

### 🎤 Voice Recognition Problems

#### "Not understanding my voice"

**Quick fixes:**
1. Try text input instead (always works!)
2. Check microphone permissions:
   ```bash
   # Test microphone
   arecord -d 5 test.wav && aplay test.wav
   ```
3. Reduce background noise
4. Speak slightly slower
5. Try rephrasing naturally

**Technical checks:**
```bash
# Check if Whisper is loaded
nix-for-humanity status whisper

# Test with sample audio
nix-for-humanity test-voice --file samples/clear-speech.wav
```

#### "Microphone not detected"

**Solutions:**
1. Text input works without microphone!
2. Check system audio:
   ```bash
   # List audio devices
   pactl list sources
   
   # Test microphone
   parecord test.wav
   ```
3. Grant microphone permission in browser
4. Try different browser (Firefox/Chrome)

### 💬 Natural Language Understanding

#### "Command not recognized"

**Common causes and fixes:**

1. **Too technical:**
   - ❌ "sudo nix-env -iA nixpkgs.firefox"
   - ✅ "install firefox"

2. **Too vague:**
   - ❌ "fix it"
   - ✅ "fix my internet connection"

3. **Multiple commands:**
   - ❌ "install firefox and vscode and update system"
   - ✅ Say each command separately

**Debug NLP:**
```bash
# Test intent recognition
nix-for-humanity debug-nlp "your command here"

# See confidence scores
nix-for-humanity debug-nlp --verbose "install firefox"
```

#### "Wrong action performed"

1. Use clearer language
2. Report the issue to improve system:
   ```bash
   nix-for-humanity report-intent \
     --said "get me online" \
     --expected "connect to wifi" \
     --got "install online-game"
   ```

### 🚀 Performance Issues

#### "Slow response time"

**Expected times:**
- Voice recognition: <500ms
- Intent processing: <100ms
- Command execution: varies

**Speed up:**
1. First run indexes packages (one-time, ~30s)
2. Disable animations:
   ```nix
   services.nix-for-humanity.animations = false;
   ```
3. Use text instead of voice for faster input
4. Check system resources:
   ```bash
   htop  # Check CPU/RAM
   ```

#### "High CPU usage"

```bash
# Check what's running
nix-for-humanity status --processes

# Limit concurrent operations
services.nix-for-humanity.maxConcurrent = 2;
```

### 🔒 Permission Issues

#### "Cannot install packages"

1. **Check user permissions:**
   ```bash
   # Are you in wheel group?
   groups | grep wheel
   ```

2. **Test with simple package:**
   ```bash
   nix-for-humanity test-install hello
   ```

3. **Check Polkit rules:**
   ```bash
   pkaction --verbose --action-id org.nixos.nix-for-humanity
   ```

#### "Authentication failed"

1. Voice commands require confirmation for system changes
2. Text "yes" or say "yes" when prompted
3. For GUI-less systems, use text confirmation

### 🌐 Network Problems

#### "Cannot search packages"

1. **Update channels:**
   ```bash
   sudo nix-channel --update
   ```

2. **Check internet:**
   ```bash
   ping nixos.org
   ```

3. **Try offline mode:**
   ```bash
   nix-for-humanity --offline "list installed packages"
   ```

### ⚙️ Service Issues

#### "Service won't start"

1. **Check logs:**
   ```bash
   journalctl -xeu nix-for-humanity
   ```

2. **Common fixes:**
   ```bash
   # Port conflict (default: 3456)
   lsof -i :3456
   
   # Change port in configuration.nix:
   services.nix-for-humanity.port = 3457;
   ```

3. **Reinstall:**
   ```bash
   sudo systemctl stop nix-for-humanity
   sudo nixos-rebuild switch
   ```

#### "Service crashes"

1. **Check resources:**
   ```bash
   # Memory
   free -h
   
   # Disk space
   df -h /
   ```

2. **Reset database:**
   ```bash
   nix-for-humanity reset-db
   ```

### 🌈 GUI Learning Issues

#### "GUI elements not appearing"

This is normal! GUI elements appear gradually:
- Week 1: Voice/text only
- Week 2-3: Visual confirmations appear
- Month 2+: More GUI elements
- Month 6+: GUI fades as you master voice

Force GUI elements (if needed):
```nix
services.nix-for-humanity.gui.forceShow = true;
```

#### "GUI too complex"

Reduce GUI complexity:
```nix
services.nix-for-humanity.gui.level = "minimal";
```

### 🔐 Security Concerns

#### "Is my voice data safe?"

✅ **Yes! Everything is local:**
- Voice processing: Local Whisper.cpp
- NLP: Local processing
- No cloud services by default
- No data collection

Verify:
```bash
# Check network connections
netstat -tulpn | grep nix-for-humanity

# Should only show local ports (3456-3459)
```

### ♿ Accessibility Problems

#### "Screen reader not working"

1. **Test screen reader mode:**
   ```bash
   nix-for-humanity --screen-reader test
   ```

2. **Enable enhanced descriptions:**
   ```nix
   services.nix-for-humanity.accessibility = {
     screenReader = true;
     verboseDescriptions = true;
   };
   ```

#### "Keyboard navigation broken"

1. Test keyboard-only mode:
   - Tab: Next element
   - Shift+Tab: Previous
   - Enter: Activate
   - Escape: Cancel

2. Reset focus:
   ```
   Press Escape twice, then Tab
   ```

## Debug Mode

### Enable verbose logging:
```nix
services.nix-for-humanity = {
  debug = true;
  logLevel = "trace";
};
```

### View detailed logs:
```bash
# Real-time logs
journalctl -fu nix-for-humanity

# NLP debugging
nix-for-humanity debug-nlp --trace "install firefox"

# Voice debugging  
nix-for-humanity debug-voice --save-audio
```

### Client-side debugging:
```javascript
// In browser console
localStorage.setItem('nfh-debug', 'true');
location.reload();
```

## Getting Help

### Before asking for help:

1. **Run diagnostics:**
   ```bash
   nix-for-humanity diagnose > diagnostic.log
   ```

2. **Collect info:**
   ```bash
   nix-for-humanity --version
   nixos-version
   nix-info -m
   ```

3. **Test basic command:**
   ```bash
   echo "help" | nix-for-humanity test-nlp
   ```

### Where to get help:

1. **Built-in help:**
   - Say: "help"
   - Say: "what can you do"
   - Say: "how do I..."

2. **Documentation:**
   - [User Guide](USER_GUIDE.md)
   - [FAQ](FAQ.md)
   - [Voice Commands](VOICE_COMMANDS.md)

3. **Community:**
   - GitHub Issues: [Report bugs](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)
   - Discord: [Join chat](https://discord.gg/nix-for-humanity)
   - Forum: [NixOS Discourse](https://discourse.nixos.org/c/nix-for-humanity)

### Reporting bugs:

Include:
1. What you said/typed
2. What you expected
3. What actually happened
4. Diagnostic output
5. Your configuration

Template:
```markdown
**Description:** 
I said "install Firefox" but nothing happened

**Expected:** 
Firefox should install

**Actual:** 
System said "I don't understand"

**System info:**
- Nix for Humanity: v1.0.0
- NixOS: 24.05
- Microphone: Blue Yeti

**Diagnostics:**
[Attach diagnostic.log]
```

## Emergency Recovery

### If system becomes unusable:

1. **Disable voice mode:**
   ```bash
   nix-for-humanity --text-only
   ```

2. **Stop service:**
   ```bash
   sudo systemctl stop nix-for-humanity
   ```

3. **Boot previous generation:**
   - Reboot
   - Hold Shift at boot
   - Select previous generation

4. **Remove from configuration:**
   ```nix
   # Comment out in configuration.nix
   # services.nix-for-humanity.enable = true;
   
   sudo nixos-rebuild switch
   ```

5. **Complete removal:**
   ```bash
   sudo rm -rf /var/lib/nix-for-humanity
   sudo rm -rf ~/.config/nix-for-humanity
   ```

## Tips for Success

### Voice Tips:
- 🎤 Speak naturally, like talking to a friend
- 🔇 Pause briefly after activating microphone
- 📝 Text input always available as backup
- 🌍 Works with accents and speech patterns

### Command Tips:
- 💬 Use simple, clear language
- 🎯 One task at a time
- ❓ Ask for help when unsure
- 🔄 Rephrase if not understood

### Learning Tips:
- 👀 Watch what commands are run
- 📚 GUI elements teach patterns
- 🎓 Graduate to voice-only over time
- 🏆 System adapts to your style

---

Remember: **There's no wrong way to ask!** The system learns from every interaction.

*Still having issues? Just say "help" or visit our [Discord](https://discord.gg/nix-for-humanity)*