#!/usr/bin/env python3
"""
Discord Server Setup Bot
This creates a fully configured Discord server programmatically
"""

import discord
from discord.ext import commands
import asyncio
import json

# You'll need to create a bot and get a token from:
# https://discord.com/developers/applications

class ServerSetupBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        print("🤖 Bot is starting up...")
    
    async def on_ready(self):
        print(f'✅ Logged in as {self.user}')
        print('Ready to create your Luminous Nix server!')
        
        # Create the server
        await self.create_luminous_server()
    
    async def create_luminous_server(self):
        """Create and configure the entire server"""
        
        print("🌟 Creating Luminous Nix server...")
        
        # Create the server
        guild = await self.create_guild(
            name="Luminous Nix | Natural Language NixOS",
            icon=None  # Add icon bytes if you have a logo
        )
        
        print(f"✅ Server created: {guild.name}")
        
        # Delete default channels
        for channel in guild.channels:
            await channel.delete()
        
        # Create categories and channels
        await self.create_channel_structure(guild)
        
        # Set up roles
        await self.create_roles(guild)
        
        # Post welcome messages
        await self.post_initial_content(guild)
        
        # Create invite
        invite = await self.create_invite(guild)
        
        print("\n" + "="*50)
        print("🎉 SERVER SETUP COMPLETE!")
        print("="*50)
        print(f"\n📧 Invite link: {invite}")
        print("\nShare this link:")
        print(f"- Hacker News: {invite}")
        print(f"- GitHub README: {invite}")
        print(f"- Twitter: {invite}")
        print("\n✨ Your Discord server is ready for launch!")
        
        # Keep bot running for management
        print("\nBot staying online for server management.")
        print("Press Ctrl+C to stop.")
    
    async def create_channel_structure(self, guild):
        """Create all categories and channels"""
        
        # Information category
        info_category = await guild.create_category("📢 INFORMATION")
        welcome = await info_category.create_text_channel("welcome")
        announcements = await info_category.create_text_channel("announcements")
        rules = await info_category.create_text_channel("rules")
        roadmap = await info_category.create_text_channel("roadmap")
        
        # Set welcome as read-only
        await welcome.set_permissions(guild.default_role, send_messages=False)
        await announcements.set_permissions(guild.default_role, send_messages=False)
        await rules.set_permissions(guild.default_role, send_messages=False)
        
        # General category
        general_category = await guild.create_category("💬 GENERAL")
        await general_category.create_text_channel("general")
        await general_category.create_text_channel("introductions")
        await general_category.create_text_channel("showcase")
        await general_category.create_text_channel("off-topic")
        
        # Support category
        support_category = await guild.create_category("🛠️ SUPPORT")
        await support_category.create_text_channel("installation-help")
        await support_category.create_text_channel("questions")
        await support_category.create_text_channel("bug-reports")
        await support_category.create_text_channel("feature-requests")
        
        # Development category
        dev_category = await guild.create_category("💻 DEVELOPMENT")
        await dev_category.create_text_channel("contributors")
        await dev_category.create_text_channel("dev-discussion")
        await dev_category.create_text_channel("pull-requests")
        await dev_category.create_text_channel("sacred-trinity")
        
        # Learning category
        learn_category = await guild.create_category("🎓 LEARNING")
        await learn_category.create_text_channel("tutorials")
        await learn_category.create_text_channel("resources")
        await learn_category.create_text_channel("daily-tips")
        
        print("✅ Channel structure created")
        return welcome, announcements, rules
    
    async def create_roles(self, guild):
        """Create all roles with colors"""
        
        # Create roles with colors
        creator_role = await guild.create_role(
            name="Creator",
            color=discord.Color.gold(),
            hoist=True,
            mentionable=True
        )
        
        core_team_role = await guild.create_role(
            name="Core Team",
            color=discord.Color.purple(),
            hoist=True,
            mentionable=True
        )
        
        contributor_role = await guild.create_role(
            name="Contributor",
            color=discord.Color.blue(),
            hoist=True
        )
        
        pioneer_role = await guild.create_role(
            name="Pioneer",
            color=discord.Color.green(),
            hoist=True
        )
        
        bug_hunter_role = await guild.create_role(
            name="Bug Hunter",
            color=discord.Color.red(),
            hoist=True
        )
        
        print("✅ Roles created")
        return creator_role
    
    async def post_initial_content(self, guild):
        """Post welcome messages and rules"""
        
        # Find channels
        welcome_channel = discord.utils.get(guild.channels, name="welcome")
        rules_channel = discord.utils.get(guild.channels, name="rules")
        announcements_channel = discord.utils.get(guild.channels, name="announcements")
        
        # Welcome message
        welcome_embed = discord.Embed(
            title="🌟 Welcome to Luminous Nix!",
            description="Making NixOS accessible through natural language.",
            color=discord.Color.blue()
        )
        welcome_embed.add_field(
            name="🚀 What is Luminous Nix?",
            value="Instead of `nix-env -iA nixos.firefox`, just say:\n```ask-nix \"install firefox\"```",
            inline=False
        )
        welcome_embed.add_field(
            name="💡 Built Different",
            value="Created by 1 developer + AI in 2 weeks for $200\n(beating $4.2M enterprise quotes!)",
            inline=False
        )
        welcome_embed.add_field(
            name="🔗 Links",
            value="[GitHub](https://github.com/Luminous-Dynamics/luminous-nix) | [Demo](link) | [Docs](link)",
            inline=False
        )
        await welcome_channel.send(embed=welcome_embed)
        
        # Rules
        rules_embed = discord.Embed(
            title="📜 Community Guidelines",
            description="Simple rules for an awesome community",
            color=discord.Color.green()
        )
        rules_embed.add_field(
            name="✅ Do",
            value="• Be kind and helpful\n• Ask any question\n• Share your wins\n• Help newcomers",
            inline=True
        )
        rules_embed.add_field(
            name="❌ Don't",
            value="• No harassment\n• No spam\n• No RTFM responses\n• No gatekeeping",
            inline=True
        )
        await rules_channel.send(embed=rules_embed)
        
        # Launch announcement
        announcement_embed = discord.Embed(
            title="🎉 We're Live on Hacker News!",
            description="Luminous Nix is officially launching!",
            color=discord.Color.gold()
        )
        announcement_embed.add_field(
            name="Show Your Support",
            value="⭐ [Star on GitHub](link)\n🔼 [Upvote on HN](link)\n🐦 [Share on Twitter](link)",
            inline=False
        )
        await announcements_channel.send(embed=announcement_embed)
        
        print("✅ Initial content posted")
    
    async def create_invite(self, guild):
        """Create permanent invite"""
        general = discord.utils.get(guild.channels, name="general")
        invite = await general.create_invite(max_age=0, max_uses=0)
        return invite.url

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # You need to get this from Discord Developer Portal

async def main():
    """Run the setup bot"""
    bot = ServerSetupBot()
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════
    Luminous Nix Discord Server Setup Bot
    ═══════════════════════════════════════════════════════
    
    This bot will automatically create and configure your
    entire Discord server for the Luminous Nix launch!
    
    Prerequisites:
    1. Create a Discord Application at:
       https://discord.com/developers/applications
    
    2. Create a Bot in your application
    
    3. Copy the Bot Token and paste it in this script
    
    4. Invite the bot to a server using OAuth2 URL Generator:
       - Scopes: bot, applications.commands
       - Permissions: Administrator
    
    The bot will:
    ✅ Create server structure
    ✅ Set up all channels
    ✅ Configure roles
    ✅ Post welcome content
    ✅ Generate invite links
    
    Starting bot...
    ═══════════════════════════════════════════════════════
    """)
    
    asyncio.run(main())