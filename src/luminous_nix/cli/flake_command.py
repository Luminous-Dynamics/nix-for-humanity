#!/usr/bin/env python3
"""
CLI commands for Nix flake management
"""

import click
from pathlib import Path
from typing import Optional

from luminous_nix.core.flake_manager import FlakeManager

@click.group()
def flake():
    """Manage Nix flakes and development environments"""
    pass

@flake.command()
@click.argument('description', nargs=-1, required=True)
@click.option('--path', '-p', default=".", help="Project path (default: current directory)")
@click.option('--force', '-f', is_flag=True, help="Overwrite existing flake.nix")
def create(description, path, force):
    """Create a new flake from natural language description
    
    Examples:
        ask-nix flake create python dev environment with pytest
        ask-nix flake create rust project with debugging tools
        ask-nix flake create node.js app with typescript and prettier
    """
    desc_text = ' '.join(description)
    manager = FlakeManager()
    
    # Parse the description
    intent = manager.parse_intent(desc_text)
    
    # Handle force flag
    if force:
        flake_path = Path(path) / "flake.nix"
        if flake_path.exists():
            click.echo(f"⚠️  Overwriting existing flake.nix...")
            flake_path.unlink()
    
    # Create the flake
    success, message = manager.create_flake(intent, Path(path))
    
    if success:
        click.echo(f"✅ {message}")
        
        # Show what was created
        click.echo(f"\n📦 Created development environment:")
        if intent['language']:
            click.echo(f"   Language: {intent['language'].capitalize()}")
        if intent['packages']:
            click.echo(f"   Packages: {', '.join(intent['packages'])}")
        if intent['features']:
            click.echo(f"   Features: {', '.join(intent['features'])}")
        
        click.echo(f"\n🚀 To use this environment:")
        click.echo(f"   nix develop        # Enter the dev shell")
        click.echo(f"   nix flake check    # Validate the flake")
        click.echo(f"   nix flake show     # Show available outputs")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)

@flake.command()
@click.option('--path', '-p', default=".", help="Project path")
def validate(path):
    """Validate a flake.nix file
    
    Checks syntax and ensures the flake is well-formed.
    """
    manager = FlakeManager()
    success, message = manager.validate_flake(Path(path))
    
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)

@flake.command()
@click.option('--path', '-p', default=".", help="Project path")
def info(path):
    """Show information about a flake
    
    Displays description, inputs, outputs, and dev shells.
    """
    manager = FlakeManager()
    info_text = manager.show_flake_info(Path(path))
    click.echo(info_text)

@flake.command()
@click.option('--path', '-p', default=".", help="Project path")
@click.option('--backup', '-b', is_flag=True, help="Create backup of original files")
def convert(path, backup):
    """Convert shell.nix or default.nix to flake.nix
    
    Automatically converts traditional Nix files to the new flake format.
    """
    manager = FlakeManager()
    project_path = Path(path)
    
    # Create backups if requested
    if backup:
        for filename in ["shell.nix", "default.nix"]:
            file_path = project_path / filename
            if file_path.exists():
                backup_path = project_path / f"{filename}.backup"
                import shutil
                shutil.copy2(file_path, backup_path)
                click.echo(f"📋 Created backup: {backup_path}")
    
    # Perform conversion
    success, message = manager.convert_to_flake(project_path)
    
    if success:
        click.echo(f"✅ {message}")
        click.echo("\n🎉 Your project now uses Nix flakes!")
        click.echo("   Run 'nix develop' to enter the dev environment")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)

@flake.command()
def templates():
    """Show available flake templates
    
    Lists common development environment templates.
    """
    templates = [
        {
            "name": "Python Web App",
            "command": "ask-nix flake create python web app with django postgresql redis",
            "includes": ["Python 3.11", "Django", "PostgreSQL", "Redis", "Development tools"]
        },
        {
            "name": "Rust CLI Tool", 
            "command": "ask-nix flake create rust cli project with clap serde testing",
            "includes": ["Rust stable", "Cargo", "Clippy", "Rustfmt", "Testing framework"]
        },
        {
            "name": "Node.js API",
            "command": "ask-nix flake create node.js api with express typescript jest",
            "includes": ["Node.js 18", "TypeScript", "Express", "Jest", "ESLint"]
        },
        {
            "name": "C++ Project",
            "command": "ask-nix flake create c++ project with cmake gdb valgrind",
            "includes": ["GCC", "CMake", "GDB debugger", "Valgrind", "Make"]
        },
        {
            "name": "Go Microservice",
            "command": "ask-nix flake create go microservice with gin docker",
            "includes": ["Go 1.21", "Gin framework", "Docker", "Golangci-lint"]
        },
        {
            "name": "Data Science",
            "command": "ask-nix flake create python data science with jupyter pandas numpy",
            "includes": ["Python 3.11", "Jupyter", "Pandas", "NumPy", "Matplotlib"]
        }
    ]
    
    click.echo("📚 Available Flake Templates\n")
    
    for template in templates:
        click.echo(f"🎯 {template['name']}")
        click.echo(f"   Command: {template['command']}")
        click.echo(f"   Includes: {', '.join(template['includes'])}")
        click.echo()
    
    click.echo("💡 Tip: Copy any command above to create your development environment!")

@flake.command()
def guide():
    """Show a guide to using Nix flakes
    
    Displays helpful information for getting started with flakes.
    """
    guide_text = """
🚀 Nix Flakes Quick Guide

## What are Flakes?
Flakes are the modern way to manage Nix projects. They provide:
- Reproducible builds across all machines
- Locked dependencies with flake.lock
- Clean, declarative project structure
- Easy sharing and composition

## Basic Commands

1. Create a flake:
   ask-nix flake create "python project with testing"

2. Enter development shell:
   nix develop

3. Build the project:
   nix build

4. Run without installing:
   nix run

5. Update dependencies:
   nix flake update

## Natural Language Examples

✨ ask-nix flake create "rust web server with actix"
✨ ask-nix flake create "python ml project with tensorflow"
✨ ask-nix flake create "node.js app with react and typescript"
✨ ask-nix flake create "c++ game with SDL2 and cmake"

## Project Detection

Nix for Humanity automatically detects your project type based on files:
- Python: requirements.txt, setup.py, pyproject.toml
- Node.js: package.json, yarn.lock
- Rust: Cargo.toml
- Go: go.mod
- Java: pom.xml, build.gradle
- C++: CMakeLists.txt, Makefile

## Tips

💡 Use 'nix develop' instead of 'nix-shell'
💡 Commit both flake.nix and flake.lock
💡 Share projects with just the repository URL
💡 Combine multiple flakes with inputs

Happy Flaking! 🎉
"""
    click.echo(guide_text)

@flake.command()
@click.argument('language')
def language(language):
    """Show language-specific flake examples
    
    Get detailed examples for a specific programming language.
    """
    examples = {
        "python": """
🐍 Python Flake Examples

## Basic Python Development
ask-nix flake create "python development environment"

## Web Development
ask-nix flake create "python web app with flask sqlite"
ask-nix flake create "django project with postgresql redis celery"

## Data Science
ask-nix flake create "python data science with jupyter numpy pandas matplotlib"
ask-nix flake create "machine learning env with tensorflow pytorch scikit-learn"

## Testing & Quality
ask-nix flake create "python with pytest mypy black flake8"

## Common Additions
- poetry: Python dependency management
- ipython: Enhanced Python shell
- requests: HTTP library
- virtualenv: Virtual environments
""",
        "javascript": """
📦 JavaScript/Node.js Flake Examples

## Basic Node.js
ask-nix flake create "node.js development environment"

## Frontend Development
ask-nix flake create "react app with typescript webpack"
ask-nix flake create "vue.js project with vite tailwind"

## Backend Development  
ask-nix flake create "express api with typescript jest"
ask-nix flake create "nest.js api with postgresql"

## Full Stack
ask-nix flake create "next.js app with prisma postgresql"

## Tools & Quality
ask-nix flake create "node with eslint prettier jest"
""",
        "rust": """
🦀 Rust Flake Examples

## Basic Rust
ask-nix flake create "rust development environment"

## CLI Applications
ask-nix flake create "rust cli tool with clap serde"

## Web Development
ask-nix flake create "rust web server with actix diesel"
ask-nix flake create "rust api with rocket sqlx"

## Systems Programming
ask-nix flake create "rust systems project with tokio"

## Tools & Quality
ask-nix flake create "rust with clippy rustfmt miri"
""",
        "go": """
🐹 Go Flake Examples

## Basic Go
ask-nix flake create "go development environment"

## Web Development
ask-nix flake create "go api with gin gorm"
ask-nix flake create "go microservice with fiber mongodb"

## CLI Tools
ask-nix flake create "go cli with cobra viper"

## Tools & Quality
ask-nix flake create "go with golangci-lint delve"
"""
    }
    
    lang_lower = language.lower()
    if lang_lower in examples:
        click.echo(examples[lang_lower])
    else:
        click.echo(f"❌ No examples available for '{language}'")
        click.echo("\nAvailable languages: python, javascript, rust, go")
        click.echo("\nTry: ask-nix flake language python")

if __name__ == "__main__":
    flake()