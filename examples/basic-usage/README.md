# Basic Usage Examples

## Common Scenarios

### Installing Software

```
User: install firefox
System: Installing Firefox web browser...

User: i need a text editor
System: Popular text editors include VS Code, Vim, and Emacs. Which would you prefer?
User: the first one
System: Installing VS Code...
```

### System Updates

```
User: update my system
System: I'll update your NixOS system. This may take about 15 minutes. Continue?

User: just security updates
System: Checking for security updates only...
```

### Troubleshooting

```
User: wifi not working
System: Let me check your network status... I see the WiFi adapter is disabled. Should I enable it?

User: my computer is slow
System: Let me analyze system performance... High memory usage detected. Would you like me to:
1. Show which programs are using memory
2. Clean up unnecessary files
3. Restart memory-hungry services
```

### Development Setup

```
User: i want to code in python
System: I'll set up Python development for you. Based on your past usage, should I include:
- Python 3.11
- pip and virtualenv
- Jupyter notebook
- Common data science libraries (numpy, pandas)?

User: yes
System: Setting up complete Python development environment...
```

### Learning Together

```
User: install the thing for making videos
System: For video creation, I found:
- OBS Studio (recording/streaming)
- Kdenlive (video editing)
- HandBrake (video conversion)
Which matches what you need?

User: editing
System: Installing Kdenlive video editor...
[Next time]
User: install video thing
System: Installing Kdenlive (the video editor you used before)...
```

## Natural Conversations

The system understands context and maintains conversation:

```
User: show me what browsers are available
System: Available web browsers:
- Firefox (recommended, open source)
- Chromium (open source Chrome)
- Brave (privacy-focused)
- Qutebrowser (keyboard-driven)

User: tell me more about the third one
System: Brave is a privacy-focused browser that blocks ads and trackers by default...

User: install it
System: Installing Brave browser...
```

## Voice Input Examples

Same commands work with voice:

🎤 "install firefox"
🎤 "update my system"
🎤 "something is broken"
🎤 "help me edit photos"

## The AI Learns Your Style

Over time, the system adapts:

### Week 1
```
User: install postgresql
System: Installing PostgreSQL database...
```

### Week 3
```
User: install postgres
System: Installing PostgreSQL with your usual extensions (pgadmin, postgis)...
```

### Month 2
```
User: new database project
System: Should I set up PostgreSQL with your standard development configuration?
```