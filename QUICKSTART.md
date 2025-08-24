# Luminous Nix Quick Start - 5 Minutes to Success

Get Luminous Nix running and experience natural language NixOS management in just 5 minutes.

## ✅ What You'll Be Able to Do

After this quickstart, you'll be able to:
- Install packages with plain English
- Search for software by description
- Use the beautiful terminal UI
- Get helpful error explanations

## 📋 Prerequisites (30 seconds)

You need:
- NixOS 24.05 or later
- Python 3.11+
- Internet connection (for package downloads)
- Terminal access

## 🚀 Installation (2 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix

# 2. Enter the Nix development shell (provides dependencies)
nix-shell

# 3. Install Python dependencies
poetry install

# 4. Verify installation
poetry run ask-nix --version
```

## 🎯 Your First Commands (2 minutes)

### Install a Package
```bash
poetry run ask-nix "install firefox"
# or try:
poetry run ask-nix "install a web browser"
```

### Search for Software
```bash
poetry run ask-nix "find markdown editors"
# or:
poetry run ask-nix "search for text editors"
```

### List Installed Packages
```bash
poetry run ask-nix "what's installed?"
# or:
poetry run ask-nix "show my packages"
```

### Get Help
```bash
poetry run ask-nix "help"
# or:
poetry run ask-nix "what can you do?"
```

## 🎨 Try the Beautiful TUI (30 seconds)

Launch the terminal user interface:
```bash
poetry run nix-tui
```

Navigation:
- `↑/↓` - Navigate options
- `Enter` - Select
- `Tab` - Switch panels
- `q` - Quit
- `?` - Show help

## 💡 Pro Tips (30 seconds)

### Use Natural Language
Don't worry about exact commands. These all work:
- "install git"
- "please install git"
- "I need git"
- "can you install git for me?"

### Educational Errors
When something goes wrong, Luminous Nix explains why:
```bash
poetry run ask-nix "install nonexistent-package"
# Returns helpful explanation about package not being found
```

### Quick Performance Mode
For faster responses, use the native Python backend:
```bash
export NIX_HUMANITY_PYTHON_BACKEND=true
poetry run ask-nix "install vim"
```

## 🎯 Common Tasks

### Install Development Tools
```bash
poetry run ask-nix "install python development tools"
poetry run ask-nix "set up javascript environment"
poetry run ask-nix "install rust toolchain"
```

### System Management
```bash
poetry run ask-nix "check for broken packages"
poetry run ask-nix "clean up old packages"
poetry run ask-nix "update package list"
```

### Configuration Help
```bash
poetry run ask-nix "how do I enable docker?"
poetry run ask-nix "generate nginx config"
poetry run ask-nix "set up postgresql"
```

## ⚠️ Important Notes

### This is Alpha Software
- Some features are experimental
- Not all NixOS operations are supported yet
- Please report bugs on GitHub

### Performance Varies
- First run may be slower (downloading models)
- Performance depends on your hardware
- Use native backend for best speed

### Privacy First
- Everything runs locally
- No data sent to cloud services
- Your commands stay on your machine

## 🆘 Troubleshooting

### Command Not Found
```bash
# Make sure you're in the project directory
cd luminous-nix
# And in the nix-shell
nix-shell
```

### Poetry Not Found
```bash
# Install poetry if needed
nix-shell -p poetry
```

### Slow Performance
```bash
# Enable native backend
export NIX_HUMANITY_PYTHON_BACKEND=true
```

### Import Errors
```bash
# Reinstall dependencies
poetry install --no-cache
```

## 📚 Next Steps

Now that you have Luminous Nix running:

1. **Explore More Commands**: Try natural variations of commands
2. **Read the Docs**: Check [UNIFIED_VISION_AND_REALITY.md](UNIFIED_VISION_AND_REALITY.md) for complete feature list
3. **Try Experimental Features**: Voice interface, learning system (see docs)
4. **Contribute**: Report bugs, suggest features, or contribute code

## 🎉 Success!

You're now using natural language to manage NixOS! Remember:
- Be conversational - talk naturally
- Explore freely - it's safe to experiment
- Check docs for advanced features
- Join the community for support

---

**Ran into issues?** Create an issue on [GitHub](https://github.com/Luminous-Dynamics/luminous-nix/issues)
**Want to learn more?** Read the [full documentation](docs/README.md)
**Ready to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

*Last tested: 2025-08-24 | Version: 0.2.0-alpha*