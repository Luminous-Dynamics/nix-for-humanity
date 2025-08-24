#!/usr/bin/env python3
"""
Discord Simple Setup - No external dependencies
"""

import webbrowser
import time

def save_to_file(filename, content):
    """Save content to file for manual copying"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✅ Saved to {filename}")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          🌟 LUMINOUS NIX DISCORD SIMPLE SETUP 🌟             ║
╚══════════════════════════════════════════════════════════════╝

This will guide you through Discord setup and save all content
to files that you can copy from!
    """)
    
    input("Press ENTER to start...")
    
    # Step 1: Open Discord
    print("\n📌 STEP 1: Opening Discord in browser...")
    webbrowser.open("https://discord.com/channels/@me")
    time.sleep(2)
    
    print("""
Now create your server:
1. Click the '+' button (left sidebar)
2. Choose "Create My Own"
3. Choose "For me and my friends"
4. Server name: Luminous Nix | Natural Language NixOS
5. Click Create
    """)
    
    input("\nPress ENTER when server is created...")
    
    # Step 2: Channel Structure
    print("\n📌 STEP 2: Creating Channels")
    print("\nCreate these channels (I'll save names to a file):")
    
    channels = """CATEGORIES AND CHANNELS TO CREATE:

📢 INFORMATION (category)
  - welcome
  - announcements
  - rules

💬 GENERAL (category)
  - general
  - introductions
  - showcase

🛠️ SUPPORT (category)
  - help
  - bugs

💻 DEVELOPMENT (category)
  - contributors"""
    
    save_to_file("discord_channels.txt", channels)
    print(f"\nChannel structure saved to discord_channels.txt")
    print("Create each category, then add channels under it.")
    
    input("\nPress ENTER when channels are created...")
    
    # Step 3: Welcome Message
    print("\n📌 STEP 3: Welcome Message for #welcome")
    
    welcome_msg = """**🌟 Welcome to Luminous Nix!**

Making NixOS accessible through natural language.

**What is Luminous Nix?**
Instead of complex commands like `nix-env -iA nixos.firefox`, just say:
```
ask-nix "install firefox"
```

**Built Different**
• Created by 1 developer + AI collaboration
• 2 weeks development time
• $200 total cost
• Beats $4.2M enterprise solutions

**Quick Start**
```bash
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix
poetry install
./bin/ask-nix "help"
```

**Get Involved**
• Introduce yourself in #general
• Get help in #help
• Report bugs in #bugs
• Show your configs in #showcase

**Important Links**
• GitHub: https://github.com/Luminous-Dynamics/luminous-nix
• Hacker News: [Launch Thread Tuesday]

**Philosophy**
"Technology should adapt to humans, not the other way around."

Welcome to the revolution! 🚀"""
    
    save_to_file("discord_welcome.txt", welcome_msg)
    print("\nCopy from discord_welcome.txt and paste in #welcome channel")
    
    input("\nPress ENTER when posted...")
    
    # Step 4: Rules
    print("\n📌 STEP 4: Rules for #rules")
    
    rules_msg = """**📜 Community Guidelines**

**✅ DO**
• Be kind and patient with everyone
• Ask questions - no matter how basic
• Share your successes AND failures
• Help newcomers get started
• Respect all skill levels
• Make technology accessible

**❌ DON'T**
• No harassment or discrimination
• No spam or unsolicited promotion
• No "RTFM" responses
• No gatekeeping
• No dismissing accessibility needs

**🎯 Remember**
We're making NixOS accessible to EVERYONE - from developers to grandmothers!

Questions? Ask in #help"""
    
    save_to_file("discord_rules.txt", rules_msg)
    print("\nCopy from discord_rules.txt and paste in #rules channel")
    
    input("\nPress ENTER when posted...")
    
    # Step 5: Announcement
    print("\n📌 STEP 5: Announcement for #announcements")
    
    announce_msg = """**🎉 WE'RE LAUNCHING ON HACKER NEWS!**

After 2 weeks of intense development using Sacred Trinity Development (Human + Claude + Local LLM), Luminous Nix is ready to revolutionize NixOS!

**🚀 Show Your Support**
⭐ Star on GitHub: https://github.com/Luminous-Dynamics/luminous-nix
🔼 Upvote on HN: [Coming Tuesday 9 AM EST]
💬 Tell your friends!

**✨ What's Working**
• Natural language → NixOS commands
• 10x-1500x faster with Python-Nix API
• Multiple personas (Grandma to Developer)
• 100% local and private

**🔮 Coming Soon**
• Voice interface
• More personas
• GUI interface
• Cross-platform support

Join us in making Linux accessible to everyone! 🌟"""
    
    save_to_file("discord_announcement.txt", announce_msg)
    print("\nCopy from discord_announcement.txt and paste in #announcements")
    
    input("\nPress ENTER when posted...")
    
    # Step 6: Permissions
    print("\n📌 STEP 6: Set Permissions")
    print("""
Make these channels read-only:
1. Right-click #welcome → Edit Channel → Permissions
2. Click @everyone → Toggle OFF "Send Messages"
3. Repeat for #announcements and #rules
    """)
    
    input("\nPress ENTER when permissions are set...")
    
    # Step 7: Get Invite
    print("\n📌 STEP 7: Create Invite Link")
    print("""
1. Right-click on #general channel
2. Click "Invite People"
3. Click "Edit invite link"
4. Set to "Never expire"
5. Copy the link
    """)
    
    invite = input("\nPaste your invite link here: ")
    
    # Save everything
    summary = f"""DISCORD SETUP COMPLETE!
======================

Discord Invite: {invite}

Share on Hacker News:
"Join our Discord community: {invite}"

Share on Twitter:
"🌟 Luminous Nix Discord is LIVE!
Natural language for NixOS.
Join us: {invite}
#NixOS #OpenSource"

Share on GitHub README:
"[![Discord](https://img.shields.io/discord/YOUR_SERVER_ID)](invite)"

All content saved in:
- discord_channels.txt (channel structure)
- discord_welcome.txt (welcome message)
- discord_rules.txt (rules)
- discord_announcement.txt (announcement)
"""
    
    save_to_file("discord_setup_complete.txt", summary)
    
    print("\n" + "="*60)
    print("🎉 DISCORD SETUP COMPLETE!")
    print("="*60)
    print(f"\n📧 Your invite link: {invite}")
    print("\nAll information saved to discord_setup_complete.txt")
    print("\n✅ Your Discord is ready for launch!")

if __name__ == "__main__":
    main()