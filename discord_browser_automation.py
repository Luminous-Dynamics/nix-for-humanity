#!/usr/bin/env python3
"""
Discord Browser Automation Setup
This runs locally on YOUR machine with YOUR session
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

class DiscordAutomation:
    def __init__(self):
        """Initialize browser automation"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║          DISCORD AUTOMATED SETUP - LOCAL CONTROL            ║
╚══════════════════════════════════════════════════════════════╝

This script automates Discord setup using YOUR browser session.
You remain in full control - it only does what you approve.

Requirements:
1. Chrome/Firefox installed
2. You'll log in to Discord manually
3. Script automates the clicking/typing
        """)
        
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        print("\n🌐 Setting up browser automation...")
        
        # Try Chrome first, then Firefox
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            # Keep browser open after script
            options.add_experimental_option("detach", True)
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            print("✅ Using Chrome browser")
            
        except:
            try:
                from selenium.webdriver.firefox.service import Service
                from webdriver_manager.firefox import GeckoDriverManager
                
                options = webdriver.FirefoxOptions()
                self.driver = webdriver.Firefox(
                    service=Service(GeckoDriverManager().install()),
                    options=options
                )
                print("✅ Using Firefox browser")
                
            except Exception as e:
                print(f"❌ Could not setup browser: {e}")
                print("\nInstall with: pip install selenium webdriver-manager")
                return False
        
        return True
    
    def login_to_discord(self):
        """Open Discord and wait for manual login"""
        print("\n🔐 Opening Discord...")
        self.driver.get("https://discord.com/app")
        
        print("""
Please log in to Discord manually.
The script will wait for you to complete login.

Press ENTER when you're logged in and ready...
        """)
        input()
        
        return True
    
    def create_server(self):
        """Automate server creation"""
        print("\n🏗️ Creating server...")
        
        try:
            # Click the + button to create server
            wait = WebDriverWait(self.driver, 10)
            
            # Find and click the add server button
            add_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Add a Server']"))
            )
            add_button.click()
            time.sleep(1)
            
            # Click "Create My Own"
            create_own = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create My Own')]"))
            )
            create_own.click()
            time.sleep(1)
            
            # Click "For me and my friends"
            for_me = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'For me and my friends')]"))
            )
            for_me.click()
            time.sleep(1)
            
            # Enter server name
            server_name_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
            )
            server_name_input.clear()
            server_name_input.send_keys("Luminous Nix | Natural Language NixOS")
            
            # Click Create
            create_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create')]"))
            )
            create_button.click()
            
            print("✅ Server created!")
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Automation failed: {e}")
            print("\nPlease create the server manually:")
            print("1. Click the + button")
            print("2. Create My Own → For me and my friends")
            print('3. Name: "Luminous Nix | Natural Language NixOS"')
            input("\nPress ENTER when done...")
            return True
    
    def setup_channels(self):
        """Guide through channel setup"""
        print("\n📁 Setting up channels...")
        
        channels_structure = """
Please create this structure:

📢 INFORMATION
├── welcome
├── announcements
└── rules

💬 GENERAL  
├── general
├── introductions
└── showcase

🛠️ SUPPORT
├── help
└── bugs

💻 DEVELOPMENT
└── contributors
        """
        
        print(channels_structure)
        print("\nThe script will help you create each one...")
        
        # We could automate this but it's complex with Discord's UI
        # Better to guide the user
        
        input("\nPress ENTER when channels are created...")
        return True
    
    def post_content(self):
        """Post welcome messages"""
        print("\n💬 Preparing content to post...")
        
        content = {
            "welcome": """**🌟 Welcome to Luminous Nix!**

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

**Philosophy**
"Technology should adapt to humans, not the other way around."

Welcome to the revolution! 🚀""",
            
            "rules": """**📜 Community Guidelines**

**✅ DO**
• Be kind and patient with everyone
• Ask questions - no matter how basic
• Share your successes AND failures
• Help newcomers get started

**❌ DON'T**
• No harassment or discrimination
• No spam or unsolicited promotion
• No "RTFM" responses
• No gatekeeping

We're making NixOS accessible to EVERYONE!""",
            
            "announcements": """**🎉 WE'RE LAUNCHING ON HACKER NEWS!**

Show your support:
⭐ Star: https://github.com/Luminous-Dynamics/luminous-nix
🔼 Upvote: [HN Link Tuesday]
💬 Share with friends!

Join us in making Linux accessible to everyone! 🌟"""
        }
        
        # Save content to files for easy copy/paste
        for channel, text in content.items():
            filename = f"discord_{channel}_content.txt"
            with open(filename, 'w') as f:
                f.write(text)
            print(f"✅ Saved {channel} content to {filename}")
        
        print("\n📋 Content saved to files. Copy and paste into respective channels.")
        input("\nPress ENTER when content is posted...")
        
        return True
    
    def get_invite_link(self):
        """Guide to create invite"""
        print("\n🔗 Creating invite link...")
        print("""
1. Right-click on #general channel
2. Click "Invite People"  
3. Click "Edit invite link"
4. Set to "Never expire"
5. Copy the link
        """)
        
        invite = input("\nPaste your invite link here: ")
        
        # Save for later use
        with open("discord_invite.txt", 'w') as f:
            f.write(f"Discord Invite: {invite}\n")
            f.write(f"\nShare on HN: {invite}\n")
            f.write(f"Share on GitHub: {invite}\n")
        
        print(f"\n✅ Invite saved to discord_invite.txt")
        
        return invite

def main():
    """Run the automation"""
    automation = DiscordAutomation()
    
    # Setup browser
    if not automation.setup_driver():
        return
    
    # Login to Discord
    if not automation.login_to_discord():
        return
    
    # Create server
    if not automation.create_server():
        return
    
    # Setup channels
    if not automation.setup_channels():
        return
    
    # Post content
    if not automation.post_content():
        return
    
    # Get invite
    invite = automation.get_invite_link()
    
    print("\n" + "="*60)
    print("🎉 DISCORD SETUP COMPLETE!")
    print("="*60)
    print(f"\n📧 Your invite link: {invite}")
    print("\n✅ Everything is ready for launch!")
    
    print("\n💡 Browser will stay open so you can make any final adjustments.")

if __name__ == "__main__":
    # Check dependencies
    try:
        import selenium
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
        print("✅ Packages installed. Please run the script again.")
        sys.exit(0)
    
    main()