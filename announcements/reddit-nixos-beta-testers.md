# [Project] Natural Language Interface for NixOS - Looking for Beta Testers

Hi r/NixOS!

I've been working on **Luminous Nix**, a tool that lets you control NixOS using natural language instead of memorizing commands.

## Quick Examples

Instead of looking up commands, you can just type what you want:

```bash
ask-nix "install firefox"
ask-nix "search for markdown editors" 
ask-nix "update my system"
ask-nix "create python development environment"
ask-nix "why is my wifi not working?"
```

## Key Features

- **Natural language understanding** - Type what you want in plain English
- **Smart package search** - Finds packages by description, not just exact names
- **Configuration generation** - Generates NixOS configs from descriptions
- **Educational errors** - Learn NixOS through helpful error messages
- **Multiple personas** - Adapts explanations to your skill level
- **10x-1500x faster** - Uses native Python-Nix API (no subprocess overhead!)

## Who This Is For

- **Beginners** frustrated with NixOS complexity
- **Experienced users** who want faster workflows  
- **Anyone** who thinks "there must be an easier way"

## Current State

It's alpha software (v0.3.1) but core features work:
- ✅ Package installation/removal
- ✅ Package search
- ✅ System updates
- ✅ Configuration generation
- ✅ Development environments
- 🚧 Voice interface (coming soon)
- 🚧 Learning system (in progress)

## How to Try It

```bash
# Clone and setup
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix
nix-shell
poetry install

# Try it out
./bin/ask-nix "help"
./bin/ask-nix "search for video players"
./bin/ask-nix --dry-run "install firefox"  # Preview without executing
```

## What I Need From Beta Testers

1. **Try basic commands** - Does it understand what you're asking?
2. **Report confusion** - Where does it fail to understand intent?
3. **Suggest features** - What would make your NixOS life easier?
4. **Find bugs** - It's alpha, there will be bugs!

## Not a Replacement, An Assistant

This isn't trying to replace Nix/NixOS. It's a friendly layer on top that helps you:
- Learn NixOS gradually
- Get things done without memorizing syntax
- Understand what commands actually do

## Why I'm Building This

I love NixOS's power but hate its learning curve. I want my non-technical friends to be able to use NixOS without spending weeks learning functional programming.

## Interested?

- ⭐ [Star the GitHub repo](https://github.com/Luminous-Dynamics/luminous-nix)
- 🐛 [Report issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- 💬 Comment below with your thoughts
- 🚀 Try it and let me know what breaks!

This is open source (MIT license) and will always be free. Building in public with daily updates.

Thanks for reading! Would love to hear if this resonates with anyone else who's struggled with NixOS's learning curve.

---

**Edit**: Fixed install command parsing bug based on early feedback - thanks!