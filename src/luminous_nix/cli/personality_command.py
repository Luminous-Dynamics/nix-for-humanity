#!/usr/bin/env python3
"""
🎭 CLI commands for Personality & User Experience

Switch between 10 personality styles that change how Luminous Nix responds.
"""

import click
import json
from typing import Optional

from ..core.user_experience import UserExperienceSystem, get_user_experience


@click.group()
def personality():
    """Personality and response style commands"""
    pass


@personality.command(name='list')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def list_personalities(output_json: bool):
    """List available personality styles"""
    ux = get_user_experience()
    modes = ux.get_available_modes()

    if output_json:
        click.echo(json.dumps(modes, indent=2))
    else:
        click.echo(click.style("🎭 Available Personality Styles", fg='cyan', bold=True))
        click.echo()

        icons = {
            'minimal': '📎',
            'friendly': '👋',
            'encouraging': '🌟',
            'playful': '🎉',
            'sacred': '🕉️',
            'professional': '💼',
            'teacher': '📚',
            'companion': '💝',
            'hacker': '💻',
            'zen': '🧘',
        }

        for mode in modes:
            icon = icons.get(mode['name'], '🎭')
            click.echo(f"  {icon} {click.style(mode['name'].upper(), bold=True)}")
            click.echo(f"     {mode['description']}")
            click.echo()


@personality.command(name='set')
@click.argument('style', type=click.Choice([
    'minimal', 'friendly', 'encouraging', 'playful', 'sacred',
    'professional', 'teacher', 'companion', 'hacker', 'zen'
]))
def set_personality(style: str):
    """Set your preferred personality style"""
    ux = get_user_experience()
    response = ux.set_mode(style)

    click.echo(click.style(f"✨ Personality set to: {style.upper()}", fg='green', bold=True))
    click.echo()
    click.echo(f"{response}")


@personality.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def current(output_json: bool):
    """Show current personality and user experience status"""
    ux = get_user_experience()
    status = ux.get_status()

    if output_json:
        click.echo(json.dumps(status, indent=2, default=str))
    else:
        click.echo(click.style("🎭 Current User Experience Status", fg='cyan', bold=True))
        click.echo()

        # Personality
        click.echo(f"  Style: {click.style(status['personality_style'], bold=True)}")
        click.echo()

        # Adaptation status
        click.echo(f"  Adaptation: {status['adaptation_status']}")
        click.echo()

        # Profile metrics
        profile = status['profile']
        click.echo("  Your Profile:")
        click.echo(f"    Technical Level: {profile['technical_level']}")
        click.echo(f"    Risk Tolerance: {profile['risk_tolerance']}")
        click.echo(f"    Speed Preference: {profile['speed_preference']}")
        click.echo()

        # Session info
        click.echo(f"  Session: {status['commands_this_session']} commands, {status['errors_this_session']} errors")


@personality.command()
def suggestions():
    """Get proactive suggestions based on your usage patterns"""
    ux = get_user_experience()
    suggestions = ux.get_proactive_suggestions()

    if not suggestions:
        click.echo(click.style("💡 No suggestions right now - you're doing great!", fg='green'))
        return

    click.echo(click.style("💡 Suggestions for You", fg='cyan', bold=True))
    click.echo()

    for s in suggestions:
        category_icons = {
            'learning': '📚',
            'optimization': '⚡',
            'help': '🆘',
            'maintenance': '🔧',
            'info': 'ℹ️',
        }
        icon = category_icons.get(s.category, '💡')

        click.echo(f"  {icon} {s.message}")
        if s.action_suggestion:
            click.echo(f"     Try: {click.style(s.action_suggestion, fg='yellow')}")
        click.echo()


@personality.command()
def reset():
    """Reset your profile to defaults"""
    ux = get_user_experience()
    ux.behavior.reset()
    ux.personality.set_style("friendly")

    click.echo(click.style("🔄 Profile reset to defaults", fg='green'))
    click.echo("  Your adaptive learning will start fresh!")


# Quick alias command for direct mode switching
@click.command(name='mode')
@click.argument('style', required=False)
@click.option('--list', '-l', 'list_modes', is_flag=True, help='List available modes')
def quick_mode(style: Optional[str], list_modes: bool):
    """Quick personality mode switch

    Examples:
        ask-nix mode hacker
        ask-nix mode zen
        ask-nix mode --list
    """
    ux = get_user_experience()

    if list_modes or not style:
        # Show available modes
        modes = ux.get_available_modes()
        click.echo(click.style("🎭 Available Modes", fg='cyan', bold=True))
        click.echo()
        for mode in modes:
            current = " (current)" if mode['name'] == ux.personality.get_current_style().value else ""
            click.echo(f"  {mode['name']:14} - {mode['description']}{click.style(current, fg='green')}")
        click.echo()
        click.echo("Usage: ask-nix mode <name>")
        return

    # Validate style
    valid_styles = [m['name'] for m in ux.get_available_modes()]
    if style not in valid_styles:
        click.echo(click.style(f"Unknown mode: {style}", fg='red'))
        click.echo(f"Available: {', '.join(valid_styles)}")
        return

    # Switch mode
    response = ux.set_mode(style)
    click.echo(click.style(f"✨ {style.upper()} mode activated", fg='green', bold=True))
    click.echo(f"   {response}")
