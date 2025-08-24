# 🚀 Discord Server Quick Setup Guide

## Step 1: Create the Server (2 minutes)

1. Go to [discord.com](https://discord.com) or open Discord app
2. Click the `+` button in left sidebar
3. Choose "Create My Own"
4. Select "For a club or community"
5. Server name: **Luminous Nix | Natural Language NixOS**
6. Upload logo (create simple one at canva.com if needed)
7. Click "Create"

## Step 2: Essential Channels Setup (5 minutes)

### Delete Default Channels
- Delete `#general` and `#voice` (we'll recreate with better structure)

### Create Categories and Channels
Right-click in channel area → Create Category, then add channels:

**📢 INFORMATION**
- `#welcome` - Read-only welcome message
- `#announcements` - Updates and releases  
- `#rules` - Community guidelines
- `#roadmap` - Development roadmap

**💬 GENERAL**
- `#general` - Main chat
- `#introductions` - New member intros
- `#showcase` - Show off your configs
- `#off-topic` - Random chat

**🛠️ SUPPORT**
- `#installation-help` - Getting started
- `#questions` - General Q&A
- `#bug-reports` - Issue reporting
- `#feature-requests` - Suggestions

**💻 DEVELOPMENT**
- `#contributors` - For active contributors
- `#dev-discussion` - Technical discussion
- `#pull-requests` - PR discussions
- `#sacred-trinity` - AI development chat

**🎓 LEARNING**
- `#tutorials` - Guides and tips
- `#resources` - Useful links
- `#daily-tips` - Daily NixOS tips

## Step 3: Copy-Paste Content

### For #welcome channel:

```markdown
# 🌟 Welcome to Luminous Nix!

**Making NixOS accessible through natural language.**

## 🚀 What is Luminous Nix?

Instead of complex commands like `nix-env -iA nixos.firefox`, just say:
```
ask-nix "install firefox"
```

Built by 1 developer + AI in 2 weeks for $200 (beating $4.2M enterprise quotes!)

## 📚 Quick Start

**Install:**
```bash
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix
poetry install
./bin/ask-nix "help"
```

## 🎯 Get Involved

1. Introduce yourself in #introductions 
2. Get help in #installation-help
3. Share your setup in #showcase
4. Contribute ideas in #feature-requests

## 🔗 Important Links

- GitHub: https://github.com/Luminous-Dynamics/luminous-nix
- Documentation: [Coming Soon]
- Demo Video: [Coming Soon]

## 💡 Philosophy

"Technology should adapt to humans, not the other way around."

Welcome to the revolution! 🚀
```

### For #rules channel:

```markdown
# 📜 Community Guidelines

## 🌟 Core Values

**1. Be Excellent to Each Other**
- Respect all skill levels
- Help newcomers with patience
- No RTFM responses
- Celebrate learning

**2. Accessibility First**
- Technology for everyone
- No gatekeeping
- Support all abilities
- Inclusive language

**3. Privacy Matters**
- Local-first approach
- No data harvesting
- Respect user privacy
- Secure by default

## ❌ Zero Tolerance

- Harassment or discrimination
- Spam or self-promotion (without permission)
- Dismissing accessibility needs
- Toxic behavior

## ✅ Encouraged

- Asking questions (no matter how basic)
- Sharing successes AND failures
- Contributing ideas
- Helping others
- Having fun!

## 🎯 Remember

We're making NixOS accessible to EVERYONE - from developers to grandmothers!

Questions? Ask in #questions or DM @Tristan
```

### For #announcements (pin this):

```markdown
# 🎉 Launch Announcement!

**Luminous Nix is LIVE on Hacker News!**

After 2 weeks of intense development using Sacred Trinity Development (Human + Claude + Local LLM), we're ready to revolutionize how people interact with NixOS.

## 🚀 Show Your Support

- ⭐ Star us on GitHub: [link]
- 🔼 Upvote on HN: [link]
- 🐦 Share on Twitter: [link]
- 💬 Tell your friends!

## 🎯 What's Working

- ✅ Natural language to NixOS commands
- ✅ 10x-1500x performance (Python-Nix API)
- ✅ Multiple personas (Grandma to Developer)
- ✅ 100% local and private

## 🔮 Coming Soon

- Voice interface
- More personas
- GUI interface
- Ubuntu/Arch support

**Join us in making Linux accessible to everyone!**
```

## Step 4: Server Settings (3 minutes)

### Go to Server Settings (right-click server name)

**Overview:**
- Upload server icon/banner if you have them

**Roles (Settings → Roles):**

Create these roles with colors:

1. **@Creator** (Gold) - You
2. **@Core Team** (Purple) - Future maintainers
3. **@Contributor** (Blue) - Made a PR
4. **@Pioneer** (Green) - First 100 members
5. **@Bug Hunter** (Red) - Found bugs
6. **@everyone** (Default) - Base permissions

**Permissions:**
- @Creator: Administrator
- @Core Team: Manage channels, messages, kick/ban
- @Contributor: Manage messages, embed links
- Others: Send messages, read, voice

**Channels Permissions:**
- Make #welcome, #announcements, #rules read-only for @everyone
- Make #contributors require @Contributor role

**Community Settings:**
- Enable Community (Settings → Enable Community)
- Set #rules as rules channel
- Set #welcome as welcome channel
- Enable member screening

**Moderation:**
- Verification Level: Medium
- Explicit Content Filter: All members

## Step 5: Invite Setup (2 minutes)

### Create Permanent Invite
1. Right-click on #welcome channel
2. "Invite People"
3. "Edit invite link"
4. Set to "Never expire"
5. Custom link: `discord.gg/luminous-nix` (if available)

### Create Tracking Invites
Create separate invites for:
- `discord.gg/luminous-hn` - For Hacker News
- `discord.gg/luminous-reddit` - For Reddit
- `discord.gg/luminous-twitter` - For Twitter

This helps track where members come from!

## Step 6: Quick Bots (Optional - 5 minutes)

### MEE6 Bot (easiest)
1. Go to [mee6.xyz](https://mee6.xyz)
2. Add to your server
3. Configure:
   - Welcome message
   - Auto-roles for new members
   - Leveling system
   - Custom commands

### Suggested MEE6 Commands:
- `!install` → "Check out our installation guide: [link]"
- `!demo` → "Watch our demo: [link]"
- `!help` → "Ask in #questions or check #tutorials"
- `!github` → "https://github.com/Luminous-Dynamics/luminous-nix"

## Step 7: Launch Day Prep (2 minutes)

### Pin Important Messages
- Pin welcome post in #general
- Pin announcement in #announcements
- Pin guidelines in #rules

### Set Status
Your status: "🚀 Launching on HN | Ask me anything!"

### Prepare Quick Responses

Save these for copy-paste:

**For new members:**
"Welcome! 🌟 Great to have you here! Check out #welcome to get started, and feel free to introduce yourself in #introductions!"

**For helpers:**
"Thanks for helping out! You've earned the @Contributor role! 🙏"

**For questions:**
"Great question! Let me help you with that..." [personalized response]

## Step 8: Share Your Server!

### Your invite links ready to share:

**Main invite:** `discord.gg/luminous-nix`

**Tracking invites:**
- HN Post: `discord.gg/luminous-hn`
- Reddit: `discord.gg/luminous-reddit`  
- Twitter: `discord.gg/luminous-twitter`

### Where to share:
1. In your Hacker News post
2. In your GitHub README
3. On your landing page
4. In your Twitter bio
5. In Reddit posts

## 🎉 You're Ready!

Your Discord is now set up and ready for launch! Total time: ~15 minutes

**Pro tips:**
- Greet first 10 members personally
- Give @Pioneer role to first 100
- Be active first week to set culture
- Celebrate milestones (10, 50, 100 members)

**Need help?** Discord setup is free - many community members would happily help moderate!

---

🚀 **Launch day mantra:** "Technology should adapt to humans, not the other way around!"