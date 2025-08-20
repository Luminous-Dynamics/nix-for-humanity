"""
Nix for Humanity CLI Commands

This module provides the main CLI entry point and command registration.
"""

import click
from .config_command import config
from .settings_command import settings
from .home_command import home  
from .error_command import error
from .generation_command import generation
from .flake_command import flake
from .discover_command import discover

@click.group()
@click.version_option(version="0.8.3", prog_name="Nix for Humanity")
@click.pass_context
def cli(ctx):
    """Nix for Humanity - Natural language interface for NixOS
    
    Transform NixOS from command-line complexity into natural conversation.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

# Register all subcommands
cli.add_command(config)
cli.add_command(settings)
cli.add_command(home)
cli.add_command(error)
cli.add_command(generation)
cli.add_command(flake)
cli.add_command(discover)

# Natural language command (default when no subcommand)
@cli.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--personality', '-p', type=click.Choice(['minimal', 'friendly', 'encouraging', 'technical', 'accessible']),
              help='Set response personality')
@click.option('--dry-run', '-d', is_flag=True, help='Show what would be done without executing')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmations')
@click.option('--no-visual', is_flag=True, help='Disable visual elements')
@click.option('--execute', '-e', is_flag=True, help='Execute commands immediately')
@click.option('--profile', help='Use a specific configuration profile')
@click.pass_context
def ask(ctx, query, personality, dry_run, yes, no_visual, execute, profile):
    """Ask Nix for Humanity anything in natural language
    
    Examples:
        ask-nix ask "install firefox"
        ask-nix ask "update my system"
        ask-nix ask "why is my wifi not working?"
    """
    from luminous_nix.interfaces.cli import UnifiedNixAssistant
    from luminous_nix.config import get_config_manager
    
    # Apply profile if specified
    if profile:
        manager = get_config_manager()
        manager.apply_profile(profile)
    
    # Create assistant with config
    config = get_config_manager().config
    assistant = UnifiedNixAssistant()
    
    # Apply settings from config
    if personality:
        assistant.set_personality(personality)
    elif config.ui.default_personality:
        assistant.set_personality(config.ui.default_personality.value)
        
    assistant.dry_run = dry_run
    assistant.skip_confirmation = yes or not config.ui.confirm_actions
    assistant.visual_mode = not no_visual and config.ui.use_colors
    assistant.show_progress = config.ui.progress_indicators
    
    # Process the query
    query_text = ' '.join(query)
    assistant.answer(query_text)
    
    # Handle auto-execution based on config
    if execute or config.ui.confirm_actions is False:
        # Execute detected commands
        intent = assistant.modern_knowledge.extract_intent(query_text)
        # ... (rest of execution logic from original CLI)

def main():
    """Main entry point for the CLI"""
    import sys
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        cli.main(['--help'])
    # If first argument doesn't start with dash and isn't a known command,
    # treat it as a natural language query
    elif len(sys.argv) > 1 and not sys.argv[1].startswith('-') and sys.argv[1] not in cli.commands:
        # Convert "ask-nix install firefox" to "ask-nix ask install firefox"
        sys.argv.insert(1, 'ask')
        cli()
    else:
        cli()

__all__ = ['cli', 'main']