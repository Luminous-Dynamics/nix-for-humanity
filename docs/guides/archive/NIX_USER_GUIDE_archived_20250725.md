# 🗣️ Nix for Humanity - User Guide [ARCHIVED]

> **Note**: This guide has been merged into USER_GUIDE.md on [DATE]. 
> The consolidated guide combines the best content from both documents while maintaining focus on natural language interaction.
> This file is preserved for reference only.

---

# Original Content:

## How to Talk to Your Computer

Nix for Humanity lets you control NixOS using natural language. Just say what you want!

## Getting Started

### First Time Setup
When you first start Nix for Humanity:

```
System: "Hi! I'm Nix for Humanity. I'll help you manage your computer using natural conversation. What would you like to do?"

You: "Hi! Can you help me install a web browser?"

System: "Of course! I can install Firefox, Chrome, or Brave. Which would you prefer?"

You: "Firefox please"

System: "Installing Firefox web browser... Done! You'll find it in your applications menu. Would you like me to open it now?"
```

## Common Tasks

### Installing Software

**Natural ways to ask:**
- "Install Firefox"
- "I need a photo editor"
- "Can you get me that video player everyone uses?"
- "Add the thing for PDFs"

**Example conversations:**

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

### Fixing Problems

**Natural ways to ask:**
- "My WiFi isn't working"
- "The internet is broken"
- "Everything is really slow"
- "I can't print"

**Example conversations:**

```
You: "My WiFi stopped working"
System: "I'll help you fix that. Let me check your WiFi... I see your WiFi adapter is disabled. Would you like me to enable it?"

You: "Yes please"
System: "Enabling WiFi adapter... Done! I can see 3 networks available. Would you like to connect to one?"
```

### System Maintenance

**Natural ways to ask:**
- "Clean up my computer"
- "Free up some space"
- "Update everything"
- "Is my system healthy?"

**Example conversations:**

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

### Getting Information

**Natural ways to ask:**
- "What's my IP address?"
- "How much RAM do I have?"
- "What version of Linux am I running?"
- "Show me what's using my CPU"

**Example conversations:**

```
You: "What's taking up all my memory?"
System: "Here are your top memory users:
1. Firefox - 2.3GB (45%)
2. VS Code - 1.1GB (22%)
3. Slack - 0.8GB (16%)

You have 5.1GB total, with 0.8GB free. Would you like tips on reducing memory usage?"
```

## Understanding Responses

### Confirmation Before Action
Nix for Humanity always confirms before making changes:

```
You: "Remove Firefox"
System: "I'll remove Firefox web browser. This will also remove your bookmarks and settings. Are you sure?"
You: "Actually, no"
System: "No problem! Firefox remains installed."
```

### Learning From You
The system learns your preferences:

```
You: "Install my usual tools"
System: "Based on your history, I'll install:
- VS Code (your preferred editor)
- Firefox (your usual browser)
- Git (you use this often)
Is this correct?"
```

### Clear Error Messages
When something goes wrong:

```
You: "Install photoshop"
System: "Photoshop isn't available for Linux, but I can suggest alternatives:
- GIMP (free, very powerful)
- Krita (great for digital art)
- You could also run Photoshop in a Windows VM
What would work best for you?"
```

## Voice Commands

### Wake Words
- "Hey Nix"
- "Nix, please"
- "Computer" (if enabled)

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

## Accessibility Features

### Screen Reader Mode
Full compatibility with:
- NVDA
- JAWS
- Orca

Every response includes:
- Clear structure
- Descriptive text
- Keyboard shortcuts

### Keyboard Navigation
- `Tab` - Navigate options
- `Enter` - Confirm
- `Escape` - Cancel
- `Ctrl+L` - Jump to input
- `Ctrl+H` - Get help

### High Contrast Mode
Automatically adapts to your system theme

### Cognitive Accessibility
- Simple language mode available
- Step-by-step guidance
- No time pressures
- Can repeat information

## Tips for Best Results

### Be Natural
❌ "nix-env -iA nixos.firefox"
✅ "Install Firefox"

### Be Specific When Needed
❌ "Install that thing"
✅ "Install that password manager with the browser extension"

### Ask for Help
✅ "What can you do?"
✅ "How do I..."
✅ "Explain what this means"

### Use Context
```
You: "Install VS Code"
System: "Installing VS Code..."
You: "Also the Python extension for it"
System: "I'll install the Python extension for VS Code..."
```

## Privacy & Safety

### Your Privacy
- ✅ All processing happens locally
- ✅ No data sent to cloud
- ✅ No usage tracking
- ✅ Voice never leaves your computer

### Safety Features
- Always shows what will change
- Confirms before system modifications
- Can undo recent changes
- Prevents dangerous operations

## Getting Help

### Built-in Help
- "What can you do?"
- "Help me with [topic]"
- "Explain [concept]"
- "Show me examples"

### Tutorial Mode
```
You: "Teach me about package management"
System: "I'll guide you through package management! In NixOS, packages are managed declaratively. This means... Would you like to try installing something as practice?"
```

### Community
- GitHub: Luminous-Dynamics/nix-for-humanity
- Matrix: #nix-for-humanity:matrix.org
- Forum: discourse.nixos.org/nix-for-humanity

## Personas & Examples

### Grandma Grace
```
Grace: "The email stopped working"
System: "I'll help you get email working again. I see Thunderbird is installed but not responding. Would you like me to restart it?"
Grace: "Yes dear"
System: "Restarting Thunderbird... It's working now! Your email should appear shortly."
```

### Anxious Alex
```
Alex: "Did I break something? The screen went black for a second"
System: "Don't worry! That was just your screen saver starting. Your computer is fine. Nothing is broken. Would you like me to adjust when the screen saver starts?"
```

### Curious Carlos
```
Carlos: "How does installing software work in NixOS?"
System: "Great question! In NixOS, software is installed declaratively. This means we describe what we want, and NixOS figures out how to make it happen. Want me to show you an example?"
```

### Developer Dana
```
Dana: "Set up Rust with VS Code and cargo-watch"
System: "Setting up Rust development environment:
- Installing Rust stable toolchain
- Installing VS Code with Rust analyzer
- Adding cargo-watch
- Configuring formatting on save
Done! You're ready to `cargo run`"
```

### Mobility-Limited Morgan
```
Morgan: "Open email" (voice only)
System: "Opening Thunderbird email client" *sound cue when ready*
Morgan: "Read first message"
System: "First message is from Amy, subject: 'Lunch tomorrow?' Shall I read the content?"
```

---

Next: See [ROADMAP.md](./ROADMAP.md) for project timeline and future plans →