#!/usr/bin/env python3
"""
Flake migration commands for Luminous Nix CLI
Helps users migrate from traditional configs to modern flakes
"""

import click
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

@click.group(name='flake')
@click.pass_context
def flake(ctx):
    """Flake migration and management commands"""
    pass

@flake.command()
@click.argument('config_path', required=False)
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def analyze(ctx, config_path, json_output):
    """Analyze configuration for flake migration readiness"""
    try:
        from ..ai.advanced_features.flake_migration import FlakeMigrationAssistant
        
        assistant = FlakeMigrationAssistant()
        analysis = assistant.analyze_configuration(config_path)
        
        if json_output:
            result = {
                'config_type': analysis.config_type,
                'complexity': analysis.migration_complexity,
                'effort_hours': analysis.estimated_effort_hours,
                'has_overlays': analysis.has_overlays,
                'has_home_manager': analysis.has_home_manager,
                'has_secrets': analysis.has_secrets,
                'breaking_changes': analysis.breaking_changes,
                'benefits': analysis.benefits,
                'confidence': analysis.confidence
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(click.style(f"🔍 Configuration Analysis", fg='cyan', bold=True))
            click.echo(f"Type: {analysis.config_type}")
            click.echo(f"Complexity: {_format_complexity(analysis.migration_complexity)}")
            click.echo(f"Estimated effort: {analysis.estimated_effort_hours} hours")
            
            if analysis.has_overlays or analysis.has_home_manager or analysis.has_secrets:
                click.echo("\n📦 Detected features:")
                if analysis.has_overlays:
                    click.echo("  • Overlays")
                if analysis.has_home_manager:
                    click.echo("  • Home Manager")
                if analysis.has_secrets:
                    click.echo("  • Secrets management")
            
            if analysis.breaking_changes:
                click.echo(click.style("\n⚠️  Breaking changes:", fg='yellow'))
                for change in analysis.breaking_changes:
                    click.echo(f"  • {change}")
            
            if analysis.benefits:
                click.echo(click.style("\n✅ Migration benefits:", fg='green'))
                for benefit in analysis.benefits[:3]:
                    click.echo(f"  • {benefit}")
            
            click.echo(f"\nConfidence: {_format_confidence(analysis.confidence)}")
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        ctx.fail(f"Error: {e}")

@flake.command()
@click.argument('config_path', required=False)
@click.option('--output', '-o', help='Output directory for flake')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def migrate(ctx, config_path, output, dry_run, json_output):
    """Migrate traditional config to flake"""
    try:
        from ..ai.advanced_features.flake_migration import FlakeMigrationAssistant
        
        assistant = FlakeMigrationAssistant()
        
        if dry_run:
            analysis = assistant.analyze_configuration(config_path)
            if json_output:
                click.echo(json.dumps({'flake_nix': analysis.flake_nix}, indent=2))
            else:
                click.echo(click.style("🔄 Generated flake.nix:", fg='cyan', bold=True))
                click.echo("─" * 50)
                click.echo(analysis.flake_nix)
                click.echo("─" * 50)
                click.echo("\nMigration commands:")
                for cmd in analysis.migration_commands[:5]:
                    if cmd.strip():
                        click.echo(f"  {cmd}")
        else:
            result = assistant.migrate_to_flake(config_path, output)
            
            if json_output:
                click.echo(json.dumps(result, indent=2))
            else:
                if result['success']:
                    click.echo(click.style("✅ Migration successful!", fg='green', bold=True))
                    click.echo(f"Flake created at: {result['flake_path']}")
                    click.echo("\n📝 Next steps:")
                    for step in result['next_steps']:
                        click.echo(f"  • {step}")
                else:
                    click.echo(click.style("❌ Migration failed", fg='red'))
                    click.echo(f"Error: {result.get('error')}")
                    if result.get('suggestions'):
                        click.echo("\n💡 Suggestions:")
                        for suggestion in result['suggestions']:
                            click.echo(f"  • {suggestion}")
                            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        ctx.fail(f"Error: {e}")

@flake.command()
@click.argument('flake_path', default='.')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def validate(ctx, flake_path, json_output):
    """Validate a flake configuration"""
    try:
        from ..ai.advanced_features.flake_migration import FlakeMigrationAssistant
        
        assistant = FlakeMigrationAssistant()
        result = assistant.validate_flake(flake_path)
        
        if json_output:
            click.echo(json.dumps(result, indent=2))
        else:
            if result['valid']:
                click.echo(click.style("✅ Flake is valid!", fg='green', bold=True))
            else:
                click.echo(click.style("❌ Flake validation failed", fg='red'))
                if 'error' in result:
                    click.echo(f"Error: {result['error']}")
            
            click.echo(f"\n📊 Validation results:")
            click.echo(f"  Syntax: {'✅' if result.get('syntax') else '❌'}")
            click.echo(f"  Inputs: {'✅' if result.get('inputs') else '❌'}")
            click.echo(f"  Outputs: {'✅' if result.get('outputs') else '❌'}")
            
            if result.get('evaluation'):
                eval_res = result['evaluation']
                if eval_res.get('success'):
                    click.echo(f"  Evaluation: ✅ ({eval_res.get('time_ms', 0)}ms)")
                else:
                    click.echo(f"  Evaluation: ❌")
            
            if result.get('warnings'):
                click.echo(click.style("\n⚠️  Warnings:", fg='yellow'))
                for warning in result['warnings']:
                    click.echo(f"  • {warning}")
            
            if result.get('suggestions'):
                click.echo(click.style("\n💡 Suggestions:", fg='cyan'))
                for suggestion in result['suggestions']:
                    click.echo(f"  • {suggestion}")
                    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        ctx.fail(f"Error: {e}")

@flake.command()
@click.argument('flake_path', default='.')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def improve(ctx, flake_path, json_output):
    """Suggest improvements for existing flake"""
    try:
        from ..ai.advanced_features.flake_migration import FlakeMigrationAssistant
        
        assistant = FlakeMigrationAssistant()
        suggestions = assistant.suggest_improvements(flake_path)
        
        if json_output:
            click.echo(json.dumps({'suggestions': suggestions}, indent=2))
        else:
            if suggestions:
                click.echo(click.style("💡 Improvement suggestions:", fg='cyan', bold=True))
                for i, suggestion in enumerate(suggestions, 1):
                    click.echo(f"{i}. {suggestion}")
            else:
                click.echo(click.style("✨ Your flake looks great!", fg='green'))
                click.echo("No improvements suggested.")
                
    except Exception as e:
        logger.error(f"Improvement analysis failed: {e}")
        ctx.fail(f"Error: {e}")

def _format_complexity(complexity: str) -> str:
    """Format complexity with color"""
    colors = {
        'trivial': 'green',
        'moderate': 'yellow',
        'complex': 'red',
        'unknown': 'white'
    }
    return click.style(complexity.capitalize(), fg=colors.get(complexity, 'white'))

def _format_confidence(confidence: float) -> str:
    """Format confidence score with color"""
    if confidence >= 0.8:
        color = 'green'
    elif confidence >= 0.5:
        color = 'yellow'
    else:
        color = 'red'
    return click.style(f"{confidence * 100:.0f}%", fg=color)