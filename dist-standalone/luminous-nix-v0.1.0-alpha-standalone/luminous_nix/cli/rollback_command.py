#!/usr/bin/env python3
"""
Rollback Intelligence CLI Commands
Intelligent system recovery using HRM
"""

import click
import json
from typing import Optional
from luminous_nix.ai.advanced_features.rollback_intelligence import RollbackIntelligence


@click.group()
@click.pass_context
def rollback(ctx):
    """🔄 Intelligent rollback and system recovery
    
    Uses AI to find safe rollback points when your system breaks.
    Analyzes what changed between generations and recommends the safest recovery path.
    """
    ctx.ensure_object(dict)
    ctx.obj['rollback'] = RollbackIntelligence()


@rollback.command()
@click.argument('symptoms', nargs=-1, required=False)
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def analyze(ctx, symptoms, json_output):
    """Find safe rollback point based on symptoms
    
    Examples:
        luminous-nix rollback analyze "system won't boot"
        luminous-nix rollback analyze "nvidia driver broken"
        luminous-nix rollback analyze  # Interactive analysis
    """
    rollback_intel = ctx.obj['rollback']
    
    # Join symptoms if provided
    symptoms_str = ' '.join(symptoms) if symptoms else None
    
    # Get analysis
    analysis = rollback_intel.analyze_system_failure(symptoms_str)
    
    if json_output:
        # JSON output
        output = {
            'current_generation': analysis.current_generation,
            'recommended_generation': analysis.recommended_generation,
            'confidence': analysis.confidence,
            'reason': analysis.reason,
            'risk_level': analysis.risk_level,
            'command': analysis.rollback_command,
            'changes': analysis.changes_detected[:5]
        }
        click.echo(json.dumps(output, indent=2))
    else:
        # Human-friendly output
        click.secho("🔄 Analyzing System for Safe Rollback...", fg='cyan', bold=True)
        click.echo()
        click.echo(f"Current Generation: {analysis.current_generation}")
        click.echo(f"Recommended Rollback: Generation {analysis.recommended_generation}")
        click.echo(f"Confidence: {analysis.confidence:.0%}")
        click.echo(f"Risk Level: {analysis.risk_level}")
        click.echo(f"Reason: {analysis.reason}")
        
        if analysis.changes_detected:
            click.echo()
            click.secho("Breaking Changes Detected:", bold=True)
            for change in analysis.changes_detected[:5]:
                click.echo(f"  • {change}")
        
        click.echo()
        click.secho("Rollback Command:", fg='green', bold=True)
        click.echo(f"  {analysis.rollback_command}")
        
        if analysis.alternative_generations:
            click.echo()
            click.secho("Alternative Options:", bold=True)
            for gen, reason in analysis.alternative_generations[:3]:
                click.echo(f"  • Generation {gen}: {reason}")


@rollback.command()
@click.argument('generation', type=int)
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def check(ctx, generation, json_output):
    """Check if a specific generation is safe to rollback to
    
    Example:
        luminous-nix rollback check 42
    """
    rollback_intel = ctx.obj['rollback']
    
    safety = rollback_intel.analyze_generation_safety(generation)
    
    if json_output:
        click.echo(json.dumps(safety, indent=2))
    else:
        click.secho(f"🔍 Checking Generation {generation} Safety...", fg='cyan', bold=True)
        click.echo()
        
        score = safety['safety_score']
        safe = safety['safe_to_rollback']
        
        click.echo(f"Generation: {generation}")
        click.echo(f"Safety Score: {score:.2f}/1.0")
        
        if safe:
            click.secho(f"Safe to Rollback: ✅ Yes", fg='green')
        else:
            click.secho(f"Safe to Rollback: ❌ No", fg='red')
        
        click.echo(f"Recommendation: {safety.get('recommendation', 'N/A')}")
        
        if safety.get('breaking_changes'):
            click.echo()
            click.secho("Breaking Changes:", bold=True, fg='yellow')
            for change in safety['breaking_changes'][:5]:
                click.echo(f"  • {change}")
        
        if safety.get('safe_changes'):
            click.echo()
            click.secho("Safe Changes:", bold=True, fg='green')
            for change in safety['safe_changes'][:5]:
                click.echo(f"  • {change}")


@rollback.command(name='find-working')
@click.argument('component')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def find_working(ctx, component, json_output):
    """Find last working generation for a component
    
    Examples:
        luminous-nix rollback find-working nvidia
        luminous-nix rollback find-working bluetooth
        luminous-nix rollback find-working audio
    """
    rollback_intel = ctx.obj['rollback']
    
    generation = rollback_intel.find_last_working_generation(component)
    
    if json_output:
        output = {'component': component, 'last_working': generation}
        click.echo(json.dumps(output, indent=2))
    else:
        click.secho(f"🔎 Finding Last Working Generation for '{component}'...", fg='cyan', bold=True)
        click.echo()
        
        if generation is not None:
            click.secho(f"✅ Found: Generation {generation}", fg='green', bold=True)
            click.echo()
            click.echo("Rollback command:")
            click.echo(f"  sudo nixos-rebuild switch --rollback-to {generation}")
        else:
            click.secho(f"⚠️ No previous working generation found", fg='yellow')
            click.echo(f"Component '{component}' may not have changed recently")


@rollback.command()
@click.argument('generation', type=int)
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def summary(ctx, generation, json_output):
    """Get summary of what changed in a generation
    
    Example:
        luminous-nix rollback summary 42
    """
    rollback_intel = ctx.obj['rollback']
    
    summary_text = rollback_intel.get_generation_summary(generation)
    
    if json_output:
        output = {'generation': generation, 'summary': summary_text}
        click.echo(json.dumps(output, indent=2))
    else:
        click.secho(f"Generation {generation} Summary:", bold=True)
        click.echo(f"  {summary_text}")