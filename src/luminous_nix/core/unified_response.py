"""
Unified Response System - Consistent, beautiful response formatting.

This consolidates functionality from:
- responses.py
- response_adapter.py
- response_enhancer.py
- enhanced_output.py

Philosophy: Every response should be clear, helpful, and optionally beautiful.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Optional rich support for beautiful output
try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

    # Mock classes for when Rich isn't available
    class Table:
        pass

    class Panel:
        pass

    class Progress:
        pass


# ==================== Response Types ====================


class ResponseType(Enum):
    """Types of responses for different formatting."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PROGRESS = "progress"
    TABLE = "table"
    LIST = "list"
    JSON = "json"


@dataclass
class Response:
    """Unified response structure."""

    success: bool
    text: str
    type: ResponseType = ResponseType.INFO
    data: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "text": self.text,
            "type": self.type.value,
            "data": self.data,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# ==================== Response Formatter ====================


class ResponseFormatter:
    """Format responses for different output modes."""

    def __init__(
        self,
        use_color: bool = True,
        use_emoji: bool = True,
        use_rich: bool = True,
        output_format: str = "text",
    ):
        """Initialize formatter.

        Args:
            use_color: Use ANSI colors
            use_emoji: Use emoji in output
            use_rich: Use rich library if available
            output_format: Default format (text, json, minimal)
        """
        self.use_color = use_color
        self.use_emoji = use_emoji
        self.use_rich = use_rich and RICH_AVAILABLE
        self.output_format = output_format

        # Emoji mappings
        self.emojis = {
            ResponseType.SUCCESS: "✅" if use_emoji else "[OK]",
            ResponseType.ERROR: "❌" if use_emoji else "[ERROR]",
            ResponseType.WARNING: "⚠️" if use_emoji else "[WARN]",
            ResponseType.INFO: "ℹ️" if use_emoji else "[INFO]",
            ResponseType.PROGRESS: "🔄" if use_emoji else "[...]",
        }

        # ANSI color codes
        self.colors = {
            ResponseType.SUCCESS: "\033[32m",  # Green
            ResponseType.ERROR: "\033[31m",  # Red
            ResponseType.WARNING: "\033[33m",  # Yellow
            ResponseType.INFO: "\033[36m",  # Cyan
            ResponseType.PROGRESS: "\033[35m",  # Magenta
        }
        self.reset_color = "\033[0m"

    def format(self, response: Response) -> str:
        """Format a response for display.

        Args:
            response: The response to format

        Returns:
            Formatted string
        """
        if self.output_format == "json":
            return response.to_json()
        elif self.output_format == "minimal":
            return self._format_minimal(response)
        elif self.use_rich and response.type == ResponseType.TABLE:
            return self._format_rich_table(response)
        elif self.use_rich and response.type == ResponseType.LIST:
            return self._format_rich_list(response)
        else:
            return self._format_text(response)

    def _format_text(self, response: Response) -> str:
        """Format as plain text with optional color/emoji."""
        # Build prefix
        prefix = self.emojis.get(response.type, "")

        # Add color if enabled
        if self.use_color and response.type in self.colors:
            color = self.colors[response.type]
            text = f"{color}{prefix} {response.text}{self.reset_color}"
        else:
            text = f"{prefix} {response.text}"

        # Add data if present
        if response.data:
            if "packages" in response.data:
                # Format package list
                packages = response.data["packages"]
                if isinstance(packages, list) and packages:
                    text += "\n\nPackages:\n"
                    for pkg in packages[:10]:  # Show first 10
                        if isinstance(pkg, dict):
                            name = pkg.get("name", "unknown")
                            desc = pkg.get("description", "")
                            text += (
                                f"  • {name}: {desc[:60]}...\n"
                                if desc
                                else f"  • {name}\n"
                            )
                        else:
                            text += f"  • {pkg}\n"
                    if len(packages) > 10:
                        text += f"  ... and {len(packages) - 10} more\n"

            elif "error" in response.data:
                # Show error details
                text += f"\n\nError details: {response.data['error']}"

            elif "output" in response.data:
                # Show command output
                output = response.data["output"]
                if output:
                    text += f"\n\nOutput:\n{output[:500]}"  # Limit output length
                    if len(output) > 500:
                        text += "\n... (truncated)"

        return text

    def _format_minimal(self, response: Response) -> str:
        """Format with minimal decoration."""
        if response.success:
            return response.text
        else:
            return f"Error: {response.text}"

    def _format_rich_table(self, response: Response) -> str:
        """Format as rich table (requires rich library)."""
        if not RICH_AVAILABLE or not response.data or "packages" not in response.data:
            return self._format_text(response)

        # Create table
        table = Table(title=response.text, box=box.ROUNDED)
        table.add_column("Package", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Description", style="white")

        # Add rows
        packages = response.data["packages"]
        for pkg in packages[:20]:  # Limit to 20 rows
            if isinstance(pkg, dict):
                table.add_row(
                    pkg.get("name", ""),
                    pkg.get("version", "unknown"),
                    pkg.get("description", "No description")[:50],
                )
            else:
                table.add_row(str(pkg), "", "")

        # Print table and capture output
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        console.print(table)
        output = buffer.getvalue()
        sys.stdout = old_stdout

        return output

    def _format_rich_list(self, response: Response) -> str:
        """Format as rich list (requires rich library)."""
        if not RICH_AVAILABLE:
            return self._format_text(response)

        # Create panel with list
        items = response.data.get("items", []) if response.data else []
        if items:
            content = "\n".join([f"• {item}" for item in items[:20]])
        else:
            content = response.text

        panel = Panel(
            content,
            title=response.text,
            border_style="green" if response.success else "red",
        )

        # Print panel and capture output
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        console.print(panel)
        output = buffer.getvalue()
        sys.stdout = old_stdout

        return output


# ==================== Response Builder ====================


class ResponseBuilder:
    """Builder pattern for creating responses."""

    def __init__(self):
        """Initialize builder."""
        self._success = True
        self._text = ""
        self._type = ResponseType.INFO
        self._data = {}
        self._metadata = {}

    def success(self, text: str = "Operation successful") -> "ResponseBuilder":
        """Set as success response."""
        self._success = True
        self._text = text
        self._type = ResponseType.SUCCESS
        return self

    def error(self, text: str = "Operation failed") -> "ResponseBuilder":
        """Set as error response."""
        self._success = False
        self._text = text
        self._type = ResponseType.ERROR
        return self

    def warning(self, text: str) -> "ResponseBuilder":
        """Set as warning response."""
        self._text = text
        self._type = ResponseType.WARNING
        return self

    def info(self, text: str) -> "ResponseBuilder":
        """Set as info response."""
        self._text = text
        self._type = ResponseType.INFO
        return self

    def with_data(self, key: str, value: Any) -> "ResponseBuilder":
        """Add data to response."""
        self._data[key] = value
        return self

    def with_packages(self, packages: list[Any]) -> "ResponseBuilder":
        """Add package list to response."""
        self._data["packages"] = packages
        if "found" in self._text.lower() or "search" in self._text.lower():
            self._type = ResponseType.TABLE
        return self

    def with_error_details(self, error: str) -> "ResponseBuilder":
        """Add error details."""
        self._data["error"] = error
        return self

    def with_metadata(self, key: str, value: Any) -> "ResponseBuilder":
        """Add metadata."""
        self._metadata[key] = value
        return self

    def build(self) -> Response:
        """Build the response."""
        return Response(
            success=self._success,
            text=self._text,
            type=self._type,
            data=self._data if self._data else None,
            metadata=self._metadata,
        )


# ==================== Progress Indicator ====================


class ProgressReporter:
    """Report progress for long operations."""

    def __init__(self, use_rich: bool = True):
        """Initialize progress reporter."""
        self.use_rich = use_rich and RICH_AVAILABLE
        self.progress = None
        self.task = None

    def start(self, description: str, total: Optional[int] = None) -> None:
        """Start progress reporting."""
        if self.use_rich:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            )
            self.progress.__enter__()
            self.task = self.progress.add_task(description, total=total)
        else:
            print(f"Starting: {description}...")

    def update(self, description: Optional[str] = None, advance: int = 1) -> None:
        """Update progress."""
        if self.use_rich and self.progress and self.task is not None:
            if description:
                self.progress.update(self.task, description=description)
            self.progress.update(self.task, advance=advance)
        elif description:
            print(f"Progress: {description}")

    def stop(self) -> None:
        """Stop progress reporting."""
        if self.use_rich and self.progress:
            self.progress.__exit__(None, None, None)
            self.progress = None
            self.task = None
        else:
            print("Complete.")


# ==================== Convenience Functions ====================

# Default formatter instance
_default_formatter = ResponseFormatter()


def format_response(response: Response, **kwargs) -> str:
    """Format a response with optional settings."""
    formatter = ResponseFormatter(**kwargs) if kwargs else _default_formatter
    return formatter.format(response)


def success_response(text: str, **data) -> Response:
    """Create a success response."""
    builder = ResponseBuilder().success(text)
    for key, value in data.items():
        builder.with_data(key, value)
    return builder.build()


def error_response(text: str, error: Optional[str] = None) -> Response:
    """Create an error response."""
    builder = ResponseBuilder().error(text)
    if error:
        builder.with_error_details(error)
    return builder.build()


def package_response(text: str, packages: list[Any]) -> Response:
    """Create a response with package list."""
    return ResponseBuilder().success(text).with_packages(packages).build()


# ==================== Output Functions ====================


def output(response: Response, file=None) -> None:
    """Output a response to console or file."""
    formatted = format_response(response)
    if file:
        file.write(formatted + "\n")
    else:
        print(formatted)


def show_packages(packages: list[Any], title: str = "Packages") -> None:
    """Show a list of packages."""
    response = package_response(title, packages)
    output(response)


def progress(description: str) -> ProgressReporter:
    """Create a progress reporter context manager."""
    reporter = ProgressReporter()
    reporter.start(description)
    return reporter
