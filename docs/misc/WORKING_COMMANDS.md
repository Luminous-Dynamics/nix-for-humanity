# ✅ Working Commands - Nix for Humanity v0.8.0

*Last Updated: 2025-01-29 - Command Consolidation Complete!*

## 🚀 THE ONE COMMAND: ask-nix

All functionality has been consolidated into a single, powerful `ask-nix` command:

```bash
# Basic usage - natural language interface
ask-nix "install firefox"
ask-nix "search for python packages"
ask-nix "update my system"
ask-nix "what is a nix generation?"
```

### Available Flags

#### Personality Modes
- `--minimal` - Just the facts, no fluff
- `--friendly` - Warm and helpful (default)
- `--encouraging` - Supportive for beginners
- `--technical` - Detailed technical explanations
- `--symbiotic` - Co-evolutionary mode that admits uncertainty

#### Execution Modes
- `--execute` - Actually run commands (becoming default)
- `--dry-run` - Show what would be done without doing it
- `--yes` - Skip confirmation prompts

#### Features
- `--voice` - Enable voice interface
- `--learning-mode` - Step-by-step guidance
- `--no-feedback` - Disable feedback collection
- `--summary` - Show learning progress and statistics

#### Advanced
- `--cache-info` - Show package cache statistics
- `--help` - Show all available options

## 📊 Example Sessions

### For Grandma Rose (Voice User)
```bash
# Start voice interface
ask-nix --voice

# Or type naturally
ask-nix --encouraging "I want to install that Firefox thing"
```

### For Carlos (Learning NixOS)
```bash
# Learning mode with step-by-step guidance
ask-nix --learning-mode "how do I manage packages?"

# See progress
ask-nix --summary
```

### For Dr. Sarah (Power User)
```bash
# Technical details with fast execution
ask-nix --technical --yes "install python311Full nodejs_20"

# Direct execution without confirmation
ask-nix --execute --yes "update system"
```

### For Maya (ADHD, Needs Speed)
```bash
# Minimal output, fast responses
ask-nix --minimal "search rust"

# Quick install with progress only
ask-nix --minimal --yes "install htop"
```

## 🗂️ Deprecated Commands

All `ask-nix-*` variants now show a deprecation notice pointing to the unified `ask-nix` command:

- ❌ `ask-nix-hybrid` → ✅ Use `ask-nix`
- ❌ `ask-nix-v3` → ✅ Use `ask-nix`  
- ❌ `ask-nix-adaptive` → ✅ Use `ask-nix --adaptive`
- ❌ `ask-nix-learning` → ✅ Use `ask-nix --learning-mode`
- ❌ `ask-nix-python` → ✅ Use `ask-nix`
- ❌ All other variants → ✅ Use `ask-nix`

## 🛠️ Supporting Tools

### nix-profile-do
Direct wrapper for nix profile commands when you need precise control:
```bash
nix-profile-do install nixpkgs#firefox
nix-profile-do list
nix-profile-do remove firefox
```

### demo-symbiotic-learning
Interactive demo of the feedback system:
```bash
demo-symbiotic-learning
```

### analyze-feedback
View collected feedback and learning patterns:
```bash
analyze-feedback
```

## 🎯 What Actually Works

### ✅ Package Management
- Install packages (declarative and imperative)
- Search packages (with smart caching)
- Remove packages
- List installed packages
- Package information lookup

### ✅ System Management
- Update system
- Rollback to previous generation
- List generations
- Garbage collection
- Channel management

### ✅ Learning & Adaptation
- Personality adaptation
- Command pattern learning
- Feedback collection
- Usage statistics
- Preference tracking

### ✅ User Experience
- Natural language understanding
- Progress indicators
- Error recovery
- Educational messages
- Safety confirmations

### ⚠️ In Progress
- Python backend integration (partial)
- Voice interface (experimental)
- GUI extraction (planned)

## 🚀 Quick Test

```bash
# Test the consolidated command
ask-nix "what can you do?"

# This should show all integrated features and capabilities
```

## 📝 Notes

- The consolidation is complete as of v0.8.0
- All features from various ask-nix variants are now in one command
- The plugin architecture allows for future extensibility
- Feedback collection helps improve the system continuously

---

*"One command to rule them all, one command to find them, one command to bring them all, and in the Nix store bind them."*