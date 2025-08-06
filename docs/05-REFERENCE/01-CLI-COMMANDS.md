# 📟 CLI Commands Reference

*Complete command reference for ask-nix and related tools*

---

💡 **Quick Context**: Complete command-line reference for all natural language NixOS tools and options  
📍 **You are here**: Reference → CLI Commands (Command Handbook)  
🔗 **Related**: [Quick Start Guide](../03-DEVELOPMENT/03-QUICK-START.md) | [User Guide](../06-TUTORIALS/USER_GUIDE.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)  
⏱️ **Read time**: 20 minutes  
📊 **Mastery Level**: 🌿 Intermediate - comprehensive reference for power users and developers

🌊 **Natural Next Steps**:
- **For new users**: Start with [Quick Start Guide](../03-DEVELOPMENT/03-QUICK-START.md) for essential commands first
- **For comprehensive help**: Continue to [User Guide](../06-TUTORIALS/USER_GUIDE.md) for complete usage patterns
- **For troubleshooting**: Reference [Troubleshooting Guide](../04-OPERATIONS/03-TROUBLESHOOTING.md) when commands fail
- **For developers**: Review [Code Standards](../03-DEVELOPMENT/04-CODE-STANDARDS.md) for implementation patterns

---

## Core Commands

### ask-nix

The main command-line interface for natural language NixOS management.

#### Basic Usage
```bash
ask-nix [options] "natural language query"
```

#### Examples
```bash
ask-nix "install firefox"
ask-nix "my wifi isn't working"  
ask-nix "update my system"
ask-nix "search for text editors"
```

#### Options

##### Personality Modes
```bash
--minimal           # Fast, minimal responses (great for ADHD)
--friendly          # Warm, helpful responses (default)
--encouraging       # Extra supportive for learning
--technical         # Detailed technical information
--accessible        # Screen reader optimized output
--learning          # Step-by-step educational responses
```

##### Response Control
```bash
--quiet             # Minimal output
--verbose           # Detailed output  
--explain           # Include explanations
--show-command      # Display the actual command that would run
--structured        # Organized, hierarchical output
```

##### Execution Control
```bash
--dry-run           # Show what would happen (default)
--execute           # Actually run the commands
--safe              # Extra confirmation prompts
--fast              # Skip non-essential checks
```

##### Output Format
```bash
--json              # JSON output for scripting
--yaml              # YAML output
--plain             # Plain text, no formatting
--no-color          # Disable colored output
```

##### Debugging
```bash
--debug             # Enable debug logging
--verbose-debug     # Maximum debug information
--diagnose          # System diagnostic information
--show-intent       # Show how the query was interpreted
```

##### Help & Information
```bash
--help              # Show help message
--version           # Show version information
--examples          # Show example commands
--status            # Show system status
```

#### Environment Variables

```bash
# Backend Configuration
NIX_HUMANITY_BACKEND=python              # Use Python backend (faster)
NIX_HUMANITY_PYTHON_BACKEND=true         # Alternative way to enable Python backend

# Logging
NIX_HUMANITY_LOG_LEVEL=debug             # Set logging level (debug, info, warn, error)
NIX_HUMANITY_DEBUG=true                  # Enable debug mode

# Features
NIX_HUMANITY_VOICE_ENABLED=true          # Enable voice features (when available)
NIX_HUMANITY_LEARNING_ENABLED=true       # Enable learning system
NIX_HUMANITY_EXECUTE_COMMANDS=true       # Allow command execution

# Paths
NIX_HUMANITY_DATA_DIR=~/.local/share/nix-for-humanity    # Data directory
NIX_HUMANITY_CACHE_DIR=~/.cache/nix-for-humanity         # Cache directory
NIX_HUMANITY_CONFIG_DIR=~/.config/nix-for-humanity       # Config directory

# Performance
NIX_HUMANITY_FAST_MODE=true              # Enable fast mode
NIX_HUMANITY_LIGHTWEIGHT=true            # Use minimal resources
NIX_HUMANITY_OFFLINE=true                # Offline mode for development
```

## Specialized Commands

### ask-nix-learning

Educational version with step-by-step guidance.

```bash
ask-nix-learning "install development tools"
ask-nix-learning "explain NixOS generations"
ask-nix-learning "how do system updates work?"
```

**Features:**
- Detailed explanations for every step
- Examples with each command
- Practice exercises
- Progress tracking
- Beginner-friendly language

### ask-nix-minimal

Fast, minimal responses for power users.

```bash
ask-nix-minimal "install firefox"
# Output: "nix-env -iA nixos.firefox"

ask-nix-minimal "update system"  
# Output: "sudo nixos-rebuild switch"
```

**Features:**
- Sub-2-second responses
- Just the essential information
- No explanations unless requested
- Ideal for scripting

### ask-nix-accessible

Screen reader and accessibility optimized.

```bash
ask-nix-accessible "install development tools"
```

**Features:**
- Structured, semantic output
- No visual-only information
- Screen reader landmarks
- Consistent terminology
- Clear navigation

### nix-tui (Coming Soon)

Beautiful terminal user interface.

```bash
nix-tui                    # Launch TUI
nix-tui --help             # TUI help
```

**Features:**
- Interactive conversations
- Visual progress indicators  
- Mouse and keyboard support
- Multiple panes and tabs
- Real-time system monitoring

## Query Patterns

### Software Management

#### Installation
```bash
ask-nix "install firefox"
ask-nix "I need a text editor"
ask-nix "set up development environment"
ask-nix "install python with data science packages"
```

#### Removal
```bash
ask-nix "remove firefox"
ask-nix "uninstall games"
ask-nix "clean up unused packages"
```

#### Search
```bash
ask-nix "search for photo editors"
ask-nix "find music players"
ask-nix "what packages are available for programming?"
ask-nix "show me browsers"
```

### System Management

#### Updates
```bash
ask-nix "update my system"
ask-nix "upgrade nixos"
ask-nix "check for updates"
ask-nix "update specific package"
```

#### Information
```bash
ask-nix "what's installed?"
ask-nix "show system information"
ask-nix "how much disk space?"
ask-nix "what version of nixos?"
```

#### Maintenance
```bash
ask-nix "clean up old generations"
ask-nix "garbage collect"
ask-nix "optimize system"
ask-nix "check system health"
```

### Troubleshooting

#### Network
```bash
ask-nix "my wifi isn't working"
ask-nix "internet is slow"
ask-nix "can't connect to network"
ask-nix "bluetooth problems"
```

#### Audio/Video
```bash
ask-nix "no sound"
ask-nix "microphone not working"
ask-nix "screen too dark"
ask-nix "display issues"
```

#### General
```bash
ask-nix "something is broken"
ask-nix "system is slow"
ask-nix "help me fix this"
ask-nix "undo last change"
```

### Configuration

#### Services
```bash
ask-nix "enable ssh"
ask-nix "start web server"
ask-nix "configure firewall"
ask-nix "set up database"
```

#### Users
```bash
ask-nix "create new user"
ask-nix "change password"
ask-nix "manage permissions"
ask-nix "set up home directory"
```

## Advanced Usage

### Scripting with ask-nix

```bash
#!/usr/bin/env bash

# Get JSON output for parsing
result=$(ask-nix --json "install firefox")
package=$(echo "$result" | jq -r '.package')
command=$(echo "$result" | jq -r '.command')

# Check if installation is recommended
if echo "$result" | jq -e '.recommend' > /dev/null; then
    echo "Installing recommended package: $package"
    eval "$command"
fi
```

### Batch Operations

```bash
# Install multiple packages
ask-nix "install firefox libreoffice gimp vlc"

# System maintenance routine
ask-nix "update system, clean old packages, check health"

# Development setup
ask-nix "install git nodejs python docker, configure development environment"
```

### Configuration File

Create `~/.config/nix-for-humanity/config.yaml`:

```yaml
# Default personality
personality: friendly

# Response preferences
response:
  explain: true          # Include explanations
  show_commands: true    # Show underlying commands
  confirm_actions: true  # Ask before executing

# Performance
performance:
  fast_mode: false       # Prioritize accuracy over speed
  cache_responses: true  # Cache common responses
  
# Learning
learning:
  enabled: true          # Learn from interactions
  privacy_mode: strict   # Don't learn personal information

# Accessibility
accessibility:
  screen_reader: false   # Enable screen reader optimizations
  high_contrast: false   # Use high contrast output
  large_text: false      # Use larger text in TUI
```

## Exit Codes

```bash
0   # Success
1   # General error
2   # Command parsing error
3   # NixOS operation failed
4   # Permission denied
5   # Network error
6   # Configuration error
7   # User cancelled operation
8   # System incompatible
```

## Examples by User Type

### For Beginners (like Grandma Rose)
```bash
ask-nix --learning "I want to browse the internet"
ask-nix --friendly "how do I check my email?"
ask-nix --encouraging "I'm confused about updates"
```

### For ADHD Users (like Maya)
```bash
ask-nix --minimal "firefox"
ask-nix --fast "update"
ask-nix --minimal "discord spotify obs"
```

### For Screen Reader Users (like Alex)
```bash
ask-nix --accessible "install development tools"
ask-nix --structured "show installed packages"
ask-nix --accessible --verbose "configure ssh server"
```

### For Learning Users (like Carlos)
```bash
ask-nix --learning "explain NixOS generations"
ask-nix --explain "why do I need to rebuild?"
ask-nix --learning --examples "show me package management"
```

### For Professionals (like Dr. Sarah)
```bash
ask-nix --technical "install R with statistical packages"
ask-nix --show-command "configure postgresql for research"
ask-nix --technical --json "setup reproducible python environment"
```

## Integration with Other Tools

### Shell Integration

Add to your `.bashrc` or `.zshrc`:

```bash
# Alias for convenience
alias nix='ask-nix'
alias nh='ask-nix'

# Function for quick installs
install() {
    ask-nix "install $*"
}

# Function for quick search
search() {
    ask-nix "search for $*"
}
```

### Git Integration

```bash
# Add to .gitconfig
[alias]
    nix-setup = "!ask-nix 'install git development tools'"
    nix-status = "!ask-nix 'check system status'"
```

## Tips for Effective Usage

### Natural Language Tips
1. **Be specific**: "install firefox" vs "install browser"
2. **Include context**: "install photo editor for professional work"
3. **Ask follow-ups**: "explain that command" or "why do I need that?"
4. **Use corrections**: "no, I meant vim not emacs"

### Performance Tips
1. **Use Python backend**: `export NIX_HUMANITY_PYTHON_BACKEND=true`
2. **Enable caching**: Keep cache directory for faster responses
3. **Use minimal mode**: For repeated operations
4. **Batch operations**: "install A B C" vs separate commands

### Accessibility Tips
1. **Use structured output**: `--structured` for screen readers
2. **Enable verbose mode**: More context for assistive technology
3. **Consistent terminology**: System uses same terms throughout
4. **Keyboard navigation**: All features accessible via keyboard

---

*"Every command is a conversation, every conversation is a step toward mastery."*

🌊 Flow with natural language!