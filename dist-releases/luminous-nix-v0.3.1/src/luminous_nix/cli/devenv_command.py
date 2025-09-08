#!/usr/bin/env python3
"""
Development environment commands for Luminous Nix CLI
Generates perfect dev shells based on project analysis
"""

import click
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

@click.group(name='devenv')
@click.pass_context
def devenv(ctx):
    """Development environment generation commands"""
    pass

@devenv.command()
@click.argument('project_path', default='.')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def analyze(ctx, project_path, json_output):
    """Analyze project and suggest dev environment"""
    try:
        from ..ai.advanced_features.dev_environment import DevEnvironmentGenerator
        
        generator = DevEnvironmentGenerator()
        spec = generator.analyze_project(project_path)
        
        if json_output:
            result = {
                'project_type': spec.project_type.value,
                'detected_stack': spec.detected_stack,
                'languages': spec.languages,
                'frameworks': spec.frameworks,
                'tools': spec.tools,
                'databases': spec.databases,
                'services': spec.services,
                'confidence': spec.confidence
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(click.style(f"🔍 Project Analysis", fg='cyan', bold=True))
            click.echo(f"Type: {click.style(spec.project_type.value, fg='green')}")
            
            if spec.detected_stack:
                click.echo(f"Stack: {', '.join(spec.detected_stack)}")
            
            if spec.languages:
                click.echo("\n🗣️ Languages:")
                for lang in spec.languages:
                    click.echo(f"  • {lang}")
            
            if spec.frameworks:
                click.echo("\n🏗️ Frameworks:")
                for framework in spec.frameworks:
                    click.echo(f"  • {framework}")
            
            if spec.databases:
                click.echo("\n🗄️ Databases:")
                for db in spec.databases:
                    click.echo(f"  • {db}")
            
            click.echo(f"\nConfidence: {_format_confidence(spec.confidence)}")
            click.echo("\n💡 Run 'devenv generate' to create development environment")
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        ctx.fail(f"Error: {e}")

@devenv.command()
@click.argument('project_path', default='.')
@click.option('--output', '-o', help='Output file for shell.nix')
@click.option('--flake', is_flag=True, help='Generate flake.nix instead')
@click.option('--docker', is_flag=True, help='Also generate docker-compose.yml')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def generate(ctx, project_path, output, flake, docker, json_output):
    """Generate development environment configuration"""
    try:
        from ..ai.advanced_features.dev_environment import DevEnvironmentGenerator
        
        generator = DevEnvironmentGenerator()
        spec = generator.analyze_project(project_path)
        
        if json_output:
            result = {
                'shell_nix': spec.shell_nix,
                'flake_nix': spec.flake_nix if flake else None,
                'docker_compose': spec.docker_compose if docker else None,
                'env_vars': spec.env_vars,
                'aliases': spec.aliases
            }
            click.echo(json.dumps(result, indent=2))
        else:
            # Determine output file
            if output:
                output_path = Path(output)
            else:
                output_path = Path(project_path) / ('flake.nix' if flake else 'shell.nix')
            
            # Write configuration
            config_to_write = spec.flake_nix if flake else spec.shell_nix
            
            if output_path.exists():
                if not click.confirm(f"{output_path} exists. Overwrite?"):
                    ctx.exit(0)
            
            with open(output_path, 'w') as f:
                f.write(config_to_write)
            
            click.echo(click.style(f"✅ Generated {output_path.name}!", fg='green', bold=True))
            
            # Write docker-compose if requested
            if docker and spec.docker_compose:
                docker_path = Path(project_path) / 'docker-compose.yml'
                if docker_path.exists():
                    if click.confirm("docker-compose.yml exists. Overwrite?"):
                        with open(docker_path, 'w') as f:
                            f.write(spec.docker_compose)
                        click.echo(click.style("✅ Generated docker-compose.yml!", fg='green'))
                else:
                    with open(docker_path, 'w') as f:
                        f.write(spec.docker_compose)
                    click.echo(click.style("✅ Generated docker-compose.yml!", fg='green'))
            
            # Show additional info
            if spec.env_vars:
                click.echo("\n🔐 Environment variables to set:")
                for key, value in spec.env_vars.items():
                    click.echo(f"  export {key}={value}")
            
            if spec.aliases:
                click.echo("\n⚡ Useful aliases:")
                for alias, cmd in spec.aliases.items():
                    click.echo(f"  {alias}: {cmd}")
            
            click.echo("\n📝 To enter the environment:")
            if flake:
                click.echo("  nix develop")
            else:
                click.echo("  nix-shell")
                
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        ctx.fail(f"Error: {e}")

@devenv.command()
@click.argument('stack')
@click.option('--output', '-o', help='Output file')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def create(ctx, stack, output, json_output):
    """Create dev environment for specific stack (e.g., 'python-django', 'rust-web')"""
    try:
        from ..ai.advanced_features.dev_environment import DevEnvironmentGenerator
        
        generator = DevEnvironmentGenerator()
        spec = generator.generate_for_stack(stack)
        
        if json_output:
            click.echo(json.dumps({
                'shell_nix': spec.shell_nix,
                'aliases': spec.aliases
            }, indent=2))
        else:
            if output:
                with open(output, 'w') as f:
                    f.write(spec.shell_nix)
                click.echo(click.style(f"✅ Generated {output}!", fg='green', bold=True))
            else:
                click.echo(click.style(f"🔧 shell.nix for {stack}:", fg='cyan', bold=True))
                click.echo("─" * 50)
                click.echo(spec.shell_nix)
                click.echo("─" * 50)
            
            if spec.aliases:
                click.echo("\n⚡ Useful aliases:")
                for alias, cmd in spec.aliases.items():
                    click.echo(f"  {alias}: {cmd}")
            
            click.echo(f"\nConfidence: {_format_confidence(spec.confidence)}")
            
    except Exception as e:
        logger.error(f"Stack creation failed: {e}")
        ctx.fail(f"Error: {e}")

@devenv.command()
@click.pass_context
def list_stacks(ctx):
    """List available technology stacks"""
    stacks = [
        ('python-django', 'Python with Django web framework'),
        ('python-flask', 'Python with Flask micro-framework'),
        ('python-fastapi', 'Python with FastAPI async framework'),
        ('python-ml', 'Python with ML/Data Science tools'),
        ('javascript-react', 'JavaScript with React frontend'),
        ('javascript-node', 'JavaScript with Node.js backend'),
        ('javascript-nextjs', 'JavaScript with Next.js fullstack'),
        ('rust-web', 'Rust with web frameworks (Actix/Rocket)'),
        ('rust-cli', 'Rust for CLI applications'),
        ('go-web', 'Go with web frameworks'),
        ('devops', 'DevOps tools (Docker, Kubernetes, Terraform)'),
    ]
    
    click.echo(click.style("📚 Available technology stacks:", fg='cyan', bold=True))
    for stack, description in stacks:
        click.echo(f"  {click.style(stack, fg='green'):20} - {description}")
    
    click.echo("\n💡 Use 'devenv create <stack>' to generate environment")

def _format_confidence(confidence: float) -> str:
    """Format confidence score with color"""
    if confidence >= 0.8:
        color = 'green'
    elif confidence >= 0.5:
        color = 'yellow'
    else:
        color = 'red'
    return click.style(f"{confidence * 100:.0f}%", fg=color)