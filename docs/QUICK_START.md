# 🚀 Luminous Nix - Quick Start Guide

*Get up and running in 5 minutes!*

## 📦 Installation (1 minute)

### Fastest Method - Standalone Binary

```bash
# Download the latest release
curl -L https://github.com/Luminous-Dynamics/luminous-nix/releases/latest/download/luminous-nix -o luminous-nix

# Make it executable
chmod +x luminous-nix

# Test it works
./luminous-nix --version
```

That's it! You're ready to use Luminous Nix.

## 🎯 Your First Commands (2 minutes)

### 1. Search for Software

Instead of memorizing package names, just describe what you want:

```bash
# Find a text editor
./luminous-nix "find text editor"

# Search for web browsers  
./luminous-nix "web browser"

# Look for development tools
./luminous-nix "python development"
```

### 2. Install Software

```bash
# Install by name
./luminous-nix "install firefox"

# Install by description
./luminous-nix "install a markdown editor"

# Preview first (dry run)
./luminous-nix "install vscode" --dry-run
```

### 3. Create a Development Environment

```bash
# Navigate to your project
cd my-project

# Create a Python development environment
./luminous-nix flake create "python web app with flask"

# Enter the environment
nix develop

# Everything is ready - Python, Flask, and tools are installed!
python --version
flask --version
```

## 🎨 Visual Interface (30 seconds)

Launch the beautiful terminal UI:

```bash
./luminous-nix tui
```

- Use **arrow keys** to navigate
- Press **/** to search
- Press **Enter** to select
- Press **q** to quit

## 💡 Real-World Examples (2 minutes)

### Example 1: Set Up a Web Development Environment

```bash
# One command to get everything
./luminous-nix flake create "web development with nodejs, react, and postgresql"

# Enter the environment
nix develop

# Start coding!
npm --version    # ✓ Node.js ready
psql --version   # ✓ PostgreSQL ready
```

### Example 2: Configure a New System

```bash
# Generate a complete system configuration
./luminous-nix "generate config for desktop with KDE and development tools"

# Save it
./luminous-nix "generate config for desktop with KDE and development tools" > ~/my-config.nix

# Review what it created
cat ~/my-config.nix
```

### Example 3: Quick Package Discovery

```bash
# Fuzzy search works!
./luminous-nix "fierfix"          # → Finds firefox
./luminous-nix "vcsode"           # → Finds vscode
./luminous-nix "kuberntes"        # → Finds kubernetes

# Natural language works too!
./luminous-nix "something to edit photos"     # → Shows GIMP, Krita, etc.
./luminous-nix "watch videos"                 # → Shows VLC, MPV, etc.
```

## 🏃 Speed Run Challenge

See how fast you can:

1. **Install a browser** (10 seconds)
   ```bash
   ./luminous-nix "install firefox" --yes
   ```

2. **Create a dev environment** (15 seconds)
   ```bash
   ./luminous-nix flake create "python with testing tools"
   ```

3. **Find and install an editor** (20 seconds)
   ```bash
   ./luminous-nix "find code editor"
   ./luminous-nix "install vscode" --yes
   ```

Total time: 45 seconds to a complete setup! ⚡

## 🎓 Next Steps

Now that you're up and running:

### Learn More Commands
```bash
# See all available commands
./luminous-nix help

# Get help for specific commands
./luminous-nix help install
./luminous-nix help flake
./luminous-nix help config
```

### Explore Features
- **[Read the User Guide](USER_GUIDE.md)** - Complete feature documentation
- **[Try the TUI](USER_GUIDE.md#4-beautiful-tui-interface)** - Visual package management
- **[Create Flakes](USER_GUIDE.md#3-flake-management-)** - Modern development environments
- **[Generate Configs](USER_GUIDE.md#2-configuration-generation-)** - System configurations

### Get Help
- **Built-in**: `./luminous-nix help`
- **Examples**: `./luminous-nix examples`
- **GitHub**: [Issues & Discussions](https://github.com/Luminous-Dynamics/luminous-nix)

## 🌟 Pro Tips

1. **Add to PATH** for easier access:
   ```bash
   sudo mv luminous-nix /usr/local/bin/ask-nix
   # Now use from anywhere:
   ask-nix "install firefox"
   ```

2. **Use aliases** for speed:
   ```bash
   alias nxs='ask-nix search'
   alias nxi='ask-nix install'
   alias nxf='ask-nix flake create'
   ```

3. **Tab completion** (bash/zsh):
   ```bash
   eval "$(ask-nix completion bash)"  # or zsh
   ```

## 🎉 Congratulations!

You've just learned how to:
- ✅ Search and install packages using natural language
- ✅ Create development environments in seconds
- ✅ Generate system configurations
- ✅ Use the visual TUI interface

**You're now ready to use NixOS like a pro, without learning Nix!** 🚀

---

*Questions? Check the [User Guide](USER_GUIDE.md) or run `ask-nix help`*