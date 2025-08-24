# 📹 2-Minute Demo Video Script for Hacker News

## Setup
- Record with phone in landscape mode
- Clean terminal with dark theme
- Have Luminous Nix ready to run

## Script (2 minutes)

### Opening (10 seconds)
"Hi Hacker News! I'm Tristan, and I built Luminous Nix - a natural language interface for NixOS. Let me show you how it works."

### Demo 1: Install Package (20 seconds)
```bash
./bin/ask-nix "install firefox"
```
"Instead of remembering complex nix commands, just say what you want. Luminous Nix understands natural language and generates the right NixOS command."

### Demo 2: Create Dev Environment (20 seconds)
```bash
./bin/ask-nix "create python environment with numpy and pandas"
```
"It handles complex tasks too. Creating development environments is just a conversation."

### Demo 3: System Management (20 seconds)
```bash
./bin/ask-nix "update my system"
./bin/ask-nix "show system health"
```
"System management becomes intuitive. No more googling NixOS commands."

### Performance (20 seconds)
"The secret? We use a native Python-Nix API that's 10 to 1500 times faster than subprocess calls. No more timeouts, real-time progress, instant responses."

### Development Story (20 seconds)
"Here's the kicker - I built this in 2 weeks for about $200 a month using AI collaboration. Claude Code helped with architecture, a local LLM provided NixOS expertise, and I handled the vision and testing."

### Closing (10 seconds)
"Luminous Nix is open source and ready to try. The question is: what if your OS understood you, not the other way around? Check the Show HN post for links!"

## Recording Tips
1. Keep energy high but natural
2. Show actual terminal output
3. Let commands complete before speaking
4. Smile - it comes through in your voice!

## Backup: Quick GIF Demo
If video doesn't work, record these as GIFs:
1. `ask-nix "install firefox"` → command generation
2. `ask-nix "create python dev environment"` → flake creation
3. `ask-nix "why is my wifi not working?"` → intelligent help