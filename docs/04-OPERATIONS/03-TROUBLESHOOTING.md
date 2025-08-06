# 🔧 Troubleshooting Guide - Nix for Humanity

*Solutions to common issues and how to get help*

---

💡 **Quick Context**: Comprehensive troubleshooting guide with solutions to common issues and support resources  
📍 **You are here**: Operations → Troubleshooting (Problem Resolution)  
🔗 **Related**: [Quick Start Guide](../03-DEVELOPMENT/03-QUICK-START.md) | [Testing Guide](../03-DEVELOPMENT/05-TESTING-GUIDE.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)  
⏱️ **Read time**: 10 minutes  
📊 **Mastery Level**: 🌱 Beginner-Intermediate - practical solutions for common scenarios

🌊 **Natural Next Steps**:
- **For new users**: Start with [Quick Start Guide](../03-DEVELOPMENT/03-QUICK-START.md) if you haven't set up the system yet
- **For developers**: Continue to [Testing Guide](../03-DEVELOPMENT/05-TESTING-GUIDE.md) for quality assurance approaches  
- **For contributors**: Review [Sacred Trinity Workflow](../03-DEVELOPMENT/02-SACRED-TRINITY-WORKFLOW.md) for development process
- **For support**: Check [Implementation Roadmap](../01-VISION/02-ROADMAP.md) to understand current development status

---

## Quick Diagnostics

If something isn't working, run this first:

```bash
# Check system status
./bin/ask-nix --diagnose

# This will show:
# - Python version
# - NixOS version  
# - Available memory
# - Backend status
# - Common issues
```

## Common Issues & Solutions

### Installation Problems

#### "Command not found: ask-nix"
**Problem**: The CLI tool isn't in your PATH.

**Solution**:
```bash
# From project directory
cd /path/to/nix-for-humanity
./bin/ask-nix  # Use relative path

# Or add to PATH
export PATH="$PATH:/path/to/nix-for-humanity/bin"
```

#### "No module named 'nix_humanity'"
**Problem**: Python dependencies not installed.

**Solution**:
```bash
# Enter development environment
./dev.sh

# Install dependencies
pip install -r requirements.txt
```

#### Nix flake download timeouts
**Problem**: `./dev.sh` hangs downloading flakes.

**Solution**:
```bash
# Use offline mode for development
export NIX_FOR_HUMANITY_OFFLINE=true
./dev.sh

# Or be patient - first download can take 5-10 minutes
```

### Runtime Issues

#### "I don't understand that command"
**Problem**: Natural language not recognized.

**Examples & Solutions**:
```
❌ Bad: "fix it"
✅ Good: "fix my wifi connection"

❌ Bad: "install"  
✅ Good: "install firefox"

❌ Bad: "why broken"
✅ Good: "why is my internet not working"
```

**Tips**:
- Be specific about what you want
- Include the object (firefox, wifi, etc.)
- Use complete phrases when possible

#### Slow responses (>2 seconds)
**Problem**: System taking too long to respond.

**Solutions**:
1. **Enable Python backend** (10x faster):
   ```bash
   export NIX_HUMANITY_PYTHON_BACKEND=true
   ./bin/ask-nix
   ```

2. **Check system resources**:
   ```bash
   free -h  # Memory usage
   top      # CPU usage
   ```

3. **Use minimal personality** (faster):
   ```
   You: switch to minimal mode
   System: Switched to minimal responses.
   ```

#### Wrong package installed
**Problem**: System misunderstood your request.

**Solution**:
```
You: install code editor
System: Installing VS Code...
You: no, I meant vim
System: Canceling VS Code. Installing Vim instead...
```

The system learns from corrections!

### Backend Issues

#### "Backend not responding"
**Problem**: Core engine isn't running.

**Solution**:
```bash
# Check if backend is running
ps aux | grep nix-humanity-backend

# Start backend manually
./bin/nix-humanity-backend &

# Check logs
tail -f ~/.local/share/nix-humanity/backend.log
```

#### Memory usage too high
**Problem**: System using >500MB RAM.

**Solution**:
```bash
# Use lightweight mode
export NIX_HUMANITY_LIGHTWEIGHT=true

# Disable learning temporarily
export NIX_HUMANITY_LEARNING=false

# Clear cache
rm -rf ~/.cache/nix-humanity/*
```

### Learning System Issues

#### "System not learning my preferences"
**Problem**: Personalization not working.

**Check**:
```bash
# Verify learning is enabled
./bin/ask-nix --show-config | grep learning

# Check data directory exists
ls -la ~/.local/share/nix-humanity/
```

**Solution**:
```bash
# Enable learning
export NIX_HUMANITY_LEARNING=true

# Reset learning data
./bin/ask-nix --reset-learning
```

#### Privacy concerns
**Problem**: Worried about data collection.

**Facts**:
- ✅ All data stays local
- ✅ No network requests
- ✅ You own all data
- ✅ Can delete anytime

**View your data**:
```bash
# See what's been learned
./bin/ask-nix --show-learned

# Export your data
./bin/ask-nix --export-data > my-data.json

# Delete all data
./bin/ask-nix --delete-all-data
```

### Persona-Specific Issues

#### Grandma Rose: "Text too small"
```bash
# Increase font size in terminal
# Most terminals: Ctrl + or Ctrl+Shift+=

# Or use voice mode (coming soon)
./bin/ask-nix --voice
```

#### Maya (ADHD): "Too slow!"
```bash
# Enable speed mode
export NIX_HUMANITY_FAST_MODE=true
export NIX_HUMANITY_PERSONALITY=minimal
```

#### Alex (Blind): "Screen reader issues"
```bash
# Enable screen reader mode
export NIX_HUMANITY_SCREEN_READER=true

# Test with your screen reader
./bin/ask-nix --test-accessibility
```

### Development Issues

#### Tests failing
```bash
# Run specific test with details
pytest -xvs tests/test_nlp_engine.py::test_function_name

# Check test environment
./dev.sh test-env

# Skip slow tests
pytest -m "not slow"
```

#### Coverage below target
```bash
# Find uncovered code
coverage report -m

# Generate HTML report
coverage html
open htmlcov/index.html

# Run missing tests
pytest tests/ -k "test_missing_function"
```

## Error Messages Explained

### Common Errors

#### "ERROR: Package not found"
**Meaning**: The requested package doesn't exist in nixpkgs.

**Solution**:
```
You: search for browsers
System: Found: firefox, chromium, brave, qutebrowser
You: install brave
```

#### "ERROR: Permission denied"
**Meaning**: Operation requires sudo/root access.

**Solution**:
```bash
# For system-wide installs
sudo ./bin/ask-nix "install firefox system-wide"

# Or use declarative config (recommended)
You: show me how to add firefox to configuration.nix
```

#### "ERROR: Disk space low"
**Meaning**: Not enough space for operation.

**Solution**:
```
You: clean up old packages
System: Running garbage collection...
System: Freed 2.3GB of space.
```

## Debug Mode

For detailed debugging information:

```bash
# Enable debug logging
export NIX_HUMANITY_DEBUG=true
export NIX_HUMANITY_LOG_LEVEL=debug

# Run with verbose output
./bin/ask-nix -vvv "your command"

# Check debug logs
tail -f ~/.local/share/nix-humanity/debug.log
```

## Getting Help

### Self-Help Commands
```
You: help
You: what can you do?
You: show examples
You: explain [error message]
```

### Check Documentation
```bash
# Built-in docs
./bin/ask-nix --docs

# Online docs
open https://github.com/Luminous-Dynamics/nix-for-humanity/docs
```

### Community Support

1. **GitHub Issues**: 
   - Search existing: https://github.com/Luminous-Dynamics/nix-for-humanity/issues
   - Create new: Include debug output!

2. **Discord** (coming soon):
   - #help channel for questions
   - #dev for development issues

3. **Matrix** (coming soon):
   - #nix-for-humanity:matrix.org

### Reporting Bugs

Include this information:
```bash
# Generate bug report
./bin/ask-nix --bug-report > bug-report.txt

# Includes:
# - System info
# - Error messages
# - Recent commands
# - Configuration
```

## Recovery Procedures

### Reset to defaults
```bash
# Reset configuration
rm ~/.config/nix-humanity/config.json
./bin/ask-nix --init

# Reset learning
./bin/ask-nix --reset-learning

# Full reset
./bin/ask-nix --factory-reset
```

### Rollback after bad update
```bash
# List versions
./bin/ask-nix --list-versions

# Rollback to previous
./bin/ask-nix --rollback

# Or specific version
./bin/ask-nix --rollback-to v0.8.0
```

## Prevention Tips

1. **Keep system updated**: `ask-nix "update nix-for-humanity"`
2. **Regular backups**: `ask-nix --backup`
3. **Test in safe mode**: `ask-nix --safe-mode "risky command"`
4. **Read suggestions**: The system often prevents issues
5. **Report problems**: Help us improve!

## Emergency Contacts

If you discover a security issue:
- 🚨 Email: security@luminousdynamics.org
- 🔐 PGP Key: [On website]

---

*Sacred Humility Context: This troubleshooting guide represents our current understanding of common issues and effective resolution strategies within our development environment. While these solutions have proven effective in our specific context and testing scenarios, troubleshooting approaches may vary significantly across different system configurations, user environments, and usage patterns. Our diagnostic procedures and solutions reflect our experience with the Sacred Trinity development model and may require adaptation for broader deployment contexts. We remain committed to improving these resources based on real-world user feedback and emerging issues beyond our current scope.*

*Remember: Every error is a chance to improve the system. Thank you for your patience! 🌊*