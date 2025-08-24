# Luminous Nix User Documentation

Welcome to the user documentation for Luminous Nix - your natural language interface to NixOS.

## 🚀 Getting Started

- **[Installation Guide](installation.md)** - Set up Luminous Nix on your system
- **[Quick Start](../../QUICKSTART.md)** - 5 minutes to your first commands
- **[Basic Usage](basic-usage.md)** - Common tasks and commands
- **[FAQ](faq.md)** - Frequently asked questions

## 📚 Learning Path

### Beginner (Start Here)
1. [Installation](installation.md)
2. [Your First Commands](basic-usage.md#first-commands)
3. [Understanding Responses](basic-usage.md#understanding-responses)
4. [Getting Help](basic-usage.md#getting-help)

### Intermediate
1. [Advanced Package Management](advanced-usage.md#packages)
2. [Configuration Generation](advanced-usage.md#configuration)
3. [Using the TUI](tui-guide.md)
4. [Customizing Behavior](customization.md)

### Advanced
1. [Voice Interface Setup](voice-setup.md)
2. [Creating Plugins](../technical/plugin-development.md)
3. [Performance Tuning](performance.md)
4. [Troubleshooting](troubleshooting.md)

## 🎯 Common Tasks

### Package Management
- Install software: `ask-nix "install firefox"`
- Search packages: `ask-nix "find text editors"`
- Remove packages: `ask-nix "uninstall vim"`
- List installed: `ask-nix "what's installed?"`

### System Configuration
- Enable services: `ask-nix "enable docker"`
- Generate configs: `ask-nix "create nginx config"`
- Check system: `ask-nix "check for problems"`

### Getting Information
- Package details: `ask-nix "tell me about postgresql"`
- System status: `ask-nix "system health"`
- Available updates: `ask-nix "check for updates"`

## 🎨 User Interfaces

### Command Line (CLI)
The primary interface - just type naturally:
```bash
ask-nix "your request here"
```

### Terminal UI (TUI)
Beautiful visual interface:
```bash
nix-tui
```

### Voice Interface (Experimental)
Hands-free operation:
```bash
ask-nix --voice
```

## ⚡ Performance Tips

1. **Enable Native Backend**: 
   ```bash
   export NIX_HUMANITY_PYTHON_BACKEND=true
   ```

2. **Use Cache**: Package searches are cached automatically

3. **Batch Operations**: Combine related tasks in one command

## 🆘 Getting Help

### Within Luminous Nix
- `ask-nix "help"` - Show available commands
- `ask-nix "explain [error]"` - Understand error messages
- `ask-nix --debug` - Enable debug output

### Documentation
- [Troubleshooting Guide](troubleshooting.md) - Common issues
- [FAQ](faq.md) - Frequently asked questions
- [Feature Status](../features/FEATURE_STATUS.md) - What's working

### Community
- [GitHub Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- [Discord Server](#) (Coming soon)
- [Forum](#) (Coming soon)

## 📊 Understanding Feature Status

Features are marked with status indicators:
- 🟢 **Ready** - Stable, use freely
- 🟡 **Experimental** - Works but may change
- 🔴 **Planned** - Not yet available

See [Feature Status](../features/FEATURE_STATUS.md) for details.

## 🔐 Privacy & Security

- **100% Local**: No data leaves your machine
- **Open Source**: Audit the code yourself
- **Safe Defaults**: Dangerous operations require confirmation
- **Audit Trail**: All commands are logged

## 📈 Improving Your Experience

Luminous Nix learns from your usage (locally):
1. Command patterns are remembered
2. Preferences adapt to your style
3. Suggestions improve over time

Note: Learning is currently session-only. Persistent memory coming in v0.3.0.

## 🤝 Contributing

Found a bug? Have a suggestion? Want to help?
- [Report Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Development Docs](../technical/)

---

*Documentation for Luminous Nix v0.2.0-alpha*
*Last updated: 2025-08-24*