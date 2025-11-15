"""
Interactive Onboarding Wizard for Luminous Nix
"""

import json
import subprocess
from pathlib import Path


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
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text

            console = Console()

            # Clear screen for fresh start
            console.clear()

            # Animated welcome
            welcome_text = Text()
            welcome_text.append("🌟 ", style="bold yellow")
            welcome_text.append("Welcome to ", style="bold white")
            welcome_text.append("Luminous Nix", style="bold cyan")
            welcome_text.append("! ", style="bold white")
            welcome_text.append("🌟", style="bold yellow")

            console.print("\n" * 2)
            console.print(
                Panel(
                    "[bold cyan]The Natural Language NixOS Assistant[/bold cyan]\n\n"
                    "[white]I'm here to make NixOS [bold]simple[/bold] and [bold]joyful[/bold] for you![/white]\n\n"
                    "In the next [yellow]2 minutes[/yellow], we'll:\n\n"
                    "  1. ✨ [green]Set up your preferences[/green]\n"
                    "  2. 🔍 [blue]Test that everything works[/blue]\n"
                    "  3. 🎯 [magenta]Complete your first task[/magenta]\n"
                    "  4. 🎉 [yellow]Celebrate your success![/yellow]\n\n"
                    "[dim]No technical knowledge required![/dim]",
                    title=welcome_text,
                    border_style="cyan",
                    padding=1,
                )
            )
            console.print("\n")
            console.input("[bold cyan]Press Enter to begin your journey...[/bold cyan]")
        except ImportError:
            # Fallback to simple text if rich not available
            print(
                """
🌟 Welcome to Luminous Nix! 🌟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I'm here to make NixOS simple and joyful for you.
In the next 2 minutes, we'll:

  1. ✓ Set up your preferences
  2. ✓ Test that everything works
  3. ✓ Complete your first task
  4. ✓ Celebrate your success!

Let's begin! 🚀
            """
            )
            input("Press Enter to continue...")

    def _check_prerequisites(self):
        """Check system requirements."""
        try:
            import time

            from rich.console import Console
            from rich.progress import Progress, SpinnerColumn, TextColumn
            from rich.table import Table

            console = Console()

            console.print("\n[bold blue]🔍 Checking your system...[/bold blue]\n")

            checks = {
                "NixOS": ("Checking for NixOS...", self._check_nixos()),
                "Network": ("Testing network connectivity...", self._check_network()),
                "Permissions": ("Checking sudo access...", self._check_permissions()),
                "AI (Ollama)": (
                    "Checking for AI capabilities...",
                    self._check_ollama(),
                ),
            }

            # Create a nice table for results
            table = Table(show_header=False, box=None)
            table.add_column("Status", style="bold", width=3)
            table.add_column("Check", style="white")
            table.add_column("Result", style="dim")

            for item, (desc, status) in checks.items():
                symbol = "✅" if status else "⚠️"
                result = "Ready" if status else "Optional"
                table.add_row(symbol, item, result)

            console.print(table)

            if not all(check[1] for check in checks.values()):
                console.print(
                    "\n[yellow]ℹ️  Some checks didn't pass, but that's OK![/yellow]"
                )
                console.print("[dim]   We'll work with what you have.[/dim]\n")
        except ImportError:
            # Fallback
            print("\n🔍 Checking your system...")

            checks = {
                "NixOS": self._check_nixos(),
                "Network": self._check_network(),
                "Permissions": self._check_permissions(),
                "AI (Ollama)": self._check_ollama(),
            }

            for item, status in checks.items():
                symbol = "✅" if status else "⚠️"
                print(f"  {symbol} {item}")

            if not all(checks.values()):
                print("\n⚠️ Some checks failed but we can still continue.")
                print("   You may need sudo access for some operations.")

    def _gather_preferences(self):
        """Gather user preferences."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.prompt import IntPrompt, Prompt

            console = Console()

            console.print(
                "\n[bold magenta]🎨 Let's personalize your experience![/bold magenta]\n"
            )

            # Skill level with nice formatting
            console.print(
                Panel(
                    "[bold]How would you describe your NixOS experience?[/bold]\n\n"
                    "[cyan]1.[/cyan] 🆕 Brand new [dim](help me with everything)[/dim]\n"
                    "[cyan]2.[/cyan] 📦 Some basics [dim](I've installed packages)[/dim]\n"
                    "[cyan]3.[/cyan] ⚙️  Comfortable [dim](I edit configuration.nix)[/dim]\n"
                    "[cyan]4.[/cyan] 🚀 Expert [dim](I write Nix expressions)[/dim]",
                    border_style="magenta",
                )
            )

            level = IntPrompt.ask(
                "Your experience level", choices=["1", "2", "3", "4"], default=1
            )
            self.user_data["skill_level"] = level

            # Map to friendly name
            level_names = {1: "Beginner", 2: "Basic", 3: "Intermediate", 4: "Expert"}
            console.print(
                f"[green]✓[/green] Set to: [bold]{level_names[level]}[/bold]\n"
            )

            # Interaction style
            console.print(
                Panel(
                    "[bold]How do you prefer to interact?[/bold]\n\n"
                    '[cyan]1.[/cyan] 💬 Natural language [dim]("install a web browser")[/dim]\n'
                    '[cyan]2.[/cyan] ⚡ Direct commands [dim]("install firefox")[/dim]\n'
                    "[cyan]3.[/cyan] 🔄 Both [dim](depending on context)[/dim]",
                    border_style="magenta",
                )
            )

            style = IntPrompt.ask(
                "Interaction style", choices=["1", "2", "3"], default=1
            )
            self.user_data["interaction_style"] = style

            style_names = {1: "Natural Language", 2: "Direct Commands", 3: "Flexible"}
            console.print(
                f"[green]✓[/green] Set to: [bold]{style_names[style]}[/bold]\n"
            )

            # Safety mode
            console.print(
                Panel(
                    "[bold]Safety preferences:[/bold]\n\n"
                    "[cyan]1.[/cyan] 👀 Always preview [dim](recommended)[/dim]\n"
                    "[cyan]2.[/cyan] ⚡ Execute simple commands directly\n"
                    "[cyan]3.[/cyan] 🤔 Ask me each time",
                    border_style="magenta",
                )
            )

            safety = IntPrompt.ask("Safety mode", choices=["1", "2", "3"], default=1)
            self.user_data["safety_mode"] = safety

            safety_names = {1: "Preview Mode", 2: "Direct Execute", 3: "Interactive"}
            console.print(
                f"[green]✓[/green] Set to: [bold]{safety_names[safety]}[/bold]\n"
            )

            # AI preference if Ollama is available
            if self._check_ollama():
                console.print(
                    Panel(
                        "[bold]AI Enhancement Available! 🤖[/bold]\n\n"
                        "Ollama is installed! Enable AI features for:\n"
                        "• Natural language understanding\n"
                        "• Smart package suggestions\n"
                        "• Error explanations\n\n"
                        "[cyan]1.[/cyan] Yes, enable AI features\n"
                        "[cyan]2.[/cyan] No, keep it simple\n"
                        "[cyan]3.[/cyan] Ask me later",
                        border_style="magenta",
                    )
                )

                ai_choice = IntPrompt.ask(
                    "Enable AI features", choices=["1", "2", "3"], default=1
                )
                self.user_data["ai_enabled"] = ai_choice == 1

                if ai_choice == 1:
                    console.print(
                        "[green]✓[/green] AI features [bold]enabled[/bold]! 🎉\n"
                    )
                elif ai_choice == 2:
                    console.print(
                        "[yellow]✓[/yellow] AI features [bold]disabled[/bold] (can enable later)\n"
                    )
                else:
                    console.print("[blue]✓[/blue] Will ask again later\n")

        except ImportError:
            # Fallback to simple prompts
            print("\n🎨 Let's personalize your experience...")

            # Skill level
            print("\nHow would you describe your NixOS experience?")
            print("  1. Brand new (help me with everything)")
            print("  2. Some basics (I've installed packages)")
            print("  3. Comfortable (I edit configuration.nix)")
            print("  4. Expert (I write Nix expressions)")

            level = input("Choose 1-4 (default: 1): ").strip() or "1"
            self.user_data["skill_level"] = int(level)

            # Preferred interaction style
            print("\nHow do you prefer to work?")
            print('  1. Natural language ("install a web browser")')
            print('  2. Direct commands ("install firefox")')
            print("  3. Both, depending on context")

            style = input("Choose 1-3 (default: 1): ").strip() or "1"
            self.user_data["interaction_style"] = int(style)

            # Safety preferences
            print("\nSafety preferences:")
            print("  1. Always preview before executing (recommended)")
            print("  2. Execute simple commands directly")
            print("  3. Ask me each time")

            safety = input("Choose 1-3 (default: 1): ").strip() or "1"
            self.user_data["safety_mode"] = int(safety)

            # Check for AI availability
            if self._check_ollama():
                print("\n🤖 AI Enhancement Available!")
                print("Ollama is installed! Enable AI features for:")
                print("  • Natural language understanding")
                print("  • Smart package suggestions")
                print("  • Error explanations")
                print("\nEnable AI features?")
                print("  1. Yes, enable AI")
                print("  2. No, keep it simple")
                print("  3. Ask me later")

                ai_choice = input("Choose 1-3 (default: 1): ").strip() or "1"
                self.user_data["ai_enabled"] = int(ai_choice) == 1

                if int(ai_choice) == 1:
                    print("✅ AI features enabled!")
                elif int(ai_choice) == 2:
                    print("✅ AI features disabled (can enable later)")
                else:
                    print("✅ Will ask again later")

    def _first_success(self):
        """Guide through first successful command."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.syntax import Syntax

            console = Console()

            console.print("\n[bold cyan]🎯 Let's try your first command![/bold cyan]")
            console.rule(style="cyan")
            console.print()

            if self.user_data["skill_level"] == 1:
                console.print("[white]I'll help you search for a text editor.[/white]")
                console.print("[yellow]Type or copy this command:[/yellow]\n")

                command = 'luminous-nix "find me a text editor"'
                syntax = Syntax(command, "bash", theme="monokai", padding=1)
                console.print(Panel(syntax, border_style="green"))
            else:
                console.print("[white]Let's search for available editors.[/white]")
                console.print("[yellow]Type this command:[/yellow]\n")

                command = "luminous-nix search editor"
                syntax = Syntax(command, "bash", theme="monokai", padding=1)
                console.print(Panel(syntax, border_style="green"))

            console.print("[dim]Tip: You can also try asking questions like:[/dim]")
            console.print('[dim]  • "how do I install firefox?"[/dim]')
            console.print('[dim]  • "what is my system version?"[/dim]')
            console.print()

            console.input(
                "[bold green]Press Enter after running the command...[/bold green]"
            )

            # Success feedback with animation
            console.print()
            console.print("[bold green]🎉 Excellent![/bold green] You just:")
            console.print("  [green]✓[/green] Used natural language with NixOS")
            console.print("  [green]✓[/green] Searched the package repository")
            console.print("  [green]✓[/green] Got relevant results 2-5 secondsly")
            console.print()
            console.print("[dim]You're already mastering Luminous Nix![/dim]")

        except ImportError:
            # Fallback
            print("\n🎯 Let's try your first command!")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            if self.user_data["skill_level"] == 1:
                print("\nI'll help you search for a text editor.")
                print("Type this command (or copy-paste):\n")
                print('  luminous-nix "find me a text editor"\n')
            else:
                print("\nLet's search for available editors.")
                print("Type this command:\n")
                print("  luminous-nix search editor\n")

            input("Press Enter after running the command...")

            print("\n🎉 Excellent! You just:")
            print("  ✓ Used natural language with NixOS")
            print("  ✓ Searched the package repository")
            print("  ✓ Got relevant results 2-5 secondsly")

    def _save_config(self):
        """Save user preferences."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        config = {"onboarding_complete": True, "version": "0.3.2", **self.user_data}

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

        # Set environment variables
        env_vars = []
        if self.user_data["safety_mode"] == 1:
            env_vars.append("export LUMINOUS_PREVIEW=true")
        if self.user_data["skill_level"] <= 2:
            env_vars.append("export LUMINOUS_VERBOSE=1")
        if self.user_data.get("ai_enabled", False):
            env_vars.append("export LUMINOUS_AI_ENABLED=true")

        if env_vars:
            print("\n💡 Add these to your shell config (~/.bashrc or ~/.zshrc):")
            for var in env_vars:
                print(f"   {var}")

    def _celebrate(self):
        """Celebration and next steps."""
        try:
            import time

            from rich.align import Align
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            console = Console()

            # Celebration animation
            console.print()
            celebration = Panel(
                Align.center(
                    "[bold yellow]🎆 🎉 🎆[/bold yellow]\n\n"
                    "[bold cyan]Setup Complete![/bold cyan]\n\n"
                    "[bold yellow]🎆 🎉 🎆[/bold yellow]",
                    vertical="middle",
                ),
                border_style="yellow",
                padding=1,
            )
            console.print(celebration)
            console.print()

            console.print(
                "[bold green]You're ready to use Luminous Nix![/bold green]\n"
            )

            # Quick reference table
            console.print("[bold cyan]📚 Quick Reference:[/bold cyan]")

            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Command", style="yellow")
            table.add_column("Description", style="white")

            table.add_row("luminous-nix help", "Show all commands")
            table.add_row('luminous-nix "install ..."', "Install packages")
            table.add_row('luminous-nix "search ..."', "Find packages")
            table.add_row('luminous-nix "update"', "Update system")
            table.add_row("luminous-nix setup --reset", "Run setup again")

            console.print(table)
            console.print()

            # Next steps with nice formatting
            console.print("[bold magenta]🚀 Your Next Adventure:[/bold magenta]")
            console.print(
                '  [cyan]1.[/cyan] Try: [yellow]luminous-nix "install your-favorite-app"[/yellow]'
            )
            console.print(
                "  [cyan]2.[/cyan] Explore: [yellow]luminous-nix discover[/yellow]"
            )
            console.print("  [cyan]3.[/cyan] Learn: [yellow]luminous-nix help[/yellow]")
            console.print()

            # Fun facts based on preferences
            if self.user_data["skill_level"] == 1:
                console.print(
                    Panel(
                        "[bold cyan]💡 Did you know?[/bold cyan]\n\n"
                        "You can ask Luminous Nix questions in plain English!\n"
                        'Try: [yellow]"why is my wifi not working?"[/yellow]\n'
                        'Or: [yellow]"how do I take a screenshot?"[/yellow]',
                        border_style="blue",
                    )
                )
            elif self.user_data["skill_level"] >= 3:
                console.print(
                    Panel(
                        "[bold cyan]💡 Pro tip:[/bold cyan]\n\n"
                        "Luminous Nix can generate complete configurations!\n"
                        "Try: [yellow]luminous-nix config generate nginx[/yellow]\n"
                        "Or: [yellow]luminous-nix flake init[/yellow]",
                        border_style="blue",
                    )
                )

            console.print()
            console.print(
                "[bold green]Welcome to the Luminous Nix community![/bold green]"
            )
            console.print(
                "[dim]Remember: There are no silly questions. We're here to help![/dim]"
            )
            console.print()
            console.print("[bold cyan]Happy Nix-ing! 🌊✨[/bold cyan]")

        except ImportError:
            # Fallback
            print(
                """
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
            """
            )

    def _check_nixos(self) -> bool:
        """Check if running on NixOS."""
        return Path("/etc/nixos").exists()

    def _check_network(self) -> bool:
        """Check network connectivity."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "cache.nixos.org"], capture_output=True, timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def _check_permissions(self) -> bool:
        """Check if user can run sudo."""
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"], capture_output=True, timeout=1
            )
            return result.returncode == 0
        except:
            return False

    def _check_ollama(self) -> bool:
        """Check if Ollama is available for AI features."""
        try:
            # Check if ollama command exists
            result = subprocess.run(["which", "ollama"], capture_output=True, timeout=1)
            if result.returncode != 0:
                return False

            # Check if ollama is running
            result = subprocess.run(["ollama", "list"], capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False


def run_wizard():
    """Entry point for the onboarding wizard."""
    wizard = OnboardingWizard()
    wizard.run()


if __name__ == "__main__":
    run_wizard()
