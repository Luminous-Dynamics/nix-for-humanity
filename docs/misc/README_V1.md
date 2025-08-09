# 🗣️ Nix for Humanity v1.0

*Making NixOS accessible through natural conversation*

## What is Nix for Humanity?

A simple command-line tool that lets you manage NixOS using plain English instead of complex commands.

**Instead of**: `nix-env -iA nixpkgs.firefox`  
**Just say**: `ask-nix "install firefox"`

## ✨ Features (v1.0)

- **Natural Language**: Type what you want in plain English
- **Safe by Default**: Preview commands before they run
- **Helpful Errors**: Clear explanations when something goes wrong
- **Basic Operations**: Install, search, update, and troubleshoot

## 🚀 Quick Start

```bash
# Install
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
nix develop

# Use it
ask-nix "install firefox"
ask-nix "search for text editors"
ask-nix "update my system"
ask-nix "why is my wifi not working?"
```

## 📋 Supported Commands

### Package Management
- Install packages: `"install firefox"`
- Search packages: `"search for editors"`
- Remove packages: `"remove firefox"`
- Update system: `"update my system"`

### Getting Help
- Show help: `"help"`
- Troubleshooting: `"my wifi isn't working"`
- Learn about NixOS: `"what are generations?"`

## 🛡️ Safety First

Every command shows you what it will do before running:

```
You asked: "install firefox"

I'll run this command:
  nix-env -iA nixpkgs.firefox

This will install Firefox web browser.

Proceed? (y/n):
```

## 🎯 Project Status

**Version**: 1.0 (Foundation Release)  
**Focus**: Core functionality that works reliably  
**Philosophy**: Better to do a few things well than many things poorly

### What's NOT in v1.0
- No graphical interface (CLI only)
- No voice control
- No learning from your preferences
- No advanced AI features

These features are preserved for future versions. See our [Version Roadmap](VERSION_ROADMAP.md) for what's coming.

## 💖 Contributing

We welcome contributions! The codebase is organized to preserve all work while focusing on v1.0:

- `src/` - Active v1.0 code only
- `features/` - Future features preserved with love
- `tests/v1.0/` - Current tests

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 🌟 Vision

While v1.0 is intentionally simple, our vision is grand: AI-powered assistance that makes NixOS accessible to everyone, from command-line experts to grandmothers.

Learn more in our [Feature Preservation Manifest](FEATURE_PRESERVATION_MANIFEST.md).

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

**Remember**: Technology should make life easier, not harder. That's what v1.0 delivers.