# 🧪 Beta Testers Guide - Welcome!

Thank you for helping test Luminous Nix! Your feedback will directly shape this tool.

## 🚀 Quick Setup

```bash
# 1. Clone the repo
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix

# 2. Enter development environment
nix-shell

# 3. Install dependencies
poetry install

# 4. Test it works
./bin/ask-nix "help"
```

## 🎯 What to Test

### Priority 1: Basic Commands
Try these and report if they work:
- [ ] `ask-nix "install htop"` (pick a small package)
- [ ] `ask-nix "search for text editors"`
- [ ] `ask-nix "update my system"`
- [ ] `ask-nix "list installed packages"`

### Priority 2: Natural Language
Try expressing the same thing different ways:
- [ ] "I need a markdown editor"
- [ ] "find me something to edit markdown"
- [ ] "what can I use to write markdown files?"

### Priority 3: Edge Cases
- [ ] Typos: "isntall firefox" 
- [ ] Unclear requests: "get me that browser thing"
- [ ] Multiple actions: "install vim and search for themes"

## 📝 How to Report Issues

### Good Bug Report
```
Command: ask-nix "install firefox"
Expected: Firefox installs
Actual: Error message about profile incompatibility
NixOS Version: 25.11
Error: profile '/home/user/.local/state/nix/profiles/profile' is incompatible
```

### Great Bug Report
Includes the above PLUS:
- Steps you tried to fix it
- What worked before
- Screenshots/recordings
- Your use case

## 🎁 What You Get

- Your name in CONTRIBUTORS.md
- Direct influence on features
- Early access to new versions
- The satisfaction of making NixOS easier for everyone!

## 💬 Communication Channels

1. **GitHub Issues** - For bugs and features
2. **GitHub Discussions** - For questions and ideas
3. **Discord** - Real-time chat (coming soon)

## 🔥 Quick Feedback Form

After testing, answer these:

1. **What worked well?**
2. **What confused you?**
3. **What feature do you wish it had?**
4. **Would you recommend this to a NixOS beginner?**
5. **One thing to improve?**

## 🚨 Known Issues

Don't report these - we're already working on them:
- Voice interface not fully integrated
- Some tests are aspirational (not real)
- Profile compatibility errors with nix-env
- Learning system not activated yet

## 💡 Testing Tips

1. **Use dry-run first**: `LUMINOUS_DRY_RUN=true ask-nix "command"`
2. **Skip confirmations**: `LUMINOUS_SKIP_CONFIRM=true ask-nix "command"`
3. **See debug output**: `LUMINOUS_VERBOSE=2 ask-nix "command"`
4. **Try different personas**: Documentation coming soon

## 🙏 Thank You!

Seriously, beta testing is hard work. You're helping make NixOS accessible to people who would never otherwise use it. That's amazing!

Questions? Open an issue or discussion. We respond quickly!

---

*Happy testing! 🚀*