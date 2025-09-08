# ❓ Luminous Nix - Frequently Asked Questions

## 🚀 Getting Started

### Q: What is Luminous Nix?
**A:** Luminous Nix is a natural language interface for NixOS. Instead of memorizing commands, just say what you want in plain English!

### Q: How is this different from regular NixOS?
**A:** Traditional NixOS:
```bash
nix-env -iA nixos.firefox  # Cryptic!
```
Luminous Nix:
```bash
ask-nix "install firefox"  # Natural!
```

### Q: Do I need to know NixOS to use this?
**A:** No! That's the whole point. Luminous Nix translates your natural language into NixOS commands.

### Q: What version of NixOS do I need?
**A:** NixOS 23.11 or newer. We're optimized for 25.11 with the new Python-based nixos-rebuild.

## 🔧 Installation Issues

### Q: I get "No module named luminous_nix"
**A:** You need to run with Poetry:
```bash
poetry install
poetry run ask-nix "your command"
# OR
./bin/ask-nix "your command"  # This wrapper uses Poetry
```

### Q: I get "profile incompatible with nix-env"
**A:** You're using the new Nix profile system. Luminous Nix handles this automatically! If you see this error, the fix is already implemented.

### Q: Installation is taking forever
**A:** First time setup downloads dependencies. This is normal and only happens once. Future runs will be 2-5 seconds.

### Q: I get "nix-shell: command not found"
**A:** Make sure Nix is installed:
```bash
curl -L https://nixos.org/nix/install | sh
```

## 💬 Natural Language

### Q: What kinds of commands can I use?
**A:** Anything! Examples:
- "install firefox"
- "i need a text editor"
- "search for music players"
- "remove steam"
- "update my system"
- "what do i have installed?"

### Q: Do I need exact command names?
**A:** No! Luminous Nix understands variations:
- "install vim" ✅
- "i want vim" ✅
- "get me vim please" ✅
- "can you install vim for me?" ✅

### Q: Can I install multiple packages at once?
**A:** Yes!
```bash
ask-nix "install firefox, vscode, and discord"
ask-nix "i need git vim and tmux"
```

### Q: What if it doesn't understand me?
**A:** Try being more specific:
```bash
# Instead of: "get that browser thing"
ask-nix "install a web browser"

# Instead of: "the editor"  
ask-nix "install a text editor"
```

## 🐛 Common Errors

### Q: "Package not found"
**A:** The package name might be different in NixOS:
```bash
# Instead of "code"
ask-nix "install vscode"

# Instead of "postgres"
ask-nix "install postgresql"
```

### Q: "Permission denied"
**A:** Some operations need sudo. Luminous Nix will prompt you when needed.

### Q: Command times out
**A:** Large operations can take time. Use background mode:
```bash
LUMINOUS_BACKGROUND=true ask-nix "update system"
```

### Q: "Dry run" - nothing happened
**A:** You're in preview mode. To actually execute:
```bash
# Disable dry-run
LUMINOUS_DRY_RUN=false ask-nix "install firefox"

# Or just use the default
ask-nix "install firefox"  # Will ask for confirmation
```

## ⚙️ Configuration

### Q: How do I skip confirmations?
**A:**
```bash
LUMINOUS_SKIP_CONFIRM=true ask-nix "install htop"
```

### Q: How do I see what's happening?
**A:**
```bash
LUMINOUS_VERBOSE=2 ask-nix "install firefox"
```

### Q: Can I change the default behavior?
**A:** Yes! Create `~/.config/luminous-nix/config.yaml`:
```yaml
skip_confirmation: false
dry_run: false
verbose: 1
persona: developer  # or grandma_rose, etc.
```

### Q: What are personas?
**A:** Different interaction styles:
- `grandma_rose` - Extra gentle, voice-friendly
- `developer` - Technical, efficient
- `student` - Educational, explains everything
- More coming soon!

## 🎯 Advanced Usage

### Q: Can I use this in scripts?
**A:** Yes!
```bash
#!/bin/bash
export LUMINOUS_SKIP_CONFIRM=true
ask-nix "install htop"
ask-nix "install git"
```

### Q: Can I create custom commands?
**A:** Coming soon! Plugin system in development.

### Q: Does it work with flakes?
**A:** Yes! 
```bash
ask-nix "create flake for rust project"
ask-nix "update flake inputs"
```

### Q: Can it manage configurations?
**A:** Basic support:
```bash
ask-nix "enable ssh server"
ask-nix "configure firewall"
```

## 🔒 Privacy & Security

### Q: Does it send my commands anywhere?
**A:** No! Everything runs locally on your machine. No telemetry, no cloud, no tracking.

### Q: Is it safe to use?
**A:** Yes! It:
- Shows you commands before running
- Asks for confirmation
- Never runs anything without your permission
- Can preview with dry-run mode

### Q: Can I audit what it does?
**A:** Absolutely!
```bash
# See exact commands
LUMINOUS_VERBOSE=2 ask-nix "install firefox"

# Dry run first
LUMINOUS_DRY_RUN=true ask-nix "install firefox"
```

## 🤝 Contributing

### Q: How can I help?
**A:** Many ways!
- Report bugs
- Suggest features
- Improve documentation  
- Write code
- Test beta versions
- Share with others

### Q: I found a bug!
**A:** Please report it:
1. Check if it's already reported: [GitHub Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
2. Create new issue with:
   - Command you ran
   - Error message
   - NixOS version
   - Luminous Nix version

### Q: I have a feature idea!
**A:** We'd love to hear it! Open a [feature request](https://github.com/Luminous-Dynamics/luminous-nix/issues/new?template=feature_request.md)

### Q: Can I add support for my language?
**A:** Yes! Translations coming soon. For now, English only.

## 🆘 Still Stuck?

### Q: Where can I get help?
**A:** 
1. This FAQ
2. [GitHub Discussions](https://github.com/Luminous-Dynamics/luminous-nix/discussions)
3. Discord (coming soon)
4. Create an issue

### Q: Is there a video tutorial?
**A:** Coming soon! For now, check the [Cookbook](COOKBOOK.md) for examples.

### Q: Why "Luminous Nix"?
**A:** 
- **Luminous** = Illuminating, making clear
- **Nix** = The package manager
- Together: Making NixOS clear and accessible!

### Q: Is this an official NixOS project?
**A:** No, this is a community project to make NixOS more accessible. We love NixOS and want everyone to be able to use it!

## 💡 Tips & Tricks

### Speed Tips
```bash
# Alias for faster typing
alias nix="ask-nix"

# Then just:
nix "install firefox"
```

### Batch Operations
```bash
# Install development environment
ask-nix "install git, vim, tmux, nodejs, and docker"
```

### Learning Mode
```bash
# See what commands would run
LUMINOUS_VERBOSE=2 LUMINOUS_DRY_RUN=true ask-nix "install firefox"
```

---

*Don't see your question? Ask in [GitHub Discussions](https://github.com/Luminous-Dynamics/luminous-nix/discussions)!*

**Remember: There are no stupid questions, only opportunities to improve the docs!** 💡