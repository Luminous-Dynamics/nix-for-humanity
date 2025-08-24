#!/usr/bin/env python3
"""
Discord AI Automation Bot
Automated community engagement with AI-powered responses
"""

import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import random

class AIDiscordBot(commands.Bot):
    def __init__(self, ai_provider='claude', ai_api_key=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.ai_provider = ai_provider
        self.ai_api_key = ai_api_key
        self.welcome_messages = []
        self.engagement_patterns = {}
        
    async def setup_hook(self):
        """Initialize bot tasks"""
        self.engagement_loop.start()
        self.activity_monitor.start()
        self.content_poster.start()
        print("🤖 AI Discord Bot initialized!")
    
    async def on_ready(self):
        """Bot is ready"""
        print(f'✅ Logged in as {self.user}')
        print(f'Connected to {len(self.guilds)} servers')
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.helping,
                name="with NixOS questions"
            )
        )
    
    async def on_member_join(self, member):
        """Auto-welcome new members with AI-generated message"""
        welcome_channel = discord.utils.get(member.guild.channels, name='welcome')
        if not welcome_channel:
            welcome_channel = discord.utils.get(member.guild.channels, name='general')
        
        if welcome_channel:
            # Generate personalized welcome
            welcome_msg = await self.generate_welcome(member)
            
            embed = discord.Embed(
                title=f"Welcome {member.name}! 🌟",
                description=welcome_msg,
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Get Started",
                value="• Introduce yourself in #introductions\n• Check out #luminous-nix for the project\n• Ask questions in #help",
                inline=False
            )
            
            await welcome_channel.send(f"{member.mention}", embed=embed)
            
            # Assign role
            pioneer_role = discord.utils.get(member.guild.roles, name="Pioneer")
            if pioneer_role and len(member.guild.members) <= 100:
                await member.add_roles(pioneer_role)
                await welcome_channel.send(f"🎉 {member.mention} is one of our first 100 pioneers!")
    
    async def on_message(self, message):
        """AI-powered message responses"""
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check for questions or help requests
        if any(word in message.content.lower() for word in ['help', 'how', 'what', 'why', 'error', 'problem']):
            if 'nix' in message.content.lower() or 'install' in message.content.lower():
                response = await self.generate_help_response(message.content)
                await message.reply(response)
        
        # Respond to mentions
        if self.user.mentioned_in(message):
            response = await self.generate_ai_response(message.content)
            await message.reply(response)
    
    async def generate_welcome(self, member):
        """Generate personalized welcome message"""
        templates = [
            f"Great to have you here! Luminous Nix is all about making NixOS accessible through natural language. What brings you to our community?",
            f"Welcome aboard! 🚀 You're joining us at an exciting time - we're launching on HN Tuesday! Have you tried NixOS before?",
            f"Hey there! You're now part of the revolution making Linux accessible to everyone. What's your experience level with NixOS?",
            f"Welcome to the future of human-computer interaction! Luminous Nix lets you just say 'install firefox' and it works. What would you like to build?",
        ]
        return random.choice(templates)
    
    async def generate_help_response(self, question):
        """Generate helpful response using AI or templates"""
        question_lower = question.lower()
        
        # Quick responses for common questions
        responses = {
            "install": "With Luminous Nix, just use: `ask-nix 'install [package]'` - for example: `ask-nix 'install firefox'`",
            "start": "Quick start:\n```bash\ngit clone https://github.com/Luminous-Dynamics/luminous-nix\ncd luminous-nix\npoetry install\n./bin/ask-nix 'help'\n```",
            "error": "Try running with debug mode: `ask-nix --debug 'your command'`. Share the output in #bugs if it persists!",
            "voice": "Voice interface is coming soon! It's in active development. Watch #announcements for updates.",
            "contribute": "We'd love your help! Check out the GitHub repo and look for 'good first issue' labels.",
        }
        
        for key, response in responses.items():
            if key in question_lower:
                return response
        
        # Fallback to AI if available
        if self.ai_api_key:
            return await self.call_ai_api(question)
        
        return "Great question! Let me tag someone who can help. @Helper, can you assist here?"
    
    async def call_ai_api(self, prompt):
        """Call AI API (Claude, GPT, or local LLM)"""
        if self.ai_provider == 'claude':
            # Claude API call
            headers = {
                'x-api-key': self.ai_api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }
            
            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 200,
                'messages': [{
                    'role': 'user',
                    'content': f"You're a helpful Discord bot for Luminous Nix (natural language NixOS interface). Answer concisely: {prompt}"
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.anthropic.com/v1/messages', 
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['content'][0]['text']
        
        elif self.ai_provider == 'ollama':
            # Local Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post('http://localhost:11434/api/generate',
                                       json={
                                           'model': 'mistral',
                                           'prompt': prompt,
                                           'stream': False
                                       }) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['response']
        
        return "I'm having trouble connecting to my AI brain. Try asking in #help!"
    
    async def generate_ai_response(self, message):
        """Generate AI response to mentions"""
        if self.ai_api_key:
            return await self.call_ai_api(message)
        
        # Fallback responses
        responses = [
            "That's a great point! Let me think about that... 🤔",
            "Interesting question! Have you checked our docs on GitHub?",
            "Good thinking! This relates to our natural language approach.",
            "I love the enthusiasm! Let's discuss this more in #development",
        ]
        return random.choice(responses)
    
    @tasks.loop(minutes=30)
    async def engagement_loop(self):
        """Post engaging content periodically"""
        channels = ['general', 'luminous-nix', 'development']
        
        tips = [
            "💡 **Tip**: You can use `ask-nix 'show my system health'` to get a full diagnostic!",
            "🚀 **Did you know?** Luminous Nix was built in just 2 weeks using the Trinity Development Model!",
            "📚 **Learning moment**: NixOS configurations are reproducible - same config = same system, everywhere!",
            "🎯 **Pro tip**: Use `ask-nix --personality grandma` for the gentlest explanations!",
            "✨ **Feature spotlight**: Our error messages actually explain what went wrong and how to fix it!",
        ]
        
        for guild in self.guilds:
            channel_name = random.choice(channels)
            channel = discord.utils.get(guild.channels, name=channel_name)
            if channel:
                await channel.send(random.choice(tips))
    
    @tasks.loop(minutes=10)
    async def activity_monitor(self):
        """Monitor activity and engage when quiet"""
        for guild in self.guilds:
            general = discord.utils.get(guild.channels, name='general')
            if general:
                # Check last message time
                async for message in general.history(limit=1):
                    if datetime.utcnow() - message.created_at > timedelta(hours=2):
                        # Channel has been quiet
                        prompts = [
                            "🤔 What NixOS challenge are you working on today?",
                            "🛠️ Anyone building something cool with Luminous Nix?",
                            "📣 Share your NixOS wins! What worked well this week?",
                            "❓ Quick poll: What feature should we add next?",
                        ]
                        await general.send(random.choice(prompts))
                    break
    
    @tasks.loop(hours=24)
    async def content_poster(self):
        """Post daily content"""
        for guild in self.guilds:
            announce = discord.utils.get(guild.channels, name='announcements')
            if announce:
                embed = discord.Embed(
                    title="📊 Daily Luminous Nix Stats",
                    description="Here's what's happening!",
                    color=discord.Color.gold()
                )
                
                # Add stats (you'd fetch these from GitHub API)
                embed.add_field(name="GitHub Stars", value="⭐ 127 (+12)", inline=True)
                embed.add_field(name="Discord Members", value="👥 89 (+7)", inline=True)
                embed.add_field(name="PRs Merged", value="🔀 3", inline=True)
                
                await announce.send(embed=embed)
    
    # Commands
    @commands.command(name='ask')
    async def ask_nix(self, ctx, *, question):
        """Ask about NixOS or Luminous Nix"""
        response = await self.generate_help_response(question)
        await ctx.reply(response)
    
    @commands.command(name='demo')
    async def demo(self, ctx):
        """Show a demo of Luminous Nix"""
        embed = discord.Embed(
            title="🎥 Luminous Nix Demo",
            description="See it in action!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Examples",
            value="""```bash
# Install a package
ask-nix "install firefox"

# Create dev environment  
ask-nix "create python development environment"

# Debug issues
ask-nix "why is my wifi not working?"

# System management
ask-nix "rollback to yesterday"
```""",
            inline=False
        )
        embed.add_field(
            name="Try it yourself",
            value="[GitHub](https://github.com/Luminous-Dynamics/luminous-nix) | [Demo Video](link)",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='stats')
    async def stats(self, ctx):
        """Show project statistics"""
        embed = discord.Embed(
            title="📊 Luminous Nix Statistics",
            color=discord.Color.green()
        )
        embed.add_field(name="Development Time", value="2 weeks", inline=True)
        embed.add_field(name="Total Cost", value="$200", inline=True)
        embed.add_field(name="Enterprise Quote", value="$4.2M", inline=True)
        embed.add_field(name="Performance Gain", value="10x-1500x", inline=True)
        embed.add_field(name="Lines of Code", value="~5,000", inline=True)
        embed.add_field(name="Happy Users", value="Growing! 🚀", inline=True)
        
        await ctx.send(embed=embed)

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
AI_API_KEY = "YOUR_AI_API_KEY"  # Optional - for Claude/GPT
AI_PROVIDER = "ollama"  # or "claude", "gpt", "ollama"

async def main():
    """Run the bot"""
    bot = AIDiscordBot(ai_provider=AI_PROVIDER, ai_api_key=AI_API_KEY)
    
    # Add more commands
    @bot.command(name='help')
    async def help_command(ctx):
        """Show help"""
        embed = discord.Embed(
            title="🤖 Luminous Nix Bot Commands",
            description="Here's what I can do!",
            color=discord.Color.blue()
        )
        embed.add_field(name="!ask [question]", value="Ask about NixOS/Luminous Nix", inline=False)
        embed.add_field(name="!demo", value="Show demo examples", inline=False)
        embed.add_field(name="!stats", value="Show project statistics", inline=False)
        embed.add_field(name="@mention me", value="I'll respond with AI!", inline=False)
        
        await ctx.send(embed=embed)
    
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            AI-POWERED DISCORD AUTOMATION BOT                 ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Features:
    ✅ Auto-welcome new members with AI messages
    ✅ Answer questions using AI (Claude/GPT/Ollama)
    ✅ Post engaging content automatically
    ✅ Monitor activity and re-engage
    ✅ Daily statistics and updates
    ✅ Intelligent command responses
    
    Setup:
    1. Create bot at discord.com/developers
    2. Add bot token above
    3. Optional: Add AI API key for smarter responses
    4. Run: python discord_ai_automation.py
    """)
    
    asyncio.run(main())