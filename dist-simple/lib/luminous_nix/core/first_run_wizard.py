#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
First-Run Wizard for Nix for Humanity

Provides an interactive setup experience for new users, detecting system
compatibility and helping them choose preferences.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import platform
import shutil
from datetime import datetime

from ..config.config_manager import ConfigManager
from ..config.schema import Personality, UIConfig, NLPConfig, PrivacyConfig, LearningConfig
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SystemInfo:
    """System information for compatibility checks"""
    nixos_version: Optional[str] = None
    nix_version: Optional[str] = None
    home_manager_installed: bool = False
    is_nixos: bool = False
    has_nix_daemon: bool = False
    has_internet: bool = True
    available_memory_mb: int = 0
    available_disk_mb: int = 0
    terminal_type: str = ""
    supports_unicode: bool = True
    supports_color: bool = True


class FirstRunWizard:
    """Interactive first-run setup wizard"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        self.system_info = SystemInfo()
        self.wizard_completed = False
        
    def should_run(self) -> bool:
        """Check if wizard should run"""
        # Check if config exists
        config_path = Path.home() / ".config" / "nix-for-humanity" / "config.yaml"
        if config_path.exists():
            return False
            
        # Check for skip flag
        if os.getenv("NIX_HUMANITY_SKIP_WIZARD", "").lower() in ("true", "1", "yes"):
            return False
            
        return True
        
    def run(self) -> bool:
        """Run the interactive wizard"""
        try:
            # Welcome message
            self._show_welcome()
            
            # System detection
            print("\n🔍 Detecting your system...")
            self.system_info = self._detect_system()
            self._show_system_info()
            
            # Check compatibility
            if not self._check_compatibility():
                return False
                
            # Configure preferences
            print("\n⚙️  Let's set up your preferences...")
            
            # Personality selection
            personality = self._choose_personality()
            self.config_manager.set("ui.default_personality", personality)
            
            # Privacy preferences
            privacy_level = self._choose_privacy()
            self._apply_privacy_settings(privacy_level)
            
            # Learning preferences
            enable_learning = self._ask_learning()
            self.config_manager.set("learning.enabled", enable_learning)
            
            # Accessibility check
            accessibility_needs = self._check_accessibility()
            if accessibility_needs:
                self._apply_accessibility_settings(accessibility_needs)
                
            # Quick tour offer
            if self._offer_tour():
                self._show_tour()
                
            # Save configuration
            print("\n💾 Saving your preferences...")
            if self.config_manager.save():
                print("✅ Configuration saved successfully!")
                self.wizard_completed = True
                return True
            else:
                print("❌ Failed to save configuration")
                return False
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled. You can run it again anytime.")
            return False
        except Exception as e:
            logger.error(f"Wizard error: {e}")
            print(f"\n❌ Setup error: {e}")
            return False
            
    def _show_welcome(self) -> None:
        """Show welcome message"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🌟 Welcome to Nix for Humanity! 🌟                    ║
║                                                              ║
║    Your AI partner for making NixOS accessible to all        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

I'm here to help you get started with a personalized experience.
This quick setup will take about 2 minutes.
        """)
        
        input("Press Enter to begin...")
        
    def _detect_system(self) -> SystemInfo:
        """Detect system capabilities"""
        info = SystemInfo()
        
        # Check if NixOS
        info.is_nixos = Path("/etc/nixos/configuration.nix").exists()
        
        # Get Nix version
        try:
            result = subprocess.run(
                ["nix", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info.nix_version = result.stdout.strip()
        except Exception:
            info.nix_version = None
            
        # Get NixOS version if applicable
        if info.is_nixos:
            try:
                result = subprocess.run(
                    ["nixos-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    info.nixos_version = result.stdout.strip()
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
                
        # Check for nix-daemon
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "nix-daemon"],
                capture_output=True,
                text=True,
                timeout=5
            )
            info.has_nix_daemon = result.returncode == 0 and result.stdout.strip() == "active"
        except Exception:
            # Try alternate check
            info.has_nix_daemon = Path("/nix/var/nix/daemon-socket/socket").exists()
            
        # Check home-manager
        info.home_manager_installed = shutil.which("home-manager") is not None
        
        # Check internet connectivity
        try:
            import socket
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            info.has_internet = True
        except Exception:
            info.has_internet = False
            
        # Get available resources
        try:
            import psutil
            info.available_memory_mb = psutil.virtual_memory().available // (1024 * 1024)
            info.available_disk_mb = psutil.disk_usage('/').free // (1024 * 1024)
        except Exception:
            # Fallback methods
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemAvailable:'):
                            info.available_memory_mb = int(line.split()[1]) // 1024
                            break
            except Exception:
                info.available_memory_mb = 1024  # Assume 1GB
                
        # Terminal capabilities
        info.terminal_type = os.getenv('TERM', 'unknown')
        info.supports_unicode = self._check_unicode_support()
        info.supports_color = self._check_color_support()
        
        return info
        
    def _check_unicode_support(self) -> bool:
        """Check if terminal supports Unicode"""
        try:
            print("✓", end='', flush=True)
            print("\r ", end='', flush=True)  # Clear
            return True
        except Exception:
            return False
            
    def _check_color_support(self) -> bool:
        """Check if terminal supports color"""
        # Check common environment variables
        if os.getenv('NO_COLOR'):
            return False
        if os.getenv('TERM') in ('dumb', 'unknown'):
            return False
        if sys.platform == 'win32':
            return os.getenv('ANSICON') is not None
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        
    def _show_system_info(self) -> None:
        """Display detected system info"""
        print("\n📊 System Information:")
        print("─" * 40)
        
        if self.system_info.is_nixos:
            print(f"✅ NixOS Version: {self.system_info.nixos_version or 'Unknown'}")
        else:
            print(f"✅ Nix Version: {self.system_info.nix_version or 'Not found'}")
            
        print(f"{'✅' if self.system_info.has_nix_daemon else '❌'} Nix Daemon: "
              f"{'Running' if self.system_info.has_nix_daemon else 'Not running'}")
              
        print(f"{'✅' if self.system_info.home_manager_installed else '❌'} Home Manager: "
              f"{'Installed' if self.system_info.home_manager_installed else 'Not installed'}")
              
        print(f"{'✅' if self.system_info.has_internet else '❌'} Internet: "
              f"{'Connected' if self.system_info.has_internet else 'Offline'}")
              
        print(f"💾 Available Memory: {self.system_info.available_memory_mb}MB")
        print(f"💿 Available Disk: {self.system_info.available_disk_mb}MB")
        
        if self.system_info.supports_unicode:
            print("✅ Unicode: Supported")
        if self.system_info.supports_color:
            print("✅ Colors: Supported")
            
    def _check_compatibility(self) -> bool:
        """Check system compatibility"""
        issues = []
        
        # Check Nix installation
        if not self.system_info.nix_version:
            issues.append("Nix is not installed or not in PATH")
            
        # Check minimum resources
        if self.system_info.available_memory_mb < 256:
            issues.append("Low memory available (minimum 256MB recommended)")
            
        if self.system_info.available_disk_mb < 100:
            issues.append("Low disk space (minimum 100MB recommended)")
            
        # Handle NixOS version compatibility
        if self.system_info.nixos_version:
            try:
                # Extract version number (e.g., "24.05" from "24.05.20240101.abcdef")
                version_parts = self.system_info.nixos_version.split('.')
                if len(version_parts) >= 2:
                    major = int(version_parts[0])
                    minor = int(version_parts[1])
                    
                    if major < 23 or (major == 23 and minor < 11):
                        issues.append(f"NixOS {major}.{minor} is quite old. Consider upgrading.")
                    elif major > 25:
                        print(f"ℹ️  NixOS {major}.{minor} is newer than tested. Some features may not work.")
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
                
        if issues:
            print("\n⚠️  Compatibility Issues Found:")
            for issue in issues:
                print(f"  • {issue}")
                
            response = input("\nContinue anyway? [y/N]: ").strip().lower()
            return response == 'y'
            
        print("\n✅ Your system is fully compatible!")
        return True
        
    def _choose_personality(self) -> Personality:
        """Let user choose personality"""
        print("\n🎭 Choose your preferred interaction style:")
        print("─" * 40)
        
        personalities = [
            ("1", Personality.MINIMAL, "Minimal", "Just the facts, no fluff"),
            ("2", Personality.FRIENDLY, "Friendly", "Warm and helpful (recommended)"),
            ("3", Personality.ENCOURAGING, "Encouraging", "Supportive for beginners"),
            ("4", Personality.TECHNICAL, "Technical", "Detailed explanations"),
            ("5", Personality.ACCESSIBLE, "Accessible", "Simple language, clear steps")
        ]
        
        for key, _, name, desc in personalities:
            print(f"  {key}. {name} - {desc}")
            
        while True:
            choice = input("\nYour choice [2]: ").strip() or "2"
            
            for key, personality, _, _ in personalities:
                if choice == key:
                    print(f"\n✅ Selected: {personality.value} mode")
                    return personality
                    
            print("❌ Invalid choice. Please enter 1-5.")
            
    def _choose_privacy(self) -> str:
        """Choose privacy level"""
        print("\n🔒 Privacy Preferences:")
        print("─" * 40)
        print("How much data should I collect to improve?")
        print()
        print("  1. Strict - No data collection, everything stays local")
        print("  2. Minimal - Basic usage patterns only (recommended)")
        print("  3. Standard - Usage patterns and anonymous errors")
        print("  4. Full - All interactions for maximum learning")
        
        while True:
            choice = input("\nYour choice [2]: ").strip() or "2"
            
            if choice in ["1", "2", "3", "4"]:
                levels = {
                    "1": "strict",
                    "2": "minimal", 
                    "3": "standard",
                    "4": "full"
                }
                level = levels[choice]
                print(f"\n✅ Privacy level: {level}")
                return level
                
            print("❌ Invalid choice. Please enter 1-4.")
            
    def _apply_privacy_settings(self, level: str) -> None:
        """Apply privacy settings based on level"""
        if level == "strict":
            self.config_manager.set("privacy.data_collection", "none")
            self.config_manager.set("privacy.share_anonymous_stats", False)
            self.config_manager.set("privacy.local_only", True)
            self.config_manager.set("learning.enabled", False)
        elif level == "minimal":
            self.config_manager.set("privacy.data_collection", "minimal")
            self.config_manager.set("privacy.share_anonymous_stats", False)
            self.config_manager.set("privacy.local_only", True)
        elif level == "standard":
            self.config_manager.set("privacy.data_collection", "standard")
            self.config_manager.set("privacy.share_anonymous_stats", True)
            self.config_manager.set("privacy.local_only", True)
        else:  # full
            self.config_manager.set("privacy.data_collection", "full")
            self.config_manager.set("privacy.share_anonymous_stats", True)
            self.config_manager.set("privacy.local_only", False)
            
    def _ask_learning(self) -> bool:
        """Ask about learning preferences"""
        print("\n🧠 Learning System:")
        print("─" * 40)
        print("Should I learn from your usage to provide better help?")
        print("(This data stays on your machine)")
        
        response = input("\nEnable learning? [Y/n]: ").strip().lower()
        enabled = response != 'n'
        
        print(f"\n✅ Learning: {'Enabled' if enabled else 'Disabled'}")
        return enabled
        
    def _check_accessibility(self) -> Optional[List[str]]:
        """Check for accessibility needs"""
        print("\n♿ Accessibility Options:")
        print("─" * 40)
        print("Do you need any accessibility features?")
        
        response = input("\nConfigure accessibility? [y/N]: ").strip().lower()
        if response != 'y':
            return None
            
        needs = []
        
        print("\nSelect all that apply (comma-separated numbers):")
        print("  1. Screen reader support")
        print("  2. High contrast mode")
        print("  3. Large text")
        print("  4. Reduced motion")
        print("  5. Keyboard-only navigation")
        print("  6. Simple language mode")
        
        choices = input("\nYour choices: ").strip()
        if choices:
            for choice in choices.split(','):
                choice = choice.strip()
                if choice == '1':
                    needs.append('screen_reader')
                elif choice == '2':
                    needs.append('high_contrast')
                elif choice == '3':
                    needs.append('large_text')
                elif choice == '4':
                    needs.append('reduce_motion')
                elif choice == '5':
                    needs.append('keyboard_only')
                elif choice == '6':
                    needs.append('simple_language')
                    
        return needs if needs else None
        
    def _apply_accessibility_settings(self, needs: List[str]) -> None:
        """Apply accessibility settings"""
        for need in needs:
            self.config_manager.set(f"accessibility.{need}", True)
            
        # Adjust other settings for accessibility
        if 'screen_reader' in needs:
            self.config_manager.set("ui.use_colors", False)
            self.config_manager.set("ui.response_format", "structured")
            
        if 'simple_language' in needs:
            self.config_manager.set("ui.default_personality", Personality.ACCESSIBLE)
            
        print(f"\n✅ Accessibility features configured: {', '.join(needs)}")
        
    def _offer_tour(self) -> bool:
        """Offer a quick tour"""
        print("\n🎯 Quick Tour:")
        print("─" * 40)
        print("Would you like a quick tour of the main features?")
        
        response = input("\nTake the tour? [Y/n]: ").strip().lower()
        return response != 'n'
        
    def _show_tour(self) -> None:
        """Show quick tour of features"""
        print("\n🚀 Quick Feature Tour:")
        print("═" * 50)
        
        features = [
            ("Natural Language", "Just describe what you need:\n  'install firefox'\n  'my wifi isn't working'\n  'update system'"),
            ("Smart Suggestions", "I'll guide you through complex tasks with helpful suggestions"),
            ("Safety First", "All commands are validated for safety before execution"),
            ("Learning System", "I learn your preferences to provide better help over time"),
            ("Multiple Interfaces", "Use me from terminal, TUI, or voice commands"),
            ("Offline Mode", "Most features work without internet connection")
        ]
        
        for i, (feature, description) in enumerate(features, 1):
            print(f"\n{i}. {feature}")
            print(f"   {description}")
            
            if i < len(features):
                input("\nPress Enter for next feature...")
                
        print("\n✅ Tour complete! You're ready to start using Nix for Humanity.")
        print("\n💡 Tip: Type 'help' anytime to see available commands.")
        
    def get_quick_setup_config(self) -> Dict[str, Any]:
        """Get a minimal config for users who skip the wizard"""
        return {
            "ui": {
                "default_personality": Personality.FRIENDLY.value,
                "confirm_actions": True
            },
            "privacy": {
                "data_collection": "minimal",
                "local_only": True
            },
            "learning": {
                "enabled": True,
                "privacy_mode": "strict"
            }
        }


def run_if_needed(config_manager: Optional[ConfigManager] = None) -> bool:
    """Run wizard if needed, return True if completed or not needed"""
    wizard = FirstRunWizard(config_manager)
    
    if not wizard.should_run():
        return True
        
    print("🌟 First-time setup detected!")
    response = input("Run setup wizard? [Y/n]: ").strip().lower()
    
    if response == 'n':
        print("\nUsing default settings. You can run 'ask-nix --setup' anytime.")
        # Apply minimal config
        if not config_manager:
            config_manager = ConfigManager()
        quick_config = wizard.get_quick_setup_config()
        for key, value in quick_config.items():
            for subkey, subvalue in value.items():
                config_manager.set(f"{key}.{subkey}", subvalue)
        config_manager.save()
        return True
        
    return wizard.run()


if __name__ == "__main__":
    # Test the wizard
    wizard = FirstRunWizard()
    wizard.run()