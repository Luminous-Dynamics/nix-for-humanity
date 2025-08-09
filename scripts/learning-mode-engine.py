#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Learning Mode Engine - Step-by-step guidance with examples for every command

Designed for users like Carlos who need clear examples and explanations
to understand NixOS concepts and commands.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from pathlib import Path

@dataclass
class LearningStep:
    """A single step in a learning sequence"""
    number: int
    action: str
    explanation: str
    command: Optional[str] = None
    example_output: Optional[str] = None
    common_mistakes: Optional[List[str]] = None
    visual_aid: Optional[str] = None

@dataclass
class LearningModule:
    """Complete learning module for a task"""
    title: str
    overview: str
    prerequisites: List[str]
    steps: List[LearningStep]
    practice_exercises: List[str]
    success_indicators: List[str]
    troubleshooting: Dict[str, str]

class LearningModeEngine:
    """
    Provides step-by-step learning experiences with examples
    for every NixOS operation.
    """
    
    def __init__(self):
        self.modules = self._load_learning_modules()
        
    def _load_learning_modules(self) -> Dict[str, LearningModule]:
        """Load all learning modules"""
        return {
            'install_package': self._create_install_module(),
            'update_system': self._create_update_module(),
            'remove_package': self._create_remove_module(),
            'search_package': self._create_search_module(),
            'rollback': self._create_rollback_module(),
            'check_status': self._create_status_module(),
        }
    
    def _create_install_module(self) -> LearningModule:
        """Create learning module for package installation"""
        return LearningModule(
            title="Installing Software on NixOS",
            overview="Learn how to install software packages on NixOS with different methods",
            prerequisites=[
                "Terminal/command line basics",
                "Know the name of software you want to install"
            ],
            steps=[
                LearningStep(
                    number=1,
                    action="Open your terminal",
                    explanation="We'll use the command line to install software. Look for 'Terminal' in your applications.",
                    visual_aid="🖥️ Terminal window"
                ),
                LearningStep(
                    number=2,
                    action="Check if package exists",
                    explanation="First, let's make sure the software is available in NixOS packages.",
                    command="nix search nixpkgs firefox",
                    example_output="""* legacyPackages.x86_64-linux.firefox (119.0)
  Mozilla Firefox - the browser, reloaded""",
                    common_mistakes=["Forgetting 'nixpkgs' before package name"]
                ),
                LearningStep(
                    number=3,
                    action="Install using nix profile (recommended for beginners)",
                    explanation="This method installs software just for your user account - no admin needed!",
                    command="nix profile install nixpkgs#firefox",
                    example_output="""[1/3] Downloading firefox-119.0...
[2/3] Building profile...
[3/3] Installing...
✓ Firefox installed successfully!""",
                    common_mistakes=[
                        "Forgetting the # symbol",
                        "Using old 'nix-env' command"
                    ]
                ),
                LearningStep(
                    number=4,
                    action="Verify installation",
                    explanation="Let's make sure Firefox was installed correctly.",
                    command="firefox --version",
                    example_output="Mozilla Firefox 119.0"
                ),
                LearningStep(
                    number=5,
                    action="Launch the application",
                    explanation="You can now start Firefox from terminal or application menu!",
                    command="firefox",
                    visual_aid="🦊 Firefox window opens"
                )
            ],
            practice_exercises=[
                "Try installing 'htop' (a system monitor) using the same method",
                "Search for and install a text editor like 'vim' or 'nano'",
                "Install 'tree' to visualize directory structures"
            ],
            success_indicators=[
                "✅ Package downloads without errors",
                "✅ Command completes with success message",
                "✅ Software launches when you type its name",
                "✅ Software appears in application menu (for GUI apps)"
            ],
            troubleshooting={
                "command not found": "Make sure you typed the command exactly as shown",
                "permission denied": "You don't need sudo! Use nix profile method",
                "package not found": "Check spelling or search first with 'nix search'",
                "download failed": "Check your internet connection"
            }
        )
    
    def _create_update_module(self) -> LearningModule:
        """Create learning module for system updates"""
        return LearningModule(
            title="Updating Your NixOS System",
            overview="Learn how to keep your NixOS system up-to-date and secure",
            prerequisites=[
                "Administrator (sudo) access",
                "Basic understanding of system vs user packages"
            ],
            steps=[
                LearningStep(
                    number=1,
                    action="Update package channels",
                    explanation="First, we download the latest package definitions.",
                    command="sudo nix-channel --update",
                    example_output="""unpacking channels...
nixos-23.11: updated from 2024-01-15 to 2024-01-28""",
                    common_mistakes=["Forgetting sudo", "Wrong channel name"]
                ),
                LearningStep(
                    number=2,
                    action="Preview what will change",
                    explanation="Before updating, see what packages will be upgraded.",
                    command="sudo nixos-rebuild dry-build",
                    example_output="""these derivations will be built:
  /nix/store/...-firefox-119.0.drv → 120.0
  /nix/store/...-system-path.drv
Updates available: 12 packages"""
                ),
                LearningStep(
                    number=3,
                    action="Perform the system update",
                    explanation="Now apply all updates. This may take several minutes.",
                    command="sudo nixos-rebuild switch",
                    example_output="""building the system configuration...
[######################] 100%
activating the configuration...
setting up /etc...
reloading system services...
✓ System updated successfully!""",
                    visual_aid="📦 Progress bar showing update"
                ),
                LearningStep(
                    number=4,
                    action="Verify the update",
                    explanation="Check that your system is running the new version.",
                    command="nixos-version",
                    example_output="23.11.2024.01.28 (Tapir)"
                )
            ],
            practice_exercises=[
                "Check current system generation with 'sudo nix-env --list-generations -p /nix/var/nix/profiles/system'",
                "Try 'nixos-rebuild test' to test changes without making permanent",
                "Update just your user packages with 'nix profile upgrade'"
            ],
            success_indicators=[
                "✅ Channel update completes",
                "✅ System rebuild finishes without errors",
                "✅ New generation created",
                "✅ Services restart properly"
            ],
            troubleshooting={
                "out of disk space": "Run 'nix-collect-garbage -d' to free space",
                "build fails": "Check error message, might be configuration issue",
                "slow download": "Normal for first update, subsequent ones are faster",
                "permission denied": "Make sure to use sudo for system updates"
            }
        )
    
    def _create_remove_module(self) -> LearningModule:
        """Create learning module for package removal"""
        return LearningModule(
            title="Removing Software from NixOS",
            overview="Learn how to safely remove software you no longer need",
            prerequisites=[
                "Know which software you want to remove",
                "Understanding of user vs system packages"
            ],
            steps=[
                LearningStep(
                    number=1,
                    action="List installed packages",
                    explanation="First, let's see what packages you have installed.",
                    command="nix profile list",
                    example_output="""Index: 0
Package: firefox
Version: 119.0

Index: 1  
Package: htop
Version: 3.2.2"""
                ),
                LearningStep(
                    number=2,
                    action="Remove by package name",
                    explanation="Remove a package using its name from the list.",
                    command="nix profile remove firefox",
                    example_output="✓ Removed firefox",
                    common_mistakes=["Using index instead of name", "Typos in package name"]
                ),
                LearningStep(
                    number=3,
                    action="Clean up unused packages",
                    explanation="Free up disk space by removing old package versions.",
                    command="nix-collect-garbage",
                    example_output="""deleting '/nix/store/abc...-firefox-119.0'
freed 287.3 MiB"""
                )
            ],
            practice_exercises=[
                "List packages before and after removal",
                "Remove a package and then reinstall it",
                "Use 'nix-collect-garbage -d' for more aggressive cleanup"
            ],
            success_indicators=[
                "✅ Package no longer in profile list",
                "✅ Command not found when trying to run",
                "✅ Disk space freed"
            ],
            troubleshooting={
                "package not found": "Check exact name with 'nix profile list'",
                "still runs after removal": "May need to restart shell or logout",
                "no space freed": "Run garbage collection after removal"
            }
        )
    
    def _create_search_module(self) -> LearningModule:
        """Create learning module for searching packages"""
        return LearningModule(
            title="Finding Software in NixOS",
            overview="Learn how to search for available packages",
            prerequisites=["Know roughly what kind of software you need"],
            steps=[
                LearningStep(
                    number=1,
                    action="Search by exact name",
                    explanation="If you know the exact name, search directly.",
                    command="nix search nixpkgs firefox",
                    example_output="""* legacyPackages.x86_64-linux.firefox (119.0)
  Mozilla Firefox - the browser, reloaded"""
                ),
                LearningStep(
                    number=2,
                    action="Search by keyword",
                    explanation="Find related packages using keywords.",
                    command="nix search nixpkgs browser",
                    example_output="""* firefox - Mozilla Firefox
* chromium - Open source Chrome
* qutebrowser - Keyboard-focused browser
... (15 more results)"""
                ),
                LearningStep(
                    number=3,
                    action="Get package details",
                    explanation="See more information about a specific package.",
                    command="nix search nixpkgs firefox --json | jq",
                    example_output="""firefox: {
  version: "119.0",
  description: "Mozilla Firefox - the browser, reloaded",
  homepage: "https://www.mozilla.org/firefox/"
}"""
                )
            ],
            practice_exercises=[
                "Search for text editors with 'editor' keyword",
                "Find all Python-related packages",
                "Search for games with 'game' keyword"
            ],
            success_indicators=[
                "✅ Found packages matching your search",
                "✅ Can see package descriptions",
                "✅ Know exact package name to install"
            ],
            troubleshooting={
                "no results": "Try broader keywords or check spelling",
                "too many results": "Use more specific search terms",
                "command hangs": "First search takes time to download index"
            }
        )
    
    def _create_rollback_module(self) -> LearningModule:
        """Create learning module for system rollback"""
        return LearningModule(
            title="Rolling Back Changes in NixOS",
            overview="Learn how to undo system changes and recover from problems",
            prerequisites=["Understanding of system generations", "Admin access"],
            steps=[
                LearningStep(
                    number=1,
                    action="List system generations",
                    explanation="See all saved system states you can rollback to.",
                    command="sudo nix-env --list-generations -p /nix/var/nix/profiles/system",
                    example_output="""  95   2024-01-25 10:30:15
  96   2024-01-26 14:22:31   
  97   2024-01-28 09:15:42   (current)"""
                ),
                LearningStep(
                    number=2,
                    action="Rollback to previous generation",
                    explanation="Go back to the last working system state.",
                    command="sudo nixos-rebuild switch --rollback",
                    example_output="""switching from generation 97 to 96
activating the configuration...
✓ Rollback successful!""",
                    visual_aid="⏪ System restored to previous state"
                ),
                LearningStep(
                    number=3,
                    action="Boot into specific generation",
                    explanation="Or choose a specific generation number.",
                    command="sudo nixos-rebuild switch --profile /nix/var/nix/profiles/system --generation 95",
                    example_output="✓ Switched to generation 95"
                )
            ],
            practice_exercises=[
                "Make a small change, then rollback",
                "Compare files between generations",
                "Use boot menu to select generation"
            ],
            success_indicators=[
                "✅ Previous generation activated",
                "✅ System works as before",
                "✅ Problem resolved"
            ],
            troubleshooting={
                "generation not found": "Check number with list command",
                "won't boot": "Use boot menu to select generation",
                "changes persist": "Some user data isn't affected by rollback"
            }
        )
    
    def _create_status_module(self) -> LearningModule:
        """Create learning module for checking system status"""
        return LearningModule(
            title="Checking Your NixOS System Status",
            overview="Learn how to inspect your system and installed packages",
            prerequisites=["Basic terminal usage"],
            steps=[
                LearningStep(
                    number=1,
                    action="Check NixOS version",
                    explanation="See which version of NixOS you're running.",
                    command="nixos-version",
                    example_output="23.11.20240128.abcd123 (Tapir)"
                ),
                LearningStep(
                    number=2,
                    action="List user packages",
                    explanation="See packages installed for your user.",
                    command="nix profile list",
                    example_output="""Index  Package         Version
0      firefox         119.0
1      htop           3.2.2
2      vim            9.0.2116"""
                ),
                LearningStep(
                    number=3,
                    action="Check system packages",
                    explanation="See packages installed system-wide.",
                    command="nix-store -q --requisites /run/current-system | cut -d- -f2- | sort | uniq | grep -v '\\.drv$' | head -20",
                    example_output="""bash-5.2
coreutils-9.3
firefox-119.0
git-2.42.0
..."""
                ),
                LearningStep(
                    number=4,
                    action="Check disk usage",
                    explanation="See how much space Nix is using.",
                    command="du -sh /nix/store",
                    example_output="15G     /nix/store"
                )
            ],
            practice_exercises=[
                "Check configuration file location",
                "Find which generation you're on",
                "See recent changes with 'nixos-rebuild dry-build'"
            ],
            success_indicators=[
                "✅ Can see system version",
                "✅ Know what's installed",
                "✅ Understand disk usage"
            ],
            troubleshooting={
                "command not found": "Some commands need full path",
                "permission denied": "Some info needs sudo",
                "output too long": "Use 'less' or 'head' to paginate"
            }
        )
    
    def get_learning_module(self, intent: str) -> Optional[LearningModule]:
        """Get learning module for a specific intent"""
        return self.modules.get(intent)
    
    def format_step_by_step(self, module: LearningModule, 
                           show_all_steps: bool = False,
                           current_step: int = 1) -> str:
        """Format module as step-by-step instructions"""
        output = []
        
        # Header
        output.append(f"📚 **Learning: {module.title}**\n")
        output.append(f"*{module.overview}*\n")
        
        # Prerequisites
        if module.prerequisites:
            output.append("**Before you start:**")
            for prereq in module.prerequisites:
                output.append(f"  • {prereq}")
            output.append("")
        
        # Steps
        output.append("**Steps:**")
        for step in module.steps:
            if not show_all_steps and step.number != current_step:
                # Just show step title for other steps
                if step.number < current_step:
                    output.append(f"  ✅ Step {step.number}: {step.action}")
                else:
                    output.append(f"  ⏭️  Step {step.number}: {step.action}")
            else:
                # Show full current step
                output.append(f"\n**→ Step {step.number}: {step.action}**")
                output.append(f"   {step.explanation}")
                
                if step.command:
                    output.append(f"\n   💻 **Run this command:**")
                    output.append(f"   ```")
                    output.append(f"   {step.command}")
                    output.append(f"   ```")
                
                if step.example_output:
                    output.append(f"\n   📋 **You should see something like:**")
                    output.append(f"   ```")
                    for line in step.example_output.split('\n'):
                        output.append(f"   {line}")
                    output.append(f"   ```")
                
                if step.common_mistakes:
                    output.append(f"\n   ⚠️  **Common mistakes to avoid:**")
                    for mistake in step.common_mistakes:
                        output.append(f"   • {mistake}")
                
                if step.visual_aid:
                    output.append(f"\n   {step.visual_aid}")
        
        # Navigation
        output.append(f"\n**Navigation:**")
        if current_step > 1:
            output.append(f"  ← Say 'previous step' to go back")
        if current_step < len(module.steps):
            output.append(f"  → Say 'next step' to continue")
        output.append(f"  ↺ Say 'start over' to begin again")
        
        # Success indicators (on last step)
        if current_step == len(module.steps):
            output.append(f"\n**How to know you succeeded:**")
            for indicator in module.success_indicators:
                output.append(f"  {indicator}")
        
        return '\n'.join(output)
    
    def format_practice_section(self, module: LearningModule) -> str:
        """Format practice exercises"""
        output = []
        output.append(f"🎯 **Practice Exercises for {module.title}**\n")
        
        output.append("**Try these on your own:**")
        for i, exercise in enumerate(module.practice_exercises, 1):
            output.append(f"  {i}. {exercise}")
        
        output.append(f"\n**Troubleshooting:**")
        output.append("If something goes wrong:")
        for problem, solution in module.troubleshooting.items():
            output.append(f"  • **{problem}**: {solution}")
        
        return '\n'.join(output)
    
    def get_example_for_command(self, command: str) -> str:
        """Get a simple example for any command"""
        examples = {
            'nix profile install': "nix profile install nixpkgs#firefox",
            'nix search': "nix search nixpkgs terminal",
            'nix profile remove': "nix profile remove firefox",
            'nixos-rebuild': "sudo nixos-rebuild switch",
            'nix-collect-garbage': "nix-collect-garbage -d",
            'nix profile list': "nix profile list",
        }
        
        for cmd, example in examples.items():
            if cmd in command:
                return f"Example: `{example}`"
        
        return f"Example: `{command} [package-name]`"


def main():
    """Test the learning mode engine"""
    engine = LearningModeEngine()
    
    # Test install module
    install_module = engine.get_learning_module('install_package')
    
    print("=== Learning Mode Demo ===\n")
    
    # Show step by step
    for step_num in range(1, 6):
        print(f"\n{'='*60}")
        print(engine.format_step_by_step(install_module, current_step=step_num))
        input("\nPress Enter for next step...")
    
    # Show practice
    print(f"\n{'='*60}")
    print(engine.format_practice_section(install_module))


if __name__ == "__main__":
    main()