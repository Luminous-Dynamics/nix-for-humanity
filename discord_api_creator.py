#!/usr/bin/env python3
"""
Discord API Server Creator
Creates a Discord server using Discord's API directly
"""

import requests
import json
import sys
import webbrowser
from datetime import datetime

class DiscordServerCreator:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://discord.com/api/v10"
    
    def create_guild(self):
        """Create a new guild (server)"""
        print("🌟 Creating Luminous Nix server...")
        
        guild_data = {
            "name": "Luminous Nix | Natural Language NixOS",
            "region": "us-west",
            "icon": None,  # Can add base64 image data here
            "channels": [
                {"name": "welcome", "type": 0, "parent_id": None},
                {"name": "general", "type": 0, "parent_id": None},
                {"name": "help", "type": 0, "parent_id": None},
                {"name": "bugs", "type": 0, "parent_id": None},
            ],
            "roles": [
                {
                    "name": "Creator",
                    "color": 0xFFD700,  # Gold
                    "hoist": True,
                    "mentionable": True
                },
                {
                    "name": "Pioneer",
                    "color": 0x00FF00,  # Green
                    "hoist": True,
                    "mentionable": False
                },
                {
                    "name": "Contributor",
                    "color": 0x0099FF,  # Blue
                    "hoist": True,
                    "mentionable": False
                }
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/guilds",
            headers=self.headers,
            json=guild_data
        )
        
        if response.status_code == 201:
            guild = response.json()
            print(f"✅ Server created: {guild['name']}")
            return guild
        else:
            print(f"❌ Failed to create server: {response.text}")
            return None
    
    def setup_channels(self, guild_id):
        """Set up channel structure"""
        print("📁 Setting up channels...")
        
        # Create categories
        categories = [
            ("📢 INFORMATION", ["welcome", "announcements", "rules"]),
            ("💬 GENERAL", ["general", "introductions", "showcase"]),
            ("🛠️ SUPPORT", ["help", "bugs", "feature-requests"]),
            ("💻 DEVELOPMENT", ["contributors", "dev-discussion"])
        ]
        
        for cat_name, channels in categories:
            # Create category
            cat_data = {
                "name": cat_name,
                "type": 4  # Category type
            }
            
            cat_response = requests.post(
                f"{self.base_url}/guilds/{guild_id}/channels",
                headers=self.headers,
                json=cat_data
            )
            
            if cat_response.status_code == 201:
                category = cat_response.json()
                print(f"  ✅ Created category: {cat_name}")
                
                # Create channels in category
                for channel_name in channels:
                    channel_data = {
                        "name": channel_name,
                        "type": 0,  # Text channel
                        "parent_id": category['id']
                    }
                    
                    ch_response = requests.post(
                        f"{self.base_url}/guilds/{guild_id}/channels",
                        headers=self.headers,
                        json=channel_data
                    )
                    
                    if ch_response.status_code == 201:
                        print(f"    ├─ {channel_name}")
    
    def post_welcome_content(self, guild_id):
        """Post initial messages"""
        print("💬 Posting welcome content...")
        
        # Get channels
        channels_response = requests.get(
            f"{self.base_url}/guilds/{guild_id}/channels",
            headers=self.headers
        )
        
        if channels_response.status_code == 200:
            channels = channels_response.json()
            
            # Find welcome channel
            welcome_channel = next((c for c in channels if c['name'] == 'welcome'), None)
            if welcome_channel:
                welcome_message = {
                    "content": "",
                    "embeds": [{
                        "title": "🌟 Welcome to Luminous Nix!",
                        "description": "Making NixOS accessible through natural language.",
                        "color": 0x667eea,
                        "fields": [
                            {
                                "name": "🚀 What is Luminous Nix?",
                                "value": "Instead of `nix-env -iA nixos.firefox`, just say:\n```ask-nix \"install firefox\"```",
                                "inline": False
                            },
                            {
                                "name": "💡 Built Different",
                                "value": "• 1 developer + AI collaboration\n• 2 weeks development\n• $200 total cost\n• Beats $4.2M enterprise quotes",
                                "inline": False
                            },
                            {
                                "name": "🔗 Links",
                                "value": "[GitHub](https://github.com/Luminous-Dynamics/luminous-nix) | [Documentation](https://github.com/Luminous-Dynamics/luminous-nix/docs)",
                                "inline": False
                            }
                        ],
                        "footer": {
                            "text": "Welcome to the revolution! 🚀"
                        }
                    }]
                }
                
                msg_response = requests.post(
                    f"{self.base_url}/channels/{welcome_channel['id']}/messages",
                    headers=self.headers,
                    json=welcome_message
                )
                
                if msg_response.status_code == 200:
                    print("  ✅ Posted welcome message")
    
    def create_invite(self, guild_id):
        """Create permanent invite link"""
        print("🔗 Creating invite link...")
        
        # Get first text channel
        channels_response = requests.get(
            f"{self.base_url}/guilds/{guild_id}/channels",
            headers=self.headers
        )
        
        if channels_response.status_code == 200:
            channels = channels_response.json()
            general = next((c for c in channels if c['name'] == 'general'), channels[0])
            
            invite_data = {
                "max_age": 0,  # Never expire
                "max_uses": 0,  # Unlimited uses
                "temporary": False
            }
            
            invite_response = requests.post(
                f"{self.base_url}/channels/{general['id']}/invites",
                headers=self.headers,
                json=invite_data
            )
            
            if invite_response.status_code == 200:
                invite = invite_response.json()
                return f"https://discord.gg/{invite['code']}"
        
        return None

def setup_with_user_token():
    """Alternative: Use user token to create server"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     DISCORD SERVER CREATOR - USER TOKEN METHOD              ║
╚══════════════════════════════════════════════════════════════╝

⚠️  This method uses your user token (advanced users only)

To get your token:
1. Open Discord in browser
2. Press F12 (Developer Tools)
3. Go to Network tab
4. Send any message in any channel
5. Look for request to 'messages'
6. In Headers, find 'authorization: [YOUR_TOKEN]'
    """)
    
    token = input("Paste your user token (or 'skip' to cancel): ")
    
    if token.lower() == 'skip':
        return
    
    # User API endpoints are slightly different
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    # Create server
    guild_data = {
        "name": "Luminous Nix | Natural Language NixOS",
        "icon": None,
        "channels": [],
        "system_channel_id": 0
    }
    
    response = requests.post(
        "https://discord.com/api/v10/guilds",
        headers=headers,
        json=guild_data
    )
    
    if response.status_code in [200, 201]:
        guild = response.json()
        print(f"✅ Server created successfully!")
        print(f"Server ID: {guild['id']}")
        print(f"Server Name: {guild['name']}")
        
        # Generate invite using vanity URL or first channel
        if 'vanity_url_code' in guild:
            invite_url = f"https://discord.gg/{guild['vanity_url_code']}"
        else:
            invite_url = f"Open Discord to get invite link from server"
        
        print(f"\n📧 Invite: {invite_url}")
        
        # Open Discord in browser
        webbrowser.open(f"https://discord.com/channels/{guild['id']}")
        
        return guild
    else:
        print(f"❌ Failed: {response.text}")
        return None

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        LUMINOUS NIX DISCORD SERVER CREATOR                  ║
╚══════════════════════════════════════════════════════════════╝

Choose method:
1. Bot Token (requires bot setup)
2. User Token (instant but advanced)
3. Manual guide (step-by-step instructions)
    """)
    
    choice = input("Select (1/2/3): ")
    
    if choice == "1":
        print("\nBot Token Method Selected")
        print("First, create a bot at: https://discord.com/developers/applications")
        token = input("Enter bot token: ")
        
        if token:
            creator = DiscordServerCreator(token)
            guild = creator.create_guild()
            
            if guild:
                guild_id = guild['id']
                creator.setup_channels(guild_id)
                creator.post_welcome_content(guild_id)
                invite = creator.create_invite(guild_id)
                
                if invite:
                    print("\n" + "="*50)
                    print("🎉 SERVER SETUP COMPLETE!")
                    print("="*50)
                    print(f"\n📧 Invite link: {invite}")
                    print("\nShare this on:")
                    print(f"- Hacker News: {invite}")
                    print(f"- GitHub README: {invite}")
                    print(f"- Twitter: {invite}")
    
    elif choice == "2":
        setup_with_user_token()
    
    elif choice == "3":
        print("\nOpening manual setup guide...")
        webbrowser.open("https://discord.com")
        print("""
Manual Setup Steps:
1. Click + → Create My Own → For me and my friends
2. Name: "Luminous Nix | Natural Language NixOS"
3. Create these channels:
   - #welcome (make read-only)
   - #general
   - #help
   - #bugs
4. Right-click #general → Invite → Never Expire → Copy
        """)
        
        print("\n✅ Guide opened! Follow the steps above.")

if __name__ == "__main__":
    main()