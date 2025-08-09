# 🚀 Daily Use Setup - Nix for Humanity

*Making it real: Set up Nix for Humanity as your daily driver*

## Quick Setup (2 minutes)

```bash
# 1. Add to your shell profile (.bashrc/.zshrc)
echo 'export PATH="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/bin:$PATH"' >> ~/.bashrc
echo 'alias nix="ask-nix"' >> ~/.bashrc
echo 'alias nixfeedback="echo \"$(date): \" >> /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/FEEDBACK_CAPTURE.md && vim /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/FEEDBACK_CAPTURE.md"' >> ~/.bashrc

# 2. Reload shell
source ~/.bashrc

# 3. Test it works
nix "help"

# 4. Enable Python backend for better performance
echo 'export NIX_HUMANITY_PYTHON_BACKEND=true' >> ~/.bashrc
source ~/.bashrc
```

## 📱 Daily Workflow Integration

### Morning Ritual
```bash
# Start your day
nix "good morning, check for updates"
nix "how much disk space do I have?"
nix "any broken packages?"
```

### Throughout the Day
Instead of:                          Use:
- `nix-env -iA nixos.firefox`   →   `nix "install firefox"`
- `nix-env -q`                  →   `nix "what do I have installed?"`
- `nixos-rebuild switch`        →   `nix "update my system"`
- `nix-collect-garbage -d`      →   `nix "clean up disk space"`
- `nix search firefox`          →   `nix "search for firefox"`

### Quick Feedback
When something breaks or annoys you:
```bash
nixfeedback  # Opens feedback file with timestamp
```

## 🎛️ Customization

### Set Your Preferred Persona
```bash
# Add to ~/.bashrc
export NIX_HUMANITY_PERSONA="maya"  # Fast, minimal responses

# Options:
# grandma_rose - Extra gentle and detailed
# maya - Lightning fast, minimal
# dr_sarah - Precise and technical
# alex - Optimized for screen readers
# jamie - Privacy-focused
```

### Custom Aliases for Common Tasks
```bash
# Add to ~/.bashrc
alias nixup="nix 'update my system'"
alias nixclean="nix 'clean up old generations'"
alias nixlist="nix 'list installed packages'"
alias nixfind="nix 'search for'"
alias nixfix="nix 'something is broken, help'"
```

## 📊 Daily Metrics

Track your usage to find patterns:

```bash
# Add to ~/.bashrc to log all usage
function nix() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" >> ~/.nix-humanity-usage.log
    ask-nix "$@"
}

# View your usage patterns
alias nixstats="cat ~/.nix-humanity-usage.log | awk '{print \$4}' | sort | uniq -c | sort -nr | head -20"
```

## 🔧 Troubleshooting Shortcuts

```bash
# When things go wrong
alias nixdebug="NIX_HUMANITY_DEBUG=true nix"
alias nixreset="rm -rf ~/.cache/nix-humanity && echo 'Cache cleared'"
alias nixtest="nix 'help' && echo 'Basic test passed'"
```

## 📱 Mobile-Style Quick Actions

Create a `.nix-shortcuts` file:
```bash
#!/bin/bash
# Quick action menu
echo "Nix for Humanity Quick Actions:"
echo "1. Update system"
echo "2. Search packages" 
echo "3. Install package"
echo "4. Clean up space"
echo "5. Show installed"
echo "6. Fix problems"
echo "7. Give feedback"
read -p "Choose action (1-7): " choice

case $choice in
    1) nix "update my system";;
    2) read -p "Search for: " pkg && nix "search for $pkg";;
    3) read -p "Install: " pkg && nix "install $pkg";;
    4) nix "clean up disk space";;
    5) nix "what's installed?";;
    6) nix "help me fix my system";;
    7) nixfeedback;;
esac
```

Make it executable: `chmod +x ~/.nix-shortcuts`
Add alias: `alias n="~/.nix-shortcuts"`

## 🎯 Daily Challenges

### Week 1 Challenge
- Use ONLY `nix` command (no `nix-env`, `nixos-rebuild`, etc.)
- Log every time you fall back to regular commands
- Note the exact reason why

### Week 2 Challenge  
- Try the TUI for one full day: `nix-tui`
- Use voice interface for an hour (when implemented)
- Test with different personas

### Week 3 Challenge
- Show it to someone else
- Use it to help them with a real task
- Note where they get confused

### Week 4 Challenge
- Go back to regular commands for a day
- Note what you miss about Nix for Humanity
- Note what you DON'T miss

## 📈 Progress Tracking

Create `~/.nix-humanity-progress.md`:

```markdown
# My Nix for Humanity Journey

## Day 1: [Date]
- Commands that worked:
- Commands that failed:
- Fallback count:
- Frustration level: /10
- Would recommend: Y/N

## Day 7: [Date]
- Commands that worked:
- Commands that failed:
- Fallback count:
- Frustration level: /10
- Would recommend: Y/N

## Day 14: [Date]
- Commands that worked:
- Commands that failed:
- Fallback count:
- Frustration level: /10
- Would recommend: Y/N

## Day 30: [Date]
- Preferred over native: Y/N
- Missing features:
- Best improvements:
- Overall rating: /10
```

## 🚨 Emergency Fallback

When you absolutely need native commands:

```bash
# Temporary disable
unalias nix

# Or use full path
/run/current-system/sw/bin/nix-env -iA nixos.firefox

# Re-enable when done
alias nix="ask-nix"
```

## 🎁 Rewards System

Motivate yourself to stick with it:

- Day 1: You tried! ⭐
- Day 3: Getting somewhere! ⭐⭐
- Day 7: One week! ⭐⭐⭐
- Day 14: Two weeks! ⭐⭐⭐⭐
- Day 30: Power user! ⭐⭐⭐⭐⭐

## 🏁 Ready to Start?

```bash
# Final check
nix "help"  # Should work
nixfeedback  # Should open editor
which nix  # Should show alias

# You're ready! Start using it for EVERYTHING
echo "Starting Nix for Humanity journey: $(date)" >> ~/.nix-humanity-progress.md
```

---

*Remember: The goal isn't to suffer through broken software. It's to discover what needs fixing by actually using it. Your daily friction is the map to making this truly useful.*

**Promise**: Use it for real tasks. Log real problems. Build real solutions.