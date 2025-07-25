# 🗣️ Nix for Humanity - User Guide

Welcome! This guide will help you use Nix for Humanity to manage your NixOS system through natural conversation. Just say what you want - no commands to memorize!

## 🌟 What is Nix for Humanity?

Nix for Humanity transforms NixOS from a command-line system into a conversational partner. Instead of typing complex commands, you simply talk to your computer naturally - through voice or text.

## 🚀 Getting Started

### First Time Setup

When you first start Nix for Humanity:

```
System: "Hi! I'm Nix for Humanity. I'll help you manage your computer using natural conversation. What would you like to do?"

You: "Hi! Can you help me install a web browser?"

System: "Of course! I can install Firefox, Chrome, or Brave. Which would you prefer?"

You: "Firefox please"

System: "Installing Firefox web browser... Done! You'll find it in your applications menu. Would you like me to open it now?"
```

### Launch Options

1. **Voice Mode** (Recommended)
   - Say "Hey Nix" to activate
   - Speak naturally after the listening tone
   - No special commands needed

2. **Text Mode**
   ```bash
   nix-for-humanity
   ```
   Or click the icon in your applications menu

3. **Hybrid Mode**
   - Mix voice, text, and clicks as feels natural
   - System adapts to your preferred style

### Set Your Comfort Level

- **Beginner** - Simple language, more guidance, confirmations for everything
- **Intermediate** - Balanced assistance, learns your patterns quickly
- **Advanced** - Minimal interface, quick actions, assumes expertise

### Your First Commands

Try these natural phrases to get started:

```
You: "What can you do?"
Nix: Shows available capabilities with examples

You: "Show me what's installed"
Nix: Lists your installed programs in categories

You: "I need a web browser"
Nix: Suggests browsers and installs your choice

You: "My WiFi isn't working"
Nix: Runs diagnostics and guides you through fixes
```

## 🧠 How It Learns Your Preferences

### Installation Method Learning

The system notices HOW you like to install packages:

```bash
# First few times, it asks:
You: "install emacs"
Nix: "How would you like to install this?
     1. Add to configuration.nix (system-wide, declarative)
     2. Add to home.nix (user-specific, declarative)
     3. Quick install with nix-env (imperative)
     4. Temporary with nix-shell (testing)"

# After learning your pattern:
You: "install emacs"
Nix: "Adding Emacs to your configuration.nix (your usual method)"
```

### Timing Intelligence

The system learns WHEN you prefer to do things:

```bash
# Friday afternoon:
You: "update system"
Nix: "I notice you usually update on weekends. Schedule for tomorrow morning?"

# During work hours:
You: "install zoom"
Nix: "Installing Zoom now (you usually need communication tools immediately)"

# Large download at 2pm:
You: "install android-studio"
Nix: "That's 8GB. Add to tonight's maintenance window (10pm)?"
```

### Context Understanding

The system learns WHAT you really want:

```bash
# Learns your stack preferences:
You: "install python"
Nix: "Installing Python with pip, jupyter, and pandas (your usual data science setup)?"

# Remembers project contexts:
You: "setup web development"
Nix: "Installing your usual: nodejs, npm, yarn, postgresql, nginx?"

# Understands relationships:
You: "remove docker"
Nix: "This will also remove docker-compose and your k8s tools. Continue?"
```

## 💬 Natural Language Examples

### Package Management

**Installing Software - Natural ways to ask:**
- "I need a text editor" → Suggests based on your past choices
- "Install VS Code" → Uses your preferred installation method
- "Get me something to edit photos" → Knows if you prefer GIMP or Krita
- "I need a photo editor" → Offers appropriate options
- "Can you get me that video player everyone uses?" → Understands common references
- "Add the thing for PDFs" → Interprets casual requests

**Example Installation Conversation:**
```
You: "I need something to edit photos"
System: "I can suggest a few photo editors:
- GIMP (full-featured, like Photoshop)
- Krita (great for digital art)
- Inkscape (for vector graphics)
Which sounds good for your needs?"

You: "The first one"
System: "Installing GIMP... Done! GIMP is now available in your applications menu under Graphics."
```

**Removing Software**
- "Remove Firefox" → Warns about dependent packages
- "Clean up old stuff" → Suggests unused packages
- "I don't need Python anymore" → Shows what else will be removed

**Updating**
- "Update everything" → Respects your timing preferences
- "Just security updates" → Selective updates
- "What needs updating?" → Shows available updates

### System Configuration

**Services**
- "Enable SSH" → Also configures firewall based on your patterns
- "Start PostgreSQL" → Includes your usual configurations
- "Is nginx running?" → Quick status check

**Network - Natural ways to ask:**
- "Connect to WiFi" → Interactive network selection
- "My internet is slow" → Runs appropriate diagnostics
- "Change DNS" → Suggests your previously used servers
- "My WiFi isn't working" → Helps troubleshoot connection
- "The internet is broken" → Comprehensive network diagnosis

**Example WiFi Fix:**
```
You: "My WiFi stopped working"
System: "I'll help you fix that. Let me check your WiFi... I see your WiFi adapter is disabled. Would you like me to enable it?"

You: "Yes please"
System: "Enabling WiFi adapter... Done! I can see 3 networks available. Would you like to connect to one?"
```

### System Information

**Natural ways to ask:**
- "What's my IP address?"
- "How much RAM do I have?"
- "What version of Linux am I running?"
- "Show me what's using my CPU"
- "What's taking up all my memory?"

**Example Memory Check:**
```
You: "What's taking up all my memory?"
System: "Here are your top memory users:
1. Firefox - 2.3GB (45%)
2. VS Code - 1.1GB (22%)
3. Slack - 0.8GB (16%)

You have 5.1GB total, with 0.8GB free. Would you like tips on reducing memory usage?"
```

### System Maintenance

**Natural ways to ask:**
- "Clean up my computer"
- "Free up some space"
- "My computer feels full"
- "Is my system healthy?"

**Example Cleanup:**
```
You: "My computer feels full"
System: "Let me check your disk space... You're using 89% of your disk. I found:
- 12GB of old system generations
- 5GB of package cache
- 3GB of log files
Would you like me to clean these up?"

You: "Yes, but keep one old generation just in case"
System: "Keeping the most recent generation and cleaning up the rest... Freed 18GB! Your disk is now at 71% usage."
```

### Troubleshooting

**Smart Diagnostics**
- "Something's wrong" → Checks recent changes first
- "Audio not working" → Knows your hardware specifics
- "System feels slow" → Checks based on your usage patterns
- "Everything is really slow" → Comprehensive performance check
- "I can't print" → Printer troubleshooting wizard

**Clear Error Messages**
When something isn't possible:
```
You: "Install photoshop"
System: "Photoshop isn't available for Linux, but I can suggest alternatives:
- GIMP (free, very powerful)
- Krita (great for digital art)
- You could also run Photoshop in a Windows VM
What would work best for you?"
```

## 🎯 Advanced Features

### Teaching Mode

Help the system learn faster:

```bash
You: "I prefer home-manager for GUI apps"
Nix: "Got it! I'll remember to use home.nix for graphical applications."

You: "Always backup before system updates"
Nix: "I'll create snapshots before each system update from now on."
```

### Pattern Shortcuts

Once learned, use shortcuts:

```bash
# Instead of listing everything:
You: "dev setup"
Nix: "Installing your development environment: 
     rust, go, nodejs, docker, postgresql, redis..."

# Quick contexts:
You: "work mode"
Nix: "Switching to work profile: VPN on, slack started, focus mode enabled"
```

### Batch Operations

The system learns your grouping preferences:

```bash
You: "install my teaching tools"
Nix: "Installing: obs-studio, zoom, libreoffice, xournalpp (your usual teaching setup)"
```

## 🗣️ Voice Commands

### Wake Words
- "Hey Nix" (default)
- "Nix, please"
- "Computer" (if enabled in settings)

### Voice Interaction Tips
1. **Speak naturally** - No need for robot talk
2. **Pause after wake word** - Wait for the listening tone
3. **Be conversational** - "Can you help me..." works great
4. **Corrections work** - "No, I meant Firefox, not Chrome"

### Example Voice Session
```
You: "Hey Nix"
*listening tone*
You: "My screen is too bright"
System: "I'll help adjust that. Your brightness is at 100%. Would you like me to set it to 70%?"
You: "Make it 50"
System: "Setting brightness to 50%... Done. Is that better?"
```

### Voice-Only Navigation
For hands-free operation:
- "Read the first item"
- "Select option 2"
- "Go back"
- "Cancel that"
- "Confirm"

## ♿ Accessibility Features

### Screen Reader Support
Full compatibility with:
- NVDA (Windows in VM)
- Orca (Linux native)
- Other AT-SPI2 compatible readers

Every response includes:
- Clear structure with headings
- Descriptive text for all actions
- Status announcements
- Keyboard shortcut hints

### Keyboard Navigation
- `Tab` / `Shift+Tab` - Navigate options
- `Enter` - Confirm selection
- `Escape` - Cancel current operation
- `Ctrl+L` - Jump to input field
- `Ctrl+H` - Get contextual help
- `Ctrl+Z` - Undo last action
- `F1` - Full help menu

### Visual Accessibility
- **High Contrast Mode** - Automatically adapts to system theme
- **Large Text Mode** - Scales with system font size
- **Reduced Motion** - Respects system animation preferences
- **Color Blind Modes** - Alternative color schemes available

### Cognitive Accessibility
- **Simple Language Mode** - Uses basic vocabulary
- **Step-by-Step Guidance** - Breaks complex tasks down
- **No Time Pressures** - Take as long as you need
- **Can Repeat Information** - "Say that again" always works
- **Clear Confirmations** - Always shows what will happen

### Example for Screen Reader Users
```
System: "Heading level 1: Search Results
3 items found:
1. Firefox - Web browser
2. Chrome - Web browser  
3. Brave - Privacy-focused browser
Use arrow keys to navigate, Enter to select."
```

## 🔒 Privacy Controls

### Managing Learned Data

```bash
You: "What do you know about me?"
Nix: Shows all learned patterns and preferences

You: "Forget my installation patterns"
Nix: Clears specific learning category

You: "Reset to defaults"
Nix: Removes all personalization
```

### Learning Controls

```bash
You: "Stop learning my patterns"
Nix: Disables pattern learning (still works, just doesn't adapt)

You: "Learn only installation methods"
Nix: Selective learning enabled
```

## ⚡ Power User Tips

### Quick Commands
- "last command" → Repeat previous action
- "undo" → Rollback last change
- "why?" → Explain last decision

### Context Switching
- "home laptop" → Switch to personal patterns
- "work machine" → Switch to professional patterns

### Predictive Help
- System suggests next steps based on patterns
- Warns about potential issues from past experience
- Offers alternatives when something failed before

## 🆘 Getting Help

### Built-in Help
- "Help" → General assistance
- "How do I..." → Specific guidance
- "Explain..." → Detailed explanations

### Learning Together
- System explains why it made choices
- You can correct misconceptions
- Preferences evolve with your expertise

## 📊 Checking System State

### Quick Status
```
You: "How's my system?"
Nix: "All services running. 15 updates available. 
     Last backup: 2 hours ago. Disk usage: 45%"
```

### Detailed Information
```
You: "Show system details"
Nix: Displays comprehensive system information

You: "What changed recently?"
Nix: Shows recent modifications with rollback options
```

## 🎉 Tips for Best Experience

1. **Be Natural** - Say things how you normally would
2. **Give Feedback** - Tell the system when it's wrong
3. **Trust the Learning** - It gets better over time
4. **Stay Secure** - The system will always confirm dangerous operations
5. **Explore** - Try new ways of asking for things

### Do's and Don'ts

**Do:**
- ✅ "Install Firefox"
- ✅ "I need something to edit photos"
- ✅ "Help me fix my WiFi"
- ✅ "What's using all my memory?"

**Don't:**
- ❌ "nix-env -iA nixos.firefox" (unless you prefer commands!)
- ❌ Use technical jargon unless necessary
- ❌ Worry about exact phrasing

## 👥 Real User Examples

### Grandma Grace (75, First Computer)
```
Grace: "The email stopped working"
System: "I'll help you get email working again. I see Thunderbird is installed but not responding. Would you like me to restart it?"
Grace: "Yes dear"
System: "Restarting Thunderbird... It's working now! Your email should appear shortly."
```

### Anxious Alex (28, Worries About Breaking Things)
```
Alex: "Did I break something? The screen went black for a second"
System: "Don't worry! That was just your screen saver starting. Your computer is fine. Nothing is broken. Would you like me to adjust when the screen saver starts?"
Alex: "Oh thank goodness. Yes, make it wait longer please"
System: "Setting screen saver to 30 minutes of inactivity. All done!"
```

### Curious Carlos (19, Wants to Understand)
```
Carlos: "How does installing software work in NixOS?"
System: "Great question! In NixOS, software is installed declaratively. This means we describe what we want, and NixOS figures out how to make it happen safely. Want me to show you an example?"
Carlos: "Yes! Show me"
System: "Let's install htop together. I'll add it to your configuration, which means it's recorded and can be rolled back if needed..."
```

### Developer Dana (35, Power User)
```
Dana: "Set up Rust with VS Code and cargo-watch"
System: "Setting up Rust development environment:
- Installing Rust stable toolchain
- Installing VS Code with Rust analyzer
- Adding cargo-watch
- Configuring formatting on save
Done! You're ready to `cargo run`"
```

### Mobility-Limited Morgan (42, Voice-Only User)
```
Morgan: "Open email" (voice command)
System: "Opening Thunderbird email client" *sound cue when ready*
Morgan: "Read first message"
System: "First message is from Amy, subject: 'Lunch tomorrow?' Shall I read the content?"
Morgan: "Yes please"
```

## 🚧 Common Issues

### System Doesn't Understand
- Try rephrasing naturally
- Use examples: "like Firefox but for email"
- Ask "what can you do with..."

### Wrong Assumption
- Say "no, I meant..."
- Correct it: "use home-manager instead"
- It learns from corrections

### Too Much/Little Help
- "Be more detailed"
- "Just do it"
- Adjust comfort level in settings

### Installation Fails
```
You: "Install docker"
System: "Docker installation failed. This might be because:
1. Your system needs a reboot for kernel modules
2. Virtualization is disabled in BIOS
3. Conflicting virtualbox installation
Which would you like me to check first?"
```

## 🆘 Getting Help

### Built-in Help
- "What can you do?" - Shows capabilities
- "Help me with [topic]" - Specific guidance
- "Explain [concept]" - Detailed explanations
- "Show me examples" - Real-world usage

### Tutorial Mode
```
You: "Teach me about package management"
System: "I'll guide you through package management! In NixOS, packages are managed declaratively. This means we list what we want in a configuration file, and NixOS makes it happen. Would you like to try installing something as practice?"
```

### Community Support
- **GitHub**: [Luminous-Dynamics/nix-for-humanity](https://github.com/Luminous-Dynamics/nix-for-humanity)
- **Matrix**: #nix-for-humanity:matrix.org
- **Forum**: discourse.nixos.org/c/nix-for-humanity

## 🌟 Remember

Nix for Humanity is your partner, not your boss. It's here to:
- Make NixOS accessible to everyone
- Learn and adapt to YOUR needs
- Keep you in control at all times
- Grow with you as you learn

The more you interact naturally, the better it understands you. Don't try to think like a computer - let the computer learn to think like you!

---

**Next Steps:**
- Try the [Quick Start Tutorial](./QUICK_START.md)
- Read about [Privacy & Security](./PRIVACY.md)
- See the [Development Roadmap](./ROADMAP.md)
- Learn about [Contributing](../CONTRIBUTING.md)

*Building bridges between humans and NixOS, one conversation at a time.* 🌉