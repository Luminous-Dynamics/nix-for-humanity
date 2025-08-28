"""
Interactive Onboarding Wizard for Luminous Nix
"""

import os
import sys
from pathlib import Path
from typing import Optional
import subprocess
import json

class OnboardingWizard:
    """Guide new users through setup and first success."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "luminous-nix"
        self.config_file = self.config_dir / "config.json"
        self.user_data = {}
        
    def run(self):
        """Run the complete onboarding flow."""
        self._welcome()
        self._check_prerequisites()
        self._gather_preferences()
        self._first_success()
        self._save_config()
        self._celebrate()
        
    def _welcome(self):
        """Welcome message and overview."""
        print("""
🌟 Welcome to Luminous Nix! 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I'm here to make NixOS simple and joyful for you.
In the next 2 minutes, we'll:

  1. ✓ Set up your preferences
  2. ✓ Test that everything works  
  3. ✓ Complete your first task
  4. ✓ Celebrate your success!

Let's begin! 🚀
        """)
        input("Press Enter to continue...")
        
    def _check_prerequisites(self):
        """Check system requirements."""
        print("\n🔍 Checking your system...")
        
        checks = {
            "NixOS": self._check_nixos(),
            "Network": self._check_network(),
            "Permissions": self._check_permissions()
        }
        
        for item, status in checks.items():
            symbol = "✅" if status else "⚠️"
            print(f"  {symbol} {item}")
            
        if not all(checks.values()):
            print("\n⚠️ Some checks failed but we can still continue.")
            print("   You may need sudo access for some operations.")
            
    def _gather_preferences(self):
        """Gather user preferences."""
        print("\n🎨 Let's personalize your experience...")
        
        # Skill level
        print("\nHow would you describe your NixOS experience?")
        print("  1. Brand new (help me with everything)")
        print("  2. Some basics (I've installed packages)")
        print("  3. Comfortable (I edit configuration.nix)")
        print("  4. Expert (I write Nix expressions)")
        
        level = input("Choose 1-4 (default: 1): ").strip() or "1"
        self.user_data['skill_level'] = int(level)
        
        # Preferred interaction style
        print("\nHow do you prefer to work?")
        print("  1. Natural language (\"install a web browser\")")
        print("  2. Direct commands (\"install firefox\")")
        print("  3. Both, depending on context")
        
        style = input("Choose 1-3 (default: 1): ").strip() or "1"
        self.user_data['interaction_style'] = int(style)
        
        # Safety preferences
        print("\nSafety preferences:")
        print("  1. Always preview before executing (recommended)")
        print("  2. Execute simple commands directly")
        print("  3. Ask me each time")
        
        safety = input("Choose 1-3 (default: 1): ").strip() or "1"
        self.user_data['safety_mode'] = int(safety)
        
    def _first_success(self):
        """Guide through first successful command."""
        print("\n🎯 Let's try your first command!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if self.user_data['skill_level'] == 1:
            print("\nI'll help you search for a text editor.")
            print("Type this command (or copy-paste):\n")
            print("  luminous-nix \"find me a text editor\"\n")
        else:
            print("\nLet's search for available editors.")
            print("Type this command:\n")
            print("  luminous-nix search editor\n")
            
        input("Press Enter after running the command...")
        
        print("\n🎉 Excellent! You just:")
        print("  ✓ Used natural language with NixOS")
        print("  ✓ Searched the package repository")
        print("  ✓ Got relevant results instantly")
        
    def _save_config(self):
        """Save user preferences."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'onboarding_complete': True,
            'version': '0.3.2',
            **self.user_data
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        # Set environment variables
        env_vars = []
        if self.user_data['safety_mode'] == 1:
            env_vars.append('export LUMINOUS_PREVIEW=true')
        if self.user_data['skill_level'] <= 2:
            env_vars.append('export LUMINOUS_VERBOSE=1')
            
        if env_vars:
            print(f"\n💡 Add these to your shell config (~/.bashrc or ~/.zshrc):")
            for var in env_vars:
                print(f"   {var}")
                
    def _celebrate(self):
        """Celebration and next steps."""
        print("""
🌟 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🌟
   🎉 Setup Complete! 🎉
🌟 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🌟

You're ready to use Luminous Nix!

📚 Quick Reference:
  • luminous-nix help          - Show all commands
  • luminous-nix "install ..." - Install packages
  • luminous-nix "search ..."  - Find packages
  • luminous-nix "update"      - Update system

🚀 Next Steps:
  1. Try installing your favorite program
  2. Explore with 'luminous-nix help'
  3. Join our community for support

Remember: There are no silly questions!
We're here to make NixOS joyful for everyone.

Happy Nix-ing! 🌊✨
        """)
        
    def _check_nixos(self) -> bool:
        """Check if running on NixOS."""
        return Path("/etc/nixos").exists()
        
    def _check_network(self) -> bool:
        """Check network connectivity."""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', 'cache.nixos.org'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
            
    def _check_permissions(self) -> bool:
        """Check if user can run sudo."""
        try:
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except:
            return False


def run_wizard():
    """Entry point for the onboarding wizard."""
    wizard = OnboardingWizard()
    wizard.run()


if __name__ == "__main__":
    run_wizard()