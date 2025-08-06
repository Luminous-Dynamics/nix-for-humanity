# 🎓 Tutorials & Guides

*Step-by-step guides for using and extending Nix for Humanity*

## Overview

This section contains hands-on tutorials that walk you through specific tasks and features. Each tutorial is designed to be completed in 15-30 minutes.

## Tutorials

### Getting Started
1. **[Quick Start](./01-QUICK-START.md)** - Get up and running in 5 minutes
2. **[First Commands](./02-FIRST-COMMANDS.md)** - Essential NixOS operations
3. **[TUI Guide](./03-TUI-GUIDE.md)** - Using the terminal interface
4. **[Python Backend](./04-PYTHON-BACKEND.md)** - Enabling native performance

### Core Features
5. **[Natural Language](./05-NATURAL-LANGUAGE.md)** - How to talk to NixOS
6. **[Learning Mode](./06-LEARNING-MODE.md)** - Teaching the system your preferences
7. **[Voice Interface](./07-VOICE-INTERFACE.md)** - Speaking to your computer
8. **[Personality Modes](./08-PERSONALITY-MODES.md)** - Customizing responses

### Advanced Usage
9. **[Creating Plugins](./09-CREATING-PLUGINS.md)** - Extending functionality
10. **[Custom Personalities](./10-CUSTOM-PERSONALITIES.md)** - Building your own style
11. **[Integration Guide](./11-INTEGRATION-GUIDE.md)** - Using with other tools
12. **[Troubleshooting](./12-TROUBLESHOOTING.md)** - When things go wrong

### Development
13. **[Contributing Your First PR](./13-FIRST-PR.md)** - Join the project
14. **[Testing Guide](./14-TESTING-GUIDE.md)** - Writing and running tests
15. **[Documentation Guide](./15-DOCUMENTATION-GUIDE.md)** - Improving docs

## Tutorial Format

Each tutorial follows this structure:
- **Goal**: What you'll accomplish
- **Time**: Expected duration
- **Prerequisites**: What you need to know
- **Steps**: Numbered instructions
- **Verification**: How to check it worked
- **Next Steps**: Where to go from here

## Quick Examples

### Your First Command
```bash
# Install a package naturally
ask-nix "I need firefox for web browsing"

# The system understands intent, not just commands
ask-nix "help me edit videos"  # Suggests video editors
```

### Using the TUI
```bash
# Launch the beautiful interface
nix-tui

# Navigate with keyboard
# Tab - Switch panels
# Enter - Select
# / - Search
# ? - Help
```

### Enabling Voice
```bash
# Set up voice (one-time)
ask-nix --setup-voice

# Use voice commands
ask-nix --voice
# Say: "Install Visual Studio Code"
```

## Learning Paths

### For New Users
1. Quick Start → First Commands → Natural Language
2. Personality Modes → Learning Mode
3. Troubleshooting

### For Developers  
1. Quick Start → Python Backend → Creating Plugins
2. Contributing Your First PR → Testing Guide
3. Documentation Guide

### For Power Users
1. TUI Guide → Voice Interface → Custom Personalities
2. Integration Guide → Advanced Usage patterns

## Tips for Success

1. **Start Simple**: Don't try to learn everything at once
2. **Use Natural Language**: Speak normally, not in commands
3. **Let It Learn**: The more you use it, the smarter it gets
4. **Ask for Help**: "ask-nix help" is always available
5. **Experiment**: The system is forgiving and safe

---

*"The best way to learn is by doing."*

🌊 We flow with learning!