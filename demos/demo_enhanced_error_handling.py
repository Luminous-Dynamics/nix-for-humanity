#!/usr/bin/env python3
"""
🚨 Demo: Enhanced Error Handling in TUI

Demonstrates the improved error handling features:
- User-friendly error messages
- Automatic recovery suggestions
- Error history tracking
- Guided error resolution
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nix_humanity.ui.error_handler import (
    TUIErrorHandler, ErrorSeverity, ErrorCategory, 
    ErrorContext, ErrorSolution, EnhancedError
)
from nix_humanity.ui.error_recovery import ErrorRecovery
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_section(title: str):
    """Print a section header"""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]{title.center(60)}[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")


async def demo_error_handling():
    """Demonstrate error handling features"""
    error_handler = TUIErrorHandler()
    error_recovery = ErrorRecovery()
    
    # Demo 1: Network Error
    print_section("Demo 1: Network Connection Error")
    
    try:
        raise ConnectionRefusedError("Unable to connect to nix-daemon")
    except Exception as e:
        enhanced_error = error_handler.handle_error(
            error=e,
            component="demo",
            operation="package_install",
            user_input="install firefox"
        )
        
        # Display the error
        console.print(Panel(
            error_handler.format_error_for_display(enhanced_error),
            title="Network Error",
            border_style="red"
        ))
        
        # Show recovery plan
        recovery_plan = await error_recovery.create_recovery_plan(enhanced_error)
        console.print("\n[bold yellow]Recovery Plan:[/bold yellow]")
        for i, action in enumerate(recovery_plan.actions, 1):
            console.print(f"  {i}. {action.description}")
            if action.estimated_duration:
                console.print(f"     ⏱️  Estimated time: {action.estimated_duration}")
    
    # Demo 2: Permission Error
    print_section("Demo 2: Permission Denied Error")
    
    try:
        raise PermissionError("Permission denied: /nix/store/...")
    except Exception as e:
        enhanced_error = error_handler.handle_error(
            error=e,
            component="demo",
            operation="system_update",
            user_input="update system"
        )
        
        console.print(Panel(
            error_handler.format_error_for_display(enhanced_error),
            title="Permission Error",
            border_style="yellow"
        ))
        
        # Show quick suggestions
        suggestions = error_recovery.get_recovery_suggestions(enhanced_error)
        if suggestions:
            console.print("\n[bold green]Quick Suggestions:[/bold green]")
            for suggestion in suggestions:
                console.print(f"  • {suggestion}")
    
    # Demo 3: Package Not Found
    print_section("Demo 3: Package Not Found Error")
    
    try:
        raise ValueError("error: package 'firefx' not found")
    except Exception as e:
        enhanced_error = error_handler.handle_error(
            error=e,
            component="demo",
            operation="package_search",
            user_input="install firefx"
        )
        
        # Override category for demo
        enhanced_error.category = ErrorCategory.PACKAGE
        enhanced_error.solutions = [
            ErrorSolution(
                "Search for similar packages",
                "ask-nix search firefox",
                confidence=0.9
            ),
            ErrorSolution(
                "Did you mean 'firefox'?",
                "ask-nix install firefox",
                confidence=0.95
            )
        ]
        
        console.print(Panel(
            error_handler.format_error_for_display(enhanced_error),
            title="Package Error",
            border_style="blue"
        ))
    
    # Demo 4: Configuration Syntax Error
    print_section("Demo 4: Configuration Syntax Error")
    
    try:
        raise SyntaxError("error: syntax error at line 42: missing semicolon")
    except Exception as e:
        enhanced_error = error_handler.handle_error(
            error=e,
            component="demo",
            operation="config_validation",
            user_input="rebuild system"
        )
        
        # Add line-specific information
        enhanced_error.solutions.append(
            ErrorSolution(
                "Add missing semicolon at line 42",
                "sudo nano +42 /etc/nixos/configuration.nix",
                confidence=0.95,
                requires_sudo=True
            )
        )
        
        console.print(Panel(
            error_handler.format_error_for_display(enhanced_error, verbose=True),
            title="Syntax Error",
            border_style="magenta"
        ))
    
    # Demo 5: Error Summary
    print_section("Demo 5: Error Summary Report")
    
    summary = error_handler.get_error_summary()
    console.print(Panel(summary, title="Session Error Summary", border_style="cyan"))
    
    # Demo 6: Recovery Statistics
    print_section("Demo 6: Recovery Statistics")
    
    # Simulate some recovery attempts
    for error in error_handler.error_history[:2]:
        plan = await error_recovery.create_recovery_plan(error)
        # Simulate success/failure
        error_recovery.recovery_history.append((error, True))
    error_recovery.recovery_history.append((error_handler.error_history[2], False))
    
    stats = error_recovery.get_recovery_stats()
    
    console.print("[bold]Recovery Statistics:[/bold]")
    console.print(f"  Total recovery attempts: {stats['total_recoveries']}")
    console.print(f"  Successful: {stats['successful']} ✅")
    console.print(f"  Failed: {stats['failed']} ❌")
    console.print(f"  Success rate: {stats['success_rate']*100:.0f}%")
    
    if stats['by_category']:
        console.print("\n[bold]By Category:[/bold]")
        for category, data in stats['by_category'].items():
            success_rate = data['successful'] / data['total'] * 100 if data['total'] > 0 else 0
            console.print(f"  • {category}: {data['successful']}/{data['total']} ({success_rate:.0f}%)")
    
    # Demo 7: Export Error Report
    print_section("Demo 7: Export Error Report")
    
    report_path = error_handler.export_error_report()
    console.print(f"[green]✅ Error report exported to:[/green] {report_path}")
    
    # Show sample content
    with open(report_path, 'r') as f:
        lines = f.readlines()[:20]  # First 20 lines
        sample = ''.join(lines)
        console.print("\n[dim]Sample of exported report:[/dim]")
        console.print(Panel(sample + "...", title="Error Report Preview", border_style="dim"))


async def demo_interactive_recovery():
    """Demonstrate interactive error recovery"""
    print_section("Interactive Error Recovery Demo")
    
    console.print("[yellow]Simulating a failed package installation...[/yellow]\n")
    
    # Simulate error
    error_handler = TUIErrorHandler()
    error_recovery = ErrorRecovery()
    
    try:
        raise RuntimeError("Failed to build package: dependency 'libfoo' not found")
    except Exception as e:
        enhanced_error = error_handler.handle_error(
            error=e,
            component="demo",
            operation="package_build",
            user_input="install custom-package"
        )
        
        enhanced_error.category = ErrorCategory.DEPENDENCY
        
        # Show error
        console.print(Panel(
            error_handler.format_error_for_display(enhanced_error),
            title="Build Error",
            border_style="red"
        ))
        
        # Create recovery plan
        recovery_plan = await error_recovery.create_recovery_plan(enhanced_error)
        
        console.print("\n[bold cyan]Available Recovery Actions:[/bold cyan]")
        for i, action in enumerate(recovery_plan.actions, 1):
            console.print(f"\n{i}. [bold]{action.description}[/bold]")
            console.print(f"   Success rate: {action.success_rate*100:.0f}%")
            if action.requires_confirmation:
                console.print("   [yellow]⚠️  Requires confirmation[/yellow]")
            if action.estimated_duration:
                console.print(f"   ⏱️  Estimated time: {action.estimated_duration}")
        
        console.print("\n[dim]In the real TUI, you could execute these recovery actions with Ctrl+R[/dim]")


def main():
    """Run all demos"""
    console.print("[bold magenta]🚨 Enhanced Error Handling Demo 🚨[/bold magenta]")
    console.print("\nThis demo showcases the improved error handling features:")
    console.print("• User-friendly error messages")
    console.print("• Automatic recovery suggestions")
    console.print("• Error categorization and solutions")
    console.print("• Recovery planning and execution")
    console.print("• Error history and reporting")
    
    # Run demos
    asyncio.run(demo_error_handling())
    asyncio.run(demo_interactive_recovery())
    
    console.print("\n[bold green]✅ Demo Complete![/bold green]")
    console.print("\nTo see this in action in the TUI:")
    console.print("  1. Run: [cyan]./bin/nix-tui-enhanced[/cyan]")
    console.print("  2. Try commands that might fail")
    console.print("  3. Use Ctrl+E to see error history")
    console.print("  4. Use Ctrl+R to execute recovery plans")
    console.print("  5. Use Ctrl+D for debug mode (verbose errors)")


if __name__ == "__main__":
    main()