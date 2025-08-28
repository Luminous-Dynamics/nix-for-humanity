#!/usr/bin/env python3
"""
from typing import List, Optional
CLI commands for Home Manager integration
"""

import click
import sys
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from luminous_nix.core.home_manager import HomeManager, HomeConfig


@click.group()
def home():
    """Manage personal configurations with Home Manager"""
    pass


@home.command()
@click.argument('description', required=False)
@click.option('--shell', type=click.Choice(['bash', 'zsh', 'fish']), 
              help='Shell preference')
@click.option('--theme', type=click.Choice(['dracula', 'nord', 'solarized-dark', 'gruvbox']), 
              help='Color theme preference')
@click.option('--preview', '-p', is_flag=True, default=True,
              help='Preview changes without applying')
def init(description: Optional[str], shell: Optional[str], theme: Optional[str], preview: bool):
    """Initialize home configuration from natural language
    
    Examples:
        ask-nix home init "set up vim and tmux with dark theme"
        ask-nix home init --shell zsh --theme dracula
        ask-nix home init "configure my development environment"
    """
    manager = HomeManager()
    
    # Build description from options if not provided
    if not description:
        parts = []
        if shell:
            parts.append(f"use {shell} shell")
        if theme:
            parts.append(f"with {theme} theme")
        description = " ".join(parts) if parts else "basic home configuration"
    
    # Initialize configuration
    config = manager.init_home_config(description)
    
    # Override with explicit options
    if shell:
        config.shell_config["shell"] = shell
    if theme and theme in manager.themes:
        manager._add_theme_to_config(config, theme, ["terminal"])
    
    # Apply or preview
    result = manager.apply_config(config, preview=preview)
    
    click.echo(click.style("🏠 Home Configuration Initialized", fg='cyan', bold=True))
    click.echo()
    
    if config.dotfiles:
        click.echo(click.style("Dotfiles:", fg='yellow'))
        for dotfile in config.dotfiles:
            click.echo(f"  • {dotfile.description}")
    
    if config.themes:
        click.echo(click.style("\nThemes:", fg='magenta'))
        for theme in config.themes:
            click.echo(f"  • {theme.name}")
    
    if config.shell_config.get("shell") != "bash":
        click.echo(click.style(f"\nShell: {config.shell_config['shell']}", fg='green'))
    
    click.echo(click.style("\nGenerated home.nix:", fg='blue'))
    click.echo("-" * 50)
    # Show first 20 lines
    lines = result["home_nix"].split("\n")[:20]
    for line in lines:
        click.echo(f"  {line}")
    if len(result["home_nix"].split("\n")) > 20:
        click.echo("  ...")
    
    if preview:
        click.echo(click.style("\n⚠️  Preview Mode - No changes made", fg='yellow'))
        click.echo("Remove --preview flag to apply changes")
    else:
        click.echo(click.style("\n✅ Configuration Applied!", fg='green'))
        for action in result["actions"]:
            click.echo(f"  • {action}")


@home.command()
@click.argument('dotfile_type', type=click.Choice(['vim', 'neovim', 'tmux', 'git', 
                                                   'bash', 'zsh', 'fish', 'alacritty', 'kitty']))
@click.option('--source', '-s', type=click.Path(exists=True),
              help='Source file to use instead of existing')
@click.option('--backup/--no-backup', default=True,
              help='Backup existing config before adding')
def add(dotfile_type: str, source: Optional[str], backup: bool):
    """Add a dotfile to managed configuration
    
    Examples:
        ask-nix home add vim
        ask-nix home add tmux --source ~/my-tmux.conf
        ask-nix home add git --no-backup
    """
    manager = HomeManager()
    
    # Create a minimal config with just this dotfile
    config = HomeConfig(
        username=Path.home().name,
        dotfiles=[],
        themes=[],
        shell_config={},
        packages=[],
        services={}
    )
    
    # Add the requested dotfile
    manager._add_dotfile_to_config(config, dotfile_type)
    
    if not config.dotfiles:
        click.echo(f"❌ No configuration found for {dotfile_type}")
        return
    
    # Handle custom source file
    if source:
        source_path = Path(source)
        for dotfile in config.dotfiles:
            if dotfile.name.startswith(f"{dotfile_type}_"):
                dotfile.source_path = source_path
                break
    
    # Backup if requested
    if backup:
        backups = manager.backup_existing_configs(config)
        if backups:
            click.echo(click.style("📦 Created backups:", fg='yellow'))
            for backup in backups:
                click.echo(f"  • {backup}")
    
    click.echo(click.style(f"✨ Adding {dotfile_type} configuration", fg='cyan', bold=True))
    
    for dotfile in config.dotfiles:
        status = "✓" if dotfile.source_path.exists() else "⚠️  (not found)"
        click.echo(f"  • {dotfile.target_path} {status}")
    
    click.echo(click.style("\n💡 Tip:", fg='green'))
    click.echo(f"  Run 'ask-nix home apply' to update your home.nix")


@home.command()
@click.argument('theme_name', type=click.Choice(['dracula', 'nord', 'solarized-dark', 'gruvbox']))
@click.option('--apps', '-a', multiple=True, 
              type=click.Choice(['terminal', 'vim', 'neovim', 'desktop']),
              help='Applications to theme (can specify multiple)')
@click.option('--preview', '-p', is_flag=True, default=True,
              help='Preview changes without applying')
def theme(theme_name: str, apps: List[str], preview: bool):
    """Apply a color theme to applications
    
    Examples:
        ask-nix home theme dracula
        ask-nix home theme nord --apps terminal vim
        ask-nix home theme solarized-dark --apps terminal --no-preview
    """
    manager = HomeManager()
    
    # Default to terminal if no apps specified
    applications = list(apps) if apps else ["terminal"]
    
    result = manager.apply_theme(theme_name, applications)
    
    if not result["success"]:
        click.echo(click.style(f"❌ {result.get('error', 'Failed to apply theme')}", fg='red'))
        if "available_themes" in result:
            click.echo("Available themes: " + ", ".join(result["available_themes"]))
        return
    
    click.echo(click.style(f"🎨 Applying {theme_name} theme", fg='cyan', bold=True))
    
    for change in result["changes"]:
        click.echo(f"  • {change['application']}: {change['file']}")
    
    if preview:
        click.echo(click.style("\n⚠️  Preview Mode - No changes made", fg='yellow'))
        click.echo("Remove --preview flag to apply changes")
    else:
        click.echo(click.style("\n✅ Theme Applied!", fg='green'))


@home.command()
def list():
    """List managed configurations and available options
    
    Shows:
    - Currently managed dotfiles
    - Available themes
    - Recent backups
    """
    manager = HomeManager()
    managed = manager.list_managed_configs()
    
    click.echo(click.style("📋 Home Manager Status", fg='cyan', bold=True))
    click.echo()
    
    # Dotfiles
    if managed["dotfiles"]:
        click.echo(click.style("Managed Dotfiles:", fg='yellow'))
        for dotfile in managed["dotfiles"]:
            click.echo(f"  • {dotfile}")
    else:
        click.echo(click.style("No dotfiles currently managed", fg='yellow'))
    
    # Themes
    click.echo(click.style("\nAvailable Themes:", fg='magenta'))
    for theme in managed["themes"]:
        click.echo(f"  • {theme}")
    
    # Backups
    if managed["backups"]:
        click.echo(click.style("\nRecent Backups:", fg='blue'))
        for backup in managed["backups"][:5]:  # Show last 5
            click.echo(f"  • {backup}")
    
    click.echo(click.style("\n💡 Tips:", fg='green'))
    click.echo("  • Use 'ask-nix home init' to set up your configuration")
    click.echo("  • Use 'ask-nix home add <tool>' to add specific dotfiles")
    click.echo("  • Use 'ask-nix home theme <name>' to apply themes")


@home.command()
@click.option('--from', 'source', required=True, help='Source machine name')
@click.option('--to', 'target', required=True, help='Target machine name')
@click.option('--configs', '-c', multiple=True,
              type=click.Choice(['vim', 'tmux', 'git', 'shell', 'all']),
              help='Specific configs to sync')
def sync(source: str, target: str, configs: List[str]):
    """Sync configurations between machines
    
    Examples:
        ask-nix home sync --from laptop --to desktop
        ask-nix home sync --from work --to home --configs vim tmux
    """
    manager = HomeManager()
    
    # Default to all if not specified
    if not configs or 'all' in configs:
        configs = ['vim', 'tmux', 'git', 'shell']
    
    result = manager.sync_configs(source, target)
    
    click.echo(click.style("🔄 Configuration Sync", fg='cyan', bold=True))
    click.echo(f"\nSyncing from '{source}' to '{target}'")
    
    click.echo(click.style("\nConfigurations to sync:", fg='yellow'))
    for config in configs:
        click.echo(f"  • {config}")
    
    click.echo(click.style(f"\n{result['message']}", fg='green'))
    
    click.echo(click.style("\n💡 Note:", fg='blue'))
    click.echo("  Full sync functionality requires additional setup")
    click.echo("  See: https://github.com/nix-community/home-manager")


@home.command()
@click.option('--no-backup', is_flag=True, help='Skip creating backup')
def apply(no_backup: bool):
    """Apply the current home configuration
    
    This will:
    1. Generate home.nix from current settings
    2. Backup existing configs (unless --no-backup)
    3. Run home-manager switch
    """
    manager = HomeManager()
    
    # Load current configuration
    # For now, we'll use a simple example
    config = manager.init_home_config("current configuration")
    
    if not no_backup:
        backups = manager.backup_existing_configs(config)
        if backups:
            click.echo(click.style("📦 Created backups:", fg='yellow'))
            for backup in backups[:3]:  # Show first 3
                click.echo(f"  • {backup}")
    
    result = manager.apply_config(config, preview=False)
    
    if result["success"]:
        click.echo(click.style("✅ Home configuration applied!", fg='green', bold=True))
        for action in result["actions"]:
            click.echo(f"  • {action}")
        
        click.echo(click.style("\n🚀 Next steps:", fg='cyan'))
        click.echo("  1. Run: home-manager switch")
        click.echo("  2. Restart your shell to see changes")
    else:
        click.echo(click.style(f"❌ Failed: {result.get('error', 'Unknown error')}", fg='red'))


@home.command()
def guide():
    """Show comprehensive Home Manager guide"""
    guide_text = """
🏠 Home Manager Integration Guide
==================================

Home Manager allows you to manage your personal environment
declaratively using Nix.

What You Can Manage
-------------------
• Dotfiles (vim, tmux, git configs)
• Shell environments (bash, zsh, fish)
• Terminal themes and colors
• Application settings
• Development environments

Getting Started
---------------
1. Initialize your configuration:
   ask-nix home init "set up my dev environment with vim and tmux"

2. Add specific tools:
   ask-nix home add vim
   ask-nix home add git

3. Apply a theme:
   ask-nix home theme dracula

4. Apply changes:
   ask-nix home apply

Natural Language Examples
-------------------------
• "set up my dotfiles for vim and tmux with dracula theme"
• "configure zsh with oh-my-zsh and powerlevel10k"
• "manage my git configuration across machines"
• "set up a rust development environment"
• "apply nord theme to my terminal and vim"

Available Themes
----------------
• dracula - Popular dark theme
• nord - Arctic, north-bluish theme
• solarized-dark - Precision colors for machines and people
• gruvbox - Retro groove color scheme

Tips
----
• Always preview changes first (--preview is default)
• Backups are created automatically
• Use 'ask-nix home list' to see current status
• Sync configs between machines with 'home sync'

Integration with NixOS
----------------------
Home Manager works alongside your system configuration:
• System config: /etc/nixos/configuration.nix
• User config: ~/.config/nixpkgs/home.nix

Both can be managed through natural language!
"""
    click.echo(guide_text)


def register_commands(cli):
    """Register home commands with main CLI"""
    cli.add_command(home)


if __name__ == "__main__":
    home()