#!/usr/bin/env python3
"""
from typing import Optional
CLI commands for NixOS error translation and resolution
"""

import sys
from pathlib import Path

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nix_for_humanity.core.error_translator import ErrorTranslator


@click.group()
def error():
    """Translate and resolve NixOS errors"""
    pass


@error.command()
@click.argument("error_text", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Read error from file")
@click.option(
    "--persona",
    "-p",
    type=click.Choice(["minimal", "friendly", "encouraging", "technical"]),
    default="friendly",
    help="Response style",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed explanation")
def explain(error_text: str | None, file: str | None, persona: str, verbose: bool):
    """Explain a NixOS error in simple terms

    Examples:
        ask-nix error explain "attribute 'nodejs_18' missing"
        ask-nix error explain --file build-error.log
        echo "error text" | ask-nix error explain
    """
    translator = ErrorTranslator()

    # Get error text from various sources
    if file:
        with open(file) as f:
            error_text = f.read()
    elif not error_text and not sys.stdin.isatty():
        # Read from pipe
        error_text = sys.stdin.read()
    elif not error_text:
        click.echo("Please provide an error to explain:")
        click.echo("  - As an argument: ask-nix error explain 'error text'")
        click.echo("  - From a file: ask-nix error explain --file error.log")
        click.echo("  - From pipe: cat error.log | ask-nix error explain")
        return

    # Translate the error
    translated = translator.translate_error(error_text)

    # Display based on persona
    click.echo(translated.format_for_persona(persona))

    if verbose:
        click.echo("\n" + click.style("Detailed Explanation:", fg="cyan", bold=True))
        click.echo(translated.detailed_explanation)

        if translated.learn_more_topics:
            click.echo("\n" + click.style("Learn More:", fg="green"))
            for topic in translated.learn_more_topics:
                click.echo(f"  • ask-nix help {topic}")

        if translated.related_commands:
            click.echo("\n" + click.style("Related Commands:", fg="yellow"))
            for cmd in translated.related_commands:
                click.echo(f"  • ask-nix {cmd}")

        click.echo(
            "\n" + click.style(f"Confidence: {translated.confidence:.0%}", fg="blue")
        )


@error.command()
@click.argument("error_type", required=False)
def common(error_type: str | None):
    """Show common NixOS errors and their solutions

    Examples:
        ask-nix error common                    # List all common errors
        ask-nix error common missing            # Show missing attribute errors
        ask-nix error common collision          # Show package collision errors
    """
    common_errors = {
        "missing": {
            "title": "Missing Attribute/Package Errors",
            "description": "When a package or attribute cannot be found",
            "examples": ["attribute 'nodejs_18' missing", "Package 'vscode' not found"],
            "solutions": [
                "Check exact package name: nix search nixpkgs#packagename",
                "Update channels: sudo nix-channel --update",
                "Use correct attribute path: pkgs.package-name",
            ],
        },
        "collision": {
            "title": "Package Collision Errors",
            "description": "When multiple packages provide the same file",
            "examples": [
                "collision between firefox and firefox-esr",
                "multiple packages with same binary",
            ],
            "solutions": [
                "Choose one package and remove the other",
                "Use priorities: lib.hiPrio package",
                "Use nix-shell for development instead",
            ],
        },
        "syntax": {
            "title": "Syntax Errors",
            "description": "Nix language syntax issues",
            "examples": ["unexpected '}', expecting ';'", "undefined variable 'pkgs'"],
            "solutions": [
                "Add semicolons after assignments",
                "Check bracket matching: {} for sets, [] for lists",
                "Add 'with pkgs;' for package references",
            ],
        },
        "disk": {
            "title": "Disk Space Errors",
            "description": "Insufficient disk space for operations",
            "examples": [
                "No space left on device",
                "cannot create temporary directory",
            ],
            "solutions": [
                "Clean garbage: nix-collect-garbage -d",
                "Delete old generations: ask-nix generation clean",
                "Check disk usage: df -h",
            ],
        },
        "permission": {
            "title": "Permission Errors",
            "description": "Insufficient privileges for operation",
            "examples": ["Permission denied", "cannot open /nix/store"],
            "solutions": [
                "Use sudo for system-wide changes",
                "Use nix profile for user packages",
                "Check file ownership",
            ],
        },
        "network": {
            "title": "Network Errors",
            "description": "Download and connection issues",
            "examples": [
                "SSL certificate problem",
                "unable to download",
                "connection timeout",
            ],
            "solutions": [
                "Check internet connection",
                "Configure proxy if needed",
                "Try different channel mirror",
                "Update ca-certificates",
            ],
        },
    }

    if error_type:
        # Show specific error type
        error_type = error_type.lower()
        if error_type in common_errors:
            info = common_errors[error_type]
            click.echo(click.style(f"📚 {info['title']}", fg="cyan", bold=True))
            click.echo(f"\n{info['description']}\n")

            click.echo(click.style("Common Examples:", fg="yellow"))
            for example in info["examples"]:
                click.echo(f"  • {example}")

            click.echo(click.style("\nSolutions:", fg="green"))
            for solution in info["solutions"]:
                click.echo(f"  ✓ {solution}")
        else:
            click.echo(f"Unknown error type: {error_type}")
            click.echo(f"Available types: {', '.join(common_errors.keys())}")
    else:
        # List all error types
        click.echo(click.style("🔍 Common NixOS Error Types", fg="cyan", bold=True))
        click.echo("\nUse 'ask-nix error common <type>' for details:\n")

        for key, info in common_errors.items():
            click.echo(f"  • {click.style(key, fg='yellow')} - {info['title']}")

        click.echo(
            "\n💡 Tip: Paste any error with 'ask-nix error explain' for instant help!"
        )


@error.command()
@click.option("--last", "-n", default=10, help="Number of recent errors to show")
def history(last: int):
    """Show history of recent errors and their solutions"""
    # This would integrate with the learning system to track errors
    click.echo(click.style("📜 Recent Error History", fg="cyan", bold=True))
    click.echo(
        "\nThis feature will track errors you've encountered and their solutions."
    )
    click.echo("Coming soon as part of the learning system integration!")

    # Placeholder for demonstration
    click.echo("\nExample history:")
    click.echo("  1. [2025-08-08] Missing attribute 'nodejs_18' → Suggested nodejs_20")
    click.echo("  2. [2025-08-07] Disk full → Ran garbage collection")
    click.echo("  3. [2025-08-06] Syntax error in config → Fixed missing semicolon")


@error.command()
def guide():
    """Show comprehensive error resolution guide"""
    guide_text = """
🔍 NixOS Error Resolution Guide
================================

Understanding NixOS Errors
--------------------------
NixOS errors can seem cryptic at first, but they follow patterns.
Each error provides clues about what went wrong and how to fix it.

Error Types Overview
--------------------

1. **Attribute/Package Errors**
   Most common - package not found or renamed
   Fix: Search for correct name, update channels

2. **Syntax Errors**
   Nix language issues - missing semicolons, wrong brackets
   Fix: Check syntax, especially line endings

3. **Collision Errors**
   Two packages conflict - both provide same file
   Fix: Choose one or use priorities

4. **Build Errors**
   Package fails to compile or test
   Fix: Check logs, try different version

5. **Permission Errors**
   Need elevated privileges
   Fix: Use sudo or install as user

6. **Disk Space Errors**
   Not enough room for operation
   Fix: Garbage collect old generations

Error Resolution Process
------------------------
1. **Don't Panic!** - Errors are learning opportunities
2. **Read Carefully** - The error often tells you exactly what's wrong
3. **Use ask-nix** - Paste the error for translation
4. **Try Suggested Fix** - Follow the recommendations
5. **Learn Pattern** - Similar errors have similar solutions

Pro Tips
--------
• Keep 5-10 generations for easy rollback
• Run garbage collection monthly
• Update channels regularly
• Use configuration.nix for reproducibility
• Test changes with 'nixos-rebuild test' first

Getting Help
------------
• ask-nix error explain <error> - Instant translation
• ask-nix error common - Browse common errors
• NixOS manual - Comprehensive documentation
• Community forums - Helpful people!

Remember: Every expert was once confused by these errors too!
"""
    click.echo(guide_text)


@error.command()
@click.argument("log_file", type=click.Path(exists=True))
@click.option("--all", "-a", is_flag=True, help="Analyze all errors, not just first")
def analyze(log_file: str, all: bool):
    """Analyze a build log for errors

    Scans a log file and explains all errors found.

    Example:
        ask-nix error analyze /tmp/nixos-rebuild.log
    """
    translator = ErrorTranslator()

    with open(log_file) as f:
        content = f.read()

    # Find error patterns in the log
    import re

    error_pattern = re.compile(
        r"error:.*?(?=\n(?:error:|warning:|$))", re.DOTALL | re.MULTILINE
    )
    errors_found = error_pattern.findall(content)

    if not errors_found:
        click.echo("✅ No errors found in the log file!")
        return

    click.echo(
        click.style(
            f"🔍 Found {len(errors_found)} error(s) in {log_file}", fg="cyan", bold=True
        )
    )
    click.echo()

    # Analyze each error
    for i, error_text in enumerate(errors_found, 1):
        if not all and i > 1:
            click.echo(
                f"\n... and {len(errors_found) - 1} more errors. Use --all to see all."
            )
            break

        click.echo(click.style(f"Error {i}:", fg="red", bold=True))
        click.echo(click.style("Original:", fg="yellow"))
        # Show first 3 lines of error
        lines = error_text.strip().split("\n")[:3]
        for line in lines:
            click.echo(f"  {line}")
        if len(error_text.strip().split("\n")) > 3:
            click.echo("  ...")

        # Translate
        translated = translator.translate_error(error_text)
        click.echo(click.style("\nTranslation:", fg="green"))
        click.echo(translated.format_for_persona("friendly"))
        click.echo("-" * 60)


def register_commands(cli):
    """Register error commands with main CLI"""
    cli.add_command(error)


if __name__ == "__main__":
    error()
