#!/usr/bin/env python3
"""
🎉 First-Run Experience - Making NixOS Accessible from the Start
Handles initial setup, Ollama installation, and model downloading.
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

logger = logging.getLogger(__name__)
console = Console()


class FirstRunExperience:
    """
    Handles the first-run setup experience for new users.
    Makes everything work with zero friction.
    """
    
    def __init__(self):
        """Initialize first-run experience"""
        self.config_dir = Path.home() / ".config" / "luminous-nix"
        self.config_file = self.config_dir / "config.json"
        self.initialized_flag = self.config_dir / ".initialized"
        
        # Recommended models by speed
        self.model_tiers = {
            'nano': {
                'models': ['qwen:0.5b', 'tinyllama'],
                'size': '300-600MB',
                'speed': '< 2s',
                'description': 'Ultra-fast for instant responses'
            },
            'mini': {
                'models': ['gemma:2b', 'phi3:mini'],
                'size': '1-2GB',
                'speed': '< 5s',
                'description': 'Fast with good quality'
            },
            'standard': {
                'models': ['mistral:7b', 'llama3.2:3b'],
                'size': '3-4GB',
                'speed': '< 10s',
                'description': 'Balanced performance'
            }
        }
        
        # Pre-cached common queries for instant response
        self.common_queries = {
            'help': "I can help you with NixOS! Try:\n• 'install <package>' - Install software\n• 'search <name>' - Find packages\n• 'config' - Generate configurations\n• 'fix' - Diagnose issues",
            'hello': "Hello! I'm your NixOS assistant. How can I help you today?",
            'install firefox': "To install Firefox:\n1. Add to configuration.nix: environment.systemPackages = [ pkgs.firefox ];\n2. Run: sudo nixos-rebuild switch",
            'list packages': "Use: nix-env -q (installed) or nix search <pattern> (available)",
        }
    
    def is_first_run(self) -> bool:
        """Check if this is the first run"""
        return not self.initialized_flag.exists()
    
    def check_ollama_installed(self) -> bool:
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def check_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_installed_models(self) -> list:
        """Get list of installed Ollama models"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            return []
        except:
            return []
    
    def install_ollama(self) -> bool:
        """Guide user through Ollama installation"""
        console.print("\n[yellow]⚠️ Ollama is not installed[/yellow]")
        console.print("Ollama is required for AI features.\n")
        
        # Show installation options
        table = Table(title="Installation Options")
        table.add_column("Method", style="cyan")
        table.add_column("Command", style="green")
        
        table.add_row("Official Script", "curl -fsSL https://ollama.ai/install.sh | sh")
        table.add_row("NixOS", "services.ollama.enable = true;")
        table.add_row("Docker", "docker run -d -v ollama:/root/.ollama -p 11434:11434 ollama/ollama")
        
        console.print(table)
        
        response = console.input("\n[cyan]Would you like to install Ollama now? (y/n): [/cyan]")
        
        if response.lower() == 'y':
            console.print("\n[green]Installing Ollama...[/green]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Installing Ollama...", total=None)
                
                try:
                    # Try official installer
                    result = subprocess.run(
                        "curl -fsSL https://ollama.ai/install.sh | sh",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        progress.update(task, description="✅ Ollama installed successfully!")
                        time.sleep(1)
                        return True
                    else:
                        console.print(f"[red]Installation failed: {result.stderr}[/red]")
                        return False
                except Exception as e:
                    console.print(f"[red]Installation error: {e}[/red]")
                    return False
        
        return False
    
    def download_model(self, model_name: str, show_progress: bool = True) -> bool:
        """Download an Ollama model with progress display"""
        if show_progress:
            console.print(f"\n[cyan]📥 Downloading {model_name}...[/cyan]")
            console.print("[dim]This may take a few minutes on first run[/dim]\n")
        
        try:
            # Start download process
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Show progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console,
                transient=False,
            ) as progress:
                
                task = progress.add_task(f"Downloading {model_name}", total=100)
                
                for line in process.stdout:
                    # Parse Ollama output for progress
                    if 'pulling' in line.lower():
                        if '%' in line:
                            try:
                                # Extract percentage
                                percent_str = line.split('%')[0].split()[-1]
                                percent = float(percent_str)
                                progress.update(task, completed=percent)
                            except:
                                pass
                        progress.update(task, description=line.strip()[:50])
                
                process.wait()
                
                if process.returncode == 0:
                    progress.update(task, completed=100, description=f"✅ {model_name} ready!")
                    return True
                else:
                    progress.update(task, description=f"❌ Failed to download {model_name}")
                    return False
                    
        except Exception as e:
            console.print(f"[red]Error downloading model: {e}[/red]")
            return False
    
    def select_model_tier(self) -> str:
        """Let user select model tier based on their needs"""
        console.print("\n[bold cyan]🤖 Select Model Size[/bold cyan]")
        console.print("Choose based on your hardware and speed requirements:\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Tier", width=10)
        table.add_column("Size", width=10)
        table.add_column("Speed", width=8)
        table.add_column("Description", width=30)
        
        table.add_row("1", "Nano", "300-600MB", "< 2s", "Ultra-fast responses")
        table.add_row("2", "Mini", "1-2GB", "< 5s", "Fast with good quality")
        table.add_row("3", "Standard", "3-4GB", "< 10s", "Balanced performance")
        
        console.print(table)
        
        while True:
            choice = console.input("\n[cyan]Select tier (1-3, default=1): [/cyan]").strip() or "1"
            
            if choice == "1":
                return "nano"
            elif choice == "2":
                return "mini"
            elif choice == "3":
                return "standard"
            else:
                console.print("[red]Please select 1, 2, or 3[/red]")
    
    def test_model(self, model_name: str) -> bool:
        """Test if a model works with a simple query"""
        console.print(f"\n[cyan]🧪 Testing {model_name}...[/cyan]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Running test query...", total=None)
                
                # Run simple test
                result = subprocess.run(
                    ['ollama', 'run', model_name, 'Say hello in 5 words or less'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    progress.update(task, description="✅ Model working!")
                    console.print(f"[green]Response: {result.stdout.strip()}[/green]")
                    return True
                else:
                    progress.update(task, description="❌ Model test failed")
                    return False
                    
        except subprocess.TimeoutExpired:
            console.print("[red]⏱️ Model timed out (too slow)[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Error testing model: {e}[/red]")
            return False
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def run_first_time_setup(self) -> bool:
        """
        Run the complete first-time setup experience.
        Returns True if setup completed successfully.
        """
        # Show welcome message
        console.print(Panel.fit(
            "[bold cyan]🌟 Welcome to Luminous Nix![/bold cyan]\n\n"
            "Natural language interface for NixOS\n"
            "Let's get you set up in < 2 minutes",
            border_style="cyan"
        ))
        
        # Step 1: Check Ollama
        console.print("\n[bold]Step 1: Checking AI Backend[/bold]")
        
        if not self.check_ollama_installed():
            if not self.install_ollama():
                console.print("\n[yellow]⚠️ Ollama is required for AI features.[/yellow]")
                console.print("You can install it later and run this setup again.")
                return False
        else:
            console.print("[green]✅ Ollama is installed[/green]")
        
        # Step 2: Check if Ollama is running
        if not self.check_ollama_running():
            console.print("\n[yellow]Starting Ollama service...[/yellow]")
            subprocess.run(['ollama', 'serve'], capture_output=True, timeout=2)
            time.sleep(2)
        
        # Step 3: Check existing models
        console.print("\n[bold]Step 2: Checking AI Models[/bold]")
        existing_models = self.get_installed_models()
        
        if existing_models:
            console.print(f"[green]✅ Found {len(existing_models)} existing models:[/green]")
            for model in existing_models[:3]:  # Show first 3
                console.print(f"   • {model}")
            
            # Test fastest existing model
            if any(m in ['qwen:0.5b', 'tinyllama', 'gemma:2b'] for m in existing_models):
                console.print("\n[green]✅ Fast model already available![/green]")
                fastest = next(m for m in ['qwen:0.5b', 'tinyllama', 'gemma:2b'] 
                             if m in existing_models)
                config = {
                    'default_model': fastest,
                    'installed_models': existing_models,
                    'setup_completed': True
                }
                self.save_config(config)
                self.initialized_flag.touch()
                return True
        
        # Step 4: Download a model
        console.print("\n[bold]Step 3: Download AI Model[/bold]")
        tier = self.select_model_tier()
        models = self.model_tiers[tier]['models']
        
        # Try to download first available model
        downloaded_model = None
        for model in models:
            if self.download_model(model):
                downloaded_model = model
                break
        
        if not downloaded_model:
            console.print("\n[red]❌ Could not download any models[/red]")
            console.print("Please check your internet connection and try again.")
            return False
        
        # Step 5: Test the model
        console.print("\n[bold]Step 4: Testing AI Model[/bold]")
        if not self.test_model(downloaded_model):
            console.print("[yellow]⚠️ Model test failed, but continuing...[/yellow]")
        
        # Step 6: Save configuration
        config = {
            'default_model': downloaded_model,
            'installed_models': [downloaded_model],
            'setup_completed': True,
            'tier': tier
        }
        self.save_config(config)
        
        # Mark as initialized
        self.initialized_flag.touch()
        
        # Show success message
        console.print("\n" + "="*50)
        console.print(Panel.fit(
            "[bold green]✨ Setup Complete![/bold green]\n\n"
            f"Default model: {downloaded_model}\n"
            f"Response time: {self.model_tiers[tier]['speed']}\n\n"
            "You can now use:\n"
            "  • ask-nix 'install firefox'\n"
            "  • ask-nix 'help'\n"
            "  • ask-nix fix (diagnose issues)",
            border_style="green"
        ))
        
        return True
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load saved configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return None
    
    def ensure_ready(self) -> Tuple[bool, str]:
        """
        Ensure system is ready to run.
        Returns (ready, message)
        """
        # Check if first run
        if self.is_first_run():
            console.print("[yellow]🎉 First run detected![/yellow]")
            if self.run_first_time_setup():
                return True, "Setup completed successfully"
            else:
                return False, "Setup incomplete - run 'ask-nix setup' to retry"
        
        # Load config
        config = self.load_config()
        if not config:
            # Config corrupted, re-run setup
            self.initialized_flag.unlink(missing_ok=True)
            return self.ensure_ready()
        
        # Quick checks
        if not self.check_ollama_installed():
            return False, "Ollama not installed - run 'ask-nix setup'"
        
        if not self.check_ollama_running():
            # Try to start it
            subprocess.run(['ollama', 'serve'], capture_output=True, timeout=1)
            time.sleep(1)
            if not self.check_ollama_running():
                return False, "Ollama not running - start with 'ollama serve'"
        
        # Check if we have at least one model
        models = self.get_installed_models()
        if not models:
            return False, "No models installed - run 'ask-nix setup'"
        
        return True, f"Ready with {len(models)} models"


def test_first_run():
    """Test the first-run experience"""
    console.print("[bold]Testing First-Run Experience[/bold]")
    console.print("="*50)
    
    # Create instance
    fre = FirstRunExperience()
    
    # Force first run by removing flag
    fre.initialized_flag.unlink(missing_ok=True)
    
    # Check status
    ready, message = fre.ensure_ready()
    
    console.print(f"\nReady: {ready}")
    console.print(f"Message: {message}")
    
    if ready:
        config = fre.load_config()
        console.print(f"\nConfiguration:")
        console.print(json.dumps(config, indent=2))


if __name__ == "__main__":
    test_first_run()