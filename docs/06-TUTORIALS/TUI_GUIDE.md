# 🖥️ Nix for Humanity TUI (Terminal User Interface) Guide

*A beautiful, intuitive way to interact with NixOS through natural conversation*

## Overview

The Nix for Humanity TUI is a modern terminal interface that brings the power of natural language NixOS management to your fingertips. Built with the Textual framework, it provides a rich, interactive experience while maintaining the efficiency of terminal-based workflows.

## Getting Started

### Launching the TUI

The TUI launches automatically when you run `ask-nix` without any arguments:

```bash
# Just type:
ask-nix

# The system will detect you're in an interactive terminal and launch the TUI
✨ Launching Nix for Humanity interactive interface...
💡 Tip: For CLI mode, use: ask-nix 'your question'
```

### Alternative Launch Methods

```bash
# Direct TUI launch
nix-tui

# Via Python module
python3 -m nix_for_humanity.tui.app
```

## Interface Overview

```
┌─ Nix for Humanity ─────────────────────────────────────┐
│                                                         │
│  Welcome! I'm here to help you with NixOS.            │
│  Current personality: Friendly                          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Chat area - your conversation appears here]          │
│                                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  > Type your message here...                           │
└─────────────────────────────────────────────────────────┘
 Ctrl+P: Personality | Ctrl+H: Help | Ctrl+C: Clear | Ctrl+Q: Quit
```

## Key Features

### 1. Natural Conversation
Simply type what you want to do in plain English:
- "install firefox"
- "update my system"
- "show me what packages are installed"
- "help me set up development tools"

### 2. Plan/Execute Pattern
The TUI implements a safe plan/execute pattern:
1. **You ask** for something
2. **System plans** what to do
3. **You review** the plan
4. **You decide** whether to execute

Example:
```
You: install vscode