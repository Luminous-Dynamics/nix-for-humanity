# Frequently Asked Questions (FAQ)

## General Questions

### What is Luminous Nix?
Luminous Nix is a natural language interface for NixOS that lets you manage your system using plain English instead of complex commands. It's currently in alpha, demonstrating a new approach to system management.

### Is it production ready?
No, this is alpha software (v0.2.0). While core features work well, it's not recommended for production systems without thorough testing in your environment.

### How is this different from just using ChatGPT for NixOS commands?
- **Local execution**: Runs directly on your system, not through a web interface
- **NixOS-specific**: Deep understanding of NixOS, not general Linux
- **Privacy-first**: No data sent to cloud services
- **Integrated**: Direct system access, not just command generation
- **Learning**: Adapts to your specific system and preferences

### What's the catch?
- It's alpha software with ~15% test coverage
- Not all NixOS operations are supported yet
- Some features are experimental
- Performance varies based on hardware
- Requires Python 3.11+ and NixOS 24.05+

## Installation & Setup

### Why does installation take so long?
First installation downloads:
- Python dependencies (~200MB)
- AI models for NLP (300MB-2GB depending on selection)
- Package cache building (one-time)

Subsequent runs are much faster.

### Do I need special hardware?
Minimum requirements:
- 4GB RAM (8GB recommended)
- 2GB free disk space
- Any modern CPU (GPU not required)

### Can I use this on non-NixOS systems?
No, Luminous Nix is specifically designed for NixOS and uses NixOS-specific APIs.

### Why do I need to use nix-shell?
The nix-shell provides system dependencies that aren't available in the base Python environment, ensuring consistent behavior across different systems.

## Usage Questions

### How natural can my commands be?
Very natural! These all work:
- "install firefox"
- "please install firefox for me"
- "I need a web browser"
- "can you set up firefox?"

### What if it doesn't understand me?
Try:
1. Rephrasing your request
2. Being more specific
3. Using simpler language
4. Checking the [command examples](basic-usage.md)

### Can I undo operations?
Yes, NixOS generations are preserved:
- `ask-nix "rollback"` - Go to previous generation
- `ask-nix "list generations"` - See available rollbacks
- Standard NixOS rollback always works

### Is it safe to experiment?
Yes! Luminous Nix:
- Previews changes before applying
- Preserves NixOS generations for rollback
- Validates dangerous operations
- Runs in user space (except system changes)

## Features & Capabilities

### What actually works today?
See [Feature Status](../features/FEATURE_STATUS.md) for a complete list. Core working features:
- Package installation/removal/search
- Configuration generation
- Error translation
- Beautiful TUI
- Basic personas

### What's the voice interface status?
Experimental (40% complete):
- Architecture is ready
- Whisper (speech-to-text) integrated
- Piper (text-to-speech) integrated
- Needs polish and testing
- Requires manual model download

### How does the learning system work?
Currently session-only:
- Learns your command patterns
- Adapts responses to your style
- Suggests based on history
- Resets when you restart (persistent memory coming in v0.3.0)

### What are personas?
Adaptive interfaces for different users:
- Grandma Rose: Voice-first, gentle
- Maya: Fast, ADHD-friendly
- Alex: Screen reader optimized
- Dr. Sarah: Technical, precise
- Others in development

## Technical Questions

### What's this "10x-1500x performance improvement"?
We use native Python-Nix API instead of subprocess calls:
- Direct API: ~10ms response
- Subprocess: 100ms-15s (can timeout)
- Measured on real operations
- Most noticeable on complex commands

### Why Python instead of Rust/Go/Haskell?
- NixOS 25.11 has native Python API (nixos-rebuild-ng)
- Fast development with AI assistance
- Rich ecosystem for NLP/AI
- Good enough performance with native API
- Easy for contributors

### How does AI assistance work in development?
The "Sacred Trinity" approach:
1. Human (Tristan): Vision and testing
2. Claude AI: Code generation and problem-solving
3. Local LLM: NixOS domain expertise

This enables solo developer productivity equivalent to small team.

### Is my data safe?
Yes:
- 100% local processing
- No cloud dependencies
- No telemetry
- Open source for auditing
- You own all your data

## Troubleshooting

### "Command not found"
Make sure you're:
1. In the project directory
2. Inside nix-shell
3. Using poetry run prefix

### "Import error"
Try:
```bash
poetry install --no-cache
```

### "Slow performance"
Enable native backend:
```bash
export NIX_HUMANITY_PYTHON_BACKEND=true
```

### "Voice not working"
1. Download required models:
   ```bash
   poetry run ask-nix --setup-voice
   ```
2. Check microphone permissions
3. See [Voice Setup Guide](voice-setup.md)

## Contributing & Community

### How can I help?
- Test and report bugs
- Improve documentation
- Add NixOS command coverage
- Contribute to personas
- Share your experience

### Where do I report bugs?
[GitHub Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)

### Is there a roadmap?
Yes! See [UNIFIED_VISION_AND_REALITY.md](../../UNIFIED_VISION_AND_REALITY.md) for the complete roadmap from alpha to v1.0.

### Who's behind this?
- **Creator**: Tristan Stoltz
- **AI Partner**: Claude (Anthropic)
- **Inspiration**: NixOS community
- **Model**: Solo developer + AI collaboration

### Why "Luminous" and "Sacred" terminology?
The project explores consciousness-first computing - technology that respects human attention and cognitive rhythms. The terminology reflects this philosophy while building practical tools.

## Philosophy Questions

### What's "consciousness-first computing"?
Design philosophy that prioritizes:
- Human attention and cognitive rhythms
- Progressive complexity
- User agency
- Educational interactions
- Privacy and local-first

See [Philosophy Docs](../philosophy/) for deep dive.

### Do I need to believe in the philosophy to use it?
No! The tool works regardless of philosophy. Use what serves you, ignore what doesn't.

### Is this trying to be sentient/conscious?
No. It's a tool that respects human consciousness, not claiming its own.

---

*FAQ for Luminous Nix v0.2.0-alpha*
*Last updated: 2025-08-24*

**Have a question not answered here?** [Ask on GitHub](https://github.com/Luminous-Dynamics/luminous-nix/issues)