#!/usr/bin/env python3
"""
Discord Instant Setup Script
Run this to create your server in seconds!
"""

import webbrowser
import pyperclip
import time
import sys

def create_discord_server():
    """Guide through Discord server creation with automation"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║          🌟 LUMINOUS NIX DISCORD INSTANT SETUP 🌟            ║
╚══════════════════════════════════════════════════════════════╝

This script will guide you through creating your Discord server
and automatically copy content to your clipboard!

Prerequisites:
✓ Discord account logged in
✓ Web browser ready
    """)
    
    input("Press ENTER when ready to start...")
    
    # Step 1: Open Discord
    print("\n📌 STEP 1: Opening Discord...")
    webbrowser.open("https://discord.com/channels/@me")
    time.sleep(2)
    
    print("""
Create your server:
1. Click the '+' button (left sidebar)
2. Choose "Create My Own"
3. Choose "For me and my friends"
4. Server name: Luminous Nix | Natural Language NixOS
5. Click Create
    """)
    
    input("\nPress ENTER when server is created...")
    
    # Step 2: Channel Structure
    print("\n📌 STEP 2: Creating Channels")
    print("I'll copy the channel names to your clipboard one by one...")
    
    channels = [
        ("CATEGORY", "📢 INFORMATION"),
        ("CHANNEL", "welcome"),
        ("CHANNEL", "announcements"),
        ("CHANNEL", "rules"),
        ("CATEGORY", "💬 GENERAL"),
        ("CHANNEL", "general"),
        ("CHANNEL", "introductions"),
        ("CHANNEL", "showcase"),
        ("CATEGORY", "🛠️ SUPPORT"),
        ("CHANNEL", "help"),
        ("CHANNEL", "bugs"),
        ("CATEGORY", "💻 DEVELOPMENT"),
        ("CHANNEL", "contributors"),
    ]
    
    for channel_type, name in channels:
        try:
            pyperclip.copy(name)
            if channel_type == "CATEGORY":
                print(f"\n➕ Create CATEGORY: '{name}' (copied to clipboard!)")
                print("   Right-click on server name → Create Category → Paste")
            else:
                print(f"   ├─ Add channel: '{name}' (copied to clipboard!)")
                print("      Right-click category → Create Channel → Paste")
            input("   Press ENTER when done...")
        except:
            print(f"Copy manually: {name}")
            input("   Press ENTER when done...")
    
    # Step 3: Welcome Message
    print("\n📌 STEP 3: Posting Welcome Message")
    
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
• Hacker News: [Launch Thread]

**Philosophy**
"Technology should adapt to humans, not the other way around."

Welcome to the revolution! 🚀"""
    
    try:
        pyperclip.copy(welcome_msg)
        print("✅ Welcome message copied to clipboard!")
        print("\nGo to #welcome channel and paste (Ctrl+V)")
    except:
        print("❌ Couldn't copy to clipboard. Message saved to: welcome_message.txt")
        with open("welcome_message.txt", "w") as f:
            f.write(welcome_msg)
    
    input("\nPress ENTER when posted...")
    
    # Step 4: Rules
    print("\n📌 STEP 4: Posting Rules")
    
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
    
    try:
        pyperclip.copy(rules_msg)
        print("✅ Rules copied to clipboard!")
        print("\nGo to #rules channel and paste (Ctrl+V)")
    except:
        print("❌ Couldn't copy to clipboard. Message saved to: rules_message.txt")
        with open("rules_message.txt", "w") as f:
            f.write(rules_msg)
    
    input("\nPress ENTER when posted...")
    
    # Step 5: Launch Announcement
    print("\n📌 STEP 5: Launch Announcement")
    
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
    
    try:
        pyperclip.copy(announce_msg)
        print("✅ Announcement copied to clipboard!")
        print("\nGo to #announcements channel and paste (Ctrl+V)")
    except:
        print("❌ Couldn't copy to clipboard. Message saved to: announcement_message.txt")
        with open("announcement_message.txt", "w") as f:
            f.write(announce_msg)
    
    input("\nPress ENTER when posted...")
    
    # Step 6: Permissions
    print("\n📌 STEP 6: Setting Permissions")
    print("""
Make these channels read-only:
1. Right-click #welcome → Edit Channel → Permissions
2. Click @everyone → Deny "Send Messages"
3. Repeat for #announcements and #rules
    """)
    
    input("\nPress ENTER when permissions are set...")
    
    # Step 7: Get Invite
    print("\n📌 STEP 7: Creating Invite Link")
    print("""
1. Right-click on #general channel
2. Click "Invite People"
3. Click "Edit invite link"
4. Set to "Never expire"
5. Copy the link
    """)
    
    invite = input("\nPaste your invite link here: ")
    
    # Step 8: Share Templates
    print("\n📌 STEP 8: Ready to Share!")
    
    hn_share = f"""Discord community is live! Join us: {invite}
    
We're building the future of NixOS interaction together."""
    
    twitter_share = f"""🌟 Luminous Nix Discord is LIVE!

Making NixOS accessible through natural language.
"install firefox" → It just works

Built in 2 weeks for $200 (vs $4.2M quote!)

Join us: {invite}

#NixOS #OpenSource #AI"""
    
    print("\n✅ DISCORD SETUP COMPLETE!")
    print("="*50)
    print(f"\n📧 Your invite link: {invite}")
    print("\n📝 Share on Hacker News:")
    print(hn_share)
    print("\n🐦 Share on Twitter:")
    print(twitter_share)
    
    # Save everything
    with open("discord_launch_info.txt", "w") as f:
        f.write(f"Discord Invite: {invite}\n\n")
        f.write(f"HN Share:\n{hn_share}\n\n")
        f.write(f"Twitter Share:\n{twitter_share}\n")
    
    print("\n💾 All information saved to: discord_launch_info.txt")
    print("\n🚀 Your Discord is ready for launch! Good luck!")

if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        print("Installing pyperclip for clipboard support...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
        import pyperclip
    
    create_discord_server()