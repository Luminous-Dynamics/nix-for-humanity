"""
Enhanced output formatting for Luminous Nix v0.5.3+

Beautiful, consistent, and user-friendly terminal output.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.markdown import Markdown
from contextlib import contextmanager
import time


class Colors:
    """Semantic color scheme for Luminous Nix"""
    PRIMARY = "cyan"          # Main brand color
    SUCCESS = "green"         # Positive actions
    ERROR = "red"            # Problems
    WARNING = "yellow"       # Caution
    INFO = "blue"           # Information
    COMMAND = "magenta"     # Commands/code
    PACKAGE = "bold cyan"   # Package names
    MUTED = "dim white"     # Secondary text
    HIGHLIGHT = "bold white" # Emphasis


class EnhancedOutput:
    """Beautiful terminal output for Luminous Nix"""
    
    def __init__(self):
        """Initialize the enhanced output system"""
        self.console = Console()
        self.colors = Colors()
        
    def success(self, message: str, detail: Optional[str] = None):
        """Show success message with optional detail"""
        self.console.print(f"[{self.colors.SUCCESS}]✅ {message}[/]")
        if detail:
            self.console.print(f"   [{self.colors.MUTED}]{detail}[/]")
    
    def error(self, message: str, suggestion: Optional[str] = None):
        """Show error message with optional suggestion"""
        self.console.print(f"[{self.colors.ERROR}]❌ {message}[/]")
        if suggestion:
            self.console.print(f"   [{self.colors.INFO}]💡 {suggestion}[/]")
    
    def warning(self, message: str):
        """Show warning message"""
        self.console.print(f"[{self.colors.WARNING}]⚠️  {message}[/]")
    
    def info(self, message: str):
        """Show informational message"""
        self.console.print(f"[{self.colors.INFO}]ℹ️  {message}[/]")
    
    def command(self, cmd: str):
        """Show a command that will be or was executed"""
        self.console.print(f"[{self.colors.COMMAND}]$ {cmd}[/]")
    
    def package(self, name: str) -> str:
        """Format a package name"""
        return f"[{self.colors.PACKAGE}]{name}[/]"
    
    @contextmanager
    def progress(self, description: str, total: Optional[int] = None):
        """Context manager for progress indication"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn() if total else TextColumn(""),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task(description, total=total)
            yield lambda advance: progress.advance(task, advance) if total else None
    
    def show_packages(self, packages: List[Dict[str, Any]], title: Optional[str] = None):
        """Display packages in a beautiful table"""
        if not packages:
            self.warning("No packages found")
            return
        
        # Create table
        table_title = title or f"📦 Found {len(packages)} package(s)"
        table = Table(title=table_title, box=box.ROUNDED, show_lines=False)
        
        # Add columns
        table.add_column("Package", style=self.colors.PACKAGE, no_wrap=True)
        table.add_column("Version", style=self.colors.SUCCESS)
        table.add_column("Description", style=self.colors.MUTED, overflow="ellipsis", max_width=50)
        
        # Add rows (limit to 20 for readability)
        for pkg in packages[:20]:
            name = pkg.get("name", "unknown")
            version = pkg.get("version", "-")
            desc = pkg.get("description", "")[:80]  # Truncate long descriptions
            
            table.add_row(name, version, desc)
        
        # Show table
        self.console.print(table)
        
        # Add note if truncated
        if len(packages) > 20:
            self.info(f"Showing first 20 of {len(packages)} packages. Refine your search for better results.")
    
    def show_help(self):
        """Display beautiful help information"""
        help_text = """
# 🌟 Luminous Nix - Natural Language NixOS

## Available Commands

- **search** <term>     - Find packages
- **install** <package> - Install a package  
- **remove** <package>  - Remove a package
- **list**             - Show installed packages
- **info**             - System information
- **clean**            - Free up disk space
- **help**             - Show this help

## Examples

```bash
ask-nix "search firefox"
ask-nix "install vim"
ask-nix "what's installed?"
ask-nix "clean up old packages"
```

## Tips

💡 Use `--dry-run` to preview actions without executing
💡 Use quotes for multi-word searches: "text editor"
💡 Natural language works: "find me a markdown editor"
"""
        md = Markdown(help_text)
        self.console.print(Panel(md, title="Help", border_style=self.colors.PRIMARY))
    
    def show_system_info(self, info: Dict[str, Any]):
        """Display system information beautifully"""
        panel_content = []
        
        for key, value in info.items():
            formatted_key = key.replace("_", " ").title()
            panel_content.append(f"[{self.colors.INFO}]{formatted_key}:[/] {value}")
        
        text = "\n".join(panel_content)
        self.console.print(
            Panel(
                text, 
                title="🖥️  System Information",
                border_style=self.colors.PRIMARY
            )
        )
    
    def suggest_commands(self, failed_input: str) -> List[str]:
        """Suggest commands based on failed input"""
        suggestions = []
        
        # Common typos and alternatives
        typo_map = {
            "instal": ["install"],
            "isntall": ["install"],
            "intall": ["install"],
            "uninstal": ["remove", "uninstall"],
            "delete": ["remove", "uninstall"],
            "find": ["search", "list"],
            "show": ["list", "info"],
            "update": ["upgrade"],
            "cleanup": ["clean", "garbage collect"],
        }
        
        # Check for typos
        for typo, corrections in typo_map.items():
            if typo in failed_input.lower():
                suggestions.extend(corrections)
        
        # If we have suggestions, show them
        if suggestions:
            self.info(f"Did you mean: {', '.join(suggestions)}?")
        
        return suggestions
    
    def dry_run_notice(self):
        """Show dry-run mode notice"""
        self.warning("DRY RUN MODE - No changes will be made")
    
    def thinking(self, message: str = "Processing"):
        """Show a thinking/processing message"""
        self.console.print(f"[{self.colors.INFO}]🤔 {message}...[/]")
    
    def section_header(self, title: str):
        """Display a section header"""
        self.console.rule(f"[{self.colors.PRIMARY}]{title}[/]", style=self.colors.PRIMARY)


# Global instance for easy access
output = EnhancedOutput()


# Convenience functions for quick access
def success(message: str, detail: Optional[str] = None):
    """Show success message"""
    output.success(message, detail)


def error(message: str, suggestion: Optional[str] = None):
    """Show error message"""
    output.error(message, suggestion)


def info(message: str):
    """Show info message"""
    output.info(message)


def warning(message: str):
    """Show warning message"""
    output.warning(message)


def show_packages(packages: List[Dict[str, Any]], title: Optional[str] = None):
    """Display packages in a table"""
    output.show_packages(packages, title)


def progress(description: str, total: Optional[int] = None):
    """Create a progress context"""
    return output.progress(description, total)